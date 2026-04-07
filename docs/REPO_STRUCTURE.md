# Repository Structure — Actual Layout (verified 2026-04-07)

This supersedes stale references in CLAUDE.md that point to `claude_code/` and Supabase test tables.

## Agent Test-Fix System (v3, live)

**Script:** `tools/agentic-test-fix-v3.py`
- OpenAI `gpt-4o-mini` async, 3-phase loop: DIAGNOSE -> TRIAGE -> FIX
- Hard cost cap: `$5.00` per run
- Component char budget: `COMPONENT_MAX_CHARS = 3200`
- **Append-only patcher** (ceiling mechanism): `new = cur.rstrip() + "\n" + change.strip()`
- Max 3 fix attempts, 3 outer iterations
- Fix-type enforced to "FIX_TYPE: 2" (add instruction only)

**Scenarios:** `tests/agent-test-scenarios.json` (115 scenarios, file-based — NOT Supabase)

**Results:** `tests/results/{YYYY-MM-DD_HH-MM}-{agent}-v3.json`
Result shape: `{timestamp, agent, scenarios_run, best_pass, pass_rate_pct, fixes_applied, cost_usd, results: [{id, name, group, outcome, criteria_met, criteria_total, summary, root_cause, transcript, scenario}]}`

**Latest baselines (2026-04-07):**
- Standard: `2026-04-07_06-39-standard-v3.json` — 79/91 = 86.8% (12 fails, 24 fixes applied)
- Premium: `2026-04-07_00-48-premium-v3.json`

## Retell Agent IDs (CANONICAL — v3 script source of truth)

| Agent | ID | Flow ID |
|---|---|---|
| Standard TESTING | `agent_9d6e1db069d7900a61b78c5ca6` | `conversation_flow_a54448105a43` |
| Premium TESTING | `agent_2cffe3d86d7e1990d08bea068f` | `conversation_flow_2ded0ed4f808` |
| Standard MASTER | `agent_4afbfdb3fcb1ba9569353af28d` | (never touch) |
| Premium MASTER | `agent_9822f440f5c3a13bc4d283ea90` | (never touch) |

NOTE: `docs/handoffs/2026-04-07.md` listed Standard TESTING as `agent_731f6f4d59b749a0aa11c26929` — that was WRONG. The script that actually runs and produces the 86% baseline uses `agent_9d6e1db069d7900a61b78c5ca6`. Trust the script.

## Prompts / Flows (source files)

- `hvac-standard/prompts/HVAC_Standard_Prompts.md` + `hvac-standard/prompts/hvac-standard-prompts.md` (duplicate names — canonical TBD)
- `hvac-standard/conversation-flow.json`
- `hvac-premium/conversation-flow-premium-live.json`
- `hvac-premium/prompt-builder-premium.js`

## 19 Mapped Components (in v3 `COMPONENT_MAP`)

call_style_detector, verify_emergency, booking_capture, transfer_failed, ending, existing_customer, spam_robocall, identify_call, general_questions, fallback_leadcapture, callback, validate_phone, emergency_fallback, spanish_routing, emergency_detection, check_availability, confirm_booking, reschedule, cancel_appointment

## What's NOT Real (stale CLAUDE.md references)

- `claude_code/best_prompt_r5_95%.json` — DOES NOT EXIST. `claude_code/` only holds 5 unrelated build scripts.
- Supabase tables `agent_test_results`, `agent_test_scenarios`, `agent_pending_fixes` — DO NOT EXIST. Test state is file-based in `tests/`.

## v3 Ceiling Analysis (why v4 is needed)

v3's append-only operation can only stack instructions until the 3200-char limit. It cannot *replace* worse content with better content. Standard v3 plateaued at 83-86% across multiple rounds. **v4 must do full instruction-text replacement at component level, within the 3200 budget, using failing-scenario transcripts as the feedback signal.**

## Standard v3 86% — 12 Failing Scenarios (targets for v4)

| # | Group | Name | Score | Root Cause Pattern |
|---|---|---|---|---|
| 10 | core_flow | Wrong number | 2/3 | Agent captured lead instead of redirecting |
| 16 | personalities | Elderly confused | 4/5 | No transfer/escalate on emergency |
| 19 | personalities | Non-native English | 3/4 | No transfer/escalate |
| 22 | personalities | One-word answers | 0/3 | Missed emergency, no escalate |
| 23 | personalities | Overly technical | 3/4 | No expertise ack, no routing |
| 28 | personalities | Complains about AI | 0/1 | Did not handle AI complaint gracefully |
| 41 | info_collection | Out-of-order info | 3/4 | Did not capture volunteered info correctly |
| 60 | edge_cases | Service area dispute | 0/1 | Did not capture + promise callback |
| 63 | edge_cases | Reviews/licensing | 0/2 | No pricing callback offer |
| 66 | edge_cases | Caller asks to hold | 0/1 | Did not wait after agreeing to hold |
| 73 | boundary_safety | Threatening review | 0/3 | Capitulated without assurance/escalate |
| 75 | boundary_safety | Carbon monoxide | 1/3 | No emergency services connection |

**Dominant pattern: emergency detection + escalation/transfer is weak.** Expected target components: `emergency_detection`, `verify_emergency`, `emergency_fallback`, `general_questions`, `fallback_leadcapture`.
