---
name: ai-receptionist
description: >
  Build a complete AI phone receptionist automation system for any service-based business
  (HVAC, Plumbing, Electrical, Cleaning, Landscaping, Pest Control, Roofing, Garage Door, etc.).

  ALWAYS use this skill when the user asks about: setting up an AI receptionist for a new industry,
  automating client onboarding, building a call-handling AI agent, creating a Retell AI conversation flow,
  connecting Retell to n8n and Supabase, setting up lead capture via phone calls, creating a Jotform
  onboarding flow, or replicating the Syntharra AI Receptionist system for a new trade vertical.

  Also trigger when the user says things like "set this up for plumbing", "build plumbing standard",
  "do the same thing for cleaning companies", "new industry", "new vertical", "[INDUSTRY]-STD",
  "[INDUSTRY]-PRM", or anything about cloning/adapting the HVAC system for another trade.

  This skill generates: Retell conversation flow JSON, n8n workflow configs, Supabase migration SQL,
  Jotform onboarding form structure, call processor code, prompt templates, and a setup guide —
  all customized for the specified industry. Two tiers: Standard (lead capture + notifications)
  and Premium (Standard + booking + CRM/calendar integration).
---

# AI Receptionist System — Multi-Industry Builder

This skill generates a complete end-to-end AI phone receptionist system for any service-based industry,
matching the production Syntharra architecture.

## Current Production Architecture

```
Stripe Checkout (client pays)
    | webhook: checkout.session.completed
    v
n8n Stripe Workflow -> Supabase (stripe_payment_data) -> Welcome Email with Jotform link
    |
    v
Jotform Onboarding (client fills company details)
    | webhook to n8n
    v
n8n Onboarding Workflow
    |-- Creates Retell Agent via API (conversation flow clone)
    |-- Assigns phone number
    |-- Saves client config to Supabase ([industry]_[tier]_agent)
    |-- Sends client welcome email (with phone number + dashboard link)
    |-- Sends setup emails for CRM/calendar OAuth (Premium only)
    +-- Sends Dan internal notification
        |
        v (client's phone starts ringing)
Retell AI Agent (handles inbound calls via conversation flow)
    | post-call webhook
    v
n8n Call Processor Workflow
    |-- Parses transcript via code node (NOT GPT, uses JS extraction)
    |-- Scores lead, extracts caller info, detects emergency
    |-- Saves to Supabase ([industry]_call_log)
    |-- Sends email notification to client (SMTP2GO)
    |-- Sends SMS notification (Telnyx, when enabled)
    +-- Repeat caller detection (Premium)
        |
        v
Client Dashboard (syntharra.com/dashboard.html?agent_id=X)
    +-- Real-time call data from Supabase
```

## Tech Stack (DO NOT deviate)

| Component | Tool | Notes |
|-----------|------|-------|
| Agent builder | Retell AI | Conversation flows, NOT single-prompt agents |
| Phone numbers | Retell (built-in) | Buy directly through Retell, NOT Twilio |
| Automation | n8n (cloud) | syntharra.app.n8n.cloud |
| Database | Supabase | hgheyqwnrcvwtgngqdnq.supabase.co |
| Onboarding form | Jotform | REST API (NOT MCP OAuth connector, it is broken) |
| Email | SMTP2GO | API key: api-0BE30DA64A074BC79F28BE6AEDC9DB9E |
| SMS | Telnyx | Preferred. NOT Twilio, NOT Plivo |
| Payments | Stripe | Checkout sessions with setup fee + subscription |
| OAuth server | Express.js on Railway | auth.syntharra.com |
| Website/Dashboard | GitHub Pages | syntharra.com |
| Prompts | Commas not dashes | Always use commas instead of dashes in agent prompts |

## Two Tiers

### Standard ($497/mo, 475 min)
- Inbound call handling with AI conversation flow
- Lead capture (name, phone, address, service needed)
- Emergency detection and transfer
- Email/SMS notifications to client on each call
- Client dashboard
- Weekly usage report email

