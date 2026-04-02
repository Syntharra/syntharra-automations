# Syntharra — Agentic Learning Protocol
> This document defines HOW Claude gets smarter on this project over time.
> Load at session start alongside TASKS.md.

## The Self-Improvement Loop

```
Test/Build → Failure Found → Root Cause → Fix → Skill Updated → FAILURES.md Updated → Next session starts smarter
```

## Session Start Checklist (Claude runs this mentally every session)
1. Load CLAUDE.md (routing)
2. Load TASKS.md (current state + open items)
3. Scan FAILURES.md (what broke before in this area)
4. Load context files relevant to the task
5. Load skill files relevant to the task
6. Do the work
7. Update FAILURES.md if anything broke
8. Update relevant skill files with verified fixes
9. Update TASKS.md
10. Push session log to docs/session-logs/

## Rules for Skill File Updates
- Only update a skill after a fix is **verified** (E2E test passes or manually confirmed)
- Never update a skill based on a theory — only on evidence
- When updating, note the date and what changed at the top of the skill

## Rules for FAILURES.md
- Every failure gets a row — no matter how small
- Include the root cause, not just the symptom
- Mark skill as updated once the fix is in the skill file

## What "Getting Better" Looks Like
| Metric | Target |
|--------|--------|
| Simulator pass rate | 90%+ across all groups |
| Session re-work rate | Zero repeated mistakes from FAILURES.md |
| Skill file freshness | Updated within 1 session of any fix |
| E2E tests | Always green before any deploy |
