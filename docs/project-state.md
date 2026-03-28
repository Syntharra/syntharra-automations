# Syntharra — Project State Reference

> Auto-generated reference doc. Last updated: 2026-03-28.
> Contains operational config, IDs, and architecture notes for fast session handoff.

---

## Brand

| Item | Value |
|---|---|
| Primary colour | `#6C63FF` (violet) |
| Accent colour | `#00D4FF` (cyan) |
| Fonts | DM Serif Display + DM Sans |
| Logo | 4 ascending signal bars (violet) + "Syntharra" wordmark |
| Contact | support@syntharra.com \| www.syntharra.com |

Logo variants in `brand-assets/`:
- Default: bars purple, "Syntharra" purple, "AI SOLUTIONS" black
- Swapped v2: bars purple, "Syntharra" black, "AI SOLUTIONS" purple

---

## Email Architecture

| Address | Purpose | Used In |
|---|---|---|
| `support@syntharra.com` | Customer-facing support, general contact | Website footer (all pages), FAQ answers, usage alerts, billing emails, legal pages |
| `feedback@syntharra.com` | Customer feedback channel | Website footer (all pages) |
| `careers@syntharra.com` | Job applications | Careers page |
| `admin@syntharra.com` | Internal admin, contract notices | Service agreement, call processor notifications, scenario test reports |
| `onboarding@syntharra.com` | Onboarding notifications (internal) | Stripe Workflow, HVAC Standard Onboarding, HVAC Premium Onboarding |
| `noreply@syntharra.com` | Sender address for automated emails | All SMTP2GO outbound emails |
| `daniel@syntharra.com` | Founder personal email | NOT used in any workflows or customer-facing content |

### n8n Workflow Email Mapping

| Workflow | Internal Notifications To | Customer-Facing Contact |
|---|---|---|
| HVAC Std Onboarding (`k0KeQxWb3j3BbQEk`) | `onboarding@` | `support@` |
| HVAC Prem Onboarding (`KXDSMVKSf59tAtal`) | `onboarding@` | `support@` |
| Stripe Workflow (`ydzfhitWiF5wNzEy`) | `onboarding@` | `support@` |
| HVAC Std Call Processor (`OyDCyiOjG0twguXq`) | `admin@` | — |
| HVAC Prem Call Processor (`UhxfrDaEeYUk4jAD`) | `admin@` | `support@` |
| Scenario Test Runner (`94QmMVGdEDl2S9MF`) | `admin@` | — |
| Usage Alert Monitor (`lQsYJWQeP5YPikam`) | `admin@` | `support@` |
| Monthly Minutes Calculator (`9SuchBjqhFmLbH8o`) | — | `support@` |

### Website Email Placement

- **Every page footer:** Contact (`support@`) + Feedback (`feedback@`)
- **Careers page:** `careers@syntharra.com`
- **Service agreement:** `admin@syntharra.com` (contract cancellation notices)
- **Legal pages footer (privacy, terms, security, service-agreement):** Contact + Feedback links

### Rules
- `daniel@syntharra.com` should NEVER appear in any workflow node logic, email body, or website content
- All customer-facing "contact us" references → `support@syntharra.com`
- All internal operational notifications → `admin@syntharra.com` or `onboarding@syntharra.com` depending on context
- All automated email sender address → `noreply@syntharra.com`

---

## Infrastructure Overview

| Platform | Purpose |
|---|---|
| Retell AI | AI phone agent builder |
| n8n (syntharra.app.n8n.cloud) | Automation / workflow orchestration |
| Supabase | Database (hgheyqwnrcvwtgngqdnq.supabase.co) |
| Jotform | Client onboarding forms |
| Stripe | Payments (currently TEST MODE) |
| Railway | Hosts Node.js checkout server |
| Amazon SES | Transactional email — noreply@syntharra.com (migration in progress) |
| SMTP2GO | Current email provider across all n8n workflows |
| Telnyx | SMS (pending AI evaluation approval — account created, $5 loaded) |
| GitHub Pages | syntharra.com website |

