# Supabase Migrations

All schema changes are applied via Supabase MCP directly.
This folder documents the current schema state.

## Tables
- `hvac_standard_agent` — Client config, one row per client
- `hvac_call_log` — Every call logged here, unique constraint on call_id
- `stripe_payment_data` — Stripe checkout payment records
- `client_subscriptions` — Subscription plan details
- `billing_cycles` — Monthly usage tracking
- `overage_charges` — Overage billing records
- `agreement_signatures` — E-signature records
- `website_leads` — Website lead captures
