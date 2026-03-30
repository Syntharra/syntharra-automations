# Session Log — 2026-03-30 (Groq AI + Key Management)

## Changes Made

### 1. Daily Digest Time
- Changed from 8am to 6am GMT (Europe/London)
- File: syntharra-ops-monitor/src/config.js
- Cron: '0 8 * * *' → '0 6 * * *'
- Commit: 47f30e22

### 2. Groq AI Assistant — Activated
- Groq API key received from Dan: gsk_***REDACTED***
- Stored in Supabase syntharra_vault: service_name='Groq', key_type='api_key'
- Added to Railway syntharra-admin service env vars: GROQ_API_KEY
- Railway auto-redeployed — AI assistant now shows ● Ready
- Model: llama-3.3-70b-versatile (free tier)

### 3. server.js — Full Syntharra Knowledge Base Embedded
- Company info, pricing, discount codes
- Every n8n workflow ID and purpose
- All Supabase tables and their purpose
- Full onboarding process (Standard + Premium)
- Email address routing rules
- Current platform status / go-live checklist
- Client support guidelines for staff
- Common troubleshooting Q&A
- Retell rules (critical — never delete agents)
- /api/ai endpoint proxies to Groq (key stays server-side, never exposed to browser)
- /api/health endpoint returns {status, ai_configured, ts}
- Commits: server.js 03ab3d16, index.html fda12d38

### 4. API Key Management Rule Established
- Rule: Any API key Dan provides must be IMMEDIATELY stored in syntharra_vault AND Railway env vars
- Added to Claude memory (slot 16)
- Vault access: requires Supabase service role key (retrieved from Railway ops-monitor env vars)
- Supabase service role key location: Railway → syntharra-ops-monitor → Variables → SUPABASE_SERVICE_KEY

### 5. Supabase Vault — Known Entries (as of this session)
service_name       | key_type
-------------------|------------------
Groq               | api_key
Retell AI          | api_key
Retell AI          | agent_id_arctic_breeze
Retell AI          | agent_id_demo_jake
Retell AI          | agent_id_demo_sophie
Retell AI          | conversation_flow_id
Retell AI          | phone_number
Supabase           | project_url
Supabase           | service_role_key
GitHub             | personal_access_token
Stripe             | product_id_standard
Stripe             | product_id_premium
Stripe             | price_standard_monthly
Stripe             | price_standard_annual
Stripe             | price_standard_setup
Stripe             | price_premium_monthly
Stripe             | price_premium_annual
Stripe             | price_premium_setup
Stripe             | coupon_founding_standard
Stripe             | coupon_founding_premium
Stripe             | webhook_url
Stripe             | webhook_id
Jotform            | api_key
Jotform            | form_id_standard
Jotform            | form_id_premium
Jotform            | webhook_standard_new
SMTP2GO            | api_key
Railway            | api_token
Railway            | project_id
Railway            | service_id_n8n
Railway            | service_id_checkout
Railway            | service_id_ops_monitor
n8n Railway        | instance_url
n8n Railway        | api_key

## How to Retrieve Any Key in Future Sessions
```python
import requests
SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
# Get service role key from Railway ops-monitor vars first, then:
res = requests.get(
    f"{SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.Groq&key_type=eq.api_key&select=key_value",
    headers={"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}
)
key = res.json()[0]['key_value']
```

## Admin Dashboard — Final State (this session)
- URL: https://admin.syntharra.com
- Login: admin / Syntharra2026!
- AI Assistant: ● Ready (Groq llama-3.3-70b, free tier)
- All times: Europe/London (GMT)
- Clients: search bar + HVAC/Plumbing/Electrical tabs + Standard/Premium split
- Forms: live Jotform data
- Marketing: live Supabase website_leads
- Favicons: deployed
- Quick Actions bar on Overview

## Commits This Session
- syntharra-admin/server.js: 03ab3d16 (Groq proxy + knowledge base)
- syntharra-admin/public/index.html: fda12d38 (AI fix + dashboard polish)
- syntharra-ops-monitor/src/config.js: 47f30e22 (6am digest)
- syntharra-ops-monitor/src/config.js: 24bec47d (GMT timezone)
- syntharra-ops-monitor/src/index.js: bb3f71ba (GMT cron)
- syntharra-automations/docs/project-state.md: fd180d1d
- syntharra-automations/docs/session-logs/2026-03-30-admin-dashboard-groq-ai.md: 272fdf43
