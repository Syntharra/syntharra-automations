# Syntharra — Slack Internal Notifications Skill
> Updated 2026-04-03 — Bot token scope issue documented, Claude MCP connector confirmed working, n8n pending dedicated bot

---

## Overview
Slack is the **only** channel for internal operational notifications.
Internal emails to `@syntharra.com` addresses are permanently paused — Slack only.
Client-facing emails (welcome, onboarding, usage alerts, weekly reports to clients) are unaffected.

---

## Webhook vs Bot Token — CRITICAL LESSON

### Incoming Webhook — DO NOT USE for multi-channel routing
- Slack incoming webhooks are hard-locked to the channel chosen at creation time
- The `channel` field in the POST payload is **silently ignored** by modern Slack apps
- All messages go to the default channel regardless of what `channel` you set
- The existing webhook (`service_name='Slack'`, `key_type='webhook_url'`) points to `#all-syntharra`
- **Never use the webhook for anything other than a single-channel notification**

### Bot Token — REQUIRED for per-channel routing
- Use `chat.postMessage` API with `Authorization: Bearer xoxb-...`
- Post to any channel using its **channel ID** (not name — IDs are stable)
- Requires scopes: `chat:write` + `chat:write.public`
- `chat:write.public` = no need to invite bot to each channel first (critical)

### Current Status
- Claude MCP connector (`syntharra_ops` bot, `U0AQ7HYCY23`) ✅ works for all channels
- n8n workflows: waiting on dedicated bot token with correct scopes
- All 16 channels verified working via MCP connector 2026-04-03

---

## Vault Entries

