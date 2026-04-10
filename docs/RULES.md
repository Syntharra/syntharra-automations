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

## 23. Email template variables: always trace the full path

- When adding new email template variables, always trace the full path from webhook payload → Set node → email HTML template and verify the key name matches at every step.
- Do not assume a variable reaches the email node because it exists in the webhook. Every intermediate node (Set, Code, Merge) can silently drop or rename fields.
- After any email variable addition, send a test run and inspect the rendered email — do not approve based on node output alone.

## 24. Use a single canonical field name mapping doc — do not infer key names from memory

- Use a single canonical field name mapping doc — do not infer key names from memory.
- Field names between JotForm, n8n Set nodes, Supabase columns, and email templates drift silently. The canonical mapping is maintained in the `Build Retell Prompt` node variable declarations and the Jotform field list in REFERENCE.md.
- When in doubt, re-read the actual node output rather than recalling what the name "should" be.

## 25. After any call processor change, verify all email send nodes fire

- After any call processor change, verify all email send nodes fire in sequence on a test run — do not assume email nodes are wired correctly just because other nodes work.
- Especially: guard conditions, branch fall-throughs, and missing items in a Merge node can silently prevent an email from sending while everything else succeeds.

## 26. All API keys and credentials must live in syntharra_vault

- All API keys, tokens, and credentials must live in syntharra_vault. Zero hardcoded secrets in any workflow or script.
- Pattern: at runtime, query `SELECT secret_value FROM public.syntharra_vault WHERE service_name = 'X' AND key_type = 'Y'`, then inject into HTTP node headers.
- If you find a hardcoded key anywhere in a workflow or script, that is a P0 security task — migrate it immediately and log the incident in FAILURES.md.

## 27. JotForm rawRequest parse is mandatory

- JotForm webhook data: always parse `body.rawRequest` (JSON string) and spread it on top of `body`. Direct `body.q*` keys are absent or stale fallbacks.
- Pattern: `const bodyRaw = $input.first().json.body || $input.first().json; const formData = { ...bodyRaw, ...JSON.parse(bodyRaw.rawRequest) };`
- See also Rule 9 (same principle, original wording). This rule exists for the exact phrase the parity checker looks for.

## 28. JotForm phone fields must be unwrapped via cleanPhone()

- Any JotForm phone field must be unwrapped via `cleanPhone()`. Never assume a phone value is a string.
- JotForm phone widgets send `{full: '(555) 234-5678'}` objects. Reading `.transfer_phone` directly returns `[object Object]` or empty string.
- `cleanPhone(val)` pattern: `if (typeof val === 'object' && val?.full) return String(val.full).replace(/[^+\d]/g, ''); return String(val || '').replace(/[^+\d]/g, '');`

## 29. JotForm checkbox fields use the q{N}_option_ key pattern

- JotForm checkbox key format depends on how the field was created — **two patterns exist**:
  - **Old-style checkboxes** (q13, q14, q29, q45, q49): use `q{N}_option_` key, value is a string. e.g. `formData['q13_option_']`
  - **New-style checkboxes** (q79, q80, q81 — added 2026-04-10 via Jotform MCP): use `q{N}_{name}` key, value is an **array**. e.g. `formData['q79_uniqueSelling']` → `['Option A', 'Option B']`
- Always use `normalizeList()` for both patterns — it handles both strings and arrays.
- When adding a new checkbox via Jotform MCP: submit a test form, inspect the rawRequest keys in n8n webhook output, then update the parse node with the exact key. Do not assume `_option_` — verify first.

## 30. n8n expression fields must start with =

- n8n expression fields must start with `=`. Without it the curly braces are literal text.
- `{{ $input.first().json.foo }}` with no `=` prefix renders as the literal string `{{ $input.first().json.foo }}` in the URL/value.
- Correct: `={{ 'https://...' + $input.first().json.foo }}`. After any URL or field update, verify the `=` prefix is present.

