# Syntharra Full-Stack E2E Test Skill — Complete Reference

## When to Use This Skill
Read this skill whenever:
- Running, debugging, or extending the E2E test
- Verifying the system works before launch
- Investigating a production issue and need to know what "correct" looks like
- Adding a new workflow, field, or email and need to add coverage

The canonical test script: `syntharra-automations/shared/e2e-test.py`

---

## Complete System Architecture

| Layer | System | URL / ID | Role |
|---|---|---|---|
| Intake (Standard) | Jotform | Form `260795139953066` | Standard client onboarding form |
| Intake (Premium) | Jotform | Form `260819259556671` | Premium client onboarding form |
| Automation | n8n (Railway) | `https://n8n.syntharra.com` | All workflow orchestration |
| AI Voice | Retell AI | `https://api.retellai.com` | Agent + conversation flow creation |
| Database | Supabase | `hgheyqwnrcvwtgngqdnq.supabase.co` | All client, call, billing data |
| Payments | Stripe | TEST MODE currently | Checkout, subscriptions, invoices |
| Email | SMTP2GO + Gmail nodes | `noreply@syntharra.com` | All outbound email |
| Telephony | Telnyx (pending) | Awaiting approval | Inbound calls, SMS |
| Phone (legacy test) | Retell phone | `+18129944371` | Arctic Breeze HVAC test line |
| Monitoring | Ops Monitor (Railway) | `syntharra-ops-monitor-production.up.railway.app` | Health checks, alerts |
| Admin Dashboard | syntharra-admin (Railway) | Private Railway URL | Internal ops dashboard |
| Checkout | syntharra-checkout (Railway) | `syntharra-checkout-production.up.railway.app` | Stripe checkout server |
| OAuth | syntharra-oauth-server (Railway) | Private | Premium CRM/Calendar OAuth |

---

## Test Credentials (stored in Claude project memory)

```python
N8N_KEY    = "eyJhbGci...NqU"   # Railway n8n API key (ends NqU)
RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
SUPABASE   = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_ANON    = "eyJhbGci...yL0"   # anon key — for reads
SB_SVC     = "eyJhbGci...qsg"   # service role — for deletes only
TEST_EMAIL = "daniel@syntharra.com"
GH_TOKEN   = "ghp_rJrptP..."
```

---

## Test Data Pattern

```python
TS           = int(time.time())
TEST_COMPANY = f"Polar Peak HVAC {TS}"   # unique per run
TEST_AGENT   = "Max"
TEST_PHONE   = "+15125550199"
# cleanup['agent_ids'], cleanup['flow_ids'] — populated during test, passed to cleanup webhook
```

---

## ALL 8 TEST PHASES

---

### PHASE 1 — Jotform Standard Submission (ALL 52 fields)

**Webhook:** `POST https://n8n.syntharra.com/webhook/jotform-hvac-onboarding`  
**Workflow triggered:** `4Hx7aRdzMl5N0uJP` (HVAC Standard Onboarding)

Every field below MUST be present in the submission payload. Missing fields = incomplete Supabase record = test failure.

