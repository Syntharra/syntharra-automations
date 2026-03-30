# Session: 2026-03-30 — Skill Library Created

## What Changed
Created 6 new Claude skill files in `skills/` directory:

| Skill | Path | Purpose |
|---|---|---|
| syntharra-website | `skills/syntharra-website/SKILL.md` | Website editing rules, brand, file map, email templates |
| hvac-standard | `skills/hvac-standard/SKILL.md` | Standard pipeline: Retell, n8n, Jotform, Supabase, Stripe |
| hvac-premium | `skills/hvac-premium/SKILL.md` | Premium pipeline: workflows, OAuth, premium Supabase columns |
| syntharra-infrastructure | `skills/syntharra-infrastructure/SKILL.md` | All services: Railway, n8n, Supabase, Stripe, Telnyx, SMTP2GO |
| syntharra-marketing | `skills/syntharra-marketing/SKILL.md` | Lead gen, VSL, demo page, blog SEO, Cal.com |
| syntharra-ops | `skills/syntharra-ops/SKILL.md` | Session rules, GitHub push pattern, ops monitor, email sigs, brand assets |

## Key Details
- All skills include an Auto-Update Rule: Claude must update the relevant skill whenever it completes work in that domain
- Workflow IDs updated to authoritative values from e2e-test skill
- Supabase table list expanded to all 12 tables (was missing: hvac_premium_agent, hvac_premium_call_log, call_processor_dlq, agreement_signatures, affiliate_applications)
- Raw secrets stored in Claude project memory only; GitHub copies use {{PLACEHOLDER}} names with a key map note
