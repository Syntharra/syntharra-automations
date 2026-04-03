# Syntharra — Engineering Standards
> These are non-negotiable rules enforced across all engineers (Claude and human).
> Add a new section for each system that has standardised conventions.
> Ref: CLAUDE.md for operating rules. ARCHITECTURE.md for design decisions.

---

## n8n Workflow Labelling Standard

**Rule: Every n8n workflow MUST have a label before it is considered complete.**

This is enforced at session close. Claude will not push a session log or close a task without
confirming all new/modified workflows are labelled.

### Required Label Fields

| Field | Required | Format | Example |
|---|---|---|---|
| **Name** | ✅ | `[Vertical] [Tier] — [Function]` | `HVAC Standard — Call Processor` |
| **Tags** | ✅ | At least 2 tags from the approved list below | `hvac`, `standard` |
| **Notes/Description** | ✅ | 1–2 sentence plain English summary | "Processes inbound call webhooks from Retell, extracts booking data, and pushes to HubSpot + Supabase." |

### Approved Tag Library

> Always tag from this list. Add new tags at the bottom only if genuinely needed.

**Vertical tags** (always include one):
- `hvac`
- `plumbing` *(future)*
- `electrical` *(future)*
- `cleaning` *(future)*
- `shared` — applies to all verticals

**Tier tags** (always include one):
- `standard`
- `premium`
- `shared` — not tier-specific

**Function tags** (include one or more):
- `onboarding` — client setup flows
- `call-processor` — handles post-call data
- `dispatcher` — premium job dispatch logic
- `billing` — Stripe events
- `lead-gen` — website/marketing leads
- `ops` — system health, backups, monitoring
- `testing` — scenario runners, E2E, simulators
- `email` — email send workflows
- `backup` — manual fallback workflows
- `crm` — HubSpot interactions

**Status tags** (always include one):
- `active` — live in production
- `inactive` — disabled, pending review
- `testing` — development/test use only
- `deprecated` — scheduled for removal

### Naming Convention

Pattern: `[Vertical] [Tier] — [Function]`

| ✅ Correct | ❌ Wrong |
|---|---|
| `HVAC Standard — Call Processor` | `call processor` |
| `HVAC Premium — Dispatcher` | `Premium Dispatcher v2 FINAL` |
| `Shared — Stripe Webhook` | `stripe` |
| `Shared — Nightly GitHub Backup` | `backup workflow` |
| `Shared — Usage Alert Monitor` | `monitor` |
| `Shared — Auto-Enable MCP` | `MCP thing` |

### Enforcement Rule for Claude

Before closing ANY session that creates or modifies n8n workflows:
1. List all workflows created or changed this session
2. Confirm each has: correct name, ≥2 tags, description
3. If any are unlabelled → label them via n8n API before pushing session log
4. Add labelling confirmation line to session log: `Labels: all workflows labelled ✅`

### How to Apply Labels via n8n API

```bash
# Step 1 — Get tag IDs (tags must exist first)
curl https://n8n.syntharra.com/api/v1/tags \
  -H "X-N8N-API-KEY: {{N8N_API_KEY}}"

# Step 2 — Apply tags to a workflow using the dedicated tags endpoint
curl -X PUT https://n8n.syntharra.com/api/v1/workflows/{WORKFLOW_ID}/tags \
  -H "X-N8N-API-KEY: {{N8N_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '[{"id": "TAG_ID_1"}, {"id": "TAG_ID_2"}]'
```

> **Critical gotchas (verified 2026-04-04):**
> - `PATCH /workflows/{id}` → 405 Method Not Allowed — does NOT exist in this n8n version
> - `PUT /workflows/{id}` with `tags` in body → 400 `tags is read-only` — ignored silently in body
> - **Correct method: `PUT /workflows/{id}/tags`** with array of `{id}` objects
> - Tags must already exist — get IDs from `GET /api/v1/tags` first
> - Full workflow PUT requires only: `name`, `nodes`, `connections`, `settings`

### Live Workflow Registry (verified 2026-04-04 — 47 total)

**38 labelled ✅ | 9 unlabelled ⚠️ (all inactive duplicates — left intentionally per Dan 2026-04-04)**

