---
name: ai-receptionist
description: >
  Build a complete AI phone receptionist system for any service-based business
  (HVAC, Plumbing, Cleaning, Landscaping, Pest Control, Electrician, etc.).
  ALWAYS use this skill when the user asks about setting up an AI receptionist for a new industry,
  replicating the Syntharra system, or says "set this up for plumbing/cleaning/electrical" etc.
  Output: Jotform config, n8n workflow JSON, Retell prompt + conversation flow, Supabase schema,
  email templates, and a setup guide — all customized for the specified industry.
---

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

# AI Receptionist System — Multi-Industry Builder

## Production Architecture (2026)

```
Client signs up via Stripe Checkout
    │
    ▼
Stripe Webhook → n8n "Stripe Workflow"
    │ Saves to Supabase, sends Welcome Email with Jotform link
    ▼
Client completes Jotform (Standard or Premium)
    │
    ▼
Jotform Webhook → n8n "Onboarding Workflow"
    │ Builds Retell prompt, creates conversation flow + agent via API
    │ Saves config to Supabase, assigns phone number
    │ Sends "You're Live" email + Call Forwarding PDF
    ▼
Calls come in → Retell AI answers
    │
    ▼
Retell call_analyzed webhook → n8n "Call Processor"
    │ GPT analyzes transcript, scores lead
    │ Saves to Supabase hvac_call_log
    │ Sends branded call alert email to client
    ▼
Weekly: n8n "Weekly Lead Report" sends summary
Daily: n8n "Usage Alert" checks minute thresholds
```

## Live Infrastructure

| Component | Service | Details |
|---|---|---|
| AI Voice | Retell AI | Agent + conversation flow per client |
| Workflows | n8n Cloud | syntharra.app.n8n.cloud |
| Database | Supabase | hgheyqwnrcvwtgngqdnq.supabase.co |
| Onboarding Forms | Jotform | Standard 260795139953066, Premium 260819259556671 |
| Email | SMTP2GO | All outbound via API |
| Checkout | Railway | Node.js, syntharra-checkout repo |
| OAuth (Premium) | Railway | syntharra-oauth-server repo |
| Website | GitHub Pages | syntharra-website repo |
| Phone Numbers | Telnyx (pending) | Plivo as backup |

## Email Branding Standard

