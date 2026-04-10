date | area | what failed | root cause | fix applied | skill updated
2026-04-09 | n8n form | `https://n8n.syntharra.com/form/client-update` returned `{"code":0,"message":"Unused Respond to Webhook node found in the workflow"}` | (1) `formTrigger` `responseMode` was `"lastNode"` — this mode auto-responds from the last node's output, making any explicit `respondToWebhook` node "unused". (2) Additionally the workflow had an IF branch (`Preview or Apply?`) with two `respondToWebhook` nodes (one per branch), which n8n rejects regardless of responseMode. | Removed IF branch + `Respond: Preview` node entirely (preview mode dropped — apply always). Changed `formTrigger.responseMode` from `"lastNode"` to `"responseNode"`. Single linear path: Form → Fetch → Apply → Compile → PATCH → Publish → Update → Respond. Rebuilt via `build_client_update_workflow.py` with `N8N_CLIENT_UPDATE_ID=6Mwire23i6InrnYZ`. Form now loads correctly. | no
2026-04-09 | prompt_compiler | `update_client_agent.py` PATCH rejected by Retell with "Please remove or update finetune examples before deleting the associated node or edge" | `prompt_compiler.py` had 3 bugs: (1) `fe-service` finetune example pointed to `node-fallback-leadcapture` instead of `node-call-style-detector`; (2) `node-call-style-detector` generated with `edges: []` instead of the required `edge-call-style-detector-after`; (3) `node-validate-phone` generated with `edges: []` instead of `edge-validate-phone-after` | Fixed all 3 in `prompt_compiler.py`. Smoke test passed (PATCH → publish → Supabase write) on TESTING agent. | no
2026-04-09 | n8n API | `POST /api/v1/workflows` returned 400 "request/body/active is read-only" | `build_client_update_workflow.py` included `active: True` in the POST body; n8n's create endpoint doesn't accept this field (use the `/activate` endpoint after creation instead) | Removed `active` from the `build_workflow()` return dict. Activation still done via separate `/activate` call. | no
2026-04-09 | Retell | MASTER + TESTING agents deleted from Retell dashboard (agent_4afbfdb3fcb1ba9569353af28d + agent_6e7a2ae03c2fbd7a251fafcd00 no longer exist in account) | Dan manually cleaned up Retell account, deleting all agents except the 2 demo agents | Re-registered via `tools/re_register_master.py` from `retell-iac/snapshots/2026-04-09_testing-autolayout-fixed/`. New MASTER: `agent_b46aef9fd327ec60c657b7a30a` / `conversation_flow_19684fe03b61`. New TESTING: `agent_41e9758d8dc956843110e29a25` / `conversation_flow_bc8bb3565dbf`. REFERENCE.md, STATE.md, CLAUDE.md, promote.py, client_agents, vault all updated. ⚠️ Dan must bind +18129944371 to new MASTER in Retell dashboard. ⚠️ n8n onboarding workflow clone node hardcodes old MASTER ID — update separately. | yes
2026-04-09 | stop hook / secrets | `feat/prompt-compiler` silently received an auto-backup commit containing `tests/fixtures/prompt_compiler/_workflow_raw.json` — full raw n8n workflow dump with 32 inlined credentials (Brevo ×4, Retell ×8, Supabase+n8n JWTs ×18, Slack bot ×2) plus four unrelated untracked `plugins/*` trees | `.claude/hooks/stop_session_log.py` did `git add -A` (staged all untracked files) and fell back to `git push origin <current-branch>` when `push origin main` failed — turning a main-only backup into a feature-branch contaminator. Saved `_workflow_raw.json` as a reference for extracting JS code nodes, forgetting that n8n's workflow API returns full documents with HTTP node credentials embedded literally in headers (from the Call Processor rewrite). Pre-existing `pre_token_scan.py` only scans bash command strings, not file contents, so couldn't catch it. | Branch never actually pushed (no upstream tracking — fallback push failed harmlessly). Branch reset to `e30f29d`, bad files deleted, clean single commit made. Stop hook rewritten (v2): early-exit on any non-`main` branch; `git add -u` (tracked modifications only, never untracked); in-hook secret regex scan of `git diff --cached` before commit, aborts if any match; no fallback push to current branch. `.gitignore` hardened: `plugins/`, `__pycache__/`, `*_raw.json`, `*.secrets.json`, the two specific fixtures. New RULES.md §14: automation API dumps are secret material. n8n Railway API key queued for rotation (Dan, UI-only action). | yes (RULES.md §14 + stop_session_log.py v2)
2026-04-09 | n8n public API | Probed `DELETE /api/v1/workflows/{id}` expecting soft-archive; n8n public API hard-deletes with no recovery | Confused soft-delete semantics; assumed DELETE would mirror UI "Archive" button (which uses internal `/rest/` API) | Restored `Premium Dispatcher — Google Calendar` from backup saved seconds earlier (`docs/audits/n8n-backups-20260409/rGrnCr5mPFP2TIc7_pre-archive.json`) via `POST /workflows`; ID changed but content identical. Standing rule: **never DELETE on n8n public API** — the endpoint is destructive, not soft. For archive: deactivate + rename with prefix, and have user click "Archive" in UI (or use Postgres UPDATE on the n8n DB) — `/rest/workflows/{id}/archive` returns 401 for API-key auth. | yes (CLAUDE.md)
2026-04-07 | n8n SDK | update_workflow rejects multi-path Switch + complex Code patches | SDK validator stricter than REST API | use raw REST PUT with X-N8N-API-KEY | yes (syntharra-infrastructure)
2026-04-07 | Postgres ALTER batch | search_path ALTER on ensure_call_log_partition | function never deployed | re-ran excluding missing function | no
2026-04-07 | syntharra_vault upsert | ON CONFLICT failed | no unique constraint matching pair | DELETE + INSERT pattern | yes
2026-04-07 | n8n raw REST PUT | initial PUT 400 with extra fields | n8n PUT only accepts name/nodes/connections/settings | strip body to allowed keys | yes
2026-04-07 | Slack credential discovery | n8n public API has no /credentials endpoint | n8n API limitation | use bot token + chat.postMessage HTTP nodes | yes
2026-04-07 | RLS audit | 4 sensitive tables had no RLS + 17 anon USING(true) policies wide open | initial migrations skipped policy hardening | enable RLS + drop anon + srv_all_* replacements; preserve website_leads INSERT | yes
2026-04-07 | testing | Groq qwen3-32b 24s rate gate caused multi-hour scenario runs | sequential + tight free-tier throttle | rebuilt as v3 on OpenAI gpt-4o-mini async (concurrency=20) with hard $5 cap | yes
2026-04-07 | n8n onboarding (P0) | Both Std+Prem onboarding crashed at Check Idempotency Insert: Cannot read properties of undefined reading submission_id | Parse JotForm Data returns flat extractedData without forwarding submission_id; idempotency node was reading $input.first().json.body.submission_id which no longer existed | Rewrote idempotency node to reach back via $(JotForm Webhook Trigger).first().json (Std) and $(JotForm Premium Webhook Trigger).first().json (Prem), defensively walk .body nesting. Both clear idempotency on smoke test. Downstream Query Client Agents has separate Credentials not found error. | yes
| 2026-04-07 | n8n onboarding | n8n PUT stripped credentials objects from HTTP nodes | Earlier raw REST PUT omitted credentials field, broke auth on Query/Insert/Retell nodes | fix_onboarding.py: set authentication=none + hardcoded headers (Bearer/apikey) | yes |
| 2026-04-07 | n8n onboarding | Query Client Agents empty result halted downstream | Supabase GET on missing row returned [] → HTTP v4 emitted 0 items | Set options.response.response.fullResponse=true; rewrote IF condition to check body length | yes |
| 2026-04-07 | n8n Standard onboarding | INSERT client_agents 400 Bad Request | client_agents NOT NULL on agent_id but agent doesn't exist yet at workflow start | Removed INSERT node entirely; repointed Query at hvac_standard_agent (canonical), added submission_id column via migration | yes |
| 2026-04-07 | n8n Standard onboarding | Create Retell LLM 401 Authorization header required | HTTP node had headerParameters set but sendHeaders=false | Patched all HTTP nodes with headers to set sendHeaders=true | yes |
| 2026-04-07 | n8n Standard onboarding | Retell create-conversation-flow 4xx (rejected payload) | Build Retell Prompt JS used field name `starting_node_id` but Retell API expects `start_node_id` | Renamed field in Build Retell Prompt + Build Premium Prompt + Flow JS code | yes |
| 2026-04-07 | n8n Premium onboarding | Send Google OAuth Email 400 (Brevo) for non-google clients | Route by Integration fall-through fired OAuth email even when integration_type=manual; client_email blank caused Brevo 400 | Added google-only guard in Send Google OAuth Email JS: early return if integration_type !== 'google' | yes |
| 2026-04-07 | email | welcome email logo rendered as broken-image placeholder in client | hosted PNG (email-logo.png) didn't resolve cleanly; trusted repo file without browser-verifying render | replaced `<img>` with inline white `<p>SYNTHARRA</p>` wordmark (28px/900/ls6px); redeployed both onboarding workflows | yes (HANDOFF-2026-04-07) |