| Jotform Field Key | Test Value | Supabase Column | Assert |
|---|---|---|---|
| `q4_hvacCompany` | `TEST_COMPANY` | `company_name` | exact match |
| `q54_ownerName` | `"James Caldwell"` | `owner_name` | exact match |
| `q6_mainCompany` | `TEST_PHONE` | `company_phone` | non-empty |
| `q5_emailAddress` | `TEST_EMAIL` | `client_email` | exact match |
| `q7_companyWebsite` | `"www.polarpeak.com"` | `website` | exact match |
| `q8_yearsIn` | `"8"` | `years_in_business` | exact match |
| `q34_timezone` | `"America/New_York"` | `timezone` | exact match |
| `q13_servicesOffered` | `["AC Repair","Heating Repair","AC Installation","Heating Installation","Maintenance","Duct Cleaning","Air Quality"]` | `services_offered` | non-empty |
| `q14_brandsequipmentServiced` | `["Carrier","Trane","Lennox","Rheem","York","Goodman"]` | `brands_serviced` | non-empty |
| `q16_primaryService` | `"New York City and surrounding boroughs"` | `service_area` | non-empty |
| `q40_serviceAreaRadius` | `"40 miles"` | `service_area_radius` | exact match |
| `q29_certifications` | `["NATE Certified","EPA 608","OSHA 10"]` | `certifications` | non-empty |
| `q28_licensedAnd` | `"Yes"` | `licensed_insured` | `"Yes"` |
| `q10_aiAgent10` | `TEST_AGENT` | `agent_name` | non-empty |
| `q11_aiVoice` | `"Male"` | `voice_gender` | non-empty |
| `q38_customGreeting` | greeting string | `custom_greeting` | contains TEST_AGENT |
| `q39_companyTagline` | `"New York City's Most Trusted HVAC"` | `company_tagline` | non-empty |
| `q17_businessHours` | `"Monday to Friday 7am to 7pm, Saturday 8am to 4pm"` | `business_hours` | non-empty |
| `q18_typicalResponse` | `"Same day or next business day"` | `response_time` | non-empty |
| `q20_247Emergency` | `"Yes"` | `emergency_service` | `"Yes"` |
| `q21_emergencyAfterhours` | `"+15125550199"` | `emergency_phone` | non-empty |
| `q22_afterhoursBehavior` | `"Transfer to emergency line"` | `after_hours_behavior` | non-empty |
| `q42_pricingPolicy` | `"Free estimates on all new installations. $95 diagnostic fee waived with repair."` | `pricing_policy` | non-empty |
| `q41_diagnosticFee` | `"$95 diagnostic fee, waived with repair"` | `diagnostic_fee` | non-empty |
| `q43_standardFees` | `"Service call $95, Tune-up $149, Emergency surcharge $75"` | `standard_fees` | non-empty |
| `q24_freeEstimates` | `"Yes - free on all new system installations"` | `free_estimates` | non-empty |
| `q25_financingAvailable` | `"Yes"` | `financing_available` | `"Yes"` |
| `q44_financingDetails` | `"0% financing for 24 months on systems over $4,000"` | `financing_details` | non-empty |
| `q26_serviceWarranties` | `"Yes"` | `warranty` | `"Yes"` |
| `q27_warrantyDetails` | `"5 years parts, 2 years labour on all repairs"` | `warranty_details` | non-empty |
| `q45_paymentMethods` | `["Cash","Credit Card","Check","Financing","Zelle"]` | `payment_methods` | non-empty |
| `q46_maintenancePlans` | `"Yes - Peak Care Club $249/year..."` | `maintenance_plans` | non-empty |
| `q58_membershipProgramName` | `"Peak Care Club"` | `membership_program` | exact match |
| `q31_leadContact` | `"Both"` | `lead_contact_method` | `"Both"` |
| `q32_leadNotification` | `"+16316330713"` | `lead_phone` | non-empty |
| `q33_leadNotification33` | `TEST_EMAIL` | `lead_email` | exact match |
| `q59_notifEmail2` | `"dispatcher@polarpeak.com"` | `notification_email_2` | exact match |
| `q60_notifEmail3` | `"salesmanager@polarpeak.com"` | `notification_email_3` | exact match |
| `q61_notifSms2` | `"+16316330714"` | `notification_sms_2` | exact match |
| `q62_notifSms3` | `"+16316330715"` | `notification_sms_3` | exact match |
| `q48_transferPhone` | `TEST_PHONE` | `transfer_phone` | non-empty |
| `q49_transferTriggers` | `["Customer is angry","Legal threat","Complex billing dispute","Customer requests manager"]` | `transfer_triggers` | non-empty |
| `q50_transferBehavior` | `"Try once - take message if no answer"` | `transfer_behavior` | non-empty |
| `q57_doNotServiceList` | `"Commercial refrigeration, window units, portable ACs"` | `do_not_service` | non-empty |
| `q55_googleReviewRating` | `"4.8"` | `google_review_rating` | `"4.8"` |
| `q56_googleReviewCount` | `"527"` | `google_review_count` | `"527"` |
| `q51_uniqueSellingPoints` | `"Family-owned, same-day service, 5-year warranty..."` | `unique_selling_points` | non-empty |
| `q52_currentPromotion` | `"$75 off any repair over $400 this month"` | `current_promotion` | non-empty |
| `q53_seasonalServices` | `"Spring AC tune-ups, Fall heating inspections..."` | `seasonal_services` | non-empty |
| `q37_additionalInfo` | `"Proudly serving NYC since 2016..."` | `additional_info` | non-empty |

**After submission wait:** `time.sleep(25)` for full workflow execution.

---

### PHASE 1B — Jotform Premium Submission (ALL fields)

**Webhook:** `POST https://n8n.syntharra.com/webhook/jotform-hvac-premium-onboarding`  
**Workflow triggered:** `kz1VmwNccunRMEaF` (HVAC Premium Onboarding)

All standard fields above PLUS these premium-specific fields:

| Jotform Field Key | Test Value | Supabase Column | Assert |
|---|---|---|---|
| `q63_afterHoursTransfer` | `"emergency_only"` | `after_hours_transfer` | non-empty |
| `q75_greetingStyle` | `"standard"` | (used to build) `custom_greeting` | greeting generated |
| `q76_customGreetingText` | `""` | `custom_greeting` | if style=custom, this used |
| `q79_notifSms2` | `"+16316330714"` | `notification_sms_2` | exact match |
| `q80_notifSms3` | `"+16316330715"` | `notification_sms_3` | exact match |
| `q81_notifEmail2` | `"dispatcher@polarpeak.com"` | `notification_email_2` | exact match |
| `q82_notifEmail3` | `"salesmanager@polarpeak.com"` | `notification_email_3` | exact match |
| `q83_addMarketingDetails` | `"Yes"` | (informational) | non-empty |

**Premium-specific Supabase columns** (`hvac_premium_agent` only):
- `crm_platform` — e.g. `"Jobber"`
- `crm_status` — starts as `"pending"`, becomes `"active"` after OAuth
- `calendar_platform` — e.g. `"Google Calendar"`
- `calendar_status` — starts as `"pending"`, becomes `"active"` after OAuth
- `booking_buffer_minutes` — int, default 30
- `default_appointment_duration` — int, default 60
- `booking_advance_days` — int, default 14
- `booking_confirmation_method` — `"email"` or `"sms"`
- `crm_access_token`, `crm_refresh_token`, `crm_token_expiry` — populated after OAuth
- `calendar_access_token`, `calendar_refresh_token`, `calendar_token_expiry` — populated after OAuth

---

### PHASE 2 — n8n Workflow Execution Checks

**All 21 active workflows — check after relevant trigger:**

