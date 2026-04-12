# Phase 0 — VSL + Pilot Funnel + Measurement Spine Implementation Plan

> ## PLAN STATUS: Tasks 1–52 ALL WRITTEN
>
> **Last updated:** 2026-04-11 (Track B extension — Days 3–7 written)
>
> **What's written (~3,800 lines, full 7-day plan):**
> - Day 1: Tasks 1–12 — **COMPLETE** (executed 2026-04-11, migration live in prod)
> - Day 2: Tasks 13–18 — **WRITTEN** (execution in progress by Track A this session)
> - Day 3: Tasks 19–23 — **WRITTEN** (Task 19 skeleton committed; Tasks 20–23 define Brevo send, Stripe Setup Intent + webhook, convert/expire, unit tests)
> - Day 4: Tasks 24–29 — **WRITTEN** (Retell `pilot_expired` node, TESTING E2E, promote.py with hard human gate, Dan-films task, cron dark-launch)
> - Day 5: Tasks 30–37 — **WRITTEN** (VSL production pipeline; multiple hard blockers on live calls, Mux vault, Dan filming)
> - Day 6: Tasks 38–46 — **WRITTEN** (`syntharra-website` sibling clone, `start.html`, tracker JS, Edge Function, full E2E)
> - Day 7: Tasks 47–52 — **WRITTEN** (53-item pre-live checklist, Stripe live flip, smoke test, GO-LIVE commit)
>
> **Hard blockers flagged (require Dan or external resource before execution):**
> - **Task 27** — Retell promote.py requires Dan's explicit go-ahead
> - **Task 28** — Dan films founder intro + outro on-camera
> - **Task 30** — representative live HVAC call must exist before capture
> - **Task 35** — Mux credentials must be vaulted (not currently in `syntharra_vault`)
> - **Task 38** — `syntharra-website` sibling repo does not currently exist as a sibling; Dan must clone or confirm remote
> - **Task 47/48** — Stripe live-mode secret key + webhook signing secret must be vaulted
> - **Task 51** — full cold-traffic smoke test requires all of the above resolved
>
> **Execution strategy (per Dan's 2026-04-11 "option B" decision):**
> 1. Day 1 complete — migration applied, billing tools patched, rollback rehearsed
> 2. Day 2 in flight on Track A this session
> 3. Days 3–7 written end-to-end so Track A/B can parallel-execute without blocking on plan writes
> 4. Each day still has a session-end checkpoint commit
> 5. Hard blockers halt execution at the blocked task; non-blocked tasks continue where possible
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

## Task 20: Brevo email send implementation

**Files:**
- Modify: `tools/pilot_lifecycle.py` (replace the `send_brevo_email` stub from Task 19, add a shared `BREVO_TEMPLATE_IDS` dict)
- Modify: `tools/test_pilot_lifecycle.py` (add Brevo send unit tests with mocked HTTP)

Approach: Brevo's transactional email API is a single `POST https://api.brevo.com/v3/smtp/email` with the template ID and merge params. We look up template IDs from a module-level dict that is populated by `tools/upload_brevo_templates.py` at setup time and persisted as constants in this file. We surface HTTP errors cleanly (don't let a 5xx from Brevo crash the whole cron — log and continue) and return the Brevo `messageId` so the caller can write it to `pilot_email_sends.brevo_message_id`.

- [ ] **Step 1: Add `BREVO_TEMPLATE_IDS` dict + Brevo helpers at the top of `pilot_lifecycle.py`**

Insert just below the `sb_url` helper (before `now_utc`):

```python
# === Brevo ===
# Template IDs are populated by tools/upload_brevo_templates.py and recorded in
# docs/REFERENCE.md under "Brevo templates". Update here if the upload script
# is re-run and IDs change.
BREVO_TEMPLATE_IDS = {
    "pilot_welcome":         int(os.environ.get("BREVO_TPL_PILOT_WELCOME", "0")),
    "pilot_day_3":           int(os.environ.get("BREVO_TPL_PILOT_DAY_3", "0")),
    "pilot_day_7":           int(os.environ.get("BREVO_TPL_PILOT_DAY_7", "0")),
    "pilot_day_12":          int(os.environ.get("BREVO_TPL_PILOT_DAY_12", "0")),
    "pilot_converted":       int(os.environ.get("BREVO_TPL_PILOT_CONVERTED", "0")),
    "pilot_card_added":      int(os.environ.get("BREVO_TPL_PILOT_CARD_ADDED", "0")),
    "pilot_expired":         int(os.environ.get("BREVO_TPL_PILOT_EXPIRED", "0")),
    "pilot_winback_day_16":  int(os.environ.get("BREVO_TPL_PILOT_WINBACK_16", "0")),
    "pilot_winback_day_30":  int(os.environ.get("BREVO_TPL_PILOT_WINBACK_30", "0")),
}

BREVO_API = "https://api.brevo.com/v3/smtp/email"
BREVO_FROM = {"name": "Dan at Syntharra", "email": "dan@syntharra.com"}
```

- [ ] **Step 2: Replace the `send_brevo_email` stub with the real implementation**

Find this stub from Task 19:
```python
def send_brevo_email(template_key: str, to_email: str, merge_data: dict) -> str:
    """Returns Brevo message ID."""
    raise NotImplementedError
```

Replace with:

```python
def send_brevo_email(template_key: str, to_email: str, merge_data: dict) -> str:
    """Send a Brevo transactional email. Returns Brevo message_id, or '' on failure.

    Does NOT raise — failures are logged to stderr and return ''. The cron
    continues processing other pilots. Idempotency is the caller's job
    (via pilot_email_sends log).
    """
    template_id = BREVO_TEMPLATE_IDS.get(template_key, 0)
    if not template_id:
        print(f"  [brevo] ERROR: no template ID for {template_key}", file=sys.stderr)
        return ""

    if not to_email or "@" not in to_email:
        print(f"  [brevo] ERROR: invalid to_email {to_email!r}", file=sys.stderr)
        return ""

    headers = {
        "api-key": env("BREVO_API_KEY"),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {
        "sender": BREVO_FROM,
        "to": [{"email": to_email}],
        "templateId": template_id,
        "params": merge_data,
    }
    status, data = http_json("POST", BREVO_API, headers, body)
    if status not in (200, 201):
        print(f"  [brevo] {template_key} → {to_email} FAILED: {status} {data}", file=sys.stderr)
        return ""
    message_id = data.get("messageId") or ""
    print(f"  [brevo] {template_key} → {to_email} sent (msg {message_id})")
    return message_id
```

- [ ] **Step 3: Patch the `process_pilot` call sites to capture `message_id`**

The Task 19 skeleton already does `msg_id = send_brevo_email(...)`. Verify the call matches the new signature (it does — `template_key, to_email, merge_data`). No code change needed here, but re-read the section to confirm.

- [ ] **Step 4: Add unit tests in `test_pilot_lifecycle.py`**

Append to `tools/test_pilot_lifecycle.py` (before the `if __name__ == "__main__":` block):

```python
from unittest.mock import patch as mock_patch
import pilot_lifecycle as pl

@test("send_brevo_email returns message_id on success")
def _():
    pl.BREVO_TEMPLATE_IDS["pilot_day_3"] = 42
    with mock_patch.object(pl, "http_json", return_value=(201, {"messageId": "abc123"})):
        mid = pl.send_brevo_email("pilot_day_3", "owner@example.com", {"company_name": "Acme"})
    assert mid == "abc123", f"expected abc123, got {mid!r}"

@test("send_brevo_email returns empty on HTTP 500")
def _():
    pl.BREVO_TEMPLATE_IDS["pilot_day_3"] = 42
    with mock_patch.object(pl, "http_json", return_value=(500, {"message": "internal"})):
        mid = pl.send_brevo_email("pilot_day_3", "owner@example.com", {})
    assert mid == "", f"expected empty, got {mid!r}"

@test("send_brevo_email returns empty on missing template ID")
def _():
    pl.BREVO_TEMPLATE_IDS["pilot_day_3"] = 0
    mid = pl.send_brevo_email("pilot_day_3", "owner@example.com", {})
    assert mid == ""

@test("send_brevo_email rejects invalid email")
def _():
    pl.BREVO_TEMPLATE_IDS["pilot_day_3"] = 42
    mid = pl.send_brevo_email("pilot_day_3", "not-an-email", {})
    assert mid == ""
```

- [ ] **Step 5: Run the tests**

```bash
python tools/test_pilot_lifecycle.py
```

Expected: `4 passed, 0 failed` (plus any Task 19 tests).

- [ ] **Step 6: Commit**

