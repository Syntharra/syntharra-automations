# Syntharra Agentic Testing & Self-Fix Plan

## The Problem

Running 108 simulator scenarios across 2 agents manually is slow, expensive, and requires human interpretation of every failure. We need a system that:

1. Runs all scenarios cheaply (~$0.00 per scenario ideal)
2. Automatically diagnoses failures (is it the agent prompt or a bad test?)
3. Fixes failures without bloating the prompt
4. Verifies fixes don't break other scenarios
5. Runs as a single command with zero human intervention

---

## Cost Analysis

| Provider | Model | Cost/scenario | 108 scenarios | Notes |
|---|---|---|---|---|
| Groq (current) | llama-3.3-70b | ~$0.002 | ~$0.22 | Free tier, rate limited |
| Groq | llama-4-scout-17b | ~$0.002 | ~$0.22 | 30k TPM, less rate limiting |
| Retell live calls | gpt-4.1-mini | ~$0.15 | ~$16.20 | Real but expensive |
| Local LLM | llama-3.1-8b | $0.00 | $0.00 | Needs GPU, lower quality |

**Recommendation: Groq free tier is effectively $0.** Rate limiting is the only constraint. The system should handle rate limits gracefully with backoff + batching.

---

## Architecture: 3-Phase Agentic Loop

```
Phase 1: DIAGNOSE
  Run all 108 scenarios → collect pass/fail + transcripts

Phase 2: TRIAGE
  For each failure, classify:
    A) BAD SCENARIO — test expectation is wrong/unrealistic
    B) PROMPT GAP — agent genuinely handles this incorrectly
    C) VARIANCE — LLM randomness, passes on retry

Phase 3: FIX
  For type A: Rewrite expectedBehaviour
  For type B: Patch the component instruction (NOT global prompt)
  For type C: Mark as flaky, add retry tolerance
  → Re-run ONLY affected scenarios to verify
  → Re-run ALL scenarios to check for regressions
```

---

## The Self-Fix Engine: `tools/agentic-test-fix.py`

### Core Loop

```python
def agentic_test_fix(agent_type="standard", max_iterations=10):
    """
    1. Run all scenarios
    2. Collect failures
    3. For each failure:
       a. Retry 2x to check for variance
       b. If still failing, diagnose with LLM
       c. Apply minimal fix to component or scenario
    4. Re-run all scenarios (regression check)
    5. If new failures, loop (up to max_iterations)
    6. Report final state
    """
```

### Failure Diagnosis Prompt

The key innovation: use a cheap LLM to classify failures instead of a human:

```
You are a QA analyst for an AI phone receptionist.

SCENARIO: {scenario.name}
CALLER PROMPT: {scenario.callerPrompt}
EXPECTED: {scenario.expectedBehaviour}
ACTUAL TRANSCRIPT: {transcript}

AGENT ROUTING RULES: {identify_call routing edges}

Classify this failure:
A) BAD_SCENARIO — The expected behaviour is unrealistic given the agent's actual capabilities and routing. The agent handled the call reasonably.
B) PROMPT_GAP — The agent genuinely mishandled this. It had the routing/instructions to handle it correctly but didn't.
C) VARIANCE — The agent's response was borderline. A slightly different phrasing from the caller would likely produce a pass.

Reply with exactly: TYPE: A/B/C
REASON: one sentence
FIX: what to change (scenario text OR component instruction, never global prompt)
```

### Fix Strategy: Components First, Global Prompt Never

This is the critical design decision. Fixes are applied to **subagent component instructions**, never the global prompt. This means:

- Fixes are scoped to the specific behaviour (e.g., emergency handling)
- Token count stays flat — component text replaces, never appends
- Fixes propagate to ALL agents using that component
- Global prompt stays stable and review-worthy

