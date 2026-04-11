#!/usr/bin/env python3
"""
test_e2e_pilot.py — Programmatic end-to-end test for the onboarding funnel.

Replaces manual Jotform clicks for Days 3-4 tasks 16/17: forges a
Jotform-shaped payload straight at the n8n onboarding webhook, then polls
Supabase for the resulting client_subscriptions row and asserts the correct
state.

Runs two variants:
    1. PAID  — pilot_mode=false, asserts status='active', pilot_mode=false
    2. PILOT — pilot_mode=true + UTM/asset params, asserts status='pilot',
               pilot_mode=true, pilot_ends_at ≈ now+14d, first_touch_asset_id
               is persisted

Each variant can cleanup the created rows (DELETE client_subscriptions + DELETE
the Retell agent) so tests don't leave residue.

Usage:
    export SUPABASE_URL=$(python tools/fetch_vault.py "Supabase" url)  # or from .env.local
    export SUPABASE_SERVICE_KEY=$(python tools/fetch_vault.py "Supabase" service_role_key)
    export RETELL_API_KEY=$(python tools/fetch_vault.py "Retell AI" api_key)
    export N8N_API_KEY=$(python tools/fetch_vault.py "n8n Railway" api_key)

    python tools/test_e2e_pilot.py --both              # run paid + pilot, cleanup after
    python tools/test_e2e_pilot.py --pilot             # just pilot variant
    python tools/test_e2e_pilot.py --paid              # just paid variant
    python tools/test_e2e_pilot.py --pilot --no-cleanup

Required env vars (from syntharra_vault via tools/fetch_vault.py):
    SUPABASE_URL
    SUPABASE_SERVICE_KEY
    RETELL_API_KEY
    N8N_API_KEY              — for looking up the webhook path once

The onboarding n8n workflow ID is hardcoded (it is the canonical ID in
docs/REFERENCE.md; verify before running): 4Hx7aRdzMl5N0uJP.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone


N8N_BASE = "https://n8n.syntharra.com"
ONBOARDING_WORKFLOW_ID = "4Hx7aRdzMl5N0uJP"  # TODO: confirm against docs/REFERENCE.md
POLL_INTERVAL_SEC = 3
POLL_MAX_ATTEMPTS = 30  # 90s


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def http_json(method: str, url: str, headers: dict, body=None, timeout: int = 60) -> tuple[int, dict]:
    data = None
    if body is not None and not isinstance(body, (bytes, bytearray)):
        data = json.dumps(body).encode("utf-8")
    elif body is not None:
        data = bytes(body)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")[:500]}


# --------------------------------------------------------------------------
# n8n webhook-path discovery
# --------------------------------------------------------------------------

def fetch_webhook_url() -> str:
    """Pull the onboarding workflow JSON and locate the Webhook trigger path."""
    status, data = http_json(
        "GET",
        f"{N8N_BASE}/api/v1/workflows/{ONBOARDING_WORKFLOW_ID}",
        {"X-N8N-API-KEY": env("N8N_API_KEY"), "accept": "application/json"},
    )
    if status != 200:
        sys.exit(f"n8n GET workflow failed: {status} {data}")

    nodes = (data.get("nodes") or [])
    for n in nodes:
        if n.get("type") in ("n8n-nodes-base.webhook", "n8n-nodes-base.webhookTrigger"):
            path = (n.get("parameters") or {}).get("path")
            if path:
                return f"{N8N_BASE}/webhook/{path}"

    sys.exit("No Webhook node with a path found in the onboarding workflow")


# --------------------------------------------------------------------------
# Supabase helpers
# --------------------------------------------------------------------------

def sb_headers() -> dict:
    k = env("SUPABASE_SERVICE_KEY")
    return {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}


def fetch_subscription(company_name: str) -> dict | None:
    url = (env("SUPABASE_URL").rstrip("/") +
           "/rest/v1/client_subscriptions"
           f"?company_name=eq.{urllib.parse.quote(company_name)}"
           "&select=*&limit=1")
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        return None
    return data[0] if data else None


def delete_subscription(company_name: str) -> None:
    url = (env("SUPABASE_URL").rstrip("/") +
           "/rest/v1/client_subscriptions"
           f"?company_name=eq.{urllib.parse.quote(company_name)}")
    http_json("DELETE", url, {**sb_headers(), "Prefer": "return=minimal"})


def delete_agent_registry(agent_id: str) -> None:
    """Also clean client_agents if the onboarding flow wrote there."""
    url = (env("SUPABASE_URL").rstrip("/") +
           "/rest/v1/client_agents"
           f"?agent_id=eq.{urllib.parse.quote(agent_id)}")
    http_json("DELETE", url, {**sb_headers(), "Prefer": "return=minimal"})


# --------------------------------------------------------------------------
# Retell cleanup
# --------------------------------------------------------------------------

def delete_retell_agent(agent_id: str) -> None:
    key = env("RETELL_API_KEY")
    status, data = http_json(
        "DELETE",
        f"https://api.retellai.com/delete-agent/{agent_id}",
        {"Authorization": f"Bearer {key}"},
    )
    if status not in (200, 204):
        print(f"  [WARN] retell delete-agent → {status} {data}")


# --------------------------------------------------------------------------
# Forged Jotform payloads
# --------------------------------------------------------------------------

def _rand_suffix() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


def forge_jotform_payload(*,
                          company_name: str,
                          pilot_mode: bool,
                          stx_asset_id: str | None = None,
                          utm_source: str | None = None) -> dict:
    """Build a payload shaped like a Jotform webhook submission.
    The n8n HVAC Standard onboarding workflow expects a flat dict of the
    raw field answers on `body`. We pass the minimum needed for the workflow
    to create a row and clone a Retell agent.
    """
    body: dict = {
        "company_name": company_name,
        "owner_name": "E2E Tester",
        "client_email": f"e2e+{_rand_suffix()}@syntharra.com",
        "phone_to_forward": "+15555550123",
        "service_area": "Test County, TS",
        "emergency_definition": "no_heat,water_leak",
        "lead_send_preferences": "slack",
        "timezone": "America/New_York",
        # Hidden attribution fields from spec § 6.1:
        "pilot_mode": bool(pilot_mode),
    }
    if stx_asset_id:
        body["stx_asset_id"] = stx_asset_id
    if utm_source:
        body["utm_source"] = utm_source
        body["utm_medium"] = "test"
        body["utm_campaign"] = "phase0-e2e"
        body["utm_content"] = "test-content"
        body["utm_term"] = "test-term"

    return {"body": body}


def submit_to_n8n(webhook_url: str, payload: dict) -> None:
    print(f"  → POST {webhook_url}")
    status, data = http_json("POST", webhook_url,
                              {"Content-Type": "application/json"}, payload)
    if status not in (200, 201, 202):
        sys.exit(f"n8n webhook rejected payload: {status} {data}")
    print(f"  n8n accepted ({status})")


def poll_until_row(company_name: str, description: str) -> dict:
    print(f"  polling client_subscriptions for {company_name!r}...")
    for attempt in range(POLL_MAX_ATTEMPTS):
        row = fetch_subscription(company_name)
        if row:
            print(f"  row appeared after {attempt * POLL_INTERVAL_SEC}s: agent_id={row.get('agent_id')}")
            return row
        time.sleep(POLL_INTERVAL_SEC)
    sys.exit(f"TIMEOUT waiting for {description} row ({POLL_MAX_ATTEMPTS * POLL_INTERVAL_SEC}s)")


# --------------------------------------------------------------------------
# Variants
# --------------------------------------------------------------------------

def submit_paid(webhook_url: str) -> tuple[dict, str]:
    company = f"E2E Paid {_rand_suffix()}"
    print(f"\n== PAID variant: {company}")
    payload = forge_jotform_payload(company_name=company, pilot_mode=False)
    submit_to_n8n(webhook_url, payload)
    row = poll_until_row(company, "paid")

    # Assertions
    assert row.get("pilot_mode") in (False, None), f"pilot_mode should be false, got {row.get('pilot_mode')}"
    assert row.get("status") == "active", f"status should be 'active', got {row.get('status')!r}"
    print("  [PASS] status='active' pilot_mode=false")
    return row, row.get("agent_id", "")


def submit_pilot(webhook_url: str) -> tuple[dict, str]:
    company = f"E2E Pilot {_rand_suffix()}"
    asset_id = "test-pilot-e2e"
    print(f"\n== PILOT variant: {company} (asset={asset_id})")
    payload = forge_jotform_payload(
        company_name=company, pilot_mode=True, stx_asset_id=asset_id, utm_source="test"
    )
    submit_to_n8n(webhook_url, payload)
    row = poll_until_row(company, "pilot")

    # Assertions
    assert row.get("pilot_mode") is True, f"pilot_mode should be true, got {row.get('pilot_mode')}"
    assert row.get("status") == "pilot", f"status should be 'pilot', got {row.get('status')!r}"
    assert row.get("first_touch_asset_id") == asset_id, (
        f"first_touch_asset_id should be {asset_id!r}, got {row.get('first_touch_asset_id')!r}"
    )

    # pilot_ends_at ≈ now + 14 days (±2 min tolerance)
    ends_str = row.get("pilot_ends_at")
    if ends_str:
        ends = datetime.fromisoformat(ends_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = ends - now
        assert timedelta(days=14) - timedelta(minutes=2) <= delta <= timedelta(days=14) + timedelta(minutes=2), (
            f"pilot_ends_at should be ~14 days from now, was {delta}"
        )
    else:
        sys.exit("pilot_ends_at missing — n8n workflow did not set it")

    print("  [PASS] status='pilot' pilot_mode=true pilot_ends_at≈+14d first_touch_asset_id persisted")
    return row, row.get("agent_id", "")


def cleanup(agent_id: str, company_name: str) -> None:
    print(f"\n== CLEANUP {company_name} ({agent_id})")
    if agent_id:
        delete_retell_agent(agent_id)
        delete_agent_registry(agent_id)
    delete_subscription(company_name)
    print("  cleaned")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 0 programmatic E2E")
    ap.add_argument("--paid", action="store_true", help="Run only the paid variant")
    ap.add_argument("--pilot", action="store_true", help="Run only the pilot variant")
    ap.add_argument("--both", action="store_true", help="Run both variants (default)")
    ap.add_argument("--no-cleanup", action="store_true", help="Leave created rows/agents behind")
    args = ap.parse_args()

    # default = both
    if not (args.paid or args.pilot or args.both):
        args.both = True

    webhook_url = fetch_webhook_url()
    print(f"Onboarding webhook URL: {webhook_url}")

    created: list[tuple[str, str]] = []  # (agent_id, company_name)

    try:
        if args.paid or args.both:
            row, agent_id = submit_paid(webhook_url)
            created.append((agent_id, row["company_name"]))
        if args.pilot or args.both:
            row, agent_id = submit_pilot(webhook_url)
            created.append((agent_id, row["company_name"]))
    finally:
        if not args.no_cleanup:
            for agent_id, company in created:
                try:
                    cleanup(agent_id, company)
                except Exception as exc:  # noqa: BLE001
                    print(f"  [WARN] cleanup failed for {company}: {exc}")

    print("\nE2E complete.")


if __name__ == "__main__":
    main()
