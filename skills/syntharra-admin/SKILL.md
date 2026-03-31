---
name: syntharra-internal-admin
description: >
  Complete reference for all work on the Syntharra Internal Admin Dashboard at admin.syntharra.com.
  ALWAYS load this skill when: editing index.html or server.js in the syntharra-admin repo, adding new
  sections/pages, adding KPI stats, updating nav items, modifying data rendering (clients, calls,
  billing, forms, agents), updating the AI assistant, editing the ops monitor, adding new Supabase
  queries, changing the MRR chart, updating checklist items, adding new sections to the sidebar,
  or deploying any change to admin.syntharra.com.
---

---

## Session Rules (CRITICAL — Every Chat)

At the **START** of every chat touching the admin dashboard:
1. Fetch `public/index.html` from `Syntharra/syntharra-admin` GitHub repo to get current live version
2. Note the current SHA — required for any push
3. Also fetch `server.js` if server-side logic is changing

At the **END** of every chat that changes anything:
1. Push updated file(s) to `Syntharra/syntharra-admin` on GitHub
2. Railway auto-deploys on push — live within ~60 seconds
3. Verify at `https://admin.syntharra.com`

---

## Repo & Deployment

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-admin` |
| Files | `public/index.html` (main UI), `server.js` (Express + AI proxy), `package.json` |
| Live URL | `https://admin.syntharra.com` |
| Hosting | Railway (auto-deploys on git push) |
| Auth | HTTP Basic Auth — `ADMIN_USER` / `ADMIN_PASS` env vars on Railway |
| Default creds | `admin` / `syntharra2026` (Railway env vars override) |
| index.html SHA | `b7a03e022446a8e15d5f567afcca934e3a5d107a` (update after every push) |

---

## Fetch & Push Pattern (Python)

```python
import requests, base64, json

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"  # from syntharra_vault
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# FETCH
def fetch_file(path):
    r = requests.get(
        f"https://api.github.com/repos/Syntharra/syntharra-admin/contents/{path}",
        headers=headers
    ).json()
    return base64.b64decode(r["content"]).decode(), r["sha"]

# PUSH
def push_file(path, new_content, sha, commit_msg):
    r = requests.put(
        f"https://api.github.com/repos/Syntharra/syntharra-admin/contents/{path}",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps({
            "message": commit_msg,
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha
        })
    )
    return r.json()

# Usage:
html, sha = fetch_file("public/index.html")
# ... make edits using str.replace() ...
push_file("public/index.html", updated_html, sha, "admin: add xyz feature")
```

**Commit message convention:** lowercase, prefixed with `admin:` — e.g. `admin: add plumbing tab`, `admin: fix billing chart`

**Edit method:** ALWAYS use Python `str.replace()` — never full rewrites. One targeted replacement per change.

---

## Tech Stack

| Layer | Details |
|---|---|
| Frontend | Vanilla JS (ES5 style), no framework, no build step |
| Backend | Node.js + Express (`server.js`) |
| CSS | Single `<style>` block in `<head>` using CSS variables |
| Charts | Chart.js 4.4.0 (CDN) |
| Markdown | marked.js 9.1.6 (CDN — used in AI assistant) |
| Fonts | Inter (Google Fonts) |
| Database | Supabase (anon key, direct REST calls from browser) |
| AI Assistant | Groq API via `/api/ai` proxy in server.js |
| Forms data | Jotform REST API (direct from browser) |
| Ops data | `syntharra-ops-monitor-production.up.railway.app` API |

---

## Design System (CSS Variables)

