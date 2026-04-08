# Claude - Syntharra Automations

**Start every session by reading `docs/SESSION_START.md`.**

That file is the single entry point. It tells you to read, in order:

1. `docs/STATE.md` - current reality (auto-maintained by `tools/session_end.py`)
2. `docs/RULES.md` - hard don'ts, testing discipline, session protocol
3. `docs/REFERENCE.md` - all agent/flow/workflow IDs (sole source of truth)
4. `docs/FAILURES.md` - past incidents and their fixes

Then run `python tools/session_start.py` to see the 15-line orientation block (last session, recent failures, in-flight work, uncommitted state).

## Iron rules (also in RULES.md)

- **Never test or fix on live Retell agents.** Clone to TESTING, promote via `retell-iac/scripts/promote.py`.
- **IDs only from `docs/REFERENCE.md`.** Never inline.
- **Per-client data lives in Supabase**, not the repo. The `client_agents` table is the source. This is how we scale to 1000+.
- **Every session ends with `python tools/session_end.py --topic <slug> --summary "<line>"`.**
- **Every new failure gets a FAILURES.md row.** If it implies a standing rule, update RULES.md in the same commit.

## GitHub MCP 403 fallback

If `mcp__562ca274-...__create_or_update_file` returns `403 Resource not accessible by integration`:
1. Retry once from a fresh subagent context
2. If still 403, use Desktop Commander MCP (`mcp__Desktop_Commander__*`) to push directly from the local clone
3. Log the incident in FAILURES.md
