# Implementation Plan — Post-Cleanup Remaining Work
_Created 2026-04-07. Source of truth for next chat. Delete rows as shipped._

## Ordering principle
Unblock launch first → scale before client #50 → harden before client #100 → hygiene anytime.

---

## TRACK A — Launch blockers (do first, sequential)

### A1. Stripe go-live  *(1 day)*
- Switch account to live mode
- Recreate in live: products (Standard $497, Premium $997), prices, coupons
- Recreate webhook → `n8n.syntharra.com/webhook/syntharra-stripe-webhook`
- Update Railway env `STRIPE_SECRET_KEY` to `sk_live_...` on `syntharra-checkout`
- Update all price IDs in `docs/context/STRIPE.md` + vault
- Test: real $1 charge + refund end-to-end
- **Done when:** live checkout session completes, webhook fires, HubSpot deal created

### A2. Ops monitor Railway redeploy  *(half day)*
- Unpause service `7ce0f943`
- Verify env vars still set (Retell, Supabase, Slack webhook)
- Verify HEAD-only health checks on n8n webhooks (never POST)
- Smoke test: kill a workflow, confirm Slack alert
- **Done when:** dashboard shows green for 24h

### A3. Telnyx SMS approval follow-up  *(blocks on Telnyx)*
- Chase 10DLC brand + campaign approval
- Once approved: update `hvac-standard` confirmation SMS node from stub → Telnyx
- Test: onboarding → confirmation SMS received
- **Done when:** production client SMS sending

---

## TRACK B — Scale to 1000 clients (Phases 6-8, blocks client #50)
_This is the #1 architectural gap from the scale review. 3 weeks. Ship before client #50._

### B1. Phase 6 — `client_agents` registry  *(3 days)*
- Supabase migration: create `client_agents` table
  - Columns: `client_id, agent_id, flow_id, tier (std|prem), prompt_version, base_tag, deployed_at, status, canary`
  - RLS: service-role only
- Backfill from current `hvac_standard_agent`
- Add unique index on `(client_id, tier)`
- `retell-iac/scripts/register.py` — writes to `client_agents` on every clone
- **Done when:** every existing + new client row exists in `client_agents`

### B2. Phase 7 — `rollout.py` fleet updater  *(5 days)*
- `retell-iac/scripts/rollout.py`:
  - Input: git tag (e.g. `std-v1.4.2`)
  - Query `client_agents WHERE tier=std AND prompt_version < tag`
  - Loop: fetch current prompt → merge new base → PATCH Retell → Publish → update `prompt_version` in DB
  - Rate limit: 5 req/s, exponential backoff on 429
  - Idempotent: re-runnable, skips already-updated
  - Dry-run mode: `--dry-run` prints diff only
- Logging: write each client update to `client_agents_rollout_log`
- **Done when:** dry-run produces correct diff against 10 test clients

### B3. Phase 8 — Canary + auto-rollback  *(5 days)*
- Canary strategy: tag 5% of fleet as `canary=true`, rollout hits canary first
- Health check: after canary rollout, query `hvac_call_log` for 1h — compare success rate vs pre-rollout baseline
- If drop >5% → auto-rollback script reverts canary to previous `base_tag`
- Slack alert on canary fail
- Full rollout only proceeds if canary green for 2h
- **Done when:** dry-run a prompt change → canary passes → full fleet updates → rollback tested by forcing a bad tag

---

## TRACK C — Scale hardening (before client #100)

### C1. n8n queue mode + workers  *(3 days)*
- Enable queue mode on `syntharra-n8n` (Redis already present: `9285c656`)
- Add 2 worker Railway services
- Stress test: 50 concurrent webhook calls

### C2. Partition `hvac_call_log`  *(2 days)*
- Supabase migration: convert to partitioned table (monthly partitions)
- Add indexes: `(client_id, created_at DESC)`, `(call_id)`
- Backfill existing rows

### C3. Enable Supabase PITR  *(30 min)*
- Dashboard → upgrade to Pro if needed → enable PITR
- Document restore procedure in `docs/context/SUPABASE.md`

### C4. Ops dashboard  *(2 days)*
- Single page in admin repo: calls/day, active clients, error rate, rollout status
- Supabase realtime subscriptions

---

## TRACK D — Hygiene (anytime, parallel)

| Task | Effort | Owner agent |
|---|---|---|
| D1. Review n8n workflow `73Y0MHVBu05bIm5p` (Premium Integration Dispatcher) — keep or kill | 30m | gsd-executor |
| D2. Re-enable MCP on `6LXpGffcWSvL6RxW` (Weekly Newsletter) | 15m | gsd-executor |
| D3. Apply n8n label scheme across all 37 workflows per STANDARDS.md | 1h | gsd-executor |
| D4. Rename Retell agent "HVAC Premium (TESTING)" → "HVAC Premium (MASTER interim)" | 5m | gsd-executor |
| D5. Create Premium MASTER agent proper (not interim) via retell-iac manifest | 1d | gsd-planner + executor |

---

## Execution pattern (every track)

Use GSD parallel orchestration. For each track:

1. **`gsd-planner`** reads this file, breaks track into DAG, emits per-task specs
2. **Parallel `gsd-executor`s** — one per independent task in the track
3. **`gsd-verifier`** — final QA pass, runs smoke tests, confirms GitHub pushes
4. Update `docs/TASKS.md` + this file, tick rows off
5. `session_end.py` — log + admin_tasks + session log to GitHub

**Track A** → sequential (A1 → A2 → A3), 2-3 days total
**Track B** → sequential phases, each phase uses parallel executors internally, 3 weeks total
**Track C** → parallel (C1 ‖ C2 ‖ C3 ‖ C4), 1 week total
**Track D** → drop into any session as filler, all parallel

**Recommended chat ordering:**
- Chat 1: Track A (launch unblocked) + Track D1-D4 in parallel
- Chat 2-4: Track B Phase 6 → 7 → 8
- Chat 5: Track C all parallel + D5

---

## Definition of done (whole plan)
- Live Stripe revenue flowing
- Ops monitor green 24/7
- `client_agents` populated, `rollout.py` tested, canary proven
- n8n in queue mode with workers
- `hvac_call_log` partitioned + indexed
- PITR on
- All hygiene items closed
- Ready for client #50 without architectural debt
