# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-03 — Jotform 429 fixed | Railway GQL fixed | RAILWAY_TOKEN wired | Personalities fix pending

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — `python3 shared/e2e-test-premium.py`

## Agent Simulator
- Script: `tools/openai-agent-simulator.py`
- Cost: ~$0.002/scenario | Model: gpt-4o-mini
- OpenAI key: in vault (service_name='OpenAI', key_type='api_key')
- Run: `GITHUB_TOKEN=... RETELL_KEY=... python3 tools/openai-agent-simulator.py --key sk-... --group core_flow`
- Groups: core_flow(15), personalities(15), info_collection(15), pricing_traps(8), edge_cases(15), boundary_safety(12)
- Results → tests/results/

## Simulator Results
| Run | Group | Pass Rate | Notes |
|---|---|---|---|
| core-flow-run8 | core_flow | 100% (15/15) | ✅ COMPLETE |
| personalities-run2 | personalities | 47% (7/15) | Personality section in global prompt ignored (prompt too long ~37k chars) |

## Key Finding — Personalities Fix
Global prompt now ~37k chars — personality instructions buried at end, ignored by model.
Fix: move personality handling INTO node-leadcapture instruction text (not global prompt).
Remaining failures: #16 elderly, #18 chatty, #19 non-native, #21 distracted, #22 brief, #23 technical, #28 AI complaint, #29 mumbling.

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 Fixes live — core_flow 100% |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Prompt fixes live |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items (priority order)
- [ ] Move personality handling from global_prompt INTO node-leadcapture instruction
- [ ] Run personalities-run3 — target 80%+
- [ ] Run info_collection, pricing_traps, edge_cases, boundary_safety groups
- [ ] Fix all failures across all groups — target 90%+ overall
- [ ] Promote Standard TESTING → MASTER once all groups verified
- [ ] Wire +18129944371 to Standard Template agent
- [ ] Live smoke test (Dan available)
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium

## Blocked
- Live smoke test — awaiting Dan availability
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)

## Completed 2026-04-03
- [x] Email hub — all 6 emails built and brand-compliant
- [x] Welcome Premium & Hot Lead Alert stubs replaced with full implementations
- [x] Call forwarding PDF rebuilt — no logo, QR codes included, set as standard
- [x] Old PDF build scripts and onboarding HTML archived
