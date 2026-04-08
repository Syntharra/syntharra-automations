# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

- **Wire Retell proxy webhook in n8n** (`POST /webhook/retell-calls`)
  Fetch call list from Retell API using vault key (`service_name='Retell'`), return array to dashboard.
  Response should match `/v2/list-calls` shape: `call_id`, `start_timestamp`, `end_timestamp`, `duration_ms`, `call_status`, `transcript`, `recording_url`, `call_analysis.call_summary`, `call_analysis.user_sentiment`.

- **Update Stripe to single product at $697/mo**
  Retire old Standard and Premium price IDs. Create one product, one price. Update n8n webhook to use new price ID. Verify in Stripe dashboard (currently test mode).

- **Update Jotform onboarding form**
  Remove tier selection field. Single product flow only. Confirm all required fields still present.

## P1

- **Update website pricing page** — single product $697/mo, remove tier comparison table
- **Update n8n onboarding workflow** — remove Premium branch, single flow only
- **Update welcome email template** — remove tier-specific language, single product messaging
- **Move Brevo API key to Supabase vault** — currently hardcoded in n8n workflow node

## Notes

- n8n webhook `/webhook/agent-test-runner` is INACTIVE (404). Do not retry.
- Dashboard URL: `https://syntharra.com/dashboard.html?a=<agent_id>`
- Retell proxy: `POST https://n8n.syntharra.com/webhook/retell-calls` `{ "agent_id": "..." }`
