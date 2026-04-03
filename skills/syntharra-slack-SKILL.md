# Syntharra Slack Skill
> Updated 2026-04-03 — Slack is the primary internal notification channel.

## Webhook
- Stored in: `syntharra_vault` → `service_name='slack_webhook_ops'`
- Retrieve with standard vault pattern (service role key required)
- Method: POST, Content-Type: application/json, no auth header needed

## Channel Map
| Event | Channel | Emoji |
|---|---|---|
| New Stripe payment | `#onboarding` | 💰 |
| Agent live (Std/Prem) | `#onboarding` | ✅ |
| Supabase write failure | `#ops-alerts` | 🚨 |
| Usage alert (80%/100%) | `#ops-alerts` | ⚡/⚠️ |
| Reconciliation mismatch | `#ops-alerts` | ⚠️ |

## Code Node Pattern
```javascript
const SLACK_URL = 'https://hooks.slack.com/services/[REDACTED — see vault: slack_webhook_ops]';
await this.helpers.httpRequest({
  method: 'POST',
  url: SLACK_URL,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    channel: '#ops-alerts',
    username: 'Syntharra Ops',
    icon_emoji: ':rotating_light:',
    blocks: [
      { type: 'header', text: { type: 'plain_text', text: 'Title' } },
      { type: 'section', fields: [{ type: 'mrkdwn', text: '*Field:*\nValue' }] },
      { type: 'context', elements: [{ type: 'mrkdwn', text: new Date().toUTCString() + ' • Source' }] }
    ]
  }),
  json: true
});
```

## HTTP Request Node (expression body)
Hardcode the webhook URL directly in the node URL field (incoming webhooks require no auth headers).
Set `specifyBody: json`, jsonBody:
```
={{ JSON.stringify({
  channel: "#onboarding",
  username: "Syntharra Ops",
  icon_emoji: ":white_check_mark:",
  blocks: [
    { type: "header", text: { type: "plain_text", text: "Title — " + $json.company_name } },
    { type: "section", fields: [{ type: "mrkdwn", text: "*Field:*\n" + $json.value }] },
    { type: "context", elements: [{ type: "mrkdwn", text: new Date().toUTCString() + " • Workflow" }] }
  ]
}) }}
```
Always add `options.response.response.neverError: true` so Slack failure never breaks the flow.

## Workflow Coverage (all updated 2026-04-03)
| Workflow | ID | Slack Node | Internal Email Status |
|---|---|---|---|
| Stripe Workflow | `xKD3ny6kfHL0HHXq` | `Slack: New Payment` → #onboarding | `Send Internal Notification` PAUSED |
| Std Onboarding | `4Hx7aRdzMl5N0uJP` | `Slack: Agent Live` → #onboarding | `Email Summary to Dan` + `Error Notification` PAUSED |
| Usage Monitor | `Wa3pHRMwSjbZHqMC` | `Slack: Usage Alert (Internal)` → #ops-alerts | `Gmail: Notify You (Internal)` PAUSED |
| Std Call Processor | `Kg576YtPM9yEacKn` | Inline in alert node → #ops-alerts | Email PAUSED |
| Prem Call Processor | `STQ4Gt3rH8ptlvMi` | Inline in Log Call retry → #ops-alerts | Email replaced |
| Prem Onboarding | `kz1VmwNccunRMEaF` | `Slack: Agent Live (Premium)` → #onboarding | `Send Internal Notification` PAUSED |

## Reactivating Paused Email Nodes
Remove the first 3 lines of the Code node jsCode:
```
// PAUSED 2026-04-03 — ...
console.log('[PAUSED] ...');
return $input.all();
```

## Rules
- NEVER touch client-facing email nodes (lead alerts, welcome emails, usage warnings, OAuth emails)
- Only internal ops emails paused (to onboarding@/alerts@syntharra.com)
- Always neverError: true on Slack HTTP nodes
- Include context block with timestamp + source in every message

## Gotchas (learned 2026-04-03)
- MCP flag resets after SDK workflow update — always run AU8DD5r6i6SlYFnb after every SDK update
- n8n REST API PUT — do NOT include `active` field (read-only, causes 400 error)
- .onFalse() only valid on IF nodes — HTTP Request error output: use .add(node).to(errorHandler)
- Premium Onboarding patched via REST API — too risky to rebuild 21-node complex flow via SDK
