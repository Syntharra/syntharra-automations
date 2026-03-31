<!-- Last updated: 2026-03-30 -->
<!-- Session: Onboarding Pack build — see session log 2026-03-30-onboarding-pack.md -->

<!-- Last updated: 2026-03-30 (session 4) — Call processor Internal Notification rewired: now runs after Supabase log on every call, fires alert to alerts@syntharra.com only on 7 error conditions (SYSTEM_ERROR, CALL_STATUS_ERROR, TRANSFER_FAILED, TRANSFER_UNSUCCESSFUL, ABNORMAL_ENDING, CLIENT_NOT_FOUND, CALL_TOO_SHORT, GEOCODE_ERROR, GPT_ANALYSIS_FAILED). Silent on normal calls. Both STD + PREM updated and activated.
<!-- Last updated: 2026-03-30 (session 3) — alerts@syntharra.com added: Railway ALERT_EMAIL_TO updated, alertManager.js fallback updated, email skill + project-state updated. Signature file already existed from prior session.
<!-- Last updated: 2026-03-31 — Email Digest LIVE: workflow 4aulrlX1v8AtWwvC running (9 inboxes, Groq AI, Supabase). N8N_EDITOR_BASE_URL added to Railway. All 22 n8n workflows tagged by category. -->
# Syntharra — Project State (Master Reference)

> **This is the single source of truth for all Syntharra operational state.**
> Last updated: 2026-03-30 (session 2) — Ops monitor efficiency pass: zero-call alert paused (PRE_LAUNCH_MODE), email check switched to SMTP2GO public status API (0 emails/month), daily digest crash fixed (nodemailer → REST), pipeline agent check reads statusStore not Retell API, jotform orphan check bulk-fetches (40 queries → 2), SSL loop removed from infrastructure. Full go-live checklist stored in syntharra-ops SKILL.md.
>
> **RULE FOR ALL CLAUDE SESSIONS:**
> 1. READ this file + `syntharra-website/CLAUDE.md` at the start of every chat
> 2. UPDATE this file at the end of every chat that changes anything
> 3. Drop a session log in `docs/session-logs/` with what changed and why
> 4. Push all changes to GitHub before the chat ends

---

## Brand

| Item | Value |
|---|---|
| Primary colour | `#6C63FF` (violet) |
| Accent colour | `#00D4FF` (cyan) |
| Gradient | `linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%)` |
| Fonts (website) | Inter (Google Fonts) |
| Fonts (checkout) | DM Serif Display + DM Sans |
| Background | `#FAFAFA` |
| Surface/cards | `#FFFFFF` |
| Text primary | `#1A1A2E` |
| Text secondary | `#4A4A6A` |
| Text tertiary | `#8A8AA0` |
| Border | `#E5E7EB` |
| Logo | 4 ascending vertical bars, rounded corners, flat `#6C63FF` |
| Contact | support@syntharra.com \| www.syntharra.com |

### Logo variants (in `brand-assets/`)
- Default: bars purple, "Syntharra" purple, "AI SOLUTIONS" black
- Swapped v2: bars purple, "Syntharra" black, "AI SOLUTIONS" purple (`syntharra-logo-swapped-v2.png`)
- Favicon: `favicon.svg` (purple on transparent), `favicon-white.svg` (white on transparent)
- NEVER use emoji as substitute for logo anywhere

### Email templates
ALL Syntharra emails must be **LIGHT THEME**

### Approved email logo block (use in ALL email templates)
```
const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
```
Inject via: `<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>` — NEVER use flat PNG images for email logo.

