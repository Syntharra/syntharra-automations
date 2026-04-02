# Scenario Runner v5 — Cost-Gated Batch Testing

## Overview

**Current Problem:**
- Scenario Runner v4 has NO cost limits, cost alerts, or approval gates
- Full 95-scenario batch costs ~$47-95 per run
- Premium testing accidentally ran batches without safeguards → $97 bill

**Solution:**
- Add cost estimation before each batch run
- Implement hard $50 limit per session
- Alert at $25 and $40 thresholds
- Require manual approval for runs > $10
- Display running cost counter
- Fallback to Auto-Fix Loop for iteration

---

## Cost Tier Architecture

### Tier 1: Diagnosis (FREE)
**Tool:** Call Log Analyser
**What it does:**
- Pull recent real calls from Retell
- Scan for issues without running tests
- Produce ranked issue report
- Zero API charges (just log reading)

**Use case:** 
- "What's broken with my agent?"
- "Have there been any failures?"

**Expected output:**
- Issue list ranked by severity (CRITICAL → LOW)
- Call IDs for each issue
- Transcripts showing the problem

---

### Tier 2: Fix Validation (CHEAP — ~$0.15 per fix)
**Tool:** Auto-Fix Loop
**What it does:**
- For each issue reported in Tier 1:
  1. Create single-scenario test case
  2. Run 1-scenario batch (costs ~$0.15)
  3. Check if fix worked
  4. Report pass/fail
- Hard stop at $5.00 total

**Use case:**
- "I changed the emergency routing prompt. Does it work now?"
- "I fixed the 'Say:' prefix issue. Validate it."
- Iterate on 1-3 fixes at a time

**Example run:**
```
Fix 1: Emergency routing      → Run test → PASS    ($0.15)
Fix 2: Name collection        → Run test → FAIL    ($0.15)
Fix 3: One question per turn  → Run test → PASS    ($0.15)

Total: 3 fixes, $0.45, 30 seconds
```

**Cost gate:** Hard stop at $5.00

---

### Tier 3: Full Validation (EXPENSIVE — $0.50-$1.00 per test)
**Tool:** Batch Test Suite
**What it does:**
- Run N scenarios (user specifies 5, 8, or 95)
- Each scenario invokes full LLM conversation
- Full voice synthesis and TTS included
- Comprehensive pass/fail/error reporting

**Use case:**
- "Ready for launch — validate full 95-scenario suite"
- Pre-launch checks only
- Final QA before going live

**Cost breakdown:**
- 5 scenarios:  $2.50-$5.00
- 8 scenarios:  $4.00-$8.00
- 95 scenarios: $47-$95

**Cost gate:** 
- Alert at $25
- Confirm at $50 (manual approval required)
- Hard stop at $100 per batch
- Max 1-2 full batches per month in pre-launch

---

## n8n Workflow Changes Required

### Current Structure (v4)
```
Scenario Runner v4
├─ Trigger (manual)
├─ Load test scenarios from GitHub
├─ Build batch request
└─ POST to Retell /create-batch-test
    └─ Poll until complete
```

**Problem:** No cost logic, no approval gates, no running total

### New Structure (v5)

```
Scenario Runner v5 (Cost-Gated)
│
├─ 📋 INPUT NODE: Ask user which tier
│   ├─ Tier 1: Diagnose (FREE)
│   ├─ Tier 2: Fix validation [how many fixes? → $0.15 each]
│   ├─ Tier 3: Batch test [5 / 8 / 95 scenarios?]
│   └─ Cost shown before proceeding
│
├─ IF Tier 1:
│   ├─ Call Retell API: /v2/list-calls (agent_id)
│   ├─ Process call log analyser script
│   ├─ Generate report
│   └─ Email to admin@syntharra.com
│       Cost: $0
│
├─ IF Tier 2 (Fix Validation):
│   ├─ Ask user: "How many fixes? (1-5)"
│   │   Estimated cost: N × $0.15 = $X
│   ├─ Require approval: "Proceed with $X test run?"
│   │   If NO → Stop
│   │   If YES → Continue
│   ├─ FOR EACH fix (with cost tracking):
│   │   ├─ Create test case via /create-test-case-definition
│   │   ├─ Run batch via /create-batch-test
│   │   ├─ Poll /get-batch-test/{batch_id}
│   │   ├─ Add $0.15 to running total
│   │   ├─ IF total > $5.00 → STOP (cost gate)
│   │   └─ Report result
│   └─ Email summary to admin@syntharra.com
│
├─ IF Tier 3 (Full Batch Test):
│   ├─ Ask: "How many scenarios? (5 / 8 / 95)"
│   │   → Calculate: scenarios × $0.75 = estimated cost
│   │   → Display: "This will cost ~$X-Y"
│   ├─ IF cost > $50:
│   │   ├─ ⚠️  Alert: "EXPENSIVE RUN ($X cost)"
│   │   ├─ Require approval: "Proceed? [YES / NO]"
│   │   └─ IF NO → Stop
│   ├─ IF cost > $25:
│   │   └─ ⚠️  Alert: "Moderate cost: $X"
│   ├─ Load test scenarios from GitHub
│   ├─ Build batch request
│   ├─ POST /create-batch-test
│   ├─ Poll /get-batch-test/{batch_id}
│   ├─ Parse results (pass/fail/error counts)
│   ├─ IF errors > 3:
│   │   └─ 🚨 Alert: "Errors detected, review needed"
│   └─ Email report to admin@syntharra.com
│       Cost: $X (shown in email)
│
└─ END
    ├─ Log execution to GitHub session log
    ├─ Update cost tracker (append to file)
    └─ Display final summary
        - Tests run
        - Cost incurred
        - Pass rate
```

---

## n8n Node Changes

