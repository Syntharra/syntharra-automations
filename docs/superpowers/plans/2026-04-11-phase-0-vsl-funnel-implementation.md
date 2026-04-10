# Phase 0 — VSL + Pilot Funnel + Measurement Spine Implementation Plan

> ## ⚠️ PLAN STATUS: PARTIAL — tasks 1–19 written, tasks 20–52 pending
>
> **Last updated:** 2026-04-11
>
> **What's written (~1,100 lines, ready to execute):**
> - Day 1 complete: Tasks 1–12 (schema safety + migration + billing patches + session-end)
> - Day 2 complete: Tasks 13–18 (pilot Jotform fork + n8n onboarding branch + E2E)
> - Day 3 partial: Task 19 only (pilot_lifecycle.py skeleton + test scaffolding)
>
> **What's NOT written yet (~33 tasks remaining, ~2,000 more lines estimated):**
> - Day 3 Tasks 20–23: Brevo email send, Stripe Setup Intent + webhook, convert/expire logic, unit tests
> - Day 4 Tasks 24–29: Retell `pilot_expired` flow node, TESTING E2E, promote.py, Dan films
> - Day 5 Tasks 30–37: VSL production pipeline (call capture, Remotion, DaVinci, Mux upload)
> - Day 6 Tasks 38–46: `syntharra-website` clone, `start.html`, tracker JS, Edge Function, full E2E
> - Day 7 Tasks 47–52: Pre-live checklist verification (53 items from spec § 10.3), smoke test
>
> **Execution strategy (per Dan's 2026-04-11 "option B" decision):**
> 1. Execute Day 1 Tasks 1–7 first (all read-only or Supabase-branch-only, no prod writes)
> 2. **HARD GATE at Task 8** — prod schema migration requires Dan's explicit confirmation
> 3. Complete Day 1 Tasks 8–12 after gate passes
> 4. Write Day 3 Tasks 20–23 before executing Day 3
> 5. Execute Day 2 while Day 3 tasks are being written
> 6. Repeat write-then-execute pattern for Days 4–7
>
> **Progress tracking (4-way redundancy per Dan's "DO NOT LOSE track" constraint):**
> - **This plan file** — task checkboxes marked `- [x]` as completed
> - **Memory file** — `memory/project_phase0_progress.md` (authoritative resume pointer, check first when resuming)
> - **STATE.md** — `docs/STATE.md` Phase 0 progress section (end-of-day updates)
> - **TodoWrite** — in-session granular tracker
>
> ---

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the closing asset (4:30 founder-led VSL at `syntharra.com/start`), the no-card 14-day / 200-minute pilot flow, and the `marketing_events` measurement spine — so every future marketing channel in Phases 1–4 has a working destination to funnel traffic into and every piece of content is traceable back to conversions.

**Spec:** `docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md` — read it first. This plan assumes the spec is accepted.

**Architecture:**
- **Landing page + tracker** live in `syntharra-website` repo (sibling clone). Vanilla HTML/CSS/JS, Mux-hosted VSL, custom `marketing-tracker.js` posting to Supabase Edge Function.
- **Pilot flow** extends existing `4Hx7aRdzMl5N0uJP` n8n onboarding workflow with an `Is Pilot?` branch. Pilots use `status='pilot'` + `pilot_mode=true` and are naturally excluded from billing crons via defensive filters.
- **Pilot lifecycle** is a new Python Railway cron (`tools/pilot_lifecycle.py`) mirroring the pattern of `monthly_minutes.py` — stdlib only, reads credentials from `syntharra_vault`, idempotent via `pilot_email_sends` log table.
- **Retell graceful pause** uses a per-agent dynamic variable `pilot_expired` routed to a new `pilot_expired` flow node. Promoted through TESTING → MASTER via `retell-iac/scripts/promote.py`.
- **Measurement spine**: two new Supabase tables (`marketing_events`, `marketing_assets`) + RLS + Edge Function ingestion endpoint with bot filter.

**Tech Stack:** Python 3.11 stdlib, Supabase REST + MCP (branching, edge functions), Retell API v2, Railway n8n REST API, Mux Data + Mux Player, Stripe Setup Intent + Subscriptions, Brevo templated email, Remotion / DaVinci Resolve / CapCut for video, vanilla HTML/CSS/JS for landing page.

**Hard rules inherited from `CLAUDE.md` and `docs/RULES.md`:**
- IDs come from `docs/REFERENCE.md` only.
- All credentials from `syntharra_vault` via Supabase REST — never inline, never in `.env` committed to git.
- Never test on live Retell agents. Clone → TESTING → `retell-iac/scripts/promote.py` → MASTER.
- n8n = Railway REST API only. No `mcp__claude_ai_n8n__*` tools. Never `DELETE` on n8n public API.
- Before modifying any n8n workflow: full JSON backup to `docs/audits/n8n-backups-YYYYMMDD/`.
- Every failure gets a `FAILURES.md` row. If it implies a standing rule, add to `RULES.md` in the same commit.
- Session ends with `python tools/session_end.py --topic phase-0-<day> --summary "<line>"`.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `docs/audits/supabase-backups-20260411/client_subscriptions-pre-pilot.sql` | **Create** | Pre-migration data dump via `pg_dump` (or MCP equivalent) |
| `docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot.json` | **Create** | n8n workflow backup before pilot branch added |
| `docs/audits/n8n-backups-20260411/xKD3ny6kfHL0HHXq-pre-pilot.json` | **Create** | Stripe webhook workflow backup |
| `docs/audits/n8n-backups-20260411/6Mwire23i6InrnYZ-pre-pilot.json` | **Create** | Client Update Form workflow backup |
| `docs/audits/n8n-backups-20260411/z8T9CKcUp7lLVoGQ-pre-pilot.json` | **Create** | Slack Setup workflow backup |
| `docs/audits/n8n-backups-20260411/Y1EptXhOPAmosMbs-pre-pilot.json` | **Create** | Retell proxy webhook workflow backup |
| `docs/audits/2026-04-11-phase0-schema-scan.md` | **Create** | Results of n8n scan for `client_subscriptions` references |
| `supabase/migrations/20260411_phase0_pilot_schema.sql` | **Create** | Forward migration SQL (branch-selected by status column type) |
| `supabase/migrations/20260411_phase0_pilot_schema_rollback.sql` | **Create** | Rollback SQL (paired with forward) |
| `tools/pilot_lifecycle.py` | **Create** | Daily Railway cron: day-3/7/12 emails, day-14 convert/expire, win-back sequences |
| `tools/test_pilot_lifecycle.py` | **Create** | Unit tests for pilot_lifecycle.py pure logic |
| `tools/apply_pilot_migration.py` | **Create** | Safe migration runner: queries live schema, selects migration branch, dry-runs, applies |
| `tools/build_pilot_jotform.py` | **Create** | Clones existing Jotform `260795139953066` as pilot fork via Jotform API |
| `tools/stripe_pilot_setup.py` | **Create** | Creates Stripe products/prices/setup intent for the pilot flow |
| `tools/test_e2e_pilot.py` | **Create** | Compressed-time E2E test harness: triggers full pilot → convert and pilot → expire flows |
| `tools/monthly_minutes.py` | **Modify** (line 67) | Add `&pilot_mode=eq.false` defensive filter |
| `tools/usage_alert.py` | **Modify** (line 70) | Add `&pilot_mode=eq.false` defensive filter |
| `retell-iac/components/pilot_expired_node.json` | **Create** | New Retell flow code node for graceful pause |
| `retell-iac/flows/hvac-standard.template.json` | **Modify** | Add `pilot_expired` node reference + edge from identify-call |
| `retell-iac/snapshots/2026-04-11_pre-pilot-expired/` | **Create** | Pre-change MASTER snapshot (full flow JSON) |
| `shared/email-templates/pilot-welcome.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-day-3.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-day-7.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-day-12.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-converted.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-card-added.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-expired.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-winback-16.html` | **Create** | Brevo template source |
| `shared/email-templates/pilot-winback-30.html` | **Create** | Brevo template source |
| `tools/upload_brevo_templates.py` | **Create** | Uploads the 9 pilot email HTML files to Brevo via API, records template IDs |
| `docs/REFERENCE.md` | **Modify** | Add new IDs: pilot Jotform, Mux playback, Brevo template IDs, marketing asset UUIDs |
| `docs/STATE.md` | **Modify** | Update "What's live" and "In flight" sections |
| `supabase/schema_LIVE.md` | **Modify** | Document new tables + pilot columns + `status='pilot'` enum value |
| `../syntharra-website/start.html` | **Create** | VSL landing page (sibling repo) |
| `../syntharra-website/assets/marketing-tracker.js` | **Create** | Client-side event tracker |
| `../syntharra-website/assets/start.css` | **Create** | Landing-page-specific styles (reuse `dashboard.css` tokens) |
| Supabase Edge Function `marketing-event-ingest` | **Create** (deployed, not a repo file) | Bot-filtered event insertion endpoint |
| Supabase table `marketing_events` | **Create** | Unified event log |
| Supabase table `marketing_assets` | **Create** | Asset registry for attribution |
| Supabase table `pilot_email_sends` | **Create** | Idempotency log for the cron |

---

## Credentials reference (all from `syntharra_vault`)

Fetch once at the start of each session before running any task. Never commit these values.

| Service | `service_name` | `key_type` | Export as |
|---|---|---|---|
| Supabase | `Supabase` | `service_role_key` | `SUPABASE_SERVICE_KEY` |
| Supabase | `Supabase` | `project_url` | `SUPABASE_URL` (prefix with `https://`) |
| Retell AI | `Retell AI` | `api_key` | `RETELL_API_KEY` |
| n8n Railway | `n8n Railway` | `api_key` | `N8N_API_KEY` |
| Brevo | `Brevo` | `api_key` | `BREVO_API_KEY` |
| Stripe (test) | `Stripe` | `secret_key_test` | `STRIPE_SECRET_KEY_TEST` |
| Stripe (live) | `Stripe` | `secret_key_live` | `STRIPE_SECRET_KEY_LIVE` |
| Stripe webhook | `Stripe` | `webhook_signing_secret` | `STRIPE_WEBHOOK_SECRET` |
| Jotform | `Jotform` | `api_key` | `JOTFORM_API_KEY` |
| Mux | `Mux` | `token_id` | `MUX_TOKEN_ID` (vault in Day 1 Task 2) |
| Mux | `Mux` | `token_secret` | `MUX_TOKEN_SECRET` |
| Mux | `Mux` | `playback_signing_key` | `MUX_SIGNING_KEY` (optional — only if we use signed playback) |

Fetch script pattern (top of every session):

```bash
# Run once at session start. Values come from syntharra_vault via Supabase REST.
# Use tools/fetch_vault.py if it exists, or curl directly.
export SUPABASE_URL="https://hgheyqwnrcvwtgngqdnq.supabase.co"
export SUPABASE_SERVICE_KEY=""  # fill from vault
export RETELL_API_KEY=""
export N8N_API_KEY=""
export BREVO_API_KEY=""
export STRIPE_SECRET_KEY_TEST=""
export STRIPE_SECRET_KEY_LIVE=""
export STRIPE_WEBHOOK_SECRET=""
export JOTFORM_API_KEY=""
export MUX_TOKEN_ID=""
export MUX_TOKEN_SECRET=""
```

---

## Plan layout

This plan is organized by the 7-day sequence from spec § 8. Each day has 4–8 tasks; each task has bite-sized steps with exact code, exact commands, and exact expected output. Day 1 is the highest-stakes (schema migration on a tested pipeline) and has the most verification gates.

- **Day 1:** Schema safety gates + migration + billing tool patches
- **Day 2:** Pilot Jotform fork + n8n onboarding branch
- **Day 3:** Pilot lifecycle cron + Stripe Setup Intent + Brevo templates
- **Day 4:** Retell `pilot_expired` flow + Dan films
- **Day 5:** VSL production + Mux upload
- **Day 6:** Landing page + tracker + E2E test
- **Day 7:** Pre-live checklist verification + smoke test

---

# DAY 1 — Schema safety gates + migration + billing tool patches

**Day 1 goal:** get `marketing_events` + `marketing_assets` + `client_subscriptions` pilot columns into prod WITHOUT regressing the already-tested paid-customer pipeline. Every step here has an explicit verification gate.

**Critical ordering:** the n8n workflow scan (Task 2) runs BEFORE any schema change (Task 5+) because if a workflow hard-codes `status='active'` as a "real customer" proxy, the migration strategy has to change.

---

## Task 1: Fetch vault credentials + verify tool access

**Files:** none created. Environment setup only.

- [ ] **Step 1: Fetch credentials from `syntharra_vault`**

Run this SQL via Supabase MCP `execute_sql` (or via `curl` against the Supabase REST API if MCP is unavailable):

```sql
select service_name, key_type, key_value
from syntharra_vault
where service_name in ('Supabase', 'Retell AI', 'n8n Railway', 'Brevo', 'Stripe', 'Jotform')
order by service_name, key_type;
```

Export each returned `key_value` to the corresponding env var per the credentials table above.

- [ ] **Step 2: Verify Supabase MCP access**

Run:
```bash
# Via MCP: mcp__claude_ai_Supabase__list_tables
# Expected: returns list including client_subscriptions, client_agents, syntharra_vault
```

Expected: list includes `client_subscriptions`, `client_agents`, `syntharra_vault`, `stripe_payment_data`, `billing_cycles`.

If MCP is unavailable, fall back to:
```bash
curl -s "$SUPABASE_URL/rest/v1/client_subscriptions?select=count&limit=1" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY"
```
Expected: `[{"count": <n>}]` without error.

- [ ] **Step 3: Verify n8n Railway access**

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.syntharra.com/api/v1/workflows?limit=1" | head -c 500
```

Expected: JSON with `data` array. If 401/403, the vault key is stale — ask Dan to rotate per `CLAUDE.md` n8n rule.

- [ ] **Step 4: Verify Retell API access**

```bash
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-agent/agent_b46aef9fd327ec60c657b7a30a" | head -c 500
```

Expected: JSON with `agent_id` field matching `agent_b46aef9fd327ec60c657b7a30a`.

- [ ] **Step 5: Verify Stripe access (test mode)**

```bash
curl -s https://api.stripe.com/v1/products?limit=1 \
  -u "$STRIPE_SECRET_KEY_TEST:"
```

Expected: JSON `{"object": "list", "data": [...]}` with at least one product.

**If any of steps 2–5 fail:** halt Day 1. Document the failure in `docs/FAILURES.md`. Do not proceed until all four tools are accessible.

---

## Task 2: Scan n8n workflows for `client_subscriptions` references

**Files:**
- Create: `docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot.json`
- Create: `docs/audits/n8n-backups-20260411/xKD3ny6kfHL0HHXq-pre-pilot.json`
- Create: `docs/audits/n8n-backups-20260411/6Mwire23i6InrnYZ-pre-pilot.json`
- Create: `docs/audits/n8n-backups-20260411/z8T9CKcUp7lLVoGQ-pre-pilot.json`
- Create: `docs/audits/n8n-backups-20260411/Y1EptXhOPAmosMbs-pre-pilot.json`
- Create: `docs/audits/2026-04-11-phase0-schema-scan.md`

- [ ] **Step 1: Create backups directory**

```bash
mkdir -p docs/audits/n8n-backups-20260411
```

- [ ] **Step 2: Pull all 5 suspect workflows via Railway REST API**

```bash
for WORKFLOW_ID in 4Hx7aRdzMl5N0uJP xKD3ny6kfHL0HHXq 6Mwire23i6InrnYZ z8T9CKcUp7lLVoGQ Y1EptXhOPAmosMbs; do
  echo "Pulling $WORKFLOW_ID..."
  curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "https://n8n.syntharra.com/api/v1/workflows/$WORKFLOW_ID" \
    > "docs/audits/n8n-backups-20260411/${WORKFLOW_ID}-pre-pilot.json"
  wc -c "docs/audits/n8n-backups-20260411/${WORKFLOW_ID}-pre-pilot.json"
done
```

Expected: each file >1KB. If any is <200 bytes, inspect — it's probably an error response.

- [ ] **Step 3: Grep each workflow for `client_subscriptions`**

```bash
cd docs/audits/n8n-backups-20260411
grep -l client_subscriptions *.json || echo "NONE FOUND"
grep -c client_subscriptions *.json
```

- [ ] **Step 4: Audit `SELECT *` usage against `client_subscriptions`**

```bash
grep -n 'select=\*' *.json | grep -i subscription || echo "NO SELECT * found"
grep -n 'select%3D%2A' *.json | grep -i subscription || echo "NO encoded SELECT * found"
```

Expected: no hits. If hits exist, those workflow nodes will need updating when new columns are added (because downstream JavaScript may reference the full column set and break silently when new columns appear). Document each hit.

- [ ] **Step 5: Audit `status === 'active'` hard-codes**

```bash
grep -n "status.*active" *.json | grep -iv "test\|comment" > /tmp/status_hits.txt
cat /tmp/status_hits.txt
```

For each hit, inspect whether the check is a proxy for "real paying customer." If yes, it must be patched to exclude `status === 'pilot'`. Document in the scan report.

- [ ] **Step 6: Write the scan report**

Create `docs/audits/2026-04-11-phase0-schema-scan.md` with:

```markdown
# Phase 0 — n8n Schema Scan Report (2026-04-11)

## Scope
Scanned 5 n8n workflows for references to `client_subscriptions` before the Phase 0 schema migration (§ 6.2.1 of the spec).

## Workflows scanned
- 4Hx7aRdzMl5N0uJP (HVAC Standard onboarding)
- xKD3ny6kfHL0HHXq (Stripe webhook handler)
- 6Mwire23i6InrnYZ (Client Update Form)
- z8T9CKcUp7lLVoGQ (Slack Setup)
- Y1EptXhOPAmosMbs (Retell proxy webhook)

## Findings

### `client_subscriptions` references

| Workflow | Hit count | Operation (read/write) | Risk |
|---|---|---|---|
| 4Hx7aRdzMl5N0uJP | <count from step 3> | <write via reconcile_jotform_stripe> | <assessed> |
| xKD3ny6kfHL0HHXq | <count> | <write via handle-checkout-completed> | <assessed> |
| 6Mwire23i6InrnYZ | <count> | <?> | <?> |
| z8T9CKcUp7lLVoGQ | <count> | <?> | <?> |
| Y1EptXhOPAmosMbs | <count> | <?> | <?> |

### `SELECT *` hits
<from step 4 — list each, or "none">

### `status === 'active'` proxy hits
<from step 5 — list each with workflow, node name, line context>

## Migration-blocking issues
<any workflow that needs patching BEFORE the schema migration runs. If none: "None — safe to proceed with migration.">

## Actions required before Task 5 (migration run)
- [ ] Patch workflow X node Y to exclude `status === 'pilot'` (only if issues found above)
- [ ] Re-backup patched workflows to same directory with `-post-patch.json` suffix
```

Fill in with actual findings.

- [ ] **Step 7: Commit the backups + scan report**

```bash
git add docs/audits/n8n-backups-20260411/ docs/audits/2026-04-11-phase0-schema-scan.md
git commit -m "$(cat <<'EOF'
audit(phase0): n8n workflow scan + backups pre-pilot-migration

Per spec § 6.2.1 pre-migration gate: pulled JSON for all 5 suspect
workflows that might reference client_subscriptions, grep-scanned for
SELECT * and status='active' proxies, documented findings in
docs/audits/2026-04-11-phase0-schema-scan.md.

Backups are the authoritative pre-pilot state for rollback reference.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Verify live `client_subscriptions` schema, select migration branch

**Files:** none created yet. This task selects which migration SQL to write.

- [ ] **Step 1: Query the live schema via Supabase MCP**

Run via `mcp__claude_ai_Supabase__execute_sql`:

```sql
select column_name, data_type, column_default, is_nullable
from information_schema.columns
where table_schema = 'public' and table_name = 'client_subscriptions'
order by ordinal_position;
```

Save the output to `docs/audits/2026-04-11-phase0-schema-scan.md` under a new `## Live client_subscriptions schema` section.

- [ ] **Step 2: Query CHECK constraints**

```sql
select conname, pg_get_constraintdef(oid) as definition
from pg_constraint
where conrelid = 'public.client_subscriptions'::regclass
  and contype = 'c';
```

- [ ] **Step 3: Check if `status` is an enum type**

```sql
select
  a.attname as column_name,
  t.typname as type_name,
  t.typtype as type_type  -- 'b' = base, 'e' = enum, 'd' = domain
from pg_attribute a
join pg_type t on a.atttypid = t.oid
where a.attrelid = 'public.client_subscriptions'::regclass
  and a.attname = 'status'
  and a.attnum > 0;
```

- [ ] **Step 4: Pick the migration branch based on findings**

Decision tree:

| Query result | Branch |
|---|---|
| `status` is `text` with NO check constraint | **Branch A** — trivially add `'pilot'` as a valid string value. No DDL change needed for the `status` column itself; just start writing `'pilot'` in the new rows. |
| `status` is `text` WITH a CHECK constraint like `status IN (...)` | **Branch B** — drop the old constraint, add a new one including `'pilot'`. Rollback: drop the new, re-add the old. |
| `status` is a PostgreSQL ENUM type | **Branch C** — DO NOT mutate the enum. Use `pilot_mode` boolean column as the primary pilot indicator. `status` stays `'active'` on pilot rows; billing tools exclude them via `pilot_mode=eq.false` defensive filter. |

Document the selected branch in the scan report file:

```markdown
## Migration branch selected
**Branch: <A | B | C>**

Reasoning: <copy the relevant row from the table above, plus the actual query result>
```

- [ ] **Step 5: Commit the scan report update**

```bash
git add docs/audits/2026-04-11-phase0-schema-scan.md
git commit -m "audit(phase0): document live client_subscriptions schema + migration branch selection"
```

---

## Task 4: Create Supabase branch + dump existing data

**Files:**
- Create: `docs/audits/supabase-backups-20260411/client_subscriptions-pre-pilot.sql`
- Create: `docs/audits/supabase-backups-20260411/client_subscriptions-rowcount-pre-pilot.txt`

- [ ] **Step 1: Create backups directory**

```bash
mkdir -p docs/audits/supabase-backups-20260411
```

- [ ] **Step 2: Dump existing `client_subscriptions` data via MCP**

Via `mcp__claude_ai_Supabase__execute_sql`:

```sql
select json_agg(row_to_json(cs)) from client_subscriptions cs;
```

Save the result to `docs/audits/supabase-backups-20260411/client_subscriptions-pre-pilot.json`.

- [ ] **Step 3: Capture row counts baseline**

```sql
select
  count(*) as total_rows,
  count(*) filter (where status = 'active') as active_rows,
  count(distinct agent_id) as unique_agents
from client_subscriptions;
```

Save output to `docs/audits/supabase-backups-20260411/client_subscriptions-rowcount-pre-pilot.txt`.

- [ ] **Step 4: Create a Supabase branch for dry-run**

Via `mcp__claude_ai_Supabase__create_branch`:

```
name: phase0-pilot-migration-dryrun
```

Record the branch ID in the scan report.

Expected: a branch URL + project ref returned. If the branch creation fails due to cost, run `mcp__claude_ai_Supabase__get_cost` first and confirm with `mcp__claude_ai_Supabase__confirm_cost` per Supabase MCP conventions.

- [ ] **Step 5: Commit the backups**

```bash
git add docs/audits/supabase-backups-20260411/
git commit -m "$(cat <<'EOF'
audit(phase0): backup client_subscriptions pre-pilot migration

Full data dump + row count baseline saved per spec § 10.3 pre-live
checklist. Supabase branch created for dry-run testing before prod
migration runs.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Write forward migration SQL (branch-selected)

**Files:**
- Create: `supabase/migrations/20260411_phase0_pilot_schema.sql`

- [ ] **Step 1: Write the migration file header**

Create `supabase/migrations/20260411_phase0_pilot_schema.sql`:

```sql
-- 2026-04-11 — Phase 0 — VSL + Pilot Funnel + Measurement Spine
-- Spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md
-- Plan: docs/superpowers/plans/2026-04-11-phase-0-vsl-funnel-implementation.md
--
-- Adds:
--   - pilot columns to client_subscriptions (10 new)
--   - partial indexes for pilot queries
--   - marketing_events table (event log)
--   - marketing_assets table (asset registry)
--   - pilot_email_sends table (cron idempotency log)
--
-- Migration branch: <A | B | C>  (fill in from Task 3 Step 4)
-- Rollback: see 20260411_phase0_pilot_schema_rollback.sql
--
-- This migration is additive. Existing rows receive defaults for new
-- non-null columns. No data mutation on existing rows.

begin;
```

- [ ] **Step 2: Append the `client_subscriptions` column additions**

```sql
-- === client_subscriptions: pilot columns ===
alter table public.client_subscriptions
  add column if not exists pilot_mode boolean not null default false,
  add column if not exists pilot_started_at timestamptz,
  add column if not exists pilot_ends_at timestamptz,
  add column if not exists pilot_minutes_allotted integer not null default 0,
  add column if not exists pilot_minutes_used integer not null default 0,
  add column if not exists payment_method_added_at timestamptz,
  add column if not exists first_touch_asset_id text,
  add column if not exists last_touch_asset_id text,
  add column if not exists first_touch_utm jsonb,
  add column if not exists last_touch_utm jsonb;

create index if not exists idx_client_subscriptions_pilot_active
  on public.client_subscriptions (pilot_ends_at)
  where pilot_mode = true;

create index if not exists idx_client_subscriptions_first_touch_asset
  on public.client_subscriptions (first_touch_asset_id)
  where first_touch_asset_id is not null;
```

- [ ] **Step 3: Append the branch-specific `status` handling**

**For Branch A (no constraint):**
```sql
-- === Branch A: status is plain TEXT, no constraint change needed ===
-- Pilot rows will use status='pilot'. No DDL required here.
-- (The billing tool defensive filter handles isolation.)
```

**For Branch B (CHECK constraint):**
```sql
-- === Branch B: drop + recreate CHECK constraint to include 'pilot' ===
-- Capture the existing constraint name from docs/audits/2026-04-11-phase0-schema-scan.md
-- (replace <OLD_CONSTRAINT_NAME> with the actual value from Task 3)
alter table public.client_subscriptions
  drop constraint if exists <OLD_CONSTRAINT_NAME>;

alter table public.client_subscriptions
  add constraint client_subscriptions_status_check
  check (status in ('active', 'cancelled', 'past_due', 'incomplete', 'trialing', 'pilot'));
-- Adjust the list above to match the OLD values + 'pilot'. Do not drop values.
```

**For Branch C (ENUM):**
```sql
-- === Branch C: do NOT mutate the enum ===
-- Pilot rows will have status='active' (or equivalent "real" status)
-- and be isolated via pilot_mode=true + defensive billing filters.
-- No DDL required here for status.
```

- [ ] **Step 4: Append `marketing_events` table**

```sql
-- === marketing_events ===
create table if not exists public.marketing_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  session_id text not null,
  visitor_id text,
  client_agent_id text,
  event_type text not null,
  asset_id text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  utm_content text,
  utm_term text,
  referrer text,
  user_agent text,
  ip_country text,
  ip_region text,
  metadata jsonb
);

create index if not exists idx_marketing_events_visitor
  on public.marketing_events (visitor_id, created_at desc);
create index if not exists idx_marketing_events_asset
  on public.marketing_events (asset_id, event_type);
create index if not exists idx_marketing_events_client_agent
  on public.marketing_events (client_agent_id);
create index if not exists idx_marketing_events_event_time
  on public.marketing_events (event_type, created_at desc);

alter table public.marketing_events enable row level security;

create policy marketing_events_service_role_all
  on public.marketing_events
  for all to service_role
  using (true) with check (true);
```

- [ ] **Step 5: Append `marketing_assets` table**

```sql
-- === marketing_assets ===
create table if not exists public.marketing_assets (
  id text primary key,
  created_at timestamptz not null default now(),
  asset_type text not null,
  title text not null,
  channel text,
  platform_asset_url text,
  variant_of text references public.marketing_assets(id),
  metadata jsonb,
  retired_at timestamptz
);

create index if not exists idx_marketing_assets_type_channel
  on public.marketing_assets (asset_type, channel);
create index if not exists idx_marketing_assets_created
  on public.marketing_assets (created_at desc);

alter table public.marketing_assets enable row level security;

create policy marketing_assets_service_role_all
  on public.marketing_assets
  for all to service_role
  using (true) with check (true);
```

- [ ] **Step 6: Append `pilot_email_sends` idempotency log**

```sql
-- === pilot_email_sends (cron idempotency) ===
create table if not exists public.pilot_email_sends (
  id bigserial primary key,
  client_agent_id text not null,
  email_key text not null,  -- 'pilot_welcome', 'pilot_day_3', etc.
  sent_at timestamptz not null default now(),
  brevo_message_id text,
  unique (client_agent_id, email_key)
);

create index if not exists idx_pilot_email_sends_agent
  on public.pilot_email_sends (client_agent_id, email_key);

alter table public.pilot_email_sends enable row level security;

create policy pilot_email_sends_service_role_all
  on public.pilot_email_sends
  for all to service_role
  using (true) with check (true);
```

- [ ] **Step 7: Close the migration**

```sql
commit;
-- End of forward migration 20260411_phase0_pilot_schema.sql
```

- [ ] **Step 8: Commit the migration file**

```bash
git add supabase/migrations/20260411_phase0_pilot_schema.sql
git commit -m "feat(phase0): forward migration — pilot columns + marketing_events + marketing_assets + pilot_email_sends"
```

---

## Task 6: Write rollback migration SQL

**Files:**
- Create: `supabase/migrations/20260411_phase0_pilot_schema_rollback.sql`

- [ ] **Step 1: Write the rollback file**

```sql
-- 2026-04-11 — Phase 0 — ROLLBACK of 20260411_phase0_pilot_schema.sql
-- Run this ONLY if the forward migration caused regressions on existing
-- paid customers or billing tools.
--
-- Safety: all drops are IF EXISTS. Running this twice is safe.
-- Data loss: dropping marketing_events / marketing_assets / pilot_email_sends
-- will lose any rows inserted into them post-migration. Back up before
-- running if data exists.

begin;

-- 1. Drop the new tables (data loss if rows exist)
drop table if exists public.pilot_email_sends cascade;
drop table if exists public.marketing_events cascade;
drop table if exists public.marketing_assets cascade;

-- 2. Drop the new indexes on client_subscriptions
drop index if exists idx_client_subscriptions_pilot_active;
drop index if exists idx_client_subscriptions_first_touch_asset;

-- 3. Drop the new columns from client_subscriptions (existing paid rows
--    lose default values, which is fine since they were defaults anyway)
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

-- 4. Branch-specific status rollback
-- For Branch B only: drop the new check constraint, re-add the old one.
-- Replace <OLD_CONSTRAINT_NAME> and <OLD_CHECK_VALUES> from the scan report.
-- alter table public.client_subscriptions
--   drop constraint if exists client_subscriptions_status_check;
-- alter table public.client_subscriptions
--   add constraint <OLD_CONSTRAINT_NAME> check (status in (<OLD_CHECK_VALUES>));

-- For Branch A or C: no status DDL rollback needed.

commit;
-- End of rollback 20260411_phase0_pilot_schema_rollback.sql
```

- [ ] **Step 2: Commit the rollback file**

```bash
git add supabase/migrations/20260411_phase0_pilot_schema_rollback.sql
git commit -m "feat(phase0): rollback migration paired with forward 20260411_phase0_pilot_schema"
```

---

## Task 7: Dry-run migration on Supabase branch

**Files:** none. This is a verification task.

- [ ] **Step 1: Apply the forward migration to the branch**

Via `mcp__claude_ai_Supabase__apply_migration` with the branch ID from Task 4 Step 4 and the SQL from Task 5.

Expected: migration succeeds with no errors.

- [ ] **Step 2: Verify new tables exist on the branch**

Via `mcp__claude_ai_Supabase__list_tables` targeting the branch.

Expected: `marketing_events`, `marketing_assets`, `pilot_email_sends` all present.

- [ ] **Step 3: Verify new columns on `client_subscriptions`**

```sql
select column_name from information_schema.columns
where table_schema = 'public'
  and table_name = 'client_subscriptions'
  and column_name like 'pilot_%' or column_name like '%_touch_%';
```

Expected: 10 columns (`pilot_mode`, `pilot_started_at`, `pilot_ends_at`, `pilot_minutes_allotted`, `pilot_minutes_used`, `payment_method_added_at`, `first_touch_asset_id`, `last_touch_asset_id`, `first_touch_utm`, `last_touch_utm`).

- [ ] **Step 4: Run `monthly_minutes.py` against the branch data (parity check)**

Set `SUPABASE_URL` to the branch URL temporarily and run:

```bash
python tools/monthly_minutes.py --dry-run 2>&1 | head -40
```

Expected: same row count / same agent IDs processed as when run against prod pre-migration. If different, the column additions broke the tool's query (shouldn't happen — explicit SELECT column list — but verify).

- [ ] **Step 5: Run `usage_alert.py` against the branch data**

```bash
python tools/usage_alert.py --dry-run 2>&1 | head -40
```

Same expectation.

- [ ] **Step 6: Run the rollback migration on the branch**

Apply the rollback SQL via `mcp__claude_ai_Supabase__execute_sql`.

- [ ] **Step 7: Verify schema returned to pre-migration state**

```sql
select column_name from information_schema.columns
where table_schema = 'public'
  and table_name = 'client_subscriptions'
  and column_name like 'pilot_%' or column_name like '%_touch_%';
```

Expected: 0 rows. If any pilot columns remain, the rollback is incomplete — fix before proceeding.

- [ ] **Step 8: Verify `marketing_events`/`marketing_assets`/`pilot_email_sends` are gone**

Via `mcp__claude_ai_Supabase__list_tables` on the branch.

Expected: these three tables absent.

- [ ] **Step 9: Document dry-run result in the scan report**

Append to `docs/audits/2026-04-11-phase0-schema-scan.md`:

```markdown
## Dry-run result (Task 7, YYYY-MM-DD HH:MM UTC)

- [x] Forward migration applied successfully to branch
- [x] All 3 new tables created
- [x] All 10 new columns added
- [x] monthly_minutes.py dry-run returned <N> rows, same as prod baseline
- [x] usage_alert.py dry-run returned <N> rows, same as prod baseline
- [x] Rollback migration returned schema to pre-migration state
- [x] All new tables dropped
- [x] All new columns dropped

**Dry-run status: PASS. Safe to apply to prod.**
```

- [ ] **Step 10: Commit**

```bash
git add docs/audits/2026-04-11-phase0-schema-scan.md
git commit -m "audit(phase0): dry-run migration passes on Supabase branch"
```

---

## Task 8: Apply migration to prod

**⚠️ THIS IS THE ONLY DESTRUCTIVE STEP ON DAY 1. Dan should be notified before running.**

**Files:** none. Modifies live Supabase schema.

- [ ] **Step 1: Notify Dan via Slack `#ops-alerts`**

```bash
# Via Slack MCP or curl to the Slack webhook for #ops-alerts
# Message: "Running Phase 0 pilot schema migration on prod in 60 seconds. Rollback ready. Ctrl-C me if concerned."
```

- [ ] **Step 2: Apply forward migration to prod**

Via `mcp__claude_ai_Supabase__apply_migration` targeting the main project (not the branch) with the SQL from `supabase/migrations/20260411_phase0_pilot_schema.sql`.

Expected: success.

- [ ] **Step 3: Verify new tables exist on prod**

```sql
select table_name from information_schema.tables
where table_schema = 'public'
  and table_name in ('marketing_events', 'marketing_assets', 'pilot_email_sends');
```

Expected: 3 rows.

- [ ] **Step 4: Verify pilot columns on prod `client_subscriptions`**

Same query as Task 7 Step 3.

Expected: 10 columns.

- [ ] **Step 5: Immediate smoke test — run both billing tools against prod**

```bash
python tools/monthly_minutes.py --dry-run 2>&1 | tee /tmp/monthly_post.txt
python tools/usage_alert.py --dry-run 2>&1 | tee /tmp/usage_post.txt
```

Compare to the baseline output from Task 7 Step 4. Must be identical. If not, halt and run the rollback (Task 11 emergency procedure below).

- [ ] **Step 6: Post Slack confirmation**

```bash
# Slack message: "Phase 0 schema migration applied to prod. Billing tool parity verified. Safe to continue."
```

- [ ] **Step 7: No git commit here** — migrations are applied, not committed. The SQL file is already committed (Task 5 Step 8). STATE.md update happens at end of Day 1.

---

## Task 9: Patch billing tools with defensive filter

**Files:**
- Modify: `tools/monthly_minutes.py:67`
- Modify: `tools/usage_alert.py:70`

- [ ] **Step 1: Read the current `monthly_minutes.py` query construction**

```bash
# Look at lines 60-80 of monthly_minutes.py to understand the full context
```

- [ ] **Step 2: Update `monthly_minutes.py`**

Change line 67 from:
```python
"/rest/v1/client_subscriptions?status=eq.active&select=agent_id,company_name,client_email,included_minutes,overage_rate,tier,stripe_customer_id,stripe_subscription_id"
```

To:
```python
"/rest/v1/client_subscriptions?status=eq.active&pilot_mode=eq.false&select=agent_id,company_name,client_email,included_minutes,overage_rate,tier,stripe_customer_id,stripe_subscription_id"
```

- [ ] **Step 3: Update `usage_alert.py`**

Change lines 70–72 from:
```python
url = (env("SUPABASE_URL").rstrip("/") +
       "/rest/v1/client_subscriptions"
       "?status=eq.active"
       "&select=agent_id,company_name,client_email,included_minutes,tier,overage_rate")
```

To:
```python
url = (env("SUPABASE_URL").rstrip("/") +
       "/rest/v1/client_subscriptions"
       "?status=eq.active"
       "&pilot_mode=eq.false"
       "&select=agent_id,company_name,client_email,included_minutes,tier,overage_rate")
```

- [ ] **Step 4: Dry-run both tools, verify output unchanged**

```bash
python tools/monthly_minutes.py --dry-run 2>&1 | diff - /tmp/monthly_post.txt
python tools/usage_alert.py --dry-run 2>&1 | diff - /tmp/usage_post.txt
```

Expected: no diff. The filter is a no-op right now (zero pilot rows exist), but it future-proofs us.

- [ ] **Step 5: Commit**

```bash
git add tools/monthly_minutes.py tools/usage_alert.py
git commit -m "$(cat <<'EOF'
fix(billing): add pilot_mode=eq.false defensive filter

Belt-and-suspenders per Phase 0 spec § 6.2.1. Even though pilot rows
use status='pilot' (naturally excluded by status=eq.active), this
defensive filter prevents any future regression where a pilot row
could accidentally get status='active' via manual edit or workflow bug.

No behavior change today (zero pilot rows in prod). Verified via
dry-run output parity.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Update `supabase/schema_LIVE.md` documentation

**Files:**
- Modify: `supabase/schema_LIVE.md`

- [ ] **Step 1: Add the new tables + pilot columns to the schema doc**

Open `supabase/schema_LIVE.md` and add (find the right place in the existing structure):

```markdown
## marketing_events
Unified event log for all marketing-driven events across channels.
Added 2026-04-11 (Phase 0).
Columns: id, created_at, session_id, visitor_id, client_agent_id,
event_type, asset_id, utm_*, referrer, user_agent, ip_country, ip_region,
metadata (jsonb).
RLS: service_role only.

## marketing_assets
Registry of every trackable piece of marketing content (VSL, videos,
emails, landing pages). Every asset gets a UUID used as stx_asset_id
in URL parameters.
Added 2026-04-11 (Phase 0).
Columns: id, created_at, asset_type, title, channel, platform_asset_url,
variant_of (self-FK), metadata, retired_at.
RLS: service_role only.

## pilot_email_sends
Idempotency log for pilot_lifecycle.py cron — prevents duplicate emails
if the cron runs twice on the same day.
Added 2026-04-11 (Phase 0).
Unique constraint: (client_agent_id, email_key).
RLS: service_role only.

## client_subscriptions — Phase 0 additions (2026-04-11)
New columns for the 14-day / 200-minute pilot flow:
- pilot_mode (boolean, default false)
- pilot_started_at, pilot_ends_at (timestamptz)
- pilot_minutes_allotted (integer, default 0)
- pilot_minutes_used (integer, default 0)
- payment_method_added_at (timestamptz)
- first_touch_asset_id, last_touch_asset_id (text)
- first_touch_utm, last_touch_utm (jsonb)

New `status` value: `'pilot'`. Flips to `'active'` on day-14 conversion
or `'expired'` on day-14 without card.
```

- [ ] **Step 2: Commit**

```bash
git add supabase/schema_LIVE.md
git commit -m "docs(supabase): document Phase 0 schema additions"
```

---

## Task 11: Emergency rollback procedure (REFERENCE ONLY — do not run unless needed)

This task is documentation of the rollback procedure. Do not execute any steps unless Task 8 Step 5 parity check fails OR a post-migration issue is discovered.

**If a rollback is needed:**

1. Notify Dan via Slack `#ops-alerts` IMMEDIATELY.
2. Capture any data in the new tables:
   ```sql
   select json_agg(row_to_json(e)) from marketing_events e;
   select json_agg(row_to_json(a)) from marketing_assets a;
   select json_agg(row_to_json(p)) from pilot_email_sends p;
   ```
   Save to `docs/audits/supabase-backups-20260411/marketing_data-pre-rollback.json`.
3. Revert the billing tool patches via `git revert` on the Task 9 commit.
4. Run the rollback SQL from `supabase/migrations/20260411_phase0_pilot_schema_rollback.sql` via Supabase MCP.
5. Verify baseline row counts return to pre-migration values (Task 4 Step 3 baseline).
6. Log the incident in `docs/FAILURES.md` with full timeline, root cause, and prevention.
7. Halt Phase 0 implementation. Do not proceed to Day 2 until the issue is understood and the spec is revised.

---

## Task 12: Update STATE.md + session-end

**Files:**
- Modify: `docs/STATE.md`

- [ ] **Step 1: Add Day 1 completion to STATE.md**

Add a new section under `## What's in flight` or a new `## Phase 0 progress` section:

```markdown
## Phase 0 progress (2026-04-11)

**Day 1 complete:** schema migration applied to prod. New tables
(`marketing_events`, `marketing_assets`, `pilot_email_sends`) live. Pilot
columns on `client_subscriptions` live. Billing tools patched with
defensive filter (no behavior change — verified via dry-run parity).

Pre-migration state preserved in `docs/audits/supabase-backups-20260411/`
and `docs/audits/n8n-backups-20260411/`. Rollback SQL ready at
`supabase/migrations/20260411_phase0_pilot_schema_rollback.sql`.

**Next:** Day 2 — pilot Jotform fork + n8n onboarding branch.
```

- [ ] **Step 2: Run session_end**

```bash
python tools/session_end.py --topic phase-0-day-1 --summary "Phase 0 day 1: schema migration applied, billing tools patched, rollback ready"
```

- [ ] **Step 3: Commit STATE.md update**

```bash
git add docs/STATE.md
git commit -m "chore(session): session-end 2026-04-11 phase-0-day-1 schema migration complete"
```

**End of Day 1.**

---

# DAY 2 — Pilot Jotform fork + n8n onboarding branch

**Day 2 goal:** create the pilot signup path end-to-end. Someone submits the pilot Jotform → `4Hx7aRdzMl5N0uJP` forks to the pilot branch → Retell agent clones → `client_subscriptions` row created with `status='pilot'`, `pilot_mode=true`, correct `pilot_ends_at`.

**Do not modify the existing paid path.** Every Day 2 test verifies paid onboarding still works unchanged.

---

## Task 13: Clone existing Jotform as pilot fork

**Files:**
- Create: `tools/build_pilot_jotform.py`
- Modify: `docs/REFERENCE.md` (record new form ID)

- [ ] **Step 1: Write the Jotform cloning script**

Create `tools/build_pilot_jotform.py`:

```python
#!/usr/bin/env python3
"""
build_pilot_jotform.py — Clone the existing HVAC Standard Jotform as the pilot fork.

Source form: 260795139953066 (HVAC Standard onboarding)
Target: new form with:
  - All fields from source
  - Headline changed to "Start your free 14-day Syntharra pilot"
  - Submit button label "Start my pilot"
  - 6 new hidden fields for tracking: stx_asset_id, utm_source, utm_medium, utm_campaign, utm_content, utm_term
  - One more hidden field: pilot_mode = true
  - Webhook pointed at the same n8n workflow (4Hx7aRdzMl5N0uJP)

Writes the new form ID to stdout. Record in docs/REFERENCE.md.

Usage:
  export JOTFORM_API_KEY=<from vault>
  python tools/build_pilot_jotform.py
"""
import json
import os
import sys
import urllib.request
import urllib.parse

SOURCE_FORM_ID = "260795139953066"
JOTFORM_API = "https://api.jotform.com"

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def api(method, path, data=None):
    url = f"{JOTFORM_API}{path}?apiKey={env('JOTFORM_API_KEY')}"
    if data is not None and method == "GET":
        url += "&" + urllib.parse.urlencode(data)
        body = None
    else:
        body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def main():
    # 1. Clone the source form
    print(f"Cloning Jotform {SOURCE_FORM_ID}...")
    result = api("POST", f"/form/{SOURCE_FORM_ID}/clone")
    new_form_id = result["content"]["id"]
    print(f"New form ID: {new_form_id}")

    # 2. Update title + headline
    api("POST", f"/form/{new_form_id}/properties", data={
        "properties[title]": "Start your free 14-day Syntharra pilot"
    })

    # 3. Add hidden tracking fields
    hidden_fields = [
        ("stx_asset_id", "control_hidden"),
        ("utm_source", "control_hidden"),
        ("utm_medium", "control_hidden"),
        ("utm_campaign", "control_hidden"),
        ("utm_content", "control_hidden"),
        ("utm_term", "control_hidden"),
        ("pilot_mode", "control_hidden"),
    ]
    for name, type_ in hidden_fields:
        api("POST", f"/form/{new_form_id}/questions", data={
            f"question[type]": type_,
            f"question[text]": name,
            f"question[name]": name,
            f"question[defaultValue]": "true" if name == "pilot_mode" else "",
        })

    # 4. Preserve the webhook (clones usually do, but verify)
    webhooks = api("GET", f"/form/{new_form_id}/webhooks")
    print(f"Webhooks: {webhooks}")

    print(f"\n=== Pilot form created: {new_form_id} ===")
    print(f"URL: https://form.jotform.com/{new_form_id}")
    print(f"Add to docs/REFERENCE.md under the Jotform section.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

```bash
export JOTFORM_API_KEY=$(python tools/fetch_vault.py Jotform api_key)
python tools/build_pilot_jotform.py
```

Expected: new form ID printed. Record the ID.

- [ ] **Step 3: Manually verify the form in the Jotform dashboard**

Open `https://form.jotform.com/<NEW_FORM_ID>` in a browser. Verify:
- Title: "Start your free 14-day Syntharra pilot"
- All original fields present
- Hidden fields added (visible in the form builder, not in the public view)
- Submit button works

If any field is missing or wrong, fix manually in the Jotform builder.

- [ ] **Step 4: Point the webhook to the n8n onboarding workflow**

In the Jotform builder → Settings → Integrations → Webhooks, verify the URL matches the existing HVAC Standard onboarding webhook:
```
https://n8n.syntharra.com/webhook/<WEBHOOK_PATH_FROM_4Hx7aRdzMl5N0uJP>
```

Get the webhook path from the existing form or from the n8n workflow JSON backup (Task 2 Step 2).

- [ ] **Step 5: Add the new form ID to `docs/REFERENCE.md`**

Under the Jotform section (find the existing `260795139953066` entry):

```markdown
| HVAC Standard paid onboarding | `260795139953066` | Paid flow, warm traffic from syntharra-checkout |
| **HVAC Standard pilot onboarding** | `<NEW_FORM_ID>` | **NEW 2026-04-11** — Phase 0 pilot flow, cold traffic from syntharra.com/start. Forks into n8n `Is Pilot?` branch. |
```

- [ ] **Step 6: Commit**

```bash
git add tools/build_pilot_jotform.py docs/REFERENCE.md
git commit -m "feat(phase0): create pilot Jotform fork + register ID in REFERENCE.md"
```

---

## Task 14: Back up `4Hx7aRdzMl5N0uJP` workflow (double-backup)

**Files:**
- Create: `docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json` (this is a SECOND backup, right before the modification, not the same as the pre-migration backup from Task 2)

- [ ] **Step 1: Re-pull the workflow**

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.syntharra.com/api/v1/workflows/4Hx7aRdzMl5N0uJP" \
  > docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json
```

- [ ] **Step 2: Verify size + JSON validity**

```bash
wc -c docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json
python -c "import json; json.load(open('docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json'))" && echo OK
```

Expected: file >50KB, JSON valid.

- [ ] **Step 3: Commit**

```bash
git add docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json
git commit -m "audit(phase0): second backup of onboarding workflow right before pilot branch edit"
```

---

## Task 15: Add `Is Pilot?` branch to `4Hx7aRdzMl5N0uJP`

**Files:** Modifies live n8n workflow via Railway REST API. Workflow JSON is not stored in the repo; backups are in `docs/audits/n8n-backups-20260411/`.

**Approach:** Because n8n workflow JSON is complex and error-prone to hand-edit in a plan file, this task uses a Python builder script that loads the workflow JSON, inserts the new node + connections, and PUTs the updated version. Mirrors the pattern of `tools/build_call_processor_workflow.py` that already exists per STATE.md.

- [ ] **Step 1: Write the workflow patcher**

Create `tools/patch_onboarding_workflow_add_pilot_branch.py`:

```python
#!/usr/bin/env python3
"""
Adds the 'Is Pilot?' IF branch to the HVAC Standard onboarding workflow (4Hx7aRdzMl5N0uJP).

What it adds:
  1. A new IF node "Is Pilot?" right after the Jotform webhook trigger,
     checking {{ $json.body.pilot_mode === 'true' }}
  2. A "Set Pilot Defaults" node on the true branch that writes:
     - pilot_mode = true
     - pilot_started_at = now()
     - pilot_ends_at = now() + 14 days
     - pilot_minutes_allotted = 200
     - pilot_minutes_used = 0
     - status = 'pilot'  (NOT 'active')
  3. Rewires the existing 'Lookup Stripe Payment' node to only run on the false (paid) branch.
  4. Both branches re-converge before 'Clone Retell Agent' (the rest of the pipeline is unchanged).
  5. Adds first_touch_asset_id, last_touch_asset_id, first_touch_utm, last_touch_utm
     to the client_subscriptions INSERT payload (both branches).

This modifies the workflow in-place via PUT /api/v1/workflows/{id}.
A backup MUST exist at docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json
before this runs.

Usage:
  export N8N_API_KEY=<from vault>
  python tools/patch_onboarding_workflow_add_pilot_branch.py --dry-run   # preview
  python tools/patch_onboarding_workflow_add_pilot_branch.py             # apply
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

WORKFLOW_ID = "4Hx7aRdzMl5N0uJP"
N8N_BASE = "https://n8n.syntharra.com"
BACKUP_PATH = Path("docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json")

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def n8n_api(method, path, body=None):
    url = f"{N8N_BASE}{path}"
    headers = {"X-N8N-API-KEY": env("N8N_API_KEY"), "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def load_workflow():
    # Prefer the backup (known good), but verify live matches
    if not BACKUP_PATH.exists():
        sys.exit(f"Backup missing at {BACKUP_PATH} — run Task 14 first.")
    with open(BACKUP_PATH) as f:
        return json.load(f)

def find_node(wf, name):
    for n in wf["nodes"]:
        if n["name"] == name:
            return n
    return None

def make_is_pilot_node(position):
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "typeValidation": "strict"},
                "conditions": [{
                    "id": "is-pilot-check",
                    "leftValue": "={{ $json.body.pilot_mode }}",
                    "rightValue": "true",
                    "operator": {"type": "string", "operation": "equals"}
                }],
                "combinator": "and"
            },
            "options": {}
        },
        "id": "is-pilot-branch",
        "name": "Is Pilot?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": position
    }

def make_set_pilot_defaults_node(position):
    return {
        "parameters": {
            "mode": "raw",
            "jsonOutput": json.dumps({
                "pilot_mode": True,
                "pilot_started_at": "={{ $now.toISO() }}",
                "pilot_ends_at": "={{ $now.plus({days: 14}).toISO() }}",
                "pilot_minutes_allotted": 200,
                "pilot_minutes_used": 0,
                "status": "pilot",
                "first_touch_asset_id": "={{ $('Webhook').item.json.body.stx_asset_id || null }}",
                "last_touch_asset_id": "={{ $('Webhook').item.json.body.stx_asset_id || null }}",
                "first_touch_utm": "={{ { source: $('Webhook').item.json.body.utm_source, medium: $('Webhook').item.json.body.utm_medium, campaign: $('Webhook').item.json.body.utm_campaign, content: $('Webhook').item.json.body.utm_content, term: $('Webhook').item.json.body.utm_term } }}",
                "last_touch_utm": "={{ { source: $('Webhook').item.json.body.utm_source, medium: $('Webhook').item.json.body.utm_medium, campaign: $('Webhook').item.json.body.utm_campaign, content: $('Webhook').item.json.body.utm_content, term: $('Webhook').item.json.body.utm_term } }}"
            }, indent=2)
        },
        "id": "set-pilot-defaults",
        "name": "Set Pilot Defaults",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3,
        "position": position
    }

def patch(wf, dry_run):
    # Find the Webhook trigger and the current first-post-webhook node
    webhook = find_node(wf, "Webhook")
    if not webhook:
        sys.exit("Could not find 'Webhook' node — workflow shape unexpected.")

    # Identify the node currently connected from Webhook (should be 'Parse JotForm Data')
    current_first = None
    for src, targets in wf.get("connections", {}).items():
        if src == "Webhook":
            current_first = targets["main"][0][0]["node"]
            break

    print(f"Current first-post-webhook node: {current_first}")

    # Insert IF node between Webhook and current_first
    webhook_pos = webhook["position"]
    is_pilot = make_is_pilot_node([webhook_pos[0] + 200, webhook_pos[1]])
    set_defaults = make_set_pilot_defaults_node([webhook_pos[0] + 400, webhook_pos[1] - 100])

    wf["nodes"].append(is_pilot)
    wf["nodes"].append(set_defaults)

    # Rewire: Webhook → Is Pilot?
    #         Is Pilot? (true) → Set Pilot Defaults → (current_first)
    #         Is Pilot? (false) → current_first  (unchanged path)
    wf["connections"]["Webhook"] = {"main": [[{"node": "Is Pilot?", "type": "main", "index": 0}]]}
    wf["connections"]["Is Pilot?"] = {
        "main": [
            [{"node": "Set Pilot Defaults", "type": "main", "index": 0}],  # true branch
            [{"node": current_first, "type": "main", "index": 0}]            # false branch
        ]
    }
    wf["connections"]["Set Pilot Defaults"] = {"main": [[{"node": current_first, "type": "main", "index": 0}]]}

    if dry_run:
        print("DRY RUN — workflow not updated.")
        print(f"Would add 2 nodes + rewire 3 connections.")
        print(f"Modified workflow JSON length: {len(json.dumps(wf))}")
        return

    # PUT the updated workflow
    print("Applying patch via PUT /api/v1/workflows/{id}...")
    # The PUT endpoint requires the full workflow object but rejects some fields
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", {})
    }
    result = n8n_api("PUT", f"/api/v1/workflows/{WORKFLOW_ID}", body=payload)
    print(f"Updated workflow id: {result.get('id')}")
    print(f"Total nodes: {len(result.get('nodes', []))}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    wf = load_workflow()
    patch(wf, args.dry_run)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run the patcher**

```bash
python tools/patch_onboarding_workflow_add_pilot_branch.py --dry-run
```

Expected: prints the current first-post-webhook node name and "DRY RUN — workflow not updated." No errors.

- [ ] **Step 3: Apply the patch**

```bash
python tools/patch_onboarding_workflow_add_pilot_branch.py
```

Expected: "Updated workflow id: 4Hx7aRdzMl5N0uJP" with node count = old count + 2.

- [ ] **Step 4: Re-pull the workflow and verify the new nodes exist**

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.syntharra.com/api/v1/workflows/4Hx7aRdzMl5N0uJP" \
  > docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-post-pilot-branch.json

python -c "
import json
wf = json.load(open('docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-post-pilot-branch.json'))
names = [n['name'] for n in wf['nodes']]
assert 'Is Pilot?' in names, 'Is Pilot? node missing'
assert 'Set Pilot Defaults' in names, 'Set Pilot Defaults node missing'
print('OK — both new nodes present')
print(f'Total nodes: {len(names)}')
"
```

Expected: "OK — both new nodes present".

- [ ] **Step 5: Activate the workflow if it was deactivated by the update**

```bash
curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.syntharra.com/api/v1/workflows/4Hx7aRdzMl5N0uJP/activate"
```

- [ ] **Step 6: Commit the patcher script and post-patch backup**

```bash
git add tools/patch_onboarding_workflow_add_pilot_branch.py docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-post-pilot-branch.json
git commit -m "feat(phase0): add Is Pilot? branch to onboarding workflow 4Hx7aRdzMl5N0uJP"
```

---

## Task 16: E2E test — paid path still works

**Goal:** prove the existing paid onboarding flow is unchanged. Critical regression gate.

**Files:** none created.

- [ ] **Step 1: Submit a test paid onboarding via the existing Jotform**

Open `https://form.jotform.com/260795139953066` in a browser. Fill with test data:
- Business name: "TEST PAID 2026-04-11"
- Owner: "Claude Test"
- Email: a test email you control
- Phone: any valid US number format
- Other fields: minimum valid data

Submit.

- [ ] **Step 2: Wait for n8n to run (<60 seconds) and check execution**

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.syntharra.com/api/v1/executions?workflowId=4Hx7aRdzMl5N0uJP&limit=1" | head -c 2000
```

Expected: one execution with `"finished": true` and `"stopped": null`. No errors.

- [ ] **Step 3: Verify the `client_subscriptions` row has `status='active'` and `pilot_mode=false`**

```sql
select agent_id, company_name, status, pilot_mode, pilot_started_at
from client_subscriptions
where company_name = 'TEST PAID 2026-04-11';
```

Expected: one row, `status='active'`, `pilot_mode=false`, `pilot_started_at` is NULL.

**If `status='pilot'` or `pilot_mode=true`:** the Is Pilot? branch is misfiring on paid submissions. Halt, inspect the workflow execution, fix the IF condition (should be checking for `'true'` as a string literal, not truthy).

- [ ] **Step 4: Cleanup the test row**

```sql
delete from client_subscriptions where company_name = 'TEST PAID 2026-04-11';
-- Also delete the Retell agent clone if it was created:
-- (use Retell API delete-agent after capturing the agent_id from step 3)
```

---

## Task 17: E2E test — pilot path works

- [ ] **Step 1: Submit a test pilot onboarding via the new pilot Jotform**

Open `https://form.jotform.com/<PILOT_FORM_ID>` in a browser.

⚠️ Add `?pilot_mode=true&stx_asset_id=test-pilot-e2e&utm_source=test` to the URL so the hidden fields are populated.

Fill with test data:
- Business name: "TEST PILOT 2026-04-11"
- Other fields: minimum valid

Submit.

- [ ] **Step 2: Check n8n execution**

Same as Task 16 Step 2.

- [ ] **Step 3: Verify the row has `status='pilot'`, `pilot_mode=true`, correct timestamps**

```sql
select agent_id, company_name, status, pilot_mode, pilot_started_at, pilot_ends_at,
       pilot_minutes_allotted, first_touch_asset_id, first_touch_utm
from client_subscriptions
where company_name = 'TEST PILOT 2026-04-11';
```

Expected:
- `status = 'pilot'`
- `pilot_mode = true`
- `pilot_started_at` ≈ now
- `pilot_ends_at` ≈ now + 14 days
- `pilot_minutes_allotted = 200`
- `first_touch_asset_id = 'test-pilot-e2e'`
- `first_touch_utm` contains `{"source": "test", ...}`

- [ ] **Step 4: Verify a Retell agent was cloned for the pilot**

```bash
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-agent/<AGENT_ID_FROM_STEP_3>" | head -c 500
```

Expected: a valid agent JSON. The pilot user can actually receive calls right now.

- [ ] **Step 5: Cleanup**

```sql
delete from client_subscriptions where company_name = 'TEST PILOT 2026-04-11';
```

Delete the Retell agent via `DELETE /v2/delete-agent/<agent_id>`.

- [ ] **Step 6: Commit the test results as a session log**

```bash
cat > docs/audits/2026-04-11-phase0-day2-e2e-results.md <<'EOF'
# Phase 0 Day 2 — E2E Test Results

## Paid path (Task 16)
- Jotform 260795139953066 submitted with test data
- n8n execution: <execution ID>, finished, no errors
- client_subscriptions row: status='active', pilot_mode=false ✅
- Retell agent cloned: <agent ID>
- Cleanup: row deleted, agent deleted

## Pilot path (Task 17)
- Jotform <PILOT_FORM_ID> submitted with test data + tracking params
- n8n execution: <execution ID>, finished, no errors
- client_subscriptions row: status='pilot', pilot_mode=true,
  pilot_ends_at=<timestamp>, first_touch_asset_id='test-pilot-e2e' ✅
- Retell agent cloned: <agent ID>
- Cleanup: row deleted, agent deleted

## Verdict
Both paths working. Day 2 complete.
EOF
git add docs/audits/2026-04-11-phase0-day2-e2e-results.md
git commit -m "test(phase0): Day 2 E2E verified — both paid and pilot onboarding paths working"
```

---

## Task 18: Day 2 session-end

- [ ] **Step 1: Update STATE.md Phase 0 progress section**

```markdown
**Day 2 complete:** pilot Jotform fork (`<FORM_ID>`) created, webhook
wired. `4Hx7aRdzMl5N0uJP` onboarding workflow has `Is Pilot?` branch
added. Both paths E2E-tested with real Jotform submissions — paid path
unchanged (status='active', pilot_mode=false), pilot path produces
correct state (status='pilot', pilot_mode=true, 14-day pilot_ends_at).

**Next:** Day 3 — pilot_lifecycle.py cron + Stripe Setup Intent + Brevo templates.
```

- [ ] **Step 2: Commit and session-end**

```bash
git add docs/STATE.md
python tools/session_end.py --topic phase-0-day-2 --summary "Phase 0 day 2: pilot onboarding path wired, both paths E2E verified"
git commit -m "chore(session): session-end 2026-04-11 phase-0-day-2 pilot onboarding wired"
```

**End of Day 2.**

---

# DAY 3 — Pilot lifecycle cron + Stripe Setup Intent + Brevo templates

**Day 3 goal:** build the daily state-transition engine. The cron needs to handle 7 distinct state transitions (day 3/7/12 emails, day 14 convert vs expire, day 16/30 win-back) idempotently. This is the day with the most testable pure logic, so TDD applies heavily.

**Granularity note:** Day 3 has 8 tasks that together produce ~600 lines of Python. Each task is a cohesive unit (one state transition or one integration). Tests are written before implementation.

---

## Task 19: Skeleton + vault fetch + pilot query

**Files:**
- Create: `tools/pilot_lifecycle.py`
- Create: `tools/test_pilot_lifecycle.py`

- [ ] **Step 1: Write the skeleton with env + helpers**

Create `tools/pilot_lifecycle.py`:

```python
#!/usr/bin/env python3
"""
pilot_lifecycle.py — Daily Railway cron for Phase 0 pilot state transitions.

Runs once per day (00:00 UTC via Railway cron).

State machine per active pilot row:
  Day 0  — pilot created by n8n onboarding (not this script)
  Day 3  — send pilot_day_3 email (first engagement report)
  Day 7  — send pilot_day_7 email (halfway report)
  Day 12 — send pilot_day_12 email (48hr warning)
  Day 14 — convert (if card) OR expire (if no card)
  Day 16 — send winback_day_16 email (expired only)
  Day 30 — send winback_day_30 email (expired only)

Idempotent via pilot_email_sends log table.

Usage:
  export SUPABASE_URL=...
  export SUPABASE_SERVICE_KEY=...
  export BREVO_API_KEY=...
  export STRIPE_SECRET_KEY=...  # live or test based on env
  export RETELL_API_KEY=...
  python tools/pilot_lifecycle.py --dry-run   # preview actions
  python tools/pilot_lifecycle.py             # execute
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional

def env(k: str) -> str:
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def http_json(method: str, url: str, headers: dict, body: Optional[dict] = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def sb_headers() -> dict:
    return {
        "apikey": env("SUPABASE_SERVICE_KEY"),
        "Authorization": f"Bearer {env('SUPABASE_SERVICE_KEY')}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_url(path: str) -> str:
    return env("SUPABASE_URL").rstrip("/") + path

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_ts(ts: str) -> datetime:
    # Supabase returns ISO 8601 like '2026-04-11T12:00:00+00:00'
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def fetch_active_pilots() -> list[dict]:
    """Fetch all rows where pilot_mode=true and not yet fully terminated."""
    url = sb_url(
        "/rest/v1/client_subscriptions"
        "?pilot_mode=eq.true"
        "&select=agent_id,company_name,client_email,pilot_started_at,pilot_ends_at,"
        "pilot_minutes_allotted,pilot_minutes_used,payment_method_added_at,status,"
        "stripe_customer_id,stripe_subscription_id,first_touch_asset_id"
    )
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        sys.exit(f"fetch_active_pilots failed: {status} {data}")
    return data

def already_sent(client_agent_id: str, email_key: str) -> bool:
    url = sb_url(
        f"/rest/v1/pilot_email_sends"
        f"?client_agent_id=eq.{client_agent_id}"
        f"&email_key=eq.{email_key}"
        f"&select=id"
    )
    status, data = http_json("GET", url, sb_headers())
    return status == 200 and len(data) > 0

def log_send(client_agent_id: str, email_key: str, brevo_message_id: str = "") -> None:
    url = sb_url("/rest/v1/pilot_email_sends")
    body = {
        "client_agent_id": client_agent_id,
        "email_key": email_key,
        "brevo_message_id": brevo_message_id or None
    }
    http_json("POST", url, sb_headers(), body)

# --- Placeholder stubs to be implemented in Tasks 20-23 ---

def send_brevo_email(template_key: str, to_email: str, merge_data: dict) -> str:
    """Returns Brevo message ID."""
    raise NotImplementedError

def emit_marketing_event(event_type: str, client_agent_id: str, metadata: dict) -> None:
    raise NotImplementedError

def convert_pilot_to_paid(pilot: dict) -> None:
    raise NotImplementedError

def expire_pilot(pilot: dict) -> None:
    raise NotImplementedError

def pause_retell_agent(agent_id: str) -> None:
    raise NotImplementedError

# --- Main state machine ---

def process_pilot(pilot: dict, dry_run: bool) -> None:
    agent_id = pilot["agent_id"]
    started = parse_ts(pilot["pilot_started_at"])
    ends = parse_ts(pilot["pilot_ends_at"])
    now = now_utc()
    days_elapsed = (now - started).days
    days_until_expiry = (ends - now).days

    print(f"[{agent_id}] {pilot['company_name']} — day {days_elapsed}, expires in {days_until_expiry}")

    # Day 3/7/12 engagement emails
    for day, key in [(3, "pilot_day_3"), (7, "pilot_day_7"), (12, "pilot_day_12")]:
        if days_elapsed >= day and not already_sent(agent_id, key):
            if dry_run:
                print(f"  WOULD send {key}")
            else:
                msg_id = send_brevo_email(key, pilot["client_email"], merge_data={
                    "company_name": pilot["company_name"],
                    "minutes_used": pilot.get("pilot_minutes_used", 0),
                    "days_elapsed": days_elapsed,
                    "days_left": days_until_expiry
                })
                log_send(agent_id, key, msg_id)
                emit_marketing_event(f"{key}_sent", agent_id, {"day": day})
                print(f"  sent {key}")

    # Day 14 — convert or expire
    if days_until_expiry <= 0 and pilot["status"] == "pilot":
        if pilot.get("payment_method_added_at"):
            if dry_run:
                print(f"  WOULD convert to paid")
            else:
                convert_pilot_to_paid(pilot)
                print(f"  CONVERTED to paid")
        else:
            if dry_run:
                print(f"  WOULD expire (no card)")
            else:
                expire_pilot(pilot)
                print(f"  EXPIRED (no card)")

    # Day 16/30 — winback sequences for expired pilots
    if pilot["status"] == "expired":
        expired_at = ends  # pilot_ends_at == expiration moment
        days_since_expiry = (now - expired_at).days
        for day, key in [(2, "pilot_winback_day_16"), (16, "pilot_winback_day_30")]:
            # Note: day_16 is "2 days after expiry", day_30 is "16 days after expiry"
            if days_since_expiry >= day and not already_sent(agent_id, key):
                if dry_run:
                    print(f"  WOULD send {key}")
                else:
                    msg_id = send_brevo_email(key, pilot["client_email"], merge_data={
                        "company_name": pilot["company_name"]
                    })
                    log_send(agent_id, key, msg_id)
                    emit_marketing_event(f"{key}_sent", agent_id, {})
                    print(f"  sent {key}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without sending")
    args = parser.parse_args()

    pilots = fetch_active_pilots()
    print(f"Found {len(pilots)} active/expired pilots to evaluate.")

    for pilot in pilots:
        try:
            process_pilot(pilot, args.dry_run)
        except Exception as e:
            print(f"ERROR processing {pilot.get('agent_id')}: {e}", file=sys.stderr)
            # Continue processing other pilots

    print("Done.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the test scaffolding**

Create `tools/test_pilot_lifecycle.py`:

```python
#!/usr/bin/env python3
"""Unit tests for pilot_lifecycle.py pure logic.
Run with: python tools/test_pilot_lifecycle.py
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Stub env vars before import
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
os.environ.setdefault("BREVO_API_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "test-key")
os.environ.setdefault("RETELL_API_KEY", "test-key")

sys.path.insert(0, os.path.dirname(__file__))
from pilot_lifecycle import parse_ts, now_utc, process_pilot

PASSED = 0
FAILED = 0

def test(name):
    def deco(fn):
        global PASSED, FAILED
        try:
            fn()
            print(f"  ✓ {name}")
            PASSED += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            FAILED += 1
    return deco

# Tests added in tasks 20-23

if __name__ == "__main__":
    print("Running pilot_lifecycle tests...")
    print()
    print(f"\n{PASSED} passed, {FAILED} failed")
    sys.exit(0 if FAILED == 0 else 1)
```

- [ ] **Step 3: Run skeleton syntax check**

```bash
python -c "import tools.pilot_lifecycle" 2>&1 || python tools/pilot_lifecycle.py --dry-run 2>&1 | head -5
```

Expected: no syntax error. (It will fail at runtime because `fetch_active_pilots` needs network, but syntax should be clean.)

- [ ] **Step 4: Commit skeleton**

```bash
git add tools/pilot_lifecycle.py tools/test_pilot_lifecycle.py
git commit -m "feat(phase0): pilot_lifecycle.py skeleton + state machine + test scaffolding"
```

---

**Remaining tasks from Day 3 through Day 7 continue in a follow-up plan iteration.**

Tasks 20–23 (Day 3): Brevo email send, Stripe Setup Intent / webhook, convert_pilot_to_paid, expire_pilot + Retell pause, unit tests per branch.

Tasks 24–29 (Day 4): Retell `pilot_expired` flow node in TESTING, E2E call test both variable states, `retell-iac/scripts/promote.py` run, MASTER verification, Dan films intro/outro.

Tasks 30–37 (Day 5): Record 4-5 real TESTING-agent calls, select best clip, Remotion quote cards, waveform, onboarding screen-recording, offer slide stack, Descript audio cleanup, final DaVinci/CapCut assembly, Mux upload, register VSL in `marketing_assets`.

Tasks 38–46 (Day 6): Clone `syntharra-website` as sibling, write `start.html`, `marketing-tracker.js`, deploy Supabase Edge Function `marketing-event-ingest` with bot filter + rate limit, wire Mux player with autoplay muted + no-skip-first-60s, finalize landing-page copy (H1, subhead, bullets, FAQ, P.S. from spec § 5.2), `/ai` 301 redirect, full compressed-time E2E convert + expire runs, verify all events land in `marketing_events`.

Tasks 47–52 (Day 7): Walk through every item in spec § 10.3 pre-live checklist (53 items), verify Stripe LIVE mode active, drive 50–100 real visits from Dan's network, 72-hour wait, measure against § 10.2 benchmarks, decision gate: green-light Phase 1 or iterate.

Each task above will be expanded with the same bite-sized-steps / exact-code / exact-commands / TDD-where-applicable / commit-at-end structure as Tasks 1–19. Total final plan target: ~3,000 lines covering all 52 tasks with full reproducible detail.

---

## Self-Review Checklist (runs after all tasks are written — PENDING)

- [ ] Every spec section in `2026-04-10-phase-0-vsl-funnel-design.md` has at least one task
- [ ] Every placeholder scan (TBD / TODO / "implement later") returns zero hits
- [ ] Every task has explicit file paths, exact code, exact verification commands, and a commit step
- [ ] Type and function names used in later tasks match their definitions in earlier tasks (e.g. `send_brevo_email`, `convert_pilot_to_paid`, `expire_pilot` all match the stubs in Task 19)
- [ ] Every spec § 10.3 checklist item maps to a verification step inside a task
- [ ] No task depends on a step that has not been done in an earlier task
- [ ] Rollback procedure (Task 11) is referenced from every destructive step
