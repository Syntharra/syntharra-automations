#!/usr/bin/env python3
"""
usage_alert.py — Mid-month usage alerts: 80% and 100% of included minutes.

Replaces broken n8n workflow Wa3pHRMwSjbZHqMC (queried dropped hvac_call_log table).
Run daily via cron. Idempotent: alert_80_sent / alert_100_sent guard against duplicates.

Logic per active subscription:
  1. Compute current billing month (calendar month).
  2. Fetch calls from Retell list-calls for month-to-date.
  3. If usage >= 80% AND billing_cycles.alert_80_sent is false  → send 80% email, set flag.
  4. If usage >= 100% AND billing_cycles.alert_100_sent is false → send 100% email, set flag.

Billing cycle assumption: calendar month (matches monthly_minutes.py).
billing_cycles row is created if it doesn't exist for the current month.

Usage:
  python tools/usage_alert.py                  # current month
  python tools/usage_alert.py --dry-run        # compute + log, no emails or DB writes
  python tools/usage_alert.py --month 2026-04  # specific month (YYYY-MM)

Required env vars:
  SUPABASE_URL          — https://hgheyqwnrcvwtgngqdnq.supabase.co
  SUPABASE_SERVICE_KEY  — service_role JWT
  RETELL_API_KEY
  BREVO_API_KEY
"""
from __future__ import annotations
import argparse, json, math, os, sys, urllib.error, urllib.parse, urllib.request
from calendar import monthrange
from datetime import datetime, timezone


# ---------- helpers ----------

def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def http_json(method: str, url: str, headers: dict, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:500]}


def sb_headers() -> dict:
    k = env("SUPABASE_SERVICE_KEY")
    return {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}


# ---------- Supabase ----------

def fetch_active_subscriptions() -> list[dict]:
    url = (env("SUPABASE_URL").rstrip("/") +
           "/rest/v1/client_subscriptions"
           "?status=eq.active"
           "&select=agent_id,company_name,client_email,included_minutes")
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        sys.exit(f"Supabase fetch subscriptions failed: {status} {data}")
    return data or []


def fetch_billing_cycle(agent_id: str, billing_month: str) -> dict | None:
    """Return billing_cycles row for (agent_id, billing_month), or None."""
    url = (env("SUPABASE_URL").rstrip("/") +
           f"/rest/v1/billing_cycles"
           f"?agent_id=eq.{urllib.parse.quote(agent_id)}"
           f"&billing_month=eq.{urllib.parse.quote(billing_month)}"
           f"&select=*"
           f"&limit=1")
    status, data = http_json("GET", url, sb_headers())
    if status != 200 or not data:
        return None
    return data[0] if isinstance(data, list) else None


def ensure_billing_cycle(agent_id: str, billing_month: str,
                          included_minutes: int) -> dict:
    """Get existing billing_cycles row or create a minimal one."""
    row = fetch_billing_cycle(agent_id, billing_month)
    if row:
        return row
    # Create a baseline row so alert flags can be written
    year, month = int(billing_month[:4]), int(billing_month[5:7])
    last_day = monthrange(year, month)[1]
    new_row = {
        "agent_id": agent_id,
        "billing_month": billing_month,
        "included_minutes": included_minutes,
        "alert_80_sent": False,
        "alert_100_sent": False,
        "cycle_start": f"{billing_month}-01",
        "cycle_end": f"{billing_month}-{last_day:02d}",
    }
    url = env("SUPABASE_URL").rstrip("/") + "/rest/v1/billing_cycles"
    headers = {**sb_headers(), "Prefer": "return=representation"}
    status, data = http_json("POST", url, headers, new_row)
    if status in (200, 201):
        return data[0] if isinstance(data, list) else data
    # Row might already exist (race) — try fetching again
    row = fetch_billing_cycle(agent_id, billing_month)
    return row or new_row


