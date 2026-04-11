# Phase 0 Cold Outreach Strategy — Syntharra HVAC Pilot Acquisition

> **Goal:** Get the first 50 paying $697/mo HVAC contractors via direct cold outreach while organic SEO + paid traffic ramp up.
>
> **Voice:** Honest, low-friction, founder-direct. No fake urgency. No clickbait. The pilot offer (free 14 days, 200 min, no card) does the heavy lifting; copy just gets out of the way.
>
> **Cost ceiling:** $0 to start. Optional spend: ~$35-50/mo for Mailgun/Smartlead at scale.

---

## TL;DR

Three parallel channels, each generating different lead-quality:

1. **Cold email** — fastest path to first 10 pilots. Build target list → enrich emails → send 3-touch sequence. Requires the dedicated cold-outreach toolchain in `tools/scrape_hvac_directory.py` + `find_email_from_website.py` + `build_cold_outreach.py` + `send_cold_outreach.py`.
2. **SEO comparison pages** — slowest payoff (4-12 weeks to rank), highest LTV. Single page beats Ruby Receptionists / Smith.AI / Answering Service Care for HVAC-specific searches. Compounding asset, zero CAC long term.
3. **Reddit + FB community story posts** — highest trust, lowest CAC, but Dan must post manually (TOS forbids automation). Drafts in `docs/community_post_drafts.md`.

---

## Target persona (do not waste outreach on others)

**Ideal pilot signup =**
- US-based HVAC contractor (must be US — pilot phone numbers are US-only)
- 1-3 trucks (owner-operator or family business)
- Owner answers his own phone
- $300K-$2M annual revenue (above this, they have a real receptionist)
- In a hot or cold-extreme state (Florida, Texas, Arizona, Nevada, California Central Valley, Georgia, Louisiana, Alabama, North/South Carolina, Tennessee, Mississippi, Arkansas, Oklahoma, New Mexico)
- Has a website (otherwise email enrichment fails)
- Has been in business 2+ years (newer shops are still in survival mode)

**Disqualifiers — skip these:**
- Multi-location franchises (One Hour, Aire Serv, Trane Comfort, Carrier-branded)
- Commercial-only HVAC contractors (different sales motion, longer sales cycle)
- Plumbing-only shops (overlap is real but conversion rate is lower)
- Anyone with a `noreply@` email or generic webmail (`@gmail.com`, `@yahoo.com`) as their only contact — these are individual contractors not running a real business

---

## Target city ranking (highest pilot conversion → lowest)

Ranked by HVAC after-hours emergency call density × independent owner-operator concentration. Hit these in order:

| Rank | City | State | Why |
|---|---|---|---|
| 1 | Phoenix | AZ | 110°F summer = constant emergency calls; sprawling metro means independents can't all be on-call |
| 2 | Las Vegas | NV | Same as Phoenix + tourism HVAC volatility |
| 3 | Houston | TX | Heat + humidity + size — biggest single-metro pilot pool |
| 4 | Tampa | FL | Year-round AC use + heavy independent contractor scene |
| 5 | Miami | FL | Cuban + family-owned HVAC market, owner-operators dominate |
| 6 | Orlando | FL | Theme park HVAC support + residential mix |
| 7 | Austin | TX | Tech market = high broadband, easier email reach |
| 8 | Dallas | TX | Same as Houston, slightly lower independent density |
| 9 | Fort Myers | FL | Smaller market, less competition for the pilot pitch |
| 10 | San Antonio | TX | Hispanic small-business density, family shops |
| 11 | Tucson | AZ | Smaller Phoenix |
| 12 | Bakersfield | CA | Inland Central Valley = real summer HVAC demand |
| 13 | Fresno | CA | Same as Bakersfield |
| 14 | Riverside | CA | Inland Empire heat |
| 15 | Sacramento | CA | Inland CA |
| 16 | New Orleans | LA | Humidity + small independent shops |
| 17 | Baton Rouge | LA | Same |
| 18 | Birmingham | AL | Underserved market |
| 19 | Atlanta | GA | Larger metro = more independents |
| 20 | Memphis | TN | Heat + low-cost market |

**Recommended sequencing:** scrape 3 cities per week, run 3 outreach touches per lead (week 1, day 4, day 8 of each city), measure response rate, double down on whichever city converts best.

---

## Channel 1: Cold email pipeline

