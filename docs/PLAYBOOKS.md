# Playbooks — Syntharra Automations

> **Positive knowledge.** This file documents HOW to do things correctly in this system.
> RULES.md tells you what NOT to do. This file tells you the established correct pattern.
> Read at every session start. Updated by the daily synthesis script + manually when patterns solidify.

_Last updated: 2026-04-11_

---

## Playbook 1 — Add or modify a Retell agent prompt / flow

**When:** Changing what the AI receptionist says, how it handles calls, its nodes, components, or flow logic.

```
1. NEVER touch MASTER directly. All changes go through TESTING first.

2. Edit the manifest / template:
   - Node prompts → retell-iac/components/<node-name>.md
   - Flow structure → retell-iac/flows/hvac-standard.template.json
   - YAML manifest  → retell-iac/manifests/hvac-standard.yaml

3. Build:
   python retell-iac/scripts/build_agent.py

4. Diff (must be clean before promoting):
   python retell-iac/scripts/diff.py

5. Promote to MASTER only after TESTING passes:
   python retell-iac/scripts/promote.py

6. Snapshot the new baseline:
   retell-iac/snapshots/YYYY-MM-DD_<label>/

7. Update REFERENCE.md if any IDs changed.
```

**Key IDs (from REFERENCE.md — never recall from memory):**
- TESTING agent: `agent_41e9758d8dc956843110e29a25` / flow `conversation_flow_bc8bb3565dbf`
- MASTER agent:  `agent_b46aef9fd327ec60c657b7a30a` / flow `conversation_flow_19684fe03b61`

**Gotchas:**
- `start_node_id` not `starting_node_id` in flow payloads (Rule 19)
- After any flow edit, check `components[]` for phantom placeholder entries (Rule 33)
- `pause_retell_agent` must NEVER be called with the MASTER agent ID (Rule 42)
- Every non-terminal node needs a non-empty `edges[]` (Rule 55)
- Every finetune example must reference an existing node ID (Rule 55)

**Disaster recovery — MASTER/TESTING agents deleted from Retell account:**
```
1. Re-register from latest snapshot:
   python tools/re_register_master.py

2. Full downstream update (Rule 57):
   a. docs/REFERENCE.md — new agent_id + flow_id for both agents
   b. docs/STATE.md — update current agent state block
   c. retell-iac/scripts/promote.py — update MASTER/TESTING ID constants
   d. Supabase: UPDATE client_agents SET template_agent_id = '<new>' WHERE ...
   e. syntharra_vault: check for rows embedding old IDs as values
   f. n8n onboarding workflow: GET workflow JSON, grep for old agent ID, update
      the Clone Agent Code node hardcoded MASTER ID to new ID

3. Take a new snapshot: retell-iac/snapshots/YYYY-MM-DD_post-recovery/

4. Notify Dan: phone number re-binding is UI-only in Retell dashboard.
   Mark incomplete until Dan confirms the binding.
```
_Tested 2026-04-09. Missing step 2f caused onboarding to silently clone from deleted ID._

---

## Playbook 2 — Add or modify an n8n workflow

**When:** Building a new workflow, patching an existing one, or adding nodes.

### Creating a new workflow
```
1. Build the workflow JSON in Python (tools/build_*.py pattern)
2. Strip 'active' from POST body — n8n returns 400 if included (Rule 53)
3. POST /api/v1/workflows  →  returns {id: "..."}
4. POST /api/v1/workflows/{id}/activate  (separate call)
5. Add the new ID to docs/REFERENCE.md immediately
6. Update STATE.md with the workflow's purpose
```

