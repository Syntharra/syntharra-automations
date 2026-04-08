# Syntharra Marketing Team Plugin

An autonomous marketing team for Syntharra's AI Receptionist product, built as a Cowork plugin. 7 specialized agents (skills) work in parallel to generate 50+ qualified HVAC leads per month.

## What You Need to Start

Almost nothing. This is designed to run lean.

### Already Built (ready to use)
- **syntharra.com** — full website with 21 blog articles, landing pages, lead magnets, demo page
- **Lead magnets** — AI Readiness Quiz, Revenue Calculator, Plan Quiz (all capture email → Supabase)
- **Google Ads landing pages** — `/lp/hvac-answering-service.html` + plumbing, electrical
- **Cold email system** — n8n + SMTP2GO (built, activate when ready)
- **HubSpot CRM** — full pipeline configured
- **Supabase** — lead database ready
- **Cal.com** — demo booking page live

### You Need to Set Up (one-time, ~2 hours total)
1. **Social media accounts** — create or claim business profiles on:
   - Facebook Business Page
   - LinkedIn Company Page
   - X (Twitter) account
   - TikTok Business account
   - Instagram Business account
   - YouTube channel
2. **A phone to record short videos** — that's it. No studio, no fancy equipment. Your phone camera, natural lighting, talking to camera or screen recordings of the AI receptionist in action. 30–90 seconds each.
3. **CapCut or similar** (free) — for adding captions to videos. Most HVAC owners watch with sound off. Captions are non-negotiable.
4. **A scheduling tool** (optional) — Buffer, Later, or Hootsuite free tier to queue posts across platforms. Or post manually — Cowork will prepare all the content, you just hit publish.
5. **Google Places API key** — for the Prospector to find HVAC businesses. Free tier gives 1,000 requests/month.

### That's It
No ad budget required to start. No expensive tools. No team to hire. The plugin does the strategy, writing, research, and planning. You record a few videos per week and hit publish.

### Optional (Add When Ready)
- **Google Local Services Ads** ($500/mo) — highest-intent paid channel for trades
- **Facebook/Meta Ads** ($500/mo) — targeting HVAC business owners
- **ElevenLabs** ($22/mo) — AI voiceover for video content if you prefer not to record yourself
- **Ahrefs/SEMrush** ($99/mo) — SEO keyword tracking (nice-to-have, not required)

---

## How It Works

### The 7 Agents (Skills)

| Agent | Skill | What It Does |
|---|---|---|
| Prospector | `/syntharra-marketing:prospect` | Finds HVAC businesses, scores them, feeds the pipeline |
| Outreach | `/syntharra-marketing:outreach` | Cold email sequences — personalized, compliant, conversion-focused |
| Content Engine | `/syntharra-marketing:content` | Blog articles, social posts, newsletters — all written content |
| Video Content | `/syntharra-marketing:video` | Short-form video scripts, hooks, captions for TikTok/Reels/Shorts |
| Conversion Optimizer | `/syntharra-marketing:optimize` | A/B tests, funnel analysis, landing page improvements |
| Intelligence | `/syntharra-marketing:intelligence` | Weekly performance analysis — tells every other agent what to change |
| Competitor Watch | `/syntharra-marketing:competitors` | Monitors competitors, flags threats and opportunities |

### Commands (Things You Trigger)

| Command | What It Does |
|---|---|
| `/syntharra-marketing:startup` | First-time setup — creates folder structure, config files, first prospect batch |
| `/syntharra-marketing:weekly-plan` | Generates this week's plan across all agents |
| `/syntharra-marketing:report` | Produces current performance report with lead count and recommendations |
| `/syntharra-marketing:batch-content` | Generates a full week of content in one session (blogs + social + video scripts) |

### The Weekly Rhythm

```
MONDAY    → Intelligence brief published. All agents adjust. Prospector batch #1. Blog #1.
TUESDAY   → Outreach sends batch #1. Social posts publish.
WEDNESDAY → Blog #2 published. Video scripts for the week finalized.
THURSDAY  → Prospector batch #2. Social posts publish.
FRIDAY    → Outreach sends batch #2. Weekend social posts queued.
SUNDAY    → Intelligence collects all data. Weekly brief produced.
```

### Scheduled Tasks

Use `/schedule` in Cowork to automate:

| Task | Schedule | Command |
|---|---|---|
| Prospect batch | Mon + Thu, 9 AM | `/syntharra-marketing:prospect` |
| Email batch | Tue + Fri, 10 AM | `/syntharra-marketing:outreach` |
| Blog publish | Mon + Wed, 8 AM | `/syntharra-marketing:content` |
| Social + video posts | Daily, 7 AM | `/syntharra-marketing:content` + `/syntharra-marketing:video` |
| Weekly intelligence | Sunday, 6 PM | `/syntharra-marketing:intelligence` |
| Competitor scan | 1st of month | `/syntharra-marketing:competitors` |

---

## Folder Structure

The plugin creates and manages this structure in your working folder:

```
syntharra-marketing/
├── prospects/                   ← Scored prospect lists
├── outreach/
│   ├── templates/               ← Email sequence templates
│   ├── sent/                    ← Send logs
│   └── results/                 ← Open/click/reply tracking
├── content/
│   ├── blog/                    ← Blog article drafts
│   ├── social/                  ← Social media posts (text platforms)
│   ├── video/                   ← Video scripts, hooks, captions
│   ├── email/                   ← Newsletter content
│   └── calendar.md              ← Content calendar
├── reports/
│   ├── weekly-intelligence.md   ← Weekly performance brief
│   ├── conversion-weekly.md     ← Funnel analysis
│   ├── competitor-monthly.md    ← Competitor intelligence
│   └── lead-tracker.csv         ← Master lead count
└── config/
    ├── target-cities.md         ← Priority HVAC markets
    ├── competitors.md           ← Competitor tracking
    ├── brand-voice.md           ← Voice and tone guidelines
    └── kpi-targets.md           ← Targets and thresholds
```

---

## KPI Targets

| Phase | Timeline | Qualified Leads/Month | Key Milestones |
|---|---|---|---|
| Foundation | Weeks 1–4 | 10–15 | First prospect batches. Email sequences sending. Content pipeline running. |
| Optimization | Weeks 5–8 | 25–35 | Intelligence loop driving improvements. Email open rates >25%. Blog traffic growing. |
| Scale | Weeks 9–12 | 50+ | All channels producing. Feedback loops tightening. Consistent lead flow. |

---

## Connectors

This plugin works best with these MCP connectors (configure in `.mcp.json`):

- **HubSpot** — CRM for lead tracking and pipeline management
- **Supabase** — Lead database and content storage
- **Gmail** — Email outreach monitoring
- **Google Calendar** — Demo booking tracking
- **Slack** — Weekly report delivery
