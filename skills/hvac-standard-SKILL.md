---
name: hvac-standard
description: >
  Master reference for the entire HVAC Standard product — Retell agent, onboarding pipeline,
  call processor, Supabase, n8n workflows, and all testing. Load this skill for ANY task
  touching the Standard product: agent prompt changes, onboarding debugging, call log issues,
  Stripe/billing, E2E testing, call processor testing, or agent behaviour testing.
  This skill is the single source of truth. The three specialist skills
  (e2e-hvac-standard, standard-call-processor-testing, hvac-standard-agent-testing) contain
  deeper detail for their specific domains — load them when you need to run or debug tests.
  This skill covers: what the system does, how it is built, all IDs and endpoints, test status,
  and known issues. Do not load all four at once — this skill alone is sufficient for most tasks.
---

> **Last verified: 2026-04-04**
> **System status: PRE-LAUNCH — Stripe TEST MODE — all testing complete**
> **Go-live gate: 3–5 live smoke calls, then unpause ops-monitor and set SMS_ENABLED=true**

---

# HVAC Standard — Master Reference

---

## 1. What This Product Is

An AI phone receptionist for HVAC contractors, built on Retell AI.
- Answers calls 24/7 as a named agent (e.g. "Sophie")
- Qualifies leads, captures caller details, scores urgency
- Handles emergencies, existing customers, wrong numbers, spam
- Routes genuine emergencies to a live transfer number
- Posts a lead notification to the client (email + SMS) within seconds of call end
- Logs every call to Supabase and HubSpot

**Pricing:** $497/mo (monthly) or $414/mo (annual) + $1,499 setup fee
**Plan name in DB:** `Standard`

---

## 2. Retell Agent

| Item | Value |
|---|---|
| MASTER Agent ID | `agent_4afbfdb3fcb1ba9569353af28d` |
| TESTING Agent ID | `agent_731f6f4d59b749a0aa11c26929` |
| Phone Number | `+1 (812) 994-4371` |
| Transfer Number | `+1 (856) 363-0633` |
| MASTER Conversation Flow | `conversation_flow_34d169608460` |
| TESTING Conversation Flow | `conversation_flow_5b98b76c8ff4` |
| Demo Agent (Female/Sophie) | `agent_2723c07c83f65c71afd06e1d50` |
| Demo Agent (Male/Jake) | `agent_b9d169e5290c609a8734e0bb45` |

### Hard rules — non-negotiable
- **NEVER delete or recreate a Retell agent** — agent_id is the FK across Retell, Supabase, call processor, and phone number
- **ALWAYS publish after any agent or flow update:** `POST https://api.retellai.com/publish-agent/{agent_id}`
- **All changes go to TESTING first** — verify at ≥95% pass rate before patching MASTER
- Demo agents must always stay published

### Conversation Flow — 12 nodes (exact)

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

If a flow has anything other than exactly 12 nodes, something is wrong.

### Prompt architecture
- Global prompt: lean (~4,000 chars) — handles identity, rules, edge cases
- Node-level instructions: specific behaviour per call type
- Dynamic variables injected at runtime: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- Code node (`node-caller-style`) detects caller style (chatty/technical/distressed) and injects `caller_style_note` into leadcapture node top
- Use commas not dashes in prompt text for better LLM readability

---

## 3. Onboarding Pipeline

**Trigger:** Client submits Jotform Standard form → webhook fires → n8n provisions everything

```
Jotform submission
  → POST /webhook/jotform-hvac-onboarding
  → n8n: HVAC AI Receptionist - JotForm Onboarding (4Hx7aRdzMl5N0uJP)
      → Parse form data
      → Create Supabase record (hvac_standard_agent)
      → Clone Retell agent from MASTER template
      → Build 12-node conversation flow with client data injected
      → Publish agent
      → Wire phone number
      → Send "You're Live" email to client
      → Notify onboarding@syntharra.com
      → HubSpot: update contact + create deal at Active stage
```

