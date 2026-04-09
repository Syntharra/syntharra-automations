# Rules — Syntharra Automations

> **Hard don'ts.** Every rule here exists because we violated it and got burned. Don't re-learn these lessons.

## 1. Never test or fix on a live Retell agent

- Live agents answer calls for paying clients. A bad prompt = a bad customer experience in real-time.
- **Always** clone the MASTER to a TESTING agent, iterate on TESTING, then promote via `retell-iac/scripts/promote.py`.
- `promote.py` is the sole path to live. No manual JSON edits in the Retell dashboard.

## 2. IDs come from `docs/REFERENCE.md` only

- Never inline an agent ID, flow ID, workflow ID, or webhook ID anywhere except REFERENCE.md.
- Not in code, not in other docs, not in commit messages beyond the short SHA, not in Slack.
- If you need an ID, open REFERENCE.md. If the ID is missing, add it to REFERENCE.md first, then reference it.
- **Why:** prevents drift when IDs rotate. Single source, grep once, update once.

## 3. Per-client data belongs in Supabase, not the repo

- The repo holds MASTER templates (Standard + Premium) and nothing per-client.
- Client clones, their phone numbers, their integration credentials, their custom prompts — all in Supabase (`client_agents`, `client_integrations`, `syntharra_vault`).
- **Why:** scales to 1000+ clients without the repo growing. If we stored per-client files, `git clone` would become unusable at scale.
- If you catch yourself writing `clients/acme-hvac.json` or similar — stop. That goes in Supabase.

## 4. GitHub MCP 403 fallback

- The Cowork GitHub MCP intermittently returns `403 Resource not accessible by integration` on write operations (reads work). Token permission injection across subagent contexts is unreliable.
- **Fallback order:** (a) retry once from a fresh subagent, (b) use Desktop Commander MCP to push directly from the local clone via GitHub Desktop's bundled git binary, (c) if neither available, mirror files to workspace + `PUSH_ME.md` with a one-shot script.
- Log every 403 incident in `FAILURES.md`. See 2026-04-07 row.
- **Why:** we've lost hours retrying the same failing MCP call across multiple sessions.

## 5. Every session ends with `tools/session_end.py`

- No exceptions. This is how STATE.md, session-logs/INDEX.md, and the RULES↔FAILURES link stay in sync.
- Usage: `python tools/session_end.py --topic <slug> --summary "<one-line>"`
- Run it even if the session was exploratory and you didn't commit anything — the index row is still useful context for next time.

## 6. Every new failure gets a FAILURES.md row

- If something broke in a non-obvious way, add a row to FAILURES.md in the same commit as the fix.
- Row format: `| date | system | symptom | root cause | fix | resolved? |`
- If the failure implies a new standing rule (e.g. "never do X"), add the rule to this file in the same commit. `session_end.py` warns if you forget.

## 7. Never test on live data

- Supabase: use `TESTING` schema or a dev branch, not `public`.
- Stripe: test mode until pre-launch-checklist §2 is complete.
- n8n: duplicate-and-pause is fine; editing a live workflow without a backup is not.
- Twilio/Telnyx: never dial out to real phone numbers during tests.

## 8. Never push without reading STATE.md first

- STATE.md tells you what's in flight. If your change touches anything in the "in flight" section, coordinate — don't just land.
- If STATE.md is out of date, that's a bug. Fix STATE.md in the same commit.

## 9. JotForm webhook data lives in rawRequest, not the body

- JotForm packs all q* field answers inside `body.rawRequest` as a JSON string. Direct `body.q*` keys are absent.
- Always parse: `formData = { ...body, ...JSON.parse(body.rawRequest) }`.
- Phone fields arrive as `{full: '(555) 234-5678'}` objects — unwrap with `cleanPhone()`.
- Checkbox fields use `q{N}_option_` keys (e.g. `q13_option_`), NOT the named keys like `q13_servicesOffered`.

## 10. n8n Code nodes cannot make outbound HTTP calls

- `fetch()`, `$helpers.httpRequest`, and `this.helpers.httpRequest` all fail in Code node context.
- For any outbound call, use an HTTP Request node. Build the payload in a Code node if needed, then chain to HTTP Request.
- When an HTTP Request response is empty (e.g. Retell publish returns 200 with no body), set `options.response.response.responseFormat: 'text'` to prevent JSON parse errors.

## 11. n8n REST API: use raw PUT for workflow patches

- Never use n8n MCP to modify existing workflows — it does full rewrites that break unrelated nodes.
- Pattern: GET `/api/v1/workflows/{id}` → modify target node(s) in Python → PUT back.
- PUT payload: only `name`, `nodes`, `connections`, and `settings` (only `executionOrder` inside settings). Extra fields cause 400.
- Credentials: n8n API key in `syntharra_vault` table (`service_name='n8n Railway'`).

## 12. IF branches drop upstream context — always reach back

- IF nodes pass the input from the node they receive data from, not the full upstream chain.
- If data is lost at an IF branch (e.g. `submission_id` disappears after IF), reach back explicitly: `$('Node Name').first().json.field`.
- After any workflow branch change, verify all required fields are present on both IF paths.

## 13. Always query syntharra_vault, never vault

- The credentials table is `public.syntharra_vault`. There is no `public.vault` and no `active` column.
- Query: `SELECT * FROM public.syntharra_vault WHERE service_name = 'X'`.
