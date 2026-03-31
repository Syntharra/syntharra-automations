---
name: syntharra-testing
description: >
  Complete reference for Syntharra agent testing, batch simulation, and results analysis.
  ALWAYS load this skill when: running batch tests, analysing test results, producing test
  reports, fixing agent issues found in testing, creating new test scenarios, or any task
  involving agent quality assurance. This skill contains the full 95-scenario test suite
  structure, the analysis framework, and the exact report format to use.
---

# Syntharra — Agent Testing & Analysis Reference

---

## Test Suite Location

- **GitHub:** `syntharra-automations/tests/retell-agent-test-suite.json`
- **Total scenarios:** 95
- **Format:** JSON array of objects with `name`, `user_prompt`, `metrics` fields

---

## Test Suite Structure (7 groups)

| Group | Scenarios | What it tests |
|---|---|---|
| Core Flow Paths | 1-15 | Every node in conversation flow is reachable and handles correctly |
| Service Variations | 16-25 | Different HVAC problems and service types |
| Caller Personalities | 26-40 | Same scenarios with different caller behaviours (elderly, impatient, angry, chatty, non-native speaker, etc.) |
| Information Collection | 41-55 | Edge cases in name, phone, address, email collection |
| Edge Cases & Anomalies | 56-80 | Unusual situations: wrong numbers, third-party callers, mid-flow changes, vendors, insurance, cancellations |
| Pricing Traps | 81-88 | Every angle a caller might use to extract pricing |
| Boundary & Safety | 89-95 | Abuse, minors, privacy, DIY requests, diagnosis requests |

---

## How to Run Tests

### In Retell Dashboard (manual)
1. Go to agent → Test tab → AI Simulated Chat
2. Create test cases one at a time using the `user_prompt` from each scenario
3. Add `metrics` as evaluation criteria
4. Save each as a named test case
5. Use Batch Test to run all at once

### Via Retell Batch Testing API (automated)
Retell has a Batch Testing API (launched ~March 2026). Check latest docs for endpoints.

---

## Analysis Framework — USE THIS WHEN ANALYSING RESULTS

When Dan provides test results (in any format — copy-paste, JSON, manual notes, screenshots), produce the following report:

### Section 1: Executive Summary
```
Total pass rate: X/95 (XX%)
Critical failures (safety/emergency): X
High priority failures (core flow broken): X  
Medium priority (degraded experience): X
Low priority (cosmetic/minor): X
```

### Section 2: Failure Heatmap by Category

| Category | Tests | Pass | Fail | Rate |
|---|---|---|---|---|
| Core Flow Paths (1-15) | 15 | ? | ? | ?% |
| Service Variations (16-25) | 10 | ? | ? | ?% |
| Caller Personalities (26-40) | 15 | ? | ? | ?% |
| Information Collection (41-55) | 15 | ? | ? | ?% |
| Edge Cases (56-80) | 25 | ? | ? | ?% |
| Pricing Traps (81-88) | 8 | ? | ? | ?% |
| Boundary & Safety (89-95) | 7 | ? | ? | ?% |

### Section 3: Failure Pattern Analysis
Group failures by ROOT CAUSE, not by individual scenario.

Example root causes:
- "Agent asks multiple questions at once" → appears in scenarios 26, 31, 37
- "Agent quotes pricing when it shouldn't" → appears in 81, 82, 84
- "Agent doesn't collect last name" → appears in 42, 31
- "Agent skips acknowledgement between details" → appears in 41, 43, 49
- "Agent doesn't recognise out-of-scope request" → appears in 58, 67
- "Agent attempts diagnosis" → appears in 89, 18
- "Agent doesn't use timezone for hours question" → appears in 74, 75

Each root cause = one fix that solves multiple failures.

### Section 4: Prioritised Fix List
Rank by: (number of scenarios affected) × (severity)

Severity levels:
- **CRITICAL**: Safety issue, emergency mishandled, data leaked
- **HIGH**: Core flow broken, lead not captured, wrong routing  
- **MEDIUM**: Poor experience, awkward transitions, missed info
- **LOW**: Cosmetic, phrasing could be better, minor tone issue

Format each fix as:
```
FIX #1 [SEVERITY] — Description
  Affected scenarios: #X, #Y, #Z
  Root cause: Why this happens
  Fix: Exact prompt text to add/change/remove
  Location: Global prompt / specific node name / agent setting
```

### Section 5: Exact Prompt Changes
For each fix, provide the exact before → after text change:
- Which file/node/section it's in
- The exact current text (or "ADD NEW")
- The exact replacement text
- Whether it needs publishing after

### Section 6: Retest Plan
After applying fixes, list which specific scenarios to rerun (not all 95).
Group reruns by fix:
```
After applying Fix #1: Rerun scenarios #7, #8, #95
After applying Fix #2: Rerun scenarios #81, #82, #84, #85
```

### Section 7: Trends (for repeat runs)
If previous results exist, compare:
- New failures (regression from prompt changes)
- Fixed failures (improvement)
- Persistent failures (need different approach)

---

## Severity Classification Guide

### CRITICAL — Must fix immediately
- Emergency calls not routed to transfer
- Gas smell / CO detector not treated as safety-critical
- Agent makes up pricing or company info
- Agent gives medical/safety advice
- Agent continues collecting info for out-of-scope service
- Minor/child safety not handled appropriately

