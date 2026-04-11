# Autonomous Marketing Team — Design Spec
**Date:** 2026-04-11  
**Author:** Claude (approved by Dan Blackmore)  
**Status:** Approved for implementation

---

## The One Metric That Matters

**Clients onboarded at $697/mo.** Every agent, every video, every post is optimised for this single outcome. The funnel is:

```
Short-form video (YouTube/TikTok/Instagram/Facebook)
  → syntharra.com
  → VSL (video sales letter)
  → 14-day free trial signup
  → Onboarded client
```

All performance tracking traces back to this funnel. A video with 100k views that produces zero trial signups is a failure. A video with 2k views that produces 3 signups is a win.

---

## Dan's Role

**CEO approval only.** Dan reviews and approves:
1. This week's video scripts + previews (via Slack + dashboard)
2. Strategic direction changes (via Slack)

Dan does NOT: write copy, source leads, post content, monitor analytics, manage platforms, or make tactical decisions. The team handles everything else autonomously.

---

## The Team — 9 Agents

### 1. Intelligence Agent
**Schedule:** Daily 06:00 UTC  
**Job:** Research what content is driving real results in the HVAC/contractor space right now.

- Scrapes YouTube search results for "HVAC business tips", "contractor missed calls", "answering service HVAC" — extracts titles, view counts, like ratios, comment sentiment
- Scrapes Reddit r/HVAC, r/Contractor, r/smallbusiness — extracts top posts, pain point language, recurring complaints
- Monitors Google Trends for HVAC-related search spikes
- Extracts winning patterns: hook formats, emotional triggers, video lengths, posting times
- Stores findings to Supabase `marketing_intelligence` table with confidence scores
- **Output:** Daily intelligence brief — top 5 trending angles with evidence

### 2. Competitor Watch Agent
**Schedule:** Monday 06:30 UTC  
**Job:** Monitor what competitors are posting and find gaps Syntharra can own.

- Tracks top 5 competitor YouTube/social channels weekly
- Identifies their top-performing content (views, engagement)
- Identifies topics they are NOT covering — these are Syntharra's content gaps
- Flags any competitor pricing/positioning changes
- Stores to `competitor_intelligence` table
- **Output:** Weekly competitor brief fed into Video Content Agent

### 3. Video Content Agent
**Schedule:** Mon/Wed/Fri 07:00 UTC  
**Job:** Write 2 video concepts per run (6/week) based on what Intelligence and Competitor Watch found.

For each concept:
- **Hook** — first 2 seconds, based on top-performing hook formats from intelligence
- **Script** — 30-45 seconds, pain-first structure, CTA to syntharra.com free trial
- **Visual prompt** — Higgsfield-ready prompt describing footage, mood, style
- **Reasoning** — why this will work: "3 videos using this hook format averaged 47k views this week in the contractor space"
- **Platform targets** — which platforms this format suits best
- **Confidence score** — based on intelligence data strength

Stores to `content_queue` table with `status = 'pending_approval'`.  
Sends Slack message to #marketing-team: "6 video concepts ready for your review → [dashboard link]"

### 4. Video Production Agent
**Schedule:** Triggered on Dan's approval  
**Job:** Turn approved scripts into complete, ready-to-post videos.

- Sends script to **Higgsfield AI Plus** (Cinema Studio 3.0) — generates cinematic footage + native audio + voiceover in one generation
- Adds auto-captions (85% of video is watched on mute)
- Exports 9:16 vertical format (YouTube Shorts / TikTok / Reels) + 16:9 horizontal (YouTube standard)
- Uploads rendered video to Supabase storage
- Updates approval dashboard with final preview
- Sends to Blotato API for scheduled distribution

### 5. Distribution Agent (via Blotato)
**Schedule:** Triggered by Video Production Agent  
**Job:** Post approved videos to all platforms simultaneously.

- Single Blotato API call posts to: YouTube, TikTok, Instagram, Facebook, LinkedIn
- Schedules posts at optimal times per platform (based on Performance Tracker data)
- Stores post URLs and platform IDs to `marketing_campaigns` table
- **Default posting times:** YouTube 18:00, TikTok 19:00, Instagram 17:00, Facebook 20:00 (local US time, adjusted per performance data)

### 6. Content Engine Agent
**Schedule:** Tue/Thu 07:00 UTC  
**Job:** Repurpose each approved video into 5 additional content pieces.

For each posted video:
- Blog post (SEO-optimised, targets HVAC answering service keywords)
- 3 social captions (text-only posts for LinkedIn/Facebook)
- Email newsletter snippet (feeds into lead nurture sequence)

Also generates standalone written content based on Intelligence findings.  
Queues for Dan approval alongside videos.

### 7. Prospector Agent
**Schedule:** Daily 05:00 UTC  
**Job:** Find HVAC businesses across 25 target US cities.

- Google Places API → searches "HVAC contractor [city]" across all 25 city targets
- Enriches leads: business name, phone, website, review count, rating
- Deduplicates against existing `outbound_leads` table
- Scores leads by size/activity signals
- Adds net-new verified leads daily

### 8. Outreach Agent
**Schedule:** Daily 09:00 UTC  
**Job:** Work Prospector leads through cold email sequences.

- Sends cold email sequences via Brevo
- A/B tests subject lines — declares winner at 50+ sends
- Tracks opens, clicks, replies
- Hot reply detection → immediate Slack alert to Dan
- Never sends from syntharra.com (secondary domain only — existing rule)
- Stores all events to `lead_machine_sequence_log`

### 9. Performance Tracker Agent
**Schedule:** Daily 10:00 UTC  
**Job:** Pull all platform analytics and score every piece of content.

