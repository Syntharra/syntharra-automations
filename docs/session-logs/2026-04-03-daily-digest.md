# Session Log — 2026-04-03 — Daily Ops Digest

## Completed
- Daily Ops Digest workflow (SiMn59qJOfrZZS81) — active, 6am GMT daily, #all-syntharra
- Pulls: hvac_standard_agent (clients), hvac_call_log (24h calls), Stripe (MRR), Ops Monitor (health)
- STRIPE_SECRET_KEY added to Railway n8n env vars
- Timezone label fixed: CST → GMT, America/Chicago → Europe/London
- Digest tested live — landed in #all-syntharra confirmed
- Dan confirmed: all Syntharra project work uses GMT timezone

## Lessons
- Slack blocks invalid_blocks: do NOT use dynamic .map() array in fields key. Use flat text string instead.
- GMT and UTC are identical — cron 0 6 * * * is correct for 6am GMT with no changes needed.
