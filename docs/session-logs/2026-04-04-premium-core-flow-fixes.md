# Session Log — 2026-04-04 — Premium core_flow fixes

## What was done
- Loaded CLAUDE.md, TASKS.md, FAILURES.md, LEARNING.md, e2e-hvac-premium skill, hvac-premium skill
- Confirmed TESTING flow live: 19 nodes (18 + code node)
- Discovered scenario JSON structure: flat list of 95 items (not nested)
- Identified root causes for all 6 core_flow failures from global prompt
- Applied 3 targeted fixes to TESTING flow global prompt:
  1. Booking push language softened — "PRIMARY function, always book" removed
  2. Booking step order fixed — service type captured before confirmation
  3. Four new CRITICAL RULES added: no repeating info, no pushing decliners, callback = name+phone only, FAQ = no lead capture
- Published TESTING agent
- Ran #5 FAQ hours → PASS ✅
- Scenarios 7,11,13,14,15 hit rate limits — pending next session

## Key learnings
- Scenario JSON is a flat array of 95 items, not nested under groups[]
- Bash tool timeout ~55s — run 1 scenario per execution with 20s cooldown between

## Next session
- Run scenarios 7, 11, 13, 14, 15 one at a time (20s gap between each)
- Fix any still-failing, then run remaining groups
