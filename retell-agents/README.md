# Retell Agents — Reference Archive (Pre-Git-IaC)

> ⚠️ **NOT the source of truth.** As of 2026-04-06, Retell agent management is canonically handled in `/retell-iac/`.
> This directory holds legacy reference templates and dated backups only. Do not modify production agents from here.
> Source-of-truth: `/retell-iac/manifests/*.yaml` → `scripts/build_agent.py` → `scripts/promote.py`

---

# retell-agents/

This folder is the source of truth for all Syntharra Retell agents and conversation flows.

## Master Templates

| File | Purpose |
|---|---|
| `HVAC-STANDARD-AGENT-TEMPLATE.md` | **← START HERE** Canonical Standard HVAC agent spec — 12 nodes, all Supabase fields, E2E assertions |
| `hvac-standard-MASTER-TEMPLATE.json` | Lightweight JSON reference (node IDs + source workflow) |

## Live Agent Backups (do not edit — auto-backed up)

| File | Agent | Notes |
|---|---|---|
| `hvac-standard-arctic-breeze_agent_4afbfdb3fcb1ba9569353af28d_LIVE.json` | Arctic Breeze HVAC Standard | Live test client — 14 nodes (has emergency_fallback + spanish_routing) |
| `conversation_flow_34d169608460_LIVE.json` | Arctic Breeze conversation flow | Full 14-node flow backup |
| `hvac-premium-v7-frostking_agent_9822f440f5c3a13bc4d283ea90_LIVE.json` | FrostKing Premium | Premium test client |
| `demo-female_agent_2723c07c83f65c71afd06e1d50_LIVE.json` | Syntharra Demo (Sophie) | Sales demo — do not modify |
| `demo-male_agent_b9d169e5290c609a8734e0bb45_LIVE.json` | Syntharra Demo (Jake) | Sales demo — do not modify |

## Archive

`archive/` — canonical JS node code from n8n, snapshotted at each major version.

| File | Contents |
|---|---|
| `node-code-parse-jotform-v5.js` | Parse JotForm Data node (maps all 52 Jotform fields) |
| `node-code-build-retell-prompt-v5.js` | Build Retell Prompt node (generates 12-node flow + agent config) |
| `node-code-merge-llm-agent-v5.js` | Merge LLM & Agent Data node (Supabase payload assembly) |

## Rules

- **NEVER delete or recreate a live Retell agent** — agent_id is a foreign key across Retell, Supabase, n8n, and phone numbers
- **ALWAYS publish after any agent update** — use n8n workflow `13cOIXxvj83NfDqQ` (Publish Retell Agent)
- **New client agents** are created by n8n onboarding workflow `4Hx7aRdzMl5N0uJP` — they get the 12-node Standard template
- **Arctic Breeze** (agent_4afbfdb3fcb1ba9569353af28d) is the live test client — has 2 extra nodes vs new clients (emergency_fallback, spanish_routing)
- **To update the master template:** edit n8n workflow → run E2E test → re-export node code to archive/ → update HVAC-STANDARD-AGENT-TEMPLATE.md
