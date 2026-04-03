---
name: standard-call-processor-testing
description: >
  Complete reference for testing the Syntharra Standard Call Processor (n8n workflow Kg576YtPM9yEacKn).
  Load this skill when: running call processor tests, debugging call log issues, adding new fields to
  the call processor output, verifying Groq analysis quality, or investigating why calls aren't logging.
---

# Standard Call Processor — Test Reference

> **Status: Pipeline verified ✅ — 2026-04-03**
> **Test script:** `tests/call-processor-test.py` (20 scenarios)
> **Workflow ID:** `Kg576YtPM9yEacKn`
> **Webhook:** `https://n8n.syntharra.com/webhook/retell-hvac-webhook`

---

## Pipeline Architecture

```
Retell POST → Filter (call_analyzed only) → Extract Call Data → Supabase Lookup Client
  → Parse Client Data → Check Repeat Caller → Build Groq Request (Code)
  → Groq: Analyze Transcript (HTTP → api.groq.com) → Parse Lead Data (Code)
  → Is Lead? → [Lead path] SMS + Email + Supabase Log Call → HubSpot Log Note
              → [Non-lead path] Log Non-Lead + Supabase Log Call → HubSpot Log Note
```

### Key nodes
| Node | Type | Purpose |
|---|---|---|
| `Build Groq Request` | Code | Builds Groq API request body with system + user prompts |
| `Groq: Analyze Transcript` | HTTP Request | POST to `api.groq.com/openai/v1/chat/completions` |
| `Parse Lead Data` | Code | Parses Groq JSON, normalises all fields, maps to DB schema |
| `Supabase: Log Call` | HTTP Request | Writes full row to `hvac_call_log` |

---

## AI Model

- **Provider:** Groq (`api.groq.com/openai/v1/chat/completions`)
- **Model:** `llama-3.3-70b-versatile`
- **Temperature:** 0.2
- **Max tokens:** 600
- **Credential:** n8n `httpHeaderAuth` → id `UfljdfOxkfTm76LE` ("Groq API Key")
- **Retry:** 3 attempts, 2s backoff (added 2026-04-03)

> ⚠️ **DO NOT use the OpenAI credential** (`1uzBYwyR7Q7bdkZe`) — it has an expired/invalid key.
> The workflow was broken with OpenAI. All AI analysis now routes through Groq.

---

## Groq Rate Limits (FREE TIER)

- **Limit:** ~30 RPM (requests per minute) on free Groq tier
- **Symptom:** `"The service is receiving too many requests from you"` — HTTP 429
- **Recovery:** Wait ~60s after hitting limit
- **Test rule:** Never fire more than 6 scenarios in 60 seconds. Space sequential test calls by at least 10s.
- **Upgrade path:** If hitting limits in production, upgrade Groq plan or add longer retry backoff.

---

## Fields Written to `hvac_call_log`

| Field | Source | Notes |
|---|---|---|
| `call_id` | Retell webhook | Dedup key — duplicate call_ids are rejected |
| `agent_id` | Retell webhook | Foreign key to `hvac_standard_agent` |
| `company_name` | Supabase lookup | From client record |
| `call_tier` | Parse Lead Data | From `plan_type` in client record, default "Standard" |
| `caller_name` | Groq | Null if not captured |
| `caller_phone` | Groq | Falls back to `from_number` |
| `caller_address` | Groq | Null if not given in call |
| `service_requested` | Groq | Free text description |
| `job_type` | Groq → normalised | See enum below |
| `lead_score` | Groq | Integer 1-10 |
| `is_lead` | Groq + override | True if score >= 5 AND real service need |
| `urgency` | Groq | Low / Medium / High / Emergency |
| `caller_sentiment` | Groq → integer | 2=Positive, 3=Neutral, 4=Frustrated, 5=Angry |
| `vulnerable_occupant` | Groq | True if elderly/child/medical mentioned |
| `transfer_attempted` | Groq | True if live transfer was offered/initiated |
| `summary` | Groq | 1-2 sentence summary |
| `notes` | Groq | Extra details |
| `duration_seconds` | Retell webhook | Call duration |
| `geocode_status` | (reserved) | Empty string currently |

### job_type enum (normalised in Parse Lead Data)
`Repair`, `Installation`, `Maintenance`, `Emergency`, `General Enquiry`,
`Wrong Number`, `Spam`, `Vendor`, `Job Application`, `Other`

### caller_sentiment scale (integer)
`2` = Positive/Satisfied · `3` = Neutral · `4` = Frustrated · `5` = Angry/Furious

> ⚠️ `caller_sentiment` column is **INTEGER** in Supabase — do NOT write strings.
> Parse Lead Data maps Groq string labels → integers via SM map.

---

## Dedup Logic

