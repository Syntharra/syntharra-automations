---
name: syntharra-social-leads
description: >
  Complete reference for Syntharra's automated social media content marketing and lead generation
  system. ALWAYS load this skill when: building or editing any part of the social content pipeline,
  working on Blotato API integrations, building or modifying the performance feedback loops,
  setting up Facebook Lead Ads or comment-to-DM automation, working on ad scaling/pausing logic,
  managing the retargeting audience engine, building the email/lead magnet funnel, adding new
  trade verticals (electrical, plumbing etc), checking which phase the system is in, asking about
  content strategy or video creation for social media, working on the infinite content loop,
  attributing revenue back to content pieces, or any task involving short-form video, social
  posting, lead capture, or paid ad automation for Syntharra. Three phases: Phase 1 = organic
  only (HVAC), Phase 2 = paid ads added (HVAC), Phase 3 = multi-vertical scale.
---

# Syntharra Social Media Lead Generation System

## Quick Reference — Current Status
- **Active Phase:** Check `syntharra_vault` or `project-state.md` for current phase
- **Active Vertical:** HVAC USA (Phase 1 default)
- **Primary Platforms:** Facebook, YouTube Shorts, TikTok, Instagram (secondary)
- **Core Tool:** Blotato ($29/mo Starter → $97/mo Creator when scaling)
- **All config stored in:** Supabase `syntharra_vault` + `content_*` tables

---

## THE THREE PHASES

### PHASE 1 — Organic Only (Start Here)
**Trigger:** Pre-launch through first 5 clients
**Cost:** ~$39/mo new spend (Blotato $29 + Claude API ~$10)
**Goal:** Build content base, test hooks, capture first leads organically

What runs in Phase 1:
- Weekly content generation loop (Claude → Blotato → post)
- Organic performance feedback loop (Sunday night analysis)
- Comment-to-DM automation (Spur, free tier)
- Email lead magnet funnel (call audit PDF)
- Manual review of all metrics — no paid spend

What does NOT run in Phase 1:
- No paid ads
- No auto-boosting
- No retargeting audiences
- No ad scaling logic

**Content volume:** 8 videos/mo + 8 static posts + unlimited text posts
**Platforms:** Facebook Page + YouTube Shorts channel + TikTok (HVAC-focused)
**Account naming:** `@syntharra` or `@syntharraHVAC` — niche bio, not generic

---

### PHASE 2 — Paid Ads Added (5–10 Clients)
**Trigger:** 5 paying HVAC clients OR consistent organic traction (500+ views/video)
**Cost:** ~$112/mo tools + $50–200/week ad spend
**Goal:** Amplify what's already working organically. Test → boost → scale.

Additional systems activated in Phase 2:
- Auto-boost loop (organic winners → Facebook ads automatically)
- Ad performance loop (Claude analyses ads every 24hrs → scale/pause/hold)
- Facebook Lead Ads wired into n8n (in-platform lead capture)
- Retargeting audiences built and refreshed weekly
- Revenue attribution active (UTM → Stripe → content piece)

**Upgrade Blotato:** Starter → Creator ($97/mo) for 5,000 credits/mo
**Ad budget guidance:** Start at $10/day per boosted post. Max $50/day until ROAS proven.

---

### PHASE 3 — Multi-Vertical Scale (10+ Clients)
**Trigger:** 10+ HVAC clients OR decision to expand to electrical/plumbing
**Cost:** ~$154/mo tools + scaled ad spend per vertical
**Goal:** Duplicate entire system per vertical with minimal rebuild

Additional systems in Phase 3:
- Full revenue attribution across all verticals
- Cross-platform learning loop (what works on HVAC informs electrical launch)
- Separate social accounts per vertical (`@syntharraElectrical`, `@syntharraPlumbing`)
- n8n `industry` parameter controls all content generation — one workflow, 3 verticals
- Blotato brand kits: one per vertical (HVAC / Electrical / Plumbing)

