# Syntharra — Tasks & Continuity
> Updated: 2026-04-03 — ALL TEST GROUPS 100% ✅ | MASTER promoted | Phone wired

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — `python3 shared/e2e-test-premium.py`

## Agent Simulator — ALL GROUPS COMPLETE ✅
| Group | Score | Status |
|---|---|---|
| core_flow | 15/15 (100%) | ✅ |
| pricing_traps | 8/8 (100%) | ✅ |
| personalities | 15/15 (100%) | ✅ |
| boundary_safety | 12/12 (100%) | ✅ |
| edge_cases | 15/15 (100%) | ✅ |
| info_collection | 15/15 (100%) | ✅ |
| **TOTAL** | **80/80 (100%)** | ✅ |

Results: `tests/results/simulator-20260403-*-all-groups.json`

## Architecture — MASTER (LIVE)
- MASTER flow `conversation_flow_34d169608460` promoted from TESTING 2026-04-03
- Code node `call_style_detector` live in MASTER
- Global prompt: 4,053 chars (was 15,354) — 74% reduction
- 15 nodes including: commercial caller, WhatsApp contact, fast-phone handling
- `+18129944371` wired → `agent_4afbfdb3fcb1ba9569353af28d` ✅

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE ✅ |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced with MASTER |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Pending |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items
- [ ] Live smoke test call to +18129944371 (Dan — manual, needs phone)
- [ ] Apply Standard MASTER improvements to HVAC Premium TESTING + test
- [ ] Wire +12292672271 (Demo line) if needed
- [ ] Go-live: unpause syntharra-ops-monitor Railway service
- [ ] Go-live: set SMS_ENABLED=true once Telnyx approved
