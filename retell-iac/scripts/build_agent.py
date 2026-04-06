import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.flow_builder import load_manifest, build_flow

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--base",default="retell-iac")
    a=p.parse_args()
    m=load_manifest(a.manifest)
    f=build_flow(m, base_dir=a.base)
    os.makedirs(os.path.dirname(a.out),exist_ok=True)
    with open(a.out,"w") as fp:
        json.dump(f, fp, indent=2, sort_keys=True)
    print(f"built {a.out}  nodes={len(f['nodes'])}")
