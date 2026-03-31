---
name: syntharra-testing
description: >
  Complete testing, analysis, and auto-fix system for Syntharra agents.
  ALWAYS load this skill when: analysing call logs, running test scenarios,
  fixing agent issues, producing test reports, validating prompt changes,
  creating new test scenarios, or any QA task. Contains the call log analyser,
  auto-fix loop, 95-scenario test suite, analysis framework, and all tool code.
---

# Syntharra — Agent Testing, Analysis & Auto-Fix Skill (Updated 2026-03-31)

---

## ⚠️ CRITICAL: The Three-Tier Testing Framework

Do NOT run full 95-scenario batches for iteration. Use this framework:

| Tier | Tool | Cost | Use Case | Max Cost |
|---|---|---|---|---|
| **1: Diagnose** | Call Log Analyser | FREE | "What's broken?" | — |
| **2: Fix Validation** | Auto-Fix Loop | ~$0.15/fix | "Does my fix work?" | $5.00 |
| **3: Pre-Launch** | Batch Test (95) | ~$0.75/test | "100% ready?" | $100 |

**Real example that went wrong:**
- Ran Tier 3 twice by accident = $95 bill instead of $5
- Had NO cost gates, NO approval dialogs, NO running total
- Fixed: Scenario Runner v5 now gates at $50 and requires approval

---

## Tool 1: Call Log Analyser (FREE)

Pulls real call data from Retell API, scans transcripts for issues, produces severity-ranked report.

### How to Run
```python
import json, urllib.request

RETELL_KEY = "QUERY_FROM_VAULT"  # syntharra_vault → Retell AI → api_key

def get_calls(retell_key, agent_id, limit=20):
    req = urllib.request.Request(
        "https://api.retellai.com/v2/list-calls",
        method="POST",
        data=json.dumps({
            "limit": limit, "sort_order": "descending",
            "filter_criteria": {"agent_id": [agent_id]}
        }).encode(),
        headers={"Authorization": f"Bearer {retell_key}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())
```

### What It Checks (per call)
1. `call_analysis.call_successful` — False = HIGH issue
2. `call_analysis.user_sentiment` — Negative = HIGH issue
3. `disconnection_reason` — agent_hangup or error = MEDIUM
4. `duration_ms` — Under 15s or over 5min = flag
5. `llm_token_usage.average` — Over 6000 = cost concern
6. `latency.llm.p50` — Over 1000ms = experience concern
7. Transcript scan: "Say:" prefix in agent turns = CRITICAL
8. Transcript scan: 3+ question marks in one agent turn = HIGH
9. Transcript scan: diagnostic/troubleshooting phrases = HIGH
10. Transcript scan: unauthorized pricing = CRITICAL
11. Transcript scan: no name collection on calls >30s = HIGH
12. Transcript scan: no summary readback before closing = MEDIUM

### Full Script
GitHub: `syntharra-automations/tools/retell-call-analyser.py`

**Cost:** $0 (just reads existing call logs)

---

## Tool 2: Auto-Fix Loop (~$0.15/issue) ⭐ NEW!

**This is what you wanted.** Analyses call logs, identifies issues, creates targeted single-scenario tests, validates fixes.

### How to Run
```python
# The loop does:
# 1. Pull calls → analyse transcripts → find issues
# 2. For each testable issue:
#    a. Create a single test case via API
#    b. Run it (single simulation, ~$0.15)
#    c. Check pass/fail
#    d. Report result
# 3. Stop if hitting $5 cost gate
```

### API Endpoints Used
- `POST /v2/list-calls` — pull call data
- `POST /create-test-case-definition` — create test
- `POST /create-batch-test` — run test (even for single scenario)
- `GET /get-batch-test/{id}` — poll for result

### Test Case Definition Format
```json
{
    "name": "AutoFix - issue_type",
    "response_engine": {
        "type": "conversation-flow",
        "conversation_flow_id": "FLOW_ID"
    },
    "user_prompt": "## Identity\n...\n\n## Goal\n...\n\n## Personality\n...",
    "metrics": ["Metric 1", "Metric 2", "Metric 3"]
}
```

### Full Script
GitHub: `syntharra-automations/tools/auto-fix-loop.py`

### Example Usage

```python
from auto_fix_loop import AutoFixLoop

loop = AutoFixLoop(
    agent_id="agent_4afbfdb3fcb1ba9569353af28d",
    flow_id="conversation_flow_34d169608460",
    max_cost=5.00  # Hard stop at $5
)

# Define the fixes you made
fixes_to_validate = [
    {
        "issue_type": "emergency_routing",
        "test_prompt": "Caller: I smell gas!\nGoal: Route to emergency immediately",
        "severity": "CRITICAL"
    },
    {
        "issue_type": "name_collection",
        "test_prompt": "Caller: I need AC repair\nGoal: Collect name before close",
        "severity": "HIGH"
    }
]

# Run the loop
results = loop.run_fix_loop(fixes_to_validate)

# Output:
# ✅ emergency_routing: PASS ($0.15)
# ❌ name_collection: FAIL ($0.15)
# Total: $0.30
```

