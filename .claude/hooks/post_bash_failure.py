#!/usr/bin/env python3
"""
Hook: PostToolUse -> Bash
When a bash command fails, writes to session-failures.log and prints
a structured self-improvement prompt so Claude logs and learns from it.
Never blocks — always exits 0.
"""
import sys
import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / ".claude" / "session-failures.log"

FAILURE_SIGNALS = [
    "Exit code 1", "Exit code 2", "Exit code 127", "Exit code 128",
    "returned non-zero exit status",
    "Traceback (most recent call last)",
    "ERROR:", "Error:", "FAILED",
    "ModuleNotFoundError", "ImportError", "SyntaxError",
    "ConnectionError", "TimeoutError", "HTTPError",
    "Permission denied", "No such file or directory",
]

# Noise signals — transient failures not worth logging
NOISE_SIGNALS = [
    "already exists", "Nothing to commit",
    "already up to date", "no changes added",
]

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    response = data.get("tool_response", "")

    if isinstance(response, dict):
        is_error = response.get("is_error", False)
        content = str(response.get("content", ""))
    else:
        is_error = False
        content = str(response)

    text_failure = any(sig in content for sig in FAILURE_SIGNALS)
    is_noise = any(sig in content for sig in NOISE_SIGNALS)

    if (is_error or text_failure) and not is_noise:
        # Write to session failure log
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        cmd_short = command[:150].replace("\n", " ") + ("..." if len(command) > 150 else "")
        err_short = content[:300] + ("..." if len(content) > 300 else "")

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\nCMD: {cmd_short}\nERR: {err_short}\n---\n")

        print("\n[HOOK: bash-failure] Non-trivial failure detected.")
        print("  Follow self-improvement-SKILL.md steps 1-3:")
        print("  1. Capture: What failed / Root cause / Fix / Rule implied")
        print("  2. Append entry to docs/FAILURES.md")
        print("  3. Memory auto-updates when FAILURES.md is saved (post_edit_failures hook)")
        print(f"  Logged to: .claude/session-failures.log")

except Exception:
    pass

sys.exit(0)
