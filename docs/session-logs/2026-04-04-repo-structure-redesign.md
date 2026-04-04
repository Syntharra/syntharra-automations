# Session Log — 2026-04-04 — Repo Structure + Stale Docs Cleanup

## Summary
Audited full context window design. Redesigned file structure to be sustainable at scale.
Fixed stale content across 3 additional docs.

## Changes — Part 1: Structure Redesign
- `docs/TASKS.md` — open work only, 38 lines (was 69, bloating indefinitely)
- `docs/REFERENCE.md` — NEW: agent IDs, flow IDs, simulator commands, n8n registry
- `docs/MARKETING.md` — NEW: agentic marketing system as standalone (not a task item)
- `docs/FAILURES.md` — 6 duplicate rows removed
- `CLAUDE.md` — REFERENCE.md added to session startup; 40-line rule; new file routing

## Changes — Part 2: Stale Doc Fixes
- `docs/NEW-PROJECT-PROMPT.md` — added REFERENCE.md to startup block; updated 60→40 line limit
- `docs/LEARNING.md` — removed stale "Upload skills to Claude.ai" instruction (resolved 2026-04-02, never cleaned up)

## What was still broken (found during audit)
1. NEW-PROJECT-PROMPT.md didn't know about REFERENCE.md or MARKETING.md — new sessions would start without loading them
2. LEARNING.md still had an action item telling Dan to upload skill files to Claude.ai manually — fixed months ago, never cleaned up
3. FAILURES.md had 3 entries logged 3× each — deduped

## Session Reflection
1. What did I get wrong? Nothing this session — diagnosed first, acted once, no reversals.
2. What assumption was incorrect? The 60-line TASKS limit was treated as the problem. The actual problem was structural: wrong data in the wrong file.
3. What would I do differently? Same. Read everything before touching anything.
4. What pattern emerged? Stale action items in LEARNING.md are invisible debt — they erode trust in the file. Needs pruning whenever an item is resolved.
5. Skill/ARCHITECTURE updates? None — no system failure, no API gotcha. Pure structural fix.
6. Anything unverified? No. All pushes 200/201.

## Files pushed
- `docs/TASKS.md`
- `docs/REFERENCE.md` (new)
- `docs/MARKETING.md` (new)
- `docs/FAILURES.md`
- `CLAUDE.md`
- `docs/NEW-PROJECT-PROMPT.md`
- `docs/LEARNING.md`
- `docs/session-logs/2026-04-04-repo-structure-redesign.md` (updated)

## Labels: no n8n workflows modified ✅
