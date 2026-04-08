# Retell Enhancement Sprint — Claude Code Prompt
> Stored: docs/integration-prompts/retell-enhancement-sprint.md
> Status: LOCKED — do not execute until Premium TESTING agent is promoted to MASTER
> Target tool: Claude Code
> Last updated: 2026-04-04

---

## Context (carry forward — read before acting)

You are the senior autonomous engineer for Syntharra. You are implementing a planned Retell enhancement sprint for both HVAC Standard and HVAC Premium agents.

**What Syntharra is:** AI phone receptionist for trade businesses. Standard ($497/mo) = lead capture only. Premium ($997/mo) = full calendar integration + booking.

**Infrastructure deployed — DO NOT change:**
- n8n: `https://n8n.syntharra.com`
- Supabase: `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- Retell API: `https://api.retellai.com`
- All API keys: Supabase `syntharra_vault` table (service role key required)
- GitHub: `Syntharra/syntharra-automations`

**Load skill files at session start — fetch GitHub token from vault, then:**
```python
def fetch(path):
    r = requests.get(f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{path}",
                     headers={"Authorization": f"token {GITHUB_TOKEN}"}).json()
    return base64.b64decode(r["content"]).decode() if "content" in r else None

claude_md      = fetch("CLAUDE.md")
tasks_md       = fetch("docs/TASKS.md")
failures_md    = fetch("docs/FAILURES.md")
retell_skill   = fetch("skills/syntharra-retell-SKILL.md")
standard_skill = fetch("skills/hvac-standard-SKILL.md")
premium_skill  = fetch("skills/hvac-premium-SKILL.md")
infra_skill    = fetch("skills/syntharra-infrastructure-SKILL.md")
```

**Agent IDs — MASTER (NEVER touch):**
- Standard MASTER: `agent_4afbfdb3fcb1ba9569353af28d`
- Premium MASTER: `agent_9822f440f5c3a13bc4d283ea90`

**Agent IDs — existing TESTING (read-only baseline, do not modify):**
- Standard TESTING: `agent_731f6f4d59b749a0aa11c26929`
- Premium TESTING: `agent_2cffe3d86d7e1990d08bea068f`

**Conversation flows:**
- Standard MASTER: `conversation_flow_34d169608460` (12 nodes)
- Premium MASTER: `conversation_flow_1dd3458b13a7` (18 nodes)
- Standard TESTING: `conversation_flow_5b98b76c8ff4`
- Premium TESTING: `conversation_flow_2ded0ed4f808`

**Standard flow node order:**
greeting → identify_call → [call_style_detector code node] → nonemergency_leadcapture → verify_emergency → callback → existing_customer → general_questions → spam_robocall → Transfer Call → transfer_failed → Ending → End Call

**Call processor workflow IDs:**
- Standard: `Kg576YtPM9yEacKn`
- Premium: `STQ4Gt3rH8ptlvMi`

**Critical Retell rules:**
- NEVER delete or recreate any agent — always patch in place
- ALWAYS publish after any agent update
- Code nodes CANNOT be created via REST API — UI only. Document UI steps for Dan if needed, continue with other phases

---

## Objective

Implement three enhancements across both Standard and Premium flows and call processors. All flow work happens on NEW V2 TESTING agents cloned from MASTER — preserving MASTER and existing TESTING as independent baselines.

---

## Starting State

- Standard MASTER: fully tested (80/80, 75/75, 20/20) — do not touch
- Premium MASTER: promoted from TESTING — do not touch
- Both existing TESTING agents: read-only baselines
- Both call processors: use Groq/GPT to parse transcripts and extract structured fields post-call

---

## Target State

