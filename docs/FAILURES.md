# Syntharra — Failure Log & Self-Teaching Record
> Updated whenever a test fails, a bug is found, or a fix is applied.
> Claude reads this at session start to avoid repeating known mistakes.
> Format: date | area | what failed | root cause | fix applied | skill updated

## How to use this file
- Claude appends a row every time something breaks and is fixed
- Claude scans this before working in any area that has prior failures
- Skill files get updated after any fix — this log is the audit trail

---

## Failure Log

| Date | Area | What Failed | Root Cause | Fix Applied | Skill Updated |
|------|------|-------------|------------|-------------|---------------|
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | core_flow run1: 47% pass rate | Loop detection not working; routing to wrong node on repeat questions | Loop fix + prompt tightening applied to TESTING agent | syntharra-retell |
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | pricing_traps run1: 50% pass rate | Agent gave vague pricing answers instead of firm $497/$997 | Pricing rules made explicit in prompt | syntharra-retell |
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | core_flow run2: 13% pass rate | Rate limited by OpenAI — not an agent failure | Evaluator notes: ignore this run | — |
| 2026-04-02 | Security | Retell API key hardcoded in 4 public Python files | Key committed directly in e2e-test.py, auto-fix-loop.py, simulator.py, e2e-test-premium.py | Replaced with `os.environ.get("RETELL_KEY", "")` in all 4 files | — |
| 2026-04-02 | Security | Retell API key hardcoded in public AGENTS.md context file | Key written inline in docs/context/AGENTS.md (public repo) | Replaced with vault lookup instruction | — |
| 2026-04-02 | Security | Stripe webhook signing secret in public STRIPE.md | `whsec_...` committed to public repo | Replaced with vault lookup instruction | — |
| 2026-04-02 | Security | GitHub token hardcoded in ops-monitor/CLAUDE.md | Token written inline (private repo, but bad practice) | Replaced with Railway env var reference | — |
| 2026-04-02 | Evaluator | Transfer scenarios scored as FAIL | Evaluator couldn't detect transfer in text sim | Fixed: evaluator now accepts "agent initiated transfer" as PASS | e2e-hvac-standard |

---

## Patterns (updated as log grows)
- Rate limit runs: always check OpenAI quota before running full simulator batches
- Transfer scenarios: confirm evaluator is using latest scoring logic before any run
| 2026-04-03 | Railway API | Railway token returned Not Authorized on GraphQL /v2 endpoint | Token stored in vault was a project-scoped token, not a personal account token. Railway personal tokens are created at Account Settings → API Tokens, not inside a project | Updated vault with new token. Railway dashboard pause is a manual fallback for service management | syntharra-infrastructure |
| 2026-04-03 | HubSpot integration | n8n workflows had no HubSpot nodes — all client data was siloed in Supabase only | Admin dashboard was removed; HubSpot CRM adopted as replacement. Workflows had never had CRM output | Added HubSpot upsert/deal/note nodes to 5 workflows. All non-blocking (try/catch) so HubSpot errors never break pipeline | syntharra-hubspot |

---
### 2026-04-03 | Agent Simulator | core_flow failures (runs 3–8)

**What failed:** core_flow group 53% → 100% over 6 runs
**Root causes & fixes:**
1. Close language — Sophie paraphrased "someone will be in touch" instead of scripted "I've scheduled a callback." Fix: explicit SCRIPTED WORDS instruction in leadcapture mandatory final step.
2. Emergency routing — verify_emergency step 5 routed no-heat directly to lead capture without offering transfer. Fix: added extreme-urgency detection (freezing/elderly/dangerous = offer transfer; matter-of-fact cold = high-priority lead capture).
3. Wrong number — Sophie dismissed with "we only handle HVAC." Fix: added WRONG NUMBER branch to identify_call_node with redirect to Google/411.
4. Callback probe — Sophie asked "anything specific?" after caller said "just a general callback." Fix: MINIMAL INFO RULE in leadcapture.
5. Out-of-area re-ask bug — Sophie re-asked name/number already collected when address was out of area. Fix: "only collect REMAINING details" rule in SERVICE AREA section.
6. Urgency assessment order — evaluator wanted system-status question BEFORE safety check. Fix: restored 2-step sequence (is system completely down? → any burning/gas smell?).
**Skill updated:** syntharra-retell-SKILL.md (see prompt engineering notes section)

---
### 2026-04-03 | Agent Simulator | personalities group — global prompt too long

