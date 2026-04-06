import argparse, json, sys

IGNORE_KEYS = {"conversation_flow_id", "version", "last_modification_timestamp", "is_published"}

def norm(x):
    if isinstance(x, dict):
        return {k: norm(v) for k, v in sorted(x.items())
                if k not in IGNORE_KEYS and not k.endswith("_timestamp")}
    if isinstance(x, list):
        items = [norm(i) for i in x]
        try:
            return sorted(items, key=lambda i: json.dumps(i, sort_keys=True))
        except Exception:
            return items
    return x

def index_nodes(flow):
    """Return {node_id: normalized_node} for id-based diff."""
    out = {}
    for n in flow.get("nodes", []):
        nid = n.get("id")
        if nid:
            out[nid] = norm({k: v for k, v in n.items() if k != "id"})
    return out

def deep_diff(a, b, path=""):
    diffs = []
    if type(a) != type(b):
        diffs.append((path, "type", type(a).__name__, type(b).__name__))
        return diffs
    if isinstance(a, dict):
        for k in set(a) | set(b):
            if k not in a:
                diffs.append((f"{path}.{k}", "missing-in-a", None, b[k]))
            elif k not in b:
                diffs.append((f"{path}.{k}", "missing-in-b", a[k], None))
            else:
                diffs += deep_diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append((path, "len", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            diffs += deep_diff(x, y, f"{path}[{i}]")
    else:
        if a != b:
            diffs.append((path, "val", a, b))
    return diffs

def diff_flows(a, b):
    """Id-matched node diff + top-level diff on everything except nodes."""
    diffs = []
    an = index_nodes(a)
    bn = index_nodes(b)
    only_a = set(an) - set(bn)
    only_b = set(bn) - set(an)
    for nid in sorted(only_a):
        diffs.append((f".nodes[id={nid}]", "only-in-a", nid, None))
    for nid in sorted(only_b):
        diffs.append((f".nodes[id={nid}]", "only-in-b", None, nid))
    for nid in sorted(set(an) & set(bn)):
        diffs += deep_diff(an[nid], bn[nid], f".nodes[id={nid}]")
    # Top-level minus nodes
    a_top = norm({k: v for k, v in a.items() if k != "nodes"})
    b_top = norm({k: v for k, v in b.items() if k != "nodes"})
    diffs += deep_diff(a_top, b_top, "")
    return diffs

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    args = p.parse_args()
    A = json.load(open(args.a))
    B = json.load(open(args.b))
    d = diff_flows(A, B)
    if not d:
        print("CLEAN — semantically identical")
        sys.exit(0)
    print(f"{len(d)} differences:")
    for row in d[:50]:
        print(" ", row)
    sys.exit(1)
