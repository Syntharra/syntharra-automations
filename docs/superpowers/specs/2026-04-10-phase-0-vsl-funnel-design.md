# Phase 0 — VSL Closing Asset, Pilot Funnel, and Measurement Spine

**Date:** 2026-04-10
**Author:** Claude (Sonnet 4.6, acting as Syntharra's marketing systems architect)
**Status:** Design — awaiting Dan's review
**Supersedes:** None (first spec in marketing-team build sequence)
**Part of:** Agentic Marketing Team (phased build — see § 13 for phase map)

---

## 0. TL;DR

Build the single converting destination that every future marketing channel will funnel into — a ~4:30 founder-led Video Sales Letter hosted at `syntharra.com/start`, a no-card 14-day / 200-minute pilot flow that lets HVAC owners put the product in their own hands within 4 minutes, and a unified `marketing_events` log in Supabase that makes every visit, video view, signup, and paid conversion attributable back to the originating asset. Nothing downstream (short-form video, cold email, ads) is built until this exists — because without it, every click dies on impact and nothing is measurable.

**Success gate for Phase 0 → Phase 1:** 50–100 real visits smoke-tested against seven step-level conversion benchmarks (§ 10). If benchmarks hit, green-light Phase 1. If not, iterate the VSL / landing / offer until they do.

---

## 1. Context & Why This Exists First

### 1.1 The problem Phase 0 solves

Syntharra has a working product (`agent_b46aef9fd327ec60c657b7a30a`, live on `+18129944371`) and a working onboarding pipeline (`4Hx7aRdzMl5N0uJP` → Retell clone → `client_agents`), but no mechanism for **cold-traffic acquisition**. The current checkout page (`syntharra-checkout`) serves warm/referred buyers who already know what they want and come directly to the 3-tier comparison. It does not serve a stranger who has never heard of Syntharra and needs to be persuaded from a dead start.

Every future acquisition channel — short-form video (Phase 1), cold email (Phase 2), paid ads (Phase 3+) — will send cold strangers to Syntharra. Those strangers need:

1. **A closing asset** that persuades them in one sitting without a human sales call.
2. **A friction-minimized activation path** so that the 5% who are persuaded actually become users, not just visitors.
3. **A measurement spine** so that every piece of content ever produced can be traced back to conversions — otherwise the self-learning optimizer in Phase 3 has nothing to learn from.

Phase 0 builds all three.

### 1.2 What this spec does NOT cover (explicit non-goals)

- **Short-form video production for TikTok/Reels/Shorts/FB** — Phase 1
- **Cold email infrastructure (ICP sourcing, Instantly.ai, reply handling)** — Phase 2
- **Cross-channel attribution + Optimizer agent** — Phase 3
- **Multi-account farming, UGC agents, niche expansion** — Phase 4
- **Paid ads as a primary channel** — deferred (organic-first strategy)
- **Testimonials/social proof on the landing page** — deferred until first 10 pilots close and generate real content
- **A/B testing infrastructure (GrowthBook etc.)** — Phase 3 (no statistical power at this traffic level)
- **Cold calling support tooling** — explicitly killed from the autonomous system; Dan retains it as manual backup activity outside the agentic team

### 1.3 Dependencies on other work

- **Stripe live-mode activation** — currently P1 on `docs/TASKS.md`. Dan is providing the live secret key. Phase 0 can smoke-test in test mode, but MUST be flipped to live before public traffic hits `syntharra.com/start`.
- **Retell agent `post_call_webhook_url` wired to Call Processor** — already done per STATE.md 2026-04-09.
- **`client_dashboard_info` view** — already exists per STATE.md 2026-04-09, used by the pilot dashboard state.

---

## 2. Locked Decisions (from brainstorming, 2026-04-10)

| # | Decision | Rationale (short) |
|---|---|---|
| D1 | **Offer:** 14-day free pilot, **200 call minutes cap**, no credit card upfront, auto-convert to $697/mo on day 14 if payment method added | Cold HVAC owners are card-skeptical and burned by prior answering-service scams; minutes cap bounds cost risk to ~$28/pilot; product sells itself once the owner hears their AI catch a real call |
| D2 | **VSL format:** Hybrid founder-led — Dan on camera for 0:00–0:25 (hook) and 4:00–4:30 (close), agent-iterable middle 3.5 min of screen-share + real TESTING-agent call recordings + animated text overlays | Real founder + real call recordings = unbeatable trust; middle sections are remixable by agents in Phase 3 without re-filming |
| D3 | **VSL length target:** 4:30 | B2B VSL sweet spot at this ACV; too short can't close $1,694 first-year value on cold traffic, too long loses HVAC owner attention |
| D4 | **Landing page URL:** `syntharra.com/start` (new page in `syntharra-website` repo) + `syntharra.com/ai` 301-redirect to `/start` | Main-domain path = highest trust for skeptical HVAC owners; `/start` implies action; same repo as `dashboard.html` = familiar patterns; does not touch `syntharra-checkout` |
| D5 | **Hook:** Verbatim real quote from r/HVAC — *"I ran out of my own 40th birthday party to get on site."* | Research-validated: owners describe pain as specific events they missed, not dollar figures; dollar-stat hooks are now white noise in the market; owner-verbatim language is unrankable authenticity |
| D6 | **VSL host:** Mux | Best-in-class play-progress events feed directly into `marketing_events`; auto-transcode; ~$1/1,000 plays |
| D7 | **CRM:** HubSpot stays (free tier, clients already imported); Brevo stays for transactional email | Dan decision 2026-04-10 — no good reason to churn now |
| D8 | **Cold calling:** killed from the autonomous machine | Dan retains it as a manual backup activity; not Phase 0/1/2/3 scope |
| D9 | **Attribution:** first-touch AND last-touch both stored; Phase 3 Optimizer decides which model to use per question | Zero cost to store both; re-instrumenting later is painful |
| D10 | **Page framework:** vanilla HTML/CSS/JS, consistent with `dashboard.html` patterns | Fast, no build step, no React dependency, matches existing repo patterns |

---

## 3. Funnel Architecture

### 3.1 End-to-end flow

```
                 ┌───────────────────────────────────────────┐
                 │  Cold traffic (Phase 1 video, Phase 2     │
                 │  email, Dan's DMs, Reddit posts, etc.)    │
                 └──────────────────┬────────────────────────┘
                                    │  link includes ?stx=<asset_id>&utm_*
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  syntharra.com/start  (NEW)               │
                 │  • Mux VSL autoplay muted                 │
                 │  • "START MY FREE PILOT" CTA              │
                 │  • stx tracker: capture, persist, emit    │
                 └──────────────────┬────────────────────────┘
                                    │  events: page_view, vsl_play,
                                    │          vsl_25/50/75/complete,
                                    │          cta_click
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  Jotform "pilot-onboarding" (NEW fork     │
                 │  of 260795139953066, 6 questions ~4 min)  │
                 └──────────────────┬────────────────────────┘
                                    │  webhook → n8n
                                    │  events: jotform_start,
                                    │          jotform_complete
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  n8n 4Hx7aRdzMl5N0uJP (MODIFIED)          │
                 │  ┌─ Is Pilot? ─ yes ─┐                    │
                 │  │                    ▼                   │
                 │  │  skip Stripe payment check             │
                 │  │  set pilot_mode=true                   │
                 │  │  set pilot_ends_at = now() + 14 days   │
                 │  │  set pilot_minutes_allotted = 200      │
                 │  │  ...rest of pipeline unchanged         │
                 │  │  (Retell clone, phone purchase,        │
                 │  │   client_agents row, youre-live email) │
                 │  └────────────────────┘                   │
                 └──────────────────┬────────────────────────┘
                                    │  event: agent_live
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  dashboard.html?a=<id>  (MODIFIED)        │
                 │  Backend reads client_subscriptions       │
                 │  .pilot_mode — if true, renders banner:   │
                 │  • "200 min / 14 days left"               │
                 │  • "Add payment" CTA → Stripe setup intent│
                 └──────────────────┬────────────────────────┘
                                    │  events: dashboard_view,
                                    │          card_added (if added)
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  tools/pilot_lifecycle.py (NEW cron,      │
                 │  runs daily 00:00 UTC on Railway)         │
                 │  • day 3/7/12 → Brevo email trigger       │
                 │  • day 14 → check card, convert or pause  │
                 │  • day 16/30 → win-back emails            │
                 └──────────────────┬────────────────────────┘
                                    │  events: day3_email_sent,
                                    │          day3_email_opened,
                                    │          day3_email_clicked,
                                    │          (same for day 7, 12)
                                    │          pilot_converted OR pilot_expired,
                                    │          pilot_winback_sent
                                    ▼
                 ┌───────────────────────────────────────────┐
                 │  Outcome: paying customer OR expired pilot│
                 │  (both feed Phase 3 learning loop)        │
                 └───────────────────────────────────────────┘
```

### 3.2 Every arrow is an event

Every state transition in the diagram above is a row in `marketing_events` (§ 7). That's the point. Phase 3's Optimizer can then ask questions like *"which of the 847 TikTok videos we posted this month produced paid customers?"* by joining `marketing_events.asset_id` → `marketing_assets` → revenue.

---

## 4. The VSL

### 4.1 Research-validated hook

From the HVAC owner pain-point research conducted 2026-04-10 via PullPush Reddit archive and open HVAC blog sources:

- **Top pain (ranked #1 by frequency and emotional charge):** "I physically can't get to the phone while I'm inside the job, and I know I'm losing work every time it rings" — seen in 12+ distinct posts/comments across r/HVAC, r/hvacadvice, r/smallbusiness
- **Top pain (ranked #2 by emotional charge):** "Being on-call is destroying me. I'm running out of my own life for this job"
- **Top pain (ranked #3):** "The answering service I'm paying for is garbage and it still misses the calls that matter"

**The winning hook** is a verbatim lift from an r/HVAC commenter (username redacted, archived via PullPush):

> **"I ran out of my own 40th birthday party to get on site."**

**Why this hook over alternatives:**

- Every competitor in the HVAC answering-service space leads with *"43% of HVAC companies never return calls"* or *"$287 per missed call."* That framing is now white noise and owners tune it out.
- Research found that **HVAC owners do not describe their pain as a statistic — they describe it as a specific event they missed.** Event-specificity beats stat-citation in 2026 for any cold-traffic B2B.
- Using a real owner's exact words signals *"the people who made this actually talked to me"* in the first 3 seconds. That cuts through the AI-content skepticism that the rest of the platform is drowning in.
- Emotional register: exhaustion bleeding into resignation. **Not anger.** The VSL must match this register throughout — no upsell energy, no hype, no "imagine the revenue." The voice of a competent friend who has been there.

**Supporting verbatim quotes we'll use as pull-quote cards in the middle section:**

> *"I almost missed my kids 8th grade graduation ceremony."*
>
> *"The fucking answering service put a lady through once at 2 am…she wanted to know what the roads were like."*
>
> *"I got sick of always being on call."*
>
> *"I ran out of my own 40th birthday party to get on site."*

### 4.2 Full VSL script (word-for-word, v1 — Dan approves before filming)

**Timing discipline:** hard-cut at each section. No transitions, no fades, no music crescendos. Direct-response VSLs win on relentless forward motion. Music bed under Dan's VO at 20% volume, silence during the call recordings.

---

#### 0:00–0:10 — Quote card (no voiceover, black frame)

**On screen (white serif on pure black, no logo):**

> *"I ran out of my own 40th birthday party to get on site."*
>
> — r/HVAC

**Beat of silence.** Ambient HVAC fan sound only. Hold for 3 seconds after text lands.

Hard cut.

---

#### 0:10–0:25 — Dan on camera, medium shot

**Visual:** Dan, clean background (not an office, not branded — looks like his actual kitchen or a truck interior). Soft natural light from one side. Eye contact with camera.

**Dan says:**

> *"If that's ever been you — or if you can't remember the last weekend your phone didn't buzz past 10 p.m. — you're in the right place. I'm Dan. I built Syntharra for exactly one reason, and in the next four minutes I'm going to show you what it does, what it sounds like, and what it costs. No sales call. Just the thing."*

Hard cut.

---

#### 0:25–1:30 — Pain agitation (screen + voiceover)

**Visual sequence:** rapid cuts between pull-quote cards (the four verbatim quotes from § 4.1) and tight b-roll shots of HVAC physical-work scenes (attic crawlspaces, hands on a condenser, phone buzzing in a toolbag, dark bedroom at 2am with a phone face-down). B-roll is licensed stock from Pexels/Pixabay or Remotion-composited — no AI generation that could trigger uncanny-valley response in this emotionally sensitive opening.

**Dan VO (recorded separately, clean mic):**

> *"You already know the story. Phone rings while you're elbows-deep. You can't pick up. You call back forty minutes later and they already booked with whoever answered first. You've done the math. You've told yourself you need a receptionist. You've looked at the $3,000-a-month part-timer who won't work nights or weekends anyway.*
>
> *You might've even bought an answering service. One of those ones that promised to handle overflow. And now it wakes you at 2 a.m. to ask if the roads are clear — while the actual emergency you needed them to catch went to voicemail.*
>
> *I talked to hundreds of HVAC owners before I built this. I didn't hear anyone complaining about the money. I heard owners running out of their own birthday parties. Missing their kids' graduations. Ignoring calls from their own bosses because they were so tired they couldn't face one more compressor.*
>
> *The problem isn't that you're a bad business owner. The problem is that the job isn't solvable with another human. You'd need three of them. So let me show you what we built instead."*

Hard cut.

---

#### 1:30–2:15 — Mechanism reveal + real call recording

**Visual:** cold open to a waveform visualization on a black screen. White text appears:

> *"An actual call our AI answered at 2:47 a.m."*

**Audio:** unmuted 30–40 second clip of a real Syntharra TESTING-agent call handling a simulated or real HVAC emergency. The call must demonstrate:
- Warm, natural voice (not robotic)
- Correctly routing the caller (gathering name, address, issue, urgency)
- Identifying it as an emergency and escalating
- The caller saying something gratifying at the end ("oh thank god, thank you")

**Production note:** we will record 4–5 candidate calls using the TESTING agent (`agent_41e9758d8dc956843110e29a25`) with Dan or a friend playing the caller from a mobile phone. The most emotionally compelling clip gets used. The agent must be tested to ensure there are no "AI tells" (unnatural pauses, misheard words) in the specific clip we ship.

**Optional lower-third text during the call:** *"[agent caught the emergency, paged Dan, logged the lead]"* updating as the call progresses. Lightweight After Effects-style animation, not heavy.

Hard cut.

---

#### 2:15–2:45 — Differentiator + answering-service contrast

**Visual:** split screen — left side shows the 2am road-conditions quote as a pull card, right side shows the just-played real call transcript (scrolling).

**Dan VO:**

> *"That's the difference. You didn't buy an answering service that bothers you at 2 a.m. about nothing. You bought one that handles the emergency, screens out the junk, and texts you only when it actually matters.*
>
> *It doesn't take lunch breaks. It doesn't quit. It doesn't mishear the address. It works the Sunday of the Super Bowl. And it never — ever — runs out of your own birthday party to get on site."*

Hard cut.

---

#### 2:45–3:30 — How it works (mechanism, no tech jargon)

**Visual:** screen recording of actual onboarding flow — 4-panel animated grid:
1. Jotform appearing (timer starts "00:00")
2. Six questions being filled out (speed-ramped)
3. A phone number activating (counter showing "Live in 3:47")
4. The dashboard appearing with "Agent is live" status

**Dan VO:**

> *"Here's how it works. You go to syntharra.com/start. You answer six questions about your business — your hours, your service area, what counts as an emergency for you, how you want leads sent. It takes four minutes. Then you pick a number, or forward your existing one. And your AI is answering your phone before your coffee's done.*
>
> *That's it. No install. No app. No training a human who'll quit in three months."*

Hard cut.

---

#### 3:30–4:00 — Offer reveal

**Visual:** clean text-forward animated slide stack, each bullet punches in as Dan says it, on brand-dark background:

- **200 call minutes**
- **14 days**
- **No credit card today**
- **Live in 4 minutes**

**Dan VO:**

> *"Here's what I'm going to do. You get 14 days and 200 call minutes to put it through its real life. No credit card up front. I'm not asking you to trust me. I'm asking you to watch it do the job for two weeks, on your phone, on your calls.*
>
> *If at the end of 14 days it hasn't caught at least five calls you would've missed — walk. Keep the data. We're done.*
>
> *And if it does what I know it'll do — you stay live at six ninety-seven a month. Which, by the way, is less than one weekend of overtime pay for a human who'd quit on you anyway."*

Hard cut.

---

#### 4:00–4:30 — Dan on camera outro (same setup as intro)

**Dan says, camera-direct:**

> *"Go to syntharra dot com slash start. Six questions, four minutes, your AI is answering your business line before you finish reading today's work orders. I'll see you inside. Talk soon."*

**Last frame:** holds on Dan's face for 1 beat, then cuts to white-on-black URL card:

> **syntharra.com/start**

Hold 2 seconds. End.

### 4.3 Production plan

**Dan's filming instructions (day 4 of implementation):**

1. **Location:** Dan's kitchen near a large window, OR outside in open shade (overcast day or within 1 hour of sunset). Never direct sunlight (harsh shadows). Background should be real, not a corporate backdrop, not a home office — HVAC owners distrust "office-looking" content.
2. **Framing:** medium shot, camera at eye level, phone or camera in landscape mode, about 4–6 feet back. Do NOT film vertical.
3. **Audio:** record Dan's voice separately using a phone's native voice memo app held 6 inches from his mouth in a small, soft-walled room (a closet full of clothes is a professional-grade sound booth). Sync to video in post. This matters more than the video.
4. **Takes:** film the intro 3 times with slight variations in tone, film the outro 3 times. More is fine — Dan picks his best two later.
5. **Wardrobe:** whatever Dan would actually wear on a workday. No branded polos, no logos. Authenticity > production value at this stage.
6. **Delivery:** Dan uploads raw footage (video + audio files) to a shared folder. Claude handles all post-production.

**Middle section production (days 4–5, Claude does this):**

1. **Audio cleanup:** run Dan's raw audio through Auphonic or Descript's Studio Sound (one click, broadcast-quality output from hand-held phone audio).
2. **Color grading:** CapCut or DaVinci Resolve auto-match with a subtle teal-and-orange lift. Keep it natural — no film-emulation LUTs.
3. **Pull-quote cards:** Remotion templates rendered programmatically. Source: white serif on pure black, 3-second hold, hard cut in/out.
4. **Real call recording capture:** run 4–5 simulated emergency calls through the TESTING agent (`agent_41e9758d8dc956843110e29a25`) using Retell's test call feature OR by calling the testing phone line from a personal cell. Record caller audio + Retell's response via Retell's call recording API. Pick the single most compelling clip. Verify there are no "AI tells" — any mispronunciation, unnatural pause, or canned-sounding phrase and we re-record.
5. **Waveform visualization:** Remotion `<AudioWaveform>` component. White waveform on black background, responsive to the call audio.
6. **Screen recording of onboarding:** record the actual Jotform + n8n → Retell live flow end-to-end at normal speed, then speed-ramp to 3x in post.
7. **Animated offer slide stack:** Remotion template, brand-dark background, 4 bullets punching in on beat with Dan's VO.
8. **Final assembly:** CapCut or DaVinci Resolve timeline, all cuts hard (no fades), music bed at 20% volume under Dan's VO sections only (royalty-free cinematic track from Artlist or Epidemic Sound), silence during call recordings.

**Music bed:** single track, same track throughout, instrumental, builds slightly during pain agitation and offer reveal. The track is subordinate to the voice and the silence — never leading the edit.

**Backup plan if Dan's footage is unusable:** the middle-section production creates a complete VSL on its own. If Dan's footage genuinely can't be saved, we replace the intro/outro Dan-on-camera sections with voiceover-over-static-quote-cards (ElevenLabs voice cloned from Dan's best audio take) and ship. This is the Option B fallback from brainstorming — zero design rework required.

### 4.4 VSL hosting (Mux)

**Why Mux over alternatives:**

- **Mux Data** gives per-viewer play/pause/seek/complete events via webhooks — these feed directly into `marketing_events` (§ 7).
- **Auto-transcode** to adaptive bitrate HLS, so the VSL plays smoothly for HVAC owners on 3G in their trucks.
- **~$1 per 1,000 plays** — at 10,000 visits/month that's $10/mo. Trivial.
- **Embed code** is a single `<mux-player>` custom element, no React, matches the vanilla HTML stack.

**Mux player config:**

- `autoplay muted` (browsers allow muted autoplay; user-initiated unmute required for sound)
- `preload="auto"` so the first frame is ready
- `playback-id` from the Mux asset uploaded once in Phase 0
- `metadata-video-id="vsl-v1"` so Mux Data can group play events
- `stream-type="on-demand"`
- **No skip button for the first 60 seconds** via custom player overlay (direct-response discipline)

**Mux Data → `marketing_events` webhook wiring:** Mux sends a webhook to a new n8n workflow (`vsl-event-ingest`, to be created in Phase 0). That workflow translates Mux events into `marketing_events` inserts via Supabase REST. Event types: `vsl_play`, `vsl_25pct`, `vsl_50pct`, `vsl_75pct`, `vsl_complete`, `vsl_pause`, `vsl_seek`.

### 4.5 Iterability

Sections 0:25–4:00 (everything except Dan's on-camera moments) are fully agent-iterable. Phase 3's Optimizer agent can, without re-filming Dan:

- Swap pull-quote cards for different verbatim quotes
- Replace the real call recording with a different winning candidate
- Rewrite the pain-agitation VO and regenerate with ElevenLabs-cloned Dan voice
- Change the offer copy
- Rearrange section order

This is why the hybrid format is specifically valuable: the trust anchor (Dan's face) is static, but everything else is a Remotion template + asset library that the optimizer can recombine infinitely.

---

## 5. Landing Page (`syntharra.com/start`)

### 5.1 Wireframe (top to bottom)

```
┌────────────────────────────────────────────────────────────┐
│  [Syntharra wordmark, top-left, small, links to /]         │
│                                                              │
│       Your phone stops ruining your life tonight.           │
│                                                              │
│     14-day free pilot. 200 call minutes. No credit card.   │
│              Your AI is live in 4 minutes.                  │
│                                                              │
│   ┌──────────────────────────────────────────────────┐     │
│   │                                                    │     │
│   │              [ MUX VSL PLAYER ]                    │     │
│   │              autoplay muted                        │     │
│   │              prominent unmute CTA                  │     │
│   │                                                    │     │
│   └──────────────────────────────────────────────────┘     │
│                                                              │
│           ┌────────────────────────────────────┐            │
│           │   START MY FREE PILOT  →           │            │
│           │   (large, brand-accent, pulse)     │            │
│           └────────────────────────────────────┘            │
│                                                              │
│          no card · cancel anytime · live in 4 min           │
│                                                              │
├────────────────────── SCROLL FOLD ─────────────────────────┤
│                                                              │
│    Hear your AI handle a real emergency call               │
│    ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│    │ ▶  2:47 AM │  │ ▶  Booking │  │ ▶  Quote   │         │
│    │  emergency │  │  a repair  │  │  request   │         │
│    └────────────┘  └────────────┘  └────────────┘         │
│    (click to play, uses same Mux for audio)                │
│                                                              │
│    What your AI does, every call, every hour               │
│    ☎  Answers in under 2 rings, 24/7, even Christmas        │
│    🚨  Escalates real emergencies to your phone, not noise  │
│    📋  Books, quotes, logs — your dashboard auto-updates    │
│                                                              │
│    [ START MY FREE PILOT  → ]    (second CTA)              │
│                                                              │
│    Frequently asked                                         │
│    — Is this actually AI or a call center? (AI)            │
│    — What happens after the 14 days? ($697/mo, cancel any) │
│    — What if it doesn't catch enough calls? (walk, free)   │
│    — Can I keep my existing number? (yes, call forward)    │
│    — How many calls/month does $697 cover? (700 min)       │
│    — Will my customers know it's AI? (depends on you)      │
│                                                              │
│    [ START MY FREE PILOT  → ]    (third and final CTA)     │
│                                                              │
│    P.S. — Dan's signed note                                │
│    ─────────────────────────────────────                    │
│    I built this because my uncle runs a plumbing shop and  │
│    I watched him run out of Thanksgiving dinner twice in   │
│    one year to go unclog a restaurant drain. He's not      │
│    getting those Thanksgivings back. You don't have to     │
│    lose the next one.                                       │
│                                                              │
│    — Dan, Founder                                           │
│                                                              │
│    [Syntharra wordmark footer, tiny legal links]           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Copy specifics

**H1:** *Your phone stops ruining your life tonight.*

**Subheading:** *14-day free pilot. 200 call minutes. No credit card. Your AI is live in 4 minutes.*

**Primary CTA button text:** *START MY FREE PILOT →*
**Micro-copy below CTA:** *no card · cancel anytime · live in 4 min*

**Section 2 H2:** *Hear your AI handle a real emergency call*

**Three call snippets** — same three recordings produced for the VSL (emergency, booking, quote). Each plays as a standalone audio clip with a waveform, header showing the category, and a caption underneath saying what the AI did.

**What your AI does (3 bullets):**

- *Answers in under 2 rings, 24/7, even Christmas morning*
- *Escalates real emergencies to your phone — not noise, not at 2am for road conditions*
- *Books, quotes, and logs every call — your dashboard is up to date by the time you're in the truck*

**FAQ (6 Q&As, direct-response style, short):**

1. **Is this actually AI or a call center?** *AI. Real humans don't scale and they sleep. This is software, it's Syntharra's agent, and you can hear it in the recordings above.*
2. **What happens after the 14 days?** *If your AI caught enough calls to be worth it, you stay live at $697/mo — same rate forever, cancel any time. If not, you walk and you keep all the data.*
3. **What if it doesn't catch enough calls to be worth it?** *Walk. Keep the call logs, keep the transcripts, we don't chase you. The offer is designed so you have zero downside.*
4. **Can I keep my existing number?** *Yes. You can either forward your existing number to your Syntharra line (no porting required) or we'll give you a new local number in your area code — your choice in the onboarding form.*
5. **How many calls does $697/mo cover?** *700 minutes, which is roughly 350–400 calls depending on length. Most 1–3 truck shops use under 500. If you go over, it's $0.18/extra minute, no surprises.*
6. **Will my customers know it's AI?** *Depends on you. You tell the AI in the onboarding form how to introduce itself. Some owners say "you've reached the auto-assistant for Acme HVAC" up front, some don't. Your call — the AI is scripted however you want.*

**P.S. copy — PLACEHOLDER, REQUIRES DAN'S REAL STORY:**

> [placeholder, not for production]
> *I built this because my uncle runs a plumbing shop and I watched him run out of Thanksgiving dinner twice in one year to go unclog a restaurant drain. He's not getting those Thanksgivings back. You don't have to lose the next one.*
>
> *— Dan, Founder*

**⚠️ BLOCKER FOR SHIP:** The P.S. above is a PLACEHOLDER demonstrating the structure and tone. It must be replaced with Dan's actual origin story before the landing page goes live. Direct-response P.S. sections always outperform generic brand copy, but only if they're true — fabricated founder anecdotes get exposed fast in a small industry and the damage is permanent. Dan needs to either (a) confirm the uncle-plumber story is literally true, or (b) provide the real story (what made him build Syntharra in the first place?) and Claude rewrites the P.S. using the real material.

### 5.3 Technical requirements

**Repo:** `syntharra-website` (existing public GitHub repo, linked to live domain)
**Route:** `/start` (new page — create `start.html` at repo root, add server rewrite so `/start` serves it)
**Redirect:** `/ai` → `/start` (301, via existing hosting config — verify in repo)
**Framework:** vanilla HTML/CSS/JS. No React, no Next, no build step. Consistent with `dashboard.html`.
**Styling:** import the same CSS variables / brand tokens used in `dashboard.html`. Dark-mode default. Mobile-first responsive (320px → 1920px).
**Analytics:** custom tracker only (§ 7.4). No Google Analytics, no Facebook Pixel, no third-party trackers in Phase 0 — they create GDPR/ePrivacy exposure and the owner tracker gives us everything we need.
**Performance target:** Lighthouse score ≥85 mobile, LCP <2.5s, CLS <0.1.
**Accessibility:** WCAG 2.1 AA. Captions on the VSL (Mux auto-generates + Dan reviews). Alt text on all imagery. Keyboard-navigable CTAs. Reduced-motion respected.

### 5.4 CTA behavior

**On click:** the "START MY FREE PILOT" button calls a JS handler that:

1. Emits a `cta_click` event to `marketing_events` via the tracker (§ 7.4).
2. Redirects to `https://form.jotform.com/<PILOT_JOTFORM_ID>?stx=<asset_id>&utm_source=<src>&utm_medium=<med>&utm_campaign=<camp>&utm_content=<ct>&utm_term=<trm>` — passing through the tracking parameters so Jotform can attach them to the submission.
3. The new Jotform is a fork of `260795139953066` (§ 6.1), with hidden fields for the 5 UTM params and `stx_asset_id`.

---

## 6. Pilot Flow Mechanics

### 6.1 Jotform pilot fork

**New form:** clone of `260795139953066` ("HVAC Standard onboarding"), save as `pilot-onboarding` with new ID (TBD during implementation — record in `docs/REFERENCE.md`).

**Changes from the clone:**

1. **Headline copy:** *"Start your free 14-day Syntharra pilot"* instead of the current paid-onboarding copy.
2. **Hero explainer:** *"200 call minutes. 14 days. No credit card. Your AI is answering calls in about 4 minutes."*
3. **Remove any copy** that mentions the $997 activation fee or first-month charge — this is a FREE pilot.
4. **Add 6 hidden fields** for tracking: `stx_asset_id`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`. These are populated from the query string on page load via Jotform's built-in URL parameter mapping.
5. **Keep all existing questions:** business name, owner name, phone number to forward, service area, emergency definitions, lead-send preferences (the `slackIncoming` field added 2026-04-09 stays).
6. **Webhook:** points to the same n8n workflow (`4Hx7aRdzMl5N0uJP`) as the paid onboarding, but includes `pilot_mode: true` in the payload (via a hidden field or query string flag passed through).

**Rationale for fork vs. modify:** forking is cheaper than adding a conditional in the existing form. The paid onboarding continues to serve warm/referred traffic from `syntharra-checkout` untouched. If the pilot fork diverges in a destructive way, we've lost nothing.

### 6.2 `client_subscriptions` schema migration

New columns to add:

```sql
alter table client_subscriptions
  add column pilot_mode boolean not null default false,
  add column pilot_started_at timestamptz,
  add column pilot_ends_at timestamptz,
  add column pilot_minutes_allotted integer not null default 0,
  add column pilot_minutes_used integer not null default 0,
  add column payment_method_added_at timestamptz,
  add column first_touch_asset_id text,
  add column last_touch_asset_id text,
  add column first_touch_utm jsonb,
  add column last_touch_utm jsonb;

create index on client_subscriptions (pilot_mode, pilot_ends_at) where pilot_mode = true;
create index on client_subscriptions (first_touch_asset_id) where first_touch_asset_id is not null;
```

**Note:** `first_touch_asset_id` / `last_touch_asset_id` / `first_touch_utm` / `last_touch_utm` store attribution directly on the subscription row so Phase 3 Optimizer can join revenue → asset without walking the `marketing_events` log. They are populated at `jotform_complete` time from the Jotform hidden fields.

### 6.3 n8n onboarding workflow modifications

**Workflow:** `4Hx7aRdzMl5N0uJP` (HVAC Standard onboarding)

**Modifications (via Railway REST API `PUT /api/v1/workflows/{id}`, per `CLAUDE.md` n8n rule):**

1. **Add `Is Pilot?` IF node** at the top, right after the Jotform webhook trigger. Condition: `{{ $json.body.pilot_mode === true }}`.
2. **Pilot branch (true):**
   - Skip the existing `Lookup Stripe Payment` node (which checks `stripe_payment_data` for a paid record — pilots don't have one).
   - Add a `Set Pilot Defaults` node that writes: `pilot_mode=true`, `pilot_started_at=now()`, `pilot_ends_at=now() + 14 days`, `pilot_minutes_allotted=200`, `pilot_minutes_used=0` into the subscription-creation payload.
   - Continue to the existing `Clone Retell Agent`, `Purchase Telnyx Number`, `Create client_agents Row`, `Send You're Live Email` nodes — unchanged.
3. **Paid branch (false):** unchanged. Existing flow continues.
4. **`Create client_agents Row` node:** add a step that also writes `first_touch_asset_id`, `last_touch_asset_id`, `first_touch_utm` (as jsonb), `last_touch_utm` to `client_subscriptions` from Jotform's hidden fields.
5. **`Send You're Live Email` node:** use a new Brevo template `pilot_welcome` (different from the existing paid `youre_live`) with copy tailored to the pilot experience. Shows the 14-day countdown, 200-min remaining counter, and a CTA to add payment method.

**Backup:** full workflow JSON backed up to `docs/audits/n8n-backups-20260410/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json` BEFORE any modifications. Per CLAUDE.md — **never hard-delete** and always back up before destructive edits.

### 6.4 Stripe setup intent flow

**Approach:** Stripe's native "trial → subscription" pattern with a custom twist: we don't collect the card at signup (that's the whole point of D1). Instead, we collect it via Stripe's **Setup Intent hosted page** any time during the pilot — triggered from the pilot dashboard banner.

**Flow:**

1. **Pilot user clicks "Add payment to stay live" in the dashboard.**
2. Dashboard calls `POST /api/pilot/payment-method-setup` (new Railway Python endpoint — see § 6.6).
3. Backend creates a Stripe `Customer` (if not exists) and a `SetupIntent`, returns the client_secret.
4. Dashboard redirects to a hosted Stripe Setup page using the client_secret.
5. User enters card. On success, Stripe calls our webhook with `setup_intent.succeeded`.
6. Webhook handler:
   - Attaches the PaymentMethod to the Customer as default.
   - Creates a `Subscription` in Stripe with `trial_end = pilot_ends_at` (meaning no charge until pilot expires).
   - Sets `payment_method_added_at = now()` on `client_subscriptions`.
   - Emits `card_added` event to `marketing_events`.
   - Sends Brevo `pilot_card_added_confirmation` email.
7. On day 14 at 00:00 UTC, `pilot_lifecycle.py` cron checks all expiring pilots:
   - **If `payment_method_added_at IS NOT NULL`:** the Stripe subscription auto-activates (trial_end has passed). Cron emits `pilot_converted` event, sends Brevo `pilot_converted` email, flips `pilot_mode = false`.
   - **If `payment_method_added_at IS NULL`:** cron calls Retell API to set a global `pilot_expired=true` variable on the client's agent, which routes all incoming calls to a new `pilot_expired` flow node (graceful message + text-us-to-reactivate). Emits `pilot_expired` event, sends Brevo `pilot_expired` email.

**Stripe test mode vs live mode:** per § 1.3, Dan is migrating Stripe to live mode as a parallel P1 task. Phase 0 implementation uses test mode for all E2E testing. The flip to live mode is a one-line config change (swap secret key, swap webhook endpoint). The flip MUST happen before any public traffic hits `syntharra.com/start`.

### 6.5 Retell graceful pause on pilot expiration

**Goal:** when a pilot expires without a payment method, the AI agent doesn't just vanish — calls to the forwarded number get a polite "temporarily paused, text us to reactivate" response. This preserves the relationship for win-back sequences.

**Mechanism:**

1. **Add a `pilot_expired` node to the HVAC Standard MASTER flow.** This is a new `code` node that runs at the start of the call, checks a global variable `pilot_expired` set per-client-agent via Retell's agent variables API, and if true, routes to an ending node with a pre-recorded message:

   > *"Thanks for calling. This line's currently paused while the owner decides on a service plan. Text the same number with your emergency and they'll get back to you. Thanks."*

2. **The global variable is set per-agent** by `pilot_lifecycle.py` via Retell's agent update API. The exact field and endpoint (likely `PATCH /v2/update-agent/{agent_id}` with `agent_level_dynamic_variables`, but Retell's API surface should be verified at implementation time against current Retell docs). If Retell's dynamic-variable API doesn't persist per-agent, the fallback is to modify the agent's conversation flow at pause time to route every call directly to the `pilot_expired` ending node, and revert on reactivation. Either approach is implementation-level detail — the spec guarantees the capability, not the specific mechanism.
3. **This is a MASTER flow change**, so it must go through `retell-iac/scripts/promote.py`:
   - Edit the flow in the TESTING agent (`agent_41e9758d8dc956843110e29a25`).
   - Run `python retell-iac/scripts/promote.py` to promote TESTING → MASTER.
   - All existing client agent clones do NOT get the update automatically — they are independent clones from pre-pilot-expired MASTER. This is OK for Phase 0 because there are no paying clients yet. For existing pilot clones, we use the per-agent variable API directly without touching their flow.

4. **Reactivation:** if an expired-pilot user comes back and adds a payment method via a win-back email link, `pilot_lifecycle.py` sets `pilot_expired=false`, creates the Stripe subscription, and the agent resumes normal operation on the next call.

### 6.6 `tools/pilot_lifecycle.py` (new Railway cron)

**Pattern:** mirrors `tools/monthly_minutes.py` and `tools/weekly_client_report.py` — standalone Python script, credentials from `syntharra_vault`, runs on Railway cron, logs to stdout.

**Schedule:** daily at 00:00 UTC via Railway cron config.

**Logic:**

```python
# Pseudo-code only — real implementation in the plan stage.
# Treat this section as requirements, not code.

def main():
    pilots = fetch_active_pilots()  # SELECT * FROM client_subscriptions WHERE pilot_mode = true

    for pilot in pilots:
        days_elapsed = (now() - pilot.pilot_started_at).days
        days_until_expiry = (pilot.pilot_ends_at - now()).days

        # Daily events the cron might fire
        if days_elapsed == 3 and not already_sent("pilot_day_3", pilot):
            send_brevo_pilot_day_3(pilot)  # "Here's what your agent did in its first 48 hours"
            emit_event("day3_email_sent", pilot)

        if days_elapsed == 7 and not already_sent("pilot_day_7", pilot):
            send_brevo_pilot_day_7(pilot)  # halfway report, real call stats
            emit_event("day7_email_sent", pilot)

        if days_elapsed == 12 and not already_sent("pilot_day_12", pilot):
            send_brevo_pilot_day_12(pilot)  # "48 hours left, add card to stay live"
            emit_event("day12_email_sent", pilot)

        # Day 14 expiration
        if days_until_expiry <= 0 and pilot.pilot_mode:
            if pilot.payment_method_added_at:
                # Auto-convert via pre-created Stripe subscription (trial_end has now passed)
                mark_converted(pilot)
                send_brevo_pilot_converted(pilot)
                emit_event("pilot_converted", pilot)
            else:
                # Pause the agent, send win-back
                pause_retell_agent(pilot.client_agent_id)  # set pilot_expired=true global var
                mark_expired(pilot)
                send_brevo_pilot_expired(pilot)
                emit_event("pilot_expired", pilot)

        # Win-back cadence for expired pilots
        days_since_expiry = (now() - pilot.pilot_ends_at).days
        if pilot.pilot_mode_status == "expired":
            if days_since_expiry == 2 and not already_sent("winback_day_16", pilot):
                send_brevo_winback(pilot, day=16)
                emit_event("winback_day_16", pilot)
            if days_since_expiry == 16 and not already_sent("winback_day_30", pilot):
                send_brevo_winback(pilot, day=30)
                emit_event("winback_day_30", pilot)

    log_summary()
```

**Idempotency:** each email send checks a `pilot_email_sends` log table (new) so the cron is safe to re-run the same day.

**Credentials from `syntharra_vault`:**

- `service_name='Supabase'`, `key_type='service_role_key'` — for reading/writing `client_subscriptions` and `marketing_events`
- `service_name='Brevo'`, `key_type='api_key'` — for sending templated emails
- `service_name='Stripe'`, `key_type='secret_key_live'` (or `secret_key_test` during smoke test) — for creating/activating subscriptions
- `service_name='Retell AI'`, `key_type='api_key'` — for setting agent variables on pilot expiry

### 6.7 Brevo email templates (new)

All templates use Syntharra-branded HTML shared base (from `shared/email-templates/`). Copy is short, direct, no marketing fluff.

| Template key | Trigger | Subject line | Primary CTA |
|---|---|---|---|
| `pilot_welcome` | Jotform submit → agent live | *Your AI is live. Here's what it's already doing.* | View dashboard → |
| `pilot_day_3` | Cron day 3 | *[FirstName], your agent handled {n} calls yesterday* | See the transcripts → |
| `pilot_day_7` | Cron day 7 | *Halfway through your pilot — {n} calls caught* | Add payment, stay live → |
| `pilot_day_12` | Cron day 12 | *48 hours left. Your agent has caught {n} calls.* | Keep it live ($697/mo) → |
| `pilot_converted` | Day 14, card on file | *You're live. Welcome to Syntharra.* | View dashboard → |
| `pilot_card_added_confirmation` | Setup Intent success | *Got it. Your pilot keeps running.* | (no CTA) |
| `pilot_expired` | Day 14, no card | *Your pilot ended. Your call data is saved.* | Reactivate ($697/mo) → |
| `pilot_winback_day_16` | Day 16 post-expiry | *{n} calls came into your old line yesterday. Want them back?* | Reactivate → |
| `pilot_winback_day_30` | Day 30 post-expiry | *Last one from me: here's what you missed.* | Reactivate → |

Each template pulls real data from the client's own pilot (call count, lead count, specific emergencies caught). **No generic marketing copy.** The emails are data-driven status updates that happen to include an upsell.

---

## 7. Measurement Spine (`marketing_events` + tracking convention)

### 7.1 `marketing_events` table schema

```sql
create table marketing_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  -- Identity
  session_id text not null,               -- random UUID per browser session
  visitor_id text,                        -- persistent cookie UUID, survives sessions
  client_agent_id text,                   -- set on jotform_complete, links to client_agents.id

  -- Event
  event_type text not null,               -- enumerated below
  asset_id text,                          -- stx_asset_id from originating content (links to marketing_assets.id)

  -- Attribution
  utm_source text,
  utm_medium text,
  utm_campaign text,
  utm_content text,
  utm_term text,
  referrer text,

  -- Context
  user_agent text,
  ip_country text,                        -- derived via Cloudflare/equivalent header
  ip_region text,                         -- US state if country=US
  metadata jsonb                          -- catchall for event-specific data
);

create index on marketing_events (visitor_id, created_at desc);
create index on marketing_events (asset_id, event_type);
create index on marketing_events (client_agent_id);
create index on marketing_events (event_type, created_at desc);

-- RLS: service_role only (no anon reads, ever)
alter table marketing_events enable row level security;
create policy "service_role_full_access" on marketing_events
  for all using (auth.role() = 'service_role');
```

### 7.2 Enumerated event types (Phase 0 set)

```
Acquisition:
  page_view              - any page load on syntharra.com/start
  vsl_impression         - VSL player element rendered (not yet played)
  vsl_play               - user initiated playback
  vsl_25pct              - watched through 25%
  vsl_50pct              - watched through 50%
  vsl_75pct              - watched through 75%
  vsl_complete           - watched to end
  vsl_pause              - paused
  vsl_seek               - scrubbed
  cta_click              - clicked "Start my free pilot"
  call_snippet_play      - clicked one of the 3 below-fold call recordings
  faq_expand             - expanded an FAQ item

Activation:
  jotform_start          - Jotform first field focused
  jotform_complete       - Jotform submitted (webhook fires)
  agent_live             - Retell agent clone succeeded, client_agents row exists
  dashboard_first_view   - user loaded ?a=<id> first time (pilot state derived from client_subscriptions.pilot_mode, not URL param)

Engagement (during pilot):
  dashboard_view         - subsequent dashboard views
  pilot_minutes_10pct    - pilot used 20 minutes
  pilot_minutes_50pct    - pilot used 100 minutes
  pilot_minutes_90pct    - pilot used 180 minutes
  card_add_click         - clicked "Add payment" button
  card_added             - Stripe setup intent succeeded

Conversion:
  pilot_converted        - day 14 with card → subscription active
  pilot_expired          - day 14 without card → agent paused

Email engagement:
  pilot_welcome_sent / _opened / _clicked
  pilot_day_3_sent / _opened / _clicked
  pilot_day_7_sent / _opened / _clicked
  pilot_day_12_sent / _opened / _clicked
  pilot_converted_sent / _opened / _clicked
  pilot_expired_sent / _opened / _clicked
  winback_day_16_sent / _opened / _clicked
  winback_day_30_sent / _opened / _clicked

Re-engagement:
  reactivation_click     - clicked reactivate CTA from a win-back email
  pilot_reactivated      - expired pilot converted via reactivation
```

### 7.3 `marketing_assets` table schema

Every piece of marketing content that can source traffic gets a row in this table. When Phase 1 (video) and Phase 2 (email) spin up, their outputs are registered here on creation.

```sql
create table marketing_assets (
  id text primary key,                    -- short UUID, also used as stx_asset_id
  created_at timestamptz not null default now(),
  asset_type text not null,               -- 'vsl', 'short_video', 'email_sequence',
                                          --  'email_variant', 'landing_page',
                                          --  'dm_template', 'cold_call_script'
  title text not null,                    -- human-readable
  channel text,                           -- 'tiktok', 'instagram_reels', 'youtube_shorts',
                                          --  'facebook_reels', 'cold_email', 'direct', 'organic_post'
  platform_asset_url text,                -- link to the content on its native platform
  variant_of text references marketing_assets(id),  -- parent if remixed
  metadata jsonb,                         -- hook text, script, production notes, etc.
  retired_at timestamptz                  -- set when killed by optimizer in Phase 3
);

create index on marketing_assets (asset_type, channel);
create index on marketing_assets (created_at desc);

alter table marketing_assets enable row level security;
create policy "service_role_full_access" on marketing_assets
  for all using (auth.role() = 'service_role');
```

**Phase 0 starts this table with 2 rows:**

1. The VSL itself (`asset_type='vsl'`, `title='VSL v1'`)
2. The landing page (`asset_type='landing_page'`, `title='start-v1'`)

Every subsequent content production in Phase 1+ adds rows here before the content goes live.

### 7.4 Client-side tracker (`assets/marketing-tracker.js`)

New file in `syntharra-website` repo. Pure vanilla JS, no dependencies.

**Responsibilities:**

1. On page load:
   - Read `visitor_id` from localStorage. If absent, generate a UUID and store.
   - Generate a fresh `session_id` UUID.
   - Read `?stx` query parameter. If present, persist to localStorage + cookie (survives future sessions — this is the first-touch asset).
   - Read `?utm_*` query parameters. Store current session attribution. Also store first-ever UTM set as `first_touch_utm` in localStorage if not already set.
   - Emit `page_view` event.
2. Wire the Mux player events to emit `vsl_*` events.
3. Wire the CTA button click to emit `cta_click` BEFORE the redirect.
4. Wire the below-fold call recording clicks to emit `call_snippet_play`.
5. Wire FAQ expand to emit `faq_expand`.
6. On the Jotform CTA click, append all persisted attribution params (`stx_asset_id`, all UTM params) to the redirect URL so Jotform captures them in hidden fields.

**Event emitter:** POST to a new Supabase Edge Function `marketing-event-ingest` that validates and inserts into `marketing_events`. Edge Function is preferred over direct REST + anon key because it lets us keep service_role key server-side AND gives us a bot-filter opportunity (basic UA and rate-limit check).

**Bot filtering:** the Edge Function drops events from obvious bots (User-Agent contains `bot`/`crawler`/`spider`) and rate-limits to 100 events/min/visitor_id. Dropped events are NOT returned as errors to the client — they silent-fail so scrapers don't learn the rules.

### 7.5 Attribution model

**Two columns on `client_subscriptions`:**

- `first_touch_asset_id` — populated from the Jotform hidden field on `jotform_complete`, sourced from the tracker's localStorage (which persists the `stx` from the very first visit).
- `last_touch_asset_id` — populated from the same Jotform submission, sourced from the tracker's sessionStorage (which holds the `stx` from the current session only).

**Same for UTM:** `first_touch_utm jsonb`, `last_touch_utm jsonb`.

**Why both:**

- First-touch answers: *"Which piece of content originally introduced this customer to Syntharra?"* — used for credit assignment to top-of-funnel content.
- Last-touch answers: *"Which piece of content closed them?"* — used for credit assignment to retargeting / middle-funnel content.
- Phase 3 Optimizer uses multi-touch by walking `marketing_events` by `visitor_id` over time, but the denormalized first/last columns are the fast path for common questions.

### 7.6 What Phase 0 does NOT build

- **Multi-touch attribution UI / dashboard** — Phase 3
- **Real-time event streaming to a BI tool** — not needed
- **Cross-device identity resolution** — out of scope; accept that mobile→desktop crossover will under-attribute
- **Fingerprinting or non-cookie tracking** — ethically out, legally risky

---

## 8. Implementation Sequence (7-day plan, summary only)

Full day-by-day implementation plan lives in the next document (the writing-plans skill output). Summary for spec reviewers:

| Day | Work | Deliverable |
|---|---|---|
| 1 | DB migrations (`marketing_events`, `marketing_assets`, `client_subscriptions` columns). Landing page HTML shell. Mux account setup + VSL placeholder upload. Tracker JS + Edge Function skeleton. | Tables live, page at `/start` returns 200, tracker fires `page_view` |
| 2 | Jotform pilot fork created + webhook wired. n8n `Is Pilot?` branch added to `4Hx7aRdzMl5N0uJP` (full JSON backup taken first). `Set Pilot Defaults` node added. Brevo `pilot_welcome` template draft. | End-to-end: Jotform submit → pilot mode client_agents row created with `pilot_ends_at` set correctly |
| 3 | `tools/pilot_lifecycle.py` script (~300 lines). Railway cron schedule set. Brevo templates for day 3/7/12/expired/converted drafted. Stripe Setup Intent flow (backend endpoint + webhook handler). `pilot_email_sends` idempotency table. | Cron can run locally against test data, hits Brevo, hits Stripe test mode. All state transitions work. |
| 4 | Retell `pilot_expired` flow node added to TESTING agent. Promoted to MASTER via `retell-iac/scripts/promote.py`. Per-agent variable API wiring in `pilot_lifecycle.py`. **Dan films** 30s intro + 30s outro using phone-in-closet audio + window light. | MASTER has pilot_expired pathway. Dan's raw footage uploaded. |
| 5 | VSL middle section production: quote cards, real call recordings captured from TESTING agent, waveform visualizations, onboarding screen recording, offer slide stack, final assembly in DaVinci/CapCut. Upload final cut to Mux. Update Mux playback ID on landing page. | VSL v1 live on Mux, embedded, autoplay working. |
| 6 | Landing page copy finalized (H1, subhead, bullets, FAQ, P.S. — replace placeholder with Dan's real origin story). Below-fold call snippet audio embedded. E2E test: fake pilot from `/start` → Jotform → agent live → dashboard → card add (test mode) → auto-convert. **Compressed-time methodology:** set `pilot_ends_at = now() + 10 minutes` on the test pilot row and set Stripe subscription `trial_end` to match; run `pilot_lifecycle.py` manually at T+11 minutes and assert convert path fires. For the expired-pilot path, repeat with no card. Do NOT use Stripe Test Clocks for Phase 0 — real-time compressed testing is simpler and catches cron bugs that time-travel would miss. All events must land in `marketing_events` with correct timestamps. Fix any breakages. | E2E pipeline green. |
| 7 | **Smoke test:** drive 50–100 real visits to `/start` from any source (Dan's network, $50 Meta ad, Reddit post, DMs). Measure against § 10 benchmarks. Fix or green-light Phase 1. | Go/no-go decision for Phase 1. |

**Runs in parallel days 1–6:** Dan migrates Stripe to live mode. Must be live before day 7 traffic.

**Critical-path blockers:**

- Day 4 depends on Dan filming (if he can't, we fall back to Option B voiceover-only, described in § 4.3).
- Day 6 depends on Stripe test mode being functional for the E2E test.
- Day 7 depends on Stripe live mode being ready before traffic.

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Dan's filmed footage is unusable** (bad audio, lighting, delivery) | Medium | High | Option B fallback baked in (§ 4.3): faceless VSL using ElevenLabs voice + static quote cards. Zero design rework. Adds 1 day to the plan. |
| **Stripe live mode not ready by day 7** | Medium | High (blocks public traffic) | Smoke test in test mode with Dan's network only (no public ad spend until live). Flip to live within 24h of Dan delivering the key. |
| **Onboarding pipeline breaks for pilot branch** (n8n workflow bug) | Medium | P0 (no agent goes live = funnel dead) | Full backup of `4Hx7aRdzMl5N0uJP` taken before edits. E2E test on day 6 catches this before any real visitor hits it. Rollback = restore from backup. |
| **Retell graceful pause doesn't work** (expired pilots keep accepting calls) | Low | Medium (unexpected Retell charges, angry customers) | Test the pause pathway in the day-6 E2E test with a compressed-time pilot. Set an alert in `pilot_lifecycle.py`: if any `pilot_expired` row has calls >0 in Retell after expiry, Slack `#ops-alerts`. |
| **Mux webhook events don't reach `marketing_events`** (wiring bug) | Medium | Medium (Phase 3 optimizer loses half the signal) | E2E test day 6 specifically asserts: page_view → vsl_play → vsl_complete all landed in `marketing_events`. If any missing, halt day 7. |
| **VSL underperforms benchmarks** (smoke test fails) | Medium | Medium (delays Phase 1, not a disaster) | Iterate the VSL script/copy/offer. The whole point of the smoke-test gate is to catch this BEFORE pouring Phase 1 content into a broken destination. Each iteration cycle is 1–2 days. |
| **Cold traffic sees "AI" at any step and bounces** | Low | Medium | Research-validated hook leads with owner verbatim, not AI framing. Real call recordings are the differentiator. We disclose AI honestly in FAQ but don't lead with it. |
| **HVAC owner enters card, gets charged in test mode somehow** | Low | High (refund drama, reputation damage) | Strict discipline: test mode only uses test cards (`4242...`). Dan NEVER runs a real card against test mode. Live mode secret key is only loaded on day 7 and after. |
| **Dashboard pilot banner breaks existing paid-customer dashboard view** | Low | Medium | Pilot banner renders only if `client_subscriptions.pilot_mode = true` for the given agent. Existing paid-customer dashboard view is untouched (`pilot_mode = false` = no banner, identical rendering). Single-source-of-truth prevents drift between URL state and DB state. |
| **Pilot users abuse free minutes with outbound spam** | Very Low | Low | 200-min cap hard-enforced. No outbound calling enabled by default in Retell agents. Dashboard doesn't expose outbound dial. |
| **Spec makes claims about research that don't hold up** | Low | Medium | Research is cited inline with source URLs in § 4.1. Dan or any reviewer can verify the PullPush URLs. |

---

## 10. Success Criteria (Phase 0 "done" gate)

### 10.1 Ship criteria (internal "done")

Phase 0 is complete — code-wise — when all 7 days of § 8 are done and the E2E test passes cleanly:

- [ ] All 3 DB schemas applied to Supabase prod (`marketing_events`, `marketing_assets`, `client_subscriptions` pilot columns)
- [ ] `syntharra.com/start` returns 200, VSL plays, tracker fires events that land in `marketing_events`
- [ ] Pilot Jotform fork is live and webhook-wired
- [ ] n8n `4Hx7aRdzMl5N0uJP` has `Is Pilot?` branch, full backup of pre-modification JSON saved to `docs/audits/n8n-backups-20260410/`
- [ ] `tools/pilot_lifecycle.py` runs green locally against a compressed-time test pilot
- [ ] Stripe Setup Intent hosted flow works end-to-end (test mode)
- [ ] Retell `pilot_expired` node is in MASTER (via promote.py), tested
- [ ] All 9 Brevo templates drafted and send successfully
- [ ] E2E compressed-time test: `/start` visit → VSL play → CTA click → Jotform submit → agent live → dashboard pilot view → card add → day-14 convert. All events logged.
- [ ] Stripe live mode active (Dan's deliverable — blocks only day 7 traffic, not days 1–6)

### 10.2 Phase 0 → Phase 1 gate (smoke test benchmarks)

**Traffic source:** any combination of Dan's personal network, Reddit posts in r/hvacbiz, small Meta test ad (<$100), LinkedIn DMs, existing mailing list, cold-outreach personal messages. Goal: 50–100 unique visits.

**Measurement:** query `marketing_events` after 72 hours of smoke-test traffic has landed.

| Step | Benchmark | Fails if below | Action if failed |
|---|---|---|---|
| Visit → VSL play (non-bounce) | ≥60% | <40% | Page load issue, autoplay blocked, player broken — debug |
| VSL play → 60% watched (vsl_50pct) | ≥35% | <20% | Script/pacing broken at the pain-agitation section — re-cut middle |
| VSL 60% → CTA click | ≥25% | <15% | Offer or CTA broken — rewrite offer language, test button copy |
| CTA click → Jotform start | ≥80% | <60% | Redirect bug or Jotform load issue — debug |
| Jotform start → Jotform complete | ≥50% | <30% | Form too long or asking wrong things — trim fields |
| Jotform complete → agent live | ≥95% | <90% | Onboarding pipeline broken — **P0, halt everything** |
| **Overall: visits → pilots started** | **≥3%** | **<2%** | **Iterate VSL / landing / offer before Phase 1** |

**Decision matrix:**

- **All benchmarks hit:** green-light Phase 1 immediately. Start building the organic video machine.
- **One benchmark ≥30% below target:** fix that specific step, re-run 50 visits, re-measure.
- **Two or more benchmarks below target:** the offer is wrong, not the execution. Go back to brainstorming with new assumptions.
- **Overall rate <2%:** do NOT advance to Phase 1. More traffic into a broken funnel wastes Phase 1 investment. Iterate until rate ≥3%.

### 10.3 What Phase 0 explicitly does NOT promise

- It does not promise a paying customer. A paying customer is a **Phase 1 traffic + Phase 0 conversion** outcome. Phase 0 alone guarantees only that when traffic arrives, the funnel works.
- It does not promise the VSL is optimal. v1 is a hypothesis. v2+ comes from Phase 3 Optimizer based on real data.
- It does not promise the pilot → paid conversion rate. That data only exists after 10+ pilots complete their 14 days, which is ~3 weeks after first traffic.

---

## 11. Invariants & Constraints (do not violate)

From `CLAUDE.md`, `docs/RULES.md`, and architecture invariants:

1. **Never test on live Retell agents.** All pilot_expired flow changes go through TESTING → `retell-iac/scripts/promote.py` → MASTER.
2. **IDs come from `docs/REFERENCE.md` only.** This spec lists IDs for context; the implementation plan must fetch them from REFERENCE.md at build time.
3. **n8n = Railway REST API only.** No `mcp__claude_ai_n8n__*` tools. No DELETE on workflows — backup + deactivate + rename + archive UI toggle.
4. **Credentials from `syntharra_vault`.** Never inline. Never commit to repo. Never put in `.env` files committed to git.
5. **Per-client data in Supabase, not the repo.** Pilot config rows live in `client_subscriptions`, never in JSON files in the repo.
6. **Every failure gets a FAILURES.md row** if it implies a standing rule — any Phase 0 implementation failure must be logged per session protocol.
7. **Session protocol:** every session ends with `python tools/session_end.py --topic <slug> --summary "<one-line>"`.
8. **Every new table gets RLS enabled** with service_role-only write policies (both new tables in this spec comply).
9. **No LLM calls to `api.anthropic.com`** — Dan pays for Claude Code subscription, the agentic team uses `claude -p` CLI only. (This matters for Phase 1+ video production pipeline, not Phase 0 directly, but noting it as a standing constraint.)
10. **TESTING → MASTER promotion discipline** — any flow change must be validated in TESTING first. No hot-patching MASTER.

---

## 12. Dependencies on Dan

Dan's hands-on input for Phase 0:

1. **Film 60 seconds of footage** (30s intro + 30s outro) on day 4. Filming instructions in § 4.3.
2. **Approve the VSL v1 script** (§ 4.2) before Dan films. Any copy changes go in before production.
3. **Verify the P.S. anecdote is true** (§ 5.2). If the family plumber story isn't accurate, tell Claude and we rewrite it to reflect Dan's actual motivation. It MUST be true — fabricated origin stories get exposed.
4. **Provide Stripe live-mode secret key** and webhook signing secret to `syntharra_vault` by day 6. This is already a P1 Dan deliverable per `docs/TASKS.md`.
5. **Approve the VSL final cut** on day 6 before the smoke test runs. 20-minute review. Dan has veto on the hook, the offer language, and the Dan-on-camera sections.
6. **Promote the MASTER agent update** on day 4 after the `pilot_expired` flow node is added. This is via `retell-iac/scripts/promote.py` as normal.
7. **Share the smoke test URL** with 50–100 people in his network on day 7. Anyone will do — the goal is 50 real human visits to measure baseline conversion, not a qualified-lead test.

Nothing else is required of Dan during implementation. Everything else is Claude-and-tools.

---

## 13. Phase Map (for context — not in scope for this spec)

| Phase | What it builds | When it starts | Spec owner |
|---|---|---|---|
| **0 — this spec** | VSL + landing + pilot flow + measurement spine | Now | Claude |
| 1 | Organic short-form video machine (research → scriptwriter → AI production → publisher → analyst → optimizer for TikTok/Reels/Shorts/FB) | After Phase 0 smoke test passes | Claude |
| 2 | Cold email machine (ICP sourcing → Instantly.ai infra → copywriter → reply handler → sequence optimizer) | Parallel with late Phase 1 | Claude |
| 3 | Cross-channel learning brain (attribution, meta-optimizer, experiment runner, weekly reports) | After Phases 1 & 2 ship | Claude |
| 4 | Scale (multi-account farming, UGC persona agents, niche expansion) | After Phase 1/2 hit CAC targets | Claude |

Each future phase is its own spec → plan → implementation cycle. Phase 0 is the only foundation required for any of them to work.

---

## 14. Open questions for Dan (review gate)

Flagging things Dan might want to push back on before writing the implementation plan:

1. **Is the family-plumber P.S. anecdote true?** (§ 5.2 / § 12.3) — If not, tell me the real story so I can rewrite.
2. **Does the hook resonate or feel too dark?** — Research says it should land, but Dan knows his own tolerance for direct-response emotional intensity. Soften if genuinely off.
3. **Is "Dan" the name you want on camera and in the P.S.?** — Or a different first name? Or "Syntharra Team"? (Strong rec: first name. Founder-led beats team-led for cold-traffic B2B every time.)
4. **Is the "no sales call, just the thing" framing in the 0:10–0:25 section good?** — It explicitly pre-handles the "when's the demo call?" objection. Dan can veto if he prefers leaving the door open.
5. **Is $697/mo the right number to say out loud in the VSL?** — Alternative: *"less than a weekend of overtime pay"* without the dollar number. I recommend saying it explicitly because obfuscating price backfires with skeptical HVAC owners, but Dan gets the call.
6. **Are there any existing n8n workflows touching `client_subscriptions`** that this schema migration would break? — I'll scan before applying, but Dan's knowledge of the workflow graph is authoritative.
7. **Is it OK to add `marketing_events` and `marketing_assets` to the main Supabase project** or does Dan want them in a separate schema for isolation? — Recommending main project with RLS + service-role-only policies. Phase 3 will need to join them with `client_agents` anyway.

**If Dan has no objections to any of the above, reply "go" and I hand off to the writing-plans skill to turn this spec into a day-by-day executable plan.** Otherwise, flag the section numbers and I revise in place before committing the implementation plan.

---

*End of spec.*
