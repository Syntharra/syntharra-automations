---
name: self-improvement
description: >
  Post-task review and self-improvement protocol for Syntharra. Invoke after any task
  involving Retell agents, n8n workflows, Supabase changes, email templates, or Stripe
  integration — especially when something breaks unexpectedly. Documents failure capture,
  FAILURES.md logging, memory updates, skill file patching, and session close.
  Also load this skill when the user says "log this failure", "analyze what went wrong",
  or "what did we learn from this".
---

# Syntharra Self-Improvement Protocol

> Run after every major task or when something breaks. The goal: every failure becomes a standing rule within the same session.

---

## When to invoke

- After any task involving Retell agent changes, n8n workflow edits, or Supabase migrations
- When a test or validation fails in a non-obvious way
- When you discover a RULES.md rule was violated during the task
- When a bug appears that earlier validation didn't catch
- Explicitly: when the user says "log this failure", "analyze what went wrong", or "what did we learn"

---

## Step 1 — Capture the failure immediately

Before context is lost, record:

```
What failed:   <one-line symptom — be specific, not generic>
Root cause:    <why it happened — name the exact file/node/field/assumption>
Fix applied:   <what resolved it>
Rule implied:  <is there a standing rule to add? or "none">
Files touched: <which files were changed>
```

---

## Step 2 — Append a row to `docs/FAILURES.md`

Use this format (section style, matches existing entries):

```markdown
## YYYY-MM-DD — <short descriptive title>
**What failed:** <symptom>
**Root cause:** <specific cause>
**Fix:** <what was done>
**Rule:** <standing rule this implies, or "none">
```

If the failure is a simple table row type (date | area | symptom | root cause | fix | resolved):

```
| 2026-04-09 | <area> | <symptom> | <root cause> | <fix> | yes |
```

**If the failure implies a standing rule → add it to `docs/RULES.md` in the same commit.**
`session_end.py` warns if FAILURES.md was updated without a matching RULES.md entry.

---

## Step 3 — Update Claude memory

After a failure or correction, update the relevant memory file at:

```
C:\Users\danie\.claude\projects\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations\memory\
```

Files:
- `feedback_anti_patterns.md` — add the new rule under the correct section (Retell / n8n / Supabase / credentials / IDs)
- `project_live_state.md` — update if system state changed (new system live, new blocker, etc.)
- `reference_systems.md` — update if a new external system was added or a credential migrated

Rule format for `feedback_anti_patterns.md`:
```markdown
**<The rule — imperative, clear>**
**Why:** <incident date + specific cause>
**How to apply:** <when this rule kicks in, what action to take>
```

---

## Step 4 — Run pattern analysis

```bash
python tools/analyze_failures.py
```

Review the output:
- **Same area failing 3+ times?** → Add a pre-task validation step to the relevant skill file
- **Specific node/integration repeating?** → Add a `## GOTCHA` entry to the relevant `skills/*.md`
- **Gap in session start protocol?** → Update `docs/SESSION_START.md`

For JSON output (useful for programmatic processing):
```bash
python tools/analyze_failures.py --json
python tools/analyze_failures.py --area n8n
```

---

## Step 5 — Patch the relevant skill file (if warranted)

If the failure revealed a knowledge gap in a domain skill:

1. Identify the skill: `skills/syntharra-{retell,infrastructure,email,stripe,slack,brand,client-dashboard}-SKILL.md`
2. Add a `## GOTCHA` or update `## Common Mistakes` with:
   - Symptom (what you see)
   - Root cause (why it happens)
   - Fix or workaround (exact command or code pattern)

---

## Step 6 — Close the session

Always run at session end:

```bash
python tools/session_end.py --topic <slug> --summary "<one-line summary>"
```

This refreshes `STATE.md`'s header, appends to `docs/session-logs/INDEX.md`, and warns if a FAILURES.md update is missing a RULES.md counterpart.

---

## Failure triage decision tree

```
Something failed during a task?
│
├─ Config gap (missing credential, unset env var, model not set)?
│    → Class A: tell user what to configure. Do NOT re-edit code.
│
├─ Wiring error (bad expression, wrong field name, HTTP error from workflow logic)?
│    → Class B: fix the code, push, re-test.
│
├─ Runtime state (webhook not armed, activation not complete, timing)?
│    → Fix the state, not the code.
│
├─ GitHub MCP returned 403?
│    → Retry once in fresh subagent → Desktop Commander MCP → mirror + PUSH_ME.md → log FAILURES.md
│
├─ Supabase query returned error or wrong result?
│    → Verify: table = syntharra_vault (not vault), no `active` column, exact service_name strings
│    → Verify RLS is not blocking the service role
│
├─ Retell API call failing?
│    → Verify agent_id is from REFERENCE.md (never recalled from memory)
│    → Verify auth: Authorization: Bearer {key from vault}
│    → Verify you're not PATCHing a MASTER agent directly
│
└─ n8n workflow node behaving unexpectedly after edit?
     → Were you using n8n MCP? → Switch to REST API (never use MCP for targeted patches)
     → Did you verify sendHeaders=true on all auth'd HTTP nodes?
     → Did you trace the full variable path (webhook → Set node → template)?
```

---

## Syntharra-specific pre-task checklist

Before starting any task that touches production systems:

- [ ] Read `docs/STATE.md` — what's in flight? Coordinate if needed.
- [ ] Read `docs/FAILURES.md` (last 5 rows) — does this task touch any system that recently failed?
- [ ] Get all IDs from `docs/REFERENCE.md` — never recall from memory.
- [ ] Confirm testing path: clone → TESTING agent, never live MASTER.
- [ ] Confirm credential source: `syntharra_vault` query, never hardcoded.
