---
name: syntharra-client-dashboard
description: >
  Complete reference for all work on the Syntharra client-facing Client Dashboard (dashboard.html).
  ALWAYS load this skill when: editing dashboard.html, adding new KPI cards or stats, changing the
  call table layout, updating badge types or score logic, modifying the period selector or filters,
  fixing Supabase data loading, changing the password gate, adding new columns or UI sections,
  debugging dashboard data issues, changing plan logic (Standard vs Premium), or deploying any
  dashboard update to production. This skill contains the full file structure, all HTML element IDs,
  the Supabase data model, JavaScript patterns, and the exact push workflow for shipping changes.
---

---

## Session Rules (CRITICAL — Every Chat)

At the **START** of every chat touching the dashboard:
1. Fetch `dashboard.html` from GitHub to get the current live version
2. Note the current SHA — required for any push

At the **END** of every chat that changes the dashboard:
1. Push updated `dashboard.html` to GitHub (see push pattern below)
2. Update `syntharra-ops` skill `## Client Dashboard` section with new SHA
3. Verify live at `syntharra.com/dashboard.html?agent_id=<test_agent_id>`

---

## File Location

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-website` |
| File path | `dashboard.html` |
| Live URL | `https://syntharra.com/dashboard.html?agent_id=<AGENT_ID>` |
| Password gate code | `syntharra2024` |
| Current SHA | `b16bda030a25aa6a9dd011da0ef8c479bb2f2150` |

---

## Fetch Current Dashboard (Python)

```python
import requests, base64

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"  # from syntharra_vault
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

r = requests.get(
    "https://api.github.com/repos/Syntharra/syntharra-website/contents/dashboard.html",
    headers=headers
).json()

current_sha = r["sha"]
content = base64.b64decode(r["content"]).decode()
```

---

## Push Updated Dashboard (Python)

```python
import requests, base64, json

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"  # from syntharra_vault
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}

def push_dashboard(new_html, current_sha, commit_msg):
    url = "https://api.github.com/repos/Syntharra/syntharra-website/contents/dashboard.html"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(new_html.encode()).decode(),
        "sha": current_sha
    }
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    return r.json()

# Example usage:
push_dashboard(updated_html, current_sha, "dashboard: add xyz feature")
```

**Commit message rules:** Short, lowercase, prefixed with `dashboard:` — e.g. `dashboard: fix premium filter`, `dashboard: add callback badge`

---

## Dashboard Overview

The dashboard is a **single-file, vanilla JS, client-facing page** — no frameworks, no build step. It loads via URL param `?agent_id=X`, looks up the agent in Supabase, and renders their call data.

### URL Pattern
```
https://syntharra.com/dashboard.html?agent_id=<RETELL_AGENT_ID>
```

### Access Gate
- Password: `syntharra2024`
- Gate is handled client-side (DOM manipulation on correct password entry)
- NOT a security gate — just friction reduction for accidental access

---

## Design System

| Token | Value |
|---|---|
| `--violet` | `#6C63FF` |
| `--violet-light` | `#8B7FFF` |
| `--violet-bg` | `#F0EEFF` |
| `--cyan` | `#00D4FF` |
| `--bg` | `#F7F7FB` |
| `--card` | `#FFFFFF` |
| `--text` | `#1A1A2E` |
| `--muted` | `#6B7280` |
| `--border` | `#E5E7EB` |
| `--green` | `#10B981` |
| `--amber` | `#F59E0B` |
| `--red` | `#EF4444` |

**Fonts:** `DM Sans` (body/UI) + `DM Serif Display` (headings/logo)
Loaded from Google Fonts CDN — both already in `<head>`.

---

## HTML Element IDs (All Critical)

| ID | What it controls |
|---|---|
| `loading` | Loading spinner — hidden after data loads |
| `error` | Error state block — shown on failure |
| `errorMsg` | Text inside error block |
| `dashboard` | Main dashboard wrapper — shown after load |
| `companyName` | Company name in header |
| `planLabel` | "Standard" or "Premium" badge in header |
| `statusBadge` | "● Active" status badge |
| `welcomeText` | "Welcome, [company]" in banner |
| `statsGrid` | KPI cards container |
| `callTableBody` | `<tbody>` of calls table |
| `tableCount` | "X calls" count label |
| `filterBookings` | Bookings filter pill (hidden for Standard) |
| `thBooked` | "Booked" table column header (hidden for Standard) |

---

## Supabase Data Model

### Agent Tables

