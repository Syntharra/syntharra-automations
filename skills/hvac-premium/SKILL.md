---
name: hvac-premium
description: >
  Complete reference for the Syntharra HVAC Premium pipeline — the full-featured enterprise tier.
  ALWAYS load this skill when: working on HVAC Premium onboarding, the Premium call processor,
  the Premium dispatcher, Premium OAuth server, Premium client Supabase records, debugging
  Premium n8n workflows, setting up Google Calendar or Jobber integrations for Premium clients,
  or doing anything related to the Premium plan ($997/mo or $831/mo annual, 1,000 min/mo).
  Also trigger for any task involving multi-notification recipients, repeat caller detection,
  Premium email sequences, or the 4-step Premium onboarding email flow.
---

# HVAC Premium Pipeline — Full Reference

---

## n8n Workflows

| Workflow | ID | Detail |
|---|---|---|
| HVAC Prem Onboarding | `KXDSMVKSf59tAtal` | 13 nodes, 17 PCA, 4 tools |
| HVAC Prem Call Processor | `UhxfrDaEeYUk4jAD` | 15 nodes, repeat caller detection |
| HVAC Prem Dispatcher | `kVKyPQO7cXKUJFbW` | 4 nodes — Google Cal + Jobber |

- n8n instance: `https://n8n.syntharra.com`
- Railway n8n API key: `{{N8N_API_KEY}}`
- **Always click Publish after any workflow edits**
- All email nodes use SMTP2GO credential: `"SMTP2GO - Syntharra"`

---

## Jotform — Premium Onboarding

| Item | Value |
|---|---|
| Form ID | `260819259556671` |
| API Key | `{{JOTFORM_API_KEY}}` (account: Blackmore_Daniel) |

**Use REST API directly** — do NOT use MCP OAuth connector (broken).

---

## OAuth Server

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-oauth-server` |
| Purpose | Handles Google Calendar / Jobber OAuth for Premium clients |

---

## Supabase — Premium Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Client config (used by both Standard and Premium — includes notification_email_2/3, notification_sms_2/3) |
| `hvac_call_log` | All call records with Premium-specific fields |
| `client_subscriptions` | Active subscription tracking |
| `billing_cycles` | Billing cycle records |
| `overage_charges` | Usage overage tracking |

- Supabase URL: `hgheyqwnrcvwtgngqdnq.supabase.co`

---

## Premium Plan Pricing

| Billing | Price | Setup Fee | Minutes |
|---|---|---|---|
| Monthly | $997/mo | $2,499 | 1,000 min/mo |
| Annual | $831/mo | $2,499 | 1,000 min/mo |

Annual = 2 months free.

---

## Stripe (TEST MODE) — Premium

| Item | Value |
|---|---|
| Premium product | `prod_UC0mYC90fSItcq` |
| Monthly price | `price_1TDclGECS71NQsk8OoLoMV0q` |
| Annual price | `price_1TDclPECS71NQsk8S9bAPGoJ` |
| Setup fee price | `price_1TEKKvECS71NQsk8vWGjHLUP` |
| Founding discount | `FOUNDING-PREMIUM` → `RsOnUuo4` ($2,499 off once) |

---

## Email Flow (Premium Clients — 4 emails)

1. Stripe welcome email
2. Integration setup email (Premium-only — Google Calendar, Jobber)
3. "You're Live" email + PDF
4. Weekly report (ongoing)

### Email Routing (Premium)

| Notification Type | To |
|---|---|
| Internal onboarding notifications | `onboarding@syntharra.com` |
| Internal call processor notifications | `admin@syntharra.com` |
| Customer-facing support reference | `support@syntharra.com` |

---

## SMS

- SMS wired but disabled: `SMS_ENABLED=false`
- Preferred provider: Telnyx (awaiting AI evaluation approval)
- Backup: Plivo. **Never Twilio.**

---

## Retell Agents

Same Retell API key and rules as Standard: `{{RETELL_API_KEY}}`
- **NEVER delete or recreate a Retell agent**
- **Always publish after any agent update**: `POST https://api.retellai.com/publish-agent/{agent_id}`
- Prompt architecture: master base prompt + company info block + call type nodes
- Dynamic variables: `{{agent_name}}`, `{{company_name}}`, `{{COMPANY_INFO_BLOCK}}`
- **Use commas not dashes** in all prompts

---

## Dashboard

- Live at `syntharra.com/dashboard.html?agent_id=X`
- Shows live Supabase data for the client's agent

---

## Shared Workflows (also affect Premium)

| Workflow | ID |
|---|---|
| Stripe Workflow | `ydzfhitWiF5wNzEy` |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` |
| Minutes Calculator | `9SuchBjqhFmLbH8o` |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` |
| Publish Retell Agent | `sBFhshlsz31L6FV8` |

---

## Scaling Architecture (for future clients)

- Retell API auto-clones agents per client via n8n onboarding triggered by Jotform
- Supabase stores all client config
- Repo structure target: `hvac-standard/`, `hvac-premium/`, `plumbing-standard/`, etc. with `shared/` folder

---

## Pre-Launch Checklist (Premium-specific)

- [ ] Enable repeat caller detection (currently wired, not enabled)
- [ ] Complete Telnyx SMS setup (awaiting AI evaluation approval)
- [ ] Switch Stripe to live mode — recreate Premium product, prices, coupons, webhook
