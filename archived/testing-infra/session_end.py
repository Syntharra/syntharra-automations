#!/usr/bin/env python3
"""
session_end.py - run at the end of every Cowork session.

Responsibilities:
  1. Refresh docs/STATE.md header (Last updated, Last commit, checklist count).
  2. Append a row to docs/session-logs/INDEX.md.
  3. Warn if docs/FAILURES.md changed since HEAD~1 without docs/RULES.md also changing.

Usage:
  python tools/session_end.py --topic standard-v4r1 --summary "resumed eval harness, 3 scenarios green"
"""
import argparse
import datetime as dt
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "docs" / "STATE.md"
INDEX = ROOT / "docs" / "session-logs" / "INDEX.md"
FAILURES = ROOT / "docs" / "FAILURES.md"
RULES = ROOT / "docs" / "RULES.md"
CHECKLIST = ROOT / "docs" / "pre-launch-checklist.md"


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
        raise RuntimeError("git not found on PATH or in GitHub Desktop")
    return subprocess.check_output([GIT, *args], cwd=ROOT, text=True).strip()


def get_last_commit():
    try:
        return sh("log", "-1", "--pretty=format:%h %s")
    except Exception as exc:
        return f"unknown ({exc})"


def count_checklist_status():
    if not CHECKLIST.exists():
        return "checklist missing"
    text = CHECKLIST.read_text(encoding="utf-8")
    done = len(re.findall(r"^\s*-\s*\[x\]", text, flags=re.MULTILINE | re.IGNORECASE))
    open_ = len(re.findall(r"^\s*-\s*\[ \]", text, flags=re.MULTILINE))
    total = done + open_
    if total == 0:
        return "no checklist items"
    return f"{done}/{total} items complete"


def refresh_state_file():
    if not STATE.exists():
        print(f"WARN: {STATE} not found", file=sys.stderr)
        return
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    commit = get_last_commit()
    checklist = count_checklist_status()
    text = STATE.read_text(encoding="utf-8")
    text = re.sub(r"^_Last updated:.*$", f"_Last updated: {today}_", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^## Last commit\n.*$", f"## Last commit\n{commit}", text, count=1, flags=re.MULTILINE)
    text = re.sub(
        r"^## Go-live checklist\n.*$",
        f"## Go-live checklist\n{checklist} (see docs/pre-launch-checklist.md)",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    STATE.write_text(text, encoding="utf-8")
    print(f"STATE.md refreshed: {today} | {commit} | {checklist}")


def append_session_log_index(topic, summary):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    commit = get_last_commit().split(" ", 1)[0] or "-"
    row = f"| {today} | {topic} | {commit} | {summary} |\n"
    if not INDEX.exists():
        header = (
            "# Session Logs - Index\n\n"
            "> Auto-maintained by tools/session_end.py. Do not hand-edit rows.\n\n"
            "| Date (UTC) | Topic | Last commit | Summary |\n"
            "|---|---|---|---|\n"
        )
        INDEX.write_text(header + row, encoding="utf-8")
    else:
        with INDEX.open("a", encoding="utf-8") as fh:
            fh.write(row)
    print(f"session-logs/INDEX.md appended: {topic}")


def check_new_failures():
    try:
        diff = sh("diff", "--name-only", "HEAD~1", "HEAD")
    except Exception:
        return
    changed = set(diff.splitlines())
    if "docs/FAILURES.md" in changed and "docs/RULES.md" not in changed:
        print(
            "REMINDER: docs/FAILURES.md changed but docs/RULES.md did not. "
            "If the failure implies a new standing rule, update RULES.md.",
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser(description="End-of-session bookkeeping for Syntharra automations.")
    parser.add_argument("--topic", required=True, help="Short slug for this session, e.g. standard-v4r1")
    parser.add_argument("--summary", required=True, help="One-line summary of what changed this session")
    args = parser.parse_args()
    refresh_state_file()
    append_session_log_index(args.topic, args.summary)
    check_new_failures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
