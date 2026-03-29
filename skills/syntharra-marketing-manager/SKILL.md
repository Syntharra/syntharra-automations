---
name: syntharra-marketing-manager
description: >
  The Syntharra Marketing Manager skill. Deploy the full automated lead generation
  and outreach funnel for any trade industry (HVAC, Plumbing, Electrical, Landscaping,
  Pest Control, etc.) in any country or region.

  ALWAYS use this skill when Dan asks about: getting leads, finding HVAC/trade businesses
  to contact, cold email outreach, demo call scripts, video landing pages, social media
  content for Syntharra, TikTok or LinkedIn posts about the AI receptionist, automating
  lead generation, sourcing business contacts, building a prospect list, sending outreach
  emails via n8n, setting up solutions@syntharra.com email sequences, or anything related
  to Syntharra marketing, sales pipeline, or customer acquisition.

  Also trigger for: "get me leads", "find HVAC companies", "build me a demo", "write a
  cold email", "social media content", "marketing automation", "outreach sequence",
  "prospect list", "video landing page", or any variation of these.

  Output: Complete working funnel — lead sourcing workflow, cold email sequence, demo
  call transcripts, video landing page, social content calendar, n8n automation JSON,
  and Supabase schema — all parameterised by industry and region.
---

# Syntharra Marketing Manager

Automated lead generation and outreach funnel for Syntharra. Parameterised by industry
and region. Point it at a trade vertical + geography and it builds the full system.

## The Funnel Architecture

```
Google Places API / Web Scraping
    │ Pull trade businesses by industry + city/state/country
    ▼
Supabase (leads table)
    │ Store: name, phone, email, website, address, industry, region, status
    ▼
n8n Cold Email Sequence (3-email drip via SMTP2GO → solutions@syntharra.com)
    │ Personalised with business name + industry
    │ Email 1: Hook + demo video link (Day 0)
    │ Email 2: Social proof + urgency (Day 3)
    │ Email 3: Final CTA + booking link (Day 7)
    ▼
Click Tracking (video link clicked = HOT LEAD)
    │ Fires instant alert → Dan's phone + email
    ▼
Video Landing Page (syntharra.com/demo)
    │ Shows AI receptionist demo call
    │ Single CTA: "Book a Free Demo" → Cal.com booking link
    ▼
Booked Call → Dan closes the deal
```

---

## How To Use This Skill

### Step 1: Gather Parameters

Confirm with Dan (or infer from context):

| Parameter | Default | Notes |
|---|---|---|
| `industry` | HVAC | Any trade vertical |
| `region` | USA | Country or state/city |
| `cities` | Top 10 US cities by HVAC density | Or specify cities |
| `email_sender` | solutions@syntharra.com | Always this for outreach |
| `booking_link` | To be set by Dan | Cal.com or Calendly URL |
| `demo_scenario` | Both (emergency + quote) | Or choose one |

### Step 2: Choose What To Build

Read user request and generate only what's needed. Full system = all components.
Single component requests = just that component.

**Components:**
1. **Lead Sourcing** → `references/lead-sourcing.md`
2. **Demo Calls** → `references/demo-calls.md`
3. **Cold Email Sequence** → `references/email-sequence.md`
4. **Video Landing Page** → `references/landing-page.md`
5. **Social Content Calendar** → `references/social-content.md`
6. **n8n Automation** → `references/n8n-automation.md`

### Step 3: Adapt Per Industry

Read the relevant industry profile:
- HVAC → `references/industries/hvac.md`
- Plumbing → `references/industries/plumbing.md`
- Electrical → `references/industries/electrical.md`
- Generic → `references/industries/generic-trade.md`

Each profile contains: pain points, hook angles, cold email subject lines,
demo call scenarios, social content hooks, and lead signals.

### Step 4: Generate Outputs

Save all outputs to `/mnt/user-data/outputs/` for download. Always generate:
- Executable n8n workflow JSON (ready to import)
- Cold email HTML templates (light theme, Syntharra brand)
- Demo call transcripts (both scenarios unless Dan picks one)
- Landing page HTML (single file, deployable to syntharra.com)
- Social content calendar (30 days of posts)

---

## Brand Rules (Apply To All Output)

All emails, pages, and content must follow Syntharra brand standards:

| Rule | Value |
|---|---|
| Primary colour | `#6C63FF` (violet) |
| Accent colour | `#00D4FF` (cyan) |
| Email theme | LIGHT ONLY — white cards, `#F7F7FB` bg, `#1A1A2E` text |
| Outreach sender | `solutions@syntharra.com` |
| Internal alerts | `admin@syntharra.com` |
| Tone | Direct, confident, no fluff. "Your phone is losing you money" not "We'd love to help" |
| CTA | Always one clear CTA. Never more than one per email or page |