| Workflow ID | Name | Triggered By | Check Method |
|---|---|---|---|
| `4Hx7aRdzMl5N0uJP` | HVAC Standard Onboarding | Jotform webhook | `GET /executions?workflowId=...&limit=1` → `status == 'success'` |
| `kz1VmwNccunRMEaF` | HVAC Premium Onboarding | Jotform webhook | Same |
| `xKD3ny6kfHL0HHXq` | Stripe Workflow | `checkout.session.completed` webhook | Same |
| `Kg576YtPM9yEacKn` | HVAC Standard Call Processor | Retell `call_analyzed` webhook | Same |
| `STQ4Gt3rH8ptlvMi` | HVAC Premium Call Processor | Retell `call_analyzed` webhook | Same |
| `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher | Premium call processor output | Same |
| `z1DNTjvTDAkExsX8` | Monthly Minutes Calculator | Schedule (1st of month, 8am UTC) | Manual trigger for test |
| `Wa3pHRMwSjbZHqMC` | Usage Alert Monitor | Schedule (daily 9am UTC) | Manual trigger for test |
| `iLPb6ByiytisqUJC` | HVAC Weekly Lead Report | Schedule (Sundays 6pm per timezone) | Manual trigger for test |
| `44WfbVmJ7Zihcwgs` | Nightly GitHub Backup | Schedule (2am daily) | Check last execution |
| `13cOIXxvj83NfDqQ` | Publish Retell Agent | Called by onboarding | Verify agent is published |
| `Ex90zUMSEWwVk4Wv` | HVAC Scenario Test Runner v4 | Manual | Run separately |
| `ccOxdvghTsNqX8x0` | HVAC Scenario Transcript Generator | Manual | Run separately |
| `eZHkfu9EYKHFoig0` | HVAC Scenario: Process Single Scenario | Manual | Run separately |
| `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed Delete | E2E test script | Fires at end of every test |
| `AU8DD5r6i6SlYFnb` | Auto-Enable MCP on All Workflows | Schedule (every 6h) | Check last execution |
| `Eo8wwvZgeDm5gA9d` | Newsletter Unsubscribe Webhook | Webhook | Check response |
| `6LXpGffcWSvL6RxW` | Weekly Newsletter | Schedule | Check last execution |
| `lXqt5anbJgsAMP7O` | Send Welcome Email (Manual) | Manual | Run and verify email |
| `QY1ZFtPJFsU5h6wQ` | Website Lead → AI Readiness Score Email | Website form | Check on submit |
| `hFU0ZeHae7EttCDK` | Website Lead → Free Report Email | Website form | Check on submit |

**Execution check pattern:**
```python
N8N_BASE = "https://n8n.syntharra.com/api/v1"
_, execs = http(f"{N8N_BASE}/executions?workflowId={wf_id}&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
latest = (execs.get('data') or [{}])[0]
assert latest.get('status') == 'success', f"Workflow {wf_id} status: {latest.get('status')}"
```

---

### PHASE 3 — Supabase Complete Field Verification

#### Table: `hvac_standard_agent` — ALL columns to assert non-null/non-empty

```python
REQUIRED_FIELDS = [
  'company_name','owner_name','company_phone','client_email','website',
  'years_in_business','timezone','industry_type','agent_name','voice_gender',
  'custom_greeting','company_tagline','services_offered','brands_serviced',
  'service_area','service_area_radius','certifications','licensed_insured',
  'business_hours','response_time','emergency_service','emergency_phone',
  'after_hours_behavior','after_hours_transfer','pricing_policy','diagnostic_fee',
  'standard_fees','free_estimates','financing_available','financing_details',
  'warranty','warranty_details','payment_methods','maintenance_plans',
  'membership_program','lead_contact_method','lead_phone','lead_email',
  'notification_email_2','notification_email_3','notification_sms_2','notification_sms_3',
  'transfer_phone','transfer_triggers','transfer_behavior','unique_selling_points',
  'current_promotion','seasonal_services','google_review_rating','google_review_count',
  'do_not_service','additional_info',
  'agent_id',           # populated by workflow after Retell agent created
  'conversation_flow_id',  # populated by workflow after Retell flow created
]

LIVE_MODE_ONLY = ['twilio_number','stripe_customer_id','subscription_id']
```

#### Table: `hvac_premium_agent` — ALL columns (superset of standard)

All standard fields above PLUS:
```python
PREMIUM_EXTRA_FIELDS = [
  'crm_platform','crm_status','calendar_platform','calendar_status',
  'booking_buffer_minutes','default_appointment_duration',
  'booking_advance_days','booking_confirmation_method',
]
# After OAuth flow completes:
PREMIUM_OAUTH_FIELDS = [
  'crm_access_token','crm_refresh_token','crm_token_expiry',
  'calendar_access_token','calendar_refresh_token','calendar_token_expiry',
]
```

#### Table: `hvac_call_log` — after fake call test

```python
CALL_LOG_FIELDS = {
  'call_id': fake_call_id,          # exact match
  'company_name': TEST_COMPANY,     # exact match
  'agent_id': agent_id,             # exact match
  'caller_name': 'non-empty',       # GPT extracted
  'caller_phone': 'non-empty',      # extracted from transcript or from_number
  'service_requested': 'non-empty and not "Other"',  # GPT classified
  'lead_score': '>= 6',             # heating emergency = high score
  'is_lead': True,
  'urgency': 'non-empty',           # 'emergency', 'urgent', 'routine', 'low'
  'summary': 'non-empty',           # GPT generated
  'duration_seconds': '> 0',
  'call_tier': '"standard" or "premium"',
  'job_type': 'non-empty',          # e.g. "Heating Repair"
  'vulnerable_occupant': 'boolean',
  'caller_sentiment': 'integer 1-10',
  'transfer_attempted': 'boolean',
  'transfer_success': 'boolean',
  'geocode_status': 'non-empty',    # 'success', 'not_found', 'skipped'
  'geocode_formatted': 'if geocode_status=success, non-empty',
  'caller_address': 'non-empty',    # extracted from transcript
  'notes': 'non-empty',
}
```

