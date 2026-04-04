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

> **Last verified: 2026-04-04** — Retell Enhancement Sprint complete (Phases 0-7). Call processor now Retell-native — no GPT/Groq.
> **System status: PRE-LAUNCH — ready for live calls. SMS pending Telnyx approval.**

# HVAC Standard — Master Pipeline Reference

---

## System Overview

```
Client pays (Stripe)
  → Jotform onboarding form submitted
    → n8n: provision Retell agent + conversation flow
      → Retell agent live on client's phone number
        → Caller rings → Sophie answers → lead captured
          → Retell post-call analysis (gpt-4.1-mini) extracts all fields
            → n8n call processor: extract fields → Supabase log → email/Slack alert
              → HubSpot: call note logged on client contact
```

> **Architecture change (2026-04-04):** GPT/Groq transcript analysis removed from n8n.
> Retell's built-in `post_call_analysis_data` (21 custom fields + 3 system presets) now
> extracts all call data at the platform level. n8n just reads the structured output.
> This eliminates LLM API costs, rate limits, and parsing failures from the call pipeline.

```
Note: the above ``` closes the architecture note block. Remove if rendering is odd.
```

One Retell agent per client. All config stored in `hvac_standard_agent` (Supabase).
Call logs in `hvac_call_log` (Supabase). CRM in HubSpot.

---

## Agent — Arctic Breeze HVAC (MASTER / TEST)

| Item | Value |
|---|---|
| Agent Name | Arctic Breeze HVAC |
| **MASTER Agent ID** | `agent_4afbfdb3fcb1ba9569353af28d` |
| **TESTING Agent ID** | `agent_731f6f4d59b749a0aa11c26929` |
| Phone Number | `+1 (812) 994-4371` |
| Transfer Number | `+1 (856) 363-0633` |
| **Conversation Flow** | `conversation_flow_34d169608460` |
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

## Conversation Flow — 15 Nodes

`greeting` → `identify_call` → `nonemergency_leadcapture` → `verify_emergency`
→ `callback` → `existing_customer` → `general_questions` → `spam_robocall`
→ `Transfer Call` → `transfer_failed` → `Ending` → `End Call`

| # | Node ID | Name | Type |
|---|---|---|---|
| 1 | `node-greeting` | `greeting_node` | conversation |
| 2 | `node-identify-call` | `identify_call_node` | conversation |
| 3 | `node-leadcapture` | `nonemergency_leadcapture_node` | conversation |
| 4 | `node-verify-emergency` | `verify_emergency_node` | conversation |
| 5 | `node-existing-customer` | `existing_customer_node` | conversation |
| 6 | `node-general-questions` | `general_questions_node` | conversation |
| 7 | `node-callback` | `callback_node` | conversation |
| 8 | `node-spam-robocall` | `spam_robocall_node` | conversation |
| 9 | `node-transfer-call` | `Transfer Call` | transfer_call |
| 10 | `node-transfer-failed` | `transfer_failed_node` | conversation |
| 11 | `node-ending` | `Ending` | conversation |
| 12 | `node-end-call` | `End Call` | end |

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
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | Jotform → Retell agent provisioning |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | Post-call webhook → Groq → Supabase |
| Cleanup (E2E) | `URbQPNQP26OIdYMo` | Auto-deletes test agents after E2E run |
| Stripe Workflow | `ydzfhitWiF5wNzEy` | Stripe checkout → welcome email |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` | Weekly digest to clients |
| Minutes Calculator | `9SuchBjqhFmLbH8o` | Usage tracking |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` | Alerts on high usage |
| Publish Retell Agent | `sBFhshlsz31L6FV8` | Utility: publish agent via webhook |
| Nightly GitHub Backup | `EAHgqAfQoCDumvPU` | Repo backup |

- **n8n instance:** `https://n8n.syntharra.com`
- **Always publish after any workflow edit**
- **n8n PUT payload fields:** only `name`, `nodes`, `connections`, `settings` (only `executionOrder` inside settings) — extra fields cause 400 errors
- All email nodes use SMTP2GO credential: `"SMTP2GO - Syntharra"`
- **n8n Code nodes do NOT support `fetch()` or `$http`** — use Code node (build body) + HTTP Request node (fire call)

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

