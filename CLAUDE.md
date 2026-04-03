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
11. **Document architectural reasoning in `docs/ARCHITECTURE.md` whenever a non-obvious choice is made**

## Claude Code — Safe Operating Rules
> Claude Code is the execution layer for session tasks. It complements this workflow — never replaces or overrides it.
> All rules in this file apply inside Claude Code sessions without exception.

### What Claude Code is used for
- Running E2E tests automatically after any agent or workflow change
- Self-healing loop: run test → see failure → fix → re-test → repeat until green
- Pushing session logs to GitHub at session close
- Verifying GitHub pushes completed correctly

### Hard limits — non-negotiable inside Claude Code
1. **TESTING agents only** — never touch MASTER agents (`agent_4afbfdb3fcb1ba9569353af28d`, `agent_9822f440f5c3a13bc4d283ea90`)
2. **No production changes without E2E pass** — every change must pass `shared/e2e-test.py` before any live push
3. **Self-healing loop max 10 iterations** — if not green after 10 cycles, stop and report to Dan
4. **3 consecutive failures on any step = stop** — do not retry indefinitely, surface the blocker
5. **Never delete or recreate Retell agents** — same as everywhere else, no exceptions
6. **Read before write** — always fetch current file before any edit
7. **Session log must be pushed before Claude Code session closes**
8. **Never wipe or rewrite a file from scratch** — always str_replace on fetched current content

### What Claude Code will NOT do
- Touch any MASTER agent
- Push to GitHub without a passing E2E test
- Modify live production n8n workflows without test verification
- Run the self-healing loop against anything other than the TESTING agent

## SELF-IMPROVEMENT PROTOCOL — NON-NEGOTIABLE

Skills and FAILURES.md are Claude's permanent, compounding memory.
They only get updated when there is a real learning — not just because a task was completed.

### When to update a skill file
- A bug was diagnosed and fixed → add root cause + correct pattern
- An API call failed before working → add what was wrong and what works
- A gotcha was discovered (wrong arg, wrong order, wrong assumption) → document it
- A rate limit, quota, or interval constraint was hit → document the limit and safe threshold
- Something was tried that doesn't work → add explicit "do NOT do X" entry

**Do NOT update a skill just because you used it normally with no issues.**
**Do NOT add entries that don't contain a real lesson.**

### When to update FAILURES.md
- Every time a bug is fixed — one row per fix
- Format: `date | area | what failed | root cause | fix applied | skill updated (yes/no)`
- Only log once the fix is **verified working** — not while still debugging

### Hard gate — answer these before closing every session
1. Did anything break or fail this session? → FAILURES.md row + skill update
2. Did I discover a correct pattern by testing/failing first? → Add to skill
3. Did I fix a wrong assumption? → Add "was wrong because X, correct is Y" to skill
4. Are skill files more accurate and useful than when I started? → If no, do it now
5. **Did I make any architectural choice this session that isn't documented?** → Write it to `docs/ARCHITECTURE.md` before closing
**If nothing went wrong and nothing was learned — no skill update needed. That's fine.**
**If something did go wrong or was figured out — it must be documented before the chat ends.**

### Which skill to update — global, covers all skills
| System touched | Skill to update |
|---|---|
| Railway, deploys, env vars, ops monitor | `syntharra-infrastructure` |
| Retell agents, flows, prompts, calls | `syntharra-retell` |
| n8n workflows, webhooks, nodes | `syntharra-infrastructure` |
| Emails, SMTP2GO, templates, alerts | `syntharra-email` |
| Stripe, billing, products, prices | `syntharra-stripe` |
| HubSpot, CRM, pipeline, contacts | `syntharra-hubspot` |
| Website, HTML, CSS, pages | `syntharra-website` |
| HVAC Standard pipeline | `hvac-standard` |
| HVAC Standard agent simulator / testing | `hvac-standard-agent-testing` |
| HVAC Premium pipeline | `hvac-premium` |
| E2E tests, simulators, scenario runner | `e2e-hvac-standard` or `e2e-hvac-premium` |
| Client dashboard | `syntharra-client-dashboard` |
| Marketing, lead gen, newsletter | `syntharra-marketing` |
| Slack notifications, channels, alerts | `syntharra-slack` |

---

## Session startup — always load these 4
```python
claude_md     = fetch("CLAUDE.md")
tasks_md      = fetch("docs/TASKS.md")
failures_md   = fetch("docs/FAILURES.md")
decisions_md  = fetch("docs/DECISIONS.md")   # why things are built the way they are
```

## Context files — load what you need
| What you're working on | File to fetch |
|---|---|
| Any session (always) | `docs/TASKS.md`, `docs/FAILURES.md`, `docs/DECISIONS.md` |
| Full reasoning behind decisions | `docs/ARCHITECTURE.md` |
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
| Slack notifications | `syntharra-slack` |
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


## Claude Code — Safe Operating Rules
> Claude Code is the execution layer for session-based tasks. It complements this chat — never replaces or overwrites it.
> These rules are as non-negotiable as the Retell agent rules above.

### Hard limits (never violate)
1. **TESTING agents only** — self-healing loop and E2E runs operate on TESTING agents exclusively. MASTER agents are never touched by Claude Code.
2. **E2E must pass before any production push** — no exceptions. Green tests = safe to push. Anything else = stop and report.
3. **No destructive operations** — no deleting files, agents, workflows, Supabase rows, or GitHub history. Ever.
4. **3-strike stop rule** — if any automated step fails 3 consecutive times, stop completely and report to Dan. Do not loop indefinitely.
5. **Max 10 iterations** on any self-healing loop before stopping and reporting.
6. **Session log mandatory** — Claude Code session cannot close without pushing a session log to `docs/session-logs/YYYY-MM-DD-topic.md`.

### What Claude Code does in a session
| Task | Script | Operates on |
|---|---|---|
| Run E2E after agent change | `python3 shared/e2e-test.py` | TESTING agent only |
| Run E2E after workflow change | `python3 shared/e2e-test-premium.py` | TESTING agent only |
| Self-healing loop | `python3 tools/self-healing-loop.py` | TESTING agent only |
| Push session log | `tools/claude-code/push-session-log.sh` | `docs/session-logs/` only |
| Verify GitHub push | `tools/claude-code/verify-push.sh` | Read-only check |

### What Claude Code never does
- Never runs against MASTER agents (`agent_4afbfdb3fcb1ba9569353af28d`, `agent_9822f440f5c3a13bc4d283ea90`)
- Never modifies n8n production workflows without E2E pass
- Never changes Railway env vars without explicit Dan instruction in chat
- Never touches Stripe in live mode
- Never sends real emails to real clients during testing

### CLAUDE.md for Claude Code
> When Claude Code starts, it must fetch and follow this CLAUDE.md exactly.
> The operating rules, skill files, and session protocols are identical whether running in chat or Claude Code.
> Claude Code is not a separate context — it is the same engineer, same rules, same memory.

## Brand tokens (quick reference)
- Violet: `#6C63FF` | Cyan: `#00D4FF` | Dark: `#1A1A2E`
- Font: DM Sans (UI) | Email font: Inter
- Logo: 4 ascending bars, flat `#6C63FF` — NEVER emoji substitute
- Icon URL: `https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png`