2026-04-07 | agent-testing | v3 optimizer ceiling 83-86% | append-only component patcher + signal dilution (CO rule 6x) AND simulator using fetch_agent_prompt_compressed blind to component text | surgical rewrites of 5 components, net -3968 chars, use fetch_agent_prompt_full for v4+ | yes

| 2026-04-07 | github-mcp | Cowork GitHub MCP returned 403 "Resource not accessible by integration" on every write attempt across multiple subagent contexts | Token permission injection inconsistent across Cowork execution contexts | Codified mirror-and-instruct fallback in CLAUDE_INSTRUCTIONS.md sec.8 and auto-memory; installed Desktop Commander MCP for direct local git access as permanent workaround | yes |

## 2026-04-08 — ai_phone_number blank in "you're live" email
**What failed:** AI Phone Number field was blank in the "Your AI Receptionist is Live" email and in the Quick Start Checklist "Set up call forwarding to [blank]"
**Root cause:** Variable extraction split rule in call processor was incorrectly keyed — ai_phone_number was not passed through to the email node
**Fix:** Corrected variable mapping in both Standard and Premium n8n call processor workflows
**Rule:** When adding new email template variables, always trace the full path from webhook payload → Set node → email HTML template and verify the key name matches at every step

## 2026-04-08 — transfer_phone_number blank in "you're live" email
**What failed:** Live Transfer Number field was blank in the "Your AI Receptionist is Live" email
**Root cause:** Wrong key name used for transfer_phone when building the email payload
**Fix:** Corrected key name in both Standard and Premium workflows
**Rule:** Use a single canonical field name mapping doc — do not infer key names from memory

