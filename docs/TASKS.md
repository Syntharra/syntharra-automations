# Syntharra — Tasks & Continuity
> Updated: 2026-04-03 — Slack setup guide PDF created for Premium clients.

## Status: PRE-LAUNCH | Stripe TEST MODE | 35 active workflows

## Slack Internal Notifications — COMPLETE ✅
- Bot: @syntharra (U0AQR9PQWCS) | Scopes: chat:write, chat:write.public, incoming-webhook
- SLACK_BOT_TOKEN in vault + Railway (n8n + ops-monitor)
- 16/16 channels confirmed live

## Ops Monitor — COMPLETE ✅
- Email alerts: PAUSED | Slack: warning+critical → #ops-alerts | SMS: critical only ✅

## Email Intelligence — LIVE ✅
- ID: PavRLBVQQpWrKUYs | Active | 15-min schedule | daniel@syntharra.com credential
- 10 aliases → per-alias channel routing

## Daily Ops Digest — LIVE ✅
- ID: SiMn59qJOfrZZS81 | Active | 6am GMT daily → #all-syntharra
- Covers: clients, 24h calls/leads, MRR, system health
- Timezone: GMT/UTC (Europe/London for date label)

## E2E Tests
- Standard: 75/75 ✅ | Premium: 89/89 ✅

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard | agent_4afbfdb3fcb1ba9569353af28d | ✅ MASTER LIVE |
| HVAC Premium | agent_9822f440f5c3a13bc4d283ea90 | ✅ MASTER |
| HVAC Standard TESTING | agent_731f6f4d59b749a0aa11c26929 | ✅ Synced |

## Open Items
- [ ] Live smoke test call to +18129944371 (Dan — manual)
- [ ] Slack setup guide PDF → email Premium clients manually when Slack webhook received at support@
- [ ] Wire Slack webhook into Premium call processor (manual trigger — support team inputs URL)
- [ ] Apply Standard MASTER improvements to HVAC Premium TESTING + test
- [ ] Go-live: unpause Syntharra, flip Stripe to live mode
