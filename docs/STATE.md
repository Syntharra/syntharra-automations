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

- **HVAC Standard agent** — MASTER at `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`. Agent ID `agent_4afbfdb3fcb1ba9569353af28d`, flow `conversation_flow_34d169608460`. retell-iac is the canonical source of truth for all changes.
- **n8n onboarding workflow** — Standard `4Hx7aRdzMl5N0uJP`.
- **Supabase schema** — `hvac_standard_agent`, `client_agents`, `stripe_payment_data`, `client_subscriptions`, `billing_cycles`, `overage_charges`, `website_leads`, `monthly_billing_snapshot`, `syntharra_vault`, `call_processor_dlq`. RLS hardened.
- **Client dashboard** — `dashboard.html` in syntharra-website. Retell-native: fetches via `POST /webhook/retell-calls` → Retell `list-calls`. URL param `?a=AGENT_ID`.
- **Retell proxy webhook** — n8n `Y1EptXhOPAmosMbs`. Returns `{ calls: [...] }` from Retell v2. E2E tested 2026-04-08.
- **OAuth server** — Railway-deployed.
- **Stripe** — still in test mode. Live-mode migration is a P0 blocker (see TASKS.md).

## 2026-04-09 — lean cleanup (Pass 1)

Removed the speculative "store everything in Supabase" layer. Retell is the source of truth for call data; Supabase keeps only billing state + client configs.

**Dropped tables (6):** `transcript_analysis`, `stripe_processed_events`, `dunning_state`, `infra_health_checks` (+ `infra_health_summary` view, cascaded), `syntharra_activation_queue`, `client_health_scores`.

**Archived n8n workflows (10):** Premium Dispatchers (Calendly/Jobber/HubSpot), HVAC Premium Call Processor, Premium "You're Live" Email, Weekly Client Health Score, Daily Transcript Analysis, Nightly PII Retention Cleanup, MAINT partition pre-create, MON per-client success rate.

**Created:** `monthly_billing_snapshot` — immutable per-agent/per-month rollup written at invoice time. Purpose: long-term dispute defense against Retell call-retention window. One row per client per month.

**Deferred to Pass 2** (next session): build lean Call Usage Logger workflow, rewrite `Monthly Minutes Calculator` to pull from Retell `list-calls` (with pagination) instead of `hvac_call_log`, dry-run against 2026-03 period, repoint Retell agent webhook (one-time `RULES.md` override — pre-launch, no live clients), archive Standard HVAC Call Processor, drop all 17 `hvac_call_log*` objects.

**Pass 2 prereq — verify before starting:** the retell-iac MASTER agent Post-Call Analysis block must declare custom variables `is_lead`, `urgency`, `is_spam` (and optionally `service_type`, `customer_name`). Retell only populates `call_analysis.custom_analysis_data.*` for fields declared on the agent. If missing, add them once in MASTER, promote, and the next billing cycle is the cutover.

## Outstanding tasks from 2026-04-09 session (pick up next session)

Alongside the Pass 2 billing/call-log migration above, three standalone tasks were deferred from the 2026-04-09 request and have not been started:

### Task 2 — Fix Retell agent auto-layout fine-tuning error
- **Agent:** `agent_4afbfdb3fcb1ba9569353af28d`, flow `conversation_flow_34d169608460`
- **Symptom:** "Fine tuning error" preventing auto-layout of nodes in the Retell canvas
- **Likely root cause:** phantom/placeholder component in the flow's `components[]` array — see FAILURES.md 2026-04-08 "Standard MASTER auto-layout blocked by phantom component". Same fix pattern: `PATCH components: []` (or delete the offending entry) after checking for entries with placeholder text or zero node references.
- **Approach:** Clone live → TESTING via `retell-iac/scripts/promote.py`, diagnose on TESTING, promote fix. (RULES.md #1 applies — this is not covered by the Pass 2 one-time override, which is scoped only to the webhook repoint.)

### Task 3 — Fetch + display current client dashboard
- **Repo:** `Syntharra/syntharra-website`
- **File:** `dashboard.html`
- **Live URL pattern:** `https://syntharra.com/dashboard.html?a=<agent_id>`
- **Data source:** `POST https://n8n.syntharra.com/webhook/retell-calls` (workflow `Y1EptXhOPAmosMbs`)
- **Ask:** fetch current HTML via GitHub MCP and display to Dan so he can review the current state before any further edits.

### Task 4 — Agent naming convention: `{Live|Demo} {Company Name}`
- **Goal:** prevent accidentally working on live agents during testing/improvements by visually distinguishing Live vs Demo at agent-list level
- **Where to change:** `retell-iac/` agent creation scripts, any n8n onboarding workflow nodes that set the Retell agent `agent_name`, and potentially the master template.
- **Open question from last session:** what signal determines Live vs Demo? Candidates: promotion target (TESTING vs prod), env var, or an explicit CLI flag on `promote.py`. Needs Dan's decision before implementation.

## What's in flight

- **Stripe live mode** — test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` ($697/mo) created and old prices archived. Live key not yet in vault. P0 blocker pending Dan's timeline.

## What's blocked

- **Telnyx SMS** — waiting on Telnyx AI evaluation approval.

## Architecture invariants (do not violate)

- **retell-iac is the source of truth for the agent.** No manual Retell dashboard edits to MASTER.
- **MASTER templates are the only thing in the repo.** Per-client clones live in Supabase `client_agents`.
- **IDs come from `docs/REFERENCE.md` only.** Never inline.
- **Never test on a live Retell agent.** Clone → TESTING → `retell-iac/scripts/promote.py` → live.