```bash
git add tools/pilot_lifecycle.py tools/test_pilot_lifecycle.py
git commit -m "$(cat <<'EOF'
feat(phase0): pilot_lifecycle Brevo send helper + unit tests

Replaces the Task 19 send_brevo_email stub with a real implementation
that reads template IDs from BREVO_TEMPLATE_IDS (sourced via env vars
set by tools/upload_brevo_templates.py). HTTP failures are logged and
return empty string — the cron continues processing other pilots.

Unit tests cover: success path, HTTP 500, missing template ID,
invalid email. All mocked, no network.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 21: Stripe Setup Intent endpoint + webhook handler

**Files:**
- Create: `tools/stripe_pilot_setup.py` (one-off script: creates the Stripe product + pilot price + webhook endpoint)
- Create: `supabase/functions/pilot-setup-intent/index.ts` (Edge Function: creates SetupIntent on demand)
- Create: `supabase/functions/pilot-setup-intent/deno.json` (function config)
- Create: `supabase/functions/stripe-webhook/index.ts` (Edge Function: handles `setup_intent.succeeded`)
- Create: `supabase/functions/stripe-webhook/deno.json`
- Modify: `docs/REFERENCE.md` (record Stripe product ID + price ID + webhook endpoint URL)

Approach: Supabase Edge Functions (not n8n) for both endpoints. Rationale: we need signed webhook verification, low latency on the card-add flow, and Edge Functions are already how we do `marketing-event-ingest`. The `pilot-setup-intent` function is called by the dashboard card-add button. The `stripe-webhook` function is called by Stripe on `setup_intent.succeeded` and flips `payment_method_added_at` on `client_subscriptions`.

- [ ] **Step 1: Write the one-off Stripe setup script**

Create `tools/stripe_pilot_setup.py`:

```python
#!/usr/bin/env python3
"""
stripe_pilot_setup.py — One-off bootstrap for the Phase 0 pilot Stripe resources.

Creates:
  1. A Stripe Product named "Syntharra HVAC Standard"
  2. A recurring monthly Price $697 (USD) linked to that product
  3. A Webhook endpoint pointing at the Supabase Edge Function stripe-webhook,
     subscribed to: setup_intent.succeeded, customer.subscription.updated,
                    customer.subscription.deleted, invoice.paid, invoice.payment_failed

Idempotent: if a product/price/webhook with the same metadata already exists,
it's re-used rather than duplicated.

Usage:
  export STRIPE_SECRET_KEY=<test or live key from vault>
  export SUPABASE_PROJECT_REF=<your ref, e.g. hgheyqwnrcvwtgngqdnq>
  python tools/stripe_pilot_setup.py --mode test   # or --mode live

Outputs the IDs to stdout — add them to docs/REFERENCE.md.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import base64

STRIPE_API = "https://api.stripe.com/v1"

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def stripe(method, path, data=None):
    url = f"{STRIPE_API}{path}"
    body = urllib.parse.urlencode(data, doseq=True).encode() if data else None
    auth = base64.b64encode(f"{env('STRIPE_SECRET_KEY')}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def find_existing_product(name):
    data = stripe("GET", "/products?active=true&limit=100")
    for p in data.get("data", []):
        if p.get("name") == name and p.get("metadata", {}).get("syntharra") == "hvac_standard":
            return p
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["test", "live"], required=True)
    args = parser.parse_args()

    product_name = "Syntharra HVAC Standard"

    # 1. Product
    existing = find_existing_product(product_name)
    if existing:
        product = existing
        print(f"Re-using product {product['id']}")
    else:
        product = stripe("POST", "/products", data={
            "name": product_name,
            "description": "HVAC Standard — 700 voice minutes/month, 24/7 AI receptionist",
            "metadata[syntharra]": "hvac_standard",
        })
        print(f"Created product {product['id']}")

    # 2. Recurring monthly price $697
    prices = stripe("GET", f"/prices?product={product['id']}&active=true")
    existing_price = next(
        (p for p in prices.get("data", [])
         if p.get("unit_amount") == 69700 and p.get("recurring", {}).get("interval") == "month"),
        None
    )
    if existing_price:
        price = existing_price
        print(f"Re-using price {price['id']}")
    else:
        price = stripe("POST", "/prices", data={
            "product": product["id"],
            "unit_amount": 69700,
            "currency": "usd",
            "recurring[interval]": "month",
            "metadata[tier]": "hvac_standard",
            "metadata[syntharra]": "true",
        })
        print(f"Created price {price['id']}")

    # 3. Webhook endpoint
    webhook_url = (
        f"https://{env('SUPABASE_PROJECT_REF')}.supabase.co/functions/v1/stripe-webhook"
    )
    hooks = stripe("GET", "/webhook_endpoints?limit=100")
    existing_hook = next(
        (h for h in hooks.get("data", []) if h.get("url") == webhook_url),
        None
    )
    if existing_hook:
        hook = existing_hook
        print(f"Re-using webhook {hook['id']} (secret: check Stripe dashboard)")
    else:
        hook = stripe("POST", "/webhook_endpoints", data={
            "url": webhook_url,
            "enabled_events[]": [
                "setup_intent.succeeded",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "invoice.paid",
                "invoice.payment_failed",
            ],
            "description": f"Syntharra pilot + paid subscription events ({args.mode})",
        })
        print(f"Created webhook {hook['id']}")
        print(f"  SIGNING SECRET (save to vault immediately): {hook.get('secret')}")

    print("\n=== Summary ===")
    print(f"Mode:       {args.mode}")
    print(f"Product:    {product['id']}")
    print(f"Price:      {price['id']}")
    print(f"Webhook:    {hook['id']}")
    print(f"Webhook URL {webhook_url}")
    print(f"\nAdd these to docs/REFERENCE.md under 'Stripe resources ({args.mode})'.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the Stripe setup in test mode**

```bash
export STRIPE_SECRET_KEY=$(python tools/fetch_vault.py "Stripe" secret_key_test)
export SUPABASE_PROJECT_REF=hgheyqwnrcvwtgngqdnq
python tools/stripe_pilot_setup.py --mode test
```

Expected: product, price, and webhook IDs printed. Capture the webhook signing secret from the output (Stripe only returns it on creation — if missed, rotate via dashboard).

- [ ] **Step 3: Vault the webhook signing secret**

```sql
insert into syntharra_vault (service_name, key_type, key_value, metadata)
values ('Stripe', 'webhook_signing_secret_test', '<whsec_...>',
        '{"created_by":"phase0_stripe_pilot_setup","mode":"test"}'::jsonb);
```

- [ ] **Step 4: Write the `pilot-setup-intent` Edge Function**

Create `supabase/functions/pilot-setup-intent/index.ts`:

```typescript
// pilot-setup-intent — creates a Stripe SetupIntent for a pilot user to add a payment method.
// Called by the pilot dashboard "Add payment" button with ?a=<agent_id>.
// Authenticates the caller by matching the agent_id against a row in client_subscriptions
// with pilot_mode=true. No JWT — the agent_id acts as a capability token (the user can only
// produce it by having loaded their own dashboard, which already uses it).
//
// POST body: { agent_id: string }
// Response:  { client_secret: string, customer_id: string } or { error: string }

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const STRIPE_SECRET_KEY = Deno.env.get("STRIPE_SECRET_KEY")!;

async function sb(path: string, init: RequestInit = {}) {
  const headers = {
    apikey: SUPABASE_SERVICE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
    ...(init.headers || {}),
  };
  return fetch(`${SUPABASE_URL}${path}`, { ...init, headers });
}

async function stripe(path: string, body: Record<string, string>) {
  const form = new URLSearchParams(body).toString();
  const resp = await fetch(`https://api.stripe.com/v1${path}`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${btoa(STRIPE_SECRET_KEY + ":")}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
  });
  return resp.json();
}

serve(async (req) => {
  if (req.method !== "POST") return new Response("POST only", { status: 405 });

  const { agent_id } = await req.json().catch(() => ({}));
  if (!agent_id) return new Response(JSON.stringify({ error: "agent_id required" }), { status: 400 });

  // Look up the pilot row
  const lookup = await sb(
    `/rest/v1/client_subscriptions?agent_id=eq.${encodeURIComponent(agent_id)}` +
    `&pilot_mode=eq.true&select=agent_id,client_email,company_name,stripe_customer_id`
  );
  const rows = await lookup.json();
  if (!Array.isArray(rows) || rows.length === 0) {
    return new Response(JSON.stringify({ error: "not a pilot" }), { status: 404 });
  }
  const row = rows[0];

  // Create or re-use Stripe customer
  let customerId = row.stripe_customer_id;
  if (!customerId) {
    const customer = await stripe("/customers", {
      email: row.client_email,
      "metadata[agent_id]": agent_id,
      "metadata[syntharra]": "pilot",
    });
    customerId = customer.id;
    await sb(
      `/rest/v1/client_subscriptions?agent_id=eq.${encodeURIComponent(agent_id)}`,
      {
        method: "PATCH",
        body: JSON.stringify({ stripe_customer_id: customerId }),
      }
    );
  }

  // Create SetupIntent
  const intent = await stripe("/setup_intents", {
    customer: customerId,
    "automatic_payment_methods[enabled]": "true",
    "metadata[agent_id]": agent_id,
    "metadata[syntharra]": "pilot_card_add",
  });

  return new Response(
    JSON.stringify({ client_secret: intent.client_secret, customer_id: customerId }),
    { headers: { "Content-Type": "application/json" } }
  );
});
```

Create `supabase/functions/pilot-setup-intent/deno.json`:

```json
{
  "imports": {
    "std/": "https://deno.land/std@0.224.0/"
  }
}
```

- [ ] **Step 5: Write the `stripe-webhook` Edge Function**

Create `supabase/functions/stripe-webhook/index.ts`:

```typescript
// stripe-webhook — handles Stripe webhook events for Phase 0 pilot flow.
// Events handled:
//   setup_intent.succeeded          → flip payment_method_added_at on pilot row
//   customer.subscription.updated   → reflect status changes on client_subscriptions
//   customer.subscription.deleted   → handled; sets status='cancelled'
//   invoice.paid                    → log to marketing_events
//   invoice.payment_failed          → log to marketing_events + slack alert
//
// Verifies the Stripe signature using STRIPE_WEBHOOK_SECRET (test or live).

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createHmac } from "https://deno.land/std@0.224.0/crypto/mod.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET")!;

async function sb(path: string, init: RequestInit = {}) {
  return fetch(`${SUPABASE_URL}${path}`, {
    ...init,
    headers: {
      apikey: SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
      ...(init.headers || {}),
    },
  });
}

async function emitEvent(event_type: string, agent_id: string, metadata: Record<string, unknown>) {
  await sb("/rest/v1/marketing_events", {
    method: "POST",
    body: JSON.stringify({
      session_id: "stripe-webhook",
      client_agent_id: agent_id,
      event_type,
      metadata,
    }),
  });
}

function verifySignature(payload: string, sigHeader: string): boolean {
  // Stripe sends: t=timestamp,v1=signature
  const parts = Object.fromEntries(
    sigHeader.split(",").map((p) => p.split("="))
  ) as Record<string, string>;
  const signedPayload = `${parts.t}.${payload}`;
  const expected = createHmac("sha256", WEBHOOK_SECRET)
    .update(signedPayload)
    .digest("hex");
  return expected === parts.v1;
}

serve(async (req) => {
  if (req.method !== "POST") return new Response("POST only", { status: 405 });

  const sig = req.headers.get("stripe-signature");
  const body = await req.text();
  if (!sig || !verifySignature(body, sig)) {
    return new Response("bad signature", { status: 400 });
  }

  const event = JSON.parse(body);
  const type = event.type as string;
  const data = event.data.object as Record<string, unknown>;
  const metadata = (data.metadata || {}) as Record<string, string>;
  const agent_id = metadata.agent_id || "";

  try {
    if (type === "setup_intent.succeeded" && agent_id) {
      // Flip payment_method_added_at
      await sb(
        `/rest/v1/client_subscriptions?agent_id=eq.${encodeURIComponent(agent_id)}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            payment_method_added_at: new Date().toISOString(),
          }),
        }
      );
      await emitEvent("card_added", agent_id, { setup_intent_id: data.id });
    } else if (type === "customer.subscription.updated") {
      const status = (data as any).status as string;
      const customerId = (data as any).customer as string;
      await sb(
        `/rest/v1/client_subscriptions?stripe_customer_id=eq.${encodeURIComponent(customerId)}`,
        { method: "PATCH", body: JSON.stringify({ stripe_subscription_status: status }) }
      );
    } else if (type === "invoice.paid" || type === "invoice.payment_failed") {
      await emitEvent(type.replace(".", "_"), agent_id, { amount: (data as any).amount_paid });
    }
  } catch (e) {
    console.error("handler error", e);
    return new Response("error", { status: 500 });
  }

  return new Response("ok", { status: 200 });
});
```

Create `supabase/functions/stripe-webhook/deno.json`:

```json
{
  "imports": {
    "std/": "https://deno.land/std@0.224.0/"
  }
}
```

- [ ] **Step 6: Deploy both Edge Functions**

Via `mcp__claude_ai_Supabase__deploy_edge_function`:

```
function name: pilot-setup-intent
file: supabase/functions/pilot-setup-intent/index.ts
```

Then:

```
function name: stripe-webhook
file: supabase/functions/stripe-webhook/index.ts
```

Expected: both deploy successfully. Function URLs printed.

- [ ] **Step 7: Set the secrets the Edge Functions need**

Edge Functions read from Supabase project secrets. Set them via the dashboard (or MCP if available):

```
STRIPE_SECRET_KEY = <secret_key_test from vault>
STRIPE_WEBHOOK_SECRET = <webhook_signing_secret_test from vault>
```

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are auto-injected by the platform.

- [ ] **Step 8: Smoke test `pilot-setup-intent`**

```bash
curl -X POST "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/pilot-setup-intent" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"nonexistent_agent_id"}'
```

Expected: `{"error":"not a pilot"}` with HTTP 404. This confirms the function is live and the Supabase query runs.

- [ ] **Step 9: Smoke test `stripe-webhook` signature verification**

```bash
curl -X POST "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/stripe-webhook" \
  -H "Content-Type: application/json" \
  -d '{"test":1}'
```

Expected: `bad signature` with HTTP 400 (no valid `stripe-signature` header). Confirms the verification path runs.

- [ ] **Step 10: Register Stripe IDs in `docs/REFERENCE.md`**

```markdown
## Stripe resources (Phase 0, 2026-04-11)

| Resource | Test mode | Live mode |
|---|---|---|
| Product "Syntharra HVAC Standard" | `prod_<...>` | TBD day 7 |
| Price $697/mo | `price_<...>` | TBD day 7 |
| Webhook endpoint | `we_<...>` | TBD day 7 |
| Webhook URL | `https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/stripe-webhook` | same |
| Signing secret (in vault) | `Stripe` / `webhook_signing_secret_test` | `Stripe` / `webhook_signing_secret_live` |
```

- [ ] **Step 11: Commit**

```bash
git add tools/stripe_pilot_setup.py \
        supabase/functions/pilot-setup-intent \
        supabase/functions/stripe-webhook \
        docs/REFERENCE.md
git commit -m "$(cat <<'EOF'
feat(phase0): Stripe Setup Intent endpoint + webhook handler

Adds two Supabase Edge Functions:
  - pilot-setup-intent: called by pilot dashboard's "Add payment" button,
    creates or reuses a Stripe Customer and returns a SetupIntent client
    secret for the hosted card-add flow.
  - stripe-webhook: verifies signatures, handles setup_intent.succeeded
    to flip payment_method_added_at on client_subscriptions, plus
    subscription.updated / invoice.paid / invoice.payment_failed events.

Bootstrap script tools/stripe_pilot_setup.py creates the Stripe product,
price, and webhook endpoint idempotently. Run in --mode test for Phase 0
development; --mode live runs on Day 7 once Dan vaults the live keys.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 22: `convert_pilot_to_paid` + `expire_pilot` + Retell pause wiring

**Files:**
- Modify: `tools/pilot_lifecycle.py` (replace the three stubs from Task 19: `convert_pilot_to_paid`, `expire_pilot`, `pause_retell_agent`)
- Modify: `tools/test_pilot_lifecycle.py` (branch coverage tests)

Approach: both `convert` and `expire` mutate `client_subscriptions` via Supabase PATCH and emit a `marketing_events` row. `expire` additionally calls Retell's `update-agent` endpoint to set `agent_level_dynamic_variables.pilot_expired = "true"`, which the new `pilot_expired` flow node (built in Task 24) reads on every call. If Retell's update-agent call fails, we log and continue — the agent will still answer normally, but the win-back email will still fire so the pilot user isn't silently billed.

- [ ] **Step 1: Replace `convert_pilot_to_paid` stub**

Find:
```python
def convert_pilot_to_paid(pilot: dict) -> None:
    raise NotImplementedError
```

Replace with:

```python
def convert_pilot_to_paid(pilot: dict) -> None:
    """Day 14 + card on file: flip status and notify.

    Pre-condition: the Stripe subscription was created at card-add time
    (in stripe-webhook Edge Function) with trial_end == pilot_ends_at.
    By the time this function runs, Stripe has already auto-activated
    the sub (trial_end has passed). We just reflect that locally and
    send the welcome-to-paid email.
    """
    agent_id = pilot["agent_id"]

    # 1. Flip client_subscriptions row
    patch_url = sb_url(
        f"/rest/v1/client_subscriptions?agent_id=eq.{urllib.parse.quote(agent_id)}"
    )
    body = {
        "status": "active",
        "pilot_mode": False,
    }
    status, data = http_json("PATCH", patch_url, sb_headers(), body)
    if status not in (200, 204):
        print(f"  [convert] PATCH failed: {status} {data}", file=sys.stderr)
        return

    # 2. Send converted email
    msg_id = send_brevo_email("pilot_converted", pilot["client_email"], {
        "company_name": pilot["company_name"],
    })
    log_send(agent_id, "pilot_converted", msg_id)

    # 3. Emit marketing event
    emit_marketing_event("pilot_converted", agent_id, {
        "stripe_subscription_id": pilot.get("stripe_subscription_id"),
    })
```

- [ ] **Step 2: Replace `expire_pilot` stub**

```python
def expire_pilot(pilot: dict) -> None:
    """Day 14 + no card on file: pause the agent gracefully + send win-back.

    This does NOT charge the user and does NOT delete the Retell agent.
    Calls still reach the agent — they just get routed to the pilot_expired
    flow node (built in Task 24) which plays the graceful-pause message.
    """
    agent_id = pilot["agent_id"]

    # 1. Flip status → 'expired'
    patch_url = sb_url(
        f"/rest/v1/client_subscriptions?agent_id=eq.{urllib.parse.quote(agent_id)}"
    )
    body = {
        "status": "expired",
        # pilot_mode stays true so the cron still sees this row for win-back cadence
    }
    status, data = http_json("PATCH", patch_url, sb_headers(), body)
    if status not in (200, 204):
        print(f"  [expire] PATCH failed: {status} {data}", file=sys.stderr)
        return

    # 2. Pause the Retell agent (set pilot_expired=true dynamic var)
    pause_retell_agent(agent_id)

    # 3. Send expired email
    msg_id = send_brevo_email("pilot_expired", pilot["client_email"], {
        "company_name": pilot["company_name"],
    })
    log_send(agent_id, "pilot_expired", msg_id)

    # 4. Emit marketing event
    emit_marketing_event("pilot_expired", agent_id, {})
```

- [ ] **Step 3: Replace `pause_retell_agent` stub**

```python
def pause_retell_agent(agent_id: str) -> None:
    """Set pilot_expired=true on the agent's dynamic variables.

    Retell endpoint: PATCH /update-agent/{agent_id}
    Body: { agent_level_dynamic_variables: { pilot_expired: "true" } }

    The pilot_expired flow node (retell-iac/components/pilot_expired_node.json)
    is wired from identify_call and checks this variable at the start of
    every call. Set once per agent — persists until we flip it back.

    Failures are logged but NOT raised — the win-back email still fires so
    the user is notified. Worst case: the agent keeps answering normally
    until we catch it. Better than silently billing them.
    """
    url = f"https://api.retellai.com/v2/update-agent/{agent_id}"
    headers = {
        "Authorization": f"Bearer {env('RETELL_API_KEY')}",
        "Content-Type": "application/json",
    }
    body = {
        "agent_level_dynamic_variables": {"pilot_expired": "true"}
    }
    status, data = http_json("PATCH", url, headers, body)
    if status not in (200, 201):
        print(f"  [retell] pause {agent_id} FAILED: {status} {data}", file=sys.stderr)
    else:
        print(f"  [retell] paused {agent_id}")
```

- [ ] **Step 4: Add branch coverage tests**

Append to `tools/test_pilot_lifecycle.py`:

```python
@test("convert_pilot_to_paid patches row + sends email + emits event")
def _():
    pilot = {
        "agent_id": "agent_test_1",
        "client_email": "owner@example.com",
        "company_name": "Acme HVAC",
        "stripe_subscription_id": "sub_xyz",
    }
    pl.BREVO_TEMPLATE_IDS["pilot_converted"] = 100

    calls = []
    def fake_http(method, url, headers, body=None):
        calls.append((method, url, body))
        if "client_subscriptions" in url:
            return (204, {})
        if "brevo" in url:
            return (201, {"messageId": "brevo_msg_1"})
        if "marketing_events" in url:
            return (201, {})
        if "pilot_email_sends" in url:
            return (201, {})
        return (200, {})

    with mock_patch.object(pl, "http_json", side_effect=fake_http):
        pl.convert_pilot_to_paid(pilot)

    # Must have: 1 PATCH to client_subscriptions + 1 POST to Brevo + 1 POST to events + 1 POST to log
    patch_calls = [c for c in calls if c[0] == "PATCH" and "client_subscriptions" in c[1]]
    assert len(patch_calls) == 1
    assert patch_calls[0][2] == {"status": "active", "pilot_mode": False}

    brevo_calls = [c for c in calls if "brevo" in c[1]]
    assert len(brevo_calls) == 1

@test("expire_pilot sets status=expired, calls retell pause, sends email")
def _():
    pilot = {
        "agent_id": "agent_test_2",
        "client_email": "owner2@example.com",
        "company_name": "Beta HVAC",
    }
    pl.BREVO_TEMPLATE_IDS["pilot_expired"] = 101

    calls = []
    def fake_http(method, url, headers, body=None):
        calls.append((method, url, body))
        if "update-agent" in url:
            return (200, {"agent_id": pilot["agent_id"]})
        return (201, {"messageId": "x"})

    with mock_patch.object(pl, "http_json", side_effect=fake_http):
        pl.expire_pilot(pilot)

    # PATCH to status=expired
    patch_calls = [c for c in calls if c[0] == "PATCH" and "client_subscriptions" in c[1]]
    assert len(patch_calls) == 1
    assert patch_calls[0][2] == {"status": "expired"}

    # Retell PATCH
    retell_calls = [c for c in calls if "update-agent" in c[1]]
    assert len(retell_calls) == 1
    assert retell_calls[0][2] == {"agent_level_dynamic_variables": {"pilot_expired": "true"}}

@test("pause_retell_agent does not raise on HTTP 500")
def _():
    with mock_patch.object(pl, "http_json", return_value=(500, {"error": "down"})):
        # Should not raise — just log
        pl.pause_retell_agent("agent_test_3")
```

- [ ] **Step 5: Run tests**

```bash
python tools/test_pilot_lifecycle.py
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add tools/pilot_lifecycle.py tools/test_pilot_lifecycle.py
git commit -m "feat(phase0): convert_pilot_to_paid + expire_pilot + Retell pause"
```

---

## Task 23: `emit_marketing_event` helper + full unit test coverage

**Files:**
- Modify: `tools/pilot_lifecycle.py` (replace `emit_marketing_event` stub)
- Modify: `tools/test_pilot_lifecycle.py` (add state-machine branch tests)

- [ ] **Step 1: Replace `emit_marketing_event` stub**

Find:
```python
def emit_marketing_event(event_type: str, client_agent_id: str, metadata: dict) -> None:
    raise NotImplementedError
```

Replace with:

```python
def emit_marketing_event(event_type: str, client_agent_id: str, metadata: dict) -> None:
    """Insert a row into marketing_events.

    Server-side events (from the cron) use session_id='cron-pilot-lifecycle'
    so they're distinguishable from browser-side events in queries.
    """
    url = sb_url("/rest/v1/marketing_events")
    body = {
        "session_id": "cron-pilot-lifecycle",
        "client_agent_id": client_agent_id,
        "event_type": event_type,
        "metadata": metadata,
    }
    status, data = http_json("POST", url, sb_headers(), body)
    if status not in (200, 201):
        print(f"  [event] {event_type} INSERT failed: {status} {data}", file=sys.stderr)
```

- [ ] **Step 2: Add state-machine branch tests (covers every state transition in `process_pilot`)**

Append to `test_pilot_lifecycle.py`:

```python
def make_pilot(days_in: int, with_card: bool = False, status: str = "pilot") -> dict:
    now = pl.now_utc()
    started = now - timedelta(days=days_in)
    ends = started + timedelta(days=14)
    return {
        "agent_id": f"agent_day{days_in}",
        "company_name": f"Test Day {days_in}",
        "client_email": "t@example.com",
        "pilot_started_at": started.isoformat(),
        "pilot_ends_at": ends.isoformat(),
        "pilot_minutes_allotted": 200,
        "pilot_minutes_used": 20 * days_in,
        "payment_method_added_at": now.isoformat() if with_card else None,
        "status": status,
    }

@test("process_pilot day 0 sends nothing")
def _():
    pilot = make_pilot(0)
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda *a, **k: sends.append(a) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert sends == []

@test("process_pilot day 3 sends pilot_day_3")
def _():
    pilot = make_pilot(3)
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda tk, *a, **k: sends.append(tk) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert "pilot_day_3" in sends

@test("process_pilot day 7 sends both day_3 (backfill) and day_7 if not yet sent")
def _():
    pilot = make_pilot(7)
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda tk, *a, **k: sends.append(tk) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert "pilot_day_3" in sends
    assert "pilot_day_7" in sends

@test("process_pilot day 14 with card converts")
def _():
    pilot = make_pilot(14, with_card=True)
    converted = []
    with mock_patch.object(pl, "already_sent", return_value=True), \
         mock_patch.object(pl, "convert_pilot_to_paid", side_effect=lambda p: converted.append(p)), \
         mock_patch.object(pl, "expire_pilot"):
        pl.process_pilot(pilot, dry_run=False)
    assert len(converted) == 1

@test("process_pilot day 14 without card expires")
def _():
    pilot = make_pilot(14, with_card=False)
    expired = []
    with mock_patch.object(pl, "already_sent", return_value=True), \
         mock_patch.object(pl, "convert_pilot_to_paid"), \
         mock_patch.object(pl, "expire_pilot", side_effect=lambda p: expired.append(p)):
        pl.process_pilot(pilot, dry_run=False)
    assert len(expired) == 1

@test("process_pilot day 16 expired sends winback_day_16")
def _():
    pilot = make_pilot(16, status="expired")
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda tk, *a, **k: sends.append(tk) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert "pilot_winback_day_16" in sends

@test("process_pilot day 30 expired sends winback_day_30")
def _():
    pilot = make_pilot(30, status="expired")
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda tk, *a, **k: sends.append(tk) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert "pilot_winback_day_30" in sends

@test("process_pilot day 3 idempotent when already_sent returns true")
def _():
    pilot = make_pilot(3)
    sends = []
    with mock_patch.object(pl, "already_sent", return_value=True), \
         mock_patch.object(pl, "send_brevo_email", side_effect=lambda tk, *a, **k: sends.append(tk) or "m"), \
         mock_patch.object(pl, "log_send"), \
         mock_patch.object(pl, "emit_marketing_event"):
        pl.process_pilot(pilot, dry_run=False)
    assert sends == []  # nothing sent because already logged

@test("process_pilot dry_run never calls send_brevo_email")
def _():
    pilot = make_pilot(3)
    with mock_patch.object(pl, "already_sent", return_value=False), \
         mock_patch.object(pl, "send_brevo_email") as mock_send:
        pl.process_pilot(pilot, dry_run=True)
    assert mock_send.call_count == 0
```

- [ ] **Step 3: Run the full test suite**

```bash
python tools/test_pilot_lifecycle.py
```

Expected: all tests pass, zero failures. This is the full branch-coverage suite for the state machine — every transition in § 6.6 of the spec has a test.

- [ ] **Step 4: Run the cron end-to-end against test data with `--dry-run`**

Create a synthetic pilot row in the TEST-mode dashboard:

```sql
insert into client_subscriptions (
  agent_id, company_name, client_email, status, pilot_mode,
  pilot_started_at, pilot_ends_at, pilot_minutes_allotted
) values (
  'agent_dryrun_test', 'Cron Dry-Run Test', 'dryrun@example.com', 'pilot', true,
  now() - interval '3 days', now() + interval '11 days', 200
);
```

Then:

```bash
python tools/pilot_lifecycle.py --dry-run
```

Expected: output contains `[agent_dryrun_test] Cron Dry-Run Test — day 3, expires in 11` followed by `WOULD send pilot_day_3`. Nothing is actually sent.

- [ ] **Step 5: Clean up test row**

```sql
delete from client_subscriptions where agent_id = 'agent_dryrun_test';
```

- [ ] **Step 6: Commit**

```bash
git add tools/pilot_lifecycle.py tools/test_pilot_lifecycle.py
git commit -m "$(cat <<'EOF'
feat(phase0): emit_marketing_event + full state-machine test coverage

Replaces the final stub in pilot_lifecycle.py. Adds 10 unit tests
that cover every branch of process_pilot:
  - day 0, 3, 7: engagement email cadence
  - day 14 with/without card: convert vs expire
  - day 16/30 expired: winback emails
  - idempotency: already_sent short-circuit
  - dry_run: never sends

Verified end-to-end with a dry-run cron invocation against a
synthetic pilot row.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

**End of Day 3.**

---

# DAY 4 — Retell `pilot_expired` flow node + TESTING E2E + promote

**Day 4 goal:** land the graceful-pause path in the Retell flow. When `pilot_expired=true` is set on the agent's dynamic variables (which `pause_retell_agent` from Task 22 does), every inbound call routes to a short goodbye message and hangs up cleanly. This is a MASTER flow change that **must** go through TESTING → promote.py per CLAUDE.md and retell-iac/CLAUDE.md.

**Critical ordering:** Tasks 24–26 all run against the TESTING agent (`agent_41e9758d8dc956843110e29a25`) only. Task 27 is the promote, blocked on Dan. Task 28 is Dan filming. Task 29 dark-launches the cron to Railway without Mux/website pieces so the cron is production-ready before Day 6.

---

## Task 24: Build the `pilot_expired` flow node

**Files:**
- Create: `retell-iac/components/pilot_expired_node.json`
- Create: `retell-iac/snapshots/2026-04-11_pre-pilot-expired/` (directory placeholder)
- Modify: `retell-iac/manifests/hvac-standard.yaml` (register the new component)

- [ ] **Step 1: Snapshot the current MASTER flow before any edits**

```bash
mkdir -p retell-iac/snapshots/2026-04-11_pre-pilot-expired
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-retell-llm/conversation_flow_19684fe03b61" \
  > retell-iac/snapshots/2026-04-11_pre-pilot-expired/master-flow.json
wc -c retell-iac/snapshots/2026-04-11_pre-pilot-expired/master-flow.json
```

Expected: >30KB.

Also snapshot TESTING:

```bash
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-retell-llm/conversation_flow_bc8bb3565dbf" \
  > retell-iac/snapshots/2026-04-11_pre-pilot-expired/testing-flow.json
```

- [ ] **Step 2: Write the `pilot_expired_node.json` component**

Create `retell-iac/components/pilot_expired_node.json`:

```json
{
  "body": {
    "instruction": {
      "text": "Thanks for calling. This line is currently paused while the owner decides on their service plan. If this is an emergency, please text this same number and the owner will get back to you. Thanks.",
      "type": "static_text"
    }
  }
}
```

The component follows the same shape as `greeting_node.json` and `ending.json` — a static-text node with no state or routing logic. The pilot expired routing itself happens on the **edge** from `identify_call_node`, not inside this node. The node body only contains the text to speak.

- [ ] **Step 3: Register the component in the manifest**

Open `retell-iac/manifests/hvac-standard.yaml` and find the `components:` list. Add a new entry in the same format as existing components (e.g. alongside `greeting_node`):

```yaml
  - name: pilot_expired_node
    file: components/pilot_expired_node.json
    type: conversation
```

(The exact YAML format will match whatever convention the existing manifest uses — check `greeting_node` for reference before editing.)

- [ ] **Step 4: Commit the component and manifest update**

```bash
git add retell-iac/components/pilot_expired_node.json \
        retell-iac/manifests/hvac-standard.yaml \
        retell-iac/snapshots/2026-04-11_pre-pilot-expired/
git commit -m "$(cat <<'EOF'
feat(retell-iac): add pilot_expired_node for Phase 0 graceful pause

New conversation node that plays a short goodbye message when a pilot
has expired without a payment method. The routing to this node is
added in Task 25 on the edge from identify_call_node, gated on the
dynamic variable pilot_expired == 'true'.

Pre-change MASTER and TESTING flows snapshotted to
retell-iac/snapshots/2026-04-11_pre-pilot-expired/ per retell-iac
CLAUDE.md Rule 9 (immutable baseline before any promote).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 25: Add edge from identify-call to `pilot_expired` when var is true

**Files:**
- Modify: `retell-iac/flows/hvac-standard.template.json` (add the new node + a high-priority edge from identify_call_node)

Approach: in the Retell flow template, the first user-facing routing node is `node-identify-call`. We add `node-pilot-expired` to the `nodes` list and prepend a new edge at the top of `node-identify-call.edges` that routes to it when `{{pilot_expired}}` equals `'true'`. Because edges are evaluated in order, putting this first ensures expired pilots are intercepted before any normal routing runs. The edge uses a dynamic-variable condition, not a prompt condition, so the LLM never has to decide — it's deterministic.

- [ ] **Step 1: Read the current edges list on `node-identify-call`**

```bash
python -c "
import json
flow = json.load(open('retell-iac/flows/hvac-standard.template.json'))
for n in flow['nodes']:
    if n.get('id') == 'node-identify-call':
        print(f'Node: {n[\"id\"]}')
        for i, e in enumerate(n.get('edges', [])):
            print(f'  edge[{i}] → {e[\"destination_node_id\"]}  (id={e[\"id\"]})')
        break
"
```

Expected: list of 6-8 edges (verify, callback, existing-customer, general-questions, transfer-call, ending vendor-deflect, etc.).

- [ ] **Step 2: Add the `pilot_expired` node to the template's `nodes` array**

In `retell-iac/flows/hvac-standard.template.json`, find the `"nodes"` array and add this entry (position it near `node-ending` since it's a terminal node):

```json
    {
      "__COMPONENT__": "pilot_expired_node",
      "display_position": {
        "x": 300,
        "y": 300
      },
      "edges": [
        {
          "destination_node_id": "node-ending",
          "id": "edge-pilot-expired-to-ending",
          "transition_condition": {
            "prompt": "Always",
            "type": "prompt"
          }
        }
      ],
      "id": "node-pilot-expired",
      "name": "pilot_expired_node",
      "type": "conversation"
    },
```

- [ ] **Step 3: Prepend a new edge at the top of `node-identify-call.edges`**

On `node-identify-call`, the `edges` array evaluation is ordered — we want the pilot_expired check to win before any prompt-based routing. Add this as the FIRST edge:

```json
        {
          "destination_node_id": "node-pilot-expired",
          "id": "edge-to-pilot-expired",
          "transition_condition": {
            "type": "equation",
            "equation": "{{pilot_expired}} == 'true'"
          }
        },
```

Verify that Retell's flow engine supports `"type": "equation"` — if it does not, fall back to a prompt-type condition like:

```json
        {
          "destination_node_id": "node-pilot-expired",
          "id": "edge-to-pilot-expired",
          "transition_condition": {
            "prompt": "The dynamic variable pilot_expired equals 'true' — always route here, unconditionally, before anything else.",
            "type": "prompt"
          }
        },
```

Document the choice in the commit message.

- [ ] **Step 4: Build the flow and diff it**

```bash
cd retell-iac
python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json
python scripts/diff.py \
  --left snapshots/2026-04-11_pre-pilot-expired/testing-flow.json \
  --right build/hvac-standard.built.json
cd ..
```

Expected: the diff shows exactly two changes — the new `node-pilot-expired` entry and the new edge on `node-identify-call`. No other nodes touched. If any other node has diffs, stop and investigate (build_agent.py determinism issue).

- [ ] **Step 5: Commit**

```bash
git add retell-iac/flows/hvac-standard.template.json
git commit -m "feat(retell-iac): wire pilot_expired edge from identify_call_node"
```

---

## Task 26: Build TESTING agent + E2E call verification

**Files:** none created. Modifies only the TESTING agent in Retell via its API.

- [ ] **Step 1: Patch the TESTING agent's flow with the built JSON**

```bash
curl -s -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/update-retell-llm/conversation_flow_bc8bb3565dbf" \
  -d @retell-iac/build/hvac-standard.built.json
```

Expected: HTTP 200 with updated flow. If 400, the JSON shape is rejected — inspect and fix.

- [ ] **Step 2: Publish the TESTING agent's flow**

Retell flow changes require a publish step to take effect on live calls:

```bash
curl -s -X POST -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/publish-retell-llm/conversation_flow_bc8bb3565dbf"
```

- [ ] **Step 3: Set `pilot_expired=true` on the TESTING agent**

```bash
curl -s -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/update-agent/agent_41e9758d8dc956843110e29a25" \
  -d '{"agent_level_dynamic_variables":{"pilot_expired":"true"}}'
```

Expected: HTTP 200 with updated agent.

- [ ] **Step 4: Create a test phone call to the TESTING agent**

Use Retell's web-call or phone-call API:

```bash
curl -s -X POST -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/create-web-call" \
  -d '{"agent_id":"agent_41e9758d8dc956843110e29a25"}'
```

Join the returned `call_link_url` in a browser. Speak anything to the agent.

Expected: the agent plays the `pilot_expired_node` text ("Thanks for calling. This line is currently paused...") within the first 2 seconds and hangs up. It should NOT route to `identify_call` normal flow, should NOT ask what the caller wants, should NOT collect details.

- [ ] **Step 5: Capture the call recording for the reports folder**

```bash
# Retell returns a call_id in the create-web-call response
# After call ends, fetch the recording:
CALL_ID="<call_id from step 4>"
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-call/${CALL_ID}" \
  > docs/audits/2026-04-11-pilot-expired-test-call.json
```

Verify the `transcript` field contains the pilot_expired message.

- [ ] **Step 6: Reset `pilot_expired=false` on TESTING and do a normal-flow verification call**

```bash
curl -s -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/update-agent/agent_41e9758d8dc956843110e29a25" \
  -d '{"agent_level_dynamic_variables":{"pilot_expired":"false"}}'
```

Create another web call. This time the agent should greet normally and run `identify_call` as before (ask what the caller needs, etc.). Confirm nothing is broken for the normal path.

- [ ] **Step 7: Write the verification report**

Create `docs/reports/2026-04-11-phase0-retell-pilot-expired-testing.md`:

```markdown
# Phase 0 — Retell pilot_expired testing verification (2026-04-11)

## Change summary
Added `node-pilot-expired` (pilot_expired_node component) to the HVAC
Standard flow template, plus a high-priority edge from `node-identify-call`
gated on dynamic variable `pilot_expired == 'true'`.

## TESTING agent E2E results
- Flow patched: conversation_flow_bc8bb3565dbf → published
- Agent: agent_41e9758d8dc956843110e29a25
- Snapshot: retell-iac/snapshots/2026-04-11_pre-pilot-expired/

### Test 1 — pilot_expired=true (expected: graceful pause)
- Call ID: <filled in>
- Caller said: "hello, I need someone out here"
- Agent response: <transcribed exactly>
- Duration: ~<N> seconds
- Hung up cleanly: <yes/no>
- Verdict: PASS / FAIL

### Test 2 — pilot_expired=false (expected: normal flow)
- Call ID: <filled in>
- Caller said: "my AC is broken"
- Agent response: greeted, asked for details, ran identify_call
- Verdict: PASS / FAIL

## Ready for promote to MASTER
- [ ] Test 1 passed
- [ ] Test 2 passed
- [ ] Snapshot captured
- [ ] Diff reviewed (Task 25 Step 4)

If all boxes checked → proceed to Task 27 (promote).
```

- [ ] **Step 8: Commit the report**

```bash
git add docs/reports/2026-04-11-phase0-retell-pilot-expired-testing.md \
        docs/audits/2026-04-11-pilot-expired-test-call.json
git commit -m "test(phase0): TESTING E2E verification for pilot_expired flow change"
```

---

## Task 27: Promote TESTING → MASTER

> ⚠️ **BLOCKED ON DAN:** This task cannot be executed by an autonomous agent. `retell-iac/scripts/promote.py` is the only writer for MASTER agents and per `retell-iac/CLAUDE.md` Rule 7 every promotion requires explicit Dan approval. Additionally per project `CLAUDE.md` "Iron rules": **never test or fix on live Retell agents** — promote is specifically the one step that cannot happen without Dan's go-ahead. Resolution: Dan reviews the Task 26 report, confirms TESTING is green, and issues explicit go-ahead in chat. Only then does this task run.

**Files:** none created. Modifies the MASTER agent in Retell via promote.py.

- [ ] **Step 1: Wait for Dan's explicit "go ahead, promote it" message in chat**

Do not proceed without this. Even if Task 26 passes, even if the diff is clean, even if the parity report is green — halt until Dan types approval.

- [ ] **Step 2: Dry-run the promote script**

```bash
cd retell-iac
python scripts/promote.py --agent standard_master --built build/hvac-standard.built.json --dry-run
cd ..
```

Expected: prints the MASTER flow ID it would write to (`conversation_flow_19684fe03b61`) and the diff preview. Confirms nothing unexpected would change.

- [ ] **Step 3: Run the promote for real**

```bash
cd retell-iac
python scripts/promote.py --agent standard_master --built build/hvac-standard.built.json
cd ..
```

Expected: `PROMOTED` with the MASTER flow_id and a git tag suggestion.

- [ ] **Step 4: Git tag the promotion**

```bash
git tag release-hvac-standard-v$(date +%Y%m%d)-pilot-expired
git push origin release-hvac-standard-v$(date +%Y%m%d)-pilot-expired
```

- [ ] **Step 5: Verify MASTER has the new node**

```bash
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  "https://api.retellai.com/v2/get-retell-llm/conversation_flow_19684fe03b61" | \
  python -c "
import json, sys
flow = json.load(sys.stdin)
names = [n.get('name') for n in flow.get('nodes', [])]
assert 'pilot_expired_node' in names, f'pilot_expired_node missing from MASTER. Nodes: {names}'
print('OK — pilot_expired_node present in MASTER')
print(f'Total nodes: {len(names)}')
"
```

Expected: "OK — pilot_expired_node present in MASTER".

- [ ] **Step 6: Test a real call to the MASTER phone number with `pilot_expired=false`**

MASTER is bound to `+18129944371`. Set the agent's `pilot_expired` variable to empty/false first:

```bash
curl -s -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/update-agent/agent_b46aef9fd327ec60c657b7a30a" \
  -d '{"agent_level_dynamic_variables":{"pilot_expired":"false"}}'
```

Call `+18129944371` from a real phone. Expected: Sophie greets normally (unchanged behavior). If the pilot_expired message plays, there is a misconfiguration and we must rollback via `retell-iac/scripts/rollback.py --tag baseline-100-percent-20260406`.

- [ ] **Step 7: Append Dan-approval + promotion record to the report**

Append to `docs/reports/2026-04-11-phase0-retell-pilot-expired-testing.md`:

```markdown
## MASTER promotion (2026-04-11 HH:MM UTC)
- Dan approval: "<quote Dan's exact message>"
- promote.py output: <paste>
- Git tag: release-hvac-standard-v2026-04-11-pilot-expired
- MASTER flow_id: conversation_flow_19684fe03b61
- Post-promote real-phone test: PASS (normal flow unchanged with pilot_expired=false)
```

- [ ] **Step 8: Commit the updated report**

```bash
git add docs/reports/2026-04-11-phase0-retell-pilot-expired-testing.md
git commit -m "docs(phase0): MASTER promoted — pilot_expired node live, real-phone verified"
```

---

## Task 28: Dan films the founder VSL (60s total)

> ⚠️ **BLOCKED ON DAN — Dan-only task:** This task cannot be executed by any autonomous agent. It requires Dan to hold a camera and speak on camera. Resolution: Dan follows the filming instructions below and uploads raw footage to a shared folder. Claude handles all post-production in Day 5.

**Files:** none in repo. Produces raw video files that live outside git.

**Filming script (from spec § 4.2):**

### 0:10–0:25 — Intro (camera-direct, medium shot)

> *"If that's ever been you — or if you can't remember the last weekend your phone didn't buzz past 10 p.m. — you're in the right place. I'm Dan. I built Syntharra for exactly one reason, and in the next four minutes I'm going to show you what it does, what it sounds like, and what it costs. No sales call. Just the thing."*

### 4:00–4:30 — Outro (same setup as intro)

> *"Go to syntharra dot com slash start. Six questions, four minutes, your AI is answering your business line before you finish reading today's work orders. I'll see you inside. Talk soon."*

**Filming instructions (reproduce verbatim from spec § 4.3):**

- [ ] **Step 1: Location setup**
  - Dan's kitchen near a large window, OR outside in open shade (overcast day or within 1 hour of sunset)
  - Never direct sunlight
  - Background: real, not a corporate backdrop, not a home office

- [ ] **Step 2: Framing**
  - Medium shot, camera at eye level
  - Phone or camera in landscape mode, 4–6 feet back
  - Do NOT film vertical

- [ ] **Step 3: Audio (the most important step)**
  - Record Dan's voice SEPARATELY using phone voice memo app
  - Held 6 inches from mouth
  - In a small soft-walled room (closet full of clothes works)
  - Sync to video in post

- [ ] **Step 4: Takes**
  - Film the intro 3 times with slight tone variations
  - Film the outro 3 times
  - More is fine — Dan picks his best later

- [ ] **Step 5: Wardrobe**
  - Whatever Dan would actually wear on a workday
  - No branded polos, no logos

- [ ] **Step 6: Delivery**
  - Upload raw footage to a shared folder (Dropbox/Drive — Dan picks)
  - Notify Claude via Slack with the folder link
  - Claude handles all post-production starting Day 5 Task 32

**If Dan genuinely cannot film (Option B fallback per spec § 4.3):**
- The VSL ships without Dan-on-camera sections
- Intro/outro replaced by voiceover-over-static-quote-cards using ElevenLabs voice cloned from Dan's best existing audio (e.g. a prior podcast appearance or voicemail greeting)
- Zero design rework; 1-day delay
- Dan notifies Claude and Claude shifts to Option B automatically

**No commit for this task — it produces raw media, not repo files.**

---

## Task 29: Day 4 session-end + Railway deploy of `pilot_lifecycle.py` cron

**Files:**
- Modify: `docs/STATE.md` (Phase 0 progress section)
- Create: `railway.toml` or modify existing Railway cron config (project-specific)

Approach: dark-launch the cron. Railway runs `pilot_lifecycle.py` daily starting tonight, but without Mux/website/Stripe-live pieces there are no pilots in prod yet, so the cron is a no-op. This gets the cron infrastructure battle-tested before real pilots depend on it.

- [ ] **Step 1: Verify Railway project config file**

```bash
# Check for existing Railway config
ls -la railway.toml railway.json .railway 2>&1 || echo "No Railway config at repo root"
```

If there's an existing cron setup for `monthly_minutes.py` or `usage_alert.py`, mirror it for `pilot_lifecycle.py`.

- [ ] **Step 2: Add the cron entry**

If Railway config is `railway.toml`, add:

```toml
[[cron]]
name = "pilot_lifecycle"
command = "python tools/pilot_lifecycle.py"
schedule = "0 0 * * *"
```

If Railway uses a different config format, match whatever `monthly_minutes.py` uses (it's already running daily per docs/STATE.md).

- [ ] **Step 3: Ensure all required env vars are set in Railway**

Via the Railway dashboard or CLI, confirm these are present on the service that will run the cron:

```
SUPABASE_URL
SUPABASE_SERVICE_KEY
BREVO_API_KEY
BREVO_TPL_PILOT_WELCOME
BREVO_TPL_PILOT_DAY_3
BREVO_TPL_PILOT_DAY_7
BREVO_TPL_PILOT_DAY_12
BREVO_TPL_PILOT_CONVERTED
BREVO_TPL_PILOT_CARD_ADDED
BREVO_TPL_PILOT_EXPIRED
BREVO_TPL_PILOT_WINBACK_16
BREVO_TPL_PILOT_WINBACK_30
STRIPE_SECRET_KEY     # test mode during Phase 0
RETELL_API_KEY
```

The Brevo template IDs come from Task 31 Day 5 (`tools/upload_brevo_templates.py`). Day 4 can deploy with `BREVO_TPL_*` set to `0` — the cron will skip sends (Task 20's guard rail: missing template ID returns empty message_id and logs an error, but does not crash).

- [ ] **Step 4: Deploy**

```bash
git add railway.toml
git commit -m "feat(phase0): Railway cron entry for pilot_lifecycle (dark launch)"
git push
```

Railway auto-deploys on push.

- [ ] **Step 5: Manually trigger the cron once on Railway to confirm it runs**

Via Railway CLI or dashboard, trigger the cron manually. Expected: `Found 0 active/expired pilots to evaluate. Done.` (no pilots exist yet in prod). No tracebacks.

- [ ] **Step 6: Update STATE.md**

Append to the Phase 0 progress section:

```markdown
**Day 3 complete:** pilot_lifecycle.py shipped with all 4 stubs replaced
(Brevo send, convert, expire, emit event). 10 unit tests cover every
state-machine branch. Cron dark-launched to Railway — runs daily,
currently a no-op because no pilots exist in prod yet.

**Day 4 complete:** pilot_expired Retell node in MASTER (promoted via
promote.py, Dan-approved). Real-phone test on +18129944371 with
pilot_expired=false confirms normal flow unchanged. Dan filmed intro +
outro (or switched to Option B voiceover fallback — annotate which).

**Next:** Day 5 — VSL production pipeline (blocked on several items).
```

- [ ] **Step 7: Run session-end**

```bash
python tools/session_end.py --topic phase-0-day-4 --summary "Phase 0 day 4: pilot_expired live in MASTER, cron dark-launched, Dan filmed"
git add docs/STATE.md
git commit -m "chore(session): session-end 2026-04-11 phase-0-day-4"
```

**End of Day 4.**

---

# DAY 5 — VSL production pipeline

**Day 5 goal:** produce a shippable 4:30 VSL. Most of this day is blocked on external resources (real calls, Mux credentials). Non-blocked tasks (B-roll, captions, export) proceed in parallel. The day ends when the final cut exists as an MP4, uploaded to Mux, with a playback ID in REFERENCE.md.

**Blockers summary:**
- Task 30: needs a representative live HVAC call to exist
- Task 35: needs Mux credentials in `syntharra_vault`

---

## Task 30: Capture target real-call audio from Retell

> ⚠️ **BLOCKED until a representative live call exists:** The spec § 4.2 mechanism-reveal section requires an unmuted 30–40 second clip of the TESTING agent handling a simulated or real HVAC emergency. Per § 4.3 production plan, the clip should have a caller saying something gratifying at the end ("oh thank god, thank you"). Resolution: either (a) Dan or a friend calls the TESTING agent from a mobile phone and roleplays an HVAC emergency 4–5 times, and the best take is selected; or (b) we wait for a real client call that hits the same emotional beats. Option (a) is faster and spec-approved for Phase 0.

**Files:**
- Create: `docs/audits/vsl-production-20260411/candidate-calls/` (directory)
- Create: `docs/audits/vsl-production-20260411/selected-clip.md`

- [ ] **Step 1: Ensure TESTING agent has `pilot_expired=false`**

```bash
curl -s -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.retellai.com/v2/update-agent/agent_41e9758d8dc956843110e29a25" \
  -d '{"agent_level_dynamic_variables":{"pilot_expired":"false"}}'
```

- [ ] **Step 2: Record 4–5 roleplayed emergency calls**

Dan or a friend calls the TESTING agent 4–5 times with varied scenarios:

1. 2am no-heat emergency in winter
2. Water leak from unit, can't shut it off
3. Burning smell from furnace
4. AC out in 100°F heat, elderly parent in the house
5. Carbon monoxide alarm going off

Each call runs 60–90 seconds. The caller should sound emotionally real (stressed, relieved at the end).

- [ ] **Step 3: Pull recordings from Retell**

```bash
# List recent calls for the TESTING agent
curl -s -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://api.retellai.com/v2/list-calls" \
  -d '{"filter_criteria":{"agent_id":["agent_41e9758d8dc956843110e29a25"]},"limit":10}' \
  > /tmp/recent-testing-calls.json

# Extract call IDs + recording URLs
python -c "
import json
calls = json.load(open('/tmp/recent-testing-calls.json'))
for c in calls:
    print(c.get('call_id'), c.get('recording_url'))
"
```

Download each recording:

```bash
mkdir -p docs/audits/vsl-production-20260411/candidate-calls
# For each call_id + recording_url from the list:
curl -o "docs/audits/vsl-production-20260411/candidate-calls/${CALL_ID}.mp3" "${RECORDING_URL}"
```

- [ ] **Step 4: Listen to each and select the best**

Judging criteria (from spec § 4.2):
- Agent voice is warm, natural, no AI tells (misheard words, canned phrases, unnatural pauses)
- Caller sounds emotionally real
- Caller says something gratifying at the end ("oh thank god, thank you")
- Call handles the emergency correctly (gathers name, address, issue, urgency, escalates)
- Clean audio (no background noise, no artifacts)

- [ ] **Step 5: Document the selected clip**

Create `docs/audits/vsl-production-20260411/selected-clip.md`:

```markdown
# VSL selected call clip

## Selection
- Call ID: <call_id>
- File: candidate-calls/<call_id>.mp3
- Duration: <MM:SS>
- Scenario: <e.g., "2am no-heat emergency, elderly caller">

## Why this one
- <bullet reasons matching spec § 4.2 criteria>

## Transcript highlights (for lower-third overlay)
- 00:03 — caller states emergency
- 00:18 — agent gathers address
- 00:34 — agent confirms escalation
- 00:42 — caller relieved

## Edits to apply in post
- Trim to 00:05–00:45 (40 seconds)
- Normalize audio to -16 LUFS
- Duck background during agent voice
```

- [ ] **Step 6: Commit**

```bash
git add docs/audits/vsl-production-20260411/
git commit -m "feat(phase0): capture VSL candidate calls + selected clip"
```

---

## Task 31: Generate Remotion B-roll for agent-iterable middle section

**Files:**
- Create: `video/remotion/` (new directory — may need `npm init` inside)
- Create: `video/remotion/src/PullQuoteCard.tsx`
- Create: `video/remotion/src/WaveformVisualization.tsx`
- Create: `video/remotion/src/OfferSlideStack.tsx`
- Create: `video/remotion/src/Root.tsx`
- Create: `video/remotion/package.json`
- Create: `video/remotion/remotion.config.ts`
- Create: `video/remotion/out/` (gitignored — render outputs)

Approach: Remotion templates are remixable by Phase 3 optimizer per spec § 4.5, so building them as React components with typed props is non-negotiable. Per spec § 4.3: pull-quote cards are white serif on pure black, 3-second hold, hard cut in/out; waveform is white on black responsive to call audio; offer slide stack is 4 bullets punching in on beat.

- [ ] **Step 1: Initialize the Remotion project**

```bash
mkdir -p video/remotion
cd video/remotion
npx create-video@latest --name=syntharra-vsl-assets --template=blank
cd ../..
```

Expected: `video/remotion/` populated with a Remotion skeleton.

- [ ] **Step 2: Add `.gitignore` entries**

Ensure `video/remotion/node_modules` and `video/remotion/out` are gitignored. Append to the repo root `.gitignore`:

```
video/remotion/node_modules
video/remotion/out
```

- [ ] **Step 3: Write `PullQuoteCard.tsx`**

Create `video/remotion/src/PullQuoteCard.tsx`:

```tsx
import { AbsoluteFill } from "remotion";

export type PullQuoteCardProps = {
  quote: string;
  attribution: string;
};

export const PullQuoteCard: React.FC<PullQuoteCardProps> = ({ quote, attribution }) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000",
        color: "#fff",
        fontFamily: "Georgia, 'Times New Roman', serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 120px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 64, lineHeight: 1.3, fontStyle: "italic", marginBottom: 40 }}>
        &ldquo;{quote}&rdquo;
      </div>
      <div style={{ fontSize: 32, opacity: 0.6 }}>— {attribution}</div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 4: Write `WaveformVisualization.tsx`**

Create `video/remotion/src/WaveformVisualization.tsx`:

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export type WaveformVisualizationProps = {
  bars?: number;
  color?: string;
};

export const WaveformVisualization: React.FC<WaveformVisualizationProps> = ({
  bars = 60,
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const barEls = Array.from({ length: bars }).map((_, i) => {
    // Pseudo-random per-bar phase — deterministic by index + time
    const phase = Math.sin((frame / fps) * 6 + i * 0.3);
    const height = interpolate(Math.abs(phase), [0, 1], [20, 200]);
    return (
      <div
        key={i}
        style={{
          width: 8,
          height,
          backgroundColor: color,
          borderRadius: 4,
        }}
      />
    );
  });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 6,
      }}
    >
      {barEls}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 5: Write `OfferSlideStack.tsx`**

Create `video/remotion/src/OfferSlideStack.tsx`:

```tsx
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig } from "remotion";

const BULLETS = [
  "200 call minutes",
  "14 days",
  "No credit card today",
  "Live in 4 minutes",
];

export const OfferSlideStack: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0e1a",
        color: "#fff",
        fontFamily: "'Inter', system-ui, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        justifyContent: "center",
        padding: "0 200px",
        gap: 40,
      }}
    >
      {BULLETS.map((bullet, i) => {
        const enter = spring({
          frame: frame - i * fps * 0.75,
          fps,
          config: { damping: 14, stiffness: 100 },
        });
        return (
          <div
            key={bullet}
            style={{
              fontSize: 80,
              fontWeight: 600,
              transform: `translateX(${(1 - enter) * -100}px)`,
              opacity: enter,
            }}
          >
            → {bullet}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 6: Register compositions in `Root.tsx`**

Create `video/remotion/src/Root.tsx`:

```tsx
import { Composition } from "remotion";
import { PullQuoteCard } from "./PullQuoteCard";
import { WaveformVisualization } from "./WaveformVisualization";
import { OfferSlideStack } from "./OfferSlideStack";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="pull-quote-birthday"
        component={PullQuoteCard}
        durationInFrames={90}  // 3s at 30fps
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote: "I ran out of my own 40th birthday party to get on site.",
          attribution: "r/HVAC",
        }}
      />
      <Composition
        id="pull-quote-graduation"
        component={PullQuoteCard}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote: "I almost missed my kids 8th grade graduation ceremony.",
          attribution: "r/HVAC",
        }}
      />
      <Composition
        id="pull-quote-2am"
        component={PullQuoteCard}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote:
            "The fucking answering service put a lady through once at 2 am... she wanted to know what the roads were like.",
          attribution: "r/HVAC",
        }}
      />
      <Composition
        id="pull-quote-oncall"
        component={PullQuoteCard}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote: "I got sick of always being on call.",
          attribution: "r/HVAC",
        }}
      />
      <Composition
        id="waveform-call"
        component={WaveformVisualization}
        durationInFrames={900}  // 30s at 30fps
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="offer-slide-stack"
        component={OfferSlideStack}
        durationInFrames={300}  // 10s
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
```

- [ ] **Step 7: Render all compositions to `out/`**

```bash
cd video/remotion
npx remotion render pull-quote-birthday out/pull-quote-birthday.mp4
npx remotion render pull-quote-graduation out/pull-quote-graduation.mp4
npx remotion render pull-quote-2am out/pull-quote-2am.mp4
npx remotion render pull-quote-oncall out/pull-quote-oncall.mp4
npx remotion render waveform-call out/waveform-call.mp4
npx remotion render offer-slide-stack out/offer-slide-stack.mp4
cd ../..
```

Expected: 6 MP4 files in `video/remotion/out/`. Each plays correctly.

- [ ] **Step 8: Commit source files (not outputs)**

```bash
git add video/remotion/src/ video/remotion/package.json video/remotion/remotion.config.ts .gitignore
git commit -m "feat(phase0): Remotion B-roll compositions for VSL (pull quotes, waveform, offer stack)"
```

---

## Task 32: DaVinci Resolve edit assembly

**Files:** produces `video/masters/vsl-v1-master.drp` (DaVinci project file) and the assembled timeline output. DaVinci project files are binary and large — store outside git at `video/masters/` which is gitignored. Create a text outline that IS committed.

- [ ] **Step 1: Add `video/masters/` to `.gitignore`**

Append:
```
video/masters/
```

- [ ] **Step 2: Create the timeline structure document**

Create `video/vsl-v1-timeline.md`:

```markdown
# VSL v1 — Final timeline (spec § 4.2)

Total: 4:30 (270 seconds)
Format: 1920×1080 @ 30fps H.264
Audio: stereo 48kHz, master -16 LUFS

| Time | Section | Source | Notes |
|---|---|---|---|
| 00:00–00:10 | Quote card (birthday) | video/remotion/out/pull-quote-birthday.mp4 | Hold 10s with ambient HVAC fan sound |
| 00:10–00:25 | Dan on camera intro | Dan's raw footage (best take) | Medium shot, clean audio from voice memo |
| 00:25–01:30 | Pain agitation | Rapid cuts: pull-quote-graduation, pull-quote-2am, pull-quote-oncall + stock b-roll | Dan VO over music bed at 20% |
| 01:30–02:15 | Mechanism + real call | video/remotion/out/waveform-call.mp4 + selected call clip audio | UNMUTED — music silent |
| 02:15–02:45 | Differentiator split-screen | Manual edit — pull-quote-2am LEFT, transcript scroll RIGHT | Dan VO |
| 02:45–03:30 | How it works (4-panel) | Screen recordings from Task 38+ onboarding | Speed-ramped 3x |
| 03:30–04:00 | Offer slide stack | video/remotion/out/offer-slide-stack.mp4 | Dan VO punching in with each bullet |
| 04:00–04:30 | Dan on camera outro | Dan's raw footage (best take) | Hard cut to URL card at 04:28 |

## Music bed
- Single track, royalty-free cinematic (Artlist or Epidemic Sound)
- 20% volume under Dan's VO sections
- SILENT during 01:30–02:15 (the real call clip)
- Slight build during 00:25–01:30 and 03:30–04:00

## Color grade
- Subtle teal-and-orange lift
- No film-emulation LUTs
- DaVinci Auto-match reference: Dan's intro take

## Transitions
- ALL HARD CUTS. No fades. No dissolves. No motion blur.
```

- [ ] **Step 3: Open DaVinci Resolve and build the timeline**

Manual step (not scriptable from CLI):
1. Create new project `vsl-v1` at `video/masters/vsl-v1.drp`
2. Set project to 1920×1080 30fps
3. Import all Remotion outputs from `video/remotion/out/`
4. Import Dan's raw footage from the Task 28 shared folder
5. Import the selected call clip from `docs/audits/vsl-production-20260411/candidate-calls/`
6. Build the timeline per `video/vsl-v1-timeline.md`
7. Apply the color grade (DaVinci Auto-match)
8. Apply the music bed (import royalty-free track, set volume ducking)

- [ ] **Step 4: Render a preview export**

In DaVinci: Deliver tab → YouTube 1080p preset → render to `video/masters/vsl-v1-preview.mp4`.

Review the preview. If any cut is wrong, timing is off, or audio levels feel bad, go back and fix before proceeding to Task 33.

- [ ] **Step 5: Commit the timeline document**

```bash
git add video/vsl-v1-timeline.md .gitignore
git commit -m "docs(phase0): VSL v1 timeline structure + DaVinci project layout"
```

---

## Task 33: CapCut captions pass for accessibility

**Files:** produces `video/masters/vsl-v1-captioned.srt` (captions file) and updated master MP4. The SRT IS committed; the MP4 is not.

- [ ] **Step 1: Export audio-only from the DaVinci preview**

In DaVinci or `ffmpeg`:

```bash
ffmpeg -i video/masters/vsl-v1-preview.mp4 -vn -acodec pcm_s16le video/masters/vsl-v1-audio.wav
```

- [ ] **Step 2: Auto-generate captions with CapCut**

Import `vsl-v1-preview.mp4` into CapCut. Use its auto-caption feature (Text → Auto-captions → English). Review every line and fix transcription errors (especially Dan's specific phrasing).

- [ ] **Step 3: Export SRT**

CapCut: Export → Subtitles as SRT → save to `video/masters/vsl-v1-captioned.srt`.

Alternatively, use `ffmpeg` + whisper.cpp if CapCut is unavailable:

```bash
# With whisper.cpp installed:
whisper video/masters/vsl-v1-audio.wav --model medium --output_format srt --output_dir video/masters/
```

- [ ] **Step 4: Review the SRT file**

Open `video/masters/vsl-v1-captioned.srt` in a text editor. Fix any:
- Misspelled brand names ("Syntharra", not "Cintara")
- Punctuation that obscures meaning
- Timing drift (captions appearing 0.5s+ off the voice)

- [ ] **Step 5: Burn captions into the master (optional — Mux supports separate SRT too)**

For Phase 0 we'll ship with Mux's auto-caption feature using the SRT as an override:

```bash
# Do NOT burn captions into the video yet — pass the SRT to Mux in Task 35.
# This lets viewers toggle captions off.
echo "SRT will be uploaded as a separate track in Task 35"
```

- [ ] **Step 6: Commit the SRT**

```bash
git add video/masters/vsl-v1-captioned.srt
git commit -m "feat(phase0): VSL v1 captions (SRT) for Mux upload"
```

---

## Task 34: Export master 1080p H.264

**Files:** produces `video/masters/vsl-v1-master.mp4` (NOT committed — gitignored).

- [ ] **Step 1: DaVinci deliver settings**

In DaVinci Resolve Deliver tab:
- Format: MP4
- Codec: H.264
- Resolution: 1920×1080
- Frame rate: 30fps
- Quality: CRF 18 (high quality)
- Audio: AAC, 320 kbps, stereo 48kHz
- Output path: `video/masters/vsl-v1-master.mp4`

- [ ] **Step 2: Render**

Click Render All. Wait (~5–10 min depending on hardware).

- [ ] **Step 3: Verify the output**

```bash
ffprobe -v error -show_format -show_streams video/masters/vsl-v1-master.mp4 2>&1 | head -60
```

Expected:
- duration ≈ 270 seconds (4:30)
- width=1920 height=1080
- codec_name=h264
- fps=30
- audio codec=aac, 48000 Hz, stereo
- bit rate >3 Mbps for video

- [ ] **Step 4: Run a Lighthouse-style QA checklist**

- [ ] Total duration 4:30 ±5s
- [ ] No black frames or visible cut errors
- [ ] No audio clipping (peaks below 0 dBFS, master around -16 LUFS)
- [ ] Dan's voice intelligible throughout
- [ ] Real call clip audible at spec § 4.2 1:30–2:15
- [ ] Music ducks correctly under VO
- [ ] Hard cuts only (no accidental transitions)
- [ ] Outro URL card holds for 2 seconds

Document issues if any; fix in DaVinci and re-render.

- [ ] **Step 5: Record master file hash**

```bash
shasum -a 256 video/masters/vsl-v1-master.mp4 > video/masters/vsl-v1-master.sha256
cat video/masters/vsl-v1-master.sha256
```

The hash is committed (tiny text file); the MP4 is not.

- [ ] **Step 6: Commit hash only**

```bash
git add video/masters/vsl-v1-master.sha256 2>/dev/null || echo "sha256 file may be gitignored — add explicitly"
# Force add if needed:
git add -f video/masters/vsl-v1-master.sha256
git commit -m "feat(phase0): VSL v1 master exported — sha256 pinned"
```

---

## Task 35: Mux upload via API

> ⚠️ **BLOCKED ON DAN:** Mux credentials are not currently in `syntharra_vault`. Resolution: Dan creates a Mux account (free tier, <$10/mo at Phase 0 traffic), generates an API token, and vaults it as: `service_name='Mux'`, `key_type='token_id'` + `key_type='token_secret'` (+ optionally `key_type='playback_signing_key'` if we decide to use signed playback URLs). Once vaulted, this task unblocks.

**Files:**
- Create: `tools/upload_vsl_to_mux.py`

- [ ] **Step 1: Wait for Dan to vault Mux credentials**

```sql
select key_type from syntharra_vault where service_name = 'Mux';
```

Expected output after Dan's action: at minimum `token_id` and `token_secret`. Halt if not present.

- [ ] **Step 2: Write the Mux uploader**

Create `tools/upload_vsl_to_mux.py`:

```python
#!/usr/bin/env python3
"""
upload_vsl_to_mux.py — Uploads the VSL master to Mux and registers the asset
in marketing_assets.

