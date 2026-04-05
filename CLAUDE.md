## MANDATORY SESSION PROTOCOL — NON-NEGOTIABLE

### Session Start (run FIRST, every session, no exceptions)
```bash
python /sessions/happy-intelligent-goodall/mnt/Cowork/session_start.py
```
This loads live TASKS.md, REFERENCE.md, and FAILURES.md from GitHub. Working without it = working blind.

### Session End (run BEFORE closing, every session)
```bash
python /sessions/happy-intelligent-goodall/mnt/Cowork/session_end.py --topic "TOPIC" --summary "SUMMARY" --tasks "task1|task2"
```
Pushes session log to GitHub. Logs open tasks to Supabase admin_tasks.

### GitHub Operations (use github_helper.py for all GitHub work)
```python
import sys; sys.path.insert(0, '/sessions/happy-intelligent-goodall/mnt/Cowork')
from github_helper import gh_fetch, gh_push, gh_append, gh_get_sha
```

---

# Syntharra — Cowork Workspace Rules
# Always mount: C:\Users\danie\OneDrive\Desktop\Cowork

## Who I Am
- **Dan Blackmore**, Founder & CEO of **Syntharra** — a global AI Solutions company providing AI Receptionists to trade industry businesses worldwide.
- Primary focus: HVAC-first US launch, expanding to plumbing, electrical, cleaning.
- Platform: Windows 11 | Tools: Cowork (desktop), Claude web.

---

## Agent Behaviour — Always Parallel & Agentic

**Default to multi-agent execution. Never single-thread when parallel is possible.**

- For any task with 2+ independent workstreams, spawn subagents in parallel immediately — no asking.
- Pattern: **Orchestrator → Specialist Subagents**. One lead coordinates; specialists execute simultaneously.
- Break complex tasks into a DAG. Identify what can run concurrently and launch it all at once.
- Do work proactively — make a reasonable call and move forward rather than stopping to clarify.
- Always add a verification/QA subagent pass at the end before presenting results.
- Use the GSD agent library in `get-shit-done/agents/` for specialised subagent roles (debugger, planner, executor, researcher, UI auditor, etc.)

When to go agentic without being asked:
- Research → one subagent per source/topic, in parallel
- Document creation → research + writing + formatting agents simultaneously
- Competitive analysis → one agent per competitor, all at once
- Marketing batch → all channels/formats in parallel
- Code + tests → write and test in parallel
- Any GSD command from `get-shit-done/commands/` → use the relevant workflow

---

## Communication Style

- No recaps, summaries, or filler at the end of responses. Dan reads the output directly.
- No "Great question!" or "Certainly!" openers.
- Technical output (JSON, SQL, API responses, configs) — raw and unfiltered.
- Be direct. Call out problems and better approaches without being asked.
- Short responses for simple tasks. Detailed only when complexity warrants it.

---

## Skills — Auto-Trigger, Always

Full skill library is loaded. Check available skills before starting any task. Trigger automatically — never make Dan ask.

| Category | Key Skills |
|---|---|
| Documents | `docx`, `pdf`, `xlsx`, `pptx` |
| Marketing | `copywriting`, `cold-email`, `seo-audit`, `content-strategy`, `social-content`, `linkedin-content`, `email-sequence`, `paid-ads`, `ad-creative`, `launch-strategy`, `competitor-alternatives` |
| CRO | `page-cro`, `signup-flow-cro`, `onboarding-cro`, `popup-cro`, `paywall-upgrade-cro`, `form-cro`, `churn-prevention` |
| AI Media | `ai-image-generation`, `ai-video-generation`, `elevenlabs-tts`, `elevenlabs-dialogue`, `ai-avatar-video`, `flux-image`, `google-veo`, `ai-music-generation` |
| Dev / Data | `supabase-postgres-best-practices`, `vercel-react-best-practices`, `python-sdk`, `javascript-sdk`, `python-executor` |
| Design | `excalidraw-diagram`, `frontend-design`, `data-visualization`, `pitch-deck-visuals`, `adapt`, `animate`, `audit`, `bolder`, `clarify`, `colorize`, `critique`, `delight`, `distill`, `harden`, `normalize`, `optimize`, `overdrive`, `polish`, `quieter`, `typeset` |
| Research | `firecrawl`, `web-search`, `customer-research`, `competitor-teardown`, `notebooklm` |
| Sales | `sales:account-research`, `sales:call-prep`, `sales:draft-outreach`, `sales:competitive-intelligence`, `sales:pipeline-review`, `apollo:prospect`, `apollo:enrich-lead`, `apollo:sequence-load` |
| Syntharra | `syntharra-marketing:content-engine`, `syntharra-marketing:prospector`, `syntharra-marketing:outreach`, `syntharra-marketing:intelligence`, `syntharra-marketing:competitor-watch`, `syntharra-marketing:conversion-optimizer`, `syntharra-marketing:video-content`, `syntharra-marketing:weekly-plan`, `syntharra-marketing:batch-content` |
| Data | `data:analyze`, `data:sql-queries`, `data:build-dashboard`, `data:statistical-analysis`, `data:create-viz` |
| Operations | `operations:process-doc`, `operations:runbook`, `operations:risk-assessment`, `operations:status-report` |

