# Syntharra Full-Stack E2E Test Skill

## Purpose
This skill tells Claude exactly how to build, run, extend, and interpret a **complete end-to-end test** of the entire Syntharra platform — every workflow, every email, every Supabase table, every Retell agent, every Jotform field. Use this skill whenever the user asks to run, update, or extend the E2E test.

The canonical test script lives at:
`syntharra-automations/shared/e2e-test.py`

---

## Architecture Overview

| Layer | System | Role |
|---|---|---|
| Intake | Jotform (Standard `260795139953066` / Premium `260819259556671`) | Client onboarding form |
| Orchestration | n8n (Railway: `https://n8n.syntharra.com`) | All automation workflows |
| AI Voice | Retell AI | Agent creation, conversation flow, call handling |
| Database | Supabase (`hgheyqwnrcvwtgngqdnq.supabase.co`) | All client/call/billing data |
| Payments | Stripe (TEST MODE) | Checkout, subscriptions, invoices |
| Email | SMTP2GO via n8n | All outbound emails |
| Telephony | Retell + Telnyx | Inbound calls, transfers, SMS |
| Monitoring | Ops Monitor (Railway) | Health checks, alerts |
| Admin | syntharra-admin (Railway) | Internal dashboard |

---

## E2E Test Structure

The test runs in **8 phases** in sequence:

```
[1] Jotform Submission (ALL fields)
[2] n8n Onboarding Workflow Execution
[3] Supabase — ALL Fields Verified
[4] Retell Agent Created & Published
[5] Retell Conversation Flow Validated
[6] Call Processor — Fake Call Test
[7] Email Delivery Verification
[8] Cleanup — 5 Min Delayed (via n8n webhook)
```

---

## Phase 1: Jotform Submission

### Standard Form (`260795139953066`)
Webhook: `POST https://n8n.syntharra.com/webhook/jotform-hvac-onboarding`

**Every field that MUST be submitted:**

| Field Key | Value | Maps To (Supabase) |
|---|---|---|
| `q4_hvacCompany` | `"Polar Peak HVAC {TS}"` | `company_name` |
| `q54_ownerName` | `"James Caldwell"` | `owner_name` |
| `q6_mainCompany` | `"+15125550199"` | `company_phone` |
| `q5_emailAddress` | `TEST_EMAIL` | `client_email` |
| `q7_companyWebsite` | `"www.polarpeak.com"` | `website` |
| `q8_yearsIn` | `"8"` | `years_in_business` |
| `q34_timezone` | `"America/New_York"` | `timezone` |
| `q13_servicesOffered` | Array of services | `services_offered` |
| `q14_brandsequipmentServiced` | Array of brands | `brands_serviced` |
| `q16_primaryService` | Service area description | `service_area` |
| `q40_serviceAreaRadius` | `"40 miles"` | `service_area_radius` |
| `q29_certifications` | Array | `certifications` |
| `q28_licensedAnd` | `"Yes"` | `licensed_insured` |
| `q10_aiAgent10` | `"Max"` | `agent_name` |
| `q11_aiVoice` | `"Male"` | `voice_gender` |
| `q38_customGreeting` | Greeting string | `custom_greeting` |
| `q39_companyTagline` | Tagline | `company_tagline` |
| `q17_businessHours` | Hours string | `business_hours` |
| `q18_typicalResponse` | Response time | `response_time` |
| `q20_247Emergency` | `"Yes"` | `emergency_service` |
| `q21_emergencyAfterhours` | Phone | `emergency_phone` |
| `q22_afterhoursBehavior` | Behavior string | `after_hours_behavior` |
| `q42_pricingPolicy` | Policy string | `pricing_policy` |
| `q41_diagnosticFee` | Fee string | `diagnostic_fee` |
| `q43_standardFees` | Fees string | `standard_fees` |
| `q24_freeEstimates` | `"Yes"` | `free_estimates` |
| `q25_financingAvailable` | `"Yes"` | `financing_available` |
| `q44_financingDetails` | Details | `financing_details` |
| `q26_serviceWarranties` | `"Yes"` | `warranty` |
| `q27_warrantyDetails` | Details | `warranty_details` |
| `q45_paymentMethods` | Array | `payment_methods` |
| `q46_maintenancePlans` | Plan description | `maintenance_plans` |
| `q58_membershipProgramName` | `"Peak Care Club"` | `membership_program` |
| `q31_leadContact` | `"Both"` | `lead_contact_method` |
| `q32_leadNotification` | Phone | `lead_phone` |
| `q33_leadNotification33` | Email | `lead_email` |
| `q59_notifEmail2` | `"dispatcher@polarpeak.com"` | `notification_email_2` |
| `q60_notifEmail3` | `"salesmanager@polarpeak.com"` | `notification_email_3` |
| `q61_notifSms2` | Phone | `notification_sms_2` |
| `q62_notifSms3` | Phone | `notification_sms_3` |
| `q48_transferPhone` | Phone | `transfer_phone` |
| `q49_transferTriggers` | Array | `transfer_triggers` |
| `q50_transferBehavior` | Behavior | `transfer_behavior` |
| `q57_doNotServiceList` | List | `do_not_service` |
| `q55_googleReviewRating` | `"4.8"` | `google_review_rating` |
| `q56_googleReviewCount` | `"527"` | `google_review_count` |
| `q51_uniqueSellingPoints` | USPs | `unique_selling_points` |
| `q52_currentPromotion` | Promo | `current_promotion` |
| `q53_seasonalServices` | Seasonal | `seasonal_services` |
| `q37_additionalInfo` | Additional info | `additional_info` |

