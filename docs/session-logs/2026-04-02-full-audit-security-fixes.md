# Session Log — 2026-04-02 — Full Repo Audit & Security Fixes

## Trigger
Dan asked: audit all repos and confirm whether public repos need to go private.

## Key Finding: Secrets in Public Repos — FIXED

### What was found
| File (public repo) | Secret | Risk |
|---|---|---|
| docs/context/AGENTS.md | Retell API key `key_0157...` | Anyone could impersonate Syntharra's voice agent |
| docs/context/STRIPE.md | Stripe webhook signing secret `whsec_...` | Could forge Stripe webhook events |
| shared/e2e-test.py | Retell API key hardcoded | Same as above |
| shared/e2e-test-premium.py | Retell API key hardcoded | Same |
| tools/auto-fix-loop.py | Retell API key hardcoded | Same |
| tools/openai-agent-simulator.py | Retell key as env fallback | Same |
| ops-monitor/CLAUDE.md (private) | GitHub token `ghp_...` | Full org infrastructure access |

### All fixed — replaced with vault lookups or env var references

## Repo Visibility Decision

### syntharra-automations — CAN STAY PUBLIC (after fixes above)
- No secrets remain after fixes
- Price IDs and product IDs are NOT secrets (public-facing Stripe identifiers)
- SUPABASE.md hits were field name strings, not actual keys
- GitHub Pages requires public for free hosting
- Skills need to be readable by Claude's infrastructure

### syntharra-website — CAN STAY PUBLIC
- Static HTML/CSS only
- No credentials anywhere
- GitHub Pages hosting requires public

### All 5 others — MUST STAY PRIVATE ✅ (already are)
- syntharra-checkout: has plain-text env file with sk_test_ Stripe key
- syntharra-oauth-server: OAuth client secrets in Railway env vars (safe, but code is sensitive)
- syntharra-admin: admin credentials in server.js fallback
- syntharra-ops-monitor: monitoring logic, internal URLs
- syntharra-artifacts: internal UI components

## Private Repo Audit Findings

### syntharra-admin
- 3 HTML files in public/: index.html, calls.html, email.html
- Knowledge base in server.js is comprehensive and current
- No issues found

### syntharra-checkout  
- Price IDs match STRIPE.md ✅
- Success URL redirects to correct Jotform URLs ✅
- ⚠️ Plain-text `env` file with sk_test_ key — needs moving to Railway env before go-live

### syntharra-oauth-server
- Supports: Google Calendar, Outlook, Calendly, Jobber, HubSpot
- Deployed at auth.syntharra.com
- All secrets via Railway env vars ✅

### syntharra-ops-monitor
- Deployed at syntharra-ops-monitor-production.up.railway.app (no custom domain)
- Currently PAUSED
- Fixed: removed hardcoded GitHub token from CLAUDE.md

### syntharra-artifacts
- 6 folders: admin, brand, client-dashboard, emails, sales, website
- React JSX components for Claude chat previews
- Has own SKILL.md at repo root

## Files Changed
- syntharra-automations/docs/context/AGENTS.md (Retell key → vault)
- syntharra-automations/docs/context/STRIPE.md (webhook secret → vault)
- syntharra-automations/shared/e2e-test.py (key → env var)
- syntharra-automations/shared/e2e-test-premium.py (key → env var)
- syntharra-automations/tools/auto-fix-loop.py (key → env var)
- syntharra-automations/tools/openai-agent-simulator.py (key fallback removed)
- syntharra-automations/CLAUDE.md (service URLs added, artifacts skill ref fixed)
- syntharra-automations/docs/DECISIONS.md (Security section added)
- syntharra-automations/docs/FAILURES.md (4 security failures logged)
- syntharra-automations/docs/TASKS.md (updated)
- syntharra-ops-monitor/CLAUDE.md (GitHub token removed)
