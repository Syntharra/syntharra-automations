# Syntharra Lead Generation Machine — Full System Design
> Version 1.0 | Created 2026-04-02 | Author: Claude (Senior Engineer)
> Purpose: 100% autonomous AI team that finds warm leads and books them into Dan's calendar.
> Every action tracked → fed back → improved → scaled. 24/7. No human input required except calendar availability.

---

## THE MISSION

One outcome only: **warm leads booked into Dan's calendar**.

Not impressions. Not followers. Not email opens.  
**Booked calls with HVAC business owners who are ready to buy.**

Every agent in this system exists to serve that single outcome.  
Every metric tracked maps back to that outcome.  
The system self-improves until it finds what works, then scales that.

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SYNTHARRA LEAD MACHINE                               │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  AGENT 1     │    │  AGENT 2     │    │  AGENT 3     │                  │
│  │  RESEARCHER  │───▶│  COPYWRITER  │───▶│  PROSPECTOR  │                  │
│  │  (daily)     │    │  (daily)     │    │  (daily)     │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                    │                          │
│         ▼                   ▼                    ▼                          │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │               Supabase: lead_machine_* tables        │                  │
│  │   research_briefs | message_variants | outbound_leads│                  │
│  │   sequence_log | ab_tests | bookings | experiments   │                  │
│  └──────────────────────────────────────────────────────┘                  │
│         │                   │                    │                          │
│         ▼                   ▼                    ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  AGENT 4     │    │  AGENT 5     │    │  AGENT 6     │                  │
│  │  SEQUENCER   │    │  HOT LEAD    │    │  OPTIMIZER   │                  │
│  │  (triggered) │    │  DETECTOR    │    │  (weekly)    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                    │                          │
│         ▼                   ▼                    ▼                          │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │                     OUTPUTS                          │                  │
│  │  Cal.com bookings | HubSpot pipeline | Dan alert     │                  │
│  └──────────────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## THE 6 AGENTS

### AGENT 1 — THE RESEARCHER
**Job:** Understand what HVAC business owners are complaining about RIGHT NOW.  
**Trigger:** Daily, 5:00 AM GMT  
**Tools:** Claude API + web_search tool  
**Input:** Target vertical (HVAC), geography (USA), existing winning angles from `lead_machine_experiments`  

**What it searches every day:**
- Reddit: r/HVAC, r/smallbusiness, r/Entrepreneur — posts from last 7 days
- Google Trends: "HVAC answering service", "missed calls HVAC", "AI receptionist" — rising queries
- Industry pain: staffing shortages, call volume spikes, seasonal demand, competitor pricing
- What's NEW this week that we can reference in outreach (makes emails feel timely)

**Output:** JSON research brief → `lead_machine_research` table  
```json
{
  "date": "2026-04-02",
  "top_pain_points": ["...", "...", "..."],
  "trending_hooks": ["...", "..."],
  "timely_angle": "Spring AC season starting — homeowners calling NOW",
  "competitor_intel": "ServiceTitan raised prices again",
  "recommended_subject_lines": ["...", "...", "..."],
  "confidence_score": 0.87
}
```

**n8n Workflow:** `LM-01 — Daily Research Brief`

---

### AGENT 2 — THE COPYWRITER
**Job:** Write ALL outbound messages. Constantly test new angles.  
**Trigger:** Fires after Agent 1 completes (event-driven)  
**Tools:** Claude API, Supabase (reads winning variants, reads research brief)  
**Input:** Research brief + all previous A/B test results + current winning control  

