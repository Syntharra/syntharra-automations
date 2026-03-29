# Session Log: March 29, 2026 — Ops Monitor Build & Deploy

## Summary
Built, deployed, and debugged the Syntharra 24/7 Ops Monitor on Railway. 11 monitor systems, 75+ individual checks, live at syntharra-ops-monitor-production.up.railway.app.

## What Was Built
- **GitHub Repo:** Syntharra/syntharra-ops-monitor (23 files)
- **Railway Service:** syntharra-ops-monitor (auto-deploys from GitHub)
- **11 Monitor Systems:** Retell AI, n8n, Supabase, Stripe, Jotform, Pipeline (E2E), CRM/Calendar, Infrastructure, Client Health, Revenue & Metrics, Email & SMS

## Key Findings & Fixes
1. **Retell is_published is NOT a health indicator** — agents work immediately after creation via API. is_published only tracks version snapshots. No manual publish step needed for onboarding pipeline.
2. **Retell API uses v2 endpoints** — /v2/list-calls (not /list-calls), filter_criteria is an object not array. Simpler to fetch all and filter in code.
3. **CRITICAL BUG FOUND & FIXED:** Infrastructure monitor was POSTing to webhook endpoints to check health — this triggered actual n8n workflow processing and created ghost Supabase entries + ghost Retell agents. Fixed to HEAD requests.
4. **Stripe key was pk_test_ (publishable)** — needed sk_test_ (secret). Copied from checkout service via Railway API.
5. **Jotform Standard v2 form** (260812373840657) was a deleted test form with 0 submissions. Removed from config and project-state.md.
6. **Twilio → Telnyx migration** — removed Twilio SDK, replaced with Telnyx REST API. Env vars updated on Railway.

## Data Cleaned
- 4x "Polar Peak HVAC TEST" rows from hvac_standard_agent
- 4x "HVAC Company" ghost rows from hvac_standard_agent (created by webhook bug)
- 4x blank ghost rows from hvac_premium_agent (created by webhook bug)
- 8x ghost Retell agents deleted
- Only Arctic Breeze HVAC remains as the single real test client

## Railway Configuration
- Project: victorious-abundance (bf04f61c-84d9-4c99-bd54-497d3f357070)
- Service: syntharra-ops-monitor (7ce0f943-5216-4a16-8aeb-794cc7cc1e65)
- Environment: production (5303bcf8-43a4-4a95-8e0c-75909094e02e)
- Railway API token saved to Claude memory for direct management
- Env vars: RETELL_API_KEY, N8N_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, STRIPE_SECRET_KEY (sk_test_), JOTFORM_API_KEY, SMTP2GO creds, TELNYX placeholders, RAILWAY_TOKEN

## Monitor Check Intervals
- Retell AI: every 5 min
- n8n: every 10 min
- Supabase, Stripe, Jotform, Pipeline, CRM: every 15 min
- Infrastructure: every 5 min
- Clients: every 30 min
- Email/SMS: every 30 min
- Revenue: every 6 hours
- Daily digest email: 8 AM CT

## Alert Tiers
- Dashboard: everything
- Email (admin@syntharra.com): warnings + critical + daily digest
- SMS (Telnyx, when approved): critical only
- 15-minute cooldown on all alerts

## Memory Updates
- Railway API token added (memory #21)
- Jotform v2 reference marked as deleted (memory #13)
- SMS switched from Twilio to Telnyx across all docs

## Files Changed
- syntharra-ops-monitor: 23 files (full new repo)
- syntharra-automations/docs/project-state.md: updated with ops monitor details
