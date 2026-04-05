---
name: hvac-premium
description: >
  Complete reference for the Syntharra HVAC Premium pipeline — the full-featured enterprise tier.
  ALWAYS load this skill when: working on HVAC Premium onboarding, the Premium call processor,
  the Premium dispatcher, Premium OAuth server, Premium client Supabase records, debugging
  Premium n8n workflows, setting up Google Calendar or Jobber integrations for Premium clients,
  or doing anything related to the Premium plan ($997/mo or $831/mo annual, 1,000 min/mo).
  Also trigger for any task involving multi-notification recipients, repeat caller detection,
  Premium email sequences, or the 4-step Premium onboarding email flow.
---

> **Last verified: 2026-04-05** — COMPONENTS architecture deployed, Premium E2E 106/106 passing, token usage optimized to ~2,670/turn.

# HVAC Premium Pipeline — Full Reference

---

## n8n Workflows

| Workflow | ID | Detail |
|---|---|---|
| HVAC Prem Onboarding | `kz1VmwNccunRMEaF` | Build code v2: COMPONENTS architecture, 20 nodes (15 conv + 2 transfer + 2 code + 1 end), 17 PCA |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | Retell-native — reads call_analysis.custom_analysis_data directly, no LLM calls |
| HVAC Prem Dispatcher | `73Y0MHVBu05bIm5p` | 4 nodes — Google Cal + Jobber |

- n8n instance: `https://n8n.syntharra.com`
- Railway n8n API key: `{{N8N_API_KEY — query syntharra_vault}}`
- **Always click Publish after any workflow edits**
- All email nodes use SMTP2GO credential: `"SMTP2GO - Syntharra"`

---

## Jotform — Premium Onboarding

| Item | Value |
|---|---|
| Form ID | `260819259556671` |
| API Key | `{{JOTFORM_API_KEY — query syntharra_vault}}` (account: Blackmore_Daniel) |

**Use REST API directly** — do NOT use MCP OAuth connector (broken).

---

## OAuth Server

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-oauth-server` |
| Purpose | Handles Google Calendar / Jobber OAuth for Premium clients |

---

## Supabase — Premium Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Client config (used by both Standard and Premium — includes notification_email_2/3, notification_sms_2/3) |
| `hvac_call_log` | All call records with Premium-specific fields |
| `client_subscriptions` | Active subscription tracking |
| `billing_cycles` | Billing cycle records |
| `overage_charges` | Usage overage tracking |

- Supabase URL: `hgheyqwnrcvwtgngqdnq.supabase.co`

### Premium-specific columns in `hvac_standard_agent` (both plans share one table)
- `crm_platform` — e.g. `"Jobber"`
- `crm_status` — `"pending"` → `"active"` after OAuth
- `calendar_platform` — e.g. `"Google Calendar"`
- `calendar_status` — `"pending"` → `"active"` after OAuth
- `booking_buffer_minutes` — int, default 30
- `default_appointment_duration` — int, default 60
- `booking_advance_days` — int, default 14
- `booking_confirmation_method` — `"email"` or `"sms"`
- `crm_access_token`, `crm_refresh_token`, `crm_token_expiry`
- `calendar_access_token`, `calendar_refresh_token`, `calendar_token_expiry`


---

## Premium Plan Pricing

| Billing | Price | Setup Fee | Minutes |
|---|---|---|---|
| Monthly | $997/mo | $2,499 | 1,000 min/mo |
| Annual | $831/mo | $2,499 | 1,000 min/mo |

Annual = 2 months free.

---

## Stripe (TEST MODE) — Premium

| Item | Value |
|---|---|
| Premium product | `prod_UC0mYC90fSItcq` |
| Monthly price | `price_1TDclGECS71NQsk8OoLoMV0q` |
| Annual price | `price_1TDclPECS71NQsk8S9bAPGoJ` |
| Setup fee price | `price_1TEKKvECS71NQsk8vWGjHLUP` |
| Founding discount | `FOUNDING-PREMIUM` → `RsOnUuo4` ($2,499 off once) |

---

## Call Processor — Architecture (Retell-native, post-enhancement 2026-04-04)

```
Retell POST (call_analyzed event)
  → Filter: call_analyzed only [IF node]
  → Extract Call Data [Code — reads call.call_analysis.custom_analysis_data]
  → Supabase: Lookup Client [HTTP — get company_name by agent_id]
  → Parse Client Data [Code]
  → Check Repeat Caller [Code — query hvac_call_log by from_number]
  → Is Lead? [IF — lead_score >= 5 AND not spam/wrong_number]
      ├─ Both → Supabase: Log Call [HTTP POST] → HubSpot Note [Code] → Slack Alert [Code]
      └─ Error → Alert: Supabase Write Failed [Code]
