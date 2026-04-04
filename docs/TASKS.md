# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Workflow registry updated to live state (47 workflows). Stale IDs corrected.

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows


## Marketing — APEX Blueprint Delivered ✅
- Full 9-section strategic blueprint: agent architecture, HVAC launch, projections, costs, risks
- 5 new agents recommended: SEO, Paid Acquisition, Email Nurture, Brand Guardian, Referral Engine
- 12-week sprint calendar with KPI gates
- Next: implement n8n workflows per blueprint recommendations

## Standard HVAC — ALL TESTING COMPLETE ✅
- Agent behaviour: 80/80 ✅
- E2E pipeline:   75/75 ✅
- Call processor: 20/20 ✅
- Go-live gate: 3–5 live smoke calls → unpause ops-monitor → SMS_ENABLED=true


## Marketing
- Agentic Marketing Blueprint: DELIVERED ✅
- Cowork Marketing Plugin: DELIVERED ✅ (14 files pushed to marketing/cowork-plugin/)
- 7 agents as skills, 4 commands, MCP connectors, startup checklist
- Next: Dan sets up social accounts, installs plugin in Cowork, runs /syntharra-marketing:startup ✅ (2026-04-03)
- 18-agent architecture designed, 12-week HVAC launch calendar, cost model, projections
- Next: Build n8n workflows for 6 new agents, set up Supabase tables

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

### Next action — Claude Code (simulator READY ✅)
- Model: llama-3.3-70b-versatile (same as standard — confirmed working)
- Prompt: global prompt only (~10k chars) — node instructions stripped, fits 12k TPM
- Groq key: in Supabase vault service_name='Groq', key_type='api_key'
- Run: `git pull && python3 tools/openai-agent-simulator-premium.py --key <groq_key> --group core_flow`
- Then: personalities → info_collection → pricing_traps → edge_cases → boundary_safety → premium_specific
- Fix failures per group, target 90/95+, then promote TESTING → MASTER

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — needs behaviour testing |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced with MASTER |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🔧 TESTING — core_flow fixes needed |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Standards & Housekeeping
- [ ] **n8n labelling (partial)** — 37/47 labelled ✅. 10 unlabelled remain (9 inactive duplicates, 1 active: `Google Keep → Groq → Slack To-Do List` `5wxgBfJL7QeNP2ab`). Duplicates left intentionally per Dan 2026-04-04.
- [ ] Review & clean up duplicate/inactive workflows when convenient (10 flagged in STANDARDS.md)

## Open Action Items
- [ ] Fix 6 core_flow failures on Premium TESTING flow
- [ ] Run remaining 6 simulator groups on Premium
- [ ] Promote Premium TESTING → MASTER once 95%+
- [ ] Live smoke test calls to +18129944371 (Standard — manual)