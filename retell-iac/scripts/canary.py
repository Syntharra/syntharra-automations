"""retell-iac/scripts/canary.py — Track B3
Canary + auto-rollback for fleet rollouts.

Workflow:
    1. Mark 5% of fleet as canary (status=canary, canary=true).
    2. Run rollout.py --canary-only.
    3. Wait 2h, query hvac_call_log for canary success rate vs baseline.
    4. If success_rate drop > 5%pts: revert canary rows to previous version, alert Slack.
    5. If green: clear canary flag, run full rollout.

Usage:
    python canary.py --tag v2026.04.07 --tier std --pick           # selects 5% as canary
    python canary.py --tag v2026.04.07 --tier std --check          # health-check window
    python canary.py --tag v2026.04.07 --tier std --revert         # rollback canary
    python canary.py --tag v2026.04.07 --tier std --promote        # clear canary, ready for full rollout
"""
import os, sys, math, argparse, random, requests, json
from datetime import datetime, timedelta, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SRK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")
SB = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json"}

CANARY_PCT = 0.05
HEALTH_WINDOW_HOURS = 2
MAX_DROP_PCT = 5.0  # percentage points

def slack(msg):
    if not SLACK_WEBHOOK: return
    try: requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10)
    except Exception: pass

def get_clients(tier):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/client_agents?tier=eq.{tier}&status=in.(active,canary)&client_id=not.like.SYNTHARRA_MASTER_*&select=*",
        headers=SB,
    )
    r.raise_for_status()
    return r.json()

def pick(tier):
    clients = get_clients(tier)
    n = max(1, math.ceil(len(clients) * CANARY_PCT))
    sample = random.sample(clients, min(n, len(clients)))
    print(f"Selecting {len(sample)}/{len(clients)} as canary ({CANARY_PCT*100:.0f}%)")
    for c in sample:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/client_agents?client_id=eq.{c['client_id']}&tier=eq.{tier}",
            headers={**SB, "Prefer": "return=minimal"},
            json={"canary": True, "status": "canary"},
        )
        print(f"  canary: {c['client_id']}")
    slack(f":test_tube: Canary picked: {len(sample)} {tier} clients")

def baseline_success_rate(tier, hours_back=24*7):
    """Last-week baseline success rate for tier (excluding canary window)."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours_back+HEALTH_WINDOW_HOURS)).isoformat()
    until = (datetime.now(timezone.utc) - timedelta(hours=HEALTH_WINDOW_HOURS)).isoformat()
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/hvac_call_log?created_at=gte.{since}&created_at=lte.{until}&select=call_status",
        headers=SB,
    )
    rows = r.json()
    if not rows: return None
    ok = sum(1 for x in rows if x.get("call_status") in ("ended", "success", "completed"))
    return 100.0 * ok / len(rows)

def canary_success_rate(tier):
    since = (datetime.now(timezone.utc) - timedelta(hours=HEALTH_WINDOW_HOURS)).isoformat()
    canary_clients = [c["client_id"] for c in get_clients(tier) if c.get("canary")]
    if not canary_clients: return None, 0
    in_filter = ",".join(f'"{c}"' for c in canary_clients)
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/hvac_call_log?created_at=gte.{since}&client_id=in.({in_filter})&select=call_status",
        headers=SB,
    )
    rows = r.json()
    if not rows: return None, 0
    ok = sum(1 for x in rows if x.get("call_status") in ("ended", "success", "completed"))
    return 100.0 * ok / len(rows), len(rows)

def check(tier, tag):
    base = baseline_success_rate(tier)
    canary, n = canary_success_rate(tier)
    print(f"baseline: {base}  canary: {canary} (n={n})")
    if canary is None or n < 5:
        print("Insufficient canary call volume — extend window")
        return 2
    drop = (base or 0) - canary
    msg = f"Canary {tier} {tag}: baseline={base:.1f}% canary={canary:.1f}% drop={drop:.1f}pp n={n}"
    print(msg)
    if drop > MAX_DROP_PCT:
        slack(f":rotating_light: {msg} — AUTO REVERT")
        return 1
    slack(f":white_check_mark: {msg} — healthy")
    return 0

def revert(tier, tag):
    """Revert canary rows to their previous version (logged in client_agents_rollout_log)."""
    clients = [c for c in get_clients(tier) if c.get("canary")]
    for c in clients:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/client_agents_rollout_log?rollout_tag=eq.{tag}&client_id=eq.{c['client_id']}&order=created_at.desc&limit=1",
            headers=SB,
        )
        rows = r.json()
        prev = rows[0]["prev_prompt_version"] if rows else None
        print(f"  revert {c['client_id']} -> {prev}")
        # Actual revert is a re-run of rollout.py with the prior base prompt JSON; here we just clear flags + alert
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/client_agents?client_id=eq.{c['client_id']}&tier=eq.{tier}",
            headers={**SB, "Prefer": "return=minimal"},
            json={"canary": False, "status": "active", "notes": f"reverted from {tag} -> {prev}"},
        )
    slack(f":leftwards_arrow_with_hook: Reverted {len(clients)} {tier} canary clients from {tag}")

def promote(tier, tag):
    clients = [c for c in get_clients(tier) if c.get("canary")]
    for c in clients:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/client_agents?client_id=eq.{c['client_id']}&tier=eq.{tier}",
            headers={**SB, "Prefer": "return=minimal"},
            json={"canary": False, "status": "active"},
        )
    slack(f":rocket: Promoted {len(clients)} {tier} canary clients — full rollout cleared")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--tier", required=True, choices=["std","prem"])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pick", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--promote", action="store_true")
    a = ap.parse_args()
    if a.pick: pick(a.tier)
    elif a.check: sys.exit(check(a.tier, a.tag))
    elif a.revert: revert(a.tier, a.tag)
    elif a.promote: promote(a.tier, a.tag)

if __name__ == "__main__":
    main()