**Scaling rule:** One Blotato account, 3 brand kits. Only split accounts if handing a
vertical to a separate operator.

---

## FULL TECH STACK

### Core Tools (always running)
| Tool | Purpose | Cost | Account/Key Location |
|---|---|---|---|
| n8n (Railway) | All orchestration | Already running | `syntharra_vault: n8n Railway` |
| Supabase | All data storage | Already running | `syntharra_vault: Supabase` |
| Blotato | Video creation + posting | $29–97/mo | `syntharra_vault: Blotato` |
| Claude API | Scripts, captions, analysis | ~$10–15/mo | `syntharra_vault: Claude` |
| SMTP2GO | Email delivery | Already running | `syntharra_vault: SMTP2GO` |
| Telnyx | SMS notifications | Already running | `syntharra_vault: Telnyx` |

### Phase 1 Additions
| Tool | Purpose | Cost | Notes |
|---|---|---|---|
| Spur | Comment-to-DM automation | Free tier | spur.so — connect FB + IG |
| Cal.com | Booking CTA | Already running | Existing setup |

### Phase 2 Additions
| Tool | Purpose | Cost | Notes |
|---|---|---|---|
| Meta Graph API | Pull post analytics | Free | Needs Meta Business App |
| Meta Marketing API | Create/scale/pause ads | Free | Same app, same token |
| Facebook Lead Ads | In-platform lead forms | Free (pay per lead) | Native n8n trigger node |
| Meta Pixel | Website visitor tracking | Free | Install on syntharra.com |
| TikTok Business API | Pull TikTok analytics | Free | Requires app approval (3–5 days) |

### Phase 3 Additions
| Tool | Purpose | Cost | Notes |
|---|---|---|---|
| Blotato Brand Kits | Per-vertical branding | Included | 3 kits: HVAC/Electrical/Plumbing |
| Additional social accounts | Per-vertical posting | Free | Create accounts before launch |

---

## SUPABASE SCHEMA

For full SQL, see: `references/supabase-schema.sql`

### Tables Overview
| Table | Purpose | Phase |
|---|---|---|
| `content_ideas` | Weekly content briefs from Claude | 1 |
| `content_scripts` | Scripts, hooks, CTAs per idea | 1 |
| `content_posts` | Per-platform post records + status | 1 |
| `content_performance` | Weekly metrics per post | 1 |
| `content_patterns` | Weekly Claude analysis output | 1 |
| `content_ads` | Ad records, budgets, status | 2 |
| `loop_decisions` | Every AI scale/pause/create decision | 2 |
| `lead_magnet_subscribers` | Email list from call audit PDF | 1 |

All lead data flows into existing `website_leads` table — do NOT create a separate leads table.

---

## THE FIVE AUTOMATION LOOPS

For full n8n workflow specs, see: `references/n8n-workflows.md`

### Loop 1 — Weekly Content Generation (Phase 1)
**Schedule:** Monday 7am
**Flow:** Claude generates 7 ideas → scripts per idea → Blotato renders videos →
Blotato schedules posts → Supabase logs everything
**Key parameter:** `industry` (default: "HVAC") — change this for Phase 3 verticals

### Loop 2 — Organic Performance Feedback (Phase 1)
**Schedule:** Sunday 11pm
**Flow:** Pull metrics from Facebook Graph API + TikTok API → store in
`content_performance` → Claude analyses patterns → writes winning brief to
`content_patterns` → Monday's Loop 1 uses this brief as context
**Output to you:** Slack/email summary with top 3 posts + recommended angles for next week

### Loop 3 — Auto-Boost Winners (Phase 2)
**Schedule:** Every 48 hours
**Threshold:** Watch time >60% AND link clicks >10 in past 48hrs
**Flow:** If post exceeds threshold → Meta Marketing API creates ad ($10/day, 5-day test)
→ Supabase logs ad → Slack notification to Dan for awareness (not approval-gated)
**Safety:** Hard cap $50/day total across all active test ads

