# Syntharra — Tasks & Continuity
> Updated: 2026-04-03 — Slack internal notifications complete + Email Intelligence live

## Status: PRE-LAUNCH | Stripe TEST MODE | 34 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — `python3 shared/e2e-test-premium.py`

## Slack Internal Notifications — COMPLETE ✅
All internal @syntharra.com emails replaced with Slack. 7 channels live, all tested.
| Channel | Source |
|---|---|
| `#billing` | Stripe payments |
| `#onboarding` | Agent go-live (Std + Prem) |
| `#ops-alerts` | Supabase failures, system errors |
| `#calls` | Lead call summaries |
| `#weekly-reports` | Weekly report sent confirmations |
| `#leads` | Website AI-scored leads |
| `#emails` | All inbox alerts (Groq-filtered, score ≥3) |

## Email Intelligence Workflow — LIVE ✅
- ID: `ghisTdGOR4ErVrUh` | Active | 15-min schedule
- Polls 9 aliases (alerts, support, sales, solutions, onboarding, info, careers, feedback, admin)
- Groq llama3-8b-8192 scores 1-5 → drops ≤2 → posts to #emails
- ⚠️ receipts@syntharra.com NOT yet connected — needs manual Gmail OAuth in n8n UI
- Sub-channels (#emails-support etc) ready in aliasMap — just update channel values when Dan creates them

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items
- [ ] receipts@syntharra.com — add Gmail OAuth2 credential in n8n UI, wire into email intelligence workflow
- [ ] Create Slack sub-channels (#emails-support, #emails-sales etc) — update aliasMap in workflow ghisTdGOR4ErVrUh
- [ ] Live smoke test call to +18129944371 (Dan — manual)
- [ ] Apply Standard MASTER improvements to HVAC Premium TESTING + test
- [ ] Go-live: unpause syntharra
