# State — Syntharra Automations

_Last updated: 2026-04-09_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
5720caa chore(session): auto-backup local changes 2026-04-09

## Go-live checklist
see docs/TASKS.md

---

## Product decision (2026-04-09)

Single product: **HVAC Standard at $697/mo**. Premium tier retired. One agent, one onboarding flow, one price.
Repo stripped to lean core. retell-iac is Standard-only.

---

## What's live in production

- **HVAC Standard agent** — MASTER at `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`. Agent ID `agent_4afbfdb3fcb1ba9569353af28d`, flow `conversation_flow_34d169608460`. retell-iac is the canonical source of truth for all changes.
- **n8n onboarding workflow** — Standard `4Hx7aRdzMl5N0uJP`. Received `submission_id` fix 2026-04-07.
- **n8n call processor** — Standard variant, active.
- **Supabase schema** — RLS hardened 2026-04-07. `hvac_standard_agent` and `hvac_call_log` are the live tables.
- **Client dashboard** — `dashboard.html` in syntharra-website (SHA: b0603b6e). Retell-native: fetches calls via POST `n8n.syntharra.com/webhook/retell-calls`. Company info from Supabase. URL param `?a=AGENT_ID`.
- **Retell proxy webhook** — n8n `POST /webhook/retell-calls` LIVE (workflow `Y1EptXhOPAmosMbs`). Returns `{ calls: [...] }` with all required Retell fields. E2E tested 2026-04-08.
- **OAuth server** — Railway-deployed.
- **Stripe** — still in test mode. Live-mode migration is a P0 blocker (see TASKS.md).

## What's in flight

- **Stripe live mode** — test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` ($697/mo) created and old prices archived. Live key not yet in vault. P0 blocker pending Dan's timeline.

## What's blocked

- **Telnyx SMS** — waiting on Telnyx AI evaluation approval.

## Architecture invariants (do not violate)

- **retell-iac is the source of truth for the agent.** No manual Retell dashboard edits to MASTER.
- **MASTER templates are the only thing in the repo.** Per-client clones live in Supabase `client_agents`.
- **IDs come from `docs/REFERENCE.md` only.** Never inline.
- **Never test on a live Retell agent.** Clone → TESTING → `retell-iac/scripts/promote.py` → live.
