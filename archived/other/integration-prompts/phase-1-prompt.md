# SYNTHARRA PREMIUM — PHASE 1
# Feed this entire prompt into Claude Code.
# Work through each task in strict order.
# Complete and verify each task before moving to the next.
# After every n8n change: publish immediately.
# After every GitHub change: push immediately using SHA-fetch pattern.
# If any credential is missing: stop, state what is needed, continue to next task.

---

## CONTEXT

Syntharra sells AI phone receptionists to HVAC contractors.
Premium clients ($997/mo) get full booking integration.
The AI (on Retell) handles calls and books appointments in real time.

Three integration types:

TYPE A — Scheduling platforms (client has own account, OAuth per client):
  Calendly, Acuity Scheduling, HubSpot Meetings

TYPE B — FSM/CRM platforms (client has own account, OAuth per client):
  Jobber — AI creates job requests via Jobber API

TYPE C — Calendar direct (Google OAuth or Microsoft OAuth per client):
  Google Calendar → Google OAuth (already partially built)
  Microsoft Outlook / Office 365 → Microsoft OAuth (build this phase)
  Apple Calendar / No system → ask client to connect Google or Outlook instead
  
  For Type C: AI reads their real calendar for availability,
  books directly into it. Client connects via OAuth during onboarding.
  No third-party platform required.

---

## CREDENTIALS

Retrieve all keys from Supabase syntharra_vault table.
Query pattern:
  GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault
    ?service_name=eq.{SERVICE}&key_type=eq.{TYPE}&select=key_value
  Headers: apikey + Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}

Known vault entries:
  Supabase service role key: service_name='Supabase', key_type='service_role_key'
  n8n API key: service_name='n8n Railway', key_type='api_key'
  Retell API key: service_name='Retell AI', key_type='api_key'
  Jotform API key: 18907cfb3b4b3be3ac47994683148728 (use directly)
  GitHub token: {{GITHUB_TOKEN — query syntharra_vault service_name=GitHub key_type=personal_access_token}} (use directly)
  SMTP2GO key: api-0BE30DA64A074BC79F28BE6AEDC9DB9E (use directly)
  Google OAuth: service_name='Google', key_type='client_id' and 'client_secret'
  Microsoft OAuth: service_name='Microsoft', key_type='client_id' and 'client_secret'
    (if missing, skip Outlook route and note it for Dan)

Fixed values:
  Supabase URL: https://hgheyqwnrcvwtgngqdnq.supabase.co
  n8n instance: https://n8n.syntharra.com
  Premium Jotform ID: 260819259556671
  Premium Onboarding workflow ID: kz1VmwNccunRMEaF
  OAuth server repo: Syntharra/syntharra-oauth-server
  Railway API token: 1eb854a8-eb65-4598-bce1-590c5639955a
  OAuth server URL: https://syntharra-oauth-server-production.up.railway.app

---

## EMAIL STANDARDS (apply to every email — non-negotiable)

Light theme ONLY:
  Outer background: #F7F7FB
  Card background: #ffffff
  Primary text: #1A1A2E
  Accent/buttons: #6C63FF
  Border: #E5E7EB

Logo block (copy exactly — nested table structure):
  Icon URL: https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png
  "Syntharra" — Inter 700 16px #0f0f1a
  "GLOBAL AI SOLUTIONS" — Inter 600 7.5px #6C63FF uppercase

Sender: noreply@syntharra.com
Support: support@syntharra.com ONLY
All content dynamic — zero hardcoded company/agent names/phone numbers

---

## TASK 1 — SUPABASE SCHEMA

Add columns to hvac_standard_agent if they don't exist.
Check first: SELECT column_name FROM information_schema.columns
             WHERE table_name = 'hvac_standard_agent';

