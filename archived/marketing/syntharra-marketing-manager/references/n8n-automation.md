# n8n Marketing Automation

All marketing workflows deploy to: syntharra.app.n8n.cloud
Supabase: hgheyqwnrcvwtgngqdnq.supabase.co

---

## Workflows To Build

| # | Workflow Name | ID (assign on create) | Purpose |
|---|---|---|---|
| 1 | Lead Sourcer | TBD | Nightly — scrapes Google Places, stores leads |
| 2 | Email Sequence Manager | TBD | Drip emails Day 0, 3, 7 per lead |
| 3 | Hot Lead Detector | TBD | Webhook — fires on demo video click |
| 4 | Demo Booking Handler | TBD | Webhook — Cal.com booking confirmed |
| 5 | Lead Re-engagement | TBD | Monthly — re-engage cold leads |

---

## Workflow 1: Lead Sourcer

**Schedule:** Nightly at 2:00am US Central
**Input:** Industry + cities array (set in workflow variables)
**Output:** New rows in `marketing_leads` Supabase table

### Node Structure

```
Schedule Trigger (CRON: 0 2 * * *)
  │
Set Variables
  industry = "hvac"
  cities = [
    {"city": "Houston", "state": "TX"},
    {"city": "Phoenix", "state": "AZ"},
    {"city": "Dallas", "state": "TX"},
    {"city": "Atlanta", "state": "GA"},
    {"city": "Miami", "state": "FL"}
  ]
  google_api_key = {{$env.GOOGLE_PLACES_API_KEY}}
  │
SplitInBatches (loop cities)
  │
HTTP Request — Google Places Search
  URL: https://maps.googleapis.com/maps/api/place/textsearch/json
  Params:
    query: "{{industry}} contractor {{city}} {{state}}"
    key: {{google_api_key}}
  │
Function — Filter & Format Results
  // Filter: rating exists, phone exists, not a chain
  // Return array of formatted lead objects
  │
Supabase — Check Duplicate
  SELECT id FROM marketing_leads
  WHERE phone = '{{phone}}' OR
  (business_name ILIKE '%{{name}}%' AND city = '{{city}}')
  │
IF — Is Duplicate?
  No → Continue
  Yes → Skip (no-op)
  │
HTTP Request — Hunter.io Email Lookup (optional)
  URL: https://api.hunter.io/v2/domain-search
  Params: domain={{website_domain}}, type=personal
  │
Supabase — INSERT marketing_leads
  business_name, industry, city, state, country,
  phone, email, website, address, source, status='new'
  │
Aggregate Count
  │
Send Summary Email → admin@syntharra.com
  "Lead Sourcer complete: {{new_count}} new leads added for {{industry}} in {{date}}"
```

---

## Workflow 2: Email Sequence Manager

**Trigger:** New row in `marketing_leads` (via Supabase webhook or polling)
**OR:** Manual trigger with lead_id
**SMTP:** SMTP2GO via n8n credentials

### Node Structure

```
Webhook / Schedule Poll — New leads with status='new'
  │
Supabase SELECT — Get lead details
  │
Set UTM Code
  utm_code = {{lead_id}}_{{timestamp_short}}
  demo_url = "https://syntharra.com/demo?ref={{utm_code}}"
  │
─── EMAIL 1 BRANCH ───
Send Email (SMTP2GO)
  From: solutions@syntharra.com
  From Name: Dan at Syntharra
  To: {{email}}
  Subject: "8:47pm Friday. AC down. Did you answer?"
  Body: [Email 1 HTML from email-sequence.md]
  │
Supabase UPDATE
  status = 'emailed'
  email_sent_at = NOW()
  email_number = 1
  │
INSERT email_events
  lead_id, event_type='sent', email_number=1, utm_code
  │
Wait 3 Days
  │
─── EMAIL 2 BRANCH ───
Supabase SELECT — Check current status
  │
IF status = 'emailed' (not replied/booked/unsubscribed)
  │
Send Email 2
  Subject: "Re: {{business_name}} — quick follow up"
  Body: [Email 2 HTML]
  │
INSERT email_events (email_number=2)
  │
Wait 4 Days
  │
─── EMAIL 3 BRANCH ───
Check status again
  │
IF still 'emailed'
  │
Send Email 3
  Subject: "Last message from me, {{first_name}}"
  Body: [Email 3 HTML]
  │
INSERT email_events (email_number=3)
  │
Supabase UPDATE status = 'sequence_complete'
```