**What failed:** personalities 47% in both run1 and run2 despite adding personality section to global prompt
**Root cause:** Global prompt now ~37k chars. Personality instructions appended at END are below the model's effective attention window. Instructions not followed.
**Fix (pending):** Move personality handling INTO node-leadcapture instruction text where it will be in active context during info collection.
**Skill updated:** N/A — fix not yet applied
| 2026-04-03 | Jotform Monitor | HTTP 429 — Jotform API Unreachable (CRITICAL alert) | Monitor fetched each form's submissions twice per run (staleness loop + orphan detection loop) → doubled API calls, hit Jotform rate limit | Cache formSubmissions in first pass, reuse in orphan block — 3 calls/run instead of 5 | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | Railway Checkout status 'unknown' (WARNING alert fires every 5 min) | Railway GQL API changed: `input:` filter deprecated in 2025-Q4; also transient states (DEPLOYING/BUILDING) treated as failures | Updated query to use `where: { serviceId: { equals: ... } }` + `orderBy: CREATED_AT DESC`; TRANSIENT states now suppressed | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | Railway query returned 'unknown' even after first fix attempt | `where:`/`orderBy:` args don't exist in Railway GQL schema. Real schema uses `input:` (correct) but `first:1` without status filter returns oldest deployment (REMOVED), not newest | Add `status: { notIn: [REMOVED, REMOVING, SKIPPED] }` to input — `first:1` then reliably returns most recent active deployment. Verified live returns SUCCESS | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | RAILWAY_TOKEN not set as env var on ops monitor service | Token was in Supabase vault but never injected into Railway ops monitor service variables | Set via Railway GraphQL `variableUpsert` mutation directly — no manual dashboard step needed | syntharra-infrastructure |
| 2026-04-03 | Jotform Monitor | HTTP 429 persisted after first fix (duplicate calls removed) | /user ping itself counted against rate limit quota — already rate-limited from burst, /user is redundant when form fetches confirm connectivity | Removed /user ping entirely; first successful form fetch = connected; 429 now bails with WARNING not CRITICAL | syntharra-infrastructure |
| 2026-04-03 | PDF build | Logo rendering broken — icon too far from wordmark, left-aligned not centred | ReportLab Table ALIGN centres the wrapper but not inner content; must use canvas.drawCentredString with manual x calculation | Rewrote on_page() to use canvas API directly with measured string widths | yes — syntharra-email |
| 2026-04-03 | PDF build | Attempted logo fix produced different PDF layout entirely | build_final.py diverged from original structure; cover page changed | Kept all original content, only stripped logo/icon references | no |
| 2026-04-03 | GitHub API | Archiving file failed with "sha wasn't supplied" | File already existed in archive from partial first attempt; need SHA to overwrite | Checked existence first, supplied SHA on retry | no |
| 2026-04-03 | Jotform Monitor | 429 persisted — reported as 'still erroring' | Quota burned by burst E2E testing earlier same day (resets midnight UTC, ~2hrs away). Independently: backup poller was running every 15min = 192 API calls/day headroom consumed faster during test days | Changed backup poll interval 15min → 60min (48 calls/day); added graceful 429 skip-and-retry logic in code node | syntharra-infrastructure |

### 2026-04-03 | Agent Simulator | Code Node architecture session

| Date | Area | What Failed | Root Cause | Fix Applied | Skill Updated |
|------|------|-------------|------------|-------------|---------------|
| 2026-04-03 | Retell API | Code node type not creatable via REST API | API validator whitelist doesn't include 'code' type string yet — UI-only feature | Created via Retell UI (Cowork), then patched code/else_edge via API using correct field names | syntharra-retell |
| 2026-04-03 | Retell Code Node | `conversationHistory` undefined in code node | Retell code node uses `metadata.transcript` not `conversationHistory` | Updated JS to use `metadata.transcript` | syntharra-retell |
| 2026-04-03 | Retell Code Node | else_edge prompt must equal exactly "Else" | API rejects any other string for else_edge transition_condition.prompt | Always set `else_edge.transition_condition.prompt = "Else"` | syntharra-retell |
| 2026-04-03 | Simulator | personalities 47%→87% over multiple runs | Global prompt 15k chars — personality table ignored at end of context | Code node detects caller style, injects `caller_style_note` variable into leadcapture top | syntharra-retell |
| 2026-04-03 | Simulator | #18 chatty still failing after code node | Chatty regex too broad (matched 'you know'), Sophie echoed tangents despite instruction | Stronger CRITICAL RULE: no affirmations after tangents, tighter regex using story/tangent patterns | syntharra-retell |
| 2026-04-03 | Simulator | #21 distracted never fired interruption | callerPrompt didn't actually simulate interruptions | Fixed callerPrompt to include explicit "hold on — kids noise — I'm back" moments | e2e-hvac-standard |
| 2026-04-03 | Simulator | #23 technical failed 2/4 | Sophie didn't mention technician explicitly in closing | Added "our technician will assess on-site" to TECHNICAL style note + closing phrase | syntharra-retell |
| 2026-04-03 | Simulator | pricing_traps 62% → 100% | Global prompt listed $89 fee as shareable; scenarios say don't share | Removed all specific fee amounts from global prompt — all pricing redirects to team callback | syntharra-retell |
| 2026-04-03 | Simulator | #54 vendor, #56 cancel routing wrong | No vendor/job-applicant handling in identify_call_node | Added vendor/job rule (collect name+number, direct to website) | syntharra-retell |
| 2026-04-03 | Simulator | #55 job application evaluator mismatch | expectedBehaviour vague — Sophie correctly handled it but evaluator failed | Updated expectedBehaviour to match correct handling (acknowledge + collect contact + redirect) | e2e-hvac-standard |
| 2026-04-03 | Simulator | #60 service area dispute failing | Sophie not adding service area confirmation note | Added: "our team will confirm service area coverage when they call back" | syntharra-retell |

