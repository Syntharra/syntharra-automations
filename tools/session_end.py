#!/usr/bin/env python3
"""
session_end.py - run at the end of every Cowork session.

1. Refreshes STATE.md header (last updated, last commit)
2. Appends a row to docs/session-logs/INDEX.md
3. Creates a session log file docs/session-logs/YYYY-MM-DD-<topic>.md
4. Warns if FAILURES.md was updated without a matching RULES.md change

Usage:
  python tools/session_end.py --topic <short-slug> --summary "<one-line>"

Example:
  python tools/session_end.py --topic agentic-setup --summary "Built self-improvement loop, hooks, weekly agent"
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE    = ROOT / "docs" / "STATE.md"
INDEX    = ROOT / "docs" / "session-logs" / "INDEX.md"
LOGS_DIR = ROOT / "docs" / "session-logs"
FAILURES = ROOT / "docs" / "FAILURES.md"
RULES    = ROOT / "docs" / "RULES.md"

BAR = "=" * 72


def find_git():
    git = shutil.which("git")
    if git:
        return git
    local = __import__("os").environ.get("LOCALAPPDATA", "")
    candidates = []
    if local:
        gh = pathlib.Path(local) / "GitHubDesktop"
        if gh.exists():
            for d in sorted(gh.glob("app-*"), reverse=True):
                candidates.append(d / "resources" / "app" / "git" / "cmd" / "git.exe")
    candidates += [
        pathlib.Path(r"C:\Program Files\Git\cmd\git.exe"),
        pathlib.Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


GIT = find_git()


def sh(*args, cwd=ROOT):
    if not GIT:
        return ""
    try:
        return subprocess.check_output(
            [GIT, *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def last_commit_sha():
    return sh("log", "-1", "--pretty=format:%h") or "unknown"


def last_commit_msg():
    return sh("log", "-1", "--pretty=format:%s") or ""


def update_state_header(today: str, sha: str):
    """Refresh the _Last updated_ and ## Last commit lines in STATE.md."""
    if not STATE.exists():
        print(f"  [!] STATE.md not found — skipping header refresh")
        return
    text = STATE.read_text(encoding="utf-8")

    # Update _Last updated_ line
    text = re.sub(
        r"^_Last updated:.*_$",
        f"_Last updated: {today}_",
        text,
        flags=re.MULTILINE,
    )
    # Update ## Last commit line (the line immediately after the header)
    text = re.sub(
        r"(^## Last commit\n).*$",
        rf"\g<1>{sha} {last_commit_msg()}",
        text,
        flags=re.MULTILINE,
    )
    STATE.write_text(text, encoding="utf-8")
    print(f"  [OK] STATE.md header refreshed (last updated: {today}, commit: {sha})")


def append_index_row(today: str, topic: str, sha: str, summary: str):
    """Append a new row to docs/session-logs/INDEX.md."""
    if not INDEX.exists():
        INDEX.write_text(
            "# Session Logs - Index\n\n"
            "> Auto-maintained by tools/session_end.py. Do not hand-edit rows.\n\n"
            "| Date (UTC) | Topic | Last commit | Summary |\n"
            "|---|---|---|---|\n",
            encoding="utf-8",
        )
    content = INDEX.read_text(encoding="utf-8")
    row = f"| {today} | {topic} | {sha} | {summary} |"
    # Don't duplicate: if today+topic already present, skip
    if f"| {today} | {topic} |" in content:
        print(f"  [--] INDEX.md already has entry for {today}/{topic} — skipping duplicate")
        return
    content = content.rstrip() + "\n" + row + "\n"
    INDEX.write_text(content, encoding="utf-8")
    print(f"  [OK] INDEX.md row appended: {today} | {topic}")


def create_session_log(today: str, topic: str, summary: str):
    """Create a minimal session log file if it doesn't already exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{today}-{topic}.md"
    if log_path.exists():
        print(f"  [--] Session log already exists: {log_path.name}")
        return
    log_path.write_text(
        f"# {today} — {topic.replace('-', ' ').title()}\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Done\n- (fill in or expand from session context)\n",
        encoding="utf-8",
    )
    print(f"  [OK] Session log created: docs/session-logs/{log_path.name}")


def write_next_session_priorities(priorities: str):
    """Write or replace the ## Next session — pick up here section in STATE.md."""
    if not STATE.exists() or not priorities.strip():
        return
    text = STATE.read_text(encoding="utf-8")
    section_header = "## Next session — pick up here"
    new_section = f"{section_header}\n{priorities.strip()}\n"

    if section_header in text:
        # Replace existing section
        text = re.sub(
            rf"^{re.escape(section_header)}\n.*?(?=\n## |\Z)",
            new_section,
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    else:
        # Insert before ## What's in flight (or append)
        if "## What's in flight" in text:
            text = text.replace("## What's in flight", f"{new_section}\n## What's in flight", 1)
        else:
            text = text.rstrip() + f"\n\n{new_section}"

    STATE.write_text(text, encoding="utf-8")
    print(f"  [OK] STATE.md 'Next session' priorities written")


def check_failures_rules_parity():
    """Warn if FAILURES.md has new entries whose Rule: field isn't in RULES.md."""
    if not FAILURES.exists() or not RULES.exists():
        return
    failures_text = FAILURES.read_text(encoding="utf-8")
    rules_text = RULES.read_text(encoding="utf-8")

    pattern = re.compile(r"\*\*Rule:\*\*\s*(.+?)(?:\n|$)")
    gaps = []
    for m in pattern.finditer(failures_text):
        rule = m.group(1).strip()
        if rule.lower() in ("none", "n/a", ""):
            continue
        # Check if any meaningful chunk of the rule text appears in RULES.md
        key = rule[:40].lower()
        if key not in rules_text.lower():
            gaps.append(rule)

    if gaps:
        print(f"\n  [!] RULES.md parity warning — {len(gaps)} FAILURES rule(s) not found in RULES.md:")
        for g in gaps[:5]:
            print(f"      - {g[:80]}")
        print("  Add these to docs/RULES.md before closing.")
    else:
        print("  [OK] FAILURES.md <-> RULES.md parity check passed")


def main():
    parser = argparse.ArgumentParser(description="Close a Syntharra Cowork session")
    parser.add_argument("--topic", required=True, help="Short slug for this session (e.g. agentic-setup)")
    parser.add_argument("--summary", required=True, help="One-line summary of what was done")
    parser.add_argument("--priorities", default="", help="Next session priorities (multiline ok, use \\n)")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sha = last_commit_sha()

    print(BAR)
    print(f"SESSION END -- {today} | topic: {args.topic}")
    print(BAR)

    update_state_header(today, sha)
    append_index_row(today, args.topic, sha, args.summary)
    create_session_log(today, args.topic, args.summary)
    if args.priorities:
        priorities_text = args.priorities.replace("\\n", "\n")
        write_next_session_priorities(priorities_text)
    check_failures_rules_parity()

    print()
    print(f"  Session closed. Stop hook will auto-commit and push on exit.")
    print(BAR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
