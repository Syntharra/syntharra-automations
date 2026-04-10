---
name: hvac-standard
description: >
  Master reference for the entire Syntharra HVAC Standard pipeline — from client onboarding
  through agent behaviour to call processing, and all three test suites.
  Load this skill when working on ANYTHING related to Standard HVAC: the Retell agent, 
  conversation flow, prompts, onboarding workflow, call processor, Supabase schema, Stripe,
  E2E testing, agent simulator, call processor testing, or go-live readiness.
  This skill is the map. The three testing sub-skills are the detail — load them alongside
  this one when deep-diving into a specific test suite.
  Sub-skills: e2e-hvac-standard | standard-call-processor-testing | hvac-standard-agent-testing
---

> **Single Syntharra product — $697/mo HVAC Standard. Premium retired 2026-04-08.**
> **Last verified: 2026-04-10** — E2E 13/13 passing, 30-scenario call processor 90/90 passing.
> **System status: PRE-LAUNCH — Telnyx vault keys needed from Dan; Stripe live mode pending.**

## retell-iac change workflow (canonical — do not bypass)

All agent changes go through `retell-iac/` on `main`. Never edit the Retell dashboard directly.

1. Edit `retell-iac/components/<name>.json` or `retell-iac/manifests/hvac-standard.yaml`
2. Build: `python retell-iac/scripts/build_agent.py --manifest retell-iac/manifests/hvac-standard.yaml --out retell-iac/build/hvac-standard.built.json`
3. Diff verify: `python retell-iac/scripts/diff.py`
4. Patch Standard CLONE agent, publish, test
5. On green: `python retell-iac/scripts/promote.py --agent standard_master --built retell-iac/build/hvac-standard.built.json`

# HVAC Standard — Master Pipeline Reference

---

## System Overview

```
Client pays (Stripe)
  → Jotform onboarding form submitted
    → n8n: provision Retell agent + conversation flow + Telnyx phone number
      → Retell agent live on client's phone number
        → Caller rings → Sophie answers → lead captured
          → Retell post-call analysis (gpt-4.1-mini) extracts all fields
            → n8n call processor (lean fan-out): filter → lookup client →
                build payload → Brevo email + Slack (if configured) + SMS stub
```

> **Architecture change (2026-04-09):** Call processor rewritten as lean fan-out.
> No Supabase writes. No HubSpot writes. Zero per-call storage in Supabase.
> Retell is the source of truth for all call data.

> **Architecture change (2026-04-04):** GPT/Groq transcript analysis removed from n8n.
> Retell's built-in `post_call_analysis_data` (21 custom fields + 3 system presets) now
> extracts all call data at the platform level. n8n just reads the structured output.
> This eliminates LLM API costs, rate limits, and parsing failures from the call pipeline.

```
Note: the above ``` closes the architecture note block. Remove if rendering is odd.
```

One Retell agent per client. All config stored in `hvac_standard_agent` (Supabase).
**No per-call Supabase storage** — Retell owns call data. Dashboard reads Retell directly via proxy webhook.
HubSpot writes removed from call processor 2026-04-09.

---

## Agent — Arctic Breeze HVAC (MASTER / TEST)

| Item | Value |
|---|---|
| **MASTER Agent ID** | `agent_b46aef9fd327ec60c657b7a30a` |
| **MASTER Flow ID** | `conversation_flow_19684fe03b61` |
| **TESTING Agent ID** | `agent_41e9758d8dc956843110e29a25` |
| **TESTING Flow ID** | `conversation_flow_bc8bb3565dbf` |
| Phone Number | `+1 (812) 994-4371` (⚠️ bind in Retell dashboard) |
| Voice | Sophie (female) |

### Demo Agents (must always stay published)
| Name | Agent ID |
|---|---|
| Jake (male demo) | `agent_b9d169e5290c609a8734e0bb45` |
| Sophie (female demo) | `agent_2723c07c83f65c71afd06e1d50` |

### Enhancement Sprint Features (applied 2026-04-04)
| Feature | Setting |
|---|---|
| Post-call analysis | 21 custom fields + 3 presets, gpt-4.1-mini |
| Guardrails | Output: 7 topics, Input: jailbreak detection |
| Boost keywords | 40+ HVAC terms (brands, refrigerants, components) |
| Pronunciation dictionary | HVAC, SEER, Trane, Rheem, Daikin, Lennox |
| Backchannel | Enabled, frequency 0.8 |
| Reminders | 15s trigger, max 2 |
| Voice tuning | responsiveness 0.85, speed 1.05, dynamic |
| Call limits | 30s silence hangup, 10min max |
| Webhook filter | call_analyzed only |
| Fallback number | +18563630633 |
| Phone geo lock | US-only inbound/outbound |

### HARD RULES — read before any Retell work
1. **NEVER delete or recreate a Retell agent.** `agent_id` is the FK tying Retell, Supabase, call processor, and phone number together. Always patch in place.
2. **Always publish after any agent update:** `POST https://api.retellai.com/publish-agent/{agent_id}` — returns 200 empty body.
3. **MASTER is sacred.** All prompt experiments happen on TESTING agent only. Never touch MASTER until changes hit 95%+ pass rate on TESTING.
4. **Demo agents must always stay published.**
5. **Use commas not dashes** in agent prompts — better AI readability.

