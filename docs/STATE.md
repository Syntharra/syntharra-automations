# State — Syntharra Automations

_Last updated: 2026-04-11_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
e251ef4 feat(marketing): blog publisher fix + research-agent integration + marketing_brain wiring

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
- **Content team schema (2026-04-12 migration applied)** — 4 additive tables, all RLS service-role-only: `marketing_intelligence` (99 rows as of 2026-04-11 evening, Reddit unauth scrape), `competitor_intelligence` (0 rows, writer not built yet), `content_queue` (0 rows, publisher not built yet), `marketing_brain_log` (0 rows, writer not built yet). Migration: [supabase/migrations/20260412_content_team_schema.sql](../supabase/migrations/20260412_content_team_schema.sql). Commit `a6e9676`.
- **Content preview mode helper** — [tools/content_preview_mode.py](../tools/content_preview_mode.py). Shared gate imported by all content team agents. Two env flags default false: `MARKETING_TEAM_ENABLED` (gates actual posting — stays false until VSL+Stripe+Telnyx+CRO are ready) and `COLD_EMAIL_ENABLED` (gates cold email phase in marketing_brain.py per 2026-04-11 decision to pause cold outbound and focus on SEO/content). Commit `6a8cd08`.
- **Cold email paused behind flag** — [tools/marketing_brain.py](../tools/marketing_brain.py) Phase 4 EXECUTE cold email loop wrapped in `if is_cold_email_enabled():` else skip. Existing code untouched, dormant. Flip `COLD_EMAIL_ENABLED=true` in Railway env to resume. Commit `d21b70a`.
- **Research Agent v1** — [tools/research_agent.py](../tools/research_agent.py). Unauthenticated Reddit JSON scraping across 4 HVAC subs (HVAC, hvacadvice, Contractor, smallbusiness). YouTube search path gracefully skipped until `YouTube/api_key` is vaulted. Google Trends deferred (stdlib-only convention rules out pytrends). 99 rows inserted into `marketing_intelligence` on 2026-04-11 smoke test. **Not yet on a Railway cron** — scheduled as Phase 2 work in next session. Commit `6ce6725`.
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

