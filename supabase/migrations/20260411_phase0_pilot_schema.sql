-- 2026-04-11 — Phase 0 — VSL + Pilot Funnel + Measurement Spine
-- Spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md
-- Plan: docs/superpowers/plans/2026-04-11-phase-0-vsl-funnel-implementation.md
-- Scan: docs/audits/2026-04-11-phase0-schema-scan.md
--
-- MIGRATION BRANCH SELECTED: BRANCH B
-- Reason: client_subscriptions.status is TEXT with an existing CHECK constraint
--   `client_subscriptions_status_check`:
--     CHECK ((status = ANY (ARRAY['active'::text, 'paused'::text, 'cancelled'::text, 'past_due'::text])))
-- Strategy: drop the old constraint, add a new one including 'pilot' and 'expired'.
-- Fully reversible — paired rollback at 20260411_phase0_pilot_schema_rollback.sql.
--
-- What this migration adds:
--   - 10 new columns on client_subscriptions (all nullable or with safe defaults)
--   - New CHECK constraint allowing 'pilot' and 'expired' status values
--   - 2 new partial indexes on client_subscriptions
--   - marketing_events table + RLS + service_role policy + indexes
--   - marketing_assets table + RLS + service_role policy + indexes
--   - pilot_email_sends idempotency log + RLS + service_role policy
--
-- Safety:
--   - All new columns are additive (IF NOT EXISTS). Existing rows receive
--     defaults that are semantically neutral for paid customers
--     (pilot_mode=false, pilot_minutes_allotted=0, etc.).
--   - New CHECK constraint is a strict superset of the old one (old values
--     still allowed, plus two new ones).
--   - No data mutation on existing rows.
--   - n8n scan confirmed zero workflows will break (see scan report).
--   - Billing tools (monthly_minutes.py, usage_alert.py) will be patched
--     immediately after this migration in Task 9 with a defensive
--     pilot_mode=eq.false filter.

begin;

-- =======================================================================
-- Part 1: client_subscriptions — new columns + new CHECK constraint
-- =======================================================================

-- 1a. Drop the old status check constraint
alter table public.client_subscriptions
  drop constraint if exists client_subscriptions_status_check;

-- 1b. Add the new check constraint with 'pilot' and 'expired' included
alter table public.client_subscriptions
  add constraint client_subscriptions_status_check
  check (status = any (array[
    'active'::text,
    'paused'::text,
    'cancelled'::text,
    'past_due'::text,
    'pilot'::text,
    'expired'::text
  ]));

-- 1c. Add the 10 pilot + attribution columns
alter table public.client_subscriptions
  add column if not exists pilot_mode boolean not null default false,
  add column if not exists pilot_started_at timestamptz,
  add column if not exists pilot_ends_at timestamptz,
  add column if not exists pilot_minutes_allotted integer not null default 0,
  add column if not exists pilot_minutes_used integer not null default 0,
  add column if not exists payment_method_added_at timestamptz,
  add column if not exists first_touch_asset_id text,
  add column if not exists last_touch_asset_id text,
  add column if not exists first_touch_utm jsonb,
  add column if not exists last_touch_utm jsonb;

-- 1d. Partial indexes for common pilot queries
create index if not exists idx_client_subscriptions_pilot_active
  on public.client_subscriptions (pilot_ends_at)
  where pilot_mode = true;

create index if not exists idx_client_subscriptions_first_touch_asset
  on public.client_subscriptions (first_touch_asset_id)
  where first_touch_asset_id is not null;

-- =======================================================================
-- Part 2: marketing_events — unified event log
-- =======================================================================

create table if not exists public.marketing_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  -- Identity
  session_id text not null,
  visitor_id text,
  client_agent_id text,

  -- Event
  event_type text not null,
  asset_id text,

  -- Attribution
  utm_source text,
  utm_medium text,
  utm_campaign text,
  utm_content text,
  utm_term text,
  referrer text,

  -- Context
  user_agent text,
  ip_country text,
  ip_region text,
  metadata jsonb
);

comment on table public.marketing_events is
  'Phase 0 unified event log. Every marketing-driven event (page view, VSL play, CTA click, signup, conversion) writes a row. Phase 3 Optimizer reads from here for attribution and learning.';

create index if not exists idx_marketing_events_visitor
  on public.marketing_events (visitor_id, created_at desc);

create index if not exists idx_marketing_events_asset
  on public.marketing_events (asset_id, event_type);

create index if not exists idx_marketing_events_client_agent
  on public.marketing_events (client_agent_id);

create index if not exists idx_marketing_events_event_time
  on public.marketing_events (event_type, created_at desc);

alter table public.marketing_events enable row level security;

create policy marketing_events_service_role_all
  on public.marketing_events
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Part 3: marketing_assets — registry of every trackable piece of content
-- =======================================================================

create table if not exists public.marketing_assets (
  id text primary key,
  created_at timestamptz not null default now(),
  asset_type text not null,
  title text not null,
  channel text,
  platform_asset_url text,
  variant_of text references public.marketing_assets(id),
  metadata jsonb,
  retired_at timestamptz
);

comment on table public.marketing_assets is
  'Phase 0 asset registry. Every video, email, landing page, ad creative gets a UUID used as stx_asset_id in URL params. Attribution joins marketing_events.asset_id → marketing_assets.id to trace revenue to content.';

create index if not exists idx_marketing_assets_type_channel
  on public.marketing_assets (asset_type, channel);

create index if not exists idx_marketing_assets_created
  on public.marketing_assets (created_at desc);

alter table public.marketing_assets enable row level security;

create policy marketing_assets_service_role_all
  on public.marketing_assets
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Part 4: pilot_email_sends — idempotency log for pilot_lifecycle.py cron
-- =======================================================================

create table if not exists public.pilot_email_sends (
  id bigserial primary key,
  client_agent_id text not null,
  email_key text not null,
  sent_at timestamptz not null default now(),
  brevo_message_id text,
  unique (client_agent_id, email_key)
);

comment on table public.pilot_email_sends is
  'Phase 0 idempotency log for pilot_lifecycle.py cron. Prevents duplicate pilot_day_3/7/12/expired/converted/winback emails if the cron runs twice on the same day. Unique constraint on (client_agent_id, email_key) is the idempotency guarantee.';

create index if not exists idx_pilot_email_sends_agent
  on public.pilot_email_sends (client_agent_id, email_key);

alter table public.pilot_email_sends enable row level security;

create policy pilot_email_sends_service_role_all
  on public.pilot_email_sends
  for all to service_role
  using (true) with check (true);

commit;

-- End of forward migration 20260411_phase0_pilot_schema.sql
