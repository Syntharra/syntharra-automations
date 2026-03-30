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

---

## 🔑 Credential Access — Supabase Vault

**NEVER store API keys in skill files, project memory, or anywhere else.**

All Syntharra credentials are stored in the `syntharra_vault` table in Supabase.

**To retrieve a key:**
1. Query `https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&select=key_value`
2. Use the **service role key** from Supabase Project Settings → API
3. Filter by `service_name` to get the `key_value`

```python
import requests

SB_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
# Get service role key from Supabase Project Settings → API

def get_key(service_name, sb_service_role_key):
    r = requests.get(
        f"{SB_URL}/rest/v1/syntharra_vault",
        params={"service_name": f"eq.{service_name}", "select": "key_value"},
        headers={
            "apikey": sb_service_role_key,
            "Authorization": f"Bearer {sb_service_role_key}"
        }
    )
    return r.json()[0]["key_value"]

# Example:
# retell_key = get_key("retell")
# n8n_key    = get_key("n8n_railway")
# github_token = get_key("github")
```

**Known service_name values** (populate before use):
- `retell` — Retell AI API key
- `n8n_railway` — Railway n8n API key
- `github` — GitHub personal access token
- `jotform` — Jotform API key
- `smtp2go` — SMTP2GO API key
- `railway` — Railway GraphQL API token
- `stripe_webhook_secret` — Stripe webhook signing secret
- `supabase_service_role` — Supabase service role key (for non-vault queries)
- `telnyx` — Telnyx API key (when active)
