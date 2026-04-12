# Tier 1 Autonomous Marketing Team — Implementation Plan

**Date:** 2026-04-11 (evening)
**Author:** Claude (coordinator), informed by 4-agent parallel reconnaissance
**Status:** PENDING DAN'S APPROVAL — no code written until approved
**Replaces:** nothing. Extends `tools/marketing_brain.py` 5-phase loop.

---

## The single most important finding

**`blog_topics` table has 41 rows — 40 queued briefs, 1 published.** You seeded 40 pre-approved SEO content topics with target keywords and angle briefs on 2026-03-31. **Nothing has been reading from this table since.** A single script turns 40 queued briefs into 40 published blog posts.

**The second most important finding:** syntharra.com has **P0 fires currently burning on live pages**. Before we publish 40 new blog posts, we have to stop the existing pages from lying about the product.

---

## Executive summary

1. **Phase 0 first — put out the P0 fires on the live site** (wrong pricing in homepage schema, fake phone in 25 city pages, "14-day trial" everywhere when it's actually "200-minute trial", duplicate content clusters, missing Product/Review schema on 19 comparison pages). Template-level fixes in `tools/generate_city_pages.py` cascade to 25 pages in one commit.

2. **Phase 1 next — drain the 40 queued `blog_topics` briefs** into real published HTML blog posts via `tools/blog_publisher.py` that (a) reads briefs, (b) calls `claude -p` with the existing blog template pattern, (c) commits HTML to `Syntharra/syntharra-website/blog/`, (d) updates `blog_topics.status='published'`, (e) re-runs `generate_sitemap.py`.

3. **Phase 2 next week — competitor intel + lead magnet + research cron + content gap fill**. These use the existing extension points in `marketing_brain.py` and require no new tables (we already have `competitor_intelligence`, `marketing_intelligence`, `content_queue`, `marketing_brain_log` from this morning's migration).

4. **Everything plugs into existing infrastructure.** Zero forks, zero parallel systems, zero duplication of things that already exist. The gap list is short and specific.

---

## Ground truth from the 4-agent recon

### Agent 1 — Website repo (static HTML, GitHub Pages)

- **Corrections to my stale numbers:** 25 city pages (not 34), 19 comparison pages (not 5), **21 blog posts already exist**, 1 lead magnet PDF (`syntharra-call-forwarding-guide.pdf`) not linked from any page
- **SEO baseline is healthy:** meta descriptions, canonicals, JSON-LD schema, OG tags, robots.txt explicitly allowing AI crawlers (GPTBot, ClaudeBot)
- **`marketing-tracker.js` already POSTs events** to Supabase Edge Function → `marketing_events` table (page_view, cta_click, scroll_depth, vsl_play_*)
- **VSL slot is on `/start.html`**, not homepage. Uses mux-player
- **No email capture form anywhere on the site**
- **`_template/page-builder.py` exists in the website repo** — partial page-generation automation that pre-dates any of my work. **Must read this before building anything that generates pages.**

### Agent 2 — Automations + DB inventory (THE BIG ONE)

- **`blog_topics`: 41 rows, 40 queued, 1 published.** Schema: `id, slug, title, tag, hero_emoji, hero_gradient, target_keyword, brief, status, created_at, published_at`. **Briefs only — not full drafts.** Nothing writes to this table currently.
- **Extension points in `marketing_brain.py` documented at exact line numbers:**
  - Phase 2 PLAN at [L441](../../tools/marketing_brain.py#L441) — emits `{cold_email, reddit, linkedin, short_form, rationale}`. Add keys.
  - Phase 4 EXECUTE at [L1126-1188](../../tools/marketing_brain.py#L1126-L1188) — hardcoded subprocess calls with `is_X_enabled()` gates. Add new executors + gates.
  - Phase 5 TRACK via `record_campaign()` at [L1028](../../tools/marketing_brain.py#L1028) — new channels plug in via unique `channel` string.
- **`marketing_campaigns`, `content_variants`, `campaign_results`: 0 rows each.** The brain has never tracked an execution end-to-end. Cold email was gated before it shipped any.
- **`newsletter-weekly.html` Brevo template exists but NOTHING sends it.** Latent lead-nurture template.
- **GSC setup doc exists but Dan hasn't done DNS verification.** GSC is not actually connected. Brain's REVIEW phase has no organic-search signal yet.
- **`research_agent.py` shipped today (99 rows in `marketing_intelligence`) but not yet on a cron.**
- **`generate_city_pages.py` has 9 cities defined but 25 live.** Existing city pages came from a different tool — probably `_template/page-builder.py` in the website repo. **Do not extend `generate_city_pages.py` without understanding this discrepancy.**

### Agent 3 — P0 FIRES burning on syntharra.com RIGHT NOW

| # | Fire | Scope | Fix location |
|---|---|---|---|
| P0-1 | Homepage Product schema advertises **$497 / $997** (old Standard/Premium, killed 2026-04-09) | Homepage JSON-LD | Homepage HTML |
| P0-2 | **Placeholder phone `+1-000-000-0000`** in LocalBusiness schema | **All 25 city pages** | Page template (one fix, 25 pages) |
| P0-3 | **"Free 14-day pilot"** everywhere, but real offer is **200-minute free trial** | **Homepage + 25 cities + 19 vs-* + lp pages** | Global find/replace |
| P0-4 | **Zero cross-linking between city pages** — all orphan spokes | All 25 city pages | Add footer block with 24 other cities |
| P0-5 | **Duplicate content cluster:** `/hvac.html`, `/lp/hvac-answering-service.html`, `/best-hvac-answering-service.html` no canonical chosen | HVAC + plumbing + electrical (6 pages) | Set canonicals |
| P0-6 | **19 vs-* pages have only FAQPage schema** — missing Product + Review | All 19 comparison pages | Template change |
| P0-7 | Homepage title/meta description may be missing/wrong | Homepage | Homepage HTML |

**Agent 3's strategic call:** most of these fixes should land as **template changes** in `tools/generate_city_pages.py` (or `_template/page-builder.py` in the website repo once I read it). One PR → 25 pages fixed in one commit.

### Agent 4 — Competitor landscape

**Your wedge (locked in):** *"The only $697 flat-rate AI phone receptionist built specifically for HVAC shops with 1-10 techs, with HVAC triage scripts out of the box, and a 200-minute free pilot — no sales call, no per-minute meter, no contracts."*

**Competitor pricing (real, verified from their pricing pages):**
- Smith.ai: $95-$292.50/mo (per-call, confusing for HVAC who think in minutes)
- Ruby: $235-$1,640/mo (human-only, can't cover 3am heatwave spikes)
- Nexa: **hides pricing** (biggest Nexa weakness)
- Abby: $99-$1,380/mo (weekly blog but zero HVAC specificity)
- PATLive: $235+/mo (most HVAC-committed with HVAC Playbook PDF, but human-only + expensive)
- Answering Service Care: Cloudflare 403'd, minimal HVAC footprint

**10 keyword opportunities** (page-1 feasible in 3 months). I'm marking two as **INVALID — cannot target**:
1. "AI answering service for HVAC" — ✅
2. "after hours HVAC call answering" — ✅
3. "HVAC no-cool emergency dispatch service" — ✅ (blue ocean)
4. ~~"ServiceTitan AI receptionist integration"~~ — ❌ **WE DO NOT HAVE THIS INTEGRATION.** Syntharra is lean architecture (per 2026-04-09 cleanup): Retell answers → email/Slack/SMS notification. No ServiceTitan integration. Cannot publish content promising it.
5. ~~"Housecall Pro answering service"~~ — ❌ Same reason. No HCP integration.
6. "HVAC receptionist cost per minute" — ✅ (we win on flat pricing angle)
7. "how many calls HVAC shops miss at night" — ✅ (data study opportunity)
8. "Smith.ai alternative HVAC" — ✅
9. "HVAC answering service [city]" — ✅ (programmatic, already 25 pages, expand to 38)
10. "cheap AI phone agent for small HVAC" — ✅

**5 content pieces Agent 4 recommended. I'm modifying:**
1. ✅ "The Real Cost of a Missed HVAC Call: 2026 Data Study" — **also doubles as the lead magnet** (kills two birds)
2. ✅ "Smith.ai vs Ruby vs Syntharra: Which Answering Service Actually Fits a 1-10 Tech HVAC Shop?" — comparison blog
3. ❌ ~~"ServiceTitan + AI Receptionist: The Complete Integration Guide"~~ — **REPLACE** with **"How Syntharra Notifies Your Shop: Email, Slack, and SMS Lead Alerts in Under 60 Seconds"** — documents what we actually have
4. ✅ "After-Hours HVAC Playbook: What Happens When Someone Calls at 2am with No Heat" — playbook blog
5. ✅ "HVAC Answering Service Pricing Explained: Per-Minute vs Per-Call vs Flat-Rate (with real math)"

**The ServiceTitan/HCP caveat is non-negotiable** — we already had the Jobber/ServiceTitan hallucination problem this morning. Not repeating it.

---

## Build sequence — atomic, committable phases

### Phase 0 — Put out the P0 fires on the live site (FIRST, BEFORE ANY NEW CONTENT)

**Rationale:** every new SEO page we publish drives traffic to a funnel that currently says the product is $497, has a fake phone number, and offers a 14-day trial that doesn't exist. Publishing more content before fixing this is scaling a broken funnel.

| Task | Scope | Dependency |
|---|---|---|
| **0.1** | Read `Syntharra/syntharra-website/_template/page-builder.py` to understand existing page-generation automation | None |
| **0.2** | Fix homepage `<head>` — update title, meta description, remove old Product schema with $497/$997, add single-tier Product schema at $697 with 200-min trial offer | After 0.1 |
| **0.3** | Fix city page template — remove placeholder phone `+1-000-000-0000`, update trial wording to "200-minute free pilot · no credit card · live in 24 hours", add 24-city cross-link footer block | After 0.1 |
| **0.4** | Regenerate all 25 city pages from fixed template | After 0.3 |
| **0.5** | Set canonical tags on duplicate clusters: `/hvac.html` and `/lp/hvac-answering-service.html` → canonical = `/best-hvac-answering-service.html` (same for plumbing + electrical) | Parallel with 0.3 |
| **0.6** | Add Product + Review JSON-LD schema template to all 19 vs-* comparison pages (aggregateRating 4.9 / 847 reviews matching homepage claim, reviewBody stubs) | Parallel with 0.3 |
| **0.7** | Global find/replace on homepage + lp/* pages for "14-day" → "200-minute" | Parallel |
| **0.8** | Regenerate sitemap via `tools/generate_sitemap.py` | After 0.4, 0.6 |
| **0.9** | Smoke test: `curl` each fixed page, verify no `$497`, `$997`, `+1-000-000-0000`, or `14-day` appears anywhere | After 0.8 |
| **0.10** | Commit + push to `Syntharra/syntharra-website` main branch (triggers GH Pages deploy) | After 0.9 |

**Parallelism:** Tasks 0.3, 0.5, 0.6, 0.7 can run in parallel via subagent swarm. 0.1 and 0.2 run in main context first.

**Estimated commits:** 2-3 (website repo). Zero commits to automations repo in this phase.

### Phase 1 — SEO content engine (drain the 40 briefs)

**Rationale:** single highest-leverage gap. 40 pre-approved topics sitting idle. One script unlocks them.

| Task | Scope | Dependency |
|---|---|---|
| **1.1** | Read 2-3 existing blog posts (`/blog/hvac-missed-calls.html`, `/blog/first-to-answer-wins.html`, `/blog/cost-of-missed-calls-contractors.html`) to learn the exact HTML template pattern (style block, schema, CTAs, header/footer) | None |
| **1.2** | Write `tools/blog_publisher.py` v1 — reads `blog_topics` WHERE status='queued' ORDER BY created_at, picks N to draft, calls `claude -p` with brief + target_keyword + template pattern, gets back full HTML | After 1.1 |
| **1.3** | Add Article JSON-LD schema generation to the template (headline, datePublished, dateModified, author, image) — solves P1-7 from Agent 3's audit for both old and new posts | Parallel |
| **1.4** | Add commit-to-GitHub path — write file to local clone of `syntharra-website`, `git add` + `git commit` + `git push` OR use GitHub API via `mcp__claude_ai_Github_MCP__create_or_update_file` | Parallel with 1.2 |
| **1.5** | Add status transition: `blog_topics.status='queued'` → `'drafted'` → (Dan approval) → `'published'` + set `published_at` | After 1.2 |
| **1.6** | Build `--dry-run` mode — writes HTML to `/tmp/` + prints diff-style summary for Dan to review before first live publish | After 1.2 |
| **1.7** | Smoke-test with 1 real topic in dry-run, then 1 real topic live, verify end-to-end | After 1.6 |
| **1.8** | Wire into `marketing_brain.py` Phase 4 EXECUTE with `is_seo_publish_enabled()` gate (default false until Dan flips it) | After 1.7 |
| **1.9** | Add Railway cron `syntharra-blog-publisher` — Mon/Wed/Fri 07:00 UTC — `python tools/blog_publisher.py --limit 2` | After 1.8 |

**Estimated commits:** 5-7 (all to automations repo), plus 1-2 commits to website repo per published blog post (auto-generated).

### Phase 2 — Research Agent cron + brain integration

**Rationale:** finishes the research agent we shipped this morning.

| Task | Scope |
|---|---|
| **2.1** | Add Railway cron `syntharra-research-agent` — daily 06:00 UTC — `python tools/research_agent.py --source all` |
| **2.2** | Wire `marketing_brain.py` Phase 1 REVIEW to read `marketing_intelligence` for the current week (top 10 by confidence) |
| **2.3** | Add intelligence summary to the Slack weekly plan in Phase 3 PROPOSE |
| **2.4** | Write per-phase rows to `marketing_brain_log` (currently empty) |

**Estimated commits:** 2.

### Phase 3 — Competitor intel writer

**Rationale:** `competitor_intelligence` table exists, no writer.

| Task | Scope |
|---|---|
| **3.1** | Build `tools/competitor_watch.py` — scrapes pricing + blog pages for 5 competitors weekly (Smith.ai, Ruby, Nexa, Abby, PATLive — Agent 4 verified the right URLs) |
| **3.2** | Diff against last week's snapshot → detect significant changes (price change, new blog post, new feature mentioned on homepage, review score change) |
| **3.3** | Write to `competitor_intelligence` table with structured `top_content` and `content_gaps` fields |
| **3.4** | On significant change, post to Slack #marketing-team |
| **3.5** | Wire into `marketing_brain.py` Phase 1 REVIEW |
| **3.6** | Add Railway cron `syntharra-competitor-watch` — Monday 06:30 UTC (30 min before brain runs) |

**Estimated commits:** 3-4.

### Phase 4 — Lead magnet capture + nurture

**Rationale:** `website_leads` has 5 rows, nothing reads them. `newsletter-weekly.html` Brevo template exists, nothing sends it. And the lead magnet itself ("2026 HVAC Missed-Calls Report") doubles as a content piece from Agent 4's recommendations.

| Task | Scope |
|---|---|
| **4.1** | Design the lead magnet asset: "The 2026 HVAC Missed-Calls Report" — data study on missed call economics (avg ticket value, after-hours call %, heatwave spikes, conversion rates). Generated by `claude -p` from known industry data. |
| **4.2** | Generate as HTML + convert to PDF via `wkhtmltopdf` or similar. Upload to `syntharra-website/resources/hvac-missed-calls-2026-report.pdf` |
| **4.3** | Build landing page `/resources/hvac-missed-calls-2026-report.html` with email capture form → Supabase Edge Function → `website_leads` table + trigger Brevo auto-send |
| **4.4** | Repurpose `shared/email-templates/newsletter-weekly.html` as Brevo template #1 for the nurture sequence (needs a rewrite) |
| **4.5** | Build 3-email nurture sequence: day-0 delivery, day-3 "here's a case study", day-7 "start your 200-min free pilot". Upload via `upload_brevo_templates.py` |
| **4.6** | Build `tools/lead_magnet_nurture.py` — daily cron, reads new `website_leads` rows, triggers Brevo auto-send |
| **4.7** | Wire into `marketing_brain.py` Phase 1 REVIEW (count new lead magnet signups as a KPI) |

**Estimated commits:** 4-5.

### Phase 5 — Content gap closure (new pages)

**Rationale:** Agent 3 identified 13 missing city pages + 6 missing money pages. Agent 4 identified 5 content pieces that don't exist. Use the blog_publisher from Phase 1 + a city-page-generator for this.

| Task | Scope |
|---|---|
| **5.1** | Read `_template/page-builder.py` to understand how existing city pages were generated. DO NOT extend `tools/generate_city_pages.py` until this is clear. |
| **5.2** | Add 13 new city pages (Chicago, LA, San Diego, San Jose, Seattle, Portland, Kansas City, St. Louis, Minneapolis, Cleveland, Pittsburgh, Sacramento, Detroit) via whichever tool generates them canonically |
| **5.3** | Add 6 new money pages: `/24-7-hvac-call-handling`, `/hvac-after-hours-dispatcher`, `/ai-receptionist-for-hvac-contractors`, `/hvac-emergency-dispatch-service`, `/hvac-overflow-answering-service`, `/hvac-answering-service-near-me` (geo-redirect hub) |
| **5.4** | Insert 5 new content pieces from Agent 4 into `blog_topics` as new queued rows — **replacing the ServiceTitan integration piece** with "How Syntharra Notifies Your Shop: Email, Slack, SMS in Under 60 Seconds" |
| **5.5** | About page E-E-A-T upgrade: founder bio section, Person JSON-LD schema, link to LinkedIn |
| **5.6** | Start `/case-studies.html` — 1 placeholder structure (wait for first paying client to fill in real data) |

**Estimated commits:** 5-8 (mostly website repo).

### Phase 6 — Marketing Brain integration (tie it together)

**Rationale:** everything above plugs into the brain in one coordinated commit.

| Task | Scope |
|---|---|
| **6.1** | Phase 2 PLAN — extend `generate_weekly_plan()` return dict with `seo_publish`, `competitor_intel`, `lead_magnet` keys |
| **6.2** | Phase 3 PROPOSE — extend `_format_slack_plan()` with Slack blocks for new tactics |
| **6.3** | Phase 4 EXECUTE — add `execute_seo_publish()`, `execute_competitor_intel()`, `execute_lead_magnet_nurture()` + `is_X_enabled()` gates |
| **6.4** | Phase 5 TRACK — add new channel strings to `record_campaign()` calls |
| **6.5** | Write audit rows to `marketing_brain_log` in each phase |

**Estimated commits:** 1 big one.

---

## Tonight's scope (realistic, 90-120 min of work)

I will execute **Phase 0 + Phase 1 + Phase 2** tonight via swarm. Phases 3-6 are scheduled for next sessions (roadmap committed to this file so nothing gets lost).

**Phase 0 dispatch plan (parallel subagents):**
- **Agent A** — read `_template/page-builder.py`, fix homepage `<head>` + Product schema ($497→$697, remove Premium)
- **Agent B** — fix city page template (phone + trial language) + regenerate all 25 cities
- **Agent C** — fix duplicate content cluster (set canonicals on 6 duplicate pages) + global 14-day → 200-min find/replace
- **Agent D** — add Product + Review schema template to 19 vs-* pages
- **Me** — review each agent's diff, run smoke tests, commit + push to `syntharra-website`

**Phase 1 dispatch plan (sequential — depends on template knowledge):**
- **Me** (main context) — read 3 existing blog posts, learn the template, then write `tools/blog_publisher.py` with careful grounding
- **Agent E** (after I'm done) — QA pass: dry-run the publisher on 1 topic, verify HTML matches template style
- **Me** — commit, add cron, smoke test

**Phase 2 (tiny, me in main context):**
- Add Railway cron for `research_agent.py`
- Patch `marketing_brain.py` Phase 1 REVIEW to read `marketing_intelligence`

---

## Risks + open questions for Dan (BEFORE I execute)

### 1. Phone number for P0-2 fix
The city pages currently have fake `+1-000-000-0000` in LocalBusiness schema. Agent 3 recommended either (a) replace with real support number, or (b) remove the `telephone` field entirely. **What do you want?** You don't have Telnyx yet so you may not have a public support number. Recommendation: **remove the `telephone` field entirely** until Telnyx lands. Cleaner than a fake.

### 2. aggregateRating on vs-* pages
Agent 3 suggested adding Product+Review schema with `aggregateRating: 4.9 from 847 reviews` matching the homepage claim. **Is that claim real or placeholder copy?** If it's placeholder, we cannot put it in schema (Google structured data review penalty). Tell me: real number, remove entirely, or keep it vague.

### 3. GitHub push mechanism for blog publisher
Agent 2 confirmed you have GitHub MCP wired but there's a known `403 Resource not accessible by integration` issue per CLAUDE.md. Fallback is Desktop Commander MCP or local clone push. **Which path should `blog_publisher.py` use?** Recommendation: **local clone push** — most reliable, matches the way `generate_sitemap.py` currently writes to the adjacent website repo.

### 4. Phase 1 blog publisher review loop
When the blog publisher generates a full HTML blog post from a brief, **do you want to review every post before it publishes, or auto-publish on success?** Recommendation: **dry-run + Slack-review for the first 5 posts**, then auto-publish with 48h manual-override window. This matches the marketing_brain pattern.

### 5. The 2 invalid keyword opportunities from Agent 4
I'm dropping "ServiceTitan AI receptionist integration" and "Housecall Pro answering service" from the keyword target list and replacing content piece #3 with "How Syntharra Notifies Your Shop: Email, Slack, SMS in Under 60 Seconds". **Confirm this is right** — you do NOT have ServiceTitan or Housecall Pro integrations, right? The 2026-04-09 lean cleanup killed all Premium dispatchers. Memory says yes but I want explicit confirmation before we publish content based on it.

### 6. Lead magnet content — is Dan OK with Claude writing a "data study"?
Phase 4 "2026 HVAC Missed-Calls Report" would be generated by Claude from public data (no proprietary Syntharra stats yet). It would cite sources and make clear what's estimated vs. measured. **Is that integrity-acceptable to you** or do you want to wait until you have real Syntharra pilot data?

---

## Success criteria

**Phase 0 done when:**
- Homepage JSON-LD shows `price: 697.00` single offer, no $497/$997 anywhere on site
- `curl https://syntharra.com/hvac-answering-service-phoenix.html | grep "+1-000-000-0000"` returns nothing
- `curl https://syntharra.com/ | grep "14-day"` returns nothing
- Each city page has a "serving HVAC contractors in X other cities" footer with 24 anchor links
- Each vs-* page has `"@type": "Product"` and `"@type": "Review"` in JSON-LD
- Supabase `marketing_events` still receives events after deploy (tracker not broken)

**Phase 1 done when:**
- `python tools/blog_publisher.py --dry-run --limit 1` prints HTML that matches the existing blog template style
- 1 real blog post published to `/blog/{slug}.html` from a `blog_topics` row
- `blog_topics.status` is `'published'` and `published_at` is set for that row
- Sitemap regenerated and contains the new post
- Railway cron configured and healthy

**Phase 2 done when:**
- `research_agent.py` runs on a daily cron and inserts rows
- `marketing_brain.py` Phase 1 REVIEW reads `marketing_intelligence` + reports top signals in the weekly Slack plan
- `marketing_brain_log` has rows after the next brain run

---

## Commit discipline (lessons from today)

1. **One atomic commit per task.** No batching.
2. **Every commit message names the file(s) + one-line justification.**
3. **Grep + read before edit.** No writing from memory.
4. **Every new executor has `is_X_enabled()` gate defaulting to false.** Nothing runs live without a flag flip.
5. **Swarm agents work on non-overlapping files.** Conflicts get resolved in main context, not in the swarm.
6. **Dry-run everything once before the first live run.**
7. **Session ends with updated `docs/STATE.md` + session log.**

---

## What I need from you

**6 decisions** above the line (questions 1-6). Once you answer them, I execute Phase 0 + Phase 1 + Phase 2 via swarm tonight.

If any of the questions make you want to change scope, tell me now. I'd rather get it right once than build something you reject.
