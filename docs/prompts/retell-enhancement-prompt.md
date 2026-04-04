# Syntharra — Retell Enhancement Sprint
## Claude Code / Cowork Implementation Prompt

> **STATUS: LOCKED — Do not begin until:**
> 1. Premium TESTING agent passes 95%+ across all simulator groups
> 2. Premium TESTING has been promoted to MASTER
> 3. Dan has given explicit go-ahead
>
> **WHY:** Any changes to conversation flows will invalidate the current E2E test suite.
> Premium must be fully signed off before touching either agent.

---

## CONTEXT — What This Sprint Does

This prompt implements a set of improvements to both the Standard and Premium HVAC agent
flows and their downstream n8n call processors. These changes were designed to:

1. Use Retell's native capabilities instead of post-call GPT processing
2. Improve lead data capture reliability via Extract Dynamic Variable nodes
3. Add phone number format validation via Code node
4. Simplify n8n call processors by removing GPT extraction and mapping Retell's
   post_call_analysis_data fields directly to Supabase
5. Add SMS node to Premium flow for in-call confirmations (NOT booking links —
   confirmation messages only, e.g. "I've noted your details, someone will call you back")

**What this sprint does NOT do:**
- Touch any MASTER agents before backup copies exist
- Add booking links to Standard (Standard is lead capture only — no booking)
- Implement mid-call calendar booking in this sprint (future Premium feature)
- Change the Premium calendar OAuth integration (Dispatcher workflows untouched)

---

## PHASE 0 — PRE-FLIGHT CHECKS (mandatory, run first)

Before touching anything, verify the system state:

```python
import requests, base64, json

TOKEN = os.environ.get("GITHUB_TOKEN")
H = {"Authorization": f"token {TOKEN}"}
RETELL_KEY = # fetch from syntharra_vault → service_name='Retell AI', key_type='api_key'
RETELL_H = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}

# 1. Confirm MASTER agent IDs (fetch live, never use memory)
STANDARD_MASTER  = "agent_4afbfdb3fcb1ba9569353af28d"
PREMIUM_MASTER   = "agent_9822f440f5c3a13bc4d283ea90"
STD_FLOW_MASTER  = "conversation_flow_34d169608460"
PREM_FLOW_MASTER = "conversation_flow_1dd3458b13a7"

# 2. Verify both MASTER agents are published and healthy
for agent_id in [STANDARD_MASTER, PREMIUM_MASTER]:
    r = requests.get(f"https://api.retellai.com/get-agent/{agent_id}", headers=RETELL_H)
    assert r.status_code == 200, f"Cannot reach agent {agent_id}"
    data = r.json()
    print(f"{agent_id}: is_published={data.get('is_published')}")

# 3. Confirm existing TESTING agents are intact (these are our current dev agents)
STD_TESTING_EXISTING  = "agent_731f6f4d59b749a0aa11c26929"
PREM_TESTING_EXISTING = "agent_2cffe3d86d7e1990d08bea068f"

# 4. Read FAILURES.md and check for any Retell-area failures before proceeding
```

**STOP if any MASTER agent returns non-200. Report to Dan before continuing.**

---

## PHASE 1 — CREATE BACKUP / NEW TESTING AGENTS

> We already have TESTING agents (agent_731f... and agent_2cffe...) which were used
> for Premium testing. After Premium promotion, these become available for this sprint.
> However — we need a CLEAN COPY of each verified MASTER to use as our new baseline.
> These copies are what we'll modify. The existing MASTER agents are never touched.

### 1A — Clone Standard MASTER → "HVAC Standard (ENHANCEMENT TESTING)"

```python
# Fetch current Standard MASTER full config
r = requests.get(f"https://api.retellai.com/get-agent/{STANDARD_MASTER}", headers=RETELL_H)
master_config = r.json()

# Fetch current Standard MASTER flow
r2 = requests.get(f"https://api.retellai.com/get-conversation-flow/{STD_FLOW_MASTER}", headers=RETELL_H)
master_flow = r2.json()

# PATCH the existing Standard TESTING agent to be a clean copy of MASTER
# (NEVER delete/recreate — patch in place)
# Copy over: prompt, voice_id, all settings — make it identical to MASTER
patch_payload = {
    "agent_name": "HVAC Standard (ENHANCEMENT TESTING)",
    "voice_id": master_config["voice_id"],
    # ... all other fields from master_config except agent_id
}
requests.patch(f"https://api.retellai.com/update-agent/{STD_TESTING_EXISTING}", 
               headers=RETELL_H, json=patch_payload)

# Publish it
requests.post(f"https://api.retellai.com/publish-agent/{STD_TESTING_EXISTING}", headers=RETELL_H)

print("Standard ENHANCEMENT TESTING agent ready — clean copy of MASTER")
```

