# Improvements — Session 2 (2026-03-27)

## E2E Test: 78/78 PASSED ✅

## Small Wins Completed

### 1. Transfer-failed email improvements
- Amber accent color (#d97706) for missed transfer emails
- "📵 Missed Transfer" header label
- Dedicated transfer-failed banner: "Call transfer failed. Caller unable to connect. Details captured, expecting callback."
- Transfer-failed SMS header: "MISSED TRANSFER" instead of "NEW LEAD"

### 2. Formatted timestamps in lead emails
- Raw ISO timestamps replaced with readable format: "Thu, Mar 27, 4:59 PM"
- Uses the client's configured timezone from Supabase

### 3. Scenario runner dynamic agent (v5)
- No longer hardcodes Arctic Breeze agent_id
- Dynamically fetches the latest agent from Supabase
- Falls back to Arctic Breeze if no agents exist
- Added 2 new scenarios: S16 (Transfer Failed), S17 (Callback Returning Call)
- Total scenarios: 17

## Medium Wins Completed

### 4. Dead Letter Queue
- New Supabase table: `call_processor_dlq`
- Captures call_id, agent_id, payload, error_message
- Connected to Supabase Lookup Client and Supabase Log Call error paths
- No call data is silently lost — failures are logged for manual review

### 5. Retell cleanup
- 60 orphaned conversation flows deleted from Retell
- Only 2 flows remain (both linked to active agents)