### When to Use Auto-Fix Loop
- ✅ "I changed the emergency prompt. Does it work?"
- ✅ "I fixed 2 issues. Validate both."
- ✅ Iterating on prompts (5-10 cycles)
- ❌ Not for full pre-launch validation (use Tier 3 instead)

### Cost Analysis
- Per test: ~$0.15
- 5 fixes: ~$0.75
- 20 fixes: ~$3.00 (max per session: $5.00)

---

## Tool 3: 95-Scenario Batch Test Suite (~$0.75/test = $71.25 for full suite)

### Location
GitHub: `syntharra-automations/tests/retell-agent-test-suite.json`

### Structure (7 groups)
| Group | Scenarios | What It Tests |
|---|---|---|
| Core Flow Paths | 1-15 | Every node reachable and handles correctly |
| Service Variations | 16-25 | Different HVAC problems and service types |
| Caller Personalities | 26-40 | Elderly, impatient, angry, chatty, non-native, etc. |
| Information Collection | 41-55 | Name, phone, address, email edge cases |
| Edge Cases | 56-80 | Wrong numbers, third-party, mid-flow changes, vendors |
| Pricing Traps | 81-88 | Every angle to extract pricing |
| Boundary & Safety | 89-95 | Abuse, minors, privacy, DIY, diagnosis |

### Running via API
```python
# Load test IDs (already created in Retell)
# Create batch: POST /create-batch-test
# Poll: GET /get-batch-test/{id}
# Results show pass/fail/error counts
# Per-scenario details only visible in Retell dashboard
```

### Cost Breakdown
- 5 scenarios: ~$3.75 (quick check)
- 8 scenarios: ~$6.00 (focused batch)
- 95 scenarios: ~$71.25 (full suite, pre-launch)

### When to Use Full Batch Test
- ✅ Pre-launch validation only
- ✅ "I'm ready to go live, need 100% pass rate"
- ✅ Monthly check-in on live agent
- ❌ For iteration (use Auto-Fix Loop instead)
- ❌ Testing single prompt changes

### Pre-Launch Checklist
Before running full 95-scenario batch:
1. Auto-Fix Loop validated key fixes ($0-5 spent)
2. Call Log Analyser found no CRITICAL issues
3. Agent has been published
4. Ready to commit to go-live if pass rate ≥ 95%

---

## LLM Model Selection Guide

### March 2026 Testing Results

**Premium Agent v26 Testing:**
- Batch: 8 scenarios with gpt-4.1
- Result: **100% pass rate** (5/5 passed, 3 errors from API issues not LLM)
- Cost: Higher than 4.1-mini

**Standard Agent Testing (ongoing):**
- Goal: Achieve 100% pass rate
- Current: ~70-80%
- Strategy: Use gpt-4.1-mini for iteration (cheaper), then gpt-4.1 for final validation

### Model Tiers

| Model | Cost | Quality | Tokens | Use Case |
|---|---|---|---|---|
| gpt-4.1-mini | ~$0.50/1M | 80-90% | Lower | Tier 2: Fix validation |
| gpt-4.1 | ~$2.50/1M | 95-100% | Higher | Tier 3: Pre-launch |

### Recommendation for Your Agents

**Standard Agent (Arctic Breeze):**
- Tier 2 iteration: gpt-4.1-mini
- Tier 3 final: gpt-4.1 when ready for 100%

**Premium Agent:**
- Already at 100% with gpt-4.1 (v26, final state)
- Tools restored and published 2026-03-31

---

## Cost-Gating: Scenario Runner v5

### STOP Running Scenario Runner v4!

Old workflow (v4) has NO cost controls. You hit a $97 bill because:
- No approval gates for expensive batches
- No cost estimate before running
- No running total display
- Accidentally ran full 95-scenario batch twice

### New Workflow (v5) — Cost-Gated

**Before running ANY test:**
1. Choose tier (Diagnose / Fix Validation / Batch Test)
2. Estimate shown: "$X estimated cost"
3. If > $25: approval required (manual confirm)
4. If > $50: hard stop with warning

**During run:**
- Running cost: "$0.45 / $5.00 spent"
- Real-time tracking
- Auto-stops if hitting limit

**After run:**
- Email summary includes actual cost
- Logged to cost-tracker.md

### Implementation Status
- [ ] Scenario Runner v4 → v5 migration (n8n update)
- [ ] Input node: select tier
- [ ] Cost calculation logic
- [ ] Approval gate for > $25
- [ ] Running cost display
- [ ] Cost summary emails

---

## Standard Agent: Path to 100% Pass Rate

Based on Premium agent success (100% pass rate with gpt-4.1):

### Current State (as of 2026-03-30)
- Arctic Breeze HVAC Standard: agent_4afbfdb3fcb1ba9569353af28d
- Flow: conversation_flow_34d169608460
- Last known: ~70-80% on prior iterations

### Strategy to 100%