**What it writes every day:**
- 3 new subject line variants for Email 1 (A/B test candidates)
- 2 new opening line variants (personalised hooks using research brief)
- 1 new sequence variant if current control has been running 7+ days
- LinkedIn connection request message (for hot leads who opened but didn't book)
- Follow-up DM template (comment-to-DM trigger on social posts)

**A/B Testing Logic:**
- Every new variant is written against a hypothesis: "I believe [X] will outperform control because [Y]"
- Hypothesis stored in `lead_machine_experiments`
- After 50 sends minimum, winner declared by reply rate
- Loser archived. Winner becomes new control. Cycle repeats.
- Over 90 days: the system will have tested 90+ variants and kept only what works

**Output:** Message variants → `lead_machine_message_variants` table  
**n8n Workflow:** `LM-02 — Daily Copy Generation`

---

### AGENT 3 — THE PROSPECTOR
**Job:** Find HVAC businesses that need Syntharra. Every single day.  
**Trigger:** Daily, 6:00 AM GMT  
**Tools:** Google Places API, Claude API, Hunter.io (email finding), ZeroBounce (verification)  
**Input:** Target cities list (rotating), exclusion list (already contacted)  

**What it does:**
1. Pulls 50–100 HVAC businesses from Google Places in today's target city
2. For each business: extracts name, phone, address, website, rating, review count
3. Scores each lead 1–10 based on: fewer than 100 reviews (smaller op), has website, has phone, active Google listing
4. Finds owner name + email via Hunter.io domain search
5. Verifies email via ZeroBounce (only queues leads with >85% deliverability score)
6. Checks Supabase: skip if already in `outbound_leads` table
7. Enriches with personalisation data: city, business name, owner first name
8. Writes personalised "first line" for Email 1 using Claude API + research brief context

**Output:** Qualified leads → `outbound_leads` table with status=`ready`  
**Daily volume:** 30–60 verified, enriched leads added  
**n8n Workflow:** `LM-03 — Daily Lead Prospector`

---

### AGENT 4 — THE SEQUENCER
**Job:** Put every qualified lead into the winning email sequence. Automatically.  
**Trigger:** New lead added to `outbound_leads` with status=`ready` (Supabase webhook)  
**Tools:** Instantly.ai API (sending + tracking), n8n, Supabase  

**Sequence structure (current control — replaced when A/B test winner found):**
| Touch | Day | Channel | Subject | Goal |
|---|---|---|---|---|
| 1 | 0 | Email | Personalised pain hook | Open + click |
| 2 | 3 | Email | Cost of missed calls | Reply or click |
| 3 | 6 | Email | "Call this number" (demo line) | Phone call to demo |
| 4 | 10 | Email | Competitor urgency | Book call |
| 5 | 14 | Email | Breakup email | Reply or unsubscribe |

**On every interaction (open / click / reply):**
- Event written to `lead_machine_sequence_log` with timestamp + event type
- Status updated in `outbound_leads`
- HubSpot contact upserted (Lead stage on first touch, Demo Booked on booking)

**On reply:**
- Claude API classifies reply: POSITIVE / NEGATIVE / OUT_OF_OFFICE / QUESTION
- POSITIVE → fires Agent 5 immediately
- QUESTION → Claude drafts reply → queued in `lead_machine_replies` for Dan review
- NEGATIVE / unsubscribe → contact marked do_not_contact in Supabase + Instantly

**n8n Workflow:** `LM-04 — Sequence Manager`

---

### AGENT 5 — THE HOT LEAD DETECTOR
**Job:** The moment someone is warm — Dan knows instantly. No lead goes cold.  
**Trigger:** Event-driven — fires on: email click, positive reply, demo page visit with email match, demo phone call  
**Tools:** Supabase, HubSpot API, Telnyx SMS, SMTP2GO  

**Hot lead triggers (any one fires the agent):**
- Clicked link in cold email (any email in sequence)
- Replied positively to cold email
- Visited `demo.html` with matching UTM → email (pixel + UTM tracking)
- Called demo line +1 (812) 994-4371 from a tracked lead's phone number

**What it does in <2 minutes:**
1. Enriches the lead record: pulls all interactions, calculates engagement score
2. Moves HubSpot deal to `Demo Booked` stage
3. Sends Dan SMS via Telnyx: "🔥 HOT LEAD — Mike Henderson, Henderson's HVAC, Phoenix AZ. Clicked Email 2. Call within the hour: +1 (480) 555-0123. Book: [Cal.com link]"
4. Sends lead a personalised Cal.com booking link via email — "I saw you were interested..."
5. Logs everything to `lead_machine_bookings`

**If lead books Cal.com slot:**
- Supabase updated: status=`booked`
- HubSpot deal stays at `Demo Booked`
- Dan gets final confirmation SMS with the slot time
- Preparation brief generated: business size, review count, pain points, talking points for the call

**n8n Workflow:** `LM-05 — Hot Lead Detector`

---

### AGENT 6 — THE OPTIMIZER
**Job:** Make the whole machine smarter every week. Agentic self-improvement.  
**Trigger:** Every Sunday at 11:00 PM GMT  
**Tools:** Claude API, Supabase (full read access to all lead_machine_* tables), HubSpot API  

**What it analyses:**
- Open rates per subject line variant (last 7 days + cumulative)
- Reply rates per email body variant
- Click rates per CTA variant
- Conversion funnel: sent → open → click → reply → book
- Which cities / business sizes / review counts convert best
- Which research angles correlated with best open rates
- Time-of-send performance (sent at 9am vs 10am vs 11am)
- Sequence drop-off: which email do people stop engaging after?

**What it decides and acts on:**
- Declares A/B test winners (≥50 sends, statistical threshold met)
- Archives losing variants in `lead_machine_experiments` with result + reason
- Promotes winning variant to new control — updates `message_variants` status
- Generates 3 new hypotheses for next week's copy tests
- Identifies best-performing city/size profile → tells Agent 3 to prioritise that profile
- Flags any deliverability issues (bounce rate creeping up, reply rate dropping)

**Output:**
- Updated `lead_machine_experiments` table (winners, losers, hypotheses)
- Updated `lead_machine_config` table (control variants, targeting parameters)
- Weekly intelligence report → email to Dan every Monday 6:00 AM
- The report tells Dan: what worked, what didn't, what's being tested next week

**n8n Workflow:** `LM-06 — Weekly Optimizer`

---

## SUPABASE SCHEMA

### Table: `lead_machine_research`
```sql
CREATE TABLE lead_machine_research (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL,
  top_pain_points JSONB,
  trending_hooks JSONB,
  timely_angle TEXT,
  competitor_intel TEXT,
  recommended_subject_lines JSONB,
  raw_research TEXT,
  confidence_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Table: `outbound_leads`
```sql
CREATE TABLE outbound_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- Identity
  business_name TEXT NOT NULL,
  owner_first_name TEXT,
  owner_email TEXT,
  owner_phone TEXT,
  website TEXT,
  city TEXT,
  state TEXT,
  -- Scoring
  lead_score INT,                  -- 1-10
  google_review_count INT,
  email_deliverability_score FLOAT,
  personalised_first_line TEXT,
  -- Status tracking
  status TEXT DEFAULT 'ready',   -- ready | sequenced | hot | booked | no_response | do_not_contact
  sequence_id TEXT,                -- Instantly campaign ID
  sequence_started_at TIMESTAMPTZ,
  last_interaction_at TIMESTAMPTZ,
  interaction_count INT DEFAULT 0,
  -- Source
  source TEXT DEFAULT 'google_places',
  target_city_batch TEXT,
  -- HubSpot
  hubspot_contact_id TEXT,
  hubspot_deal_id TEXT,
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_outbound_leads_status ON outbound_leads(status);
CREATE INDEX idx_outbound_leads_email ON outbound_leads(owner_email);
```

### Table: `lead_machine_sequence_log`
```sql
CREATE TABLE lead_machine_sequence_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES outbound_leads(id),
  event_type TEXT NOT NULL,        -- sent | opened | clicked | replied | bounced | unsubscribed
  email_number INT,                -- 1-5 (which email in sequence)
  subject_line_variant TEXT,
  body_variant TEXT,
  email_sent_at TIMESTAMPTZ,
  event_at TIMESTAMPTZ DEFAULT NOW(),
  reply_classification TEXT,       -- POSITIVE | NEGATIVE | QUESTION | OUT_OF_OFFICE
  reply_text TEXT,
  metadata JSONB
);
```

### Table: `lead_machine_message_variants`
```sql
CREATE TABLE lead_machine_message_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_type TEXT NOT NULL,      -- subject_line | opening_line | body | cta | sequence
  email_number INT,                -- 1-5 (which email this applies to)
  content TEXT NOT NULL,
  hypothesis TEXT,                 -- Why this should outperform control
  status TEXT DEFAULT 'testing',  -- testing | control | archived
  sends INT DEFAULT 0,
  opens INT DEFAULT 0,
  clicks INT DEFAULT 0,
  replies INT DEFAULT 0,
  bookings INT DEFAULT 0,
  open_rate FLOAT GENERATED ALWAYS AS (CASE WHEN sends > 0 THEN opens::FLOAT/sends ELSE 0 END) STORED,
  reply_rate FLOAT GENERATED ALWAYS AS (CASE WHEN sends > 0 THEN replies::FLOAT/sends ELSE 0 END) STORED,
  booking_rate FLOAT GENERATED ALWAYS AS (CASE WHEN sends > 0 THEN bookings::FLOAT/sends ELSE 0 END) STORED,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  declared_winner_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,
  archived_reason TEXT
);
```

### Table: `lead_machine_experiments`
```sql
CREATE TABLE lead_machine_experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_starting DATE NOT NULL,
  experiment_type TEXT,            -- subject_line | body_copy | sequence | targeting | send_time
  hypothesis TEXT NOT NULL,
  control_variant_id UUID REFERENCES lead_machine_message_variants(id),
  test_variant_id UUID REFERENCES lead_machine_message_variants(id),
  min_sends_required INT DEFAULT 50,
  status TEXT DEFAULT 'running',  -- running | winner_declared | inconclusive
  winner_variant_id UUID REFERENCES lead_machine_message_variants(id),
  result_summary TEXT,
  uplift_percentage FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  decided_at TIMESTAMPTZ
);
```

### Table: `lead_machine_bookings`
```sql
CREATE TABLE lead_machine_bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES outbound_leads(id),
  booked_at TIMESTAMPTZ DEFAULT NOW(),
  call_scheduled_at TIMESTAMPTZ,
  booking_source TEXT,             -- cold_email | demo_page | demo_phone | social_dm
  trigger_event TEXT,              -- which event triggered the hot lead alert
  cal_booking_id TEXT,
  hubspot_deal_id TEXT,
  call_preparation_brief TEXT,     -- Claude-generated briefing for Dan
  outcome TEXT,                    -- pending | showed | no_show | converted | lost
  notes TEXT
);
```

### Table: `lead_machine_config`
```sql
CREATE TABLE lead_machine_config (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by TEXT DEFAULT 'optimizer'
);