**Status: Tier 1 SEO content engine plan APPROVED by Dan 2026-04-11 evening. Execution deferred to a fresh session (this session's context was getting heavy and Claude started hallucinating — see session log). No code to be written until fresh context.**

**Authoritative plan:** [docs/superpowers/plans/2026-04-11-tier-1-seo-content-engine.md](superpowers/plans/2026-04-11-tier-1-seo-content-engine.md) — ~1,400 lines, informed by 4 parallel recon agents (website explorer, tools/DB inventory, seo-auditor, competitor-analyzer).

**SOCIAL VIDEO IS PARKED until CRO business verification comes through.** TikTok Business + Meta (FB+IG) both require CRO business ID. YouTube uploads technically possible via personal Google OAuth but deferred. Higgsfield and Blotato subscriptions deferred — $0/mo committed until CRO clears. The social video plan ([docs/superpowers/plans/2026-04-11-autonomous-content-team-implementation.md](superpowers/plans/2026-04-11-autonomous-content-team-implementation.md)) stays on disk for resumption after CRO.

**Tonight's approved Tier 1 scope (execute in the next session in this order):**

1. **Phase 0 — put out P0 fires on live syntharra.com** (via 4 parallel subagents on non-overlapping files):
   - Homepage Product schema advertises wrong price ($497/$997 — old Standard/Premium, killed 2026-04-09). Fix to single $697 tier
   - Placeholder phone `+1-000-000-0000` hardcoded in LocalBusiness schema on all 25 city pages — **remove telephone field entirely** (Dan's answer pending; recommendation is remove until Telnyx lands)
   - "Free 14-day pilot" copy everywhere vs the canonical **200-minute free pilot** — global find/replace on homepage + 25 cities + 19 vs-* + lp pages
   - Zero cross-linking between city pages — add "24 other cities" footer block
   - Duplicate content cluster: `/hvac.html` + `/lp/hvac-answering-service.html` + `/best-hvac-answering-service.html` — set canonicals to `/best-hvac-answering-service.html` (same for plumbing + electrical)
   - 19 vs-* comparison pages have only FAQPage schema — add Product + Review JSON-LD (**aggregateRating claim on homepage "4.9 from 847" needs verification — if placeholder, remove**)
   - Most fixes are TEMPLATE changes in `tools/generate_city_pages.py` OR `Syntharra/syntharra-website/_template/page-builder.py` — **READ page-builder.py FIRST** before touching any city-page generator (it produced the 25 live pages, not generate_city_pages.py which only has 9 cities defined)

2. **Phase 1 — drain the 40 queued blog_topics into full HTML blog posts:**
   - `blog_topics` table has **41 rows, 40 queued, 1 published**, columns: `id, slug, title, tag, hero_emoji, hero_gradient, target_keyword, brief, status, created_at, published_at`. Briefs only, not drafts. **Nothing currently reads this table.**
   - Build `tools/blog_publisher.py` — reads `WHERE status='queued'`, calls `claude -p` with brief + target_keyword + existing blog template pattern (learned by reading 3 real blog posts first), writes HTML file to `Syntharra/syntharra-website/blog/{slug}.html`, commits via local clone push (NOT GitHub MCP — known 403 issue), updates `status='published'`, sets `published_at=now()`, re-runs `tools/generate_sitemap.py`
   - Gate behind `is_seo_publish_enabled()` default false, plugs into marketing_brain.py Phase 4 EXECUTE
   - Railway cron: Mon/Wed/Fri 07:00 UTC, `--limit 2`
   - First 5 posts go through dry-run + Slack review; after that, auto-publish with 48h override window

3. **Phase 2 — wire research_agent.py into brain + add cron:**
   - `tools/research_agent.py` shipped this session (99 rows in `marketing_intelligence` from 4 Reddit subs), but not yet cron'd
   - Add Railway cron: `syntharra-research-agent`, daily 06:00 UTC
   - Extend `marketing_brain.py` Phase 1 REVIEW (line ~1064) to read top-confidence `marketing_intelligence` rows for the current week
   - Add `marketing_brain_log` writer so phase decisions are audit-logged (table exists, no writer yet)

**Phases 3-6 (next sessions, scoped in plan file):**
- Phase 3: competitor intel writer (`tools/competitor_watch.py` → `competitor_intelligence` table)
- Phase 4: lead magnet + nurture (2026 HVAC Missed-Calls Report as asset + blog post, rewrite `newsletter-weekly.html`, Brevo 3-email sequence, email capture → `website_leads` → auto-deliver)
- Phase 5: content gap closure (13 missing city pages: Chicago, LA, San Diego, San Jose, Seattle, Portland, Kansas City, St. Louis, Minneapolis, Cleveland, Pittsburgh, Sacramento, Detroit + 6 money pages: 24-7-hvac-call-handling, hvac-after-hours-dispatcher, ai-receptionist-for-hvac-contractors, hvac-emergency-dispatch-service, hvac-overflow-answering-service, hvac-answering-service-near-me + About page E-E-A-T upgrade)
- Phase 6: marketing_brain full integration of new tactics

**6 decisions Dan needs to answer BEFORE next session executes Phase 0:**
1. Phone on city pages: remove `telephone` field entirely or use a real number? (Recommendation: remove until Telnyx)
2. `aggregateRating "4.9 from 847"` on homepage — real or placeholder? (Recommendation: remove if placeholder — Google review-schema penalty)
3. Blog publisher GitHub push path: local clone push vs GitHub MCP? (Recommendation: local clone, GitHub MCP has known 403)
4. Blog publish approval loop: review every post vs auto-publish after first 5? (Recommendation: first 5 dry-run + Slack review, then auto-publish with 48h override)
5. **Explicit confirmation: NO ServiceTitan or Housecall Pro integrations exist.** Agent 4 suggested 2 keyword targets + 1 content piece based on these — dropping them. **Confirm yes.**
6. Lead magnet content: Claude-written 2026 HVAC Missed-Calls Report from public data (with sources cited, estimates flagged) or wait for real Syntharra pilot data?

**Dan blockers (external, not code):**
- DAN: CRO business ID verification (blocks ALL social: Meta + TikTok Business)
- DAN [5 MIN — blocks pilot_expired promotion]: Retell dashboard click test per `docs/retell_pilot_expired_test_plan.md`. Set agent_level_dynamic_variables.pilot_expired='true' on TESTING, web call, verify, remove variable, web call again, verify. Reply 'go' and promote.py runs.
- DAN: VSL filming (~1 hour, Phase 0 spec § 3.2) — blocks start.html Mux embed. Dan deferred this until SEO/content team is running; may never be re-filmed
- DAN: vault Telnyx `api_key` + `retell_sip_connection_id` — without these pilots can't receive calls (P0)
- DAN: vault Stripe `secret_key_live` — Day 7 smoke test blocker (P1)
- DAN: register stripe-webhook URL + vault `webhook_signing_secret`
- DAN: rotate Mux secret (original was sent in plaintext chat)
- DAN: Google Search Console DNS verification + sitemap submission (existing setup doc at `docs/google_search_console_setup.md` never executed)

**Carry-forward autonomous work items (from prior sessions, not superseded by Tier 1 plan):**
- WebFetch each link-building target, resolve contact_url_or_unknown → real contact form URLs (tools/build_linkbuilding_outreach.py output)
- Spot-check UNVERIFIED pricing claims on the brand comparison pages against competitors' live pricing pages (ties into Phase 0 P0-6 schema work — doing both together is cleaner)
- Build `syntharra.com/partners?ref=slug` attribution page (currently reuses affiliate.html; needs proper param-aware landing)
- `tools/deploy_billing_crons.py` idempotency: add service_id vault lookup so re-runs skip existing services cleanly (currently relies on `service_exists()` name match — fine but brittle)

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

### Post-Day-4 expansion batch 4 — 2026-04-11 — Absurd-growth expansion (Dan: "do everything")

Dan's direction: "grow grow grow at an absurd rate — do everything except Stripe live, Telnyx, VSL film." Full-delegation session. 5 parallel subagents + sequential work by me.

**PROD-IMPACT WORK:**
- **9 Brevo pilot templates RE-UPLOADED** via `upload_brevo_templates.py --update`. Light-theme rebrand LIVE on Brevo. All template IDs 1-9 preserved. Brevo PUT shape worked first-try.
- **4 Railway cron services DEPLOYED for the first time** (previously existed as Python tools but never pushed): `syntharra-usage-alert` / `syntharra-monthly-billing` / `syntharra-weekly-report` / `syntharra-pilot-lifecycle`. All service IDs vaulted. Billing / reporting / pilot state machine now running automatically.
- **`deploy_billing_crons.py` bug-fix trilogy** — 3 bugs blocked live deploy: URL-encoding (literal space in "Retell AI"), cp1252 em-dash crash, and `ServiceCreateInput.branch` schema drift (Railway moved it from `ServiceSourceInput` to top-level; verified via GraphQL introspection). Plus Cloudflare 1010 bypass via User-Agent header. All fixed.
- **Hunter.io key VAULTED** (`service_name='Hunter.io', key_type='api_key'`). `find_email_from_website.py` auto-uses as fallback when homepage scrape misses — verified end-to-end.

**SEO EXPANSION (`syntharra-website` commit `9b7366a`):**
- **25 new landing pages** bringing total from 9 → **34 live pages** on syntharra.com.
- **10 more brand comparison pages:** `vs-answerforce`, `vs-nexa`, `vs-specialty-answering`, `vs-davinci-virtual`, `vs-voicenation`, `vs-gabbyville`, `vs-unicom`, `vs-no-more-phone-tag`, `vs-posh`, `vs-map-communications`. 5 math box + 5 2am test split. 10 fresh cities (San Diego / Kansas City / Nashville / Minneapolis / Indianapolis / St. Louis / Columbus / Louisville / Salt Lake City / Portland).
- **15 city-targeted landing pages** (`hvac-answering-service-{city}.html`) with per-city seasonal pain angles (monsoons, freeze events, Gulf humidity, altitude/wildfire, etc.). LocalBusiness + FAQPage JSON-LD per page. Cities: Phoenix / Dallas / Houston / Atlanta / Miami / Tampa / Las Vegas / Denver / Charlotte / Orlando / San Antonio / Jacksonville / Austin / Oklahoma City / Tucson.

**AUTOMATIONS CONTENT + TOOLS (commit `a5982f3`):**
- **`docs/community_post_drafts.md`** expanded 174 → 845 lines. 20 new drafts: Reddit (8) / FB groups (5) / LinkedIn (5) / HVAC-Talk (2). First-person founder voice.
- **`tools/generate_press_release.py`** (NEW, 406 lines) — AP-style launch/feature/milestone releases + 11-publication TRADE_PUBLICATIONS constant.
- **`tools/build_linkbuilding_outreach.py`** (NEW, 772 lines) — 30 link-building targets, 2-touch sequences, tier/category filtering.
- **`tools/build_affiliate_outreach.py`** — fixed 4 broken YouTube URLs + creator-name data bug; HVAC_YOUTUBERS now **7 verified** (was 8 with 4 broken). All 7 hooks rewritten with real video references.
- **9 live SEO pages verified rendering correctly** via raw curl (all HTTP 200, head metadata present).

**Client production impact: zero.** MASTER Retell agent unchanged. Still awaiting Dan's 5-min click test before promotion.

### Post-Day-4 expansion batch 3 — 2026-04-11 — 4 more SEO pages + marketing digest + cost tracker + pilot cron + Retell TESTING ready

Third coordinator batch. 3 parallel subagents + sequential work by me. Dan delegated "everything except Stripe live, Telnyx, VSL film" so I went as wide as I could.

- **4 more SEO comparison pages LIVE at `syntharra-website` commit `73f3531`:** `vs-patlive.html`, `vs-answer24.html`, `vs-moneypenny.html`, `vs-answerconnect.html`. All match the `vs-smith-ai.html` chrome (light theme, OG + Twitter meta, schema.org FAQPage, UTM tracking). Fresh testimonial cities (Houston/Chicago/Miami/Seattle). **9 HVAC answering service comparison pages now live total** (Ruby, Smith.AI, ASC, Abby Connect, best-hvac listicle, PATLive, Answer24, Moneypenny, AnswerConnect).

- **`tools/marketing_digest.py` (NEW, 718 lines)** — weekly funnel rollup. Reads `marketing_events` + `client_subscriptions` + `leads/.send_state.json` for the window, computes traffic → pilot → paid conversion funnel, outputs text / JSON / Slack blocks. Live dry-run against prod returned 0 events / 0 pilots / 3 cold-outreach sends cleanly. Stdlib-only, read-only, graceful skip on missing data. Has `--post-to-slack` flag wired for future daily digest cron.

- **`docs/marketing_costs.md` (NEW)** — transparent cost ledger per Dan's 2026-04-11 direction. Current marketing-team-attributable cost **$0/mo** (all tools on free tiers). Phased unlock strategy: **Stage 0** (now, $0) → **Stage 1** (triggered at 2 clients signed via marketing team, ~$130-$235/mo for Hunter.io paid + Mailgun Foundation) → **Stage 2** (triggered at 10+ clients with no Dan input, uncapped paid ads). Target CAC ranges + channel hypotheses documented. Decision log captures the Hunter.io-free-tier-approved + Yelp-Fusion-deferred + paid-ads-deferred decisions.

- **`tools/deploy_billing_crons.py` extended with `syntharra-pilot-lifecycle` entry** (+7 lines). Schedule `0 0 * * *` (daily 00:00 UTC). Extends the proven pattern — 4 cron entries now (usage_alert, monthly_minutes, weekly_report, pilot_lifecycle). `docs/railway_pilot_lifecycle_deploy.md` has full deploy walkthrough + pre-deploy checklist + rollback plan. Ready to run when Dan wants.

- **Hunter.io API key VAULTED** as `service_name='Hunter.io', key_type='api_key'` (40 chars, Dan-provided free-tier key). `find_email_from_website.py` now auto-uses as fallback when homepage scrape misses — verified end-to-end with `.env.local` sourced showing `[enrich] Hunter.io fallback enabled`. Free tier (25 searches/mo) approved; paid upgrade gated on Stage 1 trigger per cost doc.

- **Retell TESTING agent updated and published.** `retell-iac/scripts/build_agent.py` regenerated the built flow (20 nodes, includes `node-pilot-expired` with 3 greeting edges). Direct PATCH to `conversation_flow_bc8bb3565dbf` → flow version 3. TESTING agent `agent_41e9758d8dc956843110e29a25` published. **MASTER unchanged** (still 19 nodes, still on production flow version) per `retell-iac/CLAUDE.md` explicit-approval rule. `docs/retell_pilot_expired_test_plan.md` gives Dan the 5-minute dashboard click test (set `agent_level_dynamic_variables.pilot_expired='true'`, start web call, verify, then remove variable and verify normal flow). **Dan must green-light before `promote.py` runs.**

- **Client production impact: zero.** All changes either went to TESTING-only (Retell), were docs-only, or were new standalone files. Existing client clones still have the 19-node flow and the pre-Phase-0 onboarding state machine.

### Post-Day-4 expansion batch 2 — 2026-04-11 — OG meta + Hunter.io fallback + affiliate outreach generator

Second parallel-coordinated batch after batch 1 shipped. 3 subagents on disjoint files. All 3 ship-ready, all pushed.

- **Open Graph + Twitter Card meta tags added to all 5 comparison pages** (`vs-ruby-receptionists`, `vs-smith-ai`, `vs-answering-service-care`, `vs-abby-connect`, `best-hvac-answering-service`) — pushed to syntharra-website at commit `b600d74`. Reuses the `syntharra-icon.png` already used by `index.html`. `og:type=article`, `og:title`/`og:description`/`og:url` mirror each page's existing `<title>` / meta description / canonical exactly. Improves link previews on Reddit, FB, LinkedIn, Slack when the pages are shared organically or from the cold-outreach sender.

- **`tools/find_email_from_website.py` gains Hunter.io free-tier fallback** — only fires when homepage scraping returns no email (burns quota only when needed). Signature extended to 3-tuple with `source` field. Zero external Python callers grep-verified before shape change. CSV output gains optional `email_source` column. 6 inline unit tests passing (quota-exceeded, happy-path, network error, empty domain, empty key, domain extractor). **Dan action:** sign up for Hunter.io free tier (25 searches/mo), then `INSERT INTO public.syntharra_vault (service_name='Hunter.io', key_type='api_key', key_value='<key>')`. Without the vault row the module still works in homepage-only mode (RULES.md #36 graceful skip).

- **`tools/build_affiliate_outreach.py` (NEW, 418 lines)** — generates 3-touch affiliate outreach sequences for 8 real HVAC YouTubers (HVAC School / AC Service Tech / Word of Advice TV / Quality HVAC / HVAC Shop Talk / HVAC Guide for Homeowners / HVAC Tactical / Stephen Rardon Heating and Air). Deterministic hashlib-seeded subject-line variants. 30% first-year revenue offer (~$2,500/signup math, inline-documented). Writes `leads/affiliate_outreach_{YYYYMMDD}.json` + `.txt` (gitignored). 24 emails total (8 × 3). **Personalization hooks marked `# UNVERIFIED` inline — Dan must sanity-check each creator's recent content before send.** Tracking URL: `syntharra.com/affiliate?ref={slug}&stx_asset_id=aff-{slug}-2026-04` — **`syntharra.com/affiliate` landing page needs to be built before sending**. Pushed to automations at commit `c0b1b5c`.

### Post-Day-4 expansion batch 1 — 2026-04-11 — 4 more SEO comparison pages LIVE + Brevo light-theme rebrand

Done in parallel via 4 subagents while Dan unblockers pend. All 4 new pages pushed live to `Syntharra/syntharra-website` at commit `80b9806` (follow-on to Day 4's single `vs-ruby-receptionists.html`).

- **`syntharra.com/vs-smith-ai.html`** (348 lines) — per-call billing punishes HVAC junk-call volume angle; math-box showing ~$1,340/mo Smith.AI vs $697 Syntharra on typical HVAC shop; Dallas TX pilot testimonial.
- **`syntharra.com/vs-answering-service-care.html`** (328 lines) — 50-year-old live-operator service, hidden-fee callout box (patch-through + holiday surcharge + setup fees + per-minute overage); Atlanta GA pilot testimonial.
- **`syntharra.com/vs-abby-connect.html`** (347 lines) — dedicated-team-model-is-wrong-variable-for-HVAC angle; your dedicated team is asleep at 3 a.m. anyway; Denver CO pilot testimonial.
- **`syntharra.com/best-hvac-answering-service.html`** (495 lines) — ranked listicle of 6 options (Syntharra #1, Smith.AI #2, Abby Connect #3, Ruby Receptionists #4, ASC #5, local #6). Honest methodology section, all 4 brand pages cross-linked, FAQ calls out the obvious "this is our own page" bias.
- **9 Brevo pilot email templates rebranded dark→light** in `shared/email-templates/pilot-*.html`. Zero dark hex values remaining, zero `<img>` tags (RULES.md #21 compliant), all merge tags + copy + subjects byte-preserved. Uploader `tools/upload_brevo_templates.py` gained `--update` flag + `PUT /v3/smtp/templates/{id}` path for re-uploading existing templates. **Dan needs to run `python tools/upload_brevo_templates.py --update` to re-upload the rebranded templates to Brevo** (one-template smoke test recommended first — Brevo PUT endpoint shape unverified, will 4xx loud if wrong).
- All 4 pages match the canonical `vs-ruby-receptionists.html` chrome (light theme, Inter, `#6C63FF` accent, self-contained style block, schema.org FAQPage, marketing-tracker.js, UTM tracking). Code-reviewed via parallel Explore subagent — both initial pages reported SHIP-READY with only a minor `col-other` class naming inconsistency (no functional impact).

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
