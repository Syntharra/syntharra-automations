# SYNTHARRA PREMIUM — PHASE 3
# Run ONLY after Phase 2 is verified complete.
# This phase removes manual activation, adds auto-testing,
# You're Live email, token refresh automation, and admin queue view.

---

## CONTEXT

Phases 1 and 2 complete:
  ✅ All OAuth routes live
  ✅ All dispatcher workflows active
  ✅ Onboarding workflow fully wired
  ✅ Integration Connected Handler notifies Dan

Current flow:
  Client connects → Dan gets email → Dan manually activates → Dan sends You're Live

Phase 3 target flow:
  Client connects → Auto test booking runs → If pass: auto-activate + You're Live sent
                                           → If fail: Dan gets alert, client gets holding email

---

## TASK 1 — AUTO-ACTIVATION: UPDATE INTEGRATION CONNECTED HANDLER

Fetch workflow "Premium — Integration Connected Handler" via n8n API.
Preserve all existing nodes.

After the existing Node 7 (client holding email), add:

NODE 8 — HTTP Request: run test booking
  POST to the correct dispatcher based on integration_type from Supabase record:
    google   → https://n8n.syntharra.com/webhook/dispatcher-google
    outlook  → https://n8n.syntharra.com/webhook/dispatcher-outlook
    jobber   → https://n8n.syntharra.com/webhook/dispatcher-jobber
    calendly → https://n8n.syntharra.com/webhook/dispatcher-calendly
    acuity   → https://n8n.syntharra.com/webhook/dispatcher-acuity
    hubspot  → https://n8n.syntharra.com/webhook/dispatcher-hubspot
  
  Body for all:
  {
    agent_id: {{agent_id}},
    action: "get_slots",
    caller_name: "Syntharra Test",
    caller_phone: "0000000000",
    job_type: "Onboarding Verification Test"
  }
  
  Timeout: 15 seconds
  On timeout/error: treat as failed

NODE 9 — IF: test returned slots?
  Condition: response body contains slots array with length > 0
  Yes → Node 10 (auto-activate)
  No → Node 12 (manual review alert)

NODE 10 — Supabase: mark as active
  UPDATE hvac_standard_agent WHERE agent_id = {{agent_id}}
  SET: integration_status = 'active', agent_status = 'active'
  
  UPDATE syntharra_activation_queue
  SET: activated_at = NOW(), activated_by = 'auto', integration_status = 'active'
  WHERE agent_id = {{agent_id}} AND activated_at IS NULL

NODE 11 — HTTP Request: trigger You're Live email
  POST https://n8n.syntharra.com/webhook/send-live-email
  Body: { agent_id: {{agent_id}} }
  (This workflow is built in Task 2)

NODE 12 — Supabase: mark as needs review
  UPDATE hvac_standard_agent WHERE agent_id = {{agent_id}}
  SET: integration_status = 'failed', agent_status = 'failed'
  
  UPDATE syntharra_activation_queue
  SET: notes = 'Auto test failed — manual review needed'
  WHERE agent_id = {{agent_id}}

NODE 13 — SMTP2GO: alert Dan (manual review needed)
  To: onboarding@syntharra.com
  Subject: "⚠️ Integration Test Failed — {{company_name}} Needs Manual Review"
  
  Light theme email:
  [Logo block]
  
  Auto-activation failed for {{company_name}}.
  
  Details:
  Company: {{company_name}}
  Platform: {{scheduling_platform}}
  Integration: {{integration_type}}
  Agent ID: {{agent_id}}
  
  The test booking returned no available slots.
  This could mean:
  • Their calendar has no availability in the next 7 days
  • Their OAuth token didn't save correctly
  • Their booking hours haven't been set up yet
  
  Action needed:
  Check the activation queue in admin dashboard.
  Review their Supabase record.
  Manually test and activate once resolved.
  
  [View Activation Queue →]
  href: https://admin.syntharra.com

