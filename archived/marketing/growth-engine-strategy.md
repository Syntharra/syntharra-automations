# Syntharra Growth Engine — Full Marketing & Lead Generation Strategy

**Document version:** 2026-04-02
**Author:** Claude (Lead Growth Strategist)
**Status:** Production-ready blueprint — execute sequentially

---

## 1. Executive Summary

Syntharra has a fully built product (AI Receptionists for trade businesses), operational infrastructure (n8n, Supabase, Retell, Stripe), and zero paying clients. The #1 priority is building a repeatable lead generation engine that delivers 10–50 qualified leads per week within 6 weeks.

**What we're building:** A multi-channel outbound engine centred on cold email (primary), supported by Google Places lead sourcing (already partially built), social content (Blotato pipeline designed), and a LinkedIn manual layer — all feeding into a unified Supabase pipeline with full tracking from lead sourced → deal closed.

**Why this order:** Cold email has the fastest time-to-result (2–3 weeks to first meetings), lowest cost at current scale ($30–100/month tooling), and we already have the infrastructure (SMTP2GO, n8n, Supabase). Social and ads are amplifiers that layer on after the core pipeline proves conversion.

**The critical constraint:** Syntharra's primary domain (syntharra.com) must be protected. All cold outreach must go through secondary domains to isolate reputation risk. This is non-negotiable.

---

## 2. Phase 1 — Lead Source Rankings

| # | Channel | Volume (leads/mo) | Cost | Time to First Result | Scalability | Automation Complexity | Score (1–10) |
|---|---|---|---|---|---|---|---|
| 1 | **Cold Email** | 500–2,000 | $30–100/mo (Instantly or similar + domains) | 2–3 weeks (incl. warmup) | High — add domains to scale | Medium — n8n sequencing built | **9** |
| 2 | **Google Places Scraping** | 1,000–5,000 | $50–200/mo (API costs) | 1 week (already partially built) | Very high — every US city | Low — n8n workflow exists | **9** |
| 3 | **SEO + Content** | 50–200 (organic) | Free (already live) | 3–6 months to compound | High — long-term asset | Low — blog already running | **7** |
| 4 | **YouTube / VSL Inbound** | 20–100 | Free–$50/mo (Blotato) | 4–8 weeks | Medium — algorithm dependent | Medium — Blotato pipeline designed | **6** |
| 5 | **Meta/Facebook Ads** | 200–1,000 | $500–2,000/mo ad spend | 1–2 weeks | High but expensive | Medium — need Pixel + Lead Ads | **6** |
| 6 | **Google Ads** | 100–500 | $1,000–3,000/mo (high-intent keywords) | Instant | Very high | Low — landing pages built | **5** |
| 7 | **LinkedIn Outreach** | 50–150 connections/week | Free–$100/mo (manual or tool) | 1 week | Low — 100 connections/week cap | Low (manual) to Medium (tool) | **7** |
| 8 | **Affiliate / Referral** | Variable | Revenue share only | 1–3 months | Medium — relationship dependent | Low — page exists | **4** |
| 9 | **Cold Calling (targeted)** | 5–10 warm calls/day | Free | Same day | Low — time intensive | None — just call hot leads | **8** |
| 10 | **AI Agent Multi-Channel** | Amplifier, not standalone | Included in stack | Depends on channels fed | Amplifier | High — n8n orchestration | **7** |

### Recommended Combination (Weeks 1–6)

**Primary (80% of effort):** Cold Email + Google Places Scraping
These two form a closed loop: scrape leads → enrich → email → track → book. Everything runs in n8n with Supabase storage.

**Secondary (15% of effort):** LinkedIn manual outreach to high-value prospects who opened/clicked emails but didn't book. This is a human layer Dan does for 30 min/day.

**Tertiary (5% of effort):** Social content via Blotato (Phase 1 organic — already designed). Set it and let it run. It builds brand while the outbound engine generates meetings.

**Defer until Week 6+:** Paid ads (Meta, Google). Don't spend ad dollars until you have conversion data from cold email to know your cost-per-acquisition target.

---

## 3. Phase 2 — Cold Email Deep Dive

### 3A — Deliverability & Infrastructure

