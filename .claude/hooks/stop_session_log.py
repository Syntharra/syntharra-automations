#!/usr/bin/env python3
"""
Hook: Stop (fires when Claude Code session ends)
Checks GitHub for a session log pushed today.
Warns (exit 0 — non-blocking) if no log found, because we cannot know
if the session was planned to close or not. Prints a clear reminder.
"""
import sys, json, requests
from datetime import datetime, timezone

TOKEN = None  # Loaded from env — hook reads GITHUB_TOKEN env var if set
import os
TOKEN = os.environ.get("GITHUB_TOKEN", "")

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPO = "Syntharra/syntharra-automations"
LOG_PATH = f"docs/session-logs"

try:
    if not TOKEN:
        print("⚠️  HOOK: GITHUB_TOKEN not set — cannot verify session log")
        sys.exit(0)

    H = {"Authorization": f"token {TOKEN}"}
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{LOG_PATH}", headers=H)
    
    if r.ok:
        files = r.json()
        today_logs = [f["name"] for f in files if f["name"].startswith(TODAY)]
        if today_logs:
            print(f"✅ HOOK: Session log verified — {today_logs[-1]}")
        else:
            print(f"\n⚠️  HOOK WARNING: No session log found for {TODAY}")
            print(f"   Required: docs/session-logs/{TODAY}-<topic>.md")
            print("   Per CLAUDE.md: session is NOT closed without a pushed log.")
    else:
        print(f"⚠️  HOOK: Could not verify session log (GitHub {r.status_code})")

except Exception as e:
    print(f"⚠️  HOOK: Session log check failed — {e}")

# Always exit 0 — warning only (cannot block if log genuinely not needed)
sys.exit(0)