## 2026-04-08 — Premium "you're live" email never fired
**What failed:** Premium clients received Google OAuth and HubSpot OAuth emails but never received the "Your AI Receptionist is Live" activation email
**Root cause:** Premium call processor had a guard condition that was blocking the Send Welcome Email node from executing
**Fix:** Removed the incorrect guard condition
**Rule:** After any call processor change, verify all email send nodes fire in sequence on a test run — do not assume email nodes are wired correctly just because other nodes work

## 2026-04-08 — n8n MCP unusable for targeted workflow patches
**What failed:** Attempts to patch n8n workflows via the n8n MCP resulted in full workflow rewrites that broke other nodes
**Root cause:** n8n MCP operates on full workflow JSON only — there is no "patch a single node" operation
**Fix:** Switched to direct n8n REST API (PUT /api/v1/workflows/{id}) — read full workflow, modify target nodes in Python, PUT the entire workflow back
**Rule:** Never use n8n MCP to modify existing workflows. Always use REST API with a full read-modify-write cycle. Credentials are in syntharra_vault table in Supabase.

## 2026-04-08 — Supabase vault wrong table/column name
**What failed:** Queries to `public.vault` and filtering on `active` column both returned errors
**Root cause:** The vault table is `public.syntharra_vault` (not `public.vault`), and there is no `active` column
**Fix:** Use `SELECT * FROM public.syntharra_vault WHERE service_name = 'X'` — no active filter needed
**Rule:** Always query syntharra_vault, never vault. No active column exists. Service names are exact strings (e.g. 'Retell AI', 'n8n Railway').