Add these columns:
  scheduling_platform          TEXT
    -- raw Jotform answer e.g. "Google Calendar", "Microsoft Outlook", "Jobber"
  integration_type             TEXT
    -- "google" | "outlook" | "calendly" | "jobber" | "acuity" | "hubspot" | "manual"
  integration_status           TEXT    DEFAULT 'pending'
    -- "pending" | "oauth_sent" | "connected" | "active" | "failed"
  agent_status                 TEXT    DEFAULT 'pending'
    -- "pending" | "oauth_sent" | "connected" | "active" | "paused"
  oauth_access_token           TEXT
  oauth_refresh_token          TEXT
  oauth_token_expiry           TIMESTAMPTZ
  google_calendar_id           TEXT
    -- the specific calendar ID to read/write (defaults to 'primary')
  outlook_calendar_id          TEXT
  bookable_job_types           JSONB
  slot_duration_minutes        INTEGER DEFAULT 60
  buffer_time_minutes          INTEGER DEFAULT 30
  min_notice_hours             INTEGER DEFAULT 2
  booking_hours                TEXT
  booking_confirmation_method  TEXT    DEFAULT 'both'
  cal_agreement                TEXT

Create new table:
  CREATE TABLE IF NOT EXISTS syntharra_activation_queue (
    id                   UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id             TEXT         NOT NULL,
    company_name         TEXT         NOT NULL,
    owner_name           TEXT,
    owner_email          TEXT,
    scheduling_platform  TEXT,
    integration_type     TEXT,
    integration_status   TEXT         DEFAULT 'pending',
    created_at           TIMESTAMPTZ  DEFAULT NOW(),
    activated_at         TIMESTAMPTZ,
    activated_by         TEXT,
    notes                TEXT
  );

Verify all exist before continuing.

---

## TASK 2 — UPDATE JOTFORM SECTION 7

Fetch current form state first:
  GET https://api.jotform.com/form/260819259556671/questions?apiKey=18907cfb3b4b3be3ac47994683148728

Identify all existing Section 7 fields by finding the control_head
with text containing "Booking" or "Integration" or "Section 7".
Note their IDs. Delete/replace ONLY those fields.
Do NOT touch Sections 1-6 under any circumstances.

Build new Section 7 via Jotform REST API:

FIELD 1 — Section header (control_head)
  Text: "Section 7: Scheduling & Booking Setup"
  Subheader: "Tell us how your team manages appointments.
  This sets up how your AI books jobs automatically — takes 2 minutes."

FIELD 2 — scheduling_platform (control_radio, REQUIRED)
  Name: scheduling_platform
  Label: "How do your technicians manage their schedule?"
  Options:
    "Google Calendar — we manage our schedule in Google Calendar"
    "Microsoft Outlook / Office 365 — we use Outlook for our calendar"
    "Jobber — we schedule and dispatch jobs through Jobber"
    "Calendly — we use Calendly for booking appointments"
    "Acuity Scheduling — we use Acuity for booking"
    "HubSpot — we use HubSpot meetings"
    "Apple Calendar / iCloud — we use Apple Calendar"
    "We don't have a scheduling system yet"

FIELD 3 — bookable_job_types (control_checkbox, REQUIRED)
  Name: bookable_job_types
  Label: "Which job types should the AI be able to book?"
  Options:
    "AC Repair / Service Call"
    "Heating Repair / Service Call"
    "Maintenance / Tune-up"
    "Installation Quote / Assessment"
    "New System Installation"
    "Duct Cleaning"
    "Emergency Service"
    "All job types"

FIELD 4 — slot_duration (control_dropdown, REQUIRED)
  Name: slot_duration
  Label: "Default appointment duration"
  Options: 30 minutes|60 minutes|90 minutes|120 minutes|180 minutes|240 minutes
  Default: 60 minutes

FIELD 5 — min_notice (control_dropdown, REQUIRED)
  Name: min_notice
  Label: "Minimum notice before a booking"
  Options: 1 hour|2 hours|4 hours|Same day OK|1 day|2 days
  Default: 2 hours

FIELD 6 — booking_hours (control_textbox, REQUIRED)
  Name: booking_hours
  Label: "Available booking hours"
  Placeholder: "e.g. Mon-Fri 8am-5pm, Sat 9am-1pm"
  Sublabel: "AI will only offer slots within these hours"