### Loop 4 — Ad Scale/Pause Engine (Phase 2)
**Schedule:** Every 24 hours
**Flow:** Pull all active ad metrics → Claude analyses each ad against benchmarks →
SCALE (CPC <$1.50 + CTR >3% + 3+ days running): increase budget 50%
PAUSE (CPC >$3.00 OR CTR <1% after 3+ days): pause ad
HOLD: no action
→ All decisions logged to `loop_decisions` with Claude's reasoning
→ Weekly digest email to Dan: what scaled, what paused, top performers

### Loop 5 — Cross-Platform Learning + Revenue Attribution (Phase 2/3)
**Schedule:** Monday 6am (runs before Loop 1)
**Flow:** Pull all Stripe payments from past 7 days → match to `website_leads` UTM
source → identify which `content_posts` drove revenue → inject winning content
angles into Monday's content brief as highest-priority instructions to Claude
**Output:** "Post X on TikTok → $497 MRR attributed. Angle: missed-call-cost.
Make 3 more scripts using this exact angle."

---

## THE FIVE LEAD CAPTURE MECHANISMS

### Mechanism 1 — Comment-to-DM (Phase 1, Spur)
**Setup:** Connect Facebook Page + Instagram to Spur
**Trigger keyword:** "DEMO" (used in every video CTA)
**DM template:**
```
Hey [first_name] — here's that demo call I mentioned.
This is a real HVAC company using our AI receptionist.
Call this number and hear it yourself: +1 (812) 994-4371

Want to see how it works for YOUR business?
Grab a free 15-min slot: [Cal.com link]

— Dan, Syntharra
```
**Follow-up:** If no reply in 48hrs → one follow-up DM only. Never more than 2 DMs.
**n8n integration:** Spur webhook → n8n → score lead → Supabase `website_leads`

### Mechanism 2 — Facebook Lead Ads (Phase 2)
**Form fields (pre-filled by Facebook):** Name, Email, Phone
**Custom questions:**
1. "How many inbound calls does your business receive per day?" (dropdown: <10 / 10–30 / 30–50 / 50+)
2. "Are you currently using an answering service?" (Yes / No / Used to)
**n8n trigger:** Native `Facebook Lead Ads Trigger` node (built into n8n)
**Scoring:** Claude scores 1–10 based on call volume + current setup
Score 7+: Telnyx SMS to Dan within 2 minutes + Cal.com link sent to lead
Score 4–6: 3-email SMTP2GO nurture sequence
Score 1–3: Logged only

### Mechanism 3 — Email Lead Magnet (Phase 1)
**Asset:** "The HVAC Owner's Call Audit" — 1-page PDF calculator
**Page:** `syntharra.com/call-audit` (simple form — name + email)
**Delivery:** Instant SMTP2GO email with PDF attached from `noreply@syntharra.com`
**Nurture sequence (3 emails, SMTP2GO):**
- Day 1: PDF + "What Syntharra does in 60 seconds"
- Day 3: Arctic Breeze demo call link + one-line case study
- Day 7: "Book a free 15-min call" — Cal.com CTA
**Storage:** Supabase `lead_magnet_subscribers` + `website_leads`

### Mechanism 4 — Retargeting Audiences (Phase 2)
Three Facebook Custom Audiences, refreshed weekly by n8n:
- **Warm:** 50%+ video viewers, last 30 days → show demo call clip ad
- **Hot:** demo.html visitors (Meta Pixel) → show objection-handling ad
- **Lookalike:** Built from paying Stripe client emails → show cold pain-point ad
**n8n refresh:** Weekly CRON → Stripe API → extract client emails →
Meta Marketing API → update Custom Audience

### Mechanism 5 — Organic Bio Link (Phase 1)
**All platforms:** Bio links to `syntharra.com/demo.html?utm_source=[platform]`
**Existing hot lead detector handles all demo.html visits** — no new build needed

---

## CONTENT STRATEGY

