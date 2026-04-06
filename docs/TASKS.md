# Syntharra — Open Tasks
> Open work only. Updated 2026-04-06.

## Critical Path (before client #50)
- [ ] **Phase 6-8 fleet rollout** — client_agents table, rollout.py, canary. 3 wks. See docs/SCALE-REVIEW-1000-CLIENTS.md
- [ ] Ops monitor Railway redeploy — service 7ce0f943
- [ ] Stripe go-live: activate → recreate products/prices/coupons/webhook → sk_live_
- [ ] Telnyx SMS + voice approval pending

## Agent / Testing
- [ ] E2E full run before launch (Std + Prem both green 2026-04-06)

## Infrastructure (scale)
- [ ] n8n queue mode + workers (blocks 50 concurrent onboardings)
- [ ] Ops dashboard + client_health_scores populator (blocks 100 clients)
- [ ] Partition hvac_call_log by month (year-2)
- [ ] Indexes: hvac_standard_agent(agent_id, phone_number), hvac_call_log(agent_id, created_at)
- [ ] Supabase PITR + nightly retell-iac snapshot

## Marketing
- [ ] First cold email batch activation (n8n + SMTP2GO→Brevo)
- [ ] Google Ads campaigns activation

## Cleanup / Hygiene
- [ ] Review n8n workflow 73Y0MHVBu05bIm5p (Premium Integration Dispatcher)
- [ ] Re-enable MCP on 6LXpGffcWSvL6RxW (Weekly Newsletter) or confirm off
- [ ] Apply n8n label scheme: ONBOARDING/BILLING/PREMIUM-OPS/CALL-PROCESSOR/TESTING/COMMS/MARKETING/OPS/WEBHOOKS
- [ ] Rename Retell "HVAC Premium (TESTING)" → "HVAC Premium (MASTER interim)"