**Test mode indicator:** Leave `stripe_customer_id` empty → Stripe gate skips Twilio purchase.
**Live mode:** Set `stripe_customer_id = "cus_xxxxx"` → Twilio number is purchased.

### Premium Form (`260819259556671`)
Additional fields on top of standard:
- `crm_platform`, `crm_api_key` → `crm_platform`, `crm_status`
- `calendar_platform`, `calendar_token` → `calendar_platform`, `calendar_status`
- All above standard fields apply

---

## Phase 2: n8n Workflow Execution

### All Active Workflows

| ID | Name | Critical | Triggered By |
|---|---|---|---|
| `4Hx7aRdzMl5N0uJP` | HVAC Standard Onboarding | ✅ | Jotform webhook |
| `kz1VmwNccunRMEaF` | HVAC Premium Onboarding | ✅ | Jotform webhook |
| `xKD3ny6kfHL0HHXq` | Stripe Workflow | ✅ | `checkout.session.completed` |
| `Kg576YtPM9yEacKn` | HVAC Standard Call Processor | ✅ | Retell `call_analyzed` webhook |
| `STQ4Gt3rH8ptlvMi` | HVAC Premium Call Processor | ✅ | Retell `call_analyzed` webhook |
| `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher | ✅ | Premium call processor |
| `z1DNTjvTDAkExsX8` | Monthly Minutes Calculator | ✅ | Schedule (monthly) |
| `Wa3pHRMwSjbZHqMC` | Usage Alert Monitor | ✅ | Schedule (every hour) |
| `iLPb6ByiytisqUJC` | HVAC Weekly Lead Report | ⬜ | Schedule (weekly) |
| `44WfbVmJ7Zihcwgs` | Nightly GitHub Backup | ⬜ | Schedule (2am) |
| `13cOIXxvj83NfDqQ` | Publish Retell Agent | ⬜ | Called by onboarding |
| `Ex90zUMSEWwVk4Wv` | HVAC Scenario Test Runner v4 | ⬜ | Manual |
| `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed | ⬜ | E2E test script |
| `AU8DD5r6i6SlYFnb` | Auto-Enable MCP on All Workflows | ⬜ | Schedule (6h) |

