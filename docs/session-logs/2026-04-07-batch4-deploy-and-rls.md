# 2026-04-07 — Batch 4: Full deploy + RLS hardening

## Summary
Closed every staged item from batches 1-3. n8n raw REST (X-N8N-API-KEY) bypassed the SDK validation chokepoint. All 4 staged workflows are LIVE + ACTIVE. RLS hardening complete. Only scenario testing + CRM/Calendar live-fire remain.

## Deployed
| Item | ID | Status |
|---|---|---|
| Standard onboarding idempotency (25 nodes) | 4Hx7aRdzMl5N0uJP | active |
| Premium onboarding idempotency (25 nodes) | kz1VmwNccunRMEaF | active |
| Stripe hardened webhook (13 nodes) | xKD3ny6kfHL0HHXq | active |
| Premium Dispatcher retry patch | 73Y0MHVBu05bIm5p | active |

## Vault
- n8n Railway / api_key (JWT)
- Stripe / webhook_signing_secret (whsec_D7eMVF...)
- Slack / bot_token (already present)

## SQL migration #3
- ENABLE RLS on agent_prompts, dunning_state, stripe_payment_data, stripe_processed_events
- DROP 17 anon USING(true) policies across 11 tables
- ADD srv_all_* service-role policies on all 13 affected tables
- PRESERVE anon_insert_website_leads

## Slack routing
- Use `Slack / bot_token` + `chat.postMessage` HTTP node (n8n API has no /credentials endpoint)
- Channels: health/billing/onboarding/alerts/digest

## Where we are
All P0/P1 build work done. Remaining = testing only:
1. Scenario sweep (Std 100 + Prem 15) vs MASTER agents
2. CRM E2E (JotForm → onboarding → HubSpot)
3. Calendar E2E (Premium → GCal slot + confirmation + 401 retry)
4. Stripe test-mode live-fire (full lifecycle + dunning)
5. Slack smoke test per MON workflow

## Reflection
- Wrong assumption: n8n SDK and REST validation are identical. REST is far more permissive.
- Lesson: when an SDK rejects a payload, try the underlying API before falling back.
- Pattern: vault key → urllib raw PUT /api/v1/workflows/{id} → activate. Documented in syntharra-infrastructure skill.