### Patching an existing workflow (the ONLY safe pattern)
```
1. GET  https://n8n.syntharra.com/api/v1/workflows/{id}
   Header: X-N8N-API-KEY: <from syntharra_vault service_name='n8n Railway'>

2. Modify target node(s) in Python — never hand-edit the full JSON

3. PUT  https://n8n.syntharra.com/api/v1/workflows/{id}
   Body must contain ONLY: name, nodes, connections, settings
   (settings: only executionOrder inside)
   Strip everything else or get 400.

4. After any PUT: verify HTTP nodes that need auth still have
   sendHeaders=true + headerParameters (credentials are silently stripped by PUT)
```

### Getting the n8n API key
```python
import requests, os
r = requests.post(
    "https://n8n.syntharra.com/api/v1/...",  # from REFERENCE.md
    headers={"X-N8N-API-KEY": vault_key}
)
# Key from: SELECT secret_value FROM public.syntharra_vault
#           WHERE service_name = 'n8n Railway' AND key_type = 'api_key'
```

**Gotchas:**
- NEVER use `mcp__claude_ai_n8n__*` tools — they talk to a cloud account we don't use (CLAUDE.md)
- NEVER `DELETE /api/v1/workflows/{id}` — hard delete, no recovery (CLAUDE.md)
- Code nodes cannot make outbound HTTP — use HTTP Request nodes (Rule 10/31)
- n8n expression fields must start with `=` or braces are literal (Rule 30)
- IF branches silently drop upstream context — reach back with `$('Node Name').first().json` (Rule 12)
- HTTP → Code chains where HTTP might return empty array: use `fullResponse: true` (Rule 16/43)
- n8n Code nodes hardcoding MASTER/TESTING agent IDs: fetch from vault at runtime (Rule 54)

**Active workflow IDs (from REFERENCE.md):**
- Standard onboarding: `4Hx7aRdzMl5N0uJP`
- Call processor (lean fan-out): `Kg576YtPM9yEacKn`
- Client agent update form: `6Mwire23i6InrnYZ`
- Retell proxy webhook: `Y1EptXhOPAmosMbs`

---

## Playbook 3 — Add or modify a Supabase table or query

**When:** Creating tables, writing migrations, querying data, writing RLS policies.

### Before any INSERT — always run schema check first
```sql
-- 1. Check NOT NULL + defaults
SELECT column_name, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'your_table';

-- 2. Check CHECK constraints (enum values etc.)
SELECT pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'your_table'::regclass AND contype = 'c';

-- 3. Check dependent views before any DROP
SELECT * FROM information_schema.view_table_usage
WHERE table_name = 'your_table';
```

### Credential pattern (always fetch from vault — never hardcode)
```sql
SELECT secret_value FROM public.syntharra_vault
WHERE service_name = 'X' AND key_type = 'Y';
```
**Table name is `public.syntharra_vault` — not `vault`, not `secrets`. No `active` column.**

### The canonical tables and their purpose
| Table | Purpose |
|---|---|
| `client_agents` | One row per client agent clone. `agent_id` is NOT NULL — never INSERT before Retell returns it. |
| `client_subscriptions` | Billing state. `plan_type` CHECK constraint: `'standard'` or `'premium'` only (not `'hvac_standard'`). |
| `hvac_standard_agent` | Single config row — template values for the MASTER agent (flow ID, phone, etc.) |
| `monthly_billing_snapshot` | Immutable rollup written at invoice time for dispute defense. One row per client per month. |
| `website_leads` | Inbound leads from website. RLS: service role only for writes. |
| `syntharra_vault` | All credentials. Never hardcode a secret anywhere else. |
| `client_dashboard_info` | VIEW (narrow read subset for dashboard). Do not write to it. |
| `marketing_intelligence` | Reddit/YouTube/Trends intelligence. RLS: service role only. |

### ON CONFLICT upserts
Verify a unique constraint exists on the conflict column(s) first.
If not: use DELETE WHERE + INSERT pattern (not ON CONFLICT).

### Supabase GET returning empty array in n8n
Set `options.response.response.fullResponse: true` on the HTTP Request node.
Empty 200 still emits one item with `body: []` — downstream IF nodes can check `body.length`.

