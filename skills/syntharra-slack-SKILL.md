# Syntharra — Slack Internal Notifications Skill
> Updated 2026-04-10 — Workspace cleaned 2026-04-09: 22 → 7 channels. 15 clutter channels archived. `#daily-digest` added.

---

## Status: COMPLETE ✅ (cleaned 2026-04-09)
All internal @syntharra.com email notifications replaced with Slack.
7 active channels. 15 clutter channels archived via `conversations.archive`.

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

## Channel Map — 7 Active Channels (cleaned 2026-04-09)

> 15 clutter channels archived. Only these 7 remain active.

| Channel | ID | Purpose |
|---|---|---|
| `#all-syntharra` | — | General + incoming webhook default |
| `#billing` | `C0AR3UP8A7K` | Stripe payments, renewals, failed charges |
| `#calls` | `C0AQUKMD31A` | Lead call summaries from call processor |
| `#daily-digest` | — | Automated daily ops digest (created 2026-04-09) |
| `#leads` | `C0AQR26PXNE` | Website AI-scored leads, free report sends |
| `#onboarding` | `C0AQP081RCN` | Agent go-live, new client activations |
| `#ops-alerts` | `C0AR3UH5R7B` | System errors, infra alerts |

> Archived channels included: `#weekly-reports`, `#emails`, all `#*-syntharra-com` alias channels, and other legacy channels.

---

## Workflow Coverage — All Live

| Workflow | n8n ID | Slack Node | Channel |
|---|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | `Send Internal Notification` | `#billing` |
| HVAC Std Onboarding | `4Hx7aRdzMl5N0uJP` | `Slack: Agent Live` | `#onboarding` |
| HVAC Call Processor | `Kg576YtPM9yEacKn` | `Post to Client Slack` | client's own webhook URL (per-client) |
| `tools/usage_alert.py` | — | — | `#ops-alerts` (if wired) |

> HVAC Premium call processor archived 2026-04-08. Client Slack webhooks now come through the call processor fan-out — each client optionally provides their own webhook URL via Jotform field `q76_slackIncoming`.
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

## Daily Ops Digest — LIVE ✅

**Workflow ID:** `SiMn59qJOfrZZS81`
**Schedule:** `0 6 * * *` (6:00 AM UTC daily)
**Channel:** `#all-syntharra` (`C0AQNT2S6QJ`)
**Status:** Active

### What it includes
| Section | Data source | Fields |
|---|---|---|
| 👥 Clients | `hvac_standard_agent` Supabase | Total, Std/Prem split, Active Agents, MRR |
| 📞 Calls (24h) | `hvac_call_log` Supabase | Total, Leads, Hot leads, Avg sentiment, Conv rate, Emergencies |
| System Health | Ops Monitor `/api/status` | Per-system ✅/❌, unhealthy callout → #ops-alerts |

### Format
- Slack `blocks` layout with header, divider, section fields
- Health displayed as inline text string (NOT dynamic array — causes invalid_blocks)
- Issues section only appended if unhealthy systems exist
- 0 calls section appended if no calls in 24h
- Emergencies section appended if any flagged

### Env vars required on n8n Railway service
- `SLACK_BOT_TOKEN` — bot token with chat:write, chat:write.public
- `STRIPE_SECRET_KEY` — Stripe secret key for MRR data

### Gotcha
Do NOT build the system health section using a dynamic `.map()` array directly in the `fields` key of a section block. Slack rejects this as `invalid_blocks`. Instead build a single text string with the health status and embed it in the `text` field of a section block.

---

## Gotchas & Lessons Learned

| Finding | Detail |
|---|---|
| Incoming webhook ignores `channel` field | Hard-locked to creation channel. Silently posts to #all-syntharra regardless of payload. Never use for multi-channel routing. |
| xoxb- token scope ≠ full bot token | Token generated via webhook OAuth flow only has `incoming-webhook` scope. Need separate install with `chat:write` scope. |
| Reinstall blocked by missing redirect URL | Existing app couldn't reinstall — no OAuth redirect URL configured. Fix: create new app from scratch. |
| New app still needs bot joined to channels | `chat:write` (without `chat:write.public`) requires bot to be a member of each channel. Must `/invite @botname` in each channel OR add `chat:write.public` scope. |
| `chat:write.public` best practice | Add this scope to avoid needing to invite bot to every channel. Eliminates `not_in_channel` errors entirely. |
| Slack blocks — don't use dynamic `.map()` array in `fields` | Building `fields: items.map(...)` inline in block JSON causes `invalid_blocks` error. Build health/list data as a string and embed in `text` field instead. |
| Always use channel IDs not names | IDs (C0AR...) are permanent. Names change. All nodes must use IDs. |
| All aliases = one Gmail credential | @syntharra.com aliases all live under one Google account. Use `XJwYjqAfJLES1b5I` with `to:alias@` query filter. Never create per-alias credentials. |
| Bot token stored in vault + Railway | `service_name='Slack'`, `key_type='bot_token'` in vault. `SLACK_BOT_TOKEN` env var on Railway n8n service. |