---

## Workflow 3: Hot Lead Detector

**Trigger:** HTTP Webhook at `/webhook/syntharra-demo-click`
**Fires when:** Lead clicks the demo video link (tracked via UTM redirect)

### How Click Tracking Works

1. Email contains link: `https://syntharra.com/demo?ref={{utm_code}}`
2. syntharra.com/demo page has JS that fires a pixel/webhook on load
3. n8n receives the utm_code → looks up lead → fires alert

### Node Structure

```
Webhook — POST /webhook/syntharra-demo-click
  Body: { utm_code, timestamp, user_agent }
  │
Supabase SELECT
  SELECT * FROM marketing_leads WHERE utm_code = '{{utm_code}}'
  (or join via email_events table)
  │
IF already alerted? (check video_clicked_at)
  Yes → Skip (dedup)
  No → Continue
  │
Supabase UPDATE marketing_leads
  status = 'clicked'
  video_clicked_at = NOW()
  │
INSERT email_events
  event_type = 'clicked'
  │
Send Hot Lead Alert Email → admin@syntharra.com
  Subject: "🔥 HOT LEAD: {{business_name}} just watched your demo"
  Body:
    Business: {{business_name}}
    Location: {{city}}, {{state}}
    Phone: {{phone}}
    Email: {{email}}
    Clicked at: {{timestamp}}
    [Book them now →] (link to booking page with pre-filled info)
  │
(Optional) Send SMS alert to Dan's mobile via Telnyx
```

---

## Workflow 4: Demo Booking Handler

**Trigger:** Cal.com webhook on booking created
**Fires when:** Lead books a demo call

### Node Structure

```
Webhook — POST /webhook/syntharra-booking
  Cal.com sends: attendee name, email, time, booking ID
  │
Supabase SELECT — Match by email
  SELECT * FROM marketing_leads WHERE email = '{{attendee_email}}'
  │
Supabase UPDATE marketing_leads
  status = 'booked'
  demo_booked_at = NOW()
  │
INSERT booked_demos
  lead_id, booking_time, cal_event_id, status='scheduled'
  │
Send Confirmation Email → attendee (solutions@syntharra.com)
  "Looking forward to our call, {{first_name}}!"
  Include: Cal.com calendar link, what to expect, demo video link
  │
Send Internal Alert → admin@syntharra.com
  "📅 DEMO BOOKED: {{business_name}} on {{booking_time}}"
  Full lead details for prep
```

---

## Environment Variables Required

Set in n8n → Settings → Variables or as n8n credentials:

| Variable | Value |
|---|---|
| `GOOGLE_PLACES_API_KEY` | Get from Google Cloud Console |
| `HUNTER_API_KEY` | hunter.io API key (optional) |
| `SMTP2GO_API_KEY` | api-0BE30DA64A074BC79F28BE6AEDC9DB9E |
| `SUPABASE_URL` | hgheyqwnrcvwtgngqdnq.supabase.co |
| `SUPABASE_KEY` | Supabase service role key |
| `CAL_WEBHOOK_SECRET` | Cal.com webhook signing secret |
| `BOOKING_URL` | Full Cal.com booking URL |

---

## Deployment Steps

1. Create Supabase tables (run SQL from lead-sourcing.md)
2. Import workflow JSONs to n8n (generate via this skill)
3. Set all environment variables
4. Set up UTM redirect on syntharra.com/demo page
5. Configure Cal.com webhook → n8n booking webhook URL
6. Test with 1 lead manually before enabling schedule
7. REMEMBER: Click Publish after every workflow edit

---

## UTM Redirect Setup (syntharra.com)

Add to website JavaScript:
```javascript
// On demo page load — fire click tracking
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const ref = params.get('ref');
  if (ref) {
    fetch('https://syntharra.app.n8n.cloud/webhook/syntharra-demo-click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        utm_code: ref,
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent
      })
    });
  }
});
```
