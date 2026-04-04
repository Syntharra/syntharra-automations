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
**CRITICAL — Correct API endpoint to list all org repos:**
```
GET https://api.github.com/user/repos?affiliation=owner,organization_member&per_page=100
```
NOT `/orgs/{org}/repos` — that returns 404 for org-type accounts with personal tokens.
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
| Ops Monitor | `7ce0f943-5216-4a16-8aeb-794cc7cc1e65` | syntharra-ops-monitor-production.up.railway.app — ACTIVE |
| OAuth Server | separate Railway service | |

**Railway production environment ID (all services):** `5303bcf8-43a4-4a95-8e0c-75909094e02e`

### Critical Railway Rules
- Railway **blocks all SMTP ports** (25, 465, 587, 2525) — always use SMTP2GO REST API (HTTPS 443), never nodemailer
- Railway does NOT always auto-deploy on GitHub push — trigger via API mutation if needed:
  ```
  mutation { serviceInstanceRedeploy(serviceId: "...", environmentId: "...") }
  ```
- **Never POST to webhooks for health checks** — always use HEAD. POST triggers real workflow execution.
- **Set env vars via API** — use `variableUpsert` mutation, no dashboard needed:
  ```
  mutation {
    variableUpsert(input: {
      projectId: "bf04f61c-84d9-4c99-bd54-497d3f357070",
      environmentId: "5303bcf8-43a4-4a95-8e0c-75909094e02e",
      serviceId: "SERVICE_ID",
      name: "VAR_NAME",
      value: "VALUE"
    })
  }
  ```

### Railway GQL — deployments query (verified 2026-04-03)
**Correct syntax** — `input:` is the right arg (`where:`/`orderBy:` do NOT exist in schema):
```graphql
{
  deployments(
    first: 1,
    input: {
      serviceId: "SERVICE_ID",
      environmentId: "ENV_ID",
      status: { notIn: [REMOVED, REMOVING, SKIPPED] }
    }
  ) {
    edges { node { id status createdAt } }
  }
}
```
**Critical:** Railway returns deployments **oldest-first**. Without `status: { notIn: [...] }`, `first:1` returns the oldest REMOVED deployment, not the current one. Always filter out REMOVED/REMOVING/SKIPPED.

**Healthy deployment statuses:** `SUCCESS` + transient states `DEPLOYING, INITIALIZING, BUILDING, QUEUED, WAITING, NEEDS_APPROVAL`
**Alert-worthy statuses:** `FAILED`, `CRASHED`, or no deployments found at all.

**DeploymentStatus enum values:** BUILDING, CRASHED, DEPLOYING, FAILED, INITIALIZING, NEEDS_APPROVAL, QUEUED, REMOVED, REMOVING, SKIPPED, SLEEPING, SUCCESS, WAITING

---

## n8n (Self-Hosted on Railway)

| Item | Value |
|---|---|
| URL | `https://n8n.syntharra.com` |
| Railway n8n API key | `{{N8N_API_KEY}}` |
| Migration status | Complete ✅ — all 19 workflows imported, credentials re-entered, CNAME live |

### All n8n Workflows (verified live 2026-04-04 — 47 total, 37 labelled)

> Source of truth: live n8n instance. IDs below are current.
> n8n API key: `service_name='n8n Railway', key_type='api_key'` in syntharra_vault

#### HVAC Standard
| Workflow | ID | Active |
|---|---|---|
| HVAC AI Receptionist - JotForm Onboarding (Supabase) | `4Hx7aRdzMl5N0uJP` | ✅ |
| HVAC Call Processor - Retell Webhook (Supabase) | `Kg576YtPM9yEacKn` | ✅ |
| HVAC Weekly Lead Report (Supabase) | `iLPb6ByiytisqUJC` | ✅ |

#### HVAC Premium
| Workflow | ID | Active |
|---|---|---|
| HVAC Prem Onboarding | `kz1VmwNccunRMEaF` | ✅ |
| HVAC Premium Call Processor | `STQ4Gt3rH8ptlvMi` | ✅ |
| Premium Integration Dispatcher | `73Y0MHVBu05bIm5p` | ✅ |
| Premium Dispatcher — Outlook | `La99yvfmWg6AuvM2` | ✅ |
| Premium Dispatcher — Calendly | `b9xRG7wtqCZ5fdxo` | ✅ |
| Premium Dispatcher — Jobber | `BxnR17qUfAb5BZCz` | ✅ |
| Premium Dispatcher — HubSpot | `msEy13eRz66LPxW6` | ✅ |
| Premium Dispatcher — Google Calendar | `rGrnCr5mPFP2TIc7` | ✅ |
| Premium — Integration Connected Handler | `a0IAwwUJP4YgwgjG` | ✅ |
| Premium — Daily Token Refresh | `5vphecmEhxnwFz2X` | ✅ |
| Premium — Send You're Live Email | `ptDdy38HKt9DUOAV` | ✅ |