1. Two new agents: `HVAC Standard TESTING-V2` and `HVAC Premium TESTING-V2` — cloned from MASTER, each wired to a new cloned V2 flow
2. Extract Dynamic Variable node in both V2 flows — after lead capture, before Ending — extracts: `caller_name`, `caller_phone`, `caller_address`, `service_requested`, `urgency`, `job_type`
3. Phone validation Code node in both V2 flows — after Extract Dynamic Variable — validates `{{caller_phone}}` is a valid US number, sets `phone_valid` boolean
4. `post_call_analysis_data` on both V2 agents: `is_lead` (boolean), `caller_sentiment` (selector: positive/neutral/negative), `lead_score` (number 1-10), `summary` (text), `service_requested` (text), `urgency` (selector: emergency/urgent/routine), `job_type` (text), `transfer_attempted` (boolean), `transfer_success` (boolean). Model: `gpt-4.1-mini`
5. Standard call processor simplified — GPT node removed — fields mapped from `body.post_call_analysis` in Retell webhook directly to `hvac_call_log`. Geocoding, HubSpot push, email alert untouched
6. Premium call processor simplified — GPT + JSON flattening nodes removed — same direct mapping. Repeat caller detection, dispatcher routing, multi-notification untouched
7. E2E tests updated and passing green before any push
8. All IDs documented, skills updated, session log pushed

---

## Forbidden Actions

- NEVER write to MASTER agents or flows (IDs listed above)
- NEVER write to existing TESTING agents
- NEVER delete any agent, flow, workflow, or Supabase row
- NEVER touch Railway env vars, Stripe, or live client data
- NEVER push without passing E2E tests
- NEVER rewrite files from scratch — fetch current, edit targeted sections only
- NEVER commit raw API tokens to GitHub
- NEVER POST to n8n webhooks for health checks — HEAD only

---

## Stop Conditions — pause and report to Dan

- Any MASTER agent ID appears in a write operation
- Code node creation via API fails — output exact UI steps Dan needs to take, then continue
- E2E tests fail after call processor changes — do not push, report failure with field diff
- Retell clone API returns unexpected response
- 3 consecutive failures on any single step
- Any step requires modifying the `hvac_standard_agent` Supabase schema

---

## Execution Order

### Phase 1 — Clone V2 agents and flows

1. Fetch Retell API key from `syntharra_vault` (service role key required)
2. GET Standard MASTER agent full config
3. POST clone → name: `HVAC Standard TESTING-V2` → record as `STD_V2_AGENT_ID`
4. GET Standard MASTER flow full config
5. POST clone → name: `Standard TESTING-V2` → record as `STD_V2_FLOW_ID`
6. PATCH `STD_V2_AGENT_ID` to use `STD_V2_FLOW_ID`
7. Publish `STD_V2_AGENT_ID`
8. Repeat 2-7 for Premium MASTER → `HVAC Premium TESTING-V2`, `PRM_V2_AGENT_ID`, `PRM_V2_FLOW_ID`
9. ✅ GET both V2 agents — confirm published and wired to correct V2 flows

### Phase 2 — Configure post_call_analysis_data

10. PATCH `STD_V2_AGENT_ID` — add `post_call_analysis_data` array with all 9 fields (listed in Target State), set `post_call_analysis_model: gpt-4.1-mini`
11. PATCH `PRM_V2_AGENT_ID` — same schema
12. Publish both V2 agents
13. ✅ GET both V2 agents — confirm `post_call_analysis_data` present with all 9 fields

### Phase 3 — Extract Dynamic Variable node

14. PATCH `STD_V2_FLOW_ID` — add Extract Dynamic Variable node after `nonemergency_leadcapture`, before `Ending`. Extract: `caller_name`, `caller_phone`, `caller_address`, `service_requested`, `urgency`, `job_type`. If API rejects this node type — document exact UI steps for Dan and skip
15. Repeat for `PRM_V2_FLOW_ID` — same node, same relative position
16. Publish both V2 agents
17. ✅ GET both V2 flows — confirm node present between lead capture and ending

### Phase 4 — Phone validation Code node

