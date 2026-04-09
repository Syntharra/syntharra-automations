# State — Syntharra Automations

_Last updated: 2026-04-09_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
493d69b docs(session): plan + session log for client-update form + pass 2

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

- **HVAC Standard MASTER (current, code-node arch)** — `agent_4afbfdb3fcb1ba9569353af28d` / `conversation_flow_34d169608460`, phone `+18129944371`. Promoted from TESTING on 2026-04-09. 19 nodes, all `code` / `conversation` / `transfer_call` / `end` / `extract_dynamic_variables`. Flow v28+. Pre-promotion snapshot (legacy subagent v27): `retell-iac/snapshots/2026-04-09_master-pre-promote/`. Post-promotion snapshot: `retell-iac/snapshots/2026-04-09_testing-autolayout-fixed/` (byte-identical to live).
- **HVAC Standard TESTING agent** — `agent_6e7a2ae03c2fbd7a251fafcd00` / `conversation_flow_90da7ca2b270`. Was the authoritative source during the fix-and-promote cycle; MASTER is now aligned to it byte-for-byte.
- **`retell-iac/components/` is current.** Regenerated 2026-04-09 from the live snapshot via `scripts/split_snapshot.py`. 19 flat component files, new `flows/hvac-standard.template.json`, new `manifests/hvac-standard.yaml`. `build_agent.py` output is byte-identical to the live MASTER flow. Legacy subagent files archived at `components.legacy-subagent-20260409/`, `flows/hvac-standard.template.legacy-subagent-20260409.json`, `manifests/hvac-standard.legacy-subagent-20260409.yaml`.
- **n8n onboarding workflow** — Standard `4Hx7aRdzMl5N0uJP`. Includes `slack_webhook_url` mapping from Jotform field `q76_slackIncoming` (2026-04-09) + Demo/Live agent naming patch at L25/L683 of `Build Retell Prompt` (2026-04-09).
- **HVAC Call Processor — lean fan-out** — `Kg576YtPM9yEacKn`. Rewritten 2026-04-09 as 8-node fan-out (webhook → filter → lookup → build payload → email/slack/sms). Zero Supabase writes. Triggers on `is_lead OR urgency=emergency`. Brevo key inlined from vault. SMS stub marked `TELNYX-TODO`. Generator: [tools/build_call_processor_workflow.py](../tools/build_call_processor_workflow.py).
- **Weekly client report** — [tools/weekly_client_report.py](../tools/weekly_client_report.py). Runs via external cron (`TZ=America/New_York python tools/weekly_client_report.py --tz America/New_York`) Sunday 18:00 local per timezone bucket. Pulls calls from Retell `list-calls`, sends branded email via Brevo + optional Slack to every client in that TZ. Not yet deployed on a schedule (1 client pre-launch); deploy cron once a second client lands.
- **Jotform `260795139953066`** — HVAC Standard onboarding. Field `slackIncoming` (qid 76) added to Section 5 (optional).
- **Slack (Syntharra workspace)** — clean 7-channel structure: `#all-syntharra`, `#billing`, `#calls`, `#daily-digest`, `#leads`, `#onboarding`, `#ops-alerts`. 15 clutter channels archived 2026-04-09. Bot token in vault (`service_name='Slack'`, `key_type='bot_token'`).
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

## 2026-04-09 session — late-session work (infra cleanup + notification rewire)

**MASTER arch swap promoted.** Legacy subagent MASTER replaced with code-node architecture via `split_snapshot.py` + `promote.py` round-trip; build output byte-identical to live. All 19 nodes. `retell-iac/components/` regenerated. Legacy archived.

**Custom post-call analysis fields added to MASTER** — `is_lead` (boolean), `urgency` (enum emergency/high/normal/low/none), `is_spam` (boolean). Published. Snapshot refreshed. Unblocks Call Processor fan-out logic.

**n8n cloud MCP banned.** All `mcp__claude_ai_n8n__*` tool entries removed from `.claude/settings.json` + `.claude/settings.local.json`. CLAUDE.md rule added: Railway REST API is the only path. Leaked API key in settings allowlist scrubbed. n8n key rotated by Dan; new key vaulted.

**n8n workflow audit + archives.** 56 workflows reviewed, audit report at `docs/audits/2026-04-09-n8n-workflow-audit.md`. 6 Premium workflows + Weekly Newsletter deactivated + renamed `[ARCHIVED-2026-04-09]`, Dan clicked UI Archive to set `isArchived:true`. 1 workflow (`rGrnCr5mPFP2TIc7` Google Calendar dispatcher) accidentally hard-deleted during API probing and restored from backup as new ID `tp62gP2ntiqVvWZ7`. Standing rule added: never `DELETE` on n8n public API.

**HVAC Call Processor rewritten** from bloated 11-node Supabase-writer to 8-node lean fan-out (Retell webhook → filter → lookup → build payload → email/Slack/SMS stub). Zero Supabase writes. Syntharra-branded email HTML + Slack blocks. Triggers on `is_lead OR urgency=emergency`. Brevo key inlined from vault.

**Client notification fan-out wired end-to-end:**
- Jotform adds optional `Slack Incoming Webhook URL` field (qid 76) in Section 5
- Onboarding workflow `Parse JotForm Data` maps it to `slack_webhook_url`
- Call Processor `Has Slack?` gate posts to it only if present
- Fail-safe: null/blank slack_webhook_url silently skipped, email + SMS stub still fire

**Weekly client report** shipped as [tools/weekly_client_report.py](../tools/weekly_client_report.py) — per-TZ bucket invocation (option 1), pulls from Retell `list-calls`, sends Syntharra-branded email + optional Slack. Deployment deferred (1 client, cron would fire into the void); deploy command documented in script docstring.

**Slack workspace cleaned.** 22 → 7 channels. Bot token vaulted with scopes `channels:manage,channels:read,channels:join,chat:write,chat:write.public,groups:write,users:read`. 15 clutter channels archived via `conversations.archive`. `#daily-digest` created.

**n8n L25/L683 Demo/Live naming patch** applied via API. `Build Retell Prompt` node now emits `${isDemo ? 'Demo' : 'Live'} — ${companyName}` as the agent display name.

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