-- Seed data
INSERT INTO lead_machine_config VALUES
  ('active_vertical', 'HVAC', NOW(), 'setup'),
  ('target_geography', 'USA', NOW(), 'setup'),
  ('daily_lead_target', '50', NOW(), 'setup'),
  ('min_sends_for_ab_decision', '50', NOW(), 'setup'),
  ('hot_lead_score_threshold', '7', NOW(), 'setup'),
  ('email_send_time_hour_gmt', '14', NOW(), 'setup'),
  ('priority_city_profile', '{"min_reviews": 10, "max_reviews": 150, "state": "any"}', NOW(), 'setup'),
  ('control_subject_line_email1', '{first_name}, quick question about {business_name}', NOW(), 'setup'),
  ('control_opening_line_email1', 'I called 73 HVAC companies in {city} last week. 41 went straight to voicemail.', NOW(), 'setup');
```

---

## N8N WORKFLOW SPECS

### LM-01 — Daily Research Brief
```
TRIGGER:    Schedule — 5:00 AM GMT, daily
NODES:
  1. Schedule Trigger
  2. Read Config (Supabase: get active_vertical, target_geography)
  3. Read Previous Winners (Supabase: top 3 winning angles from lead_machine_experiments)
  4. Claude API call:
     - model: claude-sonnet-4-20250514
     - tools: [web_search]
     - system: "You are a market research agent for Syntharra. Research what HVAC business 
               owners are struggling with RIGHT NOW. Focus on: pain points, seasonal trends, 
               industry news, competitor weaknesses. Return structured JSON only."
     - prompt: Built dynamically from config + previous winners
  5. Parse JSON response
  6. Write to lead_machine_research (Supabase)
  7. Trigger LM-02 via webhook
