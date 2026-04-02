---
name: syntharra-infrastructure
description: >
  Complete reference for all Syntharra infrastructure: Railway, n8n (self-hosted), GitHub repos,
  Stripe, Supabase, Telnyx, SMTP2GO, Retell, Jotform, and the ops monitor.
  ALWAYS load this skill when: managing Railway services, working on n8n migration or config,
  troubleshooting any backend service, handling Stripe live mode cutover, setting up environment
  variables, pushing GitHub changes, working with the ops monitor, managing deployments, checking
  service IDs, API tokens, webhook URLs, or any infrastructure-level task across Syntharra's stack.
---

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

---

## GitHub

| Repo | Purpose |
|---|---|
| `Syntharra/syntharra-automations` | All operational code: prompts, flows, n8n workflows, docs |
| `Syntharra/syntharra-checkout` | Pricing page + Stripe checkout (Railway) — NEVER merge into automations |
| `Syntharra/syntharra-website` | Website (GitHub Pages). `CLAUDE.md` at root = master handbook |
| `Syntharra/syntharra-oauth-server` | Premium OAuth server (Google Calendar, Jobber) |
| `Syntharra/syntharra-ops-monitor` | 24/7 monitoring (Railway service) |
| `Syntharra/syntharra-admin` | Admin tools |

**GitHub Token:** `{{GITHUB_TOKEN}}`
**Rule:** Always push to GitHub before chat ends. Never commit raw token strings — use placeholder variables before pushing.

---

## Railway

| Item | Value |
|---|---|
| GraphQL API | `https://backboard.railway.com/graphql/v2` |
| Token | `{{RAILWAY_TOKEN}}` |
| Project | Syntharra `bf04f61c-84d9-4c99-bd54-497d3f357070` |

### Services

| Service | ID | URL |
|---|---|---|
| n8n | `c40f1306-0544-4915-a304-f33fdb8d4385` | syntharra-n8n-production.up.railway.app |
| n8n Postgres | `97e13df6-6a68-435e-95db-47fd03c10fe3` | postgres:15 |
| n8n Redis | `9285c656-12b4-44f5-8338-9b569c5e42dc` | |
| Checkout | `e3df3e6d-6824-498f-bb4a-fdb6598f7638` | checkout.syntharra.com |
| Ops Monitor | `7ce0f943-5216-4a16-8aeb-794cc7cc1e65` | Currently PAUSED (stop test-mode alert spam) |
| OAuth Server | separate Railway service | |

**Railway env ID (checkout):** `5303bcf8-43a4-4a95-8e0c-75909094e02e`

### Critical Railway Rules
- Railway **blocks all SMTP ports** (25, 465, 587, 2525) — always use SMTP2GO REST API (HTTPS 443), never nodemailer
- Railway does NOT always auto-deploy on GitHub push — trigger via API mutation if needed:
  ```
  POST https://backboard.railway.com/graphql/v2
  mutation { serviceInstanceRedeploy(serviceId: "...", environmentId: "...") }
  ```
- **Never POST to webhooks for health checks** — always use HEAD. POST triggers real workflow execution.

---

## n8n (Self-Hosted on Railway)

| Item | Value |
|---|---|
| URL | `https://n8n.syntharra.com` |
| Railway n8n API key | `{{N8N_API_KEY}}` |
| Migration status | Complete ✅ — all 19 workflows imported, credentials re-entered, CNAME live |

### All n8n Workflows

#### Active
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
| Auto-Enable MCP | `AU8DD5r6i6SlYFnb` | Ops (runs every 6h) |
| E2E Cleanup | `URbQPNQP26OIdYMo` | Testing (webhook: /e2e-test-cleanup, 5-min delay) |

#### Inactive (confirm with Dan before deleting)
| Workflow | ID |
|---|---|
| Integration Hub | `8WYFy093XA6UKB7L` |

### n8n API Rules
- PUT workflow payload: only `name`, `nodes`, `connections`, `settings` (only `executionOrder` from settings)
- Extra fields (`id`, `createdAt`, `versionId`, etc.) cause 400 errors
- **Always click Publish after any workflow edits**
- All email nodes: SMTP2GO credential name `"SMTP2GO - Syntharra"`

### Webhook URLs
| Service | URL |
|---|---|
| Stripe | `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` |
| Jotform (Standard) | `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding` |

---

## Supabase

| Item | Value |
|---|---|
| URL | `hgheyqwnrcvwtgngqdnq.supabase.co` |
| Anon key | stored in n8n credentials |
| Service role key | stored in n8n credentials |

### Tables
| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Client config |
| `hvac_call_log` | Call records |
| `stripe_payment_data` | Checkout sessions |
| `client_subscriptions` | Active subscriptions |
| `billing_cycles` | Billing cycle records |
| `overage_charges` | Usage overages |
| `website_leads` | Website demo leads (anon key, no webhook) |

---

## Stripe (TEST MODE — not yet live)