def set_alert_flag(agent_id: str, billing_month: str, field: str) -> None:
    url = (env("SUPABASE_URL").rstrip("/") +
           f"/rest/v1/billing_cycles"
           f"?agent_id=eq.{urllib.parse.quote(agent_id)}"
           f"&billing_month=eq.{urllib.parse.quote(billing_month)}")
    headers = {**sb_headers(), "Prefer": "return=minimal"}
    http_json("PATCH", url, headers, {field: True})


# ---------- Retell ----------

def fetch_calls_mtd(agent_id: str, year: int, month: int) -> list[dict]:
    """Fetch month-to-date calls for agent. Paginated up to 5000 calls."""
    key = env("RETELL_API_KEY")
    period_start = datetime(year, month, 1, tzinfo=timezone.utc)
    period_end   = datetime.now(timezone.utc)  # up to now (mid-month)
    body = {
        "filter_criteria": {
            "agent_id": [agent_id],
            "start_timestamp": {
                "lower_threshold": int(period_start.timestamp() * 1000),
                "upper_threshold": int(period_end.timestamp() * 1000),
            },
        },
        "limit": 1000,
        "sort_order": "descending",
    }
    all_calls: list[dict] = []
    # Paginate up to 5 pages (5000 calls) — more than enough pre-launch
    for _ in range(5):
        status, data = http_json(
            "POST", "https://api.retellai.com/v2/list-calls",
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            body,
        )
        if status != 200:
            print(f"  [WARN] Retell list-calls failed for {agent_id}: {status} {data}")
            break
        page = data if isinstance(data, list) else data.get("calls", [])
        all_calls.extend(page)
        if len(page) < 1000:
            break  # no more pages
        # cursor pagination: advance by oldest call's start_timestamp
        oldest_ts = min(c.get("start_timestamp", 0) for c in page if c.get("start_timestamp"))
        body["filter_criteria"]["start_timestamp"]["upper_threshold"] = oldest_ts - 1
    return all_calls


# ---------- Brevo ----------

ALERT_TEMPLATES = {
    80: {
        "subject": "⚠️ You've used 80% of your AI receptionist minutes this month",
        "heading": "You're at 80% of your included minutes",
        "body_extra": (
            "<p>You still have time left in the month, but we wanted to give you a heads-up "
            "so there are no surprises at billing time. If you go over your included minutes, "
            "overage is charged per minute at your plan rate.</p>"
            "<p>No action needed — your AI receptionist keeps running. This is just a friendly alert.</p>"
        ),
    },
    100: {
        "subject": "📢 You've used 100% of your included minutes — overage now applying",
        "heading": "You've reached your included minutes limit",
        "body_extra": (
            "<p>Overage charges are now applying for any additional minutes used this month. "
            "Your AI receptionist continues to work normally — calls won't be blocked.</p>"
            "<p>You'll see the overage on your next invoice. "
            "If you have questions, reply to this email and we'll sort it out.</p>"
        ),
    },
}


def send_alert_email(sub: dict, threshold_pct: int, total_minutes: int,
                     included_minutes: int, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] would send {threshold_pct}% alert to {sub['client_email']}")
        return
    tmpl = ALERT_TEMPLATES[threshold_pct]
    usage_pct = round(total_minutes / included_minutes * 100) if included_minutes else 0
    html = f"""
<div style="font-family:sans-serif;max-width:600px;margin:0 auto">
  <h2 style="color:#1a1a2e">{tmpl['heading']}</h2>
  <p>Hi {sub.get('company_name', 'there')},</p>
  <table style="width:100%;border-collapse:collapse;margin:16px 0">
    <tr>
      <td style="padding:8px;border-bottom:1px solid #eee">Minutes used so far</td>
      <td style="padding:8px;border-bottom:1px solid #eee;text-align:right"><strong>{total_minutes}</strong></td>
    </tr>
    <tr>
      <td style="padding:8px;border-bottom:1px solid #eee">Included minutes</td>
      <td style="padding:8px;border-bottom:1px solid #eee;text-align:right">{included_minutes}</td>
    </tr>
    <tr>
      <td style="padding:8px">Usage</td>
      <td style="padding:8px;text-align:right"><strong>{usage_pct}%</strong></td>
    </tr>
  </table>
  {tmpl['body_extra']}
  <p style="color:#888;font-size:12px;margin-top:32px">
    Syntharra · <a href="mailto:support@syntharra.com">support@syntharra.com</a>
  </p>
</div>"""
    payload = {
        "sender": {"name": "Syntharra", "email": "support@syntharra.com"},
        "to": [{"email": sub["client_email"]}],
        "subject": tmpl["subject"],
        "htmlContent": html,
    }
    status, data = http_json(
        "POST", "https://api.brevo.com/v3/smtp/email",
        {"api-key": env("BREVO_API_KEY"), "Content-Type": "application/json"},
        payload,
    )
    if status not in (200, 201, 202):
        print(f"  [WARN] Brevo email failed: {status} {data}")
    else:
        print(f"  alert {threshold_pct}% email sent → {sub['client_email']}")


