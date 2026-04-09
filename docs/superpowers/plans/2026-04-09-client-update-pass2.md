# Client-Update Form + Pass 2 + Go-Live Unblock

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship n8n client-update form, fix the broken Monthly Minutes Calculator (billing is currently dead), wire the MASTER agent webhook so lead/emergency notifications actually fire, and clean up stale Premium workflows — all required for go-live.

**Architecture:**
- Monthly Minutes Calculator: Python script (`tools/monthly_minutes.py`) replaces broken n8n workflow. Reuses `fetch_calls()` pattern from `weekly_client_report.py`. Scheduled via `CronCreate`.
- MASTER webhook: Single Retell PATCH call. Pre-authorized one-time override per FAILURES.md 2026-04-09 (pre-launch, no live clients).
- n8n client-update form: Python builder script (`tools/build_client_update_workflow.py`) → POST to Railway n8n REST API. Copies `Build Retell Prompt` JS from live onboarding workflow at build time.
- Premium archive: Direct n8n REST API calls (deactivate + rename).

**Tech Stack:** Python stdlib, Retell API v2, Railway n8n REST API (`X-N8N-API-KEY`), Supabase REST, Stripe API, Brevo API v3.

**Go-live blockers this plan resolves:**
- MASTER has `post_call_webhook_url: null` → Call Processor never fires (Task 2)
- Monthly Minutes Calculator pulls from dropped `hvac_call_log` tables → billing is broken (Task 3)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `docs/REFERENCE.md` | Modify | Fix stale MASTER entry (still shows "legacy subagent" post-promotion) |
| `tools/monthly_minutes.py` | **Create** | Monthly billing: Retell list-calls → minutes → Stripe overage → Brevo email |
| `tools/build_client_update_workflow.py` | **Create** | Builder: creates n8n Form Trigger client-update workflow via Railway REST API |

---

## Credentials reference (all from `syntharra_vault`)

| Service | key_type | env var to export |
|---|---|---|
| n8n Railway | api_key | `N8N_API_KEY` |
| Retell AI | api_key | `RETELL_API_KEY` |
| Supabase | service_role_key | `SUPABASE_SERVICE_KEY` |
| Supabase | project_url | `SUPABASE_URL` (prefix with `https://`) |
| Brevo | api_key | `BREVO_API_KEY` |
| Stripe | secret_key_test | `STRIPE_SECRET_KEY` |

Fetch all six from vault before starting:
```bash
# Run this once at session start, fill in values from syntharra_vault
export N8N_API_KEY=""
export RETELL_API_KEY="key_0157d9401f66cfa1b51fadc66445"
export SUPABASE_SERVICE_KEY=""
export SUPABASE_URL="https://hgheyqwnrcvwtgngqdnq.supabase.co"
export BREVO_API_KEY=""
export STRIPE_SECRET_KEY=""
```

---

## Task 1: Fix REFERENCE.md — remove stale MASTER labels (5 min)

**Files:** Modify `docs/REFERENCE.md`

The MASTER agent `agent_4afbfdb3fcb1ba9569353af28d` was promoted to the modern code-node arch on 2026-04-09 (per STATE.md + TASKS.md completed section). REFERENCE.md still shows it as "legacy — stale". Fix both the Agent Registry and Conversation Flow Registry tables.

- [ ] **Step 1: Edit Agent Registry table in `docs/REFERENCE.md`**

Change:
```
| HVAC Standard MASTER (legacy — stale) | `agent_4afbfdb3fcb1ba9569353af28d` | ⚠️ Legacy `subagent` architecture. Last promoted 2026-04-06 (v22). Will be replaced wholesale by TESTING on next promotion. Do not use as clone source. |
```
To:
```
| **HVAC Standard MASTER (current, code-node arch)** | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ Promoted 2026-04-09 from TESTING. Modern code-node architecture, 19 nodes. Flow `conversation_flow_34d169608460`. Use as clone source for Standard clients. |
```

- [ ] **Step 2: Edit Conversation Flow Registry table**

Change:
```
| HVAC Standard MASTER (legacy) | `conversation_flow_34d169608460` | Legacy Standard MASTER — subagent architecture, to be replaced |
```
To:
```
| **HVAC Standard MASTER (current)** | `conversation_flow_34d169608460` | Promoted 2026-04-09. Code-node architecture, byte-identical to TESTING snapshot. |
```

