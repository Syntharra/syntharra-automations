---
name: syntharra-admin
description: >
  Complete reference for all work on the Syntharra Internal Admin Dashboard at admin.syntharra.com.
  ALWAYS load this skill when: editing index.html or email.html in the syntharra-admin repo,
  adding new sections or nav items, modifying Supabase data loading, adding KPI cards or stats,
  updating the AI assistant, changing the ops monitor, modifying billing/clients/call logs views,
  adding new features, fixing bugs, or deploying any changes. This skill contains the full
  file structure, all section IDs, all JS functions, Supabase queries, design system, and
  the exact push workflow for shipping changes.
---

## Session Rules (CRITICAL — Every Chat)

At the **START** of every chat touching the admin dashboard:
1. Fetch `public/index.html` from `Syntharra/syntharra-admin` to get current live version + SHA
2. Also fetch `server.js` if working on backend/AI assistant/auth

At the **END** of every chat that changes the dashboard:
1. Push updated file(s) to GitHub (see push pattern below)
2. Railway auto-deploys from the `main` branch — changes go live in ~60 seconds
3. Verify live at `https://admin.syntharra.com/`

---

## Repo & Deployment

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-admin` |
| Live URL | `https://admin.syntharra.com/` |
| Auth | HTTP Basic Auth — `ADMIN_USER` / `ADMIN_PASS` env vars in Railway |
| Default credentials | `admin` / `syntharra2026` (change via Railway env) |
| Hosting | Railway — auto-deploys from `main` branch |
| Runtime | Node.js + Express (`server.js`) |
| Frontend | Single-file vanilla JS — `public/index.html` |
| Email page | `public/email.html` (Email Intelligence section) |
| Current SHA (index.html) | fetch fresh at start of every chat — do not rely on cached SHA |

---

## Fetch Current File (Python)

```python
import requests, base64

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"  # from syntharra_vault
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

r = requests.get(
    "https://api.github.com/repos/Syntharra/syntharra-admin/contents/public/index.html",
    headers=headers
).json()

current_sha = r["sha"]
content = base64.b64decode(r["content"]).decode()
```

---

## Push Updated File (Python)

```python
import requests, base64, json

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}

def push_file(new_content, current_sha, filepath, commit_msg):
    url = f"https://api.github.com/repos/Syntharra/syntharra-admin/contents/{filepath}"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(new_content.encode()).decode(),
        "sha": current_sha
    }
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    return r.json()

# Example:
push_file(updated_html, current_sha, "public/index.html", "admin: add xyz feature")
```

**Commit message prefix:** always `admin:` — e.g. `admin: add pipeline section`, `admin: fix billing query`

---

## Architecture Overview

```
admin.syntharra.com
    │
    ├── server.js (Express, Railway)
    │     ├── HTTP Basic Auth middleware
    │     ├── POST /api/ai  → Groq LLM proxy (llama-3.3-70b-versatile)
    │     ├── GET  /api/health
    │     └── Static files from /public/
    │
    └── public/index.html (single-file SPA)
          ├── CSS (~250 lines, one <style> block)
          ├── HTML sections (one per nav item)
          └── JS (~1800 lines, vanilla, no frameworks)
                ├── Supabase REST queries (anon key, client-side)
                ├── Jotform REST API (direct, not via proxy — Jotform MCP connector is broken)
                ├── Ops monitor data (from syntharra-ops-monitor endpoint)
                └── AI Assistant (POST /api/ai)
```

**Key principle:** Single-file, no build step, no frameworks. All CSS/HTML/JS in `index.html`.
Always use `str.replace()` pattern for edits — never rewrite the whole file.

---

## Design System

| Token | Value |
|---|---|
| `--v` | `#6C63FF` (violet primary) |
| `--vl` | `#F0EFFB` (violet light bg) |
| `--vd` | `#5550E8` (violet dark/hover) |
| `--cyan` | `#00D4FF` |
| `--bg` | `#F4F5F9` (page bg) |
| `--surface` | `#fff` (card bg) |
| `--border` | `#E4E4EF` |
| `--border2` | `#F0F0F8` (subtle divider) |
| `--text` | `#1A1A2E` |
| `--text2` | `#52526E` |
| `--text3` | `#9090AA` (muted) |
| `--text4` | `#C0C0D8` (very muted) |
| `--green` | `#12B76A` |
| `--gbg` / `--gtxt` | `#ECFDF3` / `#027A48` |
| `--amber` | `#F59E0B` |
| `--abg` / `--atxt` | `#FFFAEB` / `#B54708` |
| `--red` | `#F04438` |
| `--rbg` / `--rtxt` | `#FEF3F2` / `#B42318` |
| `--sw` | `232px` (sidebar width) |

