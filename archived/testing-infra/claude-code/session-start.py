#!/usr/bin/env python3
import os, sys, requests, base64
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    print("ERROR: GITHUB_TOKEN env var not set")
    sys.exit(1)

H = {"Authorization": f"token {TOKEN}"}
REPO = "syntharra-automations"

def fetch(path):
    r = requests.get(f"https://api.github.com/repos/Syntharra/{REPO}/contents/{path}", headers=H).json()
    if "content" in r:
        return base64.b64decode(r["content"]).decode()
    return f"ERROR: {r.get('message', 'unknown')}"

print("=" * 60)
print("SYNTHARRA — Claude Code Session Start")
print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
print("=" * 60)

print("\n[1/4] Loading CLAUDE.md...")
claude_md = fetch("CLAUDE.md")
print("  OK — CLAUDE.md loaded ({} chars)".format(len(claude_md)))

print("\n[2/4] Loading TASKS.md — open items:")
tasks_md = fetch("docs/TASKS.md")
in_open = False
for line in tasks_md.split("\n"):
    if "Open Action Items" in line:
        in_open = True
    if in_open and line.startswith("## ") and "Open Action Items" not in line:
        break
    if in_open and line.strip():
        print("  " + line)

print("\n[3/4] Loading FAILURES.md — last 5 entries:")
failures_md = fetch("docs/FAILURES.md")
rows = [l for l in failures_md.split("\n") if l.startswith("| 2026")]
for row in rows[-5:]:
    print("  " + row[:120])

print("\n[4/4] Loading DECISIONS.md...")
fetch("docs/DECISIONS.md")
print("  OK — DECISIONS.md loaded")

print("\n" + "=" * 60)
print("Context loaded. Rules active. TESTING agents only.")
print("E2E must pass before any production push.")
print("=" * 60)