---

## Conversation Flow — 15 Nodes (v2 COMPONENTS architecture)

`greeting` → `identify_call` → [call_style_detector] → `fallback_leadcapture_node` → `verify_emergency`
→ `callback_node` → `existing_customer_node` → `general_questions_node` → `spam_robocall_node`
→ [validate_phone] → `warm_transfer` → `transfer_failed_node` → `ending_node` → `End Call`

| # | Node ID | Name | Type |
|---|---|---|---|
| 1 | `node-greeting` | `greeting_node` | conversation |
| 2 | `node-identify-call` | `identify_call_node` | conversation |
| 3 | — | `call_style_detector` | code |
| 4 | `node-leadcapture` | `fallback_leadcapture_node` | conversation |
| 5 | `node-verify-emergency` | `verify_emergency_node` | conversation |
| 6 | `node-callback` | `callback_node` | conversation |
| 7 | `node-existing-customer` | `existing_customer_node` | conversation |
| 8 | `node-general-questions` | `general_questions_node` | conversation |
| 9 | `node-spam-robocall` | `spam_robocall_node` | conversation |
| 10 | — | `validate_phone` | code |
| 11 | `node-transfer-call` | `warm_transfer` | transfer_call |
| 12 | `node-transfer-failed` | `transfer_failed_node` | conversation |
| 13 | `node-ending` | `ending_node` | conversation |
| 14 | `node-end-call` | `End Call` | end |
| 15 | — | `Emergency Transfer` | transfer_call |

### Code Node (caller style detection)
- Sits between `identify_call` and `nonemergency_leadcapture`
- Reads `metadata.transcript`, classifies caller style (chatty/technical/distracted/abrupt/neutral)
- Injects `caller_style_note` variable at top of leadcapture context
- **Do NOT use `conversationHistory` or `call.transcript`** — neither exists in code node context
- Use `metadata.transcript` (array of `{role, content}`)
- `else_edge.transition_condition.prompt` must equal exactly `"Else"`

### Prompt Architecture
- Global prompt: ~4,000 chars (lean — long prompts cause instruction-following failures beyond attention window)
- Dynamic variables: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- Node-level instructions for call type handling: service/repair, install/quote, existing customer, FAQ, emergency, live transfer
- Personality handling injected at leadcapture node top via code node — NOT at end of global prompt

---

## n8n Workflows

| Workflow | ID | Purpose |
|---|---|---|
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | Retell agent provisioning + Telnyx phone chain |
| HVAC Call Processor | `Kg576YtPM9yEacKn` | Lean fan-out: filter → lookup → Brevo email + Slack + SMS stub |
| Stripe Webhook | `xKD3ny6kfHL0HHXq` | Stripe checkout → tier-aware welcome email + Supabase write |
| Retell Proxy | `Y1EptXhOPAmosMbs` | Dashboard: POST /webhook/retell-calls → Retell list-calls |
| Nightly GitHub Backup | `EAHgqAfQoCDumvPU` | Repo backup |

> ⚠️ **Monthly Minutes** (`z1DNTjvTDAkExsX8`) and **Usage Alert Monitor** (`Wa3pHRMwSjbZHqMC`) are **archived** — replaced by `tools/monthly_minutes.py` and `tools/usage_alert.py` respectively.
> **Weekly client report** → `tools/weekly_client_report.py` (deploy cron once second client lands).
> **E2E Cleanup** workflow (`URbQPNQP26OIdYMo`) was never built — cleanup is manual for now.

