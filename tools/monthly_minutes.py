#!/usr/bin/env python3
"""
monthly_minutes.py — Monthly billing: Retell list-calls → minutes calc → Stripe overage → Brevo usage email.

Reads active subscriptions from Supabase client_subscriptions.
For each: calls Retell list-calls for the billing month, calculates minutes,
charges overage via Stripe if over limit, writes monthly_billing_snapshot,
sends usage report email via Brevo.

Idempotent: skips any (agent_id, billing_month) already in monthly_billing_snapshot.

Usage:
  python tools/monthly_minutes.py                   # previous calendar month
  python tools/monthly_minutes.py --month 2026-03   # specific month YYYY-MM
  python tools/monthly_minutes.py --dry-run         # compute + log, no Stripe/email/DB writes

Required env vars (fetch from syntharra_vault):
  SUPABASE_URL           — https://hgheyqwnrcvwtgngqdnq.supabase.co
  SUPABASE_SERVICE_KEY   — service_role JWT
  RETELL_API_KEY
  STRIPE_SECRET_KEY      — sk_live_... once live; sk_test_... for now
  BREVO_API_KEY
"""
from __future__ import annotations
import argparse, json, math, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from calendar import monthrange


# --------------- env / http ---------------

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


# --------------- Supabase ---------------

def sb_headers() -> dict:
    k = env("SUPABASE_SERVICE_KEY")
    return {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}


def fetch_active_subscriptions() -> list[dict]:
    url = env("SUPABASE_URL").rstrip("/") + \
        "/rest/v1/client_subscriptions?status=eq.active&select=agent_id,company_name,client_email,included_minutes,overage_rate_cents,stripe_customer_id,stripe_subscription_id"
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        sys.exit(f"Supabase fetch subscriptions failed: {status} {data}")
    return data or []


def already_processed(agent_id: str, billing_month: str) -> bool:
    url = (env("SUPABASE_URL").rstrip("/") +
           f"/rest/v1/monthly_billing_snapshot"
           f"?agent_id=eq.{urllib.parse.quote(agent_id)}"
           f"&billing_month=eq.{urllib.parse.quote(billing_month)}"
           f"&select=id")
    status, data = http_json("GET", url, sb_headers())
    return status == 200 and len(data) > 0


def write_snapshot(row: dict) -> None:
    url = env("SUPABASE_URL").rstrip("/") + "/rest/v1/monthly_billing_snapshot"
    headers = {**sb_headers(), "Prefer": "return=minimal"}
    status, data = http_json("POST", url, headers, body=row)
    if status not in (200, 201):
        print(f"  [WARN] snapshot write failed: {status} {data}")


# --------------- Retell ---------------

def fetch_calls(agent_id: str, period_start: datetime, period_end: datetime) -> list[dict]:
    """Fetch all calls for agent in period. Uses limit=1000 (pre-launch: <100/mo expected)."""
    key = env("RETELL_API_KEY")
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
    status, data = http_json(
        "POST", "https://api.retellai.com/v2/list-calls",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
    )
    if status != 200:
        print(f"  [WARN] Retell list-calls failed for {agent_id}: {status}")
        return []
    return data if isinstance(data, list) else data.get("calls", [])


# --------------- Stripe ---------------

def stripe_headers() -> dict:
    return {"Authorization": f"Bearer {env('STRIPE_SECRET_KEY')}",
            "Content-Type": "application/x-www-form-urlencoded"}


def stripe_create_invoice(customer_id: str, description: str) -> str:
    """Create a draft invoice. Returns invoice_id."""
    body = urllib.parse.urlencode({
        "customer": customer_id,
        "description": description,
        "collection_method": "charge_automatically",
        "auto_advance": "false",  # we finalize explicitly
    })
    status, data = http_json("POST", "https://api.stripe.com/v1/invoices",
                             stripe_headers(), body.encode())
    if status not in (200, 201):
        raise RuntimeError(f"Stripe create invoice failed: {status} {data}")
    return data["id"]


def stripe_add_line_item(invoice_id: str, amount_cents: int, description: str) -> None:
    body = urllib.parse.urlencode({
        "invoice": invoice_id,
        "amount": str(amount_cents),
        "currency": "usd",
        "description": description,
    })
    status, data = http_json("POST", "https://api.stripe.com/v1/invoiceitems",
                             stripe_headers(), body.encode())
    if status not in (200, 201):
        raise RuntimeError(f"Stripe add line item failed: {status} {data}")


def stripe_finalize_and_charge(invoice_id: str) -> None:
    status, data = http_json(
        "POST", f"https://api.stripe.com/v1/invoices/{invoice_id}/finalize",
        stripe_headers(), b"auto_advance=true",
    )
    if status not in (200, 201):
        raise RuntimeError(f"Stripe finalize failed: {status} {data}")


# --------------- Brevo ---------------

