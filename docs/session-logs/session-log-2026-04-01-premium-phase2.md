# Session Log: 2026-04-01 — Premium Pipeline Phase 2 Complete

## What changed

Completed Phase 2 of the HVAC Premium pipeline: Google Calendar integration end-to-end.

All Code nodes using fetch() were converted to this.helpers.httpRequest() across 3 workflows.

## Root cause

This n8n instance runs Code nodes inside @n8n/task-runner sandbox where fetch is not defined, even on typeVersion 2. Every await fetch() call was silently failing at runtime.

## Workflows patched

### Dispatcher (rGrnCr5mPFP2TIc7) — 4 nodes
- fc1 (Fetch Client Config): fetch->httpRequest, added timezone to Supabase select
- rt1 (Refresh Token If Needed): fetch->httpRequest, URL-encoded form body uses json:false + manual JSON.parse
- gs1 (Get Free Slots): fetch->httpRequest, timezone-aware slot generation with getUTCOffsetMinutes()
- cb1 (Create Booking): fetch->httpRequest, fixed hvac_call_log columns (booking_success, appointment_date, job_type_booked, booking_reference, call_tier, call_type)

### Onboarding (kz1VmwNccunRMEaF) — multiple fixes
- Send Setup Emails: fixed return format (return {...} -> return [{ json: {...} }])
- Retell nodes: assigned credential B7LTZsD2qZHSXTUb to node-create-flow, node-create-agent, node-publish-agent
- Update Booking Fields: full rewrite using httpRequest
- Send Google OAuth Email: fixed d.extractedData?.client_email path + fetch->httpRequest
- Send Outlook OAuth Email: same fixes
- Send Placeholder Email: same fixes + company_name path

### Integration Connected Handler (a0IAwwUJP4YgwgjG) — 5 nodes
- fc1: full rewrite, Supabase GET via httpRequest
- aq1: full rewrite, syntharra_activation_queue POST via httpRequest
- ea1, ce1, ua1: targeted SMTP2GO fetch->httpRequest replacement

## E2E test results (all 5 steps passing)

- Step 1 (Onboarding webhook): HTTP 200
- Step 2 (Supabase check): plan_type=premium, integration_type=google, agent_status=oauth_sent, scheduling_platform=Google Calendar, slot_duration_minutes=60
- Step 3 (Integration Connected): activation queue entry FOUND
- Step 4 (Dispatcher get_slots): structural OK (HTTP 500 with 403 from Google - expected, no real token)
- Step 5 (Cleanup): test data deleted

## Key learnings

- n8n httpRequest: json:true auto-serializes body + parses response. json:false sends raw string (needed for application/x-www-form-urlencoded Google token refresh) - must JSON.parse() the response manually.
- n8n PUT payload: only {name, nodes, connections, settings} accepted. tags, active, activeVersion are read-only and cause 400 errors.
- Onboarding data flow: form data is nested inside d.extractedData at email nodes, not at root d.client_email.
- Integration Connected Handler routes to Alert Unexpected Status if integration_status != connected - OAuth server normally sets this, but test must pre-set it via Supabase PATCH.

## Two remaining fetch() occurrences (not Phase 2 scope)

- HVAC Scenario Test Runner v4: Build Scenarios node
- Newsletter Unsubscribe Webhook: Update Supabase node