The `Check Repeat Caller` node checks if `call_id` already exists in `hvac_call_log`.
If it does, the execution exits early — no duplicate row is created.

---

## Test Suite (`tests/call-processor-test.py`)

20 scenarios covering:

| # | Scenario | Expected |
|---|---|---|
| 1 | Standard repair lead | is_lead=True, all fields captured |
| 2 | New install quote | job_type=Installation, lead |
| 3 | Emergency elderly no heat | urgency=Emergency, vulnerable_occupant=True |
| 4 | Maintenance booking | job_type=Maintenance |
| 5 | Wrong number | is_lead=False |
| 6 | Spam robocall | is_lead=False |
| 7 | Out of service area | is_lead=False |
| 8 | Live transfer gas emergency | transfer_attempted=True |
| 9 | Caller hangs up early | partial data captured |
| 10 | High-value commercial | lead_score>=8 |
| 11 | Phonetic phone number | caller_phone decoded correctly |
| 12 | Pricing enquiry, no booking | is_lead=False |
| 13 | Short call / silence | is_lead=False |
| 14 | Frustrated caller | caller_sentiment>=4 |
| 15 | No address given | caller_name + phone only |
| 16 | Vendor/supplier call | is_lead=False |
| 17 | Job applicant | is_lead=False |
| 18 | Dedup (same call_id twice) | only 1 row in DB |
| 19 | Borderline service area | is_lead=True |
| 20 | Complex address, urgent commercial | lead_score>=7, address captured |

### Running the tests

```bash
# Run all 20 — allow 15+ minutes, rate limits apply
python3 tests/call-processor-test.py

# Run a single targeted scenario (modify TS/sid in script)
# Always wait 60s after a rate limit error before retrying
```

> ⚠️ **Rate limit rule:** Do not run more than 6 scenarios in any 60-second window.
> The test script fires scenarios sequentially — running all 20 at once will hit Groq RPM limits
> on the free tier. Add `time.sleep(10)` between each call or upgrade Groq plan.

---

## Common Failure Modes

| Symptom | Root cause | Fix |
|---|---|---|
| All calls error immediately | OpenAI credential expired | Use Groq (already fixed 2026-04-03) |
| `fetch is not defined` in Code node | n8n Code nodes don't support `fetch()` | Use `$http.request()` or split into Code + HTTP Request nodes |
| `$http is not defined` | n8n version doesn't support `$http` | Use two-node pattern: Code builds body, HTTP Request fires it |
| `JSON Body is not valid JSON` | n8n expression in `specifyBody: json` | Use `contentType: raw` + `JSON.stringify(...)` in body expression |
| IIFE `(() => {})()` in jsonBody fails | n8n expression engine doesn't support IIFE | Move logic to Code node, use simple `$json.field` refs in HTTP body |
| `caller_sentiment` insert fails (22P02) | Column is INTEGER — strings rejected | Map strings to integers in Parse Lead Data (2=Positive, 3=Neutral, 4=Frustrated, 5=Angry) |
| Rows not appearing despite exec=success | `Supabase: Log Call` body error | Check jsonBody expression for invalid syntax; always verify with direct Supabase POST test |
| `The service is receiving too many requests` | Groq RPM exceeded | Wait 60s then retry; space test calls by 10s+ |
| `caller_address` null despite address in transcript | Groq didn't extract it | Richer transcript with explicit "address?" agent prompt improves extraction |
| urgency returns "High" instead of "Emergency" | Groq judges severity conservatively | Use explicit "emergency" word in transcript; acceptable — High still triggers priority routing |

---

## n8n Credential Reference

| Credential | ID | Used by |
|---|---|---|
| Groq API Key | `UfljdfOxkfTm76LE` | Groq: Analyze Transcript |
| Supabase Anon Key | `x9C4EKUtEBCiGE08` | Supabase: Log Call (write via anon — RLS allows) |
| ~~OpenAI account~~ | ~~`1uzBYwyR7Q7bdkZe`~~ | ~~BROKEN — do not use~~ |

---

## Session History

| Date | Change |
|---|---|
| 2026-04-03 | Initial build: replaced broken OpenAI credential with Groq |
| 2026-04-03 | Fixed Supabase write: added all new fields (address, job_type, sentiment, vulnerable_occupant, transfer_attempted, call_tier) |
| 2026-04-03 | Fixed IIFE expression in jsonBody — moved logic to Parse Lead Data Code node |
| 2026-04-03 | Fixed caller_sentiment integer mapping (Angry=5, not 1) |
| 2026-04-03 | Added pricing-only lead filter in Parse Lead Data |
| 2026-04-03 | Added Groq retry (3× / 2s backoff) to Groq HTTP node |
| 2026-04-03 | Wrote 20-scenario test suite → `tests/call-processor-test.py` |
