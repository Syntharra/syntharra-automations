# Syntharra — Remaining Steps (Updated 2026-03-29)

## COMPLETED TODAY
- ✅ Checkout fixed (Stripe rendering_options + invoice_creation errors)
- ✅ Custom domains live: checkout.syntharra.com + auth.syntharra.com
- ✅ All URLs updated across website, checkout, automations, n8n workflows
- ✅ Stripe webhook E2E tested — payment → Supabase → welcome email → internal notification
- ✅ All 9 email templates deployed with approved branding
- ✅ AI Readiness Quiz live on homepage
- ✅ ai-receptionist skill rewritten for production stack
- ✅ Internal notifications now go to support@/onboarding@ (not daniel@)
- ✅ Orphaned Respond to Webhook node removed from Stripe workflow

---

## 1. Stripe Test → Live Mode (15 min)
When ready to accept real payments:

**Stripe Dashboard (toggle to Live mode):**
- Create Products: Standard AI Receptionist + Premium AI Receptionist Pro
- Create 6 Prices: Std Monthly $497, Std Annual $414/mo, Std Setup $1,499, Prem Monthly $997, Prem Annual $831/mo, Prem Setup $2,499
- Create 6 Coupons: FOUNDING-STANDARD, FOUNDING-PREMIUM, CLOSER-250, CLOSER-500, CLOSER-750, CLOSER-1000
- Create Webhook: `https://syntharra.app.n8n.cloud/webhook/syntharra-stripe-webhook` → `checkout.session.completed`

**Update code:**
- Railway → syntharra-checkout → Variables → `STRIPE_SECRET_KEY` to `sk_live_...`
- `server.js` → update all 6 price IDs
- n8n Stripe Workflow → update price ID lookup table in Extract Session Data node
- n8n Stripe Workflow → update webhook signing secret

Reference: `docs/discount-codes.md`

---

## 2. Telnyx Phone Numbers (waiting on approval)
Account created, $5 credit, identity verified. Waiting on AI agent evaluation.
When approved: purchase toll-free number, configure forwarding to Retell, update Supabase.
Backup: Plivo (NOT Twilio).

---

## 3. OAuth / API / CRM Integrations (Premium)
Complete the OAuth setup for all Premium client integrations. The OAuth server is live at auth.syntharra.com — each platform needs its own OAuth app credentials registered.

**Calendar Integrations:**
- Google Calendar — ✅ OAuth working, tokens saving to Supabase
- Outlook/Microsoft Calendar — needs Azure AD app registration + OAuth flow
- Calendly — needs OAuth app in Calendly developer portal
- Cal.com — needs API key integration (no OAuth, simpler)
- Acuity Scheduling — needs OAuth app in Squarespace developer portal

**CRM Integrations:**
- HubSpot — needs OAuth app in HubSpot developer portal
- GoHighLevel — needs OAuth app in GHL marketplace
- Zoho CRM — needs OAuth app in Zoho API console
- Jobber — needs OAuth app in Jobber developer portal
- Housecall Pro — needs API key integration (check if OAuth available)
- ServiceTitan — needs API partnership application (longer process)

**For each platform:**
1. Register an OAuth app / API key in the provider's developer portal
2. Add client ID + secret to Railway OAuth server env vars
3. Add the OAuth flow route in syntharra-oauth-server/server.js
4. Test the connection end-to-end
5. Update the Premium Onboarding workflow to trigger the correct OAuth flow based on Jotform selection

Reference: `docs/oauth-platform-setup-guide.md` has step-by-step for each provider.

---

## 4. Test Full Flow End-to-End (before going live)
1. Checkout page → select plan → Stripe test card `4242 4242 4242 4242`
2. Verify welcome email received with correct plan details + Jotform link
3. Complete Jotform with test data
4. Verify agent created in Retell + saved to Supabase
5. Verify "You're Live" email received with QR codes + PDF
6. Call the AI receptionist number → test conversation
7. Verify call alert email received with caller details
8. Check dashboard shows the call

---

## Quick Reference — Current Status

| System | Status |
|---|---|
| Website (syntharra.com) | ✅ Live |
| Checkout (checkout.syntharra.com) | ✅ Working (test mode) |
| Auth (auth.syntharra.com) | ✅ Live (Google Cal working) |
| n8n (17 active workflows) | ✅ All active, branded |
| Supabase | ✅ All tables live |
| Retell agents | ✅ Arctic Breeze + 2 demos |
| Email branding | ✅ All 9 templates deployed |
| Stripe | ⚠️ TEST MODE |
| Phone numbers | ⚠️ Waiting on Telnyx |
| OAuth/CRM integrations | ⚠️ Only Google Calendar done — rest need setup |
