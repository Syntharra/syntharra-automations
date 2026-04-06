# Syntharra — Reference Data
> Static reference: agent IDs, flow IDs, simulator commands, workflow counts.
> This file does not track tasks — see TASKS.md for open work.
> Updated when IDs change or new agents are added.

---

## ⚠️ Known Script Gotchas

| Script | Gotcha | Safe Alternative |
|---|---|---|
| `run_tests.py --agent premium` | **BROKEN** — silently ignores `--agent` flag. Always runs STANDARD TESTING SUITE first regardless. Wastes ~200K TPD tokens before Premium starts. Discovered 2026-04-06 after losing full day's budget. | Use `run_premium_only.py` instead |
| `promote.py --agent premium` | **BROKEN** — tries to fetch Premium MASTER flow which doesn't exist yet (agent not created). Returns 404. | Use `promote_premium.py` instead |

---

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE (promoted 2026-04-06, flow v22, 90/91 98%) |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Awaiting full 108-scenario run (run after midnight UTC with run_premium_only.py) |
| Demo Female / Sophie | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male / Jake | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

> Note: All other agents deleted 2026-04-06 cleanup (156 → 4). Standard TESTING agent deleted after successful promotion to MASTER.
> Note: Premium MASTER agent does NOT exist yet — promote_premium.py --live will create it on first promotion.

## Conversation Flow Registry
| Flow | ID | Bound to |
|---|---|---|
| HVAC Standard (MASTER) | `conversation_flow_34d169608460` | Standard MASTER agent |
| HVAC Standard (TESTING) | `conversation_flow_5b98b76c8ff4` | Unbound — Standard TESTING agent deleted post-promotion |
| HVAC Premium (MASTER) | `conversation_flow_1dd3458b13a7` | ⚠️ NOT YET CREATED — Premium MASTER agent does not exist |
| HVAC Premium (TESTING) | `conversation_flow_2ded0ed4f808` | Premium TESTING agent |

## Simulator — Premium
```
# Run core_flow group
git pull && python3 tools/openai-agent-simulator-premium.py --key <groq_key> --group core_flow

# Group order: core_flow → personalities → info_collection → pricing_traps → edge_cases → boundary_safety → premium_specific
# Model: llama-3.3-70b-versatile
# Groq key: Supabase vault — service_name='Groq', key_type='api_key'
# Prompt: global prompt only (~10k chars) — node instructions must be INCLUDED (do not strip)
```

## n8n Workflows
- Total: 47 | Active: 32 | Labelled: 37/47
- Unlabelled active: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)
- 9 inactive duplicates: left intentionally per Dan 2026-04-04

## Phone Numbers
- Standard smoke test line: +18129944371

## core_flow — Fix Status (Premium TESTING)
| # | Scenario | Status |
|---|---|---|
| #5 | FAQ - hours inquiry | ✅ FIXED |
| #7 | Booking push | Fix applied, retest pending |
| #11 | Service type order | Fix applied, retest pending |
| #13 | Callback repetition | Fix applied, retest pending |
| #14 | Pricing redirect | Fix applied, retest pending |
| #15 | Over-eager close | Fix applied, retest pending |


## Component Library (Subagent)
| Component | ID |
|---|---|
| call_style_detector | `conversation_flow_component_ff58734c21bb` |
| verify_emergency | `conversation_flow_component_174275fc7751` |
| booking_capture | `conversation_flow_component_ca04bba21560` |
| transfer_failed | `conversation_flow_component_335da5e7364e` |
| ending | `conversation_flow_component_827d612a2cb9` |
| existing_customer | `conversation_flow_component_d8eff9881e16` |
| spam_robocall | `conversation_flow_component_2cc95ba461b7` |
| identify_call | `conversation_flow_component_ebac0db129f3` |
| general_questions | `conversation_flow_component_d46848148d1d` |
| fallback_leadcapture | `conversation_flow_component_33ab8b82f1fc` |
| callback | `conversation_flow_component_ab7909b654e2` |
| validate_phone | `conversation_flow_component_3b788e86e755` |
| emergency_fallback | `conversation_flow_component_9d3c5c904347` |
| spanish_routing | `conversation_flow_component_731ee109f18a` |
| emergency_detection | `conversation_flow_component_24d9b49e1a30` |
| check_availability | `conversation_flow_component_dfe7bd5017e5` |
| confirm_booking | `conversation_flow_component_20ac85a7954c` |
| reschedule | `conversation_flow_component_4b3d107fd73a` |
| cancel_appointment | `conversation_flow_component_eb20b4cd1d8d` |


## Testing Tools

| Tool | Path | Purpose |
|---|---|---|
| Agentic Test Engine | `tools/agentic-test-fix.py` | Full scenario suite + triage + self-fix. Respects --agent flag correctly. |
| **Premium-Only Runner** | `C:\Users\danie\syntharra-tests\run_premium_only.py` | **USE THIS for Premium runs.** Bypasses run_tests.py wrapper — downloads agentic-test-fix.py from GitHub, calls it directly with --agent premium. |
| **Premium Promoter** | `C:\Users\danie\syntharra-tests\promote_premium.py` | Promotes Premium TESTING → MASTER. Creates MASTER agent if doesn't exist. Dry run default, --live to execute, --force to skip gate. |
| Standard Simulator | `tools/openai-agent-simulator.py` | Legacy per-scenario pass/fail |
| Premium Simulator | `tools/openai-agent-simulator-premium.py` | Legacy per-scenario pass/fail (Premium) |
| Standard E2E | `shared/e2e-test.py` | Full pipeline E2E (93 assertions) |
| Premium E2E | `shared/e2e-test-premium.py` | Full pipeline E2E (106 assertions) |
| Scenarios | `tests/agent-test-scenarios.json` | 108 scenarios, 7 groups |
| Results | `tests/results/` | Timestamped JSON results |

### Groq Budget — Agentic Test Engine (qwen/qwen3-32b)
- **Model**: `qwen/qwen3-32b` via `https://api.groq.com/openai/v1/chat/completions`
- **Daily limit**: 500,000 TPD (tokens per calendar day — resets midnight UTC)
- **Per eval call**: ~2,000–3,200 tokens
- **Standard full run**: ~200K tokens (~40% of daily budget)
- **Premium full run**: ~270K tokens (~54% of daily budget)
- **Combined**: ~470K tokens — only fits if run back-to-back with no reruns
- **⚠️ NEVER run Standard before Premium if you need Premium to complete** — Standard uses 40% of budget first
- **429 symptoms**: wait times 400–550s per retry, 8 retries, then "ERR: Max retries exceeded" = TPD exhausted → wait until midnight UTC

### Groq Budget — Legacy Simulators (llama-4-scout)
- Model: `meta-llama/llama-4-scout-17b-16e-instruct`
- Rate: 30 req/min, 14,400 req/day, 30,000 TPM
- Standard full run: ~1,547 calls (10.7% daily)
- Premium full run: ~1,836 calls (12.8% daily)
- Combined: ~3,383 calls (23.5% daily) — fits comfortably in one day
