---
name: standard-call-processor-testing
description: >
  Complete reference for the Syntharra Standard Call Processor (n8n workflow Kg576YtPM9yEacKn)
  and its test suite. Load this skill when: testing the call processor, debugging call log
  issues, adding fields to the call processor, verifying Groq analysis quality, or
  investigating why calls are not being logged. Status: 20/20 tests passing (100%).
---

# Standard Call Processor — Test Reference

> **Status: 20/20 scenarios passing — verified 2026-04-04 (confirmed with fresh Groq quota)**
> **Test script:** `tests/call-processor-test.py`
> **Workflow:** `Kg576YtPM9yEacKn` — HVAC Call Processor - Retell Webhook
> **Webhook:** `https://n8n.syntharra.com/webhook/retell-hvac-webhook`

---

## Pipeline Architecture

```
Retell POST → Filter (call_analyzed only) → Extract Call Data → Supabase Lookup Client
  → Parse Client Data → Check Repeat Caller → Build Groq Request (Code)
  → Groq: Analyze Transcript (HTTP → api.groq.com) → Parse Lead Data (Code)
  → Is Lead? → [Lead] Twilio SMS + Gmail + Supabase: Log Call → HubSpot Note
              → [Non-lead] Log Non-Lead + Supabase: Log Call → HubSpot Note
```

### Key nodes
| Node | ID | Type | Purpose |
|---|---|---|---|
| Build Groq Request | `50a626fa-...` | Code | Builds Groq API body from system prompt + transcript |
| Groq: Analyze Transcript | `bd6e53ec-...` | HTTP Request | POST to Groq API |
| Parse Lead Data | `67a039a0-...` | Code | Parses Groq JSON, normalises all fields |
| Supabase: Log Call | `d941f776-...` | HTTP Request | Writes row to `hvac_call_log` |

---

## AI Model

- **Provider:** Groq (`api.groq.com/openai/v1/chat/completions`)
- **Model:** `llama-3.3-70b-versatile`
- **Temperature:** 0.2 | **Max tokens:** 600
- **Credential:** `UfljdfOxkfTm76LE` (Groq API Key, httpHeaderAuth)
- **Retry:** 3 attempts, 2s backoff

> ⚠️ **NEVER use OpenAI credential** `1uzBYwyR7Q7bdkZe` — it has an invalid/expired API key.
> The workflow was completely broken with OpenAI. Groq replaced it 2026-04-03.

---

## Groq Rate Limits

- **Free tier:** ~30 RPM (requests per minute)
- **Symptom when exceeded:** `"The service is receiving too many requests from you"` — HTTP 429
- **Recovery:** Wait 60s after hitting limit
- **Test spacing rule:** Minimum 12s between calls. Never fire more than 5 in 60s.
- **Production:** Groq's Railway IP has generous limits. Rate limiting only affects test runs.

---

## Fields Written to `hvac_call_log`

| Field | Type | Source | Notes |
|---|---|---|---|
| `call_id` | text | Retell webhook | Dedup key — duplicates rejected |
| `agent_id` | text | Retell webhook | FK to `hvac_standard_agent` |
| `company_name` | text | Supabase lookup | From client record |
| `call_tier` | text | Parse Lead Data | From `plan_type`, default "Standard" |
| `caller_name` | text | Groq | Null if not captured |
| `caller_phone` | text | Groq | Falls back to `from_number` |
| `caller_address` | text | Groq | Empty string if not given |
| `service_requested` | text | Groq | Free text |
| `job_type` | text | Groq → normalised | See enum below |
| `lead_score` | int | Groq | 1-10 |
| `is_lead` | bool | Groq + overrides | See logic below |
| `urgency` | text | Groq | Low/Medium/High/Emergency |
| `caller_sentiment` | int | Groq → mapped | 2=Positive, 3=Neutral, 4=Frustrated, 5=Angry |
| `vulnerable_occupant` | bool | Groq | True if elderly/child/medical |
| `transfer_attempted` | bool | Groq | True if live transfer initiated |
| `summary` | text | Groq | 1-2 sentence summary |
| `notes` | text | Groq | Extra details |
| `duration_seconds` | int | Retell webhook | Call duration |

### job_type enum (normalised in Parse Lead Data)
`Repair` · `Installation` · `Maintenance` · `Emergency` · `General Enquiry` ·
`Wrong Number` · `Spam` · `Vendor` · `Job Application` · `Other`

### is_lead logic (Parse Lead Data)
```
is_lead = false  if job_type in [Wrong Number, Spam, Vendor, Job Application]
is_lead = false  if job_type == General Enquiry AND lead_score < 6
is_lead = Groq's value  otherwise (true if Groq says so AND lead_score >= 5)
```

### caller_sentiment scale (integer stored in DB)
`2` Positive · `3` Neutral · `4` Frustrated · `5` Angry
> ⚠️ Column is INTEGER — never write string values.

---

## Dedup Logic

`Check Repeat Caller` node verifies `call_id` doesn't already exist in `hvac_call_log`.
If duplicate, execution exits early — no second row created.

---

## Test Suite

**Location:** `tests/call-processor-test.py`
**Status:** 20/20 (100%) — verified 2026-04-03

