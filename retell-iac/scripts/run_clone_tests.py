#!/usr/bin/env python3
"""Run the full scenario suite against a CLONE agent.

HARDCODES clone agent_ids to avoid the run_tests.py --agent wrapper bug.
Usage:
  python run_clone_tests.py --agent standard  # hits standard clone
  python run_clone_tests.py --agent premium   # hits premium clone
"""
import argparse, os, json, requests, sys

CLONES = {
    "standard": {
        "agent_id":  "agent_201b8d1e9eee10303e79710bc9",
        "flow_id":   "conversation_flow_b0f2cf9a0e58",
        "scenario_type": "standard",
        "run_id": "clone_iac_run_1",
    },
    "premium": {
        "agent_id":  "agent_eb8195c21ba2ef79e2c6d8d3c5",
        "flow_id":   "conversation_flow_746a02ffa4ac",
        "scenario_type": "premium",
        "run_id": "clone_iac_premium_run_1",
    },
}

WEBHOOK = "https://n8n.syntharra.com/webhook/agent-test-runner"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agent",required=True,choices=list(CLONES))
    p.add_argument("--scenarios",type=int,default=None,help="limit (for smoke runs)")
    a=p.parse_args()
    c=CLONES[a.agent]
    print(f"Clone target: {c['agent_id']}")
    print(f"Run ID:       {c['run_id']}")
    body={
        "agent_id": c["agent_id"],
        "scenario_type": c["scenario_type"],
        "run_id": c["run_id"],
    }
    if a.scenarios: body["limit"]=a.scenarios
    r=requests.post(WEBHOOK,json=body,timeout=30)
    print(r.status_code, r.text[:500])

if __name__=="__main__": main()