### 1B — Clone Premium MASTER → "HVAC Premium (ENHANCEMENT TESTING)"

Same pattern as 1A but for:
- Agent: `agent_2cffe3d86d7e1990d08bea068f`  
- Source: `agent_9822f440f5c3a13bc4d283ea90` (Premium MASTER)
- Flow source: `conversation_flow_1dd3458b13a7`
- New name: `"HVAC Premium (ENHANCEMENT TESTING)"`

### 1C — Verify and document

After both patches:
- Confirm both TESTING agents return 200 from GET
- Confirm both are published
- Log the agent IDs and new names to `docs/context/AGENTS.md`
- **The MASTER agents are now untouched and serve as permanent fallback**

---

## PHASE 2 — CONFIGURE post_call_analysis_data ON TESTING AGENTS

> This replaces the GPT extraction done in n8n call processors.
> Retell runs this automatically after every call using gpt-4.1-mini (included in plan cost).
> Results are delivered in the webhook payload — no extra API call needed.

### Fields to configure (matches hvac_call_log columns)

Apply this to BOTH TESTING agents via PATCH /update-agent:

```python
post_call_analysis_data = [
    {
        "type": "string",
        "name": "caller_name",
        "description": "Full name of the caller as stated during the call.",
        "examples": ["John Smith", "Maria Garcia"],
        "required": False
    },
    {
        "type": "string", 
        "name": "caller_phone",
        "description": "Phone number the caller provided for callback. May differ from caller ID.",
        "examples": ["+15551234567", "555-867-5309"],
        "required": False
    },
    {
        "type": "string",
        "name": "caller_address",
        "description": "Full service address provided by caller including street, city, state.",
        "examples": ["123 Main St, Austin TX", "456 Oak Ave, Nashville Tennessee"],
        "required": False
    },
    {
        "type": "string",
        "name": "service_requested",
        "description": "The specific HVAC service or problem the caller described.",
        "examples": ["AC not cooling", "furnace won't start", "annual maintenance tune-up", "new system install quote"],
        "required": False
    },
    {
        "type": "enum",
        "name": "job_type",
        "description": "Category of the job based on what the caller described.",
        "choices": ["repair", "install", "maintenance", "quote", "emergency", "existing_customer", "general_inquiry", "other"],
        "required": False
    },
    {
        "type": "enum",
        "name": "urgency",
        "description": "How urgently the caller needs service based on their language and situation.",
        "choices": ["emergency", "urgent", "routine", "flexible"],
        "required": False
    },
    {
        "type": "boolean",
        "name": "is_lead",
        "description": "True if the caller is a potential new customer requesting service. False for existing customers, spam, wrong numbers, or general enquiries with no service need.",
        "required": False
    },
    {
        "type": "number",
        "name": "lead_score",
        "description": "Score from 1-10 reflecting lead quality. 9-10: emergency or urgent repair. 7-8: routine repair or install quote. 5-6: maintenance or flexible job. 3-4: general question, low intent. 1-2: spam, wrong number, or no service need.",
        "required": False
    },
    {
        "type": "enum",
        "name": "caller_sentiment",
        "description": "Overall emotional tone of the caller during the call.",
        "choices": ["positive", "neutral", "frustrated", "distressed", "angry"],
        "required": False
    },
    {
        "type": "boolean",
        "name": "transfer_attempted",
        "description": "True if the agent attempted to transfer the call to a human.",
        "required": False
    },
    {
        "type": "boolean",
        "name": "transfer_success",
        "description": "True if the transfer was successfully connected. False if transfer failed or was not attempted.",
        "required": False
    },
    {
        "type": "boolean",
        "name": "vulnerable_occupant",
        "description": "True if the caller mentioned elderly, young children, medical equipment, or any vulnerable person affected by the HVAC issue.",
        "required": False
    },
    {
        "type": "string",
        "name": "summary",
        "description": "2-3 sentence summary of the call outcome for the client's internal records. Include: what the caller needed, what information was captured, and what the next step is.",
        "examples": ["Caller John Smith requested AC repair at 123 Main St Austin TX. Unit not cooling, issue started yesterday. Lead captured, callback details collected."],
        "required": False
    },
    {
        "type": "string",
        "name": "notes",
        "description": "Any additional relevant details not captured in other fields — equipment brand/model mentioned, access instructions, preferred callback time, etc.",
        "required": False
    }
]

# Set the analysis model (gpt-4.1-mini is included in Retell plan — no extra cost)
patch_payload = {
    "post_call_analysis_data": post_call_analysis_data,
    "post_call_analysis_model": "gpt-4.1-mini"
}

for agent_id in [STD_TESTING_EXISTING, PREM_TESTING_EXISTING]:
    r = requests.patch(f"https://api.retellai.com/update-agent/{agent_id}",
                       headers=RETELL_H, json=patch_payload)
    print(f"{agent_id}: {r.status_code}")
    requests.post(f"https://api.retellai.com/publish-agent/{agent_id}", headers=RETELL_H)
```

