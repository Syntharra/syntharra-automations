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
9. Update relevant skill(s) after any verified work — they auto-sync, no upload needed
10. Update `docs/TASKS.md` at end of every chat

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
| Admin dashboard | `syntharra-admin` |
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
| `syntharra-admin` | admin.syntharra.com (Railway) |
| `syntharra-checkout` | Stripe checkout server — `checkout.syntharra.com` |
| `syntharra-oauth-server` | Premium OAuth — `auth.syntharra.com` |
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
