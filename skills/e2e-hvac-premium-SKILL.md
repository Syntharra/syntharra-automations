---
name: e2e-hvac-premium
description: >
  Full reference for running, debugging, and extending the Syntharra HVAC Premium E2E test.
  ALWAYS load this skill when: running the Premium pipeline E2E test, debugging a failed
  Premium E2E run, adding a new field to the Premium onboarding pipeline, verifying a new
  Premium client was provisioned correctly, or any task involving shared/e2e-test-premium.py.
  Current status: 106/106 passing (2026-04-05). Subagent component architecture. Run with: python3 shared/e2e-test-premium.py
---

# E2E Test — HVAC Premium Pipeline

> **Status: 106/106 ✅ — Verified 2026-04-05. All passing.**
> Run: 
> No env vars needed — Retell key embedded as fallback.

---

## What It Tests

Complete Premium pipeline end-to-end, 106 assertions across 8 phases:

| Phase | What's checked |
|---|---|
| 1 | Jotform Premium webhook → HTTP 200 |
| 2 | n8n Premium onboarding workflow →  (polling, up to 45s) |
| 3 | Supabase  — 49 fields including Premium-only booking fields |
| 4 | Retell agent — exists, published, Premium webhook URL, correct voice/language |
| 5 | Conversation flow — 20+ nodes (subagent components architecture), key nodes verified by name |
| 6 | Premium call processor — fake call with Retell-native payload + booking fields, 30+ fields verified |
| 7 | Stripe gate — Twilio correctly skipped in test mode |
| 8 | Cleanup scheduled — 5 min delayed delete |

Self-cleaning: test agent, flow, and Supabase row auto-deleted 5 min after run.

---

## Architecture: Subagent Components (v2 — 2026-04-05)

The Premium flow now uses **26 nodes** (was 20). Most conversation nodes converted to 
type nodes referencing shared components from the Syntharra component library.

**Current node inventory (26 nodes):**

| Node | Type | Component |
|---|---|---|
| greeting_node | conversation | — |
| identify_call_node | subagent | Syntharra - identify_call |
| booking_capture_node | subagent | Syntharra - booking_capture |
| check_availability_node | subagent | — |
| confirm_booking_node | subagent | — |
| reschedule_node | subagent | — |
| cancel_appointment_node | subagent | — |
| fallback_leadcapture_node | subagent | Syntharra - fallback_leadcapture |
| verify_emergency_node | subagent | Syntharra - verify_emergency |
| callback_node | subagent | Syntharra - callback |
| existing_customer_node | subagent | Syntharra - existing_customer |
| general_questions_node | subagent | Syntharra - general_questions |
| spam_robocall_node | subagent | Syntharra - spam_robocall |
| Transfer Call | transfer_call | — |
| Emergency Transfer | transfer_call | — |
| transfer_failed_node | subagent | Syntharra - transfer_failed |
| Ending | subagent | Syntharra - ending |
| End Call | end | — |
| call_style_detector | subagent | Syntharra - call_style_detector |
| validate_phone | subagent | Syntharra - validate_phone |
| Emergency Detection | subagent | — |
| Spam Detection | conversation | — |
| Transfer Request | conversation | — |
| Extract Caller Data | extract_dynamic_variables | — |
| emergency_fallback_node | subagent | — |
| spanish_routing_node | subagent | — |

**Premium-only nodes (not in Standard):**
- booking_capture_node, check_availability_node, confirm_booking_node
- reschedule_node, cancel_appointment_node
- Emergency Transfer (separate from Transfer Call)

**Key changes from v1:**
- Nodes converted to subagent type reference reusable component library
- emergency_fallback_node and spanish_routing_node added
- call_style_detector and validate_phone added
- Node count check uses  not 

**Premium tool calls (4 tools via n8n dispatch):**
- check_availability: action, date, time_window
- create_booking: action, date, time_window, caller_name, caller_phone, caller_address, job_type [+optional: caller_email, notes, urgency]
- reschedule_booking: action, new_date, new_time_window, caller_name, original_date [+optional: caller_phone]
- cancel_booking: action, caller_name, appointment_date

---

## Key IDs

| Resource | ID |
|---|---|
| Premium onboarding workflow |  |
| Premium call processor workflow |  |
| Cleanup workflow |  |
| Jotform Premium form |  |
| Premium onboarding webhook |  |
| Premium call processor webhook |  |
| TESTING agent |  |
| TESTING flow |  |
| MASTER agent |  |

---

## Premium vs Standard Differences

| Feature | Standard | Premium |
|---|---|---|
| Onboarding webhook |  |  |
| Call processor webhook |  |  |
| Flow nodes | 20 (subagent v2) | 26 (subagent v2) |
| plan_type in Supabase |  |  |
| Booking fields | None | slot_duration, buffer_time, min_notice, booking_hours, bookable_job_types, booking_confirmation_method |
| call_tier in hvac_call_log |  |  |
| Tool calls | 0 | 4 (check_availability, create_booking, reschedule_booking, cancel_booking) |

---

## Supabase Premium-Only Fields

| Column | Jotform key |
|---|---|
| plan_type | (set by workflow) |
| slot_duration_minutes | q87_slot_duration |
| buffer_time_minutes | q90_buffer_time |
| min_notice_hours | q88_min_notice |
| booking_hours | q89_booking_hours |
| bookable_job_types | q86_bookable_job_types |
| booking_confirmation_method | q91_confirmation_method |

---

## Premium Call Processor — Retell-native architecture

No LLM calls in n8n. Retell's post_call_analysis (gpt-4.1-mini) extracts all fields at platform level.
Premium maps same fields as Standard PLUS: booking_attempted, booking_success, appointment_date,
appointment_time_window, job_type_booked. call_tier = "Premium".

---

## Running the test



---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 1 OK but Phase 3 plan_type=standard | Sent to Standard webhook | Use  |
| Phase 3 booking fields null | Missing q87-q92 from payload | Add booking fields |
| Phase 5 wrong node count | Template changed | Check flow matches component architecture |
| Phase 6 booking fields empty | Missing custom_analysis_data | Fake webhook must include full Retell payload |

---

## Simulator Notes

- Premium simulator uses  (30k TPM) — do NOT use 70b
- Simulator now fetches subagent component instructions + edge routing (updated 2026-04-05)
- Groups: core_flow → personalities → info_collection → pricing_traps → edge_cases → boundary_safety → premium_specific
- 95 total scenarios, 15 are premium_specific (premiumOnly: true)

---

## GOTCHA: n8n PUT Wipes Credential Bindings

When updating n8n workflow via PUT, nodes from GET do NOT include credential bindings.
Source nodes from a SUCCESSFUL execution's workflowData.nodes instead.
