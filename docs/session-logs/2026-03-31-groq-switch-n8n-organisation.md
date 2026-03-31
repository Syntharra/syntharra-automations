# Session Log: 2026-03-31 — Groq Switch + n8n Organisation

## Changes Made

### Blog Auto-Publisher — Switched to Groq
- Model changed from Anthropic Claude to Groq `llama-3.3-70b-versatile` (free tier)
- Groq API key sourced from `syntharra_vault` (already stored)
- Workflow ID: `j8hExewOREmRp3Oq` — ACTIVE, running Mon/Wed/Fri 9AM
- First article published live via end-to-end Python test:
  - URL: https://syntharra.com/blog/hvac-after-hours-answering.html
  - Topic ID 1 marked published in Supabase `blog_topics`
- All credentials wired inline (Groq key, Supabase service role, GitHub token)
- Cost: $0/month

### n8n Workflow Organisation
- 9 tags created/confirmed across all 23 active workflows:
  | Tag | ID |
  |---|---|
  | HVAC Standard | 19YQ7quHM907cfex |
  | HVAC Premium | Eb4XKFHskbuD3gXT |
  | Testing & QA | Du87oYr5lvuWOoT3 |
  | Email & Comms | KbkkTjDhj2TlVB4I |
  | Marketing & Leads | tRRK7AmO0v6TDIQt |
  | Operations | TNhP9LhDssgIJ5Jk |
  | Billing | AHi4xBZNzlUXe9nF |
  | Blog & Content | 2A4WoDoHAcCcd0No |
  | Retell & Calls | JjYhOuIIp0gFr8Qq |
- Tags applied to all 23 active workflows (see mapping below)
- 3 inactive duplicate workflows archived:
  - S3vHBQopDiOssM7G (Email Digest duplicate)
  - AZZguGm5ypF6e5m9 (Blog Auto-Publisher old duplicate)
  - TZ4p1UyzTrCJPdKA (Email Digest duplicate)
- Note: n8n folder API not available in current Railway build — tags are equivalent

### Workflow Tag Mapping
| Workflow | ID | Tags |
|---|---|---|
| HVAC Standard Onboarding | 4Hx7aRdzMl5N0uJP | HVAC Standard |
| HVAC Standard Call Processor | Kg576YtPM9yEacKn | HVAC Standard, Retell & Calls |
| HVAC Premium Onboarding | kz1VmwNccunRMEaF | HVAC Premium |
| HVAC Premium Call Processor | STQ4Gt3rH8ptlvMi | HVAC Premium, Retell & Calls |
| Premium Integration Dispatcher | 73Y0MHVBu05bIm5p | HVAC Premium |
| HVAC Scenario Test Runner v4 | Ex90zUMSEWwVk4Wv | Testing & QA |
| HVAC Scenario: Process Single | eZHkfu9EYKHFoig0 | Testing & QA |
| HVAC Scenario Transcript Gen | ccOxdvghTsNqX8x0 | Testing & QA |
| E2E Test Cleanup | URbQPNQP26OIdYMo | Testing & QA |
| Email Digest — Daily 6am GMT | 4aulrlX1v8AtWwvC | Email & Comms |
| Send Welcome Email (Manual) | lXqt5anbJgsAMP7O | Email & Comms |
| Weekly Newsletter | 6LXpGffcWSvL6RxW | Email & Comms, Marketing & Leads |
| Newsletter Unsubscribe Webhook | Eo8wwvZgeDm5gA9d | Email & Comms, Marketing & Leads |
| Website Lead → Free Report | hFU0ZeHae7EttCDK | Marketing & Leads |
| Website Lead → AI Score | QY1ZFtPJFsU5h6wQ | Marketing & Leads |
| HVAC Weekly Lead Report | iLPb6ByiytisqUJC | HVAC Standard, Marketing & Leads |
| Stripe Workflow | xKD3ny6kfHL0HHXq | Billing |
| Monthly Minutes Calculator | z1DNTjvTDAkExsX8 | Billing |
| Usage Alert Monitor | Wa3pHRMwSjbZHqMC | Billing, Operations |
| Nightly GitHub Backup | 44WfbVmJ7Zihcwgs | Operations |
| Auto-Enable MCP | AU8DD5r6i6SlYFnb | Operations |
| Publish Retell Agent | 13cOIXxvj83NfDqQ | Operations, Retell & Calls |
| Blog Auto-Publisher | j8hExewOREmRp3Oq | Blog & Content |