## 2026-04-08 — Brevo API key hardcoded in n8n workflow (security finding)
**What failed:** Brevo (email sender) API key found hardcoded directly in n8n workflow node rather than stored in vault
**Root cause:** Workflow was built before vault pattern was established, key was never migrated
**Fix:** NOT YET FIXED — P0 task logged to migrate key to syntharra_vault
**Rule:** All API keys, tokens, and credentials must live in syntharra_vault. Zero hardcoded secrets in any workflow or script.

## 2026-04-09 — Parse JotForm Data: all fields empty (rawRequest not parsed)
**What failed:** All extracted fields (company_name, phones, services, etc.) came through blank despite Jotform sending full form data.
**Root cause:** `formData = _raw.body || _raw` gives the top-level body where q* fields don't exist. JotForm packs all q* field answers inside `body.rawRequest` as a JSON string. The parse node was never reading it.
**Fix:** Parse `rawRequest` and merge: `formData = { ...bodyRaw, ...JSON.parse(bodyRaw.rawRequest) }` (Parse JotForm Data v6)
**Rule:** JotForm webhook data: always parse `body.rawRequest` (JSON string) and spread it on top of `body`. Direct `body.q*` keys are absent or stale fallbacks.

## 2026-04-09 — Phone fields arrive as objects, not strings
**What failed:** `transfer_phone`, `emergency_phone`, `lead_phone`, `main_phone` all returned as `[object Object]` or empty string.
**Root cause:** JotForm phone widgets send `{full: '(555) 234-5678'}` objects, not plain strings.
**Fix:** Added `cleanPhone()` helper: `if (typeof val === 'object' && val.full) return String(val.full).replace(/[^+\d]/g, '')`.
**Rule:** Any JotForm phone field must be unwrapped via `cleanPhone()`. Never assume a phone value is a string.

## 2026-04-09 — Checkbox fields use wrong key in rawRequest
**What failed:** `services_offered`, `brands_serviced`, `certifications` all empty despite client filling them in.
**Root cause:** Multi-select checkbox fields in rawRequest use key `q13_option_` (not `q13_servicesOffered`), `q14_option_` (not `q14_brandsequipmentServiced`), `q29_option_` (not `q29_certifications`). Named keys don't exist in rawRequest.
**Fix:** Parse using the `q*_option_` key with named-key fallback: `formData['q13_option_'] || formData.q13_servicesOffered`
**Rule:** JotForm checkbox fields always use the `q{N}_option_` key pattern inside rawRequest. Never rely on the named key.

## 2026-04-09 — submission_id lost at IF branch
**What failed:** Supabase record written with `submission_id: null` despite successful idempotency insert.
**Root cause:** The IF node (IF Already Processed) passes through the Query Client Agents HTTP response, which has no `submission_id`. The idempotency node's `submission_id` was not available downstream.
**Fix:** Merge LLM & Agent Data node reaches back directly via `$('Check Idempotency & Insert (STANDARD)').first().json.submission_id`.
**Rule:** IF branches drop upstream context — always reach back to the specific node holding the data you need rather than assuming it flows through.

