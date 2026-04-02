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

## Current Agentic Status — 2026-04-02

### ✅ Done
- FAILURES.md — logs every mistake with root cause, I read it every session
- DECISIONS.md — architectural decisions so I don't re-litigate settled questions  
- Skill files — all have freshness dates, backed up to repo
- Correct GitHub API endpoint — logged in skill AND FAILURES.md
- All 8 repos accessible — no blind spots
- Secrets removed from public repo — safe to stay public
- Duplicates removed — clean signal-to-noise

### ⚠️ Still Needs Dan's Action
- Upload 6 missing skills to Claude.ai project settings:
  `hvac-standard`, `hvac-premium`, `syntharra-testing`, `syntharra-marketing-manager`, `syntharra-social-leads`
  (admin-dashboard was deleted — was a mislabelled duplicate)
- Transfer private repos or add collaborator access confirmed working ✅

### ✅ Structural Gap — RESOLVED 2026-04-02
- Skills previously required manual upload to Claude.ai project settings (/mnt/skills/user/)
- Fixed: skills now fetched directly from GitHub at session start via API
- /mnt skills are no longer used — repo is the single source of truth
- Update a skill in GitHub → live immediately next session. Zero upload step.

### The Self-Improvement Loop — Complete
```
Session → Find mistake → Fix it → Log in FAILURES.md → Update skill in GitHub →
Next session fetches skill from GitHub → Same mistake never made again
```
No manual upload. No drift. Always current.
