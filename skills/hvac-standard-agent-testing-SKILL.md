---
name: hvac-standard-agent-testing
description: >
  Complete reference for testing the HVAC Standard AI receptionist agent.
  Covers: agentic test engine, scenario simulator, promoting TESTING to MASTER,
  scenario coverage, and Groq budget management.
  Load when: running agent tests, diagnosing simulator failures, fixing agent prompt issues,
  promoting TESTING to MASTER, adding new test scenarios, or debugging agent behaviour.
  Current: 91 Standard-compatible scenarios across 6 groups. Subagent component architecture.
---

# HVAC Standard Agent Testing

> Load when: running tests, diagnosing failures, fixing prompts, promoting TESTING → MASTER
> Agent: Standard TESTING `agent_731f6f4d59b749a0aa11c26929`
> Flow: `conversation_flow_5b98b76c8ff4`

---

## Quick Reference

| Item | Value |
|---|---|
| TESTING agent | `agent_731f6f4d59b749a0aa11c26929` |
| TESTING flow | `conversation_flow_5b98b76c8ff4` |
| MASTER agent | `agent_4afbfdb3fcb1ba9569353af28d` |
| MASTER flow | `conversation_flow_34d169608460` |
| Agentic engine | `tools/agentic-test-fix.py` |
| Simulator script | `tools/openai-agent-simulator.py` |
| Scenarios file | `tests/agent-test-scenarios.json` |
| Results dir | `tests/results/` |
| Model | `meta-llama/llama-4-scout-17b-16e-instruct` |
| Groq cost | $0.00 (free tier) |
| Scenarios | 91 Standard-compatible (108 total, 17 premium-only excluded) |

---

## Testing Tools

### 1. Agentic Test Engine (PRIMARY — use this)

Full pipeline: run all scenarios → triage failures → classify as BAD_SCENARIO / PROMPT_GAP / VARIANCE.

```bash
# Full run — test only, no fixes
python3 tools/agentic-test-fix.py --key gsk_... --agent standard --dry-run

# Specific group
python3 tools/agentic-test-fix.py --key gsk_... --agent standard --group core_flow --dry-run

# With auto-fix (future — when fix loop is enabled)
python3 tools/agentic-test-fix.py --key gsk_... --agent standard --max-fix-iterations 3
```

### 2. Scenario Simulator (LEGACY — still works)

Simple pass/fail per scenario without triage.

```bash
RETELL_KEY=key_... GITHUB_TOKEN=ghp_... python3 tools/openai-agent-simulator.py \
  --key gsk_... --group core_flow
```

---

## Groq Free Tier Budget

| Metric | Value |
|---|---|
| Model | llama-4-scout-17b-16e-instruct |
| Rate limit | 30 req/min, 14,400 req/day |
| TPM limit | 30,000 tokens/min |
| Per scenario | ~17 API calls, ~9,000 tokens |
| Standard full run | ~1,547 calls (10.7% of daily limit) |
| Runtime | ~55-70 min with rate limit gaps |

**RULES:**
- ALWAYS use llama-4-scout-17b (30k TPM). Do NOT use llama-3.3-70b (6k TPM is too slow).
- Never run Standard + Premium back-to-back without checking daily quota (~23% combined).
- If rate limited, the engine handles backoff automatically (5s → 10s → 20s → 30s).
- Groq key from vault: `service_name='Groq', key_type='api_key'`

---

## Scenario Coverage (91 scenarios)

| Group | Count | Coverage |
|---|---|---|
| core_flow | 16 | Greeting, emergency, FAQ, spam, callback, existing customer, wrong number, lead capture |
| personalities | 15 | Elderly, angry, chatty, non-native, suspicious, distracted, brief, technical, proxy, changing mind |
| info_collection | 15 | PO box, complex email, refusals, corrections, apartments, rural, commercial, out-of-order |
| pricing_traps | 9 | Direct price, comparison, hourly, service fee, refrigerant, new unit, maintenance, competitor quote |
| edge_cases | 22 | Vendor, job applicant, cancel, referral, emergency refusal, child, DIY, hold, voicemail, Spanish, multi-issue |
| boundary_safety | 14 | Abuse, diagnosis demand, medical, data request, threats, social engineering, CO, gas, false records |

### New scenarios added 2026-04-05 (#96-108):
- Spanish-speaking caller, emergency fallback, transfer failure recovery
- FAQ→booking transition, after-hours, voicemail detection
- Multiple emergencies combo, language switch mid-call, stress test
- Competitor price comparison

