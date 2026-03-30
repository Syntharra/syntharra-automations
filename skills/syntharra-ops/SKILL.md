---
name: syntharra-ops
description: >
  Complete reference for Syntharra day-to-day operations: the ops monitor, scenario testing,
  nightly backups, email signatures, brand assets, admin dashboard, and session/handoff rules.
  ALWAYS load this skill when: working on the ops monitor, running or building scenario tests,
  checking system health, generating session logs or updating project-state.md, working with
  the admin dashboard, applying or updating email signatures, accessing brand assets, managing
  the E2E test pipeline, or handling any operational/maintenance task that spans multiple systems.
---

---

## Session Rules (CRITICAL — Every Chat)

At the **START** of every chat, fetch and read:
1. `Syntharra/syntharra-automations/docs/project-state.md`
2. `Syntharra/syntharra-website/CLAUDE.md`

At the **END** of every chat that changes anything:
1. Update `project-state.md` with what changed
2. Push a session log to `docs/session-logs/` (what changed and why)
3. Push all changes to GitHub before chat ends

---

## GitHub Push (Python pattern)

```python
import requests, base64, json

TOKEN = "{{GITHUB_TOKEN}}"
headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}

def push_file(repo, path, content_str, commit_msg):
    url = f"https://api.github.com/repos/Syntharra/{repo}/contents/{path}"
    r = requests.get(url, headers=headers).json()
    sha = r.get("sha")  # None if new file
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content_str.encode()).decode()
    }
    if sha:
        payload["sha"] = sha
    requests.put(url, headers=headers, data=json.dumps(payload))
```

**Never commit raw token strings to GitHub** — replace with placeholder variables before pushing. GitHub secret scanning will block the push.

---