---

## PHASE 3 — ADD EXTRACT DYNAMIC VARIABLE NODE TO FLOWS

> This adds a dedicated variable extraction node after lead capture in both flows.
> It makes lead data capture deterministic rather than relying solely on the LLM's
> conversational extraction.
>
> IMPORTANT: Code nodes and Extract Dynamic Variable nodes can only be CREATED
> via the Retell UI — the API cannot create new node types (confirmed 2026-04-03).
> They CAN be patched/updated via API once created.
>
> Therefore: Dan must create these nodes in the UI on the TESTING flows.
> Claude Code can then verify they exist and patch their config.

### Instructions for Dan (UI steps — ~5 minutes each flow)

**Standard TESTING flow** (`conversation_flow_5b98b76c8ff4`):
1. Open the flow in Retell dashboard
2. Add an "Extract Dynamic Variable" node
3. Name it: `extract_lead_data`
4. Place it between `nonemergency_leadcapture` and `Ending`
5. Configure it to extract: caller_name, caller_phone, caller_address, service_requested
6. Connect: nonemergency_leadcapture → extract_lead_data → Ending

**Premium TESTING flow** (`conversation_flow_2ded0ed4f808`):
Same pattern — place after the final lead capture node, before the confirmation/ending node.

### After Dan confirms UI nodes are created — Claude Code verifies:

```python
# Fetch the flow and confirm the node exists
r = requests.get(f"https://api.retellai.com/get-conversation-flow/{STD_TESTING_FLOW}", 
                 headers=RETELL_H)
flow_data = r.json()
nodes = flow_data.get("nodes", [])
extract_node = next((n for n in nodes if "extract" in n.get("name","").lower()), None)
assert extract_node is not None, "Extract node not found — Dan needs to create it in UI first"
print(f"Extract node confirmed: {extract_node['name']}")
```

---

## PHASE 4 — ADD CODE NODE (PHONE VALIDATION)

> Validates phone number format after extraction — catches cases where caller
> gives a partial number or the agent mishears. Flags bad data before it hits Supabase.
>
> Same constraint as Phase 3: node must be CREATED in UI, then configured via API.

### Instructions for Dan (UI steps)

Add a "Code" node to both TESTING flows:
- Name: `validate_phone`
- Place it after `extract_lead_data`
- JavaScript code to configure (paste into the code editor):

```javascript
// Phone validation code node
const raw = dv.caller_phone || "";
const digits = raw.replace(/\D/g, "");

let phone_valid = false;
let phone_normalized = raw;
let phone_flag = "";

if (digits.length === 10) {
    phone_normalized = `+1${digits}`;
    phone_valid = true;
} else if (digits.length === 11 && digits.startsWith("1")) {
    phone_normalized = `+${digits}`;
    phone_valid = true;
} else if (digits.length < 7) {
    phone_flag = "incomplete_number";
    phone_valid = false;
} else {
    phone_flag = "unusual_format";
    phone_valid = true; // store it anyway, flag for review
}

return {
    phone_normalized,
    phone_valid,
    phone_flag
};
```