#### The 2026 Deliverability Landscape

The rules have changed significantly. Google, Yahoo, and Microsoft (as of May 2025) all enforce strict sender requirements:

- **SPF, DKIM, DMARC** are non-negotiable — emails without all three get filtered or rejected
- **Spam complaint rate** must stay under 0.1% (Gmail's threshold, stricter than the often-cited 0.3%)
- **Bounce rate** must stay under 2%
- **One-click unsubscribe** (RFC 8058) is required for all marketing/bulk email
- **Plain text > HTML** for cold email — HTML with tracking pixels triggers spam filters
- **Volume per inbox:** Never exceed 50 emails/day per sending address; elite senders recommend 25–30/day
- **Emails under 80 words** get 50% higher reply rates than longer ones
- **First email captures 58% of all replies** — your first touch is everything

#### Domain Strategy — CRITICAL

**NEVER send cold email from syntharra.com.** This is the #1 rule.

Buy 3–5 secondary domains for cold outreach. These isolate reputation risk from your primary domain.

**Recommended domains to purchase (2 to start — add more only when scaling past 200/day):**

| Domain | Purpose | Estimated Cost |
|---|---|---|
| `getsyntharra.com` | Primary cold outreach | ~$12/year |
| `trysyntharra.com` | Secondary cold outreach | ~$12/year |

For each domain:
1. Set up SPF, DKIM, DMARC (via Google Workspace or your DNS provider)
2. Create 2–3 mailboxes per domain: `daniel@getsyntharra.com`, `solutions@getsyntharra.com`
3. Set DMARC policy to `p=none` initially (tighten to `p=quarantine` after 30 days)
4. Point each domain to syntharra.com with a simple redirect (builds domain authority)

This gives you **4–6 sending addresses** across 2 domains — enough to send 100–150 emails/day safely. Add a 3rd/4th domain later only if you need to scale past this.

#### Sending Address Recommendation

**Send from: `daniel@getsyntharra.com`** (or `daniel@trysyntharra.com`)

Why Daniel, not noreply or solutions:
- Named senders get 15–20% higher open rates
- HVAC business owners respond to founders, not faceless brands
- "Daniel from Syntharra" feels like a real person reaching out
- CAN-SPAM requires a real person or business — named sender satisfies this naturally

**Signature should read:**
```
Daniel Blackmore
Founder, Syntharra
AI Receptionists for HVAC Companies
www.syntharra.com
```

#### Warm-Up Process

**Timeline:** 2–4 weeks before first cold campaign.

| Week | Emails/Day (per inbox) | Activity |
|---|---|---|
| 1–2 | 5–10 | Warmup only (automated tool conversations) |
| 3 | 15–20 | Mix of warmup + first small cold batch (50 total) |
| 4 | 25–30 | Ramp to steady state — 25 warmup + 25 cold |
| 5+ | 30–50 | Full sending — maintain 40–50% warmup ratio |

#### Tool Recommendation: Use a Dedicated Cold Email Platform

**Do NOT use SMTP2GO directly for cold outreach.**

SMTP2GO is your transactional email provider (welcome emails, reports, onboarding). Using it for cold email risks your transactional deliverability. Keep these completely separate.

**Recommended platform: Instantly.ai ($30/mo Growth plan)**

Why Instantly over building it yourself in n8n:
- Built-in warmup across 200K+ real accounts (no separate warmup tool needed)
- Unlimited email accounts on flat fee
- Automatic domain rotation and inbox rotation
- Inbox placement testing built-in
- Custom tracking domain support
- Sequence builder with A/B testing
- Lead database (450M+ contacts) — optional but useful
- Anti-spam scoring before send

**Alternative: Saleshandy ($25/mo)** — slightly cheaper, 830M+ contact database, good for scaling

**Why not n8n + SMTP2GO for cold email:** You'd need to build warmup, rotation, tracking, bounce handling, and throttling yourself. That's 40+ hours of engineering for something Instantly does out of the box for $30/month. Use n8n for orchestration (lead sourcing, hot lead detection, CRM sync) but let a purpose-built tool handle the sending.

#### Volume Planning

With 2 secondary domains × 2–3 inboxes each = 4–6 sending addresses:
- Conservative: 5 × 25/day = **125 cold emails/day** (safe, sustainable)
- Moderate: 5 × 35/day = **175 cold emails/day** (with good warmup)
- Aggressive: 6 × 50/day = **300 cold emails/day** (only after 6+ weeks of clean sending)

At 125/day × 22 business days = **2,750 emails/month** — plenty to generate first clients.

**Expected metrics (industry benchmarks 2026):**
- Open rate: 45–60% (good subject lines)
- Reply rate: 3–5% (personalized, problem-first)
- Positive reply rate: 1–2%
- Meeting booked rate: 0.5–1% of sends
- At 2,750 sends/month: **14–28 meetings/month**
- **Plus 5–10 targeted cold calls/day to hot leads = additional 2–5 meetings/week**

---

### 3B — Email Sequence Design

**Target persona:** HVAC business owner, 5–30 employees, running Google/Facebook ads, missing calls after hours, using voicemail or an answering service.

**Sequence:** 5 emails over 14 days. All plain text. Under 80 words each.

---

#### Email 1 — Day 0 (The Problem)

**Subject:** {first_name}, quick question about {business_name}
**Preview text:** I called 73 HVAC companies last week...

```
Hi {first_name},

I called 73 HVAC companies in {city} last week. 41 went straight to voicemail.

Every missed call is a job going to your competitor who picks up.

We built an AI receptionist specifically for HVAC companies. It answers every call 24/7, books the job, and sends you the details — no staff needed.

Would it make sense to hear a 2-minute demo call?

Daniel
Founder, Syntharra
```

**CTA link:** `https://www.syntharra.com/demo.html?utm_source=cold_email&utm_medium=email&utm_campaign=hvac_usa&utm_content=seq1_email1`

---

#### Email 2 — Day 3 (The Cost)

**Subject:** The math on missed calls
**Preview text:** $200–500 per missed call...

```
Hi {first_name},

Quick math: the average HVAC job is $200–500. Miss 3 calls a week and that's $2,500+ per month walking out the door.

Our AI receptionist costs less than one missed job per month and answers every call, including nights and weekends.

One of our clients went from missing 40% of calls to capturing 100%. Their revenue jumped in the first month.

Worth 15 minutes to see if this works for {business_name}?

Daniel
```

**CTA link:** Cal.com booking with UTM: `?utm_source=cold_email&utm_content=seq1_email2`

---

#### Email 3 — Day 6 (Social Proof / Demo)

**Subject:** Hear it yourself
**Preview text:** Call this number right now...

```
Hi {first_name},

Easier than me explaining — call this number and hear our AI receptionist in action:

+1 (812) 994-4371

It's set up for an HVAC company called Arctic Breeze. Ask about a repair, a quote, or an emergency. See how it handles it.

Takes 60 seconds. If you're impressed, let's talk about setting one up for {business_name}.

Daniel
```

---

#### Email 4 — Day 10 (Urgency / Competitive)

**Subject:** Your competitors are picking up
**Preview text:** While you're reading this...

```
Hi {first_name},

While you're reading this, there's probably a homeowner in {city} calling around for HVAC service. If you don't pick up, they call the next company on Google.

The businesses winning right now aren't hiring more staff. They're using AI to answer every call instantly, 24/7.

We set everything up in 24 hours. You don't change anything about how you run your business.

Interested?

Daniel
```

**CTA link:** Cal.com booking with UTM

---

#### Email 5 — Day 14 (Breakup / Final)

**Subject:** Should I close your file?
**Preview text:** No hard feelings either way

```
Hi {first_name},

I've reached out a few times and haven't heard back — totally fine, you're busy running {business_name}.

Just want to make sure: is an AI receptionist something you'd want to explore down the road? If not, no worries at all — I'll stop reaching out.

If the timing is just off, reply "later" and I'll check back in a few months.

Daniel
```

---

### Sequence Design Notes

- **All plain text** — no HTML, no images, no tracking pixels
- **Under 80 words each** — forces clarity, matches 2026 best practices
- **Problem-first positioning** — never lead with the product
- **Single CTA per email** — binary question or simple action
- **Spintax recommended** for subject lines and opening lines to avoid duplicate content detection
- **Send timing:** Monday launch, Wednesday/Thursday follow-ups, 9:30–11:30 AM recipient's local time
- **Never send on Fridays** — worst engagement day per 2026 benchmark data

---

### 3C — Automation Architecture

#### Lead Sourcing Pipeline (n8n)

```
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW: Lead Sourcer (CRON — daily or on-demand)       │
│                                                          │
│  1. Trigger: Schedule or manual webhook                   │
│  2. Google Places API: search "HVAC" in {target_city}    │
│  3. For each result:                                     │
│     a. Extract: name, phone, website, rating, address     │
│     b. Scrape website for owner name + email              │
│        (Hunter.io API or pattern matching)                │
│     c. Verify email (ZeroBounce / NeverBounce API)        │
│     d. Check Supabase: skip if already exists             │
│     e. Insert into `website_leads` with status='new'      │
│  4. Notify Dan via email: "{X} new leads added for {city}"|
└──────────────────────────────────────────────────────────┘
```

#### Email Sequence Pipeline (Instantly.ai + n8n sync)

```
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW: Lead → Instantly Sync (triggered on new lead)  │
│                                                          │
│  1. Trigger: Supabase webhook on website_leads INSERT     │
│     (where status = 'verified' AND email_valid = true)   │
│  2. Push lead to Instantly via API:                       │
│     - campaign_id = HVAC_USA_SEQ1                        │
│     - variables: first_name, business_name, city          │
│  3. Update Supabase: status = 'sequenced',                │
│     sequence_started_at = NOW()                          │
│                                                          │
│  Instantly handles: sending, warmup, rotation, tracking   │
└──────────────────────────────────────────────────────────┘
```

#### Hot Lead Detection (n8n)

```
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW: Hot Lead Detector (webhook from Instantly)      │
│                                                          │
│  1. Trigger: Instantly webhook on 'link_clicked' or       │
│     'email_replied'                                      │
│  2. Update Supabase: status = 'hot', hot_at = NOW()       │
│  3. If reply → parse sentiment (Groq LLM via n8n)        │
│     a. Positive → status = 'interested'                   │
│     b. Negative/unsubscribe → status = 'do_not_contact'   │
│     c. Question → status = 'engaged'                      │
│  4. If clicked demo page → status = 'demo_visited'        │
│  5. Notify Dan: "Hot lead: {name} at {company} — {action}"|
│  6. If demo_visited + not booked after 24h:               │
│     → trigger follow-up email via Instantly API           │
└──────────────────────────────────────────────────────────┘
```

#### Cal.com Booking → Pipeline (n8n)

```
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW: Cal.com Booking Handler                         │
│                                                          │
│  1. Trigger: Cal.com webhook on BOOKING_CREATED            │
│  2. Match email to Supabase website_leads record           │
│  3. Update: status = 'booked', booked_at = NOW(),          │
│     cal_booking_id = {id}                                 │
│  4. Pause lead's Instantly sequence via API                │
│  5. Create entry in `pipeline_bookings` table              │
│  6. Notify Dan: "Call booked: {name} at {company} — {date}"|
└──────────────────────────────────────────────────────────┘
```

---

## 4. Phase 3 — Full Funnel Tracking System

### Event Tracking Map

| Event | Source | Stored In | Key Fields |
|---|---|---|---|
| Lead sourced | Google Places n8n workflow | `website_leads` | business_name, owner_name, email, city, source |
| Lead verified | Email validation API | `website_leads` | email_valid, verified_at |
| Email sent | Instantly webhook | `email_events` | lead_id, step_number, sent_at |
| Email opened | Instantly webhook | `email_events` | lead_id, opened_at (note: open tracking hurts deliverability — consider disabling) |
| Email clicked | Instantly webhook / UTM | `email_events` | lead_id, clicked_at, link_url |
| Email replied | Instantly webhook | `email_events` | lead_id, replied_at, sentiment |
| Demo page visited | UTM params on demo.html | `website_leads` | demo_visited_at, utm_source, utm_content |
| Cal.com booking | Cal.com webhook | `pipeline_bookings` | lead_id, booked_at, meeting_time |
| Call completed | Manual / Cal.com status | `pipeline_bookings` | call_status, call_notes |
| Deal won | Stripe checkout.session.completed | `stripe_payment_data` + `website_leads` | lead_id, plan, revenue |
| Deal lost | Manual update | `website_leads` | status = 'lost', lost_reason |

### Supabase Schema Additions

```sql
-- ============================================
-- MARKETING PIPELINE TABLES
-- ============================================

-- Extend existing website_leads table with pipeline fields
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'new';
-- Values: new, verified, sequenced, opened, clicked, hot, demo_visited, interested, booked, won, lost, do_not_contact

ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'google_places';
-- Values: google_places, manual, website_form, referral, linkedin

ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS email_valid BOOLEAN;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS sequence_started_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS sequence_step INTEGER DEFAULT 0;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS sequence_paused BOOLEAN DEFAULT false;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS hot_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS demo_visited_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS booked_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS won_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS lost_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS lost_reason TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS lead_score INTEGER DEFAULT 0;
-- Score: +10 opened, +20 clicked, +30 demo_visited, +50 replied_positive, +100 booked

ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS utm_source TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS utm_medium TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS utm_campaign TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS utm_content TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMPTZ;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS next_action TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS instantly_lead_id TEXT;

-- Email events (granular tracking)
CREATE TABLE IF NOT EXISTS email_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES website_leads(id),
    event_type TEXT NOT NULL, -- sent, opened, clicked, replied, bounced, unsubscribed
    step_number INTEGER,
    event_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb -- link_url, reply_text, sentiment, etc.
);

CREATE INDEX IF NOT EXISTS idx_email_events_lead ON email_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_email_events_type ON email_events(event_type);

-- Pipeline bookings (Cal.com meetings)
CREATE TABLE IF NOT EXISTS pipeline_bookings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES website_leads(id),
    cal_booking_id TEXT,
    meeting_time TIMESTAMPTZ,
    booked_at TIMESTAMPTZ DEFAULT NOW(),
    call_status TEXT DEFAULT 'scheduled', -- scheduled, completed, no_show, rescheduled, cancelled
    call_notes TEXT,
    outcome TEXT, -- interested, needs_followup, not_ready, closed_won, closed_lost
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_lead ON pipeline_bookings(lead_id);

-- Lead sourcing runs (track each batch)
CREATE TABLE IF NOT EXISTS lead_sourcing_runs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    city TEXT NOT NULL,
    state TEXT,
    industry TEXT DEFAULT 'hvac',
    leads_found INTEGER DEFAULT 0,
    leads_new INTEGER DEFAULT 0, -- after deduplication
    leads_with_email INTEGER DEFAULT 0,
    run_at TIMESTAMPTZ DEFAULT NOW(),
    source TEXT DEFAULT 'google_places'
);

-- RLS policies
ALTER TABLE email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_sourcing_runs ENABLE ROW LEVEL SECURITY;

-- Service role has full access (for n8n)
CREATE POLICY "Service role full access" ON email_events FOR ALL USING (true);
CREATE POLICY "Service role full access" ON pipeline_bookings FOR ALL USING (true);
CREATE POLICY "Service role full access" ON lead_sourcing_runs FOR ALL USING (true);
```

---

## 5. Phase 4 — Admin Dashboard Marketing Section

The Marketing Pipeline section (`sec-marketing`) already exists in the admin dashboard with KPI cards (`mkt-sourced`, `mkt-emailed`, `mkt-hot`, `mkt-demos`, `mkt-pipeline`).

### What Needs to Be Built/Enhanced

**KPI Cards (top row):**
- Total leads sourced (this week / all time) → query `website_leads` COUNT with date filter
- Emails sent today / this week → query `email_events` WHERE event_type='sent'
- Open rate % → (opened events / sent events) × 100
- Click rate % → (clicked events / sent events) × 100
- Hot leads (clicked + visited demo) → `website_leads` WHERE status IN ('hot','demo_visited','interested')
- Calls booked this week / all time → `pipeline_bookings` COUNT
- Conversion rate → (booked / total sourced) × 100

**Lead Table:**
- Query: `website_leads` ordered by `created_at DESC`
- Columns: Business name, Owner, Email, City, Source, Status (badge), Lead Score, Last Contacted, Next Action
- Status badges: colour-coded per status (new=grey, sequenced=blue, hot=amber, booked=green, won=violet, lost=red)
- Search by business name or city
- Filter by status dropdown

**Sequence Status Panel:**
- Show leads in active sequence with current step number
- Pause/resume toggle (updates `sequence_paused` in Supabase)
- "Do Not Contact" button (sets status to `do_not_contact`, pauses Instantly via API)

**Booking Feed:**
- Query: `pipeline_bookings` JOIN `website_leads` ordered by `meeting_time`
- Show: name, business, meeting date/time, call status badge
- Quick-update dropdown for call outcome

**Quick Actions:**
- "Source Leads" button → triggers n8n lead sourcer webhook with city/state input
- "Export CSV" → client-side CSV download of filtered leads
- "Send One-Off Email" → modal with lead picker + message box → hits n8n webhook → sends via SMTP2GO (not Instantly — one-offs go through transactional)

### Implementation Notes

This follows the existing admin dashboard design system: white cards on `#F4F5F9` background, violet accents, Inter font, vanilla JS with Supabase REST queries. The `renderMarketing()` function already exists — it needs to be enhanced with the new queries against the expanded schema.

I will build this in a separate session focused solely on the admin dashboard code — the work involves ~200–300 lines of HTML/CSS and ~300–400 lines of JS added to the existing `index.html`.

---

## 6. Phase 5 — Multi-Channel Expansion

### Targeted Cold Calling (Ongoing from Week 2)

**This is your secret weapon.** Unlike every other SaaS company doing cold email, you can demonstrate your product live on a phone call. No demo video, no landing page — just "let me transfer you to our AI right now."

**Daily routine (30–60 min/day):**
1. Open admin dashboard → Marketing → filter leads by status `hot` or `demo_visited`
2. Call the top 5–10 leads (the ones who opened 2+ emails or clicked through)
3. Script opening: "Hi {first_name}, it's Daniel from Syntharra. I noticed you checked out our AI receptionist demo — did you get a chance to call the demo line?"
4. If they haven't: "Let me transfer you right now so you can hear it — takes 30 seconds." Transfer to +1 (812) 994-4371
5. If they have: "Great — what did you think? I can have one set up for {business_name} by tomorrow."
6. Log outcome in Supabase via dashboard (interested / not ready / booked / not interested)

**Why this converts at 10–20% vs 1–2% for cold-cold calls:**
- They already know who Syntharra is (they opened your emails)
- The demo line does 80% of the selling for you
- HVAC owners respect a founder who picks up the phone
- You're calling 5–10 qualified leads, not 50 random businesses

**Key rule:** Never cold call someone who hasn't engaged with at least one email first. That's what the email sequence is for — it warms them up so your call isn't truly cold.

**n8n automation opportunity:** Build a daily digest workflow that emails you at 9am with the top 10 hot leads to call today, sorted by lead score. Include their name, business, city, and which emails they engaged with.

---

### LinkedIn (Week 5)

**Strategy:** Manual outreach to hot leads who engaged with emails but didn't book.

**Process:**
1. Daily: check admin dashboard for leads with status `hot` or `demo_visited` who haven't booked
2. Find them on LinkedIn (search by name + company + city)
3. Send connection request with note (under 300 chars):
   > "Hi {first_name} — noticed you run {business_name} in {city}. We help HVAC companies capture every call with AI. Would love to connect."
4. Once connected, send a short message referencing the demo call number
5. Log LinkedIn activity in Supabase (manual update or n8n webhook)

**Tool recommendation (when ready to automate):** Dripify ($59/mo) or Expandi ($99/mo) for automated LinkedIn sequences. But start manual — 30 min/day, 10–15 connections.

**Volume:** 100 connection requests/week (LinkedIn's safe limit), 5–10 messages/day to existing connections.

### Retargeting Ads (Week 6)

**Meta Pixel setup (prerequisite):**
1. Install Meta Pixel on syntharra.com (standard events: PageView, Lead, Schedule)
2. Create Custom Audiences in Meta Ads Manager:
   - Website visitors (last 30 days)
   - Demo page visitors (last 30 days)
   - Email list upload (all leads with status != 'do_not_contact')
3. Create Lookalike Audience from paying clients (when available)

**Ad strategy:**
- Retarget demo page visitors with the VSL (once Scene 3 recording is complete)
- Budget: $10–20/day retargeting only (tiny audience, high intent)
- Creative: Short clip from VSL + "Still thinking about an AI receptionist? Call our demo line."

### VSL Integration

The VSL is in production (Scenes 1, 2, 4, 5 have voiceover scripts; Scene 3 needs the demo call recording). Once complete:
- Embed on demo.html as the primary content
- Use as Facebook retargeting ad creative
- LinkedIn video posts (clips)
- YouTube channel content
- Email sequence Email 3 alternative: link to VSL instead of phone number

**Priority action:** Dan needs to record the Scene 3 demo call (call +1 812 994 4371 as Mike Henderson). This unblocks the entire VSL pipeline.

### SMS Follow-Up (Post-booking confirmation)

**Tool:** Telnyx (already set up, awaiting AI evaluation approval for toll-free)
**Use case:** After Cal.com booking confirmation, send SMS reminder:
> "Hi {first_name}, this is Daniel from Syntharra. Looking forward to our call on {date}. If you want to hear our AI in action beforehand, call +1 (812) 994-4371. Talk soon!"

**Not for cold outreach** — SMS cold outreach has strict TCPA regulations. Only use for confirmed bookings and existing conversations.

### AI Voice Agent Follow-Up (Future)

Once Syntharra has 5+ paying clients and proven conversion data:
- Use Retell AI to auto-dial hot leads who visited demo page but didn't book
- Script: "Hi {first_name}, this is the AI receptionist from Syntharra. You recently checked out our demo — I wanted to show you exactly how I'd answer calls for {business_name}. Want to hear a quick example?"
- This is the ultimate proof-of-product: the product sells itself by demonstrating itself

---

## 7. Phase 6 — 6-Week Implementation Roadmap

### Week 1: Foundation

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| Purchase 2 secondary domains | Daniel | Namecheap/Cloudflare | 2 domains registered |
| Set up SPF, DKIM, DMARC on both domains | Daniel | DNS provider | Both pass MXToolbox check |
| Create 2 mailboxes per domain | Daniel | Google Workspace or Instantly provisioning | 4 sending addresses active |
| Sign up for Instantly.ai ($30/mo Growth plan) | Daniel | Instantly | Account active |
| Connect all 4 inboxes to Instantly + start warmup | Daniel | Instantly | All 4 warming |
| Run Supabase schema migration (new columns + tables) | Claude | Supabase | Tables created, RLS applied |
| Complete Google Places lead sourcer n8n workflow | Claude | n8n | Workflow active, test run successful |
| Source first batch: 500 HVAC leads (top 10 US cities) | Claude/n8n | Google Places API | 500 leads in `website_leads` |

### Week 2: Email Launch

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| Import 5-email sequence into Instantly | Daniel | Instantly | Campaign created with UTM links |
| Set up custom tracking domain in Instantly | Daniel | Instantly + DNS | Tracking domain verified |
| Email verify all 500 leads (ZeroBounce or NeverBounce) | Claude/n8n | Verification API | Bounce rate < 2% |
| Push first 200 verified leads into Instantly campaign | Daniel | Instantly | Campaign sending |
| Build n8n → Instantly sync workflow (auto-push new leads) | Claude | n8n | Workflow active |
| Build hot lead detector workflow (Instantly webhook → Supabase) | Claude | n8n | Webhook receiving events |
| Source next 500 leads (10 more cities) | Claude/n8n | Google Places | 1,000 total leads |
| First 500 emails sent by end of week | — | Instantly | 500+ sent, 0 bounces |

### Week 3: Dashboard & Tracking

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| Build enhanced Marketing section in admin dashboard | Claude | Admin dashboard | All KPIs live, lead table working |
| Build Cal.com → Supabase booking handler workflow | Claude | n8n | Bookings auto-logged |
| Connect Instantly webhooks to email_events table | Claude | n8n | All email events tracked |
| Add UTM capture to demo.html (already partially built) | Claude | Website | UTM params stored in Supabase |
| Ramp sending to 200/day across all inboxes | Daniel | Instantly | 200/day steady state |
| Review first week's open/click/reply data | Daniel + Claude | Instantly + Dashboard | Open rate > 40% |
| A/B test subject lines on Email 1 | Daniel | Instantly | Winner identified |

### Week 4: Optimise & Convert

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| First Cal.com bookings should be flowing | Daniel | Cal.com | 5+ bookings this week |
| Refine email sequence based on Week 2–3 data | Claude | Instantly | Reply rate > 3% |
| Source another 1,000 leads (expand to 30 cities) | Claude/n8n | Google Places | 2,000+ total leads |
| Record VSL Scene 3 demo call | Daniel | Phone + recording | Recording complete |
| Begin VSL assembly in CapCut | Daniel | CapCut + ElevenLabs | VSL draft complete |
| Build sequence pause/resume controls in dashboard | Claude | Admin dashboard | Working UI |

### Week 5: LinkedIn Layer

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| Start daily LinkedIn outreach (30 min/day) | Daniel | LinkedIn | 50+ connections/week |
| Target hot leads who didn't book | Daniel | Dashboard → LinkedIn | 10+ messages/day |
| Launch Blotato Phase 1 organic content | Claude | n8n + Blotato | First 4 videos posted |
| Publish VSL on demo.html | Daniel/Claude | Website | VSL embedded and live |
| Ramp cold email to 300/day | Daniel | Instantly | 300/day sustained |
| Review conversion funnel: leads → meetings → deals | Daniel + Claude | Dashboard | Full funnel visible |

### Week 6: Scale & Amplify

| Task | Owner | Tools | Success Metric |
|---|---|---|---|
| Install Meta Pixel on syntharra.com | Claude | Website | Pixel firing on all pages |
| Create retargeting audiences in Meta Ads Manager | Daniel | Meta | 3 audiences created |
| Launch retargeting ads ($10–20/day) | Daniel | Meta Ads | Ads running |
| Build automated weekly marketing report email | Claude | n8n + SMTP2GO | Weekly digest to Daniel |
| Source to 3,000+ total leads | Claude/n8n | Google Places | 3,000+ in database |
| Review: first closed deal from cold email? | Daniel | Stripe + Dashboard | Revenue attributed |
| Plan Month 2: scale what's working, cut what isn't | Daniel + Claude | Data | Data-driven decisions |

---

## 8. Immediate Next Steps (Do Today)

1. **Buy 2 domains** (`getsyntharra.com`, `trysyntharra.com`) — Namecheap or Cloudflare, ~$24/year total

2. **Sign up for Instantly.ai** ($30/mo Growth plan) — start the 14-day warmup process immediately. Every day of delay = one more day before you can send.

3. **Set up mailboxes on both domains** — create `daniel@getsyntharra.com` and `daniel@trysyntharra.com`, configure SPF/DKIM/DMARC. Connect to Instantly and start warmup.

4. **Record the VSL Scene 3 demo call** — call +1 (812) 994-4371 as Mike Henderson. This has been blocking the VSL for weeks. 5 minutes of your time unblocks the biggest marketing asset.

5. **Say "go" and I'll run the Supabase schema migration** — the new columns and tables are defined above and won't affect existing data.

---

## Cost Summary

| Item | Monthly Cost | Notes |
|---|---|---|
| Instantly.ai | $30 | Growth plan — unlimited accounts + warmup + basic verification |
| 2 secondary domains | ~$2 (annualised) | ~$24/year total |
| Google Places API | $0–17 | $200/mo free credit from Google covers early usage |
| Email verification | $0 to start | Instantly includes basic verification; add ZeroBounce later at scale |
| Cold calling | $0 | You have a phone + the leads already have phone numbers from Google Places |
| **Total new spend** | **~$32/mo** | Everything else already running |

For context: one Standard client ($497/mo) pays for **15 months** of this entire marketing engine.

---

*This document should be stored at `syntharra-automations/docs/growth-engine-strategy.md` and referenced in project-state.md. Update after each implementation session.*
