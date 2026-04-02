# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — TESTING agents created, Standard prompt fixes applied

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests
- Standard: 75/75 ✅ — run: `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — run: `python3 shared/e2e-test-premium.py`

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 Active — fixes applied |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Created — fixes pending |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Prompt Fixes Applied to Standard TESTING (from 52% → target 100%)
- ✅ FIX #2: Detail confirmation restored to leadcapture node
- ✅ FIX #3: Proactive info sharing (already present, verified)
- ✅ FIX #4: Diagnostic guardrail strengthened
- ✅ FIX #5: Email readback instructions added
- ✅ FIX #6: Abuse boundary-setting (already present, verified)
- ✅ FIX #7: Callback node — no service questions (already present, verified)
- ✅ FIX #8: Mike Thornton by name (already present, verified)
- ✅ FIX #9: No callback time promises (already present, verified)
- ✅ FIX #10: PO Box → physical address redirect
- ✅ FIX #1: Loop check — no loop-back edges found in this flow version
- ⏳ Premium TESTING: fixes not yet applied

## Open Action Items
- [ ] Wire +18129944371 to HVAC Standard Template agent
- [ ] Run 95-scenario batch test against Standard TESTING agent
- [ ] Apply any remaining fixes, retest until 95%+ pass rate
- [ ] Apply verified fixes to MASTER agents
- [ ] Apply prompt fixes to Premium TESTING agent
- [ ] Dan: upload e2e-hvac-premium skill to Claude settings
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium entry

## Blocked
- Live smoke test — Dan unavailable 2-3 days
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