---

## Retell Agents

| Agent | ID |
|---|---|
| Arctic Breeze HVAC (live) | `agent_4afbfdb3fcb1ba9569353af28d` |
| Demo — Jake | `agent_b9d169e5290c609a8734e0bb45` |
| Demo — Sophie | `agent_2723c07c83f65c71afd06e1d50` |

- Arctic Breeze phone: `+18129944371` | Transfer: `+18563630633`
- Live flow: `conversation_flow_34d169608460`
- **Never delete or recreate a Retell agent** — agent_id is foreign key across Retell, Supabase, call processor, and phone number
- **Always publish after any agent update**: `POST https://api.retellai.com/publish-agent/{agent_id}` (Bearer auth)
- Demo agents must always stay published

---

## n8n Workflows

| Workflow | ID |
|---|---|
| HVAC Std Onboarding | `k0KeQxWb3j3BbQEk` |
| HVAC Std Call Processor | `OyDCyiOjG0twguXq` |
| HVAC Prem Onboarding | `KXDSMVKSf59tAtal` |
| HVAC Prem Call Processor | `UhxfrDaEeYUk4jAD` |
| HVAC Prem Dispatcher | `kVKyPQO7cXKUJFbW` |
| Stripe | `ydzfhitWiF5wNzEy` |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` |
| Minutes Calculator | `9SuchBjqhFmLbH8o` |
| Usage Alert | `lQsYJWQeP5YPikam` |
| Publish Retell | `sBFhshlsz31L6FV8` |
| Scenario Runner v4 | `94QmMVGdEDl2S9MF` |
| Transcript Generator | `dHO8O0QHBZJyzytn` |
| Integration Hub (inactive) | `8WYFy093XA6UKB7L` |
| Nightly Backup | `EAHgqAfQoCDumvPU` |
| Send Welcome Email (manual backup) | `Rd5HiN7v2SRwNmiY` |

- Minutes Calculator + Usage Alert have `availableInMCP: false` — enable before editing via MCP
- Always click **Publish** after any workflow edits
- SMTP2GO key: `api-0BE30DA64A074BC79F28BE6AEDC9DB9E`

---

## Supabase Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Client config, notification emails/SMS |
| `hvac_call_log` | Call records (call_tier, job_type, vulnerable_occupant, caller_sentiment, geocode fields, notes) |
| `stripe_payment_data` | Checkout session data |
| `client_subscriptions` | Active subscription tracking |
| `billing_cycles` | Billing cycle records |
| `overage_charges` | Usage overage tracking |
| `website_leads` | Website demo leads (written via anon key, no webhook) |

---

## Stripe (TEST MODE)

### Price IDs

| Plan | Price ID |
|---|---|
| Standard Monthly | `price_1TDckaECS71NQsk8DdNsWy1o` |
| Standard Annual | `price_1TDckiECS71NQsk8fqDio8pw` |
| Standard Setup ($1,499) | `price_1TEKKrECS71NQsk8Mw3Z8CoC` |
| Premium Monthly | `price_1TDclGECS71NQsk8OoLoMV0q` |
| Premium Annual | `price_1TDclPECS71NQsk8S9bAPGoJ` |
| Premium Setup ($2,499) | `price_1TEKKvECS71NQsk8vWGjHLUP` |

Products: Standard `prod_UC0hZtntx3VEg2` | Premium `prod_UC0mYC90fSItcq`

### Coupons (TEST MODE — recreate in live mode, same names)

| Code | ID | Discount |
|---|---|---|
| FOUNDING-STANDARD | `gzp8vnD7` | $1,499 off (once) |
| FOUNDING-PREMIUM | `RsOnUuo4` | $2,499 off (once) |
| CLOSER-250 | `mGTTQZOw` | $250 off (once) |
| CLOSER-500 | `GJiRoaMY` | $500 off (once) |
| CLOSER-750 | `fUzLNIgz` | $750 off (once) |
| CLOSER-1000 | `3wraC3tQ` | $1,000 off (once) |

### Webhook
- URL: `https://syntharra.app.n8n.cloud/webhook/syntharra-stripe-webhook`
- Event: `checkout.session.completed`
- ID: `we_1TEJXzECS71NQsk8eOMIs8JE`
- Signing secret: `whsec_D7eMVF0vdm2KRrVkZLzrhTihYeMbloQO`

