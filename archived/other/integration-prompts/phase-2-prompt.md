# SYNTHARRA PREMIUM — PHASE 2
# Run ONLY after Phase 1 is verified complete.
# Same rules: complete each task in order, publish n8n after every change,
# push GitHub after every file change, stop and flag missing credentials.

---

## CONTEXT

Phase 1 complete:
  ✅ Supabase schema updated
  ✅ Jotform Section 7 rebuilt
  ✅ Google Calendar OAuth routes live
  ✅ Outlook OAuth routes live (or flagged for Dan)
  ✅ Integration Connected Handler workflow active
  ✅ Google Calendar Dispatcher workflow active
  ✅ Premium Onboarding workflow updated with Switch node

Phase 2 adds native Type A and Type B integrations:
  Type A: Calendly, Acuity Scheduling, HubSpot Meetings
  Type B: Jobber

Each one follows the same pattern:
  1. OAuth route in syntharra-oauth-server
  2. Utility functions for availability + booking
  3. n8n Dispatcher sub-workflow
  4. Wire the Onboarding workflow branch (replace placeholder)

All credentials, email standards, and repo details same as Phase 1.
Retrieve from vault as needed.

---

## TASK 1 — JOBBER (Type B)

### 1a — OAuth Routes

In syntharra-oauth-server, create /routes/jobber.js

Check vault: service_name='Jobber', key_type='client_id' and 'client_secret'
If missing: skip Task 1, note for Dan, continue to Task 2.

Jobber OAuth:
  Auth URL: https://api.getjobber.com/api/oauth/authorize
  Token URL: https://api.getjobber.com/api/oauth/token
  Scopes: read_jobs write_jobs read_clients write_clients

GET /auth/jobber?agent_id={agent_id}
  state = agent_id
  Redirect to Jobber OAuth consent

GET /auth/jobber/callback?code={code}&state={agent_id}
  POST to token URL to exchange code
  Save to Supabase WHERE agent_id = state:
    oauth_access_token, oauth_refresh_token, oauth_token_expiry
    integration_status = 'connected', agent_status = 'connected'
  POST to n8n: { agent_id, integration_type: "jobber", platform: "Jobber" }
  Show success page (same style as Google success page)

### 1b — Utility file

Create /utils/jobber.js

Jobber API base: https://api.getjobber.com/api/graphql
Auth: Authorization: Bearer {access_token}
Content-Type: application/json

Function 1 — getAvailableSlots(agentId, daysAhead = 7)
  Fetch from Supabase: oauth_access_token, oauth_refresh_token,
    oauth_token_expiry, booking_hours, slot_duration_minutes,
    buffer_time_minutes, min_notice_hours
  
  Run token refresh if needed (same pattern as Google dispatcher)
  
  GraphQL query — get scheduled jobs for next N days:
  {
    jobs(filter: { startsBetween: { from: $start, to: $end } }) {
      nodes {
        id
        startAt
        endAt
        jobNumber
      }
    }
  }
  
  From the busy periods, calculate free slots within booking_hours.
  Apply slot_duration and buffer_time logic.
  Return max 6 formatted slots + ISO8601 times.

Function 2 — createJobRequest(agentId, callerName, callerPhone, jobType, scheduledStart)
  First check if client exists:
  GraphQL query clients by phone number.
  If not found: create client via mutation clientCreate.
  
  Create job via mutation jobCreate:
    client ID, job type = jobType in instructions,
    startAt = scheduledStart,
    endAt = scheduledStart + slot_duration_minutes
  
  Log to hvac_call_log: booking_id = job.id, booking_platform = 'jobber'
  Return: { job_id, job_number, confirmation }

Function 3 — refreshTokenIfNeeded(agentId, currentToken, expiryTime)
  Standard OAuth refresh to Jobber token URL
  Save new tokens to Supabase
  Return valid access token

### 1c — n8n Dispatcher

Create workflow: "Premium Dispatcher — Jobber"
Webhook: /webhook/dispatcher-jobber
Method: POST
Same body structure as Google dispatcher.

get_slots:
  Call getAvailableSlots via HTTP Request to a helper endpoint
  OR replicate the logic directly in n8n Function nodes
  Return { success: true, slots, slot_times }

create_booking:
  Call createJobRequest
  Return { success: true, booking_id, job_number, confirmation_time }

cancel_booking:
  Respond: { success: false, message: "Please transfer to office to cancel" }

Publish workflow.

### 1d — Wire Onboarding

Update workflow kz1VmwNccunRMEaF.
Find the Switch node added in Phase 1.
Replace the "jobber" branch placeholder (Node F) with real Jobber OAuth email:

SMTP2GO email:
  To: {{client_email}}
  Subject: "Connect Jobber — One Last Step"
  
  Light theme:
  [Logo block]
  
  Hi {{owner_first_name}},
  
  Your AI receptionist is ready. Connect your Jobber account
  and your AI will check your schedule and create job requests
  automatically — no manual entry needed.
  
  [Connect Jobber →]
  Button URL: {OAUTH_SERVER_URL}/auth/jobber?agent_id={{agent_id}}
  
  What happens:
  ✓ AI checks your Jobber schedule for free slots
  ✓ New job requests created automatically on each booking
  ✓ Customer and job details logged in Jobber
  
  Takes under 2 minutes.
  
  Questions? support@syntharra.com

