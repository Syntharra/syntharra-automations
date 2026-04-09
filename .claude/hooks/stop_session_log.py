#!/usr/bin/env python3
"""
Hook: Stop (fires when Claude Code session ends)

v2 — hardened after 2026-04-09 incident where the previous version swept
secret-laden untracked files onto a feature branch via `git add -A`.

Behaviour:
  1. If current branch != main: do nothing (except the session-log checks).
     Feature branches are for in-flight work with messy trees and MUST NOT
     be auto-committed. See FAILURES.md 2026-04-09 prompt-compiler row.
  2. On main with dirty working tree: `git add -u` (modifications to
     tracked files only — NEVER untracked), then scan the staged diff for
     secret patterns, then commit + push.
  3. Secret scan: if any pattern hits, ABORT the commit, leave the index
     dirty, print loud warning. Never auto-commits a leaking diff.
  4. Session-log + FAILURES.md checks always run (were already correct).

Never blocks the session — always exits 0. Warns loudly if something is
missing.
"""
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPO = "Syntharra/syntharra-automations"
LOG_PATH = "docs/session-logs"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs" / "session-logs" / "INDEX.md"
FAILURES_PATH = ROOT / "docs" / "FAILURES.md"

# Secret patterns — if any of these match the staged diff, abort the auto-commit.
# Kept deliberately broad; false positives are fine (we just skip auto-commit
# and let the human decide), false negatives are what got us in trouble.
SECRET_PATTERNS = [
    (r"xkeysib-[a-f0-9]{40,}", "Brevo"),
    (r"key_[a-f0-9]{20,}", "Retell-style key"),
    (r"sk_(live|test)_[A-Za-z0-9]{20,}", "Stripe"),
    (r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}", "JWT (Supabase/n8n)"),
    (r"xox[bps]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub PAT"),
    (r"AKIA[0-9A-Z]{16}", "AWS key"),
]


def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def get_repo_root():
    code, out, _ = run("git rev-parse --show-toplevel")
    return out if code == 0 else None


def scan_staged_diff_for_secrets(cwd):
    """Return list of (pattern_label, redacted_match) hits in staged diff."""
    code, diff, _ = run("git diff --cached", cwd=cwd)
    if code != 0 or not diff:
        return []
    hits = []
    for pat, label in SECRET_PATTERNS:
        for m in re.finditer(pat, diff):
            s = m.group()
            redacted = s[:8] + "..." + s[-4:] if len(s) > 14 else "***"
            hits.append((label, redacted))
    return hits


# ── 1. Auto-commit local changes to main (ONLY on main) ─────────────────────
repo_root = get_repo_root()
if repo_root:
    _, branch, _ = run("git branch --show-current", cwd=repo_root)

    if branch != "main":
        print(f"[HOOK] On branch '{branch}' — auto-backup disabled on non-main branches.")
        print("       Feature branches stay clean until you commit + push them by hand.")
    else:
        # Only look at MODIFIED tracked files — never untracked. This is the
        # critical fix: `git add -u` will NEVER pull in `plugins/`, raw dumps,
        # __pycache__, etc., even if they're sitting in the tree.
        code, status_out, _ = run("git status --porcelain --untracked-files=no", cwd=repo_root)
        if status_out:
            print(f"\n[HOOK] Tracked-file changes on main — auto-committing")
            print(status_out[:500])

            run("git add -u", cwd=repo_root)

            # Second line of defence: scan the staged diff for secrets.
            hits = scan_staged_diff_for_secrets(repo_root)
            if hits:
                print("\n[HOOK] !!! SECRET PATTERN MATCH IN STAGED DIFF — ABORTING AUTO-COMMIT !!!")
                for label, red in hits[:10]:
                    print(f"   {label}: {red}")
                if len(hits) > 10:
                    print(f"   ... and {len(hits) - 10} more")
                print("\n   The index has been left dirty. Review with `git diff --cached`")
                print("   and either `git restore --staged <file>` the offenders or commit")
                print("   manually once they're removed. Nothing was committed or pushed.")
            else:
                msg = f"chore(session): auto-backup local changes {TODAY}"
                code, _, err = run(f'git commit -m "{msg}"', cwd=repo_root)
                if code == 0:
                    print(f"   [OK] Committed: {msg}")
                    code, _, err = run("git push origin main", cwd=repo_root)
                    if code == 0:
                        print("   [OK] Pushed to GitHub (origin/main)")
                    else:
                        # Note: we deliberately do NOT fall back to pushing
                        # the current branch. See FAILURES.md 2026-04-09.
                        print(f"   [!]  Push to origin/main failed: {err}")
                        print("   Manual fix: git push origin main")
                else:
                    print(f"   [!]  Commit failed: {err}")
        else:
            # No tracked changes — nothing to back up. Untracked files are
            # the user's problem, not ours.
            pass
else:
    print("[!] HOOK: Not inside a git repo — skipping auto-backup")

# ── 2. Verify session log exists in GitHub ───────────────────────────────────
if TOKEN:
    try:
        import requests
        H = {"Authorization": f"token {TOKEN}"}
        r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{LOG_PATH}", headers=H)
        if r.ok:
            files = r.json()
            today_logs = [f["name"] for f in files if f["name"].startswith(TODAY)]
            if today_logs:
                print(f"\n[HOOK] Session log verified — {today_logs[-1]}")
            else:
                print(f"\n[!] HOOK WARNING: No session log found for {TODAY}")
                print(f"   Required: {LOG_PATH}/{TODAY}-<topic>.md")
                print("   Per CLAUDE.md: session is NOT closed without a pushed log.")
        else:
            print(f"[!] HOOK: Could not verify session log (GitHub {r.status_code})")
    except Exception as e:
        print(f"[!] HOOK: Session log check failed — {e}")
else:
    print("[!] HOOK: GITHUB_TOKEN not set — cannot verify session log")

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
    print(f"\n[HOOK] session_end.py confirmed run today ({TODAY}) — INDEX.md entry found.")

# ── 4. Warn if FAILURES.md was modified in this session ──────────────────────
if repo_root:
    code, failures_diff, _ = run("git diff HEAD -- docs/FAILURES.md", cwd=repo_root)
    if not failures_diff:
        code, failures_diff, _ = run("git diff --cached -- docs/FAILURES.md", cwd=repo_root)
    if failures_diff and not session_end_ran:
        print("\n[HOOK] FAILURES.md was modified this session but session_end.py was not run.")
        print("   session_end.py checks that every FAILURES.md update has a matching RULES.md rule.")
        print("   Run session_end.py before closing.")

sys.exit(0)
