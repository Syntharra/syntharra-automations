---
name: syntharra-email
description: >
  Complete reference for all Syntharra email work — templates, SMTP2GO, address routing,
  email signatures, and the approved logo block.
  ALWAYS load this skill when: building or editing any n8n email node, creating an email template,
  designing a welcome email, weekly report, onboarding email, or any automated email; checking
  which email address to use for a given context; applying or updating an email signature;
  troubleshooting email delivery; or ensuring brand compliance on any outbound email.
  This skill is the single source of truth for all Syntharra email standards.
---

# Syntharra — Email Reference

---

## SMTP2GO

| Item | Value |
|---|---|
| API Key | query `syntharra_vault` → `service_name = 'smtp2go'` |
| n8n credential name | `"SMTP2GO - Syntharra"` |
| REST endpoint | `POST https://api.smtp2go.com/v3/email/send` |
| Sender address | `noreply@syntharra.com` |

**On Railway:** NEVER use nodemailer/SMTP — Railway blocks all SMTP ports (25, 465, 587, 2525). Always use SMTP2GO REST API over HTTPS port 443.

---

## Email Address Routing

| Address | Purpose | Used In |
|---|---|---|
| `noreply@syntharra.com` | All automated outbound sender | Every n8n email node |
| `support@syntharra.com` | Customer-facing support | Website footer, FAQ, billing emails, legal pages |
| `onboarding@syntharra.com` | Internal onboarding notifications | Stripe workflow, HVAC Std Onboarding, HVAC Prem Onboarding |
| `admin@syntharra.com` | Internal ops notifications | Call processor, scenario test reports, contract notices |
| `alerts@syntharra.com` | Ops & system alerts, internal monitoring | Ops monitor, Railway alerts, infrastructure notifications |
| `feedback@syntharra.com` | Customer feedback | Website footer |
| `careers@syntharra.com` | Job applications | Careers page |
| `info@syntharra.com` | General public enquiries | Google Workspace footer |
| `sales@syntharra.com` | Sales enquiries | Available for outreach |
| `daniel@syntharra.com` | **NEVER** use in any workflow, template, or website |  |

### Per-Workflow Routing
| Workflow | Internal → | Customer contact ref |
|---|---|---|
| HVAC Std Onboarding `4Hx7aRdzMl5N0uJP` | `onboarding@` | `support@` |
| HVAC Prem Onboarding `kz1VmwNccunRMEaF` | `onboarding@` | `support@` |
| Stripe Workflow `xKD3ny6kfHL0HHXq` | `onboarding@` | `support@` |
| HVAC Std Call Processor `Kg576YtPM9yEacKn` | `admin@` | — |
| HVAC Prem Call Processor `STQ4Gt3rH8ptlvMi` | `admin@` | `support@` |
| Scenario Runner `Ex90zUMSEWwVk4Wv` | `admin@` | — |
| Usage Alert Monitor `Wa3pHRMwSjbZHqMC` | `admin@` | `support@` |
| Monthly Minutes Calculator `z1DNTjvTDAkExsX8` | — | `support@` |

---

## Brand Rules — MANDATORY

- **ALWAYS light theme** — white `#fff` cards, grey `#F7F7FB` outer bg, dark text `#1A1A2E`, purple `#6C63FF` accents
- **NEVER dark-theme emails** — let the client's email app handle dark mode adaptation
- **NEVER base64 SVG images** — they break in Gmail mobile. Always use hosted PNG URLs
- **NEVER flat PNG for logo** — always use the approved logo HTML block below
- **NEVER `daniel@syntharra.com`** in any email body, template, or workflow

### Colour Tokens for Email
```
Background (outer):  #F7F7FB
Card background:     #FFFFFF
Text primary:        #1A1A2E
Text secondary:      #4A4A6A
Accent / CTA:        #6C63FF
Border:              #E5E7EB
```

---

## Approved Logo Block

Use this in the header of **every** email template. Never substitute a flat PNG or emoji.

```javascript
const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
```

Inject into email:
```html
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
```

---

## Email Flows by Plan

### Standard (3 emails)
1. **Stripe welcome** — triggered by `checkout.session.completed` via Stripe Workflow `xKD3ny6kfHL0HHXq`
2. **You're Live + PDF** — sent after agent is provisioned
3. **Weekly report** — ongoing, every Sunday 6pm per client timezone

### Premium (4 emails)
1. **Stripe welcome** — same as Standard
2. **Integration setup** — Premium-only, covers Google Calendar + Jobber OAuth steps
3. **You're Live + PDF** — sent after agent and integrations are live
4. **Weekly report** — ongoing

---

## Standard Email Template Structure

```html
<!-- Outer wrapper -->
<div style="background:#F7F7FB;padding:40px 20px;font-family:Inter,-apple-system,sans-serif;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:16px;border:1px solid #E5E7EB;overflow:hidden;">
    
    <!-- Header / Logo -->
    <div style="padding:32px 40px 0;text-align:center;">
      <!-- LOGO BLOCK HERE -->
    </div>

    <!-- Body -->
    <div style="padding:32px 40px;">
      <h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 16px;">Heading</h1>
      <p style="color:#4A4A6A;font-size:15px;line-height:1.6;margin:0 0 24px;">Body text</p>
      
      <!-- CTA Button -->
      <a href="#" style="display:inline-block;background:#6C63FF;color:#fff;font-weight:600;font-size:15px;padding:14px 28px;border-radius:10px;text-decoration:none;">CTA Text</a>
    </div>

    <!-- Footer -->
    <div style="padding:24px 40px;border-top:1px solid #E5E7EB;text-align:center;">
      <p style="color:#8A8AA0;font-size:12px;margin:0;">
        Questions? <a href="mailto:support@syntharra.com" style="color:#6C63FF;">support@syntharra.com</a>
      </p>
    </div>

  </div>
</div>
```

