# Syntharra Agent Test Analysis Framework

## How to use this
After running the 95-scenario batch test in Retell, paste the results into a Claude session with this framework. Claude will analyse and produce the report below.

## Input format
Paste the test results in any of these formats:
- Retell dashboard copy-paste (scenario name + pass/fail per metric + transcript)
- JSON export from Retell Batch Testing API
- Manual notes (scenario number + pass/fail + notes)

## Analysis structure

### 1. Executive Summary
- Total pass rate: X/95 (XX%)
- Critical failures (safety/emergency): X
- High priority failures (core flow broken): X
- Medium priority (degraded experience): X
- Low priority (cosmetic/minor): X

### 2. Failure Heatmap by Category

| Category | Tests | Pass | Fail | Rate |
|---|---|---|---|---|
| Core Flow Paths (1-15) | 15 | | | |
| Service Variations (16-25) | 10 | | | |
| Caller Personalities (26-40) | 15 | | | |
| Information Collection (41-55) | 15 | | | |
| Edge Cases (56-80) | 25 | | | |
| Pricing Traps (81-88) | 8 | | | |
| Boundary & Safety (89-95) | 7 | | | |

### 3. Failure Pattern Analysis
Group failures by ROOT CAUSE, not by scenario. For example:
- "Agent asks multiple questions at once" might appear in scenarios 26, 31, 37 → single prompt fix
- "Agent quotes pricing when shouldn't" might appear in 81, 82, 84, 85 → pricing guardrail issue
- "Agent doesn't collect last name" might appear in 42, 31 → name collection logic issue

### 4. Prioritised Fix List
Rank fixes by: (number of scenarios affected) × (severity)

Severity levels:
- CRITICAL: Safety issue, emergency mishandled, data leaked
- HIGH: Core flow broken, lead not captured, wrong routing
- MEDIUM: Poor experience, awkward transitions, missed info
- LOW: Cosmetic, phrasing could be better, minor tone issue

Format:
```
FIX #1 [CRITICAL] — {description}
Affected scenarios: #7, #8
Root cause: {why it happens}
Fix: {exact prompt change or config change}
Location: {global prompt / specific node / agent setting}
```

### 5. Prompt Change Recommendations
Produce the exact text to add/change/remove in:
- Global prompt
- Specific node instructions
- Agent settings (handbook toggles, voice settings etc)
- Conversation flow edges (transition conditions)

### 6. Retest Plan
After applying fixes, list which specific scenarios to rerun to verify the fix worked.
Group reruns by fix so you're not running all 95 again.

### 7. Trends (for repeat test runs)
Compare with previous run if available:
- New failures (regression)
- Fixed failures (improvement)
- Persistent failures (need different approach)
