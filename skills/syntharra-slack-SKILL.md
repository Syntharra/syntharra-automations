# Syntharra — Slack Internal Notifications Skill
> Updated 2026-04-03 — Full channel map, email intelligence workflow, receipts@ note, sub-channel migration path

---

## Overview
Slack is the **only** channel for internal operational notifications.
Internal emails to `@syntharra.com` addresses are **permanently paused** — Slack only.
Client-facing emails (welcome, onboarding, usage alerts, weekly reports TO clients) remain unaffected.

---

## Webhook

| Item | Value |
|---|---|
| Vault lookup | `service_name='Slack'`, `key_type='webhook_url'` |
| n8n env var | `SLACK_WEBHOOK_OPS` |
| Method | POST, `Content-Type: application/json`, no auth header needed |

**Never hardcode the webhook URL in skill files or GitHub — always fetch from vault.**
Actual URL pattern: `https://hooks.slack.com/services/T.../B.../...`

---

## Channel Map — Full

| Channel | ID | Purpose | Emoji |
|---|---|---|---|
| `#billing` | `C0AR3UP8A7K` | Stripe payments, renewals, failed charges | 💰 |
| `#onboarding` | `C0AQP081RCN` | Agent go-live (Std + Prem), new client activations | ✅ |
| `#ops-alerts` | `C0AR3UH5R7B` | Supabase failures, system errors, infra alerts | 🚨 |
| `#calls` | `C0AQUKMD31A` | Lead call summaries (score ≥ 3/5), caller intent | 📞 |
| `#weekly-reports` | `C0AQMKNQK0V` | Weekly report sent confirmations per client | 📊 |
| `#leads` | `C0AQR26PXNE` | Website AI-scored leads, free report sends | 🎯 |
| `#emails` | `C0AQR2CENAW` | All inbox email alerts (score ≥ 3, Groq-filtered) | 📧 |

### Planned: Email Sub-Channels (create when Dan sets them up in Slack)
When Dan creates these channels, update the `aliasMap` in workflow `ghisTdGOR4ErVrUh` → node `Prep: Tag Aliases` → change each alias `channel` value:

| Alias | Planned Sub-Channel | Current |
|---|---|---|
| `support@syntharra.com` | `#emails-support` | `#emails` |
| `sales@syntharra.com` | `#emails-sales` | `#emails` |
| `solutions@syntharra.com` | `#emails-solutions` | `#emails` |
| `onboarding@syntharra.com` | `#emails-onboarding` | `#emails` |
| `info@syntharra.com` | `#emails-info` | `#emails` |
| `careers@syntharra.com` | `#emails-careers` | `#emails` |
| `feedback@syntharra.com` | `#emails-feedback` | `#emails` |
| `admin@syntharra.com` | `#emails-admin` | `#emails` |
| `alerts@syntharra.com` | `#emails-alerts` | `#emails` |
| `receipts@syntharra.com` | `#emails-receipts` | `#emails` |

---

## Workflow Coverage — Complete

| Workflow | n8n ID | Slack Node | Channel | Internal Email Status |
|---|---|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | `Send Internal Notification` (Code) | `#billing` | PAUSED (email commented out) |
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | `Slack: Agent Live` (httpRequest) | `#onboarding` | `Email Summary to Dan` + `Error Notification` PAUSED |
| HVAC Prem Onboarding | `kz1VmwNccunRMEaF` | `Slack: Agent Live (Premium)` (httpRequest) | `#onboarding` | `Send Internal Notification` PAUSED |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Supabase Write Failed` (httpRequest) | `#ops-alerts` | Email replaced |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Lead Call Alert` (httpRequest) | `#calls` | New (no prior email) |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Supabase Write Failed` (httpRequest) | `#ops-alerts` | Email replaced |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Lead Call Alert` (httpRequest) | `#calls` | New (no prior email) |
| Usage Alert Monitor | `Wa3pHRMwSjbZHqMC` | `Slack: Usage Alert (Internal)` (httpRequest) | `#ops-alerts` | `Gmail: Notify You (Internal)` PAUSED |
| Weekly Lead Report | `iLPb6ByiytisqUJC` | `Slack: Weekly Report Summary` (httpRequest) | `#weekly-reports` | New (after Gmail send) |
| Email Intelligence | `ghisTdGOR4ErVrUh` | `Slack: Post to #emails` (httpRequest) | `#emails` (or sub-channel) | New workflow entirely |