---

## Email Signatures

All 7 branded HTML signatures in `syntharra-automations/brand-assets/email-signature/`:

| File | Alias | Role |
|---|---|---|
| `syntharra-signature-PASTE-THIS.html` | Daniel Blackmore | Founder & CEO |
| `syntharra-signature-support.html` | Syntharra Support | Customer Support |
| `syntharra-signature-admin.html` | Syntharra Admin | Administration |
| `syntharra-signature-alerts.html` | Syntharra Alerts | System Alerts & Notifications |
| `syntharra-signature-onboarding.html` | Syntharra Onboarding | Client Onboarding |
| `syntharra-signature-feedback.html` | Syntharra Feedback | Feedback & Enquiries |
| `syntharra-signature-careers.html` | Syntharra Careers | Careers & Opportunities |
| `syntharra-signature-info.html` | Syntharra Info | General Enquiries |
| `syntharra-signature-outlook.html` | Daniel Blackmore | Outlook desktop version |

**To apply:** Open HTML in Chrome → Select All → Copy → Paste into Gmail signature settings for that alias.

---

## Google Workspace Footer

Appended automatically to all outgoing `@syntharra.com` emails:
```
Syntharra | Global AI Solutions | www.syntharra.com | info@syntharra.com
```

---

---

## 🔑 Syntharra Vault — Credential Access

ALL Syntharra API keys and secrets are stored in the Supabase table `syntharra_vault`.

- **Project URL:** `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- **Table:** `syntharra_vault`
- **Query by:** `service_name` + `key_type` fields → retrieve `key_value`
- **Auth:** Supabase service role key — stored in vault as `service_name = 'Supabase'`, `key_type = 'service_role_key'`
- **NEVER** store keys in skill files, session logs, GitHub, or project memory

### REST Lookup Pattern
```
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&key_type=eq.{KEY_TYPE}&select=key_value
Headers:
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
```

### JavaScript Lookup Pattern (n8n / Node.js)
```javascript
async function getVaultKey(serviceName, keyType) {
  const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.${serviceName}&key_type=eq.${keyType}&select=key_value`,
    { headers: { apikey: SERVICE_ROLE_KEY, Authorization: `Bearer ${SERVICE_ROLE_KEY}` } }
  );
  const data = await res.json();
  return data[0]?.key_value;
}

// Examples:
const retellKey    = await getVaultKey('Retell AI', 'api_key');
const n8nUrl       = await getVaultKey('n8n Railway', 'instance_url');
const stripeMonthly = await getVaultKey('Stripe', 'price_standard_monthly');
```

### Known service_name / key_type Values

| service_name | key_type | What it is |
|---|---|---|
| `n8n Railway` | `instance_url` | `https://n8n.syntharra.com` |
| `n8n Railway` | `api_key` | n8n Railway API key |
| `Retell AI` | `api_key` | Retell API key |
| `Retell AI` | `agent_id_arctic_breeze` | Test HVAC agent ID |
| `Retell AI` | `agent_id_demo_jake` | Demo agent Jake |
| `Retell AI` | `agent_id_demo_sophie` | Demo agent Sophie |
| `Retell AI` | `conversation_flow_id` | Live conversation flow |
| `Retell AI` | `phone_number` | Arctic Breeze phone |
| `Supabase` | `project_url` | Supabase project URL |
| `Supabase` | `service_role_key` | Full admin key |
| `GitHub` | `personal_access_token` | GitHub PAT |
| `Stripe` | `product_id_standard` | Standard product ID |
| `Stripe` | `product_id_premium` | Premium product ID |
| `Stripe` | `price_standard_monthly` | $497/mo price ID |
| `Stripe` | `price_standard_annual` | $414/mo price ID |
| `Stripe` | `price_standard_setup` | $1,499 setup price ID |
| `Stripe` | `price_premium_monthly` | $997/mo price ID |
| `Stripe` | `price_premium_annual` | $831/mo price ID |
| `Stripe` | `price_premium_setup` | $2,499 setup price ID |
| `Stripe` | `coupon_founding_standard` | FOUNDING-STANDARD coupon |
| `Stripe` | `coupon_founding_premium` | FOUNDING-PREMIUM coupon |
| `Stripe` | `webhook_url` | Stripe webhook URL |
| `Stripe` | `webhook_id` | Stripe webhook ID |
| `Jotform` | `api_key` | Jotform API key |
| `Jotform` | `form_id_standard` | Standard onboarding form ID |
| `Jotform` | `form_id_premium` | Premium onboarding form ID |
| `Jotform` | `webhook_standard_new` | Railway n8n webhook URL |
| `SMTP2GO` | `api_key` | SMTP2GO API key |
| `Railway` | `api_token` | Railway API token |
| `Railway` | `project_id` | Syntharra project ID |
| `Railway` | `service_id_n8n` | n8n service ID |
| `Railway` | `service_id_checkout` | Checkout service ID |
| `Railway` | `service_id_ops_monitor` | Ops monitor service ID |

---

## 🔄 Auto-Update Rule

Only update this skill when something **fundamental** changes — not during routine work:
- ✅ New email address created → add to routing table
- ✅ New automated email added to a plan's flow → update email flows section
- ✅ Logo block URL changes → update immediately
- ✅ SMTP2GO replaced with another provider → update credentials + patterns
- ✅ New email template established as a standard → add structure to this skill
- ✅ New email signature created → add to signatures table
- ❌ Do NOT update for individual email copy changes, subject line tweaks, or one-off sends
