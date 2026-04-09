# n8n Workflow Audit — 2026-04-09

**Total workflows:** 56  |  **Active:** 24  |  **Already archived:** 31  |  **Inactive (unarchived):** 1

## Active workflows — verdicts

| Verdict | ID | Name | Last updated |
|---|---|---|---|
| **ARCHIVE (Premium retired)** | `rGrnCr5mPFP2TIc7` | Premium Dispatcher — Google Calendar | 2026-04-03 |
| **ARCHIVE (Premium retired)** | `La99yvfmWg6AuvM2` | Premium Dispatcher — Outlook | 2026-04-03 |
| **ARCHIVE (Premium retired)** | `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher | 2026-04-07 |
| **ARCHIVE (Premium retired)** | `5vphecmEhxnwFz2X` | Premium — Daily Token Refresh | 2026-04-06 |
| **ARCHIVE (Premium retired)** | `a0IAwwUJP4YgwgjG` | Premium — Integration Connected Handler | 2026-04-06 |
| **INVESTIGATE** | `AU8DD5r6i6SlYFnb` | Auto-Enable MCP on All Workflows | 2026-03-31 |
| **INVESTIGATE** | `j8hExewOREmRp3Oq` | Blog Auto-Publisher | 2026-03-31 |
| **INVESTIGATE** | `Kg576YtPM9yEacKn` | HVAC Call Processor - Retell Webhook (Supabase) | 2026-04-08 |
| **INVESTIGATE** | `z8T9CKcUp7lLVoGQ` | Slack Setup — Internal Admin Form | 2026-04-03 |
| **INVESTIGATE** | `6LXpGffcWSvL6RxW` | Weekly Newsletter - Syntharra | 2026-04-06 |
| **MIGRATE → Claude cron** | `SiMn59qJOfrZZS81` | Daily Ops Digest — 6am → #all-syntharra | 2026-04-03 |
| **MIGRATE → Claude cron** | `iLPb6ByiytisqUJC` | HVAC Weekly Lead Report (Supabase) | 2026-04-03 |
| **MIGRATE → Claude cron** | `z1DNTjvTDAkExsX8` | Monthly Minutes Calculator & Overage Billing | 2026-04-01 |
| **MIGRATE → Claude cron** | `Wa3pHRMwSjbZHqMC` | Usage Alert Monitor (80% & 100% Warnings) | 2026-04-06 |
| **KEEP (webhook / event)** | `syGlWx8TlbYlPZU4` | Affiliate Application — HubSpot Contact | 2026-04-03 |
| **KEEP (webhook / event)** | `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed Delete | 2026-04-01 |
| **KEEP (webhook / event)** | `4Hx7aRdzMl5N0uJP` | HVAC AI Receptionist - JotForm Onboarding (Supabase) | 2026-04-09 |
| **KEEP (webhook / event)** | `LF8ZSYyQbmjV4rN0` | Jotform Webhook Backup Polling | 2026-04-04 |
| **KEEP (webhook / event)** | `Eo8wwvZgeDm5gA9d` | Newsletter Unsubscribe Webhook | 2026-03-31 |
| **KEEP (webhook / event)** | `Y1EptXhOPAmosMbs` | Retell Calls Proxy | 2026-04-08 |
| **KEEP (webhook / event)** | `xKD3ny6kfHL0HHXq` | Stripe Webhook Hardened | 2026-04-07 |
| **KEEP (webhook / event)** | `I8a2N9bIZp9Qg1IN` | Website Lead — HubSpot Contact (Index + Calculator + Quiz) | 2026-04-03 |
| **KEEP (webhook / event)** | `QY1ZFtPJFsU5h6wQ` | Website Lead → AI Readiness Score Email | 2026-04-06 |
| **KEEP (webhook / event)** | `hFU0ZeHae7EttCDK` | Website Lead → Free Report Email | 2026-04-06 |

## Inactive but not archived (stragglers)

| ID | Name | Verdict |
|---|---|---|
| `kz1VmwNccunRMEaF` | HVAC Prem Onboarding | ARCHIVE (Premium retired) |

## Counts by verdict

- **ARCHIVE (Premium retired)**: 5
- **KEEP (webhook / event)**: 10
- **MIGRATE → Claude cron**: 4
- **INVESTIGATE**: 5
- **UNCLASSIFIED — check**: 0

## Cron → Claude Code migration candidates (detailed)

These run on a schedule, not a webhook, and would be simpler/more reliable as Claude Code scheduled tasks (`CronCreate`). Plan:

- **Usage Alert Monitor (80% & 100% Warnings)** (`Wa3pHRMwSjbZHqMC`) — schedule + purpose TBD after inspection. Migration = write a Python script + `CronCreate` trigger, then archive the n8n workflow.
- **HVAC Weekly Lead Report (Supabase)** (`iLPb6ByiytisqUJC`) — schedule + purpose TBD after inspection. Migration = write a Python script + `CronCreate` trigger, then archive the n8n workflow.
- **Daily Ops Digest — 6am → #all-syntharra** (`SiMn59qJOfrZZS81`) — schedule + purpose TBD after inspection. Migration = write a Python script + `CronCreate` trigger, then archive the n8n workflow.
- **Monthly Minutes Calculator & Overage Billing** (`z1DNTjvTDAkExsX8`) — schedule + purpose TBD after inspection. Migration = write a Python script + `CronCreate` trigger, then archive the n8n workflow.