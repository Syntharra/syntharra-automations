#!/usr/bin/env python3
"""
re_register_master.py — One-time: recreate MASTER + TESTING Retell agents from snapshot.

Context: MASTER (agent_4afbfdb3fcb1ba9569353af28d) and TESTING (agent_6e7a2ae03c2fbd7a251fafcd00)
were deleted from Retell 2026-04-09 during account cleanup. This script rebuilds them from the
autolayout-fixed snapshot.

What it does:
  1. POST flow.json → new TESTING flow (authoritative authoring surface)
  2. POST flow.json (same content) → new MASTER flow
  3. POST agent.json shape (name="HVAC Standard TESTING") → TESTING agent bound to TESTING flow
  4. POST agent.json shape (name="HVAC Standard MASTER", +phone +webhook) → MASTER agent bound to MASTER flow
  5. Publish MASTER agent
  6. Update syntharra_vault entries for Retell MASTER / TESTING agent IDs
  7. Print new IDs — manually update REFERENCE.md / STATE.md / retell-iac/CLAUDE.md / promote.py

Required env vars:
  RETELL_API_KEY         — from syntharra_vault (service_name='Retell AI', key_type='api_key')
  SUPABASE_URL           — https://hgheyqwnrcvwtgngqdnq.supabase.co
  SUPABASE_SERVICE_KEY   — service_role JWT

Optional:
  --dry-run              — print payloads, no API calls
"""
from __future__ import annotations
import argparse, copy, json, os, pathlib, sys, urllib.error, urllib.request

SNAPSHOT_DIR = pathlib.Path(__file__).resolve().parent.parent / "retell-iac" / "snapshots" / "2026-04-09_testing-autolayout-fixed"
RETELL_BASE  = "https://api.retellai.com"
WEBHOOK_URL  = "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
MASTER_PHONE = "+18129944371"


# ---------- helpers ----------

