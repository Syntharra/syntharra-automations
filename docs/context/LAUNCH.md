# Syntharra — Launch Status
> Load when: discussing go-live, Stripe switch, SMS, pre-launch items

## Current Status: PRE-LAUNCH | TEST MODE

## Primary Gate: Stripe Live Mode
Nothing goes live until Stripe switches. Checklist:
- [ ] Activate Stripe account (Dan action)
- [ ] Switch to live mode
- [ ] Recreate products, prices, coupons (same names — IDs change)
- [ ] Recreate webhook in live mode
- [ ] Update Railway `STRIPE_SECRET_KEY` → `sk_live_`
- [ ] Update n8n webhook signing secret

## Secondary Items
- [ ] Telnyx: buy toll-free number once AI evaluation approved, set `SMS_ENABLED=true`
- [ ] Unpause ops monitor (Railway — service ID `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`)
- [ ] Set `PRE_LAUNCH_MODE=false` in ops monitor `retell.js`
- [ ] Confirm all 15 n8n workflows are Active
- [ ] Smoke test: call test phone number, submit test Jotform as a real client would

## What's Working (TEST MODE)
- Standard pipeline: onboarding → Jotform → agent provisioning → call processing ✅
- Premium pipeline: onboarding → OAuth → dispatcher → calendar booking ✅
- Checkout + Stripe webhook → Supabase ✅
- Admin dashboard: admin.syntharra.com ✅
- Client dashboard: syntharra.com/dashboard.html ✅
- Email flows: welcome, you're live, weekly report ✅
- Branded Stripe invoices ✅

## Not Yet Built
- WhatsApp Business (deprioritised — VoIP number rejected)
- Multi-trade expansion (plumbing, electrical) — architecture ready
- Marketing automation system (built, not activated)
