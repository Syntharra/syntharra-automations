#!/usr/bin/env python3
"""Split a live Retell flow snapshot into template + component files.

Source of truth: retell-iac/snapshots/<date>/flow.json
Outputs:
  retell-iac/flows/hvac-standard.template.json
  retell-iac/components/<component_name>.json
  retell-iac/manifests/hvac-standard.yaml

Structural fields (stay in template): id, type, name, display_position, edges, edge, else_edge
Behavioral fields (go to component body): everything else
"""
import json, os, sys, argparse

STRUCTURAL = {"id", "type", "name", "display_position", "edges", "edge", "else_edge"}

# Map live node id -> component filename (without .json)
ID_TO_COMPONENT = {
    "node-greeting":              "greeting_node",
    "node-identify-call":         "identify_call_node",
    "node-call-style-detector":   "call_style_detector",
    "node-fallback-leadcapture":  "fallback_leadcapture_node",
    "node-verify-emergency":      "verify_emergency_node",
    "node-callback":              "callback_node",
    "node-existing-customer":     "existing_customer_node",
    "node-general-questions":     "general_questions_node",
    "node-spam-robocall":         "spam_robocall_node",
    "node-transfer-call":         "transfer_call",
    "node-emergency-transfer":    "emergency_transfer",
    "node-transfer-failed":       "transfer_failed_node",
    "node-ending":                "ending",
    "node-validate-phone":        "validate_phone",
    "node-end-call":              "end_call",
    "global-emergency":           "emergency_detection",
    "global-spam":                "spam_detection",
    "global-transfer":            "transfer_request",
    "node-extract-caller-data":   "extract_caller_data",
}

# Flow top-level fields that are runtime-only and must be stripped from the template
RUNTIME_TOP_LEVEL = {"conversation_flow_id", "is_published", "version", "last_modification_timestamp"}

def split(snapshot_path, base_dir):
    flow = json.load(open(snapshot_path))

    # Build template (structural skeleton)
    tmpl_nodes = []
    components = {}
    missing = []
    for n in flow["nodes"]:
        nid = n["id"]
        comp_name = ID_TO_COMPONENT.get(nid)
        if not comp_name:
            missing.append(nid)
            continue
        struct = {k: v for k, v in n.items() if k in STRUCTURAL}
        struct["__COMPONENT__"] = comp_name
        tmpl_nodes.append(struct)
        body = {k: v for k, v in n.items() if k not in STRUCTURAL}
        components[comp_name] = {"body": body}

    if missing:
        raise SystemExit(f"Unmapped node ids in ID_TO_COMPONENT: {missing}")

    template = {k: v for k, v in flow.items() if k not in RUNTIME_TOP_LEVEL and k != "nodes"}
    template["nodes"] = tmpl_nodes

    # Write template
    flows_dir = os.path.join(base_dir, "flows")
    os.makedirs(flows_dir, exist_ok=True)
    tmpl_path = os.path.join(flows_dir, "hvac-standard.template.json")
    with open(tmpl_path, "w") as f:
        json.dump(template, f, indent=2, sort_keys=True)
    print(f"wrote {tmpl_path}  ({len(tmpl_nodes)} nodes)")

    # Write components (flat, no orphans/ split)
    comp_dir = os.path.join(base_dir, "components")
    os.makedirs(comp_dir, exist_ok=True)
    for name, body in components.items():
        p = os.path.join(comp_dir, f"{name}.json")
        with open(p, "w") as f:
            json.dump(body, f, indent=2, sort_keys=True)
        print(f"wrote {p}")

    # Write manifest
    manifest_path = os.path.join(base_dir, "manifests", "hvac-standard.yaml")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    lines = [
        "agent: standard",
        "flow_template: flows/hvac-standard.template.json",
        "components:",
    ]
    for name in sorted(components.keys()):
        lines.append(f"  - name: {name}")
        lines.append(f"    source: components/{name}.json")
    lines += ["overrides: {}", "excluded: []", ""]
    with open(manifest_path, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {manifest_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", required=True, help="path to snapshot/flow.json")
    p.add_argument("--base", default="retell-iac")
    a = p.parse_args()
    split(a.snapshot, a.base)