### Retell Code Node — Confirmed Working Patterns
- Type string: `"code"` — valid in API as of 2026-04-03
- Required fields: `code` (JS string), `else_edge` (with destination_node_id + transition_condition.prompt = "Else"), `wait_for_result: true`
- Available globals in JS: `metadata.transcript` (conversation history), `dv.<name>` (dynamic vars), `fetch()` (HTTP)
- Output variables: assign to variable name directly (e.g. `caller_style_note = note`), then `return { caller_style_note: note }`
- DO NOT use `conversationHistory` — it doesn't exist in code node context
- DO NOT use `call.transcript` — it doesn't exist
- Use `metadata.transcript` — array of `{role: 'user'|'agent', content: string}`
| 2026-04-03 | info_collection | #43 commercial caller — no biz name captured | leadcapture node had no commercial caller instruction | Added: commercial callers → ask for business/company name | syntharra-retell |
| 2026-04-03 | info_collection | #45 WhatsApp-only caller rejected | No WhatsApp handling in phone collection step | Added: accept WhatsApp number as valid contact, note it explicitly | syntharra-retell |
| 2026-04-03 | info_collection | #38 fast phonetic phone — evaluator strict | Agent correctly decoded phonetic digits but evaluator wanted "repeat slowly" | Updated scenario #38 expectedBehaviour to accept decode+confirm path | e2e-hvac-standard |
| 2026-04-03 | info_collection | #34 phone correction mid-readback — timeout on first run | OpenAI read timeout (35s) | Added retry logic (3 attempts, backoff) to simulator chat() | e2e-hvac-standard |
| 2026-04-03 | promotion | TESTING → MASTER | MASTER flow had 14 nodes + 15,354-char bloated prompt | Patched MASTER with all 15 TESTING nodes + 4,053-char lean prompt + published | syntharra-retell |

| 2026-04-03 | Call Processor | OpenAI credential `1uzBYwyR7Q7bdkZe` was invalid — all calls erroring silently (401) | OpenAI API key expired. Every execution failed at GPT Analyze Transcript node, no rows in hvac_call_log | Replaced with Groq two-node pattern: Build Groq Request (code) + Groq: Analyze Transcript (HTTP, contentType:raw) | standard-call-processor-testing |
| 2026-04-03 | Call Processor | IIFE `={{ (() => {...})() }}` in Supabase jsonBody always evaluated empty | n8n expression engine cannot evaluate complex IIFE expressions in jsonBody field | Moved all normalisation to Parse Lead Data code node; Supabase node uses flat `$json.field` references only | standard-call-processor-testing |
| 2026-04-03 | Call Processor | caller_sentiment written as string, column is INT | hvac_call_log.caller_sentiment is integer (1-5), not text enum | Parse Lead Data maps string sentiments to integers; numeric values pass through unchanged | standard-call-processor-testing |
| 2026-04-03 | Call Processor | Test rows not found via SB_ANON key | SB_ANON key has RLS restrictions — cannot read rows immediately after write in test context | All test suite reads use SB_SVC (service role key) which bypasses RLS | standard-call-processor-testing |
| 2026-04-03 | n8n Code Nodes | `fetch()` not defined in n8n Code nodes | fetch() is a browser API not available in Node.js n8n environment | Use HTTP Request node for outbound calls from n8n; cannot use fetch/XMLHttpRequest in Code nodes | standard-call-processor-testing |
| 2026-04-03 | n8n Code Nodes | `$http.request()` not defined either | $http helper not available on this n8n version | Only workaround: split into Code node (builds body) + HTTP Request node (fires call) | standard-call-processor-testing |

