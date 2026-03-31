# Session Log — 2026-03-31 — Email Digest Go-Live

## Summary
Email Intelligence system fully live. Daily 6am GMT workflow scanning 9 inboxes,
Groq AI classifying, saving to Supabase, displaying on admin dashboard.

## What Was Completed

### Email Digest Workflow (n8n ID: 4aulrlX1v8AtWwvC)
- 9 Gmail inboxes: support, sales, solutions, alerts, info, admin, careers, feedback, onboarding
- Groq llama-3.3-70b-versatile classifies emails (free tier)
- Saves high/medium importance emails to Supabase email_digest table
- Idempotent — safe to re-run, deletes existing date+inbox records before insert
- Schedule: 6am GMT daily + Manual Trigger

### Credentials Created in n8n
- Gmail OAuth2 — Support/Sales/Solutions/Alerts/Info/Admin/Careers/Feedback/Onboarding Inbox (9 total)
- Groq API Key (Header Auth)
- Supabase Service Role Key (Header Auth)

### Railway Fix
- Added N8N_EDITOR_BASE_URL=https://n8n.syntharra.com to Railway env vars
- Triggered redeploy — fixed "OAuth callback state is invalid" errors

### n8n Workflow Tags (Organisation)
All 22 workflows tagged by category:
- HVAC Standard: Standard Onboarding, Standard Call Processor
- HVAC Premium: Premium Onboarding, Premium Call Processor, Premium Integration Dispatcher
- Testing & QA: Scenario Test Runner v4, Process Single Scenario, Transcript Generator, E2E Test Cleanup
- Email & Comms: Email Digest, Send Welcome Email, Weekly Newsletter, Unsubscribe Webhook
- Marketing & Leads: Lead → Free Report, Lead → AI Readiness Score, Weekly Lead Report, Newsletter, Unsubscribe
- Billing: Stripe Workflow, Monthly Minutes Calculator, Usage Alert Monitor
- Operations: Nightly GitHub Backup, Auto-Enable MCP, Publish Retell Agent

### Key Technical Notes
- n8n Code nodes block $env access — use hardcoded key or this.helpers.httpRequest
- this.getCredentials() not available in Code node sandbox — must inline keys
- $input.first().json works better than named node references for Groq prompt passing
- Groq requires max_tokens/temperature as numbers not strings in keypair body mode
- Use specifyBody: json with jsonBody object for proper type handling
- N8N_EDITOR_BASE_URL required for OAuth callback state to work on self-hosted n8n

## Files Changed
- docs/email-digest-workflow.json — final working version
- docs/session-logs/2026-03-31-email-digest-golive.md — this file