| Item | Value |
|---|---|
| Jotform Form ID | `260795139953066` |
| Jotform webhook path | `/webhook/jotform-hvac-onboarding` |
| Onboarding workflow ID | `4Hx7aRdzMl5N0uJP` |
| Supabase table | `hvac_standard_agent` |

> Always use Jotform REST API directly — never MCP connector (broken)

### Key Jotform → Supabase field mappings

| Supabase column | Jotform key |
|---|---|
| `company_name` | `q4_hvacCompany` |
| `owner_name` | `q54_ownerName` |
| `client_email` | `q5_emailAddress` |
| `company_phone` | `q6_mainCompany` |
| `agent_name` | `q10_aiAgent10` |
| `services_offered` | `q13_servicesOffered` |
| `service_area` | `q16_primaryService` |
| `emergency_service` | `q20_247Emergency` |
| `emergency_phone` | `q21_emergencyAfterhours` |
| `business_hours` | `q17_businessHours` |
| `lead_phone` | `q32_leadNotification` |
| `lead_email` | `q33_leadNotification33` |
| `transfer_phone` | `q48_transferPhone` |
| `transfer_triggers` | `q49_transferTriggers` |
| `timezone` | `q34_timezone` |

Full 40-field mapping: `skills/e2e-hvac-standard-SKILL.md`

---

## 4. Call Processor

**Trigger:** Every call end → Retell fires `call_analyzed` webhook → n8n processes

```
POST /webhook/retell-hvac-webhook
  → Filter: call_analyzed events only
  → Extract Call Data
  → Supabase Lookup Client (by agent_id)
  → Parse Client Data
  → Check Repeat Caller (dedup gate — rejects duplicate call_id)
  → Build Groq Request [Code node]
  → Groq: Analyze Transcript [HTTP → api.groq.com]
  → Parse Lead Data [Code — normalises all fields]
  → Is Lead? [IF]
      ├─ TRUE  → SMS alert + Gmail lead email + Supabase: Log Call + HubSpot Note
      └─ FALSE → Log Non-Lead + Supabase: Log Call + HubSpot Note
```

| Item | Value |
|---|---|
| Workflow ID | `Kg576YtPM9yEacKn` |
| Webhook path | `/webhook/retell-hvac-webhook` |
| AI model | Groq `llama-3.3-70b-versatile` |
| Groq credential (n8n) | `UfljdfOxkfTm76LE` |
| Output table | `hvac_call_log` |

> ⚠️ **NEVER use OpenAI credential `1uzBYwyR7Q7bdkZe`** — expired key, caused silent total failure.
> Groq replaced OpenAI entirely on 2026-04-03.

### Fields written to hvac_call_log (18 fields)

| Field | Type | Source |
|---|---|---|
| `call_id` | text | Retell webhook — dedup key |
| `agent_id` | text | Retell webhook |
| `company_name` | text | Supabase lookup |
| `call_tier` | text | `plan_type` field, default "Standard" |
| `caller_name` | text | Groq |
| `caller_phone` | text | Groq (falls back to `from_number`) |
| `caller_address` | text | Groq (empty string if not given) |
| `service_requested` | text | Groq |
| `job_type` | text | Groq → normalised enum |
| `lead_score` | int | Groq (1–10) |
| `is_lead` | bool | Groq + override rules |
| `urgency` | text | Groq: Low / Medium / High / Emergency |
| `caller_sentiment` | int | Groq → integer: 2=Positive 3=Neutral 4=Frustrated 5=Angry |
| `vulnerable_occupant` | bool | Groq |
| `transfer_attempted` | bool | Groq |
| `summary` | text | Groq |
| `notes` | text | Groq |
| `duration_seconds` | int | Retell webhook |

### is_lead override logic
```
is_lead = False  if job_type in [Wrong Number, Spam, Vendor, Job Application]
is_lead = False  if job_type == General Enquiry AND lead_score < 6
is_lead = Groq value  otherwise
```