---

## Flow Architecture (20 nodes, subagent components)

Standard flow uses shared component library. 14 of 20 nodes are subagent type.
Component updates propagate to all agents automatically.

Key routing from `identify_call_node` (10 edges):
1. Transfer Call — live person request
2. call_style_detector → leadcapture — service/repair/booking
3. verify_emergency — emergency keywords
4. callback — returning missed call
5. existing_customer — existing job/appointment question
6. general_questions — FAQ only
7. spam_robocall — automated/spam
8. spanish_routing — Spanish language detected
9. emergency_fallback — emergency + transfer unavailable
10. Ending — wrong number

---

## Triage Classification

When the agentic engine finds failures, it classifies each:

| Type | Meaning | Fix action |
|---|---|---|
| BAD_SCENARIO | Test expectation is unrealistic | Rewrite `expectedBehaviour` in scenario JSON |
| PROMPT_GAP | Agent genuinely mishandled the call | Add line to component instruction (NOT global prompt) |
| VARIANCE | LLM randomness, passes on retry | Mark as flaky, add retry tolerance |

**Fix priority:** scenario fix > edge description > component instruction > finetune example.
**NEVER grow the global prompt.** All fixes go to components.

---

## Promoting TESTING → MASTER

Only after the agentic suite passes at target rate (85%+):

```python
import requests
RH = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
MASTER_FLOW  = "conversation_flow_34d169608460"
MASTER_AGENT = "agent_4afbfdb3fcb1ba9569353af28d"
TESTING_FLOW = "conversation_flow_5b98b76c8ff4"

testing = requests.get(f"https://api.retellai.com/get-conversation-flow/{TESTING_FLOW}", headers=RH).json()
requests.patch(f"https://api.retellai.com/update-conversation-flow/{MASTER_FLOW}", headers=RH, json={
    "nodes": testing["nodes"],
    "edges": testing.get("edges", []),
    "global_prompt": testing["global_prompt"],
    "start_node_id": testing.get("start_node_id")
})
requests.post(f"https://api.retellai.com/publish-agent/{MASTER_AGENT}", headers=RH)
```

---

## Adding New Scenarios

1. Edit `tests/agent-test-scenarios.json`
2. Add scenario with next available ID (currently max=108)
3. Required fields: `id, group, name, callerPrompt, expectedBehaviour`
4. Optional: `premiumOnly: true` (excluded from Standard runs)
5. Run agentic engine on the new scenario's group to verify
6. Push to GitHub

## Gotchas & Verified Patterns

### COMPONENT_MAX_CHARS must be ≥ component size + buffer
- `COMPONENT_MAX_CHARS = 2500` in `tools/agentic-test-fix.py`
- Was 1200 — silently skipped all patches for #043 (identify_call node ~2200 chars)
- Root cause: patch generator produces correct fix but constant blocks it silently
- Fix confirmed on GitHub SHA e123a51f, 2026-04-06

### Groq qwen/qwen3-32b TPD limit (500k tokens/day)
- Standard full 3-iteration run consumes ~499k tokens
- **Do NOT run Standard + Premium on the same calendar day** — Premium will be rate-limited from the start
- Retry waits follow sliding 24h window: 116s → 352s → 451s+ as budget exhausts
- Plan: run Standard one day, Premium the next

### Desktop Commander Python output capture
- `start_process` does NOT capture Python stdout inline
- Must use: `Start-Process -FilePath python.exe -ArgumentList ... -RedirectStandardOutput out.txt -Wait -NoNewWindow`
- Then read the output file with `Get-Content`

### Scenario #043 persistent failure
- "Commercial property facilities manager" — fails due to COMPONENT_MAX_CHARS cap blocking the fix
- With COMPONENT_MAX_CHARS=2500 the fix will apply on next run
- Score without #043 fix: 90/91 (98%) — still well above gate

### Spanish routing node removal
- `spanish_routing_node` scheduled for removal from the flow
- Don't flag failures on Spanish routing scenarios as blocking
- promote.py STUB_THRESHOLD logic handles removal automatically (won't try to restore a missing node)

## Promotion History
| Date | Score | Gate | Result |
|---|---|---|---|
| 2026-04-06 | 90/91 (98%) | ≥85/91 | ✅ PROMOTED — flow v22 |
