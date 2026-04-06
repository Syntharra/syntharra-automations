# TASKS

## Track A — gated on Dan
- [ ] A1 Stripe live migration (run tools/stripe_live_migration.py once sk_live_ available)
- [ ] A2 Ops monitor unpause (Railway service 7ce0f943) — runbook ready
- [ ] A3 Telnyx 10DLC chase email — draft ready

## Track C — hardening
- [ ] C1 n8n queue mode + 2 workers (Railway env change)
- [ ] C3 Enable Supabase PITR
- [ ] C4 Ops dashboard scaffold
- [ ] Schedule tools/partition_janitor.py monthly from n8n
- [ ] Drop hvac_call_log_pre_partition after 7-day soak (target 2026-04-14)

## Track D
- [ ] D3 Apply n8n label scheme to 37 workflows
- [ ] D5 Build proper Premium MASTER agent via retell-iac manifest (after scenario testing confirms current)

## Security debt
- [ ] Move hardcoded Supabase service role key out of n8n workflow 73Y0MHVBu05bIm5p (Premium Integration Dispatcher) into n8n credentials
