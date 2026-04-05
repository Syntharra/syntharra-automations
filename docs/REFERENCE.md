# Syntharra — Reference Data
> Static reference: agent IDs, flow IDs, simulator commands, workflow counts.
> This file does not track tasks — see TASKS.md for open work.
> Updated when IDs change or new agents are added.

---

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | ✅ Synced with MASTER |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 TESTING ONLY — not promoted, testing incomplete |
| HVAC Premium (DEMO) | `agent_80d6270ab39ed3169f997cb035` | 🧪 Enhancement testing |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Conversation Flow Registry
| Flow | ID | Bound to |
|---|---|---|
| HVAC Premium (MASTER) | `conversation_flow_1dd3458b13a7` | Premium MASTER agent |
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
| transfer_failed | `conversation_flow_component_183320e7b210` |
| ending | `conversation_flow_component_801ba4098915` |
| existing_customer | `conversation_flow_component_d8eff9881e16` |
| spam_robocall | `conversation_flow_component_d23e204deb4f` |
| identify_call | `conversation_flow_component_ebac0db129f3` |
| general_questions | `conversation_flow_component_d46848148d1d` |
| fallback_leadcapture | `conversation_flow_component_e6879f7849ab` |
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
| Agentic Test Engine | `tools/agentic-test-fix.py` | Full scenario suite + triage + self-fix |
| Standard Simulator | `tools/openai-agent-simulator.py` | Legacy per-scenario pass/fail |
| Premium Simulator | `tools/openai-agent-simulator-premium.py` | Legacy per-scenario pass/fail (Premium) |
| Standard E2E | `shared/e2e-test.py` | Full pipeline E2E (93 assertions) |
| Premium E2E | `shared/e2e-test-premium.py` | Full pipeline E2E (106 assertions) |
| Scenarios | `tests/agent-test-scenarios.json` | 108 scenarios, 7 groups |
| Results | `tests/results/` | Timestamped JSON results |

### Groq Budget (free tier)
- Model: `meta-llama/llama-4-scout-17b-16e-instruct`
- Rate: 30 req/min, 14,400 req/day, 30,000 TPM
- Standard full run: ~1,547 calls (10.7% daily)
- Premium full run: ~1,836 calls (12.8% daily)
- Combined: ~3,383 calls (23.5% daily) — fits comfortably in one day