- Store response variables:
  - `phone_normalized` → path: `phone_normalized`
  - `phone_valid` → path: `phone_valid`  
  - `phone_flag` → path: `phone_flag`

---

## PHASE 5 — ADD SMS NODE TO PREMIUM FLOW ONLY

> Standard = lead capture only. No SMS. No booking. Do not add SMS to Standard.
>
> Premium SMS purpose: send an in-call confirmation to the caller after details
> are captured. Example: "We've got your details — our team will call you back
> within [timeframe] to confirm your appointment."
>
> This is NOT a booking link. It is a confirmation message only.
> It replaces nothing in the n8n pipeline — it's purely in-call UX.
>
> Telnyx pending approval — use Retell's native SMS (works on Retell Twilio numbers).
> Verify +18129944371 has SMS enabled before adding this node.

### Check SMS eligibility first:

```python
r = requests.get("https://api.retellai.com/get-phone-number/+18129944371", headers=RETELL_H)
phone_data = r.json()
sms_enabled = phone_data.get("sms_enabled", False)
print(f"SMS enabled on +18129944371: {sms_enabled}")
# If False — do not add SMS node yet. Log as blocked, move on.
```

### If SMS enabled — Dan adds via UI:

Add SMS node to Premium TESTING flow only:
- Name: `send_confirmation_sms`
- Place after `validate_phone`, before `Ending`
- SMS content type: Static
- Message: `"Thanks for calling {{company_name}}. We've got your details and our team will be in touch shortly. — {{agent_name}}"`
- Destination: caller's number (default)

---

## PHASE 6 — SIMPLIFY N8N CALL PROCESSORS

> Remove GPT extraction from both call processors.
> Map Retell post_call_analysis fields directly to Supabase.
> The webhook payload now contains all extracted fields natively.

### What the Retell webhook payload now contains:

```json
{
  "call_id": "...",
  "agent_id": "...",
  "start_timestamp": 1234567890,
  "end_timestamp": 1234567890,
  "duration_ms": 45000,
  "transcript": "...",
  "recording_url": "...",
  "call_analysis": {
    "caller_name": "John Smith",
    "caller_phone": "+15551234567",
    "caller_address": "123 Main St Austin TX",
    "service_requested": "AC not cooling",
    "job_type": "repair",
    "urgency": "urgent",
    "is_lead": true,
    "lead_score": 8,
    "caller_sentiment": "frustrated",
    "transfer_attempted": false,
    "transfer_success": false,
    "vulnerable_occupant": false,
    "summary": "Caller requested AC repair...",
    "notes": ""
  }
}
```

### Standard Call Processor changes (`Kg576YtPM9yEacKn`):

**Remove:**
- HTTP Request node → OpenAI/GPT (transcript analysis)
- JSON parse/flatten nodes
- Any error handling specific to GPT response

**Keep — these still do real work:**
- Webhook receiver node
- Supabase lookup (agent_id → client config)
- Supabase INSERT to hvac_call_log
- Geocoding node (caller_address → geocode_formatted)
- HubSpot call note
- Client email summary

**New field mapping in Supabase INSERT node:**

```
agent_id          → {{ $json.agent_id }}
call_id           → {{ $json.call_id }}
company_name      → [from Supabase client lookup]
caller_name       → {{ $json.call_analysis.caller_name }}
caller_phone      → {{ $json.call_analysis.caller_phone }}
caller_address    → {{ $json.call_analysis.caller_address }}
service_requested → {{ $json.call_analysis.service_requested }}
job_type          → {{ $json.call_analysis.job_type }}
urgency           → {{ $json.call_analysis.urgency }}
is_lead           → {{ $json.call_analysis.is_lead }}
lead_score        → {{ $json.call_analysis.lead_score }}
caller_sentiment  → {{ $json.call_analysis.caller_sentiment }}
transfer_attempted→ {{ $json.call_analysis.transfer_attempted }}
transfer_success  → {{ $json.call_analysis.transfer_success }}
vulnerable_occupant→{{ $json.call_analysis.vulnerable_occupant }}
summary           → {{ $json.call_analysis.summary }}
notes             → {{ $json.call_analysis.notes }}
call_tier         → "Standard"
duration_seconds  → {{ Math.round($json.duration_ms / 1000) }}
created_at        → {{ $now }}
```

