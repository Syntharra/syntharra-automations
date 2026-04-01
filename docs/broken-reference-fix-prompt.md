# SYNTHARRA — BROKEN REFERENCE FIX PROMPT
# Give this entire file to Claude Code.
# This fixes all remaining references to deleted Supabase tables.
# Every change must be pushed to GitHub or published in n8n immediately.

---

## WHAT HAPPENED

We deleted these Supabase tables as part of the Premium consolidation:
- hvac_premium_agent (replaced by hvac_standard_agent with plan_type column)
- hvac_premium_call_log (replaced by hvac_call_log with call_tier column)
- agreement_signatures, affiliate_applications, call_processor_dlq
- 10 unused ops-monitor tables

Multiple systems still reference the deleted tables. Every one of these
must be updated to use the consolidated tables instead.

## CRITICAL RULES

1. hvac_standard_agent is THE SINGLE client table for ALL plans (standard + premium)
   - The plan_type column distinguishes them ('standard' or 'premium')
   - Premium-specific columns are: scheduling_platform, integration_type, integration_status,
     oauth_access_token, oauth_refresh_token, oauth_token_expiry, google_calendar_id,
     outlook_calendar_id, bookable_job_types, slot_duration_minutes, buffer_time_minutes,
     min_notice_hours, booking_hours, booking_confirmation_method, cal_agreement,
     calendly_event_type_uri, acuity_appointment_type_id, hubspot_meeting_slug

2. hvac_call_log is THE SINGLE call log table for ALL calls
   - The call_tier column distinguishes them ('Standard' or 'Premium')
   - Premium calls should use call_tier = 'Premium'

3. The OLD hvac_premium_agent had different column names that NO LONGER EXIST:
   OLD column name          → NEW equivalent in hvac_standard_agent
   calendar_platform        → scheduling_platform
   crm_platform             → (not needed — integration_type covers this)
   calendar_access_token    → oauth_access_token
   calendar_refresh_token   → oauth_refresh_token
   calendar_token_expiry    → oauth_token_expiry
   calendar_api_key         → (not needed)
   calendar_status          → integration_status
   crm_access_token         → (not needed for MVP)
   crm_refresh_token        → (not needed for MVP)
   crm_api_key              → (not needed for MVP)
   crm_status               → (not needed for MVP)
   default_appointment_duration → slot_duration_minutes
   booking_buffer_minutes   → buffer_time_minutes
   booking_advance_days     → (not a column — use min_notice_hours)
   dispatch_mode            → (not needed)
   technician_names         → (not needed)

---

## CREDENTIALS

n8n API key (fetch from vault or use):
  Supabase vault: SELECT key_value FROM syntharra_vault WHERE service_name = 'n8n Railway' AND key_type = 'api_key'
  n8n instance: https://n8n.syntharra.com

GitHub token: {{GITHUB_TOKEN}}
Supabase URL: https://hgheyqwnrcvwtgngqdnq.supabase.co
Supabase service role key: fetch from vault

---

## FIX 1 — n8n: HVAC Premium Call Processor (STQ4Gt3rH8ptlvMi)

This workflow has 3 broken nodes. Fetch it via n8n API, fix these nodes, PUT back, publish.

### Node: "Look Up Client"
CURRENT (broken):
  URL: https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/hvac_premium_agent?agent_id=eq.{{ $json.agent_id }}&select=*

FIX:
  URL: https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/hvac_standard_agent?agent_id=eq.{{ $json.agent_id }}&select=*

### Node: "Log Call to Supabase"
This is a Code node that POSTs to hvac_premium_call_log.
Change the Supabase URL from hvac_premium_call_log to hvac_call_log.
Keep call_tier: 'Premium' in the body (this is correct — it distinguishes premium calls).

The hvac_call_log table has slightly different columns than the old premium table.
Map the columns correctly:
- KEEP these (they exist in hvac_call_log): agent_id, call_id, company_name, call_tier,
  duration_seconds, summary, caller_name, caller_phone, caller_address, lead_score,
  is_lead, job_type, urgency, vulnerable_occupant, notes, service_requested,
  transfer_attempted, transfer_success, caller_sentiment, call_successful,
  recording_url, retell_sentiment, latency_p50_ms, call_cost_cents, retell_summary,
  public_log_url, geocode_status, geocode_formatted
  
