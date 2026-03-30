# Session Log — 2026-03-30 (VPS Migration — COMPLETE)

## Status: LIVE

## What Was Completed This Session
- Railway Pro plan upgraded
- Created syntharra-n8n, n8n-postgres, n8n-redis services on Railway
- Diagnosed and fixed deployment issue (switched from custom Dockerfile to n8nio/n8n:latest image)
- n8n live at https://n8n.syntharra.com (custom domain, SSL, 200 OK)
- All 19 workflows imported from n8n Cloud
- Stripe webhook updated to https://n8n.syntharra.com/webhook/syntharra-stripe-webhook
- N8N_HOST and WEBHOOK_URL updated to n8n.syntharra.com

## Railway Service IDs
- syntharra-n8n: c40f1306-0544-4915-a304-f33fdb8d4385
- n8n-postgres: 97e13df6-6a68-435e-95db-47fd03c10fe3
- n8n-redis: 9285c656-12b4-44f5-8338-9b569c5e42dc

## Remaining (Cannot be automated)
1. Re-enter ALL credentials in https://n8n.syntharra.com UI:
   - Retell API key
   - Supabase URL + service key
   - Stripe webhook signing secret
   - SMTP2GO (host: mail.smtp2go.com, port: 2525, user: syntharra.com)
   - Jotform API key
   - GitHub token
   - Google Calendar OAuth (Premium)
   - Jobber OAuth (Premium)
2. Update Jotform Standard form webhook manually (API key has read-only permissions):
   - Old: https://syntharra.app.n8n.cloud/webhook/jotform-hvac-onboarding
   - New: https://n8n.syntharra.com/webhook/jotform-hvac-onboarding
3. Activate all 19 workflows in new n8n UI (toggle each one on)
4. Test end-to-end (test Stripe checkout, test Jotform submit, make test call)
5. Cancel n8n Cloud subscription (only after testing confirmed)

## "Dangerous site" warning on n8n.syntharra.com
Google Safe Browsing flags new domains. Not actually unsafe. Resolves in 24-48h.
Can bypass by clicking Details > Visit this unsafe site.