- **n8n instance:** `https://n8n.syntharra.com`
- **Never use `mcp__claude_ai_n8n__*` tools** — that MCP talks to a cloud account. Always use Railway REST API directly.
- **Always publish after any workflow edit**
- **n8n PUT payload fields:** only `name`, `nodes`, `connections`, `settings` (only `executionOrder` inside settings) — extra fields cause 400 errors
- **Email via Brevo HTTP API** (not SMTP2GO, not n8n Brevo node) — POST to `https://api.brevo.com/v3/smtp/email` with Brevo API key from vault.
- **n8n Code nodes cannot make outbound HTTP calls** — `fetch()`, `$helpers.httpRequest`, and `this.helpers.httpRequest` all fail. Always use an HTTP Request node for any outbound call.
- When an HTTP Request node returns an empty body (e.g. Retell publish returns 200 with no body), set `options.response.response.responseFormat: 'text'` to prevent JSON parse errors.
- **Telnyx HTTP nodes must have `continueOnFail: true`** — they will 401 when vault keys missing; without this flag they kill the whole workflow.

### Email Routing
| Type | To |
|---|---|
| Internal onboarding | `onboarding@syntharra.com` |
| Internal call alerts | `admin@syntharra.com` |
| Customer-facing | `support@syntharra.com` |

---

## Jotform — Standard Onboarding

| Item | Value |
|---|---|
| Form ID | `260795139953066` |
| Webhook URL | `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding` |
| API Key | vault: `service_name='Jotform'`, `key_type='api_key'` |

**Use REST API directly — do NOT use MCP OAuth connector (broken).**

### Jotform Webhook — How Data Arrives (CRITICAL — read before touching Parse node)

JotForm sends a POST with all q* field answers packed inside `body.rawRequest` as a **JSON string**.
Direct `body.q*` keys are absent or stale. The Parse node must:
1. Read `body.rawRequest`
2. `JSON.parse()` it
3. Spread the result on top of body: `formData = { ...body, ...JSON.parse(body.rawRequest) }`

**Phone fields** arrive as objects: `{ full: '(555) 234-5678' }` — NOT strings.
Use `cleanPhone()`: `if (typeof val === 'object' && val.full) return val.full.replace(/[^+\d]/g, '')`.

**Checkbox fields** use the `q{N}_option_` key pattern inside rawRequest (NOT the named key).
- `services_offered` → key is `q13_option_` (NOT `q13_servicesOffered`)
- `brands_serviced`  → key is `q14_option_` (NOT `q14_brandsequipmentServiced`)
- `certifications`   → key is `q29_option_` (NOT `q29_certifications`)
Code: `formData['q13_option_'] || formData.q13_servicesOffered` (fallback for safety)

### Jotform → Supabase Column Mapping