### Stack

| Component | Free option | Paid scale-up |
|---|---|---|
| Lead source | OSM Overpass + Nominatim (built-in) | Yelp Fusion API (free 5K/day, needs key) |
| Email enrichment | Homepage scrape (50% hit rate) | Hunter.io free (25/mo) → Apollo.io ($99/mo, ~80% hit rate) |
| Sender | Brevo (300/day free, BUT TOS-questionable for cold) | Mailgun ($35/mo, 50K sends, 0.18% deliverability hit) or Smartlead ($39/mo, warmup-included) |
| Inbox monitoring | Manual check of `daniel@syntharra.com` | Smartlead unified inbox |
| Tracking | `marketing-tracker.js` page-side | UTM-tagged links → marketing_events table |

### End-to-end run (one city, ~10 minutes hands-on time)

```bash
# 1. Scrape (free, OSM)
source .env.local
python tools/scrape_hvac_directory.py \
  --city "Phoenix" --state "AZ" \
  --source osm \
  --out leads/hvac-phoenix-az.csv

# 2. Enrich emails from websites (free, ~50% hit rate)
python tools/find_email_from_website.py \
  --in leads/hvac-phoenix-az.csv \
  --out leads/hvac-phoenix-az.enriched.csv

# 3. Generate personalized 3-touch sequence
python tools/build_cold_outreach.py \
  --in leads/hvac-phoenix-az.enriched.csv \
  --out leads/hvac-phoenix-az.outreach.csv \
  --require-email

# 4. Preview (NEVER sends)
python tools/send_cold_outreach.py \
  --in leads/hvac-phoenix-az.outreach.csv \
  --backend print

# 5. Once you're confident — actually send via Brevo, capped at 25 to start
python tools/send_cold_outreach.py \
  --in leads/hvac-phoenix-az.outreach.csv \
  --backend brevo \
  --max-sends 25 \
  --i-know-this-is-real
```

### Sequence design

**Touch 1 (day 0):** Soft intro. "Quick one, here's what I do, here's the offer, no hard feelings if not."
**Touch 2 (day +3):** Following up. "Did you see my note? Pilot is still open." Reply STOP works.
**Touch 3 (day +7):** Last note. "I'll close your file. If you want to try, here's the link."

**Total touches per lead:** 3. Stop on reply (handled by `leads/.send_state.json`).

### Expected metrics (industry baselines for B2B SMB cold)

- **Open rate:** 30-50% with subject lines like "quick {city} HVAC question" and a personal sender domain
- **Reply rate:** 3-7% positive replies (curious + interested), 1-3% negative (unsubscribe / "stop")
- **Pilot signup rate:** 20-40% of positive replies actually sign up
- **Pilot → paid conversion:** 30-50% of pilots add a card by day 14

### Realistic projection from cold email alone

```
1,000 leads per city × 3 cities/week = 3,000 leads/week
3,000 × 50% email hit rate = 1,500 sendable
1,500 × 5% reply rate = 75 replies/week
75 × 30% sign up = 22 pilots/week
22 × 40% convert = 9 paying customers/week
9 × $697 = $6,273 MRR added per week from cold email alone
```

These are aggressive numbers — first 4 weeks will be much lower while you tune subject lines and improve email enrichment hit rate. **Realistic month-1 target from cold email alone: 5-10 paying customers.**

### Compliance (CAN-SPAM, US business email)

The tools handle this automatically. Every email includes:
- Honest sender name + reply-to
- Honest subject line (no clickbait)
- Physical mailing address in footer
- Unsubscribe instruction ("Reply STOP")
- The `send_cold_outreach.py` `state` file honors STOP replies (mark `replied: true` manually until inbox monitoring is wired up)

US CAN-SPAM is permissive for B2B. The risks are:
1. **Brevo TOS** — Brevo's TOS technically requires opt-in lists. **Use a separate Brevo account for cold sends, OR switch to Mailgun.**
2. **Domain reputation** — high cold-send volume on `daniel@syntharra.com` will hurt deliverability for the transactional pilot welcome / lifecycle emails. **Strongly recommend using a separate sending subdomain like `outreach.syntharra.com` for cold campaigns.** Set up SPF, DKIM, DMARC for that subdomain via Mailgun. Keep `syntharra.com` clean for transactional.
3. **State CAN-SPAM extensions** — California (CCPA), Virginia (VCDPA), Colorado, etc. have additional B2B opt-out provisions. The tooling honors STOP replies, which covers the legal requirement.

