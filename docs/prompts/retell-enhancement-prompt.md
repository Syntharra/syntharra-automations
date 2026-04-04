# Syntharra — Retell Enhancement Sprint
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

You are working on Syntharra — an AI phone receptionist product for HVAC trade businesses.
The stack is: Retell AI (voice agents) + n8n on Railway (workflows) + Supabase (database) +
GitHub (syntharra-automations repo).

Established decisions you MUST NOT relitigate:
- Standard plan = lead capture only. No booking. No SMS booking links.
- Premium plan = full calendar integration via OAuth dispatchers already built.
- MASTER agents are NEVER deleted or recreated — always PATCH in place.
- Always publish after any agent update.
- All secrets come from syntharra_vault in Supabase — never hardcode.
- Node types (Extract Dynamic Variable, Code node, SMS node) can only be CREATED
  in the Retell UI — they can be patched via API once created. Dan handles UI steps.
- SMS confirmation node (Premium only) sends a callback confirmation, NOT a booking link.

Prior failures to avoid:
- Do NOT run simulators inside this session — they exceed the timeout wall.
- Do NOT use the anon Supabase key for vault lookups — use the service role key.
- Do NOT POST to n8n webhooks for health checks — HEAD only.
- Do NOT touch MASTER agents until all TESTING work is verified and Dan approves.

Agent IDs (verified 2026-04-04 — always re-fetch live before using):
- Standard MASTER:          agent_4afbfdb3fcb1ba9569353af28d
- Premium MASTER:           agent_9822f440f5c3a13bc4d283ea90
- Standard MASTER flow:     conversation_flow_34d169608460
- Premium MASTER flow:      conversation_flow_1dd3458b13a7
- Standard TESTING agent:   agent_731f6f4d59b749a0aa11c26929
- Premium TESTING agent:    agent_2cffe3d86d7e1990d08bea068f
- Standard TESTING flow:    conversation_flow_5b98b76c8ff4
- Premium TESTING flow:     conversation_flow_2ded0ed4f808

n8n workflow IDs:
- Standard call processor:  Kg576YtPM9yEacKn
- Premium call processor:   STQ4Gt3rH8ptlvMi

---

## Objective

Implement the Retell Enhancement Sprint across Standard and Premium HVAC agents.
This sprint: (1) replaces GPT-based post-call extraction with Retell's native
post_call_analysis_data, (2) adds Extract Dynamic Variable and Code nodes to both
TESTING flows for better lead data reliability, (3) adds an SMS confirmation node
to the Premium TESTING flow only, (4) strips GPT out of both n8n call processors
and maps Retell webhook fields directly to Supabase, and (5) re-runs E2E tests
to confirm everything is green before anything touches MASTER.

---

## Starting State

- Both MASTER agents: fully tested, published, live
- Standard TESTING agent: synced with Standard MASTER post-Premium promotion
- Premium TESTING agent: just promoted to MASTER — TESTING agent now available for this sprint
- Both n8n call processors: currently use GPT node to extract call data from transcript
- E2E test suite: passing on Standard (80/80), Premium (89/89) — pre-enhancement baseline

---

## Target State

- Both TESTING agents have post_call_analysis_data configured via API (14 fields)
- Both TESTING flows have Extract Dynamic Variable node after lead capture node
- Both TESTING flows have Code node (phone validation) after extract node
- Premium TESTING flow has SMS confirmation node (after phone validation, before Ending)
- Both n8n call processors no longer call GPT — field mapping comes directly from
  Retell webhook call_analysis payload
- E2E tests pass on both TESTING agents with new field mapping
- MASTER agents updated only after Dan's explicit go-ahead
- All changes pushed to GitHub, session log written, TASKS.md updated

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
- Update docs/TASKS.md, docs/FAILURES.md, docs/context/AGENTS.md

---

## Forbidden Actions

- NEVER delete or recreate any Retell agent
- NEVER touch MASTER agents (agent_4afb... or agent_9822...) without Dan's explicit
  go-ahead in this chat session — even if the phase plan says to promote
