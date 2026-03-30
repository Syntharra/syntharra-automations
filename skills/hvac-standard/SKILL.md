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

**NEVER use old agent ID `d180e1bd` — deleted. Always use `agent_4afbfdb3fcb1ba9569353af28d`.**

### Conversation Flow Nodes (12 total)
`greeting` → `identify_call` → `nonemergency_leadcapture` → `verify_emergency` → `callback` → `existing_customer` → `general_questions` → `spam_robocall` → `Transfer Call` → `transfer_failed` → `Ending` → `End Call`

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

To record a demo call as the Arctic Breeze agent:
- Call: `+1 (812) 994-4371`
- Persona: "Mike Henderson"
- This is used for VSL Scene 3

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

---

## 🔑 Credential Access — Supabase Vault

**NEVER store API keys in skill files, project memory, or anywhere else.**

All Syntharra credentials are stored in the `syntharra_vault` table in Supabase.

**To retrieve a key:**
1. Query `https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&select=key_value`
2. Use the **service role key** from Supabase Project Settings → API
3. Filter by `service_name` to get the `key_value`

```python
import requests

SB_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
# Get service role key from Supabase Project Settings → API

def get_key(service_name, sb_service_role_key):
    r = requests.get(
        f"{SB_URL}/rest/v1/syntharra_vault",
        params={"service_name": f"eq.{service_name}", "select": "key_value"},
        headers={
            "apikey": sb_service_role_key,
            "Authorization": f"Bearer {sb_service_role_key}"
        }
    )
    return r.json()[0]["key_value"]

# Example:
# retell_key = get_key("retell")
# n8n_key    = get_key("n8n_railway")
# github_token = get_key("github")
```

**Known service_name values** (populate before use):
- `retell` — Retell AI API key
- `n8n_railway` — Railway n8n API key
- `github` — GitHub personal access token
- `jotform` — Jotform API key
- `smtp2go` — SMTP2GO API key
- `railway` — Railway GraphQL API token
- `stripe_webhook_secret` — Stripe webhook signing secret
- `supabase_service_role` — Supabase service role key (for non-vault queries)
- `telnyx` — Telnyx API key (when active)
