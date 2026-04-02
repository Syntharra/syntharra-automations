# Syntharra — Decision Log
> Lightweight record of WHY key architectural decisions were made.
> Prevents Claude from re-litigating settled questions.
> Format: Date | Area | Decision | Reason

---

## Infrastructure

| Date | Area | Decision | Reason |
|------|------|----------|--------|
| Pre-2026 | SMS | Telnyx, NOT Twilio | Better pricing for high-volume outbound; Twilio more expensive at scale. SMS pending AI evaluation approval. |
| Pre-2026 | Email | SMTP2GO, NOT SendGrid/Mailgun | Reliable deliverability, simpler API, good pricing for transactional volume |
| Pre-2026 | Hosting | Railway, NOT Vercel/Heroku | Persistent services (n8n needs persistent disk); Vercel is stateless-only |
| Pre-2026 | DB | Supabase, NOT Firebase/PlanetScale | Postgres (relational), built-in RLS, good API, free tier covers pre-launch |
| Pre-2026 | Auth | HTTP Basic Auth on admin | Simple, no OAuth complexity needed for single-admin internal tool |

## Data Model

| Date | Area | Decision | Reason |
|------|------|----------|--------|
| 2026-03 | Supabase | Single table `hvac_standard_agent` for Standard + Premium | Simpler queries, easier reporting; plan_type column differentiates. Confirmed by Dan 2026-04-02. |
| 2026-03 | Retell | Each client gets own cloned agent | Isolation — one client's prompt changes can't affect others |
| 2026-03 | Retell | NEVER delete/recreate agents — always patch | Retell phone number bindings break on recreation; patching preserves all bindings |

## Product

| Date | Area | Decision | Reason |
|------|------|----------|--------|
| Pre-2026 | Pricing | Standard $497/mo, Premium $997/mo | Validated price points for trade businesses; covers CAC + margin |
| Pre-2026 | Market | HVAC USA first, then expand | Largest trade vertical in USA; standardised workflows make replication fast |
| Pre-2026 | Voice AI | Retell AI, NOT Bland/Vapi | Best conversation quality tested; most reliable for trade business use cases |
| Pre-2026 | Checkout | Separate `syntharra-checkout` repo | Keeps billing code isolated; can update pricing page without touching main infra |

## Development

| Date | Area | Decision | Reason |
|------|------|----------|--------|
| 2026-03 | Skills | Stored in /mnt/skills/user + backed up to repo | /mnt is runtime-loaded by Claude; repo is source of truth backup |
| 2026-04 | Docs | Old implementation guides archived to docs/archive/ | Reduce context noise; completed guides add no value to active sessions |
| 2026-04 | Token | Single GitHub token for all Syntharra repos | Simpler; token has org-level scope. Repos must be under Syntharra org to be accessible. |

---
> Add a row whenever a non-obvious decision is made. One line is enough.

## Security

| Date | Area | Decision | Reason |
|------|------|----------|--------|
| 2026-04-02 | Secrets | All API keys via `syntharra_vault` Supabase table, never hardcoded | Prevents exposure in public repos |
| 2026-04-02 | Public repos | `syntharra-automations` + `syntharra-website` public; all others private | automations needs GitHub Pages; skills need public read; no secrets stored in these files |
| 2026-04-02 | GitHub token | Stored in Claude project custom instructions only — never committed to any repo | Token has full org access; exposure = full infrastructure access |
| 2026-04-02 | `syntharra-checkout/env` | Plain-text env file in repo — OK because repo is private; contains only sk_test_ key | Move to Railway env vars before go-live with sk_live_ |

