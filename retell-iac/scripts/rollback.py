#!/usr/bin/env python3
"""Emergency rollback of a MASTER agent to a snapshot Git tag.
Usage:
  python rollback.py --tag baseline-100-percent-20260406 --agent standard_master [--dry-run]

Fetches <repo>/retell-iac/snapshots/<tag>/flow.json at the tagged commit and PATCHes MASTER.
"""
import argparse, json, os, requests, base64, sys
from promote import MASTERS

OWNER="Syntharra"; REPO="syntharra-automations"
TAG_TO_SNAP={
    "baseline-100-percent-20260406": "retell-iac/snapshots/2026-04-06_baseline-100/flow.json",
}

def gh_fetch(path, ref):
    T=os.environ.get("GITHUB_TOKEN")
    if not T: raise SystemExit("GITHUB_TOKEN env var required")
    r=requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}",
        params={"ref":ref}, headers={"Authorization":f"token {T}"})
    r.raise_for_status()
    return json.loads(base64.b64decode(r.json()["content"]).decode())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tag",required=True)
    p.add_argument("--agent",required=True,choices=list(MASTERS))
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()

    m=MASTERS[a.agent]
    if not m["agent_id"]:
        raise SystemExit(f"{a.agent} does not exist yet")

    snap_path=TAG_TO_SNAP.get(a.tag)
    if not snap_path:
        raise SystemExit(f"unknown tag {a.tag} — add to TAG_TO_SNAP")
    flow=gh_fetch(snap_path, a.tag)
    for k in ["conversation_flow_id","version","last_modification_timestamp","is_published"]:
        flow.pop(k,None)

    print(f"ROLLBACK PLAN")
    print(f"  agent:    {a.agent} ({m['agent_id']})")
    print(f"  flow_id:  {m['flow_id']}")
    print(f"  snapshot: {snap_path} @ {a.tag}")
    print(f"  nodes:    {len(flow.get('nodes',[]))}")

    if a.dry_run:
        print("DRY-RUN — no writes made.")
        return

    K=os.environ.get("RETELL_API_KEY")
    if not K: raise SystemExit("RETELL_API_KEY required")
    H={"Authorization":f"Bearer {K}","Content-Type":"application/json"}
    r=requests.patch(f"https://api.retellai.com/update-conversation-flow/{m['flow_id']}",headers=H,json=flow)
    r.raise_for_status()
    print(f"PATCH ok — version {r.json().get('version')}")
    pub=requests.post(f"https://api.retellai.com/publish-agent/{m['agent_id']}",headers=H)
    pub.raise_for_status()
    print("Published. Verify live flow against snapshot manually.")

if __name__=="__main__": main()
