# Syntharra — Supabase
> Audited live on 2026-04-02. Tables verified by direct REST call.
> Load when: querying tables, debugging data, writing to Supabase

## Connection
- Project URL: `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- REST base: `https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1`
- Anon key: safe client-side — RLS controls access
- Service role key: in `syntharra_vault` table (requires service role to read)

## Tables — Verified Live ✓
| Table | Purpose | Verified |
|---|---|---|
| `hvac_standard_agent` | Standard client config + agent settings | ✓ |
| `hvac_call_log` | Standard call records | ✓ |
| `stripe_payment_data` | Checkout session + payment data | ✓ |
| `client_subscriptions` | Active subscription tracking | ✓ |
| `billing_cycles` | Monthly billing cycle records | ✓ |
| `overage_charges` | Usage overage tracking | ✓ |
| `website_leads` | Demo page leads (written via anon key) | ✓ |
| `infra_health_checks` | Admin dashboard infra test results | ✓ |
| `syntharra_activation_queue` | Premium clients awaiting activation | ✓ |
| `transcript_analysis` | Daily AI transcript quality analysis | ✓ |
| `client_health_scores` | Weekly client health score records | ✓ |

## Tables — Not Found (404) ⚠️
| Table | Notes |
|---|---|
| `hvac_premium_agent` | 404 — may be named differently or not yet created |
| `hvac_premium_call_log` | 404 — may be named differently or not yet created |
| `e2e_test_results` | 404 — was scaffolded but table not created in Supabase |

> **Action needed:** Confirm correct table names for Premium agent + call log with Dan.
> The Premium pipeline workflows reference these tables — if named differently, queries will fail silently.

## Vault — All API Keys
Table: `syntharra_vault` — requires **service role key** to read (anon key returns 401).

```
GET /syntharra_vault?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value
Headers: apikey + Authorization Bearer (service role key only)
```

| service_name | key_type | What it is |
|---|---|---|
| `Retell AI` | `api_key` | Retell API key |
| `GitHub` | `personal_access_token` | GitHub PAT |
| `Railway` | `api_token` | Railway API token |
| `SMTP2GO` | `api_key` | SMTP2GO API key |
| `Groq` | `api_key` | Groq LLM API key |
| `Supabase` | `service_role_key` | Full admin key |
| `Stripe` | `price_standard_monthly` | etc. — see STRIPE.md |

## Key hvac_standard_agent Columns
`agent_id, company_name, agent_name, plan_type, client_email, timezone,
lead_phone, lead_email, services_offered, service_area, business_hours,
emergency_service, stripe_customer_id, subscription_id,
notification_email_2, notification_email_3, notification_sms_2, notification_sms_3`

## Key hvac_call_log Columns
`agent_id, call_id, company_name, created_at, caller_name, caller_phone,
caller_address, service_requested, job_type, urgency, lead_score, is_lead,
call_tier, caller_sentiment, summary, notes, transfer_attempted,
transfer_success, vulnerable_occupant, geocode_status, geocode_formatted,
duration_seconds`

## Removed Tables (do not reference)
- `agent_test_run_summary` — deleted with Agent Scenario Testing
- `agent_test_results` — deleted with Agent Scenario Testing
- `agent_pending_fixes` — deleted with Agent Scenario Testing