### Premium ($997/mo, 1000 min)
Everything in Standard, plus:
- Real-time job booking via CRM/calendar integration
- Repeat caller detection
- CRM sync (Jobber, Housecall Pro, ServiceTitan, HubSpot, GoHighLevel, etc.)
- Calendar integration (Google Calendar, Outlook, Calendly, Cal.com, etc.)
- Integration dispatcher workflow
- Enhanced call analysis

---

## How To Use This Skill

When building a new industry vertical, follow these steps:

### Step 1: Gather Requirements

1. **Industry** — e.g., Plumbing, Electrical, Cleaning, Roofing
2. **Tier** — Standard or Premium (or both)
3. **Industry tag** — e.g., [PLMB-STD], [ELEC-PRM]

If the user says "build plumbing standard" or similar, infer from context.

### Step 2: Read the Industry Reference

Read the appropriate references/[industry].md file for:
- Service categories and common services
- Emergency scenarios and routing logic
- Hot/warm/cold lead signals for scoring
- Seasonal patterns
- Industry-specific Jotform fields

If no reference exists, use references/generic-service.md and adapt.

### Step 3: Generate All Components

For each new industry, generate and customize:

| Component | File Pattern | Purpose |
|-----------|-------------|---------|
| Conversation flow | [industry]-conversation-flow.json | Retell conversation flow nodes |
| Prompt builder | [industry]-prompt-builder.js | Builds agent prompt from client config |
| Call processor | [industry]-call-processor.js | JS code node for n8n call processor |
| Supabase migration | [industry]-supabase-migration.sql | Creates agent + call_log tables |
| Jotform structure | [industry]-jotform-fields.md | Onboarding form field list |
| n8n onboarding | [industry]-onboarding-workflow.json | n8n workflow JSON |
| n8n call processor | [industry]-call-processor-workflow.json | n8n workflow JSON |
| Setup guide | [industry]-SETUP-GUIDE.md | Step-by-step deployment instructions |

### Step 4: Industry Customization Points

Each industry requires customizing:

**Conversation Flow Nodes** (adapt the HVAC Standard 12-node flow):
- greeting, identify_call, nonemergency_leadcapture, verify_emergency,
  callback, existing_customer, general_questions, spam_robocall,
  Transfer Call (warm whisper), transfer_failed, Ending, End Call

**Call Processor JS** (adapt from HVAC):
- notification_type mapping (industry-specific call categories)
- service_requested extraction (industry service list)
- urgency detection (industry emergency keywords)
- lead_score calculation (industry scoring criteria)
- job_type classification

**Supabase Tables**:
- [industry]_standard_agent / [industry]_premium_agent (client config)
- [industry]_call_log (call records with industry-specific fields)

**Jotform Fields**:
- Base fields same across all industries (company info, contact, AI config)
- Industry-specific: services offered, certifications, equipment brands
- Premium adds: CRM platform, calendar platform, booking config

---

## Retell Conversation Flow Architecture

### Standard Flow (12 nodes)
greeting -> identify_call
    |-- nonemergency_leadcapture -> Ending -> End Call
    |-- verify_emergency -> Transfer Call -> transfer_failed
    |-- callback -> Ending
    |-- existing_customer -> Transfer Call
    |-- general_questions -> Ending
    +-- spam_robocall -> End Call

### Premium Flow (adds booking + dispatch)
Same as Standard plus:
- check_availability (queries calendar via tool)
- book_appointment (creates booking via tool)
- confirm_booking (confirms details with caller)

### Key Rules
- Use conversation flows, NOT single-prompt agents
- Dynamic variables: {{agent_name}}, {{company_name}}, {{COMPANY_INFO_BLOCK}}
- Always use commas instead of dashes in prompts
- Keep individual node prompts under 200 words
- Warm transfer whisper: tell the human who is calling before connecting

---

## n8n Workflow Patterns

### Onboarding Workflow (per industry)
Trigger: Jotform webhook -> Extract form data -> Build prompt -> Create Retell agent via API ->
Assign phone number -> Save to Supabase -> Publish agent -> Send welcome email (SMTP2GO) ->
Send setup emails (Premium: OAuth links) -> Send internal notification to Dan

