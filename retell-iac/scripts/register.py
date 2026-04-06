"""retell-iac/scripts/register.py — Track B1
Registers a Retell agent in the client_agents Supabase registry.
Called by the onboarding workflow after a successful agent clone.
"""
import os, sys, argparse, requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SRK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}

def register(client_id, agent_id, tier, flow_id=None, prompt_version=None, base_tag=None, status="active", canary=False, notes=None):
    if tier not in ("std", "prem"):
        sys.exit(f"tier must be std|prem, got {tier}")
    row = {
        "client_id": client_id, "agent_id": agent_id, "tier": tier,
        "flow_id": flow_id, "prompt_version": prompt_version, "base_tag": base_tag,
        "status": status, "canary": canary, "notes": notes,
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/client_agents", headers=H, json=row)
    if r.status_code not in (200, 201, 204):
        sys.exit(f"register failed {r.status_code}: {r.text}")
    print(f"registered {client_id} ({tier}) -> {agent_id}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--agent-id", required=True)
    ap.add_argument("--tier", required=True, choices=["std","prem"])
    ap.add_argument("--flow-id")
    ap.add_argument("--prompt-version")
    ap.add_argument("--base-tag")
    ap.add_argument("--status", default="active")
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--notes")
    a = ap.parse_args()
    register(a.client_id, a.agent_id, a.tier, a.flow_id, a.prompt_version, a.base_tag, a.status, a.canary, a.notes)
