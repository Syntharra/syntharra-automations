# Session Log — 2026-04-03 — Simulator core_flow + personalities

## Summary
- Ran core_flow group runs 5–8: 93% → 93% → 93% → **100%** ✅
- Ran personalities runs 1–2: 47% → 47% (no improvement — global prompt too long)
- Identified root cause for personalities stall: ~37k char global prompt buries personality instructions

## Runs This Session
| Run | Group | Pass | Rate |
|---|---|---|---|
| core-flow-run5 | core_flow | 14/15 | 93.3% |
| core-flow-run6 | core_flow | 14/15 | 93.3% |
| core-flow-run7 | core_flow | 14/15 | 93.3% |
| core-flow-run8 | core_flow | 15/15 | **100%** ✅ |
| personalities-run1 | personalities | 7/15 | 46.7% |
| personalities-run2 | personalities | 7/15 | 46.7% |

## Flow Changes (conversation_flow_5b98b76c8ff4)
All changes pushed live and published to agent_731f6f4d59b749a0aa11c26929

### node-verify-emergency
- Restored 2-step urgency assessment: (1) is system completely down? (2) burning/gas smell?
- Added extreme-urgency signal detection for transfer vs lead-capture routing
- Step 5: "freezing/elderly/dangerous" → offer transfer; matter-of-fact → high-priority lead capture

### node-leadcapture  
- Scripted close made non-negotiable with explicit ⚠️ CRITICAL warning against paraphrasing
- MINIMAL INFO RULE: don't probe when caller signals they want simple callback
- SERVICE AREA: added "only collect REMAINING details" — no re-ask of already-captured fields
- Step 6 (additional details) skipped when caller signals minimal intent

### node-identify-call
- WRONG NUMBER branch added as item 2 (before spam) — warmly redirect to Google/411

### global_prompt
- Added CALLER PERSONALITY HANDLING section (~2k chars) — NOTE: ineffective at 37k total, move to node

## Carry-Forward for Next Session
1. Move personality handling OUT of global_prompt, INTO node-leadcapture instruction
2. Re-run personalities (target 80%+)
3. Run info_collection, pricing_traps, edge_cases, boundary_safety
4. Fix all failures, target 90%+ overall
5. Promote TESTING agent to MASTER when all groups pass