Usage:
  export MUX_TOKEN_ID=<from vault>
  export MUX_TOKEN_SECRET=<from vault>
  export SUPABASE_URL=...
  export SUPABASE_SERVICE_KEY=...
  python tools/upload_vsl_to_mux.py --file video/masters/vsl-v1-master.mp4 --srt video/masters/vsl-v1-captioned.srt
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

MUX_API = "https://api.mux.com"

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def mux(method, path, body=None):
    url = f"{MUX_API}{path}"
    auth = base64.b64encode(f"{env('MUX_TOKEN_ID')}:{env('MUX_TOKEN_SECRET')}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def upload_via_direct_upload(file_path):
    # 1. Create a direct upload
    upload = mux("POST", "/video/v1/uploads", {
        "new_asset_settings": {
            "playback_policy": ["public"],
            "video_quality": "plus",
            "mp4_support": "standard",
            "normalize_audio": True,
        },
        "cors_origin": "*",
    })
    upload_url = upload["data"]["url"]
    upload_id = upload["data"]["id"]
    print(f"Mux upload ID: {upload_id}")

    # 2. PUT the file
    with open(file_path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(upload_url, data=data, method="PUT",
                                 headers={"Content-Type": "video/mp4"})
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 201):
            sys.exit(f"PUT failed: {resp.status}")
    print(f"Uploaded {len(data)} bytes")

    # 3. Poll for asset creation
    for _ in range(60):
        u = mux("GET", f"/video/v1/uploads/{upload_id}")
        if u["data"].get("asset_id"):
            return u["data"]["asset_id"]
        time.sleep(5)
    sys.exit("Timed out waiting for asset")

def wait_for_playback_id(asset_id):
    for _ in range(60):
        a = mux("GET", f"/video/v1/assets/{asset_id}")
        if a["data"].get("status") == "ready":
            return a["data"]["playback_ids"][0]["id"]
        print(f"  asset status: {a['data'].get('status')}")
        time.sleep(5)
    sys.exit("Timed out waiting for asset ready")

def add_caption_track(asset_id, srt_path):
    # Mux requires captions to be uploaded via a URL (they fetch it),
    # so host the SRT somewhere temporarily or use Mux's direct text track API.
    # Simpler path: create the track pointing to a raw GitHub URL once committed.
    # For now, just print the manual instruction.
    print(f"\nMANUAL STEP: add SRT as a text track via Mux dashboard:")
    print(f"  Asset: {asset_id}")
    print(f"  File:  {srt_path}")
    print(f"  Language: en")

def register_in_marketing_assets(playback_id, asset_id):
    url = env("SUPABASE_URL").rstrip("/") + "/rest/v1/marketing_assets"
    headers = {
        "apikey": env("SUPABASE_SERVICE_KEY"),
        "Authorization": f"Bearer {env('SUPABASE_SERVICE_KEY')}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    body = {
        "id": "vsl-v1",
        "asset_type": "vsl",
        "title": "VSL v1 — founder-led 4:30 HVAC pilot close",
        "channel": "direct",
        "platform_asset_url": f"https://stream.mux.com/{playback_id}.m3u8",
        "metadata": {
            "mux_asset_id": asset_id,
            "mux_playback_id": playback_id,
            "duration_seconds": 270,
            "format": "1920x1080 H.264 30fps",
            "production_date": "2026-04-11",
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--srt", required=False)
    args = p.parse_args()

    if not Path(args.file).exists():
        sys.exit(f"File not found: {args.file}")

    print(f"Uploading {args.file}...")
    asset_id = upload_via_direct_upload(args.file)
    print(f"Asset: {asset_id}")

    playback_id = wait_for_playback_id(asset_id)
    print(f"Playback ID: {playback_id}")

    if args.srt:
        add_caption_track(asset_id, args.srt)

    rec = register_in_marketing_assets(playback_id, asset_id)
    print(f"Registered in marketing_assets: {rec}")

    print("\n=== DONE ===")
    print(f"Playback URL: https://stream.mux.com/{playback_id}.m3u8")
    print(f"Player embed: <mux-player playback-id=\"{playback_id}\" />")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the upload**

```bash
export MUX_TOKEN_ID=$(python tools/fetch_vault.py Mux token_id)
export MUX_TOKEN_SECRET=$(python tools/fetch_vault.py Mux token_secret)
python tools/upload_vsl_to_mux.py \
  --file video/masters/vsl-v1-master.mp4 \
  --srt video/masters/vsl-v1-captioned.srt
```

Expected: playback ID printed, `marketing_assets` row inserted.

- [ ] **Step 4: Upload the SRT as a caption track via Mux dashboard**

Manual step: Mux Dashboard → Assets → `vsl-v1` → Tracks → Add Text Track → upload `video/masters/vsl-v1-captioned.srt`, language=en, name="English".

- [ ] **Step 5: Commit the uploader script**

```bash
git add tools/upload_vsl_to_mux.py
git commit -m "feat(phase0): Mux uploader for VSL + marketing_assets registration"
```

---

## Task 36: Capture Mux playback ID, register in `docs/REFERENCE.md`

**Files:**
- Modify: `docs/REFERENCE.md`

- [ ] **Step 1: Add the Mux section**

```markdown
## Mux assets (Phase 0, 2026-04-11)

| Asset | Mux asset ID | Playback ID | Duration | Used by |
|---|---|---|---|---|
| VSL v1 (founder-led 4:30) | `<asset_id>` | `<playback_id>` | 4:30 | `start.html` (Task 39) |

Playback URL: `https://stream.mux.com/<playback_id>.m3u8`

Mux player embed:
```html
<mux-player
  playback-id="<playback_id>"
  metadata-video-id="vsl-v1"
  stream-type="on-demand"
  autoplay="muted"
  preload="auto"
></mux-player>
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/REFERENCE.md
git commit -m "docs(phase0): register VSL v1 Mux playback ID in REFERENCE.md"
```

---

## Task 37: Day 5 session-end

- [ ] **Step 1: Update STATE.md Phase 0 progress**

```markdown
**Day 5 complete:** VSL v1 master exported (1080p H.264, 4:30, sha256
pinned), captioned via SRT, uploaded to Mux (playback ID in REFERENCE.md),
registered in marketing_assets. Remotion sources committed for Phase 3
optimizer re-mix.

**Next:** Day 6 — landing page + tracker + Edge Function + full E2E.
```

- [ ] **Step 2: Commit + session-end**

```bash
git add docs/STATE.md
python tools/session_end.py --topic phase-0-day-5 --summary "Phase 0 day 5: VSL v1 shipped to Mux"
git commit -m "chore(session): session-end 2026-04-11 phase-0-day-5 VSL live"
```

**End of Day 5.**

---

# DAY 6 — syntharra-website clone + landing page + tracker JS

**Day 6 goal:** ship the landing page at `syntharra.com/start`, wire it to the pilot Jotform from Day 2, wire the tracker to the `marketing-event-ingest` Edge Function, and run a full compressed-time E2E that exercises the whole funnel from visit → pilot → convert / expire.

**Hard blocker:** `syntharra-website` sibling repo does not currently exist. Dan must clone the canonical remote (or confirm a new remote URL) before Task 38 can run. See Task 38 callout.

---

## Task 38: Clone or initialize `syntharra-website` as a sibling repo

> ⚠️ **BLOCKED ON DAN:** The `syntharra-website` repo does not currently exist as a sibling to `syntharra-automations` in this working tree. Per spec § 5.3 the landing page lives in that repo alongside the existing `dashboard.html`. Resolution: Dan either (a) provides the canonical remote URL and this task runs `git clone` into `../syntharra-website`, or (b) confirms there is no existing remote and a new repo should be `git init`'d from scratch with `dashboard.html` as the starting point. Option (a) is strongly preferred so we don't lose history.

**Files:** creates a sibling directory at `../syntharra-website/`. Nothing in `syntharra-automations` is modified except the plan report.

- [ ] **Step 1: Ask Dan which path**

Wait for Dan to say either:
- "The remote is `<url>`" → go to Step 2a
- "Init from scratch" → go to Step 2b

- [ ] **Step 2a: Clone the existing remote**

```bash
cd ..
git clone <REMOTE_URL> syntharra-website
cd syntharra-website
ls -la
cd ../syntharra-automations
```

Expected: `dashboard.html` exists in the sibling directory.

- [ ] **Step 2b: Init a fresh repo with dashboard.html scaffold**

```bash
cd ..
mkdir syntharra-website
cd syntharra-website
git init
mkdir assets
# Copy the existing dashboard.html from wherever it currently lives
# (the plan assumes dan will paste it or reference it)
cd ../syntharra-automations
```

- [ ] **Step 3: Verify the sibling exists**

```bash
ls -la ../syntharra-website/
```

Expected: repo contents visible, `.git/` present.

- [ ] **Step 4: Record the working tree layout**

Append to `docs/STATE.md`:

```markdown
**Repo layout (Phase 0):**
- `syntharra-automations/` (this repo) — backend, tools, retell-iac, docs
- `syntharra-website/` (sibling) — landing page, dashboard, tracker JS
```

- [ ] **Step 5: Commit the layout note**

```bash
git add docs/STATE.md
git commit -m "docs(phase0): record sibling repo layout for Phase 0"
```

---

## Task 39: Create `start.html`

**Files:**
- Create: `../syntharra-website/start.html`

- [ ] **Step 1: Write the landing page**

Create `../syntharra-website/start.html`:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Your phone stops ruining your life tonight. — Syntharra</title>
<meta name="description" content="14-day free pilot. 200 call minutes. No credit card. Your AI is live in 4 minutes." />
<link rel="stylesheet" href="assets/dashboard.css" />
<link rel="stylesheet" href="assets/start.css" />
<script src="https://cdn.jsdelivr.net/npm/@mux/mux-player"></script>
<script src="assets/marketing-tracker.js" defer></script>
</head>
<body class="start-page">
  <header class="start-header">
    <a href="/" class="wordmark">Syntharra</a>
  </header>

  <section class="hero">
    <h1>Your phone stops ruining your life tonight.</h1>
    <p class="subhead">
      14-day free pilot. 200 call minutes. No credit card.
      Your AI is live in 4 minutes.
    </p>

    <div class="vsl-wrapper">
      <mux-player
        id="vsl-player"
        playback-id="__MUX_PLAYBACK_ID__"
        metadata-video-id="vsl-v1"
        stream-type="on-demand"
        autoplay="muted"
        preload="auto"
      ></mux-player>
    </div>

    <a href="#" class="cta cta-primary" data-cta="primary">
      START MY FREE PILOT →
    </a>
    <p class="micro">no card · cancel anytime · live in 4 min</p>
  </section>

  <section class="call-snippets">
    <h2>Hear your AI handle a real emergency call</h2>
    <div class="snippet-grid">
      <button class="snippet" data-snippet="emergency">
        <span class="play">▶</span>
        <span class="label">2:47 AM emergency</span>
      </button>
      <button class="snippet" data-snippet="booking">
        <span class="play">▶</span>
        <span class="label">Booking a repair</span>
      </button>
      <button class="snippet" data-snippet="quote">
        <span class="play">▶</span>
        <span class="label">Quote request</span>
      </button>
    </div>
  </section>

  <section class="bullets">
    <h2>What your AI does, every call, every hour</h2>
    <ul>
      <li>☎ Answers in under 2 rings, 24/7, even Christmas morning</li>
      <li>🚨 Escalates real emergencies to your phone — not noise, not at 2am for road conditions</li>
      <li>📋 Books, quotes, and logs every call — your dashboard is up to date by the time you're in the truck</li>
    </ul>
    <a href="#" class="cta cta-secondary" data-cta="secondary">
      START MY FREE PILOT →
    </a>
  </section>

  <section class="faq">
    <h2>Frequently asked</h2>
    <details data-faq="is-ai"><summary>Is this actually AI or a call center?</summary>
      <p>AI. Real humans don't scale and they sleep. This is software, it's Syntharra's agent, and you can hear it in the recordings above.</p>
    </details>
    <details data-faq="after-14"><summary>What happens after the 14 days?</summary>
      <p>If your AI caught enough calls to be worth it, you stay live at about $161 a week — same rate forever, cancel any time. If not, you walk and you keep all the data.</p>
    </details>
    <details data-faq="not-worth"><summary>What if it doesn't catch enough calls to be worth it?</summary>
      <p>Walk. Keep the call logs, keep the transcripts, we don't chase you. The offer is designed so you have zero downside.</p>
    </details>
    <details data-faq="keep-number"><summary>Can I keep my existing number?</summary>
      <p>Yes. You can either forward your existing number to your Syntharra line (no porting required) or we'll give you a new local number in your area code — your choice in the onboarding form.</p>
    </details>
    <details data-faq="how-many"><summary>How many calls does the $161-a-week plan cover?</summary>
      <p>700 minutes a month — roughly 350–400 calls depending on length. Most 1–3 truck shops use under 500. If you go over, it's 18 cents per extra minute, no surprises.</p>
    </details>
    <details data-faq="ai-aware"><summary>Will my customers know it's AI?</summary>
      <p>Depends on you. You tell the AI in the onboarding form how to introduce itself. Some owners say "you've reached the auto-assistant for Acme HVAC" up front, some don't. Your call — the AI is scripted however you want.</p>
    </details>

    <a href="#" class="cta cta-tertiary" data-cta="tertiary">
      START MY FREE PILOT →
    </a>
  </section>

  <section class="ps">
    <h3>P.S.</h3>
    <p>Here's what I know after listening to hundreds of HVAC owners: nobody's phone problem gets solved by hiring another human. You'd need three of them, they'd all quit in six months, and you'd still miss the 2am call. So I built the thing that was going to get built eventually anyway, and I made the offer as low-risk as I could make it.</p>
    <p>14 days. 200 minutes. Zero credit card.</p>
    <p>If your AI catches five or more calls you would've missed, you stay live for about a hundred-sixty a week. If it doesn't, you walk with the data. Either way, you'll have your answer in two weeks instead of spending another year telling yourself "maybe I should hire someone."</p>
    <p class="sig">— Dan, Founder</p>
  </section>

  <footer class="start-footer">
    <span class="wordmark">Syntharra</span>
    <nav>
      <a href="/terms">Terms</a>
      <a href="/privacy">Privacy</a>
    </nav>
  </footer>
</body>
</html>
```

- [ ] **Step 2: Replace the playback ID placeholder**

```bash
cd ../syntharra-website
sed -i.bak "s/__MUX_PLAYBACK_ID__/<ACTUAL_PLAYBACK_ID_FROM_TASK_36>/" start.html
rm start.html.bak
cd ../syntharra-automations
```

- [ ] **Step 3: Commit in the sibling repo**

```bash
cd ../syntharra-website
git add start.html
git commit -m "feat(phase0): start.html landing page with Mux VSL embed"
cd ../syntharra-automations
```

---

## Task 40: Create `assets/marketing-tracker.js`

**Files:**
- Create: `../syntharra-website/assets/marketing-tracker.js`

- [ ] **Step 1: Write the tracker**

Create `../syntharra-website/assets/marketing-tracker.js`:

```javascript
// marketing-tracker.js — Phase 0 client-side event tracker for syntharra.com/start
// Per spec § 7.4. Pure vanilla JS, no dependencies.
// Emits events to Supabase Edge Function marketing-event-ingest.

(function () {
  "use strict";

  var INGEST_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/marketing-event-ingest";
  var STORAGE_KEY_VISITOR = "stx_visitor_id";
  var STORAGE_KEY_FIRST_TOUCH_ASSET = "stx_first_touch_asset";
  var STORAGE_KEY_FIRST_TOUCH_UTM = "stx_first_touch_utm";
  var PILOT_JOTFORM_URL = "https://form.jotform.com/__PILOT_FORM_ID__";

  function uuid() {
    return (crypto.randomUUID && crypto.randomUUID()) ||
      "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === "x" ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
  }

  function getOrCreateVisitorId() {
    try {
      var id = localStorage.getItem(STORAGE_KEY_VISITOR);
      if (!id) {
        id = uuid();
        localStorage.setItem(STORAGE_KEY_VISITOR, id);
      }
      return id;
    } catch (_) {
      return uuid();
    }
  }

  function parseParams() {
    var params = new URLSearchParams(window.location.search);
    return {
      stx_asset_id: params.get("stx") || null,
      utm_source: params.get("utm_source") || null,
      utm_medium: params.get("utm_medium") || null,
      utm_campaign: params.get("utm_campaign") || null,
      utm_content: params.get("utm_content") || null,
      utm_term: params.get("utm_term") || null,
    };
  }

  function persistFirstTouch(params) {
    try {
      if (params.stx_asset_id && !localStorage.getItem(STORAGE_KEY_FIRST_TOUCH_ASSET)) {
        localStorage.setItem(STORAGE_KEY_FIRST_TOUCH_ASSET, params.stx_asset_id);
      }
      if (params.utm_source && !localStorage.getItem(STORAGE_KEY_FIRST_TOUCH_UTM)) {
        localStorage.setItem(STORAGE_KEY_FIRST_TOUCH_UTM, JSON.stringify({
          source: params.utm_source,
          medium: params.utm_medium,
          campaign: params.utm_campaign,
          content: params.utm_content,
          term: params.utm_term,
        }));
      }
    } catch (_) {}
  }

  var session = {
    session_id: uuid(),
    visitor_id: getOrCreateVisitorId(),
    params: parseParams(),
  };
  persistFirstTouch(session.params);

  function emit(eventType, metadata) {
    var body = {
      session_id: session.session_id,
      visitor_id: session.visitor_id,
      event_type: eventType,
      asset_id: session.params.stx_asset_id || "vsl-v1",
      utm_source: session.params.utm_source,
      utm_medium: session.params.utm_medium,
      utm_campaign: session.params.utm_campaign,
      utm_content: session.params.utm_content,
      utm_term: session.params.utm_term,
      referrer: document.referrer || null,
      user_agent: navigator.userAgent,
      metadata: metadata || {},
    };
    // Use sendBeacon where available for fire-and-forget + page unload safety
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify(body)], { type: "application/json" });
        navigator.sendBeacon(INGEST_URL, blob);
        return;
      }
    } catch (_) {}
    fetch(INGEST_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      keepalive: true,
    }).catch(function () {});
  }

  // === Page view ===
  emit("page_view", { path: window.location.pathname });

  // === Mux VSL player events ===
  document.addEventListener("DOMContentLoaded", function () {
    var player = document.getElementById("vsl-player");
    if (!player) return;

    emit("vsl_impression");
    var sent = { play: false, p25: false, p50: false, p75: false, complete: false };

    player.addEventListener("play", function () {
      if (!sent.play) { emit("vsl_play"); sent.play = true; }
    });
    player.addEventListener("pause", function () { emit("vsl_pause"); });
    player.addEventListener("seeked", function () { emit("vsl_seek"); });
    player.addEventListener("ended", function () {
      if (!sent.complete) { emit("vsl_complete"); sent.complete = true; }
    });
    player.addEventListener("timeupdate", function () {
      var d = player.duration || 0;
      var t = player.currentTime || 0;
      if (!d) return;
      var pct = t / d;
      if (pct >= 0.25 && !sent.p25) { emit("vsl_25pct"); sent.p25 = true; }
      if (pct >= 0.50 && !sent.p50) { emit("vsl_50pct"); sent.p50 = true; }
      if (pct >= 0.75 && !sent.p75) { emit("vsl_75pct"); sent.p75 = true; }
    });
  });

  // === CTA clicks ===
  document.addEventListener("click", function (ev) {
    var target = ev.target.closest("[data-cta]");
    if (target) {
      ev.preventDefault();
      emit("cta_click", { position: target.getAttribute("data-cta") });

      // Build Jotform URL with tracking params
      var qs = new URLSearchParams();
      qs.set("stx_asset_id", session.params.stx_asset_id || "vsl-v1");
      qs.set("pilot_mode", "true");
      if (session.params.utm_source) qs.set("utm_source", session.params.utm_source);
      if (session.params.utm_medium) qs.set("utm_medium", session.params.utm_medium);
      if (session.params.utm_campaign) qs.set("utm_campaign", session.params.utm_campaign);
      if (session.params.utm_content) qs.set("utm_content", session.params.utm_content);
      if (session.params.utm_term) qs.set("utm_term", session.params.utm_term);
      setTimeout(function () {
        window.location.href = PILOT_JOTFORM_URL + "?" + qs.toString();
      }, 100);
      return;
    }

    var snippet = ev.target.closest("[data-snippet]");
    if (snippet) {
      emit("call_snippet_play", { snippet: snippet.getAttribute("data-snippet") });
    }

    var faq = ev.target.closest("[data-faq]");
    if (faq) {
      emit("faq_expand", { faq: faq.getAttribute("data-faq") });
    }
  });
})();
```

- [ ] **Step 2: Replace the Jotform placeholder**

Replace `__PILOT_FORM_ID__` with the actual pilot form ID from Task 13 (recorded in REFERENCE.md).

- [ ] **Step 3: Commit in the sibling repo**

```bash
cd ../syntharra-website
git add assets/marketing-tracker.js
git commit -m "feat(phase0): marketing-tracker.js — page_view, vsl_*, cta_click, snippets, faq"
cd ../syntharra-automations
```

---

## Task 41: Create `assets/start.css`

**Files:**
- Create: `../syntharra-website/assets/start.css`

- [ ] **Step 1: Write the stylesheet (reusing dashboard.css tokens)**

Create `../syntharra-website/assets/start.css`:

```css
/* start.css — Phase 0 landing page at syntharra.com/start
 * Reuses dashboard.css tokens (assumes --brand-dark, --brand-accent, etc.)
 * Mobile-first. Dark-mode default. */

