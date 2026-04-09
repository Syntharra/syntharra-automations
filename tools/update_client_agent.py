#!/usr/bin/env python3
"""
update_client_agent.py — edit-after-onboarding CLI for per-client HVAC Standard agents.

v1 scope (deliberately minimal):
  - Takes an agent_id + --set key=value pairs.
  - Reads the current `hvac_standard_agent` row from Supabase.
  - Applies --set in memory, recompiles the Retell conversation flow via
    `tools.prompt_compiler.compile`, PATCHes the live flow, publishes the
    agent, then writes the --set fields back to Supabase.
  - Prints a one-line undo command.

Explicitly out-of-scope for v1:
  - Auth, client UI, settings page.
  - Bulk updates (one agent per invocation).
  - Change history / audit table.
  - Any side effects (Stripe, HubSpot, welcome email).
  - Updating the Retell `agent` object (voice_id / agent_name / boosted_keywords).
    Only the conversation flow is patched. Identity-level and voice changes
    require a different path (a future --change-voice flag).
  - Writing to MASTER. MASTER is owned by `retell-iac/scripts/promote.py`.
    This CLI refuses unless `--allow-master` is explicitly passed.

Required env vars:
  SUPABASE_URL          — e.g. https://hgheyqwnrcvwtgngqdnq.supabase.co
  SUPABASE_SERVICE_KEY  — service_role JWT from syntharra_vault
  RETELL_API_KEY        — from syntharra_vault: Retell AI / api_key

Usage examples:
  # See what would change, no writes:
  python tools/update_client_agent.py \\
    --agent_id agent_xxx \\
    --set current_promotion="Spring tune-up $79" \\
    --dry-run

  # Apply:
  python tools/update_client_agent.py \\
    --agent_id agent_xxx \\
    --set current_promotion="Spring tune-up $79" \\
    --set lead_phone="5125550123"
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import shlex
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.prompt_compiler import compile as compile_prompt  # noqa: E402

# ------------------------------------------------------------------
# Fields the CLI allows on `--set`. Whitelist derived by scanning which
# hvac_standard_agent columns actually influence `prompt_compiler.compile()`
# output. Anything identity-shaped (agent_name, voice_gender, industry_type)
# or infrastructure-shaped (webhook_url, twilio_from, tokens) is refused.
# ------------------------------------------------------------------
EDITABLE_FIELDS = {
    # Identity-adjacent but safe to retune
    "company_name", "company_tagline", "owner_name", "website",
    "years_in_business", "certifications", "licensed_insured",
    # Services & coverage
    "services_offered", "brands_serviced", "service_area", "service_area_radius",
    "do_not_service",
    # Hours & availability
    "business_hours", "response_time", "after_hours_behavior", "after_hours_transfer",
    # Emergency
    "emergency_service", "emergency_phone",
    # Pricing & policies
    "pricing_policy", "diagnostic_fee", "standard_fees", "free_estimates",
    "financing_available", "financing_details",
    "warranty", "warranty_details",
    "maintenance_plans", "membership_program", "payment_methods",
    # Lead capture & transfer
    "lead_contact_method", "lead_phone", "lead_email",
    "transfer_phone", "transfer_triggers", "transfer_behavior",
    # Promotions
    "current_promotion", "seasonal_services", "unique_selling_points",
    "google_review_rating", "google_review_count",
    # Misc
    "company_phone", "custom_greeting", "additional_info",
}

REFUSED_FIELDS = {
    "agent_name":   "Changing agent_name would flip the Live/Demo prefix. Use a dedicated promote/demote flow.",
    "voice_gender": "Voice changes require updating the Retell agent voice_id, which v1 does not touch.",
    "industry_type": "Fixed per product line. Not editable.",
    "plan_type":    "Billing artifact — don't edit here.",
    "agent_id":     "Immutable identifier.",
    "conversation_flow_id": "Managed by Retell, not stored by us.",
}

# MASTER ids — refuse unless --allow-master
MASTER_AGENT_IDS = {"agent_4afbfdb3fcb1ba9569353af28d"}

RETELL_BASE = "https://api.retellai.com"


# ------------------------------------------------------------------
# HTTP
# ------------------------------------------------------------------

def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing env var: {name}")
    return v


def _http(method: str, url: str, headers: dict, body=None, timeout: int = 60):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")[:1000]}


# ------------------------------------------------------------------
# Supabase
# ------------------------------------------------------------------

def sb_fetch_row(agent_id: str) -> dict:
    sb = _env("SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_KEY")
    url = f"{sb}/rest/v1/hvac_standard_agent?agent_id=eq.{urllib.parse.quote(agent_id)}&select=*"
    status, data = _http("GET", url, {"apikey": key, "Authorization": f"Bearer {key}"})
    if status != 200:
        sys.exit(f"supabase fetch failed: {status} {data}")
    if not data:
        sys.exit(f"no hvac_standard_agent row for agent_id={agent_id}")
    if len(data) > 1:
        sys.exit(f"multiple rows found for agent_id={agent_id} — should never happen")
    return data[0]


def sb_update_row(agent_id: str, updates: dict) -> None:
    sb = _env("SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_KEY")
    url = f"{sb}/rest/v1/hvac_standard_agent?agent_id=eq.{urllib.parse.quote(agent_id)}"
    status, data = _http(
        "PATCH", url,
        {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        body=updates,
    )
    if status not in (200, 204):
        sys.exit(f"supabase update failed: {status} {data}")


# ------------------------------------------------------------------
# Retell
# ------------------------------------------------------------------

def retell_get_flow(flow_id: str) -> dict:
    key = _env("RETELL_API_KEY")
    status, data = _http(
        "GET", f"{RETELL_BASE}/get-conversation-flow/{flow_id}",
        {"Authorization": f"Bearer {key}"},
    )
    if status != 200:
        sys.exit(f"retell get-conversation-flow failed: {status} {data}")
    return data


def retell_get_agent(agent_id: str) -> dict:
    key = _env("RETELL_API_KEY")
    status, data = _http(
        "GET", f"{RETELL_BASE}/get-agent/{agent_id}",
        {"Authorization": f"Bearer {key}"},
    )
    if status != 200:
        sys.exit(f"retell get-agent failed: {status} {data}")
    return data


def retell_patch_flow(flow_id: str, body: dict) -> dict:
    key = _env("RETELL_API_KEY")
    # Strip fields the API rejects on PATCH
    body = {k: v for k, v in body.items()
            if k not in ("conversation_flow_id", "version", "last_modification_timestamp", "is_published")}
    status, data = _http(
        "PATCH", f"{RETELL_BASE}/update-conversation-flow/{flow_id}",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body=body,
    )
    if status not in (200, 201):
        sys.exit(f"retell update-conversation-flow failed: {status} {data}")
    return data


def retell_publish_agent(agent_id: str) -> None:
    key = _env("RETELL_API_KEY")
    status, data = _http(
        "POST", f"{RETELL_BASE}/publish-agent/{agent_id}",
        {"Authorization": f"Bearer {key}"},
    )
    if status not in (200, 201):
        sys.exit(f"retell publish-agent failed: {status} {data}")


# ------------------------------------------------------------------
# Diff
# ------------------------------------------------------------------

def show_global_prompt_diff(live_prompt: str, new_prompt: str) -> int:
    if live_prompt == new_prompt:
        print("  (global_prompt unchanged)")
        return 0
    diff = list(difflib.unified_diff(
        live_prompt.splitlines(keepends=False),
        new_prompt.splitlines(keepends=False),
        fromfile="live",
        tofile="compiled",
        lineterm="",
        n=2,
    ))
    changed = sum(1 for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))
    print(f"  global_prompt: {changed} line(s) changed")
    for line in diff[:40]:
        print(f"    {line}")
    if len(diff) > 40:
        print(f"    ... and {len(diff) - 40} more diff lines")
    return changed


def show_node_count_diff(live_flow: dict, new_flow: dict) -> None:
    live_n = len(live_flow.get("nodes", []))
    new_n = len(new_flow.get("nodes", []))
    marker = "" if live_n == new_n else f"  (!) {live_n} -> {new_n}"
    print(f"  nodes: {live_n} live, {new_n} compiled{marker}")


# ------------------------------------------------------------------
# Undo
# ------------------------------------------------------------------

def build_undo_command(agent_id: str, old_row: dict, applied: dict) -> str:
    """`python tools/update_client_agent.py --agent_id X --set k=<old_v> ...`"""
    parts = ["python", "tools/update_client_agent.py", "--agent_id", agent_id]
    for k in applied:
        old_v = old_row.get(k)
        if old_v is None:
            old_v = ""
        parts.extend(["--set", f"{k}={old_v}"])
    return " ".join(shlex.quote(p) for p in parts)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def parse_set(raw: list[str]) -> dict:
    out = {}
    for item in raw:
        if "=" not in item:
            sys.exit(f"--set expects key=value, got: {item!r}")
        k, v = item.split("=", 1)
        k = k.strip()
        if k in REFUSED_FIELDS:
            sys.exit(f"refusing to set `{k}`: {REFUSED_FIELDS[k]}")
        if k not in EDITABLE_FIELDS:
            sys.exit(f"`{k}` is not in the editable whitelist. See EDITABLE_FIELDS in update_client_agent.py")
        out[k] = v
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Update one HVAC Standard client agent")
    ap.add_argument("--agent_id", required=True, help="Retell agent_id to update")
    ap.add_argument("--set", action="append", default=[], dest="sets",
                    help="Field update, k=v. May be repeated.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Compile and diff only. No writes.")
    ap.add_argument("--allow-master", action="store_true",
                    help="Allow targeting a MASTER agent (retell-iac owns MASTER — do not use casually).")
    ap.add_argument("--yes", action="store_true",
                    help="Skip the interactive confirmation prompt.")
    args = ap.parse_args()

    if args.agent_id in MASTER_AGENT_IDS and not args.allow_master:
        sys.exit(
            f"refusing to touch MASTER agent {args.agent_id}. "
            "MASTER is owned by retell-iac/scripts/promote.py. "
            "Pass --allow-master only if you know exactly what you're doing."
        )

    if not args.sets:
        sys.exit("no --set fields provided; nothing to do")

    updates = parse_set(args.sets)
    print(f"Target agent:  {args.agent_id}")
    print(f"Updates:       {updates}")
    print(f"Dry-run:       {args.dry_run}")
    print()

    # --- 1. Fetch current state
    print("Fetching Supabase row ...")
    row = sb_fetch_row(args.agent_id)
    company = row.get("company_name", "?")
    flow_id = row.get("conversation_flow_id")
    if not flow_id:
        sys.exit(f"row for {args.agent_id} has no conversation_flow_id — was onboarding completed?")
    print(f"  Company:     {company}")
    print(f"  Flow id:     {flow_id}")
    print()

    print("Fetching live Retell flow ...")
    live_flow = retell_get_flow(flow_id)
    print()

    # --- 2. Apply updates + compile
    print("Applying updates + compiling new flow ...")
    updated_row = {**row, **updates}
    compiled = compile_prompt(updated_row)
    new_flow = compiled["conversationFlow"]
    print()

    # --- 3. Diff
    print("=== Diff ===")
    show_node_count_diff(live_flow, new_flow)
    changed_lines = show_global_prompt_diff(
        live_flow.get("global_prompt", ""),
        new_flow.get("global_prompt", ""),
    )
    print()

    if args.dry_run:
        print("DRY-RUN — no writes made.")
        print()
        print("Undo command (if you run for real):")
        print("  " + build_undo_command(args.agent_id, row, updates))
        return 0

    if changed_lines == 0:
        # Node-level changes may still exist (e.g., transfer_number in
        # Transfer Call node). Only abort if node count and prompt both match
        # AND serialized node instructions match.
        if json.dumps(live_flow.get("nodes", []), sort_keys=True) == \
           json.dumps(new_flow.get("nodes", []), sort_keys=True):
            print("No effective change — skipping PATCH.")
            return 0

    if not args.yes:
        reply = input("Apply to live Retell? [y/N] ").strip().lower()
        if reply != "y":
            print("Aborted.")
            return 1

    # --- 4. PATCH flow + publish
    print()
    print("PATCHing conversation flow ...")
    patched = retell_patch_flow(flow_id, new_flow)
    new_version = patched.get("version")
    print(f"  ok — new flow version {new_version}")

    print("Publishing agent ...")
    retell_publish_agent(args.agent_id)
    print("  published")

    # --- 5. Write back to Supabase
    print("Writing updates back to Supabase ...")
    sb_update_row(args.agent_id, updates)
    print("  ok")
    print()

    # --- 6. Undo command
    print("Done. To undo:")
    print("  " + build_undo_command(args.agent_id, row, updates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
