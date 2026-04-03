---
name: standard-call-processor-testing
description: >
  Complete reference for testing the HVAC Standard call processor (n8n workflow Kg576YtPM9yEacKn).
  Load when: running or extending the call processor test suite, debugging why calls aren't logging,
  modifying the Groq transcript analysis prompt, adding new hvac_call_log fields, or diagnosing
  Supabase write failures in the call processor.
  Test file: tests/standard-call-processor-test.py
  Status: 78/78 assertions passing across 20 scenarios — verified 2026-04-03
---

# Standard Call Processor — Testing Reference

> **Status: 78/78 ✅ — Verified 2026-04-03**
> Run: `python3 tests/standard-call-processor-test.py`
> Workflow: `Kg576YtPM9yEacKn` (HVAC Call Processor - Retell Webhook)
> Webhook: `https://n8n.syntharra.com/webhook/retell-hvac-webhook`

---

## Architecture — How the Call Processor Works

```
Retell Webhook
  → Filter: call_analyzed Only
  → Extract Call Data          (code node — extracts call fields)
  → Supabase: Lookup Client    (HTTP — matches agent_id to client record)
  → Parse Client Data          (code node — merges call + client data)
  → Check Repeat Caller        (code node — sets is_repeat_caller flag)
  → Build Groq Request         (code node — builds system+user prompt strings)
  → Groq: Analyze Transcript   (HTTP — POST to api.groq.com/openai/v1/chat/completions)
  → Parse Lead Data            (code node — parses Groq JSON, normalises fields)
  → Is Lead?                   (IF node — routes lead vs non-lead)
  → Supabase: Log Call         (HTTP — writes row to hvac_call_log)
  → HubSpot — Log Call Note    (code node — posts note to CRM contact)
```

---

## AI Model — Groq

| Item | Value |
|---|---|
| Provider | Groq |
| Model | `llama-3.3-70b-versatile` |
| Credential | `UfljdfOxkfTm76LE` (n8n httpHeaderAuth: "Groq API Key") |
| Endpoint | `https://api.groq.com/openai/v1/chat/completions` |
| Temperature | 0.2 |
| Max tokens | 600 |

**Why Groq, not OpenAI:** The original OpenAI credential (`1uzBYwyR7Q7bdkZe`) had an invalid/expired API key.
Switched to Groq on 2026-04-03. Groq returns OpenAI-compatible response format (`choices[0].message.content`).

**Two-node pattern (required):**
- `Build Groq Request` (code node) — builds `groq_system` and `groq_user` strings
- `Groq: Analyze Transcript` (HTTP node) — uses `contentType: raw` + `body: ={{ JSON.stringify({...}) }}`

Why two nodes: n8n expression engine can't evaluate complex expressions inside `specifyBody: json` jsonBody field.
The workaround is `contentType: raw` + `rawContentType: application/json` + a `JSON.stringify(...)` expression in `body`.

**CRITICAL — do NOT use:**
- `fetch()` in n8n Code nodes — not defined
- `$http.request()` in n8n Code nodes — not available on this n8n version
- IIFE `={{ (() => { ... })() }}` in HTTP node jsonBody — expression engine rejects it
- `specifyBody: json` with complex nested objects — use `contentType: raw` instead

---

## hvac_call_log Schema (key columns)

| Column | Type | Source | Notes |
|---|---|---|---|
| `call_id` | text | Retell payload | Primary key for dedup |
| `agent_id` | text | Retell payload | Links to client |
| `company_name` | text | Supabase lookup | Client's company |
| `call_tier` | text | `plan_type` from client record | "Standard" or "Premium" |
| `caller_name` | text | Groq | null if not captured |
| `caller_phone` | text | Groq | falls back to `from_number` |
| `caller_address` | text | Groq | null if not given |
| `service_requested` | text | Groq | Repair/Maintenance/Installation/Estimate/Emergency/General/Other |
| `job_type` | text | Groq (normalised) | See enum below |
| `lead_score` | int | Groq | 1-10 |
| `is_lead` | bool | Groq / Parse Lead | true if score >= 5 AND service need |
| `is_hot_lead` | bool | Groq | true if score >= 7 |
| `urgency` | text | Groq | Low/Medium/High/Emergency |
| **`caller_sentiment`** | **int** | **Groq** | **1-5 integer — NOT a string enum** |
| `vulnerable_occupant` | bool | Groq | elderly/child/medical mentioned |
| `transfer_attempted` | bool | Groq | live transfer offered/initiated |
| `emergency` | bool | Parse Lead | true when urgency=Emergency |
| `summary` | text | Groq | 1-2 sentence summary |
| `notes` | text | Groq | additional details |
| `geocode_status` | text | (not yet wired) | empty string default |
| `duration_seconds` | int | Retell payload | call duration |

### job_type Enum (normalised in Parse Lead Data)
Groq often returns variants not in the enum. Parse Lead Data normalises all to:
`Repair` | `Installation` | `Maintenance` | `Emergency` | `General Enquiry` | `Wrong Number` | `Spam` | `Vendor` | `Job Application` | `Other`

Normalisation map handles: "Residential" → Repair, "Commercial" → Repair, "Inquiry" → General Enquiry, etc.

### caller_sentiment — INTEGER (1-5)
⚠️ `caller_sentiment` is an integer column in Supabase, NOT a string.
Groq returns a number naturally. String values get mapped: Angry=1, Frustrated=2, Neutral=3, Satisfied/Positive=5.
Do NOT assert this is a string. Assert `("is_int",)` or check the numeric range.

---

## Test Suite — 20 Scenarios

