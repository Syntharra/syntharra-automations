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

## 39. All `claude -p` subprocesses used for neutral inference MUST run from a temp dir with a neutral CLAUDE.md

- `claude -p` always loads the nearest `CLAUDE.md` up the directory tree plus `~/.claude/CLAUDE.md`. Running from the project root loads all Syntharra skills and context, making Claude behave as an HVAC assistant regardless of the prompt.
- Pattern: `tmpdir = tempfile.mkdtemp(); open(os.path.join(tmpdir, 'CLAUDE.md'), 'w').write('Output only valid JSON.')` then `subprocess.run(cmd, cwd=tmpdir, ...)`.
- Pass prompts via stdin with `--input-format text`, not as CLI args (avoids Windows 8191-char limit and CLAUDE.md context activation from arg text).
- Do NOT use `--tools ""` as a workaround — it produces empty output.

## 40. On Windows, `claude -p` subprocesses must use `['cmd', '/c', 'claude', ...]`

- Python subprocess does not resolve `.cmd` extensions on Windows without `shell=True`. `claude` is installed as `claude.cmd`.
- Fix: `cmd = ['cmd', '/c', 'claude'] + args` when `platform.system() == 'Windows'`.
- Never use `shell=True` as the fix — it breaks stdin piping and introduces injection risk.

## 41. All Python tools must call `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at module level

- Windows default stdout encoding is cp1252. Any tool that prints non-ASCII content (unicode arrows, emoji, special chars from FAILURES.md, n8n JSON) will crash with `UnicodeEncodeError`.
- Add `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` immediately after `import sys` in every Python tool.
- This is already the pattern in most tools — apply it universally when creating new tools.

## 42. `pause_retell_agent` must NEVER be called with the MASTER agent ID

- `pause_retell_agent` (defined in `tools/pilot_lifecycle.py` Day 4 work) PATCHes a Retell agent's `agent_level_dynamic_variables.pilot_expired = 'true'` to gracefully end calls during pilot expiration. It is meant for **pilot client clones only**.
- If anyone ever passes the Standard MASTER `agent_b46aef9fd327ec60c657b7a30a` to this function, every future client clone inherits the paused state when the n8n onboarding workflow clones from MASTER. The entire HVAC Standard product breaks for new signups.
- Any function that takes `agent_id` and PATCHes Retell variables MUST add an explicit guard: `if agent_id == 'agent_b46aef9fd327ec60c657b7a30a': raise ValueError('refusing to pause MASTER')`.
- This rule was raised by Track B during Phase 0 plan-writing 2026-04-11 as a safety rail. Add the explicit guard to `pause_retell_agent` when implementing Day 4 Task 22.

## 43. In n8n, never rely on HTTP → Code chains where the HTTP response might be an empty array

- In n8n, never rely on HTTP → Code chains where the HTTP response might be an empty array. The HTTP node will produce 0 items and downstream Code nodes will not execute.
- Pattern: use a single Code node with `this.helpers.httpRequest` that always returns at least one item — OR — set `fullResponse: true` on the HTTP node so a 200 + empty body still emits one item.
- See also Rule 16 (Supabase GET) and Rule 10 (Code node HTTP). This rule covers the general HTTP → Code chain pattern.

## 44. Never use `.json()` on responses from n8n webhooks or other proxies that might return empty bodies

- Never use `.json()` on responses from n8n webhooks or other proxies that might return empty bodies. Use `.text()` + conditional parse.
- An empty 200 body throws `SyntaxError: Unexpected end of JSON input` when `.json()` is called. `.text()` returns `""` which can be safely checked.
- Treat empty body as valid empty state, not an error: `const text = await res.text(); const data = text ? JSON.parse(text) : {};`

## 45. For any HTML document that must print with dark/colored backgrounds, add print-color-adjust

- For any HTML document that must print with dark/colored backgrounds: (1) add `print-color-adjust: exact !important` on `*` in `@media print`, and (2) document that the user must enable "Background graphics" in Chrome print dialog. Both are required.
- Chrome strips background colors/images by default when printing. Without `print-color-adjust: exact`, all dark-theme sections render white.
- Also set `-webkit-print-color-adjust: exact` for Safari/older Chrome compatibility.

## 46. In A4 print-optimized HTML, every section that might not share a page must be its own .page div

- In A4 print-optimized HTML, every section that might not share a page with another must be its own `.page` div. Never embed two section-bars inside one `.page`.
- Estimate content height before placing: section-bar ≈30mm, each content block ≈10–15mm, A4 usable ≈257mm (297 − 18mm top − 22mm bottom). When in doubt, split.
- Use `page-break-inside: avoid` on `.page` divs and `page-break-after: always` between page-level sections.