- NEVER push to MASTER flows without passing E2E first
- NEVER hardcode API keys — always fetch from syntharra_vault
- NEVER POST to n8n webhooks — HEAD only for health checks
- NEVER modify the Premium calendar OAuth dispatcher workflows
  (rGrnCr5mPFP2TIc7, La99yvfmWg6AuvM2, b9xRG7wtqCZ5fdxo, BxnR17qUfAb5BZCz, msEy13eRz66LPxW6)
- NEVER add booking links to Standard or Premium SMS node
- NEVER run the agent simulator in this session — it will timeout
- NEVER modify Railway env vars without explicit Dan instruction
- NEVER touch Stripe
- NEVER skip E2E before promoting to MASTER

---

## Stop Conditions — Pause and report to Dan when:

- Any MASTER agent GET returns non-200
- Retell API returns an unexpected schema on post_call_analysis_data PATCH
- A TESTING flow GET shows the Extract/Code/SMS nodes are missing
  (Dan needs to create them in the UI first — this is a mandatory UI step)
- A test call fires but hvac_call_log shows null in more than 3 call_analysis fields
- E2E suite reports any failure after call processor changes
- Any n8n workflow PUT returns non-200
- 2 consecutive failures on any single step
- Anything would require touching a MASTER agent before E2E is green

---

## Execution Plan

After each step output: ✅ [step name] — [what was confirmed]

### PHASE 0 — Pre-flight

1. Fetch Retell API key from syntharra_vault (service_name='Retell AI', key_type='api_key')
2. GET both MASTER agents — confirm 200 and is_published=true
3. GET both TESTING agents — confirm 200
4. Read FAILURES.md — check for any Retell-area failures not yet in context
5. Manually back up both MASTER agent JSONs:
   - GET agent_4afbfdb3fcb1ba9569353af28d → push to retell-agents/hvac-standard-master-backup-[date].json
   - GET agent_9822f440f5c3a13bc4d283ea90 → push to retell-agents/hvac-premium-master-backup-[date].json
6. ✅ Pre-flight complete — both MASTER agents healthy, backups pushed

### PHASE 1 — Sync TESTING agents to clean MASTER copies

For each TESTING agent, fetch the corresponding MASTER agent config and PATCH the
TESTING agent to match it exactly (name, voice_id, prompt, all settings).
This ensures both TESTING agents are a known-good baseline before changes begin.

PATCH Standard TESTING (agent_731f...) to mirror Standard MASTER config.
Set agent_name = "HVAC Standard (ENHANCEMENT TESTING)"
Publish after PATCH.

PATCH Premium TESTING (agent_2cffe...) to mirror Premium MASTER config.
Set agent_name = "HVAC Premium (ENHANCEMENT TESTING)"
Publish after PATCH.

Update docs/context/AGENTS.md with the new agent names.
✅ Phase 1 complete — TESTING agents synced, named, published

### PHASE 2 — Configure post_call_analysis_data on both TESTING agents

PATCH both TESTING agents with the following post_call_analysis_data array.
Set post_call_analysis_model = "gpt-4.1-mini"
Publish both agents after PATCH.

Fields to configure (apply identically to both agents):

[
  { type: "string",  name: "caller_name",         description: "Full name of the caller as stated during the call.", examples: ["John Smith", "Maria Garcia"], required: false },
  { type: "string",  name: "caller_phone",         description: "Phone number the caller provided for callback. May differ from caller ID.", examples: ["+15551234567", "555-867-5309"], required: false },
  { type: "string",  name: "caller_address",       description: "Full service address including street, city, state.", examples: ["123 Main St, Austin TX"], required: false },
  { type: "string",  name: "service_requested",    description: "The specific HVAC service or problem described.", examples: ["AC not cooling", "furnace won't start", "annual tune-up"], required: false },
  { type: "enum",    name: "job_type",              description: "Category of the job.", choices: ["repair","install","maintenance","quote","emergency","existing_customer","general_inquiry","other"], required: false },
  { type: "enum",    name: "urgency",               description: "How urgently service is needed.", choices: ["emergency","urgent","routine","flexible"], required: false },
  { type: "boolean", name: "is_lead",               description: "True if caller is a potential new customer requesting service.", required: false },
  { type: "number",  name: "lead_score",            description: "Score 1-10. 9-10: emergency. 7-8: repair/install. 5-6: maintenance. 3-4: low intent. 1-2: spam/wrong number.", required: false },
  { type: "enum",    name: "caller_sentiment",      description: "Overall emotional tone of the caller.", choices: ["positive","neutral","frustrated","distressed","angry"], required: false },
  { type: "boolean", name: "transfer_attempted",    description: "True if agent attempted to transfer the call.", required: false },
  { type: "boolean", name: "transfer_success",      description: "True if transfer was successfully connected.", required: false },
  { type: "boolean", name: "vulnerable_occupant",   description: "True if caller mentioned elderly, children, medical equipment, or other vulnerable person affected.", required: false },
  { type: "string",  name: "summary",               description: "2-3 sentence summary: what caller needed, what was captured, what the next step is.", required: false },
  { type: "string",  name: "notes",                 description: "Additional details not captured elsewhere — equipment brand, access notes, preferred callback time.", required: false }
]

