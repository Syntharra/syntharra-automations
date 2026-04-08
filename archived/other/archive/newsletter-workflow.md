# Weekly Newsletter Automation — n8n Workflow

## Workflow Name: `Weekly Newsletter`

## Trigger
- **Cron node**: Every Monday at 9:00 AM UTC
- Expression: `0 9 * * 1`

## Node Flow

### 1. Cron Trigger
Fires every Monday at 9:00 AM.

### 2. Get Subscribers (Supabase)
- Table: `website_leads`
- Filter: `source=eq.blog_subscribe` AND `unsubscribed=eq.false`
- Select: `email`
- Returns list of active subscribers

### 3. Generate Content (Claude API / Code Node)
JavaScript code node that builds the email content. The content rotates through blog articles and generates fresh tips.

```javascript
// Blog article pool — rotate 2 per week
const articles = [
  { tag: "HVAC", title: "How HVAC companies lose $80,000 a year to missed calls", summary: "35% of HVAC calls go unanswered. At $380 per job, the math is brutal.", url: "https://syntharra.com/blog/hvac-missed-calls.html" },
  { tag: "AI", title: "The real ROI of an AI receptionist for trade businesses", summary: "Calculate exactly how much revenue your trade business loses to missed calls.", url: "https://syntharra.com/blog/ai-receptionist-roi-calculator.html" },
  { tag: "Growth", title: "Why after-hours calls are your biggest untapped revenue stream", summary: "42% of service calls come outside business hours. Your biggest growth lever.", url: "https://syntharra.com/blog/after-hours-calls-trade-business.html" },
  { tag: "HVAC", title: "How to handle HVAC emergency calls without burning out your team", summary: "HVAC emergencies spike during extreme weather. Here is how top contractors handle it.", url: "https://syntharra.com/blog/hvac-emergency-call-handling.html" },
  { tag: "Plumbing", title: "Plumbing lead capture: speed to answer beats everything", summary: "The first plumber to answer books the job 78% of the time.", url: "https://syntharra.com/blog/plumbing-lead-capture.html" },
  { tag: "Electrical", title: "How smart scheduling doubles an electrical contractor's capacity", summary: "Electrical contractors waste 15-20% of capacity on scheduling inefficiency.", url: "https://syntharra.com/blog/electrical-contractor-scheduling.html" },
  { tag: "Growth", title: "Customer experience is the new competitive moat for trades", summary: "Trade businesses investing in CX see 2-3x more referrals.", url: "https://syntharra.com/blog/trade-business-customer-experience.html" },
  { tag: "AI", title: "AI receptionist vs hiring: the honest comparison", summary: "Cost, availability, quality, and scalability — the full breakdown.", url: "https://syntharra.com/blog/ai-vs-hiring-receptionist.html" },
  { tag: "Marketing", title: "Your Google Business Profile is costing you leads", summary: "Fix these 7 common mistakes to rank higher and convert more.", url: "https://syntharra.com/blog/google-business-profile-trades.html" },
  { tag: "Business", title: "What missed calls actually cost your contracting business", summary: "Every missed call costs more than the lost job. Here is the full picture.", url: "https://syntharra.com/blog/cost-of-missed-calls-contractors.html" },
];

// Tips pool
const tips = [
  "<strong>Reply to every Google review</strong> this week — positive and negative. Takes 2 minutes each, signals to Google you are active.",
  "<strong>Check your after-hours voicemail.</strong> If more than 3 callers hung up without leaving a message, you are losing leads.",
  "<strong>Ask your last 3 happy customers</strong> for a review. Send a text with a direct link. Most will do it if you make it easy.",
  "<strong>Update your Google Business Profile</strong> hours and service area. Customers filter by 'open now.'",
  "<strong>Pull your call logs</strong> for the last 30 days. Count how many went to voicemail. Multiply by your average job value.",
  "<strong>Set a callback reminder</strong> for every missed call within 15 minutes. Speed wins.",
  "<strong>Post one photo</strong> of a completed job on your Google Business Profile this week. Real beats stock every time.",
  "<strong>Text your last 5 customers</strong> a direct Google review link. Keep it simple: 'Hey, would you mind leaving us a quick review?'",
  "<strong>Check if your website</strong> shows your phone number above the fold on mobile. If not, fix it today.",
  "<strong>Time yourself</strong> answering your next 5 calls. If average is over 15 seconds, you are losing leads to faster competitors.",
];

// CTAs pool
const ctas = [
  { title: "Losing calls = losing money", subtitle: "Find out exactly how much in 30 seconds", button: "Calculate my lost revenue", url: "https://syntharra.com/calculator.html" },
  { title: "How AI-ready is your business?", subtitle: "Take the 30-second quiz", button: "Get my score", url: "https://syntharra.com/ai-readiness.html" },
  { title: "Which plan fits your business?", subtitle: "Answer 4 quick questions", button: "Find my plan", url: "https://syntharra.com/plan-quiz.html" },
  { title: "Hear the AI for yourself", subtitle: "Talk to a live Syntharra receptionist", button: "Try the demo", url: "https://syntharra.com/demo.html" },
];

// Calculate issue number based on weeks since launch
const launchDate = new Date('2026-03-30');
const now = new Date();
const weekNum = Math.floor((now - launchDate) / (7 * 24 * 60 * 60 * 1000)) + 1;

// Pick 2 articles (rotate based on week number)
const a1 = articles[(weekNum * 2) % articles.length];
const a2 = articles[(weekNum * 2 + 1) % articles.length];

// Pick 3 tips
const t1 = tips[(weekNum * 3) % tips.length];
const t2 = tips[(weekNum * 3 + 1) % tips.length];
const t3 = tips[(weekNum * 3 + 2) % tips.length];

// Pick CTA
const cta = ctas[weekNum % ctas.length];

// Format date
const dateStr = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });

return [{
  json: {
    issue_label: `Weekly Digest · Issue #${weekNum} · ${dateStr}`,
    article1_tag: a1.tag,
    article1_title: a1.title,
    article1_summary: a1.summary,
    article1_url: a1.url,
    article2_tag: a2.tag,
    article2_title: a2.title,
    article2_summary: a2.summary,
    article2_url: a2.url,
    tip1: t1,
    tip2: t2,
    tip3: t3,
    cta_title: cta.title,
    cta_subtitle: cta.subtitle,
    cta_button: cta.button,
    cta_url: cta.url,
  }
}];
```

### 4. Split In Batches
- Batch size: 10
- Iterates over subscriber list

### 5. Send Email (SMTP2GO)
- From: `Syntharra <noreply@syntharra.com>`
- Subject: `{{ $('Generate Content').item.json.article1_title }} + more`
- HTML Body: newsletter-weekly.html template with expressions filled
- To: `{{ $json.email }}`
- Reply-To: `support@syntharra.com`

### 6. Wait
- 1 second between batches (rate limiting)

## Setup Steps in n8n

1. Create new workflow named "Weekly Newsletter"
2. Add Cron trigger: `0 9 * * 1` (Monday 9AM UTC)
3. Add Supabase node: GET from `website_leads` where `source=blog_subscribe` and `unsubscribed=false`
4. Add Code node with the content generation JS above
5. Add SplitInBatches node (batch size 10)
6. Add SMTP2GO Send Email node with the HTML template
7. Add Wait node (1 second)
8. Connect: Cron → Supabase → Code → SplitInBatches → Send Email → Wait → loop back to SplitInBatches
9. Test with your own email first
10. Publish workflow

## Email Template Location
`syntharra-automations/shared/email-templates/newsletter-weekly.html`

## Unsubscribe Flow
- Unsubscribe link in every email: `https://syntharra.com/unsubscribe.html?email={{email}}`
- Page PATCHes `website_leads` table setting `unsubscribed=true`
- Supabase query in step 2 filters out unsubscribed emails automatically