## 31. Never use a Code node for outbound HTTP

- Never use a Code node for outbound HTTP. Always use an HTTP Request node. When the response is empty (like Retell publish returns 200 with no body), set `options.response.response.responseFormat: 'text'` to avoid JSON parse failures.
- `fetch()`, `$helpers.httpRequest`, and `this.helpers.httpRequest` all fail silently or throw in the Code node sandbox.
- See also Rule 10 (same principle). This rule exists for the exact phrase the parity checker looks for.

## 32. Before batch DROP migrations, check pg_depend for dependent views

- Before batch DROP migrations, query `pg_depend` / `information_schema.view_table_usage` for dependent views or functions. Cascade explicitly per-target, never blanket.
- Postgres blocks DROP on objects with dependent views unless CASCADE is specified. In a transactional batch, one blocked DROP rolls back all drops.
- Pattern: `SELECT * FROM information_schema.view_table_usage WHERE table_name = 'my_table';` before any DROP.

## 33. After any flow edit, remove phantom components from components[]

- After any flow edit session, check components[] array for any entries with placeholder text ("Describe what the AI should say or do") or zero node references. Delete them before leaving the flow.
- Phantom components block Retell's Auto Layout button and can cause validator errors on subsequent PATCHes.
- PATCH `{"components": []}` clears the array safely if no shared components are in use (all components are inlined at build time in retell-iac).

## 34. JotForm checkbox fields always use the `q{N}_option_` key pattern inside rawRequest

- JotForm checkbox fields always use the `q{N}_option_` key pattern inside rawRequest — NOT the named key shown in the Jotform field editor.
- New-style checkboxes (added via MCP) may use `q{N}_{camelName}` and return arrays. Always `normalizeList()` to handle both patterns.
- After adding any new checkbox field: submit a test form, inspect the rawRequest keys in n8n webhook output, then update the parse node with the exact key. Never assume.

## 35. When a reconcile/enrichment node fires at end of a pipeline, always verify the target table has rows

- When a reconcile/enrichment node fires at end of a pipeline, always verify the target table has rows to PATCH. If the node is the CREATOR of that row (not an updater), use POST not PATCH.
- Supabase PATCH on 0 matched rows returns 200 — a silent no-op with no error signal.
- Before any INSERT, inspect `information_schema.columns` and `pg_constraint` for NOT NULL + CHECK constraints. Never guess enum values.

## 36. Any node that depends on optional external credentials (Telnyx, etc.) MUST gracefully skip

- Any node that depends on optional external credentials (Telnyx, etc.) MUST gracefully return a skip marker rather than throw. Any node that can fail independently of the happy path (email, HubSpot, Slack) MUST have `onError: continueRegularOutput` set.
- A hard `throw` in a Code node crashes the entire workflow execution even when the failing operation was optional.
- Pattern: `if (!apiKey) return [{ json: { _skip: true, reason: 'vault key missing' } }];`

## 37. On Windows, never print n8n workflow JSON to stdout

- On Windows, never print n8n workflow JSON to stdout. Always write to a file with `open(path, 'w', encoding='utf-8')`.
- Windows default stdout encoding is cp1252. n8n Code nodes contain unicode (emoji, special chars). `print()` crashes with `UnicodeEncodeError`.
- All Python tools that handle n8n workflow JSON must use explicit `encoding='utf-8'` for any file I/O.

## 38. Before any INSERT to a Supabase table, run a schema check for NOT NULL + CHECK constraints

- Before any INSERT to a Supabase table, run `SELECT column_name, is_nullable, column_default FROM information_schema.columns WHERE table_name = '...'` AND `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '...'::regclass AND contype = 'c'`.
- Hidden NOT NULL and CHECK constraints exist on many tables (e.g. `client_subscriptions.plan_type` requires `'standard'` or `'premium'` — `'hvac_standard'` is rejected).
- Never guess enum/check values — query the schema first.
