---
name: syntharra-website
description: >
  Complete reference for all work on the Syntharra website (syntharra.com).
  ALWAYS load this skill when: editing any HTML page on syntharra.com, adding pages, fixing styling,
  updating the nav/menu, writing blog articles, creating landing pages, working on SEO, updating
  the demo page, the checkout page, the dashboard, or any file in the Syntharra/syntharra-website
  GitHub repo. Also trigger for any task involving brand colours, logo usage, typography,
  email template design, or UI patterns used across Syntharra's web presence.
---

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

---

## GitHub Repo

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-website` |
| Branch | `main` |
| Hosting | GitHub Pages → syntharra.com |
| Token | `{{GITHUB_TOKEN}}` |

---

## Edit Workflow — MANDATORY SEQUENCE

1. **Fetch** the page from GitHub API → get SHA + base64 content
2. **Decode** content, edit using Python `str.replace()` — never shell curl for large files
3. **Verify** exactly ONE `<style>` block: `assert content.count('<style>') == 1`
4. **Push** back via GitHub API PUT with the original SHA

```python
# Fetch
import requests, base64
TOKEN = "{{GITHUB_TOKEN}}"
headers = {"Authorization": f"token {TOKEN}"}
r = requests.get(f"https://api.github.com/repos/Syntharra/syntharra-website/contents/{filename}", headers=headers)
data = r.json()
sha = data["sha"]
content = base64.b64decode(data["content"]).decode()

# Edit
content = content.replace("OLD_STRING", "NEW_STRING")

# Verify
assert content.count("<style>") == 1, "Multiple style blocks detected!"