---

## Connected MCP Tools — Use Proactively

These are live and authenticated. Use without asking:

| MCP | Tools Available | Use For |
|---|---|---|
| **GitHub** (`mcp__562ca274-ff68-4873-8410-8ecc5c606bd6__*`) | get_file_contents, create_or_update_file, push_files, search_code, list_commits, create_branch, create_pull_request | All GitHub reads/writes — session logs, TASKS.md, REFERENCE.md, FAILURES.md, code pushes |
| **Gmail** | search, read, draft | Emails, threads, inbox triage |
| **Google Calendar** | list, create, update, find free time | Scheduling, meetings, availability |
| **Google Drive** | search, fetch | Find/read documents and files |
| **Slack** | send, search, read channel/thread, schedule | Team comms, announcements, DMs |
| **HubSpot CRM** | get/search contacts, deals, pipeline | Lead status, CRM lookups |
| **Stripe** | list/create customers, invoices, subscriptions, refunds, payments | Billing, revenue, payment ops |
| **Supabase** | execute SQL, migrations, edge functions, logs, branches | All database operations |
| **n8n** | create/update/execute/publish workflows, get node types | Automation building and management |
| **JotForm** | fetch, search, create/edit forms, create submissions | Form data, onboarding submissions |
| **Apollo** | prospect leads, enrich contacts, load sequences | Outbound prospecting, lead research |
| **Scheduled Tasks** | create, list, update | Recurring automations and reminders |
| **Claude in Chrome** | navigate, click, fill forms, scrape, screenshot | Browser automation, web research |
| **PDF Viewer** | read, display, save PDFs | Document processing |

---

## The Product

**Syntharra AI Receptionist** — fully automated phone receptionist for trade businesses.
- Answers every call 24/7. Books jobs. Qualifies leads. Sends confirmations.
- Built on Retell AI. No human involvement after setup.
- Standard: $497/mo | Premium: $997/mo
- Target: HVAC contractors running 3–20 trucks in the USA
- Core value prop: Trade owners miss 30–40% of calls. Each missed call = $300–$2,000 lost. Syntharra captures every call.
- Website: syntharra.com | Demo: Cal.com on /demo.html | CRM: HubSpot

---

## Syntharra Brand

All branded output must follow the Syntharra brand standard.

- **Primary colour**: `#6C63FF` (violet) | **Font**: Inter
- Full brand spec: `C:\Users\danie\.claude\skills\theme-factory\themes\syntharra.md`
- Logo files: `C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_logo\`
- Emails: light theme only (`#F7F7FB` bg, `#FFFFFF` card), system fonts (Georgia/Arial), hosted PNG logo — never base64 SVG
- Documents: full logo top-left, Inter headings, `#6C63FF` H2, `#4A4A6A` body
- Hosted email-safe icon: `https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png`

---

## Infrastructure (Use It — Don't Rebuild)

| Asset | Status | Location |
|---|---|---|
| syntharra.com | Live | GitHub Pages |
| 21 blog articles | Live | syntharra.com/blog |
| AI Readiness Quiz | Live | /ai-readiness.html |
| Revenue Calculator | Live | /calculator.html |
| Plan Quiz | Live | /plan-quiz.html |
| Google Ads landing pages | Live | /lp/hvac-*, /lp/plumbing-*, /lp/electrical-* |
| Demo landing page | Live | /demo.html |
| Cold email system | Built, not activated | n8n + SMTP2GO |
| HubSpot CRM | Live | Full pipeline configured |
| Supabase lead DB | Live | website_leads table |
| Cal.com booking | Live | On demo page |
| Admin dashboard | Live | Railway, auto-deploys from `main` |

---

## n8n Workflow Rules

1. **No `fetch()` in Code nodes** — use HTTP Request nodes, or `this.helpers.httpRequest({...})` inside Code nodes.
2. **`responseMode: responseNode`** requires a linear chain — respond node must be on a single path, no splits.
3. **Split In Batches v3**: `output[1]` = loop items (has more), `output[0]` = done.
4. **HTTP Request v4.2** wraps array responses as `{ data: [...] }` — always access via `.data`.
5. **`runOnceForEachItem` returns** `{ json: {...} }` not `[{ json: {...} }]` — don't double-wrap.
6. **Groq free tier**: 30 RPM / 6000 TPM — add 10s Wait node inside every batch loop.
7. **Cross-node refs**: safe in HTTP Request expressions; unreliable in Code nodes — use `$input.all()` in Code nodes.
8. **SMTP2GO auth**: `api_key` in JSON body (not header). Format: `{ api_key, sender, to, subject, html_body }`.

