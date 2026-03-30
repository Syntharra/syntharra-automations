# Session: 2026-03-30 — syntharra_vault Credential Store

## What Changed
- Created `syntharra_vault` Supabase table as the single source of truth for all API keys
- Updated all 6 skill files with vault access rule and code pattern
- Updated project-state.md: syntharra_vault added to tables list, API Keys Reference section updated
- Rule: NEVER store keys in skill files, project memory, session logs, or anywhere else

## Vault Access Pattern
Query: `GET /rest/v1/syntharra_vault?service_name=eq.{name}&select=key_value`
Auth: Supabase service role key (Project Settings → API)

## Known service_name values to populate
retell, n8n_railway, github, jotform, smtp2go, railway, stripe_webhook_secret, supabase_service_role, telnyx