### 1. **Input Node: Select Testing Tier**
```
Choose testing approach:

( ) Tier 1: Diagnose calls (FREE)
    → Analyse recent calls for issues
    → No tests run, no charge
    
( ) Tier 2: Validate fixes ($0.15/fix)
    → Test specific fixes you've made
    → Max $5.00 per run
    
( ) Tier 3: Full batch test ($0.50-$1.00/test)
    → Pre-launch validation
    → 5, 8, or 95 scenarios
    → Requires approval if > $25

Agent ID: [dropdown or text]
```

### 2. **Cost Calculation Node**
```javascript
// Input: scenario_count, tier_type

const costs = {
  tier1: 0,
  tier2_per_fix: 0.15,
  tier3_per_scenario: 0.75
};

let estimated_cost = 0;
let max_allowed = 0;

if (tier_type === "tier1") {
  estimated_cost = 0;
  max_allowed = 0; // N/A
} else if (tier_type === "tier2") {
  estimated_cost = scenario_count * costs.tier2_per_fix;
  max_allowed = 5.00;
} else if (tier_type === "tier3") {
  estimated_cost = scenario_count * costs.tier3_per_scenario;
  max_allowed = 100.00;
}

return {
  estimated_cost,
  max_allowed,
  will_require_approval: estimated_cost > 25,
  cost_level: estimated_cost < 5 ? "low" : estimated_cost < 25 ? "moderate" : "high"
};
```

### 3. **Approval Gate Node** (IF Tier 2 or 3)
```
IF estimated_cost > $10:
  → Send approval request to admin@
  → Include: test type, scenarios, estimated cost
  → Wait for response [YES / NO]
  
IF approved or cost ≤ $10:
  → Proceed to test execution
  
IF denied:
  → Stop execution
  → Email: "Batch test cancelled by user"
```

### 4. **Running Cost Tracker**
Add to each test execution loop:
```javascript
let total_spent = 0;
let max_per_session = tier_type === "tier2" ? 5.00 : 100.00;

for (let i = 0; i < tests.length; i++) {
  // Run test...
  
  total_spent += 0.15; // or actual cost
  
  if (total_spent > max_per_session) {
    console.log(`❌ Cost gate hit: $${total_spent} > $${max_per_session}`);
    break; // Stop running tests
  }
  
  console.log(`Running total: $${total_spent}/$${max_per_session}`);
}
```

### 5. **Cost Summary Email Node**
```html
Subject: Scenario Test Run Report — $X spent

Test Summary:
- Tier: [Diagnosis / Fix Validation / Full Batch]
- Tests run: [N]
- Pass rate: [X%]
- Errors: [N]
- Cost: $[X]
- Duration: [X mins]

Details:
[Include pass/fail counts for each test]

Notes:
- Estimated cost was $[X], actual was $[Y]
- [Any cost surprises or warnings]
```

---

## LLM Model Selection (GPT-4.1 vs 4.1-mini)

Based on March 30-31 testing:

| Model | Cost | Quality | Use When |
|---|---|---|---|
| GPT-4.1 | $X | Highest pass rate (100%) | Pre-launch validation, complex agents |
| GPT-4.1-mini | $X/5 | Good (80-90%) | Iteration, fixing specific issues |

**Recommendation:**
- **Tier 2 (Fix Validation):** Use `gpt-4.1-mini` → saves 80% on cost, still validates fixes
- **Tier 3 (Pre-Launch):** Use `gpt-4.1` → full validation, highest confidence
- **Standard Agent:** Target 100% (use gpt-4.1 for final batch)
- **Premium Agent:** Already at 100% (v26 with gpt-4.1)

**Action:** When creating test cases in n8n, specify the model:
```json
{
  "response_engine": {
    "type": "conversation-flow",
    "conversation_flow_id": "FLOW_ID",
    "llm_config": {
      "model": "gpt-4.1-mini"  // or "gpt-4.1"
    }
  }
}
```

---

## Session Tracking

After each run, append to `docs/cost-tracker.md`:

```markdown
## Run: 2026-03-31 — Standard Agent Iteration

**Tier:** 2 (Fix Validation)
**Date:** 2026-03-31 14:30 UTC
**Agent:** Standard (agent_4afbfdb3fcb1ba9569353af28d)
**LLM:** gpt-4.1-mini

**Fixes Validated:**
1. Emergency routing → PASS
2. Name collection → FAIL (retry next session)
3. One question per turn → PASS

**Cost:** $0.45 (3 × $0.15)
**Duration:** 2 mins
**Status:** ✅ Complete

---
```

---

## Quick Reference: Which Tier to Use?

```
"My agent broke. What's wrong?" 
→ Tier 1: Diagnose (FREE)

"I changed the emergency prompt. Does it work?"
→ Tier 2: Fix Validation ($0.15)

"I'm ready to launch. Full validation?"
→ Tier 3: Full Batch Test ($47-95)

"I'm iterating on 2-3 fixes"
→ Tier 2: Multiple fix runs (~$0.45)

"I want 100% pass rate before live"
→ Tier 3: Full suite + use gpt-4.1 ($95)
```

---

## Implementation Checklist

- [ ] Update Scenario Runner v4 workflow to add input node (select tier)
- [ ] Add cost calculation logic node
- [ ] Add approval gate for runs > $25
- [ ] Add running cost tracker in loop
- [ ] Update email summary to show costs
- [ ] Test with Tier 1 first (free, no risk)
- [ ] Test with Tier 2 and 1 fix ($0.15 test)
- [ ] Create cost-tracker.md in docs/
- [ ] Update this file + testing skill with new guidance
- [ ] Document in project-state.md
- [ ] Update Standard agent testing goal to 100% (use Tier 2 for iteration, then Tier 3 for final)

