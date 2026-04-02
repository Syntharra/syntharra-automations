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

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

---

## Session Rules (CRITICAL — Every Chat)

### START of every chat — fetch in this order:
1. `Syntharra/syntharra-automations/CLAUDE.md` — master brief, rules, skill map (always)
2. `Syntharra/syntharra-automations/docs/TASKS.md` — what's in progress, what's next (always)
3. Then load only the context files relevant to the task:
   - `docs/context/AGENTS.md` — Retell agent IDs, phones, Jotform
   - `docs/context/WORKFLOWS.md` — n8n workflow IDs
   - `docs/context/STRIPE.md` — price IDs, coupons
   - `docs/context/SUPABASE.md` — tables, columns
   - `docs/context/INFRA.md` — Railway, URLs, services
   - `docs/context/ARTIFACTS.md` — Claude artifact files
   - `docs/context/LAUNCH.md` — pre-launch checklist

**Why small files?** Each context file is ~40 lines / ~500 tokens.
Load only what you need. For a Retell-only task, fetch AGENTS.md only (~500 tokens).
Compare to loading all of project-state.md (~12,000 tokens) every time.

### END of every chat that changes anything:
1. Update `docs/TASKS.md` — what changed, what's next, what's blocked
2. Push all changes to GitHub before chat ends
3. **Update relevant skill(s)** — see Universal Skill-Update Rule below
4. Update any `docs/context/` file if IDs, URLs, or state changed

---

## 📚 Universal Skill-Update Rule (ALL Syntharra Work)

**Once any work is fully tested and verified, the relevant skill MUST be updated before the chat ends.**

This applies to every skill across the entire Syntharra stack. If you touched it, you update it.

### Which skill to update
| Area of work | Skill to update |
|---|---|
| Admin dashboard (`index.html`, `server.js`) | `syntharra-admin` |
| Client dashboard (`dashboard.html`) | `syntharra-client-dashboard` |
| Website pages (`syntharra.com`) | `syntharra-website` |
| Claude chat artifacts (dashboards, emails, sales) | `syntharra-artifacts` repo SKILL.md |
| n8n workflows, Railway, Supabase, infra | `syntharra-infrastructure` |
| Retell agents, prompts, conversation flows | `syntharra-retell` |
| HVAC Standard pipeline | `hvac-standard` |
| HVAC Premium pipeline | `hvac-premium` |
| Stripe, checkout server, billing | `syntharra-stripe` |
| Email templates, SMTP2GO | `syntharra-email` |
| Marketing, lead gen, VSL, demo page | `syntharra-marketing` |
| Ops monitor, session logs, brand assets | `syntharra-ops` (this file) |

### What to update in the skill
- **New SHA** after any file push → update SHA in the skill's repo table
- **New section/feature added** → document it (IDs, functions, behaviour)
- **Feature removed** → add to a "Removed" section so future sessions don't try to restore it
- **New gotcha or learning discovered** → add to Key Patterns / Key Learnings
- **Workflow ID changed** → update workflow tables
- **Credential or key changed** → update references (never store raw values — use placeholders)
- **Config changed** → update config tables

### How to update a skill
```python
import requests, base64, json

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}

# 1. Fetch current file + SHA
r = requests.get(
    "https://api.github.com/repos/Syntharra/syntharra-automations/contents/skills/{SKILL_NAME}/SKILL.md",
    headers=headers
).json()
sha = r["sha"]
content = base64.b64decode(r["content"]).decode()

# 2. Apply changes with str.replace()
content = content.replace("old text", "new text")

# 3. Push back
payload = {
    "message": "skill({SKILL_NAME}): describe what changed",
    "content": base64.b64encode(content.encode()).decode(),
    "sha": sha
}
requests.put(
    "https://api.github.com/repos/Syntharra/syntharra-automations/contents/skills/{SKILL_NAME}/SKILL.md",
    headers=headers, data=json.dumps(payload)
)
```

### Skill commit message format
`skill(skill-name): brief description` — e.g.:
- `skill(syntharra-admin): remove agent scenario testing, add system testing docs`
- `skill(hvac-standard): update Arctic Breeze agent ID after republish`
- `skill(syntharra-stripe): add live mode cutover checklist item`

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

## 🚀 Go-Live Checklist (run when Dan says "go live")

When Dan confirms go-live, execute ALL of the following in order:

### 1. Unpause Ops Monitor (Railway)
```
POST https://backboard.railway.com/graphql/v2
Authorization: Bearer {{RAILWAY_TOKEN}}
mutation { sleepApplication(serviceId: "7ce0f943-5216-4a16-8aeb-794cc7cc1e65", sleep: false) }
```

### 2. Re-enable Zero-Call Detection (retell.js)
In `syntharra-ops-monitor/src/monitors/retell.js`:
- Find: `const PRE_LAUNCH_MODE = true;`
- Change to: `const PRE_LAUNCH_MODE = false;`
- Push to GitHub → Railway auto-deploys

### 3. Stripe Live Mode Cutover
Full checklist in `syntharra-stripe` skill:
- Activate Stripe account → switch to live mode
- Recreate all products, prices, coupons (same names, IDs will change)
- Recreate webhook in live mode → update Railway env `STRIPE_SECRET_KEY` to `sk_live_`
- Update n8n webhook signing secret

### 4. Telnyx SMS Enable
- Set `SMS_ENABLED=true` in Railway env for n8n
- Confirm Telnyx toll-free number active and AI evaluation approved

### 5. WhatsApp Business (if resolved)
- Verify business number is active and approved
- Connect to Meta Business Manager

### 6. Confirm all n8n workflows are Active (not paused)
- Check Railway n8n dashboard — all 15 active workflows should be ON
- Auto-Enable MCP workflow `AU8DD5r6i6SlYFnb` should be running

### 7. Marketing System Go-Live
- Run SQL in Supabase (lead gen schema)
- Import lead sourcer, email sequence, hot-lead detector workflows
- Add credentials (Supabase + SMTP2GO) in n8n
- Obtain Google Places API key → configure Cal.com
- Enable workflows

### 8. Final Smoke Test
- Place test call to Arctic Breeze +1 (812) 994-4371
- Submit a test Jotform Standard submission
- Verify Stripe webhook fires correctly
- Check ops monitor dashboard shows all green

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
| Artifacts repo | `Syntharra/syntharra-artifacts` — sales, emails, dashboard, admin, website previews |

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

**See Universal Skill-Update Rule above.** This ops skill covers:
- New n8n workflow created or renamed → update the workflow table
- New Supabase table or column added → update the tables section
- API key or credential changed → update references (never raw values)
- New Retell agent created → update agent IDs
- Stripe product/price/coupon added or changed → update Stripe section
- New Railway service → update infrastructure section
- New website page → update file map
- Any webhook URL changed → update webhook URLs
- Any new learnings or gotchas discovered → add to Key Operational Rules

**How:** Fetch this file from GitHub, apply changes with `str.replace()`, push back using the pattern in the Universal Skill-Update Rule above.
