#!/usr/bin/env python3
"""
weekly_self_improvement.py — Reviews recent failures, corrections, AND successful
commits, then uses Claude Code CLI to synthesise new rules (RULES.md) and positive
playbooks (PLAYBOOKS.md + DECISIONS.md).

Uses the Claude Code subscription — no separate API key required.

Schedule: Windows Task Scheduler — Syntharra-DailySelfImprovement — daily 07:00.
  Register once: powershell -ExecutionPolicy Bypass -File tools/setup_weekly_task.ps1

Manual run:     python tools/weekly_self_improvement.py
Dry run:        python tools/weekly_self_improvement.py --dry-run
Full week:      python tools/weekly_self_improvement.py --days 7
"""
from __future__ import annotations
import argparse
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

# Rule 41/50: Windows stdout is cp1252 by default — reconfigure immediately
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))
from hook_env import call_claude, claude_available, ROOT  # noqa: E402

FAILURES_PATH    = ROOT / "docs" / "FAILURES.md"
RULES_PATH       = ROOT / "docs" / "RULES.md"
PLAYBOOKS_PATH   = ROOT / "docs" / "PLAYBOOKS.md"
DECISIONS_PATH   = ROOT / "docs" / "DECISIONS.md"
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


def read_recent_commits(since: str) -> str:
    """Mine recent git commit messages for positive patterns (what worked).
    Rule 41: always specify encoding='utf-8' — Windows default is cp1252."""
    try:
        git_cmd = ["git", "log", f"--since={since}", "--pretty=format:%h %s", "--no-merges"]
        result = subprocess.run(
            git_cmd,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), timeout=15
        )
        commits = result.stdout.strip()
        return commits if commits else "(no commits in this period)"
    except Exception:
        return "(could not read git log)"


def existing_rule_titles() -> str:
    if not RULES_PATH.exists():
        return "(none)"
    titles = re.findall(r"^## \d+\. (.+)$", RULES_PATH.read_text(encoding="utf-8"), re.MULTILINE)
    return "\n".join(f"- {t}" for t in titles)


def next_rule_number() -> int:
    if not RULES_PATH.exists():
        return 1
    nums = [int(m) for m in re.findall(r"^## (\d+)\.", RULES_PATH.read_text(encoding="utf-8"), re.MULTILINE)]
    return max(nums) + 1 if nums else 1


def existing_playbook_titles() -> str:
    if not PLAYBOOKS_PATH.exists():
        return "(PLAYBOOKS.md not found)"
    titles = re.findall(r"^## Playbook \d+ — (.+)$", PLAYBOOKS_PATH.read_text(encoding="utf-8"), re.MULTILINE)
    return "\n".join(f"- {t}" for t in titles)


def build_prompt(since: str, today: str, dry_run: bool) -> str:
    failures    = read_recent_failures(since)
    corrections = read_recent_corrections(since)
    commits     = read_recent_commits(since)
    rule_titles = existing_rule_titles()
    playbooks   = existing_playbook_titles()
    next_num    = next_rule_number()

    if dry_run:
        action_rules = "PRINT what rules you would add (do not write any files)"
        action_playbooks = "PRINT what playbook updates you would make (do not write any files)"
    else:
        action_rules = f"Write new rules directly to docs/RULES.md and {MEMORY_ANTI}"
        action_playbooks = "Update docs/PLAYBOOKS.md if any canonical patterns need adding or correcting"

    quality_gate = (
        "\n\nQUALITY GATE: Any auto-written rule must end with the line:\n"
        f"  ⚠️ AUTO-WRITTEN {today} — verify before relying on this rule\n"
        "This flag is removed only when a human confirms the rule is correct."
    )

    return f"""You are performing a daily self-improvement review for Syntharra Automations —
an AI receptionist SaaS for HVAC businesses (Retell AI voice agent + n8n on Railway +
Supabase billing/clients + Stripe payments + Brevo transactional email + Python cron tools).

Review period: {since} to {today}

## Failures this period
{failures}

## User corrections this period
{corrections}

## Recent git commits (what worked — positive signal)
{commits}

## Rules already in docs/RULES.md (DO NOT duplicate)
{rule_titles}

## Playbooks already in docs/PLAYBOOKS.md (DO NOT duplicate)
{playbooks}

---

## TASK 1 — New defensive rules (from failures + corrections)

Find patterns in the failures and corrections that are NOT covered by existing rules.
For each new high-confidence pattern:
- Write it as a specific, actionable rule for the Syntharra codebase
- Format: "Always X" or "Never Y" or "When Z, do W"
- Include WHY (what breaks if violated)
- Only rules specific to this codebase — no generic software advice

{action_rules}

For docs/RULES.md, append using this exact format (next rule number is {next_num}):

## {next_num}. <Title>

- <Rule sentence>
- **Why:** <Why sentence>

{quality_gate}

For {MEMORY_ANTI}, append under the relevant section:
**<Rule sentence>**
**Why:** {today} — <Why sentence>
**How to apply:** Pattern identified in daily review {today}.

---

## TASK 2 — Positive playbook updates (from commits + patterns that worked)

Look at the recent commits for patterns that worked well and are NOT already documented
in docs/PLAYBOOKS.md. Focus on:
- Canonical operation patterns that succeeded (e.g. "this is how we correctly patched n8n")
- Gotchas that were discovered and solved (add to the relevant playbook section)
- Any established pattern that is repeated across multiple commits

{action_playbooks}

If updating PLAYBOOKS.md, add to the relevant existing playbook section or create a new
"## Playbook N — <Title>" section. Keep it concise and actionable.

---

If you find no new patterns for either task, say so clearly.
{"This is a DRY RUN — read files but do not write anything." if dry_run else "Read all files before writing so you append correctly without breaking existing content."}
""".strip()


def log_run(today: str, note: str):
    with open(IMPROVEMENTS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{today}] {note}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days", type=int, default=2,
                        help="How many days back to scan (default: 2)")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    since = since_date(args.days)

    print(BAR)
    print(f"  DAILY SELF-IMPROVEMENT — {today}  (since {since}, last {args.days}d)")
    if args.dry_run:
        print("  DRY RUN — no files will be written")
    print(BAR)

    if not claude_available():
        print("  [!] claude CLI not found on PATH.")
        print("  Install Claude Code and ensure `claude` is on PATH.")
        return 1

    prompt = build_prompt(since, today, args.dry_run)
    tools  = "Read" if args.dry_run else "Read,Write,Edit"

    print("  Running Claude Code for pattern synthesis (failures + corrections + commits)...")
    output = call_claude(prompt, tools=tools, timeout=300)

    if output:
        print(f"\n{output}\n")
        log_run(today, f"{'DRY RUN' if args.dry_run else 'LIVE'} — completed (last {args.days}d, git mining enabled)")
    else:
        print("  [!] No output from Claude. Is Claude Code running and authenticated?")
        log_run(today, "FAILED — no output from claude CLI")
        return 1

    print(BAR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
