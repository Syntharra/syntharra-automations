# Session Log — 2026-04-02 — TESTING Agents + Prompt Fixes

## Summary
- Created TESTING copies of Standard and Premium master agents (masters untouched)
- Applied all applicable prompt fixes from March 31 95-scenario analysis
- Both TESTING agents published and ready for batch testing

## Agents Created
| Agent | ID | Flow |
|---|---|---|
| HVAC Standard (TESTING) | agent_731f6f4d59b749a0aa11c26929 | conversation_flow_5b98b76c8ff4 |
| HVAC Premium (TESTING) | agent_2cffe3d86d7e1990d08bea068f | conversation_flow_2ded0ed4f808 |

## Masters (untouched — backup reference)
| Agent | ID | Flow |
|---|---|---|
| HVAC Standard Template | agent_4afbfdb3fcb1ba9569353af28d | conversation_flow_34d169608460 |
| HVAC Premium Template | agent_9822f440f5c3a13bc4d283ea90 | conversation_flow_1dd3458b13a7 |

## Fixes Applied — Standard TESTING
- FIX #1: Loop check — no loop-back edges found (already clean)
- FIX #2: Detail confirmation restored to leadcapture node
- FIX #3: Proactive info sharing (already present, verified)
- FIX #4: Diagnostic guardrail strengthened (breakers/filters/batteries/thermostats)
- FIX #5: Email readback with dot/at/dash terminology
- FIX #6: Abuse boundary-setting (already present, verified)
- FIX #7: Callback node — no service questions (already present, verified)
- FIX #8: Mike Thornton by name (already present, verified)
- FIX #9: No callback time promises (already present, verified)
- FIX #10: PO Box → physical address redirect in leadcapture

## Fixes Applied — Premium TESTING
- FIX #2: CONFIRMING DETAILS (already present in global prompt)
- FIX #3: Proactive info sharing — added new section
- FIX #4: Diagnostic guardrail strengthened (same as Standard)
- FIX #5: Email readback (already present in CAPTURING DETAILS)
- FIX #6: Abuse boundary (already present in SPECIAL SCENARIOS)
- FIX #7: Callback node — no probing if caller doesn't volunteer info
- FIX #9: No callback time promises — added to CRITICAL RULES
- FIX #10: PO Box → physical address redirect in booking_capture node
- FIX #1/8: Loop-free + manager name (already clean/present)

## Operations Protocol Established
- Changes always go to TESTING agents first
- Masters stay frozen until TESTING is verified
- Never delete old agents or flows — keep as backups
- Promotion path: TESTING verified → patch MASTER → publish MASTER

## Next Actions
1. Run 95-scenario batch test against Standard TESTING agent
2. Review results, apply further fixes if needed
3. Retest until pass rate is satisfactory (target 90%+)
4. Promote verified TESTING flows to MASTER
5. Wire +18129944371 to Standard Template agent
6. Live smoke test when Dan is available (2-3 days)
