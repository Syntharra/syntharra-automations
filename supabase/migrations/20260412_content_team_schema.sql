-- 2026-04-12 — Content Team Schema
-- Schema for the autonomous organic content team that extends marketing_brain.py.
-- Paired with docs/superpowers/plans/2026-04-11-autonomous-content-team-implementation.md
--
-- What this migration adds (4 new tables):
--   marketing_intelligence   — Research Agent daily output (YouTube/Reddit/Trends)
--   competitor_intelligence  — Competitor Watch weekly scans
--   content_queue            — Writer Agent -> Dan approval -> Publisher render/post
--   marketing_brain_log      — Weekly brain run audit trail
--
-- Existing marketing tables (content_variants, marketing_campaigns, campaign_results)
-- from 20260411_marketing_autonomy.sql are unchanged. This migration is additive-only.
--
-- RLS pattern: service_role full access (same as all other marketing tables).
-- No anon access yet — anon RLS for the approval dashboard is added in a follow-up
-- migration (Task 18 of the plan) once the dashboard HTML ships.
--
-- Safety:
--   - All CREATE TABLE statements use IF NOT EXISTS (idempotent).
--   - No ALTER on existing tables.
--   - No data migration.
--   - Grep-verified on 2026-04-12: no existing code references these 4 table names.
--
-- MANUAL APPLY REQUIRED — do NOT auto-apply via CI.
-- Run via Supabase MCP apply_migration, or paste into the Supabase SQL editor.

begin;

-- =======================================================================
-- Table 1: marketing_intelligence
-- Research Agent daily output. 30-day TTL via expires_at column.
-- =======================================================================

create table if not exists public.marketing_intelligence (
  id              bigserial   primary key,
  scraped_at      timestamptz not null default now(),
  source          text        not null
                    check (source in (
                      'youtube',
                      'reddit',
                      'google_trends',
                      'tiktok_scrape',
                      'seed'
                    )),
  query           text        not null,
  title           text,
  url             text,
  view_count      bigint,
  engagement_rate numeric(6,4),

  -- Extracted signals used by content_writer.py
  hook            text,
  angle           text,
  raw_data        jsonb       not null default '{}'::jsonb,

  -- 0.00-1.00 — higher means "more signal" per source
  confidence      numeric(3,2) not null default 0.50,

  -- 30-day TTL; a cron can later prune expired rows. Columns kept simple
  -- (no partial index) because volume is low (hundreds/day, not millions).
  expires_at      timestamptz not null default (now() + interval '30 days')
);

comment on table public.marketing_intelligence is
  'Daily trend + competitor findings from Research Agent. Consumed by '
  'content_writer.py to seed weekly video scripts. 30-day TTL via expires_at.';

-- Index: Writer Agent query pattern — recent findings by source
create index if not exists idx_marketing_intelligence_source_scraped
  on public.marketing_intelligence (source, scraped_at desc);

-- Index: TTL pruning
create index if not exists idx_marketing_intelligence_expires
  on public.marketing_intelligence (expires_at);

alter table public.marketing_intelligence enable row level security;

create policy marketing_intelligence_service_role_all
  on public.marketing_intelligence
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Table 2: competitor_intelligence
-- Weekly competitor scans. Lower volume, longer retention.
-- =======================================================================

create table if not exists public.competitor_intelligence (
  id              bigserial   primary key,
  scraped_at      timestamptz not null default now(),
  competitor_name text        not null,
  platform        text        not null
                    check (platform in (
                      'youtube',
                      'tiktok',
                      'instagram',
                      'facebook',
                      'linkedin',
                      'website'
                    )),
  top_content     jsonb       not null default '[]'::jsonb,
  content_gaps    jsonb       not null default '[]'::jsonb,
  notes           text
);

comment on table public.competitor_intelligence is
  'Weekly competitor scans from Competitor Watch Agent. Identifies topics '
  'competitors are NOT covering so Syntharra can own the gap.';

create index if not exists idx_competitor_intelligence_scraped
  on public.competitor_intelligence (scraped_at desc);

