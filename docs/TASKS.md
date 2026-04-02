# Syntharra — Tasks & Continuity
> Updated at the END of every chat that changes anything.
> Load at START of every chat after CLAUDE.md. Keep under 60 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

## Last session (2026-04-02)
- Full workflow audit: 34 active → archived 2 (TEST_RUNNER + TEST STUB dispatcher) → 32 remain
- WORKFLOWS.md rewritten from live n8n (was stale/wrong IDs)
- Full stack audit of all context files against live systems
- AGENTS.md, SUPABASE.md, INFRA.md rewritten from live API data
- Agentic context system built: CLAUDE.md + docs/context/ (7 files)
- Artifacts repo built: brand, signatures, emails, dashboard, sales tools

## Action Items from Audit (needs Dan input)
- [ ] **Phone +18129944371 shows UNASSIGNED in Retell** — verify it's wired to Arctic Breeze agent
- [ ] **Confirm Premium Supabase table names** — `hvac_premium_agent` and `hvac_premium_call_log` return 404
- [ ] **Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6)** — what is this? Keep or delete?
- [ ] **Agent "V7 Premium FrostKing HVAC"** — is this a test client? Document or clean up
- [ ] **e2e_test_results table** — 404 in Supabase, was referenced in E2E tests. Create or remove reference?

## In Progress
- [ ] Syntharra brand theme factory skill — Dan to paste .skill file from Claude Code
- [ ] Rebuild artifacts once theme factory installed
- [ ] Email artifacts: welcome-premium, hot-lead-alert still scaffold only

## Blocked
- Telnyx SMS — awaiting AI evaluation approval
- WhatsApp Business — VoIP rejected, deprioritised
- Ops monitor — PAUSED (Railway), unpause at go-live

## Next Actions (priority order)
1. Dan confirms action items above (phone, table names, agents)
2. Dan pastes theme factory .skill → install as syntharra-brand skill
3. Build welcome-premium + hot-lead-alert artifacts
4. Stripe live mode cutover when Dan confirms ready

## Go-Live Gate (Stripe)
1. Activate Stripe account → switch to live mode
2. Recreate all products, prices, coupons (same names — IDs change)
3. Update Railway env `STRIPE_SECRET_KEY` → `sk_live_`
4. Update n8n webhook signing secret
5. Unpause ops monitor, set SMS_ENABLED=true once Telnyx approved
