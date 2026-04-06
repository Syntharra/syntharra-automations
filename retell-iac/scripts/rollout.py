"""retell-iac/scripts/rollout.py — Track B2
Fleet updater for the entire client_agents registry.

Designed for 1000+ clients:
  - Rate-limited (default 5 req/s, Retell soft limit ~10/s)
  - Exponential backoff on 429/5xx
  - Idempotent (skip if prompt_version already current)
  - Canary-aware (rollout to canary=true rows first when --canary-first)
  - Dry-run mode mandatory before execute
  - Every action logged to client_agents_rollout_log
  - Resumable: re-running picks up rows that did not yet hit target version

Usage:
    python rollout.py --tag v2026.04.07 --base-prompt prompts/std_v23.json --tier std --dry-run
    python rollout.py --tag v2026.04.07 --base-prompt prompts/std_v23.json --tier std --execute
    python rollout.py --tag v2026.04.07 --base-prompt prompts/std_v23.json --tier std --execute --canary-first
"""
import os, sys, json, time, argparse, random
import requests
from datetime import datetime, timezone

RETELL_BASE = "https://api.retellai.com"
RATE_LIMIT_RPS = float(os.environ.get("ROLLOUT_RPS", "5"))
MIN_INTERVAL = 1.0 / RATE_LIMIT_RPS
MAX_RETRIES = 5

SUPABASE_URL = os.environ["SUPABASE_URL"]
SRK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
RETELL_KEY = os.environ["RETELL_API_KEY"]

SB = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json"}
RT = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}

_last_call = 0.0
def throttle():
    global _last_call
    delta = time.time() - _last_call
    if delta < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - delta)
    _last_call = time.time()

def retell_request(method, path, **kw):
    """Rate-limited Retell call with backoff. Never call Retell directly elsewhere."""
    for attempt in range(MAX_RETRIES):
        throttle()
        r = requests.request(method, f"{RETELL_BASE}{path}", headers=RT, timeout=30, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            wait = (2 ** attempt) + random.random()
            print(f"  retry {attempt+1}/{MAX_RETRIES} after {wait:.1f}s ({r.status_code})")
            time.sleep(wait)
            continue
        return r
    raise RuntimeError(f"max retries exhausted on {method} {path}")

def fetch_targets(tier, only_canary=False, exclude_master=True):
    """Pull rows from client_agents that need rollout."""
    q = f"client_agents?tier=eq.{tier}&status=neq.retired&select=*"
    if only_canary:
        q += "&canary=eq.true"
    if exclude_master:
        q += "&client_id=not.like.SYNTHARRA_MASTER_*"
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{q}", headers=SB)
    r.raise_for_status()
    return r.json()

def log_rollout(rollout_tag, row, prev_v, new_v, status, error=None):
    payload = {
        "rollout_tag": rollout_tag, "client_id": row["client_id"], "agent_id": row["agent_id"],
        "tier": row["tier"], "prev_prompt_version": prev_v, "new_prompt_version": new_v,
        "status": status, "error": error,
    }
    requests.post(f"{SUPABASE_URL}/rest/v1/client_agents_rollout_log", headers=SB, json=payload)

def update_registry(client_id, tier, new_version, base_tag):
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/client_agents?client_id=eq.{client_id}&tier=eq.{tier}",
        headers={**SB, "Prefer": "return=minimal"},
        json={"prompt_version": new_version, "base_tag": base_tag, "deployed_at": datetime.now(timezone.utc).isoformat()},
    )

def update_one_agent(row, base_prompt, new_version, base_tag, dry_run):
    """Fetch flow, merge prompt, PATCH, publish. Never delete-and-recreate."""
    flow_id = row.get("flow_id")
    if not flow_id:
        raise ValueError(f"{row['client_id']} has no flow_id")
    if row.get("prompt_version") == new_version:
        return "skipped_already_current"

    # 1. Fetch current flow
    r = retell_request("GET", f"/get-conversation-flow/{flow_id}")
    if r.status_code != 200:
        raise RuntimeError(f"GET flow failed {r.status_code}: {r.text[:200]}")
    flow = r.json()

    # 2. Merge: replace global_prompt + nodes from base_prompt template
    flow["global_prompt"] = base_prompt.get("global_prompt", flow.get("global_prompt"))
    if "nodes" in base_prompt:
        flow["nodes"] = base_prompt["nodes"]
    if "start_node_id" in base_prompt:
        flow["start_node_id"] = base_prompt["start_node_id"]

    if dry_run:
        return "dry_run_ok"

    # 3. PATCH
    patch_body = {k: flow[k] for k in ("global_prompt", "nodes", "start_node_id", "model_choice") if k in flow}
    r = retell_request("PATCH", f"/update-conversation-flow/{flow_id}", json=patch_body)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"PATCH flow failed {r.status_code}: {r.text[:200]}")

    # 4. Publish (mandatory after every Retell update)
    r = retell_request("POST", f"/publish-conversation-flow/{flow_id}")
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"publish failed {r.status_code}: {r.text[:200]}")

    return "ok"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="Rollout tag, e.g. v2026.04.07")
    ap.add_argument("--base-prompt", required=True, help="Path to JSON of merged-in flow fields")
    ap.add_argument("--tier", required=True, choices=["std", "prem"])
    ap.add_argument("--canary-first", action="store_true")
    ap.add_argument("--canary-only", action="store_true")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    a = ap.parse_args()

    with open(a.base_prompt) as f:
        base_prompt = json.load(f)
    new_version = base_prompt.get("version") or a.tag

    targets = fetch_targets(a.tier, only_canary=a.canary_only)
    if a.canary_first and not a.canary_only:
        targets.sort(key=lambda r: (not r.get("canary"), r.get("client_id")))

    print(f"rollout tag={a.tag} tier={a.tier} version={new_version} mode={'DRY_RUN' if a.dry_run else 'EXECUTE'} count={len(targets)}")

    counts = {"ok": 0, "skipped_already_current": 0, "dry_run_ok": 0, "error": 0}
    for row in targets:
        prev_v = row.get("prompt_version")
        try:
            status = update_one_agent(row, base_prompt, new_version, a.tag, a.dry_run)
            counts[status] = counts.get(status, 0) + 1
            print(f"  {row['client_id']:30s} {row['agent_id']} -> {status}")
            log_rollout(a.tag, row, prev_v, new_version, status)
            if status == "ok":
                update_registry(row["client_id"], row["tier"], new_version, a.tag)
        except Exception as e:
            counts["error"] += 1
            err = str(e)[:500]
            print(f"  {row['client_id']:30s} ERROR {err}")
            log_rollout(a.tag, row, prev_v, new_version, "error", err)

    print(f"done: {counts}")
    if counts["error"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