#### Table: `hvac_premium_call_log` — after fake premium call

Additional fields vs standard:
```python
PREMIUM_CALL_EXTRA = [
  'booking_attempted','booking_success','appointment_date','appointment_time',
  'appointment_duration_minutes','job_type_booked','booking_reference',
  'reschedule_requested','cancellation_requested','call_type',
  'caller_email','is_hot_lead','call_successful','call_status',
  'notification_sent','notification_type','notification_priority',
  'is_repeat_caller','repeat_call_count','from_number',
]
```

#### Table: `stripe_payment_data` — after Stripe checkout (live mode)

```python
STRIPE_FIELDS = {
  'stripe_customer_id': 'non-empty',
  'stripe_subscription_id': 'non-empty',
  'stripe_session_id': 'non-empty',
  'customer_email': TEST_EMAIL,
  'customer_name': TEST_COMPANY,
  'plan_name': '"HVAC Standard" or "HVAC Premium"',
  'plan_billing': '"monthly" or "annual"',
  'plan_amount': 'non-empty',
  'minutes': '"475" or "1000"',
  'payment_status': '"complete"',
  'jotform_sent': True,    # Jotform link was sent
  'agent_id': 'non-empty', # linked after onboarding
}
```

#### Table: `client_subscriptions` — after full onboarding with Stripe

```python
SUBSCRIPTION_FIELDS = {
  'agent_id': 'non-empty',
  'company_name': TEST_COMPANY,
  'client_email': TEST_EMAIL,
  'plan_type': '"standard" or "premium"',
  'included_minutes': '475 or 1000',
  'overage_rate_cents': 'non-zero',
  'monthly_rate_cents': '49700 or 99700',
  'stripe_customer_id': 'non-empty',
  'stripe_subscription_id': 'non-empty',
  'billing_anchor_day': '1-31',
  'agreement_signed': True,
  'status': '"active"',
}
```

#### Table: `billing_cycles` — after Monthly Minutes Calculator runs

```python
BILLING_CYCLE_FIELDS = {
  'subscription_id': 'non-empty UUID',
  'agent_id': 'non-empty',
  'billing_month': '"YYYY-MM"',
  'period_start': 'datetime',
  'period_end': 'datetime',
  'total_calls': 'integer >= 0',
  'total_seconds': 'integer >= 0',
  'total_minutes': 'numeric >= 0',
  'included_minutes': '475 or 1000',
  'overage_minutes': 'numeric >= 0',
  'alert_80_sent': 'boolean',
  'alert_100_sent': 'boolean',
  'status': '"calculated" or "invoiced"',
}
```

#### Table: `overage_charges` — if minutes exceeded

```python
OVERAGE_FIELDS = {
  'billing_cycle_id': 'non-empty',
  'subscription_id': 'non-empty',
  'agent_id': 'non-empty',
  'billing_month': '"YYYY-MM"',
  'overage_minutes': '> 0',
  'rate_per_minute_cents': 'non-zero',
  'total_amount_cents': '> 0',
  'stripe_invoice_id': 'non-empty (if Stripe live)',
  'status': '"pending" or "paid"',
}
```

#### Table: `call_processor_dlq` — MUST be empty

```python
dlq = sb("call_processor_dlq?resolved=eq.false&select=*")
assert len(dlq) == 0, f"DLQ has {len(dlq)} unresolved items!"
```

#### Table: `agreement_signatures` — after client signs service agreement

```python
AGREEMENT_FIELDS = [
  'agent_id','company_name','signer_name','signer_email','signer_title',
  'agreement_type','agreement_version','signature_data','signature_method',
  'ip_address','plan_type','signed_at',
]
```

#### Table: `website_leads` — after demo form submit

```python
LEAD_FIELDS = {
  'email': 'non-empty',
  'source': 'non-empty',
  'page_url': 'non-empty',
  'unsubscribed': False,
}
```

#### Table: `affiliate_applications` — after affiliate form submit

```python
AFFILIATE_FIELDS = ['full_name','email','website_or_social','referral_type','status','source']
# status should be 'pending' on creation
```

---

### PHASE 4 — Retell Agent Validation

```python
RETELL_BASE = "https://api.retellai.com"
RETELL_HEADERS = {"Authorization": f"Bearer {RETELL_KEY}"}

# GET agent
agent = retell(f"get-agent/{agent_id}")
assert agent['agent_id'] == agent_id
assert TEST_COMPANY in agent['agent_name']
assert agent['webhook_url'] == "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
assert bool(agent['voice_id'])
assert agent['language'] == 'multi'
assert agent['version'] >= 1    # published = has a version

# Verify agent is PUBLISHED
s, _ = http(f"{RETELL_BASE}/publish-agent/{agent_id}", "POST", {},
    {"Authorization": f"Bearer {RETELL_KEY}"})
assert s == 200, f"Publish agent HTTP {s}"

# List all agents — test agent should appear
all_agents = retell("list-agents")
agent_ids = [a['agent_id'] for a in all_agents]
assert agent_id in agent_ids

# NEVER DELETE these production agents:
PROTECTED_AGENTS = [
  "agent_4afbfdb3fcb1ba9569353af28d",  # Arctic Breeze HVAC
  "agent_b9d169e5290c609a8734e0bb45",  # Demo Jake
  "agent_2723c07c83f65c71afd06e1d50",  # Demo Sophie
]
assert agent_id not in PROTECTED_AGENTS, "Test created a protected agent ID!"
```

