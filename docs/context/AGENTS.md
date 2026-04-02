# Syntharra — Agents & Retell
> Load when: working on Retell agents, call processing, phone numbers, conversation flows

## Live Agents
| Agent | ID | Phone |
|---|---|---|
| Arctic Breeze HVAC (Standard client) | `agent_4afbfdb3fcb1ba9569353af28d` | `+18129944371` |
| Demo — Jake | `agent_b9d169e5290c609a8734e0bb45` | — |
| Demo — Sophie | `agent_2723c07c83f65c71afd06e1d50` | — |

- Arctic Breeze transfer number: `+18563630633`
- Live conversation flow: `conversation_flow_34d169608460`
- Flow nodes (12): greeting, identify_call, nonemergency_leadcapture, verify_emergency, callback, existing_customer, general_questions, spam_robocall, Transfer Call, transfer_failed, Ending, End Call
- API key: `key_0157d9401f66cfa1b51fadc66445`

## Critical Rules
- NEVER delete or recreate a Retell agent — agent_id is the foreign key across Retell, Supabase, call processor, phone
- ALWAYS publish after any agent update: `POST https://api.retellai.com/publish-agent/{agent_id}`
- Demo agents (Jake, Sophie) must always stay published
- If new agent ever created: update Supabase agent_id, phone, and n8n in same operation

## Jotform Forms
| Form | ID |
|---|---|
| Standard onboarding | `260795139953066` |
| Premium onboarding | `260819259556671` |
- API key: `18907cfb3b4b3be3ac47994683148728`
- Use REST API directly — Jotform MCP connector is broken
