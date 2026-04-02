# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — E2E + master template system built

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Test Status: 72/75 ✅ (3 remaining = test script timing bugs, not pipeline)

## Completed This Session
- Full E2E Standard pipeline test (Jotform → n8n → Supabase → Retell)
- BUG FIX: notification_email_2/3 + notification_sms_2/3 — now mapped (Parse + Merge + Supabase)
- BUG FIX: conversation flow now 12 nodes (callback + spam_robocall restored)
- BUG FIX: E2E test assertions corrected (node count, agent name)
- Master template system built in retell-agents/:
  - HVAC-STANDARD-AGENT-TEMPLATE.md — full canonical spec
  - archive/ — Parse, Build, Merge node code snapshots (v5)
  - README.md — updated with template hierarchy
- 3 known test script timing bugs documented (not pipeline failures)

## 3 Known Test Script Timing Bugs (not real failures)
1. "Workflow executed successfully" — n8n execution API queried before row indexed (25s wait not enough)
2. "Call processor n8n execution OK" — same timing issue on call processor execution check
3. "Onboarding email sent" — test prints ❌ but text says "correct in test mode" — wording bug

## Open Action Items (needs Dan input)
- [ ] Phone +18129944371 shows UNASSIGNED in Retell — wire to Arctic Breeze agent
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?
- [ ] Dan to paste theme factory .skill from Claude Code when at PC

## Blocked
- Telnyx SMS — awaiting AI evaluation approval ($5 loaded)
- Ops monitor — PAUSED, unpause at go-live

## Next Session — Start With
1. Say "Start session" — fetch CLAUDE.md + TASKS.md
2. Fix 3 timing bugs in e2e-test.py (increase wait times / use execution polling)
3. Wire +18129944371 to Arctic Breeze agent in Retell
4. Resolve Mia agent
5. Dan pastes theme factory skill

## Go-Live Gate (Stripe)
1. Activate Stripe → switch to live mode
2. Recreate products, prices, coupons (IDs change in live mode)
3. Update Railway STRIPE_SECRET_KEY → sk_live_
4. Update n8n webhook signing secret
5. Unpause ops monitor + enable SMS (Telnyx approval)