### Jotform → Supabase Column Mapping (all 40+ fields)

| Supabase Column | Jotform Key |
|---|---|
| `company_name` | `q4_hvacCompany` |
| `owner_name` | `q54_ownerName` |
| `client_email` | `q5_emailAddress` |
| `company_phone` | `q6_mainCompany` |
| `website` | `q7_companyWebsite` |
| `years_in_business` | `q8_yearsIn` |
| `timezone` | `q34_timezone` |
| `agent_name` | `q10_aiAgent10` |
| `custom_greeting` | `q38_customGreeting` |
| `services_offered` | `q13_servicesOffered` |
| `brands_serviced` | `q14_brandsequipmentServiced` |
| `service_area` | `q16_primaryService` |
| `service_area_radius` | `q40_serviceAreaRadius` |
| `certifications` | `q29_certifications` |
| `emergency_service` | `q20_247Emergency` |
| `emergency_phone` | `q21_emergencyAfterhours` |
| `business_hours` | `q17_businessHours` |
| `pricing_policy` | `q42_pricingPolicy` |
| `diagnostic_fee` | `q41_diagnosticFee` |
| `financing_available` | `q25_financingAvailable` |
| `warranty` | `q26_serviceWarranties` |
| `payment_methods` | `q45_paymentMethods` |
| `maintenance_plans` | `q46_maintenancePlans` |
| `membership_program` | `q58_membershipProgramName` |
| `lead_contact_method` | `q31_leadContact` |
| `lead_phone` | `q32_leadNotification` |
| `lead_email` | `q33_leadNotification33` |
| `notification_email_2` | `q66_notifEmail2` |
| `notification_email_3` | `q67_notifEmail3` |
| `notification_sms_2` | `q64_notifSms2` |
| `notification_sms_3` | `q65_notifSms3` |
| `transfer_phone` | `q48_transferPhone` |
| `transfer_triggers` | `q49_transferTriggers` |
| `google_review_rating` | `q55_googleReviewRating` |
| `google_review_count` | `q56_googleReviewCount` |
| `unique_selling_points` | `q51_uniqueSellingPoints` |
| `current_promotion` | `q52_currentPromotion` |
| `do_not_service` | `q57_doNotServiceList` |
| `additional_info` | `q37_additionalInfo` |
| `agent_id` | Retell API response |
| `conversation_flow_id` | Retell API response |

---

## Supabase

| Item | Value |
|---|---|
| URL | `https://hgheyqwnrcvwtgngqdnq.supabase.co` |
| Client config table | `hvac_standard_agent` |
| Call log table | `hvac_call_log` |

### `hvac_call_log` Fields (30+ — Retell-native extraction since 2026-04-04)

