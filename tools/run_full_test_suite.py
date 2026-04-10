#!/usr/bin/env python3
"""
run_full_test_suite.py — Orchestrate all 3 test layers.

Layer 1: Post-call analysis quality   (25 scenarios, 5 parallel claude -p workers)
Layer 2: n8n routing                  (tools/test_call_processor.py, 30 scenarios)
Layer 3: Email delivery               (1 scenario, live Brevo check via Gmail MCP)

Success criteria:
  Layer 1: 24/25 (95%+) post-call analysis scenarios correct
  Layer 2: 90/90 n8n execution checks pass (already established baseline)
  Layer 3: 1/1 email delivered to daniel@syntharra.com

Usage:
  python tools/run_full_test_suite.py              # all 3 layers
  python tools/run_full_test_suite.py --skip-gen   # skip transcript generation (already done)
  python tools/run_full_test_suite.py --layer 1    # run only one layer
  python tools/run_full_test_suite.py --layer 2    # run only n8n routing
  python tools/run_full_test_suite.py --layer 3    # run only email delivery
  python tools/run_full_test_suite.py --no-email   # skip Layer 3 (avoids Gmail check)

Total wall-clock time (all layers): ~2-3 minutes
"""
from __future__ import annotations
import argparse, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
SKIP = "[SKIP]"


def header(text: str) -> None:
    width = 64
    print(f"\n{'='*width}")
    print(f"  {text}")
    print(f"{'='*width}")


def run_script(script_path: Path, extra_args: list[str] = None) -> int:
    """Run a Python script as subprocess, inheriting stdout/stderr."""
    cmd = [sys.executable, str(script_path)] + (extra_args or [])
    result = subprocess.run(cmd, encoding="utf-8", errors="replace")
    return result.returncode


def ensure_transcripts_exist() -> bool:
    """Return True if all 25 transcripts are present."""
    import json
    scenarios_f = HERE / "fixtures" / "scenarios.json"
    transcripts = HERE / "fixtures" / "transcripts"
    if not scenarios_f.exists():
        return False
    with open(scenarios_f, encoding="utf-8") as f:
        scenarios = json.load(f)
    missing = [s["id"] for s in scenarios if not (transcripts / f"scenario_{s['id']}.txt").exists()]
    return len(missing) == 0


def run(args: argparse.Namespace) -> int:
    start = time.time()
    layer_filter = args.layer  # None = all layers

    results: dict[int, bool] = {}

    print(f"\n{'='*64}")
    print(f"  Syntharra Agent Test Suite")
    print(f"  Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*64}")

    # ── LAYER 1: Post-call analysis quality ──────────────────────────────────
    if layer_filter is None or layer_filter == 1:
        header("LAYER 1 — Post-Call Analysis Quality (25 scenarios)")

        # Step 1a: Generate transcripts if missing
        if not args.skip_gen:
            all_present = ensure_transcripts_exist()
            if not all_present:
                print(f"\n{INFO} Generating missing transcripts (claude -p)...")
                rc = run_script(HERE / "gen_transcripts.py")
                if rc != 0:
                    print(f"\n{FAIL} Transcript generation failed — aborting Layer 1")
                    results[1] = False
                else:
                    # Step 1b: Run analysis
                    print(f"\n{INFO} Running post-call analysis (5 parallel workers)...")
                    rc = run_script(HERE / "test_post_call_analysis.py", ["--workers", "5"])
                    results[1] = rc == 0
            else:
                print(f"\n{INFO} All transcripts cached — running analysis...")
                rc = run_script(HERE / "test_post_call_analysis.py", ["--workers", "5"])
                results[1] = rc == 0
        else:
            print(f"\n{INFO} --skip-gen set — assuming transcripts are cached")
            rc = run_script(HERE / "test_post_call_analysis.py", ["--workers", "5"])
            results[1] = rc == 0
    else:
        print(f"\n{SKIP} Layer 1 skipped (--layer {layer_filter})")

    # ── LAYER 2: n8n routing ─────────────────────────────────────────────────
    if layer_filter is None or layer_filter == 2:
        header("LAYER 2 — n8n Routing (30 scenarios, 90 checks)")
        print(f"\n{INFO} Running call processor integration test...")
        rc = run_script(HERE / "test_call_processor.py")
        results[2] = rc == 0
    else:
        print(f"\n{SKIP} Layer 2 skipped (--layer {layer_filter})")

    # ── LAYER 3: Email delivery ───────────────────────────────────────────────
    if (layer_filter is None or layer_filter == 3) and not args.no_email:
        header("LAYER 3 — Email Delivery Confirmation (1 scenario)")
        print(f"\n{INFO} Firing test lead webhook → checking Gmail MCP...")
        rc = run_script(HERE / "test_email_delivery.py")
        results[3] = rc == 0
    elif args.no_email and (layer_filter is None or layer_filter == 3):
        print(f"\n{SKIP} Layer 3 skipped (--no-email)")
    else:
        print(f"\n{SKIP} Layer 3 skipped (--layer {layer_filter})")

    # ── Final summary ─────────────────────────────────────────────────────────
    elapsed = time.time() - start
    layer_names = {
        1: "Post-call analysis",
        2: "n8n routing",
        3: "Email delivery",
    }

    print(f"\n{'='*64}")
    print(f"  FULL TEST SUITE RESULTS")
    print(f"  Elapsed: {elapsed:.0f}s")
    print(f"{'='*64}")

    overall_pass = True
    for layer_num in sorted(results.keys()):
        ok = results[layer_num]
        name = layer_names.get(layer_num, f"Layer {layer_num}")
        print(f"  {'[PASS]' if ok else '[FAIL]'} Layer {layer_num}: {name}")
        if not ok:
            overall_pass = False

    if not results:
        print(f"  {INFO} No layers were run")
        return 0

    print(f"\n  {'[PASS] ALL LAYERS PASSED' if overall_pass else '[FAIL] SOME LAYERS FAILED'}")
    print(f"{'='*64}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full agent test suite orchestrator")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], help="Run only one layer")
    parser.add_argument("--skip-gen", action="store_true",
                        help="Skip transcript generation (assume transcripts are cached)")
    parser.add_argument("--no-email", action="store_true",
                        help="Skip Layer 3 email delivery test (avoids Gmail MCP check)")
    raise SystemExit(run(parser.parse_args()))
