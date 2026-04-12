# Google Search Console Setup — Syntharra SEO Activation

> **Time required:** ~15 minutes. One-time setup. Gets 82 pages indexed by Google.
> **Why now:** 82 landing pages are live but Google doesn't know they exist yet. Without this, the SEO work produces zero traffic.

---

## Step 1 — Add syntharra.com property (5 min)

1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Sign in with the Google account you use for Syntharra
3. Click **Add property** → choose **Domain** (not URL prefix) → type `syntharra.com`
4. You'll be given a DNS TXT record to add. It looks like:
   `google-site-verification=xxxxxxxxxxxxxxxxxxxxxxx`
5. Add that TXT record to your DNS provider (wherever syntharra.com DNS is managed — likely Cloudflare, Namecheap, or GoDaddy):
   - Log into your DNS provider
   - Add a new **TXT record** with host `@` (root domain) and value = the verification string
   - TTL: any value (300 is fine)
6. Back in Search Console, click **Verify**
   - DNS propagation can take up to 24h but usually works in minutes
   - If it fails immediately, wait 5 minutes and try again

---

## Step 2 — Submit the sitemap (2 min)

Once verified:
1. In Search Console left sidebar → **Sitemaps**
2. In "Add a new sitemap" field, enter: `sitemap.xml`
3. Click **Submit**
4. Status should show "Success" within a few minutes (sometimes longer)

The sitemap at `https://syntharra.com/sitemap.xml` currently contains **82 URLs** including:
- All 21 brand comparison pages (vs-ruby-receptionists, vs-smith-ai, etc.)
- All 15 city landing pages (hvac-answering-service-atlanta, etc.)
- 21 blog posts
- 3 landing pages (lp/)
- Core site pages (index, start, about, etc.)

---

## Step 3 — Request indexing for priority pages (5 min)

Google's crawler will eventually find everything from the sitemap, but you can speed up the most important pages:

1. In Search Console → **URL Inspection** (search bar at top)
2. Paste each URL below, then click **Request Indexing** for each:

**Priority 1 — High-intent comparison pages (submit these first):**
- `https://syntharra.com/vs-smith-ai.html`
- `https://syntharra.com/vs-ruby-receptionists.html`
- `https://syntharra.com/vs-answering-service-care.html`
- `https://syntharra.com/vs-abby-connect.html`
- `https://syntharra.com/best-hvac-answering-service.html`

**Priority 2 — High-intent city pages (pick your top markets):**
- `https://syntharra.com/hvac-answering-service-phoenix.html`
- `https://syntharra.com/hvac-answering-service-dallas.html`
- `https://syntharra.com/hvac-answering-service-houston.html`
- `https://syntharra.com/hvac-answering-service-las-vegas.html`
- `https://syntharra.com/hvac-answering-service-miami.html`

**Priority 3 — Core pages:**
- `https://syntharra.com/`
- `https://syntharra.com/start.html`
- `https://syntharra.com/partners.html`

You can only request indexing for ~10 URLs per day via manual inspection. Start with Priority 1 and let the sitemap handle the rest automatically over 2-4 weeks.

---

## Step 4 — Set up performance monitoring (3 min)

In Search Console → **Performance** → **Search results**:

- Set date range to **Last 28 days**
- Check "Clicks", "Impressions", "CTR", "Position" checkboxes
- This is your organic traffic dashboard

**Key metrics to watch:**
| Metric | What it means | Good sign |
|---|---|---|
| Impressions | Google showed your page in search results | Any impressions = indexed |
| Clicks | Someone clicked through | > 0 per week within 30 days |
| Position | Average rank (1 = top result) | < 50 means you're appearing |
| CTR | Click-through rate | > 3% is strong for commercial terms |

---

## What to expect (timeline)

| Timeline | What happens |
|---|---|
| Day 1-3 | Google discovers sitemap, starts crawling |
| Week 1-2 | Priority pages start appearing in search results at low positions (50-100+) |
| Week 4-8 | Pages with good content + no competition start climbing to positions 20-50 |
| Month 3-6 | SEO compound effect kicks in — comparison pages for lower-competition brands can hit page 1 |

The city pages (e.g., "HVAC answering service Phoenix") have much lower competition than the brand comparison pages and may rank faster.

---

## Optional — Link Search Console to Google Analytics

If you have Google Analytics on syntharra.com:
1. Search Console → Settings → Associations → Link to Google Analytics property
2. This lets you see which search queries drive conversions, not just traffic

---

## Recurring maintenance (monthly, 5 min)

1. Run `python tools/generate_sitemap.py` after adding any new pages
2. Re-submit sitemap in Search Console
3. Check Performance report for any pages with high impressions but low CTR (title/description needs tweaking)

The sitemap generator is at `tools/generate_sitemap.py` — run it any time new pages are added to `syntharra-website/`.
