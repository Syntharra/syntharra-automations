# Syntharra Deploy Guide — Google Cloud OAuth + Next Steps

**Created:** 2026-03-27  
**Status:** Pre-launch checklist items

---

## 1. Google Cloud OAuth Credentials

The OAuth server (`Syntharra/syntharra-oauth-server`) needs Google Cloud credentials to handle Google Calendar + Jobber integrations for Premium clients.

### Step-by-step:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing): **Syntharra AI**
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Name: `Syntharra OAuth Server`
7. Authorized redirect URIs — add:
   - `https://your-oauth-server.up.railway.app/auth/google/callback`
   - `http://localhost:3000/auth/google/callback` (for local testing)
8. Click **Create** and copy the Client ID + Client Secret

### Enable required APIs:

- Google Calendar API
- Google People API (if needed for contact sync later)

### Add to Railway environment variables:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

Set these in the **syntharra-oauth-server** Railway service (not the checkout service).

### Verify:

After deploying, hit `https://your-oauth-server.up.railway.app/auth/google` — it should redirect to Google's consent screen.

---

## 2. Telnyx SMS Activation (Pending Approval)

**Status:** Identity verified, $5 credit loaded, waiting on AI evaluation approval.

### When approved:

1. Dan provides: Telnyx API key + toll-free number
2. Claude will:
   - Update n8n SMS nodes in Standard Call Processor (`OyDCyiOjG0twguXq`) and Premium Call Processor (`UhxfrDaEeYUk4jAD`)
   - Set `SMS_ENABLED=true` in workflow logic
   - Test with a scenario run
   - Push updated workflows to GitHub

### Current state:

- All SMS nodes are wired but disabled (`SMS_ENABLED=false`)
- Telnyx HTTP request nodes already in place (replaced Twilio)
- Just needs API key + number to go live

---

## 3. Sales Pitch Pack (To Build)

Deliverables:
- One-page PDF pitch sheet (Standard + Premium tiers)
- ROI calculator (interactive, for website or standalone)
- Email sequence templates (cold outreach, follow-up, closing)
- Case study template (Arctic Breeze as first case study)
- Objection handling cheat sheet

### Approach:
- Pull pricing from Stripe config
- Use brand kit (violet #6C63FF, cyan #00D4FF, DM Serif Display + DM Sans)
- Build as downloadable PDFs + website pages

---

## 4. Weekly Usage Reports (To Build)

### Requirements:
- Automated weekly email to each client
- Data: total calls, minutes used, minutes remaining, top call types, lead count
- Source: `hvac_call_log` + `billing_cycles` tables in Supabase
- Trigger: n8n cron workflow (Monday 9am client timezone)
- Template: branded HTML email via SMTP2GO

### Architecture:
- New n8n workflow: `Weekly Client Report`
- Query Supabase for all active clients
- For each client: aggregate call data from past 7 days
- Build HTML email with charts/stats
- Send via SMTP2GO

---

## 5. CRM Integrations (Future)

Potential integrations:
- **Jobber** — already wired for Premium (dispatcher workflow `kVKyPQO7cXKUJFbW`)
- **ServiceTitan** — large HVAC market, API available
- **Housecall Pro** — popular with smaller trades
- **Salesforce** — enterprise tier potential

### Approach:
- Build as modular n8n sub-workflows
- Each CRM integration = separate workflow that the Call Processor can trigger
- Standard interface: receive call data JSON, push to CRM, return confirmation

---

## Pre-Launch Critical Checklist (Reminder)

- [ ] Complete Amazon SES DNS verification (DKIM prefix-only fix)
- [ ] Switch Stripe test → live mode (recreate products, prices, coupons, webhook)
- [ ] Update Railway `STRIPE_SECRET_KEY` to `sk_live_`
- [ ] Update n8n webhook signing secret for live Stripe
- [ ] Change internal notification emails → `support@syntharra.com`
- [ ] Google Cloud OAuth credentials (this doc, section 1)
- [ ] Telnyx SMS go-live (section 2)

---

*This document lives in `syntharra-automations/docs/` and should be updated as items are completed.*