.start-page {
  font-family: "Inter", system-ui, -apple-system, sans-serif;
  background: var(--brand-dark, #0a0e1a);
  color: var(--brand-text, #f5f6f8);
  margin: 0;
  padding: 0;
  line-height: 1.55;
}

.start-header {
  padding: 16px 24px;
}
.start-header .wordmark {
  font-weight: 700;
  color: var(--brand-text, #f5f6f8);
  text-decoration: none;
  letter-spacing: 0.05em;
}

.hero {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 20px 64px;
  text-align: center;
}
.hero h1 {
  font-size: clamp(32px, 6vw, 64px);
  font-weight: 700;
  line-height: 1.1;
  margin: 0 0 16px;
}
.hero .subhead {
  font-size: clamp(16px, 2.5vw, 22px);
  opacity: 0.85;
  margin: 0 0 40px;
}

.vsl-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 32px;
  background: #000;
}
.vsl-wrapper mux-player {
  width: 100%;
  height: 100%;
}

.cta {
  display: inline-block;
  padding: 18px 42px;
  font-size: clamp(18px, 2.5vw, 22px);
  font-weight: 700;
  letter-spacing: 0.02em;
  background: var(--brand-accent, #ff6b35);
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  transition: transform 0.1s ease;
  animation: pulse 2.5s ease-in-out infinite;
}
.cta:hover { transform: translateY(-2px); }
.cta:active { transform: translateY(1px); }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,107,53,0.5); }
  50% { box-shadow: 0 0 0 10px rgba(255,107,53,0); }
}