### Account Structure
- **Phase 1:** One account per platform — bio: "AI Receptionists for HVAC Companies | Never Miss a Call"
- **Phase 3:** Sub-branded per vertical: `@syntharraHVAC`, `@syntharraElectrical`, `@syntharraPlumbing`
- **Never** use "Global AI Solutions" as social bio — too generic, kills niche targeting

### Content Mix (per week, Phase 1)
| Type | Volume | Credits Used | Platform Priority |
|---|---|---|---|
| Faceless video (mid quality) | 4–5 | ~120–150 each | Facebook, YT Shorts, TikTok |
| Static image post | 2–3 | 15 each (recraft) | Instagram, LinkedIn |
| Text-only post | Unlimited | 0 | All platforms |

### The 8 Content Pillars
1. **Missed Calls = Missed Money** — every unanswered call is a lost job
2. **After Hours Is Where You Lose** — competitors who answer at 10pm win
3. **Your Staff Shouldn't Answer Phones** — admin time = money wasted
4. **AI vs Hiring a Receptionist** — cost comparison (VSL Scene 4 graphic)
5. **The Follow-Up Problem** — leads go cold in under 5 minutes
6. **What Happens On A Call** — show the Arctic Breeze demo in action
7. **Your Ad Spend Is Wasted** — ROI angle for Google Ads users
8. **Built For HVAC, Not Generic AI** — differentiation from chatbots

### Rotating Hook Styles (rotate weekly — never same style twice in a row)
- **Stat hook:** "73 HVAC companies out of 100 sent us to voicemail"
- **Story hook:** "Your phone rang at 9pm. Here's what happened."
- **Question hook:** "What does your customer hear when you miss their call?"
- **Bold claim hook:** "Your ad spend is wasted if you don't answer"

### CTA Rotation (vary — never use same CTA twice in a week)
- "Comment DEMO below and I'll send you the link"
- "Link in bio to hear a real call"
- "Book a free audit at syntharra.com — link in bio"
- "Call +1 (812) 994-4371 right now and hear it yourself"
- "DM me HVAC and I'll send you the free call audit"

### Highest-Value Content Asset
**The Arctic Breeze demo call recording.** Call +1 (812) 994-4371 as "Mike Henderson"
to record a real call. This is more convincing than any produced video.
Use in every 2nd–3rd video. It is your #1 proof asset.

---

## BLOTATO INTEGRATION

### API Endpoint Pattern
```
POST https://backend.blotato.com/v2/posts
Headers: blotato-api-key: [from syntharra_vault]
```

### Video Generation (n8n → Blotato)
```json
{
  "blotato_api_key": "{{from_vault}}",
  "template": "empty",
  "voiceId": "elevenlabs/eleven_multilingual_v2/JBFqnCBsd6RMkjVDRZzb",
  "captionPosition": "bottom",
  "script": "{{claude_generated_script}}",
  "style": "cinematic",
  "animate_first_image": true,
  "animate_all": false,
  "text_to_image_model": "replicate/recraft-ai/recraft-v3",
  "image_to_video_model": "fal-ai/framepack"
}
```

### Credit Budget Rules
- **Phase 1 (Starter, 1,250 credits/mo):** Use recraft-v3 images (15 credits) + framepack video (55 credits). Target: 4–5 videos/mo at mid quality (~120–180 credits each) + static posts.
- **Phase 2/3 (Creator, 5,000 credits/mo):** 20 videos/mo per vertical at mid quality. Buy $6.99/1,000 top-up packs if needed.
- **Never** use veo2 (835 credits) or veo3 (1,250 credits) — too expensive for volume

### Platform Account IDs (store in Supabase `syntharra_vault`)
```
service_name: 'Blotato'
key_type: 'facebook_account_id'    → HVAC Facebook Page ID
key_type: 'youtube_account_id'     → HVAC YouTube channel ID
key_type: 'tiktok_account_id'      → HVAC TikTok account ID
key_type: 'instagram_account_id'   → HVAC Instagram account ID
key_type: 'api_key'                → Blotato API key
```

