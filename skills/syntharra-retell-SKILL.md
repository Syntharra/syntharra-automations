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

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

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