#### Billing
| Workflow | ID | Active |
|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | ✅ |
| Monthly Minutes Calculator & Overage Billing | `z1DNTjvTDAkExsX8` | ✅ |
| Usage Alert Monitor (80% & 100% Warnings) | `Wa3pHRMwSjbZHqMC` | ✅ |

#### Marketing & Leads
| Workflow | ID | Active |
|---|---|---|
| Website Lead → AI Readiness Score Email | `QY1ZFtPJFsU5h6wQ` | ✅ |
| Website Lead → Free Report Email | `hFU0ZeHae7EttCDK` | ✅ |
| Website Lead — HubSpot Contact (Index + Calculator + Quiz) | `I8a2N9bIZp9Qg1IN` | ✅ |
| Weekly Newsletter - Syntharra | `6LXpGffcWSvL6RxW` | ✅ |
| Newsletter Unsubscribe Webhook | `Eo8wwvZgeDm5gA9d` | ✅ |
| Affiliate Application — HubSpot Contact | `syGlWx8TlbYlPZU4` | ✅ |

#### Operations
| Workflow | ID | Active |
|---|---|---|
| Nightly GitHub Backup | `44WfbVmJ7Zihcwgs` | ✅ |
| Auto-Enable MCP on All Workflows | `AU8DD5r6i6SlYFnb` | ✅ |
| Jotform Webhook Backup Polling | `LF8ZSYyQbmjV4rN0` | ✅ |
| Publish Retell Agent | `13cOIXxvj83NfDqQ` | ✅ |
| Daily Ops Digest — 6am → #all-syntharra | `SiMn59qJOfrZZS81` | ✅ |
| Slack Setup — Internal Admin Form | `z8T9CKcUp7lLVoGQ` | ✅ |
| Weekly Client Health Score Calculator | `ALFSzzp3htAEjwkJ` | ✅ |
| Daily Transcript Analysis + Jailbreak Monitor | `ofoXmXwjW9WwGvL6` | ✅ |
| Nightly PII Retention Cleanup | `ngK02cSgGmvawCot` | ✅ |

#### Email & Comms
| Workflow | ID | Active |
|---|---|---|
| Email Intelligence — Inbox Scanner → Slack | `PavRLBVQQpWrKUYs` | ✅ |
| Send Welcome Email (Manual) | `lXqt5anbJgsAMP7O` | ✅ |
| Email Digest — Daily 6am GMT | `4aulrlX1v8AtWwvC` | ✅ |

#### Blog & Content
| Workflow | ID | Active |
|---|---|---|
| Blog Auto-Publisher | `j8hExewOREmRp3Oq` | ✅ |

#### Testing & QA
| Workflow | ID | Active |
|---|---|---|
| E2E Test Cleanup — 5 Min Delayed Delete | `URbQPNQP26OIdYMo` | ✅ |

#### Unlabelled / Inactive (leave duplicates for now — Dan 2026-04-04)
| Workflow | ID | Active |
|---|---|---|
| Google Keep → Groq → Slack To-Do List | `5wxgBfJL7QeNP2ab` | ✅ Tagged `Operations` |
| Keep → Slack TEST RUN | `NY6vhwLFmecAkxdH` | ⚫ |
| SYNTHARRA_TEST_RUNNER | `HeG3aJQBXyRPKSXA` | ⚫ |
| Premium — Integration Connected Handler (×3 duplicates) | `SziSvI1zl49cs3cQ`, `OXuB3WR23fg0MmEu`, `IS5eC0SEzIv76TPQ` | ⚫ |
| [TEST STUB] Retell Tool Dispatcher | `UKEoUeNqYvDDJv79` | ⚫ |
| Blog Auto-Publisher (duplicate) | `AZZguGm5ypF6e5m9` | ⚫ |
| Email Digest — Daily 6am GMT (×2 duplicates) | `TZ4p1UyzTrCJPdKA`, `S3vHBQopDiOssM7G` | ⚫ |