### job_type enum
`Repair` · `Installation` · `Maintenance` · `Emergency` · `General Enquiry` ·
`Wrong Number` · `Spam` · `Vendor` · `Job Application` · `Other`

### caller_sentiment — stored as INTEGER
`2` Positive · `3` Neutral · `4` Frustrated · `5` Angry
Never write string values — column type is INT, will throw 22P02.

---

## 5. Supabase Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | All client config — Standard AND Premium (merged, no separate premium table) |
| `hvac_call_log` | All call records — Standard AND Premium (single table, `call_tier` differentiates) |

> `hvac_premium_agent` and `hvac_premium_call_log` do NOT exist — do not reference them.

### hvac_standard_agent key columns
`agent_id, company_name, agent_name, plan_type, client_email, timezone, lead_phone, lead_email,
services_offered, service_area, business_hours, emergency_service, emergency_phone,
stripe_customer_id, subscription_id, notification_email_2/3, notification_sms_2/3,
transfer_phone, transfer_triggers, conversation_flow_id`

### hvac_call_log key columns
`call_id, agent_id, company_name, call_tier, caller_name, caller_phone, caller_address,
service_requested, job_type, urgency, lead_score, is_lead, caller_sentiment,
vulnerable_occupant, transfer_attempted, transfer_success, summary, notes,
geocode_status, geocode_formatted, duration_seconds, created_at`

---

## 6. n8n Workflows (Standard)

| Workflow | ID | Purpose |
|---|---|---|
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | Jotform → Supabase + Retell provision |
| HVAC Call Processor | `Kg576YtPM9yEacKn` | Post-call webhook → Groq → Supabase + HubSpot |
| Weekly Lead Report | `iLPb6ByiytisqUJC` | Sunday 6pm per-timezone client report |
| Usage Alert Monitor | `Wa3pHRMwSjbZHqMC` | 80% + 100% minute usage warnings |
| Monthly Minutes Calc | `z1DNTjvTDAkExsX8` | Overage billing per client |
| Send Welcome Email | `lXqt5anbJgsAMP7O` | Manual resend trigger |

**n8n rules:**
- PUT payload accepts only: `name`, `nodes`, `connections`, `settings.executionOrder` — nothing else
- Always publish after edits
- `fetch()` is NOT available in n8n Code nodes — use Code (builds body) + HTTP Request (fires call) pattern
- `$http` not available on this n8n version — same workaround

---

## 7. Stripe (TEST MODE)

| Item | Value |
|---|---|
| Standard product | `prod_UC0hZtntx3VEg2` |
| Monthly price | `price_1TDckaECS71NQsk8DdNsWy1o` ($497/mo) |
| Annual price | `price_1TDckiECS71NQsk8fqDio8pw` ($414/mo) |
| Setup fee price | `price_1TEKKrECS71NQsk8Mw3Z8CoC` ($1,499) |
| Stripe webhook | `ydzfhitWiF5wNzEy` |
| Founding discount | `FOUNDING-STANDARD` → `gzp8vnD7` ($1,499 off) |
| Closer $250–$1000 off | `CLOSER-250/500/750/1000` coupons in vault |

---

## 8. Email Flow

Three emails per Standard client:
1. **Stripe welcome** — on checkout.session.completed (automated)
2. **"You're Live"** — after agent provisioned (automated via onboarding workflow)
3. **Weekly lead report** — every Sunday, per-timezone (automated)

