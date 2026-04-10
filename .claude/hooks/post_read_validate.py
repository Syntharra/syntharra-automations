#!/usr/bin/env python3
"""
Hook: PostToolUse -> Read, Edit, Write
Checks the file path being read or edited against .claude/canonical-paths.json.
If a known-wrong path is accessed, prints a loud warning immediately so Claude
can self-correct before responding to the user.

This catches wrong-file mistakes at the moment they happen, not after the user
notices and corrects them.

Never blocks — always exits 0.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = ROOT / ".claude" / "canonical-paths.json"


def normalise(path: str) -> str:
    """Normalise path separators for consistent matching."""
    return path.replace("\\", "/").lower()


def check_path(file_path: str) -> list[dict]:
    """Return any canonical-paths violations for this file path."""
    if not CANONICAL.exists():
        return []
    try:
        config = json.loads(CANONICAL.read_text(encoding="utf-8"))
    except Exception:
        return []

    norm = normalise(file_path)
    hits = []
    for entry in config.get("wrong_paths", []):
        wrong = normalise(entry.get("wrong_pattern", ""))
        must_not = entry.get("must_not_match")

        if not wrong:
            continue
        if wrong not in norm:
            continue
        # If must_not_match is set, only fire when the path does NOT contain the correct version
        if must_not and normalise(must_not) in norm:
            continue

        hits.append(entry)
    return hits


try:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    file_path = str(
        tool_input.get("file_path", "") or
        tool_input.get("path", "") or
        ""
    ).strip()

    if file_path:
        violations = check_path(file_path)
        if violations:
            print("\n" + "!" * 66)
            print("  PATH VALIDATOR WARNING — wrong file detected")
            print("!" * 66)
            for v in violations:
                print(f"\n  Wrong:    {file_path}")
                print(f"  Correct:  {v['canonical']}")
                print(f"  Reason:   {v['reason']}")
            print("\n  STOP — use the canonical path above before continuing.")
            print("!" * 66 + "\n")

except Exception:
    pass

sys.exit(0)
