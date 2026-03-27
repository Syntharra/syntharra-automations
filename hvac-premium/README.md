# HVAC Premium Pipeline

## Status: In Development (Flow + Agent configured, workflows pending deployment)

## Architecture

### Retell Agent
- Agent ID: `agent_02766ab2c9a633e3351bbd4fc7`
- Flow: `conversation_flow_acc544e8ec84` (18 nodes)
- Voice: retell-Sloane
- Webhook: `https://syntharra.app.n8n.cloud/webhook/retell-hvac-premium-webhook`
- Post-call analysis: 17 fields (3 system + 14 custom)

### Conversation Flow (18 nodes)
1. greeting_node — static greeting
2. identify_call_node — routes to correct node (10 edges)
3. booking_capture_node — collects booking details (PRIMARY path)
4. confirm_booking_node — reads back and confirms appointment
5. check_appointment_node — handles "when is my appointment" calls
6. reschedule_node — reschedule existing appointment
7. cancel_appointment_node — cancel + offer rebook
8. lead_fallback_node — fallback lead capture when booking not possible
9. verify_emergency_node — confirms true emergency vs urgent
10. callback_node — returning missed calls
11. existing_customer_node — job/invoice/technician questions
12. general_questions_node — FAQ from global prompt
13. spam_robocall_node — end spam calls
14. Transfer Call — warm transfer to business
15. Emergency Transfer — warm transfer to emergency line
16. transfer_failed_node — capture details if transfer fails
17. Ending — "anything else?"
18. End Call — end warmly

### Call Processor (n8n)
- Webhook → Filter → Extract → Lookup Client (hvac_premium_agent) → GPT Analyze → Parse → Branch (notify/silent) → Log to Supabase → Notifications
- Notification types: booking_confirmed, reschedule, cancellation, emergency, booking_failed_lead, hot_lead, general_lead, follow_up_required, info_only, spam
- Multi-recipient email (up to 3) + SMS (up to 3)
- Internal notification to daniel@syntharra.com

### Files
- `prompt-builder-premium.js` — builds conversation flow + global prompt from Jotform data
- `call-processor-parse-premium.js` — parse GPT response + build notification HTML/SMS
- `gpt-analysis-prompt-premium.txt` — system prompt for GPT call analysis
- `n8n-call-processor-premium-v2.json` — full n8n workflow JSON
- `conversation-flow-premium-live.json` — authoritative copy of the live Retell flow
- `supabase-migration-premium.sql` — database schema

### Supabase Tables
- `hvac_premium_agent` — client config (includes CRM/calendar fields)
- `hvac_premium_call_log` — call records with booking fields

### TODO
- [ ] Deploy call processor workflow to n8n
- [ ] Run Supabase migration (create tables)
- [ ] Deploy onboarding workflow to n8n
- [ ] Update Jotform with booking/integration section
- [ ] Switch SMS from Twilio to Telnyx
- [ ] Build OAuth callback handler for CRM/calendar integrations
- [ ] Test end-to-end with a test client