| Item | Value |
|---|---|
| Mode | **TEST MODE** — all products/prices are test |
| Webhook URL | `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` |
| Webhook ID | `we_1TEJXzECS71NQsk8eOMIs8JE` |
| Webhook signing secret | `{{STRIPE_WEBHOOK_SECRET}}` |
| Event | `checkout.session.completed` |

### Products & Prices
| Plan | Product ID | Monthly Price | Annual Price | Setup Price |
|---|---|---|---|---|
| Standard | `prod_UC0hZtntx3VEg2` | `price_1TDckaECS71NQsk8DdNsWy1o` | `price_1TDckiECS71NQsk8fqDio8pw` | `price_1TEKKrECS71NQsk8Mw3Z8CoC` |
| Premium | `prod_UC0mYC90fSItcq` | `price_1TDclGECS71NQsk8OoLoMV0q` | `price_1TDclPECS71NQsk8S9bAPGoJ` | `price_1TEKKvECS71NQsk8vWGjHLUP` |

### Discount Codes (TEST MODE — recreate in live, same names)
| Code | ID | Discount |
|---|---|---|
| FOUNDING-STANDARD | `gzp8vnD7` | $1,499 off once |
| FOUNDING-PREMIUM | `RsOnUuo4` | $2,499 off once |
| CLOSER-250 | `mGTTQZOw` | $250 off once |
| CLOSER-500 | `GJiRoaMY` | $500 off once |
| CLOSER-750 | `fUzLNIgz` | $750 off once |
| CLOSER-1000 | `3wraC3tQ` | $1,000 off once |

### Stripe Live Mode Cutover Checklist
- [ ] Activate Stripe account (complete identity verification)
- [ ] Switch to live mode
- [ ] Recreate all products, prices, coupons (same names — IDs will change)
- [ ] Recreate webhook in live mode → get new signing secret
- [ ] Update Railway env `STRIPE_SECRET_KEY` → `sk_live_...`
- [ ] Update n8n webhook signing secret to live value
- Branded invoices: complete ✅ (Dashboard branding, email receipts, invoice footer, `invoice_creation` in `server.js`)

---

## Retell AI

| Item | Value |
|---|---|
| API Key | `{{RETELL_API_KEY}}` |
| Publish endpoint | `POST https://api.retellai.com/publish-agent/{agent_id}` |
| Auth | `Authorization: Bearer {{RETELL_API_KEY}}` |

---

## Jotform

| Item | Value |
|---|---|
| API Key | `{{JOTFORM_API_KEY}}` |
| Account | Blackmore_Daniel |
| Standard Form | `260795139953066` |
| Premium Form | `260819259556671` |

**Use REST API directly** — MCP OAuth connector is broken.

---

## SMTP2GO

| Item | Value |
|---|---|
| API Key | `{{SMTP2GO_API_KEY}}` |
| n8n credential name | `"SMTP2GO - Syntharra"` |
| Sender address | `noreply@syntharra.com` |

Used for ALL n8n email nodes. On Railway, use SMTP2GO REST API (not SMTP/nodemailer — Railway blocks all SMTP ports).

---

## Telnyx

| Item | Value |
|---|---|
| Number | `+1-929-451-0009` (existing — VoIP, rejected by WhatsApp for Business) |
| Status | Account active, $5 loaded, identity verified |
| Blocker | Awaiting AI evaluation approval before buying toll-free number |
| Use | SMS notifications (preferred over Plivo — never Twilio) |

WhatsApp Business setup blocked — VoIP number rejected. Alternatives: personal Irish mobile or prepaid US SIM.

---

## Ops Monitor

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-ops-monitor` |
| URL | `syntharra-ops-monitor-production.up.railway.app` |
| Railway service ID | `7ce0f943-5216-4a16-8aeb-794cc7cc1e65` |
| Status | **PAUSED** (paused 2026-03-30 to stop test-mode alert spam) |
| Monitors | 10 systems, 70+ checks |
| Alert email | SMTP2GO REST API |
| Alert SMS | Telnyx |
| Daily digest | 8am CT |

To unpause: Railway GraphQL API `sleepApplication: false`, serviceId `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`

---

## Email System

| Address | Purpose |
|---|---|
| `noreply@syntharra.com` | All automated outbound (via SMTP2GO) |
| `support@syntharra.com` | Customer-facing support |
| `onboarding@syntharra.com` | Internal onboarding notifications |
| `admin@syntharra.com` | Internal ops notifications |
| `feedback@syntharra.com` | Customer feedback |
| `info@syntharra.com` | General public enquiries |
| `sales@syntharra.com` | Sales enquiries |
| `careers@syntharra.com` | Job applications |
| `daniel@syntharra.com` | **NEVER in workflows, website, or customer-facing content** |

Google Workspace footer (appended to all outgoing): `Syntharra | Global AI Solutions | www.syntharra.com | info@syntharra.com`

---

## Pre-Launch Checklist

- [ ] Stripe live mode cutover (full checklist above)
- [ ] Telnyx toll-free number (awaiting AI evaluation approval)
- [ ] Enable repeat caller detection
- [ ] Unpause ops monitor (after Stripe is live)
- [ ] Cancel n8n Cloud (confirm Railway n8n stable first)
- [ ] WhatsApp Business number (Irish mobile or prepaid SIM)
- [ ] Amazon SES DNS verification (for future email migration from SMTP2GO)

---

---

## 🔑 Syntharra Vault — Credential Access

ALL Syntharra API keys and secrets are stored in the Supabase table `syntharra_vault`.

- **Project URL:** `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- **Table:** `syntharra_vault`
- **Query by:** `service_name` + `key_type` fields → retrieve `key_value`
- **Auth:** Supabase service role key — stored in vault as `service_name = 'Supabase'`, `key_type = 'service_role_key'`
- **NEVER** store keys in skill files, session logs, GitHub, or project memory