| # | Scenario | Key Assertions |
|---|---|---|
| 1 | Standard repair lead | caller_name, phone, address, job_type=Repair, lead_score≥6, is_lead=True |
| 2 | New install quote | job_type=Installation, lead_score≥6, is_lead=True |
| 3 | Emergency — elderly, no heat | urgency=Emergency, vulnerable_occupant=True, lead_score≥7 |
| 4 | Maintenance tune-up | service_requested, job_type=Maintenance, is_lead=True |
| 5 | Existing customer follow-up | caller_name, is_lead=True, summary |
| 6 | Wrong number | is_lead=False, summary |
| 7 | Spam robocall | is_lead=False |
| 8 | Out of service area | is_lead=False, summary |
| 9 | Live transfer — gas emergency | transfer_attempted=True, urgency present, summary |
| 10 | Caller hangs up before address | caller_name, caller_phone, summary |
| 11 | High-value commercial | lead_score≥8, is_lead=True, caller_name |
| 12 | Pricing enquiry only | summary, lead_score≥0 (stochastic — no is_lead assertion) |
| 13 | Phonetic phone number | caller_phone decoded correctly, is_lead=True |
| 14 | Frustrated repeat customer | caller_name, is_lead=True, caller_sentiment is_int |
| 15 | Vendor call | is_lead=False, summary |
| 16 | Job applicant | is_lead=False, summary |
| 17 | Dedup — no duplicate on re-send | is_lead=True, only 1 row after re-fire |
| 18 | Very short call — no info | summary |
| 19 | Emergency with vulnerable + transfer | vulnerable_occupant=True, transfer_attempted=True, urgency=Emergency |
| 20 | Caller gives only phone, no address | caller_name, caller_phone, is_lead=True |

---

## Running the Tests

```bash
# Full suite
python3 tests/standard-call-processor-test.py

# Credentials embedded — uses SB_SVC (service role) for reads
# This is intentional: bypasses RLS to see test rows immediately
# SB_ANON has RLS restrictions that cause false "row not found" on fresh writes
```

**Timing:** ~40s per scenario (Groq processing + Supabase write). Full suite ≈ 14 minutes.
Runs all 20 sequentially with unique call_ids (`cptest_{TS}_{sid:02d}`).
Self-cleaning — deletes all test rows at the end.

---

## Polling Pattern (Use SB_SVC, not SB_ANON)

```python
# CORRECT — service role bypasses RLS, sees rows immediately
_, rows = http(f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}&select=*",
    headers={"apikey": SB_SVC, "Authorization": f"Bearer {SB_SVC}"})

# WRONG — SB_ANON has RLS; rows appear "missing" even after successful write
_, rows = http(f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}&select=*",
    headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}"})
```

**Poll every 5s up to 40s total.** Groq + n8n processing typically completes in 8-15s.

---

## Diagnosing Failures

| Symptom | Cause | Fix |
|---|---|---|
| Webhook returns 200 but no row | Execution erroring silently | Check n8n exec status: `GET /api/v1/executions?workflowId=Kg576YtPM9yEacKn&limit=3` |
| Execution status=error, node=GPT | Groq credential expired/wrong | Check Groq API key in vault. Credential ID: `UfljdfOxkfTm76LE` |
| Execution status=success but no row | Supabase Log Call on branch 1 | Complex IIFE expression in jsonBody evaluated to empty — use flat `$json.field` refs only |
| Row logged but `caller_address` empty | Groq used different key name | Parse Lead Data checks: `caller_address || address || service_address || location` |
| `job_type` shows "Residential" | Groq hallucinating outside enum | Normalisation map in Parse Lead Data covers this — check map is deployed |
| `caller_sentiment` type error | Column is INT not text | Never write a string to this column — always a number 1-5 |
| Test polling returns no rows | Using SB_ANON with RLS | Switch to SB_SVC for test reads |
| Dedup test creates 2 rows | Check Repeat Caller node not working | Check `check_repeat_caller` code node — should exit early if call_id already exists |

---

## Adding a New Assertion Field

1. Add the field to the Groq system prompt (in `Build Groq Request` code node)
2. Add normalisation to `Parse Lead Data` code node if needed
3. Add the column to the `Supabase: Log Call` jsonBody expression
4. Add the assertion to the scenario(s) in `tests/standard-call-processor-test.py`
5. Run the test suite and verify pass

---

## Groq Stochasticity Rules

Some assertions are intentionally NOT strict because Groq output varies slightly across runs:

- `job_type` for ambiguous calls (wrong number, short calls) — may return "Other" or "Wrong Number"
- `is_lead` for pricing-only enquiries — may be True or False depending on how Groq reads intent
- `caller_sentiment` — always assert `("is_int",)` not a specific value unless the scenario is extreme

**Rule: if a scenario fails only 1 in 3 runs, fix the assertion — not the prompt.**
**Rule: if a scenario fails consistently, fix the prompt or normalisation.**

---

## Credential Quick Reference

| Key | Value | Used for |
|---|---|---|
| `N8N_KEY` | ends in `NqU` | n8n API execution polling |
| `SB_SVC` | ends in `qsg` | Supabase writes + test reads (service role) |
| `SB_ANON` | ends in `yL0` | NOT for test reads — RLS restricts |
| Groq credential | `UfljdfOxkfTm76LE` | httpHeaderAuth in n8n |

---

## Session History

| Date | What changed |
|---|---|
| 2026-04-03 | Initial build — replaced broken OpenAI node with Groq two-node pattern |
| 2026-04-03 | Fixed Supabase body — removed IIFE, switched to flat `$json.field` expressions |
| 2026-04-03 | Fixed sentiment — column is INT 1-5, not string enum |
| 2026-04-03 | Added full field normalisation to Parse Lead Data |
| 2026-04-03 | Test suite built, iterated to 78/78 (100%) across 20 scenarios |
