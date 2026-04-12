#!/usr/bin/env python3
"""
Hook: UserPromptSubmit
Auto-runs tools/session_start.py once per calendar day so Claude is always
oriented before responding — even if the developer forgets to run it manually.

Uses a per-day marker file in .claude/ to avoid re-running on every prompt.
Cleans up marker files older than 3 days automatically.
Never blocks — always exits 0.
"""
import sys
import json
import subprocess
import pathlib
import re
from datetime import datetime, timezone, timedelta

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
MARKER = ROOT / ".claude" / f".session-started-{TODAY}"


def cleanup_old_markers():
    """Remove marker files older than 3 days so they don't accumulate."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    for f in ROOT.glob(".claude/.session-started-*"):
        m = re.search(r"(\d{4}-\d{2}-\d{2})$", f.name)
        if m:
            try:
                file_date = datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if file_date < cutoff:
                    f.unlink(missing_ok=True)
            except ValueError:
                pass


try:
    cleanup_old_markers()

    if not MARKER.exists():
        MARKER.touch()
        result = subprocess.run(
            ["python", str(ROOT / "tools" / "session_start.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=20,
        )
        print("\n" + "=" * 64)
        print("  AUTO SESSION START — orienting before first response")
        print("=" * 64)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"[!] session_start.py stderr: {result.stderr[:300]}")
        print("")
        print("  READ BEFORE RESPONDING (in order):")
        print("  1. docs/STATE.md      — current reality, in-flight, blockers")
        print("  2. docs/RULES.md      — 56+ hard don'ts (violations = real incidents)")
        print("  3. docs/PLAYBOOKS.md  — HOW to do things correctly in this system")
        print("  4. docs/DECISIONS.md  — WHY architectural decisions were made")
        print("  5. docs/REFERENCE.md  — all IDs (sole source — never recall from memory)")
        print("  6. docs/FAILURES.md   — past incidents (skim last 10 rows)")
        print("=" * 64 + "\n")

except Exception as e:
    print(f"[!] session_auto_start hook error: {e}")

sys.exit(0)