**Font:** `Inter` (400, 500, 600, 700) from Google Fonts. Body 14px.
**Sidebar width:** 232px fixed, sticky.
**Breakpoints:** 1100px (4-col → 2-col), 768px (mobile sidebar), 480px (compact stats)

---

## Navigation Sections

| Section ID | Nav label | data-sec | JS load function |
|---|---|---|---|
| `sec-overview` | Dashboard | `overview` | `renderOverview()` |
| `sec-clients` | Clients | `clients` | `renderClients()` |
| `sec-calls` | Call Logs | `calls` | `renderCallLogs()` |
| `sec-billing` | Billing | `billing` | `renderBilling()` |
| `sec-forms` | Onboarding Forms | `forms` | `renderForms()` |
| `sec-agents` | AI Agents | `agents` | `renderAgents()` |
| `sec-opsmonitor` | Ops Monitor | `opsmonitor` | `loadOpsData()` |
| `sec-marketing` | Marketing Pipeline | `marketing` | `renderMarketing()` |
| `sec-settings` | Settings | `settings` | (static HTML) |
| `sec-testing` | System Testing | `testing` | calls `switchTestTab('infra')` on nav load |
| `sec-ai` | AI Assistant | `ai` | `aiSend()` |
| `/email.html` | Email Intelligence | (external link) | separate page |

Nav badges:
- `nav-clients-badge` — client count (violet)
- `nav-forms-badge` — pending forms (amber)
- `nav-alert-badge` — ops alerts (red, shows `!`)
- `nav-email-badge` — email count (violet)

---

## System Testing Section (sec-testing)

The Agent Scenario Testing sub-tab was **removed**. The section now has two sub-tabs only:

### Sub-tabs
| Tab ID | Panel ID | Function |
|---|---|---|
| `tab-infra` | `test-panel-infra` | `runHealthChecks()` |
| `tab-e2e` | `test-panel-e2e` | `runE2ETests()` |

### Tab switching
```javascript
switchTestTab('infra')  // default on nav
switchTestTab('e2e')
```
`switchTestTab()` only iterates `['infra','e2e']` — agent tab removed.

### Infrastructure Panel IDs
| ID | Content |
|---|---|
| `run-health-btn` | Trigger button |
| `infra-last-run` | Last run timestamp label |
| `infra-summary-bar` | Hidden until first run — shows overall pass/fail counts |
| `infra-summary-inner` | Inner div of summary bar (bg changes green/red) |
| `infra-summary-text` | "All systems operational" or "X systems need attention" |
| `infra-pulse` | Coloured dot indicator |
| `infra-pass-count` | Number passed |
| `infra-fail-count` | Number failed |
| `infra-total-count` | Total checks |
| `infra-grid` | System cards grid |

### E2E Pipeline Panel IDs
| ID | Content |
|---|---|
| `run-e2e-btn` | Trigger button |
| `e2e-last-run` | Last run timestamp |
| `e2e-summary-bar` | Hidden until run — pass/fail/skip counts |
| `e2e-summary-text` | Run status summary |
| `e2e-pass-count` | Passed count |
| `e2e-fail-count` | Failed count |
| `e2e-skip-count` | Skipped count |
| `e2e-results-list` | Test row cards container |

### HEALTH_CHECKS array (what gets tested)
Defined as `var HEALTH_CHECKS = [...]` — systems tested:
- **Supabase:** Connection, Call Log Table, Vault Accessible
- **Retell:** Standard Agent, Demo Agent Jake, Demo Agent Sophie, Conversation Flow
- **Stripe:** Checkout Server
- **n8n:** Stripe Webhook, Jotform Webhook (test runner webhook removed)
- **Jotform:** Standard Form, Premium Form
- **Website:** syntharra.com, checkout.syntharra.com
- **OAuth:** auth.syntharra.com

