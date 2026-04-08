date | area | what failed | root cause | fix applied | skill updated
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

## 2026-04-08 — Standard MASTER auto-layout blocked by phantom component
**What failed:** Retell canvas "Auto Layout" button threw an error on the Standard MASTER flow, blocking canvas operations
**Root cause:** The flow's components[] array contained a blank inline component (cf-component-1774923921746, name "Component L1") with literal Retell placeholder text "Describe what the AI should say or do" — never filled in, never referenced by any node. Retell requires all components to be in a complete state before Auto Layout can run.
**Fix:** PATCH components: [] on the flow. Auto Layout unblocked.
**Rule:** After any flow edit session, check components[] array for any entries with placeholder text or zero node references. Delete them before leaving the flow.
