-- 2026-04-11 — Marketing Autonomy Data Layer
-- Creates 3 tables that power the fully-autonomous weekly marketing machine:
--   content_variants  — A/B test memory; scores every variant on send/open/reply/signup
--   marketing_campaigns — every piece of content the system sends or posts
--   campaign_results   — per-campaign metric events (sent, opened, replied, etc.)
--
-- RLS pattern: service_role full access, anon denied (same as all other tables).
-- Indexes chosen for the three hottest query patterns:
--   1. Fetch campaigns by type+status+week (weekly cycle runner)
--   2. Fetch campaigns by cycle_id (cycle-level reporting)
--   3. Fetch results by campaign_id+metric (aggregation for scoring)
--   4. Fetch active variants ordered by score (content selection)
--
-- MANUAL APPLY REQUIRED — do NOT auto-apply via CI.
-- Run via Supabase MCP: apply_migration, or paste into the Supabase SQL editor.

begin;

-- =======================================================================
-- Table 1: content_variants
-- Must be created first — marketing_campaigns.variant_id references it
-- (soft reference via TEXT, no FK, to allow drafts before variants exist).
-- =======================================================================

create table if not exists public.content_variants (
  id                 text        primary key,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  type               text        not null
                       check (type in (
                         'cold_email_subject',
                         'cold_email_body',
                         'reddit_post',
                         'linkedin_post',
                         'short_form_script'
                       )),
  template_key       text        not null,
  content            text        not null,

  -- Counters — incremented by track_campaign_performance.py
  send_count         int         not null default 0,
  open_count         int         not null default 0,
  reply_count        int         not null default 0,
  click_count        int         not null default 0,
  engagement_count   int         not null default 0,
  pilot_signup_count int         not null default 0,

  -- Computed score: (reply_count + pilot_signup_count*5) / NULLIF(send_count, 0)
  -- Re-calculated by update_variant_scores() after each metrics pull.
  score              numeric     not null default 0.0,

  is_active          boolean     not null default true,
  notes              text
);

comment on table public.content_variants is
  'A/B test memory for the autonomous marketing machine. Every distinct piece of '
  'copy gets a row. score drives content selection each week; high-score variants '
  'are promoted, low-score variants retired (is_active = false) after N send_count.';

-- Trigger: keep updated_at current
create or replace function public.content_variants_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger content_variants_updated_at
  before update on public.content_variants
  for each row execute function public.content_variants_set_updated_at();

-- Index: content selection — active variants ordered by score within a type
create index if not exists idx_content_variants_type_active_score
  on public.content_variants (type, is_active, score desc);

-- Index: look up all variants for a given template key
create index if not exists idx_content_variants_template_key
  on public.content_variants (template_key);

alter table public.content_variants enable row level security;

create policy content_variants_service_role_all
  on public.content_variants
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Table 2: marketing_campaigns
-- One row per piece of content the system sends or posts.
-- =======================================================================

create table if not exists public.marketing_campaigns (
  id           uuid        primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),

  type         text        not null
                 check (type in ('cold_email', 'reddit', 'linkedin', 'short_form')),

  -- Soft reference to content_variants.id — TEXT so drafts can exist before a
  -- variant row is created.
  variant_id   text,

  -- Where / to whom the content was sent
  target       text        not null,   -- city slug, subreddit name, LinkedIn search, etc.
  target_name  text,                   -- human-readable: "Phoenix, AZ", "r/hvacadvice"

  -- Full content snapshot at send time (never mutated after sent_at is set)
  -- Key fields we expect: subject, body, post_text, brevo_message_id (for matching)
  content_json jsonb       not null,

  sent_at      timestamptz,
  status       text        not null default 'draft'
                 check (status in ('draft', 'approved', 'sent', 'failed')),

  approved_by  text,                   -- 'dan' or 'auto' (auto after 48 h)
  approved_at  timestamptz,

  week_number  int,                    -- ISO week number (extract(isoyear...week))
  cycle_id     text                    -- groups all campaigns from one weekly run
);

comment on table public.marketing_campaigns is
  'One row per content item the autonomous marketing machine sends or posts. '
  'content_json stores a full snapshot including brevo_message_id so that '
  'track_campaign_performance.py can match Brevo transactional events back to '
  'this row. status moves: draft → approved → sent (or failed).';

-- Index: weekly cycle runner — fetch campaigns by type+status+week
create index if not exists idx_marketing_campaigns_type_status_week
  on public.marketing_campaigns (type, status, week_number);

-- Index: cycle-level reporting
create index if not exists idx_marketing_campaigns_cycle_id
  on public.marketing_campaigns (cycle_id);

-- Index: look up by variant to compute variant-level aggregates
create index if not exists idx_marketing_campaigns_variant_id
  on public.marketing_campaigns (variant_id)
  where variant_id is not null;

alter table public.marketing_campaigns enable row level security;

create policy marketing_campaigns_service_role_all
  on public.marketing_campaigns
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Table 3: campaign_results
-- One row per metric event per campaign.
-- =======================================================================

create table if not exists public.campaign_results (
  id           uuid        primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),

  campaign_id  uuid        not null references public.marketing_campaigns(id),

  metric       text        not null
                 check (metric in (
                   'sent',
                   'delivered',
                   'opened',
                   'replied',
                   'clicked',
                   'upvoted',
                   'downvoted',
                   'pilot_signup',
                   'conversion'
                 )),

  value        numeric     not null default 1,
  recorded_at  timestamptz not null default now(),

  -- Where the event came from
  source       text        -- 'brevo_webhook', 'reddit_api', 'manual', 'marketing_events'
);

comment on table public.campaign_results is
  'Per-campaign metric events. Multiple rows can exist for the same campaign+metric '
  '(e.g. each open event). Aggregated by update_variant_scores() to recompute '
  'content_variants.score. Also feeds the weekly marketing digest.';

-- Index: aggregation by campaign and metric (the dominant query pattern)
create index if not exists idx_campaign_results_campaign_metric
  on public.campaign_results (campaign_id, metric);

-- Index: time-based slicing for the weekly digest
create index if not exists idx_campaign_results_recorded_at
  on public.campaign_results (recorded_at desc);

alter table public.campaign_results enable row level security;

create policy campaign_results_service_role_all
  on public.campaign_results
  for all to service_role
  using (true) with check (true);

commit;

-- End of forward migration 20260411_marketing_autonomy.sql
-- ⚠  MANUAL APPLY REQUIRED — do NOT auto-apply via CI.
