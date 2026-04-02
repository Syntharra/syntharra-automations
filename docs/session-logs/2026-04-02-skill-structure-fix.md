# Session Log — 2026-04-02 — Skill Structure Fix

## Changes
- Deleted `syntharra-marketing-manager` skill (deprecated)
- Deleted `syntharra-testing` skill (deprecated, previous session)
- Restructured all 16 remaining skills from `skills/{name}/SKILL.md` → `skills/{name}-SKILL.md`

## Why
Downloading `skills/{name}/SKILL.md` via GitHub raw always saved as `SKILL.md`.
Uploading multiple skills to Claude.ai project resulted in: skill, skill 1, skill 2 — unusable.
New flat naming means download gives `syntharra-retell-SKILL.md` etc — immediately identifiable.

## Logged in FAILURES.md
Root cause captured so this pattern is never repeated.
