# State — Syntharra Automations

_Last updated: 2026-04-09_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
5720caa chore(session): auto-backup local changes 2026-04-09

## Go-live checklist
see docs/TASKS.md

---

## Product decision (2026-04-09)

Single product: **HVAC Standard at $697/mo**. Premium tier retired. One agent, one onboarding flow, one price.
Repo stripped to lean core. retell-iac is Standard-only.

## Data-ownership principle (2026-04-09)

**Retell owns call data. Supabase owns client + billing state.** No per-call storage in Supabase. The dashboard reads Retell directly via `list-calls`; monthly billing reads Retell directly at invoice time. Supabase holds only: client configs, subscriptions, billing cycles, overage charges, website leads, and a tiny immutable `monthly_billing_snapshot` rollup for dispute defense against Retell's retention window.

---

## What's live in production

- **HVAC Standard TESTING agent (authoritative)** — `agent_6e7a2ae03c2fbd7a251fafcd00` / `conversation_flow_90da7ca2b270`. Modern `code`-node architecture. Autolayout + finetune orphan fix applied 2026-04-09. **This is the current source of truth for the Standard agent**, pending promotion to MASTER in a fresh session. Snapshot: `retell-iac/snapshots/2026-04-09_testing-autolayout-fixed/`.
- **HVAC Standard MASTER (legacy, stale)** — `agent_4afbfdb3fcb1ba9569353af28d` / `conversation_flow_34d169608460`. Uses legacy `subagent` architecture. Will be fully replaced on next promotion. Do not use as clone source.
- **`retell-iac/components/` is stale** — 19 component JSON files describe the legacy subagent shape and do not match the current testing flow. `build_agent.py` would produce invalid output until components are rewritten for flat `code`-node architecture. Tracked as P0 in TASKS.md.
- **n8n onboarding workflow** — Standard `4Hx7aRdzMl5N0uJP`.
- **Supabase schema** — `hvac_standard_agent`, `client_agents`, `stripe_payment_data`, `client_subscriptions`, `billing_cycles`, `overage_charges`, `website_leads`, `monthly_billing_snapshot`, `syntharra_vault`, `client_dashboard_info` (view — narrow read subset for dashboard, 2026-04-09). RLS hardened. All 15 `hvac_call_log*` tables and `call_processor_dlq` dropped 2026-04-09 (backup preserved in `backup_hvac_call_log_prepart_20260409`).
- **Client dashboard** — `dashboard.html` in syntharra-website. Full redesign shipped 2026-04-09 (a11y, dark mode, sentiment stat, CSV export, virtualisation, demo mode `?demo=1`, lead copy, triage flag, sparkline). Reads company info from `client_dashboard_info` view; reads calls via `POST /webhook/retell-calls` → Retell `list-calls`. URL param `?a=AGENT_ID`.
- **Retell proxy webhook** — n8n `Y1EptXhOPAmosMbs`. Returns `{ calls: [...] }` from Retell v2. E2E tested 2026-04-08.
- **OAuth server** — Railway-deployed.
- **Stripe** — still in test mode. Live-mode migration is a P1 (see TASKS.md).

## 2026-04-09 — lean cleanup (Pass 1)

Removed the speculative "store everything in Supabase" layer. Retell is the source of truth for call data; Supabase keeps only billing state + client configs.

**Dropped tables (6):** `transcript_analysis`, `stripe_processed_events`, `dunning_state`, `infra_health_checks` (+ `infra_health_summary` view, cascaded), `syntharra_activation_queue`, `client_health_scores`.

**Archived n8n workflows (10):** Premium Dispatchers (Calendly/Jobber/HubSpot), HVAC Premium Call Processor, Premium "You're Live" Email, Weekly Client Health Score, Daily Transcript Analysis, Nightly PII Retention Cleanup, MAINT partition pre-create, MON per-client success rate.

**Created:** `monthly_billing_snapshot` — immutable per-agent/per-month rollup written at invoice time. Purpose: long-term dispute defense against Retell call-retention window. One row per client per month.

