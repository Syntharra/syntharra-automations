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

## 14. Automation API dumps are secret material

- n8n (`GET /api/v1/workflows/{id}`), Retell full-agent dumps, and any similar "give me the whole object" endpoint return documents that **embed credentials inline** — HTTP node headers, auth blocks, connection strings baked into the payload.
- Treat any such dump as if it were a `.env` file:
  - Save under `docs/audits/` (already gitignored) or to `/tmp`, or delete after use.
  - **Never** commit one to the repo. Not even to a feature branch. Not even "temporarily, I'll strip it later".
  - Extract what you actually need (e.g. a single code-node `jsCode` field) into a focused fixture, then delete the raw dump.
- `.gitignore` blocks `*_raw.json` and `*.secrets.json` globally. If you name a dump anything else, you are on the hook for it.
- **Why:** See FAILURES.md 2026-04-09 "stop hook / secrets" — an n8n workflow dump with 32 live credentials nearly hit GitHub via a broken auto-backup hook. The hook has been hardened (branch-gate + `git add -u` + pre-commit secret scan) but the discipline is still yours — belt AND braces.

## 15. HTTP node credential stripping after raw REST PUT

- When a raw `PUT /api/v1/workflows/{id}` patches an n8n workflow, any `credentials` objects on HTTP Request nodes are silently stripped from the returned payload.
- After any raw PUT, HTTP nodes that need auth must use `authentication: "none"` with hardcoded `headerParameters` (e.g. `Authorization: Bearer <token>` or `apikey: <key>`).
- Never assume credentials survive a PUT round-trip. Verify by re-fetching and checking `headerParameters` on auth-dependent nodes.

## 16. n8n Supabase GET: always set fullResponse

- When a Supabase REST `GET` returns an empty array (row not found), the HTTP Request node emits **0 items** by default — downstream nodes never execute.
- Fix: set `options.response.response.fullResponse: true` on every Supabase query node that checks for existence. A 200 + empty body still emits one item with `body: []`, and downstream IF nodes can test `body.length`.
- After any Supabase query node change, verify the downstream IF/Switch condition handles both the found and not-found paths.

## 17. Never INSERT to client_agents before the Retell agent exists

- `client_agents.agent_id` is NOT NULL. Inserting before `POST /create-agent` returns `agent_id` fails with 400.
- Pattern: query `hvac_standard_agent` (canonical config row) for the template flow ID → proceed through Retell agent creation → INSERT/UPDATE after Retell returns the new `agent_id`.
- No optimistic early INSERT — there is no `agent_id` to put there.

## 18. n8n HTTP node: sendHeaders must be explicitly true

- Adding `headerParameters` does **not** send those headers unless `sendHeaders: true` is also set. Default is `false`.
- After any HTTP Request node add or update involving custom headers (Authorization, apikey, Content-Type), verify `sendHeaders: true` is present.
- This causes silent 401 / 4xx failures on Retell, Supabase, and Brevo nodes with no UI warning.

## 19. Retell conversation flow field is start_node_id, not starting_node_id

- `POST /create-conversation-flow` and `PATCH /update-conversation-flow/{id}` expect `start_node_id`.
- `starting_node_id` is silently ignored, resulting in a flow with no entry point that fails at publish.
- Any build script, Code node, or JSON template assembling a Retell flow must use `start_node_id`.

## 20. Google OAuth email node must guard on integration_type

- The Send Google OAuth Email node must check `integration_type === 'google'` before sending.
- Without this guard, it fires for every client. Non-Google clients have blank `client_email` → Brevo 400.
- After any onboarding workflow branch change, verify this guard is present and short-circuits cleanly.

## 21. Email templates must use inline wordmark, not a hosted image

- Never use `<img src="...">` for the Syntharra logo. Hosted images render as broken placeholders in many email clients.
- Use the inline wordmark: `<p style="font-size:28px;font-weight:900;letter-spacing:6px;color:#ffffff;">SYNTHARRA</p>`.
- Applies to all onboarding, welcome, and notification emails. Never reference a hosted asset for the logo.

## 22. GitHub MCP 403: mirror-and-instruct is the documented fallback

- When `mcp__*__create_or_update_file` returns `403 Resource not accessible by integration`: (a) retry once from a fresh subagent, (b) use Desktop Commander MCP to push from the local clone, (c) if neither works, mirror changed files + leave a `PUSH_ME.md` one-shot script for the user.
- Documented in both Rule 4 above and `CLAUDE.md §GitHub MCP 403 fallback`. Keep both in sync.
- Every 403 incident is logged in FAILURES.md with the exact call and context.
