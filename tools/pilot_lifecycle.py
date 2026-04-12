#!/usr/bin/env python3
"""
pilot_lifecycle.py — Daily Railway cron for Phase 0 pilot state transitions.

Runs once per day (00:00 UTC via Railway cron). Drives the 14-day free pilot
state machine end-to-end: engagement emails on day 3/7/12, convert-or-expire at
day 14, winback emails at day 16/30, and Retell agent pause on expiration.

State machine per row in client_subscriptions WHERE pilot_mode=true:

    Day  0  — pilot created by n8n onboarding (not this script)
    Day  3  — send pilot-day-3 email (first engagement report)
    Day  7  — send pilot-day-7 email + Setup Intent CTA (halfway)
    Day 12  — send pilot-day-12 email (48hr warning)
    Day 14  — terminal:
                 IF stripe setup intent succeeded -> convert_pilot_to_paid()
                 ELSE                              -> expire_pilot()
    Day 16  — if expired, send pilot-winback-16 email
    Day 30  — if expired, send pilot-winback-30 email

Idempotent: every email write is gated on pilot_email_sends. Safe to run
multiple times on the same day.

Usage:
    export SUPABASE_URL=https://hgheyqwnrcvwtgngqdnq.supabase.co
    export SUPABASE_SERVICE_KEY=$(python tools/fetch_vault.py "Supabase" service_role_key)
    export BREVO_API_KEY=$(python tools/fetch_vault.py "Brevo" api_key)
    export STRIPE_SECRET_KEY=$(python tools/fetch_vault.py "Stripe" secret_key_test)
    export RETELL_API_KEY=$(python tools/fetch_vault.py "Retell AI" api_key)
    python tools/pilot_lifecycle.py --dry-run
    python tools/pilot_lifecycle.py
    python tools/pilot_lifecycle.py --date 2026-04-20   # override "today" for compressed-time tests

Required env vars (fetch from syntharra_vault):
    SUPABASE_URL
    SUPABASE_SERVICE_KEY  — service_role JWT
    BREVO_API_KEY
    STRIPE_SECRET_KEY     — sk_test_... during Phase 0, sk_live_... after Stripe flip
    RETELL_API_KEY

Schedule: 0 0 * * *  python tools/pilot_lifecycle.py    (Railway cron, daily 00:00 UTC)

Related spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md § 6.6, § 7, § 8
Related schema: supabase/schema_LIVE.md — client_subscriptions, marketing_events, pilot_email_sends
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Optional


# --------------------------------------------------------------------------
# Constants — verify against docs/REFERENCE.md before go-live
# --------------------------------------------------------------------------

# Stripe HVAC Standard recurring price — $697/mo, USD, charge_automatically.
# Created 2026-04-11 in TEST MODE via tools/stripe_pilot_setup.py.
# Product: prod_UJb4pQDwyQ7lgW
# When Stripe live mode is unblocked, run stripe_pilot_setup.py with the live
# secret and replace this constant. Also vault the live price ID under
# service_name='Stripe', key_type='price_hvac_standard_live'.
STRIPE_HVAC_STANDARD_PRICE_ID = "price_1TKxruECS71NQsk8yspZnj2B"

# Brevo template IDs — populated by tools/upload_brevo_templates.py 2026-04-11.
# These IDs are stable across runs because the upload script is idempotent
# (find-by-name then return existing ID; otherwise POST new).
# Sender during upload was daniel@syntharra.com (only verified sender on the
# Syntharra Brevo account as of 2026-04-11). Per-template sender override is
# possible at send time via the body of POST /v3/smtp/email if needed.
BREVO_TEMPLATE_IDS: dict[str, int] = {
    "pilot-welcome":    7,
    "pilot-day-3":      4,
    "pilot-day-7":      5,
    "pilot-day-12":     3,
    "pilot-converted":  2,
    "pilot-card-added": 1,
    "pilot-expired":    6,
    "pilot-winback-16": 8,
    "pilot-winback-30": 9,
}

BRAND_SENDER = {"name": "Syntharra", "email": "daniel@syntharra.com"}
DASHBOARD_BASE = "https://syntharra.com/dashboard.html"
ADD_CARD_BASE = "https://syntharra.com/add-card"  # TODO: confirm against landing page once built


# --------------------------------------------------------------------------
# env / http
# --------------------------------------------------------------------------

def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def http_json(method: str, url: str, headers: dict, body=None, timeout: int = 60) -> tuple[int, dict]:
    """Low-level JSON HTTP helper. Body may be dict (-> JSON) or bytes (-> raw)."""
    if body is None:
        data = None
    elif isinstance(body, (bytes, bytearray)):
        data = bytes(body)
    else:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")[:500]}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp returned by Supabase REST."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


# --------------------------------------------------------------------------
# Supabase REST helpers
# --------------------------------------------------------------------------

def sb_headers() -> dict:
    k = env("SUPABASE_SERVICE_KEY")
    return {
        "apikey": k,
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json",
    }


def supabase_get(path: str) -> list[dict]:
    url = env("SUPABASE_URL").rstrip("/") + path
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        raise RuntimeError(f"supabase_get {path} -> {status} {data}")
    return data or []


def supabase_post(path: str, body: dict) -> dict:
    url = env("SUPABASE_URL").rstrip("/") + path
    headers = {**sb_headers(), "Prefer": "return=representation"}
    status, data = http_json("POST", url, headers, body)
    if status not in (200, 201):
        raise RuntimeError(f"supabase_post {path} -> {status} {data}")
    if isinstance(data, list) and data:
        return data[0]
    return data if isinstance(data, dict) else {}


def supabase_patch(path: str, body: dict) -> dict:
    url = env("SUPABASE_URL").rstrip("/") + path
    headers = {**sb_headers(), "Prefer": "return=representation"}
    status, data = http_json("PATCH", url, headers, body)
    if status not in (200, 204):
        raise RuntimeError(f"supabase_patch {path} -> {status} {data}")
    if isinstance(data, list) and data:
        return data[0]
    return data if isinstance(data, dict) else {}


# --------------------------------------------------------------------------
# Brevo (transactional email)
# --------------------------------------------------------------------------

def brevo_send(template_slug: str, to_email: str, params: dict) -> str:
    """Send a Brevo templated email. Returns the Brevo message ID (string) or ''."""
    template_id = BREVO_TEMPLATE_IDS.get(template_slug, 0)
    if not template_id:
        # TODO: template not yet uploaded — log and no-op so cron doesn't crash.
        print(f"  [WARN] Brevo template '{template_slug}' has no ID yet — skipping send")
        return ""
    payload = {
        "sender": BRAND_SENDER,
        "to": [{"email": to_email}],
        "templateId": template_id,
        "params": params,
    }
    status, data = http_json(
        "POST",
        "https://api.brevo.com/v3/smtp/email",
        {"api-key": env("BREVO_API_KEY"), "Content-Type": "application/json"},
        payload,
    )
    if status not in (200, 201, 202):
        print(f"  [WARN] Brevo send {template_slug} -> {status} {data}")
        return ""
    return str(data.get("messageId", ""))


# --------------------------------------------------------------------------
# Stripe (subscription creation)
# --------------------------------------------------------------------------

def stripe_call(method: str, path: str, body: Optional[dict] = None) -> dict:
    """Call Stripe REST API. Body is a flat dict — serialized as form-encoded.
    Stripe's REST API uses form-encoding for bodies, not JSON.
    """
    url = "https://api.stripe.com" + path
    headers = {
        "Authorization": f"Bearer {env('STRIPE_SECRET_KEY')}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    raw_body = None
    if body is not None:
        # Flatten nested dicts like items[0][price] per Stripe convention.
        pairs: list[tuple[str, str]] = []
        for k, v in body.items():
            if isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        for ik, iv in item.items():
                            pairs.append((f"{k}[{i}][{ik}]", str(iv)))
                    else:
                        pairs.append((f"{k}[{i}]", str(item)))
            else:
                pairs.append((k, str(v)))
        raw_body = urllib.parse.urlencode(pairs).encode("utf-8")
    status, data = http_json(method, url, headers, raw_body)
    if status not in (200, 201):
        raise RuntimeError(f"stripe_call {method} {path} -> {status} {data}")
    return data


# --------------------------------------------------------------------------
# Retell (agent pause via dynamic variable)
# --------------------------------------------------------------------------

def retell_call(method: str, path: str, body: Optional[dict] = None) -> dict:
    """Call Retell REST API. Retell uses JSON bodies with Bearer auth.
    Base URL is https://api.retellai.com; pass paths like '/update-agent/{id}'.
    """
    url = "https://api.retellai.com" + path
    headers = {
        "Authorization": f"Bearer {env('RETELL_API_KEY')}",
        "Content-Type": "application/json",
    }
    status, data = http_json(method, url, headers, body)
    if status not in (200, 201):
        raise RuntimeError(f"retell_call {method} {path} -> {status} {data}")
    return data


# --------------------------------------------------------------------------
# marketing_events emit
# --------------------------------------------------------------------------

def emit_marketing_event(event_type: str, props: dict) -> None:
    """Write a row to marketing_events. session_id is required in the schema —
    we fabricate a deterministic one based on the agent so lifecycle events
    chain together coherently.
    """
    client_agent_id = props.get("client_agent_id") or props.get("agent_id")
    session_id = f"pilot-lifecycle-{client_agent_id or 'unknown'}"
    row = {
        "session_id": session_id,
        "visitor_id": None,
        "client_agent_id": client_agent_id,
        "event_type": event_type,
        "asset_id": props.get("asset_id"),
        "utm_source": props.get("utm_source"),
        "utm_medium": props.get("utm_medium"),
        "utm_campaign": props.get("utm_campaign"),
        "utm_content": props.get("utm_content"),
        "utm_term": props.get("utm_term"),
        "referrer": None,
        "user_agent": "pilot_lifecycle.py",
        "ip_country": None,
        "ip_region": None,
        "metadata": {k: v for k, v in props.items() if k not in {
            "client_agent_id", "agent_id", "asset_id", "utm_source", "utm_medium",
            "utm_campaign", "utm_content", "utm_term",
        }},
    }
    try:
        headers = {**sb_headers(), "Prefer": "return=minimal"}
        url = env("SUPABASE_URL").rstrip("/") + "/rest/v1/marketing_events"
        status, _ = http_json("POST", url, headers, row)
        if status not in (200, 201, 204):
            print(f"  [WARN] marketing_events write failed: {status}")
    except Exception as exc:
        print(f"  [WARN] emit_marketing_event exc: {exc}")


# --------------------------------------------------------------------------
# Idempotency — pilot_email_sends
# --------------------------------------------------------------------------

def already_sent(client_agent_id: str, template_slug: str) -> bool:
    rows = supabase_get(
        "/rest/v1/pilot_email_sends"
        f"?client_agent_id=eq.{urllib.parse.quote(client_agent_id)}"
        f"&email_key=eq.{urllib.parse.quote(template_slug)}"
        "&select=id&limit=1"
    )
    return bool(rows)


def record_email_send(client_agent_id: str, template_slug: str, brevo_message_id: str, today: datetime) -> None:
    body = {
        "client_agent_id": client_agent_id,
        "email_key": template_slug,
        "brevo_message_id": brevo_message_id or None,
        "sent_at": today.isoformat(),
    }
    try:
        supabase_post("/rest/v1/pilot_email_sends", body)
    except RuntimeError as exc:
        # Unique-constraint violation = another run beat us here. That's fine.
        print(f"  [note] record_email_send: {exc}")


# --------------------------------------------------------------------------
# Pilot queries
# --------------------------------------------------------------------------

def query_active_pilots() -> list[dict]:
    """Fetch all pilot rows that are in the active 14-day window OR expired
    but still inside the 30-day winback cadence. We pull a broad set and
    filter per-row in process_pilot().

    Schema note (verified 2026-04-11 against live client_subscriptions):
    `owner_name`, `pilot_phone_number`, and `stripe_setup_intent_succeeded`
    are NOT columns on this table — those live on `hvac_standard_agent`
    (owner_name, agent_phone_number) or are derivable. Convert-trigger uses
    `payment_method_added_at IS NOT NULL` instead of stripe_setup_intent_succeeded.
    A future enhancement could embed `hvac_standard_agent(owner_name,agent_phone_number)`
    via PostgREST resource embedding once the FK relationship is declared.
    """
    return supabase_get(
        "/rest/v1/client_subscriptions"
        "?pilot_mode=eq.true"
        "&select=agent_id,company_name,client_email,"
        "pilot_started_at,pilot_ends_at,pilot_minutes_allotted,pilot_minutes_used,"
        "payment_method_added_at,status,stripe_customer_id,stripe_subscription_id,"
        "first_touch_asset_id,first_touch_utm"
    )


def _brevo_params_for(row: dict, days_remaining: Optional[int] = None) -> dict:
    """Common merge params used across all pilot templates.

    `owner_name` and `pilot_phone_number` are NOT on client_subscriptions
    (verified 2026-04-11 against live schema). They live on hvac_standard_agent.
    For now we fall back to safe defaults; Day 3 enhancement should fetch
    these via a per-pilot lookup against hvac_standard_agent (or embed via
    PostgREST resource embedding once FK is declared).
    """
    minutes_used = int(row.get("pilot_minutes_used") or 0)
    minutes_allotted = int(row.get("pilot_minutes_allotted") or 200)
    # TODO(day3): fetch owner_name + agent_phone_number from hvac_standard_agent
    # for the corresponding agent_id, instead of using these fallbacks.
    return {
        "first_name": "there",
        "company_name": row.get("company_name") or "",
        "minutes_used": minutes_used,
        "minutes_remaining": max(0, minutes_allotted - minutes_used),
        "minutes_allotted": minutes_allotted,
        "days_remaining": days_remaining if days_remaining is not None else 0,
        "add_card_url": ADD_CARD_BASE + f"?a={row.get('agent_id', '')}",
        "dashboard_url": DASHBOARD_BASE + f"?a={row.get('agent_id', '')}",
        "pilot_phone_number": "",
        # TODO: unsubscribe_url — Brevo auto-injects; confirm at upload time.
        "unsubscribe_url": "{{unsubscribe}}",
    }


# --------------------------------------------------------------------------
# Terminal transitions
# --------------------------------------------------------------------------

def convert_pilot_to_paid(row: dict, today: datetime, dry_run: bool) -> None:
    """Day-14, card on file -> create Stripe subscription, flip status to
    'active', send the pilot-converted email, emit marketing_event.
    """
    agent_id = row["agent_id"]
    customer_id = row.get("stripe_customer_id")
    payment_method_id: Optional[str] = None

    if not customer_id:
        raise RuntimeError(f"convert_pilot_to_paid: no stripe_customer_id for {agent_id}")

    print(f"  -> converting {agent_id} to paid")

    if dry_run:
        print("  [DRY-RUN] would create Stripe subscription and PATCH client_subscriptions")
        return

    # Look up the customer's default payment method (set by setup_intent.succeeded handler).
    cust = stripe_call("GET", f"/v1/customers/{customer_id}")
    default_pm = (cust.get("invoice_settings") or {}).get("default_payment_method")
    if isinstance(default_pm, dict):
        payment_method_id = default_pm.get("id")
    elif isinstance(default_pm, str):
        payment_method_id = default_pm

    sub_body: dict = {
        "customer": customer_id,
        "items": [{"price": STRIPE_HVAC_STANDARD_PRICE_ID}],
        "collection_method": "charge_automatically",
    }
    if payment_method_id:
        sub_body["default_payment_method"] = payment_method_id

    sub = stripe_call("POST", "/v1/subscriptions", sub_body)
    new_sub_id = sub.get("id", "")

    supabase_patch(
        f"/rest/v1/client_subscriptions?agent_id=eq.{urllib.parse.quote(agent_id)}",
        {
            "status": "active",
            "pilot_mode": False,
            "stripe_subscription_id": new_sub_id,
        },
    )

    emit_marketing_event("pilot_converted", {
        "client_agent_id": agent_id,
        "stripe_subscription_id": new_sub_id,
        "asset_id": row.get("first_touch_asset_id"),
    })

    msg_id = brevo_send("pilot-converted", row["client_email"], _brevo_params_for(row))
    record_email_send(agent_id, "pilot-converted", msg_id, today)
    print(f"  CONVERTED {agent_id} -> subscription {new_sub_id}")


def expire_pilot(row: dict, today: datetime, dry_run: bool) -> None:
    """Day-14, no card -> PATCH status='expired', pause Retell agent via
    dynamic variable, send pilot-expired email, emit marketing_event.
    """
    agent_id = row["agent_id"]
    print(f"  -> expiring {agent_id}")

    if dry_run:
        print("  [DRY-RUN] would PATCH status=expired, pause Retell agent, send pilot-expired")
        return

    supabase_patch(
        f"/rest/v1/client_subscriptions?agent_id=eq.{urllib.parse.quote(agent_id)}",
        {"status": "expired"},
    )

    # Retell pause: set a per-agent dynamic variable that the MASTER flow checks
    # at call start. NOTE: the exact Retell API shape for "agent-level dynamic
    # variables" varies by API version. The call below uses the documented
    # /update-agent/{id} PATCH endpoint (same endpoint used by tools/update_client_agent.py
    # and archived/testing-infra/workflows/agent-fix-approver.json).
    #
    # TODO: verify the exact key name against Retell docs at implementation time.
    # Candidates: `agent_level_dynamic_variables`, `dynamic_variables`,
    # or `response_engine.llm_dynamic_variables`. The spec § 6.5 says this is
    # implementation-level detail and lists a fallback (modify the flow route).
    try:
        retell_call("PATCH", f"/update-agent/{agent_id}", {
            "agent_level_dynamic_variables": {"pilot_expired": "true"},
        })
    except RuntimeError as exc:
        print(f"  [WARN] Retell pause failed — fallback path required: {exc}")

    emit_marketing_event("pilot_expired", {
        "client_agent_id": agent_id,
        "asset_id": row.get("first_touch_asset_id"),
    })

    msg_id = brevo_send("pilot-expired", row["client_email"], _brevo_params_for(row))
    record_email_send(agent_id, "pilot-expired", msg_id, today)
    print(f"  EXPIRED {agent_id}")


# --------------------------------------------------------------------------
# Per-pilot processing
# --------------------------------------------------------------------------

def process_pilot(row: dict, today: datetime, dry_run: bool = False) -> dict:
    """Evaluate one pilot row against `today` and fire the appropriate action.
    Returns a summary dict describing what was done (for tests and logging).
    """
    agent_id = row.get("agent_id", "<unknown>")
    started_str = row.get("pilot_started_at")
    if not started_str:
        print(f"[{agent_id}] no pilot_started_at — skipping")
        return {"agent_id": agent_id, "action": "skip_no_started_at"}

    started = parse_ts(started_str)
    days_in = (today - started).days
    status = row.get("status", "")

    print(f"[{agent_id}] {row.get('company_name', '')} day={days_in} status={status}")

    summary: dict = {"agent_id": agent_id, "day": days_in, "actions": []}

    # --- Day 3/7/12 engagement emails (only while status='pilot') ---
    engagement_map = [
        (3,  "pilot-day-3",  "pilot_day_3_sent"),
        (7,  "pilot-day-7",  "pilot_day_7_sent"),
        (12, "pilot-day-12", "pilot_day_12_sent"),
    ]
    if status == "pilot":
        for day, slug, event_name in engagement_map:
            if days_in == day and not already_sent(agent_id, slug):
                if dry_run:
                    print(f"  [DRY-RUN] would send {slug}")
                    summary["actions"].append(f"dry:{slug}")
                    continue
                params = _brevo_params_for(row, days_remaining=max(0, 14 - days_in))
                msg_id = brevo_send(slug, row["client_email"], params)
                record_email_send(agent_id, slug, msg_id, today)
                emit_marketing_event(event_name, {
                    "client_agent_id": agent_id,
                    "day": day,
                    "asset_id": row.get("first_touch_asset_id"),
                })
                summary["actions"].append(slug)
                print(f"  sent {slug}")

    # --- Day 14 terminal transition (convert OR expire) ---
    if status == "pilot" and days_in >= 14:
        # `payment_method_added_at` is set by the Stripe setup_intent.succeeded
        # webhook handler — that's the canonical "card is on file" signal.
        setup_ok = bool(row.get("payment_method_added_at"))
        if setup_ok:
            convert_pilot_to_paid(row, today, dry_run)
            summary["actions"].append("converted")
        else:
            expire_pilot(row, today, dry_run)
            summary["actions"].append("expired")
        return summary

    # --- Winback sequence for expired pilots ---
    if status == "expired":
        winback_map = [
            (16, "pilot-winback-16", "winback_day_16_sent"),
            (30, "pilot-winback-30", "winback_day_30_sent"),
        ]
        for day, slug, event_name in winback_map:
            if days_in == day and not already_sent(agent_id, slug):
                if dry_run:
                    print(f"  [DRY-RUN] would send {slug}")
                    summary["actions"].append(f"dry:{slug}")
                    continue
                params = _brevo_params_for(row)
                msg_id = brevo_send(slug, row["client_email"], params)
                record_email_send(agent_id, slug, msg_id, today)
                emit_marketing_event(event_name, {
                    "client_agent_id": agent_id,
                    "day": day,
                    "asset_id": row.get("first_touch_asset_id"),
                })
                summary["actions"].append(slug)
                print(f"  sent {slug}")

    if not summary["actions"]:
        summary["actions"].append("no-op")
    return summary


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 0 pilot daily lifecycle cron")
    ap.add_argument("--dry-run", action="store_true", help="Preview actions without sending or writing")
    ap.add_argument("--date", help="Override 'today' as YYYY-MM-DD (for compressed-time tests)")
    args = ap.parse_args()

    if args.date:
        try:
            today = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            sys.exit("--date must be YYYY-MM-DD")
    else:
        today = now_utc()

    print(f"pilot_lifecycle.py — today={today.date().isoformat()} dry_run={args.dry_run}")

    try:
        pilots = query_active_pilots()
    except RuntimeError as exc:
        sys.exit(f"fetch failed: {exc}")

    if not pilots:
        print("No pilot rows found.")
        return
    print(f"Found {len(pilots)} pilot row(s) to evaluate.")

    summaries: list[dict] = []
    for row in pilots:
        try:
            summaries.append(process_pilot(row, today, dry_run=args.dry_run))
        except Exception as exc:  # noqa: BLE001 — we want resilience across rows
            print(f"  [ERROR] {row.get('agent_id')}: {exc}", file=sys.stderr)
            summaries.append({"agent_id": row.get("agent_id"), "error": str(exc)})

    # Summary
    actions_count: dict[str, int] = {}
    for s in summaries:
        for a in s.get("actions", []):
            actions_count[a] = actions_count.get(a, 0) + 1
    print("\nSummary:")
    for k, v in sorted(actions_count.items()):
        print(f"  {k}: {v}")
    print("Done.")


if __name__ == "__main__":
    main()