---

### PHASE 5 — Conversation Flow Validation (Standard 13-node flow)

```python
flow = retell(f"get-conversation-flow/{flow_id}")
nodes = flow.get('nodes', [])
node_names = [n['name'] for n in nodes]

# Structure
assert len(nodes) == 13,                     f"Expected 13 nodes, got {len(nodes)}"
assert flow.get('flex_mode') in [False, None]
assert flow.get('start_speaker') == 'agent'

# Required nodes
REQUIRED_NODES = [
  'greeting_node',
  'nonemergency_leadcapture_node',
  'verify_emergency_node',
  'callback_node',
  'spam_robocall_node',
]
for node in REQUIRED_NODES:
    assert node in node_names, f"Missing node: {node}"

# Content checks
greeting = next(n for n in nodes if n['name'] == 'greeting_node')
assert TEST_AGENT in greeting['instruction']['text'], "Agent name not in greeting"
assert TEST_COMPANY in flow.get('global_prompt', ''), "Company not in global prompt"

# Global prompt should contain key company info sections
prompt = flow.get('global_prompt', '')
assert 'COMPANY_INFO' in prompt or TEST_COMPANY in prompt
```

---

### PHASE 6 — Call Processor Test (Standard)

**Webhook:** `POST https://n8n.syntharra.com/webhook/retell-hvac-webhook`

```python
fake_call_id = f"test_{TS}"
cleanup['call_ids'].append(fake_call_id)

fake_call = {
    "event": "call_analyzed",
    "call": {
        "call_id":          fake_call_id,
        "agent_id":         agent_id,
        "call_status":      "ended",
        "from_number":      "+16316330713",
        "to_number":        "+18129944371",
        "start_timestamp":  int(time.time()*1000) - 120000,
        "end_timestamp":    int(time.time()*1000),
        "disconnection_reason": "user_hangup",
        "call_analysis":    {},
        "transcript": (
            f"Agent: {TEST_GREETING} "
            "Caller: Hi, my heating system stopped working last night and it's very cold. "
            "I have elderly parents at home. "
            "Agent: I'm sorry to hear that — we can help. Can I get your full name please? "
            "Caller: Daniel Blackmore. "
            "Agent: And your best callback number? "
            "Caller: 631-633-0713. "
            "Agent: And the service address? "
            "Caller: 45 Park Avenue, Manhattan, New York, 10016. "
            "Agent: Thank you Daniel, I've captured all your details. "
            "Our team will call you back within the hour. Is there anything else? "
            "Caller: No that's great thank you. "
            "Agent: Great, have a good day!"
        )
    }
}

s, _ = http("https://n8n.syntharra.com/webhook/retell-hvac-webhook", "POST", fake_call)
assert s == 200
time.sleep(20)  # wait for GPT analysis

# Verify call log
rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
call = rows[0]

# All call log assertions
assert bool(call.get('caller_name')),          "caller_name missing"
assert bool(call.get('caller_phone')),         "caller_phone missing"
assert call.get('service_requested') not in ['', 'Other', None], "service_requested bad"
assert (call.get('lead_score') or 0) >= 6,    f"lead_score too low: {call.get('lead_score')}"
assert call.get('is_lead') == True,            "is_lead not True"
assert bool(call.get('summary')),              "summary missing"
assert bool(call.get('urgency')),              "urgency missing"
assert bool(call.get('job_type')),             "job_type missing"
assert call.get('company_name') == TEST_COMPANY, "company_name mismatch"
assert call.get('call_tier') in ['standard','premium'], "call_tier wrong"
assert isinstance(call.get('caller_sentiment'), int), "caller_sentiment not int"
assert isinstance(call.get('transfer_attempted'), bool), "transfer_attempted not bool"
assert isinstance(call.get('vulnerable_occupant'), bool), "vulnerable_occupant not bool"
# elderly parents → vulnerable_occupant should be True for this transcript
assert call.get('vulnerable_occupant') == True, "elderly parent not flagged as vulnerable"

# Dedup — send same call_id again → still exactly 1 row
http("https://n8n.syntharra.com/webhook/retell-hvac-webhook", "POST", fake_call)
time.sleep(8)
dup_rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
assert len(dup_rows) == 1, f"Dedup failed — {len(dup_rows)} rows"

# n8n execution check
_, cp = http(f"https://n8n.syntharra.com/api/v1/executions?workflowId=Kg576YtPM9yEacKn&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
cp_exec = (cp.get('data') or [{}])[0]
assert cp_exec.get('status') == 'success', f"Call processor exec: {cp_exec.get('status')}"
```

---

### PHASE 7 — Email Verification (ALL Emails)

Every email below MUST fire during a complete E2E test run. Currently verified manually via inbox.