> ⚠️ `agent_test_results` Supabase table check and n8n `agent-test-runner` webhook check were removed when Agent Scenario Testing was deprecated.

### E2E_TESTS array (what gets tested)
Defined as `var E2E_TESTS = [...]`:
0. Standard Checkout Server — HEAD to checkout server health
1. Standard Call Processing — POST to hvac-std-call-processor webhook
2. Jotform Submission Flow — GET Standard form via Jotform API
3. Premium Call Processing — POST to hvac-prem-call-processor webhook
4. Weekly Report Trigger — skipped in auto-run (manual only)
5. Minutes Calculator — checks billing_cycles table is accessible

Results are saved to `e2e_test_results` Supabase table after 5s delay.
Infra results saved to `infra_health_checks` Supabase table immediately after run.

---

## Removed: Agent Scenario Testing

The following were **removed** and are no longer in the codebase. Do NOT attempt to reference or restore:

**HTML removed:** Agent Tests tab, progress bar, pass-rate stats cards, run history cards, failed scenarios table, agent/group select dropdowns.

**JS functions removed:**
- `loadTestingData()` — polled `agent_test_run_summary` and `agent_pending_fixes`
- `renderTestingStats()` — populated 4 KPI stat cards
- `renderTestRuns()` — built run history list
- `renderGroupBreakdown()` — built scenario group breakdown
- `populateRunFilter()` — populated run filter dropdown
- `renderFailedScenarios()` — built failed scenario table
- `copyScenarioDetails()` — clipboard copy helper
- `startTestRun()` — sent to n8n webhook `agent-test-runner`

**Supabase tables no longer used (can be deleted):**
- `agent_test_run_summary`
- `agent_test_results`
- `agent_pending_fixes`

**n8n workflow no longer needed:**
- Agent Test Runner webhook workflow

---

## Key HTML Element IDs

### Overview
| ID | Content |
|---|---|
| `ov-clients` | Active clients count |
| `ov-mrr` | Monthly revenue |
| `ov-calls` | Calls today |
| `ov-hot` | Hot leads (7d) |
| `ov-calls-list` | Recent calls feed |
| `ov-status-list` | System status mini-list |
| `ov-minutes` | Minutes used progress bars |
| `ov-actions-list` | Pending actions list |
| `ov-actions-badge` | Action count badge |
| `mrrChart` | Chart.js MRR canvas |

### Clients
| ID | Content |
|---|---|
| `clients-tbody-std` | Standard clients table body |
| `clients-tbody-prem` | Premium clients table body |
| `clients-std-count` | Standard client count badge |
| `clients-prem-count` | Premium client count badge |
| `clients-count` | Total count badge |
| `client-search` | Search input |

### Calls
| ID | Content |
|---|---|
| `calls-tbody` | Call logs table body |

### Billing
| ID | Content |
|---|---|
| `bill-mrr` | MRR value |
| `bill-arr` | ARR projected |
| `bill-subs` | Active subs count |
| `billing-tbody` | Billing table body |

### AI Assistant
| ID | Content |
|---|---|
| `ai-msgs` | Chat messages container |
| `ai-input` | Textarea input |
| `ai-send` | Send button |
| `ai-chips` | Quick-prompt chips |

### Ops Monitor
| ID | Content |
|---|---|
| `om-systems` | Systems online count |
| `om-alerts` | Active alerts count |
| `om-mrr` | MRR display |
| `om-calls24` | Calls in last 24h |
| `om-systems-grid` | System health cards grid |
| `om-alerts-list` | Alert log list |
| `om-updated` | Last updated timestamp |

### Marketing
| ID | Content |
|---|---|
| `mkt-sourced` | Leads sourced count |
| `mkt-emailed` | Emails sent count |
| `mkt-hot` | Hot leads count |
| `mkt-demos` | Demos booked count |
| `mkt-pipeline` | Pipeline kanban board |

