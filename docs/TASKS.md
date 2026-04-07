# Syntharra Open Tasks
_Last updated 2026-04-07 (batch 3). Open work only._

## Track A -- Gated on Dan
- [ ] Activate Stripe live mode (recreate products, prices, coupons, webhook + signing secret)
- [ ] Add Stripe webhook_signing_secret to syntharra_vault
- [ ] Telnyx SMS approval
- [ ] Unpause syntharra-ops-monitor Railway service
- [ ] Attach Supabase service-role credential to Premium Integration Dispatcher
- [ ] Wire Slack + Supabase/Postgres credentials on 7 MON/MAINT workflows + publish
- [ ] Manual UI: Premium Dispatcher Jobber/GCal retry patch (file: /Cowork/premium_dispatcher_patched.js)
- [ ] Manual UI import: Std + Prem onboarding idempotency JSONs (/Cowork/workflows/)
- [ ] Manual UI import: Stripe hardened webhook (xKD3ny6kfHL0HHXq)
- [ ] Approve RLS enablement on hvac_call_log, stripe_payment_data, agent_prompts
- [ ] Approve replacing USING(true) RLS policies (9 tables)
- [ ] Get n8n API key into Claude env so future patches auto-deploy

## Pre-scenario-testing
- [ ] Re-run n8n fetch() audit on remaining ~14 workflows (excl onboarding/Stripe)
- [ ] Build v2 Retell-native call processors (refactor plan: docs/audits/2026-04-07-retell-native-refactor.md)
- [ ] Migrate 18+ hardcoded secrets to credentials (P0 batch)

## Hardening (P2)
- [ ] Refactor 5 long-running n8n workflows for queue-mode
- [ ] DLQ writes from Premium dispatcher

## Done in this session (batches 1-3)
- 8 hot-table indexes + idx_hvac_call_log_call_id
- stripe_processed_events table
- dunning_state table + retry index
- client_agents.submission_id UNIQUE column
- 12mo partition pre-creation through 2027_03
- search_path pinned on 3 trigger functions
- Premium Dispatcher hardcoded SRK removed
- 5 fetch() violations fixed
- 7 monitoring/maintenance workflows created (draft)
- Std + Prem onboarding idempotency JSONs built + validated
- Stripe hardened webhook JSON built (sig verify + idempotency + dunning routing)
- Premium Dispatcher retry patch prepared
- Retell-native refactor plan published
