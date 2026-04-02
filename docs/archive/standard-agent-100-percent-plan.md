# Standard Agent: Path to 100% Pass Rate

**Goal:** Arctic Breeze HVAC Standard agent → 100% pass rate on 95-scenario test suite  
**Agent ID:** `agent_4afbfdb3fcb1ba9569353af28d`  
**Flow ID:** `conversation_flow_34d169608460`  
**Target Model:** gpt-4.1 (final validation)  
**Budget:** ~$10-15 total for complete iteration cycle

---

## Phase 1: Diagnose Issues (FREE)

### Step 1a: Pull Real Call Data
```python
import json
import urllib.request

RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"

# Get last 20 real calls
req = urllib.request.Request(
    "https://api.retellai.com/v2/list-calls",
    method="POST",
    data=json.dumps({
        "limit": 20,
        "sort_order": "descending",
        "filter_criteria": {"agent_id": [AGENT_ID]}
    }).encode(),
    headers={
        "Authorization": f"Bearer {RETELL_KEY}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(req) as resp:
    calls_data = json.loads(resp.read().decode())
    calls = calls_data.get("calls", [])

print(f"Fetched {len(calls)} recent calls")

# Show summary
successful = sum(1 for c in calls if c.get("call_analysis", {}).get("call_successful", False))
failed = len(calls) - successful
print(f"Successful: {successful}/{len(calls)}")
print(f"Failed: {failed}/{len(calls)}")

# Analyse first 3 calls
for call in calls[:3]:
    print(f"\nCall {call.get('call_id')[:8]}...")
    print(f"  Duration: {call.get('duration_ms')/1000:.0f}s")
    print(f"  Sentiment: {call.get('call_analysis', {}).get('user_sentiment')}")
    print(f"  Success: {call.get('call_analysis', {}).get('call_successful')}")
    
    # Check transcript for issues
    transcript = call.get("transcript", [])
    for turn in transcript:
        agent_msg = turn.get("agent_message", "")
        if "Say:" in agent_msg:
            print(f"  ⚠️  'Say:' prefix found in agent response")
        if agent_msg.count("?") > 1:
            print(f"  ⚠️  Multiple questions in one turn")
```

### Step 1b: Run Call Log Analyser (via GitHub)
```bash
# Clone the script
curl -s https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/tools/retell-call-analyser.py > call-analyser.py

# Run it
python3 call-analyser.py
# Output:
# ✓ Pulled 20 calls
# ⚠️  Issue: CRITICAL — 'Say:' prefix in 3 calls
# ⚠️  Issue: HIGH — No name collected in 2 calls (>30s duration)
# ⚠️  Issue: MEDIUM — Multiple questions in 1 call
```

### Step 1c: Summarize Issues Found

Create a ranked list. Example:
```
CRITICAL Issues (Fix immediately):
1. "Say:" prefix in X calls — agent outputs literal "Say:" text
2. [Other critical issues]

HIGH Issues (Fix before Tier 3):
1. No name collection on calls >30s — 2 calls affected
2. [Other high issues]

MEDIUM Issues (Lower priority):
1. Multiple questions per turn — 1 call affected
```

---

## Phase 2: Iterate & Validate Fixes (~$0.15 per fix, max $5.00)

### For Each Issue (using Auto-Fix Loop)

**Step 2a: Update Agent Prompt/Node**

Example for "Say:" prefix issue:
```
OLD (in node instruction):
  Say: "Let me check that for you now."

NEW (corrected):
  Tell the caller: "Let me check that for you now."
  
Or even better:
  Respond with: "Let me check that for you now."
```

Location: Edit the conversation flow node via Retell dashboard or API

**Step 2b: Publish Agent**
```bash
curl -X POST \
  https://api.retellai.com/publish-agent/agent_4afbfdb3fcb1ba9569353af28d \
  -H "Authorization: Bearer key_0157d9401f66cfa1b51fadc66445"
```

**Step 2c: Create & Run Single-Scenario Test via Auto-Fix Loop**

```python
from auto_fix_loop import AutoFixLoop

loop = AutoFixLoop(
    agent_id="agent_4afbfdb3fcb1ba9569353af28d",
    flow_id="conversation_flow_34d169608460",
    max_cost=5.00
)

# Define the fix
fixes = [
    {
        "issue_type": "say_prefix_fix",
        "test_prompt": "Caller: Can you help me?\nGoal: Agent responds naturally without 'Say:' prefix",
        "severity": "CRITICAL"
    }
]

# Run the test
results = loop.run_fix_loop(fixes)

# Output:
# ✓ say_prefix_fix → PASS ($0.15)
# Total: 1 test, $0.15 spent
```

**Step 2d: Interpret Results**