## 2026-04-09 — Query Client Agents URL: literal template expression not evaluated
**What failed:** Query returned all rows (no filter) or an HTTP error — `submission_id` filter not applied.
**Root cause:** URL contained `{{ $input.first().json.submission_id }}` as literal text (missing `=` prefix). n8n only evaluates expressions when the field starts with `=`.
**Fix:** Changed to `={{ 'https://...?submission_id=eq.' + $input.first().json.submission_id + '&select=submission_id' }}`
**Rule:** n8n expression fields must start with `=`. Without it the curly braces are literal text.

## 2026-04-09 — Publish Retell Agent Code node cannot make HTTP calls
**What failed:** `_published: false` on every run — Retell agent created but never published.
**Root cause:** n8n Code nodes cannot make outbound HTTP calls. `$helpers.httpRequest` fails on the empty 200 response body (JSON parse error). `fetch()` is unavailable in the Code node sandbox.
**Fix:** Converted "Publish Retell Agent" from Code node to HTTP Request node (same type as Create Retell Agent) with `responseFormat: text` to handle empty 200 body. Added "Pass Through Agent Data" Code node after it to forward agent data to downstream nodes (HubSpot, email). Added "Update Agent Status: Active" PATCH node to set Supabase `agent_status = 'active'` after publish.
**Rule:** Never use a Code node for outbound HTTP. Always use an HTTP Request node. When the response is empty (like Retell publish), set `options.response.response.responseFormat: 'text'` to avoid JSON parse failures.

## 2026-04-09 — DROP TABLE blocked by dependent view (`infra_health_checks`)
**What failed:** Batched `DROP TABLE IF EXISTS` migration aborted because `infra_health_checks` had a dependent view `infra_health_summary`.
**Root cause:** Postgres blocks DROP on objects with dependent views unless CASCADE is specified. Migration was transactional, so all 5 drops rolled back.
**Fix:** Added `CASCADE` only to the one table that had the dependent object. Re-ran; succeeded.
**Rule:** Before batch DROP migrations, query `pg_depend` / `information_schema.view_table_usage` for dependent views or functions. Cascade explicitly per-target, never blanket.

## 2026-04-09 — Pass 2 one-time override of RULES.md #1 (Retell live agent webhook repoint)
**What will happen:** Pass 2 will repoint the post-call webhook URL on live agent `agent_4afbfdb3fcb1ba9569353af28d` from `HVAC Call Processor (Standard)` to new `Call Usage Logger` workflow.
**Why the override is authorized:** Pre-launch. Zero live clients. The standing rule ("never test or fix on live Retell agents") exists to protect revenue and data — neither is at risk here. Override granted by Dan on 2026-04-09 for this specific change only.
**Rule reinstated after Pass 2:** From the moment the first paying client is onboarded, the rule returns with no exceptions — clone → TESTING → promote via `retell-iac/scripts/promote.py`.

## 2026-04-10 — Reconcile node: wrong email field + PATCH on empty table (silent double failure)
**What failed:** `client_subscriptions` never got written after any Jotform submission. Reconcile node reported `stripe_reconciliation: 'skipped'` silently.
**Root cause — Bug 1 (email field mismatch):** Line 3 of reconcile code read `d.email || d.notification_email` but the Jotform onboarding data arrives with field `d.client_email`. Since neither `d.email` nor `d.notification_email` existed, email resolved to `''` and the node exited immediately with `skipped`.
**Root cause — Bug 2 (PATCH on empty table):** Even when email resolved correctly, the code did `PATCH /rest/v1/client_subscriptions?agent_id=eq.{id}`. The `client_subscriptions` table has zero rows at reconcile time (nothing earlier in the workflow inserts into it). Supabase PATCH on 0 matched rows does nothing and returns 200 — silent no-op.
**Fix:** (1) Changed email lookup to `d.email || d.notification_email || d.client_email`. (2) Changed `PATCH` → `POST` (INSERT) including `agent_id` in the body.
**Hidden issue found during fix:** `plan_type` column is NOT NULL with a `CHECK (plan_type IN ('standard', 'premium'))` constraint — no default. INSERT would have failed without it. Added `plan_type: 'standard'` to the body.
**Rule:** When a reconcile/enrichment node fires at end of a pipeline, always verify the target table has rows to PATCH. If the node is the CREATOR of that row (not an updater), use POST not PATCH. When adding Supabase INSERTs, always inspect `information_schema.columns` and `pg_constraint` for NOT NULL + CHECK constraints first.

