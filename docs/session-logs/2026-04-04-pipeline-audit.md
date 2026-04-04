# Session Log — 2026-04-04 — pipeline-audit

## What was done
1. E2E test ran 74/90 — all 16 failures in Phases 4+5 (Retell agent + flow verification)
2. Diagnosed: E2E test RETELL_KEY env var pointed to stale key. n8n uses correct key.
3. Fixed: embedded correct Retell key as default fallback in e2e-test.py
4. Re-ran E2E: 90/90 ✅
5. Dan reported onboarding email missing phone numbers
6. Diagnosed: Build Onboarding Pack HTML used wrong field names (d.ai_phone_number, d.transfer_phone_number)
7. Fixed field names to d.twilio_number and d.transfer_phone
8. Dan flagged transfer number logic was wrong (emergency should only override if client says yes)
9. Full Jotform audit: compared all 55 live questions vs Parse JotForm Data node
10. Found 4 critical gaps: q73 custom greeting (q38 dead), q72 greeting style, q68 after-hours transfer, q69 emergency gate
11. Fixed all 4 in Parse JotForm Data + Build Retell Prompt
12. Fixed transfer number priority using q69 gate
13. Re-ran E2E with VerifyAudit HVAC: 90/90 ✅

## Mandatory Reflection

1. What did I get wrong or do inefficiently?
   Made two incorrect changes to transfer logic before arriving at correct answer. Should have read
   the original code comment AND asked to clarify spec before touching anything.

2. What assumption was wrong?
   Assumed emergency_phone was always meant to override transfer_phone. The q69 gate exists
   precisely to make this conditional — I missed it entirely.

3. What would I do differently?
   On any logic question involving field priority, always find the gate question on the form first.
   Every Jotform conditional question exists for a reason.

4. What pattern emerged?
   Fields added to Jotform after the Parse node was last written will silently be ignored forever.
   Rule: any Jotform question addition must update Parse node in same session.

5. What was added to skill files?
   hvac-standard: full Jotform field map, correct transfer logic spec, email field names
   e2e-hvac-standard: new fields to add to test payload, RETELL_KEY note

6. Did I do anything unverified?
   The new q68/q69/q72/q73 fields are now parsed and written to Supabase extractedData,
   but the E2E test payload doesn't yet send those fields — so Supabase assertions for them
   are not confirmed green. Needs E2E payload extension next session.