- **PASS:** Fix works! Move to next issue.
- **FAIL:** Fix didn't work. Check the transcript from the batch to see why.
  - Refine the prompt or node logic
  - Re-run the test ($0.15 per retry)

### Running Multiple Issues (Batch All Fixes at Once)

Once you've prepared all fixes, run them together:

```python
fixes_to_validate = [
    {
        "issue_type": "say_prefix",
        "test_prompt": "Caller: Help!\nGoal: No 'Say:' prefix",
        "severity": "CRITICAL"
    },
    {
        "issue_type": "name_collection",
        "test_prompt": "Caller: I need AC repair\nGoal: Collect name before close",
        "severity": "HIGH"
    },
    {
        "issue_type": "one_question_per_turn",
        "test_prompt": "Caller: What's available?\nGoal: Ask one question at a time",
        "severity": "MEDIUM"
    },
    {
        "issue_type": "emergency_routing",
        "test_prompt": "Caller: I smell gas!\nGoal: Route to emergency immediately",
        "severity": "CRITICAL"
    }
]

results = loop.run_fix_loop(fixes_to_validate)

# Output:
# ✓ say_prefix → PASS ($0.15)
# ✓ name_collection → PASS ($0.15)
# ✓ one_question_per_turn → PASS ($0.15)
# ✓ emergency_routing → PASS ($0.15)
# Total: 4 fixes, $0.60 spent, 100% pass
```

### Cost Tracking Phase 2

After each iteration cycle:
```
Session: 2026-04-01
Tier: 2 (Fix Validation)
Issues fixed: 4
Cost: $0.60
Pass rate: 100%
Status: Ready for Phase 3
```

---

## Phase 3: Focused Batch Validation (~$6-8 for 8-scenario batch with gpt-4.1-mini)

### Step 3a: Run 8-Scenario Batch

Once Phase 2 issues all PASS, run a focused batch of 8 scenarios:

```python
# Via n8n Scenario Runner v5 (once cost-gated):
# 1. Select Tier 3: Full Batch Test
# 2. Choose: 8 scenarios
# 3. Model: gpt-4.1-mini
# 4. Cost estimate shown: ~$6
# 5. Approve: YES
# 6. Wait for results
```

Or via direct Retell API:
```python
# Load first 8 test cases (Core Flow Paths group)
# Run batch
# Poll results
# Check: pass_count ≥ 7 (≥88% pass rate)
```

### Step 3b: Interpret Results

- **Pass rate ≥ 95%:** Proceed to Phase 4 (full 95-scenario)
- **Pass rate < 95%:** Identify which 8 scenarios failed
  - Go back to Phase 2
  - Create targeted fixes for those scenarios
  - Re-run Phase 3

---

## Phase 4: Full Pre-Launch Validation (~$71 for 95-scenario batch with gpt-4.1)

### Step 4a: Run Full 95-Scenario Batch

Only when Phase 3 passes ≥95%:

```python
# Via n8n Scenario Runner v5:
# 1. Select Tier 3: Full Batch Test
# 2. Choose: 95 scenarios
# 3. Model: gpt-4.1  ← UPGRADE to highest quality
# 4. Cost estimate shown: ~$71
# 5. Approval required: YES (>$50)
# 6. Confirm and execute
```

### Step 4b: Analyse Results

Expected output format:
```
Batch Test Results: Full 95-Scenario Suite
=============================================
Total: 95 scenarios
Passed: 90+
Failed: < 5
Errors: 0-3

By Category:
  Core Flow Paths (1-15): 15/15 ✓
  Service Variations (16-25): 10/10 ✓
  Caller Personalities (26-40): 15/15 ✓
  Information Collection (41-55): 15/15 ✓
  Edge Cases (56-80): 20/25 ⚠️ (5 failures)
  Pricing Traps (81-88): 8/8 ✓
  Boundary & Safety (89-95): 7/7 ✓

Pass Rate: 90/95 = 94.7%

Failures Analysis:
- Scenario #62: [Description] — Root cause: [X]
- Scenario #68: [Description] — Root cause: [Y]
- ...
```

### Step 4c: Final Decision

- **Pass rate ≥ 95%:** ✅ Agent is ready for live deployment
- **Pass rate < 95%:** Go back to Phase 2
  - Target the specific failing scenarios
  - Run Auto-Fix Loop on those
  - Re-run Phase 4

---

## Budget Breakdown

| Phase | Cost | Notes |
|---|---|---|
| 1: Diagnose | $0 | Call log analysis only |
| 2: Iterate | $0.60-$3.00 | 4-20 fixes × $0.15 each |
| 3: Focused Batch | $6-8 | 8 scenarios × ~$0.75 with 4.1-mini |
| 4: Full Validation | $71 | 95 scenarios × ~$0.75 with gpt-4.1 |
| **Total** | **~$80-85** | For complete cycle to launch |