FIELD 7 — buffer_time (control_dropdown, REQUIRED)
  Name: buffer_time
  Label: "Gap between appointments"
  Options: None|15 minutes|30 minutes|45 minutes|60 minutes
  Default: 30 minutes

FIELD 8 — confirmation_method (control_dropdown, REQUIRED)
  Name: confirmation_method
  Label: "How should booking confirmations reach customers?"
  Options: Email only|SMS only|Both Email & SMS
  Default: Both Email & SMS

FIELD 9 — cal_agreement (control_dropdown)
  Name: cal_agreement
  Label: "Quick note about your calendar setup"
  Show ONLY when scheduling_platform =
    "Apple Calendar / iCloud"
    OR "We don't have a scheduling system yet"
  
  Description text above dropdown:
    "Our AI books directly into Google Calendar or Outlook Calendar.
    If you use Apple Calendar, we'll set you up with a free Google
    Calendar that syncs automatically — your Apple Calendar stays
    unchanged. Setup takes under 2 minutes and we'll guide you through it."
  
  Options:
    "Yes, sounds good — let's set it up"
    "I'd like more info before deciding"

After building, verify by fetching form again.
Confirm all 9 fields present with correct names.
Confirm Section 1-6 fields untouched.

---

## TASK 3 — GOOGLE CALENDAR OAUTH ROUTES

In syntharra-oauth-server repo, create /routes/google-calendar.js

Check if a Google route already exists first — if so, review and update it
to match this spec rather than creating a duplicate.

Google OAuth endpoints:
  Auth: https://accounts.google.com/o/oauth2/v2/auth
  Token: https://oauth2.googleapis.com/token
  Scopes: https://www.googleapis.com/auth/calendar

GET /auth/google?agent_id={agent_id}
  Build auth URL:
    client_id = Google client_id from vault
    redirect_uri = {OAUTH_SERVER_URL}/auth/google/callback
    scope = calendar scope
    access_type = offline
    prompt = consent
    state = agent_id
  Redirect to Google OAuth consent

GET /auth/google/callback?code={code}&state={agent_id}
  Exchange code for tokens via POST to token endpoint
  Save to Supabase hvac_standard_agent WHERE agent_id = state:
    oauth_access_token = access_token
    oauth_refresh_token = refresh_token
    oauth_token_expiry = NOW() + expires_in seconds
    google_calendar_id = 'primary'
    integration_status = 'connected'
    agent_status = 'connected'
  POST to n8n webhook:
    POST https://n8n.syntharra.com/webhook/integration-connected
    Body: { agent_id, integration_type: "google", platform: "Google Calendar" }
  Show success HTML page:
    White background, #6C63FF accent
    Large green checkmark
    "Google Calendar Connected!"
    "Your AI receptionist is being activated.
     You'll receive a confirmation email within a few hours."
    "Questions? support@syntharra.com"

---

## TASK 4 — MICROSOFT OUTLOOK OAUTH ROUTES

In syntharra-oauth-server, create /routes/outlook.js

Check vault for Microsoft OAuth credentials first.
If service_name='Microsoft' credentials not in vault:
  Skip this task, note: "Dan needs to create Microsoft Azure OAuth app
  and store client_id + client_secret in vault under service_name='Microsoft'"
  Continue to Task 5.

If credentials exist:

Microsoft OAuth:
  Auth: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
  Token: https://login.microsoftonline.com/common/oauth2/v2.0/token
  Scopes: Calendars.ReadWrite offline_access

GET /auth/outlook?agent_id={agent_id}
  Same pattern as Google route
  State = agent_id

GET /auth/outlook/callback
  Exchange code for tokens
  Save to Supabase:
    oauth_access_token, oauth_refresh_token, oauth_token_expiry
    outlook_calendar_id = 'primary'
    integration_status = 'connected'
    agent_status = 'connected'
  POST to n8n: { agent_id, integration_type: "outlook", platform: "Microsoft Outlook" }
  Show same success page style as Google

Push all OAuth server changes to GitHub. Redeploy on Railway.

---