```

> **No LLM calls in n8n.** All field extraction done by Retell post_call_analysis (gpt-4.1-mini).
> GPT and Groq HTTP nodes removed. n8n reads structured JSON from webhook.
> Premium call processor maps same fields as Standard PLUS: appointment_date, appointment_time,
> job_type_booked, booking_attempted, booking_success. call_tier = "Premium".

### Premium-specific call_analysis.custom_analysis_data fields
| Field | Description |
|---|---|
| `booking_attempted` | True if agent attempted to book (Premium CAN book) |
| `booking_success` | True if booking was made |
| `appointment_date` | Date of booked appointment |
| `appointment_time_window` | Time window of booked appointment |
| `job_type_booked` | Type of job booked |
| `reschedule_or_cancel` | If caller wanted to reschedule or cancel |
| `caller_email` | Email if provided during call |

---

## Email Flow (Premium Clients — 4 emails)

1. Stripe welcome email
2. Integration setup email (Premium-only — Google Calendar, Jobber)
3. "You're Live" email + PDF
4. Weekly report (ongoing)

### Email Routing (Premium)

| Notification Type | To |
|---|---|
| Internal onboarding notifications | `onboarding@syntharra.com` |
| Internal call processor notifications | `admin@syntharra.com` |
| Customer-facing support reference | `support@syntharra.com` |

---

## SMS

- SMS wired but disabled: `SMS_ENABLED=false`
- Preferred provider: Telnyx (awaiting AI evaluation approval)
- Backup: Plivo. **Never Twilio.**

---

## Retell Agents

Same Retell API key and rules as Standard: `{{RETELL_API_KEY}}`
- **NEVER delete or recreate a Retell agent**
- **Always publish after any agent update**: `POST https://api.retellai.com/publish-agent/{agent_id}`
- Prompt architecture: master base prompt + company info block + call type nodes
- Dynamic variables: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- **Use commas not dashes** in all prompts

### Enhancement Sprint Features (applied 2026-04-04)
| Feature | Setting |
|---|---|
| Post-call analysis | 21 custom fields + 5 Premium-specific + 3 presets, gpt-4.1-mini |
| Guardrails | Output: 7 topics, Input: jailbreak detection |
| Boost keywords | 40+ HVAC terms (brands, refrigerants, components) |
| Pronunciation dictionary | HVAC, SEER, Trane, Rheem, Daikin, Lennox |
| Backchannel | Enabled, frequency 0.8 |
| Reminders | 15s trigger, max 2 |
| Voice tuning | responsiveness 0.85, speed 1.05, dynamic |
| Call limits | 30s silence hangup, 10min max |
| Webhook filter | call_analyzed only |
| Handbook config | echo_verification, scope_boundaries, nato_phonetic, high_empathy |

### Premium Agent & Flow IDs
| Agent | ID | Status |
|---|---|---|
| Premium MASTER | `agent_9822f440f5c3a13bc4d283ea90` | Not yet published — awaiting Phase 8 promotion |
| Premium TESTING | `agent_2cffe3d86d7e1990d08bea068f` | Preserved — core_flow fixes applied |
| Premium DEMO | Created in Phase 1 of enhancement sprint | Enhancement target — verified config |

| Flow | ID | Bound to |
|---|---|---|
| Premium MASTER flow | `conversation_flow_1dd3458b13a7` | Premium MASTER agent |
| Premium TESTING flow | `conversation_flow_2ded0ed4f808` | Premium TESTING agent (DO NOT MODIFY) |
| Premium DEMO flow | Created in Phase 1 | Premium DEMO agent |
- Flow tools point to: `https://n8n.syntharra.com/webhook/retell-integration-dispatch` (live) or `https://n8n.syntharra.com/webhook/retell-tool-stub` (testing stub)

### Language Setting
- Premium agent language: `en-US` (Standard is `multi`)

### Tool Stub Workflow (testing only)
- n8n workflow: `[TEST STUB] Retell Tool Dispatcher` ID `UKEoUeNqYvDDJv79`
- Stub URL: `https://n8n.syntharra.com/webhook/retell-tool-stub`
- When testing is done: PATCH flow tools back to `https://n8n.syntharra.com/webhook/retell-integration-dispatch`

