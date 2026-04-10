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

Schedule: runs daily at 08:00 UTC.
  0 8 * * *  python tools/usage_alert.py

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

# Shared email shell — mirrors client-update form design system
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shared.email_template import syntharra_email_shell  # noqa: E402


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
    # pilot_mode=eq.false is a defensive filter added 2026-04-11 (Phase 0).
    # Pilot rows use status='pilot' and are naturally excluded by status=eq.active,
    # but this defensive filter prevents any regression. See spec § 6.2.1.
    url = (env("SUPABASE_URL").rstrip("/") +
           "/rest/v1/client_subscriptions"
           "?status=eq.active"
           "&pilot_mode=eq.false"
           "&select=agent_id,company_name,client_email,included_minutes,tier,overage_rate")
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
        "period_start": f"{billing_month}-01",
        "period_end": f"{billing_month}-{last_day:02d}",
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
        "body_extra": None,  # generated dynamically with actual overage_rate
    },
}


def send_alert_email(sub: dict, threshold_pct: int, total_minutes: int,
                     included_minutes: int, dry_run: bool, overage_rate: float = 0.18) -> None:
    if dry_run:
        print(f"  [DRY-RUN] would send {threshold_pct}% alert to {sub['client_email']}")
        return
    tmpl = ALERT_TEMPLATES[threshold_pct]
    company = sub.get("company_name", "there")
    # Build dynamic body_extra for 100% alert using actual overage_rate
    body_extra = tmpl.get("body_extra") or (
        f"<p>Overage charges are now applying at <strong>${overage_rate:.2f}/min</strong> "
        "for any additional minutes used this month. "
        "Your AI receptionist continues to work normally — calls won't be blocked.</p>"
        "<p>You'll see the overage on your next invoice. "
        "If you have questions, reply to this email and we'll sort it out.</p>"
    )
    usage_pct = round(total_minutes / included_minutes * 100) if included_minutes else 0
    bar_width = min(usage_pct, 100)
    bar_color = "#DC2626" if threshold_pct >= 100 else "#D97706"
    badge_style = (
        "display:inline-block;background:#DC2626;color:#fff;padding:5px 12px;border-radius:999px;"
        "font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:20px"
        if threshold_pct >= 100 else
        "display:inline-block;background:#D97706;color:#fff;padding:5px 12px;border-radius:999px;"
        "font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:20px"
    )
    badge_label = "Overage Active" if threshold_pct >= 100 else "Usage Alert"

    body = (
        f'<span style="{badge_style}">{badge_label}</span>'
        f'<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 6px;letter-spacing:-0.02em">{tmpl["heading"]}</h1>'
        f'<div style="font-size:14px;color:#6B7280;margin-bottom:24px">Hi {company} — here\'s your current usage.</div>'

        # Progress bar
        f'<div style="margin-bottom:24px">'
        f'<div style="height:8px;background:#E8E6FF;border-radius:4px;overflow:hidden">'
        f'<div style="height:8px;width:{bar_width}%;background:{bar_color};border-radius:4px"></div>'
        f'</div>'
        f'<div style="font-size:11px;color:#6B7280;margin-top:6px;text-align:right">{total_minutes} / {included_minutes} min used</div>'
        f'</div>'

        # Stats card
        '<div style="padding:20px 24px;background:#F8F7FF;border-radius:12px;border:1px solid #E8E6FF;margin-bottom:24px">'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        f'<tr><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Minutes used so far</td>'
        f'<td style="padding:8px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;font-weight:700;color:#0D0D1A">{total_minutes}</td></tr>'
        f'<tr><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Included minutes</td>'
        f'<td style="padding:8px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;color:#0D0D1A">{included_minutes}</td></tr>'
        f'<tr><td style="padding:10px 0 0;font-size:14px;color:#6B7280">Usage</td>'
        f'<td style="padding:10px 0 0;text-align:right;font-size:20px;font-weight:700;color:{bar_color}">{usage_pct}%</td></tr>'
        '</table>'
        '</div>'

        f'<div style="font-size:14px;color:#1A1A2E;line-height:1.7">{body_extra}</div>'
        f'<div style="margin-top:20px;font-size:13px;color:#6B7280">Questions? Email us at '
        f'<a href="mailto:support@syntharra.com" style="color:#6C63FF;text-decoration:none;font-weight:500">support@syntharra.com</a></div>'
    )

    html = syntharra_email_shell(
        header_context=f"Usage alert &nbsp;&middot;&nbsp; {threshold_pct}% of included minutes",
        body_html=body,
    )
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
    included       = sub.get("included_minutes") or 700
    overage_rate   = float(sub.get("overage_rate") or 0.18)
    tier           = sub.get("tier") or "professional"

    print(f"\n--- {company} ({agent_id}) [{billing_month}] tier={tier} overage=${overage_rate}/min ---")

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
        send_alert_email(sub, 100, total_minutes, included, dry_run, overage_rate)
        if not dry_run:
            set_alert_flag(agent_id, billing_month, "alert_100_sent")
            print("  billing_cycles.alert_100_sent = true")

    # 80% alert (only if not already at 100%; if at 100% they get one email, not two)
    if usage_pct >= 80 and not already_80 and usage_pct < 100:
        send_alert_email(sub, 80, total_minutes, included, dry_run, overage_rate)
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
