# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Standard complete, Premium improvements applied, simulator ready — Standard complete, Premium agent testing next

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## Standard HVAC — ALL TESTING COMPLETE ✅
- Agent behaviour: 80/80 ✅
- E2E pipeline:   75/75 ✅ — `python3 shared/e2e-test.py`
- Call processor: 20/20 ✅ — `python3 tests/call-processor-test.py`
- Master skill updated: `skills/hvac-standard-SKILL.md`
- Go-live gate: 3–5 live smoke calls → unpause ops-monitor → SMS_ENABLED=true

## Premium HVAC — READY TO TEST 🎯
- Agent: `agent_9822f440f5c3a13bc4d283ea90` (MASTER) | `agent_2cffe3d86d7e1990d08bea068f` (TESTING)
- Flow: `conversation_flow_1dd3458b13a7` (MASTER) | `conversation_flow_2ded0ed4f808` (TESTING)
- E2E: 89/89 ✅ — `python3 shared/e2e-test-premium.py`
- Agent behaviour: NOT YET TESTED — simulator built, all improvements applied to TESTING flow
- Task: run Premium simulator (need OpenAI key) → fix failures → promote to MASTER
- Simulator: `python3 tools/openai-agent-simulator-premium.py --key sk-... --group core_flow`

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — needs behaviour testing |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced with MASTER |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 TESTING — pending fixes |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items
- [ ] Premium agent behaviour testing (next session)
- [ ] Live smoke test calls to +18129944371 (Dan — manual, Standard)
- [ ] Apply Standard MASTER prompt improvements to Premium TESTING
- [ ] Go-live: unpause syntharra-ops-monitor Railway service
- [ ] Go-live: set SMS_ENABLED=true once Telnyx approved
- [ ] Get Slack webhook URL from Dan → add to vault + Railway env
