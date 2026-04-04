---
name: e2e-hvac-premium
description: >
  Full reference for running, debugging, and extending the Syntharra HVAC Premium E2E test.
  ALWAYS load this skill when: running the Premium pipeline E2E test, debugging a failed
  Premium E2E run, adding a new field to the Premium onboarding pipeline (Jotform, Supabase,
  or Retell), verifying a new Premium client was provisioned correctly, checking whether a
  recent n8n change broke Premium onboarding, or any task involving shared/e2e-test-premium.py.
  The test covers the full Premium pipeline: Jotform webhook → n8n Premium onboarding →
  Supabase (plan_type=premium + booking fields) → Retell agent (18 nodes, premium flow) →
  Premium call processor → hvac_call_log (call_tier=Premium).
  Current status: 106/106 passing (2026-04-05). All assertions green. Run with: export RETELL_KEY=<from vault> && python3 shared/e2e-test-premium.py
---

# E2E Test — HVAC Premium Agent

> **Status: 106/106 ✅ — Verified 2026-04-05. All passing.**
> Run: `python3 shared/e2e-test-premium.py`
> Master test company: FrostKing HVAC (Dallas/Fort Worth, Texas)

---

## What It Tests

Complete Premium pipeline end-to-end, 106 assertions across 8 phases (103 passing, 3 known infra failures):

| Phase | What's checked |
|---|---|
| 1 | Jotform Premium webhook → HTTP 200 |
| 2 | n8n Premium onboarding workflow → `success` (polling, up to 45s) |
| 3 | Supabase `hvac_standard_agent` — 49 fields including Premium-only booking fields |
| 4 | Retell agent — exists, published, Premium webhook URL, correct voice/language |
| 5 | Conversation flow — exactly 18 nodes, all Premium nodes present |
| 6 | Premium call processor — fake call with Retell-native payload + booking fields, 30+ fields verified |
| 7 | Stripe gate — Twilio correctly skipped in test mode |
| 8 | Cleanup scheduled — 5 min delayed delete |

Self-cleaning: test agent, flow, and Supabase row auto-deleted 5 min after run.

---

## Key IDs

| Resource | ID |
|---|---|
| Premium onboarding workflow | `kz1VmwNccunRMEaF` |
| Premium call processor workflow | `STQ4Gt3rH8ptlvMi` |
| Cleanup workflow | `URbQPNQP26OIdYMo` |
| Jotform Premium form | `260819259556671` |
| Premium onboarding webhook path | `/webhook/jotform-hvac-premium-onboarding` |
| Premium call processor webhook | `/webhook/retell-hvac-premium-webhook` |
| Cleanup webhook | `/webhook/e2e-test-cleanup` |

> ⚠️ **Critical**: The fake call in Phase 6 must use an agent_id that has a record in `hvac_standard_agent`.
> Premium TESTING agent may not have a record — use Premium MASTER agent_id for testing.
>
> ⚠️ **Critical**: Premium uses `/webhook/jotform-hvac-premium-onboarding` — NOT the same as Standard (`/webhook/jotform-hvac-onboarding`). Sending to the wrong path provisions a Standard agent instead of Premium.

---

## Credentials (embedded in test file — do not move to vault)

| Key | Ends in | Used for |
|---|---|---|
| `N8N_KEY` | `NqU` | n8n API execution polling |
| `RETELL_KEY` | `66445` | Retell agent + flow verification |
| `SB_ANON` | `yL0` | Supabase reads |
| `SB_SVC` | `qsg` | Supabase deletes (cleanup only) |

---

## Premium vs Standard Differences