```css
--v:      #6C63FF   /* violet primary */
--vl:     #F0EFFB   /* violet light bg */
--vd:     #5550E8   /* violet dark (hover) */
--cyan:   #00D4FF   /* cyan accent */
--bg:     #F4F5F9   /* page background */
--surface:#fff       /* card/panel background */
--border: #E4E4EF   /* primary border */
--border2:#F0F0F8   /* subtle border */
--text:   #1A1A2E   /* primary text */
--text2:  #52526E   /* secondary text */
--text3:  #9090AA   /* muted text */
--text4:  #C0C0D8   /* very muted / labels */
--green:  #12B76A   /* success */
--gbg:    #ECFDF3   /* green bg */
--gtxt:   #027A48   /* green text */
--amber:  #F59E0B   /* warning */
--abg:    #FFFAEB   /* amber bg */
--atxt:   #B54708   /* amber text */
--red:    #F04438   /* error */
--rbg:    #FEF3F2   /* red bg */
--rtxt:   #B42318   /* red text */
--sw:     232px     /* sidebar width */
```

**Font:** `Inter` (Google Fonts)
**Body:** `font-size: 14px`, `overflow-x: clip` (NEVER `overflow-x: hidden`)

---

## Sidebar Navigation — All Sections

| Section ID | Nav Label | data-sec |
|---|---|---|
| `sec-overview` | Dashboard | `overview` |
| `sec-clients` | Clients | `clients` |
| `sec-calls` | Call Logs | `calls` |
| `sec-billing` | Billing | `billing` |
| `sec-forms` | Onboarding Forms | `forms` |
| `sec-agents` | AI Agents | `agents` |
| `sec-opsmonitor` | Ops Monitor | `opsmonitor` |
| `sec-marketing` | Marketing Pipeline | `marketing` |
| `sec-settings` | Settings | `settings` |
| `sec-ai` | AI Assistant | `ai` |
| `/email.html` | Email Intelligence | (separate page) |

**Nav badges:**
- `nav-clients-badge` — shows client count (violet)
- `nav-forms-badge` — shows pending form count (amber)
- `nav-alert-badge` — shows `!` when ops alerts exist (red)
- `nav-email-badge` — email badge (violet)

**To add a new nav section:**
1. Add `.nav-item` div in sidebar with `data-sec="mysection"` and `onclick="nav('mysection',this)"`
2. Add `<div class="section" id="sec-mysection">...</div>` in `.content`
3. Add entry to `PAGE_TITLES` object in JS

---

## HTML Key Element IDs

### Topbar
| ID | What it controls |
|---|---|
| `page-title` | Current page title in topbar |
| `page-sub` | Page subtitle |
| `sys-pill` | System status pill (green/amber/red) |
| `sys-text` | Text inside status pill |
| `clock-gmt` | GMT clock display |

### Overview Section
| ID | What it controls |
|---|---|
| `ov-clients` | Active clients count KPI |
| `ov-clients-sub` | Clients KPI subtext |
| `ov-mrr` | MRR KPI value |
| `ov-mrr-sub` | MRR subtext |
| `ov-calls` | Calls today KPI |
| `ov-calls-sub` | Calls subtext |
| `ov-hot` | Hot leads (7d) KPI |
| `ov-calls-list` | Recent calls feed |
| `ov-status-list` | System status mini-list |
| `ov-minutes` | Minutes used progress bars |
| `ov-actions-list` | Pending actions feed |
| `ov-actions-badge` | Actions count badge |
| `mrrChart` | Chart.js canvas for MRR chart |

### Clients Section
| ID | What it controls |
|---|---|
| `clients-count` | Total client count badge |
| `client-search` | Search input |
| `clients-tbody-std` | Standard clients table body |
| `clients-tbody-prem` | Premium clients table body |
| `clients-std-count` | Standard count label |
| `clients-prem-count` | Premium count label |

### Call Logs Section
| ID | What it controls |
|---|---|
| `calls-tbody` | Call logs table body |
| `call-filter-pills` | Filter buttons container |

### Billing Section
| ID | What it controls |
|---|---|
| `bill-mrr` | MRR value |
| `bill-arr` | ARR value |
| `bill-subs` | Active subscriptions count |
| `billing-tbody` | Billing table body |