ALL Syntharra emails must be **LIGHT THEME**: white (#fff) cards, grey (#F7F7FB) outer bg, dark text (#1A1A2E), purple (#6C63FF) accents. NEVER dark-theme emails — let client email apps handle dark mode. Applies to every n8n email template: welcome, reports, scores, onboarding, invoices.

### Email signature
Final versions in `brand-assets/email-signature/`:
- `syntharra-signature-PASTE-THIS.html` — Gmail + universal, purple circle white icon, inline base64 PNGs, border-top divider
- `syntharra-signature-outlook.html` — Outlook desktop
- Phone: +1 (000) 000-0000 placeholder

---

## Email Architecture

| Address | Purpose | Used In |
|---|---|---|
| `support@syntharra.com` | Customer-facing support, general contact | Website footer (all pages), FAQ answers, usage alerts, billing emails, legal pages |
| `feedback@syntharra.com` | Customer feedback channel | Website footer (all pages) |
| `careers@syntharra.com` | Job applications | Careers page |
| `admin@syntharra.com` | Internal admin, contract notices | Service agreement, call processor notifications, scenario test reports |
| `alerts@syntharra.com` | Ops & system alerts, internal monitoring notifications | Ops monitor (all tiers: warning/critical), Railway alerts, infrastructure notifications |
| `onboarding@syntharra.com` | Onboarding notifications (internal) | Stripe Workflow, HVAC Standard Onboarding, HVAC Premium Onboarding |
| `noreply@syntharra.com` | Sender address for automated emails | All SMTP2GO outbound emails |
| `info@syntharra.com` | General enquiries, public-facing contact | Google Workspace footer (appended to all outgoing emails) |
| `solutions@syntharra.com` | Solutions enquiries, client solutions contact | Available for solutions-related outreach |
| `sales@syntharra.com` | Sales enquiries, inbound sales contact | Available for sales-related outreach |
| `daniel@syntharra.com` | Founder personal email | **NEVER** in any workflows or customer-facing content |

### n8n Workflow Email Mapping

| Workflow | Internal Notifications To | Customer-Facing Contact |
|---|---|---|
| HVAC Std Onboarding (`k0KeQxWb3j3BbQEk`) | `onboarding@` | `support@` |
| HVAC Prem Onboarding (`KXDSMVKSf59tAtal`) | `onboarding@` | `support@` |
| Stripe Workflow (`ydzfhitWiF5wNzEy`) | `onboarding@` | `support@` |
| HVAC Std Call Processor (`Kg576YtPM9yEacKn`) | `alerts@` (errors only) | — |
| HVAC Prem Call Processor (`STQ4Gt3rH8ptlvMi`) | `alerts@` (errors only) | `support@` |
| Scenario Test Runner (`94QmMVGdEDl2S9MF`) | `admin@` | — |
| Usage Alert Monitor (`lQsYJWQeP5YPikam`) | `admin@` | `support@` |
| Monthly Minutes Calculator (`9SuchBjqhFmLbH8o`) | — | `support@` |

### Website Email Placement
- **Every page footer:** Contact (`support@`) + Feedback (`feedback@`)
- **Careers page:** `careers@syntharra.com`
- **Service agreement:** `admin@syntharra.com` (contract cancellation notices)
- **Legal pages footer (privacy, terms, security, service-agreement):** Contact + Feedback links

### Google Workspace Footer
All outgoing emails from @syntharra.com append this plain text footer:
```
Syntharra | Global AI Solutions | www.syntharra.com | info@syntharra.com
```

### Email Signatures
Branded HTML signatures for each alias, stored in `brand-assets/email-signature/`:
| File | Name | Subtitle |
|---|---|---|
| `syntharra-signature-PASTE-THIS.html` | Daniel Blackmore | Founder & CEO |
| `syntharra-signature-support.html` | Syntharra Support | Customer Support |
| `syntharra-signature-admin.html` | Syntharra Admin | Administration |
| `syntharra-signature-onboarding.html` | Syntharra Onboarding | Client Onboarding |
| `syntharra-signature-feedback.html` | Syntharra Feedback | Feedback & Enquiries |
| `syntharra-signature-careers.html` | Syntharra Careers | Careers & Opportunities |
| `syntharra-signature-info.html` | Syntharra Info | General Enquiries |

To apply: open HTML file in Chrome, Select All → Copy → paste into Gmail signature settings for that alias.

### Email Rules
- `daniel@syntharra.com` must NEVER appear in any workflow node logic, email body, or website content
- All customer-facing "contact us" references → `support@syntharra.com`
- All general public enquiries → `info@syntharra.com`
- All internal operational notifications → `admin@` or `onboarding@` depending on context
- All automated email sender address → `noreply@syntharra.com`

---

## Pricing

| Plan | Monthly | Annual (2 months free) | Setup Fee | Minutes |
|---|---|---|---|---|
| Standard | $497/mo | $414/mo | $1,499 | 475 min/mo |
| Premium | $997/mo | $831/mo | $2,499 | 1,000 min/mo |

Pricing page: `https://syntharra-checkout-production.up.railway.app`
Pricing is NOT public on the main website.

---

## Infrastructure Overview

| Platform | URL / Detail |
|---|---|
| Website | syntharra.com (GitHub Pages) |
| Checkout | syntharra-checkout-production.up.railway.app (Railway) |
| n8n | n8n.syntharra.com |
| Supabase | hgheyqwnrcvwtgngqdnq.supabase.co |
| Stripe | Currently **TEST MODE** |
| Jotform | Account: Blackmore_Daniel |
| Retell AI | AI phone agent builder |
| SMTP2GO | Current email provider across all n8n workflows |
| Telnyx | SMS (pending AI evaluation approval — account created, $5 loaded, identity verified) |
| Plivo | SMS backup option if Telnyx doesn't work out. NOT Twilio. |

---

## Retell Agents

| Agent | ID |
|---|---|
| Arctic Breeze HVAC (live) | `agent_4afbfdb3fcb1ba9569353af28d` |
| Demo — Jake | `agent_b9d169e5290c609a8734e0bb45` |
| Demo — Sophie | `agent_2723c07c83f65c71afd06e1d50` |

- Arctic Breeze phone: `+18129944371` | Transfer: `+18563630633`
- Live conversation flow: `conversation_flow_34d169608460`
- Flow has 12 nodes: greeting, identify_call, nonemergency_leadcapture, verify_emergency, callback, existing_customer, general_questions, spam_robocall, Transfer Call, transfer_failed, Ending, End Call

### Retell Critical Rules
- **NEVER delete or recreate a Retell agent** — agent_id is the foreign key tying Retell, Supabase, call processor, and phone number together. Always patch in place.
- If a new agent is ever created, immediately update Supabase agent_id, phone assignment, and n8n in the same operation
- **Always publish after any agent update**: `POST https://api.retellai.com/publish-agent/{agent_id}` with Bearer auth (returns 200 empty body)
- Demo agents must always stay published

### HVAC Prompt Architecture
- Master base prompt + company info block + call type nodes (service/repair, install/quote, existing customer, FAQ, emergency, live transfer)
- Dynamic variables: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- **Always use commas instead of dashes** in agent prompts for better AI readability

---

## n8n Workflows (Active)

| Workflow | ID | Type |
|---|---|---|
| HVAC Std Onboarding | `k0KeQxWb3j3BbQEk` | Standard |
| HVAC Std Call Processor | `OyDCyiOjG0twguXq` | Standard |
| HVAC Prem Onboarding | `KXDSMVKSf59tAtal` | Premium |
| HVAC Prem Call Processor | `UhxfrDaEeYUk4jAD` | Premium |
| HVAC Prem Dispatcher | `kVKyPQO7cXKUJFbW` | Premium |
| Stripe Workflow | `ydzfhitWiF5wNzEy` | Shared |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` | Shared |
| Minutes Calculator | `9SuchBjqhFmLbH8o` | Shared |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` | Shared |
| Publish Retell Agent | `sBFhshlsz31L6FV8` | Shared |
| Scenario Runner v4 | `94QmMVGdEDl2S9MF` | Testing |
| Scenario Transcript Gen | `dHO8O0QHBZJyzytn` | Testing |
| Scenario Process Single | `rlf1dHVcTlzUbPX7` | Testing |
| Website Lead → AI Score | `FBNjSmb3eLdBS3N9` | Lead Gen |
| Website Lead → Free Report | `ykaZkQXWO2zEJCdu` | Lead Gen |
| Nightly GitHub Backup | `EAHgqAfQoCDumvPU` | Ops |
| Send Welcome Email (manual) | `Rd5HiN7v2SRwNmiY` | Backup |
| Email Digest (daily 6am GMT) | `4aulrlX1v8AtWwvC` | Email & Comms |

### Inactive (confirm with Dan before deleting)
| Integration Hub | `8WYFy093XA6UKB7L` | Inactive |

### n8n Rules
- **Always click Publish after any workflow edits**
- SMTP2GO key: `[stored in Claude project memory]`
- n8n API update payload must include: `name`, `nodes`, `connections` (required). For `settings`, only include `executionOrder` — extra keys like `availableInMCP`, `callerPolicy`, `binaryMode` cause 400 errors.

### n8n Stripe Workflow Detail (`ydzfhitWiF5wNzEy`)
Trigger: `checkout.session.completed` → Extract Session Data (JS, builds emailHtml + dynamic Jotform URL) → Save to Supabase → Send Welcome Email → Send Internal Notification

### HVAC Premium Detail
- Onboarding `KXDSMVKSf59tAtal`: 13 nodes, 17 PCA, 4 tools
- Call Processor `UhxfrDaEeYUk4jAD`: 15 nodes, repeat caller detection
- Dispatcher `kVKyPQO7cXKUJFbW`: 4 nodes, Google Cal + Jobber
- SMS wired but disabled (`SMS_ENABLED=false`)
- OAuth server repo: `Syntharra/syntharra-oauth-server`

---

## Supabase Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Client config (includes notification_email_2/3, notification_sms_2/3) |
| `hvac_call_log` | Call records (call_tier, job_type, vulnerable_occupant, caller_sentiment, geocode_status, geocode_formatted, caller_address, notes) |
| `stripe_payment_data` | Checkout session data (stripe_customer_id, subscription_id, session_id, customer_email, customer_name, plan_name, plan_billing, plan_amount, minutes, setup_fee_price_id, payment_status, jotform_sent, signup_date) |
| `client_subscriptions` | Active subscription tracking |
| `billing_cycles` | Billing cycle records |
| `overage_charges` | Usage overage tracking |
| `website_leads` | Website demo leads (written via anon key, no webhook) |
| `syntharra_vault` | **All API keys and credentials** — query by `service_name`, retrieve `key_value` |

---

## Stripe (TEST MODE)

### Price IDs

| Plan | Price ID |
|---|---|
| Standard Monthly ($497) | `price_1TDckaECS71NQsk8DdNsWy1o` |
| Standard Annual ($414/mo) | `price_1TDckiECS71NQsk8fqDio8pw` |
| Standard Setup ($1,499) | `price_1TEKKrECS71NQsk8Mw3Z8CoC` |
| Premium Monthly ($997) | `price_1TDclGECS71NQsk8OoLoMV0q` |
| Premium Annual ($831/mo) | `price_1TDclPECS71NQsk8S9bAPGoJ` |
| Premium Setup ($2,499) | `price_1TEKKvECS71NQsk8vWGjHLUP` |

Products: Standard `prod_UC0hZtntx3VEg2` | Premium `prod_UC0mYC90fSItcq`

### Coupons (TEST MODE — recreate in live mode, same code names)

| Code | ID | Discount |
|---|---|---|
| FOUNDING-STANDARD | `gzp8vnD7` | $1,499 off (once) — waives full setup |
| FOUNDING-PREMIUM | `RsOnUuo4` | $2,499 off (once) — waives full setup |
| CLOSER-250 | `mGTTQZOw` | $250 off (once) |
| CLOSER-500 | `GJiRoaMY` | $500 off (once) |
| CLOSER-750 | `fUzLNIgz` | $750 off (once) |
| CLOSER-1000 | `3wraC3tQ` | $1,000 off (once) |

Discount codes doc: `docs/discount-codes.md`

### Webhook
- URL: `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook`
- Event: `checkout.session.completed`
- ID: `we_1TEJXzECS71NQsk8eOMIs8JE`
- Signing secret: `[stored in Claude project memory]`

### Branded Invoices (COMPLETED ✅)
- Dashboard branding: logo, `#6C63FF`, `#00D4FF`
- Automatic email receipts enabled (successful payments + renewals)
- Invoice footer added
- `invoice_creation` block live in `server.js` (commit `fcec7af92232`)

---

## Checkout Server

<<<<<<< HEAD
- URL: `https://checkout.syntharra.com`
=======
- URL: `https://syntharra-checkout-production.up.railway.app`
- Repo: `Syntharra/syntharra-checkout` — keep SEPARATE from syntharra-automations
>>>>>>> 16ad4d03ce075816a5a0310de414fad45e599417
- Stack: Node.js / Express, deployed on Railway
- Key env vars: `STRIPE_SECRET_KEY`, `RETELL_API_KEY`, `SITE_URL`
- `allow_promotion_codes: true` in server.js
- `invoice_creation` block live — every checkout generates branded invoice PDF

---

## Jotform Forms

| Form | ID |
|---|---|
| Standard Onboarding | `260795139953066` |
| Premium Onboarding | `260819259556671` |

- API key: `[stored in Claude project memory]` (account: Blackmore_Daniel)
- **Use REST API directly** — do NOT use MCP OAuth connector (broken)
- Standard onboarding webhook: `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding`

---

## GitHub Repos

| Repo | Purpose |
|---|---|
| `Syntharra/syntharra-automations` | All operational code: prompts, flows, n8n workflows, docs |
| `Syntharra/syntharra-checkout` | Pricing page + Stripe checkout only (Railway) |
| `Syntharra/syntharra-website` | Website (GitHub Pages). `CLAUDE.md` at root = master handbook |
| `Syntharra/syntharra-oauth-server` | Premium OAuth server |

- **Do NOT merge syntharra-checkout into syntharra-automations**
- **Push after every session with changes**
- GitHub token: `[stored in Claude project memory]`

### Website Edit Workflow
1. Fetch page from GitHub API (get SHA + content)
2. Edit using Python `str.replace()` — never shell curl for large files
3. Verify exactly ONE `<style>` block (`content.count('<style>') == 1`)
4. Push back via GitHub API (PUT with SHA)

### Website CSS Rules
- NEVER use `overflow:hidden` on html/body — use `overflow-x:clip`
- Use `100dvh` for video sections (not `100vh`)
- Video background filter: `contrast(1.2) brightness(0.85) saturate(1.3) sepia(0.25) hue-rotate(-15deg)`
- Dark panel overlay: `linear-gradient(to bottom, rgba(0,0,0,0) 35%, rgba(4,4,14,0.97) 100%)`
- Hamburger menu must be IDENTICAL on every page — copy from existing, never build from scratch
- When adding menu items, update ALL pages via script
- `preview.html` is a temporary design tool only

### Dashboard
- Live at `syntharra.com/dashboard.html?agent_id=X`

---

## Scaling Plan

- Use Retell API to auto-clone agents per client via n8n onboarding workflow triggered by Jotform
- Supabase stores client config
- Preferred n8n scaling path: Railway (self-hosted n8n on Railway Pro)
- Repo structure: `hvac-standard/`, `hvac-premium/`, `plumbing-standard/`, etc. with `shared/` folder

---

## Marketing (Planned, Not Yet Actioned)

- Automated lead sourcing: Google Places API → Supabase
- n8n cold email sequences with click tracking
- Branded video landing page
- Social content calendar with automated posting (TikTok, LinkedIn)
- Self-booking calendar link throughout
- VSL package exists (`Syntharra_VSL_Package.docx`) — script, video assets, outreach email

---

## API Keys Reference

> **ALL credentials are stored in `syntharra_vault` Supabase table.**
> Query by `service_name` → retrieve `key_value`. Use service role key from Supabase Project Settings → API.
> NEVER store keys in skill files, session logs, project memory, or anywhere else.

| Service | Storage Location |
|---|---|
| n8n API key | Claude project memory |
| Retell API key | Claude project memory + Railway env |
| GitHub Token | Claude project memory |
| Jotform API key | Claude project memory |
| SMTP2GO key | Claude project memory + n8n credentials store |
| Stripe secret key | Railway env `STRIPE_SECRET_KEY` |
| Stripe webhook signing secret | Claude project memory |
| Supabase URL | `hgheyqwnrcvwtgngqdnq.supabase.co` (not secret) |
| Supabase service role key | n8n credentials store |

---

## Pre-Launch Checklist

- [ ] Complete Amazon SES DNS verification (DKIM CNAME — use prefix only, Squarespace auto-appends domain)
- [ ] Migrate all n8n email nodes from SMTP2GO to `noreply@syntharra.com` via SES
- [ ] Switch Stripe to live mode: recreate all products, prices, coupons (same names), webhook
- [ ] Update Railway `STRIPE_SECRET_KEY` → `sk_live_...`
- [ ] Update n8n webhook signing secret to live mode value
- [x] ~~Email migration~~ — **DONE 2026-03-28**: `daniel@` removed from all workflows + website. Replaced with `admin@`, `onboarding@`, `support@`
- [ ] Telnyx SMS swap (awaiting AI evaluation approval)
- [ ] Enable repeat caller detection
- [ ] Build Premium pipeline


---


## Session: 2026-03-30 — Skill Library Built

### 9 Claude Skills Created
All skills live in `syntharra-automations/skills/`. Each skill contains:
- Full operational reference for that domain
- Canonical `syntharra_vault` access snippet (REST + JS patterns, full service_name/key_type table)
- Auto-update rule (update only on fundamental changes — new IDs, new tables, new credentials)

| Skill | Path | Domain |
|---|---|---|
| `syntharra-website` | `skills/syntharra-website/SKILL.md` | Website editing, brand, file map, email templates |
| `hvac-standard` | `skills/hvac-standard/SKILL.md` | Standard pipeline, onboarding, Jotform, Supabase, Stripe |
| `hvac-premium` | `skills/hvac-premium/SKILL.md` | Premium pipeline, OAuth, premium Supabase columns |
| `syntharra-infrastructure` | `skills/syntharra-infrastructure/SKILL.md` | Railway, n8n, all services and workflow IDs |
| `syntharra-marketing` | `skills/syntharra-marketing/SKILL.md` | Lead gen, VSL, demo page, blog, Google Ads |
| `syntharra-ops` | `skills/syntharra-ops/SKILL.md` | Session rules, GitHub push, ops monitor, signatures |
| `syntharra-retell` | `skills/syntharra-retell/SKILL.md` | Retell agents, prompts, flows, publishing, API |
| `syntharra-email` | `skills/syntharra-email/SKILL.md` | SMTP2GO, email templates, address routing, signatures |
| `syntharra-stripe` | `skills/syntharra-stripe/SKILL.md` | Products, prices, coupons, webhooks, live mode checklist |

### Key Rules Established
- Client agents are NOT listed in skills — query Supabase (`hvac_standard_agent.agent_id`)
- Arctic Breeze = test agent only, not a real client
- All credentials via `syntharra_vault` table only — never in skill files, GitHub, or memory
- Auto-update rule = fundamental changes only (new IDs, new tables, credentials) — not routine work

### syntharra_vault Table
Added to Supabase. Full service_name/key_type map documented in every skill.
Populate with all keys before first client onboarding.

## Latest Session: March 29, 2026

### Ops Monitor v2.0 — PAUSED (pre-launch)
- Deployed: syntharra-ops-monitor-production.up.railway.app
- GitHub: Syntharra/syntharra-ops-monitor
- Railway service ID: 7ce0f943-5216-4a16-8aeb-794cc7cc1e65
- **Status: PAUSED** — Railway service sleeping to prevent pre-launch alert spam
- 10 monitor systems, 70+ individual checks
- Monitors: Retell, n8n, Supabase, Stripe, Jotform, Pipeline (E2E), CRM/Calendar, Infrastructure, Client Health, Revenue
- SMS alerts via Telnyx (not Twilio), email via SMTP2GO, daily digest at 6am GMT (Europe/London)

**Pre-launch pauses applied (2026-03-30):**
- Zero-call business hours alert: `PRE_LAUNCH_MODE = true` in retell.js — SET TO false AT GO-LIVE
- Railway service itself sleeping — unpause at go-live via Railway GraphQL mutation

**Efficiency fixes applied (2026-03-30):**
- email.js: replaced test-email-send with SMTP2GO public status API (smtp2gostatus.com) — 0 emails/month vs 1,440
  - Root cause: sending-only API key has no stats endpoint permissions — status page is the correct approach
- alertManager.js: sendDailyDigest() rewritten to use SMTP2GO REST (was calling this.transporter.sendMail — nodemailer never initialised — daily digest was silently crashing every morning)
- pipeline.js: agent reachability check now reads from statusStore.get('retell') instead of re-calling Retell API per client every 15 min
- jotform.js: orphan detection now bulk-fetches all Supabase company/email names once, compares in memory — was firing up to 40 individual Supabase queries per run, now always 2
- infrastructure.js: removed redundant SSL loop — SSL health now inferred from HTTPS endpoint check results already collected (was making 3 duplicate HEAD requests every 5 min)

**Go-live checklist stored in:** syntharra-ops SKILL.md


## Session: 2026-03-29 — Ops Monitor Fixes & Dashboard Redesign

### Ops Monitor (syntharra-ops-monitor on Railway)

**SMTP / Email — Root Cause & Fix:**
- Railway blocks ALL outbound SMTP ports (25, 465, 587, 2525) — nodemailer will never work on Railway
- Fix: replaced nodemailer entirely with SMTP2GO REST API (HTTPS port 443)
- Files changed: `src/monitors/email.js`, `src/utils/alertManager.js`
- Railway env var added: `SMTP2GO_API_KEY = api-0BE30DA64A074BC79F28BE6AEDC9DB9E`
- Also removed: `SMTP_PORT` env var no longer relevant (REST API doesn't use it)
- alertManager.js now sends all alert emails via `POST https://api.smtp2go.com/v3/email/send`

**n8n Monitor Not Loading — Root Cause & Fix:**
- alertManager constructor was initialising nodemailer transport on startup
- When n8n monitor tried to fire an alert (about execution errors), nodemailer timed out on SMTP connect
- This crashed the entire checkN8n() call silently inside safeRun()
- Fix: removing nodemailer fixed the crash — n8n monitor now loads and stores results correctly

**HVAC Premium Onboarding — 25x Ghost Errors — Root Cause:**
- NOT a credential issue. The ops monitor infrastructure.js v2.0 was using POST (not HEAD) on all webhook URLs
- Every 5 min it POSTed `{}` to `jotform-hvac-premium-onboarding` webhook → triggered real workflow execution with empty body → failed at `Create Retell Conversation Flow` node with "Credentials not found" (a side effect of empty payload, not a real cred issue)
- Fix was already committed (Mar 29 20:38): infrastructure.js webhook checks changed to HEAD
- NEVER use POST to check webhook health — always HEAD. 404 response from HEAD = healthy (endpoint exists)
- Errors will age out of 2h monitoring window automatically (~23:30 UTC Mar 29)

**Dashboard Redesign:**
- Full redesign: KPI row (6 cards), better card hierarchy, section labels, live clock, countdown progress bar
- Password login screen added: dark branded gate, access code `syntharra2024`  
- Login screen branding: Georgia italic "Syntharra" wordmark + "GLOBAL AI SOLUTIONS" in violet Inter caps
- System cards reordered by priority: Clients → Pipeline → Retell → n8n → Supabase → Stripe → etc.

### Key Learnings

- **Railway blocks all SMTP ports** — any email sending from Railway must use an HTTP/REST API (SMTP2GO REST, SendGrid API, etc.). Never use nodemailer/SMTP on Railway.
- **Never POST to webhooks for health checks** — always HEAD. POST triggers real workflow execution.
- **alertManager crash pattern** — if alertManager.js throws during monitor execution, the entire monitor silently returns without updating statusStore (healthy stays null). Always check alertManager for SMTP/transport errors first when a monitor shows null.
- **Railway build cache** — env var changes don't always trigger redeploy. Sometimes need a new git commit to bust cache and force fresh build.
- **Duplicate const declarations** — careful with str_replace edits that prepend to existing method bodies; always verify full method contents before and after edits.

---

## Checkout Page (syntharra-checkout — Railway)

| Item | Value |
|---|---|
| URL | checkout.syntharra.com (custom domain via Railway + Fastly CDN) |
| Repo | `Syntharra/syntharra-checkout` |
| Served from | `public/index.html` (NOT root index.html — Railway serves `/public`) |
| Server | `server.js` — Express, `app.use(express.static('public'))` |
| Railway service ID | `e3df3e6d-6824-498f-bb4a-fdb6598f7638` |
| Railway environment ID | `5303bcf8-43a4-4a95-8e0c-75909094e02e` |

### Current state (as of 2026-03-30)
- **3 plans**: Standard, Premium (Most Popular), Enterprise/Custom Build
- **Enterprise card**: Frosted violet theme (`#F0F0FF` bg, `#C8C2FF` border, purple accents) — `mailto:sales@syntharra.com` CTA
- **Setup fee**: Redesigned as a clean pill row (Setup fee label | strikethrough | discounted price)
- **"Everything in Standard, plus"**: Replaced with a visual callout banner with icon
- **Divider alignment**: All 3 cards aligned via consistent structure — enterprise minutes pill has `margin-top:14px` nudge
- **Background**: Subtle dot-grid pattern on page body
- **Premium card**: Linear gradient (`#7B72FF → #5A52E0`) for depth
- **Logo**: Inline SVG (4 ascending bars, `#6C63FF`) matching syntharra.com exactly
- **Fonts**: DM Serif Display + DM Sans (Google Fonts)

### CRITICAL deployment note
Railway does NOT auto-deploy on GitHub push — must trigger manually via Railway API:
```
POST https://backboard.railway.com/graphql/v2
mutation { serviceInstanceRedeploy(serviceId: "e3df3e6d...", environmentId: "5303bcf8...") }
```
Or wait ~2-3 min for Railway to pick up the push automatically (inconsistent).


## n8n

| Item | Value |
|---|---|
| Cloud instance (OLD) | n8n.syntharra.com — still active, deactivate after testing |
| Railway instance (NEW) | https://syntharra-n8n-production.up.railway.app |
| Custom domain (TODO) | n8n.syntharra.com → CNAME to syntharra-n8n-production.up.railway.app |
| Railway service ID | c40f1306-0544-4915-a304-f33fdb8d4385 |
| Postgres service ID | 97e13df6-6a68-435e-95db-47fd03c10fe3 |
| Redis service ID | 9285c656-12b4-44f5-8338-9b569c5e42dc |
| Image | n8nio/n8n:latest (direct Docker image, no Dockerfile) |
| Workflows | 19 imported (all active on cloud, inactive on Railway until credentials re-entered) |

### Migration Status
- [x] Railway Pro plan active
- [x] n8n + Postgres + Redis services created
- [x] All env vars configured
- [x] n8n live and serving (200 OK)
- [x] All 19 workflows imported
- [x] Credentials re-entered in Railway n8n UI
- [x] CNAME set: n8n.syntharra.com (live, 200 OK)
- [x] Webhook URLs updated (Stripe ✓, Retell ✓, Jotform — manual required)
- [x] End-to-end tested (all systems green)
- [ ] n8n Cloud subscription cancelled (do after confirming stable)
- [ ] **Unpause syntharra-ops-monitor on Railway** (paused 2026-03-30 to stop test-mode alert spam — use sleepApplication: false via Railway GraphQL API, serviceId: 7ce0f943-5216-4a16-8aeb-794cc7cc1e65)

### Webhook URL Changes Required (after custom domain set up)
| Service | Old URL | New URL |
|---|---|---|
| Stripe | n8n.syntharra.com/webhook/syntharra-stripe-webhook | n8n.syntharra.com/webhook/syntharra-stripe-webhook |
| Jotform | n8n.syntharra.com/webhook/jotform-hvac-onboarding | n8n.syntharra.com/webhook/jotform-hvac-onboarding |
| Retell | Any n8n cloud webhook URLs | n8n.syntharra.com equivalents |



## Admin Dashboard (updated 2026-03-30)
- Live at `https://admin.syntharra.com` (Railway — Express server, basic auth)
- Custom domain: `admin.syntharra.com` configured in Railway
- Password: `admin` / `Syntharra2026!` (set via Railway env vars ADMIN_USER / ADMIN_PASS)
- Repo: `Syntharra/syntharra-admin` — service ID `6a542e9d-9dff-4968-b908-6077e12ba96b`
- Features: KPI cards, system status, live clock, trade/plan tabs, search bar, quick links
- Sections: Overview, Clients (Standard/Premium grouped + search + trade tabs), Call Logs, Billing, Form Submissions, AI Agents, Ops Monitor, System Health, Marketing Pipeline, Settings, AI Assistant
- AI Assistant: Groq-powered (llama-3.3-70b-versatile, free tier) — proxied via /api/ai on server.js
  - Full Syntharra knowledge base embedded in server.js system prompt
  - Live dashboard context (clients, calls, billing) injected per request
  - Activation: add GROQ_API_KEY to Railway env vars (get free key at console.groq.com)
  - Health endpoint: GET /api/health → returns {status, ai_configured, ts}
- All times display in Europe/London (GMT) timezone
- Wired to live Supabase data (anon key in frontend, no service role exposed)
- Jotform forms fetched live (Standard: 260795139953066, Premium: 260819259556671)
- Marketing pipeline from Supabase website_leads table
- Favicons: favicon.svg + favicon-white.svg served from /public/
- noindex/nofollow meta tag (prevents search engine indexing)
- Latest commit: fda12d38


## Blog Auto-Publisher (added 2026-03-31)
- n8n workflow ID: `j8hExewOREmRp3Oq` — ACTIVE
- Schedule: Mon/Wed/Fri 9AM (`0 9 * * 1,3,5`)
- Model: Groq `llama-3.3-70b-versatile` (free, existing key in vault)
- Supabase table: `blog_topics` — 41 topics queued, 1 published
- Workflow file: `syntharra-automations/blog/blog-auto-publisher.json`
- First article live: https://syntharra.com/blog/hvac-after-hours-answering.html
- To add more topics: INSERT into `blog_topics` with `status='queued'`
