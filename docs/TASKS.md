# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Full E2E test + all bugs fixed

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## Completed This Session
- Full E2E test run: 64/75 passing (3 false failures, 8 real issues fixed)
- BUG FIX: n8n Parse JotForm Data — added notification_email_2/3 + notification_sms_2/3 mapping
- BUG FIX: n8n Build Retell Prompt — added callback + spam_robocall nodes (10→12 nodes)
- BUG FIX: E2E test — corrected node count assertion (13→12) + agent_name assertion
- Pushed master template reference: retell-agents/hvac-standard-MASTER-TEMPLATE.json
- Confirmed: 18-node flows are Premium (booking/calendar), Standard = 12 nodes
- Confirmed: Arctic Breeze live flow has 14 nodes (extra: emergency_fallback + spanish_routing — specific to that client)
- Workflow now pushed live to n8n and active

## Open Action Items (needs Dan input)
- [ ] Phone +18129944371 shows UNASSIGNED in Retell — verify wired to Arctic Breeze agent
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?
- [ ] Dan to paste Syntharra theme factory .skill from Claude Code when at PC

## Blocked
- Telnyx SMS — awaiting AI evaluation approval (account active, $5 loaded)
- WhatsApp Business — VoIP rejected, deprioritised
- Ops monitor — PAUSED (service 7ce0f943), unpause at go-live

## Next Session — Start With
1. Say "Start session" — I'll fetch CLAUDE.md + TASKS.md and confirm state
2. Run full E2E test again to verify 75/75
3. Resolve phone number assignment (+18129944371 → Arctic Breeze)
4. Dan pastes theme factory .skill → install → rebuild artifacts

## Go-Live Gate (Stripe)
1. Activate Stripe account → switch to live mode
2. Recreate all products, prices, coupons (same names — IDs change)
3. Update Railway STRIPE_SECRET_KEY → sk_live_
4. Update n8n webhook signing secret
5. Unpause ops monitor, enable SMS once Telnyx approved
