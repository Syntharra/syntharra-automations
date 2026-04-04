# Syntharra — Retell Enhancement Sprint (v2)
## Claude Code Implementation Prompt (built with prompt-master v1.5.0 — Template H: ReAct + Stop Conditions)

> **STATUS: LOCKED**
> Do not execute until:
> 1. Premium TESTING agent passes 95%+ across all simulator groups
> 2. Premium TESTING has been promoted to MASTER
> 3. Dan gives explicit go-ahead in chat
>
> Paste the prompt below directly into Claude Code when ready.

---

```
## Context (carry forward)

You are working on Syntharra — an AI phone receptionist product for trade businesses.
The stack is: Retell AI (voice agents) + n8n on Railway (workflows) + Supabase (database) +
GitHub (syntharra-automations repo).

Established decisions you MUST NOT relitigate:
- Standard plan = lead capture only. No booking. No SMS booking links.
- Premium plan = full calendar integration via OAuth dispatchers already built.
- MASTER agents are NEVER deleted or recreated — always PATCH in place.
- Always publish after any agent update.
- All secrets come from syntharra_vault in Supabase — never hardcode.
- Node types (Extract Dynamic Variable, Code node) can only be CREATED
  in the Retell UI — they can be patched via API once created. Dan handles UI steps.
- SMS is handled via Telnyx (pending approval), NOT Retell's built-in Twilio SMS.
  Do NOT use Retell SMS nodes in conversation flows. SMS confirmations fire from n8n
  after the call ends, via Telnyx, once approval is granted.
- Fallback phone number for any client = their lead_phone from hvac_standard_agent.
  Both Standard and Premium clients are in the same table (hvac_standard_agent).

Prior failures to avoid:
- Do NOT run simulators inside this session — they exceed the timeout wall.
- Do NOT use the anon Supabase key for vault lookups — use the service role key.
- Do NOT POST to n8n webhooks for health checks — HEAD only.
- Do NOT touch MASTER agents until all TESTING work is verified and Dan approves.
- PATCH endpoint is https://api.retellai.com/update-agent/{agent_id} (NO /v2/ prefix)
- GET endpoint is https://api.retellai.com/get-agent/{agent_id} (NO /v2/ prefix)
- List calls is POST https://api.retellai.com/v2/list-calls (HAS /v2/ prefix)

Premium MASTER agent (agent_9822f440f5c3a13bc4d283ea90) does not have a published
version yet — Premium testing is still in progress. GET on this agent will 404 until
Premium testing is complete and the agent is published for the first time. This is
expected. This sprint runs on TESTING agents only. Premium MASTER promotion happens
in Phase 8 after all testing is green.

Agent IDs (verified 2026-04-04 — always re-fetch live before using):
- Standard MASTER:          agent_4afbfdb3fcb1ba9569353af28d (published, live)
- Premium MASTER:           agent_9822f440f5c3a13bc4d283ea90 (not yet published — expected)
- Standard MASTER flow:     conversation_flow_34d169608460
- Premium MASTER flow:      conversation_flow_1dd3458b13a7
- Standard TESTING agent:   agent_731f6f4d59b749a0aa11c26929 (working)
- Premium TESTING agent:    agent_2cffe3d86d7e1990d08bea068f (working)
- Standard TESTING flow:    conversation_flow_5b98b76c8ff4 (15 nodes)
- Premium TESTING flow:     conversation_flow_2ded0ed4f808 (19 nodes)

n8n workflow IDs:
- Standard call processor:  Kg576YtPM9yEacKn
- Premium call processor:   STQ4Gt3rH8ptlvMi

Phone number:
- +18129944371 — currently pinned to Standard MASTER version 10
  No fallback number. No geo restrictions. SMS not enabled.

---

## Objective

Implement the Retell Enhancement Sprint across Standard and Premium HVAC agents.
This sprint maximises Retell's built-in features to reduce our own processing load
and create the perfect replicable template agent for any trade business.

Changes in this sprint:
1. Replace GPT-based post-call extraction with Retell's native post_call_analysis_data
2. Add Extract Dynamic Variable and Code nodes to both TESTING flows for data reliability
3. Strip GPT out of both n8n call processors and map webhook fields directly to Supabase
4. Enable guardrails (jailbreak + content moderation) on both agents via API
5. Add HVAC boost keywords for speech recognition accuracy
6. Add pronunciation dictionary for commonly mispronounced terms
7. Enable backchannel ("uh-huh", "yeah") for natural conversation feel
8. Configure reminder triggers for silent callers
9. Tune voice speed, responsiveness, and silence timeout
10. Configure fallback numbers and geo restrictions on phone number
11. Map all new webhook fields to Supabase to populate the client dashboard
12. Re-run E2E tests to confirm everything green before MASTER promotion

---

## Starting State (verified live 2026-04-04)

Standard TESTING agent:
- post_call_analysis_data: 3 system presets (call_summary, call_successful, user_sentiment)
- No custom analysis fields
- No boosted_keywords
- No guardrail_config
- end_call_after_silence_ms: 30000 (already set)
- max_call_duration_ms: 600000 (already set)
- enable_dynamic_voice_speed: true (already set)
- handbook_config: echo_verification, scope_boundaries, natural_filler_words, nato_phonetic,
  high_empathy, smart_matching all enabled
- Flow: 15 nodes (12 conversation + transfer + end + call_style_detector code node)
- webhook_events: ["call_analyzed"]
- responsiveness: 0.9
- voice_speed: 1

Premium TESTING agent:
- post_call_analysis_data: 18 fields (3 system presets + 15 custom)
  Custom fields include: booking_attempted, booking_success, appointment_date,
  appointment_time_window, job_type_booked, reschedule_or_cancel, caller_name,
  caller_phone, caller_email, caller_address, service_requested, call_type,
  urgency, is_hot_lead, lead_score
- No boosted_keywords
- No guardrail_config
- No handbook_config (empty {})
- end_call_after_silence_ms: null (NOT set — differs from Standard)
- max_call_duration_ms: 600000
- enable_dynamic_voice_speed: true
- webhook_events: null (not filtered — gets all events)
- Flow: 19 nodes (booking/scheduling nodes + call_style_detector code node)
- responsiveness: 0.9
- voice_speed: 1

Supabase hvac_call_log: 47 columns (many more than documented). Key columns already
exist for: recording_url, from_number, retell_sentiment, is_hot_lead, notification_type,
call_type, booking_success, booking_attempted, call_successful, latency_p50_ms,
public_log_url, call_cost_cents, disconnection_reason, etc.

IMPORTANT — Sentiment column conflict:
- caller_sentiment column = INTEGER type (old numeric approach)
- retell_sentiment column = TEXT type (what the client dashboard reads)
- Retell's system preset returns user_sentiment as text (e.g. "Neutral")
Map Retell's user_sentiment → retell_sentiment column. Do NOT write to caller_sentiment.

---

## Target State

Both TESTING agents configured as the "perfect replicable template" with:
- Full post_call_analysis_data (system presets + custom fields matching Supabase)
- Guardrails enabled (jailbreak + content moderation)
- HVAC boost keywords (35+ terms)
- Pronunciation dictionary for commonly mispronounced trade terms
- Backchannel enabled for natural conversation
- Reminder triggers for silent callers
- Tuned voice speed, responsiveness, silence timeout
- Extract Dynamic Variable node in flows
- Code node for phone validation in flows

Both n8n call processors updated:
- GPT nodes removed
- Field mapping from webhook call_analysis + call metadata directly to Supabase
- All 47 hvac_call_log columns populated where data is available
- Client dashboard fully populated with no empty fields

Phone number configured:
- Fallback number set (lead_phone from client config)
- Geo restricted to US only
- Outage mode ready to toggle

---

## Allowed Actions

- Read and write files in the syntharra-automations repo via GitHub API
- PATCH Retell agents and flows via Retell API (never DELETE, never create new agents)
- Publish Retell agents after any PATCH
- Read from Supabase (any table)
- Write to Supabase (hvac_call_log, hvac_standard_agent, syntharra_activation_queue only)
- Read n8n workflows via n8n API
- Update n8n workflows via n8n PUT (name/nodes/connections/settings.executionOrder only)
- Make HEAD requests to n8n webhooks to verify they are live (never POST)
- Trigger a single test call on TESTING agents only for verification
- Write session log to docs/session-logs/
- Update docs/TASKS.md, docs/FAILURES.md, docs/REFERENCE.md, docs/context/AGENTS.md

---

## Forbidden Actions

- NEVER delete or recreate any Retell agent
- NEVER touch MASTER agents without Dan's explicit go-ahead
- NEVER push to MASTER flows without passing E2E first
- NEVER hardcode API keys — always fetch from syntharra_vault
- NEVER POST to n8n webhooks — HEAD only for health checks
- NEVER modify the Premium calendar OAuth dispatcher workflows
- NEVER add booking links to any agent or workflow
- NEVER run the agent simulator in this session — it will timeout
- NEVER modify Railway env vars without explicit Dan instruction
- NEVER touch Stripe
- NEVER skip E2E before promoting to MASTER
- NEVER remove the existing call_style_detector code node from either flow

---

## Stop Conditions — Pause and report to Dan when:

- Any MASTER agent GET returns non-200 (⚠️ Premium MASTER already 404 — investigate first)
- Retell API returns an unexpected schema on any PATCH
- A TESTING flow GET shows the Extract/Code nodes are missing
  (Dan needs to create them in the UI first — mandatory UI step)
- A test call fires but hvac_call_log shows null in more than 3 call_analysis fields
- E2E suite reports any failure after call processor changes
- Any n8n workflow PUT returns non-200
- 2 consecutive failures on any single step
- Anything would require touching a MASTER agent before E2E is green

---

## Execution Plan

After each step output: ✅ [step name] — [what was confirmed]

### PHASE 0 — Pre-flight

1. Fetch Retell API key from syntharra_vault
2. GET Standard MASTER — confirm 200 and is_published status
3. GET Premium MASTER — check if still 404. If 404, log as critical blocker in
   FAILURES.md and proceed with Premium TESTING only. Report to Dan.
4. GET both TESTING agents — confirm 200
5. Read FAILURES.md — check for any Retell-area failures not yet in context
6. Back up both MASTER agent JSONs to retell-agents/ in GitHub
   (if Premium MASTER is 404, back up whatever the API returns)
7. Verify Supabase column types for hvac_call_log:
   Run: SELECT column_name, data_type FROM information_schema.columns
        WHERE table_name = 'hvac_call_log' ORDER BY ordinal_position;
   Confirm: lead_score=integer, is_lead=boolean, retell_sentiment=text,
   recording_url=text, from_number=text exist.

✅ Pre-flight complete

### PHASE 1 — Sync TESTING agents to clean MASTER copies

For Standard TESTING: fetch Standard MASTER config and PATCH TESTING to match
(name, voice_id, prompt, all settings).
Set agent_name = "HVAC Standard (ENHANCEMENT TESTING)"
Publish after PATCH.

For Premium TESTING: if Premium MASTER is accessible, sync from it.
If Premium MASTER is 404, keep Premium TESTING as-is (it already has 18 custom fields).
Set agent_name = "HVAC Premium (ENHANCEMENT TESTING)"
Publish after PATCH.

Update docs/context/AGENTS.md with new agent names.
✅ Phase 1 complete

### PHASE 2 — Configure agent features via API on both TESTING agents

Apply ALL of the following via PATCH to BOTH TESTING agents.
PATCH endpoint: https://api.retellai.com/update-agent/{agent_id}
Publish both agents after all PATCHes.

A) POST-CALL ANALYSIS DATA

Standard TESTING currently has 3 system presets only.
Premium TESTING already has 18 fields.

Standard needs custom fields added to match Premium + our Supabase columns.
PATCH Standard TESTING with the FULL post_call_analysis_data array:

[
  { "type": "system-presets", "name": "call_summary",
    "description": "Write a 2-3 sentence summary: what caller needed, what was captured, what the next step is." },
  { "type": "system-presets", "name": "call_successful",
    "description": "True if agent completed the conversation naturally without errors or caller frustration." },
  { "type": "system-presets", "name": "user_sentiment",
    "description": "Evaluate caller sentiment and satisfaction." },
  { "type": "string",  "name": "caller_name",
    "description": "Full name of the caller as stated during the call. Empty string if not provided.",
    "examples": ["John Smith", "Maria Garcia"] },
  { "type": "string",  "name": "caller_phone",
    "description": "Phone number the caller provided for callback. May differ from caller ID. Empty string if not provided.",
    "examples": ["+15551234567", "555-867-5309"] },
  { "type": "string",  "name": "caller_address",
    "description": "Full service address including street, city, state. Empty string if not provided.",
    "examples": ["123 Main St, Austin TX"] },
  { "type": "string",  "name": "service_requested",
    "description": "The specific HVAC service or problem described. Short description.",
    "examples": ["AC not cooling", "furnace won't start", "annual tune-up"] },
  { "type": "string",  "name": "call_type",
    "description": "Type of call. One of: new_service, emergency, callback, existing_customer, general_question, spam, wrong_number." },
  { "type": "string",  "name": "urgency",
    "description": "Urgency level: emergency, high, medium, low." },
  { "type": "boolean", "name": "is_hot_lead",
    "description": "True if this is a hot lead — caller wants service soon and provided contact details." },
  { "type": "number",  "name": "lead_score",
    "description": "Score 1-10. 9-10: emergency needing immediate service. 7-8: active repair/install request. 5-6: maintenance/quote. 3-4: low intent. 1-2: spam/wrong number/robocall." },
  { "type": "boolean", "name": "transfer_attempted",
    "description": "True if agent attempted to transfer the call to a human." },
  { "type": "boolean", "name": "transfer_success",
    "description": "True if transfer was successfully connected. False if transfer failed." },
  { "type": "boolean", "name": "vulnerable_occupant",
    "description": "True if caller mentioned elderly, children, medical equipment, or other vulnerable person affected by the HVAC issue." },
  { "type": "boolean", "name": "emergency",
    "description": "True if this is a genuine HVAC emergency (no heat in winter, no AC with vulnerable occupant, gas smell, CO detector)." },
  { "type": "string",  "name": "notification_type",
    "description": "Notification priority routing. One of: emergency, hot_lead, general_lead, follow_up_required, existing_customer, spam, nonemergency_lead." },
  { "type": "string",  "name": "notes",
    "description": "Additional details not captured elsewhere — equipment brand, model, access notes, preferred callback time, anything relevant." }
]

Set post_call_analysis_model = "gpt-4.1-mini" on both.

For Premium TESTING: PATCH the SAME custom fields as above, PLUS keep its existing
Premium-specific fields (booking_attempted, booking_success, appointment_date,
appointment_time_window, job_type_booked, reschedule_or_cancel, caller_email).
Merge, do not replace — the Premium array should be a superset of Standard.

Verify: GET each agent, confirm custom fields present. Standard should have ~17 entries.
Premium should have ~22 entries (Standard fields + Premium booking fields).


B) GUARDRAILS — real-time content moderation + jailbreak detection

PATCH both TESTING agents with:
{
  "guardrail_config": {
    "output_topics": [
      "harassment", "self_harm", "sexual_exploitation", "violence",
      "child_safety_and_exploitation", "illicit_and_harmful_activity",
      "regulated_professional_advice"
    ],
    "input_topics": [
      "platform_integrity_jailbreaking"
    ]
  }
}

Note: gambling + defense_and_national_security omitted — irrelevant to HVAC.
regulated_professional_advice included — agent must NOT give pricing or legal advice.
Jailbreak detection blocks prompt injection attempts in real-time.
Adds ~50ms latency — acceptable tradeoff.
Our Daily Transcript Analysis workflow STAYS for post-hoc quality reporting.

Verify: GET each agent, confirm guardrail_config field is present with correct topics.


C) BOOST KEYWORDS — HVAC vocabulary for speech recognition

PATCH both TESTING agents with:
{
  "boosted_keywords": [
    "HVAC", "compressor", "condenser", "furnace", "AC", "air conditioning",
    "Trane", "Lennox", "Carrier", "Rheem", "Goodman", "York", "Daikin",
    "Amana", "Bryant", "American Standard", "Ruud", "Mitsubishi",
    "R-410A", "R-22", "refrigerant", "Freon",
    "mini split", "ductless", "heat pump", "air handler", "evaporator",
    "thermostat", "Honeywell", "Nest", "Ecobee", "Trane XL",
    "tonnage", "SEER", "SEER2", "BTU", "EER",
    "ductwork", "capacitor", "blower motor", "drain line", "coil",
    "tune up", "maintenance", "annual service",
    "Syntharra", "callback"
  ]
}

Verify: GET each agent, confirm boosted_keywords array populated.


D) PRONUNCIATION DICTIONARY

PATCH both TESTING agents with:
{
  "pronunciation_dictionary": [
    { "word": "HVAC", "alphabet": "ipa", "phoneme": "eɪtʃ viː eɪ siː" },
    { "word": "SEER", "alphabet": "ipa", "phoneme": "sɪr" },
    { "word": "Trane", "alphabet": "ipa", "phoneme": "treɪn" },
    { "word": "Rheem", "alphabet": "ipa", "phoneme": "riːm" },
    { "word": "Daikin", "alphabet": "ipa", "phoneme": "daɪkɪn" },
    { "word": "Lennox", "alphabet": "ipa", "phoneme": "lɛnəks" }
  ]
}


E) BACKCHANNEL + REMINDERS

PATCH both TESTING agents with:
{
  "enable_backchannel": true,
  "backchannel_frequency": 0.8,
  "backchannel_words": ["yeah", "uh-huh", "got it", "okay", "right"],
  "reminder_trigger_ms": 15000,
  "reminder_max_count": 2
}

enable_backchannel: agent says "uh-huh" etc while caller talks — more natural.
backchannel_frequency 0.8: fairly frequent but not every sentence.
reminder_trigger_ms 15000: if caller goes silent for 15s, agent gives a gentle nudge.
reminder_max_count 2: max 2 reminders before end_call_after_silence kicks in.


F) VOICE & CONVERSATION TUNING

PATCH both TESTING agents with:
{
  "responsiveness": 0.85,
  "voice_speed": 1.05,
  "end_call_after_silence_ms": 30000,
  "max_call_duration_ms": 600000,
  "normalize_for_speech": true,
  "enable_dynamic_voice_speed": true,
  "enable_dynamic_responsiveness": true
}

responsiveness 0.85: slightly faster response for direct trade callers.
voice_speed 1.05: marginally brisker, professional not rushed.
end_call_after_silence_ms 30000: auto-hangup after 30s dead air (saves billing).
max_call_duration_ms 600000: hard cap at 10 minutes (prevents runaway calls).
normalize_for_speech: improves how numbers and addresses are spoken aloud.
Dynamic speed + responsiveness: agent matches caller's pace automatically.


G) HANDBOOK CONFIG (Standard already has this, Premium doesn't)

PATCH Premium TESTING agent only with:
{
  "handbook_config": {
    "echo_verification": true,
    "speech_normalization": false,
    "default_personality": false,
    "scope_boundaries": true,
    "natural_filler_words": true,
    "nato_phonetic_alphabet": true,
    "high_empathy": true,
    "ai_disclosure": false,
    "smart_matching": true
  }
}

echo_verification: agent confirms back what it heard (critical for addresses/names).
scope_boundaries: agent stays in HVAC scope, won't answer unrelated questions.
nato_phonetic_alphabet: spells back names/codes clearly.
high_empathy: appropriate for stressed callers with HVAC emergencies.
ai_disclosure: off — agent does not proactively say it's AI.


H) WEBHOOK EVENTS FILTER

PATCH Premium TESTING agent with:
{
  "webhook_events": ["call_analyzed"]
}

Standard already has this. Premium was getting all events (call_started, call_ended,
transcript_updated, etc) — wasteful. We only need call_analyzed for our processing.


After ALL PATCHes: Publish both TESTING agents.
Verify: GET each agent, check every field from A-H is correctly set.

✅ Phase 2 complete — all agent features configured


### PHASE 3 — UI steps required from Dan (pause here)

The following node types MUST be created in the Retell UI — they cannot be created via API.
Stop and present Dan with these instructions:

---

DAN — UI STEPS REQUIRED (approximately 10 minutes):

Standard TESTING flow (conversation_flow_5b98b76c8ff4):
1. Open this flow in Retell dashboard
2. Add an "Extract Dynamic Variable" node — name it: extract_lead_data
   Place it between: nonemergency_leadcapture → extract_lead_data → Ending
   Configure to extract: caller_name, caller_phone, caller_address, service_requested
3. Add a "Code" node — name it: validate_phone
   Place it between: extract_lead_data → validate_phone → Ending
   ⚠️ Do NOT remove the existing call_style_detector code node — it stays.
   Paste this JavaScript into the code editor:

   const raw = dv.caller_phone || "";
   const digits = raw.replace(/\D/g, "");
   let phone_normalized = raw, phone_valid = false, phone_flag = "";
   if (digits.length === 10) { phone_normalized = `+1${digits}`; phone_valid = true; }
   else if (digits.length === 11 && digits.startsWith("1")) { phone_normalized = `+${digits}`; phone_valid = true; }
   else if (digits.length < 7) { phone_flag = "incomplete_number"; }
   else { phone_flag = "unusual_format"; phone_valid = true; }
   return { phone_normalized, phone_valid, phone_flag };

   Store response variables: phone_normalized, phone_valid, phone_flag

Premium TESTING flow (conversation_flow_2ded0ed4f808):
Same Extract Dynamic Variable and Code node — identical config.
⚠️ Do NOT remove the existing call_style_detector code node — it stays here too.

Tell Claude Code when UI steps are done and which nodes were successfully added.

---

After Dan confirms: verify all nodes exist via GET on each flow.
✅ Phase 3 complete — all UI nodes confirmed present in both flows


### PHASE 4 — Configure fallback numbers, geo restrictions, fraud protection

Configure safety features on phone number +18129944371:

First, look up the client's lead_phone from hvac_standard_agent:
  SELECT lead_phone FROM hvac_standard_agent
  WHERE agent_id = 'agent_4afbfdb3fcb1ba9569353af28d';

If lead_phone exists, use it as fallback. If null, use +18563630633 (transfer dest).

PATCH https://api.retellai.com/update-phone-number/+18129944371 with:
{
  "fallback_number": "<lead_phone or +18563630633>",
  "allowed_inbound_country_list": ["US"],
  "allowed_outbound_country_list": ["US"]
}

This configures:
- Fallback: if outage mode toggled, inbound routes to client's office number
- Geo restriction: only US callers (prevents IRSF fraud)
- Outbound locked to US

Do NOT enable outage mode — just configure so it's ready.
Dan can toggle from Retell dashboard (Settings > Reliability) when needed.

NOTE FOR ONBOARDING WORKFLOWS: After this sprint, update BOTH onboarding workflows
(4Hx7aRdzMl5N0uJP Standard, kz1VmwNccunRMEaF Premium) to set fallback_number
to lead_phone whenever a new client phone number is provisioned. Add to TASKS.md.

Verify: GET phone number, confirm fallback_number and country lists set.

✅ Phase 4A complete


### PHASE 4B — Dan dashboard tasks (alerting + analytics charts)

Present to Dan as a task list — these are DASHBOARD-ONLY:

RETELL ALERTING (Settings > Alerting tab) — create 5 rules:

1. "Call Volume Spike"
   Metric: Call Count | Relative > 200% vs previous | Window: 1 hour | Freq: 5 min
   Notify: alerts@syntharra.com

2. "Transfer Failures"
   Metric: Transfer Call Failure Count | Absolute > 3 | Window: 1 hour | Freq: 5 min
   Notify: alerts@syntharra.com

3. "Daily Cost Cap"
   Metric: Total Call Cost | Absolute > $50 | Window: 24 hours | Freq: 1 hour
   Notify: alerts@syntharra.com

4. "Negative Sentiment"
   Metric: Negative Sentiment Rate | Absolute > 30% | Window: 12 hours | Freq: 1 hour
   Notify: alerts@syntharra.com

5. "API Errors"
   Metric: API Error Count | Absolute > 5 | Window: 1 hour | Freq: 5 min
   Notify: alerts@syntharra.com

RETELL GUARDRAILS (Agent > Security & Fallback — EACH agent):
If guardrail_config PATCH in Phase 2 didn't work, Dan must enable guardrails
manually in the dashboard for both TESTING agents:
- Output: harassment, self_harm, sexual_exploitation, violence,
  child_safety, illicit_activity, regulated_professional_advice → all ON
- Input: jailbreaking → ON

RETELL ANALYTICS (Analytics tab) — create 5 charts:
1. Lead Score Distribution (donut, post_call field: lead_score)
2. Daily Call Volume (line chart)
3. Urgency Breakdown (donut, post_call field: urgency)
4. Caller Sentiment Trend (line, system preset: user_sentiment)
5. Is Hot Lead Rate (number, post_call field: is_hot_lead)

After creation: syntharra-ops-monitor Railway service can remain PAUSED permanently.

✅ Phase 4B complete


### PHASE 5 — Simplify n8n call processors

For Standard call processor (Kg576YtPM9yEacKn):
1. GET the workflow via n8n API
2. Identify and remove: OpenAI/GPT HTTP node, JSON parse/flatten nodes
3. In the Supabase INSERT node, update field mapping.

The webhook fires event "call_analyzed" with this structure:
{
  "event": "call_analyzed",
  "call": {
    "call_id": "...",
    "call_type": "phone_call",
    "agent_id": "...",
    "agent_version": 10,
    "from_number": "+15551234567",      ← only on phone calls
    "to_number": "+18129944371",        ← only on phone calls
    "direction": "inbound",             ← only on phone calls
    "disconnection_reason": "user_hangup",
    "duration_ms": 95000,
    "recording_url": "https://...",
    "public_log_url": "https://...",
    "transcript": "...",
    "call_analysis": {
      "in_voicemail": false,
      "call_summary": "...",            ← system preset
      "user_sentiment": "Neutral",      ← system preset (capitalised text)
      "call_successful": true,          ← system preset
      "custom_analysis_data": {
        "caller_name": "John Smith",    ← our custom fields
        "caller_phone": "+15551234567",
        "caller_address": "123 Main St",
        "service_requested": "AC not cooling",
        "call_type": "new_service",
        "urgency": "high",
        "is_hot_lead": true,
        "lead_score": 8,
        "transfer_attempted": false,
        "transfer_success": false,
        "vulnerable_occupant": false,
        "emergency": false,
        "notification_type": "hot_lead",
        "notes": "Trane unit, 5 years old"
      }
    },
    "call_cost": {
      "total_duration_unit_price": 0.20,
      "product_costs": [...]
    },
    "latency": {
      "e2e": { "p50": 1098, ... },
      "llm": { "p50": 646, ... }
    },
    "collected_dynamic_variables": { "current_node": "Ending", ... }
  }
}

FIELD MAPPING — Supabase INSERT for hvac_call_log:

call_id              → {{ $json.call.call_id }}
agent_id             → {{ $json.call.agent_id }}
company_name         → [from Supabase client lookup by agent_id — KEEP EXISTING NODE]
caller_name          → {{ $json.call.call_analysis.custom_analysis_data.caller_name }}
caller_phone         → {{ $json.call.call_analysis.custom_analysis_data.caller_phone }}
caller_address       → {{ $json.call.call_analysis.custom_analysis_data.caller_address }}
service_requested    → {{ $json.call.call_analysis.custom_analysis_data.service_requested }}
job_type             → [keep from existing logic or derive from call_type]
urgency              → {{ $json.call.call_analysis.custom_analysis_data.urgency }}
is_lead              → {{ $json.call.call_analysis.custom_analysis_data.is_hot_lead }}
lead_score           → {{ $json.call.call_analysis.custom_analysis_data.lead_score }}
retell_sentiment     → {{ $json.call.call_analysis.user_sentiment }}
                        ⚠️ Map to retell_sentiment column (TEXT), NOT caller_sentiment (INTEGER)
transfer_attempted   → {{ $json.call.call_analysis.custom_analysis_data.transfer_attempted }}
transfer_success     → {{ $json.call.call_analysis.custom_analysis_data.transfer_success }}
vulnerable_occupant  → {{ $json.call.call_analysis.custom_analysis_data.vulnerable_occupant }}
summary              → {{ $json.call.call_analysis.call_summary }}
retell_summary       → {{ $json.call.call_analysis.call_summary }}
notes                → {{ $json.call.call_analysis.custom_analysis_data.notes }}
call_tier            → "Standard"
duration_seconds     → {{ Math.round($json.call.duration_ms / 1000) }}
recording_url        → {{ $json.call.recording_url }}
public_log_url       → {{ $json.call.public_log_url }}
from_number          → {{ $json.call.from_number }}
call_type            → {{ $json.call.call_analysis.custom_analysis_data.call_type }}
is_hot_lead          → {{ $json.call.call_analysis.custom_analysis_data.is_hot_lead }}
call_successful      → {{ $json.call.call_analysis.call_successful }}
notification_type    → {{ $json.call.call_analysis.custom_analysis_data.notification_type }}
emergency            → {{ $json.call.call_analysis.custom_analysis_data.emergency }}
disconnection_reason → {{ $json.call.disconnection_reason }}  [NEW — add to INSERT]
latency_p50_ms       → {{ $json.call.latency?.e2e?.p50 }}
call_cost_cents      → {{ Math.round(($json.call.call_cost?.total_duration_unit_price || 0) * $json.call.duration_ms / 60000 * 100) }}
transcript           → {{ $json.call.transcript }}
geocode_status       → [populated by geocoding node downstream — KEEP AS-IS]
geocode_formatted    → [populated by geocoding node downstream — KEEP AS-IS]

4. Keep untouched: Supabase client lookup, geocoding node, HubSpot note, email node,
   Slack notification node
5. PUT updated workflow — Publish

Repeat for Premium call processor (STQ4Gt3rH8ptlvMi):
Same field mapping. call_tier = "Premium".
ADDITIONALLY map Premium-specific fields:
booking_attempted    → {{ $json.call.call_analysis.custom_analysis_data.booking_attempted }}
booking_success      → {{ $json.call.call_analysis.custom_analysis_data.booking_success }}
appointment_date     → {{ $json.call.call_analysis.custom_analysis_data.appointment_date }}
appointment_time     → {{ $json.call.call_analysis.custom_analysis_data.appointment_time_window }}
job_type_booked      → {{ $json.call.call_analysis.custom_analysis_data.job_type_booked }}
booking_reference    → [from dispatcher workflow if booking was created — KEEP AS-IS]

Preserve all Premium-specific nodes (dispatcher trigger, OAuth handling).

✅ Phase 5 complete — both processors updated, GPT nodes removed, published


### PHASE 6 — Verification test calls

Trigger a test call on Standard TESTING agent.
Wait for call_analyzed webhook to fire.
Query hvac_call_log for the test record.

Confirm:
- call_analysis custom fields are populated (not null) for at least 10 of 17 fields
- duration_seconds populated and > 0
- recording_url is not null and starts with "https://"
- retell_sentiment is not null and is a text string (e.g. "Neutral")
- call_successful is boolean, not null
- call_type is one of our defined values
- lead_score is an integer
- notification_type is not null
- geocode ran if address was provided
- HubSpot note was logged (check n8n execution log)
- Client email did not fire (TESTING agent has no real client email)
- latency_p50_ms populated
- from_number populated (only if phone call — will be null for web call test)

If any critical field is null when it shouldn't be, check the webhook payload
structure by inspecting the n8n execution log raw input. The JSON path might be
different — adjust the field mapping and re-test.

Repeat for Premium TESTING agent.

Downstream verification:
1. Weekly Lead Report (iLPb6ByiytisqUJC) — manually trigger. Verify it renders
   with the new data. lead_score is now integer (was sometimes string) — confirm.
2. Monthly Minutes Calculator (z1DNTjvTDAkExsX8) — confirm duration_seconds populated.
3. Daily Transcript Analysis (ofoXmXwjW9WwGvL6) — confirm transcript field still written.
4. Slack notification — if wired, confirm fires on lead_score >= 7 test call.

✅ Phase 6 complete — both test calls verified, all downstream workflows confirmed


### PHASE 7 — Re-run E2E tests

Update E2E test assertions BEFORE running:
1. lead_score: accept integer (was sometimes string from GPT)
2. is_lead: accept boolean (was sometimes string)
3. Add assertions for new fields: recording_url not null, retell_sentiment not null,
   call_type in defined values, notification_type not null, is_hot_lead boolean
4. Remove GPT-specific response format assertions
5. Add guardrail check: GET agent, confirm guardrail_config present

Run Standard E2E: python3 shared/e2e-test.py
Run Premium E2E: python3 shared/e2e-test-premium.py

Both must be green before Phase 8.
✅ Phase 7 complete — Standard E2E: [X/X] ✅ | Premium E2E: [X/X] ✅


### PHASE 8 — Promote to MASTER (requires Dan go-ahead)

Stop here. Present Dan with:
- Phase 7 E2E results
- Sample hvac_call_log rows from test calls showing field quality
- Confirmation both TESTING agents are working correctly

Wait for explicit Dan approval.

After approval:

STANDARD MASTER:
1. PATCH Standard MASTER with all Phase 2 config (post_call_analysis_data, guardrails,
   boost keywords, pronunciation, backchannel, reminders, tuning, handbook)
2. Publish via API
3. Dan publishes via "Deployment" button in dashboard to create versioned snapshot
4. Pin phone number to the new version number
5. Dan adds Extract Dynamic Variable + Code nodes to Standard MASTER flow in UI

PREMIUM MASTER:
- Premium MASTER has not been published before. First publish will make it accessible.
- PATCH Premium MASTER with all Phase 2 config
- Publish via API, then Dan publishes via Deployment button
- Dan adds Extract Dynamic Variable + Code nodes to Premium MASTER flow in UI

6. Dan adds Extract Dynamic Variable + Code nodes to Premium MASTER flow in UI
7. Confirm both MASTER agents published successfully
8. n8n processors are already live (not agent-specific — already updated in Phase 5)

Document version numbers in docs/context/AGENTS.md.
✅ Phase 8 complete


---

## Session Close (mandatory)

Before ending:
1. Append any new failures/fixes to docs/FAILURES.md
2. Update syntharra-retell-SKILL.md with:
   - post_call_analysis_data pattern and full field list
   - Guardrail configuration (guardrail_config with output_topics and input_topics)
   - Boost keywords pattern and HVAC vocabulary list
   - Pronunciation dictionary pattern
   - Backchannel + reminder configuration
   - Responsiveness/voice_speed/silence_timeout settings
   - Fallback number configuration (default to lead_phone)
   - Versioning workflow (Deployment button → version pin → rollback)
   - Correct PATCH endpoint: /update-agent/ (no /v2/)
   - Correct list calls endpoint: /v2/list-calls (HAS /v2/)
   - Webhook payload structure with correct JSON paths
   - Note: custom_analysis_data is nested inside call_analysis
   - Note: user_sentiment maps to retell_sentiment column (text, not integer)
   - Note: guardrails add ~50ms latency
   - Note: existing call_style_detector code node must NOT be removed
3. Update docs/ARCHITECTURE.md with decisions:
   - Retell guardrails for live protection + Groq for post-hoc quality
   - Retell alerting replaces syntharra-ops-monitor for call monitoring
   - Retell versioning is primary rollback, GitHub JSON is secondary
   - recording_url stored in Supabase but Retell holds recordings indefinitely
   - Sentiment: retell_sentiment (text) is canonical; caller_sentiment (integer) is deprecated
   - Fallback number defaults to lead_phone from hvac_standard_agent
   - Onboarding workflows must set fallback_number on new client phone numbers
4. Update docs/TASKS.md with:
   - Onboarding workflow update: set fallback_number = lead_phone on phone provision
   - Telnyx SMS integration: post-call confirmation SMS via n8n once Telnyx approved
   - Inbound webhook for caller context injection (FUTURE SPRINT)
   - Two-way SMS evaluation: Retell native vs Telnyx (DECISION NEEDED)
   - Retell HubSpot native integration evaluation (FUTURE)
   - A/B testing for prompt/voice variants (POST-LAUNCH)
5. Update docs/REFERENCE.md if agent versions changed
6. Update docs/context/AGENTS.md with final agent config
7. Update docs/context/SUPABASE.md — document ALL 47 columns of hvac_call_log
8. Push session log to docs/session-logs/
9. Back up any changed Retell agents to retell-agents/
10. Confirm ALL changes pushed to GitHub

Session log must include mandatory reflection (1-6 from CLAUDE.md rules).
```
