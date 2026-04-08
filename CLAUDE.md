# Claude - Syntharra Automations

> **Single product — $697/mo HVAC Standard. retell-iac is the canonical agent source of truth.**

**Start every session by reading `docs/SESSION_START.md`.**

That file is the single entry point. It tells you to read, in order:

1. `docs/STATE.md` - current reality
2. `docs/RULES.md` - hard don'ts, testing discipline, session protocol
3. `docs/REFERENCE.md` - all agent/flow/workflow IDs (sole source of truth)
4. `docs/FAILURES.md` - past incidents and their fixes

Then run `python tools/session_start.py` to see the 15-line orientation block (last session, recent failures, in-flight work, uncommitted state).

## Iron rules (also in RULES.md)

- **Never test or fix on live Retell agents.** Clone to TESTING, promote via `retell-iac/scripts/promote.py`.
- **IDs only from `docs/REFERENCE.md`.** Never inline.
- **Per-client data lives in Supabase**, not the repo. The `client_agents` table is the source. This is how we scale to 1000+.
- **Every new failure gets a FAILURES.md row.** If it implies a standing rule, update RULES.md in the same commit.

## Tools

| Tool | Path | Purpose |
|---|---|---|
| Session start | `tools/session_start.py` | Orientation block — run at session start |
| Safety checks | `tools/safety-checks.py` | Pre-change validation |

## Skills routing

| Topic | Skill file |
|---|---|
| Retell agent / flow changes | `skills/syntharra-retell-SKILL.md` |
| Infrastructure / retell-iac | `skills/syntharra-infrastructure-SKILL.md` |
| Email templates | `skills/syntharra-email-SKILL.md` |
| Stripe / billing | `skills/syntharra-stripe-SKILL.md` |
| Website / landing page | `skills/syntharra-website-SKILL.md` |
| Slack notifications | `skills/syntharra-slack-SKILL.md` |
| Brand standards | `skills/syntharra-brand-SKILL.md` |
| Client dashboard | `skills/syntharra-client-dashboard-SKILL.md` |
| HVAC Standard pipeline | `skills/hvac-standard-SKILL.md` |

## GitHub MCP 403 fallback

If `mcp__562ca274-...__create_or_update_file` returns `403 Resource not accessible by integration`:
1. Retry once from a fresh subagent context
2. If still 403, use Desktop Commander MCP (`mcp__Desktop_Commander__*`) to push directly from the local clone
3. Log the incident in FAILURES.md