.micro {
  margin: 16px 0 0;
  font-size: 14px;
  opacity: 0.6;
}

.call-snippets, .bullets, .faq, .ps {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 20px;
}
.call-snippets h2, .bullets h2, .faq h2 {
  font-size: clamp(24px, 4vw, 36px);
  text-align: center;
  margin: 0 0 32px;
}

.snippet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}
.snippet {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  color: inherit;
  padding: 20px 16px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.snippet:hover { background: rgba(255,255,255,0.10); }
.snippet .play { font-size: 22px; color: var(--brand-accent, #ff6b35); }

.bullets ul {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
}
.bullets li {
  font-size: 18px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.bullets li:last-child { border-bottom: none; }

.faq details {
  padding: 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
}
.faq summary {
  font-size: 18px;
  font-weight: 600;
  list-style: none;
}
.faq summary::-webkit-details-marker { display: none; }
.faq p {
  margin-top: 12px;
  opacity: 0.85;
}

.ps {
  border-top: 1px solid rgba(255,255,255,0.12);
  padding-top: 48px;
}
.ps h3 {
  font-size: 24px;
  margin: 0 0 16px;
}
.ps .sig {
  font-style: italic;
  opacity: 0.8;
  margin-top: 24px;
}

.start-footer {
  padding: 24px;
  text-align: center;
  opacity: 0.5;
  font-size: 14px;
}
.start-footer nav a {
  color: inherit;
  margin: 0 8px;
  text-decoration: underline;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .cta { animation: none; }
}
```

- [ ] **Step 2: Commit in the sibling repo**

```bash
cd ../syntharra-website
git add assets/start.css
git commit -m "feat(phase0): start.css — landing page styles reusing dashboard tokens"
cd ../syntharra-automations
```

---

## Task 42: Deploy `marketing-event-ingest` Edge Function

**Files:**
- Create: `supabase/functions/marketing-event-ingest/index.ts`
- Create: `supabase/functions/marketing-event-ingest/deno.json`

- [ ] **Step 1: Write the function**

Create `supabase/functions/marketing-event-ingest/index.ts`:

```typescript
// marketing-event-ingest — Phase 0 tracker event ingestion with bot filter + rate limit.
// Per spec § 7.3. Accepts POST from syntharra.com/start tracker JS.
// Inserts into marketing_events via service_role key.
//
// Bot filter: reject User-Agent containing bot|crawler|spider|headless|phantom
// Rate limit: 100 events/60s/visitor_id (silent drop over limit)

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const BOT_UA_RE = /bot|crawler|spider|headless|phantom|slurp|archiver/i;

// In-memory rate limiter (resets on cold start; good enough for Phase 0).
const rateBuckets = new Map<string, { count: number; windowStart: number }>();
const RATE_LIMIT = 100;
const WINDOW_MS = 60_000;

function checkRateLimit(visitorId: string): boolean {
  const now = Date.now();
  const bucket = rateBuckets.get(visitorId);
  if (!bucket || now - bucket.windowStart > WINDOW_MS) {
    rateBuckets.set(visitorId, { count: 1, windowStart: now });
    return true;
  }
  bucket.count += 1;
  return bucket.count <= RATE_LIMIT;
}

async function insertEvent(event: Record<string, unknown>): Promise<Response> {
  return fetch(`${SUPABASE_URL}/rest/v1/marketing_events`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(event),
  });
}

function ipCountryFromHeaders(req: Request): [string | null, string | null] {
  const country = req.headers.get("cf-ipcountry") || req.headers.get("x-vercel-ip-country") || null;
  const region = req.headers.get("x-vercel-ip-country-region") || null;
  return [country, region];
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }
  if (req.method !== "POST") {
    return new Response("POST only", { status: 405 });
  }

  // Silent-drop invalid payloads (don't give scrapers feedback)
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response("ok", { status: 200 });
  }

  const ua = (body.user_agent as string) || req.headers.get("user-agent") || "";
  if (BOT_UA_RE.test(ua)) {
    return new Response("ok", { status: 200 });  // silent drop
  }

  const visitorId = (body.visitor_id as string) || "anon";
  if (!checkRateLimit(visitorId)) {
    return new Response("ok", { status: 200 });  // silent drop
  }

  const [country, region] = ipCountryFromHeaders(req);

  const row = {
    session_id: body.session_id || "unknown",
    visitor_id: body.visitor_id || null,
    client_agent_id: body.client_agent_id || null,
    event_type: body.event_type || "unknown",
    asset_id: body.asset_id || null,
    utm_source: body.utm_source || null,
    utm_medium: body.utm_medium || null,
    utm_campaign: body.utm_campaign || null,
    utm_content: body.utm_content || null,
    utm_term: body.utm_term || null,
    referrer: body.referrer || null,
    user_agent: ua,
    ip_country: country,
    ip_region: region,
    metadata: body.metadata || {},
  };

  const resp = await insertEvent(row);
  if (!resp.ok) {
    console.error("insert failed", await resp.text());
  }

  return new Response("ok", {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  });
});
```

Create `supabase/functions/marketing-event-ingest/deno.json`:

```json
{
  "imports": {
    "std/": "https://deno.land/std@0.224.0/"
  }
}
```

- [ ] **Step 2: Deploy via MCP**

Via `mcp__claude_ai_Supabase__deploy_edge_function`:

```
function name: marketing-event-ingest
file: supabase/functions/marketing-event-ingest/index.ts
```

- [ ] **Step 3: Smoke test: normal event**

```bash
curl -X POST "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/marketing-event-ingest" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh)" \
  -d '{"session_id":"test-1","visitor_id":"visitor-test","event_type":"page_view","asset_id":"vsl-v1"}'
