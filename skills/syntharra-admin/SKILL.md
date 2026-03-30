---
name: syntharra-admin
description: >
  Complete reference for the Syntharra Admin Dashboard (admin.syntharra.com).
  ALWAYS load this skill when: working on the admin dashboard, adding new pages
  or sections, editing the sidebar nav, modifying the server.js backend, adding
  new admin features (email intelligence, ops monitor, etc.), changing the admin
  password/auth, updating the AI assistant knowledge base, or anything touching
  the syntharra-admin GitHub repo or admin.syntharra.com Railway service.
---

---

## Overview

| Item | Value |
|---|---|
| URL | `https://admin.syntharra.com` |
| Repo | `Syntharra/syntharra-admin` |
| Auth | HTTP Basic Auth — `ADMIN_USER` + `ADMIN_PASS` env vars (default: `admin` / `syntharra2026`) |
| Hosting | Railway — service in Syntharra project |
| Stack | Node.js + Express + static HTML (no build step) |
| AI backend | Groq (`llama-3.3-70b-versatile`) via `GROQ_API_KEY` Railway env var |

---

## Repo Structure

```
syntharra-admin/
├── server.js              ← Express server: auth, AI proxy /api/ai, health /api/health
├── package.json           ← deps: express only
└── public/
    ├── index.html         ← Main admin dashboard (all sections in one SPA)
    ├── email.html         ← Email Intelligence page (standalone page)
    ├── favicon.svg
    └── favicon-white.svg
```

---

## Architecture

- **Single-page app (SPA):** `index.html` contains all sections. Nav toggles `.section.active` via `nav()` JS function.
- **Separate pages:** Some features (e.g. Email Intelligence) are standalone HTML pages with their own sidebar. Always replicate the sidebar exactly.
- **Auth:** Server-level HTTP Basic Auth via Express middleware. All routes protected.
- **Data:** Supabase anon key in HTML for reads. Service role key only in server.js/n8n (never in browser-facing HTML).
- **AI:** Groq API proxied through `/api/ai` endpoint on the server. Client never sees API key.
- **Deployed on Railway** — push to GitHub triggers auto-deploy.

---

## Pages & Sections

### index.html — Section IDs
| Nav Item | Section ID | Key Elements |
|---|---|---|
| Dashboard | `sec-overview` | KPI stats, recent calls, system status, MRR chart, minutes usage, pending actions |
| Clients | `sec-clients` | Standard + Premium client tables, trade tabs, search, modal |
| Call Logs | `sec-calls` | Full call log table, filter pills, CSV export |
| Billing | `sec-billing` | MRR stats, billing table, Stripe go-live checklist |
| Onboarding Forms | `sec-forms` | Jotform submissions list |
| AI Agents | `sec-agents` | Retell agent cards grid |
| Ops Monitor | `sec-opsmonitor` | Live health, system cards, alert log |
| Marketing | `sec-marketing` | Lead gen pipeline |
| Settings | `sec-settings` | Config settings |
| AI Assistant | `sec-ai` | Groq-powered chat, live context injection |

### email.html — Email Intelligence (standalone page)
- Reads from Supabase `email_digest` table (populated by n8n 6am GMT workflow)
- Two views: "By Inbox" (card grid) and "All Emails" (table)
- KPIs: Inboxes to check, High priority count, Action required count, Total important
- Shows all-clear state when no important emails
- Shows setup card when `email_digest` table doesn't exist yet
- Nav links back to `index.html` sections via `/?sec=SECTION_ID` pattern

---

## Design System (CSS Variables)

```css
--v: #6C63FF;       /* Violet — primary brand */
--vl: #F0EFFB;      /* Violet light — hover/active bg */
--vd: #5550E8;      /* Violet dark — hover state */
--cyan: #00D4FF;    /* Cyan — accent */
--bg: #F4F5F9;      /* Page background */
--surface: #fff;    /* Card/sidebar background */
--border: #E4E4EF;  /* Border colour */
--border2: #F0F0F8; /* Light border (within cards) */
--text: #1A1A2E;    /* Primary text */
--text2: #52526E;   /* Secondary text */
--text3: #9090AA;   /* Muted text */
--text4: #C0C0D8;   /* Very muted / placeholders */
--green: #12B76A;   --gbg: #ECFDF3;  --gtxt: #027A48;
--amber: #F59E0B;   --abg: #FFFAEB;  --atxt: #B54708;
--red: #F04438;     --rbg: #FEF3F2;  --rtxt: #B42318;
--sw: 232px;        /* Sidebar width */
```

**Font:** `Inter` (Google Fonts) — weights 400, 500, 600, 700

---

## Key Components

### Sidebar (replicate exactly on all pages)
```html
<div class="sidebar" id="sidebar">
  <div class="sb-logo">...</div>
  <div class="nav">
    <div class="nav-section">Section Label</div>
    <div class="nav-item [active]" ...>
      <svg class="nav-icon">...</svg>
      Label
      <span class="nav-badge nb-v">count</span>  <!-- optional -->
    </div>
    <!-- On standalone pages, use <a href="/..."> instead of onclick -->
  </div>
  <div class="sb-footer">...</div>
</div>
```
- **CRITICAL:** On standalone pages (not index.html), nav items use `<a href="/section">` not `onclick`. Nav links to index sections use `href="/?sec=SECTION_ID"`.
- Active item gets class `nav-item active`.
- Nav badges: `nb-v` (violet), `nb-r` (red), `nb-a` (amber).

