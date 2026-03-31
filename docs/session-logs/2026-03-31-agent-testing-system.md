# Session Log — 2026-03-31 — Agent Testing System + Claude Code Setup

## What Was Built

### Admin Dashboard — Go-Live Checklist
- Added 30-item Go-Live Checklist card to Settings tab in `admin.syntharra.com`
- 5 sections: Stripe, Retell, n8n Workflows, Infrastructure, Comms & Emails
- Interactive — click to tick, badge updates from Not Ready → Almost Ready → Ready to Launch
- JS functions: `toggleGolive()`, `updateGoliveBadge()`, `resetGolive()`

### Supabase — Agent Testing Tables
- Created `agent_test_results` table (one row per scenario per test run)
- Created `agent_pending_fixes` table (pending prompt fixes awaiting Dan's approval)
- Created `agent_test_run_summary` view (one row per run with pass rate)
- Created `agent_pending_fixes_view` (pending fixes with run context)

### Admin Dashboard — Agent Testing Tab
- New "Agent Testing" nav item added
- Full UI: run button, agent/group selector, run label input
- Live progress bar, pass rate stats, group breakdown chart
- Failed scenarios table with expandable transcripts (click to see full conversation)
- Pending Fixes card with Approve/Reject buttons per fix
- JS functions: `loadTestingData()`, `startTestRun()`, `approveFix()`, `rejectFix()`, `renderPendingFixes()`, etc.

### n8n — Agent Test Runner (ID: 3MMp9J8QN0YKgA6Q)
- Webhook: POST https://n8n.syntharra.com/webhook/agent-test-runner
- Body: { agent_type, groups, run_label }
- Status: CREATED + ACTIVATED — but broken (Code node uses fetch() which is blocked in n8n sandbox)
- Needs rebuild using HTTP Request nodes — best done in Claude Code

### n8n — Fix Approver (ID: ZAAtRETIIVZSMMDk)
- Webhook: POST https://n8n.syntharra.com/webhook/apply-agent-fix
- Body: { fix_id, approved_by }
- Status: CREATED + ACTIVATED — same fetch() issue as test runner
- Needs rebuild using HTTP Request nodes — best done in Claude Code

### Test Scenarios
- 95 scenarios pushed to `tests/agent-test-scenarios.json`
- Groups: core_flow (15), personalities (15), info_collection (15), pricing_traps (8), edge_cases (15), boundary_safety (12), premium_specific (15)
- Standard uses 80 scenarios (excludes premiumOnly), Premium uses all 95

### CLAUDE.md Files (Claude Code Setup)
- `syntharra-automations/CLAUDE.md` — comprehensive master context (259 lines)
- `syntharra-admin/CLAUDE.md` — admin repo context
- `syntharra-ops-monitor/CLAUDE.md` — ops monitor context
- `syntharra-checkout/CLAUDE.md` — checkout context
- All include pointer to project-state.md and vault for credentials

## What Needs Finishing

### PRIORITY: Fix n8n test runner workflows
Both workflows need rebuilding to use HTTP Request nodes instead of fetch() in Code nodes.
Use Claude Code with the prompt in project-state.md.
Workflow IDs to update (not recreate): 3MMp9J8QN0YKgA6Q and ZAAtRETIIVZSMMDk

## Key Decisions Made
- Using Groq (free) for all test simulation and evaluation — not Claude API
- Groq model: llama-3.3-70b-versatile
- Fixes require Dan's manual approval before being applied to Retell — never automatic
- 5-10% false pass rate acceptable at this stage — real call data will refine after launch

## Claude Code MCP Config
Full config documented in syntharra-automations/CLAUDE.md
MCPs needed: Supabase, n8n, Railway, Stripe, GitHub
Railway MCP package: @railway/mcp-server (confirm package name when online)
