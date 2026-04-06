import json, os, yaml

def load_manifest(path):
    with open(path) as f: return yaml.safe_load(f)

def load_component(path):
    with open(path) as f: return json.load(f)

def build_flow(manifest, base_dir="retell-iac"):
    tmpl=json.load(open(os.path.join(base_dir, manifest["flow_template"])))
    comp_map={c["name"]: load_component(os.path.join(base_dir,c["source"])) for c in manifest["components"]}
    overrides=manifest.get("overrides") or {}
    new_nodes=[]
    for n in tmpl["nodes"]:
        name=n["__COMPONENT__"]
        comp=comp_map[name]
        merged={k:v for k,v in n.items() if k!="__COMPONENT__"}
        merged.update(comp["body"])
        if comp.get("source_component_id"):
            merged["component_id"]=comp["source_component_id"]
        if name in overrides:
            merged.update(overrides[name])
        new_nodes.append(merged)
    out={k:v for k,v in tmpl.items() if k!="nodes"}
    out["nodes"]=new_nodes
    return out
