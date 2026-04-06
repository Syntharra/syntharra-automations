"""
Syntharra Agent Promotion Script
=================================
Promotes TESTING agent -> MASTER by:
1. Fetching the TESTING flow (subagent architecture, patched by agentic-test-fix)
2. Patching the MASTER flow with the same global_prompt + nodes + edges
3. For subagent nodes with empty component_id and short stub instructions,
   restores MASTER's original full instructions (safety-critical nodes)
4. Publishing the MASTER agent

Usage: python promote.py --agent standard|premium [--dry-run]
"""
import argparse, requests, json, copy

RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
H = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
BASE = "https://api.retellai.com"

AGENTS = {
    "standard": {
        "testing_agent_id":  "agent_731f6f4d59b749a0aa11c26929",
        "master_agent_id":   "agent_4afbfdb3fcb1ba9569353af28d",
        "testing_flow_id":   "conversation_flow_5b98b76c8ff4",
        "master_flow_id":    "conversation_flow_34d169608460",
    },
    "premium": {
        "testing_agent_id":  "agent_2cffe3d86d7e1990d08bea068f",
        "master_agent_id":   "agent_9822f440f5c3a13bc4d283ea90",
        "testing_flow_id":   "conversation_flow_2ded0ed4f808",
        "master_flow_id":    "conversation_flow_1dd3458b13a7",
    },
}

# Instruction length threshold: nodes with stubs shorter than this get restored
# from MASTER's version (if MASTER has a longer instruction)
STUB_THRESHOLD = 200

def fetch_flow(flow_id):
    r = requests.get(f"{BASE}/get-conversation-flow/{flow_id}", headers=H, timeout=30)
    r.raise_for_status()
    return r.json()

def patch_flow(flow_id, payload):
    r = requests.patch(f"{BASE}/update-conversation-flow/{flow_id}", headers=H, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def publish_agent(agent_id):
    r = requests.post(f"{BASE}/publish-agent/{agent_id}", headers=H, json={}, timeout=30)
    return r.status_code, r.text[:200]

def promote(agent_type, dry_run=False):
    cfg = AGENTS[agent_type]
    print(f"\n{'='*60}")
    print(f"  PROMOTING: {agent_type.upper()} TESTING -> MASTER")
    print(f"  {'DRY-RUN -- no changes will be made' if dry_run else 'LIVE -- changes will be applied'}")
    print(f"{'='*60}\n")

    # 1. Fetch both flows
    print("Fetching TESTING flow...")
    testing_flow = fetch_flow(cfg["testing_flow_id"])
    t_nodes = testing_flow.get("nodes", [])
    print(f"  TESTING: {len(t_nodes)} nodes, global_prompt {len(testing_flow.get('global_prompt',''))} chars")

    print("Fetching MASTER flow...")
    master_flow = fetch_flow(cfg["master_flow_id"])
    m_nodes = master_flow.get("nodes", [])
    print(f"  MASTER:  {len(m_nodes)} nodes, global_prompt {len(master_flow.get('global_prompt',''))} chars")

    # Build lookup: master nodes by name
    master_by_name = {n.get("name"): n for n in m_nodes}

    # 2. Build promotion payload from TESTING flow
    COPY_FIELDS = ["global_prompt", "nodes", "edges", "start_node_id"]
    payload = {k: copy.deepcopy(testing_flow[k]) for k in COPY_FIELDS if k in testing_flow}

    # 3. For each node: fix stub subagent nodes with no component
    restored = []
    for node in payload.get("nodes", []):
        ntype = node.get("type", "")
        name  = node.get("name", "")
        comp  = node.get("component_id", "")
        instr = node.get("instruction", {}).get("text", "")

        if ntype == "subagent" and not comp and len(instr) < STUB_THRESHOLD:
            master_node = master_by_name.get(name)
            if master_node:
                master_instr = master_node.get("instruction", {}).get("text", "")
                if len(master_instr) > len(instr):
                    # Restore MASTER instruction + keep as conversation type
                    # (subagent without component doesn't route correctly)
                    node["type"] = "conversation"
                    node["instruction"] = copy.deepcopy(master_node.get("instruction", {}))
                    node["edges"] = copy.deepcopy(master_node.get("edges", node.get("edges", [])))
                    restored.append(f"    RESTORED '{name}': {len(instr)} -> {len(master_instr)} chars (kept MASTER instructions)")

    # 4. Print summary
    print(f"\nPromotion payload: {len(payload.get('nodes',[]))} nodes, {len(payload.get('global_prompt',''))} char prompt")
    if restored:
        print("\nSafety-critical nodes restored from MASTER:")
        for r_info in restored:
            print(r_info)
    print("\nFinal node layout:")
    for node in payload.get("nodes", []):
        ntype = node.get("type", "?")
        name  = node.get("name", "?")
        comp  = node.get("component_id", "")
        instr_len = len(node.get("instruction", {}).get("text", ""))
        comp_str  = f"[comp: {comp[:20]}]" if comp else f"[inline: {instr_len}ch]"
        print(f"    {ntype:30s} {name[:40]:40s} {comp_str}")

    if dry_run:
        print("\n[DRY-RUN] Would PATCH master flow and publish master agent. No changes made.")
        return True

    # 5. PATCH MASTER flow
    print(f"\nPatching MASTER flow ({cfg['master_flow_id']})...")
    try:
        result = patch_flow(cfg["master_flow_id"], payload)
        print(f"  Flow patched -- new version: {result.get('version', '?')}")
    except requests.HTTPError as e:
        print(f"  ERROR patching flow: {e.response.status_code} {e.response.text[:300]}")
        return False

    # 6. Publish MASTER agent
    print(f"\nPublishing MASTER agent ({cfg['master_agent_id']})...")
    status, body = publish_agent(cfg["master_agent_id"])
    if status == 200:
        print(f"  [OK] MASTER agent published and live")
    else:
        print(f"  [WARN] Publish returned {status}: {body}")

    print(f"\n[DONE] {agent_type.upper()} MASTER promoted and live.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["standard", "premium"], required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    promote(args.agent, dry_run=args.dry_run)
