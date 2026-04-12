#!/usr/bin/env python3
"""
Hook: UserPromptSubmit
Detects when the user is correcting Claude mid-session and automatically:
  1. Appends the raw correction to .claude/session-corrections.log
  2. Writes a structured entry to memory/feedback_anti_patterns.md

This means every correction teaches a future rule without any manual step.
Never blocks — always exits 0.
"""
import sys
import json
import re
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_LOG = ROOT / ".claude" / "session-corrections.log"
MEMORY_DIR = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory"
)
ANTI_PATTERNS = MEMORY_DIR / "feedback_anti_patterns.md"

SECTION = "## Process / workflow corrections"

# Patterns that reliably signal a user correction (not just a question or request)
CORRECTION_PATTERNS = [
    r"\bdon'?t\b.{0,40}\b(again|ever|always|that)\b",
    r"\bstop\b.{0,30}\b(doing|using|reading|calling|that|making)\b",
    r"\bwrong\b.{0,40}\b(file|path|version|approach|place|one|tool|way|method)\b",
    r"\byou'?re?\s+(reading|using|looking\s+at)\s+the\s+wrong\b",
    r"\bold\s+version\b",
    r"\bcome\s+on\b",
    r"\bnever\b.{0,30}\b(do|use|call|read|touch|make)\b",
    r"\bi\s+told\s+you\b",
    r"\bplease\s+don'?t\b",
    r"\bsame\s+mistake\b",
    r"\bnot\s+(that|the right|the old|the wrong)\b",
    r"\blearn\s+from\b",
    r"\bremember\s+(this|that|next\s+time)\b",
    r"\bfrom\s+now\s+on\b",
    r"\balways\s+(use|check|read|look)\b",
    # Additional patterns for corrections phrased as observations or directives
    r"\bthat'?s?\s+the\s+old\b",                          # "that's the old approach/version"
    r"\buse\s+the\s+right\b",                              # "use the right file/tool"
    r"\byou\s+(missed|skipped|forgot)\b",                  # "you missed the point"
    r"\bthat'?s?\s+(not|wrong)\b.{0,30}\b(right|correct|it|the)\b",  # "that's not right"
    r"\bwrong\s+(approach|tool|way|method|place|file)\b",  # "wrong approach"
    r"\bcheck\s+\w+\s+first\b",                           # "check REFERENCE.md first"
    r"\byou('?re|\s+are)\s+supposed\s+to\b",              # "you're supposed to use..."
    r"\bthat'?s?\s+not\s+how\b",                          # "that's not how it works"
    r"\bnot\s+that\s+(file|one|tool|approach|way)\b",     # "not that file"
    r"\b(read|check|look\s+at)\s+\w+\s+first\b",         # "read STATE.md first"
]

# Phrases that look like corrections but are genuinely questions or meta-requests — skip them.
# NOTE: "can you / could you / please / would you" are intentionally NOT blocked here —
# politely-phrased corrections like "could you stop doing that" or "please don't do X again"
# are real corrections and should be captured.
FALSE_POSITIVE_GUARDS = [
    r"^(what|how|why|when|where|which)\b",   # pure questions
    r"update\s+this\s+so\s+you\s+learn",     # meta-request like the one that built this hook
]


def is_correction(text: str) -> bool:
    lower = text.lower().strip()
    # Check strong correction signals first — these override false-positive guards
    strong_signals = [
        r"\bi\s+told\s+you\b",
        r"\bsame\s+mistake\b",
        r"\bfrom\s+now\s+on\b",
        r"\bnever\b.{0,30}\b(do|use|call|read|touch|make)\b",
    ]
    if any(re.search(p, lower) for p in strong_signals):
        return True
    # For all other patterns, still apply false-positive guards
    if any(re.match(p, lower) for p in FALSE_POSITIVE_GUARDS):
        return False
    return any(re.search(p, lower) for p in CORRECTION_PATTERNS)


def already_captured(content: str, prompt: str) -> bool:
    """Rough dedup — avoid re-writing the same correction."""
    needle = prompt[:60].lower()
    return needle in content.lower()


def write_to_corrections_log(prompt: str, timestamp: str):
    try:
        with open(CORRECTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n{prompt}\n---\n")
    except Exception:
        pass


def write_to_memory(prompt: str, today: str):
    if not ANTI_PATTERNS.exists():
        return

    content = ANTI_PATTERNS.read_text(encoding="utf-8")
    if already_captured(content, prompt):
        return

    entry = (
        f"\n**User correction ({today}):** \"{prompt[:250]}\"\n"
        f"**Why:** User directly corrected Claude's approach mid-session. "
        f"Derive the standing rule from this wording and add to the relevant section above.\n"
        f"**How to apply:** Before taking an action similar to what triggered this correction, "
        f"recall this feedback and choose the right path instead.\n"
    )

    if SECTION in content:
        # Insert after section header
        new_content = content.replace(SECTION, SECTION + "\n" + entry.strip(), 1)
    else:
        new_content = content.rstrip() + f"\n\n{SECTION}\n\n" + entry.strip() + "\n"

    ANTI_PATTERNS.write_text(new_content, encoding="utf-8")


try:
    data = json.load(sys.stdin)
    prompt = str(data.get("prompt", "")).strip()

    if len(prompt) >= 8 and is_correction(prompt):
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
        today = now.strftime("%Y-%m-%d")

        write_to_corrections_log(prompt, timestamp)
        write_to_memory(prompt, today)

        print(f"\n[HOOK: correction-capture] Correction detected — saved to memory & corrections log.")
        print(f"  \"{prompt[:100]}\"")
        print(f"  ACTION: Before closing session, distil this into a named rule in RULES.md.")

except Exception as e:
    print(f"[!] correction_capture hook error: {e}")

sys.exit(0)