- [ ] **Step 3: Commit**
```bash
git add docs/REFERENCE.md
git commit -m "docs(reference): update MASTER as current code-node arch post-2026-04-09 promotion"
```

---

## Task 2: Wire MASTER agent webhook → Call Processor (5 min, go-live blocker)

**Files:** No file changes — one Retell API PATCH.

Current state: `agent_4afbfdb3fcb1ba9569353af28d` has `post_call_webhook_url: null`. The Call Processor (`Kg576YtPM9yEacKn`) is live but never receives events. This means zero lead notifications, zero emergency alerts for any live client.

Target: `post_call_webhook_url = "https://n8n.syntharra.com/webhook/retell-hvac-webhook"` (the Call Processor's verified webhook path).

One-time RULES.md §1 override: pre-authorized per FAILURES.md 2026-04-09 row "Pass 2 one-time override". Pre-launch, no live clients.

- [ ] **Step 1: PATCH the MASTER agent**
```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/agent_4afbfdb3fcb1ba9569353af28d" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"post_call_webhook_url": "https://n8n.syntharra.com/webhook/retell-hvac-webhook"}' \
  | python -c "import json,sys; d=json.load(sys.stdin); print('webhook:', d.get('post_call_webhook_url','ERROR'))"
```

Expected output:
```
webhook: https://n8n.syntharra.com/webhook/retell-hvac-webhook
```

- [ ] **Step 2: Verify — GET agent and confirm field is set**
```bash
curl -s "https://api.retellai.com/get-agent/agent_4afbfdb3fcb1ba9569353af28d" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | python -c "import json,sys; d=json.load(sys.stdin); print('webhook:', d.get('post_call_webhook_url'))"
```
Expected: `webhook: https://n8n.syntharra.com/webhook/retell-hvac-webhook`

- [ ] **Step 3: Commit note to STATE.md**

Add under "What's live in production":
```markdown
- **MASTER agent webhook wired** — `post_call_webhook_url` set to `https://n8n.syntharra.com/webhook/retell-hvac-webhook` (Call Processor `Kg576YtPM9yEacKn`). Done 2026-04-09 Pass 2, one-time override.
```

```bash
git add docs/STATE.md
git commit -m "fix(retell): wire MASTER agent webhook to Call Processor"
```

---

## Task 3: Monthly Minutes Calculator → `tools/monthly_minutes.py`

**Files:**
- Create: `tools/monthly_minutes.py`

The existing n8n workflow `z1DNTjvTDAkExsX8` queries `hvac_call_log` tables that were dropped 2026-04-09. Billing is currently dead. This Python script replaces it: queries Retell `list-calls` directly for all active subscriptions.

Billing model (from existing workflow):
- `included_minutes` and `overage_rate_cents` come from `client_subscriptions` row
- Minutes = `ceil(total_duration_ms / 60_000)`
- Overage = `max(0, total_minutes - included_minutes) * overage_rate_cents` (cents)
- Write `monthly_billing_snapshot` row (idempotent — unique on `agent_id + billing_month`)
- If overage > 0: Stripe invoice → line item → finalize
- Send Brevo usage report email to `client_email`

- [ ] **Step 1: Create `tools/monthly_minutes.py`**

```python
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
```

- [ ] **Step 2: Dry-run against 2026-03 (no writes)**
```bash
cd "c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations"
python tools/monthly_minutes.py --month 2026-03 --dry-run
```

Expected output (will vary):
```
Monthly Minutes Calculator — 2026-03  dry_run=True
Found N active subscription(s)

--- <company> (<agent_id>) ---
  period: 2026-03-01 → 2026-03-31
  calls=N  minutes=N/500 (N%)
  [DRY-RUN] would send usage email to ...
```

If `No active subscriptions found.` — that's expected pre-launch (no real clients yet). The script is correct.

- [ ] **Step 3: Deactivate the broken n8n workflow**
```bash
curl -s -X POST \
  "https://n8n.syntharra.com/api/v1/workflows/z1DNTjvTDAkExsX8/deactivate" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" | python -c "import json,sys; d=json.load(sys.stdin); print('active:', d.get('active'))"
```
Expected: `active: False`

Then rename it via PUT (get + modify name + PUT back):
```bash
# Get current workflow
curl -s "https://n8n.syntharra.com/api/v1/workflows/z1DNTjvTDAkExsX8" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" > /tmp/mmcalc.json

# Rename + PUT back
python -c "
import json
with open('/tmp/mmcalc.json') as f:
    d = json.load(f)
d['name'] = '[ARCHIVED-2026-04-09] Monthly Minutes Calculator & Overage Billing'
payload = {k: d[k] for k in ('name','nodes','connections','settings') if k in d}
import urllib.request, os
req = urllib.request.Request(
    'https://n8n.syntharra.com/api/v1/workflows/z1DNTjvTDAkExsX8',
    data=json.dumps(payload).encode(),
    headers={'X-N8N-API-KEY': os.environ['N8N_API_KEY'], 'Content-Type': 'application/json'},
    method='PUT'
)
with urllib.request.urlopen(req) as r:
    print('renamed:', json.load(r)['name'])
"
```
Expected: `renamed: [ARCHIVED-2026-04-09] Monthly Minutes Calculator & Overage Billing`

- [ ] **Step 4: Schedule with CronCreate (1st of month, 8:10 AM UTC — 10 min after old n8n trigger)**

```
/schedule monthly_minutes 10 8 1 * * "cd /path && python tools/monthly_minutes.py"
```

Or via CronCreate tool with:
- Schedule: `10 8 1 * *` (1st of month, 08:10 UTC)
- Command: `cd "c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations" && SUPABASE_URL=... SUPABASE_SERVICE_KEY=... RETELL_API_KEY=... STRIPE_SECRET_KEY=... BREVO_API_KEY=... python tools/monthly_minutes.py`

Note: Credentials need to be present at cron runtime. Options: (a) `.env` file sourced by cron, or (b) set as system env vars. Do not hardcode.

- [ ] **Step 5: Commit**
```bash
git add tools/monthly_minutes.py docs/STATE.md
git commit -m "feat(billing): monthly_minutes.py replaces broken n8n workflow — pulls from Retell list-calls"
```

---

## Task 4: Build n8n client-update form workflow

**Files:**
- Create: `tools/build_client_update_workflow.py`

Builds + POSTs a new n8n workflow to Railway. The workflow has an n8n Form Trigger so Dan can update a client agent from a browser (no CLI needed). Uses the same Build Retell Prompt JS code copied from the live onboarding workflow at build time.

Form fields: Agent ID (text, required) · Field to Update (dropdown of EDITABLE_FIELDS) · New Value (text, required) · Mode (Apply / Preview Only).

Workflow nodes:
1. Form Trigger → receives agent_id, field, new_value, mode
2. Supabase: Fetch row → `GET /rest/v1/hvac_standard_agent?agent_id=eq.{{formData.agentId}}`
3. Code: Apply update — merge new_value into field on the row
4. Code: Build Retell Prompt — full JS copy from onboarding workflow (fetched at build time)
5. HTTP: PATCH Retell flow — `PATCH /update-conversation-flow/{flow_id}`
6. HTTP: Publish agent — `POST /publish-agent/{agent_id}` (skipped in preview mode)
7. HTTP: Update Supabase row — `PATCH /rest/v1/hvac_standard_agent?agent_id=eq.{agent_id}`
8. Respond to Webhook — shows result (or preview diff)

- [ ] **Step 1: Create `tools/build_client_update_workflow.py`**

```python
#!/usr/bin/env python3
"""
build_client_update_workflow.py — Create (or replace) the n8n client-update form workflow.

Run once to create. Re-run to replace (uses fixed workflow ID if env var N8N_CLIENT_UPDATE_ID set,
otherwise creates new and prints the ID for REFERENCE.md).

Required env vars:
  N8N_API_KEY            — from syntharra_vault
  SUPABASE_SERVICE_KEY   — from syntharra_vault
  SUPABASE_URL           — https://hgheyqwnrcvwtgngqdnq.supabase.co
  RETELL_API_KEY         — from syntharra_vault

Optional:
  N8N_CLIENT_UPDATE_ID   — if set, PUT (update) that workflow ID instead of POST (create new)
"""
import json, os, sys, uuid, urllib.request, urllib.error

N8N_BASE = "https://n8n.syntharra.com/api/v1"
ONBOARDING_WF_ID = "4Hx7aRdzMl5N0uJP"  # source of Build Retell Prompt JS

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://hgheyqwnrcvwtgngqdnq.supabase.co").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
RETELL_KEY   = os.environ.get("RETELL_API_KEY", "")
N8N_KEY      = os.environ.get("N8N_API_KEY", "")

for name, val in [("N8N_API_KEY", N8N_KEY), ("SUPABASE_SERVICE_KEY", SUPABASE_KEY), ("RETELL_API_KEY", RETELL_KEY)]:
    if not val:
        sys.exit(f"Missing env var: {name}")


def n8n_get(path: str) -> dict:
    req = urllib.request.Request(f"{N8N_BASE}{path}", headers={"X-N8N-API-KEY": N8N_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def n8n_post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{N8N_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def n8n_put(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{N8N_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_build_retell_prompt_js() -> str:
    """Copy Build Retell Prompt JS from the live onboarding workflow."""
    wf = n8n_get(f"/workflows/{ONBOARDING_WF_ID}")
    for node in wf.get("nodes", []):
        if node.get("name") == "Build Retell Prompt":
            js = node.get("parameters", {}).get("jsCode", "")
            if js:
                print(f"  Fetched Build Retell Prompt JS ({len(js):,} chars)")
                return js
    sys.exit("Could not find 'Build Retell Prompt' node in onboarding workflow")


def nid() -> str:
    return str(uuid.uuid4())


EDITABLE_FIELDS = [
    "company_name", "company_tagline", "owner_name", "website", "years_in_business",
    "certifications", "licensed_insured", "services_offered", "brands_serviced",
    "service_area", "service_area_radius", "do_not_service", "business_hours",
    "response_time", "after_hours_behavior", "after_hours_transfer", "emergency_service",
    "emergency_phone", "pricing_policy", "diagnostic_fee", "standard_fees",
    "free_estimates", "financing_available", "financing_details", "warranty",
    "warranty_details", "maintenance_plans", "membership_program", "payment_methods",
    "lead_contact_method", "lead_phone", "lead_email", "transfer_phone",
    "transfer_triggers", "transfer_behavior", "current_promotion", "seasonal_services",
    "unique_selling_points", "google_review_rating", "google_review_count",
    "company_phone", "custom_greeting", "additional_info",
]


def build_workflow(build_retell_js: str) -> dict:
    # ---- Node IDs (fixed so workflow is re-runnable without creating duplicate URLs)
    ID_FORM    = "form-trigger-client-update-v1"
    ID_FETCH   = "sb-fetch-row-v1"
    ID_APPLY   = "apply-field-update-v1"
    ID_COMPILE = "build-retell-prompt-v1"
    ID_PATCH   = "retell-patch-flow-v1"
    ID_PUBLISH = "retell-publish-v1"
    ID_UPDATE  = "sb-update-row-v1"
    ID_RESPOND = "form-respond-v1"

    field_options = [{"option": f} for f in EDITABLE_FIELDS]

    nodes = [
        # 1 — Form Trigger
        {
            "id": ID_FORM,
            "name": "Client Update Form",
            "type": "n8n-nodes-base.formTrigger",
            "typeVersion": 2,
            "position": [240, 400],
            "parameters": {
                "formTitle": "Update Client Agent",
                "formDescription": "Update HVAC Standard agent settings. Changes are applied live immediately (unless Preview mode selected).",
                "path": "client-update",
                "responseMode": "lastNode",
                "formFields": {
                    "values": [
                        {
                            "fieldLabel": "Agent ID",
                            "fieldType": "text",
                            "placeholder": "agent_xxxxxxxxxxxxxxxxxxxxxxxx",
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "Field to Update",
                            "fieldType": "dropdown",
                            "fieldOptions": {"values": field_options},
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "New Value",
                            "fieldType": "textarea",
                            "placeholder": "Enter the new value",
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "Mode",
                            "fieldType": "dropdown",
                            "fieldOptions": {"values": [
                                {"option": "Apply — write changes live"},
                                {"option": "Preview — show diff only, no writes"},
                            ]},
                            "requiredField": True,
                        },
                    ]
                },
            },
        },

        # 2 — Supabase: fetch current row
        {
            "id": ID_FETCH,
            "name": "Supabase: Fetch Agent Row",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [460, 400],
            "parameters": {
                "method": "GET",
                "url": f"={SUPABASE_URL}/rest/v1/hvac_standard_agent",
                "sendQuery": True,
                "queryParameters": {"parameters": [
                    {"name": "agent_id", "value": "=eq.{{ $json['Agent ID'] }}"},
                    {"name": "select", "value": "*"},
                ]},
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                ]},
                "options": {},
            },
        },

        # 3 — Code: apply the field update in memory
        {
            "id": ID_APPLY,
            "name": "Apply Field Update",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 400],
            "parameters": {
                "jsCode": """
const formData = $('Client Update Form').first().json;
const rows = $input.first().json;
const rowArray = Array.isArray(rows) ? rows : [rows];
if (!rowArray.length) throw new Error('No hvac_standard_agent row found for agent_id: ' + formData['Agent ID']);
const row = rowArray[0];
const field = formData['Field to Update'];
const newValue = formData['New Value'];
const mode = formData['Mode'] || '';
const isDryRun = mode.startsWith('Preview');
const oldValue = row[field];
const updatedRow = { ...row, [field]: newValue };
return [{ json: { row: updatedRow, field, newValue, oldValue, agentId: row.agent_id, flowId: row.conversation_flow_id, isDryRun } }];
""".strip(),
            },
        },

        # 4 — Code: Build Retell Prompt (full JS copy from onboarding workflow)
        {
            "id": ID_COMPILE,
            "name": "Build Retell Prompt",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 400],
            "parameters": {
                "jsCode": build_retell_js,
            },
        },

        # 5 — HTTP: PATCH Retell conversation flow
        {
            "id": ID_PATCH,
            "name": "Retell: PATCH Flow",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1120, 300],
            "parameters": {
                "method": "PATCH",
                "url": "={{ 'https://api.retellai.com/update-conversation-flow/' + $('Apply Field Update').first().json.flowId }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {RETELL_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify($json.conversationFlow) }}",
                "options": {"response": {"response": {"responseFormat": "json"}}},
            },
        },

        # 6 — HTTP: Publish agent
        {
            "id": ID_PUBLISH,
            "name": "Retell: Publish Agent",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1340, 300],
            "parameters": {
                "method": "POST",
                "url": "={{ 'https://api.retellai.com/publish-agent/' + $('Apply Field Update').first().json.agentId }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {RETELL_KEY}"},
                ]},
                "options": {"response": {"response": {"responseFormat": "text"}}},
            },
        },

        # 7 — HTTP: Update Supabase row
        {
            "id": ID_UPDATE,
            "name": "Supabase: Update Row",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1560, 300],
            "parameters": {
                "method": "PATCH",
                "url": f"={SUPABASE_URL}/rest/v1/hvac_standard_agent",
                "sendQuery": True,
                "queryParameters": {"parameters": [
                    {"name": "agent_id", "value": "={{ 'eq.' + $('Apply Field Update').first().json.agentId }}"},
                ]},
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"},
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ [$('Apply Field Update').first().json.field]: $('Apply Field Update').first().json.newValue }) }}",
                "options": {},
            },
        },

        # 8 — Form response
        {
            "id": ID_RESPOND,
            "name": "Respond to Form",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1780, 300],
            "parameters": {
                "respondWith": "text",
                "responseBody": "={{ $('Apply Field Update').first().json.isDryRun ? 'PREVIEW ONLY — No changes made.\\nField: ' + $('Apply Field Update').first().json.field + '\\nOld: ' + $('Apply Field Update').first().json.oldValue + '\\nNew: ' + $('Apply Field Update').first().json.newValue : 'Done. Updated ' + $('Apply Field Update').first().json.field + ' on ' + $('Apply Field Update').first().json.agentId }}",
            },
        },
    ]

    # Connections: Form → Fetch → Apply → Compile → Patch → Publish → Update → Respond
    connections = {
        "Client Update Form":        {"main": [[{"node": "Supabase: Fetch Agent Row",  "type": "main", "index": 0}]]},
        "Supabase: Fetch Agent Row":  {"main": [[{"node": "Apply Field Update",         "type": "main", "index": 0}]]},
        "Apply Field Update":         {"main": [[{"node": "Build Retell Prompt",        "type": "main", "index": 0}]]},
        "Build Retell Prompt":        {"main": [[{"node": "Retell: PATCH Flow",         "type": "main", "index": 0}]]},
        "Retell: PATCH Flow":         {"main": [[{"node": "Retell: Publish Agent",      "type": "main", "index": 0}]]},
        "Retell: Publish Agent":      {"main": [[{"node": "Supabase: Update Row",       "type": "main", "index": 0}]]},
        "Supabase: Update Row":       {"main": [[{"node": "Respond to Form",            "type": "main", "index": 0}]]},
    }

    return {
        "name": "Client Agent Update Form",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
        "active": True,
    }


