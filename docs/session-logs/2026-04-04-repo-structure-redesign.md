# Session Log — 2026-04-04 — Repo Structure Redesign

## Summary
Audited the full context window design at Dan's request. Found structural flaws in TASKS.md growth,
marketing conflation, and FAILURES.md duplicates. Redesigned the file structure to be sustainable
at scale.

## What was done

### TASKS.md redesign
- Problem: TASKS.md was doing 3 jobs — open work, reference data, marketing state. Would grow forever.
- Solution: Split into 3 purpose-built files.
- TASKS.md now: open work only, 38 lines, enforced at 40-line limit.

### New: docs/REFERENCE.md
- Agent IDs, conversation flow IDs, simulator commands, n8n workflow registry, fix status tables.
- Static reference data that never needs trimming — grows with the project without polluting task state.

### New: docs/MARKETING.md
- Standalone home for the agentic marketing system.
- Correctly modelled as a separate system (Cowork plugin, 18-agent architecture) not a task item.
- Contains: current state, 6-agent n8n backlog, plugin setup, file locations, design principles.

### FAILURES.md deduplicated
- 6 duplicate rows removed (3 unique failures × 3 copies each).
- Before: 139 lines | After: 133 lines.

### CLAUDE.md updated
- Session startup now loads REFERENCE.md alongside TASKS.md.
- Rule 10 updated: TASKS.md open work only, under 40 lines. Reference → REFERENCE.md. Marketing → MARKETING.md.
- Context table updated with new files.

## Files pushed
- `docs/TASKS.md` — open work only, 38 lines
- `docs/REFERENCE.md` — new file, all reference data
- `docs/MARKETING.md` — new file, marketing system state
- `docs/FAILURES.md` — deduplicated (6 rows removed)
- `CLAUDE.md` — startup + rule + context table updated
- `docs/session-logs/2026-04-04-repo-structure-redesign.md` — this file

## Session Reflection
1. What did I get wrong or do inefficiently? Nothing — diagnosed before acting, no reversals needed.
2. What assumption turned out incorrect? The 60-line limit was stated as a rule but the file structure made it impossible to honour. The rule wasn't wrong — the structure was.
3. What would I do differently? Same approach. Read everything, diagnose the root cause, then act once.
4. What pattern emerged? TASKS.md conflation is a common failure mode in agentic systems — tasks, state, and reference data need separate files from day one.
5. What was added to skill files / ARCHITECTURE.md? No skill update needed — no system failure, no API gotcha. This was a structural design fix.
6. Did I do anything unverified? No. All pushes confirmed 200/201.

## Labels: no n8n workflows modified this session ✅