## Ops Monitor

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-ops-monitor` |
| URL | `syntharra-ops-monitor-production.up.railway.app` |
| Railway service ID | `7ce0f943-5216-4a16-8aeb-794cc7cc1e65` |
| Status | **PAUSED** (2026-03-30 — stop test-mode alert spam) |

### Monitor Systems (10 total, 70+ checks)
1. Retell — agent health
2. n8n — workflow execution errors
3. Supabase — table accessibility
4. Stripe — webhook, product validity
5. Jotform — form accessibility
6. Pipeline (E2E) — full onboarding path
7. CRM/Calendar — Google Cal, Jobber
8. Infrastructure — Railway services, DNS, webhooks
9. Client Health — per-client agent status
10. Revenue — billing cycles, overages

### Alert Channels
- Email: SMTP2GO REST API (not nodemailer — Railway blocks SMTP ports)
- SMS: Telnyx
- Daily digest: 8am CT

### Key Ops Monitor Learnings
- **Never POST to webhooks for health checks** — always HEAD. POST triggers real n8n execution.
- `is_published` on Retell agents is NOT a health indicator — agents work immediately after creation
- alertManager crash pattern: if alertManager throws on startup, entire monitor silently returns null
- Railway build cache: env var changes don't always trigger redeploy — sometimes need a new git commit

To unpause ops monitor:
```
POST https://backboard.railway.com/graphql/v2
Authorization: Bearer {{RAILWAY_TOKEN}}
mutation { sleepApplication(serviceId: "7ce0f943-5216-4a16-8aeb-794cc7cc1e65", sleep: false) }
```

---

## Admin Dashboard

- Live at `syntharra.com/dashboard.html?agent_id=X` (also accessible at root dashboard URL)
- Password gate: code `syntharra2024`
- Features: KPI cards (6), system cards by priority, live clock, countdown progress bar
- AI Assistant: Claude-powered, has live Syntharra context
- Card order: Clients → Pipeline → Retell → n8n → Supabase → Stripe → etc.
- Wired to live Supabase data
- Latest SHA: `d753064c`

---

## Scenario Testing

| Workflow | ID |
|---|---|
| Scenario Runner v4 | `94QmMVGdEDl2S9MF` |
| Scenario Transcript Gen | `dHO8O0QHBZJyzytn` |
| Scenario Process Single | `rlf1dHVcTlzUbPX7` |

- E2E skill: `skills/e2e-test/SKILL.md` in `syntharra-automations`
- E2E cleanup workflow: `URbQPNQP26OIdYMo` (webhook: `/e2e-test-cleanup`, 5-min delay)
- Scenario test reports → `admin@syntharra.com`

---

## Nightly GitHub Backup

- Workflow: `EAHgqAfQoCDumvPU`
- Backs up all n8n workflows to `syntharra-automations` repo nightly

---

## Email Signatures

All 7 branded HTML signatures in `syntharra-automations/brand-assets/email-signature/`:

| File | Name | Role |
|---|---|---|
| `syntharra-signature-PASTE-THIS.html` | Daniel Blackmore | Founder & CEO |
| `syntharra-signature-support.html` | Syntharra Support | Customer Support |
| `syntharra-signature-admin.html` | Syntharra Admin | Administration |
| `syntharra-signature-onboarding.html` | Syntharra Onboarding | Client Onboarding |
| `syntharra-signature-feedback.html` | Syntharra Feedback | Feedback & Enquiries |
| `syntharra-signature-careers.html` | Syntharra Careers | Careers & Opportunities |
| `syntharra-signature-info.html` | Syntharra Info | General Enquiries |

**To apply:** Open HTML file in Chrome → Select All → Copy → Paste into Gmail signature settings for that alias.
- Outlook version: `syntharra-signature-outlook.html`
- Phone placeholder: `+1 (000) 000-0000` (update when Telnyx number obtained)

---

## Brand Assets

Location: `syntharra-automations/brand-assets/`

| Asset | Location |
|---|---|
| Logo icon (email) | `https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png` |
| Logo swapped v2 (invoices) | `syntharra-logo-swapped-v2.png` — bars purple, "Syntharra" black, "AI SOLUTIONS" purple |
| Favicon (purple) | `syntharra-website/favicon.svg` |
| Favicon (white) | `syntharra-website/favicon-white.svg` |
| Email signatures | `brand-assets/email-signature/` |
| Discount codes doc | `docs/discount-codes.md` |

### Logo Variants
- Default: bars purple, "Syntharra" purple, "AI SOLUTIONS" black
- Swapped v2 (for invoices): bars purple, "Syntharra" black, "AI SOLUTIONS" purple
- NEVER use emoji as substitute for logo

---

## Discount Codes Reference

Full doc: `syntharra-automations/docs/discount-codes.md`

| Code | Discount | Use Case |
|---|---|---|
| `FOUNDING-STANDARD` | $1,499 off once | Waives Standard setup fee |
| `FOUNDING-PREMIUM` | $2,499 off once | Waives Premium setup fee |
| `CLOSER-250` | $250 off once | Sales closer discount |
| `CLOSER-500` | $500 off once | Sales closer discount |
| `CLOSER-750` | $750 off once | Sales closer discount |
| `CLOSER-1000` | $1,000 off once | Sales closer discount |

---

## Key Operational Rules

1. **Never delete or recreate a Retell agent** — always patch in place
2. **Always publish after Retell API updates** — `POST /publish-agent/{agent_id}`
3. **After any n8n edits, click Publish** to make active version live
4. **GitHub secret scanning** blocks raw tokens — always use placeholder variables before pushing
5. **n8n PUT workflow** requires only `name`, `nodes`, `connections`, `settings.executionOrder`
6. **Gmail mobile dark mode** auto-converts light-theme emails — this is correct behaviour, not a bug
7. **Base64 SVG images break in Gmail mobile** — always use hosted PNG URLs
8. **WhatsApp Business rejects VoIP numbers** — need real SIM
9. **Avoid over-engineering** support tooling before clients exist
10. **Hamburger menu:** NEVER build from scratch — always copy from existing page
11. **Agent prompts:** always use commas instead of dashes
12. **`daniel@syntharra.com` must never appear** in workflows or on the website
13. **`invoice_creation`** is incompatible with `mode: 'subscription'` in Stripe — subscriptions auto-create invoices

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