- YouTube Analytics API: views, watch time, CTR, subscriber conversions
- Meta Graph API: Instagram + Facebook reach, engagement, profile visits
- TikTok Analytics: views, completion rate, shares
- Blotato analytics endpoint: cross-platform summary
- Tracks full funnel: video view → website visit → trial signup (via UTM parameters)
- Scores each video: engagement rate, funnel conversion rate, client acquisition contribution
- Feeds performance scores back to Intelligence Agent — closes the learning loop
- Stores to `campaign_results` table

---

## Marketing Brain — Weekly Orchestrator
**Schedule:** Monday 08:00 UTC  
**Job:** Synthesise all agent outputs, generate weekly plan, manage approvals, report results.

**Phase 1 — Review (08:00)**
- Reads last 7 days of `campaign_results`
- Identifies: top 3 performing videos, worst 3, funnel conversion by platform
- Reads Intelligence brief + Competitor brief

**Phase 2 — Plan (08:15)**
- Confirms Video Content Agent's 6 concepts are queued
- Confirms Content Engine Agent's written content is queued
- Confirms Outreach Agent's sequence plan for the week

**Phase 3 — Propose (08:30)**
- Posts to Slack #marketing-team:
  ```
  Week [X] Marketing Plan — ready for review
  
  Last week: [X] videos posted, [X] total views, [X] trial signups
  Best performer: "[hook]" — [X] views, [X] signups
  
  This week's 6 video concepts → [dashboard link]
  
  Reply 'go' to approve all, or review individually in the dashboard.
  Auto-approves in 48h if no response.
  ```

**Phase 4 — Execute (on approval)**
- Triggers Video Production Agent for each approved script
- Triggers Distribution Agent on render completion
- Triggers Content Engine repurposing

**Phase 5 — Report (following Monday 07:45)**
- Weekly performance report to Slack:
  - Videos posted vs approved
  - Total reach across all platforms
  - Website visits attributed to social (UTM)
  - Trial signups attributed to social
  - Best hook/format this week
  - What the team is doing differently next week

---

## Approval Dashboard

**Location:** `syntharra.com/marketing` (password protected)  
**Tech:** Static HTML + Supabase JS client

**Pending tab** — for each queued item:
- Video preview (Higgsfield render)
- Full script
- Reasoning panel: why this will work + supporting data
- Projected reach (based on similar content performance)
- Approve / Reject buttons
- Rejection reason field (logged as learning — team never repeats same mistake)

**Performance tab:**
- Weekly views, signups, clients — all platforms combined
- "Getting smarter" chart: avg performance score week over week
- Top 5 videos of all time by funnel conversion
- Platform breakdown

**Learning tab:**
- What the Intelligence Agent found this week
- What changed vs last week
- Rejection history + what was learned

---

## Data Architecture (Supabase)

| Table | Owned by | Purpose |
|---|---|---|
| `marketing_intelligence` | Intelligence Agent | Daily trending findings |
| `competitor_intelligence` | Competitor Watch | Weekly competitor data |
| `content_queue` | Video Content Agent | Scripts pending approval |
| `content_variants` | A/B system | Hook/script variants + scores |
| `marketing_campaigns` | Distribution Agent | All posted content + platform IDs |
| `campaign_results` | Performance Tracker | All analytics data |
| `outbound_leads` | Prospector | All sourced HVAC leads |
| `lead_machine_sequence_log` | Outreach Agent | Email sequence events |
| `marketing_brain_log` | Brain | Weekly plans + decisions |

---

## Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Video generation | Higgsfield AI Plus | $34/mo |
| Multi-platform distribution | Blotato Starter | $29/mo |
| Voiceover/audio | Higgsfield Cinema Studio 3.0 (built in) | $0 extra |
| Scheduling/crons | Railway (existing) | $0 extra |
| Data storage | Supabase (existing) | $0 extra |
| Cold email | Brevo (existing) | $0 extra |
| Notifications | Slack (existing) | $0 extra |
| **Total new spend** | | **$63/mo** |

---

## Platform Credentials Required

| Platform | Status | What's needed |
|---|---|---|
| YouTube | Credentials vaulted ✅ | OAuth refresh token (one-time auth script) |
| Higgsfield AI | Need account | API key → vault |
| Blotato | Need account | API key → vault |
| Instagram | Pending Meta app | Facebook Business Page + Meta Developer app |
| Facebook | Pending Meta app | Same Meta app as Instagram |
| TikTok | Need account | Business account + API key (draft-only posting) |

---

## Learning Loop

Every rejection Dan makes, every video that flops, every video that goes viral — all of it feeds back into the Intelligence Agent's scoring model. The team gets measurably smarter every week. The dashboard's "Getting smarter" chart makes this visible to Dan.

Concretely:
- Rejected script → logs rejection reason → Video Content Agent avoids that pattern
- Low-performing video → Performance Tracker flags format → Intelligence deprioritises that angle
- High-performing video → Intelligence Agent doubles down on that hook format
- Trial signup attributed to a video → that video's hook/format gets highest priority score

After 8 weeks of live data, the system will know more about what converts HVAC owners on social media than any human marketer who hasn't specifically studied this niche.

---

## Success Criteria

| Week | Target |
|---|---|
| 2 | All platforms live, 3 videos/week posting consistently |
| 4 | 10k+ total views across platforms, Intelligence loop proving value |
| 8 | First trial signup attributed to social content |
| 12 | 3+ trial signups/month from social, system visibly improving week over week |
| 24 | Social content is primary client acquisition channel |