### Other Sections
| ID | What it controls |
|---|---|
| `forms-list` | Jotform submissions feed |
| `forms-badge` | Forms status badge |
| `agents-grid` | AI agents card grid |
| `agents-count` | Agent count badge |
| `mkt-sourced` | Marketing leads sourced KPI |
| `mkt-emailed` | Emails sent KPI |
| `mkt-hot` | Hot leads KPI |
| `mkt-demos` | Demos booked KPI |
| `mkt-pipeline` | Lead pipeline board |
| `om-systems` | Ops: systems online count |
| `om-alerts` | Ops: alert count |
| `om-mrr` | Ops: MRR display |
| `om-calls24` | Ops: calls in last 24h |
| `om-systems-grid` | Ops: system health cards |
| `om-alerts-list` | Ops: alert log |
| `om-updated` | Ops: last updated timestamp |
| `ai-msgs` | AI chat messages container |
| `ai-input` | AI chat textarea |
| `ai-send` | AI send button |

---

## Data Sources

### Supabase (browser-side REST)
```javascript
const SB_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGci...'; // anon key — safe to expose client-side
const SB_H   = { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY };

async function sbFetch(path) {
  const r = await fetch(SB_URL + path, { headers: SB_H });
  return r.ok ? r.json() : [];
}
```

**Tables queried:**
| Table | Used for |
|---|---|
| `hvac_standard_agent` | Standard client list, agent IDs |
| `hvac_premium_agent` | Premium client list |
| `hvac_call_log` | All call records (Standard) |
| `hvac_premium_call_log` | Premium call records |
| `client_subscriptions` | Subscription status + MRR |
| `stripe_payment_data` | Stripe payment records |
| `website_leads` | Marketing lead pipeline |

