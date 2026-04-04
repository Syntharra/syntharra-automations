#!/usr/bin/env python3
"""
Hook: Stop (fires when Claude Code session ends)
1. Auto-commits and pushes any local changes to GitHub
2. Verifies a session log was pushed for today
Never blocks — always exits 0. Warns loudly if something is missing.
"""
import sys, os, subprocess, requests
from datetime import datetime, timezone

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPO = "Syntharra/syntharra-automations"
LOG_PATH = "docs/session-logs"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root():
    code, out, _ = run("git rev-parse --show-toplevel")
    return out if code == 0 else None

# ── 1. Auto-push local changes ────────────────────────────────────────────────
repo_root = get_repo_root()
if repo_root:
    # Check for uncommitted changes
    code, status_out, _ = run("git status --porcelain", cwd=repo_root)
    if status_out:
        print(f"\n📦 HOOK: Local changes detected — auto-committing before session close")
        print(status_out[:500])  # show what's changing (truncated)

        run("git add -A", cwd=repo_root)
        commit_msg = f"chore(session): auto-backup local changes {TODAY}"
        code, out, err = run(f'git commit -m "{commit_msg}"', cwd=repo_root)
        if code == 0:
            print(f"   ✅ Committed: {commit_msg}")
        else:
            print(f"   ⚠️  Commit failed: {err}")

    # Push regardless (in case commits exist that aren't pushed)
    code, out, err = run("git push origin main", cwd=repo_root)
    if code == 0:
        print(f"   ✅ Pushed to GitHub (origin/main)")
    else:
        # Try current branch name
        _, branch, _ = run("git branch --show-current", cwd=repo_root)
        code2, out2, err2 = run(f"git push origin {branch}", cwd=repo_root)
        if code2 == 0:
            print(f"   ✅ Pushed to GitHub (origin/{branch})")
        else:
            print(f"   ⚠️  Push failed: {err2}")
            print("   Manual fix: git push origin main")
else:
    print("⚠️  HOOK: Not inside a git repo — skipping auto-push")

# ── 2. Verify session log exists in GitHub ────────────────────────────────────
if TOKEN:
    try:
        H = {"Authorization": f"token {TOKEN}"}
        r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{LOG_PATH}", headers=H)
        if r.ok:
            files = r.json()
            today_logs = [f["name"] for f in files if f["name"].startswith(TODAY)]
            if today_logs:
                print(f"\n✅ HOOK: Session log verified — {today_logs[-1]}")
            else:
                print(f"\n⚠️  HOOK WARNING: No session log found for {TODAY}")
                print(f"   Required: {LOG_PATH}/{TODAY}-<topic>.md")
                print("   Per CLAUDE.md: session is NOT closed without a pushed log.")
        else:
            print(f"⚠️  HOOK: Could not verify session log (GitHub {r.status_code})")
    except Exception as e:
        print(f"⚠️  HOOK: Session log check failed — {e}")
else:
    print("⚠️  HOOK: GITHUB_TOKEN not set — cannot verify session log")
    print("   Add to Claude Code env: GITHUB_TOKEN=ghp_...")

sys.exit(0)
