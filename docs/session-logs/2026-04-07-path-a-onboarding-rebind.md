# Session Log — 2026-04-07 — Path A onboarding rebind + downstream fixes

## Goal
Path A: get full HVAC onboarding pipeline working end-to-end (minus Telnyx + Stripe live mode flip).

## Done
- Rebound Supabase + Retell auth on both onboarding workflows (n8n PUT had stripped credentials)
- Added explicit Bearer/apikey headers to all HTTP nodes
- Fixed `Query Client Agents` empty-response halting (fullResponse + body length check)
- Removed broken `INSERT client_agents` node — repointed dedupe at canonical `hvac_standard_agent` (added submission_id column)
- Fixed `sendHeaders=false` flag preventing header injection on Retell HTTP nodes
- Renamed `starting_node_id` -> `start_node_id` in Standard + Premium prompt builders (Retell API contract)
- Added google-only guard in `Send Google OAuth Email` to skip Brevo call when integration_type != 'google'
- Created **HVAC Premium MASTER** Retell agent: `agent_af3ac35808a5b5ae1492090155` (flow `conversation_flow_fbc9507db46b`)
- Backed up Premium MASTER to `retell-agents/hvac-premium-master.json`

## Smoke test results
- Standard exec 2015: success — agent `agent_c900c5816124465f7681e3d279` created, terminates at Validate: Token Budget
- Premium exec 2016: success — runs through 20+ nodes, ends at Slack notification

## Open
- **Path B**: build v4 rewrite-based agentic test-fix script (replace v3 append-only ceiling at 86%/83%) — NOT STARTED, deferred
- Standard onboarding stops at `Validate: Token Budget` — verify whether downstream activation/email steps exist or need wiring
- Telnyx + Stripe live (waiting on Dan)

## Failures captured
See FAILURES.md — 6 new rows.

## Key IDs
- Standard MASTER: agent_4afbfdb3fcb1ba9569353af28d
- Premium MASTER: agent_af3ac35808a5b5ae1492090155 (NEW)
- Premium MASTER flow: conversation_flow_fbc9507db46b (NEW)
