---
name: syntharra-slack
description: >
  Complete reference for all Syntharra Slack integrations.
  Load when: adding Slack notifications to any n8n workflow, building new Slack alerts,
  debugging Slack message delivery, adding new channels, or working on the Claude Code
  progress notification system.
---

> Last verified: 2026-04-03 — initial setup

# Syntharra — Slack Reference

---

## Workspace Setup
- Workspace: Syntharra (internal ops only)
- Slack webhook URL: stored in `syntharra_vault` → `service_name='slack_webhook_ops'`
- n8n env var: `SLACK_WEBHOOK_OPS` (set in Railway n8n service)
- All messages sent via Incoming Webhook — no OAuth bot needed for current use

---

## Channel Structure

| Channel | Purpose | Who sees it |
|---|---|---|
| `#ops-alerts` | System alerts, errors, infra issues | Dan |
| `#onboarding` | New client events (payment, agent live, integration connected) | Dan |
| `#calls` | Notable call events (lead captured, emergency, transfer) | Dan |
| `#claude-code` | Claude Code session progress, E2E results, self-heal updates | Dan |
| `#weekly-digest` | Weekly summary — leads, calls, health scores | Dan |

---

## n8n HTTP Node Pattern (all Slack messages)

```javascript
// HTTP Request node — POST to Slack webhook
Method: POST
URL: {{ $env.SLACK_WEBHOOK_OPS }}
Body (JSON):
{
  "channel": "#ops-alerts",
  "username": "Syntharra Ops",
  "icon_emoji": ":robot_face:",
  "blocks": [
    {
      "type": "header",
      "text": { "type": "plain_text", "text": "🔔 Alert Title" }
    },
    {
      "type": "section",
      "fields": [
        { "type": "mrkdwn", "text": "*Client:*\nAcme HVAC" },
        { "type": "mrkdwn", "text": "*Event:*\nAgent went live" }
      ]
    },
    {
      "type": "context",
      "elements": [{ "type": "mrkdwn", "text": "2026-04-03 14:32 UTC" }]
    }
  ]
}
```

---

## Message Templates

### New Payment (Stripe)
```json
{
  "channel": "#onboarding",
  "username": "Syntharra Ops",
  "icon_emoji": ":moneybag:",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "💰 New Payment Received" }},
    { "type": "section", "fields": [
      { "type": "mrkdwn", "text": "*Client:*\n{{company_name}}" },
      { "type": "mrkdwn", "text": "*Plan:*\n{{plan_type}}" },
      { "type": "mrkdwn", "text": "*Amount:*\n{{amount}}" },
      { "type": "mrkdwn", "text": "*Email:*\n{{email}}" }
    ]},
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "{{timestamp}} • Stripe" }]}
  ]
}
```

### Agent Live (Onboarding Complete)
```json
{
  "channel": "#onboarding",
  "username": "Syntharra Ops",
  "icon_emoji": ":white_check_mark:",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "✅ Agent Live — {{company_name}}" }},
    { "type": "section", "fields": [
      { "type": "mrkdwn", "text": "*Agent ID:*\n{{agent_id}}" },
      { "type": "mrkdwn", "text": "*Plan:*\n{{plan_type}}" },
      { "type": "mrkdwn", "text": "*Phone:*\n{{phone_number}}" },
      { "type": "mrkdwn", "text": "*Transfer #:*\n{{transfer_number}}" }
    ]},
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "{{timestamp}} • JotForm Onboarding" }]}
  ]
}
```

### Lead Captured (Call Processor)
```json
{
  "channel": "#calls",
  "username": "Syntharra Ops",
  "icon_emoji": ":telephone_receiver:",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "📞 Lead Captured — {{company_name}}" }},
    { "type": "section", "fields": [
      { "type": "mrkdwn", "text": "*Caller:*\n{{caller_name}}" },
      { "type": "mrkdwn", "text": "*Service:*\n{{service_type}}" },
      { "type": "mrkdwn", "text": "*Lead Score:*\n{{lead_score}}/10" },
      { "type": "mrkdwn", "text": "*Call Duration:*\n{{duration}}s" }
    ]},
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "{{timestamp}} • Standard" }]}
  ]
}
```

### Claude Code — E2E Result
```json
{
  "channel": "#claude-code",
  "username": "Claude Code",
  "icon_emoji": ":robot_face:",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "{{status_emoji}} E2E {{tier}} — {{result}}" }},
    { "type": "section", "text": { "type": "mrkdwn", "text": "{{pass_count}} passed • {{fail_count}} failed • {{duration}}" }},
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "{{timestamp}} • {{agent_id}}" }]}
  ]
}
```

### Claude Code — Session Summary
```json
{
  "channel": "#claude-code",
  "username": "Claude Code",
  "icon_emoji": ":memo:",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "📋 Session Complete — {{topic}}" }},
    { "type": "section", "text": { "type": "mrkdwn", "text": "{{summary}}" }},
    { "type": "section", "fields": [
      { "type": "mrkdwn", "text": "*Changes:*\n{{changes}}" },
      { "type": "mrkdwn", "text": "*E2E:*\n{{e2e_result}}" }
    ]},
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "{{timestamp}} • Log: {{log_url}}" }]}
  ]
}
```

---

## Sending from Claude Code (Python)

```python
import os, requests, json
from datetime import datetime, timezone

WEBHOOK = os.environ.get("SLACK_WEBHOOK_OPS", "")

def slack(channel, emoji, title, fields=None, text=None):
    if not WEBHOOK:
        print(f"[SLACK SKIP] {title}")
        return
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": title}}]
    if text:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    if fields:
        blocks.append({"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*{k}:*\n{v}"} for k, v in fields.items()
        ]})
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": ts}]})
    requests.post(WEBHOOK, json={"channel": channel, "username": "Syntharra Ops",
                                  "icon_emoji": emoji, "blocks": blocks})
```

Usage:
```python
slack("#claude-code", ":white_check_mark:", "E2E Standard — 75/75 PASSED",
      fields={"Duration": "2m 14s", "Agent": "TESTING"})

slack("#onboarding", ":moneybag:", "New Payment — Acme HVAC",
      fields={"Plan": "Standard", "Amount": "$497/mo"})
```

---

## Architecture Decisions

| Decision | Chose | Why | Revisit if |
|---|---|---|---|
| Delivery method | Incoming Webhook (no bot) | Simpler setup, no OAuth, no bot token management. Sufficient for one-way notifications | Need 2-way interaction (slash commands, button responses) |
| Single webhook URL | One webhook, channel specified per message | Fewer credentials to manage; one Railway env var | Slack workspace splits across teams |
| Channel per domain | ops-alerts / onboarding / calls / claude-code | Clean separation — Dan can mute #calls without missing #onboarding | More team members with different access needs |
| Blocks format | Slack Block Kit (not plain text) | Structured, scannable on mobile; fields show key:value at a glance | — |
