# HVAC Premium Pipeline

## Status: IN DEVELOPMENT

## Architecture

### Retell Agent
- Agent ID: `agent_02766ab2c9a633e3351bbd4fc7`
- Flow ID: `conversation_flow_acc544e8ec84` (18 nodes)
- Webhook: `https://syntharra.app.n8n.cloud/webhook/retell-hvac-premium-webhook`
- Voice: retell-Sloane
- Post-call analysis: 17 fields (3 system presets + 14 custom)

### Conversation Flow — 18 Nodes
1. **greeting_node** — Custom greeting from Jotform
2. **identify_call_node** — Routes to correct node (10 edges, finetune examples)
3. **booking_capture_node** — PRIMARY PATH: collects service, name, phone, address, date, time
4. **confirm_booking_node** — Reads back all details, confirms with caller
5. **check_appointment_node** — Caller checking on existing appointment
6. **reschedule_node** — Handles appointment rescheduling
7. **cancel_appointment_node** — Handles cancellation, offers rebook
8. **lead_fallback_node** — FALLBACK: collects lead details when booking not possible
9. **verify_emergency_node** — Confirms emergency, routes to transfer or priority booking
10. **callback_node** — Handles return calls, routes to booking if new need
11. **existing_customer_node** — Existing customer enquiries (no lookup, callback or transfer)
12. **general_questions_node** — FAQ from global prompt, offers booking after
13. **spam_robocall_node** — Ends spam calls
14. **Transfer Call** — Warm transfer with whisper summary
15. **Emergency Transfer** — Warm transfer with emergency brief
16. **transfer_failed_node** — Captures details if transfer fails
17. **Ending** — Offers further help
18. **End Call** — Ends call warmly

### Call Processor
- GPT-4o-mini analyzes transcript with premium-specific extraction
- 10 notification types: booking_confirmed, booking_failed, reschedule, cancellation, hot_lead, warm_lead, emergency, existing_customer, general_info, spam
- Branded HTML emails per notification type
- SMS alerts per notification type
- Multi-recipient support (up to 3 email + 3 SMS)
- Supabase logging to `hvac_premium_call_log`

### Post-Call Analysis Fields
System: call_summary, call_successful, user_sentiment
Custom: caller_name, caller_phone, caller_address, service_requested, booking_attempted, booking_success, appointment_date, appointment_time_window, job_type_booked, reschedule_or_cancel, call_type, urgency, is_hot_lead, lead_score

### Supabase Tables
- `hvac_premium_agent` — Client config (all standard + CRM/calendar fields)
- `hvac_premium_call_log` — Call records with booking data

### Files
- `prompt-builder-premium.js` — Builds Retell conversation flow + agent config from Jotform data
- `call-processor-parse-premium.js` — Parses GPT response, determines notification type, builds email/SMS
- `gpt-analysis-prompt-premium.js` — System prompt for GPT transcript analysis
- `n8n-call-processor-premium.json` — n8n workflow JSON (placeholder — full workflow in n8n-workflows/)
- `n8n-onboarding-premium.json` — n8n onboarding workflow
- `supabase-migration-premium.sql` — Table creation SQL

### TODO
- [ ] Deploy call processor to n8n
- [ ] Build configurable Jotform fields (estimate window toggle, CRM/calendar selection)
- [ ] Upgrade node prompts with per-client variable pricing/estimate handling
- [ ] Test full end-to-end flow
- [ ] Wire up calendar integration (check_availability, create_booking, reschedule_booking, cancel_booking tool calls)
- [ ] Wire up CRM integration (push contact/job to CRM)
