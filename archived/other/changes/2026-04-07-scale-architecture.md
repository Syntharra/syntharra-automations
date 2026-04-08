# 2026-04-07 — Architecture changes for 1000+ scale

## B1 — client_agents registry
- New tables: `client_agents`, `client_agents_rollout_log` (RLS service-role only)
- Backfilled from live Retell agents (only 2 actually exist: Standard MASTER + Premium MASTER interim)

## B2 — rollout.py
- `retell-iac/scripts/rollout.py` — rate-limited (5 rps), exp backoff, idempotent, dry-run/execute
- Designed to push prompt updates to entire fleet in <15 min for 1000 agents

## B3 — canary.py
- `retell-iac/scripts/canary.py` — 5% canary, 2h health window, auto-revert on >5pp success-rate drop
- Slack alerts via $SLACK_WEBHOOK_URL

## C2 — hvac_call_log partitioning
- Converted to RANGE-partitioned by created_at, monthly
- 13 initial partitions: 2026-03 .. 2027-02 + default
- Old table preserved as `hvac_call_log_pre_partition` (9 rows backup, drop after 7-day soak)
- Helper: `SELECT public.ensure_call_log_partition('2027-03-01'::date);`
- Janitor: `tools/partition_janitor.py` — schedule monthly from n8n

## D4 — Retell agent rename
- `agent_2cffe3d86d7e1990d08bea068f`: HVAC Premium (TESTING) → HVAC Premium (MASTER interim)

## CRITICAL: stale agent IDs in CLAUDE.md
The following IDs in project instructions DO NOT exist on Retell anymore:
- `agent_9822f440f5c3a13bc4d283ea90` (claimed Premium MASTER)
- `agent_731f6f4d59b749a0aa11c26929` (claimed Standard TESTING)

Live truth (from `list-agents`, 2026-04-07):
- Standard MASTER: `agent_4afbfdb3fcb1ba9569353af28d` flow `conversation_flow_34d169608460`
- Premium MASTER (interim): `agent_2cffe3d86d7e1990d08bea068f` flow `conversation_flow_2ded0ed4f808`

D5 (build proper Premium MASTER via retell-iac manifest) should run before scaling Premium >0 clients.

## Known security debt
- Premium Integration Dispatcher n8n workflow `73Y0MHVBu05bIm5p` has hardcoded Supabase service role key in node JS code. Move to credential before client #1.
