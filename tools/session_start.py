#!/usr/bin/env python3
"""
session_start.py - run at the start of every Cowork session.

Prints a ~15-line orientation block so Claude can pick up exactly where the last
session left off, without re-reading the entire repo.

Output:
  - Current branch and last commit
  - Last row from docs/session-logs/INDEX.md (previous session's topic + summary)
  - Last 3 rows from docs/FAILURES.md (most recent incidents)
  - First "in flight" + "next session" section from docs/STATE.md
  - Unstaged / uncommitted files (if any)

Usage:
  python tools/session_start.py
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs" / "session-logs" / "INDEX.md"
FAILURES = ROOT / "docs" / "FAILURES.md"
STATE = ROOT / "docs" / "STATE.md"

BAR = "=" * 72


def find_git():
    """Find git executable. PATH first, then common Windows GitHub Desktop locations."""
    git = shutil.which("git")
    if git:
        return git
    candidates = []
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        gh_desktop = pathlib.Path(local) / "GitHubDesktop"
        if gh_desktop.exists():
            for app_dir in sorted(gh_desktop.glob("app-*"), reverse=True):
                candidates.append(app_dir / "resources" / "app" / "git" / "cmd" / "git.exe")
    candidates.extend([
        pathlib.Path(r"C:\Program Files\Git\cmd\git.exe"),
        pathlib.Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
    ])
    for c in candidates:
        if c.exists():
            return str(c)
    return None


GIT = find_git()


def sh(*args):
    if not GIT:
        return ""
    try:
        return subprocess.check_output([GIT, *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def print_header():
    branch = sh("rev-parse", "--abbrev-ref", "HEAD") or "?"
    commit = sh("log", "-1", "--pretty=format:%h %s") or "?"
    print(BAR)
    print(f"BRANCH: {branch}")
    print(f"HEAD:   {commit}")
    print(BAR)


def print_last_session():
    if not INDEX.exists():
        print("LAST SESSION: (no session-logs/INDEX.md yet)")
        return
    lines = [l for l in INDEX.read_text(encoding="utf-8").splitlines() if l.startswith("|") and not l.startswith("| Date") and not l.startswith("|---")]
    if not lines:
        print("LAST SESSION: (no rows)")
        return
    print("LAST SESSION:")
    print(f"  {lines[-1]}")


def print_recent_failures(n=3):
    if not FAILURES.exists():
        print("RECENT FAILURES: (no FAILURES.md)")
        return
    lines = [l for l in FAILURES.read_text(encoding="utf-8").splitlines() if l.startswith("|") and not l.startswith("| Date") and not l.startswith("|---")]
    if not lines:
        print("RECENT FAILURES: (none)")
        return
    print(f"LAST {min(n, len(lines))} FAILURES:")
    for row in lines[-n:]:
        short = row[:180] + ("..." if len(row) > 180 else "")
        print(f"  {short}")


def print_state_sections():
    if not STATE.exists():
        print("STATE: (no STATE.md)")
        return
    text = STATE.read_text(encoding="utf-8")

    def extract(header):
        m = re.search(rf"^## {re.escape(header)}\n(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
        return m.group(1).strip() if m else ""

    in_flight = extract("What's in flight")
    next_session = extract("Next session — pick up here")
    blocked = extract("What's blocked")

    if in_flight:
        print("IN FLIGHT:")
        for line in in_flight.splitlines()[:6]:
            if line.strip():
                print(f"  {line}")
    if blocked:
        print("BLOCKED:")
        for line in blocked.splitlines()[:4]:
            if line.strip():
                print(f"  {line}")
    if next_session:
        print("NEXT SESSION:")
        for line in next_session.splitlines()[:6]:
            if line.strip():
                print(f"  {line}")


def print_dirty_state():
    status = sh("status", "--short")
    if status:
        print("UNCOMMITTED:")
        for line in status.splitlines()[:10]:
            print(f"  {line}")
    else:
        print("UNCOMMITTED: (clean)")


def main():
    print_header()
    print_last_session()
    print()
    print_recent_failures()
    print()
    print_state_sections()
    print()
    print_dirty_state()
    print(BAR)
    print("Now read: docs/SESSION_START.md -> STATE.md -> RULES.md -> REFERENCE.md -> FAILURES.md")
    print(BAR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
