# Generic Service Business Reference

Use this template for any service industry not covered by a dedicated reference file.
Adapt the field names, service lists, and lead signals to match the specific business type.

## Form Fields Template

### Company Info
- [Industry] Company Name
- Main Company Phone Number
- Company Website
- Years in Business

### Agent Config
- AI Agent Name
- AI Voice Gender (Male / Female)

### Services
- Services Offered: [list of 6-12 common services for this industry]
- Specialties / Certifications: [any industry-specific credentials]

### Service Area & Hours
- Primary Service Area
- Business Hours
- Typical Response Time

### Emergency
- Do you offer emergency service? (Yes / No)
- Emergency Phone Number (if Yes)
- After-Hours Behavior

### Pricing & Trust
- Are estimates/consultations free? (Yes / No)
- Financing Available? (Yes / No)
- Do you offer service guarantees or warranties? (Yes / No)
- Guarantee/Warranty Details
- Licensed and Insured? (Yes / No)
- Certifications

### Lead Routing
- Preferred Lead Contact Method (Phone / Email / Both)
- Lead Notification Phone Number
- Lead Notification Email
- Twilio Sender Number

### Other
- Booking System Used
- Anything else the AI should know?

---

## Call Flow Template

All service businesses share this general call flow:

1. **Greet** → "How can I help you today?"
2. **Identify Need** → Is this emergency / estimate / scheduling / general question?
3. **Qualify** → What's the issue? How big is the job? Residential or commercial?
4. **Collect Info** → Name, address, phone, best time for callback or appointment
5. **Set Expectations** → "Someone will follow up within [response_time]"
6. **Close Warmly** → Confirm everything, thank them

---

## Lead Scoring Template

Customize these signals per industry:

Score 8-10 (hot lead):
- Emergency or urgent service need (same-day)
- Large-scale job (commercial, multi-unit, new construction)
- Caller is ready to schedule now
- High-value service type (installation, full replacement, ongoing contract)

Score 5-7 (warm lead):
- Wants an estimate or quote
- Interested in recurring/maintenance service
- Shopping around but has a real need
- Has a specific service in mind, flexible on timing

Score 1-4 (cold):
- Asking general questions with no service intent
- Wrong number
- Job application
- Competitor checking prices
- Already has service scheduled elsewhere

---

## Adapting for Specific Industries

### Landscaping / Lawn Care
- Emergency: fallen trees, storm damage
- Hot leads: commercial properties, seasonal contracts, irrigation installation
- Seasonal: spring cleanup, fall leaf removal

### Pest Control
- Emergency: active infestation (bees/wasps in walls, rats in home)
- Hot leads: commercial kitchens (regulatory requirement), new construction treatment, termite damage
- Recurring: monthly/quarterly service contracts are the bread-and-butter

### Electrician
- Emergency: power outage, sparking outlets, burning smell
- Hot leads: panel upgrade, EV charger installation, new construction rough-in, commercial
- SAFETY NOTE: For "sparking wires" or "burning smell" → tell caller to cut power at the breaker and call 911 if any fire risk

### Roofing
- Emergency: active roof leak, storm damage
- Hot leads: full roof replacement, insurance claim assistance, commercial flat roof
- Seasonal: spring (post-winter inspection), fall (pre-winter prep)

### Pool Service
- Emergency: green/unsafe water, equipment failure before an event
- Hot leads: new pool installation, complete renovation, commercial/HOA pools
- Recurring: weekly maintenance contracts

### General Contracting / Remodeling
- Emergency: structural damage, flood damage
- Hot leads: kitchen/bath remodel, home addition, insurance restoration
- Sales cycle is long — capture contact info and follow up with a consultation

---

## Sample GPT Lead Scoring Prompt (n8n node — generic)

```
You are analyzing a call transcript for a [INDUSTRY] service company.

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
  "notes": "<job size, residential vs commercial, repeat customer, timeline, special requirements>"
}

SCORING GUIDE:
- 8-10: Emergency or urgent need, large-scale job, commercial property, caller ready to book
- 5-7: Estimate request, recurring service interest, specific need with flexible timing
- 1-4: General question, wrong number, job application, no clear service intent

TRANSCRIPT:
---
{{transcript}}
---
```
