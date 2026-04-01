# Session Log: 2026-04-01 — Fix Agent Testing Workflows

## What changed

Rebuilt both broken n8n workflows (SYNTHARRA_AGENT_TEST_RUNNER and SYNTHARRA_FIX_APPROVER) from scratch using HTTP Request nodes instead of fetch() Code nodes.

## Root cause (prior breakage)

Both workflows used `fetch()` inside n8n Code nodes. Fetch is blocked in n8n's sandbox environment — executions silently failed or errored out.

## Fixes applied

### WF1 — SYNTHARRA_AGENT_TEST_RUNNER (`3MMp9J8QN0YKgA6Q`)

**Architecture (17 nodes):**
`Webhook Trigger → Respond Immediately → GET Scenarios → Filter Scenarios → Split In Batches (batchSize=1) → Wait (10s) → Groq Caller T1 → Groq Agent T1 → Groq Caller T2 → Groq Agent T2 → Groq Evaluate → Parse Eval (Code) → Save Test Result → Check If Failed → [TRUE: Groq Fix Suggestion → Save Pending Fix → loop-back] [FALSE: No Op → loop-back]`

**Key debugging learnings:**
1. **Webhook dual-branch problem**: `responseMode: responseNode` only executes the branch containing the Respond node. Fix: linear chain (Webhook → Respond Immediately → GET Scenarios → ...).
2. **n8n HTTP array wrapping**: HTTP Request node wraps JSON array responses as `{data: [...]}`. Filter Scenarios code handles both formats.
3. **Split In Batches v3 output indices**: output[0] = done signal, output[1] = loop items (opposite of v1/v2).
4. **Code node return format**: `runOnceForEachItem` requires `return {json: {...}}` directly, NOT `return [{json: {...}}]`.
5. **Groq rate limits**: Groq free tier has 30 RPM / 6000 TPM limits. Without throttling, 15 scenarios × 5 Groq calls each overwhelmed the limit. Fixed with 10-second Wait node between scenarios (~3.5 RPM effective rate).
6. **Cross-node references**: `$('NodeName').item.json` works fine in HTTP Request jsonBody expressions. Code nodes should avoid cross-node refs — pass data forward via item json instead.

### WF2 — SYNTHARRA_FIX_APPROVER (`ZAAtRETIIVZSMMDk`)

**Architecture (9 nodes):**
`Webhook: Apply Fix → GET Pending Fix (Supabase) → Parse Fix Data (Code) → GET Retell Agent → Groq: Apply Fix → PATCH Retell Agent → POST Publish Agent → PATCH Fix Status (Supabase) → Respond Success`

No debugging issues — deployed cleanly on first run.

## Smoke test results

**Run:** `POST /webhook/agent-test-runner {"agent_type":"standard","groups":["core_flow"],"run_label":"Claude Code Smoke Test"}`

**Result (15/15 rows in agent_test_results):**

| scenario_id | scenario_name | pass | severity |
|---|---|---|---|
| 1 | Basic service request | PASS | LOW |
| 2 | Emergency - no heat in winter | FAIL | CRITICAL |
| 3 | Quote request | PASS | LOW |
| 4 | Existing customer follow-up | PASS | LOW |
| 5 | FAQ - hours inquiry | FAIL | MEDIUM |
| 6 | Request live person immediately | FAIL | CRITICAL |
| 7 | AC making strange noise | PASS | LOW |
| 8 | Heating system not working | FAIL | MEDIUM |
| 9 | Spam robocall | FAIL | CRITICAL |
| 10 | Wrong number | FAIL | MEDIUM |
| 11 | Maintenance request | PASS | LOW |
| 12 | No cooling with burning smell | FAIL | HIGH |
| 13 | Callback requested | FAIL | MEDIUM |
| 14 | Ductwork cleaning inquiry | PASS | LOW |
| 15 | End of call - caller decides to wait | FAIL | MEDIUM |

**Pass rate:** 6/15 (40%) — many failures relate to agent not reading back details or not handling edge cases. 9 pending fixes generated in `agent_pending_fixes`.

## Build scripts

- `claude_code/build_wf1.py` — Test Runner (PUT to n8n API)
- `claude_code/build_wf2.py` — Fix Approver (PUT to n8n API)

Both scripts read credentials from constants at top of file. Run with `python build_wf1.py` from the claude_code directory.
