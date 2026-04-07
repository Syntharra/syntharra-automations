# Syntharra Open Tasks

_Last updated 2026-04-07 (post second batch). Open work only._

## Track A — Gated on Dan
- [ ] Activate Stripe live mode (recreate products, prices, coupons, webhook + signing secret)
- [ ] Telnyx SMS approval
- [ ] Unpause syntharra-ops-monitor Railway service
- [ ] Attach Supabase service-role credential to Premium Integration Dispatcher (post SRK removal)
- [ ] Wire Slack + Supabase/Postgres credentials on 7 new MON/MAINT workflows + publish
- [ ] Manual UI edit: Premium Dispatcher Jobber 429 backoff + GCal 401 refresh retry (SDK blocked)
- [ ] Approve RLS enablement on hvac_call_log, stripe_payment_data, agent_prompts
- [ ] Approve replacing USING (true) RLS policies (9 tables)

## Pre-scenario-testing P0/P1
- [ ] Onboarding: idempotency lookup + client_agents insert (Std + Prem)
- [ ] Onboarding: real Retell error branches → DLQ
- [ ] Stripe: webhook signature verification (HMAC)
- [ ] Stripe: idempotency guard via stripe_processed_events
- [ ] Stripe: handle subscription.* + invoice.payment_failed (dunning)
- [ ] Stripe: monthly overage aggregator
- [ ] n8n: migrate 18+ hardcoded secrets to credentials (P0 batch)
- [ ] n8n: scan remaining 14 workflows for fetch() (excl onboarding/Stripe)

## Re-scoped (Retell-native pivot)
- [ ] Audit Retell post_call_analysis / call_analysis fields vs custom processors
- [ ] Refactor Kg576YtPM9yEacKn + STQ4Gt3rH8ptlvMi to passthrough + Retell-native enrichment

## Hardening (P2)
- [ ] Refactor 5 long-running n8n workflows for queue-mode
- [ ] DLQ writes from Premium dispatcher

## Done ✓ this session
- 8 hot-table indexes + idx_hvac_call_log_call_id
- stripe_processed_events table
- 12mo partition pre-creation
- search_path pinned on 3 trigger functions
- Premium Dispatcher hardcoded SRK removed
- 5 fetch() violations fixed
- 7 monitoring/maintenance workflows created (draft)