NODE 14 — SMTP2GO: updated holding email to client
  (only fires if test failed — Node 12 path)
  To: {{client_email}}
  Subject: "We're Just Finishing Your Setup — Almost There!"
  
  Light theme:
  [Logo block]
  
  Hi {{owner_first_name}},
  
  We're just completing a final check on your setup.
  Our team will be in touch within a few hours to make
  sure everything is working perfectly.
  
  Questions? support@syntharra.com

Publish after changes.

---

## TASK 2 — YOU'RE LIVE EMAIL WORKFLOW

Create new n8n workflow: "Premium — Send You're Live Email"
Webhook trigger: /webhook/send-live-email
Method: POST
Body: { agent_id }

Node 1 — Webhook trigger

Node 2 — Supabase fetch
  SELECT agent_id, company_name, owner_name, notification_email,
         agent_name, scheduling_platform, integration_type,
         slot_duration_minutes, booking_hours
  FROM hvac_standard_agent WHERE agent_id = {{$json.agent_id}}
  
  Also fetch: phone number from Retell API if available
  GET https://api.retellai.com/get-agent/{{agent_id}}
  Headers: Authorization: Bearer {{RETELL_API_KEY}}
  Get agent's phone number from response

Node 3 — Function: extract first name + format details
  const firstName = owner_name.split(' ')[0];
  const dashboardUrl = 'https://syntharra.com/dashboard.html?agent_id=' + agent_id;

Node 4 — SMTP2GO: You're Live email
  To: {{notification_email}}
  From: noreply@syntharra.com
  Subject: "🎉 Your AI Receptionist Is Live — {{company_name}}"
  
  Light theme HTML email — make this one polished, it's the money email:
  
  Outer bg: #F7F7FB
  Card: white, border-radius 12px, max-width 600px, padding 40px
  
  [Logo block — centered]
  
  --- Large heading ---
  "You're Live, {{owner_first_name}}! 🎉"
  Font: Inter 700 28px #1A1A2E, centered
  
  --- Subheading ---
  "{{company_name}}'s AI receptionist is now active
   and ready to take calls 24/7."
  Color: #4A4A6A, centered
  
  --- Divider ---
  
  --- What's active now section ---
  3-column or list layout:
  
  ✓ 24/7 Call Answering
    "Never miss a customer call again"
  
  ✓ Automatic Booking
    "Jobs booked directly into {{scheduling_platform}}"
  
  ✓ Instant Notifications
    "You're alerted on every call and booking"
  
  --- Your AI details box ---
  Background: #F7F7FB, border-radius 8px, padding 20px
  
  AI Receptionist Name: {{agent_name}}
  Scheduling: {{scheduling_platform}}
  Booking hours: {{booking_hours}}
  
  --- CTA buttons ---
  Primary: [View Your Dashboard →]
    Background: #6C63FF, white text, rounded
    href: {{dashboardUrl}}
  
  Secondary: [Test Your AI Now →]
    Border: 1px solid #6C63FF, #6C63FF text, rounded
    href: tel:{{agent_phone}} (if available)
  
  --- Final note ---
  "Your weekly performance report will arrive every Monday.
   Questions or need changes? support@syntharra.com"
  
  --- Footer ---
  "Syntharra · Global AI Solutions · support@syntharra.com"
  Color: #8A8AA0, small font

Node 5 — Supabase: log activation event
  INSERT INTO hvac_call_log:
    agent_id, event_type = 'agent_activated',
    notes = 'You're Live email sent', created_at = NOW()

Publish workflow.

---

## TASK 3 — OUTLOOK DISPATCHER

If Outlook OAuth was built in Phase 1, build its dispatcher now.
If it was skipped (credentials missing), skip this task.

Create workflow: "Premium Dispatcher — Outlook"
Webhook: /webhook/dispatcher-outlook

Microsoft Calendar API base: https://graph.microsoft.com/v1.0