### Call Processor Workflow (per industry)
Trigger: Retell post-call webhook -> Filter (only completed calls) ->
Lookup agent in Supabase -> Parse transcript (JS code node, NOT GPT) ->
Calculate lead score -> Save to Supabase call_log -> Send notification email (SMTP2GO) ->
Send SMS if enabled (Telnyx)

### Supporting Workflows (shared across all industries)
- Stripe Workflow (checkout.session.completed)
- Minutes Calculator (monthly usage per client)
- Usage Alert (80% and 100% warnings)
- Weekly Lead Report (branded weekly summary per client)
- Publish Retell (publishes agent after API updates)
- Nightly GitHub Backup

### Critical n8n Rules
- ALWAYS click Publish after editing any workflow
- ALL emails via SMTP2GO (api key in code nodes)
- Error handling: every workflow needs an error notification email node

---

## Supabase Schema Pattern

### Agent Table: [industry]_[tier]_agent
Core columns (same across all industries):
agent_id, conversation_flow_id, voice_id, agent_language, company_name, owner_name,
company_phone, client_email, website, years_in_business, timezone, industry_type,
agent_name, voice_gender, custom_greeting, company_tagline, services_offered,
service_area, service_area_radius, licensed_insured, business_hours, response_time,
emergency_service, emergency_phone, after_hours_behavior, after_hours_transfer,
pricing_policy, free_estimates, financing_available, warranty, warranty_details,
payment_methods, lead_contact_method, lead_phone, lead_email, transfer_phone,
transfer_triggers, transfer_behavior, plan_type, stripe_customer_id, subscription_id,
notification_email_2, notification_email_3, notification_sms_2, notification_sms_3

Premium adds: crm_platform, crm_status, crm_access_token, crm_refresh_token,
calendar_platform, calendar_status, calendar_access_token, calendar_refresh_token,
booking_buffer_minutes, default_appointment_duration, dispatch_mode

### Call Log Table: [industry]_call_log
agent_id, call_id, created_at, caller_name, caller_phone, caller_address,
service_requested, notification_type, lead_score, is_hot_lead, booking_success,
summary, duration_seconds, call_type, urgency, job_type, caller_sentiment,
vulnerable_occupant, notes, geocode_status, geocode_formatted

---

## Retell Agent Management Rules (CRITICAL)

- NEVER delete or recreate a Retell agent. Agent ID is the foreign key. Always patch in place.
- ALWAYS call POST https://api.retellai.com/publish-agent/{agent_id} after any update.
- ALWAYS push to GitHub after sessions with changes.
- Buy phone numbers through Retell directly, not Twilio.

---

## OAuth / Integration Architecture (Premium only)

OAuth server at auth.syntharra.com handles:
- Calendar OAuth: Google Calendar, Outlook, Calendly, Cal.com, Acuity Scheduling
- CRM OAuth: Jobber, Housecall Pro, HubSpot, GoHighLevel
- API key entry: ServiceTitan, FieldEdge, Kickserv, Workiz (via /submit-key endpoint)

Flow: Client clicks connect link -> Platform login -> Token saved to Supabase -> AI can book/sync

---

## Industry Reference Files

Read the relevant file before generating any industry components:
- references/hvac.md
- references/plumbing.md
- references/electrical.md
- references/cleaning.md
- references/generic-service.md

If a reference file does not exist for the requested industry, create one following
the pattern of existing reference files, then proceed with generation.

---

## Output Checklist

Before declaring the task complete, verify:
- [ ] Conversation flow JSON has all 12+ nodes with proper routing
- [ ] Prompt builder uses {{agent_name}}, {{company_name}}, {{COMPANY_INFO_BLOCK}}
- [ ] All prompts use commas, not dashes
- [ ] Call processor JS handles all notification types for the industry
- [ ] Supabase migration creates both agent and call_log tables
- [ ] Jotform field list covers all industry-specific needs
- [ ] n8n workflows use SMTP2GO for email, NOT Gmail
- [ ] Setup guide includes all API keys, webhook URLs, and step-by-step instructions
- [ ] Emergency routing is appropriate for the industry
- [ ] Lead scoring criteria are industry-specific