| # | Workflow | Trigger | From | To | Subject Pattern | When |
|---|---|---|---|---|---|---|
| 1 | `4Hx7aRdzMl5N0uJP` | Jotform std submission | `noreply@syntharra.com` | `TEST_EMAIL` | "Welcome" + company name | On onboarding |
| 2 | `4Hx7aRdzMl5N0uJP` | Jotform std submission | `noreply@syntharra.com` | `onboarding@syntharra.com` | "New Client: " + company name | On onboarding (internal) |
| 3 | `kz1VmwNccunRMEaF` | Jotform prem submission | `noreply@syntharra.com` | `TEST_EMAIL` | Premium welcome | On prem onboarding |
| 4 | `kz1VmwNccunRMEaF` | Jotform prem submission | `noreply@syntharra.com` | `onboarding@syntharra.com` | Internal premium notification | On prem onboarding |
| 5 | `xKD3ny6kfHL0HHXq` | Stripe checkout complete | `noreply@syntharra.com` | `TEST_EMAIL` | Jotform link + welcome | After Stripe checkout |
| 6 | `xKD3ny6kfHL0HHXq` | Stripe checkout complete | `noreply@syntharra.com` | `onboarding@syntharra.com` | Stripe internal notification | After Stripe checkout |
| 7 | `Kg576YtPM9yEacKn` | Fake call (is_lead=true) | `noreply@syntharra.com` | `lead_email` (TEST_EMAIL) | Lead captured + caller details | After call processed |
| 8 | `Kg576YtPM9yEacKn` | Fake call (is_lead=true) | `noreply@syntharra.com` | `notification_email_2` | Lead notification | After call processed |
| 9 | `Kg576YtPM9yEacKn` | Fake call (is_lead=true) | `noreply@syntharra.com` | `admin@syntharra.com` | Internal call notification | After call processed |
| 10 | `iLPb6ByiytisqUJC` | Sunday 6pm trigger | `noreply@syntharra.com` | `TEST_EMAIL` | "Weekly Lead Report" | Weekly |
| 11 | `Wa3pHRMwSjbZHqMC` | Usage hits 80% | `noreply@syntharra.com` | `TEST_EMAIL` | "⚠️" + "80%" + company | When 80% limit hit |
| 12 | `Wa3pHRMwSjbZHqMC` | Usage hits 100% | `noreply@syntharra.com` | `TEST_EMAIL` | "⚠️" + "exceeded" | When 100% hit |
| 13 | `Wa3pHRMwSjbZHqMC` | Usage alert any | `noreply@syntharra.com` | `admin@syntharra.com` | "[INTERNAL] Usage Alert" | Same time |
| 14 | `z1DNTjvTDAkExsX8` | 1st of month | `noreply@syntharra.com` | `TEST_EMAIL` | "Syntharra Usage Report" | Monthly |
| 15 | `QY1ZFtPJFsU5h6wQ` | Website form submit | `noreply@syntharra.com` | Lead email | "AI Readiness Score" | On submit |
| 16 | `hFU0ZeHae7EttCDK` | Website form submit | `noreply@syntharra.com` | Lead email | "Free Report" | On submit |
| 17 | Stripe (automatic) | Checkout complete | Stripe | Customer email | Invoice/receipt | On purchase |

**Email standards — ALL emails MUST:**
- Be LIGHT THEME: white `#fff` cards, grey `#F7F7FB` outer bg, dark `#1A1A2E` text, `#6C63FF` accent
- Use hosted PNG logo (NOT inline SVG, NOT base64 in Gmail mobile)
- Show `support@syntharra.com` as support contact
- Come from `noreply@syntharra.com`
- Never reference `daniel@syntharra.com`
- Work in Gmail mobile dark mode (light theme CSS, let client handle dark)

---

### PHASE 8 — Stripe Gate Behavior

```python
# Test mode: stripe_customer_id empty → Stripe gate IF skips Twilio purchase
row = sb(f"hvac_standard_agent?company_name=eq.{urllib.parse.quote(TEST_COMPANY)}&select=*")[0]
assert not row.get('twilio_number'), "Test mode should NOT purchase Twilio number"
# workflow should still complete successfully

# Live mode: stripe_customer_id set → Twilio number purchased
# payload['stripe_customer_id'] = "cus_xxxxx"
# After test:
# assert bool(row.get('twilio_number')), "Live mode MUST assign Twilio number"
# assert row.get('twilio_number').startswith('+1')
```

---

### PHASE 9 — Usage Minutes & Billing (Full Cycle Test)

To fully test the billing pipeline:

**Step 1:** Populate enough fake calls to exceed 80% of plan limit
```python
# Standard = 475 min limit, 80% = 380 min
# Send ~25 fake calls of 4 min each (25 × 240s = 6000s = 100 min) — adjust as needed
CALLS_TO_SEND = 96  # each ~4 min = ~384 min total (> 80%)
for i in range(CALLS_TO_SEND):
    fake = {**fake_call_template, "call": {**fake_call["call"], 
            "call_id": f"test_{TS}_{i}",
            "start_timestamp": int(time.time()*1000) - 240000,
            "end_timestamp": int(time.time()*1000)}}
    http("https://n8n.syntharra.com/webhook/retell-hvac-webhook", "POST", fake)
    time.sleep(0.5)
```

**Step 2:** Manually trigger Usage Alert Monitor
```python
_, trigger = http(f"https://n8n.syntharra.com/api/v1/workflows/Wa3pHRMwSjbZHqMC/run",
    "POST", {}, {"X-N8N-API-KEY": N8N_KEY})
time.sleep(30)
# Assert: billing_cycles row has alert_80_sent = True
# Assert: email #11 received
```