### Global
| ID | Content |
|---|---|
| `sys-pill` | Top-right system health pill (green/amber/red) |
| `sys-text` | Text inside sys-pill |
| `clock-gmt` | GMT clock display |
| `page-title` | Top bar page title |
| `page-sub` | Top bar subtitle |
| `agents-grid` | AI agents card grid |
| `agents-count` | Agent count badge |
| `forms-list` | Jotform submissions list |
| `forms-badge` | Forms count badge |

---

## Supabase Connection (Client-Side JS)

```javascript
const SB_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'; // anon key — safe client-side
const SB_H   = { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY };

async function sbFetch(path) {
  const r = await fetch(SB_URL + path, { headers: SB_H });
  if (!r.ok) throw new Error('Supabase error: ' + r.status);
  return r.json();
}
```

### Common Queries Used

```javascript
// All standard clients
sbFetch('/hvac_standard_agent?select=*&order=created_at.desc')

// All premium clients
sbFetch('/hvac_premium_agent?select=*&order=created_at.desc')

// Recent calls (last 50, all clients)
sbFetch('/hvac_call_log?select=*&order=created_at.desc&limit=50')

// Subscriptions
sbFetch('/client_subscriptions?select=*')

// Stripe payments
sbFetch('/stripe_payment_data?select=*&order=created_at.desc&limit=20')

// Marketing leads
sbFetch('/website_leads?select=*&order=created_at.desc&limit=100')

// Billing cycles
sbFetch('/billing_cycles?select=*&order=created_at.desc')

// E2E test results (write only, after runE2ETests)
// POST /e2e_test_results

// Infra health checks (write only, after runHealthChecks)
// POST /infra_health_checks
```

---

## All JavaScript Functions

### Core / Navigation
| Function | Purpose |
|---|---|
| `nav(id, el)` | Switch active section, update topbar title |
| `toggleSidebar()` | Mobile sidebar open/close |
| `closeSidebar()` | Close mobile sidebar |
| `updateClock()` | Update GMT clock every second |
| `sbFetch(path)` | Supabase REST helper |

### Formatters
| Function | Purpose |
|---|---|
| `fmtTime(d)` | Format ISO → time string (GMT) |
| `fmtDate(d)` | Format ISO → "15 Jan 2026" |
| `fmtDateShort(d)` | Format ISO → "Jan 2026" |
| `fmtDur(s)` | Seconds → "2m 34s" |
| `fmtPhone(p)` | Format US phone number |
| `timeAgo(iso)` | ISO → "5m ago" |

### Data Loading
| Function | Purpose |
|---|---|
| `loadLiveData()` | Master loader — fetches all Supabase data, calls all render functions |
| `loadOpsData(force)` | Fetch ops monitor health data (30s cache) |

### Render Functions
| Function | Purpose |
|---|---|
| `renderOverview(clients, calls, subs)` | Build overview KPIs, recent calls, minutes bars, status |
| `renderClients(clients, subs)` | Build clients tables (Standard + Premium split) |
| `renderClientGroups(clients, subs)` | Sub-render for client table rows |
| `renderCallLogs(calls)` | Build call logs table |
| `renderBilling(clients, subs, stripeData)` | Build billing KPIs and table |
| `renderForms()` | Fetch + render Jotform submissions |
| `renderAgents(clients)` | Build AI agent cards grid |
| `renderMarketing()` | Fetch website_leads, build pipeline + KPIs |
| `renderOpsKPIs(status, alerts)` | Build ops monitor KPI cells |
| `renderOpsSystems(systems)` | Build system health cards |
| `renderOpsAlerts(alerts)` | Build alert log rows |
| `renderOvStatus(systems)` | Mini system status in overview |
| `updateSysPill(healthy)` | Update top-right system health pill |

### System Testing
| Function | Purpose |
|---|---|
| `switchTestTab(tab)` | Toggle between 'infra' and 'e2e' panels |
| `runHealthChecks()` | Run all HEALTH_CHECKS, call renderInfraResults() |
| `renderInfraResults(results)` | Render system cards grid + update summary bar |
| `runE2ETests()` | Run all E2E_TESTS sequentially, update row statuses |

