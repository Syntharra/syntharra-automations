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
# Update workflow name + tags via PATCH
curl -X PATCH https://n8n.syntharra.com/api/v1/workflows/{WORKFLOW_ID} \
  -H "X-N8N-API-KEY: {{N8N_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HVAC Standard — Call Processor",
    "tags": [{"name": "hvac"}, {"name": "standard"}, {"name": "call-processor"}, {"name": "active"}]
  }'
```

> Note: n8n tags are created on first use. No pre-registration needed.
> For tag-only or name-only updates, PATCH accepts partial payloads.
> Full workflow PUT requires only: `name`, `nodes`, `connections`, `settings`.

### Existing Workflow Labels (Pending Audit — 2026-04-04)

| Workflow Name (target) | ID | Tags (target) | Status |
|---|---|---|---|
| HVAC Standard — Onboarding | `k0KeQxWb3j3BbQEk` | `hvac`, `standard`, `onboarding`, `active` | ⬜ Pending |
| HVAC Standard — Call Processor | `OyDCyiOjG0twguXq` | `hvac`, `standard`, `call-processor`, `active` | ⬜ Pending |
| HVAC Premium — Onboarding | `KXDSMVKSf59tAtal` | `hvac`, `premium`, `onboarding`, `active` | ⬜ Pending |
| HVAC Premium — Call Processor | `UhxfrDaEeYUk4jAD` | `hvac`, `premium`, `call-processor`, `active` | ⬜ Pending |
| HVAC Premium — Dispatcher | `kVKyPQO7cXKUJFbW` | `hvac`, `premium`, `dispatcher`, `active` | ⬜ Pending |
| Shared — Stripe Webhook | `ydzfhitWiF5wNzEy` | `shared`, `billing`, `active` | ⬜ Pending |
| Shared — Weekly Lead Report | `mFuiB4pyXyWSIM5P` | `shared`, `lead-gen`, `ops`, `active` | ⬜ Pending |
| Shared — Minutes Calculator | `9SuchBjqhFmLbH8o` | `shared`, `ops`, `active` | ⬜ Pending |
| Shared — Usage Alert Monitor | `lQsYJWQeP5YPikam` | `shared`, `ops`, `active` | ⬜ Pending |
| Shared — Publish Retell Agent | `sBFhshlsz31L6FV8` | `shared`, `ops`, `active` | ⬜ Pending |
| Testing — Scenario Runner v4 | `94QmMVGdEDl2S9MF` | `shared`, `testing`, `active` | ⬜ Pending |
| Testing — Scenario Transcript Gen | `dHO8O0QHBZJyzytn` | `shared`, `testing`, `active` | ⬜ Pending |
| Testing — Scenario Process Single | `rlf1dHVcTlzUbPX7` | `shared`, `testing`, `active` | ⬜ Pending |
| Shared — Website Lead AI Score | `FBNjSmb3eLdBS3N9` | `shared`, `lead-gen`, `active` | ⬜ Pending |
| Shared — Website Lead Free Report | `ykaZkQXWO2zEJCdu` | `shared`, `lead-gen`, `email`, `active` | ⬜ Pending |
| Shared — Nightly GitHub Backup | `EAHgqAfQoCDumvPU` | `shared`, `ops`, `backup`, `active` | ⬜ Pending |
| Shared — Send Welcome Email | `Rd5HiN7v2SRwNmiY` | `shared`, `email`, `backup`, `inactive` | ⬜ Pending |
| Shared — Auto-Enable MCP | `AU8DD5r6i6SlYFnb` | `shared`, `ops`, `active` | ⬜ Pending |
| Shared — E2E Cleanup | `URbQPNQP26OIdYMo` | `shared`, `testing`, `active` | ⬜ Pending |
| Shared — Integration Hub | `8WYFy093XA6UKB7L` | `shared`, `inactive` | ⬜ Pending |

> Run the labelling audit task in the next available session. See TASKS.md.

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
