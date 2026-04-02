# Syntharra — Live Agent Backups
> Last backed up: 2026-04-02
> All files are live snapshots from Retell API. Do not edit manually — push via Retell API then back up.

## Live Agents

| File | Agent ID | Name | Voice | Purpose |
|---|---|---|---|---|
| `hvac-standard-arctic-breeze_agent_4afbfdb3fcb1ba9569353af28d_LIVE.json` | `agent_4afbfdb3fcb1ba9569353af28d` | HVAC Standard | retell-Sloane | Arctic Breeze test client — Standard pipeline |
| `hvac-premium-v7-frostking_agent_9822f440f5c3a13bc4d283ea90_LIVE.json` | `agent_9822f440f5c3a13bc4d283ea90` | V7 Premium FrostKing | retell-Nico | Premium test client — V7 most current |
| `demo-male_agent_b9d169e5290c609a8734e0bb45_LIVE.json` | `agent_b9d169e5290c609a8734e0bb45` | Demo Agent (Male) | retell-Nico | Sales demo — must stay published |
| `demo-female_agent_2723c07c83f65c71afd06e1d50_LIVE.json` | `agent_2723c07c83f65c71afd06e1d50` | Demo Agent (Female) | retell-Sloane | Sales demo — must stay published |
| `conversation_flow_34d169608460_LIVE.json` | `conversation_flow_34d169608460` | Standard Flow | — | 14-node Standard conversation flow — Arctic Breeze |

## Critical Rules
- **NEVER delete or recreate a Retell agent** — agent_id is the foreign key across Retell, Supabase, call processor, and phone number
- **ALWAYS publish after any agent update:** `POST https://api.retellai.com/publish-agent/{agent_id}`
- After ANY change to an agent, back up the new JSON to this folder
- Premium agent (V7 FrostKing) is the most current — this is the template for new Premium clients

## Phone Numbers
| Number | Agent | Status |
|---|---|---|
| `+18129944371` | Arctic Breeze Standard | ⚠️ Shows UNASSIGNED in Retell — verify wired |
| `+12292672271` | Unassigned | Demo line |
| Transfer: `+18563630633` | — | Arctic Breeze transfer destination |

## How to restore an agent from backup
```python
import requests, json
data = json.load(open("hvac-standard-arctic-breeze_agent_4afbfdb3fcb1ba9569353af28d_LIVE.json"))
requests.patch(
    f"https://api.retellai.com/update-agent/{data['agent_id']}",
    headers={"Authorization": "Bearer key_0157d9401f66cfa1b51fadc66445"},
    json={k: v for k, v in data.items() if k not in ["agent_id","last_modification_timestamp"]}
)
# Then always publish:
requests.post(f"https://api.retellai.com/publish-agent/{data['agent_id']}",
    headers={"Authorization": "Bearer key_0157d9401f66cfa1b51fadc66445"})
```