# ---------- per-subscription logic ----------

def process_subscription(sub: dict, year: int, month: int, dry_run: bool) -> None:
    agent_id       = sub["agent_id"]
    company        = sub.get("company_name", agent_id)
    billing_month  = f"{year}-{month:02d}"
    included       = sub.get("included_minutes") or 500

    print(f"\n--- {company} ({agent_id}) [{billing_month}] ---")

    cycle = ensure_billing_cycle(agent_id, billing_month, included)
    already_80  = cycle.get("alert_80_sent", False)
    already_100 = cycle.get("alert_100_sent", False)

    if already_80 and already_100:
        print("  both alerts already sent — skip")
        return

    calls        = fetch_calls_mtd(agent_id, year, month)
    total_ms     = sum(c.get("duration_ms") or 0 for c in calls)
    total_minutes = math.ceil(total_ms / 60_000)
    usage_pct    = round(total_minutes / included * 100) if included else 0

    print(f"  {total_minutes}/{included} min used ({usage_pct}%) — {len(calls)} calls")
    print(f"  alert_80_sent={already_80}, alert_100_sent={already_100}")

    # 100% alert (check first so we don't double-send 80 when already at 100+)
    if usage_pct >= 100 and not already_100:
        send_alert_email(sub, 100, total_minutes, included, dry_run)
        if not dry_run:
            set_alert_flag(agent_id, billing_month, "alert_100_sent")
            print("  billing_cycles.alert_100_sent = true")

    # 80% alert (only if not already at 100%; if at 100% they get one email, not two)
    if usage_pct >= 80 and not already_80 and usage_pct < 100:
        send_alert_email(sub, 80, total_minutes, included, dry_run)
        if not dry_run:
            set_alert_flag(agent_id, billing_month, "alert_80_sent")
            print("  billing_cycles.alert_80_sent = true")

    # If we just hit 100% we should also mark 80% as sent (it was implicitly passed)
    if usage_pct >= 100 and not already_80 and not dry_run:
        set_alert_flag(agent_id, billing_month, "alert_80_sent")


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--month", help="YYYY-MM override (default: current calendar month)")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    if args.month:
        try:
            year, month = int(args.month[:4]), int(args.month[5:7])
        except (ValueError, IndexError):
            sys.exit("--month must be YYYY-MM")
    else:
        year, month = now.year, now.month

    print(f"usage_alert.py — {year}-{month:02d} {'[DRY-RUN]' if args.dry_run else ''}")

    subs = fetch_active_subscriptions()
    if not subs:
        print("No active subscriptions — nothing to do.")
        return

    print(f"Checking {len(subs)} active subscription(s)...")
    for sub in subs:
        try:
            process_subscription(sub, year, month, args.dry_run)
        except Exception as exc:
            print(f"  [ERROR] {sub.get('agent_id')}: {exc}")

    print("\nDone.")


if __name__ == "__main__":
    main()
