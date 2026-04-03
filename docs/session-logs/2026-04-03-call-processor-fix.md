# Session Log — 2026-04-03 — Call Processor Fix + Test Suite

## What Was Done

### Root Cause: Call Processor Broken Since OpenAI Key Expiry
- The HVAC Standard Call Processor (Kg576YtPM9yEacKn) had a dead OpenAI credential
- Every Retell post-call webhook was 401-failing silently at the GPT Analyze Transcript node
- Zero calls were being logged to hvac_call_log — this was a silent production bug

### Fix Applied
1. **Replaced OpenAI node with Groq** — model: llama-3.3-70b-versatile
   - Required two-node pattern: Code (builds prompt strings) + HTTP Request (fires call)
   - `fetch()` and `$http.request()` both unavailable in n8n Code nodes — HTTP node required
   - Body pattern: `contentType: raw`, `rawContentType: application/json`, `body: ={ JSON.stringify(Ellipsis) }`
2. **Fixed Supabase Log Call node** — IIFE expression evaluated empty
   - Moved all normalisation to Parse Lead Data (code node)
   - Supabase node now uses simple flat `$json.field` references
3. **Expanded field coverage** — all hvac_call_log columns now written:
   - caller_address, job_type (normalised), caller_sentiment (INT 1-5), vulnerable_occupant,
   - transfer_attempted, emergency, call_tier, notes, geocode_status
4. **job_type normalisation map** — Groq returns "Residential", "Commercial" etc → mapped to enum

### Test Suite Built
- File: `tests/standard-call-processor-test.py`
- 20 scenarios across: repair, install, emergency, maintenance, wrong number, spam,
  out-of-area, transfer, hang-up, commercial, pricing, phonetic phone, frustrated caller,
  vendor, job applicant, dedup, short call, vulnerable+transfer, address-only
- Final result: **78/78 assertions — 100%** ✅
- Self-cleaning: all test rows deleted after run

### Skill Created
- `skills/standard-call-processor-testing-SKILL.md` — full reference for running and debugging

## Key Learnings
- hvac_call_log.caller_sentiment is INTEGER (1-5), not a string enum
- SB_ANON RLS prevents test rows from appearing — always use SB_SVC for test reads
- n8n Code nodes: no fetch(), no $http — use HTTP Request node for outbound calls
- n8n HTTP Request: IIFE in jsonBody fails — use contentType:raw + JSON.stringify expression
- Groq response format: choices[0].message.content (same as OpenAI)

## Files Changed
- `n8n workflow Kg576YtPM9yEacKn` — GPT node replaced, full field writes, normalisation
- `tests/standard-call-processor-test.py` — NEW 20-scenario test suite
- `skills/standard-call-processor-testing-SKILL.md` — NEW skill
- `docs/TASKS.md` — updated with call processor status
- `docs/FAILURES.md` — 6 new rows appended