| service_name | key_type | Value |
|---|---|---|
| `Slack` | `webhook_url` | incoming webhook (locked to #all-syntharra — legacy only) |
| `Slack` | `bot_token` | xoxb- token (stored but only has incoming-webhook scope — pending new app) |

---

## Channel Map — Complete (all IDs confirmed 2026-04-03)

### Operational Channels
| Channel | ID | Purpose | Emoji |
|---|---|---|---|
| `#billing` | `C0AR3UP8A7K` | Stripe payments, renewals, failed charges | 💰 |
| `#onboarding` | `C0AQP081RCN` | Agent go-live (Std + Prem), new client activations | ✅ |
| `#ops-alerts` | `C0AR3UH5R7B` | Supabase failures, system errors, infra alerts | 🚨 |
| `#calls` | `C0AQUKMD31A` | Lead call summaries (hot/warm only) | 📞 |
| `#weekly-reports` | `C0AQMKNQK0V` | Weekly report sent confirmations | 📊 |
| `#leads` | `C0AQR26PXNE` | Website AI-scored leads | 🎯 |
| `#emails` | `C0AQR2CENAW` | Fallback / general email alerts | 📧 |

### Email Sub-Channels (alias-specific)
| Channel | ID | Alias |
|---|---|---|
| `#sales-syntharra-com` | `C0AR41A0H7B` | sales@syntharra.com |
| `#support-syntharra-com` | `C0AQJN9N6LT` | support@syntharra.com |
| `#solutions-syntharra-com` | `C0AQJNE445R` | solutions@syntharra.com |
| `#onboarding-syntharra-com` | `C0AQMN55H6H` | onboarding@syntharra.com |
| `#info-syntharra-com` | `C0ARKCCJMRN` | info@syntharra.com |
| `#careers-syntharra-com` | `C0AQR4NPCJW` | careers@syntharra.com |
| `#alerts-syntharra-com` | `C0AQP29J5KQ` | alerts@syntharra.com |
| `#admin-syntharra-com` | `C0AQUMSD8TE` | admin@syntharra.com |
| `#receipts-syntharra-com` | `C0AQ9LSREJK` | receipts@syntharra.com |
| `#feedback-syntharra-com` | TBC | feedback@syntharra.com (channel not yet created) |

---

## n8n Bot Token Setup — PENDING (one-time task for Dan)

The existing `xoxb-` token only has `incoming-webhook` scope. The Slack app's reinstall
is blocked due to missing OAuth redirect URL config. 

**Solution: Create a new dedicated Slack app for n8n in 3 minutes:**

1. Go to **https://api.slack.com/apps/new**
2. "From scratch" → Name: `Syntharra Ops Bot` → Workspace: Syntharra → Create App
3. Left nav → **OAuth & Permissions** → Bot Token Scopes → Add:
   - `chat:write`
   - `chat:write.public` ← critical — lets bot post without joining each channel
4. Scroll up → **Install to Workspace** → Allow
5. Copy the **Bot User OAuth Token** (`xoxb-...`) → paste to Claude
6. Claude will store in vault + Railway env var `SLACK_BOT_TOKEN` + activate email workflow

---

## Workflow Coverage

| Workflow | n8n ID | Slack Node | Channel | Email Status |
|---|---|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | `Send Internal Notification` (Code) | `#billing` `C0AR3UP8A7K` | PAUSED |
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | `Slack: Agent Live` (Code) | `#onboarding` `C0AQP081RCN` | PAUSED |
| HVAC Prem Onboarding | `kz1VmwNccunRMEaF` | `Slack: Agent Live (Premium)` (Code) | `#onboarding` `C0AQP081RCN` | PAUSED |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Supabase Write Failed` (Code) | `#ops-alerts` `C0AR3UH5R7B` | Replaced |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Lead Call Alert` (Code) | `#calls` `C0AQUKMD31A` | New |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Supabase Write Failed` (Code) | `#ops-alerts` `C0AR3UH5R7B` | Replaced |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Lead Call Alert` (Code) | `#calls` `C0AQUKMD31A` | New |
| Usage Alert Monitor | `Wa3pHRMwSjbZHqMC` | `Slack: Usage Alert (Internal)` (Code) | `#ops-alerts` `C0AR3UH5R7B` | PAUSED |
| Weekly Lead Report | `iLPb6ByiytisqUJC` | `Slack: Weekly Report Summary` (Code) | `#weekly-reports` `C0AQMKNQK0V` | New |
| Email Intelligence | `PavRLBVQQpWrKUYs` | `Slack: Post to Channel` (Code) | per-alias channel ID | New — awaiting bot token |

All Slack Code nodes read `$env.SLACK_BOT_TOKEN` and call `https://slack.com/api/chat.postMessage`.
They gracefully skip (log + return) if token is not set.

---

## Email Intelligence Workflow

**ID:** `PavRLBVQQpWrKUYs`
**Status:** Created, NOT yet activated (awaiting bot token)
**Schedule:** Every 15 minutes
**Gmail credential:** `XJwYjqAfJLES1b5I` ("Gmail account" = daniel@syntharra.com with all aliases)
**Key insight:** All @syntharra.com aliases are aliases of a single Google account — use ONE Gmail credential, filter by `to:alias@syntharra.com` query per Gmail node. Do NOT create separate credentials per alias.

### Alias → Channel Routing
| Alias | Channel ID |
|---|---|
| alerts@syntharra.com | C0AQP29J5KQ |
| support@syntharra.com | C0AQJN9N6LT |
| sales@syntharra.com | C0AR41A0H7B |
| solutions@syntharra.com | C0AQJNE445R |
| onboarding@syntharra.com | C0AQMN55H6H |
| info@syntharra.com | C0ARKCCJMRN |
| careers@syntharra.com | C0AQR4NPCJW |
| feedback@syntharra.com | C0AQR2CENAW (fallback — no sub-channel yet) |
| admin@syntharra.com | C0AQUMSD8TE |
| receipts@syntharra.com | C0AQ9LSREJK |

### Groq Scoring
- Score 1-2 (spam/automated/newsletters) → dropped, no Slack post
- Score 3+ → posted to alias-specific channel
- Model: `llama3-8b-8192`, max_tokens: 150, temperature: 0
- Categories: client_issue, lead, payment, partner, feedback, support, recruitment, billing, spam, automated, general

---

## Code Node Pattern (all workflows)

```javascript
const TOKEN = $env.SLACK_BOT_TOKEN || '';
if (!TOKEN) { console.log('[SLACK] No bot token'); return { json: { skipped: true } }; }

await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://slack.com/api/chat.postMessage',
  headers: { 'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    channel: 'C0AR3UP8A7K',  // always use channel ID, never channel name
    username: 'Syntharra Ops',
    icon_emoji: ':moneybag:',
    blocks: [
      { type: 'header', text: { type: 'plain_text', text: '💰 Title' } },
      { type: 'section', fields: [{ type: 'mrkdwn', text: '*Field:*\nValue' }] },
      { type: 'context', elements: [{ type: 'mrkdwn', text: new Date().toUTCString() + ' • Source' }] }
    ]
  }),
  json: true
});
```

---

## Gotchas & Lessons Learned

| Finding | Detail |
|---|---|
| Incoming webhooks ignore `channel` field | Modern Slack app webhooks are hard-locked to creation channel. `channel` payload field silently ignored. Never use for multi-channel routing. |
| `chat:write.public` is essential | Without it, bot must join every channel before posting. With it, posts anywhere without joining. Add both `chat:write` + `chat:write.public`. |
| Reinstall blocked by missing redirect URL | If Slack app has no OAuth redirect URL configured, the reinstall flow breaks. Fix: create a new app from scratch instead. |
| xoxb- token scope doesn't update on save | Adding scopes in app settings does NOT update the existing token. Must click "Reinstall to Workspace" to regenerate token with new scopes. |
| Always use channel IDs not names | Channel IDs (C0AR...) are permanent. Channel names can change. All n8n nodes must use IDs. |
| All aliases use single Gmail credential | @syntharra.com aliases all live under one Google account. Use credential `XJwYjqAfJLES1b5I` with `to:alias@syntharra.com` query filter — do NOT create one credential per alias. |
| `active` field read-only on POST | Do not include `active` in workflow creation payload — causes 400. Activate separately via POST /activate. |
| Groq in Code nodes | Use `this.helpers.httpRequest()` with manual `Authorization: Bearer` header. `$credentials` syntax does not work in Code nodes. |
