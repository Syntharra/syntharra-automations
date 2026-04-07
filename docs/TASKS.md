# Open Tasks

## P0 — Critical
- **Fix n8n onboarding workflows**: `Check Idempotency & Insert` node throws `Cannot read properties of undefined (reading 'submission_id')` on both Standard (`4Hx7aRdzMl5N0uJP`) and Premium (`kz1VmwNccunRMEaF`). Blocks ALL new client onboarding. Likely JotForm payload schema drift — fix Code node line 2 to read submission_id from correct path.

## P1 — High
- Build `agentic-test-fix-v4.py` with **rewrite-based** fixes (not append-only). v3 hits 86% ceiling because COMPONENT_MAX_CHARS cap blocks further appends after ~3200 chars.
- Make `call_style_detector` patchable — currently "no instruction node", blocks abuse/profanity scenario fixes.
- Re-run E2E (`shared/e2e-test.py`, `shared/e2e-test-premium.py`) once n8n is fixed, to verify today's component patches did not regress live agents.

## P2 — Medium
- Test ceiling: Premium 90/108 (83%), Standard 79/91 (86%) — gap to 95% requires v4 architecture.

## Reference (current)
- Standard TESTING: `agent_9d6e1db069d7900a61b78c5ca6` / `conversation_flow_a54448105a43` (cloned 2026-04-07)
- Premium TESTING == Premium MASTER: `agent_2cffe3d86d7e1990d08bea068f` / `conversation_flow_2ded0ed4f808`
- v3 script: COMPONENT_MAX_CHARS=3200, $5 cap per agent, ~$0.15/run typical
