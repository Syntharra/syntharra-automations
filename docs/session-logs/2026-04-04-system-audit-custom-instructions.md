# Session Log — 2026-04-04 — System Audit & Custom Instructions Overhaul

## Summary
Full audit of context window design, repo structure, and custom instructions.
No product work — pure infrastructure/documentation session.

## What was done

### Repo restructure
- `docs/TASKS.md` — split to open work only, 38 lines
- `docs/REFERENCE.md` — new: agent IDs, flow IDs, simulator commands, n8n registry
- `docs/MARKETING.md` — new: agentic marketing system as standalone (not a task item)
- `docs/FAILURES.md` — 6 duplicate rows removed
- `docs/LEARNING.md` — removed stale /mnt skill upload instruction (resolved 2026-04-02)
- `docs/NEW-PROJECT-PROMPT.md` — synced: REFERENCE.md added, admin deprecated, full skill list, routing rule 17
- `marketing/cowork-plugin/COWORK-SYSTEM-PROMPT.md` — new: clean Cowork system prompt for agentic marketing team
- `CLAUDE.md` — REFERENCE.md added to session startup; 40-line rule updated; context table updated

### Custom instructions
- Full definitive custom instructions written, merging CLAUDE.md agentic rules + NEW-PROJECT-PROMPT.md + current repo state
- Includes: identity/operating mode, session start/end protocols, self-improvement loop, pre-action protocol, Claude Code rules, all non-negotiables, full infra/brand/skill reference
- Ready to paste into Syntharra Claude project custom instructions

### Cowork marketing prompt
- Scoped purely to marketing: 7 sub-agents, 12-week plan, KPI gates, brand voice, infrastructure inventory
- Deliberately excludes: Retell IDs, Railway service IDs, Supabase vault patterns, E2E protocols
- Pushed to `marketing/cowork-plugin/COWORK-SYSTEM-PROMPT.md`

## Flaws identified and fixed
| Flaw | Fix |
|---|---|
| TASKS.md growing indefinitely | Split into TASKS + REFERENCE + MARKETING |
| Marketing conflated with engineering tasks | MARKETING.md as standalone system file |
| FAILURES.md duplicate rows (3×3) | Deduplicated |
| NEW-PROJECT-PROMPT.md stale | Synced with repo state |
| LEARNING.md ghost action item | Removed |
| Custom instructions missing agentic rules | Full rewrite merging all sources |
| Two nested skill folders undocumented | Noted — intentional reference libraries |

## Files pushed this session
- `docs/TASKS.md`
- `docs/REFERENCE.md` (new)
- `docs/MARKETING.md` (new)
- `docs/FAILURES.md`
- `docs/LEARNING.md`
- `docs/NEW-PROJECT-PROMPT.md`
- `docs/STANDARDS.md` (no change)
- `CLAUDE.md`
- `marketing/cowork-plugin/COWORK-SYSTEM-PROMPT.md` (new)
- `docs/session-logs/2026-04-04-system-audit-custom-instructions.md` (this file)

## Session Reflection
1. What did I get wrong? Nothing — read everything before acting, no reversals needed.
2. What assumption was incorrect? That the 60-line TASKS limit was achievable within the old structure. It wasn't — wrong data in the wrong file.
3. What would I do differently? Same approach. Full audit before any action.
4. What pattern emerged? Stale instructions in docs are silent debt. When a fix is made, the instruction that prompted it must be deleted in the same session.
5. Skill/ARCHITECTURE updates? None — no system failure, no API gotcha. Pure structural work.
6. Anything unverified? No. All pushes 200/201.

## Labels: no n8n workflows modified ✅
