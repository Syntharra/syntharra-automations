# E2E Test — HVAC Standard Agent

## When to Use This Skill
Load this skill whenever:
- Running an E2E test on the Standard HVAC pipeline
- Debugging a failed E2E run
- Adding new fields to the pipeline (Jotform → Supabase → Retell)
- Checking that a recent n8n change didn't break onboarding
- Verifying a new client was provisioned correctly

---

## What the E2E Test Covers

The test validates the **complete Standard pipeline** end-to-end:

```
Jotform webhook → n8n onboarding → Supabase row → Retell agent + flow → Call processor → hvac_call_log
```

**75 assertions across 7 phases:**
- Phase 1: Jotform webhook accepted (HTTP 200)
- Phase 2: n8n onboarding workflow executed successfully
- Phase 3: Supabase — all 40+ fields populated correctly
- Phase 4: Retell agent exists, published, correct voice/webhook/language
- Phase 5: Conversation flow — 12 nodes, correct structure
- Phase 6: Call processor — fake call logged, scored, deduplicated
- Phase 7: Stripe gate behaviour in test mode

Self-cleaning: auto-deletes test agent, flow, and Supabase row after 5 minutes.

---

## How to Run

```bash
cd syntharra-automations
python3 shared/e2e-test.py
```

**Requirements:** Python 3, no extra packages (stdlib only — urllib, json, time).

**Expected output:**
```
RESULT: 75/75 passed  |  0 failed
✅ ALL SYSTEMS GO — Full pipeline verified
```

---

## Test Data

| Field | Value |
|---|---|
| Company | `Polar Peak HVAC {timestamp}` — unique per run |
| AI Name | `Max` |
| Phone | `+15125550199` |
| Email | `daniel@syntharra.com` |
| Timezone | `America/New_York` |
| Voice | Male → `retell-Nico` |

---

## Credentials (hardcoded in test file)

All credentials are embedded directly in `shared/e2e-test.py`.
Do not move them to vault — the test must run standalone.

| Key | Ends in | Used for |
|---|---|---|
| `N8N_KEY` | `NqU` | n8n API — execution polling |
| `RETELL_KEY` | `66445` | Retell — agent + flow verification |
| `SB_ANON` | `yL0` | Supabase reads |
| `SB_SVC` | `qsg` | Supabase deletes (cleanup) |

---

## Key IDs (never hardcode in test — always fetch dynamically)

| Resource | ID | Notes |
|---|---|---|
| Onboarding workflow | `4Hx7aRdzMl5N0uJP` | HVAC AI Receptionist - JotForm Onboarding |
| Call processor workflow | `Kg576YtPM9yEacKn` | HVAC Call Processor - Retell Webhook |
| Cleanup workflow | `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed Delete |
| Jotform Standard form | `260795139953066` | Standard onboarding form |
| Jotform webhook path | `/webhook/jotform-hvac-onboarding` | n8n endpoint |
| Call processor webhook | `/webhook/hvac-std-call-processor` | n8n endpoint |
| Cleanup webhook | `/webhook/e2e-test-cleanup` | n8n endpoint |

---

## Execution Polling Pattern

The test polls n8n for execution results instead of sleeping:

```python
for attempt in range(9):       # up to 45s
    time.sleep(5)
    _, execs = http(f".../executions?workflowId={WF_ID}&limit=3",
        headers={"X-N8N-API-KEY": N8N_KEY})
    candidates = [e for e in (execs.get('data') or [])
                  if e.get('status') in ('success','error','crashed')]
    if candidates:
        exec_status = candidates[0].get('status')
        break