```

### LM-02 — Daily Copy Generation
```
TRIGGER:    Webhook from LM-01 (also manual)
NODES:
  1. Webhook Trigger
  2. Fetch today's research brief (Supabase)
  3. Fetch current control variants (Supabase: status='control')
  4. Fetch running experiments (Supabase: status='running')
  5. Claude API call:
     - system: "You are a cold email copywriter for Syntharra. Write short, punchy, 
               plain-text cold emails for HVAC business owners. Under 80 words each. 
               Always problem-first, never product-first. Return JSON only."
     - prompt: Includes research brief + existing controls + what's been tested before
     - Output: 3 subject line variants + 2 opening line variants + hypothesis for each
  6. Write variants to lead_machine_message_variants (status='testing')
  7. Write experiments to lead_machine_experiments (status='running')
  8. No notification — silent operation
```

### LM-03 — Daily Lead Prospector
```
TRIGGER:    Schedule — 6:00 AM GMT, daily
NODES:
  1. Schedule Trigger
  2. Read Config (Supabase: target city for today, daily_lead_target)
  3. Google Places API: search "HVAC contractor" in today's city
  4. SplitInBatches: process each result
  5. For each business:
     a. Check Supabase: owner_email already in outbound_leads? → Skip
     b. Score lead (review count, has website, active listing)
     c. Hunter.io API: find owner email by domain
     d. ZeroBounce API: verify email deliverability
     e. Score < 5 OR deliverability < 0.85? → Skip
     f. Fetch today's research brief for personalised first line context
     g. Claude API: generate personalised first line (1 sentence, specific to this business)
     h. Insert to outbound_leads (status='ready')
  6. Count leads added
  7. Rotate to next city in city list
