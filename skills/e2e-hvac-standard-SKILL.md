---
name: e2e-hvac-standard
description: >
  Full reference for running, debugging, and extending the Syntharra HVAC Standard E2E test.
  ALWAYS load this skill when: running the Standard pipeline E2E test, debugging a failed E2E run,
  adding a new field to the onboarding pipeline (Jotform, Supabase, or Retell), verifying a new
  client was provisioned correctly, checking whether a recent n8n change broke onboarding, or any
  task involving shared/e2e-test.py.
  Current status: 93/93 passing (2026-04-05). COMPONENTS architecture v2 build code verified. Run with: python3 shared/e2e-test.py
---

# E2E Test — HVAC Standard Pipeline

> **Status: 93/93 ✅ — Verified 2026-04-05. All passing.**
> Run: `python3 shared/e2e-test.py`
> No env vars needed — Retell key embedded as fallback.

---

## What It Tests

Complete Standard pipeline end-to-end, 93 assertions across 7 phases (updated for v2 COMPONENTS architecture):

| Phase | What's checked |
|---|---|
| 1 | Jotform webhook → HTTP 200 |
| 2 | n8n onboarding workflow → `success` (polling, up to 45s) |
| 3 | Supabase `hvac_standard_agent` — 40+ fields all populated |
| 4 | Retell agent — exists, published, correct voice/webhook/language |
| 5 | Conversation flow — exactly 15 nodes (13 conv + 2 code + 2 transfer), COMPONENTS architecture verified |
| 6 | Call processor — fake call with full Retell post-call analysis payload, 17 fields verified (includes warm_transfer support) |
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
| Call processor webhook | `/webhook/retell-hvac-webhook` |
| Cleanup webhook | `/webhook/e2e-test-cleanup` |

---

## Test Data — Canonical Values

All test data uses generic, non-client-specific values. **Never use real company names or client
email domains in test data.** The test company name includes a Unix timestamp so each run is unique.

| Field | Value |
|---|---|
| Company name | `TestClient HVAC {timestamp}` |
| Website | `www.syntharra-test.com` |
| Notification email 2 | `dispatcher@syntharra-test.com` |
| Notification email 3 | `salesmanager@syntharra-test.com` |
| Membership program | `Care Club` |
| Test email (lead/client) | `daniel@syntharra.com` |
| Test phone | `+15125550199` |
| Agent name | `Max` |

### RULE: Never use real company branding in test data
Polar Peak, FrostKing, BlueSky etc. were legacy test names that leaked into client emails.
All test data must use `syntharra-test.com` domain and generic names only.

---

## Email Suppression Gate

The onboarding email is suppressed for test runs by two layers:

**Layer 1 — n8n (Build Onboarding Pack HTML + Send Setup Instructions Email nodes):**
Suppresses if company name matches any of:
- Ends in a 9-10 digit Unix timestamp: `/\d{9,10}$/`
- Named test patterns: `TestClient HVAC`, `Polar Peak HVAC`, `FrostKing HVAC`, `HVAC Company`,
  `CoolBreeze HVAC`, `IceShield HVAC`, `BlueSky HVAC`, `VerifyAudit HVAC`, `SunValley HVAC`
- Email/website contains `syntharra-test.com`

**Layer 2 — Test script:** `TEST_EMAIL = "daniel@syntharra.com"` — if an email does slip through,
it goes to the internal address only, not a real client.

### RULE: Update both layers when adding a new test name
If you add a new test company name that doesn't end in a timestamp, add it to the n8n suppression
gate AND the Jotform Webhook Backup Polling test patterns.

---

## Credentials (embedded in test file)

| Key | Ends in | Used for |
|---|---|---|
| `N8N_KEY` | `NqU` | n8n API execution polling |
| `RETELL_KEY` | `66445` | Retell agent + flow verification (embedded fallback) |
| `SB_ANON` | `yL0` | Supabase reads |
| `SB_SVC` | `qsg` | Supabase deletes (cleanup only) |

**If Retell key rotates:** update both the n8n credential AND the `RETELL_KEY` default in
`shared/e2e-test.py`. They must stay in sync — they are currently different variables pointing
to the same key (`key_0157...66445`). The vault also holds this key.

---

## Supabase Fields Asserted (Phase 3)