### HIGH — Fix before go-live
- Agent doesn't collect required lead info (name, phone)
- Agent doesn't confirm details back
- Call routing goes to wrong node
- Agent can't handle basic service requests
- Transfer triggers not firing when they should
- Spam/robocalls not detected

### MEDIUM — Fix for quality
- Agent asks multiple questions at once
- No acknowledgement filler between detail collection
- Awkward transitions between topics
- Agent too verbose or too terse
- Doesn't mention promotions when relevant
- Doesn't adapt to caller personality

### LOW — Polish
- Phrasing could sound more natural
- Agent says filler words too much or not enough
- Minor formatting issues in how details are read back
- Could mention value props more naturally

---

## Agent Configuration Reference (for fixes)

### Current Handbook Config (Arctic Breeze test agent)
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

### Conversation Flow Nodes
| Node | ID | Type |
|---|---|---|
| greeting | node-greeting | static_text |
| identify_call | node-identify-call | prompt |
| nonemergency_leadcapture | node-leadcapture | prompt |
| verify_emergency | node-verify-emergency | prompt |
| callback | node-callback | prompt |
| existing_customer | node-existing-customer | prompt |
| general_questions | node-general-questions | prompt |
| spam_robocall | node-spam-robocall | static_text |
| Transfer Call | node-transfer-call | transfer_call |
| transfer_failed | node-transfer-failed | prompt |
| Ending | node-ending | static_text |
| End Call | node-end-call | end |

### How to Apply Fixes
1. Global prompt changes: Update via Retell API `PATCH /update-conversation-flow/{flow_id}`
2. Node instruction changes: Update `nodes[].instruction.text` in same API call
3. Agent settings: Update via `PATCH /update-agent/{agent_id}`
4. Always publish after: `POST /publish-agent/{agent_id}`
5. Test only on Arctic Breeze first (agent_4afbfdb3fcb1ba9569353af28d)
6. Roll out to production prompt builder only after Dan approves

---

## Retell API Quick Reference (for testing)

- **Flow ID:** `conversation_flow_34d169608460`
- **Test Agent ID:** `agent_4afbfdb3fcb1ba9569353af28d`  
- **API Key:** Query from `syntharra_vault` → `service_name = 'Retell AI'`
- **Publish after any change:** `POST https://api.retellai.com/publish-agent/{agent_id}`

---

## Retell Test Import Format

When importing test cases into Retell dashboard, the expected format for each test case is:

**User Prompt** (paste into the user scenario field):
```
## Identity
Your name is [Name]. Your phone number is [Number]. You live at [Address].

## Goal
[What the caller wants to achieve]

## Personality
[How the caller behaves, speaks, reacts]
```

**Metrics** (paste into evaluation criteria):
```
1. [First metric to evaluate]
2. [Second metric to evaluate]
...
```

Note: Retell does NOT currently support bulk JSON import of test cases. Each must be created manually in the dashboard. The JSON file in GitHub is for OUR reference and for future API automation when Retell adds that capability.

---

## 🔄 Auto-Update Rule

Update this skill when:
- ✅ New test scenarios added to the suite
- ✅ Analysis framework structure changes
- ✅ New test groups or categories added
- ✅ Severity classification criteria change
- ✅ Retell testing API endpoints change
- ❌ Do NOT update for individual test run results (those are transient)
- ❌ Do NOT update for individual fix applications (those go in session logs)

---

## Auto-Fix Loop

The auto-fix loop is a script that automates issue detection and fix validation.

**Location:** `syntharra-automations/tools/auto-fix-loop.py`
**Cost:** ~$0.15 per issue tested (single simulation, not full batch)

### How it works:
1. Pulls last 20 calls from Retell API
2. Scans every transcript for known issue patterns
3. Groups issues by type and deduplicates
4. For each testable issue, creates a single targeted simulation test
5. Runs the test and checks pass/fail
6. Reports which issues are fixed and which still need work

### Issue patterns it detects:
- Agent literally says "Say:" prefix
- Agent asks 3+ questions in one turn
- No summary readback before closing
- Agent gives diagnostic/troubleshooting advice
- Call marked unsuccessful
- Negative caller sentiment

### How to run it:
In any Claude session, run:
```python
python3 /path/to/auto-fix-loop.py
```
Or ask Claude to "run the auto-fix loop" and it will pull the script from GitHub and execute it.

### When to use it:
- After making prompt or node changes — validate they work
- After a client reports a bad call — diagnose the issue
- Weekly quality check — run against recent calls
- Before going live with a new client agent

### When NOT to use it:
- For routine monitoring — use the free call log analyser instead
- For comprehensive testing — use the 95-scenario batch test ($7/run)
- For real voice quality testing — use Hamming AI (real phone calls)

---

## Call Log Analyser

The call log analyser pulls real call data and scans for issues at zero cost.

**Location:** `syntharra-automations/tools/retell-call-analyser.py`
**Cost:** Free (reads existing call data)

### How to run:
```python
python3 retell_call_analyser.py --limit 50 --agent AGENT_ID
```
Or ask Claude to "analyse our recent calls" / "run the call log analyser".

### What it checks:
- Call success/failure status
- User sentiment (negative/very negative)
- Abnormal disconnections (agent_hangup, error)
- Very short calls (<15s) or very long calls (>5min)
- High token usage (>6000 avg per turn)
- High latency (LLM p50 >1000ms)
- Transcript patterns: diagnosis, pricing leaks, multi-questions, missing names, missing summaries

### Output:
Markdown report grouped by severity × frequency, with call quality stats.