**Onboarding execution check:**
```python
_, execs = http("https://n8n.syntharra.com/api/v1/executions?workflowId=4Hx7aRdzMl5N0uJP&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
latest = (execs.get('data') or [{}])[0]
assert latest.get('status') == 'success'
```

---

## Phase 3: Supabase Verification

### Tables & Expected State After Test

| Table | Expected After Standard Test |
|---|---|
| `hvac_standard_agent` | 1 new row, ALL fields populated |
| `hvac_premium_agent` | (Premium test only) 1 new row |
| `hvac_call_log` | 1 new row per fake call sent |
| `hvac_premium_call_log` | (Premium test only) |
| `stripe_payment_data` | 1 row if stripe_customer_id present |
| `client_subscriptions` | 1 row after full onboarding with billing |
| `billing_cycles` | Created by monthly calculator |
| `overage_charges` | Created when minutes exceeded |
| `call_processor_dlq` | Should be empty (no DLQ items) |
| `website_leads` | Separate — written by demo form |

### Supabase Query Pattern
```python
SB_ANON = "eyJhbGci..."  # anon key
SB_SVC  = "eyJhbGci..."  # service role key (for deletes)

def sb(path, method="GET", body=None, service=False):
    key = SB_SVC if service else SB_ANON
    _, data = http(f"{SUPABASE}/rest/v1/{path}", method, body,
        {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "return=representation"})
    return data if isinstance(data, list) else []
```

### ALL hvac_standard_agent fields to assert non-null:
`company_name`, `owner_name`, `company_phone`, `client_email`, `website`, `years_in_business`,
`timezone`, `agent_name`, `voice_gender`, `custom_greeting`, `company_tagline`, `services_offered`,
`brands_serviced`, `service_area`, `service_area_radius`, `certifications`, `licensed_insured`,
`business_hours`, `response_time`, `emergency_service`, `emergency_phone`, `after_hours_behavior`,
`pricing_policy`, `diagnostic_fee`, `standard_fees`, `free_estimates`, `financing_available`,
`financing_details`, `warranty`, `warranty_details`, `payment_methods`, `maintenance_plans`,
`membership_program`, `lead_contact_method`, `lead_phone`, `lead_email`,
`notification_email_2`, `notification_email_3`, `notification_sms_2`, `notification_sms_3`,
`transfer_phone`, `transfer_triggers`, `transfer_behavior`, `do_not_service`,
`google_review_rating`, `google_review_count`, `unique_selling_points`, `current_promotion`,
`seasonal_services`, `additional_info`, `agent_id`, `conversation_flow_id`

**Live-mode only:** `twilio_number`, `stripe_customer_id`, `subscription_id`

---

## Phase 4: Retell Agent Validation

```python
RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
BASE = "https://api.retellai.com"

# Get agent
agent = retell(f"get-agent/{agent_id}")
assert agent['agent_id'] == agent_id
assert TEST_COMPANY in agent['agent_name']
assert agent['webhook_url'] == "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
assert agent['voice_id']  # not empty
assert agent['language'] == 'multi'

# Publish agent
s, _ = http(f"{BASE}/publish-agent/{agent_id}", "POST", {}, {"Authorization": f"Bearer {RETELL_KEY}"})
assert s == 200
```

**Known agent IDs (do NOT delete):**
- Arctic Breeze HVAC (Standard): `agent_4afbfdb3fcb1ba9569353af28d`
- Demo Jake: `agent_b9d169e5290c609a8734e0bb45`
- Demo Sophie: `agent_2723c07c83f65c71afd06e1d50`

---

## Phase 5: Conversation Flow Validation

