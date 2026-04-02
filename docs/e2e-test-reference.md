# E2E Test — HVAC Standard Agent

> **Status: 75/75 ✅ — Last verified 2026-04-02**  
> Script: `shared/e2e-test.py`  
> Full skill reference: `skills/e2e-hvac-standard/SKILL.md`

## Quick Start

```bash
python3 shared/e2e-test.py
```

Expected: `75/75 passed | 0 failed ✅ ALL SYSTEMS GO`

## What It Tests

Full pipeline: **Jotform → n8n → Supabase → Retell → Call Processor**

| Phase | What's checked |
|---|---|
| 1 | Jotform webhook → HTTP 200 |
| 2 | n8n onboarding workflow → success (polling, up to 45s) |
| 3 | Supabase `hvac_standard_agent` — 40+ fields all populated |
| 4 | Retell agent — exists, published, correct voice/webhook |
| 5 | Conversation flow — 12 nodes, correct structure |
| 6 | Call processor — fake call logged + scored in `hvac_call_log` |
| 7 | Stripe gate — Twilio correctly skipped in test mode |

## Key IDs

| Resource | ID |
|---|---|
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` |
| Call processor workflow | `Kg576YtPM9yEacKn` |
| Cleanup workflow | `URbQPNQP26OIdYMo` |
| Jotform Standard form | `260795139953066` |

## Related Files

| File | Purpose |
|---|---|
| `shared/e2e-test.py` | The test script (run this) |
| `skills/e2e-hvac-standard/SKILL.md` | Full skill reference for Claude |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | Master template spec (12 nodes) |
| `retell-agents/archive/node-code-*.js` | n8n node code snapshots |

## Test Mode vs Live Mode

| Mode | How | Difference |
|---|---|---|
| TEST (default) | Run as-is | No Twilio purchase, email has no phone number |
| LIVE | Set `STRIPE_CUSTOMER_ID = 'cus_xxx'` at top of file | Real Twilio number purchased |