## 2026-04-10 — n8n onboarding crashed on every execution (3 compounding root causes)
**What failed:** Every execution of `4Hx7aRdzMl5N0uJP` completed with `status=error`. `client_subscriptions` was never reached.
**Root cause 1:** `Code: Fetch Telnyx Creds` did a hard `throw new Error(...)` when Telnyx vault entries were missing. This crashed the execution immediately.
**Root cause 2:** After fixing root cause 1, the three Telnyx HTTP nodes (`Search Available Numbers`, `Order Phone Number`, `Bind to Retell SIP`) still fired with empty credentials → Telnyx returned 401 → n8n execution error.
**Root cause 3:** Eight downstream nodes (`Build Onboarding Pack HTML`, `Send Setup Instructions Email`, `Reconcile: Check Stripe Payment`, `Validate: Token Budget`, `HubSpot - Update Deal (Active)`, `Slack: Agent Live`, `Send Welcome Email`, `Update Agent Status: Active`) had no `onError` setting — any single node failure crashed the whole execution before later nodes could run.
**Fix:** (1) `Fetch Telnyx Creds` now returns `{ _telnyx_skip: true, ... }` gracefully instead of throwing. (2) Set `onError: continueRegularOutput` on all three Telnyx HTTP nodes. (3) Set `onError: continueRegularOutput` on all eight brittle downstream nodes.
**Rule:** Any node that depends on optional external credentials (Telnyx, etc.) MUST gracefully return a skip marker rather than throw. Any node that can fail independently of the happy path (email, HubSpot, Slack) MUST have `onError: continueRegularOutput` set so failures don't cascade.

## 2026-04-10 — n8n workflow PUT: Windows cp1252 encoding error
**What failed:** Python `print()` of n8n workflow JSON (containing unicode chars from n8n node code) crashed with `UnicodeEncodeError: 'charmap' codec can't encode character`.
**Root cause:** Windows default stdout encoding is cp1252. n8n Code nodes contain unicode (emoji, special chars). `print()` tried to encode to cp1252 and failed.
**Fix:** Write output to file with `encoding='utf-8'` instead of printing to stdout.
**Rule:** On Windows, never print n8n workflow JSON to stdout. Always write to a file with `open(path, 'w', encoding='utf-8')`.

## 2026-04-10 — client_subscriptions schema: hidden NOT NULL + CHECK constraints
**What failed:** First attempt at Supabase INSERT to `client_subscriptions` failed with `violates check constraint "client_subscriptions_plan_type_check"`.
**Root cause:** `plan_type` column is NOT NULL with CHECK constraint limiting values to `('standard', 'premium')`. This was not obvious from the column name alone — `'hvac_standard'` was the natural guess but is rejected.
**Fix:** Queried `information_schema.columns` + `pg_constraint` first. Used `plan_type: 'standard'`.
**Rule:** Before any INSERT to a Supabase table, run `SELECT column_name, is_nullable, column_default FROM information_schema.columns WHERE table_name = '...'` AND `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '...'::regclass AND contype = 'c'`. Never guess enum/check values.

## 2026-04-08 — Standard MASTER auto-layout blocked by phantom component
**What failed:** Retell canvas "Auto Layout" button threw an error on the Standard MASTER flow, blocking canvas operations
**Root cause:** The flow's components[] array contained a blank inline component (cf-component-1774923921746, name "Component L1") with literal Retell placeholder text "Describe what the AI should say or do" — never filled in, never referenced by any node. Retell requires all components to be in a complete state before Auto Layout can run.
**Fix:** PATCH components: [] on the flow. Auto Layout unblocked.
**Rule:** After any flow edit session, check components[] array for any entries with placeholder text or zero node references. Delete them before leaving the flow.
