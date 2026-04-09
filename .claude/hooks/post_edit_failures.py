#!/usr/bin/env python3
"""
Hook: PostToolUse -> Edit, Write
When FAILURES.md is edited, AUTOMATICALLY extracts the newest failure entry
and writes it into memory/feedback_anti_patterns.md — no human step required.

Also fires when RULES.md is edited — checks if memory already reflects the rule.
Never blocks — always exits 0.
"""
import sys
import json
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILURES_PATH = ROOT / "docs" / "FAILURES.md"
RULES_PATH = ROOT / "docs" / "RULES.md"
MEMORY_DIR = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory"
)
ANTI_PATTERNS = MEMORY_DIR / "feedback_anti_patterns.md"

# Map area keywords -> section header in feedback_anti_patterns.md
AREA_SECTIONS = {
    "retell":      "## Retell rules",
    "n8n":         "## n8n rules",
    "supabase":    "## Supabase rules",
    "credential":  "## Credential / security rules",
    "secret":      "## Credential / security rules",
    "token":       "## Credential / security rules",
    "api key":     "## Credential / security rules",
    "github":      "## GitHub MCP rules",
    "testing":     "## Testing rules",
    "test":        "## Testing rules",
    "email":       "## n8n rules",
    "slack":       "## n8n rules",
    "stripe":      "## Credential / security rules",
    "id":          "## ID / reference rules",
    "reference":   "## ID / reference rules",
}


def infer_section(text: str) -> str:
    lower = text.lower()
    for keyword, section in AREA_SECTIONS.items():
        if keyword in lower:
            return section
    return "## General rules"


def extract_last_section_failure(text: str) -> dict | None:
    """Parse the last ## YYYY-MM-DD section from FAILURES.md."""
    pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) — (.+?)$(.*?)(?=^## \d{4}|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    m = matches[-1]
    date = m.group(1)
    title = m.group(2).strip()
    body = m.group(3)

    def extract_field(label: str) -> str:
        match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)", body)
        return match.group(1).strip() if match else ""

    return {
        "date": date,
        "title": title,
        "symptom": extract_field("What failed") or title,
        "root_cause": extract_field("Root cause"),
        "fix": extract_field("Fix"),
        "rule": extract_field("Rule"),
    }


def already_in_memory(content: str, failure: dict) -> bool:
    """Rough dedup — check if the key symptom phrase is already in memory."""
    needle = failure["title"][:40].lower()
    symptom_needle = failure["symptom"][:40].lower()
    return needle in content.lower() or symptom_needle in content.lower()


def append_failure_to_memory(failure: dict) -> bool:
    """Auto-write the failure rule into feedback_anti_patterns.md."""
    if not ANTI_PATTERNS.exists():
        return False

    content = ANTI_PATTERNS.read_text(encoding="utf-8")

    if already_in_memory(content, failure):
        return False  # Already captured

    rule_text = failure["rule"]
    if not rule_text or rule_text.lower() in ("none", "n/a", ""):
        rule_text = failure["fix"]
    if not rule_text:
        return False  # Nothing useful to write

    section = infer_section(
        failure["title"] + " " + failure["symptom"] + " " + failure["root_cause"]
    )

    entry = (
        f"\n**{rule_text}**\n"
        f"**Why:** {failure['date']} — {failure['root_cause'] or failure['symptom']}\n"
        f"**How to apply:** Logged from FAILURES.md: \"{failure['title']}\". "
        f"Refine this entry if the wording is too generic.\n"
    )

    # Insert under the correct section header (after the header line)
    sec_pattern = re.compile(rf"^{re.escape(section)}$", re.MULTILINE)
    if sec_pattern.search(content):
        new_content = sec_pattern.sub(section + "\n" + entry.strip(), content, count=1)
    else:
        # Section doesn't exist yet — append it
        new_content = content.rstrip() + f"\n\n{section}\n\n" + entry.strip() + "\n"

    ANTI_PATTERNS.write_text(new_content, encoding="utf-8")
    return True


try:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    file_path = str(
        tool_input.get("file_path", "") or tool_input.get("path", "")
    )

    if "FAILURES.md" in file_path:
        if FAILURES_PATH.exists():
            text = FAILURES_PATH.read_text(encoding="utf-8")
            failure = extract_last_section_failure(text)
            if failure:
                updated = append_failure_to_memory(failure)
                if updated:
                    print("\n[HOOK: failures-memory] Auto-wrote rule to memory/feedback_anti_patterns.md")
                    print(f"  Entry: \"{failure['title']}\" ({failure['date']})")
                    print("  [ ] Still TODO: add matching rule to docs/RULES.md if standing rule implied")
                else:
                    print("\n[HOOK: failures-memory] FAILURES.md updated — entry already in memory or no rule text.")
                    print("  [ ] Still TODO: add matching rule to docs/RULES.md if standing rule implied")

    elif "RULES.md" in file_path:
        # Just remind — rules are already in RULES.md, memory is the secondary store
        print("\n[HOOK: failures-memory] RULES.md updated.")
        print("  Memory (feedback_anti_patterns.md) is auto-updated from FAILURES.md edits.")
        print("  If this rule has no matching FAILURES.md entry, consider adding one.")

except Exception:
    pass

sys.exit(0)