get_slots:
  Node 1 — Supabase fetch: oauth_access_token, oauth_refresh_token,
    oauth_token_expiry, outlook_calendar_id, booking_hours,
    slot_duration_minutes, buffer_time_minutes, min_notice_hours

  Node 2 — Token refresh if needed:
    POST https://login.microsoftonline.com/common/oauth2/v2.0/token
    Body: grant_type=refresh_token, refresh_token, client_id, client_secret
    Save new tokens to Supabase

  Node 3 — HTTP Request: GET busy times
    POST https://graph.microsoft.com/v1.0/me/calendar/getSchedule
    Headers: Authorization: Bearer {access_token}
    Body:
    {
      "schedules": ["me"],
      "startTime": { "dateTime": "{{NOW}}", "timeZone": "UTC" },
      "endTime": { "dateTime": "{{NOW + 7 days}}", "timeZone": "UTC" },
      "availabilityViewInterval": {{slot_duration_minutes}}
    }

  Node 4 — Function: calculate free slots
    Same logic as Google dispatcher — parse busy periods,
    calculate free slots within booking_hours,
    return max 6 formatted slots + ISO8601 times

  Node 5 — Respond: { success: true, slots, slot_times }

create_booking:
  Node 1 — Supabase fetch + token refresh

  Node 2 — HTTP Request: POST new calendar event
    POST https://graph.microsoft.com/v1.0/me/calendars/{{outlook_calendar_id}}/events
    Headers: Authorization: Bearer {access_token}
    Body:
    {
      "subject": "{{job_type}} — {{caller_name}}",
      "body": {
        "contentType": "Text",
        "content": "Booked by Syntharra AI\nCustomer: {{caller_name}}\nPhone: {{caller_phone}}\nJob: {{job_type}}"
      },
      "start": { "dateTime": "{{selected_slot}}", "timeZone": "UTC" },
      "end": { "dateTime": "{{selected_slot + slot_duration_minutes}}", "timeZone": "UTC" }
    }

  Node 3 — Supabase: log to hvac_call_log
    booking_id = response.id, booking_platform = 'outlook'

  Node 4 — Respond: { success: true, booking_id, confirmation_time }

Publish workflow.

---

## TASK 4 — DAILY TOKEN REFRESH WORKFLOW

Create workflow: "Premium — Daily Token Refresh"
Trigger: Schedule node — every day at 02:00 UTC

Node 1 — Supabase: get all active clients
  SELECT agent_id, integration_type, oauth_access_token,
         oauth_refresh_token, oauth_token_expiry, company_name,
         notification_email
  FROM hvac_standard_agent
  WHERE agent_status = 'active'
    AND integration_type != 'manual'
    AND oauth_refresh_token IS NOT NULL

Node 2 — Split in batches (1 at a time to avoid rate limits)

Node 3 — Function: check if refresh needed
  If oauth_token_expiry < NOW() + 2 days → needs refresh

Node 4 — IF needs refresh:
  Yes → Node 5
  No → skip to next item

Node 5 — Switch by integration_type:
  google:   POST https://oauth2.googleapis.com/token
            grant_type=refresh_token + Google client creds
  outlook:  POST https://login.microsoftonline.com/common/oauth2/v2.0/token
            grant_type=refresh_token + Microsoft client creds
  jobber:   POST https://api.getjobber.com/api/oauth/token
  calendly: POST https://auth.calendly.com/oauth/token
  acuity:   POST https://acuityscheduling.com/oauth2/token
  hubspot:  POST https://api.hubapi.com/oauth/v1/token

Node 6 — IF refresh successful:
  Yes → UPDATE Supabase: new access_token, refresh_token, token_expiry
  No → UPDATE integration_status = 'token_expired'
       Send alert to alerts@syntharra.com:
         "⚠️ Token refresh failed — {{company_name}} / {{integration_type}}"
       Send reconnect email to client:
         Subject: "Action Needed — Reconnect Your Calendar"
         Body:
         "Hi {{first_name}},
          
          Your calendar connection needs to be refreshed.
          This takes under 1 minute.
          
          [Reconnect Now →]
          href: {OAUTH_SERVER_URL}/auth/{{integration_type}}?agent_id={{agent_id}}
          
          Questions? support@syntharra.com"

