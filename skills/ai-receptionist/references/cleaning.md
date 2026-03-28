# Cleaning Industry Reference

## Form Fields (Google Form questions)

### Company Info
- Cleaning Company Name
- Main Company Phone Number
- Company Website
- Years in Business

### Agent Config
- AI Agent Name
- AI Voice Gender (Male / Female)

### Services
- Services Offered: Standard Residential Cleaning, Deep Cleaning, Move-In/Move-Out Cleaning, Office/Commercial Cleaning, Post-Construction Cleaning, Carpet Cleaning, Window Washing, Pressure Washing, Recurring Weekly/Biweekly/Monthly Service, One-Time Cleaning, Airbnb/Short-Term Rental Cleaning
- Specialties: Eco-Friendly Products, Pet-Friendly Cleaning, Allergy-Safe Products

### Service Area & Hours
- Primary Service Area
- Business Hours
- Typical Response Time / Next Available Appointment

### Pricing
- Pricing model: Per hour / Flat rate by home size / Custom quote
- Do you offer free estimates? (Yes / No / Quote over phone)
- Minimum booking size?
- Are products included? (Yes / Client provides / Optional)

### Trust & Credentials
- Are staff background-checked? (Yes / No)
- Are you bonded and insured? (Yes / No)
- Do you offer a satisfaction guarantee? (Yes / No / Policy)
- Staff size / number of crews

### Lead Routing
- Preferred Lead Contact Method (Phone / Email / Both)
- Lead Notification Phone Number
- Lead Notification Email
- Twilio Sender Number

### Other
- Booking System Used (Housecall Pro, Jobber, Launch27, Swept, Google Calendar, etc.)
- Anything else the AI should know about your company?

---

## Hot Lead Signals (GPT Scoring)

Note: Cleaning is NOT typically an emergency service. "Hot lead" means high-value or high-intent.

Score 8-10 (hot lead):
- Move-in/move-out cleaning (one-time high-value job, time-sensitive)
- Post-construction cleaning (large, profitable)
- Commercial/office cleaning inquiry (recurring, high value)
- Airbnb/short-term rental cleaning (recurring revenue)
- Caller ready to book: "when can you come?", "available this week?"
- Multiple properties or large home (4+ bedrooms)
- Explicitly mentions budget or "I'm looking for a regular service"

Score 5-7 (warm lead):
- One-time deep clean inquiry
- Standard residential recurring interest but price-shopping
- Moving in/out (vague timeline)
- Asking for a quote or estimate

Score 1-4 (cold):
- Just asking about products used
- Wants something extremely specific we likely don't do
- Very low intent ("just curious")
- Asking about job opportunities

---

## Cleaning-Specific Call Routing

Unlike HVAC or Plumbing, cleaning calls are almost never emergencies. Focus the AI on:

1. Understanding service type (residential one-time vs. recurring vs. commercial)
2. Getting property details (bedrooms, bathrooms, square footage, condition)
3. Getting timeline ("when do you need this done?")
4. Confirming what the caller cares about (price, products, background checks, etc.)
5. Capturing name, number, address, and best time for a quote

**Key difference from trade industries:** Don't rush to close. Cleaning clients often want to feel they can trust the people entering their home. The AI should acknowledge this: "All our staff are background-checked and bonded — your home is in good hands."

---

## Common Objections & Responses

- "How much does it cost?" → "Our pricing depends on the size of your home and the type of clean. Can I grab a few details so I can get you an accurate quote?"
- "Do I need to be home?" → "That's completely up to you — many of our clients give us a key or entry code. We're fully insured and background-checked."
- "What products do you use?" → Answer from form data. If eco-friendly: highlight it. If not specified: "We bring all our own professional-grade supplies."
- "Do you offer discounts for regular service?" → "Yes! Recurring weekly or biweekly service typically comes at a lower rate than one-time cleans."

---

## Sample GPT Lead Scoring Prompt (n8n node)

```
You are analyzing a call transcript for a residential and commercial cleaning company.

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
  "notes": "<property size, residential vs commercial, recurring vs one-time, timeline mentioned, etc.>"
}

CLEANING SCORING GUIDE:
- 8-10: Move-in/out cleaning (time-sensitive), post-construction, commercial/office inquiry, Airbnb/rental cleaning, large property, caller ready to book
- 5-7: Deep clean request, recurring residential interest, estimate for standard cleaning
- 1-4: Casual inquiry with no intent, asking about products only, wrong number, job application

TRANSCRIPT:
---
{{transcript}}
---
```
