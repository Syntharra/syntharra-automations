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

### client_subscriptions — Phase 0 additions (2026-04-11)
Migration: `supabase/migrations/20260411_phase0_pilot_schema.sql`
Rollback: `supabase/migrations/20260411_phase0_pilot_schema_rollback.sql`

New columns (all additive, safe defaults):
- `pilot_mode` (boolean, NOT NULL, default false) — true for 14-day free pilot rows
- `pilot_started_at`, `pilot_ends_at` (timestamptz, nullable) — pilot window
- `pilot_minutes_allotted` (int, NOT NULL, default 0) — 200 for pilots
- `pilot_minutes_used` (int, NOT NULL, default 0) — updated by pilot_lifecycle.py
- `payment_method_added_at` (timestamptz, nullable) — day Stripe setup intent succeeded
- `first_touch_asset_id`, `last_touch_asset_id` (text, nullable) — attribution IDs
- `first_touch_utm`, `last_touch_utm` (jsonb, nullable) — full UTM objects

Extended CHECK constraint on `status`:
- Old: `CHECK (status IN ('active', 'paused', 'cancelled', 'past_due'))`
- **New: `CHECK (status IN ('active', 'paused', 'cancelled', 'past_due', 'pilot', 'expired'))`**
- `'pilot'` = active pilot in its 14-day window
- `'expired'` = day-14 elapsed, no card, Retell agent paused, win-back sequence firing
- Flips to `'active'` on day-14 successful conversion

Partial indexes:
- `idx_client_subscriptions_pilot_active` on `pilot_ends_at` WHERE `pilot_mode=true`
- `idx_client_subscriptions_first_touch_asset` on `first_touch_asset_id` WHERE NOT NULL

### Billing tool isolation
`tools/monthly_minutes.py` and `tools/usage_alert.py` both filter on `status=eq.active&pilot_mode=eq.false` — belt-and-suspenders isolation so pilot rows never get billed.

## marketing_events (Phase 0, 2026-04-11)
Unified event log for all marketing-driven events across channels.
Every VSL play, CTA click, form submission, email open, conversion, and expiration writes a row.
Phase 3 Optimizer reads from here for attribution and learning.

Columns:
- `id` (uuid PK), `created_at` (timestamptz)
- `session_id` (NOT NULL), `visitor_id`, `client_agent_id` (all text)
- `event_type` (NOT NULL), `asset_id`
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- `referrer`, `user_agent`, `ip_country`, `ip_region`
- `metadata` (jsonb)

Indexes: visitor+time, asset+event_type, client_agent_id, event_type+time
RLS: service_role only (no anon reads)

## marketing_assets (Phase 0, 2026-04-11)
Registry of every trackable piece of marketing content (VSL, videos, emails, ads).
Every asset gets a UUID used as `stx_asset_id` in URL parameters.
Attribution joins `marketing_events.asset_id` → `marketing_assets.id` to trace revenue to content.

Columns:
- `id` (text PK, UUID as text), `created_at` (timestamptz)
- `asset_type` (NOT NULL): 'vsl', 'short_video', 'email_sequence', 'email_variant', 'landing_page', 'dm_template', 'cold_call_script'
- `title` (NOT NULL, text), `channel` (text)
- `platform_asset_url` (text), `variant_of` (text, self-FK)
- `metadata` (jsonb), `retired_at` (timestamptz)

RLS: service_role only

## pilot_email_sends (Phase 0, 2026-04-11)
Idempotency log for `tools/pilot_lifecycle.py` cron.
Prevents duplicate day-3/7/12/expired/converted/winback emails if the cron runs twice on the same day.

Columns:
- `id` (bigserial PK), `client_agent_id`, `email_key`, `sent_at`, `brevo_message_id`
- UNIQUE constraint on `(client_agent_id, email_key)` = the idempotency guarantee

RLS: service_role only