```python
flow = retell(f"get-conversation-flow/{flow_id}")
nodes = flow.get('nodes', [])
node_names = [n['name'] for n in nodes]

assert len(nodes) == 13                       # exact count
assert flow['flex_mode'] in [False, None]
assert flow['start_speaker'] == 'agent'
assert 'greeting_node' in node_names
assert 'nonemergency_leadcapture_node' in node_names
assert 'verify_emergency_node' in node_names
assert 'callback_node' in node_names
assert 'spam_robocall_node' in node_names

# Greeting text contains agent name
greeting = next(n for n in nodes if n['name'] == 'greeting_node')
assert TEST_AGENT in greeting['instruction']['text']

# Global prompt contains company name
assert TEST_COMPANY in flow['global_prompt']
```

---

## Phase 6: Call Processor Test

### Fake Call Payload
```python
fake_call = {
    "event": "call_analyzed",
    "call": {
        "call_id": f"test_{TS}",
        "agent_id": agent_id,
        "call_status": "ended",
        "from_number": "+16316330713",
        "to_number": "+18129944371",
        "start_timestamp": int(time.time()*1000) - 120000,
        "end_timestamp": int(time.time()*1000),
        "disconnection_reason": "user_hangup",
        "call_analysis": {},
        "transcript": (
            f"Agent: {TEST_GREETING} "
            "Caller: Hi, my heating system stopped working last night. "
            "Agent: I'm sorry to hear that. Can I get your full name please? "
            "Caller: Daniel Blackmore. "
            "Agent: And your best callback number? "
            "Caller: 631-633-0713. "
            "Agent: And the service address? "
            "Caller: 45 Park Avenue, Manhattan, New York. "
            "Agent: Perfect, I have passed all of that through to the team."
        )
    }
}
# POST to: https://n8n.syntharra.com/webhook/retell-hvac-webhook
```

### Expected hvac_call_log row assertions:
- `call_id` = fake call id (present, dedup checked)
- `company_name` = TEST_COMPANY
- `caller_name` populated
- `caller_phone` populated
- `service_requested` not empty / not "Other"
- `lead_score` >= 6
- `is_lead` = True
- `summary` not empty
- `duration_seconds` > 0
- `call_tier` = "standard" or "premium"
- `job_type` populated
- `caller_sentiment` populated (integer)
- `transfer_attempted` = boolean
- `geocode_status` populated

**Dedup check:** Send same call twice — expect exactly 1 row.

---

## Phase 7: Email Verification

### Emails That MUST Fire During a Full E2E Test

| Trigger | From | To | Subject Contains | Workflow |
|---|---|---|---|---|
| Jotform submitted | `noreply@syntharra.com` | Client email | "Welcome" / "Setup" | `4Hx7aRdzMl5N0uJP` |
| Onboarding complete | `noreply@syntharra.com` | `onboarding@syntharra.com` | "New Client" / company name | `4Hx7aRdzMl5N0uJP` |
| Call received (lead) | `noreply@syntharra.com` | `lead_email` | Lead details / caller name | `Kg576YtPM9yEacKn` |
| Call received (lead) | `noreply@syntharra.com` | `notification_email_2` | Lead notification | `Kg576YtPM9yEacKn` |
| Weekly lead report | `noreply@syntharra.com` | Client email | "Weekly Lead Report" | `iLPb6ByiytisqUJC` |
| Usage at 80% | `noreply@syntharra.com` | Client email | "80%" / minutes warning | `Wa3pHRMwSjbZHqMC` |
| Usage at 100% | `noreply@syntharra.com` | Client email | "100%" / limit reached | `Wa3pHRMwSjbZHqMC` |
| Stripe checkout | Stripe | Client email | Invoice / receipt | Stripe (not n8n) |

**Email check method (currently manual):**
The test prints "Check daniel@syntharra.com inbox" — future improvement: add Gmail API check via n8n execution output.

### All emails MUST be:
- Light theme (white cards, grey bg, purple accent `#6C63FF`)
- From `noreply@syntharra.com`
- Contain Syntharra logo (hosted PNG)
- Support link: `support@syntharra.com`
- No `daniel@syntharra.com` reference

---

## Phase 8: Cleanup

**DO NOT** instant-delete. Always use the delayed cleanup webhook:

