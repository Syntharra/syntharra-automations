# Onboarding & Agent Creation — Canonical Standard
_Effective: 2026-04-06. Supersedes all prior onboarding notes._

This is the **only** supported path to create a Syntharra client agent. No bypasses.

## 1. Sources of Truth
| Layer | Location | Rule |
|---|---|---|
| Flow IaC | `retell-iac/` (this repo) | All flow changes start here. Never edit a MASTER directly in the Retell UI. |
| n8n pipeline | workflows `4Hx7aRdzMl5N0uJP` (Std) / `kz1VmwNccunRMEaF` (Prem) | All client config flows from Jotform through these workflows. |
| Client DB | Supabase `hvac_standard_agent` table | Written exclusively by the onboarding workflows. No manual inserts. |
| Secrets | Supabase `syntharra_vault` | All API keys live here, pulled server-side only. |

## 2. MASTER Agents (clone sources)
| Tier | Master Agent ID | Flow ID | Notes |
|---|---|---|---|
| Standard | `agent_4afbfdb3fcb1ba9569353af28d` | `conversation_flow_34d169608460` | Promoted 2026-04-06 from TESTING. |
| Premium  | `agent_2cffe3d86d7e1990d08bea068f` | `conversation_flow_2ded0ed4f808` | Interim — TESTING agent serving as MASTER until post-launch. |

Both are locked for manual edits. Changes go via `retell-iac/` → `scripts/build_agent.py` → `scripts/diff.py` round-trip → `scripts/promote.py`.

## 3. Onboarding Pipeline (per client)
```
Jotform submission (q4–q67)
   │
   ▼
n8n onboarding workflow (Standard or Premium)
   │
   ├─ Parse Jotform Data (v5)
   ├─ Build Retell Prompt (global prompt + company info block)
   ├─ Create Retell LLM
   ├─ Clone Retell Agent  ◄── clones from MASTER above
   ├─ Merge LLM + Agent Data
   ├─ Write Client Data → hvac_standard_agent
   ├─ Reconcile Stripe Payment
   ├─ Validate Token Budget
   ├─ Purchase Phone Number (Twilio today → Telnyx post-migration)
   ├─ Publish Retell Agent
   ├─ HubSpot — Update Deal → Active
   ├─ Slack notification
   └─ Send "You're Live" email
```

## 4. Greeting Fallback (both tiers)
If the client leaves the Jotform custom greeting field blank, the workflow auto-builds:
```
{company_name}, this is {agent_name} speaking, how may I assist you?
```
Never persist an empty `custom_greeting`.

## 5. Spanish Handling
Spanish routing is **not** part of the flow. It is excluded at build time (`retell-iac/manifests/hvac-standard.yaml` + `hvac-premium.yaml` → `excluded: [spanish_routing_node]`). Retell native multilingual handles Spanish callers inline.

## 6. Phone Number Provisioning
### Current (Twilio)
- Only active Syntharra line: `+18129944371` (sales + demo, burning down Twilio credit).
- No per-client Twilio auto-purchase in production until Telnyx swap lands.

### Target (Telnyx) — post-migration
- Supabase vault: `service_name='Telnyx', key_type='api_key'`.
- Onboarding auto-purchases on every new client:
  1. `GET /v2/available_phone_numbers?filter[country_code]=US&filter[locality]={client_city}&filter[features][]=voice&filter[features][]=sms`
  2. `POST /v2/number_orders` with `phone_numbers: [{phone_number: <selected>}]`
  3. `PATCH /v2/phone_numbers/{id}` → `voice.connection_id = <Retell SIP connection id>`
- Auth on all three: `Authorization: Bearer <vault key>`.
- Telnyx becomes the permanent provider the day it ships. Twilio is retired.

## 7. Backups & Rollback
- Any MASTER edit must be preceded by a snapshot in `retell-iac/snapshots/YYYY-MM-DD_<label>/flow.json`.
- Git tag baseline before `promote.py --live`.
- Rollback = re-run `promote.py` with a previous baseline tag.

## 8. Forbidden
- Hand-editing MASTER agents in the Retell UI.
- Direct Retell API PATCHes bypassing `retell-iac/`.
- Direct Supabase inserts into `hvac_standard_agent`.
- Adding phone providers other than Telnyx (once Telnyx is live).
- Creating new Premium MASTER without updating `promote.py` + this doc.
- Using `daniel@syntharra.com` in any automated send.

## 9. Change Log
- 2026-04-06 — Canonical standard adopted. Premium TESTING declared interim MASTER. `+12292672271` decommissioned.