Internal notifications:
- New onboarding → `onboarding@syntharra.com`
- Lead alert (call processor) → `admin@syntharra.com`
- All: SMTP2GO credential `"SMTP2GO - Syntharra"`, light theme (#F7F7FB bg, #6C63FF accent)

---

## 9. HubSpot CRM

All client and lead activity flows to HubSpot automatically:
- Website lead → `Lead` stage
- Stripe payment → `Paid Client` stage
- Jotform onboarding → `Active` stage
- Post-call → note logged to client contact

Pipeline: "Syntharra Sales" → Lead → Demo Booked → Paid Client → Active
Full reference: `skills/syntharra-hubspot-SKILL.md`

---

## 10. SMS

- SMS wired but disabled: `SMS_ENABLED=false`
- Provider: Telnyx (awaiting AI evaluation approval — account active, $5 loaded)
- **Never Twilio**
- Enable at go-live: set `SMS_ENABLED=true` in Railway env once Telnyx approved

---

## 11. Credentials & Vault

All API keys in Supabase `syntharra_vault` — never hardcode. Query by `service_name` + `key_type`.

```
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault
  ?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value
Headers: apikey + Authorization: Bearer {SERVICE_ROLE_KEY}
```

Key vault entries:
| service_name | key_type |
|---|---|
| `Retell AI` | `api_key` |
| `Groq` | `api_key` |
| `n8n Railway` | `api_key`, `instance_url` |
| `Supabase` | `service_role_key` |
| `Stripe` | `price_standard_monthly`, `price_standard_annual`, `price_standard_setup` |
| `Jotform` | `api_key`, `form_id_standard` |
| `GitHub` | `personal_access_token` |
| `Railway` | `api_token` |

---

## 12. Testing — Complete Status

### 12.1 Agent Behaviour Testing — 80/80 ✅

Tests Sophie's conversation behaviour across all scenario types.
**Tool:** `tools/openai-agent-simulator.py`
**Specialist skill:** `skills/hvac-standard-agent-testing-SKILL.md` (load for prompt changes or re-testing)

| Group | Scenarios | Score | Status |
|---|---|---|---|
| core_flow | 15 | 15/15 | ✅ 100% |
| pricing_traps | 8 | 8/8 | ✅ 100% |
| personalities | 15 | 15/15 | ✅ 100% |
| boundary_safety | 12 | 12/12 | ✅ 100% |
| edge_cases | 15 | 15/15 | ✅ 100% |
| info_collection | 15 | 15/15 | ✅ 100% |
| **TOTAL** | **80** | **80/80** | ✅ **100%** |

Last verified: 2026-04-03

**When to re-run:** Any time the global prompt or a conversation flow node is edited.
**Rule:** Never promote TESTING → MASTER until agent behaviour tests pass at ≥95%.

### 12.2 E2E Pipeline Test — 75/75 ✅

Tests the full onboarding pipeline from Jotform submission to Retell agent live.
**Script:** `python3 shared/e2e-test.py`
**Specialist skill:** `skills/e2e-hvac-standard-SKILL.md` (load when running or debugging)

| Phase | What's tested | Assertions |
|---|---|---|
| 1 | Jotform webhook → HTTP 200 | 1 |
| 2 | n8n onboarding workflow completes | 1 |
| 3 | Supabase record — all 40+ fields populated | 40+ |
| 4 | Retell agent exists, published, correct config | 8 |
| 5 | Conversation flow — exactly 12 nodes | 12 |
| 6 | Call processor — fake call logged to hvac_call_log | 8 |
| 7 | Stripe gate — SMS/Twilio correctly skipped in test mode | 1 |

Last verified: 2026-04-02. Self-cleaning — test agent + row auto-deleted after 5 mins.

**When to re-run:** Any time onboarding workflow, Supabase schema, or Retell provisioning logic changes.

### 12.3 Call Processor Test — 20/20 ✅

Tests Groq transcript analysis, field extraction, lead scoring, and Supabase writes.
**Script:** `python3 tests/call-processor-test.py`
**Specialist skill:** `skills/standard-call-processor-testing-SKILL.md` (load when running or debugging)

| Scenario group | Count | Status |
|---|---|---|
| Core leads (repair, install, maintenance, emergency, follow-up) | 5 | ✅ |
| Edge cases (hang-up, wrong number, spam, out-of-area, live transfer) | 5 | ✅ |
| Lead scoring (commercial, pricing-only, phonetic number, dedup, short call) | 5 | ✅ |
| Field accuracy (sentiment, geocode, no-address, vendor, job applicant) | 5 | ✅ |

Last verified: 2026-04-04. Script spaces calls 12s apart to respect Groq free-tier RPM.

**When to re-run:** Any time the call processor workflow, Groq prompt, Parse Lead Data node, or Supabase schema changes.

### Key assertion calibration notes (call processor)
- `caller_address` — assert `present`, not `contains city-name` (Groq stores street line only)
- `urgency` for no-heat without gas — "High" is correct, not "Emergency" (Emergency = gas/fire/safety only)
- `geocode_status` — async, do not assert in timed tests (may not populate within 25s)
- `is_lead` for no-address vague calls — correctly `False`, do not assert True

---

## 13. Testing Protocol — How to Make Changes Safely

```
1. Load current TESTING agent config
2. Make change on TESTING agent/flow only
3. Run targeted simulator scenarios (--scenarios X,Y,Z) — verify fix
4. Run full group (--group core_flow etc.) — confirm no regressions
5. If call processor changed: run python3 tests/call-processor-test.py
6. If onboarding pipeline changed: run python3 shared/e2e-test.py
7. Once all pass at ≥95%: patch MASTER agent/flow with exact same change
8. Publish MASTER
9. Update this skill
```

**TESTING agent IDs (safe to modify):**
- Agent: `agent_731f6f4d59b749a0aa11c26929`
- Flow: `conversation_flow_5b98b76c8ff4`

**MASTER agent IDs (only patch after tests pass):**
- Agent: `agent_4afbfdb3fcb1ba9569353af28d`
- Flow: `conversation_flow_34d169608460`

---

## 14. Go-Live Checklist

- [x] Agent behaviour testing — 80/80 ✅
- [x] E2E pipeline testing — 75/75 ✅
- [x] Call processor testing — 20/20 ✅
- [x] MASTER flow promoted with lean 4,053-char prompt ✅
- [x] HubSpot CRM integration wired to all workflows ✅
- [ ] Live smoke calls — 3–5 real calls to +18129944371 (Dan manual)
- [ ] Unpause syntharra-ops-monitor on Railway
- [ ] Set `SMS_ENABLED=true` once Telnyx approved
- [ ] Get Slack webhook URL from Dan → wire to 8 n8n workflows

---

## 15. Known Issues / Watch Points

| Issue | Status | Notes |
|---|---|---|
| SMS disabled | Pending Telnyx approval | Set SMS_ENABLED=true in Railway env to enable |
| Slack not wired | Pending webhook URL from Dan | 8 workflows ready to receive it |
| geocode_status async | By design | Populated after row write — not visible in immediate reads |
| Groq free-tier RPM ~30/min | Production unaffected | Only matters during bulk test runs |
| OpenAI credential `1uzBYwyR7Q7bdkZe` | Dead — do not use | Expired key, caused silent call processor failure |

---

## 16. Architecture Decisions

| Decision | Chose | Reason |
|---|---|---|
| Node-based conversation flow | 12-node Retell flow | Deterministic routing — more reliable than freeform; each path independently testable |
| Caller style detection | Code node → inject variable at leadcapture top | Long global prompt ignores style rules at bottom; code node injects at active context position |
| Separate TESTING agents | Always keep TESTING separate from MASTER | Zero risk to live callers during prompt iteration |
| Groq for transcript analysis | Groq `llama-3.3-70b-versatile` | OpenAI credential died; Groq faster + cheaper, 3× retry gives production resilience |
| Single Supabase table for Standard + Premium | `hvac_standard_agent` + `hvac_call_log` | Simplifies queries; `plan_type` + `call_tier` fields differentiate; no join complexity |
| HubSpot as CRM | HubSpot | Admin dashboard deprecated; HubSpot gives sales pipeline + contact history without building it |

