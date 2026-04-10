-- 2026-04-11 — Phase 0 — ROLLBACK of 20260411_phase0_pilot_schema.sql
--
-- RUN THIS ONLY IF the forward migration caused regressions on existing
-- paid customers or billing tools. Not a routine tool — only for incident recovery.
--
-- Safety:
--   - All drops are IF EXISTS. Running this twice is safe.
--   - Restores the ORIGINAL status check constraint (active/paused/cancelled/past_due)
--     verified against live schema at scan time (docs/audits/2026-04-11-phase0-schema-scan.md).
--
-- Data loss considerations:
--   - Dropping marketing_events / marketing_assets / pilot_email_sends will lose any
--     rows inserted into them post-migration. If any rows exist, back them up first:
--     select json_agg(row_to_json(e)) from marketing_events e;
--     select json_agg(row_to_json(a)) from marketing_assets a;
--     select json_agg(row_to_json(p)) from pilot_email_sends p;
--   - Dropping client_subscriptions pilot columns on rows that have pilot_mode=true
--     will lose pilot state (minutes used, pilot_ends_at, etc.). If any pilot rows
--     exist, back them up first:
--     select json_agg(row_to_json(cs)) from client_subscriptions cs where pilot_mode=true;
--
-- Rollback sequence:
--   1. Drop new tables (data loss if rows exist — see above)
--   2. Drop new indexes on client_subscriptions
--   3. Drop new columns on client_subscriptions
--   4. Drop the new status check constraint
--   5. Restore the original status check constraint
--   6. [Outside SQL] revert tools/monthly_minutes.py and tools/usage_alert.py
--      defensive filter via `git revert` on the patch commit

begin;

-- 1. Drop new tables
drop table if exists public.pilot_email_sends cascade;
drop table if exists public.marketing_events cascade;
drop table if exists public.marketing_assets cascade;

-- 2. Drop new indexes on client_subscriptions
drop index if exists public.idx_client_subscriptions_pilot_active;
drop index if exists public.idx_client_subscriptions_first_touch_asset;

-- 3. Drop new columns from client_subscriptions
alter table public.client_subscriptions
  drop column if exists pilot_mode,
  drop column if exists pilot_started_at,
  drop column if exists pilot_ends_at,
  drop column if exists pilot_minutes_allotted,
  drop column if exists pilot_minutes_used,
  drop column if exists payment_method_added_at,
  drop column if exists first_touch_asset_id,
  drop column if exists last_touch_asset_id,
  drop column if exists first_touch_utm,
  drop column if exists last_touch_utm;

-- 4. Drop the expanded status check constraint
alter table public.client_subscriptions
  drop constraint if exists client_subscriptions_status_check;

-- 5. Restore the original status check constraint (verified from live schema 2026-04-11)
alter table public.client_subscriptions
  add constraint client_subscriptions_status_check
  check (status = any (array[
    'active'::text,
    'paused'::text,
    'cancelled'::text,
    'past_due'::text
  ]));

commit;

-- End of rollback migration 20260411_phase0_pilot_schema_rollback.sql
