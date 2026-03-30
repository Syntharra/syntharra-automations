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

## 🔄 Auto-Update Rule

Only update this skill when something **fundamental** changes — not during routine work:
- ✅ New agent created for a client → add to agents table
- ✅ Agent ID changes for any reason → update immediately
- ✅ Conversation flow rebuilt or nodes added/removed → update flow section
- ✅ New prompt architecture pattern established → update prompt section
- ✅ Retell API endpoint or auth method changes → update API section
- ❌ Do NOT update for routine prompt edits, debugging sessions, or temporary changes