---

## Email Intelligence Workflow

**ID:** `ghisTdGOR4ErVrUh`
**Name:** Email Intelligence — Inbox Scanner → Slack
**Status:** ✅ Active
**Schedule:** Every 15 minutes
**Last tested:** 2026-04-03 ✅

### Architecture
```
Schedule (15min) → Set Time Window (30min lookback)
  → Gmail nodes (9 inboxes, parallel) → Merge → Prep: Tag Aliases
  → Groq: Score Importance (per item) → [drop score ≤ 2] → Slack: Post to #emails
```

### Gmail Credentials — All 9 Inboxes

| Alias | Credential ID | Credential Name |
|---|---|---|
| `alerts@syntharra.com` | `PhQNVvTS6HC1zU2b` | Gmail OAuth2 — Alerts Inbox |
| `support@syntharra.com` | `JvsxgXKALaaNcUYu` | Gmail OAuth2 — Support Inbox |
| `sales@syntharra.com` | `HUbJjKZI17i3rNNU` | Gmail OAuth2 — Sales Inbox |
| `solutions@syntharra.com` | `Y3Dvl0p5VMFPwVqM` | Gmail OAuth2 — Solutions Inbox |
| `onboarding@syntharra.com` | `H2v4erNUfViQbl0u` | Gmail OAuth2 — Onboarding Inbox |
| `info@syntharra.com` | `1xxgvvSOJsJEq1Wq` | Gmail OAuth2 — Info Inbox |
| `careers@syntharra.com` | `L4n5HXbGtPO1Ev5O` | Gmail OAuth2 — Careers Inbox |
| `feedback@syntharra.com` | `m18e17Sgh7O0V09c` | Gmail OAuth2 — Feedback Inbox |
| `admin@syntharra.com` | `y8WGEzyiuymSw0SM` | Gmail OAuth2 — Admin Inbox |
| `receipts@syntharra.com` | **NOT YET CREATED** | — see action required below |

### ⚠️ Action Required — receipts@syntharra.com
**receipts@ is NOT yet connected to the email intelligence workflow.**

To add it:
1. Go to n8n → Credentials → New → Gmail OAuth2
2. Name it exactly: `Gmail OAuth2 — Receipts Inbox`
3. Use Google OAuth client from vault (`Google` / `client_id` + `client_secret`)
4. Authenticate with `receipts@syntharra.com`
5. Note the new credential ID
6. In workflow `ghisTdGOR4ErVrUh`:
   - Add a new Gmail node: `Gmail: Receipts`
   - Use the new credential
   - Wire `Set Time Window → Gmail: Receipts → Merge All Inboxes`
7. The `aliasMap` in `Prep: Tag Aliases` already includes `receipts@syntharra.com` with emoji 🧾

### Groq Scoring Logic

| Score | Meaning | Passes to Slack? |
|---|---|---|
| 5 | Urgent — client issue, payment failure, security | ✅ Yes — :rotating_light: |
| 4 | Client/lead inquiry, partner outreach | ✅ Yes — :bell: |
| 3 | General business, vendor comms | ✅ Yes — :email: |
| 2 | Newsletter, marketing | ❌ Dropped |
| 1 | Spam, automated | ❌ Dropped |

**Categories:** `client_issue`, `lead`, `payment`, `partner`, `feedback`, `support`, `recruitment`, `billing`, `spam`, `automated`, `general`

### Slack Message Format (per email)
- **Header:** `{alias_emoji} {⚡ if action_needed} [{Alias Label}] {subject (55 chars)}`
- **Fields:** From, Inbox (alias address), Category, Priority (stars + n/5)
- **Section:** AI Summary (80 chars max, Groq-generated)
- **Context:** Date + "⚡ Action Required" if flagged

---

## Code Node Pattern — Slack via httpRequest helper

Use this in Code nodes (avoids $credentials syntax issues with httpRequest nodes):