18. Attempt to add Code node to `STD_V2_FLOW_ID` via API:
    - Position: after Extract Dynamic Variable, before Ending
    - Logic: strip non-digits from `{{caller_phone}}`, validate length is 10 or 11 digits starting with 1, return `phone_valid` (boolean) and `caller_phone_cleaned` (string)
    - If API rejects — output exact UI instructions (node type, position, JS code to paste, response variable names) and continue
19. Repeat for `PRM_V2_FLOW_ID`
20. ✅ Report: API success or complete UI instructions for Dan

### Phase 5 — Simplify Standard call processor

21. GET `Kg576YtPM9yEacKn` full workflow from n8n API
22. Identify and remove the GPT/Groq transcript analysis node
23. Add Set node after webhook trigger — map fields from `body.post_call_analysis.*` to: `is_lead`, `caller_sentiment`, `lead_score`, `summary`, `service_requested`, `urgency`, `job_type`, `transfer_attempted`, `transfer_success`. Pass through: `agent_id`, `call_id`, `duration_ms`, `transcript`, `recording_url`, `caller_phone_number`
24. Verify downstream nodes (geocoding, Supabase insert, HubSpot push, email alert) receive all expected fields — remap if needed
25. Publish workflow
26. ✅ Workflow published, GPT node absent, field mapping confirmed

### Phase 6 — Simplify Premium call processor

27. GET `STQ4Gt3rH8ptlvMi` full workflow from n8n API
28. Remove GPT node AND JSON flattening node
29. Add same direct field mapping Set node as Phase 5
30. Verify Premium-specific nodes intact: repeat caller check, dispatcher routing, multi-notification
31. Publish workflow
32. ✅ Workflow published, both removed nodes absent, Premium nodes confirmed connected

### Phase 7 — Update and run E2E tests

33. Fetch `shared/e2e-test.py` — update assertions from GPT field paths to `post_call_analysis` paths
34. Run `python3 shared/e2e-test.py` — must be green. Max 3 fix attempts if failing, then stop and report
35. Fetch `shared/e2e-test-premium.py` — same updates
36. Run `python3 shared/e2e-test-premium.py` — must be green
37. ✅ Both E2E suites passing — output pass/fail counts

### Phase 8 — Document and close

38. Update `docs/context/AGENTS.md` — add V2 agent IDs and flow IDs
39. Update `skills/syntharra-retell-SKILL.md` — add post_call_analysis_data pattern and V2 IDs
40. Update `skills/hvac-standard-SKILL.md` — add V2 agent ID and flow ID
41. Update `skills/hvac-premium-SKILL.md` — add V2 agent ID and flow ID
42. Append to `docs/FAILURES.md` — any failures and fixes
43. Append to `docs/ARCHITECTURE.md`:
    - Decision: post_call_analysis_data replaces GPT extraction
    - Why: Retell runs it natively, results delivered in webhook payload, no extra API cost, eliminates JSON flattening bugs, simpler call processors
    - Trade-offs accepted: extraction quality depends on Retell's gpt-4.1-mini — if accuracy drops below 90% in production, revert
    - Revisit if: field accuracy is demonstrably lower than prior Groq extraction
44. Update `docs/TASKS.md` — mark Retell Enhancement Sprint complete
45. Write session log to `docs/session-logs/YYYY-MM-DD-retell-enhancement-sprint.md` — include mandatory 6-point reflection
46. Push ALL files to GitHub
47. ✅ Final summary output:
    - STD_V2_AGENT_ID, STD_V2_FLOW_ID
    - PRM_V2_AGENT_ID, PRM_V2_FLOW_ID
    - Phases completed via API
    - Phases requiring Dan UI action (with exact instructions)
    - E2E pass/fail counts
    - All files pushed

---

## Progress format — output after every phase

```
✅ Phase [N] — [name]
   IDs: [any new agent/flow IDs]
   Files changed: [list]
   Notes: [anything Dan needs to know]
   Next: Phase [N+1]
```
