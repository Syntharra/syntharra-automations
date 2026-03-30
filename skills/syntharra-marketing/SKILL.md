---
name: syntharra-marketing
description: >
  Complete reference for all Syntharra marketing, lead generation, and growth systems.
  ALWAYS load this skill when: working on the automated lead generation system, cold email sequences,
  the demo landing page, the VSL (video sales letter), the Google Places lead sourcer, the n8n
  lead gen workflows, UTM tracking, Cal.com booking setup, hot-lead detection, or any outbound
  or inbound marketing activity. Also trigger for: content strategy, blog SEO, social media
  automation, affiliate program, Google Ads landing pages, or any growth/acquisition task.
---

# Syntharra Marketing & Lead Gen — Full Reference

---

## Lead Generation System (HVAC USA — Built, Not Yet Live)

### Architecture
```
Google Places API → Supabase (website_leads)
    ↓
n8n Cold Email Sequence (SMTP2GO)
    ↓
Click tracking / UTM → Demo landing page
    ↓
Hot Lead Detector → Cal.com booking
```

### Go-Live Sequence
1. Run SQL schema in Supabase
2. Import n8n workflows
3. Add credentials (Supabase + SMTP2GO)
4. Obtain Google Places API key
5. Configure Cal.com
6. Enable workflows

### n8n Lead Gen Workflows
| Workflow | ID |
|---|---|
| Lead Sourcer | (import from GitHub — `syntharra-automations` repo) |
| Email Sequence | (import from GitHub) |
| Hot Lead Detector | (import from GitHub) |
| Website Lead → AI Score | `FBNjSmb3eLdBS3N9` |
| Website Lead → Free Report | `ykaZkQXWO2zEJCdu` |

---

## Demo Landing Page

- File: `demo.html` in `Syntharra/syntharra-website`
- Features: animated demo, UTM tracking, Cal.com CTA
- Purpose: destination for cold email clicks

---

## VSL (Video Sales Letter)

**Status: In Production**

| Scene | Status |
|---|---|
| Scene 1 | ElevenLabs voiceover script written |
| Scene 2 | ElevenLabs voiceover script written |
| Scene 3 | Needs demo call recording (call `+1 812 994 4371` as "Mike Henderson") |
| Scene 4 | Cost comparison graphic built (HTML, 1920×1080) |
| Scene 5 | ElevenLabs voiceover script written |

CapCut assembly guide built. VSL package: `Syntharra_VSL_Package.docx` in automations repo.

---

## Cal.com

- Used as booking CTA on demo landing page and throughout marketing
- Link appears across: demo page, blog CTAs, exit-intent popups, AI readiness quiz, revenue calculator, plan quiz

---

## Website Lead Magnets (all email-gated → Supabase)

| Tool | URL | Purpose |
|---|---|---|
| AI Readiness Quiz | `/ai-readiness.html` | Assess readiness, capture email |
| Revenue Calculator | `/calculator.html` | Show missed revenue, capture email |
| Plan Quiz | `/plan-quiz.html` | Match to Standard/Premium, capture email |
| Content Upgrades | 5 blog articles | Checklist/template/guide gated content |

All feeds: `website_leads` Supabase table → n8n webhook notification

---

## Google Ads Landing Pages

Located in `/lp/` directory — noindex, no nav, single CTA focus:
- `lp/hvac-answering-service.html`
- `lp/plumbing-answering-service.html`
- `lp/electrical-answering-service.html`

---

## Blog SEO

- 8 blog articles live (+ index page)
- Article schema markup on all posts
- Template: `_template/BLOG_STANDARD.md` in website repo
- Author: "Syntharra Team" | Role: "AI Solutions for Trade Businesses"
- Bottom CTA on every article: Book a Call + Demo buttons

### Blog Newsletter
- Subscribe wired to Supabase `website_leads` + n8n webhook
- TODO: Wire subscribe input → Supabase directly

---

## Exit-Intent Popups

Context-aware popups on: HVAC, Plumbing, Electrical industry pages, How It Works, Case Studies

---

## Affiliate Program

- Page: `/affiliate.html`
- Form wired to Supabase

---

## Pricing Strategy

| Plan | Monthly | Annual | Setup |
|---|---|---|---|
| Standard | $497/mo | $414/mo | $1,499 |
| Premium | $997/mo | $831/mo | $2,499 |

**Pricing is NOT public on the website.** Never display dollar amounts or link to pricing page from public-facing content.

Checkout URL: `checkout.syntharra.com`

---

## Marketing Expansion Plan

- Single-parameter redeployment: HVAC USA → other US trades → international
- Same lead gen architecture adapts by changing industry + geography parameter
- Repo architecture: `hvac-standard/`, `plumbing-standard/`, etc. in `syntharra-automations`

### Target Verticals (after HVAC USA)
- Plumbing
- Electrical
- Cleaning
- Pest Control
- Landscaping

### Target Geographies (after USA)
- Canada
- UK
- Australia
- Ireland

---

## Brand Voice

- Professional but approachable
- Confidence without arrogance — "your competitors are already using AI"
- Urgency without pressure
- Clear ROI focus: missed calls = missed revenue
- Target persona: HVAC business owner, 5-30 employees, overwhelmed by phone volume

---

## Key Messaging

- "Never miss another call"
- "Your AI receptionist works 24/7"
- "Set up in 24 hours"
- "Cancel anytime"
- Country/market count: "10+ countries" (updated from 30+)

---

## SMTP2GO (Email)

All cold outreach and automated emails via SMTP2GO:
- API Key: `api-0BE30DA64A074BC79F28BE6AEDC9DB9E`
- n8n credential: `"SMTP2GO - Syntharra"`
- Sender: `noreply@syntharra.com`

Email template rules: Light theme only — white cards, grey outer bg, purple accents. See `syntharra-website` skill for logo block code.