# Push
import json
payload = {"message": "commit message", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
requests.put(f"https://api.github.com/repos/Syntharra/syntharra-website/contents/{filename}", headers=headers, data=json.dumps(payload))
```

---

## Critical CSS Rules

- **NEVER** `overflow: hidden` on html/body — use `overflow-x: clip`
- Use `100dvh` for video sections (not `100vh`)
- Video background filter: `contrast(1.2) brightness(0.85) saturate(1.3) sepia(0.25) hue-rotate(-15deg)`
- Dark panel overlay: `linear-gradient(to bottom, rgba(0,0,0,0) 35%, rgba(4,4,14,0.97) 100%)`

---

## Brand Tokens

```css
--primary:        #6C63FF;
--secondary:      #00D4FF;
--gradient:       linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%);
--background:     #FAFAFA;
--surface:        #FFFFFF;
--text-primary:   #1A1A2E;
--text-secondary: #4A4A6A;
--text-tertiary:  #8A8AA0;
--border:         #E5E7EB;
--dark-section:   linear-gradient(135deg, #0d0d1a, #1a1a3e);
```

Font: Inter (Google Fonts)
Logo: 4 ascending vertical bars, rounded corners, flat `#6C63FF`
Favicon: `favicon.svg` (purple), `favicon-white.svg` (white on dark)

---

## Design Patterns

### Cards
```css
background: #fff; border-radius: 20px; border: 1px solid var(--border);
/* Hover */ border-color: rgba(108,99,255,0.25); box-shadow: 0 8px 32px rgba(108,99,255,0.06);
/* Featured */ /* ::before violet gradient 4px top strip */
```

### Buttons
- Primary: `background: var(--gradient); color: white; border-radius: 10px; font-weight: 600`
- Outline: `border: 1.5px solid #6C63FF; color: #6C63FF`
- CTA dark section outline: `color: #fff !important; border-color: rgba(255,255,255,0.3)`

### Pills / Tags
`font-size: 11-12px; font-weight: 600; color: #6C63FF; background: rgba(108,99,255,0.08); border-radius: 20px; padding: 5px 14px`

### CTA Blocks
Dark gradient `linear-gradient(135deg, #0d0d1a, #1a1a3e)`, white heading, 60% white description, primary + outline buttons

### Testimonials / Blockquotes
Left border `3px solid #6C63FF`, background `rgba(108,99,255,0.03)`, right radius `0 10px 10px 0`

### Disclaimers
`font-style: italic; font-size: 11px; color: var(--text-tertiary); text-align: center`

---

## Page Structure (every page)

1. `<head>` — meta, Google Fonts, ONE `<style>` block
2. `<header>` — fixed, blurred bg, logo + nav + hamburger
3. `.menu-backdrop` + `.menu-panel` — 300px slide-out (copy from existing page, NEVER rebuild)
4. Page content
5. `<footer>` — dark bg, 4-column grid, copyright
6. `<script>` — menu JS only

---

## Canonical Hamburger Menu

**CRITICAL:** ALWAYS copy from existing page. NEVER build from scratch. When adding a new item, update ALL pages via script.

Sections:
- **Product:** Solutions, How It Works, Demo, FAQ, AI Readiness Score, Revenue Calculator
- **Learn:** Case Studies, Blog, Why AI Wins
- **Industries:** HVAC, Plumbing, Electrical
- **Company:** About, Affiliate Program, Careers, System Status
- **CTA:** Book a Call

---

## Email Templates (Light Theme — MANDATORY)

ALL Syntharra emails: white `#fff` cards, grey `#F7F7FB` outer bg, dark text `#1A1A2E`, purple `#6C63FF` accents.
**NEVER dark-theme emails** — let client email apps handle dark mode.

### Approved Logo Block (use in ALL email templates)
```javascript
const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
```
Inject: `<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>`
**NEVER** use flat PNG images for email logo — always use the hosted PNG via the table block above.
**Base64 SVG images break in Gmail mobile** — always use hosted PNG URLs.

---

## Email Addresses (Website Placement)

| Address | Where |
|---|---|
| `support@syntharra.com` | Footer contact link (ALL pages), FAQ, legal pages, usage alerts |
| `feedback@syntharra.com` | Footer feedback link (ALL pages) |
| `careers@syntharra.com` | Careers page only |
| `admin@syntharra.com` | Service agreement (contract notices) |
| `daniel@syntharra.com` | **NEVER** on website or in any customer-facing content |

---

## Full File Map

| File | Purpose |
|---|---|
| `index.html` | Homepage |
| `demo.html` | Interactive AI demo |
| `case-studies.html` | Client results |
| `blog.html` | Blog index |
| `blog/*.html` | Individual articles (8 currently) |
| `affiliate.html` | Affiliate program + Supabase form |
| `careers.html` | Careers page |
| `status.html` | System status |
| `vs-answering-service.html` | Comparison page |
| `dashboard.html` | Client dashboard (`?agent_id=X`) |
| `ai-readiness.html` | AI readiness quiz (lead magnet) |
| `faq.html` | FAQ — 30+ questions, 6 categories, search |
| `how-it-works.html` | 5-step onboarding walkthrough |
| `about.html` | Company story, mission, values |
| `calculator.html` | Missed revenue calculator (lead magnet) |
| `plan-quiz.html` | "Which plan?" quiz (lead magnet) |
| `hvac.html` | HVAC industry landing page |
| `plumbing.html` | Plumbing industry landing page |
| `electrical.html` | Electrical industry landing page |
| `lp/hvac-answering-service.html` | Google Ads LP — HVAC (noindex, no nav) |
| `lp/plumbing-answering-service.html` | Google Ads LP — Plumbing |
| `lp/electrical-answering-service.html` | Google Ads LP — Electrical |
| `privacy.html` | Privacy policy |
| `terms.html` | Terms of service |
| `security.html` | Security page |
| `service-agreement.html` | Client service agreement |
| `favicon.svg` | Purple logo |
| `favicon-white.svg` | White logo (dark/gradient backgrounds) |
| `logo-icon-2x.png` | Logo icon (used in email templates) |
| `og-image.png` | Social share 1200×630 |
| `_template/page-builder.py` | Page builder function |
| `_template/TEMPLATE.md` | Page template docs |
| `_template/BLOG_STANDARD.md` | Blog article spec |

---

## Blog Articles

- Author: **Syntharra Team** | Role: "AI Solutions for Trade Businesses"
- Author logo: always `favicon-white.svg` — NEVER emoji
- Hero: gradient background + large emoji overlay + title
- Bottom CTA: dark gradient block with Book a Call + Demo buttons
- See `_template/BLOG_STANDARD.md` for full spec

---

## SEO & Lead Generation

- FAQPage schema on `faq.html`; Article schema on 11 blog posts; Service schema on 3 industry pages
- Content upgrades: 5 blog articles email-gate bonus content → Supabase `website_leads`
- Exit-intent popups: HVAC, Plumbing, Electrical, How It Works, Case Studies
- Google Ads LPs: `/lp/` directory, noindex, no nav, single CTA
- **Pricing is NOT public** — never show dollar amounts or link to pricing page

---

## Checkout Page

| Item | Value |
|---|---|
| URL | `checkout.syntharra.com` |
| Repo | `Syntharra/syntharra-checkout` (SEPARATE — never merge into automations) |
| Served from | `public/index.html` |
| Server | `server.js` — Express |
| Railway service ID | `e3df3e6d-6824-498f-bb4a-fdb6598f7638` |
| Railway env ID | `5303bcf8-43a4-4a95-8e0c-75909094e02e` |
| Fonts | DM Serif Display + DM Sans |
| Logo | Inline SVG (4 bars, `#6C63FF`) |

Railway does NOT auto-deploy on GitHub push — trigger manually via Railway API mutation or wait ~2-3 min.

---

## Outstanding Tasks (from CLAUDE.md)

- [ ] Wire blog subscribe → Supabase `website_leads` table
- [ ] Switch Stripe TEST → LIVE
- [ ] Write more SEO blog articles (follow `_template/BLOG_STANDARD.md`)
- [ ] Create `og-image.png` for social share

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

**Whenever you complete any task that touches this skill's domain, you MUST update this SKILL.md before the chat ends.**

This includes:
- New n8n workflow created or renamed → update the workflow table
- New Supabase table or column added → update the tables section
- New Jotform field added → update field mappings
- API key or credential changed → update the keys section
- New Retell agent created → update agent IDs
- Stripe product/price/coupon added or changed → update Stripe section
- New Railway service created → update infrastructure section
- New website page created → update file map
- Any webhook URL changed → update webhook URLs
- Any new learnings or gotchas discovered → add to key rules/learnings

**How:** At end of chat, fetch this file from GitHub, apply changes with `str.replace()`, push back.
**GitHub push function:** See `syntharra-ops` skill for the standard push pattern.

## CRM — HubSpot (active since 2026-04-03)
> HubSpot replaced the admin dashboard as Syntharra's CRM layer.
> Load `skills/syntharra-hubspot-SKILL.md` for full API reference.

- **All client records, deals, and sales pipeline live in HubSpot**
- **All marketing leads flow into HubSpot** (website form → Lead stage)
- **All paying clients auto-create in HubSpot** (Stripe → Paid Client stage)
- **All onboarded clients auto-update in HubSpot** (Jotform → Active stage)
- **All call activity is logged in HubSpot** (Retell post-call → contact note)
- Supabase remains operational source of truth for Retell agent config + call logs
- HubSpot is the sales, marketing, and client relationship layer
- API key: `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- Pipeline: "Syntharra Sales" — Lead → Demo Booked → Paid Client → Active

> Every website demo form submission fires the Website Lead n8n workflow which creates a HubSpot contact + deal at Lead stage, in addition to sending the AI readiness score email.
