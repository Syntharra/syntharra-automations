---
name: hvac-premium-agent-testing
description: >
  Complete reference for testing the HVAC Premium AI receptionist agent.
  Covers: agentic test engine, scenario simulator, promoting TESTING to MASTER,
  Premium-specific scenarios (booking, rescheduling, cancellation, tool calls),
  and Groq budget management.
  Load when: running Premium agent tests, diagnosing Premium simulator failures,
  fixing Premium agent prompt issues, testing booking/calendar tool calls,
  promoting Premium TESTING to MASTER, or any task involving Premium agent behaviour.
  Current: 108 scenarios (91 shared + 17 premium-specific) across 7 groups.
---

# HVAC Premium Agent Testing

> Load when: running Premium tests, diagnosing failures, fixing prompts, testing booking tools
> Agent: Premium TESTING `agent_2cffe3d86d7e1990d08bea068f`
> Flow: `conversation_flow_2ded0ed4f808`

---

## Quick Reference

| Item | Value |
|---|---|
| TESTING agent | `agent_2cffe3d86d7e1990d08bea068f` |
| TESTING flow | `conversation_flow_2ded0ed4f808` |
| MASTER agent | `agent_9822f440f5c3a13bc4d283ea90` |
| Agentic engine | `tools/agentic-test-fix.py` |
| Simulator script | `tools/openai-agent-simulator-premium.py` |
| Scenarios file | `tests/agent-test-scenarios.json` |
| Results dir | `tests/results/` |
| Model | `meta-llama/llama-4-scout-17b-16e-instruct` |
| Groq cost | $0.00 (free tier) |
| Scenarios | 108 total (91 shared + 17 premium-specific) |

---

## Testing Tools

### 1. Agentic Test Engine (PRIMARY)

```bash
# Full run — test only
python3 tools/agentic-test-fix.py --key gsk_... --agent premium --dry-run

# Premium-specific scenarios only
python3 tools/agentic-test-fix.py --key gsk_... --agent premium --group premium_specific --dry-run

# With auto-fix
python3 tools/agentic-test-fix.py --key gsk_... --agent premium --max-fix-iterations 3
```

### 2. Scenario Simulator (LEGACY)

```bash
RETELL_KEY=key_... GITHUB_TOKEN=ghp_... python3 tools/openai-agent-simulator-premium.py \
  --key gsk_... --group premium_specific
```

---

## Groq Free Tier Budget

| Metric | Value |
|---|---|
| Model | llama-4-scout-17b-16e-instruct |
| Rate limit | 30 req/min, 14,400 req/day |
| TPM limit | 30,000 tokens/min |
| Per scenario | ~17 API calls, ~12,000 tokens (larger prompt) |
| Premium full run | ~1,836 calls (12.8% of daily limit) |
| Combined (both agents) | ~3,383 calls (23.5% of daily limit) |
| Runtime | ~55-70 min with rate limit gaps |

**RULES:**
- ALWAYS use llama-4-scout-17b (30k TPM). Premium prompt is ~27k chars — needs high TPM.
- Do NOT use llama-3.3-70b for Premium — 6k TPM is exhausted by the full prompt on scenario #1.
- If running both agents same day, run Standard first (smaller), then Premium.
- Groq key from vault: `service_name='Groq', key_type='api_key'`

---

## Scenario Coverage (108 scenarios)

| Group | Count | Notes |
|---|---|---|
| core_flow | 16 | All Standard paths + FAQ→booking transition |
| personalities | 15 | Same as Standard — tests how Premium handles diverse callers |
| info_collection | 15 | Same as Standard — lead capture applies to Premium too |
| pricing_traps | 9 | Same as Standard + competitor quote comparison |
| edge_cases | 22 | Extended: Spanish routing, voicemail, multi-issue, transfer recovery |
| boundary_safety | 14 | Extended: gas emergency fallback, multiple emergency signals |
| premium_specific | 17 | Booking, rescheduling, cancellation, tool failures, calendar full, priority status |