| Field | Type | Source | Notes |
|---|---|---|---|
| `call_id` | text | Retell | Dedup key — duplicates rejected |
| `agent_id` | text | Retell | FK to `hvac_standard_agent` |
| `company_name` | text | Supabase lookup | From client record |
| `call_tier` | text | Parse Lead Data | Default "Standard" |
| `caller_name` | text | Retell custom analysis | Full name as stated |
| `caller_phone` | text | Retell custom analysis | Falls back to `from_number` |
| `caller_address` | text | Retell custom analysis | Full service address |
| `service_requested` | text | Retell custom analysis | Short description |
| `job_type` | text | Retell custom analysis | repair, install, maintenance, quote, emergency, etc |
| `lead_score` | int | Retell custom analysis | 1–10 |
| `is_lead` | bool | n8n computed | lead_score >= 5 AND not spam/wrong_number |
| `urgency` | text | Retell custom analysis | emergency, high, medium, low |
| `retell_sentiment` | text | Retell system preset | "Positive", "Neutral", "Negative" (TEXT not int) |
| `vulnerable_occupant` | bool | Retell custom analysis | Elderly, children, medical equipment |
| `transfer_attempted` | bool | Retell custom analysis | True if live transfer initiated |
| `summary` | text | Retell system preset | call_summary — 2-3 sentence summary |
| `notes` | text | Retell custom analysis | Additional context |
| `duration_seconds` | int | Retell webhook | `Math.round(duration_ms / 1000)` |
| `from_number` | text | Retell webhook | Caller ID |
| `recording_url` | text | Retell webhook | S3 URL to recording |
| `public_log_url` | text | Retell webhook | Retell dashboard link |
| `disconnection_reason` | text | Retell webhook | user_hangup, agent_hangup, etc |
| `transcript` | text | Retell webhook | Full call transcript |
| `latency_p50_ms` | int | Retell webhook | e2e latency p50 |
| `call_cost_cents` | int | n8n computed | unit_price * duration / 60000 * 100 |
| `retell_summary` | text | Retell system preset | Same as summary (compatibility) |
| `call_successful` | bool | Retell system preset | Conversation completed naturally |
| `call_type` | text | Retell custom analysis | new_service, emergency, callback, etc |
| `is_hot_lead` | bool | Retell custom analysis | Wants service soon + gave contact |
| `transfer_success` | bool | Retell custom analysis | Transfer connected |
| `emergency` | bool | Retell custom analysis | Genuine HVAC emergency |
| `notification_type` | text | Retell custom analysis | Routing: emergency, hot_lead, etc |
| `language` | text | Retell custom analysis | en, es, other |
| `booking_attempted` | bool | Retell custom analysis | Always false for Standard |
| `booking_success` | bool | Retell custom analysis | Always false for Standard |
| `is_repeat_caller` | bool | n8n computed | from_number seen before |
| `repeat_call_count` | int | n8n computed | Count of prior calls |

### is_lead logic (n8n Extract Call Data node)
```javascript
const NON_LEAD_TYPES = ['spam', 'wrong_number'];
const is_lead = NON_LEAD_TYPES.includes(call_type) ? false : (lead_score >= 5);
```

### retell_sentiment — TEXT string, NOT integer
> **Breaking change from pre-enhancement:** Old system used integer `caller_sentiment`.
> New system stores Retell's native text in `retell_sentiment`: "Positive", "Neutral", "Negative".

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

### Retell Post-Call Analysis
| Item | Value |
|---|---|
| Model | `gpt-4.1-mini` (set on Retell agent) |
| Custom fields | 21 (all call data) |
| System presets | call_summary, call_successful, user_sentiment |
| webhook_events | call_analyzed only |

---

## Stripe (TEST MODE)

| Item | Value |
|---|---|
| Standard product | `prod_UC0hZtntx3VEg2` |
| Monthly price | `price_1TDckaECS71NQsk8DdNsWy1o` · $497/mo |
| Annual price | `price_1TDckiECS71NQsk8fqDio8pw` · $414/mo |
| Setup fee | `price_1TEKKrECS71NQsk8Mw3Z8CoC` · $1,499 |
| Founding discount | `FOUNDING-STANDARD` → `gzp8vnD7` ($1,499 off once) |
| Closer $250 off | `CLOSER-250` → `mGTTQZOw` |
| Closer $500 off | `CLOSER-500` → `GJiRoaMY` |
| Closer $750 off | `CLOSER-750` → `fUzLNIgz` |
| Closer $1000 off | `CLOSER-1000` → `3wraC3tQ` |

---

## SMS
- Wired but disabled: `SMS_ENABLED=false`
- Provider: Telnyx (awaiting AI evaluation approval — account active, $5 loaded)
- **Never Twilio**

---

## HubSpot Integration
- All call activity auto-logged as contact notes after each processed call
- Client contacts created at signup (Stripe), updated at onboarding (Jotform), active stage on go-live
- Pipeline: Lead → Demo Booked → Paid Client → Active
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
| `Stripe` | `price_standard_monthly` | $497/mo price ID |
| `Stripe` | `price_standard_annual` | $414/mo price ID |
| `Stripe` | `price_standard_setup` | $1,499 setup price ID |
| `GitHub` | `personal_access_token` | GitHub PAT |