Verify: GET each TESTING agent after PATCH and confirm post_call_analysis_data is present
and has 14 entries.
✅ Phase 2 complete — post_call_analysis_data confirmed on both TESTING agents

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
Additionally:
4. Check if +18129944371 has SMS enabled (Claude Code will check this via API)
   If yes: Add an "SMS" node — name it: send_confirmation_sms
   Place it: after validate_phone, before Ending
   SMS type: Static
   Message: "Thanks for calling {{company_name}}. We've got your details and our
   team will be in touch shortly. — {{agent_name}}"
   Destination: caller's number (default)

Tell Claude Code when UI steps are done and which nodes were successfully added.

---

After Dan confirms: verify all nodes exist via GET on each flow.
✅ Phase 3 complete — all UI nodes confirmed present in both flows

### PHASE 4 — Check SMS eligibility

Before Dan adds the SMS node to Premium flow:
GET https://api.retellai.com/get-phone-number/+18129944371
Check sms_enabled field.
If false: log as blocked, skip SMS node, note in TASKS.md. Move on.
If true: confirm to Dan that SMS node can be added.
✅ Phase 4 complete — SMS eligibility confirmed [enabled/blocked]

### PHASE 5 — Simplify n8n call processors

For Standard call processor (Kg576YtPM9yEacKn):
1. GET the workflow via n8n API
2. Identify and remove: OpenAI/GPT HTTP node, JSON parse/flatten nodes
3. In the Supabase INSERT node, update field mapping to read from
   {{ $json.call_analysis.* }} instead of GPT response fields:
   
   call_id           → {{ $json.call_id }}
   agent_id          → {{ $json.agent_id }}
   company_name      → [from Supabase client lookup by agent_id — already in workflow]
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
   geocode_status    → [populated by geocoding node downstream — leave as-is]
   geocode_formatted → [populated by geocoding node downstream — leave as-is]
   
4. Keep untouched: Supabase client lookup, geocoding node, HubSpot note, email node
5. PUT updated workflow — Publish

Repeat for Premium call processor (STQ4Gt3rH8ptlvMi):
Same removals and same field mapping. call_tier = "Premium".
Preserve all Premium-specific nodes (dispatcher trigger, OAuth handling).

Important note on SMS node + dispatcher interaction:
The SMS confirmation node fires AFTER lead data is captured (end of call flow).
The Premium dispatcher (73Y0MHVBu05bIm5p) fires from the post-call webhook when
a booking action was triggered mid-call. These are sequential and independent —
the SMS fires during the call, the dispatcher fires after it ends via webhook.
There is no conflict. Do NOT modify the dispatcher workflow (73Y0MHVBu05bIm5p).

✅ Phase 5 complete — both processors updated, GPT nodes removed, published

### PHASE 6 — Verification test calls

Trigger a test call on Standard TESTING agent (agent_731f...).
Wait for webhook to fire.
Query hvac_call_log for the test record (filter by agent_id = Standard TESTING).
Confirm:
- call_analysis fields are populated (not null) for at least 8 of 14 fields
- duration_seconds populated
- geocode ran on caller_address if address was given
- HubSpot note was logged (check n8n execution log)
- Client email did not fire (TESTING agent has no real client email)

