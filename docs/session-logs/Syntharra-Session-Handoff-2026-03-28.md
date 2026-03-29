# Syntharra Session Handoff — 2026-03-28
## Pick up from here in the new chat

---

## COMPLETED THIS SESSION

### Deployed & Live:
- OAuth server on Railway — fixed deployment (package-lock.json, 0.0.0.0 bind, health endpoint, Procfile, railway.json)
- OAuth server — removed Postimages logo, replaced with inline SVG 4-bar icon
- OAuth server — dual-table agent lookup (premium + standard) so both plan types work
- Google Calendar OAuth — fully tested and working, tokens saving to Supabase
- SUPABASE_KEY added to Railway OAuth server env vars
- Dashboard v2 — new logo, expandable summaries, plan-aware stats, time filters, usage bar
- New 4-bar logo updated across ALL 10 website pages + favicon + OAuth server + checkout page
- Checkout page v2 — updated features list, integration badges, fixed button color, relative API calls
- 17 inactive n8n workflows deleted (workspace now: 15 active, 0 inactive)
- Arctic Breeze agent_4afbfdb3fcb1ba9569353af28d inserted into Supabase hvac_standard_agent
- Weekly client report email upgraded with branded template (stats cards, service breakdown, top leads)
- Jotform Premium form: added HubSpot, GoHighLevel, Zoho CRM, Cal.com, Acuity Scheduling
- ai-receptionist skill completely rewritten for production stack
- Brand assets saved to GitHub (PNG, SVG, white SVG of new logo)

### Documentation Created (all in GitHub syntharra-automations/docs/):
- Pre-launch checklist with E2E test plan
- Google OAuth deploy guide
- OAuth platform setup guide (all 7 integrations — Outlook, Calendly, Jobber, Housecall Pro, HubSpot, GoHighLevel)
- Retell components specifications (10 components for multi-industry scaling)
- Chat handoff doc

### All 4 GitHub repos backed up and current:
- syntharra-automations
- syntharra-website
- syntharra-checkout
- syntharra-oauth-server

---

## NEEDS DEPLOYING (network was down, couldn't push)

### 1. Checkout page — Stripe button fix
The "Get Started" buttons return "Failed to create checkout session." 
- All 6 Stripe price IDs verified correct and exist
- Issue is the STRIPE_SECRET_KEY env var on Railway — Dan needs to check it's set correctly
- Also: server.js was updated to return actual Stripe error detail (needs pushing)
- File: syntharra-checkout/server.js — change `res.status(500).json({ error: 'Failed to create checkout session.' })` to include `detail: err.message`

### 2. AI Readiness Quiz — embed on website
- Interactive 5-question quiz with scoring
- Saves to Supabase website_leads with score + answers metadata
- Triggers n8n webhook to send personalised results email
- Files ready in outputs: ai-readiness-quiz-preview.html (standalone), ai-readiness-quiz.jsx (React)
- Needs: embed into index.html replacing existing AI readiness popup, create n8n webhook workflow

### 3. Lead capture emails — 2 new n8n workflows needed
- Workflow A: /webhook/free-report → sends branded missed call revenue report
  - Code: free-report-email-node.js
  - Trigger: exit-intent popup ("Wait — before you go") email capture
- Workflow B: /webhook/ai-readiness-score → sends personalised score results  
  - Code: ai-readiness-email-node.js
  - Trigger: AI readiness quiz completion

### 4. Exit-intent popup update
- Wire existing "Wait — before you go" popup to save to Supabase + trigger n8n webhook
- Currently just saves to Supabase, doesn't send email

### 5. Custom domains on Railway
- checkout.syntharra.com → syntharra-checkout service
- auth.syntharra.com → syntharra-oauth-server service
- Both need: Railway custom domain setup + Squarespace CNAME record (prefix only, not full hostname)

---

## REMINDERS

- **DO NOT change emails to support@syntharra.com yet** — Dan wants a few sales first
- **Stripe is in TEST MODE** — all products/prices/coupons need recreating in live mode before launch
- **Telnyx SMS** — waiting on AI evaluation approval, wired but SMS_ENABLED=false
- **Retell components** — specs built (10 components), can only be created in Retell dashboard UI (no API). Build when ready for next industry vertical.
- **VSL video** — package uploaded but no work done. Second lead nurture email has commented-out video link ready to uncomment.

---

## KEY IDS (quick reference)

- HVAC Standard agent: agent_4afbfdb3fcb1ba9569353af28d
- Conversation flow: conversation_flow_34d169608460
- Demo Jake: agent_b9d169e5290c609a8734e0bb45
- Demo Sophie: agent_2723c07c83f65c71afd06e1d50
- Supabase: hgheyqwnrcvwtgngqdnq.supabase.co
- n8n: syntharra.app.n8n.cloud
- Jotform Standard: 260795139953066
- Jotform Premium: 260819259556671
