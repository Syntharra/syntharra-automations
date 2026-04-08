# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

_(none — all P0 items shipped 2026-04-08)_

## P1

- **Update website pricing page** — single product $697/mo, remove tier comparison table
- **Update n8n onboarding workflow** — remove Premium branch, single flow only
- **Update welcome email template** — remove tier-specific language, single product messaging
- **Move Brevo API key to Supabase vault** — currently hardcoded in n8n workflow node
- **Stripe live mode** — add live secret key to vault, create $697/mo live price (test price created: `price_1TK5b1ECS71NQsk8Ru3Gyybl`)

## Notes

- n8n webhook `/webhook/agent-test-runner` is INACTIVE (404). Do not retry.
- Dashboard URL: `https://syntharra.com/dashboard.html?a=<agent_id>`
- Retell proxy: `POST https://n8n.syntharra.com/webhook/retell-calls` `{ "agent_id": "..." }` — LIVE (n8n workflow `Y1EptXhOPAmosMbs`)
- Jotform Standard form `260795139953066` — already Standard-only, no tier field exists
- Stripe test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` = $697/mo on `prod_UC0hZtntx3VEg2`. Old prices archived.
