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

## 🔄 Auto-Update Rule

Only update this skill when something **fundamental** changes — not during routine work:
- ✅ New email address created → add to routing table
- ✅ New automated email added to a plan's flow → update email flows section
- ✅ Logo block URL changes → update immediately
- ✅ SMTP2GO replaced with another provider → update credentials + patterns
- ✅ New email template established as a standard → add structure to this skill
- ✅ New email signature created → add to signatures table
- ❌ Do NOT update for individual email copy changes, subject line tweaks, or one-off sends
