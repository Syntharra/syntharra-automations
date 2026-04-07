"""
run-scenario-tests.py
=====================
Loads credentials from Supabase vault at runtime (no keys in repo).
Runs agentic-test-fix-v3.py for Standard then Premium, full suite.

Usage:
    python3 run-scenario-tests.py [--dry-run] [--agent standard|premium] [--group <group>]
"""

import subprocess, sys, os, requests, json, argparse

# ── Supabase vault ─────────────────────────────────────────────────────────
SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
# Service role key injected here at runtime (not stored in repo)
# Set env var: SUPABASE_SERVICE_ROLE_KEY or pass via stdin
SRK = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

def get_key(service, key_type):
    if not SRK:
        return None
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/syntharra_vault",
        params={"service_name": f"eq.{service}", "key_type": f"eq.{key_type}", "select": "key_value"},
        headers={"apikey": SRK, "Authorization": f"Bearer {SRK}"},
        timeout=10,
    )
    if r.ok and r.json():
        return r.json()[0]["key_value"]
    return None

# ── Load credentials ────────────────────────────────────────────────────────
def load_credentials():
    creds = {}

    # Prefer env vars (fast path)
    creds["GROQ_KEY"]     = os.environ.get("GROQ_KEY")     or get_key("OpenAI", "api_key")
    creds["RETELL_KEY"]   = os.environ.get("RETELL_KEY")   or get_key("Retell AI", "api_key")
    creds["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN") or get_key("GitHub", "personal_access_token")

    for k, v in creds.items():
        if not v:
            print(f"ERROR: Could not load {k}")
            sys.exit(1)
        print(f"  ✅ {k} loaded")

    return creds

# ── Run a single agent ──────────────────────────────────────────────────────
def run_agent(agent_type, creds, dry_run=False, group=None, scenarios=None):
    script = os.path.join(os.path.dirname(__file__), "tools", "agentic-test-fix-v3.py")
    if not os.path.exists(script):
        # Fall back to same directory
        script = os.path.join(os.path.dirname(__file__), "agentic-test-fix-v3.py")

    cmd = [sys.executable, script, "--agent", agent_type]
    if dry_run:
        cmd.append("--dry-run")
    if group:
        cmd.extend(["--group", group])
    if scenarios:
        cmd.extend(["--scenarios", scenarios])

    env = os.environ.copy()
    env["GROQ_KEY"]     = creds["GROQ_KEY"]
    env["RETELL_KEY"]   = creds["RETELL_KEY"]
    env["GITHUB_TOKEN"] = creds["GITHUB_TOKEN"]

    print(f"\n{'='*62}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"{'='*62}\n")

    result = subprocess.run(cmd, env=env)
    return result.returncode

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Run Syntharra scenario tests")
    parser.add_argument("--agent",    choices=["standard", "premium", "both"], default="both")
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--group",    help="Run only this scenario group")
    parser.add_argument("--scenarios",help="Comma-separated scenario IDs")
    args = parser.parse_args()

    print("\n  Loading credentials from Supabase vault...")
    creds = load_credentials()

    agents = ["standard", "premium"] if args.agent == "both" else [args.agent]
    codes  = []

    for agent in agents:
        rc = run_agent(agent, creds, dry_run=args.dry_run, group=args.group, scenarios=args.scenarios)
        codes.append((agent, rc))
        if rc != 0:
            print(f"\n[WARNING] {agent} exited with code {rc}")

    print("\n\n" + "="*62)
    print("  SUMMARY")
    print("="*62)
    for agent, rc in codes:
        status = "✅ DONE" if rc == 0 else f"❌ EXIT {rc}"
        print(f"  {agent:12s}  {status}")
    print("="*62 + "\n")

if __name__ == "__main__":
    main()
