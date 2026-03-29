# Syntharra — Remaining Steps (Tonight)

## 1. Fix Stripe Checkout Buttons (5 min)
The "Get Started" buttons on the checkout page return "Failed to create checkout session."
The server.js now returns the actual Stripe error detail so you can see what's wrong.

**Steps:**
1. Go to [Railway Dashboard](https://railway.app) → syntharra-checkout service
2. Click **Variables** tab
3. Check `STRIPE_SECRET_KEY` is set — it should start with `sk_test_`
4. If missing or wrong, get it from [Stripe Dashboard](https://dashboard.stripe.com/apikeys) → Standard keys → Secret key
5. Paste it as the value for `STRIPE_SECRET_KEY`
6. Railway will auto-redeploy
7. Test: go to https://checkout.syntharra.com and click "Get Started"

**If it still fails:** Open browser dev tools (F12) → Network tab → click the button → check the response body. The `detail` field now shows the actual Stripe error.

---

## 2. Custom Domains on Railway (10 min)
Currently: `checkout.syntharra.com` and `syntharra-oauth-server-production.up.railway.app`
Target: `checkout.syntharra.com` and `auth.syntharra.com`

**Steps for each domain:**

### Railway side:
1. Go to Railway → select the service (checkout or oauth)
2. Click **Settings** → **Networking** → **Custom Domain**
3. Add: `checkout.syntharra.com` (or `auth.syntharra.com`)
4. Railway will show you a CNAME target (something like `xxx.up.railway.app`)

### DNS side (Squarespace):
1. Log into Squarespace → Domains → syntharra.com → DNS Settings
2. Add a CNAME record:
   - **Host:** `checkout` (just the prefix, not the full domain)
   - **Value:** the CNAME target Railway gave you
   - **TTL:** leave default
3. Repeat for `auth`
4. Wait 5-10 min for DNS propagation
5. Railway will auto-provision SSL

**After both are done:** Update these URLs across the system:
- `syntharra-checkout/public/index.html` — update any self-referencing links
- `syntharra-website/index.html` — update checkout links from `checkout.syntharra.com` to `checkout.syntharra.com`
- n8n workflows — update any webhook URLs that reference the old Railway URLs

---

## 3. Stripe Test → Live Mode (15 min)
**DO NOT DO THIS until you've tested the full flow end-to-end in test mode first.**

When ready to go live:

### Stripe Dashboard:
1. Toggle the **Test/Live** switch at the top of Stripe Dashboard
2. **Create Products** (same names):
   - Standard — AI Receptionist: Monthly $497, Annual $414/mo
   - Premium — AI Receptionist Pro: Monthly $997, Annual $831/mo
3. **Create Prices** for each (recurring)
4. **Create Setup Fee prices** (one-time): Standard $1,499, Premium $2,499
5. **Create Coupons** (same code names):
   - FOUNDING-STANDARD (100% off Standard setup fee, once)
   - FOUNDING-PREMIUM (100% off Premium setup fee, once)
   - CLOSER-250 ($250 off, once)
   - CLOSER-500 ($500 off, once)
   - CLOSER-750 ($750 off, once)
   - CLOSER-1000 ($1,000 off, once)
6. **Create Webhook:**
   - URL: `https://syntharra.app.n8n.cloud/webhook/syntharra-stripe-webhook`
   - Events: `checkout.session.completed`
   - Copy the new signing secret

### Update Code:
1. Railway → syntharra-checkout → Variables → change `STRIPE_SECRET_KEY` to `sk_live_...`
2. Update `server.js` price IDs (6 prices — Standard monthly/annual/setup, Premium monthly/annual/setup)
3. n8n Stripe Workflow → update the webhook signing secret
4. n8n Stripe Workflow → update the price ID lookup table in "Extract Session Data" node

**Reference:** `syntharra-automations/docs/discount-codes.md` has all current test mode IDs

---

## 4. Telnyx Phone Numbers (waiting)
Status: Account created, $5 credit loaded, identity verified. Waiting on AI agent evaluation approval.

**When approved:**
1. Purchase a toll-free number in Telnyx portal
2. Configure the number to forward to Retell
3. Update Supabase `hvac_standard_agent` with the new number
4. Test with a real call

**If Telnyx takes too long:** Plivo is the backup. NOT Twilio.

---

## 5. Test the Full Flow End-to-End
Before going live, run through this:

1. **Checkout:** Go to checkout page → select Standard Monthly → use test card `4242 4242 4242 4242`
2. **Welcome Email:** Check you receive the Stripe welcome email with Jotform link
3. **Jotform:** Complete the onboarding form with test data
4. **Agent Created:** Check Supabase `hvac_standard_agent` for the new row
5. **You're Live Email:** Check you receive the "You're Live" email with QR codes + PDF
6. **Test Call:** Call the AI receptionist number → have a conversation
7. **Call Alert:** Check you receive the call alert email with caller details
8. **Dashboard:** Check syntharra.com/dashboard.html?agent_id=X shows the call

---

## 6. Reminder: Don't Change Emails to support@ Yet
All internal notifications currently go to daniel@syntharra.com. Switch to support@syntharra.com after you get a few sales and have the support@ inbox set up.

---

## Quick Reference — What's Live Now

| System | Status |
|---|---|
| Website (syntharra.com) | ✅ Live — quiz, exit-intent, all pages |
| Checkout page | ⚠️ Buttons broken — fix STRIPE_SECRET_KEY |
| n8n (17 workflows) | ✅ All active, all emails branded |
| Supabase | ✅ All tables live |
| Retell agents | ✅ Arctic Breeze + 2 demos live |
| Email branding | ✅ All 9 templates approved and deployed |
| Call Forwarding PDF | ✅ Built and attached to onboarding email |
| AI Readiness Quiz | ✅ Live on homepage |
| Stripe | ⚠️ TEST MODE — needs switching to live |
| Phone numbers | ⚠️ Waiting on Telnyx approval |
| Custom domains | ❌ Not set up yet |