**Step 3:** Manually trigger Monthly Minutes Calculator
```python
_, trigger = http(f"https://n8n.syntharra.com/api/v1/workflows/z1DNTjvTDAkExsX8/run",
    "POST", {}, {"X-N8N-API-KEY": N8N_KEY})
time.sleep(30)

cycles = sb(f"billing_cycles?agent_id=eq.{agent_id}&select=*")
assert len(cycles) >= 1
cycle = cycles[0]
assert cycle['total_minutes'] > 0
assert cycle['status'] in ['calculated', 'invoiced']
# If overage: assert overage_charges row created
```

---

### PHASE 10 — Ops Monitor Health Check

```python
import urllib.request
with urllib.request.urlopen("https://syntharra-ops-monitor-production.up.railway.app/api/status") as r:
    status = json.load(r)

# All critical systems must be healthy
critical_systems = ['retell', 'n8n', 'supabase', 'stripe', 'infrastructure']
for sys in critical_systems:
    s = status['systems'].get(sys, {})
    assert s.get('healthy') == True, f"System {sys} is NOT healthy: {s.get('checks')}"

# No unresolved DLQ items
dlq = sb("call_processor_dlq?resolved=eq.false&select=*")
assert len(dlq) == 0, f"{len(dlq)} unresolved DLQ items"

# All critical n8n workflows active
for wf_id in ['4Hx7aRdzMl5N0uJP','Kg576YtPM9yEacKn','xKD3ny6kfHL0HHXq','kz1VmwNccunRMEaF','STQ4Gt3rH8ptlvMi']:
    _, wf = http(f"https://n8n.syntharra.com/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": N8N_KEY})
    assert wf.get('active') == True, f"Workflow {wf_id} is NOT active"
```

---

### PHASE 11 — Website & Lead Forms

```python
# Test website lead form
lead_payload = {
    "email": f"test+{TS}@polarpeak.com",
    "source": "e2e_test",
    "page_url": "https://syntharra.com/hvac"
}
# POST to demo.html form endpoint / Supabase direct
s, _ = http(f"{SUPABASE}/rest/v1/website_leads", "POST", lead_payload,
    {"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}", "Prefer": "return=representation"})
assert s == 201, f"Website lead insert HTTP {s}"
time.sleep(15)

# Verify AI Readiness Score email fired (check workflow execution)
_, execs = http(f"https://n8n.syntharra.com/api/v1/executions?workflowId=QY1ZFtPJFsU5h6wQ&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
latest = (execs.get('data') or [{}])[0]
assert latest.get('status') == 'success', f"AI Score email workflow: {latest.get('status')}"
```

---

### PHASE 12 — Nightly Backup Verification

```python
import base64, json, urllib.request

# Check nightly backup ran successfully within last 25 hours
_, backup_execs = http("https://n8n.syntharra.com/api/v1/executions?workflowId=44WfbVmJ7Zihcwgs&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
last_backup = (backup_execs.get('data') or [{}])[0]
assert last_backup.get('status') == 'success', "Last nightly backup failed"

# Optionally verify GitHub files were updated
req = urllib.request.Request(
    "https://api.github.com/repos/Syntharra/syntharra-automations/commits?per_page=1",
    headers={"Authorization": f"token {GH_TOKEN}"}
)
with urllib.request.urlopen(req) as r:
    commits = json.load(r)
last_commit_msg = commits[0]['commit']['message']
# Should contain "nightly:" prefix
assert 'nightly:' in last_commit_msg.lower() or 'backup' in last_commit_msg.lower()
```

---

### PHASE 13 — Scenario Test Runner

```python
# Run one HVAC scenario to verify the scenario system works
_, scenario_exec = http(f"https://n8n.syntharra.com/api/v1/workflows/Ex90zUMSEWwVk4Wv/run",
    "POST", {}, {"X-N8N-API-KEY": N8N_KEY})
time.sleep(60)  # scenarios take longer — wait for Retell call + analysis

_, execs = http(f"https://n8n.syntharra.com/api/v1/executions?workflowId=Ex90zUMSEWwVk4Wv&limit=1",
    headers={"X-N8N-API-KEY": N8N_KEY})
latest = (execs.get('data') or [{}])[0]
assert latest.get('status') == 'success', f"Scenario runner: {latest.get('status')}"
# Verify scenario report email sent to admin@syntharra.com
```

---

### PHASE 14 — Checkout Server Health

```python
# Verify Railway checkout server is responding
s, data = http("https://syntharra-checkout-production.up.railway.app/health")
assert s == 200, f"Checkout server health: HTTP {s}"

# Test that the checkout page loads
s, _ = http("https://syntharra-checkout-production.up.railway.app")
assert s == 200, "Checkout server not responding"
```

---

### PHASE 8 (FINAL) — Cleanup via 5-Min Delayed Webhook

**NEVER instant-delete. Always use this webhook:**

```python
cleanup_payload = {
    "company_name": TEST_COMPANY,
    "agent_ids": cleanup["agent_ids"],   # list[str]
    "flow_ids":  cleanup["flow_ids"],    # list[str]
}
s, resp = http("https://n8n.syntharra.com/webhook/e2e-test-cleanup", "POST", cleanup_payload)
assert s == 200, f"Cleanup webhook HTTP {s}"
print(f"\n⏱  5-minute window to inspect:")
print(f"   Company: {TEST_COMPANY}")
print(f"   Supabase: hvac_standard_agent / hvac_call_log")
print(f"   Retell agents: {cleanup['agent_ids']}")
print(f"   Retell flows:  {cleanup['flow_ids']}")
print(f"   Check emails in daniel@syntharra.com inbox")
```