## TASK 5 — N8N: INTEGRATION CONNECTED HANDLER

Create new n8n workflow: "Premium — Integration Connected Handler"
Webhook path: /webhook/integration-connected
Method: POST
Body: { agent_id, integration_type, platform }

Node 1 — Webhook trigger

Node 2 — Supabase: fetch client record
  SELECT agent_id, company_name, notification_email, notification_email_2,
         owner_name, scheduling_platform, integration_type, integration_status
  FROM hvac_standard_agent
  WHERE agent_id = '{{$json.agent_id}}'

Node 3 — Function: extract first name
  const fullName = $json.owner_name || 'there';
  const firstName = fullName.split(' ')[0];
  return { ...$json, owner_first_name: firstName };

Node 4 — IF: integration_status = "connected"?
  Yes → continue
  No → send alert to alerts@syntharra.com
       Subject: "⚠️ Unexpected integration webhook — {{company_name}}"
       Body: agent_id, received status, timestamp
       Then STOP

Node 5 — Supabase: insert to activation queue
  INSERT INTO syntharra_activation_queue:
    agent_id, company_name, owner_name, owner_email = notification_email,
    scheduling_platform, integration_type,
    integration_status = 'connected',
    created_at = NOW()

Node 6 — SMTP2GO: send activation alert to onboarding@syntharra.com
  From: noreply@syntharra.com
  Subject: "⚡ Premium Client Ready — {{company_name}}"
  
  Light theme HTML email:
  [Logo block]
  
  New Premium Client Connected
  
  Company: {{company_name}}
  Owner: {{owner_name}}
  Platform: {{scheduling_platform}}
  Integration: {{integration_type}}
  Agent ID: {{agent_id}}
  Connected at: {{$now formatted as readable datetime}}
  
  Next steps:
  1. Check activation queue in admin dashboard
  2. Run a test booking on the demo line
  3. Once happy, activate — "You're Live" email sends automatically
  
  [View Activation Queue →]
  href: https://admin.syntharra.com

Node 7 — SMTP2GO: send holding email to client
  To: {{notification_email}}
  From: noreply@syntharra.com
  Subject: "✅ {{scheduling_platform}} Connected — Almost Live!"
  
  Light theme HTML email:
  [Logo block]
  
  Hi {{owner_first_name}},
  
  Your {{scheduling_platform}} account is now connected to
  your Syntharra AI Receptionist.
  
  We're running a final check to make sure everything is
  working perfectly. You'll receive your "You're Live"
  confirmation within a few hours.
  
  Questions? Contact us at support@syntharra.com
  
  The Syntharra Team

Publish workflow after building.

---

## TASK 6 — UPDATE PREMIUM ONBOARDING WORKFLOW

Fetch workflow kz1VmwNccunRMEaF via n8n API.
Preserve ALL existing nodes exactly.
Add new nodes AFTER the existing Supabase client INSERT node.

Parse these new fields from the Jotform webhook payload:
  scheduling_platform, bookable_job_types, slot_duration,
  min_notice, booking_hours, buffer_time,
  confirmation_method, cal_agreement

NODE A — Function: Map to integration type
  Input: scheduling_platform string from Jotform
  
  const p = scheduling_platform || '';
  let integration_type = 'manual';
  
  if (p.includes('Google')) integration_type = 'google';
  else if (p.includes('Outlook') || p.includes('Microsoft')) integration_type = 'outlook';
  else if (p.includes('Jobber')) integration_type = 'jobber';
  else if (p.includes('Calendly')) integration_type = 'calendly';
  else if (p.includes('Acuity')) integration_type = 'acuity';
  else if (p.includes('HubSpot')) integration_type = 'hubspot';
  else if (p.includes('Apple') || p.includes("don't")) integration_type = 'google';
  // Apple and no-system clients default to Google Calendar flow
  
  Parse booking fields:
  const slot_duration_minutes = parseInt(slot_duration) || 60;
  const buffer_time_minutes = parseInt(buffer_time) || 30;
  const min_notice_map = {
    '1 hour': 1, '2 hours': 2, '4 hours': 4,
    'Same day OK': 0, '1 day': 24, '2 days': 48
  };
  const min_notice_hours = min_notice_map[min_notice] || 2;
  const bookable_job_types = Array.isArray(bookable_job_types)
    ? bookable_job_types : [bookable_job_types];
  
  Return all parsed values plus integration_type.

