# SYNTHARRA PREMIUM PIPELINE — FULL REBUILD PROMPT
# Give this entire file to Claude Code.
# Work through each phase in strict order.
# After every n8n change: publish immediately.
# After every GitHub change: push immediately using SHA-fetch pattern.
# If any credential is missing: stop, state what is needed, continue to next task.

---

## SYSTEM AUDIT FINDINGS (Read before starting — this is the current state)

### SUPABASE — TABLES TO DELETE

The following tables have 0 rows and serve no active purpose.
They were created by a previous ops-monitor build that was never used.
DELETE ALL OF THESE:

```
deployment_gates          — 0 rows, unused ops-monitor table
system_health_checks      — 0 rows, unused ops-monitor table
workflow_deployments      — 0 rows, unused ops-monitor table
retell_deployments        — 0 rows, unused ops-monitor table
stripe_validation_checks  — 0 rows, unused ops-monitor table
environment_audit_log     — 0 rows, unused ops-monitor table
webhook_validation_checks — 0 rows, unused ops-monitor table
drift_detection_checks    — 0 rows, unused ops-monitor table
email_template_validation — 0 rows, unused ops-monitor table
deployment_history        — 0 rows, unused ops-monitor table
hvac_premium_agent        — 0 rows, DUPLICATE of hvac_standard_agent with premium columns bolted on
hvac_premium_call_log     — 27 rows BUT these are all test data, and we are consolidating to one call log table
agreement_signatures      — 0 rows, never used (agreement flow was never built)
affiliate_applications    — 0 rows, never used
call_processor_dlq        — 0 rows, dead letter queue never triggered
```

