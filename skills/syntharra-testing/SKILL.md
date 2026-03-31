---
name: syntharra-testing
description: >
  Complete testing, analysis, and auto-fix system for Syntharra agents.
  ALWAYS load this skill when: analysing call logs, running test scenarios,
  fixing agent issues, producing test reports, validating prompt changes,
  creating new test scenarios, or any QA task. Contains the call log analyser,
  auto-fix loop, 95-scenario test suite, analysis framework, and all tool code.
---

# Syntharra — Agent Testing, Analysis & Auto-Fix Skill

---

## Quick Reference

| Tool | Cost | Use When |
|---|---|---|
| Call Log Analyser | FREE | Routine monitoring, checking recent calls |
| Auto-Fix Loop | ~$0.15/issue | After changes, validating specific fixes |
| Full Batch Test (95) | ~$7/run | Pre-launch, major prompt rewrites only |
| Hamming AI | TBD | Real voice quality testing (100 free calls) |

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

---

## Tool 2: Auto-Fix Loop (~$0.15/issue)

Analyses call logs, identifies issues, creates targeted single-scenario tests, validates fixes.

### How to Run
```python
# The loop does:
# 1. Pull calls → analyse transcripts → find issues
# 2. For each testable issue:
#    a. Create a single test case via API
#    b. Run it (single simulation, ~$0.15)
#    c. Check pass/fail
#    d. Report result
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

---

## Tool 3: 95-Scenario Batch Test Suite (~$7/run)

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

### Premium Agent Additional Scenarios (to be added)
When testing Premium agents, add scenarios for:
- Cal.com appointment booking flow
- Google Calendar availability check
- Jobber integration
- Multi-notification recipients
- Dispatcher workflow
- Repeat caller detection

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

## Current HVAC Standard Agent Config (v18 — March 2026)

### Handbook Config
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
- ❌ NOT for individual test results or fix applications
