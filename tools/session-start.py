#!/usr/bin/env python3
"""
session-start.py - Run at the start of every Claude Code session.
Fetches CLAUDE.md, TASKS.md, FAILURES.md, DECISIONS.md and prints a session brief.
"""
import requests, base64, os
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
H = {"Authorization": f"token {TOKEN}"}
REPO = "syntharra-automations"

def fetch(path):
    r = requests.get(f"https://api.github.com/repos/Syntharra/{REPO}/contents/{path}", headers=H).json()
    if "content" in r:
        return base64.b64decode(r["content"]).decode()
    return f"[NOT FOUND: {path}]"

print("=" * 60)
print(f"SYNTHARRA - Claude Code Session Start")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

print("\n[1/4] Fetching CLAUDE.md...")
claude = fetch("CLAUDE.md")
print(f"  OK ({len(claude)} chars)")

print("[2/4] Fetching TASKS.md - open items:")
tasks = fetch("docs/TASKS.md")
if "## Open Action Items" in tasks:
    section = tasks[tasks.find("## Open Action Items"):]
    print(section[:600])
else:
    print(tasks[:400])

print("\n[3/4] Fetching FAILURES.md - last 8 entries:")
failures = fetch("docs/FAILURES.md")
lines = [l for l in failures.split("\n") if l.strip()]
for line in lines[-8:]:
    print(f"  {line}")

print("\n[4/4] Fetching DECISIONS.md...")
decisions = fetch("docs/DECISIONS.md")
print(f"  OK ({len(decisions.split(chr(10)))} lines)")

print("\n" + "=" * 60)
print("SAFETY REMINDERS")
print("  MASTER agents - NEVER TOUCH:")
print("    Standard: agent_4afbfdb3fcb1ba9569353af28d")
print("    Premium:  agent_9822f440f5c3a13bc4d283ea90")
print("  TESTING agents - all work goes here:")
print("    Standard: agent_731f6f4d59b749a0aa11c26929")
print("    Premium:  agent_2cffe3d86d7e1990d08bea068f")
print("  Run E2E before any production push")
print("  Run tools/session-close.py before ending session")
print("=" * 60)
print("\nContext loaded. Ready.")