KEEP these tables (they're either actively used or will be needed):
```
hvac_standard_agent       — 1 row (Arctic Breeze), THE master client table for ALL plans
hvac_call_log             — 50 rows, active call log
stripe_payment_data       — 0 rows but active in Stripe workflow
client_subscriptions      — 0 rows but active in billing pipeline
billing_cycles            — 0 rows but active in billing pipeline
overage_charges           — 0 rows but active in billing pipeline
syntharra_vault           — 57 rows, credential store
website_leads             — 5 rows, active lead capture
blog_topics               — 41 rows, active blog system
email_digest              — 2 rows, active daily digest
agent_test_results        — 15 rows, active testing system
agent_pending_fixes       — 25 rows, active testing system
syntharra_activation_queue — 0 rows but needed for Premium activation flow
```

### SUPABASE — hvac_standard_agent IS THE SINGLE TABLE

Critical design decision: We use ONE table (`hvac_standard_agent`) for BOTH Standard and Premium clients.
The `plan_type` column distinguishes them (`standard` or `premium`).
The Phase 1 prompts already added the premium booking columns to this table. Confirmed present:
- scheduling_platform, integration_type, integration_status, agent_status
- oauth_access_token, oauth_refresh_token, oauth_token_expiry
- google_calendar_id, outlook_calendar_id
- bookable_job_types (JSONB), slot_duration_minutes, buffer_time_minutes, min_notice_hours
- booking_hours, booking_confirmation_method, cal_agreement

The old `hvac_premium_agent` table was a failed duplicate approach with different column names
(e.g. `crm_platform`, `calendar_platform`, `crm_access_token` etc). It must be deleted.

### SUPABASE — COLUMNS STILL NEEDED ON hvac_standard_agent

These columns are NOT yet present and will be needed for Phase 2 integrations:
```sql
calendly_event_type_uri    TEXT    — Calendly event type URI for availability lookups
acuity_appointment_type_id INTEGER — Acuity Scheduling appointment type ID
hubspot_meeting_slug       TEXT    — HubSpot meeting link slug
```

### N8N WORKFLOWS — CURRENT STATE (31 total)

ACTIVE & NEEDED (keep):
```
Kg576YtPM9yEacKn  HVAC Standard Call Processor
STQ4Gt3rH8ptlvMi  HVAC Premium Call Processor
4Hx7aRdzMl5N0uJP  HVAC Standard Onboarding
kz1VmwNccunRMEaF  HVAC Prem Onboarding (Premium onboarding — has Switch node from Phase 1)
a0IAwwUJP4YgwgjG  Premium — Integration Connected Handler (THE active one)
rGrnCr5mPFP2TIc7  Premium Dispatcher — Google Calendar
xKD3ny6kfHL0HHXq  Stripe Workflow
lXqt5anbJgsAMP7O  Send Welcome Email (Manual)
iLPb6ByiytisqUJC  HVAC Weekly Lead Report
Wa3pHRMwSjbZHqMC  Usage Alert Monitor (80% & 100% Warnings)
z1DNTjvTDAkExsX8  Monthly Minutes Calculator & Overage Billing
44WfbVmJ7Zihcwgs  Nightly GitHub Backup
13cOIXxvj83NfDqQ  Publish Retell Agent
73Y0MHVBu05bIm5p  Premium Integration Dispatcher
j8hExewOREmRp3Oq  Blog Auto-Publisher
4aulrlX1v8AtWwvC  Email Digest — Daily 6am GMT
QY1ZFtPJFsU5h6wQ  Website Lead → AI Readiness Score Email
hFU0ZeHae7EttCDK  Website Lead → Free Report Email
6LXpGffcWSvL6RxW  Weekly Newsletter - Syntharra
Eo8wwvZgeDm5gA9d  Newsletter Unsubscribe Webhook
Ex90zUMSEWwVk4Wv  HVAC Scenario Test Runner v4
ccOxdvghTsNqX8x0  HVAC Scenario Transcript Generator
eZHkfu9EYKHFoig0  HVAC Scenario: Process Single Scenario
3MMp9J8QN0YKgA6Q  SYNTHARRA_AGENT_TEST_RUNNER
ZAAtRETIIVZSMMDk  SYNTHARRA_FIX_APPROVER
AU8DD5r6i6SlYFnb  Auto-Enable MCP on All Workflows
URbQPNQP26OIdYMo  E2E Test Cleanup — 5 Min Delayed Delete
```

DELETE — duplicate Integration Connected Handler workflows (inactive):
```
IS5eC0SEzIv76TPQ  Premium — Integration Connected Handler (INACTIVE DUPLICATE)
OXuB3WR23fg0MmEu  Premium — Integration Connected Handler (INACTIVE DUPLICATE)
SziSvI1zl49cs3cQ  Premium — Integration Connected Handler (INACTIVE DUPLICATE)
```

REVIEW — test stub:
```
UKEoUeNqYvDDJv79  [TEST STUB] Retell Tool Dispatcher (active but may be superseded)
```

### JOTFORM — CURRENT STATE (Premium form 260819259556671)

Section 7 (Scheduling & Booking Setup) is FULLY BUILT with 9 fields:
- Q84: Section header
- Q85: scheduling_platform (radio)
- Q86: bookable_job_types (checkbox)
- Q87: slot_duration (dropdown)
- Q88: min_notice (dropdown)
- Q89: booking_hours (textbox)
- Q90: buffer_time (dropdown)
- Q91: confirmation_method (dropdown)
- Q92: cal_agreement (dropdown, conditional)

Sections 1-6 are intact. DO NOT TOUCH THEM.

### OAUTH SERVER — CURRENT STATE

Repo: Syntharra/syntharra-oauth-server (504 lines in server.js)
Deployed at: https://auth.syntharra.com (Railway)

Routes that EXIST and WORK:
- GET /auth/google?agent_id=xxx → Google Calendar OAuth
- GET /auth/outlook?agent_id=xxx → Microsoft Outlook OAuth
- GET /callback → Universal OAuth callback (handles both Google & Outlook)
- GET /connect?platform=xxx&agent=xxx → Legacy API key form
- POST /submit-key → Legacy API key submission

Routes that DO NOT EXIST yet (need building in Phase 2):
- GET /auth/jobber?agent_id=xxx
- GET /auth/calendly?agent_id=xxx
- GET /auth/acuity?agent_id=xxx
- GET /auth/hubspot?agent_id=xxx

Platform configs ARE defined in the PLATFORMS object for:
google_calendar, outlook, calendly, jobber, housecallpro, hubspot, gohighlevel

But only google_calendar and outlook have actual /auth/ route handlers.
The universal /callback handler already reads platform from state param,
so new platforms just need initiation routes + any post-callback logic.

### VAULT — OAUTH CREDENTIALS AVAILABLE

```
Google:    client_id ✅  client_secret ✅
Microsoft: client_id ✅  client_secret ✅
Jobber:    NOT IN VAULT — skip, flag for Dan
Calendly:  NOT IN VAULT — skip, flag for Dan
Acuity:    NOT IN VAULT — skip, flag for Dan
HubSpot:   NOT IN VAULT — skip, flag for Dan
```

### PREMIUM ONBOARDING WORKFLOW (kz1VmwNccunRMEaF)

This workflow is active and has:
- Webhook trigger for Jotform Premium submissions
- Data parsing nodes
- Supabase insert
- Switch node routing by integration_type
- Google Calendar OAuth email branch
- Outlook OAuth email branch
- Placeholder email branch for other platforms

The Switch node branches for jobber, calendly, acuity, hubspot currently
send a generic "we'll be in touch" placeholder email.

---

## CREDENTIALS (use throughout all phases)

Retrieve keys from Supabase syntharra_vault table.
Query pattern:
  SELECT key_value FROM syntharra_vault
  WHERE service_name = '{SERVICE}' AND key_type = '{TYPE}'

Known direct values:
  Jotform API key: {{JOTFORM_API_KEY}}
  GitHub token: {{GITHUB_TOKEN}}
  SMTP2GO API key: {{SMTP2GO_API_KEY}}
  Retell API key: {{RETELL_API_KEY}}

Fixed values:
  Supabase URL: https://hgheyqwnrcvwtgngqdnq.supabase.co
  n8n instance: https://n8n.syntharra.com
  Premium Jotform ID: 260819259556671
  Premium Onboarding workflow ID: kz1VmwNccunRMEaF
  OAuth server repo: Syntharra/syntharra-oauth-server
  OAuth server URL: https://auth.syntharra.com
  Railway API token: {{RAILWAY_API_TOKEN}}

---

## EMAIL STANDARDS (apply to every email — non-negotiable)

Light theme ONLY:
  Outer background: #F7F7FB
  Card background: #ffffff
  Primary text: #1A1A2E
  Secondary text: #4A4A6A
  Accent/buttons: #6C63FF
  Border: #E5E7EB

Logo block (copy exactly — nested table structure):
  Icon URL: https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png
  "Syntharra" — Inter 700 16px #0f0f1a
  "GLOBAL AI SOLUTIONS" — Inter 600 7.5px #6C63FF uppercase

Sender: noreply@syntharra.com
Support: support@syntharra.com ONLY (never "reply to this email")
All content dynamic — zero hardcoded company names, agent names, or phone numbers

---

# PHASE 1 — CLEANUP & CONSOLIDATION

## TASK 1.1 — DELETE UNUSED SUPABASE TABLES

Drop these tables in this order (respecting any FK constraints):

```sql
DROP TABLE IF EXISTS overage_charges CASCADE;
-- Wait, overage_charges IS needed. Do NOT drop it.
```

Actually drop ONLY these:
```sql
DROP TABLE IF EXISTS deployment_gates CASCADE;
DROP TABLE IF EXISTS system_health_checks CASCADE;
DROP TABLE IF EXISTS workflow_deployments CASCADE;
DROP TABLE IF EXISTS retell_deployments CASCADE;
DROP TABLE IF EXISTS stripe_validation_checks CASCADE;
DROP TABLE IF EXISTS environment_audit_log CASCADE;
DROP TABLE IF EXISTS webhook_validation_checks CASCADE;
DROP TABLE IF EXISTS drift_detection_checks CASCADE;
DROP TABLE IF EXISTS email_template_validation CASCADE;
DROP TABLE IF EXISTS deployment_history CASCADE;
DROP TABLE IF EXISTS hvac_premium_agent CASCADE;
DROP TABLE IF EXISTS hvac_premium_call_log CASCADE;
DROP TABLE IF EXISTS agreement_signatures CASCADE;
DROP TABLE IF EXISTS affiliate_applications CASCADE;
DROP TABLE IF EXISTS call_processor_dlq CASCADE;
```

After dropping, verify by listing all remaining public tables.
Expected remaining: hvac_standard_agent, hvac_call_log, stripe_payment_data,
client_subscriptions, billing_cycles, overage_charges, syntharra_vault,
website_leads, blog_topics, email_digest, agent_test_results,
agent_pending_fixes, syntharra_activation_queue

## TASK 1.2 — ADD MISSING COLUMNS TO hvac_standard_agent

Check first, then add only if missing:

```sql
ALTER TABLE hvac_standard_agent
  ADD COLUMN IF NOT EXISTS calendly_event_type_uri TEXT,
  ADD COLUMN IF NOT EXISTS acuity_appointment_type_id INTEGER,
  ADD COLUMN IF NOT EXISTS hubspot_meeting_slug TEXT;
```

Verify all premium-related columns exist after this.

## TASK 1.3 — DELETE DUPLICATE N8N WORKFLOWS

Delete these three INACTIVE duplicate "Integration Connected Handler" workflows:
- IS5eC0SEzIv76TPQ
- OXuB3WR23fg0MmEu
- SziSvI1zl49cs3cQ

Use n8n API:
  DELETE https://n8n.syntharra.com/api/v1/workflows/{id}
  Header: X-N8N-API-KEY: {n8n_api_key}

Verify the ACTIVE one remains: a0IAwwUJP4YgwgjG

## TASK 1.4 — VERIFY EXISTING PREMIUM WORKFLOWS

Check that these are all active and have webhook triggers responding:

1. Premium Onboarding (kz1VmwNccunRMEaF) — ACTIVE ✅
2. Integration Connected Handler (a0IAwwUJP4YgwgjG) — ACTIVE ✅
3. Premium Dispatcher — Google Calendar (rGrnCr5mPFP2TIc7) — ACTIVE ✅

For each, fetch the workflow via n8n API and confirm:
- Webhook node exists with correct path
- Key nodes are present (Switch, Supabase, SMTP2GO etc)

Report: ✅/❌ for each workflow

## TASK 1.5 — VERIFY JOTFORM SECTION 7

Fetch form 260819259556671 via Jotform API.
Confirm all 9 Section 7 fields are present (Q84-Q92).
Confirm Sections 1-6 are untouched.
Report field names and IDs.

## TASK 1.6 — VERIFY OAUTH SERVER

Test that the OAuth server is responding:
  GET https://auth.syntharra.com/health
  Expected: { status: 'ok' }

  GET https://auth.syntharra.com/auth/google?agent_id=test_audit
  Expected: redirect to Google OAuth (302)

  GET https://auth.syntharra.com/auth/outlook?agent_id=test_audit
  Expected: redirect to Microsoft OAuth (302)

Report: ✅/❌ for each

---

# PHASE 1 CHECKPOINT

Before proceeding to Phase 2, provide a full report:
- Tables deleted: list
- Tables remaining: list
- Columns added: list
- Duplicate workflows deleted: list
- Workflow health: ✅/❌ per workflow
- Jotform status: ✅/❌
- OAuth server status: ✅/❌

Wait for Dan's confirmation before proceeding to Phase 2.

---

# PHASE 2 — GOOGLE CALENDAR INTEGRATION (Full End-to-End)

Phase 2 focuses ONLY on Google Calendar — the first and most important integration.
We get this working perfectly before touching any other platform.

## TASK 2.1 — VERIFY GOOGLE OAUTH FLOW

The OAuth server already has /auth/google and /callback routes.
After the callback:
1. Tokens are saved to hvac_standard_agent (oauth_access_token, oauth_refresh_token, oauth_token_expiry)
2. integration_status is set to 'connected'
3. A POST is sent to n8n webhook /webhook/integration-connected

Verify this by reading the server.js callback handler code.
Check the POST to n8n includes: { agent_id, integration_type: "google", platform: "Google Calendar" }

If anything is wrong or missing, fix it in server.js and push to GitHub.
Railway auto-deploys from the repo.

## TASK 2.2 — VERIFY/FIX GOOGLE CALENDAR DISPATCHER

Fetch workflow rGrnCr5mPFP2TIc7 ("Premium Dispatcher — Google Calendar").
This workflow should handle:

**get_slots action:**
1. Receive POST with { agent_id, action: "get_slots", caller_name, caller_phone, job_type }
2. Fetch client record from hvac_standard_agent by agent_id
3. Check if oauth_access_token is expired, refresh if needed using Google OAuth
4. Call Google Calendar freeBusy API for next 7 days
5. Parse busy periods, calculate free slots within booking_hours
6. Apply slot_duration_minutes, buffer_time_minutes, min_notice_hours
7. Return max 6 slots as human-readable strings + ISO8601 times

**create_booking action:**
1. Receive POST with { agent_id, action: "create_booking", caller_name, caller_phone, job_type, selected_slot }
2. Token refresh if needed
3. Create Google Calendar event with:
   - Summary: "{job_type} — {caller_name}"
   - Description: "Booked by Syntharra AI\nCustomer: {caller_name}\nPhone: {caller_phone}\nJob: {job_type}"
   - Start/end based on selected_slot and slot_duration_minutes
4. Log to hvac_call_log
5. Return { success: true, booking_id, confirmation_time }

**cancel_booking action:**
1. Return { success: false, message: "Please transfer to office to cancel" }

Review the existing workflow. Fix any issues. Ensure Google client_id and client_secret
are fetched from syntharra_vault (not hardcoded). Publish after any changes.

## TASK 2.3 — VERIFY/FIX INTEGRATION CONNECTED HANDLER

Fetch workflow a0IAwwUJP4YgwgjG.
This workflow fires when a client completes OAuth.

It should:
1. Receive POST with { agent_id, integration_type, platform }
2. Fetch client record from hvac_standard_agent
3. Update integration_status = 'connected' in Supabase
4. Insert row into syntharra_activation_queue
5. Send notification email to onboarding@syntharra.com
6. Send holding email to client

Review and fix any issues. Publish after changes.

## TASK 2.4 — VERIFY/FIX PREMIUM ONBOARDING WORKFLOW

Fetch workflow kz1VmwNccunRMEaF.
This workflow fires when a Premium Jotform is submitted.

It should:
1. Receive Jotform webhook POST
2. Parse all Section 1-7 fields including booking fields
3. Map scheduling_platform to integration_type:
   - "Google Calendar..." → "google"
   - "Microsoft Outlook..." → "outlook"
   - "Jobber..." → "jobber"
   - "Calendly..." → "calendly"
   - "Acuity..." → "acuity"
   - "HubSpot..." → "hubspot"
   - "Apple Calendar..." or "We don't have..." → "manual"
4. INSERT or UPDATE hvac_standard_agent with ALL fields including:
   - All Section 1-6 business info fields
   - plan_type = 'premium'
   - scheduling_platform, integration_type
   - slot_duration_minutes (parsed from dropdown)
   - buffer_time_minutes (parsed from dropdown)
   - min_notice_hours (parsed from dropdown)
   - booking_hours
   - bookable_job_types (as JSONB array)
   - booking_confirmation_method
   - cal_agreement
5. Switch by integration_type:
   - "google" → Send Google OAuth email with button to auth.syntharra.com/auth/google?agent_id={agent_id}
   - "outlook" → Send Outlook OAuth email
   - All others → Send placeholder "we'll be in touch" email
6. After email sent → UPDATE agent_status = 'oauth_sent'

Review the existing workflow carefully. The Jotform field names must match
EXACTLY what the form sends. Check the mapping of Jotform question names
to Supabase column names. Fix any mismatches.

Key Jotform field names (from the actual form):
```
q4_hvacCompany          → company_name
q54_ownerName           → owner_name
q5_emailAddress         → client_email
q6_mainCompany          → company_phone
q7_companyWebsite       → website
q8_yearsIn              → years_in_business
q34_timezone            → timezone
q10_aiAgent10           → agent_name
q11_aiVoice             → voice_gender
q75_greetingStyle       → custom_greeting (if "Custom")
q76_customGreetingText  → custom_greeting (actual text)
q13_servicesOffered     → services_offered
q14_brandsequipmentServiced → brands_serviced
q16_primaryService      → service_area
q40_serviceAreaRadius   → service_area_radius
q29_certifications      → certifications
q28_licensedAnd         → licensed_insured
q17_businessHours       → business_hours
q18_typicalResponse     → response_time
q20_247Emergency        → emergency_service
q21_emergencyAfterhours → emergency_phone
q22_afterhoursBehavior  → after_hours_behavior
q42_pricingPolicy       → pricing_policy
q41_diagnosticFee       → diagnostic_fee
q43_standardFees        → standard_fees
q24_freeEstimates       → free_estimates
q26_serviceWarranties   → warranty
q27_warrantyDetails     → warranty_details
q25_financingAvailable  → financing_available
q44_financingDetails    → financing_details
q45_paymentMethods      → payment_methods
q46_maintenancePlans    → maintenance_plans
q57_doNotServiceList    → do_not_service
q48_transferPhone       → transfer_phone
q49_transferTriggers    → transfer_triggers
q50_transferBehavior    → transfer_behavior
q31_leadContact         → lead_contact_method
q32_leadNotification    → lead_phone
q33_leadNotification33  → lead_email
q78_additionalNotifications → (conditional gate)
q79_notifSms2           → notification_sms_2
q80_notifSms3           → notification_sms_3
q81_notifEmail2         → notification_email_2
q82_notifEmail3         → notification_email_3
q39_companyTagline      → company_tagline
q51_uniqueSellingPoints → unique_selling_points
q52_currentPromotion    → current_promotion
q53_seasonalServices    → seasonal_services
q55_googleReviewRating  → google_review_rating
q56_googleReviewCount   → google_review_count
q58_membershipProgramName → membership_program
q37_additionalInfo      → additional_info
q85_scheduling_platform → scheduling_platform
q86_bookable_job_types  → bookable_job_types (JSONB)
q87_slot_duration       → slot_duration_minutes (parse int)
q88_min_notice          → min_notice_hours (map to hours)
q89_booking_hours       → booking_hours
q90_buffer_time         → buffer_time_minutes (parse int)
q91_confirmation_method → booking_confirmation_method
q92_cal_agreement       → cal_agreement
```

Publish after any changes.

## TASK 2.5 — END-TO-END TEST (Google Calendar)

Simulate a full Premium onboarding:

Step 1 — Create a test submission:
POST to the Premium Onboarding webhook (kz1VmwNccunRMEaF) with test data:
```json
{
  "q4_hvacCompany": "Test Premium HVAC",
  "q54_ownerName": "Test Owner",
  "q5_emailAddress": "test@syntharra.com",
  "q6_mainCompany": "5550001234",
  "q34_timezone": "Eastern Time ET",
  "q85_scheduling_platform": "Google Calendar — we manage our schedule in Google Calendar",
  "q86_bookable_job_types": ["AC Repair / Service Call", "Maintenance / Tune-up"],
  "q87_slot_duration": "60 minutes",
  "q88_min_notice": "2 hours",
  "q89_booking_hours": "Mon-Fri 8am-5pm",
  "q90_buffer_time": "30 minutes",
  "q91_confirmation_method": "Both Email & SMS",
  "q10_aiAgent10": "Sarah",
  "q11_aiVoice": "Female",
  "q13_servicesOffered": "AC Repair, Heating, Maintenance",
  "q16_primaryService": "Miami FL",
  "q17_businessHours": "Mon-Fri 8am-6pm",
  "q48_transferPhone": "5550009999"
}
```

Step 2 — Check n8n execution:
- Verify onboarding workflow ran successfully
- Verify Supabase row was created with plan_type='premium' and integration_type='google'
- Verify agent_status was set to 'oauth_sent'
- Check that the Google OAuth email node fired

Step 3 — Simulate OAuth callback:
POST to the Integration Connected Handler webhook:
```json
{
  "agent_id": "{the agent_id from Step 2}",
  "integration_type": "google",
  "platform": "Google Calendar"
}
```
Verify:
- Handler workflow ran
- Activation queue has an entry
- Notification email node fired

Step 4 — Test the dispatcher:
POST to the Google Calendar Dispatcher webhook:
```json
{
  "agent_id": "{the agent_id from Step 2}",
  "action": "get_slots",
  "caller_name": "Test Caller",
  "caller_phone": "5550001111",
  "job_type": "AC Repair"
}
```
This will likely fail (no real OAuth tokens) — that's expected.
Just verify the workflow executed and the error is about invalid token, not a structural issue.

Step 5 — Clean up test data:
DELETE FROM hvac_standard_agent WHERE company_name = 'Test Premium HVAC';
DELETE FROM syntharra_activation_queue WHERE company_name = 'Test Premium HVAC';

## PHASE 2 CHECKPOINT

Report:
- Google OAuth flow: ✅/❌ (server routes working)
- Google Calendar Dispatcher: ✅/❌ (workflow structure correct)
- Integration Connected Handler: ✅/❌ (workflow firing correctly)
- Premium Onboarding: ✅/❌ (all field mappings correct)
- End-to-end test: ✅/❌ (data flows correctly through all stages)
- List any issues found and fixed
- List any issues still remaining

Wait for Dan's confirmation before proceeding to Phase 3.

---

# PHASE 3 — AUTO-ACTIVATION & YOU'RE LIVE EMAIL

## TASK 3.1 — UPDATE INTEGRATION CONNECTED HANDLER FOR AUTO-ACTIVATION

Fetch workflow a0IAwwUJP4YgwgjG.
After the existing nodes (holding email to client, notification to Dan), add:

**New Node — HTTP Request: Run test booking**
POST to the correct dispatcher based on integration_type from the Supabase record:
  google → https://n8n.syntharra.com/webhook/dispatcher-google
  outlook → https://n8n.syntharra.com/webhook/dispatcher-outlook

Body:
```json
{
  "agent_id": "{{agent_id}}",
  "action": "get_slots",
  "caller_name": "Syntharra Test",
  "caller_phone": "0000000000",
  "job_type": "Onboarding Verification Test"
}
```
Timeout: 15 seconds. On timeout/error: treat as failed.

**New Node — IF: test returned slots?**
Condition: response body has slots array with length > 0
Yes → auto-activate
No → manual review path

**Auto-activate path:**
1. UPDATE hvac_standard_agent SET integration_status='active', agent_status='active' WHERE agent_id={{agent_id}}
2. UPDATE syntharra_activation_queue SET activated_at=NOW(), activated_by='auto', integration_status='active' WHERE agent_id={{agent_id}} AND activated_at IS NULL
3. Trigger You're Live email (POST to /webhook/send-live-email with { agent_id })

**Manual review path:**
1. UPDATE hvac_standard_agent SET integration_status='failed', agent_status='failed'
2. UPDATE syntharra_activation_queue SET notes='Auto test failed — manual review needed'
3. Send alert email to onboarding@syntharra.com with failure details
4. Send updated holding email to client saying "We're just completing a final check"

Publish after changes.

## TASK 3.2 — CREATE YOU'RE LIVE EMAIL WORKFLOW

Create new n8n workflow: "Premium — Send You're Live Email"
Webhook trigger: /webhook/send-live-email
Method: POST
Body: { agent_id }

Nodes:
1. Webhook trigger
2. Supabase fetch — get all client details from hvac_standard_agent
3. Function — extract first name, build dashboard URL
4. SMTP2GO — send the "You're Live" email

The email should be polished and celebratory:
- Subject: "🎉 Your AI Receptionist Is Live — {{company_name}}"
- From: noreply@syntharra.com
- Light theme, centered logo block
- Large heading: "You're Live, {{first_name}}! 🎉"
- Subheading about 24/7 call handling
- 3 feature highlights (24/7 Answering, Automatic Booking, Instant Notifications)
- "Your AI Details" box with agent name, scheduling platform, booking hours
- Primary CTA: "View Your Dashboard →" linking to syntharra.com/dashboard.html?agent_id={{agent_id}}
- Secondary CTA: "Test Your AI Now →" (tel: link to agent phone if available)
- Note about weekly reports arriving every Monday
- Footer with support@syntharra.com

5. Supabase — log activation event to hvac_call_log (event_type='agent_activated')

Publish workflow.

## TASK 3.3 — DAILY TOKEN REFRESH WORKFLOW

Create new n8n workflow: "Premium — Daily Token Refresh"
Trigger: Schedule node — every day at 02:00 UTC

1. Fetch all active premium clients with OAuth tokens from hvac_standard_agent
   WHERE agent_status = 'active' AND integration_type IN ('google', 'outlook') AND oauth_refresh_token IS NOT NULL
2. For each client, check if token expires within 2 days
3. If needs refresh:
   - Google: POST to https://oauth2.googleapis.com/token with refresh_token + Google client creds
   - Outlook: POST to https://login.microsoftonline.com/common/oauth2/v2.0/token
4. If refresh successful: update tokens in Supabase
5. If refresh fails:
   - SET integration_status = 'token_expired'
   - Send alert to onboarding@syntharra.com
   - Send reconnect email to client with link to re-auth

Publish workflow.

## PHASE 3 CHECKPOINT

Report:
- Integration Connected Handler updated with auto-activation: ✅/❌
- You're Live email workflow created and active: ✅/❌
- Daily Token Refresh workflow created and active: ✅/❌
- List any issues

Wait for Dan's confirmation before proceeding to Phase 4.

---

# PHASE 4 — ADDITIONAL PLATFORM DISPATCHERS

This phase adds OAuth routes and dispatcher workflows for other platforms.
ONLY build platforms where OAuth credentials exist in the vault.

For each platform below, FIRST check syntharra_vault for credentials.
If credentials are missing, SKIP that platform entirely and note it for Dan.

## TASK 4.1 — OUTLOOK DISPATCHER

OAuth routes already exist in server.js. Build the dispatcher workflow.

Create workflow: "Premium Dispatcher — Outlook"
Webhook: /webhook/dispatcher-outlook

Same pattern as Google Calendar dispatcher but using Microsoft Graph API:
- Token refresh via Microsoft endpoint
- Get busy times via POST https://graph.microsoft.com/v1.0/me/calendar/getSchedule
- Create events via POST https://graph.microsoft.com/v1.0/me/calendars/{id}/events

Publish workflow.

## TASK 4.2 — JOBBER (if credentials available)

Check vault for service_name='Jobber'. If missing, skip.

1. Add /auth/jobber route to server.js (initiation + callback handling)
2. Create workflow: "Premium Dispatcher — Jobber" at /webhook/dispatcher-jobber
   - Jobber uses GraphQL API at https://api.getjobber.com/api/graphql
   - get_slots: query scheduled jobs, calculate free periods
   - create_booking: create client (if needed) + job via mutations
3. Update Premium Onboarding workflow — replace jobber placeholder branch with real OAuth email
4. Push server.js to GitHub

## TASK 4.3 — CALENDLY (if credentials available)

Check vault for service_name='Calendly'. If missing, skip.

1. Add /auth/calendly route to server.js
   - After token exchange, fetch event types and save first active URI to calendly_event_type_uri
2. Create workflow: "Premium Dispatcher — Calendly" at /webhook/dispatcher-calendly
   - get_slots: GET /event_type_available_times
   - create_booking: POST /scheduling_links to generate single-use link
   - Return link_sent: true flag so call processor knows to send SMS link
3. Update onboarding workflow — replace calendly placeholder
4. Push to GitHub

## TASK 4.4 — ACUITY SCHEDULING (if credentials available)

Check vault for service_name='Acuity'. If missing, skip.

1. Add /auth/acuity route to server.js
   - After token exchange, fetch appointment types, save first active ID to acuity_appointment_type_id
2. Create workflow: "Premium Dispatcher — Acuity" at /webhook/dispatcher-acuity
   - get_slots: GET /availability/times per date
   - create_booking: POST /appointments
3. Update onboarding workflow — replace acuity placeholder
4. Push to GitHub

## TASK 4.5 — HUBSPOT MEETINGS (if credentials available)

Check vault for service_name='HubSpot'. If missing, skip.

1. Add /auth/hubspot route to server.js
   - After token exchange, fetch meeting links, save slug to hubspot_meeting_slug
2. Create workflow: "Premium Dispatcher — HubSpot" at /webhook/dispatcher-hubspot
   - get_slots: GET meeting link availability
   - create_booking: POST to book meeting slot
3. Update onboarding workflow — replace hubspot placeholder
4. Push to GitHub

## PHASE 4 CHECKPOINT

For each integration, report:
```
GOOGLE:   OAuth ✅  Dispatcher ✅  Onboarding branch ✅
OUTLOOK:  OAuth ✅  Dispatcher ✅/❌  Onboarding branch ✅
JOBBER:   OAuth ✅/❌/SKIPPED  Dispatcher ✅/❌/SKIPPED  Onboarding branch ✅/❌/SKIPPED
CALENDLY: OAuth ✅/❌/SKIPPED  Dispatcher ✅/❌/SKIPPED  Onboarding branch ✅/❌/SKIPPED
ACUITY:   OAuth ✅/❌/SKIPPED  Dispatcher ✅/❌/SKIPPED  Onboarding branch ✅/❌/SKIPPED
HUBSPOT:  OAuth ✅/❌/SKIPPED  Dispatcher ✅/❌/SKIPPED  Onboarding branch ✅/❌/SKIPPED
```

List any credentials needed from Dan.
List any remaining placeholder branches in onboarding workflow.

---

# PHASE 5 — ADMIN DASHBOARD ACTIVATION QUEUE

## TASK 5.1 — ADD ACTIVATION QUEUE TO ADMIN DASHBOARD

Fetch current admin dashboard from GitHub:
  Repo: Syntharra/syntharra-admin
  File: index.html

Add a new section: "Activation Queue"
Position: near the top, after system status, before Clients list.

Query: syntharra_activation_queue WHERE activated_at IS NULL ORDER BY created_at DESC

Display as a styled table matching existing admin dashboard design:
Columns: Company | Platform | Integration | Connected | Status | Actions

Actions per row:
- [✅ Activate] button: POST to /webhook/send-live-email, update queue + agent status
- [🔍 Test] button: POST to correct dispatcher with get_slots, show result in modal
- [📝 Notes] button: modal with text input, save to queue notes column

If empty: show "✅ All clients are active — nothing pending"

Add badge on nav item showing pending count.
Auto-refresh every 60 seconds.

Push to GitHub after changes.

---

# FINAL REPORT

After all phases, provide:

1. Complete table inventory (what exists, row counts)
2. Complete workflow inventory (what exists, active status)
3. Integration matrix — which platforms are fully working end-to-end
4. List of credentials still needed from Dan
5. List of any remaining manual steps
6. Recommended go-live actions:
   a. Get missing OAuth credentials from Dan
   b. Switch Stripe to live mode
   c. Test one real Premium client through full flow
   d. Monitor activation queue for first 48 hours

---
END OF PROMPT