### n8n API Rules
- PUT workflow payload: only `name`, `nodes`, `connections`, `settings` (only `executionOrder` from settings)
- Extra fields (`id`, `createdAt`, `versionId`, etc.) cause 400 errors
- **Always click Publish after any workflow edits**
- All email nodes: SMTP2GO credential name `"SMTP2GO - Syntharra"`

### n8n Workflow Labelling — MANDATORY
> Full standard: `docs/STANDARDS.md`. Summary rules here for quick reference.

**Every workflow MUST have before session close:**
1. **Name** — pattern: `[Vertical] [Tier] — [Function]` e.g. `HVAC Standard — Call Processor`
2. **Tags** — minimum 2: one vertical/shared tag + one function tag + one status tag
3. **Description** — 1–2 sentences in plain English

**Apply tags via dedicated endpoint (verified 2026-04-04):**
```bash
# 1. Get tag IDs
curl https://n8n.syntharra.com/api/v1/tags -H "X-N8N-API-KEY: {{N8N_API_KEY}}"

# 2. Apply to workflow
curl -X PUT https://n8n.syntharra.com/api/v1/workflows/{ID}/tags \
  -H "X-N8N-API-KEY: {{N8N_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '[{"id": "TAG_ID_1"}, {"id": "TAG_ID_2"}]'
```

> ⚠️ `PATCH /workflows/{id}` = 405. `PUT /workflows/{id}` with tags in body = 400 read-only error.
> Only correct method: `PUT /workflows/{id}/tags` with tag ID array.

**Session close checklist line:** `Labels: all workflows labelled ✅`
**Current status:** 38/47 active workflows labelled ✅. 9 inactive duplicates left intentionally.

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

### Jotform Rate Limit Rules (learned 2026-04-03)
- Jotform free tier has a strict hourly API call limit — easy to exceed with inefficient monitors
- **Never use `/user` as a connectivity ping** — it wastes a rate-limit slot. Use the first form fetch as connectivity check instead
- **Never fetch form submissions more than once per run** — cache results in memory, reuse for all downstream checks
- **Ops monitor check interval: 30 minutes** (not 15) — stays well within rate limits
- **HTTP 429 = transient rate limit, not an outage** — alert as WARNING not CRITICAL, bail immediately, retry next scheduled cycle

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

## CRM — HubSpot (active since 2026-04-03)
> HubSpot replaced the admin dashboard as Syntharra's CRM layer.
> Load `skills/syntharra-hubspot-SKILL.md` for full API reference.