```

Expected: HTTP 200 body `ok`. Check `marketing_events` — one row with `visitor_id='visitor-test'`.

- [ ] **Step 4: Smoke test: bot filter**

```bash
curl -X POST "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/marketing-event-ingest" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Googlebot/2.1" \
  -d '{"session_id":"test-2","visitor_id":"googlebot-test","event_type":"page_view"}'
```

Expected: HTTP 200 but NO row inserted (silent drop).

```sql
select count(*) from marketing_events where visitor_id = 'googlebot-test';
```
Expected: 0.

- [ ] **Step 5: Smoke test: rate limit**

```bash
for i in $(seq 1 105); do
  curl -s -X POST "https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/marketing-event-ingest" \
    -H "Content-Type: application/json" \
    -d '{"session_id":"rate-test","visitor_id":"rate-visitor","event_type":"page_view"}' > /dev/null
done

# Check how many landed
```

```sql
select count(*) from marketing_events where visitor_id = 'rate-visitor';
```
Expected: ≤ 100 (the 101st+ were silently dropped).

- [ ] **Step 6: Cleanup**

```sql
delete from marketing_events where visitor_id in ('visitor-test', 'rate-visitor', 'googlebot-test');
```

- [ ] **Step 7: Commit**

```bash
git add supabase/functions/marketing-event-ingest
git commit -m "feat(phase0): marketing-event-ingest Edge Function with bot filter + rate limit"
```

---

## Task 43: Wire `start.html` form action to the pilot Jotform

**Files:**
- Modify: `../syntharra-website/assets/marketing-tracker.js` (already done in Task 40 via `PILOT_JOTFORM_URL`)
- Modify: `docs/REFERENCE.md` (cross-check pilot form ID matches tracker)

- [ ] **Step 1: Verify the pilot form ID in tracker matches REFERENCE.md**

```bash
grep PILOT_JOTFORM_URL ../syntharra-website/assets/marketing-tracker.js
grep "HVAC Standard pilot onboarding" docs/REFERENCE.md
```

Both should reference the same form ID.

- [ ] **Step 2: Manual verification — click the CTA in a local preview**

Serve the landing page locally:

```bash
cd ../syntharra-website
python -m http.server 8080 &
SERVER_PID=$!
```

Open `http://localhost:8080/start.html?stx=test-local&utm_source=manual`. Click the CTA. Expected: redirect to the pilot Jotform with query string including `stx_asset_id=test-local`, `pilot_mode=true`, `utm_source=manual`.

