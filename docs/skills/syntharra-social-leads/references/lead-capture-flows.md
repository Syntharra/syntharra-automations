# Lead Capture Mechanisms — Syntharra Social Leads
# Detailed setup and flow for all 5 lead capture paths

---

## MECHANISM 1 — Comment-to-DM (Phase 1)
**Tool:** Spur (spur.so) — free tier to start
**Platforms:** Facebook Page + Instagram Business Account
**Keyword:** "DEMO" (used as the primary CTA in all video content)

### Setup Checklist
- [ ] Create Spur account at spur.so
- [ ] Connect Facebook Page to Spur
- [ ] Connect Instagram Business Account to Spur
- [ ] Create automation: trigger = comment contains "DEMO"
- [ ] Set DM template (see below)
- [ ] Set webhook: POST to `https://n8n.syntharra.com/webhook/spur-comment-dm`
- [ ] Test: comment "DEMO" on a test post and verify DM fires

### DM Template (Facebook + Instagram)
```
Hey {{first_name}} 👋

Here's that demo I mentioned — this is a real HVAC company using our AI receptionist.

Call this number right now and see what your customers will hear:
📞 +1 (812) 994-4371

If you want to see how this would work for YOUR business, grab a free 15-min call:
👉 [Cal.com link]

— Dan
Syntharra AI
```

### Follow-up DM (sent 48hrs later if no reply, once only)
```
Hey {{first_name}} — just checking you got my last message.

A lot of HVAC owners tell me they get busy and forget to call.
The demo line is still live whenever you're ready: +1 (812) 994-4371

Free call here if you want to chat: [Cal.com link]
```

### n8n Webhook Handler
- Receive Spur webhook → check for duplicate (same commenter this week)
- Log to `website_leads`: source='comment_dm', platform, name, post context
- If score >= 4: Telnyx SMS alert to Dan
- Schedule 48hr follow-up check via n8n Wait node

### Compliance Rules
- Max 2 DMs per person per campaign (first DM + one follow-up)
- Never DM someone who previously asked to stop
- Store opted-out commenter IDs in Supabase to prevent re-contact

---

## MECHANISM 2 — Facebook Lead Ads (Phase 2)
**Tool:** Meta Ads Manager + n8n Facebook Lead Ads Trigger node
**Platform:** Facebook (extend to Instagram later)

### Lead Form Setup (in Meta Ads Manager)
**Form name:** "Syntharra HVAC Free Call Audit"
**Intro headline:** "Find out how many calls your HVAC business is missing"
**Intro description:** "Takes 30 seconds. No sales pitch — just honest numbers."

**Pre-filled fields (Facebook auto-fills from profile):**
- Full name
- Email address
- Phone number

**Custom questions:**
1. "How many inbound calls does your HVAC business receive per day?"
   - Options: Under 10 / 10–30 / 30–50 / Over 50
2. "Are you currently using an answering or receptionist service?"
   - Options: Yes, we use one / No, we handle it ourselves / We used to but stopped

**Thank you screen:**
"Thanks! Check your messages — we're sending you the demo link now."

### n8n Integration
- Native node: `Facebook Lead Ads Trigger`
- One Meta App per form (Facebook API limitation — one trigger per app)
- For Phase 3 multiple verticals: use form_id field to route inside n8n

### Scoring → Routing Logic
| Call Volume | Current Service | Score | Action |
|---|---|---|---|
| 50+ | No | 9–10 | HOT: SMS Dan + immediate personal email |
| 30–50 | No | 7–8 | HOT: SMS Dan + immediate email |
| 10–30 | No | 5–6 | WARM: 3-email nurture |
| Any | Used to | 4–5 | WARM: nurture |
| Any | Yes | 3 | COLD: log only |
| Under 10 | Any | 1–2 | COLD: log only |

### HOT Lead Email (score 7+, sent within 2 minutes)
```
Subject: Here's the Syntharra demo — [first_name]

Hi [first_name],

Thanks for your interest — I wanted to get back to you straight away.

The best way to understand what we do is to hear it. Call this number
right now and experience our AI receptionist yourself:

📞 +1 (812) 994-4371

It's a real HVAC company using our system. Most people are surprised
how natural it sounds.

When you're ready to talk about setting this up for [company if known]:
👉 Book a free 15-min call: [Cal.com link]

Slots this week are limited — we only take on a few new clients at a time.

— Dan Blackmore
Founder, Syntharra AI
support@syntharra.com
```

---

## MECHANISM 3 — Email Lead Magnet (Phase 1)
**Asset:** "The HVAC Owner's Call Audit" — 1-page PDF
**Landing page:** `syntharra.com/call-audit`
**Delivery:** SMTP2GO from `noreply@syntharra.com`

### PDF Content (1 page)
**Title:** The HVAC Owner's Call Audit
**Subtitle:** Find out exactly how many leads you're losing and what it's costing you

**Section 1: Your Numbers**
- How many calls/day does your business receive? ___
- What % do you answer during business hours? ___% 
- What % do you answer after hours? ___%
- Average job value: $___

**Section 2: The Calculation**
```
Daily calls × (1 - answer rate) = Missed calls/day
Missed calls/day × 30 = Missed calls/month
Missed calls/month × 20% close rate × avg job value = Monthly revenue leakage

Example: 20 calls/day × 30% missed = 6 missed/day
6 × 30 days = 180 missed/month
180 × 20% close rate = 36 potential jobs
36 × $350 avg job = $12,600/month you're leaving on the table
```

