# HVAC Industry Reference

## Form Fields (Google Form questions)

### Company Info
- HVAC Company Name
- Main Company Phone Number
- Company Website
- Years in Business

### Agent Config
- AI Agent Name
- AI Voice Gender (Male / Female)

### Services
- Services Offered: Installation, Repair, Maintenance, Tune-Up, Duct Cleaning, Air Quality Testing, Thermostat Installation, Heat Pump Service, Boiler Service
- Brands / Equipment Serviced: Lennox, Carrier, Trane, Goodman, Rheem, York, Bryant, Daikin, Mitsubishi, American Standard

### Service Area & Hours
- Primary Service Area
- Business Hours
- Typical Response Time

### Emergency
- Do you offer 24/7 emergency service? (Yes / No)
- Emergency After-Hours Phone Number
- After-Hours Behavior

### Pricing & Trust
- Are estimates free? (Yes / No / For some services)
- Financing Available? (Yes / No)
- Do you offer service warranties? (Yes / No)
- Warranty Details
- Licensed and Insured? (Yes / No)
- Certifications: EPA 608, NATE Certified, ACCA Member, Factory Authorized, North American Technician Excellence

### Lead Routing
- Preferred Lead Contact Method (Phone / Email / Both)
- Lead Notification Phone Number
- Lead Notification Email
- Twilio Sender Number

### Other
- Booking System Used (ServiceTitan, HouseCall Pro, Google Calendar, Jobber, etc.)
- Anything else the AI should know about your company?

---

## Hot Lead Signals (GPT Scoring)

Score 8-10 (hot lead, needs immediate follow-up):
- "no heat", "no AC", "air conditioner not working", "furnace broke", "pipes freezing"
- Emergency calls (outside hours + urgent language)
- "replace the whole system", "new installation", "brand new home", "just bought a house"
- Commercial property or multi-unit building
- Caller has already decided to buy / "how soon can you come?"
- Mentions specific equipment by brand suggesting existing system failure

Score 5-7 (warm lead, good follow-up):
- Wants an estimate or quote
- Asking about maintenance plans / tune-ups
- Seasonal preparation ("getting ready for summer/winter")
- Asking about financing or payment plans
- Has an older system, asking about replacement options

Score 1-4 (cold or non-lead):
- Calling to pay a bill or check invoice
- Wrong number
- Asking about job applications / hiring
- Competitor inquiry
- Unintelligible or very short call with no service need expressed

---

## Seasonal Context (prompt tuning note)

Note in the prompt for seasonal relevance:
- **Summer** (Jun-Aug): AC failures are emergencies; maintenance tune-ups are high-value
- **Winter** (Dec-Feb): Heat failures are emergencies; furnace installations spike
- **Spring/Fall**: Shoulder season — ideal for maintenance, system evaluations, duct cleaning

---

## Emergency Routing Logic

```
IF caller mentions:
  - "no heat" or "no AC" or system failure AND it's cold/hot season
  - "gas smell" → immediately say: call 911 or gas company first, then us
  - "CO alarm" (carbon monoxide) → immediately say: evacuate, call 911, then call us
  - "flooding from unit" → urgent, same-day service
THEN:
  - After-hours: give emergency_phone
  - During hours: flag as urgent, collect name/address/phone, promise call-back within response_time
```

---

## Upsell Prompts

When caller mentions old equipment:
- "How old is your current system? If it's over 10-12 years, replacing it might actually be more cost-effective — we can run the numbers for you."

When caller asks about repair:
- "While we're there, we can also do a system tune-up to make sure everything is running at peak efficiency — many customers find this saves on energy bills."

---

## Sample GPT Lead Scoring Prompt (n8n node)

```
You are analyzing a call transcript for an HVAC company lead qualification.

Return ONLY valid JSON:
{
  "lead_score": <1-10>,
  "is_hot_lead": <true if score >= 6>,
  "caller_name": "<string or null>",
  "caller_phone": "<string or null>",
  "caller_address": "<string or null>",
  "service_requested": "<one line description>",
  "summary": "<2-3 sentence summary of the call>",
  "urgency": "<low / medium / high>",
  "notes": "<anything important: system age, commercial property, repeat customer, etc.>"
}

HVAC SCORING GUIDE:
- 8-10: Emergency (no heat/AC), system replacement inquiry, commercial/multi-unit, caller ready to book
- 5-7: Estimate request, maintenance scheduling, seasonal tune-up, financing question
- 1-4: Bill inquiry, wrong number, job application, no service need expressed

TRANSCRIPT:
---
{{transcript}}
---
```
