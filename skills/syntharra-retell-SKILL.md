---
name: syntharra-retell
description: >
  Complete reference for all Retell AI work at Syntharra — agents, conversation flows,
  prompts, voices, publishing, and the API.
  ALWAYS load this skill when: creating or editing a Retell agent, updating an agent prompt,
  working on conversation flow nodes, changing a voice or LLM setting, debugging a call issue,
  publishing an agent, adding a new client agent, working with the Retell API directly,
  or any task where Retell AI is involved. This is the single source of truth for all
  Retell configuration — never rely on memory alone for agent IDs or API patterns.
---

> **Last verified: 2026-04-05** — COMPONENTS architecture deployed both tiers, Supabase 409 fix applied

# Syntharra — Retell AI Reference

---

## Credentials

- **API Key:** query `syntharra_vault` table → `service_name = 'retell'`
- **Base URL:** `https://api.retellai.com`
- **Auth header:** `Authorization: Bearer {retell_api_key}`

---

## Agent Registry

Client agents are **not listed here** — they live in Supabase.

To look up any client's agent: query `hvac_standard_agent` (Standard) or `hvac_premium_agent` (Premium), filter by `company_name` or `agent_id`.

### Demo / Test Agents
These 3 are the only agents hardcoded here because they're system-level, not client data:

| Agent | ID | Purpose |
|---|---|---|
| Arctic Breeze HVAC | `agent_4afbfdb3fcb1ba9569353af28d` | Test agent — demos + VSL recording |
| Jake | `agent_b9d169e5290c609a8734e0bb45` | Demo agent — must stay published |
| Sophie | `agent_2723c07c83f65c71afd06e1d50` | Demo agent — must stay published |

**Never reference old agent ID `d180e1bd` — deleted.**

---

## Conversation Flow

| Item | Value |
|---|---|
| Flow ID | `conversation_flow_34d169608460` |
| Node count | 12 |

### Flow Nodes (in order)
`greeting` → `identify_call` → `nonemergency_leadcapture` → `verify_emergency` → `callback` → `existing_customer` → `general_questions` → `spam_robocall` → `Transfer Call` → `transfer_failed` → `Ending` → `End Call`

---

## GOTCHAs

### Supabase 409 Conflict on hvac_call_log
When the call processor receives a duplicate `call_id`, Supabase 409 fails on the unique constraint.
This happens when Retell retries the webhook or the same call data arrives twice.

**Fix:** Add HTTP header to Supabase requests in call processor:
```
Prefer: resolution=merge-duplicates
```

This tells Supabase to resolve duplicates instead of 409 failing. Applied to Standard call processor 2026-04-05.

### COMPONENTS Architecture — Shared Instructions Across Tiers
Both Premium and Standard now reference the same 14 COMPONENTS functions. This is a SINGLE SOURCE OF TRUTH pattern.

If you update node instructions, you update ONE place — the COMPONENTS object in the build code. Both tiers automatically use the new instructions.

Functions accept parameters to adapt for tier differences:
- `primaryCaptureNode` — `fallback_leadcapture_node` (Standard) vs `booking_capture_node` (Premium)
- `bookingAvailable` — `false` (Standard) vs `true` (Premium)

---

## Critical Rules — READ BEFORE ANY RETELL WORK

1. **NEVER delete or recreate a Retell agent.** The `agent_id` is the foreign key tying together Retell, Supabase (`hvac_standard_agent`), the call processor workflow, and the phone number assignment. Deleting it breaks everything. Always patch in place.

2. **Always publish after any agent update.** Changes to an agent do not go live until published.
   ```
   POST https://api.retellai.com/publish-agent/{agent_id}
   Authorization: Bearer {retell_api_key}
   ```
   Returns 200 with empty body on success.

3. **If a new agent is ever created** (e.g. for a new client), immediately in the same operation:
   - Update `agent_id` in Supabase `hvac_standard_agent`
   - Reassign phone number in Retell
   - Update the call processor n8n workflow

4. **`is_published` is NOT a health indicator** — agents work immediately after creation regardless of publish status. The publish step is for prompt/config changes, not initial creation.

