# Syntharra — Agents & Retell
> Audited live from Retell API on 2026-04-02. Update from live API, not memory.
> Load when: Retell agents, call processing, phone numbers, conversation flows, Jotform

## Retell API
- Base URL: `https://api.retellai.com`
- API key: query `syntharra_vault` → `service_name = 'retell'` (never hardcode)

## Live Agents
| Agent | ID | Purpose | Status |
|---|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | Standard master template | ✅ MASTER — do not modify |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | Premium master template | ✅ MASTER — do not modify |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | Standard prompt fix testing | 🧪 TESTING — active |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | Premium prompt fix testing | 🧪 TESTING — pending fixes |
| Syntharra Demo Agent (Female) | `agent_2723c07c83f65c71afd06e1d50` | Demo / sales use | ✅ Live |
| Syntharra Demo Agent (Male) | `agent_b9d169e5290c609a8734e0bb45` | Demo / sales use | ✅ Live |

## Conversation Flows
| Flow | ID | Linked To |
|---|---|---|
| Standard Master | `conversation_flow_34d169608460` | HVAC Standard Template (MASTER) |
| Premium Master | `conversation_flow_1dd3458b13a7` | HVAC Premium Template (MASTER) |
| Standard TESTING | `conversation_flow_5b98b76c8ff4` | HVAC Standard (TESTING) |
| Premium TESTING | `conversation_flow_2ded0ed4f808` | HVAC Premium (TESTING) |

## Testing Protocol
- Apply all prompt changes to TESTING agents/flows ONLY
- Verify fixes pass 95-scenario suite on TESTING agent
- Once confirmed: patch fixes onto MASTER flows, publish MASTER agents
- NEVER delete old master flows — keep as backup
| Syntharra Demo Agent (Female) | `agent_2723c07c83f65c71afd06e1d50` | Demo / sales use |
| Syntharra Demo Agent (Male) | `agent_b9d169e5290c609a8734e0bb45` | Demo / sales use |

## Phone Numbers (Retell)
| Number | Assigned Agent | Notes |
|---|---|---|
| `+18129944371` | UNASSIGNED ⚠️ | Unassigned — wire to HVAC Standard template agent |
| `+12292672271` | UNASSIGNED | Demo line (nickname: DEMO) |

⚠️ **Action needed:** `+18129944371` shows as unassigned in Retell. Verify it is correctly
wired to `agent_4afbfdb3fcb1ba9569353af28d` via Retell dashboard or API.

## Live Conversation Flow (Standard)
- ID: `conversation_flow_34d169608460`
- Agent: HVAC Standard Template
- Nodes (12): greeting, identify_call, nonemergency_leadcapture, verify_emergency,
  callback, existing_customer, general_questions, spam_robocall,
  Transfer Call, transfer_failed, Ending, End Call
- New client flows: 12 nodes (callback + spam_robocall restored 2026-04-02)
- Transfer number: `+18563630633`

> Note: 50 total conversation flows exist in Retell — all others are old test/dev flows.
> Only `conversation_flow_34d169608460` is wired to a live agent.
> Mia agent DELETED 2026-04-02.

## Jotform Forms
| Form | ID | Status |
|---|---|---|
| Standard onboarding | `260795139953066` | ENABLED ✓ |
| Premium onboarding | `260819259556671` | ENABLED ✓ |
| v2 Standard (old) | `260812373840657` | DELETED — do not reference |
| HVAC Checklist (old) | `260748804230051` | DELETED — do not reference |

- Jotform API key: `18907cfb3b4b3be3ac47994683148728` (account: Blackmore_Daniel)
- **Always use REST API directly** — Jotform MCP connector is broken
- Webhook path: `/webhook/jotform-hvac-onboarding` on `n8n.syntharra.com`

## Retell Critical Rules
- **NEVER delete or recreate a Retell agent** — agent_id is foreign key across Retell, Supabase, call processor, phone
- **ALWAYS publish after any agent update:** `POST https://api.retellai.com/publish-agent/{agent_id}`
- Demo agents must always stay published
- If new agent created: update Supabase client record, phone assignment, and n8n in same operation
