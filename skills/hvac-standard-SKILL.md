---
name: hvac-standard
description: >
  Complete reference for the Syntharra HVAC Standard pipeline — the first and primary live product.
  ALWAYS load this skill when: debugging the HVAC Standard onboarding flow, working on the Standard
  call processor, editing the Arctic Breeze demo agent, troubleshooting Jotform Standard submissions,
  checking Standard client records in Supabase, working on n8n Standard workflows, editing Retell
  agent prompts or conversation flows for Standard tier, handling Standard client calls or call logs,
  or doing anything related to the Standard plan ($497/mo or $414/mo annual).
---

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

# HVAC Standard Pipeline — Full Reference

---

## Retell Agent

| Item | Value |
|---|---|
| Agent Name | Arctic Breeze HVAC |
| Agent ID | `agent_4afbfdb3fcb1ba9569353af28d` |
| Phone Number | `+1 (812) 994-4371` |
| Transfer Number | `+1 (856) 363-0633` |
| Conversation Flow | `conversation_flow_34d169608460` |
| Retell API Key | `{{RETELL_API_KEY}}` |



### Demo Agents (must always stay published)
| Name | Agent ID |
|---|---|
| Jake | `agent_b9d169e5290c609a8734e0bb45` |
| Sophie | `agent_2723c07c83f65c71afd06e1d50` |

---

## Critical Retell Rules

- **NEVER delete or recreate a Retell agent** — agent_id is the foreign key tying Retell, Supabase, call processor, and phone number together. Always patch in place.
- **Always publish after any agent update**: `POST https://api.retellai.com/publish-agent/{agent_id}` with `Authorization: Bearer {{RETELL_API_KEY}}` (returns 200 empty body)
- If a new agent is ever created: immediately update Supabase `agent_id`, phone assignment, and n8n in same operation
- Demo agents must always stay published
- **Use commas not dashes** in agent prompts for better AI readability

### Prompt Architecture
- Master base prompt + company info block + call type nodes
- Dynamic variables: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- Call types: service/repair, install/quote, existing customer, FAQ, emergency, live transfer

---

## n8n Workflows

| Workflow | ID |
|---|---|
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` |

- n8n instance: `https://n8n.syntharra.com`
- Railway n8n API key: `{{N8N_API_KEY — query syntharra_vault}}`
- **Always click Publish after any workflow edits**
- n8n PUT payload: only `name`, `nodes`, `connections`, `settings` (only `executionOrder` from settings) — extra fields cause 400 errors
- All email nodes use SMTP2GO credential: `"SMTP2GO - Syntharra"`

### Email Routing (Standard)

| Notification Type | To |
|---|---|
| Internal onboarding notifications | `onboarding@syntharra.com` |
| Internal call processor notifications | `admin@syntharra.com` |
| Customer-facing contact reference | `support@syntharra.com` |

---

## Jotform — Standard Onboarding

| Item | Value |
|---|---|
| Form ID | `260795139953066` |
| Webhook URL | `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding` |
| API Key | `{{JOTFORM_API_KEY — query syntharra_vault}}` (account: Blackmore_Daniel) |

**Use REST API directly** — do NOT use MCP OAuth connector (broken).

---

## Supabase

| Item | Value |
|---|---|
| URL | `hgheyqwnrcvwtgngqdnq.supabase.co` |
| Primary table | `hvac_standard_agent` |
| Call log table | `hvac_call_log` |

### `hvac_standard_agent` key fields
`agent_id`, `company_name`, `notification_email`, `notification_email_2`, `notification_email_3`, `notification_sms_2`, `notification_sms_3`

### `hvac_call_log` key fields
`call_tier`, `job_type`, `vulnerable_occupant`, `caller_sentiment`, `geocode_status`, `geocode_formatted`, `caller_address`, `notes`

---

## Standard Plan Pricing

| Billing | Price | Setup Fee | Minutes |
|---|---|---|---|
| Monthly | $497/mo | $1,499 | 475 min/mo |
| Annual | $414/mo | $1,499 | 475 min/mo |

---

## Stripe (TEST MODE)

| Item | Value |
|---|---|
| Standard product | `prod_UC0hZtntx3VEg2` |
| Monthly price | `price_1TDckaECS71NQsk8DdNsWy1o` |
| Annual price | `price_1TDckiECS71NQsk8fqDio8pw` |
| Setup fee price | `price_1TEKKrECS71NQsk8Mw3Z8CoC` |
| Founding discount | `FOUNDING-STANDARD` → `gzp8vnD7` ($1,499 off once) |
| Closer $250 off | `CLOSER-250` → `mGTTQZOw` |
| Closer $500 off | `CLOSER-500` → `GJiRoaMY` |
| Closer $750 off | `CLOSER-750` → `fUzLNIgz` |
| Closer $1000 off | `CLOSER-1000` → `3wraC3tQ` |

---

## Stripe Workflow (Shared — also affects Standard)

| Item | Value |
|---|---|
| Workflow ID | `ydzfhitWiF5wNzEy` |
| Trigger | `checkout.session.completed` |
| Flow | Extract Session → Save to Supabase → Send Welcome Email → Internal Notification |
| Webhook URL | `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` |
| Webhook signing secret | `{{STRIPE_WEBHOOK_SECRET}}` |

---

## Email Flow (Standard Clients — 3 emails)

1. Stripe welcome email (automated via Stripe → n8n)
2. "You're Live" email + PDF (sent after agent is provisioned)
3. Weekly report (ongoing)

---

## Shared n8n Workflows (affect Standard)

| Workflow | ID |
|---|---|
| Stripe Workflow | `ydzfhitWiF5wNzEy` |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` |
| Minutes Calculator | `9SuchBjqhFmLbH8o` |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` |
| Publish Retell Agent | `sBFhshlsz31L6FV8` |
| Nightly GitHub Backup | `EAHgqAfQoCDumvPU` |

---

## SMS

- SMS wired but disabled: `SMS_ENABLED=false`
- Preferred provider: Telnyx (awaiting AI evaluation approval — account active, $5 loaded, identity verified)
- Backup: Plivo. **Never Twilio.**

---

## Demo Call Instructions

Arctic Breeze is the **test agent only** — used for demos and VSL recording, not a real client.
- Call: `+1 (812) 994-4371`
- Persona: "Mike Henderson"
- Used for VSL Scene 3

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

> After Jotform Standard onboarding completes and the agent goes live, the workflow updates the client contact and creates a deal at **Active** stage in HubSpot automatically.