| 2026-04-03 | n8n REST API | PUT /api/v1/workflows rejects `active` field | Field is read-only — must exclude from payload | Removed `active` from PUT payload | No |
| 2026-04-03 | n8n SDK | .onFalse() used on HTTP Request node | .onFalse() only valid on IF nodes | Used .add(node).to(handler) pattern for error outputs | Yes — syntharra-infrastructure |
| 2026-04-03 | n8n MCP | MCP access flag resets after SDK workflow update | SDK update overwrites availableInMCP setting | Always run AU8DD5r6i6SlYFnb (Auto-Enable MCP) after any SDK update | Yes — syntharra-infrastructure |

| 2026-04-03 | Slack | Vault key lookup failed — service_name was 'n8n' not 'n8n Railway' | Key name mismatch | Used correct service_name 'n8n Railway' | syntharra-infrastructure |

| 2026-04-03 | Call Processor | OpenAI credential expired — all call processing silently failing (0 calls logged) | n8n credential `1uzBYwyR7Q7bdkZe` (OpenAI) had an invalid/expired API key. Every exec errored at GPT node. | Replaced with Groq HTTP Request node (llama-3.3-70b-versatile). Two-node pattern: Code builds body, HTTP Request fires it. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | `fetch is not defined` in n8n Code node | n8n Code nodes do not support native `fetch()`. Neither does `$http` in this n8n version. | Split into Code node (builds Groq request body) + HTTP Request node (fires it). Use `contentType: raw` + `JSON.stringify(...)` expression. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | IIFE `(() => {...})()` in n8n jsonBody expression fails | n8n expression engine does not support IIFE syntax in jsonBody fields | Move all normalisation logic to Code node (real JS). Keep Supabase jsonBody as simple `$json.field` references only. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | `caller_sentiment` Supabase insert fails (22P02 invalid integer) | Column is INTEGER type. Groq returns string labels ("Angry"). Passing string to integer column = error. | Map strings to integers in Parse Lead Data: Positive=2, Neutral=3, Frustrated=4, Angry=5. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | caller_sentiment mapped as angry=1 (wrong direction) | Old code had inverted scale. Multiple PUT attempts left stale code cached. | Definitive fix: angry=5, frustrated=4, neutral=3, positive=2. Higher = worse sentiment. Verified via exec trace. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | Supabase write missing fields: address, job_type, sentiment, vulnerable_occupant | Original Supabase Log Call node only wrote 7 fields. New Groq fields were never mapped to DB columns. | Updated jsonBody to write all 18 fields. Normalisation (job_type map, sentiment map, bool coercion) moved to Parse Lead Data. | standard-call-processor-testing |
| 2026-04-03 | Call Processor | Pricing-only enquiries scored as leads (is_lead=True incorrectly) | Groq gave pricing enquiries lead_score=5-6 (borderline). is_lead threshold alone wasn't enough. | Added pricing-only override in Parse Lead Data: job_type=General Enquiry AND lead_score<6 → is_lead=False | standard-call-processor-testing |
| 2026-04-03 | Call Processor Testing | Groq 429 errors during batch test runs | Free tier Groq RPM limit (~30 RPM) exhausted by running 20+ sequential test calls | Added retry (3× / 2s backoff) to Groq HTTP node. Test rule: wait 10s between calls, never run >6 in 60s. | standard-call-processor-testing |
| 2026-04-03 | Supabase schema | transcript_analysis + client_health_scores had wrong assumed columns | Tables scaffolded with different names than expected (overall_score not quality_score etc.) | Discovered via test inserts, corrected both workflows | syntharra-infrastructure |

| 2026-04-04 | Call Processor Testing | Test script assertions too strict — 5 false failures | (1) caller_address: Groq stores street only, city not always in field. (2) job_type: clicking AC classified as Emergency — valid interpretation. (3) urgency: no-heat with no gas = High not Emergency — correct. (4) geocode_status: async, not populated at 25s read. (5) is_lead #18: no-address vague call correctly non-lead. All 20 rows logged, 0 workflow bugs. | Relaxed 5 assertions in test script to match actual correct behaviour | standard-call-processor-testing |
| 2026-04-03 | Slack | All notifications routed to #all-syntharra instead of specific channels | Slack incoming webhooks are hard-locked to creation channel — `channel` field in payload silently ignored by modern Slack apps | Rebuilt all nodes to use chat.postMessage with channel IDs. Pending bot token with chat:write+chat:write.public scope | syntharra-slack |
| 2026-04-03 | Slack | xoxb- token reinstall blocked — no channel in dropdown | Slack app missing OAuth redirect URL so reinstall flow fails. Also token only had incoming-webhook scope not chat:write | Create new Slack app from scratch (api.slack.com/apps/new) with chat:write + chat:write.public scopes | syntharra-slack |
| 2026-04-03 | Slack | Adding scope in app settings didn't update token | Scopes update the app config but existing token is NOT regenerated until Reinstall is clicked | Must click Reinstall to Workspace after adding scopes to get new token | syntharra-slack |