---

## Playbook 4 — Add a new email template

**When:** Adding a new transactional email (onboarding, pilot lifecycle, notification).

```
1. Write HTML in shared/email-templates/<slug>.html
   - Logo: inline wordmark only — <p style="font-size:28px;font-weight:900;
     letter-spacing:6px;color:#ffffff;">SYNTHARRA</p>
   - NEVER use <img src="..."> for the logo (renders as broken placeholder)

2. Upload to Brevo:
   python tools/upload_brevo_templates.py
   (idempotent — safe to re-run, updates existing templates)
   Sender: daniel@syntharra.com (only verified Brevo sender)

3. Note the Brevo template ID returned and add to REFERENCE.md

4. Wire in n8n: HTTP Request node → POST https://api.brevo.com/v3/smtp/email
   - Template ID in body
   - Auth: X-API-KEY from syntharra_vault (service_name='Brevo')
   - sendHeaders: true (Rule 18)

5. Trace the variable path end-to-end:
   webhook payload → Set node key name → email HTML {{params.X}}
   Key names must match exactly at every step (Rule 23/24)

6. Test with a real send — inspect the rendered email in a mail client.
   Do not approve based on n8n node output alone (Rule 25).
```

**Active Brevo pilot templates (REFERENCE.md):**
- `pilot-welcome` → ID 7, `pilot-day-3` → 4, `pilot-day-7` → 5, `pilot-day-12` → 3
- `pilot-converted` → 2, `pilot-card-added` → 1, `pilot-expired` → 6
- `pilot-winback-16` → 8, `pilot-winback-30` → 9

---

## Playbook 5 — Handle a JotForm webhook in n8n

**When:** Parsing a JotForm submission in any n8n workflow.

```javascript
// Step 1: Always parse rawRequest — direct body.q* keys are absent or stale
const bodyRaw = $input.first().json.body || $input.first().json;
const formData = { ...bodyRaw, ...JSON.parse(bodyRaw.rawRequest) };

// Step 2: Unwrap phone fields (come as objects, not strings)
function cleanPhone(val) {
  if (typeof val === 'object' && val?.full)
    return String(val.full).replace(/[^+\d]/g, '');
  return String(val || '').replace(/[^+\d]/g, '');
}

// Step 3: Normalise checkbox fields (two patterns exist)
// Old-style (q13, q14, q29, q45, q49): formData['q{N}_option_'] → string
// New-style (q79, q80, q81): formData['q{N}_{camelName}'] → array
function normalizeList(val) {
  if (!val) return [];
  if (Array.isArray(val)) return val;
  return String(val).split(',').map(s => s.trim()).filter(Boolean);
}

// Step 4: After adding any new checkbox field — submit a test form,
// inspect rawRequest keys in n8n webhook output, then hardcode the exact key.
// NEVER assume the key pattern without verifying.
```

**HVAC Standard form ID:** `260795139953066`
**Pilot onboarding form ID:** `261002359315044` (Phase 0, branches internally on `pilot_mode` hidden field)

---

## Playbook 6 — Add or rotate a credential in the vault

**When:** New API key, rotating an existing secret, adding a new service.

```sql
-- Add new credential
INSERT INTO public.syntharra_vault (service_name, key_type, secret_value)
VALUES ('ServiceName', 'api_key', 'sk-...');

-- Rotate existing (no ON CONFLICT — use DELETE + INSERT)
DELETE FROM public.syntharra_vault
WHERE service_name = 'ServiceName' AND key_type = 'api_key';

INSERT INTO public.syntharra_vault (service_name, key_type, secret_value)
VALUES ('ServiceName', 'api_key', 'sk-new...');

-- Fetch at runtime (always this exact query)
SELECT secret_value FROM public.syntharra_vault
WHERE service_name = 'ServiceName' AND key_type = 'api_key';
```

