# State — Syntharra Automations

_Last updated: 2026-04-11_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
eee258c feat(phase0): Day 4 â€” Retell pilot_expired component + cold outreach engine + community post drafts

## Go-live checklist
see docs/GO-LIVE.md

---

## Product decision (2026-04-09)

Single product: **HVAC Standard at $697/mo**. Premium tier retired. One agent, one onboarding flow, one price.
Repo stripped to lean core. retell-iac is Standard-only.

## Data-ownership principle (2026-04-09)

**Retell owns call data. Supabase owns client + billing state.** No per-call storage in Supabase. The dashboard reads Retell directly via `list-calls`; monthly billing reads Retell directly at invoice time. Supabase holds only: client configs, subscriptions, billing cycles, overage charges, website leads, and a tiny immutable `monthly_billing_snapshot` rollup for dispute defense against Retell's retention window.

---

## What's live in production

- **HVAC Standard MASTER** — `agent_b46aef9fd327ec60c657b7a30a` / `conversation_flow_19684fe03b61`, phone `+18129944371` (⚠️ bind in Retell dashboard). Re-registered 2026-04-09 from `retell-iac/snapshots/2026-04-09_testing-autolayout-fixed/` after Dan deleted both agents. 19 nodes, modern code-node arch, published. Clone source for Standard clients.
- **HVAC Standard TESTING agent** — `agent_41e9758d8dc956843110e29a25` / `conversation_flow_bc8bb3565dbf`. Re-registered 2026-04-09 from same snapshot. Authoring surface — edit here, promote to MASTER via `retell-iac/scripts/promote.py`.
- **`retell-iac/components/` is current.** Regenerated 2026-04-09 from the live snapshot via `scripts/split_snapshot.py`. 19 flat component files, new `flows/hvac-standard.template.json`, new `manifests/hvac-standard.yaml`. `build_agent.py` output is byte-identical to the live MASTER flow. Legacy subagent files archived at `components.legacy-subagent-20260409/`, `flows/hvac-standard.template.legacy-subagent-20260409.json`, `manifests/hvac-standard.legacy-subagent-20260409.yaml`.
- **n8n onboarding workflow** — Standard `4Hx7aRdzMl5N0uJP`. Includes `slack_webhook_url` mapping from Jotform field `q76_slackIncoming` (2026-04-09) + Demo/Live agent naming patch at L25/L683 of `Build Retell Prompt` (2026-04-09).
- **HVAC Call Processor — lean fan-out** — `Kg576YtPM9yEacKn`. Rewritten 2026-04-09 as 8-node fan-out (webhook → filter → lookup → build payload → email/slack/sms). Zero Supabase writes. Triggers on `is_lead OR urgency=emergency`. Brevo key inlined from vault. SMS stub marked `TELNYX-TODO`. Generator: [tools/build_call_processor_workflow.py](../tools/build_call_processor_workflow.py).
- **Weekly client report** — [tools/weekly_client_report.py](../tools/weekly_client_report.py). Runs via external cron (`TZ=America/New_York python tools/weekly_client_report.py --tz America/New_York`) Sunday 18:00 local per timezone bucket. Pulls calls from Retell `list-calls`, sends branded email via Brevo + optional Slack to every client in that TZ. Not yet deployed on a schedule (1 client pre-launch); deploy cron once a second client lands.
- **Monthly minutes billing** — [tools/monthly_minutes.py](../tools/monthly_minutes.py). Replaces broken n8n workflow `z1DNTjvTDAkExsX8` (now archived). Pulls from Retell `list-calls`, computes overage, charges Stripe, writes `monthly_billing_snapshot`, sends Brevo usage email. Run: `python tools/monthly_minutes.py` (defaults to prev month). Not yet on cron — deploy 1st-of-month once live clients exist. `z1DNTjvTDAkExsX8` deactivated + renamed `[ARCHIVED-2026-04-09]` 2026-04-09 Pass 2. ⚠️ Does NOT include 80%/100% mid-month usage alerts — `Usage Alert Monitor` (`Wa3pHRMwSjbZHqMC`) still broken (queries dropped `hvac_call_log`); needs `tools/usage_alert.py` migration.
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