**Cleanup workflow deletes from:**
- `hvac_standard_agent` (by company_name)
- `hvac_premium_agent` (by company_name)
- `stripe_payment_data` (by customer_name)
- `hvac_call_log` (by company_name)
- `hvac_premium_call_log` (by company_name)
- `client_subscriptions` (by company_name)
- Retell: DELETE `/delete-agent/{id}` for each agent_id
- Retell: DELETE `/delete-conversation-flow/{id}` for each flow_id

**Does NOT clean up:** `website_leads`, `billing_cycles`, `overage_charges`, `agreement_signatures`, `affiliate_applications` (these are deleted manually if needed)

---

## Full Pass Expected Output

```
============================================================
SYNTHARRA FULL E2E TEST  —  SELF CLEANING
Mode    : TEST
Company : Polar Peak HVAC 1234567890
Started : 2026-03-30 22:00:00 UTC
============================================================

[1]  Jotform Standard Submission ................ 52 fields
[2]  n8n Onboarding Execution .................. ✅ success
[3]  Supabase — ALL Fields ..................... 52 checks
[4]  Retell Agent Created & Published .......... ✅
[5]  Conversation Flow (13 nodes) .............. ✅
[6]  Call Processor + Dedup ................... ✅
[7]  Email Verification (manual inbox check) ... 17 emails expected
[8]  Stripe Gate — Test Mode .................. ✅ no Twilio purchase
[9]  Usage Minutes (optional) ................. ✅
[10] Ops Monitor Health ........................ all systems ✅
[11] Website Lead Form ......................... ✅
[12] Nightly Backup ............................ ✅
[13] Scenario Runner ........................... ✅
[14] Checkout Server ........................... ✅
[8F] Cleanup scheduled (5 min delay) ........... ✅

RESULT: 65/65 passed | 0 failed
✅ ALL SYSTEMS GO
```

---

## Common Failures & Fixes

| Failure | Cause | Fix |
|---|---|---|
| Webhook 404 | n8n workflow not active | Activate in n8n UI |
| exec status 'error' | Check n8n execution logs | `GET /executions/{id}` |
| Supabase row missing | Workflow errored before write | Check n8n exec + Retell API |
| agent_id empty | Retell creation failed | Check Retell API key validity |
| flow_id empty | Retell LLM creation failed | Check `Create Retell LLM` node |
| lead_score < 6 | Weak transcript | Use richer transcript with address + emergency |
| vulnerable_occupant false | Elderly not mentioned clearly | Add "elderly parents" to transcript |
| Dedup fails (2 rows) | Dedup logic missing in call processor | Check `Check Repeat Caller` node |
| Emails not received | SMTP2GO quota or wrong To | Check SMTP2GO dashboard |
| Stripe data missing | Checkout not completed (test mode skip) | Expected in test mode — use live mode for full test |
| DLQ has items | Call processor threw error mid-execution | Check `call_processor_dlq` table + fix error |
| Ops monitor alerts | Test data not cleaned up | Run cleanup webhook manually |
| Cleanup webhook 404 | `URbQPNQP26OIdYMo` not active | Activate in n8n UI |
| Geocode missing | Google Maps API key not set | Check Railway env `GOOGLE_MAPS_API_KEY` |
| Booking not created | Premium CRM/Calendar OAuth pending | Expected pre-OAuth — fix after OAuth setup |

---

## Extending the Test

When new features are added, update in this order:
1. Add Jotform field → Phase 1 table + Phase 3 assertion
2. Add n8n workflow → Phase 2 workflow table
3. Add Supabase column → Phase 3 field list for relevant table
4. Add email → Phase 7 email table
5. Update `e2e-test.py` with new assertions
6. The cleanup workflow handles all existing tables automatically — add new tables if needed

---

## Key IDs Quick Reference

| Item | ID / Value |
|---|---|
| Standard Jotform | `260795139953066` |
| Premium Jotform | `260819259556671` |
| Standard Onboarding n8n | `4Hx7aRdzMl5N0uJP` |
| Premium Onboarding n8n | `kz1VmwNccunRMEaF` |
| Std Call Processor n8n | `Kg576YtPM9yEacKn` |
| Prem Call Processor n8n | `STQ4Gt3rH8ptlvMi` |
| Stripe Workflow n8n | `xKD3ny6kfHL0HHXq` |
| E2E Cleanup n8n | `URbQPNQP26OIdYMo` |
| Arctic Breeze HVAC agent | `agent_4afbfdb3fcb1ba9569353af28d` |
| Demo Jake agent | `agent_b9d169e5290c609a8734e0bb45` |
| Demo Sophie agent | `agent_2723c07c83f65c71afd06e1d50` |
| Standard Retell webhook | `https://n8n.syntharra.com/webhook/retell-hvac-webhook` |
| Onboarding webhook | `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding` |
| E2E cleanup webhook | `https://n8n.syntharra.com/webhook/e2e-test-cleanup` |
| Supabase URL | `https://hgheyqwnrcvwtgngqdnq.supabase.co` |
| Ops Monitor API | `https://syntharra-ops-monitor-production.up.railway.app` |
| Checkout server | `https://syntharra-checkout-production.up.railway.app` |