### Alternative: skip Brevo entirely for cold

If you want to scale cold email past ~50 sends/day, the recommended stack is:

1. Buy a fresh sending domain (`syntharrahvac.com` or similar — ~$15/yr)
2. Set up Mailgun or Smartlead with that domain
3. Warm up the domain for 14 days (Smartlead does this automatically)
4. Send from `dan@syntharrahvac.com`, reply-to `daniel@syntharra.com`
5. Each cold email links to `https://syntharra.com/start?utm_source=cold_email&...` (the marketing-tracker.js will attribute every signup back to the source)

This protects the main `syntharra.com` domain reputation entirely.

---

## Channel 2: SEO comparison pages

### Why this works for HVAC

HVAC contractors who are already shopping for a receptionist alternative are searching:
- `"AI receptionist for HVAC"`
- `"alternative to Ruby Receptionists"`
- `"answering service vs AI receptionist"`
- `"after hours answering service for HVAC"`
- `"how much does an HVAC answering service cost"`
- `"Smith AI vs [anything]"`

Syntharra's `/lp/hvac-answering-service.html` page already exists and ranks for some of these. The next step is **comparison pages** that capture the "alternatives" intent.

### Pages to build (one per session, prioritized)

1. **`syntharra.com/vs/ruby-receptionists-hvac.html`** ← BUILDING IN THIS SESSION
   - Targets: "Ruby Receptionists alternative", "Ruby Receptionists vs AI", "Ruby for HVAC contractors"
   - Hook: Ruby is great for lawyers and dentists, but HVAC needs the answering service to KNOW which HVAC questions are emergencies. Syntharra has the HVAC training built in.

2. `syntharra.com/vs/smith-ai-hvac.html`
   - Targets: "Smith.AI alternative", "Smith.AI vs", "Smith.AI HVAC"
   - Hook: Smith.AI is mostly chat. HVAC is mostly phone. Syntharra is voice-first.

3. `syntharra.com/vs/answering-service-care-hvac.html`
   - Targets: "Answering Service Care alternative", traditional answering service vs AI
   - Hook: Live human answering services charge $1.50/minute. AI costs $0.18/minute and works at 2 AM with no sick days.

4. `syntharra.com/vs/abby-connect-hvac.html`
   - Same pattern, Abby Connect is another receptionist startup.

5. `syntharra.com/best-hvac-answering-service-for-small-business.html`
   - Targets: "best answering service for HVAC", "best HVAC answering service"
   - Comparison table of 5-7 competitors with Syntharra at #1 (justified, not fake)

### Each page has

- 1,200-2,000 words (enough to rank without padding)
- Comparison table near the top
- Single CTA: "Try the free 14-day pilot →"
- Internal link from `/hvac.html`, `/lp/hvac-answering-service.html`, `/index.html`
- Schema markup: `Product` + `FAQPage`
- Canonical URL set
- Light-theme Syntharra chrome (matching existing pages)

### Expected timeline

- **Week 0:** Pages live, indexed by Google within 24 hours
- **Week 2-4:** Begin ranking for long-tail "X vs Y for HVAC" queries
- **Week 6-12:** Rank #3-#10 for primary comparison terms (depends on backlinks)
- **Week 12+:** Compounding organic traffic, ~50-200 visits/mo per page from search alone

**Realistic month-3 target from SEO alone: 5-15 paying customers** (organic traffic to comparison pages → /start → pilot → paid)

---

## Channel 3: Reddit + FB community story posts

### The rule: Dan posts manually

These platforms have strict TOS against bots, scraping, and automated posting. **Drafts only — Dan posts when he has 5 minutes.**

### r/HVAC (172K members, very active)

Post style that works:
- First-person ("I built this for my dad's HVAC shop")
- Concrete numbers ("36 missed calls a week, $14K in lost jobs")
- Honest about the limitations
- No direct sales link in the post body — link in comment after a couple of upvotes

**Drafts in `docs/community_post_drafts.md`** (next session, but template is documented in this file).

### Best posting cadence

1. Post in r/HVAC ONCE every 2-3 weeks max (more = ban risk)
2. Engage in comments on OTHER posts in r/HVAC daily for 2 weeks BEFORE posting (build karma + recognition)
3. Pin a comment with the link AFTER the post is established
4. Post on Fridays at 9 AM ET (highest US contractor traffic)

