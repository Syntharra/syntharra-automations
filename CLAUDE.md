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
6. Edit files with str_replace — never rewrite from scratch
7. ONE `<style>` block per HTML page, `overflow-x:clip` on body
8. Push all changes to GitHub before chat ends
9. **Update relevant skill(s) after ANY verified work — no exceptions, no skipping**
10. Update `docs/TASKS.md` at end of every chat

## SELF-IMPROVEMENT — MANDATORY, NOT OPTIONAL
> This is the most important long-term rule. Every session must make Claude smarter.
> Skill files are the permanent brain. FAILURES.md is the audit trail.
> If you fixed something, learned something, or hit a gotcha — it goes in the skill. Always.

### Hard trigger rule — if you touched it, you update it
| If you worked on... | Update this skill |
|---|---|
| Railway, n8n, ops monitor, env vars, deploys | `syntharra-infrastructure` |
| Retell agents, conversation flows, prompts | `syntharra-retell` |
| Emails, SMTP2GO, alert templates | `syntharra-email` |
| Stripe, billing, pricing, webhooks | `syntharra-stripe` |
| HubSpot CRM, pipeline stages, contacts | `syntharra-hubspot` |
| Website, landing pages, HTML/CSS | `syntharra-website` |
| HVAC Standard pipeline, onboarding | `hvac-standard` |
| HVAC Premium pipeline, onboarding | `hvac-premium` |
| E2E tests, scenario runner, simulators | `e2e-hvac-standard` or `e2e-hvac-premium` |
| Client dashboard | `syntharra-client-dashboard` |
| Marketing, lead gen, newsletter | `syntharra-marketing` |

### What goes in a skill update
- Correct API patterns (with working examples)
- Things that look right but are wrong (e.g. Railway `where:` vs `input:`)
- Rate limits, quotas, intervals to stay within
- Gotchas discovered during debugging
- Confirmed working mutations/queries
- Things NOT to do and why

### What goes in FAILURES.md
Every new failure/fix gets a row: `date | area | what failed | root cause | fix applied | skill updated`
- Log it even if the fix was trivial
- Mark skill updated = YES/NO — if NO, update the skill before closing

### Self-improvement checklist — run before EVERY session end
- [ ] Did I fix a bug? → Root cause in FAILURES.md + gotcha in skill
- [ ] Did I learn a correct API pattern? → Add to skill with working example
- [ ] Did I discover something that doesn't work? → Add "do NOT do X" to skill
- [ ] Did I change any config/IDs/URLs? → Update skill tables
- [ ] Are skill files richer than when I started this session? → If no, do it now

---

## Session startup — always load these 3
```python
claude_md   = fetch("CLAUDE.md")
tasks_md    = fetch("docs/TASKS.md")
failures_md = fetch("docs/FAILURES.md")
```

## Context files — load what you need
| What you're working on | File to fetch |
|---|---|
| Any session (always) | `docs/TASKS.md`, `docs/FAILURES.md` |
| Architectural decisions | `docs/DECISIONS.md` |
| Agents, calls, Retell | `docs/context/AGENTS.md` |
| n8n workflows | `docs/context/WORKFLOWS.md` |
| Stripe billing | `docs/context/STRIPE.md` |
| Supabase tables | `docs/context/SUPABASE.md` |
| Infrastructure / Railway | `docs/context/INFRA.md` |
| Artifacts / UI previews | `docs/context/ARTIFACTS.md` |
| Pre-launch status | `docs/context/LAUNCH.md` |
| HubSpot CRM | `docs/context/HUBSPOT.md` |

## Skill files — fetch from GitHub, never from /mnt
> Skills live in `skills/{name}-SKILL.md` in this repo.
> Fetch them directly — they are always current, no upload step needed.
> Load only the skills relevant to the task. Never load all 16 at once.

```python
def load_skill(name):
    return fetch(f"skills/{name}-SKILL.md")
```

| Area | Skill name |
|---|---|
| ~~Admin dashboard~~ | DEPRECATED — replaced by HubSpot |
| HubSpot CRM | `syntharra-hubspot` |
| Client dashboard | `syntharra-client-dashboard` |
| Website | `syntharra-website` |
| Retell / agents | `syntharra-retell` |
| n8n / infrastructure | `syntharra-infrastructure` |
| Emails | `syntharra-email` |
| Stripe / billing | `syntharra-stripe` |
| HVAC Standard pipeline | `hvac-standard` |
| HVAC Premium pipeline | `hvac-premium` |
| E2E test — Standard | `e2e-hvac-standard` |
| E2E test — Premium | `e2e-hvac-premium` |
| Ops / session rules | `syntharra-ops` |
| Marketing / lead gen | `syntharra-marketing` |
| Social leads system | `syntharra-social-leads` |
| Brand / visual identity | `syntharra-brand` |
| AI receptionist (new verticals) | `ai-receptionist` |
| Artifacts (React previews) | fetch `syntharra-artifacts/SKILL.md` directly |

## Tools — use these, don't build from scratch
| Script | Location | When to use |
|---|---|---|
| Agent simulator | `tools/openai-agent-simulator.py` | Test agent behaviour across scenario groups |
| Auto-fix loop | `tools/auto-fix-loop.py` | Targeted fix validation after prompt changes (~$0.15/test) |
| Retell call analyser | `tools/retell-call-analyser.py` | Analyse real call transcripts for issues |
| E2E test — Standard | `shared/e2e-test.py` | Full pipeline test before any deploy |
| E2E test — Premium | `shared/e2e-test-premium.py` | Full Premium pipeline test |
| Self-healing loop | `tools/self-healing-loop.py` | Automated fix → test → fix cycle |
| Safety checks | `tools/safety-checks.py` | Pre-deploy safety validation |

## GitHub repos
| Repo | Purpose |
|---|---|
| `syntharra-automations` | All ops code, skills, docs, n8n backups |
| `syntharra-website` | syntharra.com (GitHub Pages) |
| ~~`syntharra-admin`~~ | DEPRECATED — admin dashboard replaced by HubSpot |
| `syntharra-checkout` | Stripe checkout server — `checkout.syntharra.com` |
| `syntharra-oauth-server` | Premium OAuth — `auth.syntharra.com` |
| `syntharra-ops-monitor` | 24/7 monitor (Railway, ACTIVE) |
| `syntharra-artifacts` | Claude chat artifact files |

## CRM — HubSpot (replaced admin dashboard 2026-04-03)
- URL: `https://app.hubspot.com`
- API key: in `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- Base URL: `https://api.hubapi.com`
- Pipeline stages: Lead → Demo Booked → Paid Client → Active
- All n8n workflows push contact + deal data to HubSpot automatically
- See `docs/context/HUBSPOT.md` for full integration reference

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
