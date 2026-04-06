import json, os, yaml

def load_manifest(path):
    with open(path) as f: return yaml.safe_load(f)

def load_component(path):
    with open(path) as f: return json.load(f)

def build_flow(manifest, base_dir="retell-iac"):
    tmpl=json.load(open(os.path.join(base_dir, manifest["flow_template"])))
    comp_map={c["name"]: load_component(os.path.join(base_dir,c["source"])) for c in (manifest.get("components") or [])}
    overrides=manifest.get("overrides") or {}
    excluded=set(manifest.get("excluded") or [])
    new_nodes=[]
    excluded_ids=set()
    # First pass: identify excluded node ids by name
    for n in tmpl["nodes"]:
        name=n.get("__COMPONENT__") or n.get("name")
        if name in excluded:
            excluded_ids.add(n.get("id"))
    # Second pass: build
    for n in tmpl["nodes"]:
        name=n.get("__COMPONENT__") or n.get("name")
        if name in excluded:
            continue
        comp=comp_map.get(name)
        merged={k:v for k,v in n.items() if k!="__COMPONENT__"}
        if comp:
            merged.update(comp["body"])
            if comp.get("source_component_id"):
                merged["component_id"]=comp["source_component_id"]
        # Strip edges pointing at excluded nodes
        if merged.get("edges"):
            merged["edges"]=[e for e in merged["edges"] if e.get("destination_node_id") not in excluded_ids]
        if name in overrides:
            merged.update(overrides[name])
        new_nodes.append(merged)
    out={k:v for k,v in tmpl.items() if k!="nodes"}
    out["nodes"]=new_nodes
    return out