---

---

# TEST SUITES

Three independent test suites. All must pass before any production change. Run order: E2E → Agent Simulator → Call Processor.

---

## TEST SUITE 1 — E2E Pipeline Test

**Script:** `python3 shared/e2e-test.py`
**Status: 98 assertions — Updated 2026-04-04 for Retell-native fields**
**Sub-skill:** `e2e-hvac-standard` (load for deep detail)

Tests the full provisioning pipeline: Jotform → n8n → Supabase → Retell → Call Processor.

| Phase | What's checked | Assertions |
|---|---|---|
| 1 | Jotform webhook accepted | HTTP 200 |
| 2 | n8n onboarding workflow completes | status = success (polls up to 45s) |
| 3 | Supabase `hvac_standard_agent` — all 40+ fields populated | 40+ field checks |
| 4 | Retell agent exists, published, correct voice/webhook/language | Agent health |
| 5 | Conversation flow — exactly 12 nodes, correct structure | Node count + IDs |
| 6 | Call processor — fake call with Retell post-call analysis payload, all 30+ fields verified | Row + 15 new field assertions |
| 7 | Stripe gate — SMS correctly skipped in test mode | Gate check |

Self-cleaning: test agent, flow, and Supabase row auto-deleted 5 min after run.

### When to run
- Before any n8n onboarding workflow change
- After any Retell conversation flow structural change
- Before going live with a new client
- After any Supabase schema change