| Supabase Column | rawRequest Key | Notes |
|---|---|---|
| `company_name` | `q4_hvacCompany` | |
| `owner_name` | `q54_ownerName` | |
| `client_email` | `q5_emailAddress` | |
| `main_phone` | `q6_mainCompany` | phone object → `cleanPhone()` |
| `website` | `q7_companyWebsite` | |
| `years_in_business` | `q8_yearsIn` | |
| `timezone` | `q34_timezone` | default `America/Chicago` |
| `agent_name` | `q10_aiAgent10` | |
| `voice_gender` | `q11_aiVoice` | default `Female` |
| `custom_greeting` | `q73_customGreetingText` OR `q38_customGreeting` | try q73 first |
| `services_offered` | **`q13_option_`** (checkbox) | NOT `q13_servicesOffered` |
| `brands_serviced` | **`q14_option_`** (checkbox) | NOT `q14_brandsequipmentServiced` |
| `certifications` | **`q29_option_`** (checkbox) | NOT `q29_certifications` |
| `service_area` | `q16_primaryService` | |
| `service_area_radius` | `q40_serviceAreaRadius` | |
| `licensed_insured` | `q28_licensedAnd` | default `Yes` |
| `emergency_service` | `q20_247Emergency` | default `No` |
| `emergency_phone` | `q21_emergencyAfterhours` | phone object → `cleanPhone()` |
| `after_hours_behavior` | `q22_afterhoursBehavior` | |
| `after_hours_transfer` | `q68_afterHoursTransfer` | |
| `business_hours` | `q17_businessHours` | |
| `response_time` | `q18_typicalResponse` | |
| `pricing_policy` | `q42_pricingPolicy` | |
| `diagnostic_fee` | `q41_diagnosticFee` | |
| `standard_fees` | `q43_standardFees` | |
| `free_estimates` | `q24_freeEstimates` | default `Yes - always free` |
| `do_not_service` | `q57_doNotServiceList` | |
| `transfer_phone` | `q48_transferPhone` | phone object → `cleanPhone()` |
| `transfer_triggers` | `q49_transferTriggers` | |
| `transfer_behavior` | `q50_transferBehavior` | |
| `financing_available` | `q25_financingAvailable` | default `No` |
| `financing_details` | `q44_financingDetails` | |
| `warranty` | `q26_serviceWarranties` | default `Yes` |
| `warranty_details` | `q27_warrantyDetails` | |
| `payment_methods` | `q45_paymentMethods` | |
| `maintenance_plans` | `q46_maintenancePlans` | default `No` |
| `membership_program` | `q58_membershipProgramName` | |
| `lead_contact_method` | `q31_leadContact` | default `Both` |
| `lead_phone` | `q32_leadNotification` | phone object → `cleanPhone()` |
| `lead_email` | `q33_leadNotification33` | |
| `notification_email_2` | `q66_notifEmail2` | |
| `notification_email_3` | `q67_notifEmail3` | |
| `notification_sms_2` | `q64_notifSms2` | phone object → `cleanPhone()` |
| `notification_sms_3` | `q65_notifSms3` | phone object → `cleanPhone()` |
| `google_review_rating` | `q55_googleReviewRating` | |
| `google_review_count` | `q56_googleReviewCount` | |
| `unique_selling_points` | `q51_uniqueSellingPoints` | |
| `current_promotion` | `q52_currentPromotion` | |
| `seasonal_services` | `q53_seasonalServices` | |
| `additional_info` | `q37_additionalInfo` | |
| `stripe_customer_id` | `stripe_customer_id` | top-level body field |
| `submission_id` | `submissionID` / `submission_id` / `submission` | top-level body; also in rawRequest |
| `agent_id` | Retell API response | |
| `conversation_flow_id` | Retell API response | |

---

## Supabase

| Item | Value |
|---|---|
| URL | `https://hgheyqwnrcvwtgngqdnq.supabase.co` |
| Client config table | `hvac_standard_agent` |
| Billing state tables | `client_subscriptions`, `billing_cycles`, `overage_charges`, `monthly_billing_snapshot` |
| Vault table | `syntharra_vault` |
| Dashboard view | `client_dashboard_info` (narrow read-only subset — SECURITY DEFINER) |

> ⚠️ **`hvac_call_log` was dropped 2026-04-09.** All 15 `hvac_call_log*` tables deleted (backup in `backup_hvac_call_log_prepart_20260409`). **Retell is the source of truth for call data.** The dashboard reads calls via Retell `list-calls` API, not Supabase. No per-call writes happen anywhere in n8n.

### Call Processor filter logic (n8n IF node)
```javascript
// Filter: Lead or Emergency
event === "call_analyzed"
AND (is_lead === true OR urgency === "emergency")
```
- `is_lead` and `urgency` come pre-computed in `call.call_analysis.custom_analysis_data`
- Retell's post-call analysis (gpt-4.1-mini) populates these fields — n8n reads, does not recompute
- Calls that fail the filter silently drop (false branch unconnected)

---

## Call Processor — Architecture (lean fan-out, rewritten 2026-04-09)

```
Retell POST → Webhook: retell-hvac-webhook
  → Filter: Lead or Emergency [IF — event=call_analyzed AND (is_lead OR urgency=emergency)]
      FALSE branch → silent drop (dead end)
      TRUE branch:
        → Lookup Client [HTTP GET Supabase hvac_standard_agent by agent_id]
        → Build Payload [Code — assembles email HTML, Slack blocks, SMS stub]
        → Send Lead Email (Brevo) [HTTP POST → api.brevo.com/v3/smtp/email]
        → Has Slack? [IF — slack_webhook_url non-null]
            TRUE → Post to Client Slack [HTTP POST → client webhook URL]
        → SMS Stub (Telnyx TODO) [Code — no-op, logs to console, returns sms_pending:true]
```

**7 nodes total. Zero Supabase writes. Zero HubSpot writes. Retell is source of truth.**

Generator: `tools/build_call_processor_workflow.py` (not yet updated to match current live — use n8n API to edit live).

### Retell Post-Call Analysis
| Item | Value |
|---|---|
| Model | `gpt-4.1-mini` (set on Retell agent) |
| Custom fields | `is_lead`, `urgency`, `is_spam` (+ 18 others) |
| System presets | `call_summary`, `call_successful`, `user_sentiment` |
| webhook_events | `call_analyzed` only |