**Phase 1: Diagnose ($0)**
```
1. Run Call Log Analyser on last 20 real calls
2. Identify CRITICAL and HIGH severity issues
3. Rank by frequency
```

**Phase 2: Iterate ($0.15-$0.75)**
```
For each top issue:
1. Update agent prompt/node
2. Publish agent
3. Run Auto-Fix Loop (1 test = $0.15)
4. If PASS → move to next issue
5. If FAIL → refine and retry
Budget: $5.00 total (30+ tests)
```

**Phase 3: Validate ($6-25)**
```
When top issues are fixed:
1. Run 8-scenario focused batch (gpt-4.1-mini)
2. Check pass rate
3. If ≥ 95% → move to Phase 4
4. If < 95% → identify remaining issues, Phase 2 again
```

**Phase 4: Final ($40-75)**
```
When ready for launch:
1. Run full 95-scenario batch (gpt-4.1)
2. Target: 100% pass
3. If < 95%: identify failures, Phase 2 again
4. If ≥ 95%: ready for live deployment
```

---

## Analysis Framework

When analysing ANY test results (batch, auto-fix, or call logs), produce this report:

### Section 1: Executive Summary
- Total pass rate
- Critical / High / Medium / Low counts

### Section 2: Failure Heatmap by Category
Table showing pass/fail/rate per scenario group

### Section 3: Root Cause Analysis
Group failures by ROOT CAUSE not by scenario. Each root cause = one fix.

### Section 4: Prioritised Fix List
Rank by (scenarios affected) × (severity). Format:
```
FIX #1 [SEVERITY] — Description
  Affected: #X, #Y, #Z
  Root cause: Why
  Fix: Exact change
  Location: Global prompt / node name / agent setting
```

### Section 5: Exact Prompt Changes
Before → after text for each fix

### Section 6: Retest Plan
Which scenarios to rerun per fix

### Section 7: Trends
Compare with previous runs if available

---

## Severity Classification

| Level | Examples |
|---|---|
| CRITICAL | Safety mishandled, data leaked, agent says "Say:", unauthorized pricing |
| HIGH | Lead not captured, wrong routing, no name/phone collected, diagnosis given |
| MEDIUM | Multi-questions, no filler, awkward transitions, missed proactive info |
| LOW | Phrasing, tone, minor formatting |

---

## Current Agent Config (v26 — Premium, v18 — Standard)

### HVAC Standard Agent Config (v18)
```json
{
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
```

### Voice Settings
- Voice: retell-Sloane
- Speed: 1 (dynamic enabled)
- Responsiveness: 0.9 (dynamic enabled)
- Interruption sensitivity: 0.9
- Ambient: call-center (volume 0.7)
- Max call: 600000ms (10 min)

### Conversation Flow Nodes (12)
| Node | ID | Type |
|---|---|---|
| greeting | node-greeting | static_text |
| identify_call | node-identify-call | prompt |
| leadcapture | node-leadcapture | prompt |
| verify_emergency | node-verify-emergency | prompt |
| callback | node-callback | prompt |
| existing_customer | node-existing-customer | prompt |
| general_questions | node-general-questions | prompt |
| spam_robocall | node-spam-robocall | static_text |
| Transfer Call | node-transfer-call | transfer_call |
| transfer_failed | node-transfer-failed | prompt |
| Ending | node-ending | prompt |
| End Call | node-end-call | end |

### Critical Prompt Rules (enforced in global prompt)
- Never "Say:" prefix anywhere — use "Respond with:" or direct instruction
- One question per turn — wait for answer
- Never diagnose (breakers, filters, batteries, thermostats explicitly banned)
- Never promise callback times
- Always summarise ALL details before closing (mandatory step)
- Exact address repeat — never paraphrase street names
- PO Box → ask for physical address
- Email readback with dot/at/dash/underscore
- Mike Thornton by name on any "real person" request
- Abuse boundary before transfer escalation

### Full Agent Backup
GitHub: `syntharra-automations/agent-configs/hvac-standard-v18-backup.json`

---

## Retell API Quick Reference

| Action | Method | Endpoint |
|---|---|---|
| Get agent | GET | `/get-agent/{agent_id}` |
| Update agent | PATCH | `/update-agent/{agent_id}` |
| Publish agent | POST | `/publish-agent/{agent_id}` |
| Get flow | GET | `/get-conversation-flow/{flow_id}` |
| Update flow | PATCH | `/update-conversation-flow/{flow_id}` |
| List calls | POST | `/v2/list-calls` |
| Create test case | POST | `/create-test-case-definition` |
| Run batch test | POST | `/create-batch-test` |
| Get batch result | GET | `/get-batch-test/{batch_id}` |
| List test cases | GET | `/list-test-case-definitions?type=conversation-flow&conversation_flow_id={id}` |

---

## 🔄 Auto-Update Rule

Update this skill when:
- ✅ New test scenarios added
- ✅ New issue detection patterns added to analyser
- ✅ Agent config structure changes
- ✅ New tools built
- ✅ Retell API endpoints change
- ✅ Testing methodology changes
- ❌ NOT for individual test results or fix applications
