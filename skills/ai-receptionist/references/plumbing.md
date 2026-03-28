# Plumbing Industry Reference

## Form Fields (Google Form questions)

### Company Info
- Plumbing Company Name
- Main Company Phone Number
- Company Website
- Years in Business

### Agent Config
- AI Agent Name
- AI Voice Gender (Male / Female)

### Services
- Services Offered: Leak Repair, Drain Cleaning, Pipe Replacement, Water Heater Install/Repair, Toilet Repair/Install, Faucet Repair/Install, Sewer Line Service, Hydro Jetting, Backflow Prevention, Gas Line Service, Water Softener Install, Emergency Plumbing
- Specialties: Residential, Commercial, New Construction, Remodels

### Service Area & Hours
- Primary Service Area
- Business Hours
- Typical Response Time

### Emergency
- Do you offer 24/7 emergency service? (Yes / No)
- Emergency After-Hours Phone Number
- After-Hours Behavior

### Pricing & Trust
- Are estimates free? (Yes / No / Diagnostic fee applies)
- Financing Available? (Yes / No)
- Do you offer service warranties? (Yes / No)
- Warranty Details
- Licensed and Insured? (Yes / No)
- Certifications: Master Plumber, Journeyman Plumber, Backflow Certified, Gas Line Certified, State License Number

### Lead Routing
- Preferred Lead Contact Method (Phone / Email / Both)
- Lead Notification Phone Number
- Lead Notification Email
- Twilio Sender Number

### Other
- Booking System Used
- Anything else the AI should know about your company?

---

## Hot Lead Signals (GPT Scoring)

Score 8-10 (hot lead):
- "burst pipe", "water everywhere", "flooding", "sewage backup"
- "no hot water" (water heater failure) — daily necessity, high urgency
- "gas smell" or "gas leak" → ALWAYS: tell caller to leave and call gas company + 911 first
- Sewer line issues ("backing up everywhere", "raw sewage")
- Commercial property or multi-unit (higher revenue)
- Water heater replacement (big-ticket job)
- Caller says "it's an emergency" or "ASAP"

Score 5-7 (warm lead):
- Slow drains, clogged drains (scheduled service)
- Leaky faucet or running toilet (not urgent but real need)
- Water pressure issues
- Planning a remodel or new construction
- Asking about water softener installation
- Requesting an estimate

Score 1-4 (cold):
- Asking about job openings
- Calling to pay a bill
- Wrong number
- Very vague inquiry with no commitment

---

## Emergency Routing Logic

```
IF caller mentions:
  - "gas smell" → "For your safety, please leave the building immediately and call your gas company and 911 before calling us. Once you're safe, we can send someone right away."
  - "burst pipe" / "flooding" / "water everywhere" → immediate emergency, give emergency number after hours
  - "sewage backup" → high urgency, same-day service
  - "no hot water" + household with children/elderly → elevated urgency
THEN:
  - After-hours: give emergency_phone
  - During hours: flag as urgent, collect name/address, promise callback within response_time
```

---

## Key Differentiators (helpful for trust-building)

Questions the AI might answer:
- "Are you licensed?" → confirm licensed and insured status
- "Do you do free estimates?" → answer from form data
- "Do you charge for coming out?" → answer from form data (some plumbers charge a diagnostic fee)
- "How long will it take?" → "It depends on the issue, but for most jobs our technician can give you a timeframe when they arrive."

---

## Sample GPT Lead Scoring Prompt (n8n node)

```
You are analyzing a call transcript for a plumbing company lead qualification.

Return ONLY valid JSON:
{
  "lead_score": <1-10>,
  "is_hot_lead": <true if score >= 6>,
  "caller_name": "<string or null>",
  "caller_phone": "<string or null>",
  "caller_address": "<string or null>",
  "service_requested": "<one line description>",
  "summary": "<2-3 sentence summary>",
  "urgency": "<low / medium / high>",
  "notes": "<commercial vs residential, recurring issue, prior service history mentioned, etc.>"
}

PLUMBING SCORING GUIDE:
- 8-10: Burst pipe, flooding, sewage backup, no hot water, gas smell, commercial/multi-unit property
- 5-7: Clogged drains, leaky faucets, estimate requests, remodel inquiry, water heater replacement quote
- 1-4: Bill inquiry, wrong number, job application, general question with no service need

TRANSCRIPT:
---
{{transcript}}
---
```