- REMOVE these (they don't exist in hvac_call_log): booking_attempted, booking_success,
  appointment_date, appointment_time, appointment_duration_minutes, job_type_booked,
  booking_reference, reschedule_requested, cancellation_requested, call_type,
  from_number, notification_sent, notification_type, is_hot_lead, notification_priority,
  is_repeat_caller, repeat_call_count, call_status, caller_email, transcript

Note: Some of these removed columns ARE useful for Premium. We will add them
to hvac_call_log later. For now, store them in the 'notes' field as JSON string
so no data is lost:

```javascript
notes: JSON.stringify({
  booking_attempted: d.booking_attempted,
  booking_success: d.booking_success,
  appointment_date: d.appointment_date,
  appointment_time: d.appointment_time_window,
  call_type: d.call_type,
  from_number: d.from_number,
  is_hot_lead: d.is_hot_lead,
  is_repeat_caller: d._repeat_caller || false,
  repeat_call_count: d._call_history?.length || 0,
  original_notes: d.notes || ''
})
```

### Node: "Check Repeat Caller"
This is a Code node that queries hvac_premium_call_log for previous calls.
Change the Supabase URL from hvac_premium_call_log to hvac_call_log.
The SELECT columns need adjusting too — hvac_call_log uses slightly different names.
Change the select to: call_id,caller_name,service_requested,call_tier,summary,created_at

After fixing all 3 nodes, PUT the workflow back and PUBLISH it.

---

## FIX 2 — n8n: Premium Integration Dispatcher (73Y0MHVBu05bIm5p)

This workflow has 2 broken nodes. It uses the OLD column names from hvac_premium_agent.

### Node: "Extract and Lookup Client"
CURRENT: Queries hvac_premium_agent and selects old column names like
  calendar_platform, crm_platform, calendar_access_token, etc.

FIX: Change table to hvac_standard_agent. Change column names:
  calendar_platform → scheduling_platform
  crm_platform → integration_type
  calendar_access_token → oauth_access_token
  calendar_refresh_token → oauth_refresh_token
  calendar_api_key → (remove)
  crm_access_token → (remove)
  crm_api_key → (remove)
  default_appointment_duration → slot_duration_minutes
  booking_buffer_minutes → buffer_time_minutes
  booking_advance_days → min_notice_hours

Update the SELECT to:
  company_name,scheduling_platform,integration_type,oauth_access_token,oauth_refresh_token,slot_duration_minutes,buffer_time_minutes,min_notice_hours,timezone,booking_hours,bookable_job_types

Also update any return values that use the old column names — e.g.:
  calendar_platform → scheduling_platform
  crm_platform → integration_type

### Node: "Process Function Call"
This node also references hvac_premium_agent for token refresh PATCH operations.
Change ALL occurrences of hvac_premium_agent to hvac_standard_agent.
Also update any column name references:
  calendar_access_token → oauth_access_token
  calendar_token_expiry → oauth_token_expiry

PUT and PUBLISH after fixing.

---

## FIX 3 — GitHub: OAuth Server (syntharra-oauth-server/server.js)

Two locations reference hvac_premium_agent in a dual-table loop pattern:
  for (const table of ['hvac_premium_agent', 'hvac_standard_agent']) {

Since we now only use hvac_standard_agent, simplify to just query that one table.
Remove the loop entirely and just query hvac_standard_agent directly.

Line ~333 (submit-key handler):
  BEFORE: for (const table of ['hvac_premium_agent', 'hvac_standard_agent']) { ... }
  AFTER: query only hvac_standard_agent

Line ~449 (if there's another loop):
  Same fix.

Fetch server.js from GitHub (with SHA), make the replacements, push back.
Railway will auto-deploy.

---

## FIX 4 — GitHub: Client Dashboard (syntharra-website/dashboard.html)

References both hvac_premium_agent and hvac_premium_call_log.
This dashboard already uses hvac_standard_agent and hvac_call_log as primary tables,
but has fallback logic or conditional queries for premium.

Fix: Remove ALL references to hvac_premium_agent and hvac_premium_call_log.
The dashboard should query ONLY:
- hvac_standard_agent (for client info)
- hvac_call_log (for call data, filtered by agent_id)

Fetch dashboard.html from GitHub, fix, push back.

---

## FIX 5 — GitHub: Admin Dashboard (syntharra-admin)

Three files have references:

### public/index.html — 1 reference to hvac_premium_agent
Fix: Replace with hvac_standard_agent

### public/calls.html — 1 reference to hvac_premium_agent
Fix: Replace with hvac_standard_agent

### server.js — 1 reference to hvac_premium_agent, 1 to hvac_premium_call_log
Fix: Replace hvac_premium_agent with hvac_standard_agent
Fix: Replace hvac_premium_call_log with hvac_call_log

Fetch each file, fix, push back.

---

## FIX 6 — ADD MISSING COLUMNS TO hvac_call_log

The Premium call processor needs some columns that exist in the old premium call log
but not in hvac_call_log. Add them:

```sql
ALTER TABLE hvac_call_log
  ADD COLUMN IF NOT EXISTS booking_attempted BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS booking_success BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS appointment_date TEXT,
  ADD COLUMN IF NOT EXISTS appointment_time TEXT,
  ADD COLUMN IF NOT EXISTS job_type_booked TEXT,
  ADD COLUMN IF NOT EXISTS booking_reference TEXT,
  ADD COLUMN IF NOT EXISTS call_type TEXT,
  ADD COLUMN IF NOT EXISTS from_number TEXT,
  ADD COLUMN IF NOT EXISTS is_hot_lead BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_repeat_caller BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS repeat_call_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS notification_sent BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS notification_type TEXT,
  ADD COLUMN IF NOT EXISTS notification_priority TEXT;
```

After adding these columns, go back to the Premium Call Processor (Fix 1)
and update the "Log Call to Supabase" node to use these columns directly
instead of stuffing them into the notes field.

---

## VERIFICATION

After all fixes, run this scan:

1. Fetch ALL n8n workflows and grep for "hvac_premium_agent" and "hvac_premium_call_log"
   Expected: ZERO matches

2. Fetch all GitHub files and grep:
   - syntharra-oauth-server/server.js — ZERO matches
   - syntharra-website/dashboard.html — ZERO matches
   - syntharra-admin/public/index.html — ZERO matches
   - syntharra-admin/public/calls.html — ZERO matches
   - syntharra-admin/server.js — ZERO matches

3. Test the Premium Call Processor by checking its execution history
   (just verify the workflow is valid and can be triggered)

4. Report: ✅/❌ for each fix

---
END OF FIX PROMPT