### Key E2E IDs
| Resource | ID |
|---|---|
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` |
| Call processor workflow | `Kg576YtPM9yEacKn` |
| Cleanup workflow | `URbQPNQP26OIdYMo` |
| Jotform Standard form | `260795139953066` |

### Adding a new field to the pipeline
1. Parse Jotform Data node — add mapping
2. Build Retell Prompt extractedData — add field
3. Merge LLM & Agent Data node — add field
4. E2E test payload — add Jotform key + value
5. E2E test assertion — add check
6. Run test — verify N+1 passing
7. Update this skill + `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`

### E2E Gotchas
- Phase 2 fails with `exec status unknown` → n8n slow, increase polling attempts
- Phase 3 field null → wrong Jotform key in Parse node or test payload
- Phase 5 wrong node count → Build Retell Prompt node builds wrong number of nodes
- Phase 6 call not logged → call processor webhook path changed
- Cleanup doesn't fire → Cleanup workflow `URbQPNQP26OIdYMo` is paused

---

## TEST SUITE 2 — Agent Behaviour Simulator

**Script:** `python3 tools/openai-agent-simulator.py --group {group}`
**Status: 80/80 ✅ — All groups 100% — Verified 2026-04-03**
**Sub-skill:** `hvac-standard-agent-testing` (load for deep detail)

Tests Sophie's behaviour across 80 realistic caller scenarios using an LLM evaluator.
Operates on **TESTING agent only** — never MASTER.

| Group | Scenarios | Score | What it tests |
|---|---|---|---|
| `core_flow` | 15 | 15/15 ✅ | Standard service calls, lead capture, callbacks |
| `pricing_traps` | 8 | 8/8 ✅ | Pricing questions, Sophie must not quote fees |
| `personalities` | 15 | 15/15 ✅ | Chatty, abrupt, technical, distracted, angry callers |
| `boundary_safety` | 12 | 12/12 ✅ | Attempts to break Sophie out of role |
| `edge_cases` | 15 | 15/15 ✅ | Wrong number, out-of-area, spam, vendor, job applicant |
| `info_collection` | 15 | 15/15 ✅ | Address formats, phonetic numbers, WhatsApp, commercial |

### When to run
- After any prompt or node instruction change
- After any conversation flow structural change
- Before promoting TESTING → MASTER

### Promoting TESTING → MASTER
Only promote when:
1. All 6 simulator groups ≥ 95% on TESTING agent
2. E2E passes on TESTING agent
3. Then patch MASTER in place (never delete, never recreate)
4. Publish MASTER immediately after patch

### Agent Simulator Gotchas
- **Rate limits:** Never run more than 2 groups in parallel — hammers OpenAI RPM
- **Evaluator variance:** A single FAIL on an otherwise-passing scenario = run it twice in isolation before changing the prompt. Cost: ~$0.002.
- **Two failure types:** (a) Sophie does the wrong thing → fix prompt; (b) Sophie does the right thing, evaluator fails → fix `expectedBehaviour` in scenarios.json
- **Prompt length:** Global prompt must stay under ~5,000 chars. Beyond ~15k chars, instructions at the bottom are ignored by the model. Personality handling MUST be in the code node injection, not appended to global prompt.
- **callerPrompt quality:** If `expectedBehaviour` requires Sophie to handle an interruption/distraction, the `callerPrompt` must actually simulate it. Read the transcript before fixing Sophie.
- **Targeted runs first:** Always `--scenarios 18,21` before `--group personalities` — validates the fix fast before full run.

---

## TEST SUITE 3 — Call Processor Test

**Script:** `python3 tests/call-processor-test.py`
**Status: 20/20 ✅ — Verified 2026-04-04 (confirmed with fresh Groq quota)**
**Sub-skill:** `standard-call-processor-testing` (load for deep detail)

Tests the n8n call processor workflow in isolation, firing 20 fake post-call webhooks and asserting on the resulting `hvac_call_log` rows.

| Scenario range | What's covered |
|---|---|
| 1–5 | Core leads: repair, install, maintenance, follow-up, emergency |
| 6–10 | Edge cases: early hangup, wrong number, spam, out-of-area, live transfer |
| 11–15 | Lead scoring: commercial, pricing-only, phonetic phone, dedup, silent call |
| 16–20 | Field accuracy: sentiment, geocode, no-address, vendor, job applicant |

### When to run
- After any call processor n8n workflow change
- After any change to the Groq prompt or Parse Lead Data code
- After any `hvac_call_log` schema change
- Before go-live

### Running the test
```bash
python3 tests/call-processor-test.py
# Runs in 4 batches — ~8 minutes total
# 12s spacing between calls to respect Groq free-tier RPM limit
# Wait 60s after any 429 error, then resume
```

### Call Processor Gotchas
- **No LLM calls in call processor** — Groq/OpenAI removed. All extraction by Retell post_call_analysis.
- **`retell_sentiment` is TEXT** — "Positive"/"Neutral"/"Negative". Old `caller_sentiment` INTEGER deprecated.
- **`fetch()` not defined in n8n Code nodes** — split into Code (build body) + HTTP Request (fire)
- **IIFE expressions fail in n8n jsonBody** — put all logic in Code node, keep jsonBody as `$json.field` refs
- **SB_ANON key has RLS restrictions** — always use SB_SVC (service role) for test reads
- **Dedup via `call_id`** — same call_id resent = early exit, no second row
- **Fake webhooks must include `custom_analysis_data`** — n8n reads directly from this, not from transcript
- **is_lead computed in n8n** — `lead_score >= 5 AND call_type not in [spam, wrong_number]`

### Assertion calibration (Retell-native — deterministic extraction)
| Field | Groq behaviour | Correct assertion |
|---|---|---|
| `caller_address` | Full address as stated during call | Assert `present` (non-empty string) |
| `urgency` | One of: emergency, high, medium, low | Assert `in list` |
| `call_type` | One of 7 defined values | Assert `in list` |
| `retell_sentiment` | Capitalised text | Assert `present` and is string |
| `lead_score` | Integer 1-10 | Assert `>= 1` |

---

## Test Run Order & Go-Live Gate

```
Before any production change:
  1. python3 shared/e2e-test.py              → must be 75/75
  2. python3 tools/openai-agent-simulator.py → must be ≥ 95% per group
  3. python3 tests/call-processor-test.py    → must be 20/20

Before go-live:
  4. 3–5 real phone calls to +18129944371   → manual smoke test (Dan)
  5. Confirm hvac_call_log rows appear for real calls
  6. Unpause syntharra-ops-monitor on Railway
  7. Set SMS_ENABLED=true once Telnyx approved
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