Publish workflow.

---

## TASK 5 — ADMIN DASHBOARD: ACTIVATION QUEUE

Fetch current admin dashboard from GitHub:
  Repo: Syntharra/syntharra-admin
  File: index.html (or whatever the main dashboard file is)
  Use SHA-fetch pattern before editing.

Add a new section: "Activation Queue"
Position: near the top, after any system status section, before Clients list.

This section queries syntharra_activation_queue
WHERE activated_at IS NULL
ORDER BY created_at DESC

Display as a styled table matching existing admin dashboard design:

Columns:
  Company | Platform | Integration | Connected | Status | Actions

Actions per row:
  [✅ Activate] button
    On click:
    1. POST to /webhook/send-live-email with { agent_id }
    2. UPDATE syntharra_activation_queue SET activated_at = NOW(), activated_by = 'manual'
    3. UPDATE hvac_standard_agent SET agent_status = 'active', integration_status = 'active'
    4. Remove row from table / show "Activated" badge
  
  [🔍 Test] button
    On click:
    1. POST to correct dispatcher with action = "get_slots"
    2. Show result in a modal:
       "✅ X slots available" or "❌ No slots returned — check calendar setup"
  
  [📝 Notes] button
    On click: show modal with text input
    Save to syntharra_activation_queue.notes

If queue is empty, show:
  "✅ All clients are active — nothing pending"

Add a small badge on the nav item showing count of pending activations.
Update every 60 seconds via setInterval fetch.

Push to GitHub after changes.

---

## TASK 6 — FINAL VERIFICATION

Run full end-to-end simulation:

Step 1 — Simulate Jotform submission:
  POST to the Premium Onboarding webhook with test data:
  {
    "q4_companyName": "Test HVAC Co",
    "q54_ownerName": "Test Owner",
    "q5_clientEmail": "test@syntharra.com",
    "q6_mainPhone": "5550001234",
    "q34_timezone": "Eastern Time ET",
    "scheduling_platform": "Google Calendar",
    "bookable_job_types": ["AC Repair / Service Call"],
    "slot_duration": "60 minutes",
    "min_notice": "2 hours",
    "booking_hours": "Mon-Fri 8am-5pm",
    "buffer_time": "30 minutes",
    "confirmation_method": "Both Email & SMS"
  }
  Use agent_id = "test_phase3_verify_" + timestamp

Step 2 — Verify onboarding workflow:
  Check n8n execution history for kz1VmwNccunRMEaF
  Confirm: Supabase row created, Switch node routed to "google",
  OAuth email node fired (don't check actual email delivery, just node ran)

Step 3 — Simulate OAuth callback:
  POST https://n8n.syntharra.com/webhook/integration-connected
  Body: { agent_id: "test_phase3_verify_...", integration_type: "google", platform: "Google Calendar" }
  
  Verify:
  - Integration Connected Handler ran
  - Test booking was attempted (check execution log)
  - Either auto-activated OR manual review alert sent
  - Activation queue has entry

Step 4 — Verify daily refresh workflow:
  Check it's scheduled and ACTIVE in n8n

Step 5 — Verify admin dashboard:
  Confirm activation queue section loads
  Confirm test entry appears from Step 3

Step 6 — Clean up:
  DELETE FROM hvac_standard_agent WHERE agent_id LIKE 'test_phase3_%'
  DELETE FROM syntharra_activation_queue WHERE agent_id LIKE 'test_phase3_%'

Final report:
  ✅ / ❌ for each step
  Complete integration matrix — which platforms fully working end to end
  List any remaining manual steps
  List any credentials still needed
  
  Recommended go-live actions:
  1. Switch Stripe to live mode
  2. Test one real client through full flow
  3. Monitor activation queue for first 48 hours

---
END OF PHASE 3