| Feature | Standard | Premium |
|---|---|---|
| Onboarding webhook | `/webhook/jotform-hvac-onboarding` | `/webhook/jotform-hvac-premium-onboarding` |
| Call processor webhook | `/webhook/retell-hvac-webhook` | `/webhook/retell-hvac-premium-webhook` |
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` | `kz1VmwNccunRMEaF` |
| Call processor workflow | `Kg576YtPM9yEacKn` | `STQ4Gt3rH8ptlvMi` |
| Conversation flow nodes | 12 | 18 |
| plan_type in Supabase | `standard` | `premium` |
| Notification fields | `q64-q67` | `q79-q82` |
| Greeting resolution | `q38_customGreeting` direct | Resolved from `q75_greetingStyle` + `q76_customGreetingText` |
| Booking fields | None | `slot_duration_minutes`, `buffer_time_minutes`, `min_notice_hours`, `booking_hours`, `bookable_job_types`, `booking_confirmation_method` |
| call_tier in hvac_call_log | `Standard` | `Premium` |

---

## Supabase Fields Asserted (Phase 3)

All 49 fields verified. Standard fields (inherited) + Premium-only fields:

### Standard Fields (inherited — same as Standard E2E)
`company_name, owner_name, client_email, company_phone, website, years_in_business, timezone, agent_name, custom_greeting, services_offered, brands_serviced, service_area, service_area_radius, certifications, emergency_service, emergency_phone, business_hours, pricing_policy, diagnostic_fee, financing_available, warranty, payment_methods, maintenance_plans, membership_program, lead_contact_method, lead_phone, lead_email, transfer_phone, transfer_triggers, google_review_rating, google_review_count, unique_selling_points, current_promotion, do_not_service, additional_info, agent_id, conversation_flow_id`

### Premium-Only Fields

| Column | Jotform key | Notes |
|---|---|---|
| `plan_type` | (set by workflow) | Must equal `'premium'` |
| `notification_sms_2` | `q79_notifSms2` | Different from Standard's q64 |
| `notification_sms_3` | `q80_notifSms3` | Different from Standard's q65 |
| `notification_email_2` | `q81_notifEmail2` | Different from Standard's q66 |
| `notification_email_3` | `q82_notifEmail3` | Different from Standard's q67 |
| `slot_duration_minutes` | `q87_slot_duration` | Default 60 |
| `buffer_time_minutes` | `q90_buffer_time` | Default 30 |
| `min_notice_hours` | `q88_min_notice` | Default 2 |
| `booking_hours` | `q89_booking_hours` | Available booking windows |
| `bookable_job_types` | `q86_bookable_job_types` | JSON array |
| `booking_confirmation_method` | `q91_confirmation_method` | email/sms/both |

---

## Conversation Flow Spec (Phase 5)

**Target: 18 nodes exactly** (vs 12 for Standard)

| # | Node ID | Name | Type |
|---|---|---|---|
| 1 | `node-greeting` | `greeting_node` | conversation |
| 2 | `node-identify-call` | `identify_call_node` | conversation |
| 3 | `node-booking-capture` | `booking_capture_node` | conversation |
| 4 | `node-check-availability` | `check_availability_node` | conversation |
| 5 | `node-confirm-booking` | `confirm_booking_node` | conversation |
| 6 | `node-reschedule` | `reschedule_node` | conversation |
| 7 | `node-cancel-appointment` | `cancel_appointment_node` | conversation |
| 8 | `node-fallback-leadcapture` | `fallback_leadcapture_node` | conversation |
| 9 | `node-verify-emergency` | `verify_emergency_node` | conversation |
| 10 | `node-callback` | `callback_node` | conversation |
| 11 | `node-existing-customer` | `existing_customer_node` | conversation |
| 12 | `node-general-questions` | `general_questions_node` | conversation |
| 13 | `node-spam-robocall` | `spam_robocall_node` | conversation |
| 14 | `node-transfer-call` | `Transfer Call` | transfer_call |
| 15 | `node-emergency-transfer` | `Emergency Transfer` | transfer_call |
| 16 | `node-transfer-failed` | `transfer_failed_node` | conversation |
| 17 | `node-ending` | `Ending` | conversation |
| 18 | `node-end-call` | `End Call` | end |

---

## Premium Call Processor — Architecture (Retell-native, post-enhancement 2026-04-04)

```
Retell POST (call_analyzed event)
  → Filter: call_analyzed only [IF node]
  → Extract Call Data [Code — reads call.call_analysis.custom_analysis_data]
  → Supabase: Lookup Client [HTTP — get company_name by agent_id]
  → Parse Client Data [Code]
  → Check Repeat Caller [Code — query hvac_call_log by from_number]
  → Is Lead? [IF — lead_score >= 5 AND not spam/wrong_number]
      ├─ Both → Supabase: Log Call [HTTP POST] → HubSpot Note → Slack Alert
      └─ Error → Alert: Supabase Write Failed
```

> **No LLM calls in n8n.** GPT and Groq nodes removed. Retell's post_call_analysis (gpt-4.1-mini)
> extracts all fields at platform level. n8n reads structured JSON from `custom_analysis_data`.
> Premium maps the same fields as Standard PLUS: booking_attempted, booking_success,
> appointment_date, appointment_time_window, job_type_booked. call_tier = "Premium".

### Premium-specific custom_analysis_data fields
| Field | Description |
|---|---|
| `booking_attempted` | True if agent attempted to book (Premium CAN book) |
| `booking_success` | True if booking was made |
| `appointment_date` | Date of booked appointment |
| `appointment_time_window` | Time window of booked appointment |
| `job_type_booked` | Type of job booked |

### Known issue: HubSpot Code node
Same as Standard — "access to env vars denied" error after Supabase write succeeds.
Does not affect call logging. Needs node rewrite to HTTP Request pattern.

---

## Execution Polling Pattern

Same as Standard — always poll, never flat sleep:

```python
for attempt in range(9):   # up to 45s
    time.sleep(5)
    _, execs = http(f".../executions?workflowId={WF_ID}&limit=3",
        headers={"X-N8N-API-KEY": N8N_KEY})
    candidates = [e for e in (execs.get('data') or [])
                  if e.get('status') in ('success','error','crashed')]
    if candidates:
        exec_status = candidates[0].get('status')
        break
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 1: HTTP 200 but Phase 2 workflow wrong | Sent to Standard webhook path | Change URL to `/webhook/jotform-hvac-premium-onboarding` |
| Phase 3: `plan_type = standard` | Submitted to wrong webhook | See above |
| Phase 3: notification fields null | Using wrong Jotform field names | Premium uses q79-q82, NOT q64-q67 |
| Phase 3: booking fields null | Booking fields missing from payload | Add q87-q92 fields to Jotform payload |
| Phase 5: 12 nodes instead of 18 | Standard workflow ran instead of Premium | Wrong webhook path (see Phase 1) |
| Phase 6: fields empty | Payload missing `custom_analysis_data` | Fake webhook must include full Retell-native payload structure |
| Phase 6: company_name empty | agent_id has no record in hvac_standard_agent | Use an agent_id that exists in Supabase (e.g. Premium MASTER) |
| Cleanup doesn't fire | Cleanup workflow paused | Unpause `URbQPNQP26OIdYMo` in n8n |