**If required retries:** +$3-10 per extra iteration cycle

---

## Quick Start: Run This Today

### Minimal Test (Cost: $0.15)

If you want to validate the Auto-Fix Loop works:

```python
# Copy this script and run it

import json
import urllib.request
import sys
sys.path.insert(0, '/path/to/syntharra-automations/tools')

from auto_fix_loop import AutoFixLoop

# Test a single fix
loop = AutoFixLoop(
    agent_id="agent_4afbfdb3fcb1ba9569353af28d",
    flow_id="conversation_flow_34d169608460",
    max_cost=5.00
)

results = loop.run_fix_loop([
    {
        "issue_type": "test_emergency_routing",
        "test_prompt": "Caller: There's a fire!\nGoal: Immediately route to emergency, no questions asked",
        "severity": "CRITICAL"
    }
])

print(f"\nTest complete!")
print(f"Result: {'PASS ✓' if results['test_emergency_routing']['passed'] else 'FAIL ✗'}")
```

---

## Session Log Template

After completing each phase, log the results:

```markdown
# Session: Standard Agent — Phase X Iteration Y
Date: 2026-04-01
Agent: Arctic Breeze (agent_4afbfdb3fcb1ba9569353af28d)
Model: gpt-4.1-mini (iteration) / gpt-4.1 (final)

## Issues Fixed
1. [Issue] → [Fix Applied] → [Result: PASS/FAIL]
2. [Issue] → [Fix Applied] → [Result: PASS/FAIL]

## Metrics
- Cost: $X
- Tests run: N
- Pass rate: X%
- Duration: X mins

## Next Steps
- [ ] If all issues PASS → move to Phase 3
- [ ] If issues FAIL → retry with refined fix

## Notes
[Any observations about agent behavior, unexpected issues, etc.]
```

---

## Failure Diagnosis Guide

If a test FAILs, here's how to debug:

### 1. Get the Batch Results
```python
# After running test, get batch ID from result
batch_id = results["batch_id"]

# Fetch full results
req = urllib.request.Request(
    f"https://api.retellai.com/get-batch-test/{batch_id}",
    method="GET",
    headers={"Authorization": f"Bearer {RETELL_KEY}"}
)

with urllib.request.urlopen(req) as resp:
    batch_result = json.loads(resp.read().decode())
    
# Check if we can get more details
print(batch_result)
```

### 2. Check the Call Transcript

For single-scenario batch tests, the transcript is usually available via:
```python
# Get the call from /v2/list-calls filtered by the test
# (May need to wait ~30 seconds for call to appear)
```

### 3. Refine Your Fix

Common reasons for FAIL:
- Prompt wording unclear to LLM
- Node logic not updated (old version still published)
- Agent not republished after changes
- Test prompt too vague

### 4. Retry

Update your fix and run another test ($0.15 each):
```python
results2 = loop.run_fix_loop([
    {
        "issue_type": "name_collection_refined",
        "test_prompt": "Caller: I need HVAC repair. [Says name: John]\nGoal: Confirm name, ask for phone, close with summary",
        "severity": "HIGH"
    }
])
```

---

## Standard Agent: Current Known Issues

Based on prior testing cycles, watch for:

1. **"Say:" prefix** — Agent should never output literal "Say:" text
2. **Multiple questions per turn** — Ask one question, wait for answer
3. **No emergency routing** — Gas smell, CO alarm, fire should go immediately
4. **Name not collected** — Especially on calls >30 seconds
5. **No readback before close** — Summary all details before ending

These are the likely culprits preventing 100% pass rate.

---

## When Ready for Live

Once Phase 4 completes with ≥95% pass rate:

1. ✅ Update `docs/project-state.md` with final agent version
2. ✅ Log final batch test results to session log
3. ✅ Email summary to `admin@syntharra.com`
4. ✅ Schedule go-live (coordinate with Stripe live mode cutover)
5. ✅ Set up monitoring alerts for live calls

---

## Commands Quick Reference

```bash
# Get recent calls
curl -X POST https://api.retellai.com/v2/list-calls \
  -H "Authorization: Bearer key_0157d9401f66cfa1b51fadc66445" \
  -d '{"limit":20,"sort_order":"descending","filter_criteria":{"agent_id":["agent_4afbfdb3fcb1ba9569353af28d"]}}'

# Publish agent after changes
curl -X POST https://api.retellai.com/publish-agent/agent_4afbfdb3fcb1ba9569353af28d \
  -H "Authorization: Bearer key_0157d9401f66cfa1b51fadc66445"

# Get test batch results
curl https://api.retellai.com/get-batch-test/{batch_id} \
  -H "Authorization: Bearer key_0157d9401f66cfa1b51fadc66445"
```

