# Syntharra Open Tasks

_Last updated 2026-04-07. Open work only. Reference data lives in REFERENCE.md._

## Track A — Gated on Dan
- [ ] Activate Stripe live mode (recreate products, prices, coupons, webhook + signing secret)
- [ ] Telnyx SMS approval
- [ ] Unpause `syntharra-ops-monitor` Railway service
- [ ] Attach Supabase service-role credential to Premium Integration Dispatcher (post SRK removal)
- [ ] Approve RLS enablement on `hvac_call_log`, `stripe_payment_data`, `agent_prompts`
- [ ] Approve replacing `USING (true)` RLS policies (9 tables)

## Track B — Done ✓
- B1 `client_agents` registry, B2 rollout.py, B3 canary.py, C2 monthly partitioning, D4 Premium rename

## Pre-scenario-testing (P0/P1 from 2026-04-07 audit)
- [ ] Onboarding: add idempotency lookup before Retell clone (Std + Prem)
- [ ] Onboarding: insert into `client_agents` after agent creation (Std + Prem)
- [ ] Onboarding: real error branches on Retell clone, route fails to DLQ
- [ ] Premium Dispatcher: Jobber GraphQL exponential backoff on 429/5xx
- [ ] Premium Dispatcher: Google Calendar 401 retry loop
- [ ] Call ingestion: require `call.start_timestamp`, drop `new Date()` fallback
- [ ] Stripe: webhook signature verification (HMAC against `Stripe-Signature`)
- [ ] Stripe: idempotency guard using `stripe_processed_events`
- [ ] Stripe: handle subscription.* + invoice.payment_failed (dunning)
- [ ] Stripe: locate or build monthly overage aggregator
- [ ] n8n: migrate 18+ hardcoded secrets to credentials/env (P0 batch)
- [ ] n8n: replace 5 raw `fetch()` calls with `this.helpers.httpRequest`
- [ ] Alerting: per-client success-rate < 90 % (P0)
- [ ] Alerting: Retell error-rate spike > 2 % (P0)
- [ ] Alerting: n8n critical workflow failure rate
- [ ] Alerting: Supabase pool saturation
- [ ] Verify Brevo on every email-sending node (zero SMTP2GO references confirmed)

## Hardening (P2)
- [ ] Pin `search_path` on 4 trigger functions
- [ ] Refactor 5 long-running n8n workflows for queue-mode (no static data)
- [ ] Pre-partition automation as a scheduled n8n workflow (currently manual)
- [ ] DLQ writes from call processors and Premium dispatcher