```

This handles variable n8n execution times without brittle fixed sleeps.

---

## Supabase Fields Verified (Phase 3)

Every field in the table below is asserted in the test. If you add a new field to the pipeline, add it here and to the test.

| Column | Jotform Field | Test Value |
|---|---|---|
| `company_name` | q4 | `Polar Peak HVAC {ts}` |
| `owner_name` | q54 | `James Caldwell` |
| `client_email` | q5 | `daniel@syntharra.com` |
| `company_phone` | q6 | `+15125550199` |
| `website` | q7 | `www.polarpeak.com` |
| `years_in_business` | q8 | `8` |
| `timezone` | q34 | `America/New_York` |
| `agent_name` | q10 | `Max` |
| `custom_greeting` | q38 | contains `Max` |
| `services_offered` | q13 | comma-separated list |
| `brands_serviced` | q14 | comma-separated list |
| `service_area` | q16 | populated |
| `service_area_radius` | q40 | `40 miles` |
| `certifications` | q29 | comma-separated list |
| `emergency_service` | q20 | `Yes` |
| `emergency_phone` | q21 | `+15125550199` |
| `business_hours` | q17 | populated |
| `pricing_policy` | q42 | populated |
| `diagnostic_fee` | q41 | populated |
| `financing_available` | q25 | `Yes` |
| `warranty` | q26 | `Yes` |
| `payment_methods` | q45 | populated |
| `maintenance_plans` | q46 | populated |
| `membership_program` | q58 | `Peak Care Club` |
| `lead_contact_method` | q31 | `Both` |
| `lead_phone` | q32 | `+16316330713` |
| `lead_email` | q33 | `daniel@syntharra.com` |
| `notification_email_2` | q66 | `dispatcher@polarpeak.com` |
| `notification_email_3` | q67 | `salesmanager@polarpeak.com` |
| `notification_sms_2` | q64 | `+16316330714` |
| `notification_sms_3` | q65 | `+16316330715` |
| `transfer_phone` | q48 | `+15125550199` |
| `transfer_triggers` | q49 | populated |
| `google_review_rating` | q55 | `4.8` |
| `google_review_count` | q56 | `527` |
| `unique_selling_points` | q51 | populated |
| `current_promotion` | q52 | populated |
| `do_not_service` | q57 | populated |
| `additional_info` | q37 | populated |
| `agent_id` | Retell API | populated |
| `conversation_flow_id` | Retell API | populated |

---

## Retell Agent Assertions (Phase 4)

| Check | Expected |
|---|---|
| Agent exists | `agent_id` returned from Retell |
| Agent name | equals `TEST_AGENT` (`Max`) — AI receptionist name, not company |
| Webhook URL | `https://n8n.syntharra.com/webhook/retell-hvac-webhook` |
| Voice | `retell-Nico` (male) or `retell-Sloane` (female) |
| Language | `multi` |

---

## Conversation Flow Assertions (Phase 5)

| Check | Expected |
|---|---|
| Node count | **12** |
| flex_mode | `false` |
| start_speaker | `agent` |
| `node-greeting` | present |
| `node-leadcapture` | present |
| `node-verify-emergency` | present |
| `node-callback` | present |
| `node-spam-robocall` | present |
| Greeting contains agent name | `Max` |
| Global prompt contains company info | yes |
| Agent published | HTTP 200 from Retell publish endpoint |

---

## Call Processor Assertions (Phase 6)

Sends a fake Retell post-call webhook and verifies n8n processes it correctly.

| Check | Expected |
|---|---|
| Webhook accepted | HTTP 200 |
| `hvac_call_log` row created | yes |
| `caller_name` | `Daniel Blackmore` |
| `caller_phone` | `631-633-0713` |
| `service_requested` | not null/empty/Other |
| `lead_score` | >= 6 |
| `is_lead` | `true` |
| `summary` | populated |
| `company_name` | matches test company |
| Dedup — no duplicate on re-send | 1 row only |
| Call processor n8n execution | `success` |

---

## Stripe Gate Assertions (Phase 7)

| Mode | Check | Expected |
|---|---|---|
| TEST (default) | Twilio number NOT purchased | `twilio_number` null |
| TEST (default) | Onboarding email sent | workflow status `success` |
| LIVE | Twilio number purchased | `twilio_number` populated |

To run in LIVE mode: set `STRIPE_CUSTOMER_ID = 'cus_xxxxx'` at top of test file.

---

## Cleanup

The test fires the E2E cleanup webhook at the end. The cleanup workflow:
1. Waits 5 minutes (giving you time to manually inspect Supabase/Retell)
2. Deletes the Supabase row from `hvac_standard_agent`
3. Deletes the test Retell agent
4. Deletes the test conversation flow
5. Deletes the `hvac_call_log` test row

**You have 5 minutes after the test completes to inspect data before it's wiped.**

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 2 fails (exec status unknown) | n8n slow to start | Increase polling attempts (default: 9×5s = 45s) |
| Phase 3 field is null | Jotform field key wrong in test payload or Parse node | Check field key against Jotform form `260795139953066` |
| Phase 5 wrong node count | Template changed in n8n | Check Build Retell Prompt node — should build 12 nodes |
| Phase 6 call not logged | Call processor webhook path changed | Verify `/webhook/hvac-std-call-processor` is active |
| Cleanup doesn't fire | Cleanup workflow paused | Unpause workflow `URbQPNQP26OIdYMo` in n8n |

---

## Credential Access Rule
ALL Syntharra API keys are in Supabase `syntharra_vault`.
The E2E test embeds credentials directly for standalone operation — do not refactor to vault lookups.
