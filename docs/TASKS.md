# Syntharra — Tasks & Continuity
> Updated at the END of every chat that changes anything.
> Load this at the START of every chat after CLAUDE.md.
> Keep it under 60 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

## Last session (2026-04-02)
- Built `syntharra-artifacts` repo with brand showcase, signatures, 3 email previews, client dashboard, VSL, ROI calculator
- Removed Agent Scenario Testing from admin dashboard (sec-testing now has infra + e2e only)
- Built agentic context system (CLAUDE.md + docs/context/ files) — THIS session
- Updated syntharra-admin and syntharra-ops skills with new patterns

## In progress
- [ ] Syntharra brand theme factory skill — Dan to paste .skill file from Claude Code
- [ ] Admin dashboard testing section redesign — partially done, needs final push to GitHub
- [ ] Email artifacts: welcome-premium, hot-lead-alert still scaffold only

## Blocked
- Telnyx SMS — awaiting AI evaluation approval before buying toll-free number
- WhatsApp Business — VoIP number rejected, deprioritised
- Ops monitor — PAUSED (Railway) to stop test-mode alert spam, unpause at go-live

## Next actions (priority order)
1. Dan to paste theme factory .skill → install as `syntharra-brand` skill
2. Rebuild all artifacts using correct theme factory standards
3. Finish admin dashboard testing section (push to GitHub)
4. Build `welcome-premium.jsx` and `hot-lead-alert.jsx` artifacts
5. Build the full agentic context folder (docs/context/) — THIS session
6. Stripe live mode cutover — when Dan confirms ready

## Go-live gate (Stripe)
1. Activate Stripe account
2. Switch to live mode — recreate all products, prices, coupons (same names)
3. Update Railway env `STRIPE_SECRET_KEY` → `sk_live_`
4. Update n8n webhook signing secret
5. Discount codes doc: `docs/discount-codes.md`