**Rule:** Zero hardcoded secrets anywhere. If you find one, that's a P0 security task — migrate immediately and log in FAILURES.md (Rule 26).

---

## Playbook 7 — Handle a Retell post-call webhook in n8n (Call Processor)

**When:** Processing call events from Retell's webhook in the lean fan-out workflow.

```
Active workflow: Kg576YtPM9yEacKn (HVAC Call Processor — lean fan-out)
Triggers on: is_lead === true OR urgency === 'emergency'

Pipeline:
  Retell webhook → filter (is_lead OR urgency=emergency) → lookup client
  → build payload → [email fan-out] [Slack fan-out] [SMS stub]

Post-call analysis custom fields declared on MASTER (must exist on agent):
  - is_lead    (boolean)
  - urgency    (enum: emergency / high / normal / low / none)
  - is_spam    (boolean)
  - service_type    (string, optional)
  - customer_name   (string, optional)

Gotcha: Retell only populates call_analysis.custom_analysis_data.*
for fields declared on the agent. If missing, add to MASTER first,
promote, then next billing cycle is the cutover.

SMS: stub node present, blocked on Telnyx vault entries being added.
Slack: fires only if client has slack_webhook_url set in client_agents.
Email: always fires via Brevo — key from syntharra_vault service_name='Brevo'.
```

---

## Playbook 8 — Run the daily self-improvement synthesis manually

**When:** Testing the learning loop, running after a bad session, or verifying fixes.

```bash
# Dry run (no files written — shows what would be added)
python tools/weekly_self_improvement.py --dry-run

# Live run covering last 2 days (same as scheduled run)
python tools/weekly_self_improvement.py --days 2

# Full week review
python tools/weekly_self_improvement.py --days 7

# View failures analysis
python tools/analyze_failures.py
python tools/analyze_failures.py --area n8n
python tools/analyze_failures.py --top 5
```

**Schedule:** Windows Task Scheduler — `Syntharra-DailySelfImprovement` — every day at 07:00.
**Log:** `.claude/weekly-task.log`

---

## Playbook 9 — Deploy or update a Python cron tool to Railway

**When:** A new Python tool needs to run on a schedule in production.

```
1. Tool lives in tools/<name>.py in this repo
2. On Windows: always write output to file with encoding='utf-8' — never print()
   for non-ASCII content (Rule 37/41)
3. Any claude -p subprocess call:
   - Windows: ['cmd', '/c', 'claude'] + args (Rule 40/49)
   - Run from temp dir with neutral CLAUDE.md for neutral inference (Rule 39/47)
4. All credentials fetched from syntharra_vault at runtime — zero hardcoded
5. Deploy via Railway: connect repo, set env vars, set cron schedule
6. Log to .claude/weekly-task.log or tool-specific log file
```

**Never use shell=True** in subprocesses — breaks stdin piping and introduces injection risk.

---

## Playbook 10 — Session start / end protocol

**When:** Every single session, no exceptions.

### Session start (auto-triggered by hook on first prompt)
```
1. session_auto_start.py fires → runs tools/session_start.py
2. Read output: last session, ghost-session warning, recent commits,
   last 3 failures, in-flight work, next session priorities, uncommitted files
3. Read docs/SESSION_START.md → STATE.md → RULES.md → REFERENCE.md → FAILURES.md
4. Read docs/PLAYBOOKS.md (this file) → docs/DECISIONS.md
```

### Session end (run before closing — hook auto-runs if forgotten)
```bash
python tools/session_end.py --topic <short-slug> \
  --summary "<one-line>" \
  --priorities "- item 1\n- item 2"
```

**If a mistake was made during the session:**
→ Write the rule to `docs/RULES.md` NOW (Rule 56) — do not wait for the hook.
→ Write entry to `memory/feedback_anti_patterns.md` NOW.
→ Add row to `docs/FAILURES.md` if the mistake caused a real incident.
