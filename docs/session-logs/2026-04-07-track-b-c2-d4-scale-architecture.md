# 2026-04-07 — Track B + C2 + D4 — scale architecture to 1000+ clients

## What shipped
- **B1 client_agents registry**: `client_agents` + `client_agents_rollout_log` Supabase tables (RLS service-role only, unique (client_id, tier))
- **B1 register.py**: onboarding helper at `retell-iac/scripts/register.py`
- **B2 rollout.py**: rate-limited (5 rps), exp backoff, idempotent fleet updater. ~13 min for 1000 agents.
- **B3 canary.py**: 5% canary, 2h health window vs baseline, auto-revert on >5pp drop, Slack alerts
- **C2 hvac_call_log partitioning**: monthly RANGE on created_at, 13 partitions live, helper `ensure_call_log_partition()`, janitor for n8n monthly schedule. Old table preserved as `hvac_call_log_pre_partition`.
- **D4 Retell rename**: agent_2cffe3d... renamed and promoted to Premium MASTER (provisional)

## Key findings
- 2 of 4 master/testing agent IDs in CLAUDE.md don't exist on Retell. Only 1 std + 1 prem agent live. Authoritative source now Supabase `client_agents`.
- Premium Integration Dispatcher n8n workflow has hardcoded Supabase service role key — flagged as security debt.
- Premium MASTER is provisional pending scenario testing completion (per Dan).

## Architecture readiness for 1000+ clients
- ✅ Single registry (client_agents) — no spreadsheets
- ✅ Idempotent rate-limited fleet updates (rollout.py)
- ✅ Canary-gated rollouts with auto-revert (canary.py)
- ✅ Partitioned call log (partition pruning, fast inserts at scale)
- ⏳ C1 n8n queue mode + workers (gates on Dan-side approval)
- ⏳ C3 Supabase PITR (gates on Dan-side approval)
- ⏳ C4 ops dashboard
- ⏳ A1/A2/A3 Track A all gated on Dan

## Lessons / SELF-IMPROVEMENT
1. **CLAUDE.md drift** — manual ID lists rot. Authoritative state belongs in DB (`client_agents`), not in markdown. Apply this everywhere: any ID in markdown should be a *pointer* to a query, not the source.
2. **Partition before scale, not during** — 9 rows now → trivial swap. 9M rows later → multi-day operation. C2 was the cheapest C-track item to do today.
3. **Always verify list-agents before trusting documented IDs** — saved a destructive PATCH against a non-existent agent.

## Files pushed
- supabase/migrations/20260407_create_client_agents_registry.sql
- supabase/migrations/20260407_partition_hvac_call_log_monthly.sql
- retell-iac/scripts/register.py, rollout.py, canary.py, README.md
- tools/partition_janitor.py
- docs/changes/2026-04-07-scale-architecture.md
- docs/REFERENCE.md (appended)
- docs/FAILURES.md (appended)
