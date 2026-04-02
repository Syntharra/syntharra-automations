---
name: e2e-hvac-standard
description: >
  Full reference for running, debugging, and extending the Syntharra HVAC Standard E2E test.
  ALWAYS load this skill when: running the Standard pipeline E2E test, debugging a failed E2E run,
  adding a new field to the onboarding pipeline (Jotform, Supabase, or Retell), verifying a new
  client was provisioned correctly, checking whether a recent n8n change broke onboarding, or any
  task involving shared/e2e-test.py. The test covers the full pipeline: Jotform webhook → n8n
  onboarding → Supabase → Retell agent + conversation flow → call processor → hvac_call_log.
  Current status: 75/75 passing. Run with: python3 shared/e2e-test.py
---

# E2E Test — HVAC Standard Agent

> **Status: 75/75 ✅ — Verified 2026-04-02**
> Run: `python3 shared/e2e-test.py`
> Full docs: `docs/e2e-test-reference.md`
> Master template: `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`

---

## What It Tests

Complete Standard pipeline end-to-end, 75 assertions across 7 phases:

| Phase | What's checked |
|---|---|
| 1 | Jotform webhook → HTTP 200 |
| 2 | n8n onboarding workflow → `success` (polling, up to 45s) |
| 3 | Supabase `hvac_standard_agent` — 40+ fields all populated |
| 4 | Retell agent — exists, published, correct voice/webhook/language |
| 5 | Conversation flow — exactly 12 nodes, correct structure |
| 6 | Call processor — fake call logged + scored in `hvac_call_log` |
| 7 | Stripe gate — Twilio correctly skipped in test mode |

Self-cleaning: test agent, flow, and Supabase row auto-deleted 5 min after run.

---

## Key IDs

| Resource | ID |
|---|---|
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` |
| Call processor workflow | `Kg576YtPM9yEacKn` |
| Cleanup workflow | `URbQPNQP26OIdYMo` |
| Jotform Standard form | `260795139953066` |
| Jotform webhook path | `/webhook/jotform-hvac-onboarding` |
| Call processor webhook | `/webhook/hvac-std-call-processor` |
| Cleanup webhook | `/webhook/e2e-test-cleanup` |

---

## Credentials (embedded in test file — do not move to vault)

| Key | Ends in | Used for |
|---|---|---|
| `N8N_KEY` | `NqU` | n8n API execution polling |
| `RETELL_KEY` | `66445` | Retell agent + flow verification |
| `SB_ANON` | `yL0` | Supabase reads |
| `SB_SVC` | `qsg` | Supabase deletes (cleanup only) |

---

## Supabase Fields Asserted (Phase 3)

All 40+ fields below are verified in the test. If you add a field to the pipeline, add it here and to the test payload + assertion.

### Jotform → Column mapping

| Column | Jotform key |
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

## Conversation Flow Spec (Phase 5)

**Target: 12 nodes exactly**

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

---

## Execution Polling Pattern

**Always poll — never flat sleep** for n8n execution checks:

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

## Adding a New Field to the Pipeline

When adding a new Jotform field that must reach Supabase:

1. **Parse JotForm Data node** (n8n `4Hx7aRdzMl5N0uJP`) — add mapping: `new_field: clean(formData.qXX_fieldName)`
2. **Build Retell Prompt extractedData** — add: `new_field: data.new_field || null`
3. **Merge LLM & Agent Data node** — add: `new_field: ed.new_field || null`
4. **E2E test payload** — add the Jotform field key + value
5. **E2E test assertion** — add `check("new_field saved", row.get('new_field') == expected_value, ...)`
6. **Run test** — verify 75+1/76 passing
7. **Update this skill** + `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 2 fails (`exec status unknown`) | n8n slow | Increase polling attempts (9×5s = 45s default) |
| Phase 3 field null | Wrong Jotform key in Parse node or test payload | Check key against Jotform form `260795139953066` |
| Phase 5 wrong node count | Template changed in n8n | Check Build Retell Prompt node — must build 12 nodes |
| Phase 6 call not logged | Call processor webhook path changed | Verify `/webhook/hvac-std-call-processor` active |
| Cleanup doesn't fire | Cleanup workflow paused | Unpause `URbQPNQP26OIdYMo` in n8n |

---

## Credential Access Rule
ALL Syntharra API keys live in Supabase `syntharra_vault`.
The E2E test embeds credentials directly for standalone operation — do not refactor to vault lookups.
