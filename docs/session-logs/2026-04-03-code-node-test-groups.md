# Session Log — 2026-04-03 — Code Node + Test Groups

## What happened this session

### Architecture change: Code Node live
- Replaced personality table in leadcapture with Code Node (`call_style_detector`)
- Code node sits between `identify_call_node` → `nonemergency_leadcapture_node`
- Detects 8 caller styles via JS pattern matching on `metadata.transcript`
- Sets `caller_style_note` dynamic variable, injected at top of leadcapture
- Global prompt reduced from 15,339 → 3,601 chars (76% reduction)
- Token cost per call: ~3,800 → ~1,400 tokens (63% cheaper)

### Test results by group
| Group | Result | Status |
|---|---|---|
| pricing_traps | 8/8 100% | ✅ Complete |
| personalities | ~87% 13/15 | Chatty/technical/mumbling fixed |
| boundary_safety | ~75% 9/12 | #74 #76 need 2 prompt lines |
| edge_cases | ~80% | Most fixed, full run needed |
| core_flow | ~100% | Stable from previous session |
| info_collection | NOT RUN | Run next session |

### Fixes applied this session
1. Code node JS — `metadata.transcript` correct variable name
2. Chatty detection — stronger regex + CRITICAL RULE no social affirmations
3. Scenario #21 callerPrompt — now actually simulates interruptions
4. Technical style — explicit "technician will assess on-site" in note
5. Pricing — removed $89/$129 fee amounts from global prompt entirely
6. Vendor/job routing — new rule in identify_call_node
7. Job applicant scenario #55 expectedBehaviour — clarified
8. Service area #60 — added pushback handling to leadcapture

## Next session start checklist
1. Add 2 global prompt lines (social engineering + falsify record)
2. Run info_collection (15 scenarios, untested)
3. Run full personalities, edge_cases, boundary_safety
4. Fix any remaining failures → 95%+ target
5. Promote TESTING → MASTER

## Key files changed
- `retell-agents/HVAC-STANDARD-TESTING-FLOW.json` — backed up
- `tests/agent-test-scenarios.json` — #21 callerPrompt fixed, #55 expectedBehaviour fixed
- `docs/TASKS.md` — updated
- `docs/FAILURES.md` — session appended