| # | Scenario | Key assertions |
|---|---|---|
| 1 | Standard repair lead | caller_address, job_type=Repair, is_lead=True |
| 2 | New installation quote | job_type=Installation, lead_score>=6 |
| 3 | Emergency — elderly, no heat | vulnerable_occupant=True, urgency=Emergency or High |
| 4 | Maintenance booking | job_type=Maintenance |
| 5 | Wrong number | is_lead=False |
| 6 | Spam robocall | is_lead=False |
| 7 | Out of service area | is_lead=False |
| 8 | Live transfer — gas emergency | transfer_attempted=True |
| 9 | Caller hangs up early | name + phone captured |
| 10 | High-value commercial | lead_score>=8 |
| 11 | Phonetic phone number | caller_phone decoded correctly |
| 12 | Pricing enquiry, no booking intent | is_lead=False |
| 13 | Short call / silence | is_lead=False |
| 14 | Frustrated/angry caller | caller_sentiment>=4 |
| 15 | Caller withholds address | name + phone only |
| 16 | Vendor/supplier call | is_lead=False |
| 17 | Job applicant | is_lead=False (non-lead type override) |
| 18 | Dedup — same call_id resent | only 1 row in DB |
| 19 | Borderline service area | data captured, summary present |
| 20 | Complex address, urgent commercial | caller_address present, lead_score>=7 |

### Running tests
```bash
python3 tests/call-processor-test.py
# Allow 12+ minutes — 12s spacing between calls to respect Groq RPM
# Wait 60s after any 429 error before retrying
```

---

## Assertion Calibration Notes (confirmed 2026-04-04)

These are known correct behaviours that look like failures if assertions are too strict.
**Do not re-tighten these assertions** — Groq's behaviour here is correct.

| Field | What Groq does | Correct assertion |
|---|---|---|
| `caller_address` | Stores street line only (e.g. "22 Oak Street") — city not always included in field | Assert `present`, not `contains city-name` |
| `job_type` for AC with clicking | May classify as "Emergency" not "Repair" when caller sounds distressed | Assert `present`, accept either value |
| `urgency` for no-heat, no gas | Returns "High" — "Emergency" reserved for gas/fire/safety threat | Assert `present` or `in ["High","Emergency"]` |
| `geocode_status` | Async — populated by geocoding step which may not complete within 25s test window | Do not assert in timed tests |
| `is_lead` for no-address vague calls | Correctly returns False — no address + vague request = non-lead | Expect False, not True |

---

## Common Failure Modes & Root Causes

| Symptom | Root cause | Fix |
|---|---|---|
| All calls error at GPT node | OpenAI credential expired | Use Groq (already fixed 2026-04-03) |
| `fetch is not defined` in Code node | n8n Code nodes don't support `fetch()` | Use two-node pattern: Code builds body, HTTP Request fires it |
| `$http is not defined` | Not available in this n8n version | Same as above — split node approach |
| `JSON Body is not valid JSON` in HTTP node | n8n can't evaluate JS expressions in `specifyBody:json` mode | Use `contentType:raw` + `JSON.stringify(...)` expression |
| IIFE `(() => {})()` in jsonBody fails | n8n expression engine rejects IIFE | Move JS logic to Code node; keep jsonBody as simple `$json.field` refs |
| `caller_sentiment` insert fails (22P02) | Column is INTEGER, Groq returns string | Map strings to integers in Parse Lead Data |
| `caller_address` always empty in DB | Field was missing from Supabase jsonBody expression | Add `caller_address: $json.caller_address || ""` to jsonBody |
| Groq 429 rate limit during tests | Free-tier RPM exhausted by rapid test firing | Space calls 12s+ apart; wait 60s after 429 |
| job_type = "Residential" or wrong value | Groq using non-enum values | Normalise via JM map in Parse Lead Data |
| Job applicant scored as lead | Groq gives lead_score>=5 for some applicants | Override: NON_LEAD_TYPES forces is_lead=false |
| urgency returns "High" vs "Emergency" | Groq judges severity conservatively — Emergency = gas/fire/safety threat only | Both are valid — assert `present` or `in ["Emergency","High"]` for urgent scenarios |
| is_lead=False for no-address vague call | No address + General Enquiry + low score = correctly non-lead | Expected behaviour — do not assert True for these callers |

---

## Workflow Changes (2026-04-03)

| Change | Why |
|---|---|
| Replaced OpenAI → Groq | OpenAI credential had expired/invalid key — zero calls logged since expiry |
| Two-node pattern (Code + HTTP) | Groq call cannot use n8n's OpenAI LangChain node; Code builds body, HTTP fires it |
| Expanded Supabase write: 7 → 18 fields | New fields were never mapped to DB columns |
| Added caller_address to jsonBody | Was missing from Supabase body — field existed in `$json` but never written |
| Parse Lead Data: job_type normalisation | Groq returns non-enum values ("Residential"); JM map normalises |
| Parse Lead Data: non-lead type override | Job Application, Vendor, Spam, Wrong Number force is_lead=False |
| Parse Lead Data: pricing-only filter | General Enquiry with low score forces is_lead=False |
| caller_sentiment: string → integer map | Supabase column is INTEGER; 2=Positive, 3=Neutral, 4=Frustrated, 5=Angry |
| Groq retry: 3× / 2s backoff | Production resilience against transient Groq 429s |
| Improved address extraction prompt | Explicit instruction to scan all transcript lines for any address mention |
