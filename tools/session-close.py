#!/usr/bin/env python3
"""
session-close.py - Mandatory end-of-session script for Claude Code.
Enforces hard gate questions, writes session log, pushes to GitHub.

Usage:
  python3 tools/session-close.py --topic "simulator-fixes"
  python3 tools/session-close.py --topic "prompt-updates" --skip-gate
"""
import requests, base64, os, sys, argparse
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
H = {"Authorization": f"token {TOKEN}"}
REPO = "syntharra-automations"

def get_sha(path):
    r = requests.get(f"https://api.github.com/repos/Syntharra/{REPO}/contents/{path}", headers=H).json()
    return r.get("sha")

def push_file(path, content, msg):
    sha = get_sha(path)
    body = {"message": msg, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        body["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/Syntharra/{REPO}/contents/{path}", headers=H, json=body)
    return r.status_code

def hard_gate():
    print("\n" + "="*60)
    print("HARD GATE - answer before closing")
    print("="*60)
    answers = {}
    questions = [
        ("failures",     "1. Anything break or fail this session?"),
        ("patterns",     "2. Correct pattern discovered by testing/failing?"),
        ("assumptions",  "3. Wrong assumption fixed?"),
        ("skills",       "4. Skill files updated where needed?"),
        ("architecture", "5. Any architectural choice not yet in ARCHITECTURE.md?"),
    ]
    for key, q in questions:
        print(f"\n{q}")
        answers[key] = input("  > ").strip()
    if answers.get("architecture", "no").lower().startswith("y"):
        print("\nARCHITECTURE decision flagged.")
        print("Update docs/ARCHITECTURE.md now, then press Enter.")
        input("  Press Enter when done... ")
    return answers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--work-done", default="See session transcript.")
    parser.add_argument("--skip-gate", action="store_true")
    args = parser.parse_args()

    print(f"\nSyntharra Session Close - {args.topic}")
    print(datetime.now().strftime("%Y-%m-%d %H:%M"))

    answers = ({k: "skipped" for k in ["failures","patterns","assumptions","skills","architecture"]}
               if args.skip_gate else hard_gate())

    date = datetime.now().strftime("%Y-%m-%d")
    log = f"""# Session Log - {date} - {args.topic}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Work Done
{args.work_done}

## Hard Gate
1. Failures: {answers.get("failures","n/a")}
2. Patterns: {answers.get("patterns","n/a")}
3. Assumptions: {answers.get("assumptions","n/a")}
4. Skills: {answers.get("skills","n/a")}
5. Architecture: {answers.get("architecture","n/a")}

## Next Priority
See docs/TASKS.md open items.
"""
    log_path = f"docs/session-logs/{date}-{args.topic}.md"
    print(f"\nPushing session log to {log_path}...")
    status = push_file(log_path, log, f"docs: session log {date} {args.topic}")

    if status in (200, 201):
        print("Session log pushed.")
    else:
        print(f"Push failed HTTP {status} - push manually before closing.")
        sys.exit(1)

    print("\nSession close complete.")

if __name__ == "__main__":
    main()
