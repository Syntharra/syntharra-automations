---
name: ai-receptionist
description: >
  Build a complete AI phone receptionist automation system for any service-based business
  (HVAC, Plumbing, Cleaning, Landscaping, Pest Control, Electrician, etc.).

  ALWAYS use this skill when the user asks about: setting up an AI receptionist for a new
  industry/vertical, automating client onboarding, building a call-handling AI agent,
  creating a Retell AI conversation flow, connecting Retell to n8n workflows, setting up
  lead capture via phone calls, creating Jotform onboarding for service businesses,
  replicating the Syntharra system for a new industry, or anything involving the
  Standard or Premium AI receptionist pipelines.

  Also trigger when the user says things like "set this up for plumbing",
  "do the same thing for cleaning companies", "new industry", "new vertical",
  "build the electrical version", or references the Syntharra receptionist system.

  This skill covers the COMPLETE production stack: Retell AI agents + conversation flows,
  Jotform onboarding, n8n workflows (onboarding, call processor, Stripe, usage tracking),
  Supabase database, SMTP2GO emails, OAuth integrations, client dashboard, and the
  Stripe checkout pipeline. Use the HVAC Standard and Premium pipelines as the template.
---

# AI Receptionist System — Multi-Industry Builder

This skill generates a complete end-to-end AI phone receptionist system for any service-based industry, based on the production Syntharra architecture.

## Production Architecture (2026)

```
Stripe Checkout (pricing page)
    | checkout.session.completed webhook
    v
n8n Stripe Workflow -> Supabase (stripe_payment_data) -> Welcome Email with Jotform link
    |
    v
Jotform Onboarding Form (industry-specific, 50-60 questions)
    | webhook to n8n
    v
n8n Onboarding Workflow
    |-- Parse form data
    |-- Build prompts from template
    |-- Create Retell agent via API (conversation flow based)
    |-- Save client config to Supabase
    |-- Send branded welcome email (SMTP2GO)
    |-- Send integration setup emails (OAuth/API key)
    +-- Notify Dan internally

Retell AI Agent (live, per-client)
    | post_call_analysis webhook
    v
n8n Call Processor Workflow
    |-- Parse transcript + call analysis
    |-- Score lead, extract caller data
    |-- Save to Supabase (call_log)
    |-- Send notification emails (SMTP2GO)
    |-- Send SMS notifications (Telnyx, when enabled)
    +-- Repeat caller detection (Premium)

Premium Extras:
    |-- Integration Dispatcher (Google Cal + Jobber booking)
    |-- OAuth Server (calendar/CRM connections)
    +-- Client Dashboard (syntharra.com/dashboard.html?agent_id=X)

Supporting Workflows:
    |-- Weekly Lead Report (branded email to clients)
    |-- Monthly Minutes Calculator + Overage Billing
    |-- Usage Alert Monitor (80% / 100% warnings)
    |-- Nightly GitHub Backup
    +-- Scenario Test Runner (E2E testing)
```

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Agent builder | Retell AI | Conversation flow based, not prompt-only |
| Automation | n8n (cloud) | syntharra.app.n8n.cloud |
| Database | Supabase | hgheyqwnrcvwtgngqdnq.supabase.co |
| Onboarding forms | Jotform | REST API (NOT MCP connector) |
| Email | SMTP2GO | API key in all email nodes |
| SMS | Telnyx | Pending activation, wired but disabled |
| Payments | Stripe | Checkout + webhook pipeline |
| OAuth | Custom Express server | Railway, Google/Outlook/Calendly/CRM |
| Website | GitHub Pages | syntharra.com |
| Hosting | Railway | OAuth server + Stripe checkout |
| Version control | GitHub | syntharra-automations repo |

## Two Tiers

### Standard ($497/mo)
- AI receptionist handles inbound calls
- Lead capture, scoring, notifications
- Emergency detection + live transfer
- Client dashboard
- Weekly lead report emails
- 475 minutes/month

### Premium ($997/mo)
- Everything in Standard, plus:
- Calendar booking (Google Cal, Outlook, Calendly, etc.)
- CRM integration (Jobber, Housecall Pro, HubSpot, GoHighLevel, etc.)
- Repeat caller detection
- Integration dispatcher workflow
- 1,000 minutes/month

---

## How To Build a New Industry

When the user asks to set up this system for a new industry, follow these steps:

### Step 1: Read References

Read the industry-specific reference file:
- `references/hvac.md` — production template
- `references/plumbing.md`
- `references/cleaning.md`
- `references/generic-service.md` — any other industry

Also read production files from GitHub syntharra-automations repo for exact patterns.

### Step 2: Create Supabase Tables

Create per industry (clone from HVAC schema):

**`[industry]_standard_agent`** — client config (60+ columns):
Core, Agent config, Services, Hours, Pricing, Notifications, Transfer, Marketing, Billing, Meta

**`[industry]_call_log`** — call data:
agent_id, call_id, retell_call_id, created_at, caller_name, caller_phone, caller_address, service_requested, notification_type, lead_score, is_hot_lead, booking_success, summary, duration_seconds, call_type, urgency, caller_sentiment, job_type, notes

Premium adds: `[industry]_premium_agent` (standard + CRM/calendar integration columns)

### Step 3: Create Jotform Onboarding Form

50-60 questions in 5-7 sections via Jotform REST API:
1. Business Information
2. AI Receptionist Configuration
3. Services and Coverage (industry-specific)
4. Call Handling and Pricing
5. Lead Capture and Notifications
6. Branding, Promotions and Extras
7. Booking and Integration (Premium only)

### Step 4: Build Retell Conversation Flow

Standard flow (12 nodes): greeting, identify_call, nonemergency_leadcapture, verify_emergency, callback, existing_customer, general_questions, spam_robocall, Transfer Call, transfer_failed, Ending, End Call

**Prompt rules:** commas not dashes, dynamic variables (agent_name, company_name, COMPANY_INFO_BLOCK), under 30 words per response, never guess pricing.

### Step 5: Build n8n Workflows

Clone from HVAC and adapt:
1. **Onboarding** — Jotform webhook -> parse -> create Retell agent -> Supabase -> welcome email
2. **Call Processor** — Retell webhook -> parse -> score -> Supabase -> notifications
3. **Stripe** — update Jotform URL for new industry
4. **Supporting** — weekly report, minutes calc, usage alerts (shared)

### Step 6: Update Dashboard

Add new table names to the dashboard lookup chain in dashboard.html.

### Step 7: Test End-to-End

Simulate: Jotform submission -> agent creation -> test call -> call log -> dashboard -> weekly report.

---

## Key Rules (ALWAYS follow)

- Never delete or recreate a Retell agent — patch in place
- Always publish after Retell agent updates
- Always push to GitHub after sessions with changes
- Use commas not dashes in all agent prompts
- n8n edits require manual Publish to go live
- Jotform: REST API only, NOT MCP connector
- SMTP2GO for all emails, never Gmail or SES
- Telnyx for SMS, never Twilio

---

## Industry Reference Files

- `references/hvac.md` — HVAC (production template)
- `references/plumbing.md` — Plumbing
- `references/cleaning.md` — Cleaning
- `references/generic-service.md` — Any other industry

For unlisted industries, use generic-service.md and adapt services, emergencies, lead signals, seasonal patterns.