### Cards
```html
<div class="card">
  <div class="card-header">
    <span class="card-title">Title</span>
    <div class="card-actions">...</div>
  </div>
  <!-- content -->
</div>
```

### Stat cards
```html
<div class="stats-grid sg4">  <!-- sg2, sg3, sg4 -->
  <div class="stat">
    <div class="stat-accent" style="background:var(--v)"></div>
    <div class="stat-label">Label</div>
    <div class="stat-value" id="...">—</div>
    <div class="stat-sub">sub text</div>
  </div>
</div>
```

### Badge classes
| Class | Colour |
|---|---|
| `bg` | Green |
| `bp` | Violet/Purple |
| `ba` | Amber |
| `br` | Red |
| `bgr` | Grey |
| `bb` | Blue |

---

## Server.js API Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/*` | ALL | Basic Auth | All routes require HTTP Basic Auth |
| `/api/ai` | POST | — | Groq AI proxy. Body: `{ messages: [...], liveContext: string }` |
| `/api/health` | GET | — | Returns `{ status, ai_configured, ts }` |
| `/` | GET | — | Serves `public/index.html` |

**AI Knowledge Base:** `SYNTHARRA_KNOWLEDGE` const in `server.js` — update whenever Syntharra stack changes significantly. Injected into every AI system prompt.

---

## Email Intelligence System

### Purpose
Scans all @syntharra.com inboxes daily at 6am GMT. AI classifies emails by importance. Results stored in Supabase. Displayed in `/email.html`.

### Monitored Inboxes (daniel@ is never scanned)
| Address | Label | Priority |
|---|---|---|
| `support@syntharra.com` | Support | High |
| `sales@syntharra.com` | Sales | High |
| `solutions@syntharra.com` | Solutions | High |
| `alerts@syntharra.com` | Alerts | High |
| `info@syntharra.com` | Info | Medium |
| `admin@syntharra.com` | Admin | Medium |
| `careers@syntharra.com` | Careers | Medium |

### n8n Workflow
- **Name:** Daily Email Digest — 6am GMT
- **File:** `syntharra-automations/n8n-workflows/email-digest-workflow.json`
- **Schedule:** 6:00 AM GMT daily (`Europe/London` timezone)
- **Credentials needed:** Gmail service account for each inbox + `SUPABASE_SERVICE_ROLE_KEY` env var
- **AI:** Groq API (`llama-3.3-70b-versatile`) for classification

### Supabase Table: `email_digest`
| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | PK |
| `digest_date` | date | e.g. 2026-03-30 |
| `inbox_address` | text | e.g. support@syntharra.com |
| `inbox_label` | text | e.g. Support |
| `email_id` | text | Gmail message ID |
| `thread_id` | text | Gmail thread ID |
| `from_address` | text | Full From: header |
| `subject` | text | |
| `snippet` | text | Raw Gmail preview |
| `ai_summary` | text | AI one-line summary |
| `importance` | text | high / medium / low |
| `category` | text | client_enquiry, sales_lead, job_application, etc. |
| `action_required` | boolean | |
| `flag` | text | urgent / opportunity / hire |
| `received_at` | timestamptz | |
| `created_at` | timestamptz | |

**Setup SQL:** `syntharra-automations/docs/email-digest-setup.sql`

### Importance Classification Rules
- **high:** Real person emailing about business — enquiries, support issues, complaints, partnerships, qualified job applications
- **medium:** Could be relevant — key vendor newsletters, invoices, automated alerts needing attention
- **low:** Automated reports, informational notifications
- **ignore (filtered out):** Promotional spam, marketing blasts, automated receipts

---

## Adding a New Page

1. Copy the sidebar HTML from `email.html` (standalone page pattern)
2. Use `<a href="...">` for nav links, not `onclick`
3. Add nav item to **both** `index.html` sidebar AND `email.html` sidebar
4. Keep the same CSS variables and design system
5. Add nav item to `index.html` sidebar referencing new page
6. Push both files to GitHub

## Adding a New Section to index.html

1. Add nav item in sidebar: `<div class="nav-item" data-sec="XXX" onclick="nav('XXX',this)">...`
2. Add section HTML: `<div class="section" id="sec-XXX">...`
3. Add page title mapping in `nav()` JS function
4. Wire up data loading in `loadLiveData()` or separately
5. Use `str.replace()` edits — never rewrite the whole file

---

## Critical Rules

1. **Never rewrite the whole file** — always fetch from GitHub, use `str.replace()` in Python, push back
2. **One `<style>` block per page** — never add a second
3. **`overflow-x:clip`** on body — never `overflow:hidden` on html/body
4. **Sidebar must be identical** across all pages (same nav items, same order)
5. **daniel@ never in any page** — not in email lists, not in nav, not in content
6. **Anon key in HTML is fine for reads** — never put service role key in browser-facing HTML
7. **Nav badge updates** — update badge counts on page load from live data
8. **Mobile:** Always test sidebar hamburger works. CSS already handles it.
9. **Groq key never in HTML** — proxied through `/api/ai` server endpoint only

---

## 🔄 Auto-Update Rule

Update this skill whenever:
- A new page is added to the admin dashboard
- A new section is added to index.html
- The auth credentials change
- A new API route is added to server.js
- The Email Intelligence system is updated (new inboxes, new table columns)
- The Groq model is changed
- Any Railway env var affecting the admin service changes

**How:** Fetch this file from `/mnt/skills/user/syntharra-admin/SKILL.md` (or GitHub), apply `str.replace()`, push back.
