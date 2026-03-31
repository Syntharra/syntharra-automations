# Syntharra Testing Cost Tracker

**Purpose:** Track all testing costs to ensure budget compliance  
**Max per session:** Variable by tier (Tier 2: $5, Tier 3: $100)  
**Updated:** 2026-03-31

---

## Session History

### Session: 2026-03-31 — Infrastructure Setup
- **Type:** Planning & diagnostics (Tier 1 = FREE)
- **Cost:** $0
- **Details:**
  - Call Log Analyser run (9 calls analysed)
  - Standard agent Phase 1 diagnostics
  - Auto-Fix Loop tool built
  - Testing framework documented
- **Status:** ✅ Complete

### Next Session: Standard Agent Phase 2 (TBD)
- **Type:** Fix validation (Tier 2)
- **Estimated cost:** $1-2 (5-10 fixes)
- **Max allowed:** $5.00
- **Fixes to validate:**
  - Emergency routing (CRITICAL)
  - Name collection (HIGH)
  - One question per turn (MEDIUM)
  - [Others identified during Phase 2]

---

## Budget Allocation

**Overall Project Budget:** ~$80-85 for complete path to 100%

| Phase | Budget | Used | Remaining |
|---|---|---|---|
| Phase 1: Diagnose | $0 | $0 | $0 |
| Phase 2: Iterate | $5 | TBD | TBD |
| Phase 3: Batch (8) | $10 | TBD | TBD |
| Phase 4: Final (95) | $100 | TBD | TBD |
| **Total** | **$115** | **$0** | **$115** |

---

## Cost Rules

1. **Tier 2 (Auto-Fix Loop):** Hard stop at $5.00 per session
2. **Tier 3 (Batch Test):** Alert at $25, approval required at $50, stop at $100
3. **Weekly cap:** $20 (unless pre-planned launch week)
4. **Monthly cap:** $150 (unless special circumstances)

---

## Historical Costs (Before This Session)

- 2026-03-30: ~$20-30 (E2E testing of pipelines)
- 2026-03-31: ~$95 (Two full 95-scenario batches — unplanned)
- **Problem:** No cost gates, no approvals needed
- **Solution:** Tier 2 (Auto-Fix Loop) prevents this going forward

---

## LLM Model Costs (Estimates)

Based on Retell's pricing and GPT token usage:

| Model | Per Test | Notes |
|---|---|---|
| gpt-4.1-mini | ~$0.15 | Tier 2 (iteration) |
| gpt-4.1-mini | ~$0.75/test | Tier 3 × 8 scenarios = $6 |
| gpt-4.1 | ~$0.75/test | Tier 3 × 95 scenarios = $71 |

**Why 4.1 for final:** 100% pass rate on Premium agent was achieved with gpt-4.1 (v26)

---

## Next Session: How to Run Phase 2

When you're ready to iterate on the Standard agent:

```bash
# Run Auto-Fix Loop
python3 syntharra-automations/tools/auto-fix-loop.py

# Or import directly
python3 << 'PYTHON'
from auto_fix_loop import AutoFixLoop

loop = AutoFixLoop(
    agent_id="agent_4afbfdb3fcb1ba9569353af28d",
    flow_id="conversation_flow_34d169608460",
    max_cost=5.00
)

# Define your fixes
fixes = [
    {
        "issue_type": "emergency_routing",
        "test_prompt": "Caller: Gas smell!\nGoal: Route to emergency immediately",
        "severity": "CRITICAL"
    },
    # ... more fixes
]

results = loop.run_fix_loop(fixes)
PYTHON
```

**Each test:** ~$0.15  
**Cost display:** Real-time in console output  
**Email report:** Sent to admin@syntharra.com

---

## Cost Control Features Added

- ✅ Auto-Fix Loop with $5 gate
- ✅ Scenario Runner v5 spec with approval gates
- ✅ Cost estimation before each batch
- ✅ Running cost tracker display
- ✅ Hard stops at tier limits
- ⏳ n8n workflow implementation (pending)

---

**Last updated:** 2026-03-31  
**Next review:** After Phase 2 completes

