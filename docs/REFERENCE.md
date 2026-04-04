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