```

### LM-04 — Sequence Manager
```
TRIGGER:    Supabase webhook (INSERT on outbound_leads where status='ready')
            + Instantly.ai webhook (email events: opened, clicked, replied, bounced)
NODES (on new lead):
  1. Webhook Trigger
  2. Fetch lead record + current control variants
  3. Build email sequence using control variants + lead personalisation
  4. Instantly.ai API: add lead to campaign with personalised variables
  5. Update outbound_leads: status='sequenced', sequence_started_at=NOW()
  6. Upsert HubSpot contact (Lead stage)

NODES (on email event):
  1. Webhook Trigger (Instantly event)
  2. Match to outbound_leads by email
  3. Write to lead_machine_sequence_log
  4. Update outbound_leads: last_interaction_at, interaction_count++
  5. Increment variant stats in lead_machine_message_variants
  6. If event='replied':
     a. Claude API: classify reply (POSITIVE/NEGATIVE/QUESTION/OOO)
     b. POSITIVE → trigger LM-05 immediately
     c. QUESTION → write draft reply → insert to lead_machine_replies for Dan
     d. NEGATIVE/UNSUBSCRIBE → mark do_not_contact
  7. If event='clicked':
     a. Trigger LM-05 (hot lead detector)
```

### LM-05 — Hot Lead Detector
```
TRIGGER:    Webhook (from LM-04 on click/positive reply, from demo.html pixel, from Retell post-call)
NODES:
  1. Webhook Trigger
  2. Identify lead (email match to outbound_leads OR phone match)
  3. Calculate engagement score (interactions, which emails, timing)
  4. Update outbound_leads: status='hot'
  5. Move HubSpot deal to Demo Booked stage
  6. Generate call preparation brief (Claude API):
     - Business summary, estimated size, pain points from research, suggested talking points
  7. Telnyx SMS to Dan:
     "🔥 HOT LEAD — {name}, {business}, {city}. {trigger_event}. 
      Call: {phone}. Book: [Cal.com]. Brief: [link to supabase record]"
  8. Send Cal.com link to lead via SMTP2GO:
     "Hi {first_name}, saw you were checking out Syntharra — here's a quick link to 
      grab 15 minutes with our founder: [Cal.com link]"
  9. Write to lead_machine_bookings (outcome='pending')
  10. If Cal.com webhook fires (booking confirmed):
      - Update booking: call_scheduled_at, cal_booking_id
      - SMS Dan: "✅ BOOKED — {name} locked in for {time}"
