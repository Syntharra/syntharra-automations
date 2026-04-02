# Syntharra — Supabase
> Load when: querying tables, debugging data, adding columns

## Connection
- Project URL: `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- REST base: `https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1`
- Anon key: safe client-side (RLS controls access)
- Service role key: in `syntharra_vault` table

## Tables
| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Standard client config + agent settings |
| `hvac_premium_agent` | Premium client config (+ OAuth tokens, calendar, CRM) |
| `hvac_call_log` | Standard call records |
| `hvac_premium_call_log` | Premium call records (bookings, hot leads, repeat callers) |
| `stripe_payment_data` | Checkout session data |
| `client_subscriptions` | Active subscription tracking |
| `billing_cycles` | Monthly billing cycle records |
| `overage_charges` | Usage overage tracking |
| `website_leads` | Demo page leads |
| `syntharra_vault` | **ALL API keys** — query by `service_name` + `key_type` |
| `infra_health_checks` | Admin dashboard infra test results |
| `e2e_test_results` | Admin dashboard E2E test results |
| `syntharra_activation_queue` | Premium clients awaiting activation |

## Key hvac_call_log columns
`agent_id, call_id, company_name, created_at, caller_name, caller_phone, caller_address,
service_requested, job_type, urgency, lead_score, is_lead, call_tier, caller_sentiment,
summary, notes, transfer_attempted, transfer_success, vulnerable_occupant,
geocode_status, geocode_formatted, duration_seconds`

## Vault lookup pattern
```javascript
GET /syntharra_vault?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value
Headers: apikey + Authorization Bearer (service role key)
```

## Removed tables (do not reference)
- `agent_test_run_summary` — removed with Agent Scenario Testing
- `agent_test_results` — removed with Agent Scenario Testing  
- `agent_pending_fixes` — removed with Agent Scenario Testing
