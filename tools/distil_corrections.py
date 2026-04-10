#!/usr/bin/env python3
"""
distil_corrections.py — Turns raw user corrections into standing rules.

Reads today's entries from .claude/session-corrections.log, then invokes
Claude Code CLI (`claude -p`) to distil each into an actionable rule written
directly to docs/RULES.md and memory/feedback_anti_patterns.md.

Uses the Claude Code subscription — no separate API key required.

Called automatically by stop_session_log.py at session end.
Manual run: python tools/distil_corrections.py
"""
from __future__ import annotations
import pathlib
import re
import sys
from datetime import datetime, timezone

HOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))
from hook_env import call_claude, claude_available, ROOT  # noqa: E402

TODAY            = datetime.now(timezone.utc).strftime("%Y-%m-%d")
CORRECTIONS_LOG  = ROOT / ".claude" / "session-corrections.log"
DISTILLED_LOG    = ROOT / ".claude" / "distilled-rules.log"
RULES_PATH       = ROOT / "docs" / "RULES.md"
MEMORY_ANTI      = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory\feedback_anti_patterns.md"
)


def parse_today_corrections() -> list[str]:
    if not CORRECTIONS_LOG.exists():
        return []
    text = CORRECTIONS_LOG.read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", text)
    results = []
    for block in blocks:
        block = block.strip()
        m = re.match(r"\[(\d{4}-\d{2}-\d{2})", block)
        if m and m.group(1) == TODAY:
            lines = block.splitlines()
            correction = "\n".join(lines[1:]).strip()
            if correction:
                results.append(correction)
    return results


def already_distilled(correction: str) -> bool:
    if not DISTILLED_LOG.exists():
        return False
    return correction[:60] in DISTILLED_LOG.read_text(encoding="utf-8")


def log_distilled(correction: str):
    with open(DISTILLED_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{TODAY}] {correction[:80]}\n")


def build_prompt(corrections: list[str]) -> str:
    corrections_block = "\n\n".join(f'"{c}"' for c in corrections)

    # Existing rule titles to avoid duplication
    existing_titles = ""
    if RULES_PATH.exists():
        titles = re.findall(r"^## \d+\. (.+)$", RULES_PATH.read_text(), re.MULTILINE)
        existing_titles = "\n".join(f"- {t}" for t in titles)

    next_num = 1
    if RULES_PATH.exists():
        nums = [int(m) for m in re.findall(r"^## (\d+)\.", RULES_PATH.read_text(), re.MULTILINE)]
        if nums:
            next_num = max(nums) + 1

    return f"""You are performing a self-improvement task for Syntharra Automations — an AI
receptionist SaaS for HVAC businesses (Retell AI + n8n + Supabase + Stripe + Brevo).

Today ({TODAY}), the developer made the following corrections to Claude's behaviour:

{corrections_block}

Existing rules already in docs/RULES.md (DO NOT duplicate these):
{existing_titles or "(none yet)"}

Your task:
1. For each correction above that implies a new rule NOT already in RULES.md:
   a. Append a new rule to docs/RULES.md starting at rule number {next_num}.
      Use this exact format (copy the style of existing rules in that file):

      ## {next_num}. <Short imperative title>

      - <One actionable sentence: Always X / Never Y / When Z, do W>
      - **Why:** <One sentence: what goes wrong if violated>

      _Source: distilled from user correction {TODAY}_

   b. Also append to {MEMORY_ANTI} under the relevant section header
      (## File paths | ## Process / workflow corrections | ## n8n rules | etc.)
      using this format:
      **<same rule sentence>**
      **Why:** {TODAY} — <same why sentence>
      **How to apply:** Derived from correction: "<first 80 chars of correction>"

2. If a correction is too vague or already covered, skip it.
3. Only add rules that are specific to the Syntharra codebase, not generic advice.
4. Read both files before editing so you append correctly without breaking existing content.

Do it now — read the files and write the new rules directly.
""".strip()


def main():
    if not claude_available():
        print("[distil_corrections] claude CLI not found on PATH — skipping distillation.")
        return 0

    corrections = parse_today_corrections()
    new_corrections = [c for c in corrections if not already_distilled(c)]

    if not new_corrections:
        print("[distil_corrections] No new corrections to distil today.")
        return 0

    print(f"[distil_corrections] Distilling {len(new_corrections)} correction(s) via Claude Code CLI...")

    prompt = build_prompt(new_corrections)
    output = call_claude(prompt, tools="Read,Write,Edit", timeout=180)

    if output:
        print(f"[distil_corrections] Claude response:\n{output[:500]}")
    else:
        print("[distil_corrections] No output from Claude — rules may not have been written.")

    for c in new_corrections:
        log_distilled(c)

    print("[distil_corrections] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