#### `hvac_standard_agent`
Key fields used by dashboard:
- `agent_id` (text) — Retell agent ID, used as URL param
- `company_name` (text)
- `agent_name` (text)
- `plan_type` (text)
- `client_email` (text)
- `timezone` (text)
- `lead_phone`, `lead_email`
- `services_offered`, `service_area`
- `business_hours`, `emergency_service`
- `stripe_customer_id`, `subscription_id`

#### `hvac_premium_agent`
All Standard fields plus:
- `crm_platform`, `crm_status`, `crm_access_token`, `crm_refresh_token`
- `calendar_platform`, `calendar_status`, `calendar_access_token`
- `booking_buffer_minutes`, `default_appointment_duration`, `booking_advance_days`
- `dispatch_mode`, `technician_names`
- `notification_email_2/3`, `notification_sms_2/3`

### Call Log Tables

#### `hvac_call_log` (Standard)
Key fields:
- `agent_id`, `call_id`, `company_name`
- `created_at`, `call_timestamp`, `duration_seconds`
- `caller_name`, `caller_phone`, `caller_address`
- `service_requested`, `job_type`, `urgency`
- `lead_score` (int), `is_lead` (bool)
- `call_tier`, `caller_sentiment` (int)
- `summary`, `notes`
- `transfer_attempted`, `transfer_success` (bool)
- `vulnerable_occupant` (bool)
- `geocode_status`, `geocode_formatted`

#### `hvac_premium_call_log` (Premium)
All Standard fields plus:
- `notification_type` (text) — call classification
- `is_hot_lead` (bool)
- `booking_success`, `booking_attempted` (bool)
- `appointment_date`, `appointment_time`, `appointment_duration_minutes`
- `job_type_booked`, `booking_reference`
- `reschedule_requested`, `cancellation_requested` (bool)
- `call_type`, `call_status`, `call_successful` (bool)
- `notification_sent`, `notification_priority`
- `is_repeat_caller`, `repeat_call_count`
- `transcript`, `caller_email`
- `from_number`

---

## Supabase Connection (In-Dashboard JS)

```javascript
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{{SUPABASE_ANON_KEY}}'; // anon key — safe to expose client-side

async function supabaseGet(table, query) {
  const res = await fetch(SUPABASE_URL + '/rest/v1/' + table + '?' + query, {
    headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }
  });
  if (!res.ok) throw new Error('API error: ' + res.status);
  return res.json();
}
```

**Uses anon key** — row-level security handles access control.

---

## Plan Logic

```javascript
// Standard: planMinutes = 475, no booking column
// Premium: planMinutes = 1000, shows booking column + filter

let planType = 'standard';
let planMinutes = 475;

// On load — check premium table first, fall back to standard:
var agents = await supabaseGet('hvac_premium_agent', 'agent_id=eq.' + agentId + '&select=company_name,agent_name,plan_type');
if (agents.length) {
  planType = 'premium'; planMinutes = 1000;
} else {
  agents = await supabaseGet('hvac_standard_agent', 'agent_id=eq.' + agentId + '&select=...');
  planType = 'standard'; planMinutes = 475;
}

// Call table varies by plan:
var callTable = planType === 'premium' ? 'hvac_premium_call_log' : 'hvac_call_log';
```

---

## notification_type Values (Badge Map)

| Value | Badge Label | CSS Class |
|---|---|---|
| `booking_confirmed` | Booked | `badge-booking` |
| `booking_failed_lead` | Lead | `badge-lead` |
| `emergency` | Emergency | `badge-emergency` |
| `hot_lead` | Hot Lead | `badge-hot` |
| `general_lead` | Lead | `badge-lead` |
| `follow_up_required` | Follow Up | `badge-hot` |
| `info_only` | Info | `badge-info` |
| `spam` | Spam | `badge-spam` |
| `reschedule` | Reschedule | `badge-info` |
| `cancellation` | Cancel | `badge-info` |
| `callback_requested` | Callback | `badge-callback` |
| `existing_customer` | Existing | `badge-existing` |
| `nonemergency_lead` | Lead | `badge-lead` |

To add a new type: add to the `map` object in `typeBadge()` + add CSS class in `<style>`.

---

## Score Display Logic

```javascript
function scoreEl(score) {
  if (!score && score !== 0) return '—';
  var cls = score >= 7 ? 'score-high' : score >= 4 ? 'score-mid' : 'score-low';
  return '<span class="score ' + cls + '">' + score + '</span>';
}
// score-high = green, score-mid = amber, score-low = red
```

---

## KPI Cards (statsGrid)

