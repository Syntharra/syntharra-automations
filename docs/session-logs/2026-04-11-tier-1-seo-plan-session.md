# 2026-04-11 (evening) — Tier 1 SEO Content Engine Plan + 4 Commits

**Session duration:** ~6 hours
**Ratio:** poor — ~4 of 6 hours lost to circular research/hallucinations/rework. See "Failures" section.
**Outcome:** 4 commits shipped, 1 detailed plan file approved, clean handoff to next session.

---

## Summary

Started pulling up the "autonomous organic marketing team" from the prior session. Over the course of the session the scope evolved twice based on external blockers:

1. **AM → midday:** Designed and partially scoped a social-video content pipeline (Research → Writer → Publisher → Brain). Discovered via the 4-agent recon that the existing `marketing_brain.py` already has 5 phases + cold email + Reddit + LinkedIn posting (shipped 2026-04-11 morning in commit `e1796a3`). New work is extension, not rebuild.
2. **Midday → afternoon:** Investigated Higgsfield vs PixVerse vs Blotato pricing across 4 rounds (too many). Dan verified Higgsfield Plus $34/mo pricing via screenshot. Decision initially locked on Higgsfield Plus + Blotato Starter (~$63/mo).
3. **Afternoon pivot — CRO blocker discovered:** Dan cannot complete Meta Business Suite or TikTok Business registration until his Irish CRO (Companies Registration Office) business ID verification comes through. That blocks Facebook, Instagram, and TikTok posting. YouTube is technically possible via personal Google OAuth. The whole social pipeline is parked until CRO clears. **$63/mo in subscriptions correctly deferred → $0 committed.**
4. **Late afternoon pivot — Tier 1 non-social reframe:** Dan asked "what else can we build now while waiting on CRO". Strategic answer: the autonomous marketing team was always about continuous lead experimentation across channels, not specifically social. SEO + content + lead magnets + competitor intel are all un-blocked by CRO and can run tonight.
5. **Evening — 4-agent parallel recon + plan:** Dispatched 4 parallel subagents (website explorer, tools/DB inventory, seo-auditor, competitor-analyzer). Synthesized findings into a 1,400-line implementation plan for Tier 1. **Plan approved by Dan.** Execution deferred to a fresh session (this session was getting long and context-heavy).

## Commits shipped (4 total)

| SHA | Commit | Files | Lines | Verified |
|---|---|---|---|---|
| `a6e9676` | feat(content-team): schema for autonomous content pipeline | `supabase/migrations/20260412_content_team_schema.sql` | +257 | Applied to prod via Supabase MCP, verified all 4 tables exist with RLS + comments |
| `6a8cd08` | feat(content-team): preview mode gate + cold email flag | `tools/content_preview_mode.py` (new) | +73 | Smoke-tested both branches (default preview, live when env set) |
| `d21b70a` | feat(marketing-brain): gate cold email behind COLD_EMAIL_ENABLED flag | `tools/marketing_brain.py` (modified, +20/-8) | +20/-8 | AST parse clean, skip branch prints expected message |
| `6ce6725` | feat(research-agent): Reddit unauth scraping for HVAC niche | `tools/research_agent.py` (new) | +316 | Live run inserted 99 rows into `marketing_intelligence` in 9.8s |

**Total new code shipped this session:** 646 lines across 4 commits.

## Database state after this session

- `marketing_intelligence` — **99 rows** (Reddit unauth scrape, avg confidence 0.48, top post 1126 upvotes from r/smallbusiness). Schema applied via `a6e9676`. Writer: `tools/research_agent.py` (commit `6ce6725`).
- `competitor_intelligence` — 0 rows. Schema applied, no writer yet.
- `content_queue` — 0 rows. Schema applied, no writer yet. **Note: schema still includes Blotato-specific columns (`video_url`, `blotato_post_id`, `platform_post_urls`) from the social video plan. Fine for now — those columns are nullable and unused by the SEO content pipeline.**
- `marketing_brain_log` — 0 rows. Schema applied, no writer yet.

## Plan file created (approved, not yet executed)

**[docs/superpowers/plans/2026-04-11-tier-1-seo-content-engine.md](../superpowers/plans/2026-04-11-tier-1-seo-content-engine.md)** — the authoritative Tier 1 plan, informed by 4-agent recon. Phases 0-6 scoped. Phases 0-2 scheduled for execution in the next session.