### Jotform API (browser-side)
```javascript
const JF_KEY = '18907cfb3b4b3be3ac47994683148728';
// Standard form: 260795139953066
// Premium form:  260819259556671
fetch(`https://api.jotform.com/form/${formId}/submissions?apiKey=${JF_KEY}&limit=20&orderby=created_at,DESC`)
```

### Ops Monitor API (browser-side)
```javascript
const OPS_URL = 'https://syntharra-ops-monitor-production.up.railway.app';
// Endpoints used: /api/status (health check data)
```

---

## `loadLiveData()` — Main Data Load

Called on page init. Fetches all data in parallel:
```javascript
const [stdAgents, premAgents, callLogs, subs, stripeData] = await Promise.all([...]);
allClients = [...stdAgents (tier:'standard'), ...premAgents (tier:'premium')];
```

Then calls: `renderOverview()`, `renderClients()`, `renderCallLogs()`, `renderBilling()`, `renderAgents()`, `renderMarketing()`, `renderForms()`

---

## Render Functions Map

| Function | What it renders |
|---|---|
| `renderOverview(clients, calls, subs)` | 4 KPI cards, recent calls feed, system status, minutes bars, pending actions |
| `renderClients(clients, subs)` | Standard + Premium client tables, nav badge |
| `renderClientGroups(clients, subs)` | Inner table rows after filtering |
| `renderCallLogs(calls)` | Call log table rows (respects `callFilter`) |
| `renderBilling(clients, subs, stripeData)` | Billing KPIs + table |
| `renderForms()` | Async — fetches Jotform submissions and renders feed |
| `renderAgents(clients)` | Agent cards grid (client agents + demo agents) |
| `renderMarketing()` | Marketing KPIs + lead pipeline board |
| `loadOpsData(force)` | Async — fetches ops monitor, renders system health + alerts |

---

## Badge CSS Classes

| Class | Colour | Use for |
|---|---|---|
| `.bg` | Green | Active, success, booked, provisioned |
| `.bp` | Violet | Premium, new features |
| `.ba` | Amber | Warning, pending, in-progress |
| `.br` | Red | Error, blocked, emergency |
| `.bgr` | Grey | Neutral, info, standard |
| `.bb` | Blue | Info lead, general |

---

## Call Type Map (notification_type → badge)
```javascript
const typeMap = {
  booking_confirmed:   ['Booked',    'bg'],
  emergency:           ['Emergency', 'br'],
  hot_lead:            ['Hot Lead',  'ba'],
  general_lead:        ['Lead',      'bb'],
  info_only:           ['Info',      'bgr'],
  spam:                ['Spam',      'bgr'],
  callback_requested:  ['Callback',  'bp'],
  existing_customer:   ['Existing',  'bgr'],
  nonemergency_lead:   ['Lead',      'bb'],
  booking_failed_lead: ['Lead',      'bb'],
  follow_up_required:  ['Follow Up', 'ba'],
};
```

---

## Helper Functions

```javascript
fmtTime(d)       // → "9:45 AM" (Europe/London)
fmtDate(d)       // → "12 Mar 2026"
fmtDateShort(d)  // → "Mar 2026"
fmtDur(s)        // → "3m 22s"
fmtPhone(p)      // → "(812) 994-4371"
timeAgo(iso)     // → "5m ago"
el(id)           // → document.getElementById(id)
set(id, val)     // → el(id).textContent = val
sbFetch(path)    // → Supabase REST GET
```

---

## Client Modal (`openClientModal(c)`)

Opens a slide-up modal showing full client details:
- Contact (phone, email, website, timezone)
- Agent (agent_name, agent_id, plan, industry)
- Business Details (services, hours, emergency, transfer phone)
- Onboarding (created_at, stripe_customer_id, subscription_id, lead_email)
- Link to client-facing dashboard: `syntharra.com/dashboard.html?agent_id=X`

---

## AI Assistant (Section: `sec-ai`)

**Frontend:** Chat UI with message history, typing indicator, quick-chips, markdown rendering (marked.js)

**Backend:** `POST /api/ai` in `server.js`
- Proxies to Groq API (`llama-3.3-70b-versatile`)
- Requires `GROQ_API_KEY` env var on Railway
- System prompt includes full `SYNTHARRA_KNOWLEDGE` block + live dashboard context passed as `liveContext`
- `AI_HISTORY` array stores conversation (trimmed to last 20 messages)
- If `GROQ_API_KEY` not set → returns 503 with clear message

**To update AI knowledge base:** Edit `SYNTHARRA_KNOWLEDGE` const in `server.js`

**AI chips** (quick prompts):
```html
<span class="ai-chip" onclick="aiChip(this)">How many clients do I have?</span>
```
To add new chips: add `.ai-chip` spans inside `#ai-chips`

---

## Ops Monitor Section

- Loads on first nav to `opsmonitor` section (`omLoaded` flag prevents double-load)
- Auto-refreshes every 30 seconds (countdown bar at bottom of page)
- `loadOpsData(force)` fetches from `OPS_URL/api/status`
- Renders: systems grid, alert log, 4 KPI cells (systems online, alerts, MRR, calls 24h)
- Topbar `sys-pill` reflects overall health (green/amber/red)

---

## MRR Chart

Chart.js line chart on the Overview page:
- Canvas: `#mrrChart`
- Data currently hardcoded: `[997, 1991, 3488, 4482]` for Jan–Apr (proj)
- Labels: `['Jan','Feb','Mar','Apr (proj)']`
- Update data when real Stripe MRR is live

---

## Trade Tabs (Clients Section)

Tabs: All | HVAC | Plumbing | Electrical | Other

```javascript
function setTrade(trade, btn) { ... filterClients(); }
```

Filtering uses `c.industry_type` field from agent table. "Other" = anything not HVAC/Plumbing/Electrical.

To add a new trade tab:
```html
<button class="trade-tab" data-trade="Cleaning" onclick="setTrade('Cleaning',this)">Cleaning</button>
```

---

## server.js — Key Endpoints

| Method + Path | What it does |
|---|---|
| `GET /` | Serves `public/index.html` |
| `GET /email.html` | Serves `public/email.html` (Email Intelligence page) |
| `POST /api/ai` | Groq AI proxy (requires `GROQ_API_KEY` env var) |
| `GET /api/health` | Health check — returns `{status:'ok', ai_configured: bool}` |