5. **Always use commas instead of dashes** in agent prompts — better AI readability and parsing.

---

## Prompt Architecture

Every Syntharra agent uses this 3-part structure:

```
[Master Base Prompt]
    +
[Company Info Block]
    +
[Call Type Nodes]
```

### Dynamic Variables
| Variable | Populated From |
|---|---|
| `{{agent_name}}` | Jotform `q10_aiAgent10` → Supabase `agent_name` |
| `{{company_name}}` | Jotform `q4_hvacCompany` → Supabase `company_name` |
| `{{COMPANY_INFO_BLOCK}}` | Built by onboarding workflow from all Supabase fields |

### Call Type Nodes
Each node handles a specific call scenario:
- Service/repair request
- Install/quote request
- Existing customer inquiry
- FAQ / general question
- Emergency
- Live transfer trigger

### Prompt Writing Rules
- Use commas, not dashes, for lists and pauses
- Keep responses short — under 30 words where possible
- Never guess at pricing — "I'll have someone call you with exact pricing"
- If unsure: "Let me have someone from the team follow up"
- Always confirm name, phone, and address before ending a service call
- Warm but efficient — no over-explaining

---

## API Patterns

### Get agent details
```python
GET https://api.retellai.com/get-agent/{agent_id}
Authorization: Bearer {retell_api_key}
```

### Update agent
```python
PATCH https://api.retellai.com/update-agent/{agent_id}
Authorization: Bearer {retell_api_key}
Content-Type: application/json

{ "prompt": "...", "voice_id": "...", ... }
```
Always follow with a publish call.

### Publish agent
```python
POST https://api.retellai.com/publish-agent/{agent_id}
Authorization: Bearer {retell_api_key}
```

### Create agent (new client onboarding)
```python
POST https://api.retellai.com/create-agent
Authorization: Bearer {retell_api_key}
Content-Type: application/json
```
After creating: immediately update Supabase, assign phone, update n8n — all in same operation.

### List agents
```python
GET https://api.retellai.com/list-agents
Authorization: Bearer {retell_api_key}
```

---

## Voice Configuration

- Voice gender set per client from Jotform `q11_aiVoice` field (`"Male"` or `"Female"`)
- Stored in Supabase `hvac_standard_agent.voice_gender`
- Applied during agent creation in onboarding workflow

---

## Webhook (Call Events)

Retell sends call events to n8n after each call:
- Event type filtered: `call_analyzed` only (completed + analyzed calls)
- Standard webhook handled by: HVAC Std Call Processor `Kg576YtPM9yEacKn`
- Premium webhook handled by: HVAC Prem Call Processor `STQ4Gt3rH8ptlvMi`

Payload includes: `transcript`, `agent_id`, `duration`, `call_id`

---

## Demo Call

To record a demo call (VSL Scene 3):
- Call: `+1 (812) 994-4371` (Arctic Breeze agent)
- Use persona: **"Mike Henderson"**

---

---


## 🔧 Conversation Flow API — Verified Patterns (2026-04-04)

### Cloning a flow
When creating a new conversation flow from an existing one:
- GET the source flow
- POST to `create-conversation-flow` with: `start_speaker`, `nodes`, `global_prompt`, `tools`, `model_choice`, `tool_call_strict_mode`, `knowledge_base_ids`
- `start_speaker` is REQUIRED but NOT obvious from GET response — always include it (usually `"agent"`)
- `edges` field in GET is always 0 — edges are embedded inside node objects
- Remove read-only fields: `conversation_flow_id`, `version`, `is_published`, `kb_config`, `begin_tag_display_position`

### Code nodes CAN be created via API
- Type: `code`
- Required fields: `id`, `type`, `name`, `code`, `edges`, `else_edge`, `speak_during_execution`, `wait_for_result`, `display_position`
- CRITICAL: `else_edge` MUST be an object (not null). Use: `{"destination_node_id": "node-ending", "id": "edge-xxx-else", "transition_condition": {"type": "prompt", "prompt": "Else"}}`
- `edges` is an array of conditional edges (can be empty `[]`)