### Client Slack webhook — how it works
- Jotform field `q76_slackIncoming` (Section 5, optional)
- Onboarding workflow maps it to `slack_webhook_url` in `hvac_standard_agent`
- Call processor checks `Has Slack?` IF node — only posts if non-null/non-empty
- Null/blank: silently skipped, email + SMS stub still fire

---

## COMPONENTS Architecture (v2 Build Code — 2026-04-05)

**Build code location:** n8n workflow `4Hx7aRdzMl5N0uJP`, "Build Retell Prompt" node (Code node v2)

Standard now uses the **same shared COMPONENTS object** as Premium — 14 reusable instruction functions. Single source of truth for all node behavior.

Functions accept parameters to adapt for Standard tier:
- `primaryCaptureNode`: `fallback_leadcapture_node` (vs Premium's `booking_capture_node`)
- `pricingInstr`: Standard pricing rules (no booking availability)
- `bookingAvailable`: `false` for Standard

### Flow Structure — Standard (15 nodes total)
- 13 conversation nodes (use COMPONENTS functions)
- 2 code nodes (call_style_detector, validate_phone)
- 2 transfer nodes (warm_transfer, emergency_transfer)
  - **Changed from cold_transfer to warm_transfer** (2026-04-05) for consistent caller experience

### Token Usage — Standard v2
- Per-turn: ~2,400 tokens (optimized for lean tier)
- Global prompt: ~1,300 tokens
- Largest node instruction: ~1,000 tokens (fallback_leadcapture_node)
- Well within 4k target

### Post-Call Analysis — Standard
17 custom fields (same as Premium for consistency):
- Standard: call_type, lead_score, urgency, sentiment, summary, notes, transfer info, repeat caller status
- Always-false fields: booking_attempted, booking_success (placeholder for Premium compatibility)
- Enables same HubSpot data model + Slack alert format across both tiers

### GOTCHA: Supabase 409 Conflicts
Call processor hits 409 conflict on `hvac_call_log` unique constraint when duplicate `call_id` arrives.
**Fix:** Standard call processor adds HTTP header: `Prefer: resolution=merge-duplicates`
This tells Supabase to resolve duplicates instead of 409 failing. Applied 2026-04-05.

---

## Stripe (TEST MODE — live mode migration P1 blocker)

3-tier pricing as of 2026-04-09. All IDs in `syntharra_vault` (service_name='Stripe').

| Tier | Monthly | Annual | Minutes | Overage |
|---|---|---|---|---|
| Starter | $397/mo | $330/mo | 350 min | $0.25/min |
| **Professional** (hero) | **$697/mo** | **$581/mo** | **700 min** | **$0.18/min** |
| Business | $1,097/mo | $914/mo | 1,400 min | $0.12/min |

- Activation Fee: $997 (one-time, all tiers)
- Annual = 2 months free (annual price × 12)
- ⚠️ **All IDs are TEST MODE.** Dan to provide live secret key before first paying client.
- Stripe webhook workflow: `xKD3ny6kfHL0HHXq` — maps all 6 price IDs → tier config → welcome email
- Checkout server: Railway-deployed OAuth server handles `/create-checkout-session`

---

## SMS
- Wired but disabled: `SMS_ENABLED=false`
- Provider: Telnyx (awaiting AI evaluation approval — account active, $5 loaded)
- **Never Twilio**

---

## HubSpot Integration
> ⚠️ **HubSpot removed from call processor 2026-04-09.** The lean fan-out call processor no longer writes call notes to HubSpot. If re-adding, build a separate fan-out node — do NOT add Supabase writes.
- Client contacts: created at Stripe signup, updated at Jotform onboarding (still relevant for CRM)
- API key: vault `service_name='HubSpot'`, `key_type='api_key'`

---

## Credential Access — Syntharra Vault

All keys in Supabase `syntharra_vault`. Query pattern:
```
GET /rest/v1/syntharra_vault?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value
Headers: apikey + Authorization: Bearer {SB_SERVICE_ROLE_KEY}
```

| service_name | key_type | What it is |
|---|---|---|
| `Retell AI` | `api_key` | Retell API key |
| `Retell AI` | `agent_id_arctic_breeze` | MASTER agent ID |
| `Retell AI` | `conversation_flow_id` | Live flow ID |
| `n8n Railway` | `api_key` | n8n API key |
| `n8n Railway` | `instance_url` | `https://n8n.syntharra.com` |
| `Supabase` | `service_role_key` | Full admin key |
| `Jotform` | `api_key` | Jotform API key |
| `Jotform` | `form_id_standard` | `260795139953066` |
| `Stripe` | `prod_starter` / `prod_professional` / `prod_business` | Product IDs (3 tiers) |
| `Stripe` | `price_starter_monthly` / `price_professional_monthly` / `price_business_monthly` | Monthly price IDs |
| `Stripe` | `price_starter_annual` / `price_professional_annual` / `price_business_annual` | Annual price IDs |
| `Stripe` | `price_activation_fee` | $997 one-time activation fee |
| `Telnyx` | `api_key` | Telnyx API key (needed to activate phone chain) |
| `Telnyx` | `retell_sip_connection_id` | Retell SIP connection ID (needed to bind phone numbers) |
| `Brevo` | `api_key` | Email API key (call processor + welcome emails) |
| `Slack` | `bot_token` | Slack bot token |
| `GitHub` | `personal_access_token` | GitHub PAT |

---

---

# TEST SUITES

Three active test suites + one in-design. Run before any production change. Run order: E2E → Call Processor → (Post-Call Analysis when built).
> Agent Simulator (`tools/openai-agent-simulator.py`) is archived infra — was used for conversation flow testing. May be revived if agent prompt changes need validation.

> **Testing System Design (2026-04-10):** Full multi-layer testing architecture documented at `docs/TESTING-SYSTEM-DESIGN.md`. Build it in the next session. Near-zero cost — no Retell voice minutes used.

---

## TEST SUITE 1 — E2E Pipeline Test

**Script:** `python tools/test_e2e_pipeline.py`
**Status: 13/13 ✅ — Verified 2026-04-10**

Tests the full provisioning pipeline: Jotform webhook → n8n execution → Supabase row → Dashboard 0-calls.

```bash
python tools/test_e2e_pipeline.py              # full run (auto-cleanup)
python tools/test_e2e_pipeline.py --no-clean   # skip cleanup (inspect artefacts)
python tools/test_e2e_pipeline.py --dry-run    # print payload only
```

| Phase | What's checked | Checks |
|---|---|---|
| 1 | Jotform webhook accepted (HTTP 200) | 1 |
| 2 | n8n onboarding execution found + succeeded | 2 |
| 3 | Supabase row created, 7 key fields populated | 8 |
| 4 | Retell agent exists + published | 2 (skipped if no RETELL_API_KEY) |
| 5 | Dashboard proxy returns 0 calls for new agent | 2 |

**Cleanup:** on success, triggers cleanup webhook (manual delete until E2E cleanup workflow built).

### When to run
- Before any n8n onboarding workflow change
- After any Retell conversation flow structural change
- Before going live with a new client
- After any Supabase schema change to `hvac_standard_agent`

### Key E2E IDs
| Resource | ID |
|---|---|
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` |
| Jotform Standard form | `260795139953066` |
| Webhook path | `/webhook/jotform-hvac-onboarding` |
| Dashboard proxy webhook | `/webhook/retell-calls` |

### E2E Gotchas
- **Execution not found** → n8n server clock ~300ms behind local. Script uses 3s lookback buffer.
- **Execution `running` forever** → script polls specific exec ID by `/api/v1/executions/{id}` until done.
- **Supabase query 400** → use `company_name=eq.{name}` not `submission_id=eq.{id}` (underscores cause issues).
- **Telnyx nodes fail** → expected — vault keys not yet added. Nodes have `continueOnFail: true`.
- **Cleanup 404** → E2E cleanup workflow not yet built. Delete test agent manually from Retell dashboard.

---

## TEST SUITE 2 — Agent Behaviour Simulator (ARCHIVED)

> **Status: Archived infra.** The OpenAI simulator (`tools/openai-agent-simulator.py`) and its 91-scenario suite are in `archived/testing-infra/`. Groq free tier (500k TPD limit) was exhausted by full runs. Revive if major prompt surgery is needed.

### Promoting TESTING → MASTER
Only promote when:
1. E2E passes on TESTING agent
2. Call processor test passes
3. Manual phone test confirms Sophie behaves correctly on a real call
4. Then patch MASTER in place via `retell-iac/scripts/promote.py` — never delete, never recreate
5. Publish MASTER immediately after patch

---

## TEST SUITE 3 — Call Processor Test

**Script:** `python tools/test_call_processor.py`
**Status: 90/90 ✅ — 30 scenarios — Verified 2026-04-10**

Tests the n8n call processor workflow in isolation. Fires fake Retell post-call webhooks with pre-set `is_lead`/`urgency` flags and verifies n8n execution status. Does NOT check email delivery (Brevo has no read API).

```bash
python tools/test_call_processor.py              # run all 30 scenarios
python tools/test_call_processor.py --scenario 3 # run one scenario by ID
python tools/test_call_processor.py --dry-run    # print payloads only
```

| Scenario range | Category | What's covered |
|---|---|---|
| 1–15 | Should notify | Lead/emergency: repair, install, maintenance, emergency, commercial, transfer, vulnerable occupant |
| 16–25 | Should filter | Spam, wrong number, out-of-area, pricing-only, silence, vendor, job applicant, urgency=high (not emergency) |
| 26–30 | Edge cases | Wrong event type, max lead score, empty fields, score=0+emergency, is_spam+is_lead |

### When to run
- After any change to the call processor n8n workflow (`Kg576YtPM9yEacKn`)
- After any change to the filter logic (`is_lead` OR `urgency=emergency`)
- Before go-live

### Call Processor Gotchas
- **`urgency=high` does NOT trigger** — only `urgency=emergency` passes the filter. `high` is filtered.
- **is_lead=true always triggers** regardless of lead_score or is_spam value — the filter only checks those two fields.
- **Wrong event type filtered** — only `event=call_analyzed` passes. `call_started`, `call_ended` are dropped.
- **n8n clock skew** — test sets trigger_time 3s in the past to handle ~300ms server clock offset vs local clock.
- **Execution discovery** — test polls `status=running` first, then tracks specific exec ID to completion. Default listing excludes running executions.

---

## TEST SUITE 4 — Post-Call Analysis Quality (DESIGN READY, NOT YET BUILT)

**Design:** `docs/TESTING-SYSTEM-DESIGN.md`
**Status: Not yet built — build in next session**

Tests whether Retell's gpt-4.1-mini post-call analysis correctly classifies transcripts as `is_lead`, `urgency`, `is_spam`. This is the gap that existing suites don't cover.

| Layer | Script (to build) | What it tests | Cost |
|---|---|---|---|
| 1 | `tools/test_post_call_analysis.py` | 25 transcript scenarios → correct `is_lead`/`urgency`/`is_spam` | FREE (`claude -p`) |
| 2 | `tools/test_email_delivery.py` | Brevo actually delivered to inbox | FREE (Gmail MCP) |
| Runner | `tools/run_full_test_suite.py` | Orchestrates all 3 layers | — |

**25 scenarios:** 15 should-notify (lead/emergency), 7 should-filter (spam/wrong number/billing), 3 edge cases.
**Swarm:** 5 parallel subagents × 5 scenarios each. ~30s total vs 2min serial.
**Fix rule:** When a scenario fails, update the post-call analysis config (not Sophie's conversation prompt). Max 10 words per fix.

---

## Test Run Order & Go-Live Gate

```bash
# Before any production change:
python tools/test_e2e_pipeline.py          # must be 13/13
python tools/test_call_processor.py        # must be 90/90

# Once TEST SUITE 4 is built:
python tools/run_full_test_suite.py        # all 3 layers in one run

# Before go-live:
# 1. Dan: add Telnyx vault keys (api_key + retell_sip_connection_id)
# 2. Dan: provide Stripe live secret key → replicate 7 prices in live mode
# 3. Dan: bind +18129944371 to MASTER in Retell dashboard (Phone Numbers)
# 4. 3-5 real phone calls to +18129944371 → manual smoke (Dan)
# 5. Confirm lead emails arrive at test-e2e@syntharra.com
# 6. Deploy monthly_minutes.py + usage_alert.py crons on Railway
```

---

## Architecture Decisions

| Decision | Chose | Why |
|---|---|---|
| Node-based conversation flow | Deterministic node routing | More reliable than freeform prompt; each path independently testable |
| Caller style detection | Code node injects `caller_style_note` at leadcapture top | Long global prompt had style instructions ignored at bottom of context |
| Transfer fallback | `transfer_failed` node | If live transfer fails, agent collects contact — never dead-ends caller |
| Single TESTING agent | Separate from MASTER | All prompt experiments on TESTING; MASTER never touched until ≥95% pass rate |
| Retell-native over Groq/OpenAI | Retell `post_call_analysis_data` (gpt-4.1-mini) | Eliminates LLM costs + rate limits from n8n; extraction at platform level |
| Lean global prompt | ~4,000 chars | Instructions beyond ~15k chars fall outside model attention window |
| All pricing redirected | Team callback only | No specific fees in prompt — prevents Sophie quoting wrong amounts |
| SMS disabled at launch | `SMS_ENABLED=false` | Telnyx approval pending — Twilio never |

---

## Demo Call
- **Number:** `+1 (812) 994-4371`
- **Persona to use:** "Mike Henderson"
- Arctic Breeze is the test/demo agent — not a real client

---

## Auto-Update Rule
When any task touches this skill's domain, update this file before chat ends:
- New workflow created/renamed → update workflow table
- Schema change → update Supabase section
- Retell agent/flow change → update agent section
- Stripe product/price change → update Stripe section
- New test suite result → update test suite section
- New gotcha discovered → add to relevant gotchas section


---

## Session Update — 2026-04-04 (Full Pipeline Audit)

### Jotform → Parse → Supabase — Verified Field Map

All 55 data questions on form `260795139953066` audited against Parse JotForm Data node.

**Fixes applied this session:**

| Jotform | Field | Status |
|---|---|---|
| q73_customGreetingText | custom_greeting | ✅ Fixed — was reading dead q38 |
| q72_greetingStyle | greeting_style | ✅ Fixed — was not parsed at all |
| q68_afterHoursTransfer | after_hours_transfer | ✅ Fixed — was not parsed at all |
| q69_separateEmergencyPhone | separate_emergency_phone | ✅ Fixed — was not parsed at all |

### Transfer Number Logic — Correct Spec
```
Priority: (q69 == "Yes - dedicated emergency line" && emergencyPhone) ? emergencyPhone
          : (transferPhone || leadPhone)
```
- q48 transfer_phone = standard live transfer destination (company/office number)
- q21 emergency_phone = ONLY overrides if client explicitly answers q69 = "Yes"
- Fallback = lead_phone

### Email Builder — Correct Field Names
- AI Phone Number: `d.twilio_number` (Telnyx number written here post-provisioning)
- Live Transfer Number: `d.transfer_phone` (q48 — client's company number)

### RULE: Never skip Jotform audit when adding questions
Any new question added to the Jotform MUST be added to Parse JotForm Data in the same session.
This session's bugs all caused by questions added to form without updating the Parse node.


---

## Transfer Number — Authoritative Spec (2026-04-04)

```
Priority:
  if (q69 == "Yes - I have a dedicated emergency line" && emergency_phone)
    → use emergency_phone
  else
    → use transfer_phone (q48) || lead_phone

Fallback: '+10000000000' placeholder if all three are blank
```

| Field | Jotform | Purpose |
|---|---|---|
| `transfer_phone` | q48 | Standard live transfer — the client's company number |
| `emergency_phone` | q21 | Dedicated emergency line — only used if q69 = Yes |
| `separate_emergency_phone` | q69 | Gate: "Yes" = emergency overrides, "No" = use transfer_phone |
| `lead_phone` | q32 | Fallback if transfer_phone not provided |

The email "Live Transfer Number" field always shows `transfer_phone` (q48) — the number
clients give to their customers. The emergency override only applies inside the Retell flow.

---

## Email Builder — Correct Field Names (2026-04-04)

| Email field | Supabase column | Notes |
|---|---|---|
| AI Phone Number | `twilio_number` | Telnyx number written here post-provisioning |
| Live Transfer Number | `transfer_phone` | q48 — client's company number |

Previously `d.ai_phone_number` and `d.transfer_phone_number` — both wrong. Fixed.

---

## Test Data Rule

All E2E test data must use generic values:
- Website: `www.syntharra-test.com`
- Notification emails: `*@syntharra-test.com`
- Membership program: `Care Club` (no company branding)
- Company name: `TestClient HVAC {timestamp}`

Never use real company names, real domains, or branded plan names in test payloads.

## Session Update — 2026-04-06
- Full agentic test run (3 iterations × 91 scenarios) completed
- Final score: **90/91 (98%)** — best ever
- Only failure: #043 commercial property facilities manager (fix blocked by COMPONENT_MAX_CHARS=1200, now raised to 2500)
- Standard MASTER promoted from TESTING — flow version 22
- MASTER architecture now matches TESTING: 20 nodes, modular subagent/component
- Spanish routing node (`spanish_routing_node`) pending removal — not safety-critical
