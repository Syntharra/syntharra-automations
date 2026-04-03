#!/usr/bin/env python3
import sys, os, requests, base64

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "session.md"
DATE = sys.argv[2] if len(sys.argv) > 2 else "unknown-date"
TOPIC = sys.argv[3] if len(sys.argv) > 3 else "general"

TOKEN = os.environ.get("GITHUB_TOKEN", "")
H = {"Authorization": f"token {TOKEN}"}

with open(LOG_FILE) as f:
    content = f.read()

path = f"docs/session-logs/{DATE}-{TOPIC}.md"
existing = requests.get(f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{path}", headers=H).json()
sha = existing.get("sha")

body = {
    "message": f"docs: session log {DATE} {TOPIC}",
    "content": base64.b64encode(content.encode()).decode()
}
if sha:
    body["sha"] = sha

r = requests.put(f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{path}", headers=H, json=body)
if r.status_code in (200, 201):
    print(f"Session log pushed: {path}")
else:
    print(f"Push failed: {r.json()}")
    sys.exit(1)
