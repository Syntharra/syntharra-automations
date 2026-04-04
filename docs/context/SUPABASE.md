# Syntharra — Supabase
> Audited live on 2026-04-02. Updated with Dan's clarification on Premium table merge.
> Load when: querying tables, debugging data, writing to Supabase

## Connection
- Project URL: `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- REST base: `https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1`
- Anon key: safe client-side — RLS controls access
- Service role key: in `syntharra_vault` (requires service role to read vault)

## Tables — Verified Live (2026-04-02)

### Client & Call Data
| Table | Purpose | Status |
|---|---|---|
| `hvac_standard_agent` | **All client config — Standard AND Premium** (merged into one table) | ✓ Live |
| `hvac_call_log` | **All call records — Standard AND Premium** (single table) | ✓ Live |

> ⚠️ `hvac_premium_agent` and `hvac_premium_call_log` do NOT exist (404).
> Premium client config and call logs were merged into the Standard tables.
> Do not reference the premium-specific table names anywhere.

### Billing & Payments
| Table | Purpose | Status |
|---|---|---|
| `stripe_payment_data` | Checkout session + payment records | ✓ Live |
| `client_subscriptions` | Active subscription tracking | ✓ Live |
| `billing_cycles` | Monthly billing cycle records | ✓ Live |
| `overage_charges` | Usage overage tracking | ✓ Live |

### Ops & Intelligence
| Table | Purpose | Status |
|---|---|---|
| `syntharra_activation_queue` | Premium clients awaiting manual activation | ✓ Live |
| `transcript_analysis` | Daily AI transcript quality + jailbreak analysis | ✓ Live |
| `client_health_scores` | Weekly per-client health score records | ✓ Live |
| `infra_health_checks` | Admin dashboard infra test results | ✓ Live |
| `website_leads` | Demo page leads (written via anon key) | ✓ Live |

### Credentials
| Table | Purpose | Status |
|---|---|---|
| `syntharra_vault` | ALL API keys — requires service role key to read | ✓ Live (401 on anon) |

### Deleted — Do Not Reference
| Table/View | Notes |
|---|---|
| `hvac_premium_agent` | Merged into `hvac_standard_agent` |
| `hvac_premium_call_log` | Merged into `hvac_call_log` |
| `e2e_test_results` | Scaffolded but not created |
| `agent_test_results` | Dropped 2026-04-04 (0 rows, deprecated testing system) |
| `agent_test_run_summary` | View dropped 2026-04-04 (depended on agent_test_results) |
| `agent_pending_fixes` | Deleted with Agent Scenario Testing |

## Vault Lookup Pattern
```
GET /syntharra_vault?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value
Headers: apikey + Authorization Bearer — SERVICE ROLE KEY required
```

| service_name | key_type |
|---|---|
| `Retell AI` | `api_key` |
| `GitHub` | `personal_access_token` |
| `Railway` | `api_token` |
| `SMTP2GO` | `api_key` |
| `Groq` | `api_key` |
| `Supabase` | `service_role_key` |
| `Stripe` | `price_standard_monthly` (and other price/product IDs) |

## Key hvac_standard_agent Columns
`agent_id, company_name, agent_name, plan_type, client_email, timezone,
lead_phone, lead_email, services_offered, service_area, business_hours,
emergency_service, stripe_customer_id, subscription_id,
notification_email_2, notification_email_3, notification_sms_2, notification_sms_3`

## Key hvac_call_log Columns (49 total — audited 2026-04-04)

### Core call data
`id, call_id, agent_id, company_name, call_timestamp, created_at, call_tier,
duration_seconds, from_number, disconnection_reason, transcript`

### Retell system presets (from call_analysis root)
`retell_sentiment (TEXT — maps from user_sentiment), call_successful (BOOLEAN),
retell_summary (TEXT — maps from call_summary), recording_url, public_log_url,
latency_p50_ms, call_cost_cents`

### Retell custom post-call analysis (from call_analysis.custom_analysis_data)
`caller_name, caller_phone, caller_address, service_requested, job_type,
urgency, lead_score (INTEGER), is_lead (BOOLEAN), is_hot_lead (BOOLEAN),
transfer_attempted (BOOLEAN), transfer_success (BOOLEAN),
vulnerable_occupant (BOOLEAN), emergency (BOOLEAN), call_type,
notification_type, language, booking_attempted (BOOLEAN),
booking_success (BOOLEAN), notes, summary`

### n8n-computed fields (set by call processor workflow, not Retell)
`is_repeat_caller (BOOLEAN), repeat_call_count (INTEGER),
notification_sent (BOOLEAN), notification_priority`

### Geocoding (set by geocoding node downstream)
`geocode_status, geocode_formatted`

### Premium booking fields (from Premium post-call analysis)
`appointment_date, appointment_time, job_type_booked, booking_reference`

### Deprecated — do not write to
`caller_sentiment (INTEGER) — replaced by retell_sentiment (TEXT)`