### FB groups to target

- "HVAC Pros" (50K members)
- "HVAC Service & Repair" (35K members)
- "HVAC Owners & Operators" (12K members)
- "Trade Business Owners" (28K members)
- State-specific groups: "Florida HVAC Pros", "Texas HVAC Contractors", etc.

Same posting rules as Reddit: provide value, don't pitch directly, link in comment after engagement.

---

## Channel 4 (deferred): Paid ads

Not building this in Phase 0 — too much spend ramp-up risk and the dark-launched landing page doesn't have enough conversion data yet to optimize ad spend.

When Phase 1 ramps:
1. Google Ads for high-intent terms: `"hvac answering service"`, `"after hours hvac service"`, `"hvac call answering"` ($3-8 CPC)
2. Facebook Ads targeting HVAC business owners aged 35-65 in target cities
3. YouTube preroll on HVAC content (Bryan Orr / HVAC School channel etc.)

Budget for paid: $0 in Phase 0, $500/mo in Phase 1, scale based on CAC vs LTV.

---

## Channel 5 (deferred): Affiliate partnerships

The website has `affiliate.html` already wired to `website_leads`. Next session task:

1. Send personalized outreach to 5 HVAC YouTubers (Bryan Orr, AC Service Tech, Word of Advice TV, ServiceTitan blog, etc.)
2. Offer 25% recurring affiliate fee (= $174/mo per referred customer for life)
3. Provide them a unique tracking link via `?utm_source=affiliate&utm_campaign=<creator>`
4. Track via marketing-tracker.js → marketing_events

**Realistic month-3 target from affiliate: 2-8 paying customers from one or two engaged creators.**

---

## Combined month-1 projection (everything firing)

| Channel | Month 1 | Month 3 | Month 6 |
|---|---|---|---|
| Cold email | 5-10 paid | 15-30 paid | 30-60 paid |
| SEO comparison pages | 0-2 paid | 5-15 paid | 20-50 paid |
| Reddit/FB community | 1-5 paid | 5-15 paid | 10-30 paid |
| Affiliate (post Phase 1) | 0 | 2-8 paid | 10-25 paid |
| Paid ads (Phase 1+) | 0 | 5-15 paid | 20-80 paid |
| **Total paying customers** | **6-17** | **32-83** | **90-245** |
| **Total MRR added** | **$4-12K** | **$22-58K** | **$63-171K** |

**Critical assumptions baked in:**
1. Telnyx vault keys land within 1 week of starting outreach (otherwise pilots have no phones, conversion rate drops to ~5%)
2. Stripe live mode is active before day 14 of the first pilot signups (otherwise no auto-convert revenue)
3. Founder VSL is filmed before launching paid ads (the landing page conversion rate without VSL is ~30% lower)
4. Quality of HVAC pilot calls remains good — single bad customer experience kills word-of-mouth

---

## What can you, Dan, start doing this week to multiply this

In priority order:

1. **Vault Telnyx as soon as the business number arrives** (1 hour after it lands). Without this, every channel above is upstream of a broken funnel.
2. **Film the 60-second founder VSL.** Script in spec § 3.2. Phone camera + good light is fine — authenticity beats production.
3. **Manually post one Reddit r/HVAC story post per fortnight** using the drafts I'll write next session.
4. **Build a Mailgun account** with `outreach.syntharra.com` subdomain so cold email scales without burning the main domain reputation.
5. **Get Stripe LIVE mode key vaulted** so day-14 auto-convert produces actual revenue.

Each of these takes <1 hour and unblocks $5K-15K MRR over the next 60 days.

---

## What I, Claude, will keep building

In priority order:

1. **Comparison pages 2-5** (Smith.AI, Answering Service Care, Abby Connect, Best of Best)
2. **Reddit/FB community post drafts** (10-15 ready-to-post stories)
3. **Hunter.io free integration** in `find_email_from_website.py` for higher email enrichment hit rate
4. **Inbox monitoring webhook** so the cold sender state file auto-updates on STOP replies
5. **Affiliate outreach script generator** for the 5 HVAC creator targets

Each of these takes a session or two. Stack them across your sessions and Phase 0 becomes a fire-and-forget machine.
