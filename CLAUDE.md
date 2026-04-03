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
12. **Every new/modified n8n workflow MUST be labelled before session close** — see `docs/STANDARDS.md`
13. **Route execution tasks to Claude Code, not Chat** — see `docs/STANDARDS.md` for routing rules

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

This is not an end-of-session checklist. It is an active loop running throughout every session.
Skills, FAILURES.md, and ARCHITECTURE.md are Claude's permanent compounding memory.
Every session must leave them more accurate and useful than they were at the start.

### The compounding intelligence loop
```
Observe → Question assumptions → Act → Reflect → Document → Next session starts smarter
```
This loop runs on EVERY non-trivial action — not just when things break.

### When to update a skill file
- A bug was diagnosed and fixed → add root cause + correct pattern
- An API call failed before working → add what was wrong and what works
- A gotcha was discovered (wrong arg, wrong order, wrong assumption) → document it
- A rate limit, quota, or interval constraint was hit → document the limit and safe threshold
- Something was tried that doesn't work → add "do NOT do X" entry
- A correct pattern was confirmed by testing → add it as a verified working pattern

**Do NOT update a skill just because you used it normally with no issues.**
**Do NOT add entries that don't contain a real lesson.**

### When to update FAILURES.md
- Every time a bug is fixed — one row per fix
- Format: `date | area | what failed | root cause | fix applied | skill updated (yes/no)`
- Only log once the fix is verified working — not while still debugging

### When to update ARCHITECTURE.md
- Any non-obvious decision was made → document WHY, what was considered, what was rejected
- A "quick fix" was tempting but a better path was chosen → document both and why
- A constraint was discovered (API limit, token limit, timeout) → document with correct workaround
- An assumption was tested and confirmed or disproved → document the result

### Mandatory session-end REFLECTION — written into session log every single session
Before closing, write and answer every line of this block honestly in the session log:

```
## Session Reflection
1. What did I get wrong or do inefficiently, and why?
2. What assumption did I make that turned out to be incorrect?
3. What would I do differently if this exact task came up again?
4. What pattern emerged that future-me needs to know?
5. What was added to ARCHITECTURE.md / skill files, and what was the specific lesson?
6. Did I do anything "because that's how it's done" that I haven't actually verified?
   If yes → add to ARCHITECTURE.md as an open question to test next session.
```

**This reflection is not optional. Shallow answers are not acceptable.**
**If it isn't in the session log, the session is not closed.**

### Compounding intelligence rule
Any time Claude catches itself doing something "because that's how it's done" — stop.
Ask: has this assumption been tested and verified on this project?
- Verified → add to skill file as confirmed pattern
- Not verified → flag in ARCHITECTURE.md as open question, test next opportunity
- Proven wrong → add to FAILURES.md, correct the skill file, never repeat it

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

## PRE-ACTION PROTOCOL — mandatory before every non-trivial decision

Before taking any action that involves changing a model, prompt, config, test, or fix — especially under time pressure — answer these 3 questions explicitly in your response:

1. **WHY am I doing it this way?** — Is this fixing the root cause or just a symptom?
2. **WHAT would be invalidated if I'm wrong?** — What breaks downstream if this assumption is incorrect?
3. **Does this decision belong in ARCHITECTURE.md or a skill file?** — If yes, write it there before closing the session.

**If you cannot answer question 1 clearly — stop and diagnose further before acting.**

### Why this rule exists
On 2026-04-04, the simulator was hitting Groq TPM limits. The "quick fix" was to strip node instructions from the prompt to reduce token count. Question 1 answer was "saves tokens" — technically true. But question 2 was never asked: *"What does stripping node instructions invalidate?"* — Answer: the entire test. Node instructions define how the agent behaves at each stage of the call. Testing without them means testing an incomplete agent. The fix was wrong and had to be reverted.

The correct fix (switch to a higher-TPM model) was already known — it just wasn't reached because the shortcut was taken first.

### The pattern to break
> Task is hard → quick fix appears → quick fix is taken → quick fix causes a new problem → revert → do it properly

### The pattern to enforce
> Task is hard → ask WHY → ask WHAT BREAKS → take the right action → document the decision

---

## Session startup — always load these 6
```python
claude_md     = fetch("CLAUDE.md")            # operating rules — always first
tasks_md      = fetch("docs/TASKS.md")        # current state + open items
failures_md   = fetch("docs/FAILURES.md")     # what broke before — scan before touching anything
decisions_md  = fetch("docs/DECISIONS.md")    # why things are built the way they are
standards_md  = fetch("docs/STANDARDS.md")    # labelling rules + Claude Code routing
arch_md       = fetch("docs/ARCHITECTURE.md") # non-obvious decisions — MANDATORY, read before acting
```

> ARCHITECTURE.md is mandatory every session — not optional, not "when relevant".
> It contains reasoning behind decisions that aren't obvious from the code.
> Reading it prevents re-litigating settled choices and repeating past mistakes.

## Context files — load what you need
| What you're working on | File to fetch |
|---|---|
| Any session (always) | `docs/TASKS.md`, `docs/FAILURES.md`, `docs/DECISIONS.md`, `docs/STANDARDS.md` |
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