NODE B — Supabase: UPDATE client record
  UPDATE hvac_standard_agent
  WHERE agent_id = {{agent_id}}
  SET:
    scheduling_platform, integration_type,
    slot_duration_minutes, buffer_time_minutes,
    min_notice_hours, booking_hours,
    bookable_job_types (as JSONB),
    booking_confirmation_method = confirmation_method,
    cal_agreement,
    agent_status = 'pending_integration'

NODE C — Switch: route by integration_type
  Branch "google" → Node D (Google OAuth email)
  Branch "outlook" → Node E (Outlook OAuth email)
  Branch "jobber" → Node F (placeholder)
  Branch "calendly" → Node F (placeholder)
  Branch "acuity" → Node F (placeholder)
  Branch "hubspot" → Node F (placeholder)
  Branch "manual" → Node F (placeholder)

NODE D — SMTP2GO: Google Calendar OAuth email
  To: {{client_email}}
  Subject: "Connect Google Calendar — One Last Step"
  
  Light theme HTML email:
  [Logo block]
  
  Hi {{owner_first_name}},
  
  Your AI receptionist is built and ready. The last step
  is connecting your Google Calendar so your AI knows
  when you're available and can book jobs automatically.
  
  [Connect Google Calendar →]
  Button URL: {OAUTH_SERVER_URL}/auth/google?agent_id={{agent_id}}
  Button style: background #6C63FF, white text, rounded
  
  What happens when you connect:
  ✓ Your AI checks your real availability before offering any slots
  ✓ Bookings appear directly in your Google Calendar
  ✓ Customers get instant confirmation — no back and forth
  
  This takes under 2 minutes.
  
  Questions? support@syntharra.com
  
  After sending: UPDATE agent_status = 'oauth_sent' in Supabase

NODE E — SMTP2GO: Outlook OAuth email
  Same as Node D but:
  Subject: "Connect Outlook Calendar — One Last Step"
  Button text: "Connect Outlook Calendar →"
  Button URL: {OAUTH_SERVER_URL}/auth/outlook?agent_id={{agent_id}}
  
  After sending: UPDATE agent_status = 'oauth_sent' in Supabase

NODE F — SMTP2GO: Placeholder email (Type A/B + manual)
  To: {{client_email}}
  Subject: "Your AI Is Being Configured — We'll Be In Touch"
  
  Light theme HTML email:
  [Logo block]
  
  Hi {{owner_first_name}},
  
  Your AI receptionist is being set up. Our team will
  contact you within 1 business day to complete your
  {{scheduling_platform}} integration.
  
  Questions? support@syntharra.com
  
  Also send internal note to onboarding@syntharra.com:
  Subject: "Manual setup needed — {{company_name}} / {{scheduling_platform}}"

Publish workflow after all changes.

---

## TASK 7 — BUILD GOOGLE CALENDAR DISPATCHER

Create new n8n workflow: "Premium Dispatcher — Google Calendar"
Webhook trigger: /webhook/dispatcher-google
Method: POST

Expected body:
{
  agent_id: string,
  action: "get_slots" | "create_booking" | "cancel_booking",
  caller_name: string,
  caller_phone: string,
  job_type: string,
  selected_slot: string  (ISO8601 datetime, only for create_booking)
}

=== FOR action = "get_slots" ===

Node 1 — Supabase fetch client
  SELECT oauth_access_token, oauth_refresh_token, oauth_token_expiry,
         google_calendar_id, booking_hours, slot_duration_minutes,
         buffer_time_minutes, min_notice_hours
  FROM hvac_standard_agent WHERE agent_id = {{agent_id}}

Node 2 — Function: check token expiry
  If oauth_token_expiry < NOW():
    flag needsRefresh = true
  Else:
    flag needsRefresh = false