If any field mapping is null across all 14 fields: stop and report — Phase 5 mapping
may have a path error. Do NOT proceed to Premium test call until Standard is confirmed.

Repeat for Premium TESTING agent.

Additional downstream verification after both test calls:

1. Weekly Lead Report (iLPb6ByiytisqUJC) — manually trigger for the test client.
   Confirm it renders correctly with the new field data. Key fields to check:
   is_lead, lead_score, caller_name, service_requested. If report is blank or broken,
   the field format from call_analysis may differ — stop and report.

2. Monthly Minutes Calculator (z1DNTjvTDAkExsX8) — check that duration_seconds is
   correctly populated in hvac_call_log for both test calls. This field drives billing.
   A null or zero value here is a critical failure — stop and report immediately.

3. Weekly Health Score Calculator (ALFSzzp3htAEjwkJ) — no action needed during this
   sprint. Runs weekly. Verify it does not error on next run after go-live by checking
   n8n execution logs the following week.

4. Daily Transcript Analysis (ofoXmXwjW9WwGvL6) — this workflow currently re-analyses
   transcripts from hvac_call_log with Groq for quality issues and jailbreak detection.
   It is NOT being retired in this sprint — it reads the raw transcript field which is
   still present in the Retell webhook payload. Confirm transcript field is still being
   written to hvac_call_log. No changes needed to this workflow.

5. Slack lead notification — both call processors have a pending Slack notification
   to #calls when lead_score ≥ 7. This trigger reads lead_score from the Supabase row.
   Confirm the lead_score field is populated correctly in the test call row. If Slack
   notifications are already wired in at this point, confirm they fire on the test call.

✅ Phase 6 complete — both test calls verified, all downstream workflows confirmed

### PHASE 7 — Re-run E2E tests

Run Standard E2E:
python3 shared/e2e-test.py

Review results. Any failures:
- If failure is a field assertion: update the assertion to match new Retell field format
- If failure is agent behaviour: stop and report — do not patch MASTER
- Re-run until green

Run Premium E2E only after Standard is green:
python3 shared/e2e-test-premium.py

Both must be green before Phase 8.
✅ Phase 7 complete — Standard E2E: [X/X] ✅ | Premium E2E: [X/X] ✅

### PHASE 8 — Promote to MASTER (requires Dan go-ahead)

Stop here. Present Dan with:
- Phase 7 E2E results
- Sample of 3 hvac_call_log rows from test calls showing field quality
- Confirmation that both TESTING agents are working correctly

Wait for explicit Dan approval before continuing.

After Dan approval:
1. PATCH Standard MASTER with post_call_analysis_data (same 14 fields, same model)
   Publish Standard MASTER
2. Dan adds Extract Dynamic Variable + Code nodes to Standard MASTER flow in UI
3. PATCH Premium MASTER with post_call_analysis_data
   Publish Premium MASTER
4. Dan adds Extract Dynamic Variable + Code + SMS nodes to Premium MASTER flow in UI
5. Confirm both MASTER agents publish successfully
6. Confirm n8n processors are already live (they are not agent-specific — already updated)

✅ Phase 8 complete — both MASTER agents updated and published

---

## Session Close (mandatory)

Before ending:
1. Append any new failures/fixes to docs/FAILURES.md
2. Update syntharra-retell-SKILL.md with:
   - post_call_analysis_data pattern and field list
   - Confirmed: Extract/Code/SMS nodes require UI creation (cannot create via API)
   - New field mapping pattern for n8n call processors
3. Update docs/TASKS.md — mark completed phases, note any blocked items
4. Update docs/context/AGENTS.md with final agent names and node info
5. Push session log to docs/session-logs/YYYY-MM-DD-retell-enhancement-sprint.md
6. Confirm all changes pushed to GitHub — never end session with unpushed work

Session log must include mandatory reflection:
1. What did I get wrong or do inefficiently, and why?
2. What assumption did I make that turned out to be incorrect?
3. What would I do differently if this exact task came up again?
4. What pattern emerged that future-me needs to know?
5. What was added to skill files / ARCHITECTURE.md and what was the specific lesson?
6. Did I do anything "because that's how it's done" that I haven't verified?
```
