# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

_(none — all P0 items shipped 2026-04-08)_

## P1

- **Stripe live mode** — add live secret key to vault, create $697/mo live price (test price created: `price_1TK5b1ECS71NQsk8Ru3Gyybl`)

## Completed (2026-04-09)

- ~~Update website pricing page~~ — `plan-quiz.html` updated: single product $697/mo, Premium tier removed, quiz always returns Standard, JSON-LD updated
- ~~Update n8n onboarding workflow~~ — Premium onboarding (`kz1VmwNccunRMEaF`) deactivated; Standard workflow has no Premium branch
- ~~Update welcome email template~~ — `Send Welcome Email` node: removed "Standard Tier" comment, removed unused `PLAN_NAME` + dead `hasCRM`/`hasCal` vars
- ~~Move Brevo API key to Supabase vault~~ — `Send Setup Instructions Email` + `Send Welcome Email` nodes now fetch from `syntharra_vault` (Brevo/api_key)

## Notes

- n8n webhook `/webhook/agent-test-runner` is INACTIVE (404). Do not retry.
- Dashboard URL: `https://syntharra.com/dashboard.html?a=<agent_id>`
- Retell proxy: `POST https://n8n.syntharra.com/webhook/retell-calls` `{ "agent_id": "..." }` — LIVE (n8n workflow `Y1EptXhOPAmosMbs`)
- Jotform Standard form `260795139953066` — already Standard-only, no tier field exists
- Stripe test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` = $697/mo on `prod_UC0hZtntx3VEg2`. Old prices archived.