After send: UPDATE agent_status = 'oauth_sent' in Supabase

Publish after changes.

---

## TASK 2 — CALENDLY (Type A)

### 2a — OAuth Routes

Check vault: service_name='Calendly', key_type='client_id' and 'client_secret'
If missing: skip Task 2, note for Dan, continue to Task 3.

Calendly OAuth:
  Auth URL: https://auth.calendly.com/oauth/authorize
  Token URL: https://auth.calendly.com/oauth/token
  Scopes: default

GET /auth/calendly?agent_id={agent_id} → redirect
GET /auth/calendly/callback
  Exchange code for tokens
  
  After getting tokens, immediately fetch the user's event type:
  GET https://api.calendly.com/event_types
  Headers: Authorization: Bearer {access_token}
  Save first active event type URI to Supabase as:
    -- add column if needed: calendly_event_type_uri TEXT
  
  Save tokens to Supabase, set statuses, POST to n8n, show success page.

### 2b — Utility file

Create /utils/calendly.js

Function 1 — getAvailableSlots(agentId, daysAhead = 7)
  Fetch from Supabase: oauth_access_token, calendly_event_type_uri,
    booking_hours, min_notice_hours
  
  GET https://api.calendly.com/event_type_available_times
  Params:
    event_type = calendly_event_type_uri
    start_time = NOW() ISO8601
    end_time = NOW() + daysAhead ISO8601
  Headers: Authorization: Bearer {access_token}
  
  Parse available_times array from response
  Filter within booking_hours
  Return max 6 formatted slots + ISO8601 times

Function 2 — createBooking(agentId, callerName, callerPhone, jobType, slotStartUTC)
  Note: Calendly's API does not support creating bookings directly
  via API without the invitee going through the UI.
  
  Workaround: Create a single-use scheduling link:
  POST https://api.calendly.com/scheduling_links
  Body: {
    max_event_count: 1,
    owner: calendly_event_type_uri,
    owner_type: "EventType"
  }
  
  Return the scheduling_url to the call processor.
  The AI tells the caller:
  "I'll send you a booking link by text right now —
   it's set up just for you and takes 30 seconds to confirm."
  
  Send SMS (via Telnyx when enabled, or log for now) with the link.
  Log to hvac_call_log: booking_platform = 'calendly', booking_link = scheduling_url
  
  Return: { success: true, booking_link: scheduling_url,
            message: "Booking link sent to customer" }

Note for dispatcher: Calendly requires a slightly different
AI conversation flow — instead of confirming a time on the call,
the AI generates a personalised link and sends it.
This is noted in the dispatcher response so the call processor
knows to use a different script branch.

### 2c — n8n Dispatcher

Create workflow: "Premium Dispatcher — Calendly"
Webhook: /webhook/dispatcher-calendly

get_slots: return available slots as normal (for AI to offer times)
create_booking: return scheduling link + flag link_sent: true
  The call processor uses link_sent flag to trigger SMS send

Publish workflow.

### 2d — Wire Onboarding

Replace "calendly" branch placeholder in onboarding Switch node:

SMTP2GO email:
  Subject: "Connect Calendly — One Last Step"
  Button URL: {OAUTH_SERVER_URL}/auth/calendly?agent_id={{agent_id}}
  
  Text:
  "Connect your Calendly account and your AI will check your
  real availability and send customers personalised booking
  links instantly during the call."

Publish after changes.

---

## TASK 3 — ACUITY SCHEDULING (Type A)

### 3a — OAuth Routes

Check vault: service_name='Acuity', key_type='client_id' and 'client_secret'
If missing: skip, note for Dan, continue to Task 4.

Acuity OAuth:
  Auth URL: https://acuityscheduling.com/oauth2/authorize
  Token URL: https://acuityscheduling.com/oauth2/token
  Scope: api-v1

GET /auth/acuity?agent_id={agent_id} → redirect
GET /auth/acuity/callback
  Exchange code
  
  After getting tokens, fetch appointment type ID:
  GET https://acuityscheduling.com/api/v1/appointment-types
  Headers: Authorization: Bearer {access_token}
  Save first active type ID to Supabase:
    -- add column if needed: acuity_appointment_type_id INTEGER
  
  Save tokens, set statuses, POST to n8n, show success page.

### 3b — Utility file

Create /utils/acuity.js

Function 1 — getAvailableSlots(agentId, daysAhead = 7)
  For each date in next 7 days:
    GET https://acuityscheduling.com/api/v1/availability/times
    Params: date=YYYY-MM-DD, appointmentTypeID={id}
    Headers: Authorization: Bearer {access_token}
  
  Collect all available slots across all dates
  Filter within booking_hours
  Return max 6 formatted + ISO8601 times