def env(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def retell_post(path: str, body: dict, key: str, dry_run: bool) -> dict:
    url = f"{RETELL_BASE}{path}"
    if dry_run:
        print(f"[DRY-RUN] POST {url}")
        print(json.dumps(body, indent=2)[:400], "...\n")
        return {"conversation_flow_id": "dry_flow_id", "agent_id": "dry_agent_id"}
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data,
           headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
           method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()[:600]
        sys.exit(f"Retell POST {path} failed {e.code}: {body_err}")


def sb_request(method: str, path: str, body, url: str, key: str, dry_run: bool, label: str = ""):
    if dry_run:
        print(f"[DRY-RUN] {method} Supabase {path} {label}")
        return
    full_url = url.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req  = urllib.request.Request(full_url, data=data, method=method,
           headers={"apikey": key, "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        print(f"  WARN Supabase {method} {path}: {e.code} {e.read().decode()[:200]}")


# ---------- flow / agent payload builders ----------

FLOW_STRIP = {"conversation_flow_id", "version", "last_modification_timestamp", "is_published"}
AGENT_STRIP = {"agent_id", "last_modification_timestamp", "version", "is_published"}


def build_flow_payload(flow_raw: dict) -> dict:
    return {k: v for k, v in flow_raw.items() if k not in FLOW_STRIP}


def build_agent_payload(agent_raw: dict, flow_id: str, name: str,
                        include_phone: bool, include_webhook: bool) -> dict:
    payload = {k: v for k, v in agent_raw.items() if k not in AGENT_STRIP}
    payload["agent_name"] = name
    # point at new flow
    if "response_engine" in payload:
        payload["response_engine"] = copy.deepcopy(agent_raw["response_engine"])
        payload["response_engine"].pop("version", None)
        payload["response_engine"]["conversation_flow_id"] = flow_id
    if include_phone:
        # phone binding is done via Retell's phone-number endpoints, not agent create —
        # agent_name is enough; leave phone wiring for the existing Twilio/Telnyx line.
        pass
    if include_webhook:
        payload["webhook_url"] = WEBHOOK_URL
    else:
        payload.pop("webhook_url", None)
    return payload


# ---------- vault update ----------

def vault_upsert(sb_url: str, sb_key: str, service_name: str, key_type: str, key_value: str,
                 notes: str, dry_run: bool):
    # Pattern from FAILURES.md: DELETE + INSERT (no unique constraint on upsert)
    qs = f"?service_name=eq.{urllib.parse.quote(service_name)}&key_type=eq.{urllib.parse.quote(key_type)}"
    sb_request("DELETE", f"/rest/v1/syntharra_vault{qs}", None, sb_url, sb_key, dry_run,
               f"DELETE {service_name}/{key_type}")
    sb_request("POST", "/rest/v1/syntharra_vault",
               {"service_name": service_name, "key_type": key_type,
                "key_value": key_value, "notes": notes},
               sb_url, sb_key, dry_run, f"INSERT {service_name}/{key_type}")


import urllib.parse  # needed above; import here to avoid circular with sys.exit


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    retell_key = env("RETELL_API_KEY")
    sb_url     = env("SUPABASE_URL")
    sb_key     = env("SUPABASE_SERVICE_KEY")

    flow_raw  = json.loads((SNAPSHOT_DIR / "flow.json").read_text())
    agent_raw = json.loads((SNAPSHOT_DIR / "agent.json").read_text())

    print("=" * 60)
    print("Step 1: Create TESTING conversation flow")
    testing_flow_payload = build_flow_payload(flow_raw)
    r1 = retell_post("/create-conversation-flow", testing_flow_payload, retell_key, args.dry_run)
    testing_flow_id = r1.get("conversation_flow_id", "")
    print(f"  TESTING flow_id: {testing_flow_id}")

    print("Step 2: Create MASTER conversation flow (same content)")
    master_flow_payload = build_flow_payload(flow_raw)
    r2 = retell_post("/create-conversation-flow", master_flow_payload, retell_key, args.dry_run)
    master_flow_id = r2.get("conversation_flow_id", "")
    print(f"  MASTER  flow_id: {master_flow_id}")

    print("Step 3: Create TESTING agent")
    testing_agent_payload = build_agent_payload(
        agent_raw, testing_flow_id,
        name="HVAC Standard TESTING",
        include_phone=False,
        include_webhook=False,   # TESTING doesn't fire real webhooks
    )
    r3 = retell_post("/create-agent", testing_agent_payload, retell_key, args.dry_run)
    testing_agent_id = r3.get("agent_id", "")
    print(f"  TESTING agent_id: {testing_agent_id}")

    print("Step 4: Create MASTER agent")
    master_agent_payload = build_agent_payload(
        agent_raw, master_flow_id,
        name="HVAC Standard MASTER",
        include_phone=True,
        include_webhook=True,
    )
    r4 = retell_post("/create-agent", master_agent_payload, retell_key, args.dry_run)
    master_agent_id = r4.get("agent_id", "")
    print(f"  MASTER  agent_id: {master_agent_id}")

    print("Step 5: Publish MASTER agent")
    pub_url = f"{RETELL_BASE}/publish-agent/{master_agent_id}"
    if not args.dry_run:
        pub_req = urllib.request.Request(pub_url, data=b"",
                  headers={"Authorization": f"Bearer {retell_key}", "Content-Type": "application/json"},
                  method="POST")
        try:
            with urllib.request.urlopen(pub_req, timeout=30) as rr:
                print(f"  Published. ({rr.status})")
        except urllib.error.HTTPError as e:
            print(f"  WARN publish failed {e.code}: {e.read().decode()[:200]}")
    else:
        print(f"  [DRY-RUN] POST {pub_url}")

    print("Step 6: Update syntharra_vault")
    vault_upsert(sb_url, sb_key, "Retell AI", "master_agent_id", master_agent_id,
                 f"MASTER agent ID as of 2026-04-09 re-register", args.dry_run)
    vault_upsert(sb_url, sb_key, "Retell AI", "testing_agent_id", testing_agent_id,
                 f"TESTING agent ID as of 2026-04-09 re-register", args.dry_run)
    vault_upsert(sb_url, sb_key, "Retell AI", "master_flow_id", master_flow_id,
                 f"MASTER flow ID as of 2026-04-09 re-register", args.dry_run)
    vault_upsert(sb_url, sb_key, "Retell AI", "testing_flow_id", testing_flow_id,
                 f"TESTING flow ID as of 2026-04-09 re-register", args.dry_run)

    print("=" * 60)
    print("DONE — copy these IDs into REFERENCE.md / STATE.md / retell-iac/CLAUDE.md / promote.py:")
    print(f"  MASTER  agent_id : {master_agent_id}")
    print(f"  MASTER  flow_id  : {master_flow_id}")
    print(f"  TESTING agent_id : {testing_agent_id}")
    print(f"  TESTING flow_id  : {testing_flow_id}")
    print()
    print("Manual follow-ups:")
    print("  1. Update REFERENCE.md Agent Registry + Conversation Flow Registry tables")
    print("  2. Update STATE.md 'What's live in production' section")
    print("  3. Update retell-iac/CLAUDE.md Canonical Agents table")
    print("  4. Update retell-iac/scripts/promote.py MASTERS dict (both agent_id + flow_id)")
    print("  5. Bind +18129944371 to MASTER agent in Retell dashboard (Manage > Phone Numbers)")
    print("  6. Register in Supabase client_agents:")
    print(f"     python retell-iac/scripts/register.py --client-id SYNTHARRA_MASTER_STD --agent-id {master_agent_id} --tier std --flow-id {master_flow_id} --status active")
    print(f"     python retell-iac/scripts/register.py --client-id SYNTHARRA_TESTING_STD --agent-id {testing_agent_id} --tier std --flow-id {testing_flow_id} --status active")
    print("  7. Tag a new baseline snapshot: cp -r retell-iac/snapshots/2026-04-09_testing-autolayout-fixed retell-iac/snapshots/2026-04-09_reregister-baseline")


if __name__ == "__main__":
    main()
