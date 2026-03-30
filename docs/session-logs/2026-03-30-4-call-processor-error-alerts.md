# Session Log — 2026-03-30 (Session 4)

## Summary
Rewired Internal Notification in both call processors to fire ONLY on error conditions,
routing to alerts@syntharra.com instead of admin@syntharra.com on every call.

## Changes Made

### n8n — HVAC Standard Call Processor (Kg576YtPM9yEacKn)
- Internal Notification node: completely rewritten with error-only logic
- Connection rewired: removed from Should Notify? true branch
- Now runs after Supabase: Log Call on EVERY call (self-gates internally)
- Activated (published)

### n8n — HVAC Premium Call Processor (STQ4Gt3rH8ptlvMi)
- Internal Notification node: same error-only logic applied
- Connection rewired: removed from Should Notify? true branch
- Now runs after Log Call to Supabase on EVERY call (self-gates internally)
- Activated (published)

## Error Conditions Now Detected (both processors)

| Code | Trigger |
|---|---|
| SYSTEM_ERROR | disconnection_reason contains: error, error_inbound_webhook, error_llm_websocket, error_frontend_websocket, concurrency_limit_reached, server_error, rate_limit_error, webhook_failed |
| CALL_STATUS_ERROR | call_status = 'error' or 'failed' |
| TRANSFER_FAILED | disconnection_reason: dial_failed, dial_busy, dial_no_answer, dial_no_answer_voicemail, transfer_failed, transfer_to_human_failed, voicemail, inactivity, machine_detected |
| TRANSFER_UNSUCCESSFUL | transfer_attempted=true AND transfer_success=false |
| ABNORMAL_ENDING | disconnection_reason: abandoned, call_ended_early |
| CLIENT_NOT_FOUND | _client_found=false (agent fired but agent_id not in Supabase) |
| CALL_TOO_SHORT | duration_seconds > 0 AND < 8 (likely failed connection) |
| GEOCODE_ERROR | geocode_status = 'error' |
| GPT_ANALYSIS_FAILED | _gpt_failed = true |

## Alert Email
- Sender: Syntharra Alerts <noreply@syntharra.com>
- To: alerts@syntharra.com
- Subject: 🚨 [CALL {ERROR_TYPE}] — {company_name} | {call_id}
- Red accent for CRITICAL (SYSTEM_ERROR, CALL_STATUS_ERROR, CLIENT_NOT_FOUND)
- Amber accent for WARNING (all others)
- Includes: call details table, all error conditions detected, transcript snippet (first 400 chars)
- Silent (no email) when no errors detected
