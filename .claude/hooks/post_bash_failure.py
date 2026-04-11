#!/usr/bin/env python3
"""
Hook: PostToolUse -> Bash
When a bash command fails:
  1. Writes structured entry to .claude/session-failures.log
  2. Auto-appends a skeleton row to docs/FAILURES.md (with [TODO] markers)
     so the failure is captured even if Claude forgets to log it manually.
  3. If the root cause is auto-inferred (not a TODO), writes an anti-pattern
     rule directly into memory/feedback_anti_patterns.md so repeated failures
     teach standing rules without waiting for FAILURES.md to be filled in.
  4. Prints a reminder with the pre-filled skeleton for easy editing.

Never blocks — always exits 0.
"""
import sys
import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / ".claude" / "session-failures.log"
FAILURES_MD = ROOT / "docs" / "FAILURES.md"
MEMORY_DIR = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory"
)
ANTI_PATTERNS = MEMORY_DIR / "feedback_anti_patterns.md"

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

# Infer area from command/error text
AREA_HINTS = {
    "retell": "retell",
    "n8n": "n8n",
    "supabase": "supabase",
    "stripe": "stripe",
    "git": "git",
    "python": "python",
    "npm": "npm",
    "curl": "api",
    "railway": "railway",
}

# Root cause patterns: (regex on combined cmd+err, inferred root cause string)
ROOT_CAUSE_PATTERNS = [
    (r"no such file or directory",        "Wrong file path — file doesn't exist at the specified location"),
    (r"modulenotfounderror|importerror",  "Missing Python dependency — package not installed in this environment"),
    (r"syntaxerror",                       "Python syntax error in the script"),
    (r"permission denied",                 "Insufficient filesystem or execution permissions"),
    (r"command not found|exit code 127",  "Command not on PATH or not installed"),
    (r"connection(error|refused)|timeout","Service unreachable — check if the target service is running"),
    (r"401|unauthorized",                  "Invalid or missing auth credentials"),
    (r"403|forbidden",                     "Auth token lacks required permissions for this operation"),
    (r"404|not found",                     "Endpoint or resource doesn't exist — check URL and IDs"),
    (r"400|bad request",                   "Malformed request body — check required fields and types"),
    (r"500|internal server error",         "Server-side error — check service logs"),
    (r"git.*conflict|merge conflict",      "Git merge conflict — manual resolution required"),
    (r"nothing to commit",                 "No tracked changes staged — nothing to commit"),
    (r"json.*decode|jsondecodeerror",      "Invalid JSON in response or input"),
    (r"keyerror|attributeerror",           "Missing key or attribute — check data shape matches expected schema"),
    (r"typeerror",                          "Type mismatch — check argument types being passed"),
    (r"ssl|certificate",                   "SSL/TLS certificate issue — check cert validity or trust store"),
]


# Map area -> section header in feedback_anti_patterns.md
AREA_SECTION_MAP = {
    "retell":   "## Retell rules",
    "n8n":      "## n8n rules",
    "supabase": "## Supabase rules",
    "stripe":   "## Credential / security rules",
    "railway":  "## n8n rules",
    "api":      "## General rules",
    "git":      "## General rules",
    "python":   "## General rules",
    "npm":      "## General rules",
    "general":  "## General rules",
}


def infer_area(cmd: str, err: str) -> str:
    combined = (cmd + " " + err).lower()
    for keyword, area in AREA_HINTS.items():
        if keyword in combined:
            return area
    return "general"


def infer_root_cause(cmd: str, err: str) -> str:
    import re
    combined = (cmd + " " + err).lower()
    for pattern, cause in ROOT_CAUSE_PATTERNS:
        if re.search(pattern, combined):
            return cause
    return "[TODO: root cause — fill in before session close]"


def skeleton_row(today: str, area: str, cmd_short: str, err_short: str, root_cause: str) -> str:
    what = f"bash failure — {err_short[:80]}"
    fix = "[TODO: fix applied]" if "[TODO" in root_cause else "See session-failures.log"
    return (
        f"\n{today} | {area} | {what} | "
        f"{root_cause} | {fix} | no\n"
    )


def write_failure_to_memory(area: str, root_cause: str, cmd_short: str, today: str) -> bool:
    """
    Write a standing anti-pattern rule to feedback_anti_patterns.md when the
    root cause is auto-inferred (not a TODO).  Deduplicated by root_cause text.
    Returns True if a new entry was written.
    """
    import re as _re
    if not ANTI_PATTERNS.exists():
        return False

    content = ANTI_PATTERNS.read_text(encoding="utf-8")

    # Dedup: skip if the first 60 chars of root_cause already appear in memory
    needle = root_cause[:60].lower()
    if needle in content.lower():
        return False

    section = AREA_SECTION_MAP.get(area, "## General rules")

    entry = (
        f"\n**{root_cause}**\n"
        f"**Why:** Auto-captured from bash failure on {today} — "
        f"command: `{cmd_short[:80]}`\n"
        f"**How to apply:** Before running similar commands, verify this condition "
        f"is met to avoid the same failure. Update wording if too generic.\n"
    )

    sec_pattern = _re.compile(rf"^{_re.escape(section)}$", _re.MULTILINE)
    if sec_pattern.search(content):
        new_content = sec_pattern.sub(section + "\n" + entry.strip(), content, count=1)
    else:
        new_content = content.rstrip() + f"\n\n{section}\n\n" + entry.strip() + "\n"

    ANTI_PATTERNS.write_text(new_content, encoding="utf-8")
    return True


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
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cmd_short = command[:120].replace("\n", " ") + ("..." if len(command) > 120 else "")
        err_short = content[:200] + ("..." if len(content) > 200 else "")
        area = infer_area(command, content)
        root_cause = infer_root_cause(command, content)
        has_todo = "[TODO" in root_cause

        # 1. Write to session-failures.log
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\nCMD: {cmd_short}\nERR: {err_short}\nROOT CAUSE: {root_cause}\n---\n")

        # 2. Auto-append row to FAILURES.md (pre-filled where possible)
        skeleton = skeleton_row(today, area, cmd_short, err_short, root_cause)
        if FAILURES_MD.exists():
            with open(FAILURES_MD, "a", encoding="utf-8") as f:
                f.write(skeleton)

        # 3. If root cause is known, write anti-pattern rule directly to memory
        #    (don't wait for a human to fill in the FAILURES.md TODO markers)
        wrote_to_memory = False
        if not has_todo:
            wrote_to_memory = write_failure_to_memory(area, root_cause, cmd_short, today)

        # 4. Print structured reminder
        print("\n[HOOK: bash-failure] Failure captured — row added to FAILURES.md.")
        print(f"  Area:       {area}")
        print(f"  Root cause: {root_cause}")
        if has_todo:
            print("  ACTION: Root cause could not be inferred — fill in [TODO] in FAILURES.md.")
            print("  Memory auto-updates when you save FAILURES.md (post_edit_failures hook).")
        else:
            print("  ACTION: Root cause auto-inferred. Verify it's accurate in FAILURES.md.")
            if wrote_to_memory:
                print("  Memory: Anti-pattern rule written to feedback_anti_patterns.md.")
            else:
                print("  Memory: Rule already in feedback_anti_patterns.md — skipped dedup.")

except Exception:
    pass

sys.exit(0)
