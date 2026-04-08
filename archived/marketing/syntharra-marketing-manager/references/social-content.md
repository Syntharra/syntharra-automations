# Social Content Calendar

30-day social content plan for Syntharra. TikTok primary, Instagram Reels, LinkedIn.
Parameterised by industry — swap {{industry}} to redeploy.

---

## Platform Strategy

| Platform | Frequency | Format | Goal |
|---|---|---|---|
| TikTok | 4x/week | 30–60 sec vertical video | Reach + virality |
| Instagram Reels | 3x/week | 30–45 sec vertical video | Brand credibility |
| LinkedIn | 2x/week | Text post or short video | B2B decision makers |

---

## Content Pillars (5 Rotating)

1. **DEMO CLIP** — Show a real call being handled by the AI (30 sec highlight)
2. **STAT SHOCK** — A missed call stat that makes business owners uncomfortable
3. **BEFORE/AFTER** — Voicemail vs AI receptionist outcome
4. **OBJECTION KILLER** — Answer the #1 objection in 30 seconds
5. **BEHIND THE SCENES** — How Syntharra onboards a client / sets up the AI

---

## 30-Day Content Calendar

### Week 1 — Launch with the Demo

| Day | Platform | Pillar | Hook / Caption |
|---|---|---|---|
| Mon | TikTok + Reels | DEMO CLIP | "It's 8:47pm Friday. AC breaks. Watch what happens when you have Syntharra." |
| Tue | LinkedIn | STAT SHOCK | "The average HVAC business misses 37% of after-hours calls. That's not a small problem." |
| Wed | TikTok | BEFORE/AFTER | "Without Syntharra: voicemail. With Syntharra: lead captured, tech alerted, job booked." |
| Thu | Reels | DEMO CLIP | "She called at 9pm. No human answered. She still got a tech dispatched in 20 minutes." |
| Fri | TikTok + LinkedIn | OBJECTION KILLER | '"Isn't it expensive?" Here's what one missed $8,000 AC replacement job costs you.' |

### Week 2 — Build Credibility

| Day | Platform | Pillar | Hook / Caption |
|---|---|---|---|
| Mon | TikTok + Reels | STAT SHOCK | "62% of customers won't leave a voicemail. They just call your competitor." |
| Tue | LinkedIn | BEHIND THE SCENES | "How we set up an AI receptionist for an HVAC company in under 5 days." |
| Wed | TikTok | DEMO CLIP | "New customer. $9,200 quote. Booked at 10:30pm. No human involved." |
| Thu | Reels | BEFORE/AFTER | "Old way vs new way. You tell me which business you'd rather own." |
| Fri | TikTok + LinkedIn | OBJECTION KILLER | '"What if the AI says something wrong?" Here's exactly how we handle that.' |

### Week 3 — Objections + Social Proof

| Day | Platform | Pillar | Hook / Caption |
|---|---|---|---|
| Mon | TikTok + Reels | DEMO CLIP | "Emergency call. Elderly woman. 97°F. Watch how the AI handled this." |
| Tue | LinkedIn | STAT SHOCK | "The average missed call costs an HVAC business $340. Miss 3 a week = $53k/year." |
| Wed | TikTok | OBJECTION KILLER | '"I already have an answering service." Here's the difference.' |
| Thu | Reels | BEHIND THE SCENES | "What Syntharra's AI actually does on a call — step by step." |
| Fri | TikTok + LinkedIn | BEFORE/AFTER | "Your voicemail vs our AI. Which one booked the job?" |

### Week 4 — Call To Action Push