#### HVAC Standard (active)
| ID | Name | Tags |
|---|---|---|
| `4Hx7aRdzMl5N0uJP` | HVAC AI Receptionist - JotForm Onboarding (Supabase) | `HVAC Standard` |
| `Kg576YtPM9yEacKn` | HVAC Call Processor - Retell Webhook (Supabase) | `HVAC Standard` |
| `iLPb6ByiytisqUJC` | HVAC Weekly Lead Report (Supabase) | `HVAC Standard` |

#### HVAC Premium (active)
| ID | Name | Tags |
|---|---|---|
| `kz1VmwNccunRMEaF` | HVAC Prem Onboarding | `HVAC Premium` |
| `STQ4Gt3rH8ptlvMi` | HVAC Premium Call Processor | `HVAC Premium` |
| `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher | `HVAC Premium` |
| `La99yvfmWg6AuvM2` | Premium Dispatcher — Outlook | `HVAC Premium` |
| `b9xRG7wtqCZ5fdxo` | Premium Dispatcher — Calendly | `HVAC Premium` |
| `BxnR17qUfAb5BZCz` | Premium Dispatcher — Jobber | `HVAC Premium` |
| `msEy13eRz66LPxW6` | Premium Dispatcher — HubSpot | `HVAC Premium` |
| `rGrnCr5mPFP2TIc7` | Premium Dispatcher — Google Calendar | `HVAC Premium` |
| `a0IAwwUJP4YgwgjG` | Premium — Integration Connected Handler | `HVAC Premium` |
| `5vphecmEhxnwFz2X` | Premium — Daily Token Refresh | `HVAC Premium` |
| `ptDdy38HKt9DUOAV` | Premium — Send You're Live Email | `HVAC Premium` |

#### Billing
| ID | Name | Tags |
|---|---|---|
| `xKD3ny6kfHL0HHXq` | Stripe Workflow | `Billing` |
| `z1DNTjvTDAkExsX8` | Monthly Minutes Calculator & Overage Billing | `Billing` |
| `Wa3pHRMwSjbZHqMC` | Usage Alert Monitor (80% & 100% Warnings) | `Operations`, `Billing` |

#### Marketing & Leads
| ID | Name | Tags |
|---|---|---|
| `QY1ZFtPJFsU5h6wQ` | Website Lead → AI Readiness Score Email | `Marketing & Leads` |
| `hFU0ZeHae7EttCDK` | Website Lead → Free Report Email | `Marketing & Leads` |
| `I8a2N9bIZp9Qg1IN` | Website Lead — HubSpot Contact (Index + Calculator + Quiz) | `Marketing & Leads` |
| `6LXpGffcWSvL6RxW` | Weekly Newsletter - Syntharra | `Marketing & Leads` |
| `Eo8wwvZgeDm5gA9d` | Newsletter Unsubscribe Webhook | `Marketing & Leads` |
| `syGlWx8TlbYlPZU4` | Affiliate Application — HubSpot Contact | `Marketing & Leads` |

#### Operations
| ID | Name | Tags |
|---|---|---|
| `44WfbVmJ7Zihcwgs` | Nightly GitHub Backup | `Operations` |
| `AU8DD5r6i6SlYFnb` | Auto-Enable MCP on All Workflows | `Operations` |
| `LF8ZSYyQbmjV4rN0` | Jotform Webhook Backup Polling | `Operations` |
| `13cOIXxvj83NfDqQ` | Publish Retell Agent | `Retell & Calls`, `Operations` |
| `SiMn59qJOfrZZS81` | Daily Ops Digest — 6am → #all-syntharra | `Operations` |
| `z8T9CKcUp7lLVoGQ` | Slack Setup — Internal Admin Form | `Operations` |
| `ALFSzzp3htAEjwkJ` | Weekly Client Health Score Calculator | `Operations` |
| `ofoXmXwjW9WwGvL6` | Daily Transcript Analysis + Jailbreak Monitor | `Operations` |
| `ngK02cSgGmvawCot` | Nightly PII Retention Cleanup | `Operations` |

#### Email & Comms
| ID | Name | Tags |
|---|---|---|
| `PavRLBVQQpWrKUYs` | Email Intelligence — Inbox Scanner → Slack | `Operations`, `Email & Comms` |
| `lXqt5anbJgsAMP7O` | Send Welcome Email (Manual) | `Email & Comms` |
| `4aulrlX1v8AtWwvC` | Email Digest — Daily 6am GMT | `Email & Comms` |

#### Blog & Content
| ID | Name | Tags |
|---|---|---|
| `j8hExewOREmRp3Oq` | Blog Auto-Publisher | `Blog & Content` |

#### Testing & QA
| ID | Name | Tags |
|---|---|---|
| `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed Delete | `Testing & QA` |

