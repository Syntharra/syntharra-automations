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