### REST Lookup Pattern
```
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&key_type=eq.{KEY_TYPE}&select=key_value
Headers:
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
```

### JavaScript Lookup Pattern (n8n / Node.js)
```javascript
async function getVaultKey(serviceName, keyType) {
  const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.${serviceName}&key_type=eq.${keyType}&select=key_value`,
    { headers: { apikey: SERVICE_ROLE_KEY, Authorization: `Bearer ${SERVICE_ROLE_KEY}` } }
  );
  const data = await res.json();
  return data[0]?.key_value;
}

// Examples:
const retellKey    = await getVaultKey('Retell AI', 'api_key');
const n8nUrl       = await getVaultKey('n8n Railway', 'instance_url');
const stripeMonthly = await getVaultKey('Stripe', 'price_standard_monthly');
```

### Known service_name / key_type Values

| service_name | key_type | What it is |
|---|---|---|
| `n8n Railway` | `instance_url` | `https://n8n.syntharra.com` |
| `n8n Railway` | `api_key` | n8n Railway API key |
| `Retell AI` | `api_key` | Retell API key |
| `Retell AI` | `agent_id_arctic_breeze` | Test HVAC agent ID |
| `Retell AI` | `agent_id_demo_jake` | Demo agent Jake |
| `Retell AI` | `agent_id_demo_sophie` | Demo agent Sophie |
| `Retell AI` | `conversation_flow_id` | Live conversation flow |
| `Retell AI` | `phone_number` | Arctic Breeze phone |
| `Supabase` | `project_url` | Supabase project URL |
| `Supabase` | `service_role_key` | Full admin key |
| `GitHub` | `personal_access_token` | GitHub PAT |
| `Stripe` | `product_id_standard` | Standard product ID |
| `Stripe` | `product_id_premium` | Premium product ID |
| `Stripe` | `price_standard_monthly` | $497/mo price ID |
| `Stripe` | `price_standard_annual` | $414/mo price ID |
| `Stripe` | `price_standard_setup` | $1,499 setup price ID |
| `Stripe` | `price_premium_monthly` | $997/mo price ID |
| `Stripe` | `price_premium_annual` | $831/mo price ID |
| `Stripe` | `price_premium_setup` | $2,499 setup price ID |
| `Stripe` | `coupon_founding_standard` | FOUNDING-STANDARD coupon |
| `Stripe` | `coupon_founding_premium` | FOUNDING-PREMIUM coupon |
| `Stripe` | `webhook_url` | Stripe webhook URL |
| `Stripe` | `webhook_id` | Stripe webhook ID |
| `Jotform` | `api_key` | Jotform API key |
| `Jotform` | `form_id_standard` | Standard onboarding form ID |
| `Jotform` | `form_id_premium` | Premium onboarding form ID |
| `Jotform` | `webhook_standard_new` | Railway n8n webhook URL |
| `SMTP2GO` | `api_key` | SMTP2GO API key |
| `Railway` | `api_token` | Railway API token |
| `Railway` | `project_id` | Syntharra project ID |
| `Railway` | `service_id_n8n` | n8n service ID |
| `Railway` | `service_id_checkout` | Checkout service ID |
| `Railway` | `service_id_ops_monitor` | Ops monitor service ID |

---

## 🔄 Auto-Update Rule

**Whenever you complete any task that touches this skill's domain, you MUST update this SKILL.md before the chat ends.**

This includes:
- New n8n workflow created or renamed → update the workflow table
- New Supabase table or column added → update the tables section
- New Jotform field added → update field mappings
- API key or credential changed → update the keys section
- New Retell agent created → update agent IDs
- Stripe product/price/coupon added or changed → update Stripe section
- New Railway service created → update infrastructure section
- New website page created → update file map
- Any webhook URL changed → update webhook URLs
- Any new learnings or gotchas discovered → add to key rules/learnings

**How:** At end of chat, fetch this file from GitHub, apply changes with `str.replace()`, push back.
**GitHub push function:** See `syntharra-ops` skill for the standard push pattern.