```

### LM-06 — Weekly Optimizer
```
TRIGGER:    Schedule — Sunday 11:00 PM GMT
NODES:
  1. Schedule Trigger
  2. Pull all data from last 7 days:
     - lead_machine_sequence_log (open/click/reply rates per variant)
     - lead_machine_message_variants (running stats)
     - lead_machine_experiments (running tests)
     - lead_machine_bookings (conversions)
     - outbound_leads (city/size/profile breakdown)
  3. Claude API analysis:
     - Identify statistically significant winners (≥50 sends)
     - Calculate uplift vs control
     - Identify best-performing lead profile
     - Flag any deliverability concerns
     - Generate 3 new hypotheses for next week
     - Return structured JSON
  4. Update database:
     - Declare winners: update experiments, promote variants to 'control'
     - Archive losers: update variants status='archived' with reason
     - Insert new hypotheses as experiments (status='running')
     - Update lead_machine_config (priority_city_profile, send_time, etc.)
  5. Generate weekly intelligence report (HTML email)
  6. Send to Dan via SMTP2GO (Monday 6:00 AM GMT)
     Subject: "Lead Machine Report — Week of {date}"
```

---

## TRACKING & MEASUREMENT

### The Only Metrics That Matter
| Metric | Target (Week 4) | Target (Week 8) | Target (Week 12) |
|---|---|---|---|
| Leads sourced/week | 250 | 350 | 500 |
| Emails sent/week | 200 | 300 | 400 |
| Open rate | 45% | 50% | 55% |
| Reply rate | 3% | 4% | 5% |
| Hot leads/week | 3 | 6 | 10 |
| Booked calls/week | 1–2 | 3–5 | 5–8 |
| Conversion to client | — | — | 1–3/mo |

### Funnel View (end-state, Week 12)
```
500 leads sourced/week
  → 400 emailed (80% pass verification)
    → 200 opens (50% open rate)
      → 20 replies (10% of openers)
        → 10 hot leads (50% of replies are positive)
          → 6–8 booked calls
            → 1–3 new clients/month
```

### What Gets Logged Per Lead
Every interaction is timestamped, tagged with variant IDs, and stored:
- Which subject line they opened (or didn't)
- Which email they clicked (or didn't)  
- How they replied
- How long from first email to booking
- City, state, business size, review count
- Source: which sequence, which day, which variant

After 90 days: the system knows exactly which HVAC business profile converts best,
which email angle wins, which city has the hungriest buyers. Then it scales that exclusively.

---

## WHAT YOU NEED TO PROVIDE (3 THINGS)

1. **Secondary sending domain** (~$12/yr — `getsyntharra.com` or `trysyntharra.com`)
   - I configure: SPF, DKIM, DMARC, redirect to syntharra.com
   - I set up: 2–3 sending inboxes on that domain
   
2. **Instantly.ai account** ($30/mo Growth plan)
   - I configure: campaigns, sequences, A/B testing, webhook to n8n
   - I handle: warmup, domain authentication, Supabase sync
   
3. **Hunter.io account** (free tier = 25 searches/day, $34/mo Starter = 500/day)
   - I configure: API integration into Lead Prospector workflow

**Total new spend: $42–76/month.** Everything else runs on existing infrastructure.

---

## SELF-IMPROVEMENT PROTOCOL

The Optimizer runs this loop every week:

```
WEEK 1: Baseline established. 3 experiments running.
WEEK 2: First results. 1–2 winners declared. 3 new experiments queued.
WEEK 3: Compounding. Winning angles reinforce research brief. 
         Copy gets sharper. Targeting gets tighter.
WEEK 4: Pattern recognition. System identifies best lead profile.
         Prospector prioritises that profile.
WEEK 6: Control variants are 2x better than Week 1 baseline.
WEEK 8: System knows the winning playbook. Scale begins.
WEEK 12: Machine runs at full capacity. Minimal noise, maximum signal.
```

The system doesn't wait for permission to improve. It tests, measures, decides, and 
updates its own config. The only thing it asks of Dan: show up for the booked calls.

---

## BUILD ORDER

| Session | What Gets Built | Blocker |
|---|---|---|
| Session 1 | Supabase schema (all tables) | None — build now |
| Session 1 | LM-01 Research Brief | None — build now |
| Session 1 | LM-02 Copy Generation | None — build now |
| Session 2 | LM-03 Lead Prospector | Google Places API key needed |
| Session 2 | LM-06 Optimizer | None — build now |
| Session 3 | LM-04 Sequence Manager | Instantly.ai account needed |
| Session 3 | LM-05 Hot Lead Detector | Instantly.ai webhooks needed |
| Session 4 | End-to-end test + go-live | All above complete |

Sessions 1 + partial 2 can start immediately — no new tools required.
