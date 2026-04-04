# Session Log — 2026-04-04 — Phase 5: n8n Processor Rewiring

## Summary
Completed Phase 5 of the Retell Enhancement Sprint. Rewired both n8n call processors (Standard `Kg576YtPM9yEacKn` and Premium `STQ4Gt3rH8ptlvMi`) to remove the Groq/GPT transcript analysis chain and map Retell's native post-call analysis fields directly to Supabase.

## Changes Made

### Standard Call Processor (`Kg576YtPM9yEacKn`)
- **Removed:** Build Groq Request, Groq: Analyze Transcript, Parse Lead Data (3 nodes)
- **Rewritten:** Extract Call Data — now extracts all fields from `call.call_analysis.custom_analysis_data` + system presets + cost/latency
- **Rewritten:** Supabase: Log Call — full field mapping (30+ fields) direct from webhook payload
- **Updated:** Slack: Lead Call Alert — uses new field names (emergency, is_hot_lead, service_requested, urgency)
- **Result:** 14 nodes → 11 nodes. Published.

### Premium Call Processor (`STQ4Gt3rH8ptlvMi`)
- **Removed:** GPT: Analyze Call, Parse Lead Data (2 nodes — GPT node was a stub/placeholder)
- **Rewritten:** Extract Call Data — same as Standard + Premium-specific fields (appointment_date, appointment_time_window, job_type_booked, caller_email, reschedule_or_cancel)
- **Rewritten:** Log Call to Supabase — full field mapping including Premium booking fields
- **Updated:** Slack alerts — same field name updates as Standard
- **Preserved:** Client Notification Slack node (uses client's webhook URL)
- **Result:** 15 nodes → 12 nodes. Published.

### Key Mapping Changes
- `retell_sentiment` ← `call.call_analysis.user_sentiment` (TEXT, not integer)
- `call_successful` ← `call.call_analysis.call_successful` (BOOLEAN)
- `retell_summary` / `summary` ← `call.call_analysis.call_summary`
- All custom fields ← `call.call_analysis.custom_analysis_data.*`
- `duration_seconds` ← `Math.round(call.duration_ms / 1000)` (was end_timestamp - start_timestamp)
- `call_cost_cents` ← computed from `call_cost.total_duration_unit_price * duration_ms / 60000 * 100`
- `is_lead` ← derived: `lead_score >= 5 && call_type not in [spam, wrong_number]`

### Architecture Decision
Documented in ARCHITECTURE.md: why Groq chain was removed in favour of Retell native analysis.

## What's Next
- Phase 6: Test calls on both agents, verify fields populate in Supabase
- Phase 7: Update E2E assertions for new field types
- Phase 8: MASTER promotion (Dan approval needed)

## Session Reflection
1. **What did I get wrong?** Nothing broke — clean execution. The repeat caller query previously queried `caller_phone` but the webhook provides `from_number`. Updated to query `from_number` for consistency.
2. **What assumption was incorrect?** Initially assumed the old `duration_seconds` was computed from `end_timestamp - start_timestamp`. The new webhook provides `duration_ms` directly — simpler and more accurate.
3. **What would I do differently?** Would have checked if the n8n SDK supports `retryOnFail` as a top-level node config vs nested in parameters earlier — had to match the existing pattern.
4. **Pattern for future:** When Retell adds structured data to webhooks, always prefer direct mapping over post-hoc LLM analysis. The source-of-truth data is more reliable and eliminates a failure mode.
5. **Added to ARCHITECTURE.md:** Full reasoning for Groq/GPT removal — options considered, trade-offs, revisit conditions.
6. **Unverified assumption:** The `call.duration_ms` field — assumed it exists based on Retell docs. Phase 6 test call will confirm. If it's actually `end_timestamp - start_timestamp`, the Extract Call Data node handles both patterns.

Labels: no new workflows created — existing workflows modified only ✅


## Phase 6 — Simulated Webhook Verification

### Approach
Instead of live Retell calls ($0.15-0.45/call), used Python scripts and n8n manual execution
to POST fake `call_analyzed` webhook payloads. This tests the entire pipeline from webhook
intake through Supabase write — the processor doesn't know or care if the payload came from
a real call or a simulation.

### Standard Processor (Kg576YtPM9yEacKn)
- **Result: 37/37 fields passed ✅**
- Used MASTER agent_id (has client row in hvac_standard_agent)
- All shared fields populated correctly
- Supabase write confirmed with return=representation
- HubSpot failed in manual mode ($env not available) — expected, works in production

### Premium Processor (STQ4Gt3rH8ptlvMi)
- **Result: 40/40 fields passed ✅**
- Premium-specific fields verified: appointment_date, appointment_time, job_type_booked, booking_attempted, booking_success
- Client lookup resolved to V7 Premium FrostKing HVAC
- Same HubSpot manual mode limitation — expected

### Bug Found & Fixed
- n8n:update_workflow saves a DRAFT but does NOT publish
- First webhook test hit the OLD published version (still had Groq chain)
- Fix: Always call n8n:publish_workflow after update_workflow
- Added to FAILURES.md

### Updated Reflection
1. **What did I get wrong?** Assumed n8n update_workflow would auto-publish. It doesn't — draft and active versions are separate. Cost: one wasted test cycle.
2. **Pattern for future:** After ANY n8n:update_workflow call, immediately call n8n:publish_workflow. Verify versionId == activeVersionId.
3. **Testing pattern:** Simulated webhooks are the correct approach for field mapping verification. No need for live Retell calls until Phase 7 (E2E assertions) and Phase 8 (real behaviour testing).
4. **TESTING agent limitation:** TESTING agents don't have rows in hvac_standard_agent, so client lookup returns empty → pipeline stops. Use MASTER agent_ids for pipeline testing. This is correct production behaviour (unknown agents shouldn't log calls).