### Premium-Specific Scenarios (#81-95, #101-102):
- #81: Appointment booking (full booking flow)
- #82: Repeat caller recognition
- #83: Dispatcher routing
- #84: Multi-notification recipients
- #85: Jobber service history
- #86: Calendar fully booked (fallback to lead capture)
- #87: Emergency after-hours
- #88: Rescheduling appointment
- #89: Service history inquiry
- #90: Large quote request
- #91: Plan upgrade inquiry
- #92: Priority status assertion
- #93: Notification preference change
- #94: Multiple units at commercial property
- #95: Compliment and referral inquiry
- #101: Cancel appointment (dedicated cancel flow)
- #102: Booking system unavailable (tool failure → fallback)

---

## Premium Flow Architecture (26 nodes)

Premium has 6 additional nodes vs Standard:
- `booking_capture_node` — collect booking details
- `check_availability_node` — tool call to check calendar
- `confirm_booking_node` — confirm and create booking
- `reschedule_node` — change existing appointment
- `cancel_appointment_node` — cancel existing appointment
- `Emergency Transfer` — separate transfer node for emergencies

### Premium Tool Calls (4 tools, all via n8n dispatch)

| Tool | Required params | Optional |
|---|---|---|
| check_availability | action, date, time_window | — |
| create_booking | action, date, time_window, caller_name, caller_phone, caller_address, job_type | caller_email, notes, urgency |
| reschedule_booking | action, new_date, new_time_window, caller_name, original_date | caller_phone |
| cancel_booking | action, caller_name, appointment_date | — |

All tools POST to: `https://n8n.syntharra.com/webhook/retell-integration-dispatch`

### Key routing from identify_call_node (12 edges):
All Standard edges PLUS:
- booking_capture (via call_style_detector) — new service requests
- reschedule — change appointment
- cancel_appointment — cancel appointment

---

## Triage Classification

Same as Standard — failures classified as BAD_SCENARIO / PROMPT_GAP / VARIANCE.

**Premium-specific triage notes:**
- Booking tool failures may show as PROMPT_GAP even if the agent handled it correctly (tool isn't wired yet)
- Calendar-related scenarios depend on tool responses — if dispatch webhook isn't built yet, expect failures in booking flow
- Until `retell-integration-dispatch` is live, booking scenarios should be marked as known failures

---

## Promoting TESTING → MASTER

Only after agentic suite passes at target rate (90%+):

```python
import requests
RH = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
MASTER_AGENT = "agent_9822f440f5c3a13bc4d283ea90"
TESTING_FLOW = "conversation_flow_2ded0ed4f808"

testing = requests.get(f"https://api.retellai.com/get-conversation-flow/{TESTING_FLOW}", headers=RH).json()
# Get MASTER flow ID from MASTER agent
master = requests.get(f"https://api.retellai.com/get-agent/{MASTER_AGENT}", headers=RH).json()
master_flow = master.get("conversation_flow_id")

requests.patch(f"https://api.retellai.com/update-conversation-flow/{master_flow}", headers=RH, json={
    "nodes": testing["nodes"],
    "edges": testing.get("edges", []),
    "global_prompt": testing["global_prompt"],
    "start_node_id": testing.get("start_node_id")
})
requests.post(f"https://api.retellai.com/publish-agent/{MASTER_AGENT}", headers=RH)
```

---

## Simulator Model Requirement

Premium prompt is significantly larger (~27k chars vs ~17k for Standard) due to:
- 26 nodes vs 20 (6 extra booking/calendar nodes)
- 4 tool call schemas embedded in prompt
- Richer global prompt with booking rules

This means:
- `llama-3.3-70b-versatile` CANNOT run Premium (12k context exhausted by prompt alone)
- `llama-4-scout-17b-16e-instruct` MUST be used (30k TPM handles the full prompt)
- If a new model is needed, verify it supports 30k+ tokens per minute