**Deferred to Pass 2** (next session): build lean Call Usage Logger workflow, rewrite `Monthly Minutes Calculator` to pull from Retell `list-calls` (with pagination) instead of `hvac_call_log`, dry-run against 2026-03 period, repoint Retell agent webhook (one-time `RULES.md` override — pre-launch, no live clients), archive Standard HVAC Call Processor, drop all 17 `hvac_call_log*` objects.

**Pass 2 prereq — verify before starting:** the retell-iac MASTER agent Post-Call Analysis block must declare custom variables `is_lead`, `urgency`, `is_spam` (and optionally `service_type`, `customer_name`). Retell only populates `call_analysis.custom_analysis_data.*` for fields declared on the agent. If missing, add them once in MASTER, promote, and the next billing cycle is the cutover.

## 2026-04-09 session — results

**Task 2 — Retell autolayout / finetune error: ✅ FIXED on testing agent `agent_6e7a2ae03c2fbd7a251fafcd00`.** Three fixes PATCHed directly via Retell API on `conversation_flow_90da7ca2b270`:
  1. `node-identify-call.finetune_transition_examples[fe-service]` was orphaned (pointed at `node-fallback-leadcapture` with no matching edge). Repointed to `node-call-style-detector`. **This was the "fine tuning error" — Retell's validator caught it on every PATCH but not on GET.**
  2. `node-call-style-detector` (code, `wait_for_result:true`) had empty `edges[]`. Added edge → `node-fallback-leadcapture`.
  3. `node-validate-phone` (code, `wait_for_result:true`) had empty `edges[]`. Added edge → `node-ending`.
  
  Pending Dan's UI verification + promotion to MASTER (will be a full architecture swap — the legacy MASTER uses `subagent` nodes, the current testing uses flat `code` nodes).

**Task 3 — Dashboard redesign: ✅ SHIPPED.** Full rewrite merged to `main` in `Syntharra/syntharra-website`. Includes security hardening (URL whitelist, escHtml), a11y (keyboard, ARIA), dashboard-specific header, client monogram, sentiment stat with bar chart, CSV export, dark mode, virtualised rendering (25/batch via IntersectionObserver), demo preview (`?demo=1`), lead copy button, needs-followup triage flag, 7-day sparkline. Also fixed a silent-empty-read bug where the base-table fetch was returning nothing for every real client — created `client_dashboard_info` SECURITY DEFINER view exposing only 4 safe columns.

**Task 4 — `Live — / Demo —` agent naming: ⏸ diff prepared, Dan will paste.** Location: `Build Retell Prompt` code node of workflow `4Hx7aRdzMl5N0uJP`, lines 25 + 683. Exact diff in TASKS.md P0.

**Supabase cleanup: ✅ DONE.** Dropped 15 `hvac_call_log*` tables + `call_processor_dlq`. 9 rows preserved in `backup_hvac_call_log_prepart_20260409`. `syntharra_vault` explicitly preserved and protected via memory rule.

### Carry-forward to next session (P0 in TASKS.md)
- Verify autolayout fix works in Retell UI, then promote testing → MASTER (full architecture swap).
- Rewrite `retell-iac/components/` for flat `code`-node architecture before any IaC rebuild is possible.
- Paste Task 4 naming diff into the onboarding workflow.

## What's in flight

- **Stripe live mode** — test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` ($697/mo) created and old prices archived. Live key not yet in vault. P0 blocker pending Dan's timeline.

## What's blocked

- **Telnyx SMS** — waiting on Telnyx AI evaluation approval.

## Architecture invariants (do not violate)

- **retell-iac is the source of truth for the agent.** No manual Retell dashboard edits to MASTER.
- **MASTER templates are the only thing in the repo.** Per-client clones live in Supabase `client_agents`.
- **IDs come from `docs/REFERENCE.md` only.** Never inline.
- **Never test on a live Retell agent.** Clone → TESTING → `retell-iac/scripts/promote.py` → live.
