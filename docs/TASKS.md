# TASKS

## Done — 2026-04-08

- Standard MASTER auto-layout blocker fixed (removed phantom blank Component L1 from flow)
- Premium start_node_id set to node-greeting (was null)
- Premium end_call_after_silence_ms added (was missing, Standard had it)
- node-extract-caller-data deleted from both Standard and Premium flows (was orphaned)
- All 4 agents renamed: Arctic Breeze Standard LIVE, Arctic Breeze Premium LIVE, Arctic Breeze Standard DEMO, Arctic Breeze Premium DEMO
- E2E 73/73 Standard ✅, 73/73 Premium ✅ (post-rename, post-flow-fix run)
- Email fix: ai_phone_number variable wired correctly (was blank in "you're live" email and Quick Start Checklist)
- Email fix: transfer_phone_number wrong key corrected (was blank in email)
- Email fix: Premium "you're live" email guard condition removed (was blocking send entirely)
- Email template simplified: call forwarding section replaced with one-line reference + download button
- Email template: "What Happens on Every Call" section removed (covered in PDF)
- Email template: "Common Questions" FAQ section removed (covered in PDF — verified across pages 6, 7, 10-11)
- Both n8n workflows patched and live-verified (8/8 Standard nodes, 4/4 Premium nodes)

## P0 — Migrate Brevo API key to Supabase vault
- Move hardcoded Brevo API key from n8n workflow node to syntharra_vault table
- Update workflow to read key from vault at runtime

## P0 — Run Standard 12-scenario eval harness (v4r1)
- Write async eval harness using fetch_agent_prompt_full (tools/agentic-test-fix-v3.py has the helper)
- Run 12 failing scenarios first (10,16,19,22,23,28,41,60,63,66,73,75)
- Run full 91 regression
- Target ≥95%, no prompt bloat
- Agent: agent_9d6e1db069d7900a61b78c5ca6 / flow conversation_flow_a54448105a43

## P0 — n8n onboarding broken at submission_id (pre-existing)

## P1 — Fix dashboard URL in Standard and Premium email templates
- dashboard.html exists in syntharra-website repo (50,515 bytes, confirmed)
- Replace broken/placeholder dashboard URL in both Standard and Premium n8n "you're live" email templates
- Correct URL: https://syntharra.com/dashboard.html
- Also fix Quick Start Checklist "Open your dashboard at..." line

## P1 — After Standard green, repeat for Premium
- agent_2cffe3d86d7e1990d08bea068f (interim) vs agent_af3ac35808a5b5ae1492090155 (new) — determine canonical first

## Notes
- n8n webhook /webhook/agent-test-runner is INACTIVE (404). Do not retry — use direct harness.
- v3 simulator default uses compressed prompt (blind to components). Always use _full for v4+.