```javascript
const SLACK_URL = 'https://hooks.slack.com/services/[FETCH FROM VAULT]';

try {
  await this.helpers.httpRequest({
    method: 'POST',
    url: SLACK_URL,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      channel: '#ops-alerts',
      username: 'Syntharra Ops',
      icon_emoji: ':rotating_light:',
      blocks: [
        { type: 'header', text: { type: 'plain_text', text: '🚨 Title' } },
        { type: 'section', fields: [
          { type: 'mrkdwn', text: '*Field:*\nValue' }
        ]},
        { type: 'context', elements: [{ type: 'mrkdwn', text: new Date().toUTCString() + ' • Source' }] }
      ]
    }),
    json: true
  });
} catch (e) { console.error('[SLACK] Failed:', e.message); }
```

## HTTP Request Node Pattern — expression body

```
Method: POST
URL: [webhook URL hardcoded or from env var $env.SLACK_WEBHOOK_OPS]
Body Type: JSON (specifyBody: json)
jsonBody:
={{ JSON.stringify({
  channel: "#onboarding",
  username: "Syntharra Ops",
  icon_emoji: ":white_check_mark:",
  blocks: [
    { type: "header", text: { type: "plain_text", text: "✅ Title — " + $json.company_name } },
    { type: "section", fields: [{ type: "mrkdwn", text: "*Field:*\n" + $json.value }] },
    { type: "context", elements: [{ type: "mrkdwn", text: new Date().toUTCString() + " • Workflow" }] }
  ]
}) }}
Options: neverError: true (always — Slack failure must never break flow)
```

---

## Rules

- **NEVER** touch client-facing email nodes (lead alerts, welcome emails, usage warnings to clients, OAuth emails)
- **ONLY** internal ops emails paused (those going to `@syntharra.com` addresses)
- **ALWAYS** `neverError: true` on all Slack HTTP nodes — Slack down ≠ workflow failure
- **ALWAYS** include `context` block with timestamp + source workflow name in every message
- **Stripe** payment notifications → `#billing` (NOT `#onboarding`)
- **Agent go-live** → `#onboarding`
- **System failures** → `#ops-alerts`
- **Lead calls** → `#calls` (hot/warm only — fires after HubSpot Log Call node)
- **Email triage** → `#emails` (until sub-channels created, then per-alias channels)

---

## Reactivating Paused Email Nodes (if ever needed)

All paused Code nodes have this pattern at the top:
```javascript
// PAUSED 2026-04-03 — replaced by Slack. To reactivate: remove these 3 lines
console.log('[PAUSED] Skipping internal email');
return $input.all();
```
Remove those 3 lines to restore.

---

## Gotchas & Lessons Learned

| Finding | Detail |
|---|---|
| `active` field is read-only | Do NOT include `active` in `POST /api/v1/workflows` payload — causes 400. Activate separately via `POST /api/v1/workflows/{id}/activate` |
| Groq in Code nodes | Use `this.helpers.httpRequest()` with manual `Authorization: Bearer {key}` — do NOT use `$credentials.groqApiKey` syntax in Code nodes (only works in native nodes) |
| Gmail OAuth2 credential via API | Cannot create via REST API with `scope` field — n8n schema rejects it. Must create via n8n UI (Credentials → New → Gmail OAuth2) and authenticate manually |
| n8n REST PUT — no `active` field | `active` is read-only on PUT too — strip from payload |
| MCP flag resets after SDK workflow update | Always run `AU8DD5r6i6SlYFnb` (Auto-Enable MCP) after any SDK workflow update |
| Webhook URL is stable | Slack incoming webhook URL does not rotate — safe to cache in vault and Railway env var |
| Merge node receives multi-input | When wiring N Gmail nodes → 1 Merge node, all connections go to `index: 0` on the merge node (not index 0,1,2...) — n8n handles the fan-in |
| Groq score filter | Return `null` from Code node to drop items. Items with score ≤ 2 (spam/automated) are dropped before Slack post |

---

## Vault Entry

```
service_name: 'Slack'
key_type: 'webhook_url'
Lookup: GET /syntharra_vault?service_name=eq.Slack&key_type=eq.webhook_url
```

## n8n Railway Env Var
```
SLACK_WEBHOOK_OPS = <value from vault>
```