### Workflow IDs
- `SYNTHARRA_AGENT_TEST_RUNNER` = `3MMp9J8QN0YKgA6Q`
- `SYNTHARRA_FIX_APPROVER` = `ZAAtRETIIVZSMMDk`
- Standard Onboarding = `4Hx7aRdzMl5N0uJP` (webhook: `jotform-hvac-onboarding`)
- Premium Onboarding = `kz1VmwNccunRMEaF` (webhook: `jotform-hvac-premium-onboarding`)

---

## Retell AI Rules

- **Always fetch before updating**: `GET /get-conversation-flow/{flow_id}` first, merge changes, then `PATCH`. Never push a stripped/reconstructed node.
- **Groq 403 = firewall block** (not rate limit). Switch to OpenAI GPT-4.1-mini as fallback.
- **Prompt optimizer patch cap**: Max 3–4 patches per round. More causes prompt bloat and regression.

---

## Agent Testing System

### Supabase Tables (project: `hgheyqwnrcvwtgngqdnq`)
- `agent_test_scenarios` — 115 scenarios (100 standard, 15 premium)
- `agent_test_results` — test run results
- `agent_pending_fixes` — diagnosis only
- `infra_health_checks` — health check results
- `e2e_test_results` — E2E results

### Baselines
- Best result: **90/95 pass (94.7%)** — Round 5, `best_prompt_r5_95%.json` in `claude_code/`
- Always start optimizer from `best_prompt_r5_95%.json`, not from live flow
- Test webhook: `POST /webhook/agent-test-runner`

---

## Admin Dashboard (`syntharra-admin` repo)
- Single-file SPA: `public/index.html` — auto-deploys to Railway from `main`
- Nav: `nav(id, el)` toggles `class="section"` divs by `id="sec-{id}"`
- **JS rule**: `var` not `const`/`let` inside render functions; one `<style>` block; `overflow-x:clip` on body
- A single JS SyntaxError crashes ALL navigation — run `node --check` on extracted script before pushing
- Extract: `python3 -c "open('test_script.js','w').write(open('index.html').read().split('<script>')[-1].split('</script>')[0])"`

---

## Build Scripts (`claude_code/` directory)
- `build_wf1.py` / `build_wf2.py` — main workflow builders
- `build_wf*_clean.py` — working/current versions
- Run from `claude_code/`: `python build_wf1_clean.py`

---

## Vendor Rules

- **Never use Twilio.** Email: SMTP2GO. SMS: Telnyx (not live yet).

---

## Get Shit Done (GSD) — Meta-Prompting System

GSD commands and agents are installed in `get-shit-done/` within this workspace.

- **Commands**: `get-shit-done/commands/` — slash-style workflows (do, debug, autonomous, execute-phase, new-project, health, forensics, etc.)
- **Agents**: `get-shit-done/agents/` — specialist subagent roles (planner, executor, debugger, researcher, UI auditor, doc writer, security auditor, etc.)
- **References**: `get-shit-done/references/` — best practices and patterns
- **Workflows**: `get-shit-done/workflows/` — structured multi-step workflows

Use GSD agent roles when spawning subagents for complex tasks. Reference `gsd-planner.md` for planning phases, `gsd-executor.md` for execution, `gsd-debugger.md` for debugging.

---

## END-OF-SESSION ENFORCEMENT — NON-NEGOTIABLE

**Every session MUST end with all of the following. No exceptions. No skipping.**

### 1. Push Session Log to GitHub
```python
import sys; sys.path.insert(0, '/sessions/happy-intelligent-goodall/mnt/Cowork')
from github_helper import gh_push
# Push to: docs/session-logs/YYYY-MM-DD-topic.md
```
Or via GitHub MCP: `mcp__562ca274-ff68-4873-8410-8ecc5c606bd6__create_or_update_file`

### 2. Update TASKS.md on GitHub
Push the current open task list to `docs/TASKS.md` in `Syntharra/syntharra-automations`. Under 40 lines. Open work only.

### 3. Log Incomplete Tasks to Supabase
Use Supabase MCP (`mcp__0e5f1d37-9510-4d3f-87c0-0808af0ce81d__execute_sql`) to insert any tasks discussed but not completed:

```sql
INSERT INTO public.admin_tasks (title, category, priority) VALUES ('...', '...', '...');
```

Categories: `Pre-Launch`, `Agent Testing`, `Infrastructure`, `Marketing`, `Operations`
Priorities: `critical`, `high`, `medium`, `low`

### 4. Update FAILURES.md (if any bugs fixed this session)
Append one row per fix: `date | area | what failed | root cause | fix applied | skill updated`

### 5. Update REFERENCE.md (if any IDs changed)
Push to `docs/REFERENCE.md` if any agent IDs, flow IDs, workflow IDs, or URLs changed.

### 6. Push ALL Changed Files
Every file edited this session must be pushed to GitHub before closing. **Never end a session with unpushed work.**

### 7. Update Auto-Memory (if significant decisions made)
Write to `/sessions/happy-intelligent-goodall/mnt/.auto-memory/` if anything material was learned, decided, or discovered.

---

**FAILURE TO PUSH = SESSION NOT CLOSED.** If GitHub writes are blocked (403), note it explicitly and give Dan the exact files + content to push manually. Do not silently skip.
