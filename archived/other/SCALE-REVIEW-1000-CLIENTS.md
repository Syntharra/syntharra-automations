# Syntharra Architecture Scale Review — 1000+ HVAC Clients
Date: 2026-04-06

## Verdict
**Architecturally sound. Implementation incomplete. Git-IaC design will scale to 1000+. Critical gaps must be closed before client #50.**

## ✅ Scales Fine As-Is
- Retell platform — enterprise, 1000+ cloned agents no issue
- Git-IaC core — manifest-driven builds are the right pattern
- `hvac_standard_agent` at 1000 rows — trivial (index on agent_id, phone_number)
- `hvac_call_log` at ~50k rows/day — partition at year 2
- Stripe, HubSpot — well within rate limits
- Supabase RLS — sound tenant isolation

## ⚠️ Needs Attention Before 500 Clients
- Telnyx migration (Twilio is interim)
- n8n horizontal scaling — single instance fails at 50+ concurrent onboardings
- `client_health_scores` has no populator or dashboard yet

## 🚨 Hard Blockers Before 1000 Clients

### #1 — Global Prompt Updates (CRITICAL)
**Problem:** No mechanism to push a MASTER prompt fix to 1000 cloned agents. Each clone drifts.
**Impact:** First regression at client 50 becomes unmanageable.
**Fix:** Implement SCALING_ADDENDUM Phases 6-8:
- `client_agents` table (client_id, retell_agent_id, release_tag, overrides_json)
- `scripts/rollout.py` — rebuild all client flows from release_tag + overrides
- Canary → batch → monitor → auto-rollback
**Deadline:** Before client #50. Non-negotiable.

### #2 — Disaster Recovery
**Problem:** Retell outage = all 1000 clients dark. Loss estimate $2.4M–$16M for a 4h outage.
**Fix:** Dual-agent (Bland AI fallback) or SIP failover.
**Deadline:** Before client #500.

### #3 — Per-Client Observability
**Problem:** No dashboard for 1000 agents.
**Fix:** 1 week — populator + React ops dashboard (or Supabase + Metabase).
**Deadline:** Before client #100.

## Prioritized Actions

| # | Action | Effort | Blocks At |
|---|---|---|---|
| 1 | Phase 6-8 client_agents + rollout.py + canary | 3 weeks | 50 clients |
| 2 | Ops dashboard + health populator | 1 week | 100 clients |
| 3 | n8n queue mode + workers on Railway | 3 days | 50 concurrent onboardings |
| 4 | Telnyx live + auto-provisioning | 1 week | 200 clients |
| 5 | DR: dual-agent or SIP failover | 2 weeks | 500 clients |
| 6 | Partition hvac_call_log by month | 2 days | year 2 |
| 7 | Indexes: hvac_standard_agent, hvac_call_log | 1 hour | immediate |
| 8 | Supabase PITR + nightly retell-iac snapshot | 1 day | immediate |
| 9 | Per-client cost telemetry | 3 days | 200 clients |
| 10 | Load-test onboarding with 50 concurrent | 2 days | pre-launch |

## Top Risk
Without Phases 6-8 coded, Syntharra cannot push a global prompt fix to its fleet. This is the #1 gap and must ship before significant client acquisition.

## Single Points of Failure
- Retell (no fallback) — high
- Single n8n instance — high
- Single Supabase project — medium
- Twilio (until Telnyx) — medium

## Cost Sanity at 1000 clients
Fixed infra ~$5-8k/mo + variable ~$12-25/client/mo. Gross ~$750k/mo avg tier. Margin comfortable. Scale bottleneck is engineering, not infra cost.