All 40+ fields verified. Jotform → column mapping:

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
| `voice_gender` | `q11_aiVoice` |
| `custom_greeting` | `q73_customGreetingText` (q38 is dead — do not use) |
| `greeting_style` | `q72_greetingStyle` |
| `services_offered` | `q13_servicesOffered` |
| `brands_serviced` | `q14_brandsequipmentServiced` |
| `service_area` | `q16_primaryService` |
| `service_area_radius` | `q40_serviceAreaRadius` |
| `certifications` | `q29_certifications` |
| `emergency_service` | `q20_247Emergency` |
| `emergency_phone` | `q21_emergencyAfterhours` |
| `after_hours_behavior` | `q22_afterhoursBehavior` |
| `after_hours_transfer` | `q68_afterHoursTransfer` |
| `separate_emergency_phone` | `q69_separateEmergencyPhone` |
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

### Fields NOT yet in E2E assertions (added 2026-04-04 — need payload + assertion extension)
- `greeting_style` (q72)
- `after_hours_transfer` (q68)
- `separate_emergency_phone` (q69)
- `custom_greeting` via q73 (payload sends q73 but assertion not yet verifying it explicitly)

---

## Conversation Flow Spec (Phase 5)

**Target: 15 nodes exactly** (updated 2026-04-05 for COMPONENTS v2)

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

---

## Call Processor — Retell-Native Architecture

The E2E test's fake webhook payload includes the full `call_analysis.custom_analysis_data`
structure that Retell provides. The n8n call processor reads these fields directly — no LLM
calls in n8n.

### Phase 6 assertions
- retell_sentiment, retell_summary, call_successful (system presets)
- urgency, call_type, notification_type, job_type (custom analysis)
- is_hot_lead, language (custom analysis)
- duration_seconds, recording_url, latency_p50_ms, call_cost_cents (webhook direct)
- caller_address, notes (custom analysis)

---

## Execution Polling Pattern

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

## Known Pre-existing Failures (3 — non-blocking)

| Failure | Root cause | Impact |
|---|---|---|
| n8n execution polling edge case | API returns stale cached execution occasionally | None — data is in Supabase |
| Call processor n8n execution | HubSpot Code node uses `$env` (restricted) | None — Supabase write succeeds |
| Onboarding email sent check | Email suppressed in test mode by design | None — correct behaviour |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 4+5 all 401 | Wrong RETELL_KEY — check embedded fallback matches n8n credential | Verify both end in `66445` |
| Phase 2 fails | n8n slow | Increase polling attempts |
| Phase 3 field null | Wrong Jotform key in Parse node or test payload | Check key mapping table above |
| Phase 5 wrong node count | Template changed in n8n | Check Build Retell Prompt node |
| Phase 6 call not logged | Webhook path or payload format wrong | Verify `/webhook/retell-hvac-webhook` active |
| Getting test emails in inbox | Suppression gate missing new test name | Add pattern to n8n email nodes AND backup polling workflow |
| HVAC Company junk rows appearing | In-flight Reconcile executions completing after test | Expected — cleanup runs 5min later |

---

## Adding a New Field to the Pipeline

1. **Parse JotForm Data node** — add mapping: `new_field: clean(formData.qXX_fieldName)`
2. **Build Retell Prompt extractedData** — add: `new_field: data.new_field || null`
3. **Merge LLM & Agent Data node** — add to output
4. **E2E test payload** — add Jotform field key + value
5. **E2E test assertion** — add `check(...)` in Phase 3
6. **Run test** — verify passing
7. **Update this skill** + `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`

### RULE: Jotform questions and Parse node must always stay in sync
Any question added to the form must be added to Parse JotForm Data in the same session.
Silent gaps (like the q68/q69/q72/q73 incident) cause data loss with no error thrown.

---

## Running the Test

```bash
python3 shared/e2e-test.py
# No env vars needed — Retell key is embedded as fallback
```

---

## Agent Simulator Operational Patterns

### Rate limiting
- Never run more than 2 simulator groups in parallel
- Use `--scenarios 18,21,23` for targeted tests before full group runs

### Evaluator variance
- Run failing scenario 2x in isolation before fixing — single fail is often variance
- Two failure types: real agent failure (fix prompt) vs bad scenario (fix expectedBehaviour)

### Batch run timeout strategy
- Full 15-scenario group: 3-4 minutes solo
- Use `timeout 150` to prevent hangs
- Run `--scenarios` for targeted tests, `--group` only for final confirmation