| Day | Platform | Pillar | Hook / Caption |
|---|---|---|---|
| Mon | TikTok + Reels | DEMO CLIP | "Quote call. AC replacement. Homeowner ready to spend $11k. See how it went." |
| Tue | LinkedIn | STAT SHOCK | "HVAC companies that answer every call grow 2.4x faster than those that don't." |
| Wed | TikTok | OBJECTION KILLER | '"I don't have time to set it up." Here's how fast this actually takes.' |
| Thu | Reels | BEHIND THE SCENES | "Inside a Syntharra AI receptionist: what the business owner sees after every call." |
| Fri | TikTok + LinkedIn | CTA | "We're taking on 10 new HVAC clients this month. Link in bio to see if you qualify." |

---

## Caption Templates

### TikTok / Reels Caption (max 150 chars)
```
[HOOK — first line stops the scroll]
[2-line context]
[CTA: link in bio / comment DEMO]

#HVAC #HVACBusiness #AIReceptionist #SmallBusiness #Trades #TradesLife
```

### LinkedIn Caption
```
[Bold opening stat or question]

[2-3 sentence story or scenario]

[What Syntharra does about it — 1-2 sentences]

[Soft CTA: "Curious how it works? Drop a comment or DM me."]

#HVAC #TradesBusiness #AIReceptionist #Syntharra #BusinessGrowth
```

---

## Script Templates for Video Content

### Demo Clip Script (30 sec)
```
[0-3s] HOOK TEXT ON SCREEN: "8:47pm. Friday night. AC breaks."
[3-8s] Show incoming call on screen / phone ringing
[8-25s] Play audio highlight of demo call (best 20 seconds)
[25-30s] Show post-call data captured: name, address, issue, tech alerted
TEXT: "Every call. Answered. Every lead. Captured."
CTA: "Link in bio for the full demo."
```

### Stat Shock Script (20 sec)
```
[0-3s] HOOK: "This stat will make HVAC business owners uncomfortable."
[3-10s] Text animation: "37% of after-hours calls go unanswered."
[10-15s] "That's not a staffing problem. That's a technology problem."
[15-20s] "We solved it. Link in bio."
```

### Before/After Script (45 sec)
```
[0-5s] "Before Syntharra:" [Show voicemail playing]
       "You've reached Arctic Breeze HVAC, please leave a message..."
[5-10s] Show caller hanging up. Text: "They called your competitor."
[10-15s] "After Syntharra:"
[15-35s] Play 20-sec highlight from demo call
[35-40s] Text: Lead captured. Appointment booked. Tech alerted.
[40-45s] "Same call. Different outcome. Link in bio."
```

---

## Hashtag Banks

### HVAC
```
#HVAC #HVACTech #HVACLife #HVACContractor #HVACBusiness #AirConditioning
#HeatingAndCooling #HVACRepair #HVACInstallation #TradesLife #TradesBusiness
```

### General / AI
```
#AIReceptionist #SmallBusiness #BusinessAutomation #Syntharra #AIForBusiness
#NeverMissACall #TradeContractor #BusinessGrowth #LeadGeneration
```

### LinkedIn
```
#HVAC #Trades #SmallBusiness #BusinessOwner #AIReceptionist #Syntharra
#CustomerService #BusinessGrowth #Automation #Entrepreneur
```

---

## Automation Options

### Buffer (Easiest)
- Connect TikTok, Instagram, LinkedIn
- Upload video + caption + schedule
- API available for n8n integration

### n8n → Buffer API
```
POST https://api.bufferapp.com/1/updates/create.json
{
  "profile_ids": ["tiktok_id", "instagram_id"],
  "text": "{{caption}}",
  "scheduled_at": "{{post_datetime}}",
  "media": { "video": "{{video_url}}" }
}
```

### Direct TikTok API (Advanced)
TikTok Content Posting API — requires business account verification.
Apply at: developers.tiktok.com

---

## Content Production Notes

- Record demo calls using Retell test interface
- Screen record the call in progress (show waveform + transcript)
- Add Syntharra logo watermark bottom-right (white on dark)
- Captions always on (85% of TikTok watched without sound)
- No stock footage — raw, real, authentic performs better in trades niche
- Hook must be on screen in first 2 seconds or viewer scrolls