**Auth middleware:** All routes protected by HTTP Basic Auth using `ADMIN_USER` / `ADMIN_PASS` env vars.

---

## Railway Environment Variables

| Var | Value |
|---|---|
| `ADMIN_USER` | `admin` (or custom) |
| `ADMIN_PASS` | `syntharra2026` (or custom) |
| `GROQ_API_KEY` | Groq API key (stored in `syntharra_vault` as service_name='Groq') |
| `PORT` | Set by Railway automatically |

---

## Common Tasks

### Add a new KPI card to Overview
1. Add HTML `<div class="stat">...` in `#sec-overview .stats-grid`
2. Give it an `id` (e.g. `ov-newmetric`)
3. In `renderOverview()`, add: `set('ov-newmetric', value);`

### Add a new section
1. Add `.nav-item` in sidebar with `data-sec="newsection"`
2. Add `PAGE_TITLES['newsection'] = 'Title'` in JS
3. Add `<div class="section" id="sec-newsection">...</div>` in `.content`
4. Add a render function if it loads data

### Add a new trade tab
1. Add `<button class="trade-tab" data-trade="X" onclick="setTrade('X',this)">X</button>`
2. No JS changes needed — `filterClients()` uses `c.industry_type` automatically

### Add a Supabase table query
1. Add to `Promise.all([...])` in `loadLiveData()`
2. Pass result to relevant render function
3. Pattern: `sbFetch('/table_name?select=*&order=created_at.desc&limit=100')`

### Update the pending actions list
- Actions are hardcoded in `renderOverview()` as the `actions` array
- Update text/status/cls as items are completed or added

### Add AI quick-chips
- Add `<span class="ai-chip" onclick="aiChip(this)">Your prompt here</span>` inside `#ai-chips`

### Update AI knowledge base
- Edit `SYNTHARRA_KNOWLEDGE` string in `server.js`
- Push `server.js` to GitHub — Railway redeploys automatically

---

## Key Gotchas

1. **Vanilla JS / ES5 style** — use `var`, `function`, not `const`/`let`/arrow functions at top level
2. **Single `<style>` block** — all CSS lives in the one block in `<head>`. Never add a second `<style>` tag.
3. **`overflow-x: clip`** on body — NEVER use `overflow-x: hidden`
4. **Anon key is safe** — Supabase anon key in the HTML is fine; RLS controls access
5. **Jotform API key** in HTML — intentional (read-only submissions API)
6. **Railway redeploys automatically** on git push — no manual deploy needed
7. **`email.html` is a separate page** — linked from sidebar as `<a href="/email.html">`, not a JS nav section
8. **AI assistant uses Groq, not Claude** — the AI proxy at `/api/ai` calls Groq's `llama-3.3-70b-versatile`
9. **Chart.js and marked.js from CDN** — both loaded via `<script src="https://cdnjs...">` at bottom of body
10. **`allClients` state** includes both Standard + Premium merged — always check `c.tier` to distinguish
11. **MRR chart data is currently hardcoded** — update when Stripe goes live
12. **Client modal** uses `JSON.stringify(c)` inline — be careful with apostrophes in company names

---

## Auto-Update Rule

**After any change to index.html, update this SKILL.md before the chat ends:**
- New section added → add to Sidebar Navigation table + HTML Key Element IDs
- New data source added → update Data Sources section
- New render function → add to Render Functions Map
- SHA changed → update index.html SHA in Repo & Deployment table
- New env var needed → add to Railway Environment Variables table

**How:** Fetch this file from `Syntharra/syntharra-automations`, apply changes, push back.
SKILL.md path: `skills/admin-dashboard/SKILL.md` → **wait, this is for the INTERNAL admin at admin.syntharra.com**
Store this skill at: `skills/syntharra-admin/SKILL.md` in `Syntharra/syntharra-automations`