---

## META API SETUP (Phase 2 prerequisite)

1. Go to `developers.facebook.com` → Create App → Business type
2. Add products: Facebook Login + Instagram Graph API + Marketing API
3. Generate Page Access Token (never expires if set up correctly)
4. Store in `syntharra_vault: Meta, key_type: page_access_token`
5. Install Meta Pixel on `syntharra.com` — standard events: PageView, Lead, Schedule
6. Create Custom Audiences manually first in Ads Manager — then automate refresh via API

**Key API endpoints used:**
- `GET /{page-id}/posts?fields=insights` — organic post metrics
- `POST /act_{ad-account-id}/adcreatives` — create ad from post
- `POST /act_{ad-account-id}/ads` — launch ad
- `GET /act_{ad-account-id}/insights` — ad performance data
- `POST /act_{ad-account-id}/customaudiences/{id}/users` — update retargeting audience

---

## REVENUE ATTRIBUTION (Phase 2)

### UTM Structure
Every social post/ad uses:
```
utm_source=[platform]        facebook | tiktok | youtube | instagram
utm_medium=[type]            organic | paid
utm_campaign=[vertical]      hvac | electrical | plumbing
utm_content=[post_id]        Supabase content_posts.id
```

### Attribution Chain
1. `demo.html` captures UTM → stored in `website_leads.utm_source/content`
2. Cal.com booking includes lead email
3. Stripe `checkout.session.completed` → n8n matches email → finds `website_leads` record
4. Revenue written to `content_posts` via `content_performance.attributed_revenue`
5. Loop 5 reads this field to prioritise content angles

---

## KEY RULES & GOTCHAS

- **Never post pricing publicly.** All CTAs go to demo or booking — never mention $497/$997
- **Spur free tier limit:** Monitor DM volume — upgrade if hitting limits
- **TikTok API approval:** Apply early — takes 3–5 business days
- **Meta Pixel must be installed** before Phase 2 retargeting will work
- **Facebook Lead Ads n8n limitation:** One trigger per Meta App — use one form per vertical max, route by form_id inside n8n
- **Blotato API key activates paid plan** — do not generate during free trial unless ready to subscribe
- **ElevenLabs voice is included in Blotato** — do NOT pay for separate ElevenLabs subscription
- **Credits roll over** month-to-month on Blotato paid plans
- **Comment-to-DM compliance:** Never send more than 2 DMs to any person. Respect Meta's 24-hour messaging window rules.
- **Ad scaling safety:** Claude must never scale an ad that has been running <3 days. Minimum data window is 72 hours before any budget change.
- **Always check `syntharra_vault`** for API keys — never hardcode in workflows

---

## ADDING A NEW VERTICAL (Phase 3 Checklist)

When expanding to Electrical or Plumbing:
1. Create social media accounts (`@syntharraElectrical` etc.)
2. Add Blotato brand kit for the new vertical
3. Add social account IDs to `syntharra_vault`
4. Update n8n Loop 1 `industry` parameter to include new vertical
5. Write 8 content pillars for new vertical (adapt from HVAC — change pain points)
6. Create new Facebook Lead Ad form for new vertical
7. Create new retargeting audiences in Meta Ads Manager
8. Add UTM `utm_campaign=[vertical]` to all new posts
9. Update `content_ideas` table to include `vertical` column if not present
10. Test one full content cycle manually before enabling automation

**Time to add a vertical:** ~30 minutes of config + 1 day of testing

---

## REFERENCE FILES

Read these when working on specific parts of the system:

- `references/supabase-schema.sql` — Full SQL for all content tables
- `references/n8n-workflows.md` — Step-by-step workflow specs for all 5 loops
- `references/ad-benchmarks.md` — Claude's decision thresholds for ad scaling
- `references/content-prompts.md` — Claude API prompts for each content generation step
- `references/lead-capture-flows.md` — Detailed specs for all 5 lead capture mechanisms
