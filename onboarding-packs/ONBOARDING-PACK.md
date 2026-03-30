# Syntharra — Client Onboarding Pack

**Version:** 1.0  
**Created:** 2026-03-30  
**Location:** `syntharra-automations/onboarding-packs/`

---

## Overview

The Onboarding Pack is a rich HTML email sent to clients when their AI Receptionist goes live. It covers everything they need to get started: their agent details, call forwarding instructions, how calls are handled, FAQs, and a dashboard link.

Two versions exist — **Standard** and **Premium**. The Premium version includes integration status, repeat caller details, and a WhatsApp support block (commented out until the number is configured).

---

## Files

| File | Description |
|---|---|
| `onboarding-pack-standard.html` | Standalone Standard email template (preview/design reference) |
| `onboarding-pack-premium.html` | Standalone Premium email template (preview/design reference) |
| `n8n-onboarding-pack-standard.json` | n8n Code node + HTTP node for Standard workflow |
| `ONBOARDING-PACK.md` | This documentation |

---

## Email Design

Both templates follow Syntharra brand standards:

| Token | Value |
|---|---|
| Background (outer) | `#F7F7FB` |
| Card background | `#FFFFFF` |
| Text primary | `#1A1A2E` |
| Text secondary | `#4A4A6A` |
| Accent / CTA | `#6C63FF` |
| Cyan accent | `#00D4FF` |
| Border | `#E5E7EB` |

---

## Template Sections

### Standard Onboarding Pack

1. **Header** — Purple gradient, plan badge ("Standard Plan · Active"), company welcome
2. **Stats strip** — 24/7 · 475 min/mo · <2s answer time
3. **AI Receptionist Details** — agent name, AI phone number, plan, live transfer number
4. **Call Forwarding Instructions** — iPhone, Android, Universal USSD code (*72)
5. **How Calls Work** — 4-step numbered flow
6. **FAQs** — 4 common questions (missed calls, live transfer, unknown queries, minutes)
7. **Dashboard CTA** — link to `syntharra.com/dashboard.html?agent_id={{agent_id}}`
8. **Quick Start Checklist** — 4 tick-off items
9. **Support strip** — dark footer with `support@syntharra.com`

### Premium Onboarding Pack (superset of Standard)

All Standard sections, plus:

1. **Header** — Dark luxury gradient, "Premium Plan · Active" badge with gradient border
2. **Stats strip** — 4 columns: 24/7 · 1,000 min/mo · Smart Booking · Full Integration
3. **Integration Block** — dark card showing Google Calendar + CRM integration status
4. **WhatsApp Support Block** — **COMMENTED OUT** — install now, activate when number is ready
5. **Enhanced FAQs** — includes repeat caller recognition, integration authorisation steps

---

## Dynamic Variables

### Standard

| Variable | Source | Example |
|---|---|---|
| `{{company_name}}` | Jotform / Supabase | `Arctic Breeze HVAC` |
| `{{first_name}}` | Jotform | `Mike` |
| `{{agent_name}}` | Supabase `hvac_standard_agent.agent_name` | `Alex` |
| `{{ai_phone_number}}` | Supabase / Retell | `+1 (812) 994-4371` |
| `{{ai_phone_number_digits}}` | Derived (digits only) | `18129944371` |
| `{{transfer_phone_number}}` | Supabase | `+1 (856) 363-0633` |
| `{{notification_email}}` | Supabase | `owner@arcticbreezehvac.com` |
| `{{agent_id}}` | Supabase | `agent_4afbfdb3fcb1ba9569353af28d` |

### Premium (additional)

| Variable | Source | Example |
|---|---|---|
| `{{crm_platform}}` | Supabase `crm_platform` | `Jobber` |
| `{{crm_status}}` | Supabase `crm_status` | `Active` or `Pending` |
| `{{calendar_status}}` | Supabase `calendar_status` | `Active` or `Pending` |

---

## Where to Wire in n8n

### Standard
- **Workflow:** HVAC Std Onboarding (`4Hx7aRdzMl5N0uJP`)
- **Trigger:** Wire after "You Are Live" confirmation step, or as a standalone step just before closing the onboarding sequence
- **Nodes to add:** 
  1. `Build Standard Onboarding Pack HTML` (Code node — builds the HTML)
  2. `Send Onboarding Pack (Standard)` (HTTP Request → SMTP2GO REST API)

### Premium
- **Workflow:** HVAC Prem Onboarding (`kz1VmwNccunRMEaF`)
- **Position:** Email 3 of 4 — after Integration Setup, before weekly reports begin
- Same pattern: Code node builds HTML → HTTP Request sends via SMTP2GO

---

## SMTP2GO Send Pattern

```javascript
// n8n HTTP Request node body (JSON)
{
  "api_key": "{{SMTP2GO_API_KEY from vault}}",
  "to": [{ "email": "{{notification_email}}", "name": "{{company_name}}" }],
  "sender": "Syntharra <noreply@syntharra.com>",
  "subject": "Your AI Receptionist is Live — Onboarding Pack 📋",
  "html_body": "{{onboarding_pack_html from Code node}}"
}
```

Subject lines:
- **Standard:** `Your AI Receptionist is Live — Onboarding Pack 📋`
- **Premium:** `Your Premium AI Receptionist is Live — Onboarding Pack 📋`

---

## WhatsApp Support Block (Premium Only)

The WhatsApp block is **fully built but commented out** in `onboarding-pack-premium.html`.

When the WhatsApp number is ready:
1. Open `onboarding-pack-premium.html`
2. Find the comment block: `<!-- WHATSAPP SUPPORT BLOCK — INSTALL NOW, CONFIGURE LATER -->`
3. Uncomment the block
4. Replace `{{WHATSAPP_NUMBER}}` with the live number (digits only, including country code, e.g. `353851234567`)
5. Update the Code node in the Premium n8n workflow with the same change
6. Push to GitHub and update `project-state.md`

The block includes:
- Green WhatsApp-branded card
- "Message on WhatsApp" button → `https://wa.me/{{WHATSAPP_NUMBER}}`
- "Add to Contacts" button → pre-filled WhatsApp link
- Support number display
- Note: "Typically responds within 2 hours"

---

## Call Forwarding Instructions Summary (in email)

The email covers three methods:

1. **iPhone** — Settings → Phone → Call Forwarding → ON → enter AI number
2. **Android** — Phone app → ⋮ Settings → Calls → Call Forwarding → Always Forward
3. **Universal USSD** — Dial `*72{ai_phone_digits}` from any phone · Cancel: dial `*73`
4. **VoIP tip** — Contact provider to set unconditional forwarding

---

## Checklist — Before Activating

- [ ] SMTP2GO key confirmed in `syntharra_vault` (`service_name='smtp2go'`, `key_type='api_key'`)
- [ ] All Supabase variable fields populated for client record
- [ ] Code node tested with sample data — confirm no rendering errors
- [ ] Test send to internal address before first live client
- [ ] Premium: WhatsApp block commented out (confirmed)
- [ ] Premium: integration status variables (`crm_status`, `calendar_status`) populate correctly

---

## Email Flow Position

```
Standard (3 emails):
  1. Stripe Welcome Email  ← existing
  2. Onboarding Pack       ← THIS EMAIL (wire after agent provisioned)
  3. Weekly Report         ← existing (starts following Sunday)

Premium (4 emails):
  1. Stripe Welcome Email      ← existing
  2. Integration Setup Email   ← existing
  3. Onboarding Pack           ← THIS EMAIL (wire after integrations live)
  4. Weekly Report             ← existing
```

---

*Last updated: 2026-03-30*
