# Syntharra — Tasks & Continuity
> Updated: 2026-04-03 — Slack notifications FULLY LIVE. Bot token working, 14/16 channels confirmed.

## Status: PRE-LAUNCH | Stripe TEST MODE | 34 active workflows

## Slack Internal Notifications — LIVE ✅
Bot: @syntharra (U0AQR9PQWCS) | Token in vault (Slack/bot_token) + Railway SLACK_BOT_TOKEN
14/16 channels confirmed. 2 pending /invite:
- [ ] `/invite @syntharra` in #alerts-syntharra-com
- [ ] `/invite @syntharra` in #admin-syntharra-com

## Email Intelligence — LIVE ✅
ID: `PavRLBVQQpWrKUYs` | Active | 15-min schedule | Single Gmail credential (daniel@syntharra.com)
Scans 10 aliases → Groq scores 1-5 → drops ≤2 → posts to per-alias channel

## E2E Tests
- Standard: 75/75 ✅
- Premium: 89/89 ✅

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Items
- [ ] /invite @syntharra in #alerts-syntharra-com + #admin-syntharra-com (2 remaining)
- [ ] Add chat:write.public scope to Slack app (eliminates need to invite bot to future channels)
- [ ] Live smoke test call to +18129944371 (Dan — manual)
- [ ] Apply Standard MASTER improvements to HVAC Premium TESTING + test
- [ ] Go-live: unpause syntharra