**Also still on disk (parked until CRO):**
- [docs/superpowers/plans/2026-04-11-autonomous-content-team-implementation.md](../superpowers/plans/2026-04-11-autonomous-content-team-implementation.md) — the social video plan. Resurrect when CRO clears and TikTok Business + Meta + Higgsfield + Blotato are all unblocked.
- [docs/superpowers/specs/2026-04-11-autonomous-marketing-team-design.md](../superpowers/specs/2026-04-11-autonomous-marketing-team-design.md) — the original 9-agent design spec. Superseded by the lean 4-agent version inside the content-team-implementation plan, but kept for historical context.

## 4-agent recon summary (what we learned)

### Agent 1 — website repo explorer
- `Syntharra/syntharra-website` is a static HTML site deployed via GitHub Pages. Raw HTML, Inter font, #6C63FF primary. Strict style rules in the website's own CLAUDE.md governance doc.
- **25 city pages** (not 34 as I thought), **19 competitor comparison pages** (not 5), **21 blog posts already exist** (not 0)
- SEO baseline is healthy: meta descriptions, canonicals, JSON-LD schema, OG tags, robots.txt explicitly allowing AI crawlers
- `marketing-tracker.js` already POSTs page_view/cta_click/scroll_depth/vsl_play_* events to `marketing_events` via a Supabase Edge Function
- ONE lead magnet PDF (`syntharra-call-forwarding-guide.pdf`), not linked from any visible page
- No email capture form anywhere on the site
- VSL slot on `/start.html` (mux-player placeholder), not homepage
- `_template/page-builder.py` exists inside the website repo — partial page-generation automation that pre-dates my work. **Must be read before touching city page generation.**

### Agent 2 — automations + DB inventory (THE BIG DISCOVERY)
- **`blog_topics` table has 41 rows — 40 queued briefs, 1 published.** Columns: `id, slug, title, tag, hero_emoji, hero_gradient, target_keyword, brief, status, created_at, published_at`. Briefs only, not drafts. Seeded manually 2026-03-31. **Nothing currently reads or writes this table.** This is the biggest leverage point of the entire session — 40 SEO topics pre-approved with target keywords, sitting idle for 11 days.
- `marketing_brain.py` extension points documented at exact line numbers: Phase 2 PLAN at L441, Phase 4 EXECUTE at L1126-1188, Phase 5 TRACK at L1028. Every new tactic plugs in with an `is_X_enabled()` gate pattern.
- `marketing_campaigns`, `content_variants`, `campaign_results` — all 0 rows. The brain has never tracked an execution end-to-end yet.
- `shared/email-templates/newsletter-weekly.html` exists but nothing sends it. Latent lead-nurture template.
- Google Search Console setup doc exists but Dan hasn't done DNS verification. **GSC is not connected.**
- `tools/generate_city_pages.py` has only 9 cities defined but 25 city pages exist — existing pages were generated by `_template/page-builder.py` inside the website repo, not by this tool.

### Agent 3 — SEO audit of syntharra.com (P0 FIRES)
- **Homepage JSON-LD Product schema advertises $497 / $997** — old Standard/Premium pricing killed 2026-04-09. Canonical is $697 flat single tier. This is currently live.
- **Placeholder phone `+1-000-000-0000`** hardcoded in LocalBusiness schema on all 25 city pages. Invalid schema, breaks NAP consistency.
- **"Free 14-day pilot"** copy on homepage + all 25 cities + 19 vs-* + lp pages. Canonical offer is 200-minute free pilot, not 14 days. Memory `project_pilot_model.md` confirms 200-minute.
- **Zero cross-linking between city pages** — classic orphan-spoke problem.
- **Duplicate content cluster**: `/hvac.html` + `/lp/hvac-answering-service.html` + `/best-hvac-answering-service.html` all target same intent, no canonical chosen. Same for plumbing and electrical verticals.
- **19 vs-* comparison pages ship with only FAQPage schema** — missing Product and Review JSON-LD which matter most for "X vs Y" SERPs.
- Agent 3 also caught a prompt injection attempt embedded in one of the WebFetch responses during the audit and correctly flagged + ignored it. Good defensive behavior.
- Most P0 fixes should land as template changes in `generate_city_pages.py` (or `_template/page-builder.py` — needs verification which one) — one PR → 25 pages fixed.

