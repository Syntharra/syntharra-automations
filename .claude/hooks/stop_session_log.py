#!/usr/bin/env python3
"""
Hook: Stop (fires when Claude Code session ends)
1. Auto-commits and pushes any local changes to GitHub
2. Verifies a session log was pushed for today
3. Checks if session_end.py was run (INDEX.md entry for today)
4. Warns if FAILURES.md was updated without session_end.py being run
Never blocks — always exits 0. Warns loudly if something is missing.
"""
import sys, os, subprocess, pathlib
from datetime import datetime, timezone

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPO = "Syntharra/syntharra-automations"
LOG_PATH = "docs/session-logs"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs" / "session-logs" / "INDEX.md"
FAILURES_PATH = ROOT / "docs" / "FAILURES.md"

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
        print(f"\n[HOOK] Local changes detected -- auto-committing before session close")
        print(status_out[:500])  # show what's changing (truncated)

        run("git add -A", cwd=repo_root)
        commit_msg = f"chore(session): auto-backup local changes {TODAY}"
        code, out, err = run(f'git commit -m "{commit_msg}"', cwd=repo_root)
        if code == 0:
            print(f"   [OK] Committed: {commit_msg}")
        else:
            print(f"   [!]  Commit failed: {err}")

    # Push regardless (in case commits exist that aren't pushed)
    code, out, err = run("git push origin main", cwd=repo_root)
    if code == 0:
        print(f"   [OK] Pushed to GitHub (origin/main)")
    else:
        # Try current branch name
        _, branch, _ = run("git branch --show-current", cwd=repo_root)
        code2, out2, err2 = run(f"git push origin {branch}", cwd=repo_root)
        if code2 == 0:
            print(f"   [OK] Pushed to GitHub (origin/{branch})")
        else:
            print(f"   [!]  Push failed: {err2}")
            print("   Manual fix: git push origin main")
else:
    print("[!] HOOK: Not inside a git repo -- skipping auto-push")

# ── 2. Verify session log exists in GitHub ────────────────────────────────────
if TOKEN:
    try:
        import requests
        H = {"Authorization": f"token {TOKEN}"}
        r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{LOG_PATH}", headers=H)
        if r.ok:
            files = r.json()
            today_logs = [f["name"] for f in files if f["name"].startswith(TODAY)]
            if today_logs:
                print(f"\n[HOOK] Session log verified -- {today_logs[-1]}")
            else:
                print(f"\n[!] HOOK WARNING: No session log found for {TODAY}")
                print(f"   Required: {LOG_PATH}/{TODAY}-<topic>.md")
                print("   Per CLAUDE.md: session is NOT closed without a pushed log.")
        else:
            print(f"[!] HOOK: Could not verify session log (GitHub {r.status_code})")
    except Exception as e:
        print(f"[!] HOOK: Session log check failed -- {e}")
else:
    print("[!] HOOK: GITHUB_TOKEN not set -- cannot verify session log")
    print("   Add to Claude Code env: GITHUB_TOKEN=ghp_...")

# ── 3. Check if session_end.py was run today (INDEX.md entry) ────────────────
session_end_ran = False
if INDEX_PATH.exists():
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    session_end_ran = TODAY in index_text

if not session_end_ran:
    print(f"\n{'='*60}")
    print(f"  STOP HOOK WARNING: session_end.py NOT run for {TODAY}")
    print(f"  This is REQUIRED per RULES.md section 5.")
    print(f"  Run now:")
    print(f'    python tools/session_end.py --topic <slug> --summary "<one-line>"')
    print(f"  Without this: STATE.md is stale, INDEX.md is incomplete.")
    print(f"{'='*60}")
else:
    print(f"\n[HOOK] session_end.py confirmed run today ({TODAY}) -- INDEX.md entry found.")

# ── 4. Warn if FAILURES.md was modified in this session ──────────────────────
code, failures_diff, _ = run("git diff HEAD -- docs/FAILURES.md", cwd=repo_root)
if not failures_diff:
    code, failures_diff, _ = run("git diff --cached -- docs/FAILURES.md", cwd=repo_root)

if failures_diff and not session_end_ran:
    print("\n[HOOK] FAILURES.md was modified this session but session_end.py was not run.")
    print("   session_end.py checks that every FAILURES.md update has a matching RULES.md rule.")
    print("   Run session_end.py before closing.")

sys.exit(0)
