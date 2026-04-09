#!/usr/bin/env python3
"""Promote a built flow to MASTER. The ONLY script allowed to write to MASTER.
Usage:
  python promote.py --agent standard_master --built build/hvac-standard.built.json [--dry-run]
"""
import argparse, json, os, sys, requests

MASTERS = {
    "standard_master": {
        "agent_id": "agent_b46aef9fd327ec60c657b7a30a",
        "flow_id":  "conversation_flow_19684fe03b61",
    },
}
TESTING = {
    "standard_testing": {
        "agent_id": "agent_41e9758d8dc956843110e29a25",
        "flow_id":  "conversation_flow_bc8bb3565dbf",
    },
}

def get_key():
    # Read from env; in Cowork we inject via vault lookup at call-site
    k=os.environ.get("RETELL_API_KEY")
    if not k: raise SystemExit("RETELL_API_KEY env var required")
    return k

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agent",required=True,choices=list(MASTERS))
    p.add_argument("--built",required=True)
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()

    m=MASTERS[a.agent]
    if not m["agent_id"]:
        raise SystemExit(f"{a.agent} does not exist yet")

    built=json.load(open(a.built))
    for k in ["conversation_flow_id","version","last_modification_timestamp","is_published"]:
        built.pop(k,None)

    print(f"Target agent:  {m['agent_id']}")
    print(f"Target flow:   {m['flow_id']}")
    print(f"Source build:  {a.built} ({len(built.get('nodes',[]))} nodes)")

    if a.dry_run:
        print("DRY-RUN — no writes made.")
        return

    K=get_key()
    H={"Authorization":f"Bearer {K}","Content-Type":"application/json"}
    r=requests.patch(f"https://api.retellai.com/update-conversation-flow/{m['flow_id']}",headers=H,json=built)
    r.raise_for_status()
    new_ver=r.json().get("version")
    print(f"PATCH ok — new flow version {new_ver}")

    pub=requests.post(f"https://api.retellai.com/publish-agent/{m['agent_id']}",headers=H)
    pub.raise_for_status()
    print("Published.")

if __name__=="__main__": main()