### Agent 4 — competitor SEO landscape
- Smith.ai has the deepest HVAC page of any generalist (~3,000 words) but sells per-call pricing that confuses HVAC owners who think in minutes.
- Ruby Receptionists: human-only, $235-$1,640/mo, 14-day trial, zero HVAC vertical page.
- Nexa: programmatic city pages, **hides pricing entirely** (biggest weakness), thin HVAC vertical with no testimonials.
- Abby: $99-$1,380/mo, active blog but zero HVAC specificity.
- PATLive: $235+/mo, has a "HVAC Customer Service Playbook" PDF lead magnet, most HVAC-committed human service, but expensive and human-only.
- Answering Service Care: Cloudflare 403'd, minimal HVAC SEO footprint.
- **Wedge positioning locked:** "The only $697 flat-rate AI phone receptionist built specifically for HVAC shops with 1-10 techs, with HVAC triage scripts out of the box, and a 200-minute free pilot — no sales call, no per-minute meter, no contracts."
- **10 keyword opportunities identified**, but 2 flagged invalid: Agent 4 suggested "ServiceTitan AI receptionist integration" and "Housecall Pro answering service" — **Syntharra does NOT have these integrations** (per 2026-04-09 lean cleanup archiving the Premium Dispatchers). Dropping both from the content plan. Replacing the corresponding content piece with "How Syntharra Notifies Your Shop: Email, Slack, SMS in Under 60 Seconds" (documents what we actually have).

## Failures in this session (honest post-mortem)

**Ratio of talking-about-building to actually-building was poor.** ~6 hours session, only 646 lines of code shipped.

1. **Two material hallucinations** cost ~40 min of rework:
   - Put Facebook in the initial Publisher platform list despite memory explicitly saying FB/Meta Business Suite is blocked by the aged-account problem. Caught by Dan.
   - Wrote Blotato form copy claiming Syntharra integrates with Jobber and ServiceTitan. Both CRM integrations were explicitly archived on 2026-04-09 as part of the Pass 1 lean cleanup. STATE.md line 49 says so directly. Caught by Dan.
   - **Root cause:** writing from memory instead of grepping the repo first. Both errors would have been caught by a 10-second grep before writing product copy.
2. **Pricing research done in 4 rounds** when it should have been 1. Higgsfield → PixVerse → back to Higgsfield → verified via screenshot. Each round recomputed things that were already known.
3. **Wrote a 1,400-line plan file for the social video pipeline** (`2026-04-11-autonomous-content-team-implementation.md`) that we're not executing tonight. Fine as documentation for when CRO clears, but it consumed time better spent on code.
4. **Didn't discover the CRO blocker until mid-session.** Should have asked "what external dependencies could block posting?" at the very start of the session, not after locking into the Higgsfield + Blotato subscription path.
5. **`blog_topics` table with 40 queued rows was not discovered until the Agent 2 recon at the END of the session.** If I'd explored the database earlier in the session, the entire day would have pivoted to SEO content engine hours sooner.

## Lessons → rules for next session

1. **Before writing any product copy or feature claim, grep the repo for the claim.** Not memory, not training data. Grep.
2. **At session start, explicitly ask: "what external dependencies or manual blockers exist?"** before locking into any implementation path.
3. **Read STATE.md + the authoritative memory index + recent commits BEFORE writing the first line of anything.** Not during the apology for getting it wrong.
4. **Discover the database state at the start, not at the end.** `list_tables` via Supabase MCP takes 1 second and catches things like "41 rows in blog_topics".
5. **One atomic commit per task. No batching. No "while I'm here" additions.**
6. **Every new executor has `is_X_enabled()` gate defaulting to false.** Nothing runs live without a flag flip.
7. **Pricing research: decide once, move on. Or defer the spend entirely until data justifies it.** Do not re-research a decision that's already made unless the ground facts changed.

## Pickup pointer for next session

See the updated [`## Next session — pick up here`](../STATE.md#next-session--pick-up-here) block in `docs/STATE.md`. The 6 decisions Dan needs to answer are listed there. Execution starts after Dan answers them in the next session.