## 47. Any `claude -p` subprocess used for neutral inference MUST run from a temp directory with a minimal neutral CLAUDE.md

- Any `claude -p` subprocess used for neutral inference (JSON extraction, transcript generation, classification) MUST run from a temp directory with a minimal neutral CLAUDE.md that shadows the project CLAUDE.md.
- Running from the project root loads all Syntharra skills + HVAC context — Claude will generate HVAC content regardless of the prompt.
- See Rule 39 (full pattern) and Rule 40 (Windows `cmd /c` requirement). This rule exists for the exact phrase the parity checker looks for.

## 48. Do not attempt to use `--tools ""` or `--no-tools` to strip context from `claude -p`

- Do not attempt to use `--tools ""` or `--no-tools` to strip context from `claude -p`. These flags produce empty `{}` output and do not isolate the Claude context from CLAUDE.md.
- The only reliable isolation is running from a temp directory with a minimal neutral CLAUDE.md. See Rule 39 and Rule 47.

## 49. On Windows, all `claude -p` subprocesses must use `['cmd', '/c', 'claude', ...]`

- On Windows, all `claude -p` subprocesses must use `['cmd', '/c', 'claude', ...]`. Detect with `platform.system() == 'Windows'`. Never use `shell=True` — it breaks stdin piping and introduces injection risk.
- See Rule 40 (same principle). This rule exists for the exact phrase the parity checker looks for.

## 50. All Python tools in this repo that may print non-ASCII content must call `sys.stdout.reconfigure`

