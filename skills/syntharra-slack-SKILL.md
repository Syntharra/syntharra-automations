# Syntharra — Slack Internal Notifications Skill
> Updated 2026-04-03 — COMPLETE. 16/16 channels confirmed. chat:write.public active. Ops monitor email paused. Email intelligence live.

---

## Status: COMPLETE ✅
All internal @syntharra.com email notifications replaced with Slack.
All 16 channels live and tested. Email intelligence scanning 10 aliases every 15 min.

---

## Bot Token

| Item | Value |
|---|---|
| Bot name | `@syntharra` (user `U0AQR9PQWCS`, bot `B0AR46TCYDP`) |
| Vault | `service_name='Slack'`, `key_type='bot_token'` |
| Railway env var | `SLACK_BOT_TOKEN` (set on n8n service) |
| Scope | `chat:write` + `chat:write.public` + `incoming-webhook` |
| API endpoint | `POST https://slack.com/api/chat.postMessage` |

**IMPORTANT: Always use channel IDs (C0...), never channel names. IDs are permanent.**
**chat:write.public is active — bot posts to ANY channel without /invite. Never need to invite again.**

---

## Incoming Webhook — LEGACY, DO NOT USE FOR ROUTING

| Item | Value |
|---|---|
| Vault | `service_name='Slack'`, `key_type='webhook_url'` |
| Default channel | `#all-syntharra` (hard-locked, ignores `channel` field) |
| Status | Retired for notifications — webhook silently ignores channel field |

**Never use the webhook for multi-channel routing. It always posts to #all-syntharra regardless.**

---

## Channel Map — All IDs Confirmed ✅

### Operational Channels
| Channel | ID | Purpose | Emoji |
|---|---|---|---|
| `#billing` | `C0AR3UP8A7K` | Stripe payments, renewals, failed charges | 💰 |
| `#onboarding` | `C0AQP081RCN` | Agent go-live (Std + Prem), new client activations | ✅ |
| `#ops-alerts` | `C0AR3UH5R7B` | Supabase failures, system errors, infra alerts | 🚨 |
| `#calls` | `C0AQUKMD31A` | Lead call summaries (hot/warm only, after HubSpot) | 📞 |
| `#weekly-reports` | `C0AQMKNQK0V` | Weekly report sent confirmations per client | 📊 |
| `#leads` | `C0AQR26PXNE` | Website AI-scored leads, free report sends | 🎯 |
| `#emails` | `C0AQR2CENAW` | Fallback / feedback@ (no dedicated sub-channel yet) | 📧 |

### Email Sub-Channels
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

---

## Workflow Coverage — All Live

| Workflow | n8n ID | Slack Node | Channel ID |
|---|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | `Send Internal Notification` | `C0AR3UP8A7K` billing |
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | `Slack: Agent Live` | `C0AQP081RCN` onboarding |
| HVAC Prem Onboarding | `kz1VmwNccunRMEaF` | `Slack: Agent Live (Premium)` | `C0AQP081RCN` onboarding |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Supabase Write Failed` | `C0AR3UH5R7B` ops-alerts |
| HVAC Std Call Processor | `Kg576YtPM9yEacKn` | `Slack: Lead Call Alert` | `C0AQUKMD31A` calls |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Supabase Write Failed` | `C0AR3UH5R7B` ops-alerts |
| HVAC Prem Call Processor | `STQ4Gt3rH8ptlvMi` | `Slack: Lead Call Alert` | `C0AQUKMD31A` calls |
| Usage Alert Monitor | `Wa3pHRMwSjbZHqMC` | `Slack: Usage Alert (Internal)` | `C0AR3UH5R7B` ops-alerts |
| Weekly Lead Report | `iLPb6ByiytisqUJC` | `Slack: Weekly Report Summary` | `C0AQMKNQK0V` weekly-reports |
| Email Intelligence | `PavRLBVQQpWrKUYs` | `Slack: Post to Channel` | per-alias channel ID |

---

## Email Intelligence Workflow

**ID:** `PavRLBVQQpWrKUYs` | **Status:** ✅ ACTIVE | **Schedule:** every 15 min

