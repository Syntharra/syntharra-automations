# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Premium agent prep complete, core_flow run done (9/15), fixes needed

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## Standard HVAC — ALL TESTING COMPLETE ✅
- Agent behaviour: 80/80 ✅
- E2E pipeline:   75/75 ✅
- Call processor: 20/20 ✅
- Go-live gate: 3–5 live smoke calls → unpause ops-monitor → SMS_ENABLED=true

## Premium HVAC — IN PROGRESS 🔧
- Agent: `agent_9822f440f5c3a13bc4d283ea90` (MASTER) | `agent_2cffe3d86d7e1990d08bea068f` (TESTING)
- Flow: `conversation_flow_1dd3458b13a7` (MASTER) | `conversation_flow_2ded0ed4f808` (TESTING)
- E2E: 89/89 ✅
- All 9 Standard improvements applied to TESTING flow ✅ (incl. code node)
- Simulator: `tools/openai-agent-simulator-premium.py` ✅

### core_flow — fixes applied, partial retest in progress
- #5  ✅ FIXED & PASSING
- #7  Booking push — fix applied, retest pending
- #11 Service type order — fix applied, retest pending
- #13 Callback repetition — fix applied, retest pending
- #14 Pricing redirect — fix applied, retest pending
- #15 Over-eager close — fix applied, retest pending

### Next action — Claude Code (simulator fixed, ready to run)
- Simulator switched to Groq (llama-3.3-70b-versatile) — key in Supabase vault service_name='Groq'
- Run: `python3 tools/openai-agent-simulator-premium.py --key <groq_key> --group core_flow`
- Then run remaining 6 groups: personalities, info_collection, pricing_traps, edge_cases, boundary_safety, premium_specific
- Fix any failures, re-run affected group, target 90/95+
- Promote TESTING → MASTER once passing

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — needs behaviour testing |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced with MASTER |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🔧 TESTING — core_flow fixes needed |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items
- [ ] Fix 6 core_flow failures on Premium TESTING flow
- [ ] Run remaining 6 simulator groups on Premium
- [ ] Promote Premium TESTING → MASTER once 95%+
- [ ] Live smoke test calls to +18129944371 (Standard — manual)
- [ ] Go-live: unpause syntharra-ops-monitor Railway service
- [ ] Go-live: set SMS_ENABLED=true once Telnyx approved
- [ ] Get Slack webhook URL from Dan → add to vault + Railway env