### Branded Invoices (COMPLETED ✅)
- Stripe Dashboard branding set: logo, `#6C63FF`, `#00D4FF`
- Automatic email receipts enabled (successful payments + renewals)
- Invoice footer added
- `invoice_creation` block live in `server.js` (commit `fcec7af92232`)

---

## Checkout Server (syntharra-checkout repo)

- URL: `https://syntharra-checkout-production.up.railway.app`
- Stack: Node.js / Express, deployed on Railway
- Key env vars: `STRIPE_SECRET_KEY`, `RETELL_API_KEY`, `SITE_URL`
- `allow_promotion_codes: true` in server.js
- `invoice_creation` block added — every checkout generates branded invoice PDF

---

## Jotform Forms

| Form | ID |
|---|---|
| Standard Onboarding | `260795139953066` |
| Standard Onboarding v2 | `260812373840657` |
| Premium Onboarding | `260819259556671` |

- Standard onboarding webhook: `https://syntharra.app.n8n.cloud/webhook/jotform-hvac-onboarding`
- Use REST API directly with API key — do NOT use MCP OAuth connector (broken)

---

## GitHub Repos

| Repo | Purpose |
|---|---|
| `Syntharra/syntharra-automations` | All operational code: prompts, flows, n8n workflows, docs |
| `Syntharra/syntharra-checkout` | Pricing page + Stripe checkout only (Railway) |
| `Syntharra/syntharra-website` | index.html, demo.html, terms/privacy/security.html, favicon.svg |
| `Syntharra/syntharra-oauth-server` | Premium OAuth server |

- **Do NOT merge syntharra-checkout into syntharra-automations**
- Push after every session with changes

---

## Website CSS Rules

- Never use `overflow:hidden` on `html`/`body` — use `overflow-x:clip`
- Use `100dvh` for video sections
- Video background filter: `contrast(1.2) brightness(0.85) saturate(1.3) sepia(0.25) hue-rotate(-15deg)`
- Dark panel overlay: `linear-gradient(to bottom, rgba(0,0,0,0) 35%, rgba(4,4,14,0.97) 100%)`
- `preview.html` is a temporary design tool only

---

## Pre-Launch Checklist

- [ ] Complete Amazon SES DNS verification (DKIM CNAME — use prefix only, Squarespace auto-appends domain)
- [ ] Migrate all n8n email nodes from SMTP2GO to `noreply@syntharra.com` via SES
- [ ] Switch Stripe to live mode: recreate all products, prices, coupons (same names), webhook
- [ ] Update Railway `STRIPE_SECRET_KEY` → `sk_live_...`
- [ ] Update n8n webhook signing secret to live mode value
- [x] ~~Change all internal notification emails from `daniel@syntharra.com`~~ — **DONE 2026-03-28**: migrated to `admin@`, `onboarding@`, and `support@` across all workflows + website
- [ ] Telnyx SMS swap (replace Twilio nodes — awaiting AI evaluation approval)
- [ ] Enable repeat caller detection
- [ ] Build Premium pipeline

---

## Key API Keys

> Actual keys are stored in Claude project memory, Railway env vars, and n8n credentials — not committed to GitHub.

| Service | Location |
|---|---|
| n8n API key | Claude memory |
| Retell API key | Claude memory + Railway env |
| GitHub Token | Claude memory |
| Jotform API key | Claude memory |
| SMTP2GO key | n8n credentials store |
| Stripe secret key | Railway env `STRIPE_SECRET_KEY` |
| Supabase service role key | n8n credentials store |
