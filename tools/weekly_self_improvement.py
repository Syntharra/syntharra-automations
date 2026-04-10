#!/usr/bin/env python3
"""
weekly_self_improvement.py — Reviews the past week of failures and corrections,
then uses Claude Code CLI to synthesise new rules and update RULES.md + memory.

Uses the Claude Code subscription — no separate API key required.

Schedule: Windows Task Scheduler — run tools/setup_weekly_task.ps1 once to register.
  Weekly on Monday at 07:00 — reviews the weekend + previous week.

Manual run:     python tools/weekly_self_improvement.py
Dry run:        python tools/weekly_self_improvement.py --dry-run
"""
from __future__ import annotations
import argparse
import pathlib
import re
import sys
from datetime import datetime, timezone, timedelta

HOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))
from hook_env import call_claude, claude_available, ROOT  # noqa: E402

FAILURES_PATH    = ROOT / "docs" / "FAILURES.md"
RULES_PATH       = ROOT / "docs" / "RULES.md"
CORRECTIONS_LOG  = ROOT / ".claude" / "session-corrections.log"
IMPROVEMENTS_LOG = ROOT / ".claude" / "weekly-improvements.log"
MEMORY_ANTI      = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory\feedback_anti_patterns.md"
)

BAR = "=" * 70


def since_date(days: int = 7) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


def read_recent_failures(since: str) -> str:
    if not FAILURES_PATH.exists():
        return "(no failures file found)"
    text = FAILURES_PATH.read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if re.match(r"\d{4}-\d{2}-\d{2}", l) and l[:10] >= since]
    return "\n".join(rows) if rows else "(no failures in this period)"


def read_recent_corrections(since: str) -> str:
    if not CORRECTIONS_LOG.exists():
        return "(no corrections logged)"
    text = CORRECTIONS_LOG.read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", text)
    relevant = []
    for block in blocks:
        block = block.strip()
        m = re.match(r"\[(\d{4}-\d{2}-\d{2})", block)
        if m and m.group(1) >= since:
            lines = block.splitlines()
            correction = "\n".join(lines[1:]).strip()
            if correction:
                relevant.append(correction)
    return "\n\n".join(relevant) if relevant else "(no corrections in this period)"


def existing_rule_titles() -> str:
    if not RULES_PATH.exists():
        return "(none)"
    titles = re.findall(r"^## \d+\. (.+)$", RULES_PATH.read_text(), re.MULTILINE)
    return "\n".join(f"- {t}" for t in titles)


def next_rule_number() -> int:
    if not RULES_PATH.exists():
        return 1
    nums = [int(m) for m in re.findall(r"^## (\d+)\.", RULES_PATH.read_text(), re.MULTILINE)]
    return max(nums) + 1 if nums else 1


def build_prompt(since: str, today: str, dry_run: bool) -> str:
    failures    = read_recent_failures(since)
    corrections = read_recent_corrections(since)
    rule_titles = existing_rule_titles()
    next_num    = next_rule_number()

    action = "PRINT what you would add (do not write any files)" if dry_run else (
        f"Write new rules directly to docs/RULES.md and {MEMORY_ANTI}"
    )

    return f"""You are performing a weekly self-improvement review for Syntharra Automations —
an AI receptionist SaaS for HVAC businesses (Retell AI voice agent + n8n on Railway +
Supabase billing/clients + Stripe payments + Brevo transactional email + Python cron tools).

Review period: {since} to {today}

## Failures this week
{failures}

## User corrections this week
{corrections}

## Rules already in docs/RULES.md (DO NOT duplicate)
{rule_titles}

Your task:
1. Find patterns in the failures and corrections above that are NOT covered by existing rules.
   Look for: recurring areas, root cause categories, process gaps, wrong assumptions.

2. For each new high-confidence pattern:
   - Write it as a specific, actionable rule for the Syntharra codebase
   - Format: "Always X" or "Never Y" or "When Z, do W"
   - Include WHY (what breaks if violated)

3. {action}

   For docs/RULES.md, append using this exact format (next rule number is {next_num}):

   ## {next_num}. <Title>

   - <Rule sentence>
   - **Why:** <Why sentence>

   _Source: weekly-self-improvement {today}_

   For {MEMORY_ANTI}, append under the relevant section:
   **<Rule sentence>**
   **Why:** {today} — <Why sentence>
   **How to apply:** Pattern identified in weekly review {today}.

4. If you find no new patterns, say so clearly.
5. Only add rules specific to this codebase. No generic software advice.

{"This is a DRY RUN — read files but do not write anything." if dry_run else "Read both files before writing so you don't break existing content."}
""".strip()


def log_run(today: str, note: str):
    with open(IMPROVEMENTS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{today}] {note}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    since = since_date(7)

    print(BAR)
    print(f"  WEEKLY SELF-IMPROVEMENT — {today}  (since {since})")
    if args.dry_run:
        print("  DRY RUN — no files will be written")
    print(BAR)

    if not claude_available():
        print("  [!] claude CLI not found on PATH.")
        print("  Install Claude Code and ensure `claude` is on PATH.")
        return 1

    prompt = build_prompt(since, today, args.dry_run)
    tools  = "Read" if args.dry_run else "Read,Write,Edit"

    print("  Running Claude Code for pattern synthesis...")
    output = call_claude(prompt, tools=tools, timeout=300)

    if output:
        print(f"\n{output}\n")
        log_run(today, f"{'DRY RUN' if args.dry_run else 'LIVE'} — completed")
    else:
        print("  [!] No output from Claude. Is Claude Code running and authenticated?")
        log_run(today, "FAILED — no output from claude CLI")
        return 1

    print(BAR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