## 2026-04-09 session — 3-tier pricing system

Full pricing overhaul shipped. 3 tiers: Starter ($397/mo, 350 min, $0.25/min), Professional ($697/mo, 700 min, $0.18/min — hero), Business ($1,097/mo, 1,400 min, $0.12/min). Annual = 2 months free. Flat $997 Activation Fee all tiers.

**What shipped:**
- **`Syntharra/syntharra-checkout` `public/index.html`** — full 3-tier checkout page (3 cards + Enterprise dark section, monthly/annual toggle, activation fee on all cards, overage rates per card). GitHub SHA `4249ba66`.
- **Stripe test-mode products/prices** — 3 products (Starter/Professional/Business) + Activation Fee product, 6 subscription prices + 1 one-time price. All IDs stored in `syntharra_vault` (`service_name='Stripe'`, key_type prefixed `prod_` / `price_`).
- **`client_subscriptions` schema** — added `tier` (text, default 'professional'), `overage_rate` (numeric, default 0.18), `billing_cycle` (text, default 'monthly'), `stripe_price_id` (text).
- **n8n Stripe webhook `xKD3ny6kfHL0HHXq`** — `handle-checkout-completed` node now maps all 6 price IDs → tier config, saves to `stripe_payment_data`, sends tier-aware welcome email (Brevo), Jotform URL: `form.jotform.com/260795139953066?tier={tier}`.
- **n8n Onboarding workflow `4Hx7aRdzMl5N0uJP`** — `reconcile_jotform_stripe` node fetches tier/overage_rate/minutes from `stripe_payment_data` by email, then PATCHes `client_subscriptions` with tier data. Defaults to Professional if no Stripe record found.
- **`tools/usage_alert.py`** — overage rate now dynamic per subscription (was hardcoded 0.18). Reads `tier,overage_rate` from `client_subscriptions`.
- **`shared/email-templates/youre-live-template.js`** — tier-aware "Your Plan" card showing minutes + overage rate. Conditional WhatsApp support section for Professional/Business (gated on `whatsapp_number` input being set).

**⚠️ All Stripe price IDs are TEST MODE.** Needs live IDs before go-live. See TASKS.md.

**WhatsApp support approach decided:** Single "You're Live" email with conditional WhatsApp section (already wired). When Dan provides a dedicated Telnyx number verified on WhatsApp Business: (1) store in `syntharra_vault` as `service_name='WhatsApp', key_type='support_number'`, (2) update the n8n onboarding node that calls the "You're Live" template to fetch the number from vault and pass it as `whatsapp_number` for Professional/Business tiers only.

## Next session — pick up here
- Day 5+: Build SEO comparison pages 2-5 (Smith.AI, Answering Service Care, Abby Connect, Best of HVAC services)
- Rebrand 9 Brevo pilot templates from dark to light theme + re-upload (idempotent script needs UPDATE-mode added)
- Add Hunter.io free tier to find_email_from_website.py for higher email hit rate
- Affiliate outreach script generator targeting HVAC YouTubers (Bryan Orr, AC Service Tech, etc.)
- Day 6 Railway deploy of pilot_lifecycle.py cron
- DAN unblockers (still): Telnyx vault keys (waiting on business number), Stripe secret_key_live, film founder VSL, register stripe-webhook URL in Stripe dashboard + vault webhook_signing_secret, rotate Mux secret (security)
- DAN test action: build TESTING agent from updated retell-iac, verify pilot_expired branch fires when {{pilot_expired}}=true, then promote.py if clean

## Phase 0 progress (marketing build)

