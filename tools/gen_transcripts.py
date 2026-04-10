#!/usr/bin/env python3
"""
gen_transcripts.py — Generate and cache synthetic HVAC call transcripts.

Reads scenarios from tools/fixtures/scenarios.json.
Generates a realistic transcript for each scenario via `claude -p` subprocess.
Saves to tools/fixtures/transcripts/scenario_{id}.txt — run once, cached after.

Usage:
  python tools/gen_transcripts.py              # generate missing transcripts
  python tools/gen_transcripts.py --force      # regenerate all (even cached)
  python tools/gen_transcripts.py --scenario 5 # generate one scenario
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE        = Path(__file__).parent
FIXTURES    = HERE / "fixtures"
TRANSCRIPTS = FIXTURES / "transcripts"
SCENARIOS_F = FIXTURES / "scenarios.json"

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
SKIP = "[SKIP]"


def load_scenarios() -> list[dict]:
    with open(SCENARIOS_F, encoding="utf-8") as f:
        return json.load(f)


def transcript_path(scenario_id: int) -> Path:
    return TRANSCRIPTS / f"scenario_{scenario_id}.txt"


def build_prompt(scenario: dict) -> str:
    return f"""Generate a realistic call center customer service transcript.

An AI receptionist named Alex answers for a home services company.
The caller's situation: {scenario['description']}

Rules:
- Format alternates: AGENT: ... then CALLER: ... (4-12 exchanges total)
- AGENT answers, says "Thanks for calling, this is Alex, how can I help?"
- The transcript MUST accurately reflect the scenario described above
- If the caller is a spam/telemarketer: AGENT should politely say wrong department and end call
- If the caller is a robocall/dead air: show silence markers and AGENT ending the call
- If the caller is a wrong number: very short, caller quickly says wrong number and hangs up
- If the caller has an invoice question: talk only about billing, no repair needed
- If it is an emergency: caller conveys urgency clearly
- Return ONLY the raw dialogue, no headers, timestamps, or stage directions

Scenario type: {scenario['name']}"""


def run_claude(prompt: str) -> str | None:
    """Run claude -p with the given prompt via stdin. Returns text or None on failure.

    Passes prompt via stdin (not CLI arg) to avoid Windows 8191-char limit.
    Runs from a temp dir with a minimal CLAUDE.md so the project's HVAC skills
    don't override the simple generation request.
    """
    import platform, tempfile, shutil
    on_windows = platform.system() == "Windows"
    tmpdir = tempfile.mkdtemp(prefix="gen_tx_")
    try:
        with open(os.path.join(tmpdir, "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("Generate transcripts as requested. No tools needed.")
        cmd = (["cmd", "/c", "claude"] if on_windows else ["claude"]) + [
            "-p", "--input-format", "text"
        ]
        result = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace", cwd=tmpdir
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        print(f"  {FAIL} `claude` CLI not found. Is Claude Code installed?")
        return None
    finally:
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


def generate_transcript(scenario: dict, force: bool = False) -> bool:
    path = transcript_path(scenario["id"])
    if path.exists() and not force:
        print(f"  {SKIP} Scenario {scenario['id']}: {scenario['name']} (cached)")
        return True

    print(f"  {INFO} Generating scenario {scenario['id']}: {scenario['name']} ...")
    prompt = build_prompt(scenario)
    text = run_claude(prompt)
    if not text:
        print(f"  {FAIL} Scenario {scenario['id']}: claude -p returned empty/error")
        return False

    # Sanity check — must have some meaningful content (at least 100 chars)
    if len(text) < 100:
        print(f"  {FAIL} Scenario {scenario['id']}: transcript too short ({len(text)} chars)")
        return False

    path.write_text(text, encoding="utf-8")
    print(f"  {PASS} Scenario {scenario['id']}: {len(text)} chars saved")
    return True


def main(args: argparse.Namespace) -> int:
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    scenarios = load_scenarios()

    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] == args.scenario]
        if not scenarios:
            print(f"{FAIL} Scenario {args.scenario} not found in scenarios.json")
            return 1

    print(f"\n{'='*60}")
    print(f"  Transcript Generator — {len(scenarios)} scenario(s)")
    print(f"  Output: {TRANSCRIPTS}")
    print(f"{'='*60}\n")

    results = []
    for sc in scenarios:
        ok = generate_transcript(sc, force=args.force)
        results.append(ok)

    passed = sum(results)
    total  = len(results)
    print(f"\n{'='*60}")
    print(f"  Generated: {passed}/{total} transcripts")
    if passed < total:
        print(f"  {FAIL} {total - passed} transcript(s) failed — rerun to retry")
    else:
        print(f"  {PASS} All transcripts ready")
    print(f"{'='*60}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic HVAC call transcripts")
    parser.add_argument("--force", action="store_true", help="Regenerate even cached transcripts")
    parser.add_argument("--scenario", type=int, help="Generate one scenario by ID")
    raise SystemExit(main(parser.parse_args()))