**Gmail credential:** `XJwYjqAfJLES1b5I` ("Gmail account" = daniel@syntharra.com)
All aliases (sales@, support@, etc.) are aliases of one Google account — use ONE credential with `to:alias@syntharra.com` query per Gmail node. Never create separate credentials per alias.

### Alias → Channel Routing
| Alias | Channel ID | Channel Name |
|---|---|---|
| alerts@syntharra.com | C0AQP29J5KQ | #alerts-syntharra-com |
| support@syntharra.com | C0AQJN9N6LT | #support-syntharra-com |
| sales@syntharra.com | C0AR41A0H7B | #sales-syntharra-com |
| solutions@syntharra.com | C0AQJNE445R | #solutions-syntharra-com |
| onboarding@syntharra.com | C0AQMN55H6H | #onboarding-syntharra-com |
| info@syntharra.com | C0ARKCCJMRN | #info-syntharra-com |
| careers@syntharra.com | C0AQR4NPCJW | #careers-syntharra-com |
| feedback@syntharra.com | C0AQR2CENAW | #emails (fallback) |
| admin@syntharra.com | C0AQUMSD8TE | #admin-syntharra-com |
| receipts@syntharra.com | C0AQ9LSREJK | #receipts-syntharra-com |

### Groq Filter
Score 1-2 (spam/automated) → dropped. Score 3-5 → posted to channel.
Model: `llama3-8b-8192` | via `this.helpers.httpRequest()` in Code node.


---

## Ops Monitor Integration — LIVE ✅

**Repo:** `Syntharra/syntharra-ops-monitor`
**File:** `src/utils/alertManager.js`

Alert routing:
| Tier | Dashboard | Slack | Email | SMS |
|---|---|---|---|---|
| info | ✅ | ❌ (noise) | ❌ paused | ❌ |
| warning | ✅ | ✅ #ops-alerts | ❌ paused | ❌ |
| critical | ✅ | ✅ #ops-alerts | ❌ paused | ✅ Telnyx |

Email paused with `if(false)` wrapper — one line to reactivate.
Daily digest email also paused — Slack real-time replaces it.
SMS (Telnyx) on critical: untouched, still active.

`SLACK_BOT_TOKEN` env var set on Railway ops monitor service.

---

## n8n Code Node Pattern

```javascript
const TOKEN = $env.SLACK_BOT_TOKEN || '';
if (!TOKEN) { console.log('[SLACK] No token'); return { json: { skipped: true } }; }

const res = await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://slack.com/api/chat.postMessage',
  headers: { 'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    channel: 'C0AR3UP8A7K',          // always channel ID, never name
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
if (!res.ok) console.error('[SLACK]', res.error);
return { json: { ok: res.ok } };
```

---

## Gotchas & Lessons Learned

| Finding | Detail |
|---|---|
| Incoming webhook ignores `channel` field | Hard-locked to creation channel. Silently posts to #all-syntharra regardless of payload. Never use for multi-channel routing. |
| xoxb- token scope ≠ full bot token | Token generated via webhook OAuth flow only has `incoming-webhook` scope. Need separate install with `chat:write` scope. |
| Reinstall blocked by missing redirect URL | Existing app couldn't reinstall — no OAuth redirect URL configured. Fix: create new app from scratch. |
| New app still needs bot joined to channels | `chat:write` (without `chat:write.public`) requires bot to be a member of each channel. Must `/invite @botname` in each channel OR add `chat:write.public` scope. |
| `chat:write.public` best practice | Add this scope to avoid needing to invite bot to every channel. Eliminates `not_in_channel` errors entirely. |
| Always use channel IDs not names | IDs (C0AR...) are permanent. Names change. All nodes must use IDs. |
| All aliases = one Gmail credential | @syntharra.com aliases all live under one Google account. Use `XJwYjqAfJLES1b5I` with `to:alias@` query filter. Never create per-alias credentials. |
| Bot token stored in vault + Railway | `service_name='Slack'`, `key_type='bot_token'` in vault. `SLACK_BOT_TOKEN` env var on Railway n8n service. |
