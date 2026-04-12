# Marketing team cost tracker

> **Purpose:** transparent ledger of what Syntharra's marketing machine costs to run, at each stage of growth, so Dan can see the ROI before investing more. Updated whenever we add a paid tool or hit a new client milestone.

**Last updated:** 2026-04-11

---

## Current state (0 paying clients, 0 pilots running)

Per-month spend right now, excluding Dan's own time:

| Line item | Cost/mo | Status | Notes |
|---|---|---|---|
| n8n Railway hosting | ~$20 | **active** | Shared with production onboarding + billing workflows, not marketing-only |
| Supabase | $0 | **active** | Free tier — comfortably under limits |
| Brevo transactional | $0 | **active** | Free tier (300/day = ~9,000/mo), way under quota at Phase 0 volumes |
| Hunter.io | $0 | **active** | **Free tier — 25 domain searches/month.** Key vaulted 2026-04-11. Auto-used as fallback in `tools/find_email_from_website.py` when homepage scrape misses. |
| OpenStreetMap / Overpass | $0 | **active** | Lead scraping via `tools/scrape_hvac_directory.py` (stdlib, no API key) |
| Stripe (test mode) | $0 | **active** | No transaction fees until live mode |
| Mux | $0 | **inactive** | Key vaulted but no VSL uploaded yet |
| Retell AI | $0 | **inactive** | No live calls yet (Telnyx not vaulted — pilots can't receive calls) |
| Telnyx | $0 | **inactive** | Not vaulted yet (waiting on Dan's business number) |
| Railway cron (this repo) | ~$5 | **active** | Shared hosting for billing crons + (soon) pilot lifecycle cron |
| **Total** | **~$25/mo** | | Almost entirely fixed infra, not per-marketing-spend |

**Interpretation:** Syntharra's marketing machine currently costs about $25/month to run and produces zero paying clients. This is the "it's infrastructure, not marketing" baseline. The actual marketing work (cold outreach, SEO, community posts, affiliate outreach) all ride on free tiers. The ~$25 is just the rails.

---

## Dan's phased budget (agreed 2026-04-11)

Dan's direction on paid marketing spend:

> "We need to sign at least 2 clients through the syntharra marketing team before I'm willing to pay for this [Hunter.io paid tier, Yelp Fusion, paid ads]. Once we get 10+ clients through the marketing team without needing my input, I will go all in on whatever you recommend to get this off the ground and get unlimited leads."

### Unlock stages

| Stage | Trigger | Budget unlock | What it enables |
|---|---|---|---|
| **0** (now) | Phase 0, pre-signups | $25/mo | Free-tier everything. Prove the machine works without spending more. |
| **1** | 2 clients signed via the marketing team | $300-$500/mo additional | Hunter.io paid tier ($49-$99/mo), Yelp Fusion API (if useful), paid transactional email beyond Brevo free, small paid community ads. |
| **2** | 10+ clients signed without Dan's manual input | Uncapped ("go all in") | Paid search ads (Google Ads, Bing), paid social (Facebook/Meta, LinkedIn), sponsored placements in HVAC trade publications, paid affiliate commissions, scaled cold outreach via Mailgun/Smartlead. |

**"Through the marketing team" definition:** a client who came in via autonomous channels (cold outreach, SEO organic traffic, community post clicks, affiliate referrals). NOT counted: Dan's friends-of-friends, Dan-initiated referrals, word-of-mouth from existing clients, Dan doing his own Reddit AMA.

---

## Paid tools waiting at Stage 1

These are vaulted-but-disabled or ready-to-sign-up-for when we cross the 2-client threshold. Don't turn them on yet.

| Tool | Stage 1 cost/mo | Marginal value | Notes |
|---|---|---|---|
| **Hunter.io Starter** | $49 | 1,000 searches/mo, up from the free 25. Unlocks ~50→~75% enrichment hit rate on ALL cold outreach batches, not just the first 25 domains. | Already vaulted (free tier); upgrade = `UPDATE syntharra_vault SET key_value=...` and Stripe signup on hunter.io. |
| **Yelp Fusion** | ~$229-$299+ | Unknown — Yelp's API pricing is custom and NOT published. Dan's earlier estimate was $300+/mo. Would enable higher-volume lead scraping beyond what OpenStreetMap covers. | **Do not pursue** until Stage 1 is crossed AND Dan confirms quote. Strong risk of sticker shock. |
| **Mailgun Foundation** | $35 | 50,000 transactional emails/mo — enables real cold outreach sending at scale (currently Brevo's 300/day free tier caps us at ~9k/mo and burns deliverability if we push that hard). | Preferred Stage 1 upgrade. Apollo/Smartlead are the Stage 2 upgrade path. |
| **Ahrefs Lite / Semrush Lite** | $99-$139 | Real SEO rank tracking on the 9 comparison pages, keyword research for pages 10-20, competitor backlink analysis. | Nice-to-have. Google Search Console is free and gives us 80% of the signal. |
| **Apollo.io (free tier)** | $0 | B2B contact database with HVAC filters; 50 credits/mo free. Complements Hunter.io. | Free tier available now — can test without spending. |
| **Stage 1 total (conservative)** | **~$130-$235/mo** | | Hunter.io Starter + Mailgun Foundation + optional Ahrefs Lite |

---

## Stage 2 (10+ clients) investment menu

When Dan greenlights "go all in," here's the recommended allocation. Each entry is a hypothesis to test with a ~4-week budget before doubling down.

| Channel | Monthly test budget | Expected CAC | Hypothesis |
|---|---|---|---|
| **Google Ads — "hvac answering service" + branded terms** | $1,000 | $200-$500 per lead | High intent, low volume. Anchor the top 5 comparison pages against the highest-intent keywords. |
| **Facebook/Meta Lead Ads — HVAC business owners** | $800 | $50-$150 per lead (unqualified) | Broad reach into owner-operator audience; lower quality than search but massive top-of-funnel. |
| **LinkedIn Sponsored Content — HVAC owners + GM titles** | $600 | $300-$800 per lead | B2B quality filter via job-title targeting. Worth testing but LinkedIn is brutal on cost. |
| **Reddit Ads — r/HVAC, r/HVACTech, r/smallbusiness** | $300 | $50-$200 per lead | Highly targeted but Reddit audiences are ad-averse. Community posts (free) might outperform paid ads here. |
| **Trade publication sponsorships** (ACCA Now, Contracting Business, HVAC-Talk) | $500-$1,500 flat | Varies | One-off buys, harder to measure directly. Use for brand-building once the comparison pages are indexed. |
| **YouTube affiliate commissions** (HVAC YouTuber partnerships from `build_affiliate_outreach.py`) | $2,500/signup (30% year 1) | Pay-per-outcome — no upfront risk | The `build_affiliate_outreach.py` tool is already built. Needs landing page at `/affiliate?ref=slug` — already exists at `affiliate.html`. Just needs to be activated at Stage 1. |
| **Paid cold outreach at scale** (Smartlead/Instantly + warmed domains) | $200-$500 + $50-$100 per domain warmup | $20-$100 per lead | Biggest scale lever once the 3-touch sequence is validated on free Mailgun tier. |
| **Stage 2 total (conservative)** | **~$5,000-$8,000/mo** | | Assuming all channels are running in parallel. Actual spend should be reallocated weekly based on CAC. |

---

## Target CAC ranges

Guidelines for when each stage makes sense:

| Stage | Revenue/mo per client | Max sustainable CAC | Rationale |
|---|---|---|---|
| Stage 0 (0-2 clients) | $697 | ~$500 | First clients are validation, not profit. Any CAC under $700 = net positive first month. |
| Stage 1 (2-10 clients) | $697 | $300-$400 | Need to maintain >50% gross margin after Retell COGS. |
| Stage 2 (10+ clients) | $697 | $200-$300 | Scale economics kick in; lower CAC = higher growth rate. |
| Stage 3 (50+ clients, not yet planned) | $697 → $997 (tier upgrade?) | $400-$600 | At 50 clients the pricing model likely changes; higher LTV justifies higher CAC. |

---

## Cost allocation to "the marketing team"

Dan asked that Hunter.io and Yelp costs be included in the marketing team's total monthly cost, not buried in infra. Here's the convention:

**"Marketing team cost" = all tools, services, and infra directly attributable to acquiring new clients**

Included:
- Lead scraping infrastructure (OSM free, Yelp Fusion paid when unlocked)
- Lead enrichment (Hunter.io free/paid, Apollo free tier)
- Outreach sending (Brevo/Mailgun/Smartlead)
- Ad spend (Google/Facebook/LinkedIn/Reddit)
- Affiliate commissions (paid per conversion, not monthly)
- Content hosting (the 9 live comparison pages, hosted on GitHub Pages = free)
- Comparison page SEO tooling (Search Console free, Ahrefs/Semrush paid when unlocked)

Excluded (not marketing, operations):
- n8n Railway hosting (billing + onboarding infra, not marketing)
- Supabase (storage + auth, not marketing)
- Retell AI minutes (product delivery, not marketing)
- Twilio/Telnyx (product delivery, not marketing)

**Current marketing-team-attributable cost:** **$0/mo** (all tools on free tiers).

---

## Tracking

- **Weekly funnel rollup:** `python tools/marketing_digest.py --since 7d --output text`. Reads marketing_events + client_subscriptions + cold outreach send state, outputs leads → pilots → conversions. First run will show near-zero across the board because no traffic is indexed yet; the comparison pages went live 2026-04-11.
- **Daily Slack digest (future):** `python tools/marketing_digest.py --post-to-slack --since 1d` in a Railway cron. Not yet deployed.
- **Per-client CAC:** computed in `marketing_digest.py` by dividing total cold-outreach send cost (~$0.0004/email × sends) by paid conversions in the same window. Crude until we have a real cost ledger, but honest.

---

## Decision log

- **2026-04-11:** Hunter.io free tier (25 searches/mo) approved. Key vaulted as `service_name='Hunter.io', key_type='api_key'`. Auto-used as fallback in `find_email_from_website.py` when homepage scrape misses. No upgrade to paid tier until Stage 1 trigger.
- **2026-04-11:** Yelp Fusion kept disabled. Dan estimates ~$300/mo. Revisit at Stage 1 trigger, and only if we need lead volume beyond what OSM + Hunter.io provide.
- **2026-04-11:** Paid ads deferred to Stage 2. Current strategy is free-channel-only: SEO, cold outreach, community posts, affiliate outreach. Dan agreed.
- **2026-04-11:** Retell MASTER promotion gated on Dan's manual verification of the pilot_expired flow branch on TESTING. No auto-promote per retell-iac/CLAUDE.md rules.
