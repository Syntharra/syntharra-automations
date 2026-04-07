# Syntharra Open Tasks
_Last updated 2026-04-07 (batch 4). Open work only._

## Track A — Final pre-launch testing (where we are now)
- [ ] Full scenario test sweep — Standard 100 + Premium 15 (e2e against MASTER agents)
- [ ] CRM end-to-end test — JotForm → n8n onboarding → HubSpot deal + contact + pipeline move
- [ ] Calendar end-to-end test — Premium dispatcher books real GCal slot, confirmation back, 401 retry path
- [ ] Stripe test-mode webhook live-fire — checkout → invoice.payment_succeeded → failed → dunning advance
- [ ] Slack alert smoke test — one message per channel from each of the 7 MON workflows

## Track B — Gated on Dan
- [ ] Activate Stripe LIVE mode (recreate products/prices/coupons/webhook + swap whsec_)
- [ ] Telnyx SMS approval
- [ ] Unpause syntharra-ops-monitor Railway service post-launch

## Done in batch 4
- n8n raw REST API deploy path unlocked (X-N8N-API-KEY)
- Std onboarding idempotency (4Hx7aRdzMl5N0uJP) — DEPLOYED + ACTIVE
- Prem onboarding idempotency (kz1VmwNccunRMEaF) — DEPLOYED + ACTIVE
- Stripe hardened webhook (xKD3ny6kfHL0HHXq) — DEPLOYED + ACTIVE; whsec_ in vault
- Premium Dispatcher Jobber/GCal retry patch — DEPLOYED + ACTIVE
- RLS enabled on agent_prompts, dunning_state, stripe_payment_data, stripe_processed_events
- 17 anon USING(true) policies dropped → service-role-only
- website_leads anon INSERT preserved
- Slack bot_token confirmed in vault — 7 MON workflows being patched to chat.postMessage with channel routing

## Done batches 1–3
- 8 hot-table indexes; stripe_processed_events; dunning_state; client_agents.submission_id UNIQUE
- 12mo partitions through 2027_03; search_path pinned on 3 trigger fns
- Premium Dispatcher SRK removed; 5 fetch() violations fixed
- 7 MON/MAINT workflow drafts; Retell-native refactor plan published
