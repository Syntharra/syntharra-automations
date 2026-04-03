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
  Current status: 89/89 passing. Run with: python3 shared/e2e-test-premium.py
---

# E2E Test — HVAC Premium Agent

> **Status: 89/89 ✅ — Verified 2026-04-02**
> Run: `python3 shared/e2e-test-premium.py`
> Master test company: FrostKing HVAC (Dallas/Fort Worth, Texas)

---

## What It Tests

Complete Premium pipeline end-to-end, 89 assertions across 8 phases:

| Phase | What's checked |
|---|---|
| 1 | Jotform Premium webhook → HTTP 200 |
| 2 | n8n Premium onboarding workflow → `success` (polling, up to 45s) |
| 3 | Supabase `hvac_standard_agent` — 49 fields including Premium-only booking fields |
| 4 | Retell agent — exists, published, Premium webhook URL, correct voice/language |
| 5 | Conversation flow — exactly 18 nodes, all Premium nodes present |
| 6 | Premium call processor — fake call logged + scored in `hvac_call_log` |
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

## Premium Call Processor — Architecture Notes

The Premium call processor (`STQ4Gt3rH8ptlvMi`) was rebuilt from the Standard base on 2026-04-02 to fix a pre-existing bug where `n8n-nodes-base.filter` caused silent crashes before any node ran. Key differences from original:

- **Filter node**: `n8n-nodes-base.if` (replaced broken `n8n-nodes-base.filter`)
- **GPT prompt**: Premium-specific with booking fields, returns NESTED JSON with section headers (`CALLER INFORMATION`, `CALL CLASSIFICATION`, `BOOKING DATA`, `LEAD QUALIFICATION`, `ADDITIONAL`)
- **Parse Lead Data**: Enhanced Standard code that flattens nested GPT response using section header keys
- **Log Call**: Sets `call_tier: 'Premium'` + includes `booking_attempted`, `booking_success`, `appointment_date`, `appointment_time`, `job_type_booked`, `is_repeat_caller`
- **SMS node**: Stub (Telnyx disabled) — no `$vars` references
- **Email node**: Stub — no Gmail credential (uses SMTP2GO pattern)

### Parse Lead Data — Premium-Specific Code

The GPT returns nested JSON. Parse Lead Data flattens it:

```javascript
const ci = leadData['CALLER INFORMATION'] || {};
const cc = leadData['CALL CLASSIFICATION'] || {};
const lq = leadData['LEAD QUALIFICATION'] || {};
const ad = leadData['ADDITIONAL'] || {};
const score = lq.lead_score || leadData.lead_score || 0;
return {
  ...clientData, ...leadData,
  caller_name: ci.caller_name || leadData.caller_name || '',
  caller_phone: ci.caller_phone || leadData.caller_phone || '',
  service_requested: cc.service_requested || leadData.service_requested || '',
  summary: ad.summary || lq.summary || leadData.summary || '',
  lead_score: score,
  is_lead: score >= 6 || lq.is_lead || leadData.is_lead || false
};
```

> ⚠️ **Code length limit**: Parse Lead Data code must stay under ~1100 chars. The n8n instance on Railway has a JS compilation limit. Exceeding it causes silent workflow-level crashes with empty runData. Keep additions terse.

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
| Phase 6: exec=error, empty runData | Code node JS compilation crash | Parse Lead Data code too long (>1100 chars) |
| Phase 6: score=0, fields empty | GPT returned nested JSON, not flattened | Check Parse Lead Data has section-header flattener |
| Phase 6: workflow never ran | Filter node type wrong | Must be `n8n-nodes-base.if`, not `n8n-nodes-base.filter` |
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