---

## Demo Call Generation

Two scenarios. Generate both unless Dan picks one.

### Scenario A — Emergency Call (More Dramatic)

**Setup:** It's 8pm on a Friday in July. AC unit failed. House at 95°F. Elderly parent inside.
**Goal:** Show the AI staying calm, collecting info, dispatching urgently, not missing the lead.
**Hook for business owners:** "This call came in at 8pm on a Friday. Your phone rang. Who answered?"

See `references/demo-calls.md` for full transcript templates.

### Scenario B — New Customer Quote

**Setup:** Homeowner calling Monday morning. Wants a quote for AC replacement. Ready to buy.
**Goal:** Show the AI gathering all info, booking the appointment, upselling service plan.
**Hook for business owners:** "This caller had $8,000 to spend. Did your voicemail get it?"

---

## Lead Sourcing Strategy

Three methods, run in order:

1. **Google Places API** (best quality, requires API key)
   - Search: `"hvac contractor" near "{city}, {state}"`
   - Returns: name, address, phone, website, rating, review count
   - Filter: 5+ reviews (established businesses), has phone number

2. **Apollo.io / Hunter.io API** (email discovery)
   - Input: business name + domain from Places
   - Output: owner/manager email address
   - Fallback: `info@domain.com` or `contact@domain.com`

3. **Web scraping fallback** (if no API key)
   - Yelp, Angi, HomeAdvisor business listings
   - Pull name, phone, location, website

See `references/lead-sourcing.md` for full implementation.

---

## Cold Email Rules

- Sender: `solutions@syntharra.com`
- Subject lines: test 3 variants (see industry file)
- Body: max 100 words. One link. One CTA.
- Personalisation: `{{business_name}}`, `{{city}}`, `{{industry}}`
- Tracking: unique UTM link per lead for click detection
- SMTP: SMTP2GO (`api-0BE30DA64A074BC79F28BE6AEDC9DB9E`)
- Sequence: 3 emails over 7 days, stop on reply or booking

See `references/email-sequence.md` for full templates.

---

## n8n Automation IDs (Syntharra Cloud)

Deploy new marketing workflows to: `syntharra.app.n8n.cloud`
Use existing Supabase: `hgheyqwnrcvwtgngqdnq.supabase.co`

New tables needed:
- `marketing_leads` — all sourced prospects
- `email_events` — sends, opens, clicks per lead
- `booked_demos` — converted leads

See `references/n8n-automation.md` for full workflow JSON.

---

## Social Content Strategy

Platform priority: TikTok → Instagram Reels → LinkedIn

**Content pillars (rotate weekly):**
1. Demo call clip — show the AI handling a real call
2. "Did you know" — stat about missed calls costing trades businesses
3. Before/after — voicemail vs. AI receptionist
4. Behind the scenes — how Syntharra sets up a client
5. Objection handling — "isn't it expensive?" answered in 30 seconds

**Posting cadence:** 4x per week TikTok, 3x Instagram, 2x LinkedIn
**Automation:** Buffer or n8n → social APIs where available

See `references/social-content.md` for 30-day content calendar.

---

## Output Checklist

Before declaring done:

- [ ] Lead sourcing n8n workflow JSON — valid, importable
- [ ] Supabase schema SQL — creates `marketing_leads`, `email_events`, `booked_demos`
- [ ] Email sequence — 3 HTML templates (light theme, Syntharra brand)
- [ ] Demo call transcripts — both scenarios (emergency + quote)
- [ ] Landing page HTML — single file, deployable, embeds demo video
- [ ] Social content calendar — 30 days, 3 platforms
- [ ] All outputs parameterised: swap `industry` variable to redeploy for plumbing/electrical

---

## Reference Files

| File | Read When |
|---|---|
| `references/lead-sourcing.md` | Building lead scraping workflow |
| `references/demo-calls.md` | Generating demo call transcripts |
| `references/email-sequence.md` | Writing cold email templates |
| `references/landing-page.md` | Building video landing page |
| `references/social-content.md` | Creating social content calendar |
| `references/n8n-automation.md` | Building n8n workflows |
| `references/industries/hvac.md` | HVAC-specific hooks, pain points, scripts |
| `references/industries/plumbing.md` | Plumbing-specific content |
| `references/industries/electrical.md` | Electrical-specific content |
| `references/industries/generic-trade.md` | Generic trade fallback |