---

#### ⚠️ Unlabelled — Pending (leave duplicates for now per Dan)

| ID | Name | Active | Action needed |
|---|---|---|---|
| `5wxgBfJL7QeNP2ab` | Google Keep → Groq → Slack To-Do List | 🟢 Yes | ✅ Tagged `Operations` (2026-04-04) |
| `NY6vhwLFmecAkxdH` | Keep → Slack TEST RUN | ⚫ No | Duplicate/test — add tags or delete |
| `HeG3aJQBXyRPKSXA` | SYNTHARRA_TEST_RUNNER | ⚫ No | Add tags |
| `SziSvI1zl49cs3cQ` | Premium — Integration Connected Handler | ⚫ No | Duplicate — leave for now |
| `OXuB3WR23fg0MmEu` | Premium — Integration Connected Handler | ⚫ No | Duplicate — leave for now |
| `IS5eC0SEzIv76TPQ` | Premium — Integration Connected Handler | ⚫ No | Duplicate — leave for now |
| `UKEoUeNqYvDDJv79` | [TEST STUB] Retell Tool Dispatcher | ⚫ No | Add tags |
| `AZZguGm5ypF6e5m9` | Blog Auto-Publisher | ⚫ No | Duplicate — leave for now |
| `TZ4p1UyzTrCJPdKA` | Email Digest — Daily 6am GMT | ⚫ No | Duplicate — leave for now |
| `S3vHBQopDiOssM7G` | Email Digest — Daily 6am GMT | ⚫ No | Duplicate — leave for now |

> Duplicates left in place per Dan's instruction (2026-04-04). Review separately.

---

## Claude Code vs Claude Chat — Task Routing

**Rule: Route tasks to the right tool. Don't default to chat for everything.**

### Use Claude Code when:

| Task type | Why Code wins |
|---|---|
| Running E2E test suites (`e2e-test.py`, `e2e-test-premium.py`) | Real Python execution, live output, self-heals |
| Self-healing loop (`self-healing-loop.py`) | Persistent execution across 10+ iterations |
| Pushing session logs to GitHub | File ops + git — native to Code |
| Verifying GitHub push completion | Shell execution |
| Running the agent simulator (`openai-agent-simulator*.py`) | Multi-step Python with live output |
| Auto-fix loop (`auto-fix-loop.py`) | Iterative fix → test → fix |
| Retell call analyser (`retell-call-analyser.py`) | Heavy file I/O on transcripts |
| Bulk file edits across 10+ files | Git staging + atomic commits |
| Any task needing `subprocess`, `os`, or live filesystem | Chat has no real FS |
| Railway deploy verification | Shell + API calls in sequence |
| Safety checks (`safety-checks.py`) | Real execution required |

### Use Claude Chat when:

| Task type | Why Chat wins |
|---|---|
| GitHub file read/write via API | Chat has token access |
| Updating skill files | Chat-native; no FS needed |
| n8n workflow design + editing | API calls → Chat handles it |
| Retell agent prompt editing | API calls → Chat handles it |
| HubSpot CRM operations | MCP connector is Chat-only |
| Stripe API operations | MCP connector is Chat-only |
| Email template design + preview | Artifact rendering is Chat-only |
| React/HTML artifact creation | Artifact rendering is Chat-only |
| Session planning + architecture | Reasoning task — no execution |
| Supabase queries via MCP | MCP connector is Chat-only |
| Jotform, Slack, Google Calendar | MCP connectors are Chat-only |

### Decision Logic

When a task arrives, ask:
> "Does this require real code execution, live file I/O, or multi-step script running?"

- **YES** → Claude Code. If currently in Chat, say: *"This task needs Claude Code — requires [reason]. Switch and run: `[exact command]`"*
- **NO** → Handle in Chat.

**Claude will NOT simulate script execution in Chat when Claude Code is the right tool.**

---