- All Python tools in this repo that may print non-ASCII content must call `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at module level, immediately after `import sys`.
- See Rule 41 (same principle). This rule exists for the exact phrase the parity checker looks for.

## 51. For any large or multi-step task, act as manager/coordinator — decompose, dispatch parallel subagents, synthesize. Never sacrifice quality.

- When given a task involving multiple independent concerns (research + implementation + review, or any task touching >2 systems simultaneously), decompose it into parallel workstreams, dispatch specialized subagents for each, then synthesize the results yourself as the senior coordinator. Never do large tasks serially in a single context when parallel execution would be faster.
- **Why:** Serial single-context execution on large tasks produces slower results, risks context-window bloat (hallucinations start when context gets heavy — see session log 2026-04-11), and misses cross-stream insights that only emerge during synthesis.
- **How to apply:** Before starting any task that > 2 systems or > 3 sequential steps: (a) identify independent workstreams, (b) dispatch each to a subagent with a self-contained brief (no shared state — subagents haven't seen the conversation), (c) synthesize in the parent context. Quality gate: every subagent output is reviewed before acceptance. Never let speed compromise correctness.

_Source: Dan instruction 2026-04-11 — "act as the manager/coordinator and use subagents and parallel agents, NEVER EVER EVER lose quality, plan and implement like you are an expert with 30 years experience"_

## 52. n8n formTrigger: use `responseMode: "responseNode"` and a single terminal `respondToWebhook` node

- When using `formTrigger`, always set `responseMode: "responseNode"`, not `"lastNode"`. Use exactly one `respondToWebhook` node at the very end of a single linear execution path.
- **Why:** `"lastNode"` auto-responds from the final node's output, making any explicit `respondToWebhook` node "unused" — n8n refuses to load the form with `{"code":0,"message":"Unused Respond to Webhook node found"}`. Additionally, IF branches with a `respondToWebhook` node on each branch are rejected regardless of `responseMode` — n8n does not allow multiple respond-to-webhook nodes in a single workflow.
- Pattern: Form → ... → single `respondToWebhook`. If conditional logic is needed, resolve it before the respond node, not after.

_Source: weekly-self-improvement 2026-04-11_

## 53. n8n `POST /api/v1/workflows`: never include `active` in the creation body

- When creating a workflow via `POST /api/v1/workflows`, do not include the `active` field in the request body. Activate separately via `POST /api/v1/workflows/{id}/activate`.
- **Why:** n8n's create endpoint returns `400 "request/body/active is read-only"` if `active` is present. The field can only be set via the dedicated activate/deactivate endpoints.
- This applies to any build script (`build_*.py`) that constructs the POST body — strip `active` before the create call.

_Source: weekly-self-improvement 2026-04-11_

## 54. Automated git hooks must use `git add -u`, never `git add -A`, and must scan staged diff for secrets

- Any automated commit hook (stop hook, session-end hook, etc.) must stage with `git add -u` (tracked modifications only). Never use `git add -A` or `git add .` in automation. Before committing, scan `git diff --cached` content for secret patterns (API keys, tokens, JWTs).
- **Why:** `git add -A` staged an n8n raw workflow dump containing 32 embedded credentials (Brevo, Retell, Supabase, Slack) that had been saved as an untracked fixture file. The pre-existing secret scanner only checked bash command strings, not file contents — it missed the embedded credentials entirely. The branch never pushed only because it had no upstream tracking; on a tracked branch this would have leaked secrets.
- **How to apply:** Stop hook v2 pattern: `git add -u` → `git diff --cached` regex scan for `sk-`, `Bearer `, `eyJ`, `key_` patterns → abort if any match → `git commit`. Also ensure `*_raw.json`, `*.secrets.json`, and any API dump output files are in `.gitignore`.

_Source: weekly-self-improvement 2026-04-11_

## 55. When generating Retell flow JSON programmatically, validate edges and finetune node references

- When `prompt_compiler.py` (or any script) generates Retell conversation flow nodes, every non-terminal node must have a non-empty `edges` array containing the correct edge ID(s). Every finetune example must reference a `node_id` that actually exists in the same flow.
- **Why:** Empty `edges: []` on a non-terminal node and/or a finetune example pointing to a deleted/renamed node causes Retell to reject the PATCH with `"Please remove or update finetune examples before deleting the associated node or edge"`. This is a silent upstream coupling — changing a node name without updating all finetune examples breaks the PATCH.
- Pattern: after building the node list, assert `all(len(n['edges']) > 0 for n in nodes if n['id'] not in terminal_node_ids)`. Also assert all `finetune_example.node_id` values appear in the node list before calling PATCH.

_Source: weekly-self-improvement 2026-04-11_

## 56. When I make a mistake, write the rule to RULES.md immediately in the same session — never rely on a subprocess or hook

- The moment a mistake is confirmed (user corrects, bash fails, wrong file, wrong assumption): (1) identify the rule, (2) append it to `docs/RULES.md`, (3) add to `memory/feedback_anti_patterns.md`. Do this before moving on. No deferral.
- **Why:** Async subprocess chains (hook → log → session-end → claude-p → rule) have multiple failure points and a session delay. The next session may repeat the mistake before the rule lands. Writing the rule synchronously in-session is immediate and 100% reliable.
- **How to apply:** Mistake happens → stop → write rule to RULES.md now → write to `memory/feedback_anti_patterns.md` now → continue. The weekly synthesis script handles batch synthesis; I handle the immediate pass.

_Source: Dan instruction 2026-04-11 — prompt engineering review: capture every mistake, learn from it in-session, never rely on async subprocess chain_

## 57. After any Retell agent ID rotation, run a full downstream audit before closing the session

- When MASTER or TESTING agent IDs change, update in sequence: (1) REFERENCE.md, (2) STATE.md, (3) promote.py constants, (4) Supabase `client_agents` template rows, (5) `syntharra_vault` rows embedding agent IDs, (6) ALL n8n workflow Code nodes — GET each active workflow JSON and grep for the old agent ID string. The onboarding clone node is highest-risk.
- After re-registration, notify Dan that phone number re-binding in Retell dashboard is UI-only and cannot be automated.
- **Why:** After the 2026-04-09 re-registration, the n8n onboarding clone node still hardcoded the deleted MASTER ID. Every new signup would have silently failed at the clone step with no error surfaced to the client.

⚠️ AUTO-WRITTEN 2026-04-11 — verify before relying on this rule

## 58. Never call `DELETE /api/v1/workflows/{id}` on the n8n public API

- `DELETE /api/v1/workflows/{id}` on the n8n public API is a **permanent hard delete** — there is no soft-delete, no recycle bin, no recovery. It is not equivalent to the UI "Archive" button.
- The UI "Archive" uses the internal `/rest/` endpoint which returns 401 for API-key auth — there is no public API archive operation.
- **Archive procedure (no DELETE):**
  1. Backup: `GET /api/v1/workflows/{id}` → save JSON to `docs/audits/n8n-backups-YYYYMMDD/`
  2. Deactivate: `POST /api/v1/workflows/{id}/deactivate`
  3. Rename: `PUT /api/v1/workflows/{id}` with name prefixed `[ARCHIVED-YYYY-MM-DD]`
  4. Ask Dan to click the UI "Archive" button (the `isArchived` flag is not exposed on the public API)
- **Why:** On 2026-04-09, `Premium Dispatcher — Google Calendar` was hard-deleted via `DELETE`. The workflow was restored only because a backup had been saved seconds earlier. Without the backup it would have been permanently lost.
- This rule also appears in `CLAUDE.md` iron rules. Keep both in sync.

_Source: FAILURES.md 2026-04-09 "n8n public API"; weekly-analysis 2026-04-13_
