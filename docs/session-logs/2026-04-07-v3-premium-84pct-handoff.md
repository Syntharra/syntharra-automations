# Session Log — 2026-04-07 — Scenario Tester v3 + Handoff

## What ran
- v3 agentic tester on Premium TESTING (agent_2cffe3d86d7e1990d08bea068f, flow conversation_flow_2ded0ed4f808)
- Result: 91/108 (84%), 20 fixes applied, $0.1702/$5.00 spent
- Results: tests/results/2026-04-07_00-48-premium-v3.json
- Standard NOT executed: AGENT_CONFIG standard (agent_731f6f4d59b749a0aa11c26929 / conversation_flow_5b98b76c8ff4) returns 404

## Why Premium plateaued at 84%
Three components saturated against COMPONENT_MAX_CHARS=2500:
- booking_capture ~4900 (over cap, blocks all appends)
- verify_emergency ~2437
- identify_call ~2500
Append-only loop cannot fix. Requires intelligent compression.

## Handoff for next chat — DO THIS

### 1. Compress 3 bloated Premium components WITHOUT losing efficacy
Dan's constraint: compression must NOT reduce behavior coverage. Before shortening prose, evaluate alternatives:
- Move deterministic logic into Code/Function nodes in the conversation flow (validation, formatting, branching) instead of prompt instructions
- Move static data (zip lists, hours, pricing) to knowledge base / dynamic vars
- Collapse repeated phrasing, consolidate examples, remove redundancy
Target: <2000 chars each, all behaviors preserved. Re-run v3 Premium → 95%+.

### 2. Clone HVAC Standard MASTER → new Standard TESTING
- Source: agent_4afbfdb3fcb1ba9569353af28d, flow conversation_flow_34d169608460
- GET master flow → POST as new flow (suffix " TESTING") → POST new agent → publish
- Back up to retell-agents/

### 3. Fix stale AGENT_CONFIG in tools/agentic-test-fix-v3.py
- Replace standard agent_id + flow_id with new TESTING values
- Remap COMPONENT_MAP standard entries to new flow's component IDs (match by name)

### 4. Run v3 Standard → 95%+

## Hard rules still in force
- TESTING agents only — never patch MASTER (agent_4afbfdb3fcb1ba9569353af28d, agent_9822f440f5c3a13bc4d283ea90)
- $5.00 HARD_CAP per agent run
- Always fetch flow → merge → PATCH; never reconstruct
- Always publish after Retell update
- Retell batch sim testing requires 3x explicit permission

## Files to read at start of next chat
- tools/agentic-test-fix-v3.py
- tests/results/2026-04-07_00-48-premium-v3.json
- docs/HARD_RULES.md, docs/REFERENCE.md, docs/FAILURES.md
