# Session Log — 2026-04-04 — Retell Enhancement Sprint (Phases 0-4)
> Date: 2026-04-04
> Duration: ~45 min
> Tool: Claude Chat (not Claude Code — laptop unavailable)
> Sprint prompt: docs/prompts/retell-enhancement-prompt.md (v2.4)

---

## What was done

### Phase 0 — Pre-flight ✅
- Verified all 5 agents via Retell API (Standard MASTER v20, Premium MASTER 404 expected, Standard TESTING, Premium TESTING, Demo agents)
- Confirmed Supabase hvac_call_log has 49 columns including disconnection_reason and transcript (added prior session)
- Retrieved Retell API key from syntharra_vault via Supabase MCP

### Phase 1 — Clone Premium DEMO ✅
- Cloned Premium TESTING conversation flow → `conversation_flow_82e70e18fef3` (19 nodes)
  - Required `start_speaker: "agent"` field not documented in prompt — discovered via error
- Created Premium DEMO agent → `agent_80d6270ab39ed3169f997cb035`
  - Voice: retell-Nico, 18 post_call fields inherited from Premium TESTING
  - Wired to new DEMO flow

### Phase 2 — Configure all agent features ✅
Applied to BOTH Standard TESTING + Premium DEMO:
- **2A: Post-call analysis** — Standard: 21 fields, Premium: 26 fields (superset), model: gpt-4.1-mini
- **2B: Guardrails** — 7 output topics + jailbreak input detection
- **2C: Boost keywords** — 47 HVAC terms (brands, components, ratings)
- **2D: Pronunciation dictionary** — 6 terms (HVAC, SEER, Trane, Rheem, Daikin, Lennox)
- **2E: Backchannel + reminders** — backchannel on (0.8 freq), reminder at 15s, max 2
- **2F: Voice tuning** — responsiveness 0.85, speed 1.05, silence 30s, dynamic speed+responsiveness
- **2G: Handbook config** — Premium DEMO now has echo_verification, scope_boundaries, etc. (Standard already had it)
- **2H: Webhook filter** — Premium DEMO now filtered to call_analyzed only (Standard already had it)
- ALL settings verified via GET on both agents

### Phase 3 — Flow nodes (partial) ✅
- **Code node (validate_phone)** — Added to BOTH flows via API ✅
  - Standard TESTING: 15→16 nodes
  - Premium DEMO: 19→20 nodes
  - JS: strips non-digits, validates US format, returns phone_normalized/phone_valid/phone_flag
- **Extract Dynamic Variable node** — Cannot be created via API ❌ (UI-only node type)
  - Dan must add manually in Retell dashboard (instructions below)

### Phase 4A — Phone number config ✅
- +18129944371 pinned to Standard MASTER v20 (was v10)
- Nickname: "HVAC Standard Line"
- Fallback number: +18563630633 (transfer destination)

---

## New IDs created this session

| Item | ID |
|---|---|
| Premium DEMO agent | `agent_80d6270ab39ed3169f997cb035` |
| Premium DEMO flow | `conversation_flow_82e70e18fef3` |

---

## Dan UI tasks (Phase 3 + Phase 4B)

### Extract Dynamic Variable nodes (~5 min)
**Standard TESTING flow** (`conversation_flow_5b98b76c8ff4`):
1. Open flow in Retell dashboard
2. Add "Extract Dynamic Variable" node — name: `extract_lead_data`
3. Place: `nonemergency_leadcapture` → `extract_lead_data` → `validate_phone` → `Ending`
4. Variables: caller_name, caller_phone, caller_address, service_requested

**Premium DEMO flow** (`conversation_flow_82e70e18fef3`):
Same — add `extract_lead_data` before `validate_phone` → `Ending`

### Alerting rules (Phase 4B — dashboard only)
Create 5 alerting rules in Retell Settings > Alerting:
1. Call Volume Spike: Call Count > 200% vs previous, 1hr window, 5min freq → alerts@syntharra.com
2. Transfer Failures: Transfer Failure Count > 3, 1hr, 5min → alerts@syntharra.com
3. Daily Cost Cap: Total Call Cost > $50, 24hr, 1hr → alerts@syntharra.com
4. Negative Sentiment: Negative Rate > 30%, 12hr, 1hr → alerts@syntharra.com
5. API Errors: Error Count > 5, 1hr, 5min → alerts@syntharra.com

### Analytics charts (Phase 4B — dashboard only)
Create 5 charts in Retell Analytics tab:
1. Lead Score Distribution (donut)
2. Daily Call Volume (line)
3. Urgency Breakdown (donut)
4. Caller Sentiment Trend (line)
5. Is Hot Lead Rate (number)

---

## What's left — Phase 5-8

### Phase 5 — Simplify n8n call processors (NEXT SESSION)
Standard processor (`Kg576YtPM9yEacKn`) loaded and inspected:
- 14 nodes total
- GPT chain to remove: `Build Groq Request` → `Groq: Analyze Transcript` → `Parse Lead Data`
- Replace with Set node mapping Retell webhook `call_analysis.custom_analysis_data.*` fields
- Keep: webhook, filter, Extract Call Data, client lookup, repeat caller check, Supabase insert, HubSpot, Slack
- Field mapping spec is fully documented in the enhancement prompt (Phase 5 section)

Premium processor (`STQ4Gt3rH8ptlvMi`) — same treatment, plus Premium-specific fields.

### Phase 6 — Test calls on both agents
### Phase 7 — Update E2E test assertions + run green
### Phase 8 — MASTER promotion (requires Dan approval)

---

## Discoveries & lessons

1. **Retell create-conversation-flow requires `start_speaker`** — not in GET response docs, discovered via 400 error. Must include `start_speaker: "agent"` when cloning flows.
2. **Code nodes CAN be created via API** — contrary to what the prompt assumed. The key is matching the exact schema: `else_edge` must be an object (not null), with `destination_node_id`, `id`, and `transition_condition`.
3. **Extract Dynamic Variable nodes CANNOT be created via API** — confirmed. UI-only.
4. **Retell list-agents returns versions, not unique agents** — 94 results for 5 unique agents. Each version appears as a separate entry.
5. **Phone number `fallback_number` works via API** — `fallback_destination` also accepted but `fallback_number` is the field that persists in GET.
6. **Premium MASTER 404 is expected** — agent exists but has never been published. Not a bug.

## Mandatory reflection

1. **What did I get wrong?** Initially assumed both Code and Extract Dynamic Variable nodes were UI-only per the prompt. Tested both — Code works via API, Extract doesn't. Always test assumptions.
2. **What assumption was incorrect?** The flow clone would work with just `nodes` and `edges`. Retell requires `start_speaker` which isn't obvious from the GET response structure.
3. **What would I do differently?** For any Retell create/clone operation, always GET a working example first and include ALL top-level fields (not just nodes/edges) in the POST.
4. **Pattern for future-me:** Retell's create endpoints require more fields than documented. Always dump the full GET response, identify all non-readonly fields, and include them all in the POST.
5. **What was added to skills/architecture?** Will update retell skill with: flow clone requires start_speaker, code nodes work via API (else_edge must be object), extract_variable is UI-only. Architecture update: post_call_analysis replaces GPT (pending Phase 5 completion).
6. **Did I do anything unverified?** No — every PATCH was followed by a GET to verify.