---

## Dashboard

- Live at `syntharra.com/dashboard.html?agent_id=X`
- Shows live Supabase data for the client's agent

---

## Shared Workflows (also affect Premium)

| Workflow | ID |
|---|---|
| Stripe Workflow | `ydzfhitWiF5wNzEy` |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` |
| Minutes Calculator | `9SuchBjqhFmLbH8o` |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` |
| Publish Retell Agent | `sBFhshlsz31L6FV8` |

---

## Scaling Architecture (for future clients)

- Retell API auto-clones agents per client via n8n onboarding triggered by Jotform
- Supabase stores all client config
- Repo structure target: `hvac-standard/`, `hvac-premium/`, `plumbing-standard/`, etc. with `shared/` folder

---

## Pre-Launch Checklist (Premium-specific)

- [ ] Enable repeat caller detection (currently wired, not enabled)
- [ ] Complete Telnyx SMS setup (awaiting AI evaluation approval)
- [ ] Switch Stripe to live mode — recreate Premium product, prices, coupons, webhook

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

> After Jotform Premium onboarding completes and the agent goes live, the workflow updates the client contact and creates a deal at **Active** stage in HubSpot automatically.

---

## COMPONENTS Architecture (v2 Build Code — 2026-04-05)

**Build code location:** n8n workflow `kz1VmwNccunRMEaF`, "Build Premium Prompt + Flow" node (Code node v2)

Premium now uses a shared **COMPONENTS object** with 14 reusable instruction functions:
1. `identify_call` — Classify call type (new service, emergency, callback, spam, wrong number)
2. `verify_emergency` — Emergency detection with safe vs urgent routing
3. `callback_node` — Existing customer callback handling
4. `existing_customer_node` — Identified repeat customer workflow
5. `general_questions_node` — FAQ and product questions
6. `spam_robocall_node` — Spam/robocall handling
7. `transfer_failed_node` — Failed transfer recovery
8. `ending_node` — Call conclusion
9. `call_style_detector` — Classify caller personality (chatty/technical/distracted/abrupt/neutral)
10. `validate_phone` — Phone number validation
11. `warm_transfer_summary` — Warm transfer preamble
12. `emergency_transfer_summary` — Emergency transfer preamble
13. `booking_capture_node` — Premium-specific: booking capture with appointment scheduling
14. `fallback_leadcapture_node` — Fallback lead capture when premium features unavailable

**Why COMPONENTS:** Single source of truth for all node instructions. Both Premium and Standard reference the same 14 functions. Functions accept parameters (`primaryCaptureNode`, `pricingInstr`, `bookingAvailable`) to adapt behavior for each tier.

### Flow Structure — Premium (20 nodes total)
- 15 conversation nodes (use COMPONENTS functions)
- 2 code nodes (call_style_detector, validate_phone)
- 2 transfer nodes (warm_transfer, emergency_transfer)
- 1 end node (End Call)

### Token Usage — Premium v2
- Per-turn: ~2,670 tokens (37% reduction from v1)
- Global prompt: ~1,500 tokens
- Largest node instruction: ~1,100 tokens (booking_capture_node)
- Well within 4k target

### Post-Call Analysis — Premium
17 custom fields including:
- Standard: call_type, lead_score, urgency, sentiment, summary, notes
- Premium-specific: booking_attempted, booking_success, appointment_date, appointment_time, job_type_booked, reschedule_or_cancel, caller_email

---

## Architecture Decisions

| Decision | Chose | Why | Revisit if |
|---|---|---|---|
| Same Supabase table as Standard | hvac_standard_agent with plan_type column | Simpler cross-plan queries; Premium extras are nullable columns; confirmed by Dan 2026-04-02 | 10+ Premium-only columns needed |
| OAuth server | Separate Railway service | Google Calendar and Jobber OAuth require redirect URIs; separate service keeps auth concerns isolated from n8n | — |
| Multi-notification | notification_email_2/3, notification_sms_2/3 in table | Premium clients often have multiple staff who need call alerts; built into schema from the start | — |
| Repeat caller detection | In call processor workflow | Premium clients pay for a more intelligent receptionist; repeat caller = existing customer path, warmer tone |
| Retell-native over Groq/OpenAI | Retell `post_call_analysis_data` (gpt-4.1-mini) | Eliminates LLM costs + rate limits from n8n; extraction at platform level; 21 custom + 5 Premium-specific fields | — |