- **All client records, deals, and sales pipeline live in HubSpot**
- **All marketing leads flow into HubSpot** (website form → Lead stage)
- **All paying clients auto-create in HubSpot** (Stripe → Paid Client stage)
- **All onboarded clients auto-update in HubSpot** (Jotform → Active stage)
- **All call activity is logged in HubSpot** (Retell post-call → contact note)
- Supabase remains operational source of truth for Retell agent config + call logs
- HubSpot is the sales, marketing, and client relationship layer
- API key: `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- Pipeline: "Syntharra Sales" — Lead → Demo Booked → Paid Client → Active


### Jotform Rate Limiting — Key Facts
- Free tier: **1,000 API calls/day**, resets at **midnight UTC** (not rolling 24h)
- A burst of E2E test runs can exhaust the daily quota in one session
- When quota is exhausted, ALL subsequent calls return 429 until midnight UTC reset
- The 429 response has **no Retry-After header** — you must know the reset time
- Backup poller at 15min = 192 calls/day; at 60min = 48 calls/day — always use 60min
- **Graceful 429 handler pattern**: check `jotRes.responseCode === 429` and return `{ status: 'rate_limited', skipped: true }` — do NOT throw, just skip and let the next scheduled run retry
- Onboarding webhook workflow makes 0 Jotform API calls (Jotform calls n8n, not vice versa)
- Safe daily budget: 48 (poller) + ~50 (testing buffer) = well under 1,000

### n8n SDK — Known Forbidden Patterns
- `new WorkflowBuilder(...)` → INVALID. Use `workflow('id', 'name')` factory
- `new ScheduleTriggerNode(...)` → INVALID. Use `trigger({ type: '...', ... })` factory
- `new CodeNode(...)` → INVALID. Use `node({ type: 'n8n-nodes-base.code', ... })` factory
- `new` expressions of any kind are blocked by the SDK security layer
- Always call `validate_workflow` before `update_workflow` — saves failed push attempts

---

## Architecture Decisions

| Decision | Chose | Why | Revisit if |
|---|---|---|---|
| Hosting | Railway | n8n needs persistent filesystem — Vercel is stateless. Railway gives persistent services + Postgres + Redis in one platform | Railway pricing increases significantly |
| Email sending | SMTP2GO REST API | Railway blocks SMTP ports 25/465/587/2525 — SMTP2GO over HTTPS 443 is the only viable option | Move off Railway |
| Repo listing | `/user/repos?affiliation=owner,organization_member` | `/orgs/{org}/repos` returns 404 for org accounts with personal tokens | — |
| Ops monitor | Separate Railway service (syntharra-ops-monitor repo) | Decoupled from n8n — monitor survives n8n restarts; can alert on n8n being down | — |
| n8n deployment | Self-hosted on Railway | Workflow engine needs persistent state; Railway's persistent service model fits exactly | Hosted n8n pricing improves |
| Skills location | GitHub, fetched at session start | /mnt has no API — GitHub allows programmatic updates, always current next session | Claude.ai adds /mnt API |
| Context files | Small domain-specific files in docs/context/ | Single 12k-token project-state.md wasted context; each domain file is ~500 tokens, load only what's needed | Context file count exceeds 20 |


## n8n MCP + SDK Gotchas (learned 2026-04-03)

### MCP flag resets after SDK update
After any `update_workflow` via MCP SDK, the `availableInMCP` flag gets reset to false.
**Fix:** Always run workflow `AU8DD5r6i6SlYFnb` (Auto-Enable MCP) immediately after any SDK update.

### n8n REST API PUT — active field is read-only
When patching workflows via `PUT /api/v1/workflows/{id}`, do NOT include `active` in the payload.
Returns 400 with "request/body/active is read-only".
**Safe payload keys:** `name`, `nodes`, `connections`, `settings` only.

### .onFalse() only valid on IF nodes
The SDK `.onFalse()` chaining method only works on `n8n-nodes-base.if` nodes.
HTTP Request nodes with `onError: continueErrorOutput` use a different pattern:
```javascript
export default workflow('id', 'name')
  .add(httpRequestNode)
  .to(successHandler)
  .add(httpRequestNode)   // reference same node again
  .to(errorHandler);      // connects to error output
```

## Agentic Learning Tables — Real Schemas (verified 2026-04-03)

### transcript_analysis — REAL columns
`id, call_id, agent_id, company_name, analysis_date, confusion_loops, frustration_detected,`
`price_hallucination, premature_ending, security_flags (text[]), overall_score (int 1-100), analysis_notes (text), created_at`
❌ DO NOT use: quality_score, issue_category, learning_note, requires_prompt_fix, missed_lead, duration_seconds, job_type

### client_health_scores — REAL columns
`id, agent_id, company_name, week_start, call_volume_current, call_volume_previous,`
`call_volume_trend (int %), dashboard_logins, payment_status (text 'ok'), health_score, calculated_at`
❌ DO NOT use: lead_count, lead_rate, success_rate, avg_lead_score, prompt_fix_count, frustration_rate, missed_lead_count
Upsert pattern: DELETE then INSERT (no ON CONFLICT configured)

### Slack vault key
service_name='Slack', key_type='webhook_url'


## n8n Workflow Update — MUST PUBLISH
- `n8n:update_workflow` saves a DRAFT only — does NOT auto-publish
- Production webhooks continue running the OLD activeVersion until you publish
- ALWAYS call `n8n:publish_workflow` immediately after `n8n:update_workflow`
- Verify: `versionId` must equal `activeVersionId` after publish
- Discovered 2026-04-04: Phase 6 test hit stale Groq code because draft wasn't published

## GOTCHA: n8n REST API PUT Strips Credential Bindings (2026-04-05)

`GET /api/v1/workflows/{id}` returns nodes WITHOUT credential bindings.
If you PUT those nodes back, all HTTP Request credentials are wiped → "Credentials not found."

**Safe pattern:**
1. `GET /api/v1/executions/{id}?includeData=true` from a SUCCESSFUL execution
2. Extract `workflowData.nodes` (these HAVE credential bindings)
3. Apply code changes to those nodes
4. PUT back with credentials preserved

**Unsafe pattern:** GET workflow → edit → PUT. Always loses credentials.