def main() -> None:
    print("Fetching Build Retell Prompt JS from onboarding workflow...")
    build_js = fetch_build_retell_prompt_js()

    print("Building workflow JSON...")
    wf = build_workflow(build_js)

    existing_id = os.environ.get("N8N_CLIENT_UPDATE_ID")
    if existing_id:
        print(f"Updating existing workflow {existing_id}...")
        payload = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
        result = n8n_put(f"/workflows/{existing_id}", payload)
        wf_id = result["id"]
        print(f"Updated: {wf_id}")
    else:
        print("Creating new workflow...")
        result = n8n_post("/workflows", wf)
        wf_id = result["id"]
        print(f"Created: {wf_id}")
        print(f"\nAdd to REFERENCE.md:")
        print(f"  Client Update Form: `{wf_id}` — https://n8n.syntharra.com/form/client-update")

    # Activate
    try:
        req = urllib.request.Request(
            f"{N8N_BASE}/workflows/{wf_id}/activate",
            headers={"X-N8N-API-KEY": N8N_KEY},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
            print(f"Active: {d.get('active')}")
    except Exception as e:
        print(f"[WARN] activate failed (may already be active): {e}")

    print(f"\nForm URL: https://n8n.syntharra.com/form/client-update")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the builder**
```bash
cd "c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations"
python tools/build_client_update_workflow.py
```

Expected output:
```
Fetching Build Retell Prompt JS from onboarding workflow...
  Fetched Build Retell Prompt JS (53,930 chars)
Building workflow JSON...
Creating new workflow...
Created: <wf_id>
Add to REFERENCE.md:
  Client Update Form: `<wf_id>` — https://n8n.syntharra.com/form/client-update
Active: True

Form URL: https://n8n.syntharra.com/form/client-update
```

- [ ] **Step 3: Smoke test the form in Preview mode**

Open `https://n8n.syntharra.com/form/client-update` in browser.
- Agent ID: `agent_6e7a2ae03c2fbd7a251fafcd00` (TESTING — safe)
- Field: `current_promotion`
- New Value: `TEST preview $1 off`
- Mode: `Preview — show diff only, no writes`

Expected response: `PREVIEW ONLY — No changes made.\nField: current_promotion\nOld: <current value>\nNew: TEST preview $1 off`

- [ ] **Step 4: Add workflow ID to REFERENCE.md**

Add new row to n8n Workflows section:
```markdown
| Client Agent Update Form | `<wf_id from output>` | Form: https://n8n.syntharra.com/form/client-update |
```

- [ ] **Step 5: Commit**
```bash
git add tools/build_client_update_workflow.py docs/REFERENCE.md
git commit -m "feat(tools): n8n client-update form workflow builder"
```

---

## Task 5: Archive 6 stale Premium n8n workflows

**Files:** None (API-only)

These 6 workflows were identified in the 2026-04-09 audit as "ARCHIVE (Premium retired)" but were not archived in that session (the hard-delete incident interrupted). Archive = deactivate + rename with `[ARCHIVED-2026-04-09]` prefix + ask Dan to click UI Archive button.

Workflows to archive:
| ID | Name |
|---|---|
| `rGrnCr5mPFP2TIc7` | Premium Dispatcher — Google Calendar *(restored from backup — different ID now: `tp62gP2ntiqVvWZ7`)* |
| `La99yvfmWg6AuvM2` | Premium Dispatcher — Outlook |
| `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher |
| `5vphecmEhxnwFz2X` | Premium — Daily Token Refresh |
| `a0IAwwUJP4YgwgjG` | Premium — Integration Connected Handler |
| `kz1VmwNccunRMEaF` | HVAC Prem Onboarding (already inactive) |

- [ ] **Step 1: Deactivate + rename all 6**
```bash
python -c "
import json, os, urllib.request

N8N_BASE = 'https://n8n.syntharra.com/api/v1'
N8N_KEY = os.environ['N8N_API_KEY']
headers = {'X-N8N-API-KEY': N8N_KEY, 'Content-Type': 'application/json'}

# NOTE: rGrnCr5mPFP2TIc7 was hard-deleted and restored as tp62gP2ntiqVvWZ7 (per STATE.md)
WORKFLOWS = [
    'tp62gP2ntiqVvWZ7',
    'La99yvfmWg6AuvM2',
    '73Y0MHVBu05bIm5p',
    '5vphecmEhxnwFz2X',
    'a0IAwwUJP4YgwgjG',
    'kz1VmwNccunRMEaF',
]

for wf_id in WORKFLOWS:
    # Deactivate
    req = urllib.request.Request(f'{N8N_BASE}/workflows/{wf_id}/deactivate',
        headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        pass  # may already be inactive

    # Fetch + rename
    req = urllib.request.Request(f'{N8N_BASE}/workflows/{wf_id}', headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
    except:
        print(f'  SKIP {wf_id} (not found)')
        continue

    old_name = d['name']
    if old_name.startswith('[ARCHIVED'):
        print(f'  already archived: {old_name}')
        continue

    new_name = f'[ARCHIVED-2026-04-09] {old_name}'
    payload = {k: d[k] for k in ('name','nodes','connections','settings') if k in d}
    payload['name'] = new_name

    req = urllib.request.Request(f'{N8N_BASE}/workflows/{wf_id}',
        data=json.dumps(payload).encode(), headers=headers, method='PUT')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f'  archived: {json.load(r)[\"name\"]}')
    except Exception as e:
        print(f'  ERROR {wf_id}: {e}')
"
```

Expected output: 6 lines like `archived: [ARCHIVED-2026-04-09] Premium Dispatcher — ...`

- [ ] **Step 2: Ask Dan to click UI Archive button on all 6**

Post in `#ops-alerts`:
> "6 Premium workflows renamed [ARCHIVED-2026-04-09] and deactivated. Can you open n8n → Workflows, filter by `[ARCHIVED-2026-04-09]`, and click the Archive button on each? The public API can't set `isArchived:true` directly."

- [ ] **Step 3: Commit audit note**
```bash
git add docs/STATE.md  # add note: "6 Premium workflows deactivated + renamed 2026-04-09 Pass 2"
git commit -m "chore(n8n): archive 6 stale Premium workflows"
```

---

## Task 6: Smoke test `update_client_agent.py` CLI (TASKS.md P0)

This is a TASKS.md P0 item that was merged but never smoke-tested against a real agent.

- [ ] **Step 1: Dry-run against TESTING agent**
```bash
python tools/update_client_agent.py \
  --agent_id agent_6e7a2ae03c2fbd7a251fafcd00 \
  --set current_promotion="TEST smoke $1 off" \
  --dry-run
```

Expected: shows diff, prints undo command, no writes made.

- [ ] **Step 2: Live run + revert**
```bash
# Apply
python tools/update_client_agent.py \
  --agent_id agent_6e7a2ae03c2fbd7a251fafcd00 \
  --set current_promotion="TEST smoke $1 off" \
  --yes

# Copy the printed undo command, then immediately run it to revert
```

Expected: `Done. To undo: python tools/update_client_agent.py ...`

- [ ] **Step 3: Verify revert applied**
```bash
python tools/update_client_agent.py \
  --agent_id agent_6e7a2ae03c2fbd7a251fafcd00 \
  --set current_promotion="TEST smoke $1 off" \
  --dry-run
```
Expected: `global_prompt unchanged` (or 0 changed lines if the revert worked).

- [ ] **Step 4: Mark P0 task done in TASKS.md**

Move the update_client_agent smoke test item to Completed section in `docs/TASKS.md`.

```bash
git add docs/TASKS.md
git commit -m "chore(tasks): smoke test update_client_agent.py — PASSED"
```

---

## Go-Live Blockers Remaining (after this plan)

After this plan is complete, the remaining blockers for first live client are:

| Blocker | Owner | Status |
|---|---|---|
| Stripe live mode (live key in vault, live price active) | Dan | Pending Dan's timeline |
| Telnyx SMS (replace stub in Call Processor) | Dan / external | Waiting on Telnyx AI approval |
| Test call on MASTER `+18129944371` | Dan | Manual — call the number, verify Call Processor fires |
| Jotform Standard onboarding end-to-end smoke test | Dan + Claude | Not yet run post-arch-swap |

The **test call** is cheap and should happen immediately after Task 2 (webhook wired) to confirm the Call Processor fan-out actually fires end-to-end on the new code-node MASTER.
