#!/usr/bin/env python3
"""
post-change-verify.py — Run after any Retell agent or n8n workflow change.
Triggers E2E test, reads results, enters self-healing loop if failures found.

Usage:
  python3 tools/post-change-verify.py --scope standard
  python3 tools/post-change-verify.py --scope premium
  python3 tools/post-change-verify.py --scope both
"""
import subprocess, sys, os, argparse
from datetime import datetime

# ── Safety gate — refuse to run against MASTER agents ──
MASTER_AGENTS = [
    "agent_4afbfdb3fcb1ba9569353af28d",  # Standard MASTER
    "agent_9822f440f5c3a13bc4d283ea90",  # Premium MASTER
]
TESTING_AGENTS = {
    "standard": "agent_731f6f4d59b749a0aa11c26929",
    "premium":  "agent_2cffe3d86d7e1990d08bea068f",
}

MAX_ITERATIONS = 10
MAX_CONSECUTIVE_FAILS = 3

def check_env():
    """Verify environment is safe before running."""
    # Make sure RETELL_KEY is set
    if not os.environ.get("RETELL_KEY"):
        print("WARNING: RETELL_KEY not set. E2E tests will use vault lookup.")
    # Confirm we are NOT targeting a master agent
    for master in MASTER_AGENTS:
        if master in str(os.environ):
            print(f"SAFETY BLOCK: MASTER agent ID detected in environment: {master}")
            print("Refusing to run. Only TESTING agents allowed.")
            sys.exit(1)

def run_e2e(scope):
    """Run the appropriate E2E test script."""
    script = "shared/e2e-test.py" if scope == "standard" else "shared/e2e-test-premium.py"
    print(f"\n[E2E] Running {script}...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=300
    )
    return result.returncode, result.stdout, result.stderr

def parse_failures(stdout):
    """Extract failing scenario numbers from test output."""
    failures = []
    for line in stdout.split("\n"):
        if "FAIL" in line or "❌" in line:
            failures.append(line.strip())
    return failures

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["standard", "premium", "both"], default="standard")
    args = parser.parse_args()

    check_env()

    scopes = ["standard", "premium"] if args.scope == "both" else [args.scope]

    for scope in scopes:
        print(f"\n{'='*60}")
        print(f"POST-CHANGE VERIFY — {scope.upper()}")
        print(f"Testing agent: {TESTING_AGENTS[scope]}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)

        iteration = 0
        consecutive_fails = 0

        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n[Iteration {iteration}/{MAX_ITERATIONS}]")

            returncode, stdout, stderr = run_e2e(scope)

            if returncode == 0:
                print(f"\n✅ E2E PASSED on iteration {iteration}")
                print("Safe to push to production.")
                consecutive_fails = 0
                break
            else:
                failures = parse_failures(stdout)
                consecutive_fails += 1
                print(f"\n❌ E2E FAILED — {len(failures)} failures")
                for f in failures[:10]:
                    print(f"  {f}")

                if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                    print(f"\n🛑 STOPPED: {MAX_CONSECUTIVE_FAILS} consecutive failures.")
                    print("Surface this to Dan before continuing.")
                    print("Do NOT push to production.")
                    sys.exit(1)

                print(f"\nEntering self-healing loop (consecutive fails: {consecutive_fails}/{MAX_CONSECUTIVE_FAILS})...")
                print("Claude Code will now diagnose and attempt fixes...")
                # Claude Code reads this output and acts on the failures
                print("FAILURES TO FIX:")
                for f in failures:
                    print(f"  - {f}")
                # The actual fix happens via Claude Code's agentic loop reading this output
                # and applying fixes to the TESTING agent prompt

        else:
            print(f"\n🛑 STOPPED: Reached max {MAX_ITERATIONS} iterations without passing.")
            print("Surface this to Dan. Do NOT push to production.")
            sys.exit(1)

if __name__ == "__main__":
    main()