Function 2 — createBooking(agentId, callerName, callerPhone, jobType, datetime)
  POST https://acuityscheduling.com/api/v1/appointments
  Headers: Authorization: Bearer {access_token}
  Body:
  {
    appointmentTypeID: acuity_appointment_type_id,
    datetime: datetime,
    firstName: callerName.split(' ')[0],
    lastName: callerName.split(' ').slice(1).join(' ') || 'Customer',
    phone: callerPhone,
    notes: jobType
  }
  
  Log to hvac_call_log
  Return: { success: true, booking_id: response.id, confirmation_time: datetime }

### 3c — n8n Dispatcher

Create workflow: "Premium Dispatcher — Acuity"
Webhook: /webhook/dispatcher-acuity
Standard get_slots / create_booking / cancel_booking structure.
Publish.

### 3d — Wire Onboarding

Replace "acuity" branch placeholder:

SMTP2GO email:
  Subject: "Connect Acuity Scheduling — One Last Step"
  Button URL: {OAUTH_SERVER_URL}/auth/acuity?agent_id={{agent_id}}

Publish after changes.

---

## TASK 4 — HUBSPOT MEETINGS (Type A)

### 4a — OAuth Routes

Check vault: service_name='HubSpot', key_type='client_id' and 'client_secret'
If missing: skip, note for Dan, continue to Task 5.

HubSpot OAuth:
  Auth URL: https://app.hubspot.com/oauth/authorize
  Token URL: https://api.hubapi.com/oauth/v1/token
  Scopes: crm.objects.contacts.read scheduler.meetings

GET /auth/hubspot?agent_id={agent_id} → redirect
GET /auth/hubspot/callback
  Exchange code
  
  After tokens, fetch the client's meeting link slug:
  GET https://api.hubapi.com/scheduler/v3/meetings/meeting-links
  Headers: Authorization: Bearer {access_token}
  Save first active link's slug to Supabase:
    -- add column if needed: hubspot_meeting_slug TEXT
  
  Save tokens, statuses, POST to n8n, show success page.

### 4b — Utility file

Create /utils/hubspot.js

Function 1 — getAvailableSlots(agentId, daysAhead = 7)
  Fetch slug and token from Supabase
  
  GET /scheduler/v3/meetings/meeting-links/book/availability-page/{slug}
  Params: timezone = client timezone (default America/New_York)
  Headers: Authorization: Bearer {access_token}
  
  If near end of month, call again with monthOffset=1 to get next month too.
  
  Parse linkAvailability.linkAvailabilityByDuration
  Get the first duration key's availabilities array
  Each availability has startMillisUtc + endMillisUtc
  Convert to human readable + ISO8601
  Filter within booking_hours
  Return max 6 slots

Function 2 — createBooking(agentId, callerName, callerPhone, jobType, slotStartMillis)
  POST /scheduler/v3/meetings/meeting-links/book?timezone={tz}
  Headers: Authorization: Bearer {access_token}
  Body:
  {
    slug: hubspot_meeting_slug,
    startTime: slotStartMillis,
    firstName: callerName.split(' ')[0],
    lastName: callerName.split(' ').slice(1).join(' ') || 'Customer',
    email: callerPhone + '@syntharra-booking.com',
    formFields: []
  }
  
  Log to hvac_call_log
  Return: { success: true, booking_id: response.id || slotStartMillis }

### 4c — n8n Dispatcher

Create workflow: "Premium Dispatcher — HubSpot"
Webhook: /webhook/dispatcher-hubspot
Standard structure. Publish.

### 4d — Wire Onboarding

Replace "hubspot" branch placeholder:

SMTP2GO email:
  Subject: "Connect HubSpot — One Last Step"
  Button URL: {OAUTH_SERVER_URL}/auth/hubspot?agent_id={{agent_id}}

Publish after changes.

---

## TASK 5 — ADD SUPABASE COLUMNS FOR PHASE 2

Add any new columns needed by the integrations built above
if not already present:
  calendly_event_type_uri    TEXT
  acuity_appointment_type_id INTEGER
  hubspot_meeting_slug       TEXT

---

## TASK 6 — PHASE 2 VERIFICATION

For each integration, check and report:

JOBBER:
  ✅/❌ OAuth route deployed on Railway
  ✅/❌ Dispatcher workflow active in n8n
  ✅/❌ Onboarding workflow branch wired (not placeholder)

CALENDLY:
  ✅/❌ OAuth route deployed
  ✅/❌ Dispatcher workflow active
  ✅/❌ Onboarding branch wired

ACUITY:
  ✅/❌ OAuth route deployed
  ✅/❌ Dispatcher workflow active
  ✅/❌ Onboarding branch wired

HUBSPOT:
  ✅/❌ OAuth route deployed
  ✅/❌ Dispatcher workflow active
  ✅/❌ Onboarding branch wired

List any credentials that were missing (these need adding to vault before those integrations work).
List anything skipped.
Confirm Premium Onboarding workflow has no remaining placeholder branches
(or list which ones still need credentials).

---
END OF PHASE 2