### Interactions
| Function | Purpose |
|---|---|
| `setTrade(trade, btn)` | Filter clients by trade tab |
| `filterClients()` | Live search filter on client table |
| `setCallFilter(f, btn)` | Filter calls by type (all/lead/emergency) |
| `exportCallsCsv()` | Download current call logs as CSV |
| `openClientModal(c)` | Open client detail modal |
| `openNewClientModal()` | Link to Jotform onboarding |
| `closeModal(e)` | Close modal on overlay click |
| `startCountdown()` | Animate auto-refresh countdown bar |

### AI Assistant
| Function | Purpose |
|---|---|
| `buildLiveContext()` | Assemble live data summary string for AI system prompt |
| `aiSend(override)` | Send message to /api/ai, render response |
| `addAiMsg(role, text, isError)` | Append message bubble to chat |
| `aiKeydown(e)` | Enter to send, Shift+Enter for newline |
| `aiAutosize(el)` | Auto-resize textarea |
| `aiChip(el)` | Send chip text as message |
| `clearAiChat()` | Reset chat to welcome message |

---

## AI Assistant (Backend)

- **Route:** `POST /api/ai` in `server.js`
- **Model:** Groq `llama-3.3-70b-versatile` (free tier)
- **Env var required:** `GROQ_API_KEY` in Railway
- **System prompt includes:** Full Syntharra knowledge base (hardcoded in `server.js`) + live context string built by `buildLiveContext()` on the frontend
- **If no GROQ_API_KEY:** Returns 503 with message to add it to Railway env
- **Message history:** Sends last 20 messages for context
- **Max tokens:** 1024

To update AI knowledge base: edit the `SYNTHARRA_KNOWLEDGE` template literal in `server.js`.

---

## Badge CSS Classes

| Class | Colour | Use |
|---|---|---|
| `.bg` | Green | Active, success, live |
| `.bp` | Violet | Plan badge, primary info |
| `.ba` | Amber | Warning, pending, test mode |
| `.br` | Red | Error, blocked, critical |
| `.bgr` | Grey | Neutral count, default |
| `.bb` | Blue | Info, secondary |

---

## Common Tasks

### Add a new nav section
1. Add `.nav-item` div in sidebar with `data-sec="newsec"` and `onclick="nav('newsec',this)"`
2. Add `<div class="section" id="sec-newsec">` in content area
3. Add case in `nav()` function to set page title
4. Add render call in `loadLiveData()` if data is needed

### Add a new KPI stat card
Follow the existing pattern:
```html
<div class="stat">
  <div class="stat-accent" style="background:var(--cyan)"></div>
  <div class="stat-label">Label</div>
  <div class="stat-value" id="new-stat-id">—</div>
  <div class="stat-sub">Subtitle text</div>
</div>
```
Then set value in JS: `el('new-stat-id').textContent = value;`

### Add a new HEALTH_CHECK endpoint
Add to the `HEALTH_CHECKS` array:
```javascript
{system:'SystemName', check:'Check Name', url:'https://endpoint.com/health', method:'GET', headers:{}}
// or for authenticated endpoints:
{system:'Supabase', check:'New Table', url:'https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/table_name?select=id&limit=1', method:'GET', headers:{apikey:SB_KEY, Authorization:'Bearer '+SB_KEY}}
// Use HEAD method + mode:'no-cors' for endpoints that don't allow CORS GET
```

### Add a new E2E test
Add to `E2E_TESTS` array and add a corresponding fetch call in `runE2ETests()` matching the index.

### Add a new table column
1. Add `<th>` in thead
2. Add `<td>` in the row-building loop in the relevant render function
3. Add `class="hide-m"` for columns that should hide on mobile

### Add a checklist item
```html
<div class="cl-item"><span>⬜</span><span>Task description here</span></div>
<!-- or: ✅ for complete -->
```

### Update the AI knowledge base
Edit the `SYNTHARRA_KNOWLEDGE` template literal in `server.js` and push.

### Update the Stripe Go-Live checklist
Edit the `.cl-item` divs inside `sec-billing` in `index.html`. Change `⬜` to `✅` as items complete.

### Update pending actions in Settings
Edit the `.feed-row` blocks inside the "Pending Actions" card in `sec-settings`.

---

## Key Patterns & Rules

