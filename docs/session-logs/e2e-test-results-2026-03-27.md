# E2E Test Results — 2026-03-27

**Result: 78/78 PASSED**
**Mode: TEST (no Stripe customer ID)**
**Test Company: Polar Peak HVAC**
**Timestamp: 2026-03-27 03:09:14 UTC**

## Pipeline Stages Tested

### 1. Jotform Onboarding Webhook
- HTTP 200 accepted
- All 50+ fields submitted

### 2. n8n Workflow Execution
- Onboarding workflow k0KeQxWb3j3BbQEk executed successfully (exec 573)

### 3. Supabase — All Fields (42 checks)
- All fields correctly mapped and stored
- Multi-notification fields (email_2, email_3, sms_2, sms_3) all saved
- Membership program, transfer triggers, do_not_service all populated
- agent_id and conversation_flow_id correctly generated

### 4. Retell Agent
- Created with correct name, voice (Nico/male), webhook URL
- Language set to multilingual
- Published via API

### 5. Retell Conversation Flow
- 12 nodes created correctly
- flex_mode off, start_speaker agent
- All node types present: greeting, identify, leadcapture, emergency, callback, existing, FAQ, spam, transfer, transfer_failed, ending, end
- Greeting contains agent name
- Global prompt contains company info block

### 6. Call Processor
- Fake call webhook accepted
- GPT analysis extracted: caller_name, caller_phone, service_requested (Repair), lead_score (8), is_lead (true), summary
- Dedup check passed (no duplicate row on repeat webhook)
- n8n call processor execution successful (exec 575)

### 7. Stripe Gate
- Correctly skipped Twilio purchase in test mode
- Onboarding email sent to daniel@syntharra.com

### 8. Cleanup
- All test data removed from Supabase and Retell

## Live Agent Status
- Arctic Breeze HVAC agent_d180e1bd5b9b724c8f616a0415 — active, webhook connected
- Live flow conversation_flow_ed1ff4a600af — 12 nodes, all routing correct
- Demo agents (Jake + Sophie) — published and active

## Notes
- hvac_standard_agent table is currently empty (Arctic Breeze was cleaned up in a prior session)
- Arctic Breeze agent has conversation_flow_id: null in Retell API (flow is managed separately via flow ID ed1ff4a600af)