### Extract Dynamic Variable nodes are UI-ONLY
- Cannot be created via API — returns validation error
- Dan must create these in the Retell dashboard manually
- Place between lead capture node and ending/code nodes

### Node types supported by API
- `conversation` — standard conversation nodes (require `instruction`)
- `code` — JavaScript execution nodes
- `end` — end call nodes
- `transfer_call` — call transfer nodes (require `transfer_destination`)
- `extract_variable` — NOT supported via API (UI-only)

### Phone number configuration
- `fallback_number` field works via PATCH update-phone-number
- `fallback_destination` also accepted but `fallback_number` is what persists
- Geo restrictions (`allowed_inbound_country_list`) — dashboard only
- `inbound_agent_version` auto-updates when agent is patched

### List agents returns versions, not unique agents
- `GET /list-agents` returns every published version as a separate entry
- 5 unique agents may return 90+ entries
- Filter by unique `agent_id` to get actual agent count

## 🔑 Syntharra Vault — Credential Access

ALL Syntharra API keys and secrets are stored in the Supabase table `syntharra_vault`.

- **Project URL:** `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- **Table:** `syntharra_vault`
- **Query by:** `service_name` + `key_type` fields → retrieve `key_value`
- **Auth:** Supabase service role key — stored in vault as `service_name = 'Supabase'`, `key_type = 'service_role_key'`
- **NEVER** store keys in skill files, session logs, GitHub, or project memory

### REST Lookup Pattern
```
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&key_type=eq.{KEY_TYPE}&select=key_value
Headers:
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
```

### JavaScript Lookup Pattern (n8n / Node.js)
```javascript
async function getVaultKey(serviceName, keyType) {
  const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.${serviceName}&key_type=eq.${keyType}&select=key_value`,
    { headers: { apikey: SERVICE_ROLE_KEY, Authorization: `Bearer ${SERVICE_ROLE_KEY}` } }
  );
  const data = await res.json();
  return data[0]?.key_value;
}

// Examples:
const retellKey    = await getVaultKey('Retell AI', 'api_key');
const n8nUrl       = await getVaultKey('n8n Railway', 'instance_url');
const stripeMonthly = await getVaultKey('Stripe', 'price_standard_monthly');
```

### Known service_name / key_type Values

| service_name | key_type | What it is |
|---|---|---|
| `n8n Railway` | `instance_url` | `https://n8n.syntharra.com` |
| `n8n Railway` | `api_key` | n8n Railway API key |
| `Retell AI` | `api_key` | Retell API key |
| `Retell AI` | `agent_id_arctic_breeze` | Test HVAC agent ID |
| `Retell AI` | `agent_id_demo_jake` | Demo agent Jake |
| `Retell AI` | `agent_id_demo_sophie` | Demo agent Sophie |
| `Retell AI` | `conversation_flow_id` | Live conversation flow |
| `Retell AI` | `phone_number` | Arctic Breeze phone |
| `Supabase` | `project_url` | Supabase project URL |
| `Supabase` | `service_role_key` | Full admin key |
| `GitHub` | `personal_access_token` | GitHub PAT |
| `Stripe` | `product_id_standard` | Standard product ID |
| `Stripe` | `product_id_premium` | Premium product ID |
| `Stripe` | `price_standard_monthly` | $497/mo price ID |
| `Stripe` | `price_standard_annual` | $414/mo price ID |
| `Stripe` | `price_standard_setup` | $1,499 setup price ID |
| `Stripe` | `price_premium_monthly` | $997/mo price ID |
| `Stripe` | `price_premium_annual` | $831/mo price ID |
| `Stripe` | `price_premium_setup` | $2,499 setup price ID |
| `Stripe` | `coupon_founding_standard` | FOUNDING-STANDARD coupon |
| `Stripe` | `coupon_founding_premium` | FOUNDING-PREMIUM coupon |
| `Stripe` | `webhook_url` | Stripe webhook URL |
| `Stripe` | `webhook_id` | Stripe webhook ID |
| `Jotform` | `api_key` | Jotform API key |
| `Jotform` | `form_id_standard` | Standard onboarding form ID |
| `Jotform` | `form_id_premium` | Premium onboarding form ID |
| `Jotform` | `webhook_standard_new` | Railway n8n webhook URL |
| `SMTP2GO` | `api_key` | SMTP2GO API key |
| `Railway` | `api_token` | Railway API token |
| `Railway` | `project_id` | Syntharra project ID |
| `Railway` | `service_id_n8n` | n8n service ID |
| `Railway` | `service_id_checkout` | Checkout service ID |
| `Railway` | `service_id_ops_monitor` | Ops monitor service ID |

---

## 🔄 Auto-Update Rule

Only update this skill when something **fundamental** changes — not during routine work:
- ✅ New agent created for a client → add to agents table
- ✅ Agent ID changes for any reason → update immediately
- ✅ Conversation flow rebuilt or nodes added/removed → update flow section
- ✅ New prompt architecture pattern established → update prompt section
- ✅ Retell API endpoint or auth method changes → update API section
- ❌ Do NOT update for routine prompt edits, debugging sessions, or temporary changes

## CRM — HubSpot (active since 2026-04-03)
> HubSpot replaced the admin dashboard as Syntharra's CRM layer.
> Load `skills/syntharra-hubspot-SKILL.md` for full API reference.

- **All client records, deals, and sales pipeline live in HubSpot**
- **All marketing leads flow into HubSpot** (website form → Lead stage)
- **All paying clients auto-create in HubSpot** (Stripe → Paid Client stage)
- **All onboarded clients auto-update in HubSpot** (Jotform → Active stage)
- **All call activity is logged in HubSpot** (Retell post-call → contact note)
- Supabase remains operational source of truth for Retell agent config + call logs
- HubSpot is the sales, marketing, and client relationship layer
- API key: `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- Pipeline: "Syntharra Sales" — Lead → Demo Booked → Paid Client → Active

> After every call, the Retell post-call webhook triggers the Call Processor workflow which logs a structured call note (caller name, service, lead score, sentiment, summary) to the client's HubSpot contact record.


---

## Prompt Engineering Lessons (from simulator runs)

### Global prompt length warning
- >30k chars: model begins ignoring instructions appended at the END of global prompt
- >35k chars: personality/edge-case instructions at end are effectively invisible
- Rule: put behavioural instructions in NODE text, not global prompt, for reliability

### Scripted close phrases
- Soft close ("someone will be in touch") → evaluators and real callers may not register as "scheduled callback"
- Use explicit scripted language with ⚠️ CRITICAL: do not paraphrase warnings
- Example: "Perfect — I've scheduled a callback for you. Someone from our team will be in touch with you shortly."

### Emergency routing — 2-step sequence
- Step 1: "Is your system completely not working?" (urgency assessment)
- Step 2: "Any burning smell, gas, smoke, water leak?" (safety check)
- Transfer offer only for EXTREME urgency (freezing, elderly occupants, dangerous cold)
- Matter-of-fact outage (furnace won't turn on, cold but not dangerous) → high-priority lead capture

### Out-of-area mid-collection
- When out-of-area fires after name+number already collected: do NOT re-ask
- Instruction must say "collect only REMAINING details"

### Personality handling placement
- Must be in NODE instruction text, NOT global prompt
- Place in nonemergency_leadcapture_node for maximum effect during info collection

## Code Node (Retell) — Verified Patterns

### Creating via API
- Type string `"code"` IS accepted by the API (confirmed 2026-04-03)
- Required fields:
  ```json
  {
    "id": "node-xxx",
    "name": "node_name",
    "type": "code",
    "code": "// JS here",
    "speak_during_execution": false,
    "wait_for_result": true,
    "else_edge": {
      "id": "edge-xxx",
      "destination_node_id": "target-node-id",
      "transition_condition": { "type": "prompt", "prompt": "Else" }
    },
    "edges": [],
    "display_position": { "x": 0, "y": 0 }
  }
  ```
- `else_edge.transition_condition.prompt` MUST equal exactly `"Else"` — any other string rejected

### Available globals inside code node JS
- `metadata.transcript` — array of `{role: 'user'|'agent', content: string}` — conversation history
- `dv.<name>` — read dynamic variables set elsewhere in flow
- `fetch(url)` — make HTTP requests
- `console.log()` — shows in Run results
- DO NOT use `conversationHistory` (undefined), `call.transcript` (undefined)

### Setting output variables
```js
// Assign directly to variable name, then return it
caller_style_note = note;
return { caller_style_note: note };
```

### Caller style detector pattern
- Run code node BETWEEN identify_call_node and leadcapture
- Reads `metadata.transcript`, detects caller style signals
- Sets `caller_style_note` variable
- Leadcapture reads `{{caller_style_note}}` at top of instruction
- This replaces a large personality table in the prompt — saves ~800 tokens per call

---


## Edge Rewiring Gotcha (discovered 2026-04-04)

### Problem
`PATCH update-conversation-flow` returns 400: "Please remove or update finetune examples before deleting the associated node or edge" when you change the `destination_node_id` of an existing edge — even when `get-conversation-flow` shows `finetune_examples: []`.

### Root cause
Retell stores finetune examples in its backend and does NOT expose them in the API response. The example count returned is unreliable. Any change to `destination_node_id` is treated as "deleting" the old edge.

### Fix
Do NOT change `destination_node_id` on existing edges. Instead:
1. Add a NEW edge with the same `transition_condition.prompt` text
2. Insert the new edge FIRST in the `edges` array (Retell uses first-match routing)
3. Leave the original edge in place — it acts as a fallback and won't trigger if the new edge fires first

```python
new_edge = {
    "id": "edge-to-NEW-destination",
    "destination_node_id": "node-new-target",
    "transition_condition": {
        "type": "prompt",
        "prompt": original_edge['transition_condition']['prompt']  # same condition
    }
}
node['edges'].insert(0, new_edge)  # insert FIRST for routing priority
```

### Note
Adding entirely NEW edges (without changing existing ones) works fine. Adding new nodes also works fine. Only changing `destination_node_id` of existing edges is blocked.

## Architecture Decisions

| Decision | Chose | Why | Revisit if |
|---|---|---|---|
| Agent lifecycle | PATCH in place, never delete/recreate | Deleting breaks phone binding, Supabase FK, call processor routing, and all call history — Retell has no versioning | Retell adds versioning/backup |
| One agent per client | Clone from template per client | Phone numbers bind 1:1 to agents; isolation prevents one client's changes affecting others | Retell adds multi-tenant features |
| Caller style handling | Code node detector → inject short note | 15k char global prompt = personality instructions ignored (below attention window); code node detects style, injects 30-50 char note at TOP of active node; 76% prompt reduction | Retell improves LLM context handling |
| Code node creation | UI-create then API-patch | Code node type not in REST API validator whitelist as of 2026-04-03 — UI only | Retell updates API whitelist |
| Prompt style | Commas not dashes | Better AI readability in voice context | — |
| Publish after every update | Always call publish-agent after any patch | Retell agents are draft until published — unpublished changes have no effect on live calls | — |

## Info Collection — Verified Patterns (added 2026-04-03)

### Commercial callers
- Facilities managers / commercial property callers need business name captured
- Add to phone collection step: "And what's the business or company name?" for commercial inquiries
- Pattern: detect commercial context (building, facility, office park, etc.) → ask for company name

### WhatsApp-only callers
- Some callers have no phone/email but have WhatsApp
- DO NOT reject — accept WhatsApp number as valid contact method
- Note it explicitly: "Got it, I'll note that as a WhatsApp number."
- Pattern in leadcapture: under phone collection, add WhatsApp acceptance clause

### Fast phonetic phone delivery
- Caller gives number as words ("fivefivefive...") all in one breath
- Agent should: either ask to repeat slowly OR decode and confirm back digit by digit
- If agent decodes correctly and confirms digits → PASS (both paths are valid)
- If caller refuses to repeat slowly → offer "Would it be okay to use the number you're calling from?"
- Never record a placeholder like "[your number]" — always confirm actual digits

### Placeholder digits bug
- Agent was saying "callback number [your number]" in confirmation readback
- Root cause: agent accepted caller's refusal to repeat and moved on without a real number
- Fix: persist with digit confirmation OR offer caller-ID fallback before moving on

---

## Premium Agent Prompt — Verified Fixes (2026-04-04)

### Booking push behaviour
- Do NOT use language like "this is your PRIMARY function — always attempt to book before offering a callback"
- This causes agent to push booking on FAQ callers, callback-only callers, and non-bookable enquiries
- Correct: "offer to book if the caller is open to it — never push on callers who just want a callback or FAQ answer"

### Booking step order
- Agent must ask "what service do you need?" BEFORE confirming details back
- Correct flow: (1) identify service → (2) collect contact details → (3) ask once if they want to book or callback → (4) read back ALL details including service type

### CRITICAL RULES that must exist in premium global prompt
Add these if missing — each fixes a simulator failure:
- NEVER repeat information already stated in this call. Each fact is said once only
- NEVER push for booking or extra details if caller says they will call back or are not ready. Accept gracefully and end call
- For callback-only callers: name and phone number is sufficient. Do NOT ask for address or service type unless they offer it
- For simple FAQ calls (hours, services, area): answer the question, offer further help once. Do NOT collect lead info unless caller has booking intent

### em-dash encoding in Retell prompts
Retell stores em-dashes as a 3-char garbled sequence: `\xe2\u20ac\u201d`
When doing str.replace() on Retell prompt content in Python, use this exact sequence — not `—` or `\u2014`
Always fetch the prompt fresh and inspect with repr() before attempting replacements.



---

## API Endpoint Patterns — VERIFIED 2026-04-04

⚠️ Retell API has INCONSISTENT URL patterns:

| Operation | Endpoint | /v2/ prefix? |
|---|---|---|
| GET agent | `GET /get-agent/{agent_id}` | NO |
| PATCH agent | `PATCH /update-agent/{agent_id}` | NO |
| Publish agent | `POST /publish-agent/{agent_id}` | NO |
| Create agent | `POST /create-agent` | NO |
| List calls | `POST /v2/list-calls` | YES |
| Get call | `GET /v2/get-call/{call_id}` | YES |
| GET phone number | `GET /get-phone-number/{number}` | NO |
| PATCH phone number | `PATCH /update-phone-number/{number}` | NO |

---

## Agent Configuration Fields — VERIFIED WORKING VIA API

All of these were tested live with PATCH + GET + revert on 2026-04-04:

```
guardrail_config: {
  output_topics: ["harassment", "self_harm", "sexual_exploitation", "violence",
                   "child_safety_and_exploitation", "illicit_and_harmful_activity",
                   "regulated_professional_advice"],
  input_topics: ["platform_integrity_jailbreaking"]
}

boosted_keywords: ["HVAC", "compressor", "Trane", "Lennox", ...]
pronunciation_dictionary: [{ word: "HVAC", alphabet: "ipa", phoneme: "eɪtʃ viː eɪ siː" }]
enable_backchannel: true
backchannel_frequency: 0.8
backchannel_words: ["yeah", "uh-huh", "got it", "okay", "right"]
reminder_trigger_ms: 15000
reminder_max_count: 2
normalize_for_speech: true
responsiveness: 0.85
voice_speed: 1.05
end_call_after_silence_ms: 30000
max_call_duration_ms: 600000
```

Phone number fields (also verified):
```
fallback_number: "+1XXXXXXXXXX" (E.164, external only)
allowed_inbound_country_list: ["US"]
allowed_outbound_country_list: ["US"]
```

---

## Guardrails — Key Notes

- guardrail_config field does NOT appear in GET response until it has been SET
- Once set, it persists and appears in all subsequent GET calls
- Adds ~50ms latency per call
- gambling and defense_and_national_security: omit for HVAC (irrelevant)
- regulated_professional_advice: ENABLE (agent must not give pricing/legal advice)
- platform_integrity_jailbreaking: ENABLE (real-time prompt injection detection)
- If API PATCH doesn't work, Dan can enable in dashboard: Agent > Security & Fallback

---

## Webhook Payload Structure — VERIFIED FROM REAL CALL

The call_analyzed webhook wraps everything under `call`:
```json
{
  "event": "call_analyzed",
  "call": {
    "call_id": "...",
    "agent_id": "...",
    "from_number": "+1...",        // only on phone_call type
    "to_number": "+1...",          // only on phone_call type
    "direction": "inbound",        // only on phone_call type
    "duration_ms": 95000,
    "disconnection_reason": "user_hangup",
    "recording_url": "https://...",
    "public_log_url": "https://...",
    "transcript": "...",
    "call_analysis": {
      "in_voicemail": false,
      "call_summary": "...",           // system preset — root level
      "user_sentiment": "Neutral",     // system preset — root level (capitalised)
      "call_successful": true,         // system preset — root level
      "custom_analysis_data": {
        "caller_name": "...",          // our custom fields — NESTED
        "lead_score": 8,
        "is_hot_lead": true,
        ...
      }
    },
    "latency": { "e2e": { "p50": 1098 }, "llm": { "p50": 646 } },
    "call_cost": { "total_duration_unit_price": 0.20 }
  }
}
```

CRITICAL: System presets at call_analysis root. Custom fields NESTED in custom_analysis_data.

---

## Sentiment Field Mapping

- Retell sends: `call_analysis.user_sentiment` (text, e.g. "Neutral", "Positive")
- Map to: `retell_sentiment` column (TEXT) in hvac_call_log
- DO NOT map to: `caller_sentiment` column (INTEGER) — this is legacy/deprecated
- The client dashboard reads `retell_sentiment`

---

## Premium DEMO Clone Pattern

When making significant changes to Premium, don't modify Premium TESTING directly:
1. Clone Premium TESTING via `POST /create-agent` with its full config
2. Clone its conversation flow via `POST /create-conversation-flow`
3. Work on the DEMO clone
4. After verification, apply DEMO config back to Premium TESTING → MASTER

---

## Conversation Flow Node Types (complete list)

| Node Type | Can Create via API? | Purpose |
|---|---|---|
| Conversation | No (UI only, patchable after) | Main dialogue node |
| Extract Dynamic Variable | No (UI only) | Extract caller info mid-call |
| Code | No (UI only) | Run JavaScript mid-flow |
| SMS | No (UI only) | Send SMS (Retell Twilio only — we use Telnyx instead) |
| Function | No (UI only) | Call external APIs/webhooks |
| Logic Split | No (UI only) | Instant branching on conditions |
| Call Transfer | No (UI only) | Transfer to phone number |
| Agent Transfer | No (UI only) | Transfer to another AI agent (near-instant) |
| Press Digit (DTMF) | No (UI only) | Touchtone input |
| MCP | No (UI only) | Call MCP server tools |
| End | No (UI only) | Terminate call |
| Global Node | No (UI only) | Universal handler from any point in flow |
| Component | No (UI only) | Reusable sub-flow shareable across agents |

⚠️ Existing call_style_detector code nodes in both flows must NOT be removed.

---

## Retell Dashboard-Only Features (not in API)

- Alerting rules (10 max) — email + webhook notifications
- Analytics charts — custom post_call_analysis fields supported
- Guardrails toggle (backup if API doesn't work)
- Session history — stored indefinitely, searchable, filterable
- Finetune examples — per-node transcript examples for response + transition
- Flex Mode — compiles flow into single prompt (higher cost, more natural)
- Version comparison — diff between agent versions

---

## Code Node Configuration — CRITICAL PATTERNS

**Code nodes (type: "code") in Retell need else_edge configured even if they have no explicit incoming edges.**

Without else_edge, a code node becomes a dead end — execution reaches the node but has nowhere to go afterward.

Example: `validate_phone` code node validates caller input and has no incoming edges (it's triggered automatically by transcript observation), but MUST have:
```json
{
  "type": "code",
  "else_edge": {
    "destination_node_id": "ending_node_id",
    "transition_condition": {
      "prompt": "Else"
    }
  }
}
```

Without this, the code node runs but call disconnects because there's no exit path.

**Transfer nodes (type: "transfer_call") use singular `edge` property (not `edges` array).**

This is different from Conversation nodes which use `transitions` (array).

```json
{
  "type": "transfer_call",
  "edge": {
    "destination_node_id": "transfer_failed_node_id",
    "transition_condition": {
      "prompt": "transfer_failed"
    }
  }
}
```

**validate_phone code node:** Runs automatically via transcript observation. Doesn't need incoming edges but MUST have else_edge pointing to Ending node.

**call_style_detector code node:** Should have incoming edge from identify_call node + else_edge to primary capture node.
If identify_call → call_style_detector → leadcapture, both edges must exist.

---


## Library Component Node Type Constraints (verified 2026-04-05)

**ALLOWED inside Library Components:** conversation, subagent (nested refs), extract_dynamic_variables, end
**NOT ALLOWED:** code, tool_call, transfer_call

Code nodes (call_style_detector, validate_phone) MUST stay as single-node Library Components.
They CAN be referenced as nested subagent nodes inside multi-node components.

**Subagent node does NOT support start_node_id.** You cannot route to a specific internal node of a multi-node component. Entry point is always node at index 0.

**Code components as subagent:** When referencing a code-type Library Component, the subagent node carries: code, else_edge, speak_during_execution, wait_for_result fields.

**else_edge prompt MUST be exactly "Else"** — any other value causes Retell API 400.

---

## Retell API Patterns (verified 2026-04-05)

### Endpoint Format
- GET: `https://api.retellai.com/get-agent/{agent_id}`, `get-conversation-flow/{flow_id}`
- PATCH: `https://api.retellai.com/update-agent/{agent_id}`, `update-conversation-flow/{flow_id}`, `update-conversation-flow-component/{comp_id}`
- POST: `https://api.retellai.com/create-conversation-flow-component`
- DELETE: `https://api.retellai.com/delete-conversation-flow-component/{comp_id}`
- LIST: `https://api.retellai.com/list-agents`, `list-conversation-flow-components`

### Component API
- Components are global — shared across all flows
- Create: POST /create-conversation-flow-component with {name, nodes[], start_node_id}
- Each component needs at least: one start node + one end node
- Nodes inside a component use normal types: conversation, code, end
- To use a component in a flow: set node type to "subagent" and add "conversation_flow_component_id"

### Transfer Numbers
- Must be valid E.164 format — +1XXXXXXXXXX
- 555- numbers are NOT valid and will be rejected
- For TESTING agents, use +18563630633 (Syntharra test transfer line)

### Tool Calls
- All Premium booking tools POST to: https://n8n.syntharra.com/webhook/retell-integration-dispatch
- Action routing via "action" const field in params
- Always include error handling guidance in the component that uses the tool

## Standard MASTER Architecture (2026-04-06)
- MASTER and TESTING are now **identical architecture** — both modular subagent/component
- 20 nodes, 5086-char global_prompt
- MASTER was promoted from TESTING on 2026-04-06 (flow version 22)
- MASTER previously had monolithic inline `conversation` nodes — that architecture is retired

## Promotion Script
- Path: `tools/promote-agent.py`
- Copies TESTING flow (nodes + edges + global_prompt) to MASTER flow via PATCH
- `STUB_THRESHOLD = 200`: any subagent node with empty component_id and instruction < 200 chars gets restored from MASTER's original content
- Dry-run: `python promote.py --agent standard --dry-run`
- Live: `python promote.py --agent standard`
- Safety nodes restored in last promotion: emergency_fallback_node (50→897ch), spanish_routing_node (50→592ch)

## Spanish Routing Node
- `spanish_routing_node` is scheduled for removal from the flow
- Do NOT treat as safety-critical — failures on Spanish routing scenarios are not blocking
- promote.py handles removal automatically: if node absent from TESTING, it won't be promoted to MASTER
