# TASKS

## P0 — Resume v4r1 Standard measurement
- Write async eval harness using fetch_agent_prompt_full (tools/agentic-test-fix-v3.py has the helper)
- Run 12 failing scenarios first (10,16,19,22,23,28,41,60,63,66,73,75)
- Run full 91 regression
- Target ≥95%, no prompt bloat
- Agent: agent_9d6e1db069d7900a61b78c5ca6 / flow conversation_flow_a54448105a43

## P0 — n8n onboarding broken at submission_id (pre-existing)

## P1 — After Standard green, repeat for Premium
- agent_2cffe3d86d7e1990d08bea068f (interim) vs agent_af3ac35808a5b5ae1492090155 (new) — determine canonical first

## Notes
- n8n webhook /webhook/agent-test-runner is INACTIVE (404). Do not retry — use direct harness.
- v3 simulator default uses compressed prompt (blind to components). Always use _full for v4+.
