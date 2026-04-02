# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — TESTING agents created + all prompt fixes applied

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — run: `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — run: `python3 shared/e2e-test-premium.py`

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 All fixes applied — ready to test |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 All fixes applied — ready to test |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Conversation Flows
| Flow | ID | Status |
|---|---|---|
| Standard Master | `conversation_flow_34d169608460` | ✅ MASTER — do not touch |
| Premium Master | `conversation_flow_1dd3458b13a7` | ✅ MASTER — do not touch |
| Standard TESTING | `conversation_flow_5b98b76c8ff4` | 🧪 Fixes applied |
| Premium TESTING | `conversation_flow_2ded0ed4f808` | 🧪 Fixes applied |

## Operations Protocol
1. Changes → TESTING agents only
2. Run 95-scenario batch test to verify
3. Pass rate satisfactory → patch MASTER, publish MASTER
4. NEVER delete old agents or flows — backup only

## Open Action Items
- [ ] Run 95-scenario batch test on Standard TESTING agent
- [ ] Review results + apply further fixes if needed
- [ ] Retest until 90%+ pass rate
- [ ] Promote Standard TESTING → MASTER
- [ ] Repeat for Premium TESTING
- [ ] Wire +18129944371 to Standard Template agent
- [ ] Live smoke test (Dan available in 2-3 days)
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
