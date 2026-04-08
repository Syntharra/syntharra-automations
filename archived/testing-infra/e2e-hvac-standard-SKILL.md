---
name: e2e-hvac-standard
description: >
  Full reference for running, debugging, and extending the Syntharra HVAC Standard E2E test.
  ALWAYS load this skill when: running the Standard pipeline E2E test, debugging a failed E2E run,
  adding a new field to the onboarding pipeline (Jotform, Supabase, or Retell), verifying a new
  client was provisioned correctly, checking whether a recent n8n change broke onboarding, or any
  task involving shared/e2e-test.py.
  Current status: 93/93 passing (2026-04-05). Subagent component architecture. Run with: python3 shared/e2e-test.py
---

# E2E Test — HVAC Standard Pipeline

> **Status: 93/93 ✅ — Verified 2026-04-05. All passing.**
> Run: 
> No env vars needed — Retell key embedded as fallback.

---

## What It Tests

Complete Standard pipeline end-to-end, 93 assertions across 7 phases:

| Phase | What's checked |
|---|---|
| 1 | Jotform webhook → HTTP 200 |
| 2 | n8n onboarding workflow →  (polling, up to 45s) |
| 3 | Supabase  — 40+ fields all populated |
| 4 | Retell agent — exists, published, correct voice/webhook/language |
| 5 | Conversation flow — 15+ nodes (subagent components architecture), key nodes verified by name |
| 6 | Call processor — fake call with full Retell post-call analysis payload, 17 fields verified |
| 7 | Stripe gate — Twilio correctly skipped in test mode |

Self-cleaning: test agent, flow, and Supabase row auto-deleted 5 min after run.

---

## Architecture: Subagent Components (v2 — 2026-04-05)

The Standard flow now uses **20 nodes** (was 15). Most conversation nodes have been converted to
 type nodes that reference shared components from the Syntharra component library.
This means node count is ≥15 and may grow as new components are added. The E2E test asserts
 not exact equality.

**Current node inventory (20 nodes):**

| Node | Type | Component |
|---|---|---|
| greeting_node | conversation | — |
| identify_call_node | subagent | Syntharra - identify_call |
| nonemergency_leadcapture_node | subagent | Syntharra - fallback_leadcapture |
| verify_emergency_node | subagent | Syntharra - verify_emergency |
| callback_node | subagent | Syntharra - callback |
| existing_customer_node | subagent | Syntharra - existing_customer |
| general_questions_node | subagent | Syntharra - general_questions |
| spam_robocall_node | subagent | Syntharra - spam_robocall |
| Transfer Call | transfer_call | — |
| transfer_failed_node | subagent | Syntharra - transfer_failed |
| Ending | subagent | Syntharra - ending |
| End Call | end | — |
| emergency_fallback_node | subagent | — |
| spanish_routing_node | subagent | — |
| call_style_detector | subagent | Syntharra - call_style_detector |
| validate_phone | subagent | Syntharra - validate_phone |
| Emergency Detection | subagent | — |
| Spam Detection | conversation | — |
| Transfer Request | conversation | — |
| Extract Caller Data | extract_dynamic_variables | — |

**Key changes from v1:**
- Nodes converted to subagent type reference reusable component library
- Component updates propagate to all agents using that component
- emergency_fallback_node and spanish_routing_node added (new)
- call_style_detector and validate_phone added (new)
- Node count check uses  not 

---

## Key IDs

| Resource | ID |
|---|---|
| Onboarding workflow |  |
| Call processor workflow |  |
| Cleanup workflow |  |
| Jotform Standard form |  |
| Jotform webhook path |  |
| Call processor webhook |  |
| Cleanup webhook |  |
| TESTING agent |  |
| TESTING flow |  |
| MASTER agent |  |
| MASTER flow |  |

---

## Test Data — Canonical Values

| Field | Value |
|---|---|
| Company name |  |
| Website |  |
| Agent name |  |
| Test email |  |
| Test phone |  |

### RULE: Never use real company branding in test data.

---

## Credentials (embedded in test file)

| Key | Ends in | Used for |
|---|---|---|
|  |  | n8n API execution polling |
|  |  | Retell agent + flow verification (embedded fallback) |
|  |  | Supabase reads |
|  |  | Supabase deletes (cleanup only) |

---

## Conversation Flow Assertions (Phase 5)

The E2E test checks for key node names rather than exact count:

- greeting_node, identify_call_node, verify_emergency_node, callback_node
- spam_robocall_node, call_style_detector, validate_phone
- Transfer Call (transfer_call type), Emergency Transfer (transfer_call type)
- Node count >= 15

---

## Supabase Fields Asserted (Phase 3)

All 40+ fields verified. See full column mapping in .

### Fields NOT yet in E2E assertions (need payload + assertion extension)
-  (q72)
-  (q68)
-  (q69)

---

## Running the Test



---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 4+5 all 401 | Wrong RETELL_KEY | Verify ends in  |
| Phase 2 fails | n8n slow | Increase polling attempts |
| Phase 5 wrong node count | Template changed | Check flow matches component architecture |
| Phase 6 call not logged | Webhook path wrong | Verify  active |

---

## Adding a New Field to the Pipeline

1. **Parse JotForm Data node** — add mapping
2. **Build Retell Prompt extractedData** — add field
3. **E2E test payload** — add Jotform field key + value
4. **E2E test assertion** — add  in Phase 3
5. **Run test** — verify passing
6. **Update this skill**