alter table public.competitor_intelligence enable row level security;

create policy competitor_intelligence_service_role_all
  on public.competitor_intelligence
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Table 3: content_queue
-- The main content pipeline table. Rows flow:
--   pending_approval -> approved -> rendering -> rendered -> posted
--                   \-> rejected                          \-> failed
-- =======================================================================

create table if not exists public.content_queue (
  id                  bigserial   primary key,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),

  content_type        text        not null
                        check (content_type in (
                          'short_video',
                          'long_video',
                          'blog',
                          'caption',
                          'vsl'
                        )),

  -- Writer Agent output
  hook                text        not null,
  script              text        not null,
  visual_prompt       text,
  reasoning           text        not null,
  confidence_score    numeric(3,2) not null default 0.50,

  -- Platform targets as a jsonb array: ["youtube_shorts", "tiktok", ...]
  -- Defaults to empty array; Writer Agent populates per-concept.
  platform_targets    jsonb       not null default '[]'::jsonb,

  -- Back-reference to marketing_intelligence.id[] that seeded this concept
  source_intelligence jsonb       not null default '[]'::jsonb,

  -- Publisher Agent fills these after render
  video_provider      text,
  video_model         text,
  video_url           text,
  thumbnail_url       text,

  -- Blotato response after posting
  blotato_post_id     text,
  platform_post_urls  jsonb       not null default '{}'::jsonb,

  status              text        not null default 'pending_approval'
                        check (status in (
                          'pending_approval',
                          'approved',
                          'rejected',
                          'rendering',
                          'rendered',
                          'posted',
                          'failed'
                        )),
  rejection_reason    text,
  approved_by         text,   -- 'dan' | 'auto' (48h rule)
  approved_at         timestamptz,
  posted_at           timestamptz
);

comment on table public.content_queue is
  'Core content pipeline. Writer Agent inserts rows with pending_approval; '
  'Dan approves via syntharra.com/marketing dashboard; Publisher Agent '
  'renders via Higgsfield, posts via Blotato, and tracks through to posted.';

-- Trigger: keep updated_at current
create or replace function public.content_queue_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists content_queue_updated_at on public.content_queue;
create trigger content_queue_updated_at
  before update on public.content_queue
  for each row execute function public.content_queue_set_updated_at();

-- Index: dashboard + publisher query patterns — fetch by status
create index if not exists idx_content_queue_status_created
  on public.content_queue (status, created_at desc);

-- Index: posted_at for analytics lookback queries
create index if not exists idx_content_queue_posted_at
  on public.content_queue (posted_at desc)
  where posted_at is not null;

alter table public.content_queue enable row level security;

create policy content_queue_service_role_all
  on public.content_queue
  for all to service_role
  using (true) with check (true);

-- =======================================================================
-- Table 4: marketing_brain_log
-- One row per brain phase run. Audit trail + decision log.
-- =======================================================================

create table if not exists public.marketing_brain_log (
  id                bigserial   primary key,
  run_at            timestamptz not null default now(),
  phase             text        not null
                      check (phase in (
                        'review',
                        'plan',
                        'propose',
                        'execute',
                        'track'
                      )),
  week_of           date        not null,
  content_queue_ids jsonb       not null default '[]'::jsonb,
  slack_message_ts  text,
  decisions         jsonb       not null default '{}'::jsonb,
  preview_mode      boolean     not null default true,
  notes             text
);

comment on table public.marketing_brain_log is
  'Weekly marketing_brain.py audit trail. One row per phase per run. '
  'preview_mode=true means the run was gated (no live posts).';

create index if not exists idx_marketing_brain_log_week
  on public.marketing_brain_log (week_of desc, run_at desc);

alter table public.marketing_brain_log enable row level security;

create policy marketing_brain_log_service_role_all
  on public.marketing_brain_log
  for all to service_role
  using (true) with check (true);

commit;

-- End of forward migration 20260412_content_team_schema.sql
-- ⚠  MANUAL APPLY REQUIRED — do NOT auto-apply via CI.