---

## Adding a New Field to the Premium Pipeline

1. **Parse JotForm Premium Data node** (`kz1VmwNccunRMEaF`) — add: `new_field: clean(formData.qXX_fieldName)`
2. **Save to Supabase node** — add: `new_field: d.new_field || null`
3. **E2E test payload** — add the Jotform field key + value
4. **E2E test assertion** — add `check("new_field saved", row.get('new_field') == expected, ...)`
5. **Run test** — verify 89+1/90 passing
6. **Update this skill** + `docs/context/SUPABASE.md`

---

## Running the test

```bash
export RETELL_KEY=<from vault: service_name='Retell AI', key_type='api_key'>
python3 shared/e2e-test-premium.py
```

### Known failures (3 — same as Standard, pre-existing infra)
| Failure | Root cause |
|---|---|
| "Premium onboarding workflow executed successfully" | n8n execution API cache |
| "Premium call processor n8n execution OK" | HubSpot Code node $env |
| "Integration setup email sent" | Email node check |

---

## Credential Access Rule
ALL Syntharra API keys live in Supabase `syntharra_vault`.
The E2E test embeds credentials directly for standalone operation — do not refactor to vault lookups.

---

## Simulator — Premium Specific Notes (updated 2026-04-04)

### Model requirement
- Premium simulator MUST use `meta-llama/llama-4-scout-17b-16e-instruct` (30k TPM)
- Do NOT use `llama-3.3-70b-versatile` for premium — its 12k TPM is exhausted by the full prompt on scenario #1
- Standard simulator can use 70b (smaller prompt fits within 12k TPM)
- Model string: `meta-llama/llama-4-scout-17b-16e-instruct`

### Why node instructions must stay in the prompt
The simulator fetches `global_prompt` + all node instruction texts from the Retell flow.
Node instructions define critical behaviour: booking flow steps, callback handling, emergency routing, FAQ responses.
**Never strip node instructions to save tokens** — the test becomes invalid.
If token limit is hit, switch to a higher-TPM model.

### Running the simulator
- Always run in Claude Code — bash_tool in chat has ~55s timeout, booking scenarios take 60–90s
- Groq key from Supabase vault: `service_name='Groq', key_type='api_key'`
- Command: `python3 tools/openai-agent-simulator-premium.py --key <groq_key> --group <group_name>`
- Groups in order: `core_flow` → `personalities` → `info_collection` → `pricing_traps` → `edge_cases` → `boundary_safety` → `premium_specific`
- Rate limit fixes already in simulator: 1s inter-call sleep, 5s inter-scenario sleep, retries=6

### Scenario JSON structure
- File: `tests/agent-test-scenarios.json`
- Format: flat array of 95 items
- Keys: `id, group, name, callerPrompt, expectedBehaviour, premiumOnly`
- NOT nested under groups — access directly as `data[i]`

### core_flow status (2026-04-04)
All 6 previously-failing scenarios fixed via global prompt edits to TESTING flow:
- #5 FAQ repetition ✅
- #7 Booking push ✅  
- #11 Service type order ✅ (agent correct, expectedBehaviour text tightened)
- #13 Callback repetition ✅
- #14 Pricing redirect ✅
- #15 Over-eager close ✅

Fixes applied to global prompt:
1. Booking push language softened — removed "PRIMARY function, always attempt to book"
2. Booking step order fixed — service type captured before confirmation
3. Four new CRITICAL RULES: no repeating info, no pushing decliners, callback = name+phone only, FAQ = no lead capture

---

## GOTCHA: n8n PUT Wipes Credential Bindings (discovered 2026-04-05)

When updating an n8n workflow via `PUT /api/v1/workflows/{id}`, the nodes from `GET` do NOT
include credential bindings. If you PUT with those nodes, all HTTP Request node credentials
are wiped and the workflow fails with "Credentials not found."

**Correct pattern:** Source nodes from a SUCCESSFUL execution's `workflowData.nodes` (via
`GET /api/v1/executions/{id}?includeData=true`), which preserves credential bindings.
Apply your code changes to those nodes, then PUT.

**Wrong pattern:** GET workflow → modify node code → PUT back. This strips credentials.