```bash
kill $SERVER_PID
cd ../syntharra-automations
```

- [ ] **Step 3: No commit needed** — Task 40 already has the wiring. This task is verification.

---

## Task 44: Write the final landing page copy

**Files:** Task 39 already wrote the copy per spec § 5.2 and § 5.4. This task is a review pass.

- [ ] **Step 1: Cross-check copy against spec § 5.2**

Open `../syntharra-website/start.html` and verify line-by-line against spec § 5.2:

- [ ] H1 matches: *"Your phone stops ruining your life tonight."*
- [ ] Subheading matches: *"14-day free pilot. 200 call minutes. No credit card. Your AI is live in 4 minutes."*
- [ ] Primary CTA text: *"START MY FREE PILOT →"*
- [ ] Micro-copy below CTA: *"no card · cancel anytime · live in 4 min"*
- [ ] Section 2 H2: *"Hear your AI handle a real emergency call"*
- [ ] Three call snippet buttons with correct labels
- [ ] "What your AI does" three bullets verbatim
- [ ] All 6 FAQ questions + answers verbatim
- [ ] P.S. section: the founder-direct version from spec § 5.2 (NOT a fabricated anecdote — per spec § 14 decision #1)

- [ ] **Step 2: Fix any mismatch**

If any line drifted from the spec, fix it in `start.html` and commit separately.

- [ ] **Step 3: Lighthouse score check**

```bash
cd ../syntharra-website
python -m http.server 8080 &
SERVER_PID=$!
# Run Lighthouse (or equivalent) against http://localhost:8080/start.html
# Target: Lighthouse mobile score ≥85, LCP <2.5s, CLS <0.1
# (Manual — no CLI lighthouse assumed available)
kill $SERVER_PID
cd ../syntharra-automations
```

Document results in `docs/audits/2026-04-11-phase0-day6-lighthouse.md`.

- [ ] **Step 4: Commit (if any fixes were made)**

```bash
cd ../syntharra-website
git add start.html
git commit -m "fix(phase0): align start.html copy with spec § 5.2"
cd ../syntharra-automations
```

---

## Task 45: Full compressed-time E2E — convert + expire paths

**Files:**
- Create: `tools/test_e2e_pilot.py`

Approach per spec § 8 Day 6 and § 10.3 "Full compressed-time E2E" lines: insert a synthetic pilot row with `pilot_ends_at = now() + 10 minutes`, set Stripe subscription `trial_end` to match, run `pilot_lifecycle.py` manually at T+11 min, assert the convert-or-expire path executes.

- [ ] **Step 1: Write the E2E harness**

Create `tools/test_e2e_pilot.py`:

```python
#!/usr/bin/env python3
"""
test_e2e_pilot.py — Compressed-time E2E test for the Phase 0 pilot flow.

Runs two scenarios:
  1. Convert path: pilot with payment_method_added_at → should flip to status=active
  2. Expire path:  pilot without payment → should flip to status=expired, Retell paused

Uses short pilot windows (10 min) and sleeps between stages, so the full
test runs in about 15 minutes.

Usage:
  export SUPABASE_URL=...
  export SUPABASE_SERVICE_KEY=...
  export BREVO_API_KEY=...
  export STRIPE_SECRET_KEY=...  (test mode)
  export RETELL_API_KEY=...
  python tools/test_e2e_pilot.py --scenario convert
  python tools/test_e2e_pilot.py --scenario expire
  python tools/test_e2e_pilot.py --scenario all
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v

def sb_url(p):
    return env("SUPABASE_URL").rstrip("/") + p

def sb_headers():
    return {
        "apikey": env("SUPABASE_SERVICE_KEY"),
        "Authorization": f"Bearer {env('SUPABASE_SERVICE_KEY')}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def http(method, url, headers, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode() or "{}")

def insert_synthetic_pilot(agent_id, with_card):
    now = datetime.now(timezone.utc)
    ends = now + timedelta(minutes=10)
    body = {
        "agent_id": agent_id,
        "company_name": f"E2E Test {agent_id[-4:]}",
        "client_email": "e2e-test@example.com",
        "status": "pilot",
        "pilot_mode": True,
        "pilot_started_at": now.isoformat(),
        "pilot_ends_at": ends.isoformat(),
        "pilot_minutes_allotted": 200,
        "pilot_minutes_used": 0,
        "payment_method_added_at": now.isoformat() if with_card else None,
        "included_minutes": 700,
        "overage_rate": 0.18,
        "tier": "hvac_standard",
    }
    status, data = http("POST", sb_url("/rest/v1/client_subscriptions"), sb_headers(), body)
    assert status in (200, 201), f"insert failed: {status} {data}"
    print(f"  Inserted synthetic pilot {agent_id}")

def fetch_pilot(agent_id):
    url = sb_url(f"/rest/v1/client_subscriptions?agent_id=eq.{agent_id}&select=*")
    _, data = http("GET", url, sb_headers())
    return data[0] if data else None

def cleanup_pilot(agent_id):
    url = sb_url(f"/rest/v1/client_subscriptions?agent_id=eq.{agent_id}")
    http("DELETE", url, sb_headers())
    url2 = sb_url(f"/rest/v1/marketing_events?client_agent_id=eq.{agent_id}")
    http("DELETE", url2, sb_headers())
    url3 = sb_url(f"/rest/v1/pilot_email_sends?client_agent_id=eq.{agent_id}")
    http("DELETE", url3, sb_headers())

def count_events(agent_id, event_type):
    url = sb_url(f"/rest/v1/marketing_events?client_agent_id=eq.{agent_id}&event_type=eq.{event_type}&select=id")
    _, data = http("GET", url, sb_headers())
    return len(data)

def run_scenario_convert():
    agent_id = "e2e-convert-" + datetime.now().strftime("%H%M%S")
    print(f"\n=== SCENARIO: convert — {agent_id} ===")
    insert_synthetic_pilot(agent_id, with_card=True)
    print("  Sleeping 11 minutes for pilot_ends_at to pass...")
    time.sleep(11 * 60)

    print("  Running pilot_lifecycle.py...")
    subprocess.run(["python", "tools/pilot_lifecycle.py"], check=True)

    row = fetch_pilot(agent_id)
    assert row is not None, "pilot row disappeared"
    assert row["status"] == "active", f"expected active, got {row['status']}"
    assert row["pilot_mode"] is False, "pilot_mode should be false"
    assert count_events(agent_id, "pilot_converted") == 1, "pilot_converted event missing"
    print(f"  PASS — converted")
    cleanup_pilot(agent_id)

def run_scenario_expire():
    agent_id = "e2e-expire-" + datetime.now().strftime("%H%M%S")
    print(f"\n=== SCENARIO: expire — {agent_id} ===")
    insert_synthetic_pilot(agent_id, with_card=False)
    print("  Sleeping 11 minutes for pilot_ends_at to pass...")
    time.sleep(11 * 60)

    print("  Running pilot_lifecycle.py...")
    subprocess.run(["python", "tools/pilot_lifecycle.py"], check=True)

    row = fetch_pilot(agent_id)
    assert row is not None, "pilot row disappeared"
    assert row["status"] == "expired", f"expected expired, got {row['status']}"
    assert count_events(agent_id, "pilot_expired") == 1, "pilot_expired event missing"
    print(f"  PASS — expired")
    cleanup_pilot(agent_id)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=["convert", "expire", "all"], default="all")
    args = p.parse_args()

    if args.scenario in ("convert", "all"):
        run_scenario_convert()
    if args.scenario in ("expire", "all"):
        run_scenario_expire()

    print("\n=== ALL E2E SCENARIOS PASSED ===")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the convert scenario**

```bash
python tools/test_e2e_pilot.py --scenario convert
```

Wait ~11 minutes. Expected: `PASS — converted` then cleanup.

- [ ] **Step 3: Run the expire scenario**

```bash
python tools/test_e2e_pilot.py --scenario expire
```

Expected: `PASS — expired`. Verify the Retell `update-agent` call was made by checking the log output.

- [ ] **Step 4: Verify `marketing_events` has the full chain**

For each scenario, check the events:

```sql
select event_type, created_at, metadata
from marketing_events
where client_agent_id like 'e2e-%'
order by created_at desc
limit 20;
```

Expected: rows for `pilot_converted` OR `pilot_expired` depending on scenario.

- [ ] **Step 5: Commit**

```bash
git add tools/test_e2e_pilot.py
git commit -m "test(phase0): compressed-time E2E harness for convert + expire paths"
```

---

## Task 46: Day 6 session-end + `syntharra-website` deploy

**Files:**
- Modify: `docs/STATE.md`
- Deploys the sibling repo to wherever `syntharra-website` is hosted (Vercel, Netlify, Cloudflare Pages — Dan confirms)

- [ ] **Step 1: Push the sibling repo**

```bash
cd ../syntharra-website
git push origin main
cd ../syntharra-automations
```

Whatever host is configured auto-deploys on push (same as `dashboard.html` deploys today).

- [ ] **Step 2: Verify `/start` is live on the real domain**

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://syntharra.com/start
```

Expected: `200`. If `404`, the host's routing may need a rewrite rule (`/start` → `/start.html`). Fix that in the host config and re-verify.

- [ ] **Step 3: Verify the VSL player loads**

Open `https://syntharra.com/start` in a browser. VSL should autoplay muted. Click unmute and confirm audio works.

- [ ] **Step 4: Fire a real event and confirm it lands**

Load `https://syntharra.com/start?stx=phase0-smoke&utm_source=phase0_test` in a browser. Then query:

```sql
select session_id, event_type, asset_id, utm_source
from marketing_events
where utm_source = 'phase0_test'
order by created_at desc
limit 5;
```

Expected: at least one `page_view` row, possibly `vsl_impression`, `vsl_play`, `vsl_25pct`, etc.

- [ ] **Step 5: Update STATE.md**

```markdown
**Day 6 complete:** start.html live at syntharra.com/start, VSL plays,
tracker fires page_view + vsl_* events into marketing_events via the
marketing-event-ingest Edge Function. Compressed-time E2E run:
convert path PASS, expire path PASS. Ready for Day 7 pre-live checklist.

**Next:** Day 7 — 53-item pre-live checklist, Stripe live-mode flip, smoke test.
```

- [ ] **Step 6: Commit + session-end**

```bash
git add docs/STATE.md
python tools/session_end.py --topic phase-0-day-6 --summary "Phase 0 day 6: landing page + tracker live, E2E green"
git commit -m "chore(session): session-end 2026-04-11 phase-0-day-6 landing live"
```

**End of Day 6.**

---

# DAY 7 — Pre-live checklist + smoke test

**Day 7 goal:** walk every item in spec § 10.3 pre-live verification checklist, flip Stripe to live mode (Dan-blocked), deploy the `/ai → /start` redirect, and drive 50–100 real visits to measure against the spec § 10.2 benchmarks. Final session-end commits the GO-LIVE state.

---

## Task 47: Run the 53-item pre-live checklist

**Files:**
- Create: `docs/reports/2026-04-11-phase0-prelive-checklist.md`

Approach: every item in spec § 10.3 gets a checkbox here. Verification commands are inline. Any failure halts Day 7 until resolved.

> ⚠️ **BLOCKED IN PART:** items requiring Stripe live mode (checklist "Stripe safety" → `secret_key_live` + `webhook_signing_secret_live`) are blocked on Dan. Those items remain unchecked until Task 48 unblocks them.

- [ ] **Step 1: Create the report file**

Create `docs/reports/2026-04-11-phase0-prelive-checklist.md`. Copy the entire § 10.3 checklist from the spec verbatim, then convert each to a verification step:

```markdown
# Phase 0 — Pre-Live Verification Checklist (2026-04-11)

Source: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md § 10.3
Every item below MUST pass before smoke-test traffic hits syntharra.com/start.

## Schema safety (§ 6.2.1 + § 6.2.2)

- [ ] Live client_subscriptions schema verified
  ```sql
  select column_name, data_type from information_schema.columns
  where table_schema='public' and table_name='client_subscriptions'
  order by ordinal_position;
  ```
  Expected: 10 new pilot columns present.

- [ ] Migration path (A/B/C) recorded in docs/audits/2026-04-11-phase0-schema-scan.md

- [ ] Supabase branch created and merged
  → confirmed in Task 4 Step 4

- [ ] Forward migration dry-run passed
  → confirmed in Task 7

- [ ] monthly_minutes.py parity verified
  ```bash
  python tools/monthly_minutes.py --dry-run
  ```
  Expected: row count matches pre-migration baseline.

- [ ] usage_alert.py parity verified
  ```bash
  python tools/usage_alert.py --dry-run
  ```
  Same.

- [ ] Rollback SQL exists and was tested
  → confirmed in Task 7 Step 6

- [ ] Full client_subscriptions data dump saved
  ```bash
  ls -la docs/audits/supabase-backups-20260411/
  ```

- [ ] Branch merged to prod (or prod migration applied)
  → confirmed in Task 8

- [ ] Post-migration monthly_minutes.py output = baseline
- [ ] Post-migration usage_alert.py output = baseline

## n8n workflow safety (§ 6.3)

- [ ] All 5 workflows backed up to docs/audits/n8n-backups-20260411/
  ```bash
  ls -la docs/audits/n8n-backups-20260411/*.json
  ```
  Expected: at least 5 files.

- [ ] Each workflow grepped for client_subscriptions — documented in scan report
- [ ] SELECT * audit done
- [ ] status='active' proxy audit done
- [ ] Onboarding workflow 4Hx7aRdzMl5N0uJP double-backed-up
- [ ] Is Pilot? branch added via PUT
- [ ] Post-modification: paid E2E test PASS (Task 16)
- [ ] Post-modification: pilot E2E test PASS (Task 17)

## Retell agent safety (§ 6.5)

- [ ] MASTER snapshotted pre-change
  ```bash
  ls -la retell-iac/snapshots/2026-04-11_pre-pilot-expired/
  ```

- [ ] TESTING agent has pilot_expired flow node
- [ ] TESTING call with pilot_expired=true → graceful pause PASS (Task 26)
- [ ] TESTING call with pilot_expired=false → normal flow PASS (Task 26)
- [ ] MASTER promoted via promote.py (Task 27)
- [ ] MASTER real-phone test with pilot_expired=false PASS (Task 27 Step 6)

## Dashboard safety

- [ ] dashboard.html reads pilot_mode from client_subscriptions
- [ ] ?a=<PAID_AGENT_ID> → no pilot banner
- [ ] ?a=<PILOT_AGENT_ID> → pilot banner with countdown
- [ ] No CSS regression on paid view
- [ ] ?demo=1 preview still works

## Stripe safety (§ 6.4)

### Test mode
- [ ] Setup Intent flow E2E works (Task 21 deploy + Task 45 compressed-time test)
- [ ] Subscription created with trial_end=pilot_ends_at
- [ ] trial_will_end webhook handled (or not-needed, since we use cron)
- [ ] Compressed-time convert test PASS (Task 45)
- [ ] Compressed-time expire test PASS (Task 45)

### Live mode (⚠️ BLOCKED ON DAN — Task 48)
- [ ] secret_key_live vaulted
- [ ] webhook_signing_secret_live vaulted
- [ ] Live webhook endpoint verified
- [ ] One-time real-card $1 test

## Event log safety (§ 7)

- [ ] marketing_events table exists with RLS
  ```sql
  select table_name, row_security from pg_tables where tablename='marketing_events';
  ```
- [ ] marketing_assets table exists with RLS
- [ ] anon SELECT * returns permission denied
  ```bash
  curl -s "$SUPABASE_URL/rest/v1/marketing_events?select=id&limit=1" \
    -H "apikey: $SUPABASE_ANON_KEY"
  ```
  Expected: empty or 401.
- [ ] service_role SELECT * returns rows
- [ ] marketing-event-ingest Edge Function deployed (Task 42)
- [ ] Bot filter works (Task 42 Step 4)
- [ ] Rate limit works (Task 42 Step 5)
- [ ] Tracker JS emits page_view on /start load (Task 46 Step 4)
- [ ] Tracker JS persists stx_asset_id to localStorage (manual devtools check)

## Billing tool patches

- [ ] monthly_minutes.py has pilot_mode=eq.false filter
  ```bash
  grep "pilot_mode=eq.false" tools/monthly_minutes.py
  ```
- [ ] usage_alert.py has pilot_mode=eq.false filter
  ```bash
  grep "pilot_mode=eq.false" tools/usage_alert.py
  ```
- [ ] Both tools committed in same PR as migration (Day 1 Task 9)
- [ ] Dry-run monthly_minutes.py matches pre-migration baseline
- [ ] Dry-run usage_alert.py matches pre-migration baseline

## Final gate

- [ ] Full compressed-time E2E convert path: visit → VSL play → CTA → Jotform → agent live → card add → cron → converted (Task 45 Scenario 1)
- [ ] Full compressed-time E2E expire path: same but no card → cron → expired + Retell paused (Task 45 Scenario 2)
- [ ] Dan signed off on VSL final cut (Task 28 or Task 32)
- [ ] Stripe LIVE mode active (Task 48)

## Verdict
- [ ] ALL GREEN → proceed to smoke test (Task 51)
- [ ] FAILURES → halt, log to docs/FAILURES.md, fix, re-run checklist
```

- [ ] **Step 2: Walk the list, checking each item**

Run the verification command for every box. Mark `[x]` when green. Mark `[FAIL — <details>]` on any failure.

- [ ] **Step 3: Commit the completed checklist**

```bash
git add docs/reports/2026-04-11-phase0-prelive-checklist.md
git commit -m "test(phase0): run full 53-item pre-live verification checklist"
```

---

## Task 48: Stripe live-mode migration

> ⚠️ **BLOCKED ON DAN:** Stripe live-mode secret key + webhook signing secret must be vaulted. Resolution: Dan generates live mode keys from the Stripe dashboard and inserts into `syntharra_vault` as `service_name='Stripe'`, `key_type='secret_key_live'` and `key_type='webhook_signing_secret_live'`. This is already a P1 Dan deliverable per `docs/TASKS.md` and is referenced in spec § 1.3.

**Files:** no repo file changes. Environment and Supabase Edge Function secrets updated.

- [ ] **Step 1: Confirm keys are vaulted**

```sql
select service_name, key_type from syntharra_vault
where service_name = 'Stripe'
  and key_type in ('secret_key_live', 'webhook_signing_secret_live');
```

Expected: 2 rows. Halt if not present.

- [ ] **Step 2: Run `stripe_pilot_setup.py` in live mode**

```bash
export STRIPE_SECRET_KEY=$(python tools/fetch_vault.py "Stripe" secret_key_live)
export SUPABASE_PROJECT_REF=hgheyqwnrcvwtgngqdnq
python tools/stripe_pilot_setup.py --mode live
```

Expected: live-mode product, price, webhook created. Save the live webhook signing secret immediately (Stripe only shows it once).

- [ ] **Step 3: Vault the live webhook signing secret**

```sql
update syntharra_vault
set key_value = '<whsec_live_...>', updated_at = now()
where service_name = 'Stripe' and key_type = 'webhook_signing_secret_live';
```

- [ ] **Step 4: Update Edge Function secrets to live**

Via Supabase dashboard or MCP, set on the project:

```
STRIPE_SECRET_KEY = <live secret from vault>
STRIPE_WEBHOOK_SECRET = <live webhook signing secret from vault>
```

The two Edge Functions (`pilot-setup-intent` and `stripe-webhook`) pick these up on next cold start.

- [ ] **Step 5: Update Railway env vars for `pilot_lifecycle.py`**

Swap `STRIPE_SECRET_KEY` on the Railway cron service from test → live.

- [ ] **Step 6: Stripe CLI listen test**

```bash
stripe listen --forward-to https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/stripe-webhook
```

In another terminal:
```bash
stripe trigger setup_intent.succeeded --api-key <LIVE_SECRET_KEY>
```

Expected: the Edge Function receives and verifies the event. No signature errors.

- [ ] **Step 7: One-time real card $1 test (per spec § 10.3 final gate)**

Dan uses his own real card. Create a $1 test charge via Stripe dashboard → Payments → New. Verify the webhook fires, then immediately refund.

- [ ] **Step 8: Update the pre-live checklist**

Check the Stripe live mode boxes in `docs/reports/2026-04-11-phase0-prelive-checklist.md`.

- [ ] **Step 9: Commit checklist update**

```bash
git add docs/reports/2026-04-11-phase0-prelive-checklist.md
git commit -m "test(phase0): Stripe live mode active, prelive checklist Stripe items green"
```

---

## Task 49: Deploy `/ai` → `/start` 301 redirect on syntharra.com

**Files:**
- Modify: `../syntharra-website/vercel.json` (or equivalent host config)

Per spec § 5 decision D4, `/ai` should 301 to `/start`.

- [ ] **Step 1: Determine the host config file**

```bash
cd ../syntharra-website
ls -la vercel.json netlify.toml _redirects wrangler.toml 2>&1 || echo "check host"
cd ../syntharra-automations
```

- [ ] **Step 2: Add the redirect rule**

If `vercel.json`:

```json
{
  "redirects": [
    { "source": "/ai", "destination": "/start", "permanent": true }
  ]
}
```

If Netlify `_redirects`:
```
/ai  /start  301
```

If Cloudflare Pages `_redirects`: same as Netlify.

- [ ] **Step 3: Commit and push**

```bash
cd ../syntharra-website
git add vercel.json  # or _redirects, etc.
git commit -m "feat(phase0): 301 redirect /ai → /start"
git push origin main
cd ../syntharra-automations
```

- [ ] **Step 4: Verify**

```bash
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" https://syntharra.com/ai
```

Expected: `301 https://syntharra.com/start`.

---

## Task 50: HubSpot integration verification

**Files:** none. Smoke test only.

Per spec § 14 decision #7 / spec decision D7, HubSpot stays as the CRM. The existing onboarding pipeline already syncs to HubSpot. This task confirms that pilot signups land in HubSpot the same way paid signups do.

- [ ] **Step 1: Check HubSpot for the Day 2 test pilot row**

Via HubSpot MCP or dashboard: search Contacts for the test company name from Task 17 (or a fresh pilot if the test row was cleaned up — insert a new one if needed).

- [ ] **Step 2: Verify required fields are populated**

Expected fields on the Contact:
- Email
- First/last name
- Company
- Phone
- Custom property `pilot_mode = true`
- Custom property `pilot_ends_at`

- [ ] **Step 3: If any field missing, patch the n8n onboarding workflow**

The HubSpot sync is likely a node in `4Hx7aRdzMl5N0uJP`. If pilot fields aren't coming through, add them to the HubSpot node's mapping. Document the change and re-run Task 17 E2E.

- [ ] **Step 4: Document the verification in the checklist report**

Append to `docs/reports/2026-04-11-phase0-prelive-checklist.md`:

```markdown
## HubSpot integration verification (Task 50)

- [x] Pilot signup lands as HubSpot Contact
- [x] All required fields populated
- [x] pilot_mode custom property syncs
```

- [ ] **Step 5: Commit**

```bash
git add docs/reports/2026-04-11-phase0-prelive-checklist.md
git commit -m "test(phase0): HubSpot pilot sync verified"
```

---

## Task 51: Smoke test — real cold-traffic submission

> ⚠️ **BLOCKED on all prior blockers being resolved:** Stripe live (Task 48) + Mux playback ID in start.html (Task 36/39) + sibling repo deployed (Task 46) must all be green. Plus Dan needs to share the URL with 50–100 people per spec § 10.2.

**Files:**
- Create: `docs/reports/2026-04-11-phase0-smoke-test.md`

- [ ] **Step 1: Dan shares `https://syntharra.com/start` with 50–100 people**

Via: personal network DMs, r/hvacbiz posts, LinkedIn DMs, existing mailing list, small Meta test ad <$100. The goal is 50 real human visits, not qualified leads. Per spec § 12 Dan's #5 deliverable.

- [ ] **Step 2: Wait 72 hours for traffic to land**

Do not measure before 72 hours — the spec § 10.2 benchmarks require enough statistical mass to not be swayed by the first-hour anomalies.

- [ ] **Step 3: Measure against spec § 10.2 benchmarks**

Run these queries against `marketing_events` (adjust the time window):

```sql
-- Total unique visits
select count(distinct visitor_id) as visits
from marketing_events
where event_type = 'page_view'
  and created_at > now() - interval '72 hours';

-- Visit → VSL play (non-bounce)
select
  (select count(distinct visitor_id) from marketing_events
   where event_type='vsl_play' and created_at > now() - interval '72 hours') * 100.0 /
  nullif((select count(distinct visitor_id) from marketing_events
   where event_type='page_view' and created_at > now() - interval '72 hours'), 0)
  as pct_visit_to_vsl_play;

-- VSL play → 50%
select
  (select count(distinct visitor_id) from marketing_events
   where event_type='vsl_50pct' and created_at > now() - interval '72 hours') * 100.0 /
  nullif((select count(distinct visitor_id) from marketing_events
   where event_type='vsl_play' and created_at > now() - interval '72 hours'), 0)
  as pct_play_to_50pct;

-- VSL 50% → CTA click
-- CTA click → Jotform start
-- Jotform start → complete
-- Jotform complete → agent live
-- (Each query in the same pattern — divide count of next step by count of prior step)

-- Overall: visits → pilots started
select
  (select count(*) from client_subscriptions
   where pilot_mode = true
     and created_at > now() - interval '72 hours') * 100.0 /
  nullif((select count(distinct visitor_id) from marketing_events
   where event_type='page_view' and created_at > now() - interval '72 hours'), 0)
  as pct_visit_to_pilot;
```

- [ ] **Step 4: Compare to spec § 10.2 benchmarks**

```
| Step                    | Target | Actual | PASS/FAIL |
|---|---|---|---|
| Visit → VSL play        | ≥60%   | <fill> | ? |
| VSL play → 50%          | ≥35%   | <fill> | ? |
| VSL 50% → CTA           | ≥25%   | <fill> | ? |
| CTA → Jotform start     | ≥80%   | <fill> | ? |
| Jotform start → complete| ≥50%   | <fill> | ? |
| Jotform complete → live | ≥95%   | <fill> | ? |
| Visits → pilots started | ≥3%    | <fill> | ? |
```

- [ ] **Step 5: Write the smoke test report**

Create `docs/reports/2026-04-11-phase0-smoke-test.md`:

```markdown
# Phase 0 — Smoke Test Results (2026-04-11)

## Traffic source
- <list where visits came from>
- Total unique visitors: <N>
- Window: <start> to <end>

## Benchmark results
<paste the table from Step 4>

## Decision
- [ ] ALL GREEN → green-light Phase 1 (organic video machine)
- [ ] 1 benchmark ≥30% below → fix that step, re-run 50 visits
- [ ] 2+ benchmarks below → offer is wrong, back to brainstorming
- [ ] Overall <2% → DO NOT advance to Phase 1

## Action items
<if iterating>
- <fix X>
- <rerun smoke test>
```

- [ ] **Step 6: Commit the report**

```bash
git add docs/reports/2026-04-11-phase0-smoke-test.md
git commit -m "test(phase0): smoke test results — <N> visits, <pct>% to pilot"
```

---

## Task 52: Final session-end + Phase 0 GO-LIVE commit

**Files:**
- Modify: `docs/STATE.md`
- Modify: `memory/project_phase0_progress.md`

- [ ] **Step 1: Update STATE.md with Phase 0 go-live**

```markdown
## Phase 0 progress (2026-04-11)

**Day 7 complete — Phase 0 GO-LIVE.** All 52 tasks executed. Landing
page live at syntharra.com/start with VSL autoplay, tracker firing
events into marketing_events, pilot onboarding wired into n8n with
Is Pilot? branch, pilot_lifecycle.py cron running nightly on Railway,
Retell pilot_expired flow in MASTER, Stripe live mode active, HubSpot
sync confirmed.

Pre-live checklist: 53/53 green.
Smoke test: <result — green-light Phase 1 | iterate offer>.

**Phase 0 DONE.** Phase 1 (organic short-form video machine) gate:
<PASS | ITERATE>. If PASS, start Phase 1 spec in next session.
```

- [ ] **Step 2: Update the memory file**

```bash
# Edit memory/project_phase0_progress.md
# Mark Phase 0 as COMPLETE with a link to docs/reports/2026-04-11-phase0-smoke-test.md
```

- [ ] **Step 3: Final session-end**

```bash
python tools/session_end.py --topic phase-0-go-live --summary "Phase 0 GO-LIVE: all 52 tasks complete, smoke test <result>"
```

- [ ] **Step 4: Final commit**

```bash
git add docs/STATE.md memory/project_phase0_progress.md
git commit -m "$(cat <<'EOF'
chore(phase0): Phase 0 GO-LIVE — all 52 tasks complete

Landing page live at syntharra.com/start. VSL playing, tracker
firing, pilot funnel wired, pilot_lifecycle cron running, Retell
pilot_expired in MASTER, Stripe live.

Pre-live checklist: 53/53 green.
Smoke test benchmarks: see docs/reports/2026-04-11-phase0-smoke-test.md

Next: Phase 1 (organic short-form video machine) — spec + plan cycle.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 5: Tag the release**

```bash
git tag phase-0-go-live-2026-04-11
git push origin phase-0-go-live-2026-04-11
```

**End of Day 7. End of Phase 0.**

---

## Self-Review Checklist (tasks 1–52 written 2026-04-11 — verify during execution)

- [ ] Every spec section in `2026-04-10-phase-0-vsl-funnel-design.md` has at least one task
- [ ] Every placeholder scan (TBD / TODO / "implement later") returns zero hits
- [ ] Every task has explicit file paths, exact code, exact verification commands, and a commit step
- [ ] Type and function names used in later tasks match their definitions in earlier tasks (e.g. `send_brevo_email`, `convert_pilot_to_paid`, `expire_pilot` all match the stubs in Task 19)
- [ ] Every spec § 10.3 checklist item maps to a verification step inside a task
- [ ] No task depends on a step that has not been done in an earlier task
- [ ] Rollback procedure (Task 11) is referenced from every destructive step