1. **Single `<style>` block** — all CSS stays in the one block at top of `<head>`. Never add a second.
2. **`overflow-x:clip`** on body — never use `overflow:hidden` on html/body.
3. **`var` not `const/let`** in render functions — dashboard JS uses function-scoped vars for compatibility.
4. **`el(id)`** helper — shorthand for `document.getElementById(id)`.
5. **Anon key is safe** — Supabase anon key is in client-side HTML. RLS controls data access.
6. **No frameworks** — vanilla JS only. No React, Vue, jQuery.
7. **Edit with str.replace** — never rewrite the whole file. Always fetch → str.replace → push.
8. **Railway auto-deploys** — push to `main` → Railway detects change → deploys in ~60s.
9. **One commit per feature** — prefix with `admin:` e.g. `admin: add revenue chart`.
10. **`TZ = 'Europe/London'`** — all dates/times formatted in Dan's timezone (GMT/BST).
11. **CRITICAL: JS onclick string escaping** — When building HTML strings with inline onclick handlers inside single-quoted JS strings, use `\'` (escaped quote) NOT `''` (two bare single quotes). Two bare quotes inside a single-quoted string TERMINATE the string and create a JS syntax error that silently breaks the ENTIRE script. Correct pattern: `h += '<button onclick=\'fn(\'' + id + '\')\'>`.
12. **File is large (~190KB).** Use positional searches (find exact boundary strings) for str.replace. When searching for function boundaries, use `content.find('  async function X(')` or `content.find('  function X(')`. Never assume two-newline patterns are unique — verify with positional search first.
13. **str.replace requires exact character match.** Always copy the target string directly from the fetched file content — do not type from memory. Even one different whitespace character will cause the replace to silently fail.
14. **Stage edits across multiple intermediate files** for large changes (v2.html → v3.html → v4.html). Verify each stage before proceeding.
15. **Jotform MCP connector is broken** — always use Jotform REST API directly with API key `18907cfb3b4b3be3ac47994683148728`.
16. **Removing a feature? Document it explicitly.** Add a "Removed: [Feature Name]" section listing all deleted HTML, JS functions, and Supabase tables. Future sessions must not try to reference or restore deprecated code.
17. **`async function` vs `function`** — the admin dashboard JS mixes sync and async functions. When searching for a function boundary use `content.find('  async function X(')` first, then fall back to `content.find('  function X(')`. Never assume.
18. **Health check endpoints — use HEAD not POST for n8n webhooks.** POST triggers real workflow execution. HEAD just checks reachability. Always `method:'HEAD'` for n8n webhook health checks in HEALTH_CHECKS array.
19. **`renderInfraResults()` now drives a summary bar** (`infra-summary-bar`) in addition to the card grid. It sets background colour (green/red), pulse dot, pass/fail counts, and summary text. When adding new health checks, no additional code is needed — the summary auto-calculates.
20. **`runE2ETests()` saves results to `e2e_test_results` Supabase table** after a 5-second delay (to let all async fetches settle). Results include `test_run_id`, `test_name`, `status`, `duration_ms`, `error_message`.

---

## Environment Variables (Railway)

| Var | Value | Notes |
|---|---|---|
| `PORT` | Set by Railway | Auto |
| `ADMIN_USER` | `admin` | Basic auth username |
| `ADMIN_PASS` | `syntharra2026` | Change to something strong |
| `GROQ_API_KEY` | `gsk_...` | Required for AI assistant — stored in syntharra_vault |

---

## Auto-Update Rule

**See Universal Skill-Update Rule in `syntharra-ops` skill.** This skill specifically tracks:
- New section added → update Navigation Sections table + Element IDs
- New JS function added → update JS Functions table
- File pushed → note to always fetch fresh SHA at chat start
- New env var → update Environment Variables table
- Design token changed → update Design System table
- Feature removed → document in a "Removed" section (critical — prevents future sessions restoring deprecated features)
- New pattern or gotcha → add to Key Patterns & Rules (numbered list)

**How:** At end of every chat that changes the admin dashboard, fetch `skills/syntharra-admin/SKILL.md` from `Syntharra/syntharra-automations`, apply changes with `str.replace()`, push back.
**Commit format:** `skill(syntharra-admin): brief description of what changed`