```python
cleanup_payload = {
    "company_name": TEST_COMPANY,
    "agent_ids": cleanup["agent_ids"],   # list of Retell agent IDs created
    "flow_ids":  cleanup["flow_ids"],    # list of Retell flow IDs created
}
s, _ = http("https://n8n.syntharra.com/webhook/e2e-test-cleanup", "POST", cleanup_payload)
# Workflow ID: URbQPNQP26OIdYMo
# Deletes after 5 minutes: hvac_standard_agent, hvac_premium_agent,
# stripe_payment_data, hvac_call_log, hvac_premium_call_log,
# client_subscriptions, Retell agents, Retell flows
```

---

## Usage Minutes Test (Future Phase 9)

To test the minutes calculator and usage alerts:
1. Submit enough fake calls to push `SUM(duration_seconds)/60` past 80% of plan limit (475 min standard / 1000 min premium)
2. Trigger `z1DNTjvTDAkExsX8` (Monthly Minutes Calculator) manually
3. Assert `billing_cycles` row created with correct `minutes_used`
4. Assert `overage_charges` row created if over limit
5. Assert 80% and 100% alert emails fired from `Wa3pHRMwSjbZHqMC`

---

## Premium-Specific Test Extensions (Future Phase 10)

After premium onboarding is triggered:
- `hvac_premium_agent` row created with ALL fields including `crm_platform`, `crm_status`, `calendar_platform`, `calendar_status`
- `73Y0MHVBu05bIm5p` (Premium Integration Dispatcher) should execute
- OAuth tokens stored (tested via `syntharra-oauth-server`)
- CRM push tested (Jobber API)
- Calendar booking tested (Google Calendar)

---

## Running the Test

```bash
# From any machine with Python 3.8+
cd syntharra-automations/shared
python3 e2e-test.py
```

**Test modes:**
- `STRIPE_CUSTOMER_ID = ""` → Test mode (no phone purchase, no Stripe billing)
- `STRIPE_CUSTOMER_ID = "cus_xxxxx"` → Live mode (full flow incl. Twilio)

**Expected output on success:**
```
✅ ALL SYSTEMS GO — Full pipeline verified
MODE  : TEST
RESULT: 45/45 passed | 0 failed
```

---

## Key Credentials (all stored in Claude project memory)

| Key | Used For |
|---|---|
| `N8N_KEY` | Railway n8n API (ends in `NqU`) |
| `RETELL_KEY` | `key_0157d9401f66cfa1b51fadc66445` |
| `SB_ANON` | Supabase reads (in e2e-test.py) |
| `SB_SVC` | Supabase deletes (service role) |
| `GH_TOKEN` | GitHub pushes |

---

## Extending the Test

When adding new fields/workflows/emails to Syntharra, update the test by:
1. Adding the new Jotform field key + expected Supabase column to Phase 1 table
2. Adding the new assertion to Phase 3 field list
3. Adding any new email trigger to Phase 7 table
4. If a new workflow was created, add it to the Phase 2 workflow table
5. Update `e2e-test.py` in `shared/` with the new assertions
6. The cleanup workflow (`URbQPNQP26OIdYMo`) handles all tables — no changes needed unless a new table is added

---

## Common Failures & Fixes

| Failure | Likely Cause | Fix |
|---|---|---|
| Webhook 404 | n8n workflow inactive | Activate in n8n UI |
| Supabase row missing | Onboarding workflow errored | Check n8n executions |
| agent_id empty | Retell API error | Check Retell API key |
| flow_id empty | LLM creation failed | Check Retell LLM endpoint |
| Emails not received | SMTP2GO quota / wrong `To` | Check SMTP2GO dashboard |
| Lead score < 6 | GPT analysis weak transcript | Use richer test transcript |
| Dedup failed (2 rows) | Call processor no dedup logic | Check call_id check in workflow |
| Cleanup webhook 404 | Cleanup workflow inactive | Activate `URbQPNQP26OIdYMo` |