**Section 3: The Fix**
- Syntharra AI receptionist answers every call, 24/7
- Set up in 24 hours. No contracts.
- Book a free 15-min call: [Cal.com link]
- Or call our demo line: +1 (812) 994-4371

### Landing Page (syntharra.com/call-audit)
- Simple: headline + 2-line description + name + email field + "Get the Free Audit" button
- On submit: webhook to n8n → email delivery → Supabase log
- UTM parameters passed through from whatever social post drove them here

### 3-Email Nurture Sequence (SMTP2GO)

**Email 1 — Immediate delivery**
```
Subject: Your HVAC Call Audit is attached 📊

Hi [first_name],

Here's your free call audit (attached).

Run the numbers — most HVAC owners are shocked when they see it.

The short version: if you're missing 20–30% of your calls,
you're likely losing $8,000–$15,000/month in potential revenue.

That's the problem Syntharra solves. Our AI receptionist answers
every call, 24/7, for a fraction of what a receptionist costs.

— Dan
P.S. Want to hear what it sounds like? Call +1 (812) 994-4371
```

**Email 2 — Day 3**
```
Subject: Real call, real HVAC company

Hi [first_name],

Did you have a chance to run your numbers from the audit?

I want to share something that shows exactly what we do.
Arctic Breeze HVAC in Indiana has been using Syntharra for
[X months]. Their AI receptionist handles every call —
even at 2am during an emergency.

Hear it yourself: +1 (812) 994-4371 (live demo — call now)

Most people call expecting a robot. They're surprised.

If you want to talk about setting this up for your business:
👉 [Cal.com link] — 15 minutes, no pressure

— Dan
```

**Email 3 — Day 7**
```
Subject: Last thing from me

Hi [first_name],

I don't want to keep filling your inbox.

This is the last email in this sequence — after this,
I'll only email you when we have something genuinely useful to share.

One question: did you run the call audit numbers?

If the answer is "yes and it was depressing" — we should talk.
If the answer is "not yet" — here's the link again: [audit page]

And if you're ready to see how Syntharra would work for you:
👉 [Cal.com link]

Either way, the demo line is always live: +1 (812) 994-4371

— Dan
```

---

## MECHANISM 4 — Retargeting Audiences (Phase 2)
**Platform:** Facebook/Instagram via Meta Custom Audiences
**Updated by:** n8n weekly CRON (Monday 6:30am, after Loop 5)

### Audience A — Warm: Video Viewers
**Definition:** People who watched 50%+ of any Syntharra video in the last 30 days
**Size:** Grows organically as videos get views
**Ad shown:** Demo call clip — "You watched this earlier. Ready to hear the real thing?"
**Setup:** Create in Meta Ads Manager as Video Engagement custom audience

### Audience B — Hot: Website Visitors
**Definition:** People who visited syntharra.com/demo.html in the last 30 days
**Requires:** Meta Pixel installed on syntharra.com (Events: PageView, Lead, Schedule)
**Ad shown:** Objection-handling ad — "Still thinking about it? Here's what HVAC owners say after 30 days."
**Setup:** Create Website Traffic custom audience, URL contains 'demo'

### Audience C — Lookalike: Like Our Clients
**Definition:** Facebook-built audience of people similar to paying Syntharra clients
**Source:** Custom audience of paying client emails (updated weekly from Stripe)
**Ad shown:** Cold pain point hook — same as organic content
**n8n update process:**
1. Stripe API → get all customer emails
2. Meta Marketing API → update Custom Audience with email list
3. Facebook auto-refreshes Lookalike from updated source

### n8n Audience Refresh Workflow
```
Every Monday 6:30am:
1. GET all Stripe customers → extract emails
2. Meta Marketing API: POST /{{audience_id}}/users
   { "payload": { "schema": ["EMAIL"], "data": [[hashed_email], ...] } }
   Note: Facebook requires SHA-256 hashed emails
3. Log to Supabase: audience_refresh_log table
4. Notify Dan: "Audiences updated. Client list: X emails."
```

---

## MECHANISM 5 — Organic Bio Link (Phase 1, Already Running)
**Existing:** demo.html already built with UTM tracking
**All platforms bio:** `syntharra.com/demo.html?utm_source=[platform]&utm_medium=organic&utm_campaign=hvac`

### UTM Values by Platform
| Platform | utm_source | utm_medium |
|---|---|---|
| Facebook | facebook | organic |
| TikTok | tiktok | organic |
| YouTube | youtube | organic |
| Instagram | instagram | organic |
| Facebook Ad | facebook | paid |

### Existing Hot Lead Detector Integration
This mechanism already feeds into the existing n8n hot lead detector workflow.
No new build required — just ensure UTM parameters are consistent.

---

## LEAD SCORING CONSOLIDATION

All leads from all 5 mechanisms flow into `website_leads` table.
Existing hot lead detector handles follow-up for high-score leads.

| Source field value | Mechanism |
|---|---|
| `comment_dm` | Mechanism 1 |
| `fb_lead_ad` | Mechanism 2 |
| `lead_magnet` | Mechanism 3 |
| `retargeting_ad` | Mechanism 4 |
| `demo_page_organic` | Mechanism 5 |
