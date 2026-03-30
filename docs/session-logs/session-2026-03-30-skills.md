# Session: 2026-03-30 — Full Skill Library Built

## 9 skills created in skills/ directory

- syntharra-website: Website editing, brand, file map, CSS rules
- hvac-standard: Standard pipeline, workflows, Jotform, Supabase, Stripe
- hvac-premium: Premium pipeline, OAuth, premium Supabase columns
- syntharra-infrastructure: Railway, n8n, Supabase, Stripe, Telnyx, SMTP2GO
- syntharra-marketing: Lead gen, VSL, demo page, blog, Google Ads
- syntharra-ops: Session rules, GitHub push, ops monitor, signatures
- syntharra-retell: Agents, prompts, flows, publishing, API patterns
- syntharra-email: Templates, SMTP2GO, address routing, logo block
- syntharra-stripe: Products, prices, coupons, webhooks, live mode checklist

## Key Decisions
- Client agents NOT in skills - live in Supabase only
- Arctic Breeze = test agent only, not a real client
- Auto-update rule = fundamental changes only, not routine work
- Canonical syntharra_vault snippet in all 9 skills
- No raw keys stored anywhere - always query syntharra_vault