Node 3 — IF needsRefresh:
  Yes → HTTP Request: POST https://oauth2.googleapis.com/token
    Body: grant_type=refresh_token, refresh_token={{refresh_token}},
          client_id={{GOOGLE_CLIENT_ID}}, client_secret={{GOOGLE_CLIENT_SECRET}}
    Save new access_token + expiry to Supabase
  No → use existing token

Node 4 — HTTP Request: GET Google Calendar busy times
  URL: https://www.googleapis.com/calendar/v3/freeBusy
  Method: POST
  Headers: Authorization: Bearer {{access_token}}
  Body:
  {
    "timeMin": "{{NOW in ISO8601}}",
    "timeMax": "{{NOW + 7 days in ISO8601}}",
    "timeZone": "UTC",
    "items": [{ "id": "{{google_calendar_id}}" }]
  }

Node 5 — Function: calculate free slots
  Input: busy periods from freeBusy response
  Logic:
    Parse booking_hours into daily start/end times
    For each day in next 7 days:
      Start with full booking_hours window
      Remove all busy periods (with buffer_time on each side)
      Generate available slot_duration_minutes slots
      Apply min_notice_hours filter (no slots sooner than min_notice)
    Collect all free slots
    Return first 6 as human-readable strings:
      e.g. "Tuesday April 8 at 9:00 AM"
    Also return ISO8601 versions for booking use
  
  Return: { slots: ["Tuesday...", ...], slot_times: ["2025-04-08T09:00:00Z", ...] }

Node 6 — Respond to webhook
  { success: true, slots: [...], slot_times: [...] }

=== FOR action = "create_booking" ===

Node 1 — Same Supabase fetch + token refresh check

Node 2 — HTTP Request: POST Google Calendar event
  URL: https://www.googleapis.com/calendar/v3/calendars/{{google_calendar_id}}/events
  Headers: Authorization: Bearer {{access_token}}
  Body:
  {
    "summary": "{{job_type}} — {{caller_name}}",
    "description": "Booked by Syntharra AI\nCustomer: {{caller_name}}\nPhone: {{caller_phone}}\nJob: {{job_type}}",
    "start": { "dateTime": "{{selected_slot}}", "timeZone": "UTC" },
    "end": { "dateTime": "{{selected_slot + slot_duration_minutes}}", "timeZone": "UTC" }
  }

Node 3 — Supabase: INSERT booking log to hvac_call_log
  booking_id = response.id
  booking_platform = 'google'
  booking_time = selected_slot
  job_type, caller_name, caller_phone, agent_id

Node 4 — Respond:
  { success: true, booking_id: response.id, confirmation_time: selected_slot }

=== FOR action = "cancel_booking" ===
  Respond: { success: false, message: "Please transfer to office to cancel" }

Publish workflow after building.

---

## TASK 8 — VERIFICATION

Run each check and report pass ✅ or fail ❌:

1. Supabase:
   - All new columns exist on hvac_standard_agent
   - syntharra_activation_queue table exists

2. Jotform:
   - Fetch form 260819259556671
   - Confirm 9 Section 7 fields present with correct names
   - Confirm Sections 1-6 untouched
   - List all Section 7 field IDs found

3. OAuth Server (check Railway deployment):
   - GET {OAUTH_SERVER_URL}/auth/google?agent_id=test_verify
     Should redirect to Google OAuth (or show Google error — both fine)
   - If Outlook built:
     GET {OAUTH_SERVER_URL}/auth/outlook?agent_id=test_verify
     Should redirect to Microsoft OAuth

4. n8n workflows:
   - "Premium — Integration Connected Handler" — ACTIVE ✅
   - "Premium Dispatcher — Google Calendar" — ACTIVE ✅
   - Premium Onboarding kz1VmwNccunRMEaF — Switch node present, PUBLISHED ✅

5. Final report:
   ✅ / ❌ for each item above
   List any missing credentials
   List anything skipped and why
   Confirm what Dan needs to do before Phase 2

---
END OF PHASE 1
