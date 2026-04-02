# Syntharra — Claude Master Brief

> Fetch this file **first** at the start of every Syntharra chat session.
> It is intentionally short. It tells you exactly which context files to load next.

## Who you are working with
**Dan** — Founder & CEO of Syntharra. Prefers concise direct responses.
OCD about brand consistency. Delegates all technical work to Claude.

## What Syntharra is
Global AI Solutions company. Core product: fully automated AI phone receptionist
for trade businesses (HVAC, plumbing, electrical etc). Built on Retell AI.
Sold as Standard ($497/mo) and Premium ($997/mo). Currently pre-launch, TEST MODE.

## Non-negotiable rules (memorise these)
1. NEVER delete or recreate a Retell agent — always patch in place
2. ALWAYS publish after any Retell API update
3. ALL emails LIGHT THEME — white cards, #F7F7FB outer bg, #1A1A2E text, #6C63FF accent
4. NEVER use `daniel@syntharra.com` in any workflow, email, or website
5. NEVER use base64 SVG in emails — always hosted PNG
6. Edit files with str.replace — never rewrite from scratch
7. ONE `<style>` block per HTML page, `overflow-x:clip` on body
8. Push all changes to GitHub before chat ends
9. Update relevant skill(s) after any verified work
10. Update `docs/TASKS.md` at end of every chat

## Context files — load what you need
| What you're working on | Files to fetch |
|---|---|
| Any session (always) | `docs/TASKS.md` |
| Agents, calls, Retell | `docs/context/AGENTS.md` |
| n8n workflows | `docs/context/WORKFLOWS.md` |
| Stripe billing | `docs/context/STRIPE.md` |
| Supabase tables | `docs/context/SUPABASE.md` |
| Infrastructure / Railway | `docs/context/INFRA.md` |
| Artifacts / UI previews | `docs/context/ARTIFACTS.md` |
| Pre-launch status | `docs/context/LAUNCH.md` |

## Skill files — load by area of work
| Area | Skill |
|---|---|
| Admin dashboard | `syntharra-admin` |
| Client dashboard | `syntharra-client-dashboard` |
| Website | `syntharra-website` |
| Retell / agents | `syntharra-retell` |
| n8n / infra | `syntharra-infrastructure` |
| Emails | `syntharra-email` |
| Stripe | `syntharra-stripe` |
| HVAC Standard | `hvac-standard` |
| HVAC Premium | `hvac-premium` |
| Ops / session rules | `syntharra-ops` |
| Marketing | `syntharra-marketing` |
| Artifacts / brand | `syntharra-artifacts` repo SKILL.md |
| Brand / visual identity | `syntharra-brand` |
| E2E test — Standard HVAC | `e2e-hvac-standard` |

## GitHub repos
| Repo | Purpose |
|---|---|
| `syntharra-automations` | All ops code, skills, docs, n8n backups |
| `syntharra-website` | syntharra.com (GitHub Pages) |
| `syntharra-admin` | admin.syntharra.com (Railway) |
| `syntharra-checkout` | Stripe checkout server (Railway) |
| `syntharra-oauth-server` | Premium OAuth (Railway) |
| `syntharra-ops-monitor` | 24/7 monitor (Railway, PAUSED) |
| `syntharra-artifacts` | Claude chat artifact files |

## Scaling Architecture
- Each client gets their own Retell agent cloned via Retell API
- Triggered by Jotform submission → n8n onboarding workflow
- Client config stored in `hvac_standard_agent` Supabase table (single table for Standard + Premium)
- Current focus: HVAC contractors USA. Expansion: plumbing, electrical, cleaning — same system, one parameter change
- SMS via Telnyx (pending approval). NOT Twilio.

## Brand tokens (quick reference)
- Violet: `#6C63FF` | Cyan: `#00D4FF` | Dark: `#1A1A2E`
- Font: DM Sans (UI) | Email font: Inter
- Logo: 4 ascending bars, flat `#6C63FF` — NEVER emoji substitute
- Icon URL: `https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png`