### Premium Call Processor changes (`STQ4Gt3rH8ptlvMi`):

Identical approach — same field mapping, same removals.
Additional Premium-only fields remain (call_tier = "Premium", any booking-related fields).
The GPT node + filter node crash + JSON flattening complexity — all gone.

### After updating both processors:

1. Trigger a test call on the Standard TESTING agent
2. Confirm webhook fires and Supabase row is written correctly
3. Confirm all fields populate from call_analysis (not null)
4. Confirm geocoding still runs on caller_address
5. Confirm HubSpot note is logged
6. Confirm client email fires

---

## PHASE 7 — UPDATE E2E TESTS

> The E2E tests assert on specific Supabase field values after a test call.
> The field names are the same — but the data source changed from GPT → Retell.
> Tests need to be re-verified, not rewritten.

### Steps:

```bash
# In Claude Code:
cd /path/to/syntharra-automations
python3 shared/e2e-test.py  # Standard E2E
# Review any failures — check if they're field mapping issues vs agent issues
# Update field assertions if Retell returns data in slightly different format
# Re-run until green
```

**Do NOT run Premium E2E until Standard is confirmed green.**
Premium E2E after Standard passes.

---

## PHASE 8 — PROMOTE TO MASTER (final gate)

Only after:
- [ ] Both E2E suites pass on TESTING agents
- [ ] At least 3 real test calls made and Supabase data verified
- [ ] Dan has reviewed call data quality in Retell analytics dashboard
- [ ] Dan gives explicit go-ahead

### Promotion sequence:

```python
# 1. Patch Standard MASTER with the same post_call_analysis_data config
requests.patch(f"https://api.retellai.com/update-agent/{STANDARD_MASTER}",
               headers=RETELL_H, json={"post_call_analysis_data": post_call_analysis_data,
                                        "post_call_analysis_model": "gpt-4.1-mini"})
requests.post(f"https://api.retellai.com/publish-agent/{STANDARD_MASTER}", headers=RETELL_H)

# 2. Apply same flow changes to Standard MASTER flow
# (Extract node, Code node must be manually added to MASTER flow in UI by Dan first)

# 3. Same for Premium MASTER

# 4. Switch n8n call processors from TESTING webhook → live webhook
# (or confirm they already fire on MASTER agent calls)

# 5. Update docs/context/AGENTS.md with any new node IDs
# 6. Push session log
# 7. Update TASKS.md — mark sprint complete
```

---

## FALLBACK PLAN

If anything goes wrong after promotion:

- MASTER agents still have their original flows — the TESTING agents were patched,
  not the MASTER flows (except for post_call_analysis_data which is easily reverted)
- To revert post_call_analysis_data: PATCH with empty array `[]` and publish
- Flow changes: revert via Retell dashboard version history
- Call processors: restore from nightly GitHub backup (`Nightly GitHub Backup` workflow)

**The original MASTER agent configurations are preserved in:**
- `retell-agents/hvac-standard-master-backup-[date].json`
- `retell-agents/hvac-premium-master-backup-[date].json`
- Run `Nightly GitHub Backup` workflow manually to capture current state before starting

---

## TASKS.md UPDATE — Add this to open work after session

```
### Retell Enhancement Sprint — POST-PREMIUM-PROMOTION ⏸️
> DO NOT START until Premium TESTING → MASTER promotion is complete
- [ ] Run Phase 0 pre-flight checks
- [ ] Phase 1: Sync TESTING agents to clean MASTER copies
- [ ] Phase 2: Configure post_call_analysis_data via API on both TESTING agents
- [ ] Phase 3: Dan adds Extract Dynamic Variable nodes in UI (Standard + Premium TESTING flows)
- [ ] Phase 4: Dan adds Code node (phone validation) in UI (both flows)
- [ ] Phase 5: Check SMS eligibility on +18129944371 — add SMS node to Premium if enabled
- [ ] Phase 6: Simplify n8n Standard + Premium call processors (remove GPT, direct field map)
- [ ] Phase 7: Re-run E2E tests — Standard first, then Premium
- [ ] Phase 8: Dan review + go-ahead → promote to MASTER
- Reference: docs/prompts/retell-enhancement-prompt.md
```
