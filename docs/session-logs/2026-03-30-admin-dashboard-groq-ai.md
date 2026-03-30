# Session Log — 2026-03-30 (Admin Dashboard & AI Assistant)

## Changes Made

### 1. Admin Dashboard — Clients Section Rebuilt
- Added search bar (filters by company, agent name, trade)
- Added trade tabs: All / HVAC / Plumbing / Electrical / Other
- Split clients into Standard and Premium groups with separate tables
- Added direct ↗ Dashboard link per client row
- Nav badge now dynamic (hidden when 0 clients)

### 2. Admin Dashboard — Forms Section
- Replaced all hardcoded fake submissions with live Jotform API
- Fetches Standard (260795139953066) and Premium (260819259556671) forms
- Filters out DELETED/test submissions automatically
- Nav badge shows live pending count

### 3. Admin Dashboard — Marketing Pipeline
- Replaced hardcoded pipeline cards with live Supabase website_leads data
- KPI cards (Sourced, Emailed, Hot Leads, Demos) from real data

### 4. Admin Dashboard — System Health
- Replaced hardcoded metrics with live Supabase call log calculations
- Uptime card wired to ops monitor live status

### 5. Admin Dashboard — UI Polish
- Quick Actions bar added to Overview (n8n, Supabase, Stripe, Retell, Jotform, AI links)
- New Client button links to Jotform onboarding form
- Call log timestamps show date + time with GMT timezone
- Stripe Mode card has amber left border warning
- noindex/nofollow meta tag added
- All times now display in Europe/London (GMT) timezone (en-GB locale)

### 6. Admin Dashboard — Favicons
- favicon.svg and favicon-white.svg copied from syntharra-website to syntharra-admin/public/
- Link tags added to index.html head
- Works on custom domain admin.syntharra.com

### 7. AI Assistant — Fixed & Upgraded to Groq
- Was broken: was calling Anthropic API directly from browser (no key, CORS blocked)
- Fixed: all AI calls now proxy through /api/ai on Express server.js
- Switched from Anthropic to Groq (free tier, llama-3.3-70b-versatile)
- Full Syntharra knowledge base embedded in server.js system prompt:
  - Company info, pricing, discount codes
  - Every n8n workflow ID and purpose
  - All Supabase tables
  - Onboarding process (Standard + Premium)
  - Email addresses and routing rules
  - Current status / go-live checklist
  - Client support guidelines
  - Common troubleshooting Q&A
  - Retell rules (critical)
- Live dashboard context (clients, calls, billing, KPIs) injected per request
- /api/health endpoint added (returns ai_configured flag)
- UI shows ● Ready / ● Not configured / ● Offline status
- Activation: add GROQ_API_KEY to Railway syntharra-admin env vars

### 8. Daily Digest Time
- Changed from 8am GMT to 6am GMT (Europe/London)
- ops-monitor/src/config.js: cron updated from '0 8 * * *' to '0 6 * * *'

### 9. Timezone — All Personal Timezones Set to GMT
- ops-monitor/src/index.js: all 12 cron schedules changed from America/Chicago → Europe/London
- ops-monitor/src/config.js: digest hour updated, comments updated
- admin dashboard: all toLocaleTimeString/toLocaleDateString → timeZone: Europe/London, locale en-GB
- project-state.md: timezone references updated

## Pending (manual steps for Dan)
1. Get free Groq API key: https://console.groq.com → create key
2. Add to Railway: syntharra-admin service → Variables → GROQ_API_KEY = gsk_...
3. Railway will auto-redeploy — AI shows ● Ready

## Commits
- syntharra-admin server.js: 03ab3d16
- syntharra-admin index.html: fda12d38
- syntharra-ops-monitor config.js: 47f30e22 (6am digest)
- syntharra-ops-monitor config.js: 24bec47d (GMT timezone)
- syntharra-ops-monitor index.js: bb3f71ba (GMT cron)
- syntharra-automations project-state.md: fd180d1d