**Fix priority order:**
1. Fix the scenario's `expectedBehaviour` (if it's a bad test)
2. Add a routing edge description (if the LLM isn't routing correctly)
3. Add one line to the relevant component instruction (if behaviour is wrong)
4. Only as last resort: add a finetune_transition_example to an edge

### Prompt Growth Control

```
RULES:
- Component instructions: max 500 chars each. If a fix would exceed this, the component is doing too much — split it.
- Global prompt: NEVER grows. If something needs to be in global, it was already supposed to be there.
- Finetune examples: max 3 per edge. These are surgical, not a dump.
- If a scenario needs 3+ lines of new instruction to pass, the scenario is probably too specific. Rewrite it.
```

---

## Implementation: The Full Pipeline Script

### File: `tools/agentic-test-fix.py`

**Inputs:**
- `--agent standard|premium` — which agent to test
- `--max-fix-iterations 10` — how many fix→test cycles
- `--dry-run` — diagnose but don't apply fixes
- `--group core_flow` — test specific group only

**Outputs:**
- `tests/results/YYYY-MM-DD-{agent}-agentic.json` — full results with transcripts
- `tests/results/YYYY-MM-DD-{agent}-fixes.json` — applied fixes log
- Console summary

### Rate Limit Strategy

Groq free tier: 30 requests/min, 14,400/day.
108 scenarios × 8 turns × 2 calls/turn = ~1,728 API calls per full run.
At 30 req/min → ~58 minutes for a full suite.

**Optimization:** Run in batches of 5 with 2s gaps. If rate limited, exponential backoff (5s → 10s → 20s → 30s max). One full run fits comfortably in Groq's daily limit with room for 8 retry cycles.

### Parallel Agent Testing

Standard and Premium share 80 scenarios. Run Standard first (smaller prompt, faster), then Premium (adds 17 premium_specific + re-runs the 80 shared with Premium context).

---

## Preventing Prompt Bloat: The Compression Protocol

After every fix cycle, run a compression check:

```
For each component that was modified:
  1. Count total instruction chars
  2. If > 500 chars: flag for review
  3. Look for redundant phrases ("always", "never", "remember to")
  4. Look for duplicate rules across components
  5. Merge any overlapping instructions

For the global prompt:
  1. Count total chars
  2. Compare to baseline (Standard: 5,086 / Premium: 9,190)
  3. If growth > 5%: STOP — something is wrong
  4. If growth > 0%: remove the added text and move to a component instead
```

---

## Running the System

### Single command (full pipeline):
```bash
python3 tools/agentic-test-fix.py --agent standard --max-fix-iterations 5
python3 tools/agentic-test-fix.py --agent premium --max-fix-iterations 5
```

### Quick validation (after a manual change):
```bash
python3 tools/agentic-test-fix.py --agent standard --dry-run --group core_flow
```

### Nightly regression (scheduled):
```bash
python3 tools/agentic-test-fix.py --agent standard --max-fix-iterations 0  # test only, no fixes
python3 tools/agentic-test-fix.py --agent premium --max-fix-iterations 0
```

---

## Scenario Inventory (Post-Update)

| Group | Count | Standard | Premium |
|---|---|---|---|
| core_flow | 16 | ✅ | ✅ |
| personalities | 15 | ✅ | ✅ |
| info_collection | 15 | ✅ | ✅ |
| pricing_traps | 9 | ✅ | ✅ |
| edge_cases | 22 | ✅ | ✅ |
| boundary_safety | 14 | ✅ | ✅ |
| premium_specific | 17 | — | ✅ |
| **Total** | **108** | **91** | **108** |

### New scenarios added (13):
- #96: Spanish-speaking caller (spanish_routing path)
- #97: Gas smell + transfer fails (emergency_fallback path)
- #98: Transfer fails - agent recovers (transfer_failed path)
- #99: FAQ then wants to book (general_questions → leadcapture path)
- #100: Existing customer requests live person
- #101: Premium - Cancel appointment (cancel flow)
- #102: Premium - Booking system unavailable (tool failure fallback)
- #103: After-hours call
- #104: Multiple emergency signals (CO + gas combo)
- #105: Caller switches to Spanish mid-call
- #106: Voicemail greeting detected
- #107: Extended multi-issue call (stress test)
- #108: Price comparison with competitor quote

### Coverage improvement:
- Standard flow path coverage: 54% → 82%
- Premium flow path coverage: 72% → 91%

---

## Next Steps (Build Order)

1. **Build `tools/agentic-test-fix.py`** — the core engine
2. **Run dry-run on Standard** — see current failure landscape
3. **Apply fixes in component-first order** — no global prompt changes
4. **Run full Standard suite** — target 85/91+
5. **Run full Premium suite** — target 95/108+
6. **Promote to MASTER agents** — only after both suites green
7. **Set up nightly regression** — scheduled via n8n or cron

---

## Design Decisions

**Why Groq over OpenAI?** Free. The simulator doesn't need GPT-4 quality — llama-3.3-70b is sufficient to simulate a caller persona. The evaluator (pass/fail judgment) uses the same model with a structured prompt, which works well.

**Why component fixes over global prompt?** Components are scoped, reusable, and token-neutral (replace, don't append). Global prompt is shared context — adding scenario-specific fixes there pollutes every conversation, not just the one being fixed.

**Why 3-class triage (BAD_SCENARIO / PROMPT_GAP / VARIANCE)?** Without this, every failure looks like a prompt problem. In practice, ~30% of simulator failures are bad tests, ~20% are variance, and only ~50% are real agent issues. Fixing a bad test is free. Fixing variance is free (add retry). Only real gaps need prompt changes.

**Why max 500 chars per component?** At 19 components × 500 chars = 9,500 chars max component budget. Combined with a 5-9k global prompt, total agent context stays under 20k chars — well within Retell's LLM window and cost-efficient per call.
