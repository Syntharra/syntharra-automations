# Syntharra Pre-Launch Checklist & Next Steps
**Updated: 2026-03-28**

---

## COMPLETED THIS SESSION

- [x] Full GitHub backup — all 4 repos up to date
  - `syntharra-automations`: 16 n8n workflows, 3 Retell agents, conv flow, handoff doc
  - `syntharra-website`: Dashboard v2 pushed live
  - `syntharra-checkout`: Clean, current
  - `syntharra-oauth-server`: Clean, current

- [x] Dashboard v2 improvements
  - Inline SVG logo (removed Postimages dependency)
  - Expandable call summaries (Read more / Show less)
  - Plan-aware: Standard hides booking stats, Premium shows everything
  - Time period selector (7d / 30d / All)
  - Call type filters (All / Leads / Booked / Emergency)
  - Minutes usage progress bar with color coding
  - Call duration display, emergency counter, plan badge in header

- [x] n8n workflow audit: 15 active, 17 inactive (all safe, ready for deletion)

- [x] Jotform Premium form updated:
  - CRM: Added HubSpot, GoHighLevel, Zoho CRM
  - Calendar: Added Cal.com, Acuity Scheduling

- [x] Google OAuth deploy guide created (in outputs)

- [x] Retell agent ID updated in memory (agent_4afbfdb3fcb1ba9569353af28d)

---

## CRITICAL PRE-LAUNCH (must complete before first paying client)

### 1. Google Cloud OAuth Credentials (Dan — see deploy guide)
- [ ] Create Google Cloud project + enable Calendar API
- [ ] Create OAuth credentials
- [ ] Add `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` to Railway env vars
- [ ] Test: visit `auth.syntharra.com/connect?platform=google_calendar&agent=TEST`
- **Unblocks:** Premium calendar booking for Google Calendar users

### 2. Stripe Test → Live Mode
- [ ] Activate Stripe account (if not already)
- [ ] Switch to live mode in Stripe dashboard
- [ ] Recreate all products (Standard + Premium) in live mode
- [ ] Recreate all prices (monthly + annual for each) in live mode
- [ ] Recreate all coupons (same code names: FOUNDING-STANDARD, FOUNDING-PREMIUM, CLOSER-250/500/750/1000)
- [ ] Recreate webhook in live mode → same URL `https://syntharra.app.n8n.cloud/webhook/syntharra-stripe-webhook`
- [ ] Update Railway env: `STRIPE_SECRET_KEY` → `sk_live_...`
- [ ] Update n8n Stripe workflow: new webhook signing secret
- [ ] Update `server.js` price IDs to live mode IDs
- [ ] Test: complete a real $1 test payment through the full flow
- **Unblocks:** Real payments, live customer onboarding

### 3. Telnyx SMS Activation (waiting on approval)
- [ ] Receive Telnyx AI evaluation approval
- [ ] Buy toll-free number
- [ ] Provide API key + number to Claude to wire into workflows
- [ ] Set `SMS_ENABLED=true` in call processor workflows
- **Unblocks:** SMS notifications to clients on new leads/emergencies

### 4. Internal Email Switch
- [ ] Change all `daniel@syntharra.com` → `support@syntharra.com` across all n8n workflows
- Affects: onboarding summary, lead notifications, call processor alerts, error notifications

---

## END-TO-END TEST (run after above items complete)

1. Go to pricing page → select Standard Monthly
2. Complete Stripe checkout (use FOUNDING-STANDARD coupon)
3. Confirm: Stripe webhook fires → n8n Stripe workflow runs → Supabase row created → welcome email sent with Jotform link
4. Fill out Jotform onboarding form
5. Confirm: n8n onboarding workflow runs → Retell agent created → phone number assigned → welcome email with phone number sent → Dan gets internal notification
6. Call the assigned phone number → confirm AI answers correctly
7. Check dashboard shows the call data
8. Check lead notification email/SMS arrives

---

## NEXT TO BUILD (priority order)

### Near-term
1. **Sales pitch pack** — VSL package uploaded but needs production
2. **Weekly usage reports** — enhance existing minutes calculator to send weekly client summary emails
3. **Repeat caller enhancements** — already built in call processor, needs testing at scale

### Integration expansion
4. **Microsoft Outlook OAuth** — create Azure AD app registration, add env vars to Railway
5. **Calendly OAuth** — create Calendly developer app
6. **Additional CRMs** — Zoho, Salesforce, etc. (OAuth server scaffolding exists)

### Scaling
7. **Automated lead gen system** — Google Places API scraping → Supabase, cold email sequences via n8n + SMTP2GO
8. **Branded video landing page** — VSL + booking calendar
9. **Social content calendar** — automated posting (TikTok, LinkedIn)
10. **Retell folder auto-assign** — organize agents by client
11. **Self-hosted n8n on Railway Pro** — when workflow volume requires it

---

## PLATFORM CREDENTIALS STILL NEEDED

| Platform | Type | Where to Create | Railway Env Var |
|----------|------|-----------------|-----------------|
| Google Calendar | OAuth | console.cloud.google.com | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Microsoft Outlook | OAuth | portal.azure.com | `MS_CLIENT_ID`, `MS_CLIENT_SECRET` |
| Calendly | OAuth | developer.calendly.com | `CALENDLY_CLIENT_ID`, `CALENDLY_CLIENT_SECRET` |
| Jobber | OAuth | developer.getjobber.com | `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET` |
| Housecall Pro | OAuth | developer.housecallpro.com | `HCP_CLIENT_ID`, `HCP_CLIENT_SECRET` |
| HubSpot | OAuth | developers.hubspot.com | `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET` |
| GoHighLevel | OAuth | marketplace.gohighlevel.com | `GHL_CLIENT_ID`, `GHL_CLIENT_SECRET` |

ServiceTitan, FieldEdge, Kickserv, Workiz → API key based (clients enter their own via `/submit-key` endpoint)

---

## INACTIVE N8N WORKFLOWS TO DELETE

All 17 are already unpublished. Safe to delete in n8n portal:

**Old Standard:** `0ZTMm1X19k0mBtRf`, `2gI7jDAEEf4nK5Wz`, `58CPtEzia5ReaZnQ`, `BmK96RBQl4jdRhZX`, `Dgmj8BCiqu3igGQ3`, `KhsOBdGDY2Hrat4B`, `w8iBZvJR14ir3nTi`

**Old Scenarios:** `eialTmWalhJV3PFW`, `5A0EiHXsRk1nehfv`, `siy8kxDbiuEl3tur`

**Old Premium:** `0wXZ367toqLNPFGG`, `yGNScL9rCpiPsvEQ`, `sP6gIIZS931b6Hh1`, `TWFn9WdbBw1w9OrB`

**Temp utilities:** `82Ml5Ov2rqH4zu4v`, `sQdaSXicKH8MzcwT`

**Confirm before deleting:** `8WYFy093XA6UKB7L` (Integration Hub — inactive but may be referenced)