def send_usage_email(sub: dict, result: dict, billing_month: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] would send usage email to {sub['client_email']}")
        return
    overage_line = (
        f"<p><strong>Overage charge: ${result['overage_amount_dollars']}</strong> "
        f"({result['overage_minutes']} min × $0.{result['overage_rate_cents']:02d}/min)</p>"
        if result["has_overage"] else
        "<p>No overage this month.</p>"
    )
    html = f"""
<div style="font-family:sans-serif;max-width:600px;margin:0 auto">
  <h2 style="color:#1a1a2e">Monthly Usage Report — {billing_month}</h2>
  <p>Hi {sub.get('company_name','')},</p>
  <p>Here's your Syntharra AI Receptionist usage summary for <strong>{billing_month}</strong>:</p>
  <table style="width:100%;border-collapse:collapse">
    <tr><td style="padding:8px;border-bottom:1px solid #eee">Total calls</td>
        <td style="padding:8px;border-bottom:1px solid #eee;text-align:right"><strong>{result['call_count']}</strong></td></tr>
    <tr><td style="padding:8px;border-bottom:1px solid #eee">Total minutes</td>
        <td style="padding:8px;border-bottom:1px solid #eee;text-align:right"><strong>{result['total_minutes']}</strong></td></tr>
    <tr><td style="padding:8px;border-bottom:1px solid #eee">Included minutes</td>
        <td style="padding:8px;border-bottom:1px solid #eee;text-align:right">{result['included_minutes']}</td></tr>
    <tr><td style="padding:8px">Usage</td>
        <td style="padding:8px;text-align:right">{result['usage_percent']}%</td></tr>
  </table>
  {overage_line}
  <p style="color:#888;font-size:12px;margin-top:32px">Syntharra · support@syntharra.com</p>
</div>"""
    payload = {
        "sender": {"name": "Syntharra", "email": "support@syntharra.com"},
        "to": [{"email": sub["client_email"]}],
        "subject": f"Your Syntharra Usage Report — {billing_month}",
        "htmlContent": html,
    }
    status, data = http_json(
        "POST", "https://api.brevo.com/v3/smtp/email",
        {"api-key": env("BREVO_API_KEY"), "Content-Type": "application/json"},
        payload,
    )
    if status not in (200, 201):
        print(f"  [WARN] Brevo email failed: {status} {data}")
    else:
        print(f"  email sent → {sub['client_email']}")


# --------------- main ---------------

def billing_period(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, 999999, tzinfo=timezone.utc)
    return start, end


def process_subscription(sub: dict, year: int, month: int, dry_run: bool) -> None:
    agent_id = sub["agent_id"]
    billing_month = f"{year}-{month:02d}"
    company = sub.get("company_name", agent_id)

    print(f"\n--- {company} ({agent_id}) ---")

    if already_processed(agent_id, billing_month):
        print(f"  already processed for {billing_month} — skipping")
        return

    period_start, period_end = billing_period(year, month)
    print(f"  period: {period_start.date()} → {period_end.date()}")

    calls = fetch_calls(agent_id, period_start, period_end)
    call_count = len(calls)
    total_ms = sum(c.get("duration_ms") or 0 for c in calls)
    total_seconds = total_ms // 1000
    total_minutes = math.ceil(total_ms / 60_000)
    included_minutes = sub.get("included_minutes") or 500
    overage_rate_cents = sub.get("overage_rate_cents") or 25
    overage_minutes = max(0, total_minutes - included_minutes)
    overage_amount_cents = overage_minutes * overage_rate_cents
    usage_percent = round((total_minutes / included_minutes * 100)) if included_minutes else 0
    has_overage = overage_minutes > 0

    result = {
        "call_count": call_count,
        "total_seconds": total_seconds,
        "total_minutes": total_minutes,
        "included_minutes": included_minutes,
        "overage_minutes": overage_minutes,
        "overage_rate_cents": overage_rate_cents,
        "overage_amount_cents": overage_amount_cents,
        "overage_amount_dollars": f"{overage_amount_cents / 100:.2f}",
        "usage_percent": usage_percent,
        "has_overage": has_overage,
    }

    print(f"  calls={call_count}  minutes={total_minutes}/{included_minutes} ({usage_percent}%)"
          + (f"  OVERAGE={overage_minutes}min ${overage_amount_cents/100:.2f}" if has_overage else ""))

    stripe_invoice_id = None
    if has_overage and not dry_run:
        try:
            invoice_id = stripe_create_invoice(
                sub["stripe_customer_id"],
                f"Overage — {billing_month}: {overage_minutes} min @ ${overage_rate_cents/100:.2f}/min",
            )
            stripe_add_line_item(
                invoice_id, overage_amount_cents,
                f"HVAC Standard overage — {billing_month}: {overage_minutes} min",
            )
            stripe_finalize_and_charge(invoice_id)
            stripe_invoice_id = invoice_id
            print(f"  Stripe invoice: {invoice_id}")
        except RuntimeError as e:
            print(f"  [ERROR] Stripe: {e}")

    if not dry_run:
        write_snapshot({
            "agent_id": agent_id,
            "billing_month": billing_month,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "call_count": call_count,
            "total_seconds": total_seconds,
            "total_minutes": total_minutes,
            "included_minutes": included_minutes,
            "overage_minutes": overage_minutes,
            "overage_amount_cents": overage_amount_cents,
            "stripe_invoice_id": stripe_invoice_id,
            "source": "retell_list_calls",
            "computed_at": datetime.now(timezone.utc).isoformat(),
        })
        print("  snapshot written")

    send_usage_email(sub, result, billing_month, dry_run)


def main() -> None:
    ap = argparse.ArgumentParser(description="Monthly billing: Retell → minutes → Stripe → Brevo")
    ap.add_argument("--month", help="Target month YYYY-MM (default: previous month)")
    ap.add_argument("--dry-run", action="store_true", help="Compute only — no writes, no email, no Stripe")
    args = ap.parse_args()

    if args.month:
        try:
            year, month = [int(x) for x in args.month.split("-")]
        except ValueError:
            sys.exit("--month must be YYYY-MM")
    else:
        now = datetime.now(timezone.utc)
        month = now.month - 1 if now.month > 1 else 12
        year = now.year if now.month > 1 else now.year - 1

    print(f"Monthly Minutes Calculator — {year}-{month:02d}  dry_run={args.dry_run}")

    subs = fetch_active_subscriptions()
    if not subs:
        print("No active subscriptions found.")
        return
    print(f"Found {len(subs)} active subscription(s)")

    for sub in subs:
        process_subscription(sub, year, month, args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
