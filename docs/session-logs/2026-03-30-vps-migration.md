# Session Log — 2026-03-30

## Summary
Migrated n8n from n8n Cloud (Starter, 2500 exec/mo) to self-hosted Railway.

## What Was Done
- Upgraded Railway account to Pro plan
- Created 3 new services in Syntharra Railway project:
  - `syntharra-n8n` (service ID: c40f1306-0544-4915-a304-f33fdb8d4385)
  - `n8n-postgres` (service ID: 97e13df6-6a68-435e-95db-47fd03c10fe3)
  - `n8n-redis` (service ID: 9285c656-12b4-44f5-8338-9b569c5e42dc)
- Set all environment variables on n8n service (all secrets stored in Railway env vars only)
- Fixed deployment: switched from custom Dockerfile to `n8nio/n8n:latest` image directly
  - Root cause: Railway injects PORT dynamically; custom Dockerfile was ignoring it
  - Fix: use official image directly, set PORT=5678 and N8N_PORT=5678 explicitly as env vars
- n8n is LIVE at: https://syntharra-n8n-production.up.railway.app (200 OK confirmed)
- Exported all 19 workflows from n8n Cloud to /n8n-backup-2026-03-30/

## Remaining Steps
1. Go to https://syntharra-n8n-production.up.railway.app — create owner account
2. Add CNAME in Cloudflare: n8n.syntharra.com -> syntharra-n8n-production.up.railway.app
3. Re-enter all credentials in new n8n UI (Retell, Supabase, Stripe, SMTP2GO, Jotform, GitHub, Google Calendar, Jobber)
4. Generate n8n API key in new instance -> give to Claude to import all 19 workflows
5. Update webhook URLs: Stripe, Jotform, Retell -> new n8n URL
6. Test end-to-end
7. Cancel n8n Cloud

## n8n Cloud Status
Still active. DO NOT cancel until Railway is fully tested and all webhooks updated.