- **Spec:** `docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md` — COMPLETE (1,182 lines, 3 commits). Covers VSL + pilot funnel + measurement spine.
- **Plan:** `docs/superpowers/plans/2026-04-11-phase-0-vsl-funnel-implementation.md` — PARTIAL (~1,100 lines). Day 1 (Tasks 1-12) + Day 2 (Tasks 13-18) + Day 3 Task 19 skeleton written. Tasks 20-52 (Day 3 remainder + Days 4-7) pending.
- **Resume pointer:** `memory/project_phase0_progress.md` (authoritative progress tracker, check first when resuming).

### Day 1 — COMPLETE (2026-04-11)

Schema migration `20260411_phase0_pilot_schema` applied to prod:
- 10 pilot/attribution columns added to `client_subscriptions`
- 3 new tables: `marketing_events`, `marketing_assets`, `pilot_email_sends` (all RLS-enabled, service-role-only)
- `client_subscriptions_status_check` extended to allow `'pilot'` + `'expired'` (strict superset)
- `tools/monthly_minutes.py` + `tools/usage_alert.py` patched with `pilot_mode=eq.false` defensive filter
- Billing tool output parity verified byte-identical pre/post migration
- Existing `client_subscriptions` row (Dan's test agent, `status='active'`) unchanged
- Rollback SQL ready at `supabase/migrations/20260411_phase0_pilot_schema_rollback.sql`
- Pre-migration backups: `docs/audits/supabase-backups-20260411/` + `docs/audits/n8n-backups-20260411/`
- Scan report: `docs/audits/2026-04-11-phase0-schema-scan.md`

### Day 2 — COMPLETE (2026-04-11) — pilot infrastructure dark-launched

Pilot signup machine is **live and ready to receive traffic**, but won't get any until Days 5-7 unblock the landing page + VSL. Per-pilot cost in dark-launched state: **~$0** (Telnyx graceful skip + cron not yet deployed + Brevo templates not yet uploaded).

- **Jotform pilot fork `261002359315044`** created from paid form `260795139953066`. Title "Start your free 14-day Syntharra pilot". 7 hidden tracking fields (`stx_asset_id`, `utm_source/medium/campaign/content/term`, `pilot_mode=true`). Webhook inherited correctly — same `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding` URL as paid form. Registered in `docs/REFERENCE.md` Jotform Forms section.
- **n8n workflow `4Hx7aRdzMl5N0uJP` patched** in-place (deviation from plan: surgical Reconcile Code-node modification, NOT the proposed IF+Set node insertion — see commit `ba0b8f1` for the reasoning). The `Reconcile: Check Stripe Payment` jsCode now has a Phase 0 pilot block at the top that reaches back to the JotForm Webhook Trigger to read `pilot_mode`, and on `pilot_mode='true'` writes a `client_subscriptions` row with `status='pilot' + pilot_started_at + pilot_ends_at + pilot_minutes_allotted=200 + first/last_touch_asset_id + first/last_touch_utm` and returns early (skipping the 60s Stripe wait). Paid path is byte-identical below the pilot block (verified post-patch: 84/84 lines match, only 1 of 32 nodes differs).
- **Synthetic pilot row test** (no real Retell/Telnyx/Brevo cost): inserted via SQL with the same shape the pilot block writes, confirmed (a) billing-cron defensive filter excludes pilots (0 rows), (b) pilot lifecycle query includes pilots (1 row), (c) `status='pilot'` passes the CHECK constraint, (d) timestamps consistent. Synthetic row deleted. `client_subscriptions` is back to 1 row (Dan's test agent).
- **Track C drafts committed (`e52ade2`):** `tools/pilot_lifecycle.py` (611 lines, full state machine, **14/14 unit tests passing**), `tools/test_pilot_lifecycle.py`, `tools/stripe_pilot_setup.py` (test mode, idempotent), `tools/test_e2e_pilot.py` (programmatic webhook submitter for Day 7 smoke test), `tools/upload_brevo_templates.py`, 9 Brevo email HTML templates in `shared/email-templates/pilot-*.html` (Syntharra dark theme, 600px Gmail-compat layout). All Python files syntax-clean. `pilot_lifecycle.py` SELECT was patched to drop 3 columns that don't exist on `client_subscriptions` (they live on `hvac_standard_agent`) and to use `payment_method_added_at IS NOT NULL` instead of the imaginary `stripe_setup_intent_succeeded` column.
- **New tools committed (`ba0b8f1`):** `tools/build_pilot_jotform.py`, `tools/patch_pilot_jotform_hidden_fields.py`, `tools/patch_onboarding_workflow_add_pilot_branch.py` (idempotent via `// === Phase 0 pilot block === //` marker), `tools/fetch_vault.py` (vault helper).
- **Backups (gitignored):** `docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json` (290KB, sha256-verified pre-apply), `-pre-apply-recheck.json`, `-post-pilot-branch.json` for rollback if ever needed.

### Day 3 — COMPLETE (2026-04-11) — pilot funnel infrastructure end-to-end

Day 3 closed the loop on the dark-launched pilot funnel. Every system in the lead pathway is now wired, tested, and waiting on the Dan-blockers (Telnyx, VSL filming, Stripe live).

- **9 Brevo pilot email templates uploaded** via `tools/upload_brevo_templates.py` (idempotent, find-by-name → existing ID). IDs 1-9, registered in `docs/REFERENCE.md` Brevo Templates section, inlined into `tools/pilot_lifecycle.py` `BREVO_TEMPLATE_IDS`. Sender = `daniel@syntharra.com` (only verified sender on Brevo). ⚠ Followup: rebrand from dark-theme to light-theme to match brand rules; `founders@`/`support@` need verification in Brevo dashboard.
- **Stripe TEST mode pilot products created** via `tools/stripe_pilot_setup.py` (idempotent via metadata markers). Product `prod_UJb4pQDwyQ7lgW`, price `price_1TKxruECS71NQsk8yspZnj2B` ($697/mo recurring). Inlined into `pilot_lifecycle.py` `STRIPE_HVAC_STANDARD_PRICE_ID`. Replace with live equivalents when Dan vaults the live key.
- **`Send Welcome Email` n8n node patched** via the second n8n patcher (`tools/patch_onboarding_workflow_pilot_welcome.py`). Pilot block at the top of jsCode reaches back to JotForm Webhook Trigger, on `pilot_mode='true'` sends Brevo template id 7 (pilot-welcome) immediately with pilot params, returns. Paid path 143/143 lines byte-identical. **Day 2 Reconcile pilot block still intact** (verified — no clobber). Workflow `4Hx7aRdzMl5N0uJP` now has TWO independent pilot blocks (Reconcile + Send Welcome Email), both surgical, both with markers for idempotency.
- **Three Supabase Edge Functions deployed** to project `hgheyqwnrcvwtgngqdnq`. Source committed under `supabase/functions/`:
  1. `marketing-event-ingest` v2 — public POST endpoint for browser tracker, bot filter + 15-event-type whitelist, INSERTs into `marketing_events`. Smoke test passed (POST 200, row inserted with all fields, deleted). v1 had a schema bug (assumed `props` and `occurred_at` columns that don't exist on the live table); v2 corrected to use `metadata` jsonb + `session_id` NOT NULL fallback.
  2. `pilot-setup-intent` v1 — POST endpoint that takes `{ agent_id }`, finds the matching pilot, creates/reuses Stripe customer, creates Setup Intent, returns `client_secret`. Reads Stripe key from vault (prefers `secret_key_live`, falls back to `secret_key_test`) — auto-promotes to live when Dan vaults the live key, no redeploy needed.
  3. `stripe-webhook` v1 — handles `setup_intent.succeeded` → marks `payment_method_added_at` → emits marketing event → sends Brevo template 1 (pilot-card-added). HMAC verification via vault `webhook_signing_secret` (currently absent — verification SKIPPED with warning, acceptable in dark-launch). ⚠ Followup: register webhook URL in Stripe dashboard, vault the signing secret.
- **Mux credentials VAULTED 2026-04-11** as `service_name='Mux'`, `key_type='token_id'` + `key_type='secret_key'`. Day 5 Task 35 (Mux upload) is unblocked once VSL is filmed. Dan should rotate the secret in Mux dashboard ASAP since the original was sent in chat (leak vector exists in conversation log).
- **Phase 0 landing page scaffolded in syntharra-website sibling repo** (commit `f9cddc1`, NOT pushed). `start.html` (227 lines, 1 style block, light-theme Syntharra chrome, hero with the r/HVAC quote, VSL placeholder div, 200-min/14-day pilot offer card, 4-question FAQ, final CTA pointing to pilot Jotform `261002359315044?pilot_mode=true`) + `marketing-tracker.js` (234 lines, vanilla, sendBeacon-preferred, fires page_view/cta_click/scroll_depth/vsl_*_pct events to the marketing-event-ingest Edge Function). Pushing requires Mux playback ID swap-in OR explicit dark-launch decision.
- **`docs/RULES.md` #42 added:** `pause_retell_agent` must NEVER target MASTER. Track B's safety rail captured as a standing rule.

### Day 4 — COMPLETE (2026-04-11) — Retell pilot_expired drafted + cold outreach engine + 1st SEO comparison page LIVE

Day 4 went hard. Drafted the Retell pilot_expired flow node, shipped a complete $0 cold outreach toolchain with end-to-end smoke test, wrote a comprehensive cold outreach playbook, drafted 5 community posts for Reddit/FB, and pushed the first SEO comparison page (`vs-ruby-receptionists.html`) live to syntharra.com. **The lead-generation machine is now operational.**

- **Retell `pilot_expired` flow component drafted** (NOT promoted to MASTER — Dan's gate). New `retell-iac/components/pilot_expired_node.json` with the apologetic pilot-ended message + visit-to-reactivate CTA. Added to `retell-iac/manifests/hvac-standard.yaml`. Flow template patched: new `node-pilot-expired` (now 20 nodes total), single edge to `node-end-call`, two new conditional edges PREPENDED to `node-greeting` (equation-type primary + prompt-type fallback). Build verified with `retell-iac/scripts/build_agent.py` — 20 nodes, body inlined, greeting edges in correct order. ⚠ Dan must build TESTING + verify the pilot_expired branch fires before running `promote.py` (equation syntax is speculative — fallback prompt-type edge exists as belt-and-suspenders).
- **Cold outreach engine ($0 stack)** — 4 new tools, all stdlib, all idempotent, end-to-end smoke-tested on Las Vegas leads:
  - `tools/scrape_hvac_directory.py` — scrapes US HVAC contractors by city via OpenStreetMap Overpass (multi-mirror retry) with Nominatim fallback and Yelp Fusion as optional. Hardcoded city center bboxes for 30 priority US cities. Smoke test: Las Vegas → 6 OSM businesses in 3 seconds.
  - `tools/find_email_from_website.py` — visits each business website + common contact paths, scrapes emails, filters junk. Smoke test: 3/6 emails found (50% hit rate, industry-normal for SMB).
  - `tools/build_cold_outreach.py` — generates personalized 3-touch sequence per lead. Subject line variants, NOT_A_NAME filter for first-name extraction, CAN-SPAM compliant footer.
  - `tools/send_cold_outreach.py` — configurable backend (print/brevo/mailgun) with hard safety rails. Defaults to print mode. Real send REQUIRES `--i-know-this-is-real`. Tracks state in `leads/.send_state.json` (gitignored).
- **`docs/cold_outreach_strategy.md`** — comprehensive playbook: target persona, 20 priority US cities ranked by HVAC after-hours emergency density, full toolchain command flow, sequence design, expected metrics, CAN-SPAM compliance, Brevo TOS warning, Mailgun/Smartlead scale-up path, 5 SEO comparison pages prioritized, paid ads + affiliate deferred to Phase 1, combined month-1/3/6 projections. **Realistic month-1: 6-17 paying customers from cold email + SEO + community alone (assuming Telnyx + Stripe live land within first week).**
- **`docs/community_post_drafts.md`** — 5 ready-to-post drafts for r/HVAC, r/HVACTech, r/smallbusiness, FB "HVAC Owners & Operators". Founder-direct voice, no marketing speak, link goes in follow-up comment after upvotes (Reddit anti-spam compliance). Posting checklist + what-works principles included. Designed for Dan to copy-paste manually.
- **`vs-ruby-receptionists.html` LIVE on syntharra.com** (309 lines, 1 style block, light-theme chrome). Comparison table, 2 a.m. test scenario, honest "what Ruby is better at" section, 5-question FAQ, schema.org FAQPage markup. CTA → `/start` with `utm_source=vs-ruby` for attribution.
- **`leads/` and `build/` added to .gitignore** — real business data and regenerable build artifacts never committed.

**Next session — Day 5+ work** (when Dan unblockers land OR independent improvements):
- Build comparison pages 2-5 (Smith.AI, Answering Service Care, Abby Connect, Best of Best HVAC answering services)
- Rebrand 9 Brevo pilot templates from dark theme to light theme + re-upload
- Add Hunter.io free integration to `find_email_from_website.py` for higher email enrichment hit rate
- Wire inbox monitoring webhook so cold sender state file auto-updates on STOP replies
- Affiliate outreach script generator (target HVAC YouTubers: Bryan Orr / HVAC School, AC Service Tech, Word of Advice TV)
- Day 5 VSL pipeline (when filming + Mux upload happen)
- Day 6 Railway deploy of `pilot_lifecycle.py` cron
- Day 7 pre-live checklist + first cold-traffic smoke test (when Telnyx + Stripe live land)

## What's in flight

- **Phase 0 marketing build** — Day 1 + Day 2 LIVE in prod. Plan Days 3-7 still being expanded (Track B). Day 3 cron + Brevo upload + Day 3 followup (`Send Welcome Email` node patch) is the next executable batch. Days 5-7 are blocked on Dan unblockers below.
- **Stripe live mode** — test-mode only. Dan to provide live secret key. P1 blocker before first paying client AND before Phase 0 Day 7 smoke test.
- **Telnyx phone chain** — built, blocked on Dan vaulting `service_name='Telnyx'` `key_type='api_key'` + `key_type='retell_sip_connection_id'`. **Without these, Phase 0 pilot signups will create Retell agents but provision no phone number — the AI receptionist exists but can't actually receive calls.** Top priority unblocker.
- **Mux account + creds** — ✅ **VAULTED 2026-04-11** as `service_name='Mux'`, `key_type='token_id'` + `key_type='secret_key'` (Mux API access token pair). Day 5 Task 35 (Mux upload) is unblocked once the VSL is filmed. **Dan should rotate the Mux secret in dashboard ASAP** since the original was sent in chat — pull the new value into the same vault row (`UPDATE syntharra_vault SET key_value=...`). Note: spec/plan reference key types `data_token` and `playback_signing_key` — the actual Mux API auth pair is `token_id` + `secret_key`. Plan will be aligned at Day 5 execution time.
- **Founder VSL filming** — Dan-only, ~1 hour shoot, script in spec § 3.2. Day 5 blocker.

## What's blocked

- **Telnyx SMS** — waiting on Telnyx AI evaluation approval.

## Architecture invariants (do not violate)

- **retell-iac is the source of truth for the agent.** No manual Retell dashboard edits to MASTER.
- **MASTER templates are the only thing in the repo.** Per-client clones live in Supabase `client_agents`.
- **IDs come from `docs/REFERENCE.md` only.** Never inline.
- **Never test on a live Retell agent.** Clone → TESTING → `retell-iac/scripts/promote.py` → live.
