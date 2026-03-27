# Supabase Schema — LIVE

## hvac_standard_agent
Client configuration table. One row per onboarded HVAC client.

Key columns:
- agent_id, conversation_flow_id — Retell references
- transfer_phone — general transfer destination (q48)
- emergency_phone — emergency transfer destination (q21)
- after_hours_transfer — 'all' | 'emergency_only' | 'never' (q63, default 'all')
- notification_email_2/3, notification_sms_2/3 — multi-notification
- All Jotform fields stored directly

## hvac_call_log
Call records with GPT analysis.

Key columns:
- call_id, agent_id, company_name
- caller_name, caller_phone, caller_address
- service_requested, lead_score, is_lead, call_tier, urgency
- job_type, vulnerable_occupant, caller_sentiment
- transfer_attempted (bool) — did the agent try to transfer?
- transfer_success (bool/null) — did the transfer connect?
- geocode_status, geocode_formatted
- duration_seconds, summary, notes, transcript

## stripe_payment_data
Checkout session data from Stripe webhook.

## client_subscriptions, billing_cycles, overage_charges
Billing and usage tracking tables.