Built by `buildStats(calls)`. Currently renders:
1. **Total Calls** — with period label sub-text
2. **Jobs Booked** — Premium only
3. **Hot Leads** — score 7+
4. **Minutes Used** — with usage bar (green/amber/red)
5. **This Week** — last 7 days count
6. **Avg Lead Score** — from scored calls
7. **Emergencies** — only shown if > 0

To add a new card: add a new `html +=` block in `buildStats()` following the existing pattern.

---

## Filters & Period Selector

```javascript
// Period buttons (in welcome banner)
setPeriod(days)  // 0 = all time, 7 = last 7 days, 30 = last 30 days

// Filter pills (above table)
setFilter(filter)  // 'all' | 'leads' | 'bookings' | 'emergency'
```

Filter logic lives in `getFilteredCalls()`. To add a new filter:
1. Add a `.filter-pill` button in HTML with `data-filter="new_filter"`
2. Add a case in `getFilteredCalls()` for the new filter value
3. Call `setFilter()` on click

---

## Call Table Columns

| Column | Source Field | Mobile |
|---|---|---|
| Date / Duration | `created_at`, `duration_seconds` | ✅ |
| Caller | `caller_name`, `caller_phone` | ✅ |
| Service | `service_requested` | ✅ |
| Type badge | `notification_type` | ✅ |
| Score | `lead_score` | hide-mobile |
| Booked (Premium) | `booking_success` | hide-mobile |
| Summary | `summary` | ✅ (truncated → expand) |

---

## Summary Expand/Collapse

Summaries over 80 chars get a "Read more" toggle:
```javascript
// IDs: summary-0, summary-1, etc.
// Toggle function:
function toggleSummary(id, btn) { ... }
```

---

## Common Tasks

### Add a new KPI card
1. Add `html +=` block in `buildStats()` following existing pattern
2. Cards auto-fit via `grid-template-columns: repeat(auto-fit, minmax(170px, 1fr))`

### Add a new table column
1. Add `<th>` in the HTML table header
2. Add the cell value in the `rows +=` loop in `buildTable()`
3. Add `class="hide-mobile"` if it should hide on small screens

### Add a new badge type
1. Add entry to `map` in `typeBadge()`
2. Add CSS `.badge-<name>` class with background/color

### Change plan minutes
- Standard: change `planMinutes = 475`
- Premium: change `planMinutes = 1000`
- Both in `loadDashboard()` where plan is determined

### Fix "Agent not found" error
Check `hvac_standard_agent` and `hvac_premium_agent` tables for the agent_id.
The dashboard checks Premium first, then Standard.

---

## Key Learnings & Gotchas

1. **Single-file, no build** — all CSS, HTML, JS in one `dashboard.html`. Don't split.
2. **Anon key is safe client-side** — it's in the public HTML; RLS on Supabase controls access.
3. **Always use `var` not `const/let`** in the dashboard JS — it's written in ES5-compatible style for max compatibility.
4. **Premium-only features** hidden via `style.display = ''` on load — not via CSS classes.
5. **`notification_type` is Premium-only** — Standard call log doesn't have this column.
6. **`is_hot_lead`** exists on Premium call log, not Standard.
7. **Booking column** only shown for Premium: controlled by `bookedCol` variable.
8. **Period selector** filters from `allCalls` (full dataset), not re-fetched from Supabase.
9. **Table limit** is 200 rows (`limit=200` in Supabase query).
10. **GitHub Pages** — changes go live within ~30 seconds of push (no build step).
11. **Password gate** — code is `syntharra2024`, stored plain in JS. Change in HTML if rotating.

---

## Credential Access

All keys pulled from `syntharra_vault` Supabase table. Never hardcode in skill files.

```python
# Standard REST lookup:
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault
  ?service_name=eq.{SERVICE_NAME}&key_type=eq.{KEY_TYPE}&select=key_value
Headers:
  apikey: {SERVICE_ROLE_KEY}
  Authorization: Bearer {SERVICE_ROLE_KEY}
```

| service_name | key_type | Notes |
|---|---|---|
| `GitHub` | `personal_access_token` | For pushing dashboard.html |
| `Supabase` | `service_role_key` | For reading vault |
| `Supabase` | `project_url` | `hgheyqwnrcvwtgngqdnq.supabase.co` |

---

## 🔄 Auto-Update Rule

**Whenever dashboard.html changes, update this SKILL.md before the chat ends:**
- New SHA after push → update `Current SHA` in File Location table
- New badge type added → update badge map table
- New KPI card added → update KPI Cards section
- New column added → update Call Table Columns table
- Password changed → update `Password gate code`
- planMinutes changed → update Plan Logic section

**How:** Fetch this file from `syntharra-automations` repo, apply changes, push back.