ALL client-facing emails MUST use the approved Syntharra branding:
- Light theme: white (#fff) cards, grey (#F7F7FB) outer bg
- Approved logo block: `brand-assets/email-logo-block.html`
- Icon: hosted PNG at raw.githubusercontent.com (NOT base64 SVG)
- Wordmark: "Syntharra" + "GLOBAL AI SOLUTIONS" left-aligned to same edge
- Support: support@syntharra.com (never "reply to this email")
- CTA buttons: #6C63FF background, white text, 10px radius
- See `brand-assets/BRAND-SPEC.md` for full spec

Email templates with dynamic variables: `marketing/emails/templates/`

## How To Use This Skill

### Step 1: Gather Requirements

Required for a new industry vertical:

1. **Industry** — e.g., Plumbing, Cleaning, Electrical, Pest Control, Landscaping
2. **Service categories** — what services do these businesses typically offer?
3. **Emergency scenarios** — what constitutes an emergency in this industry?
4. **Lead signals** — what phrases indicate a high-value lead?
5. **Common call types** — service/repair, new install/quote, existing customer, general enquiry

If the user says "do the same as HVAC but for Plumbing", infer from the HVAC reference and adapt.

### Step 2: Read Industry Reference

Check `references/[industry].md` for pre-built service lists, emergency scenarios, and lead signals:
- `references/hvac.md` — HVAC
- `references/plumbing.md` — Plumbing
- `references/electrical.md` — Electrical
- `references/cleaning.md` — Cleaning
- `references/generic-service.md` — Template for any industry

### Step 3: Generate All Files

| File | Purpose |
|---|---|
| `[industry]-standard/prompt-builder.js` | Builds Retell prompt from Jotform data |
| `[industry]-standard/conversation-flow.json` | Retell conversation flow (12 nodes) |
| `[industry]-standard/call-processor-parse.js` | GPT analysis prompt + lead scoring |
| `[industry]-standard/jotform-fields.md` | Jotform field config for this industry |
| `[industry]-standard/supabase-schema.sql` | Supabase table creation |
| `[industry]-standard/email-templates/` | All email templates with dynamic variables |
| `[industry]-SETUP-GUIDE.md` | Complete deployment guide |

### Step 4: Adapt Per Industry

Each industry needs custom:

**Conversation Flow (12 nodes — same structure, different content):**
- `greeting` — industry-appropriate welcome
- `identify_call` — route to correct flow
- `nonemergency_leadcapture` — capture name, phone, address, service needed
- `verify_emergency` — industry-specific emergency detection
- `callback` — schedule callback
- `existing_customer` — handle existing customer requests
- `general_questions` — FAQ using company info block
- `spam_robocall` — detect and end junk calls
- `Transfer Call` — live transfer to owner
- `transfer_failed` — fallback if transfer fails
- `Ending` — confirm details captured
- `End Call` — goodbye

**Prompt Template (uses commas not dashes for AI readability):**
```
You are {{agent_name}}, the friendly AI receptionist for {{company_name}}.

YOUR MISSION:
1. [industry-specific greeting]
2. Gather caller's name, callback number, and service address
3. Answer questions using company info below
4. [industry-specific routing: emergency / quote / schedule]
5. End warmly, confirming what you've captured

COMMUNICATION STYLE:
- Keep responses short and clear (under 30 words)
- Be warm but professional
- Never guess at pricing
- Always confirm name, phone, and address before ending

COMPANY INFORMATION:
{{COMPANY_INFO_BLOCK}}
```

**GPT Lead Scoring (call processor):**
```json
{
  "lead_score": 1-10,
  "is_lead": true/false,
  "caller_name": "string",
  "caller_phone": "string",
  "caller_address": "string",
  "service_type": "string",
  "job_type": "repair|install|maintenance|quote|emergency",
  "urgency": "low|medium|high|emergency",
  "call_summary": "2-3 sentences",
  "vulnerable_occupant": true/false,
  "caller_sentiment": "positive|neutral|frustrated|angry"
}
```

Scoring guide per industry:
- 8-10: [hot signals — active emergency, high-value job, ready to book]
- 5-7: [warm — needs service soon, comparing quotes]
- 1-4: [cold — spam, wrong number, just browsing]

### Step 5: Supabase Schema

Two tables per industry:

**`[industry]_standard_agent`** — client config:
```sql
CREATE TABLE [industry]_standard_agent (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id TEXT UNIQUE NOT NULL,
  company_name TEXT, agent_name TEXT, business_phone TEXT,
  notification_email TEXT, notification_email_2 TEXT, notification_email_3 TEXT,
  notification_sms TEXT, notification_sms_2 TEXT, notification_sms_3 TEXT,
  transfer_number TEXT, service_area TEXT, business_hours TEXT,
  services_offered TEXT, emergency_protocol TEXT,
  plan TEXT DEFAULT 'standard', status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**`[industry]_call_log`** — call records:
```sql
CREATE TABLE [industry]_call_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id TEXT REFERENCES [industry]_standard_agent(agent_id),
  call_id TEXT, caller_name TEXT, caller_phone TEXT, caller_address TEXT,
  service_type TEXT, job_type TEXT, urgency TEXT,
  is_lead BOOLEAN, lead_score INTEGER,
  call_summary TEXT, call_duration TEXT, call_tier TEXT,
  vulnerable_occupant BOOLEAN, caller_sentiment TEXT,
  geocode_status TEXT, geocode_formatted TEXT,
  notification_sent BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### Step 6: n8n Workflow Pattern

**Onboarding Workflow** (triggered by Jotform webhook):
1. Jotform Webhook Trigger → `/webhook/[industry]-onboarding`
2. Parse Jotform Data (Code node)
3. Save to Supabase `[industry]_standard_agent`
4. Build Retell Prompt (Code node — reads industry prompt template)
5. Create Retell Conversation Flow (HTTP node → Retell API)
6. Build Agent Payload (Code node)
7. Create Retell Agent (HTTP node → Retell API)
8. Extract Agent ID
9. Publish Agent (HTTP node → Retell publish endpoint)
10. Update Supabase with agent_id
11. Send "You're Live" Email (Code node — uses approved template)
12. Send Internal Notification

**Call Processor** (triggered by Retell webhook):
1. Retell Webhook → `/webhook/[industry]-call-processor`
2. Filter: call_analyzed only
3. Extract Call Data
4. Supabase: Lookup Client by agent_id
5. Parse Client Data
6. GPT: Analyze Transcript (industry-specific scoring)
7. Parse Lead Data
8. Is Lead? (IF node)
9. Supabase: Log Call
10. Route Notifications (Code node — builds branded email)
11. Send Client Email (Code node — SMTP2GO)
12. Internal Notification

### Step 7: Jotform Configuration

Standard form fields (adapt per industry):
- Company Name, Contact Name, Email, Phone
- Business Address, Service Area
- Agent Name preference, Agent Voice preference
- Services Offered (checkboxes — industry-specific)
- Business Hours
- Emergency Protocol (what counts as emergency)
- Transfer Number (for live transfers)
- Additional notification emails (up to 3)
- Special instructions

Premium form adds:
- CRM Platform (HubSpot, GoHighLevel, Zoho, Jobber, Housecall Pro, ServiceTitan, None)
- Calendar Platform (Google Calendar, Outlook, Calendly, Cal.com, Acuity, None)
- Dispatch preferences

### Step 8: Email Templates

Use the approved templates in `marketing/emails/templates/`:
- `stripe-welcome.js` — post-purchase (works for all industries, plan-aware)
- `youre-live.js` — agent live + QR codes + PDF (works for all, plan-aware)
- `call-alert.js` — call notification (works for all, Premium appointment block)
- `usage-alert.js` — minute threshold warnings ($0.25/min overage)

All templates use dynamic variables — no hardcoded names, phones, or companies.
PDF attachment: `brand-assets/syntharra-call-forwarding-guide.pdf` (dynamically generated per client phone number in production)

### Step 9: Retell API Reference

**Create Conversation Flow:**
```
POST https://api.retellai.com/create-retell-llm
Authorization: Bearer {{RETELL_API_KEY}}
```

**Create Agent:**
```
POST https://api.retellai.com/create-agent
Authorization: Bearer {{RETELL_API_KEY}}
```

**Publish Agent (CRITICAL — always call after any update):**
```
POST https://api.retellai.com/publish-agent/{{agent_id}}
Authorization: Bearer {{RETELL_API_KEY}}
```

**NEVER delete or recreate an agent.** Agent ID is the foreign key across Retell, Supabase, n8n, and phone assignment. Always patch in place.

## Output Checklist

Before declaring complete:
- [ ] Conversation flow JSON has all 12 nodes
- [ ] Prompt uses commas not dashes, has {{agent_name}}, {{company_name}}, {{COMPANY_INFO_BLOCK}}
- [ ] GPT scoring prompt has industry-specific hot/warm/cold signals
- [ ] Supabase schema matches the standard column set
- [ ] Jotform fields documented with industry-specific services
- [ ] Email templates use approved branding (check brand-assets/BRAND-SPEC.md)
- [ ] n8n workflow JSON is valid, all nodes connected
- [ ] Setup guide covers: Jotform creation, n8n import, Supabase tables, Retell setup, email config

## Industry Reference Files

- `references/hvac.md` — HVAC services, emergency signals, seasonal notes
- `references/plumbing.md` — Plumbing services, emergency signals
- `references/electrical.md` — Electrical services, safety protocols
- `references/cleaning.md` — Cleaning services, residential vs commercial
- `references/generic-service.md` — Template for any service industry

To add a new industry: create `references/[industry].md` with service list, emergency scenarios, lead signals, seasonal notes, and common call types.
