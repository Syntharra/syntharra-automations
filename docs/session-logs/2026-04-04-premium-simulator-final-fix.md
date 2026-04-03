# Session Log — 2026-04-04 — Premium simulator fixed + agentic rules enforced

## Simulator fix
Problem: Groq llama-3.3-70b TPM=12k. Premium prompt ~24k chars (global + 18 node instructions) = ~6k tokens.
12 API calls/scenario × 6k tokens = constant rate limit.

Wrong fix attempted: Strip node instructions to reduce tokens. REVERTED — invalidates the test entirely.
Node instructions define booking flow, callback handling, emergency routing. Required for valid results.

Correct fix: Switch to meta-llama/llama-4-scout-17b-16e-instruct (30k TPM). Full prompt fits cleanly.

Rule: If TPM limit hit — upgrade model TPM. Never reduce prompt content.

## Agentic self-improvement
Dan identified that PRE-ACTION reasoning was missing — quick fixes were being taken without asking
"what does this break?" Added PRE-ACTION PROTOCOL to CLAUDE.md with 3 mandatory questions:
1. WHY am I doing it this way? (root cause vs symptom)
2. WHAT would be invalidated if I'm wrong?
3. Does this belong in ARCHITECTURE.md or a skill file?

## Files updated this session
- CLAUDE.md — PRE-ACTION PROTOCOL added (permanent, loads every session)
- ARCHITECTURE.md — 3 decisions: simulator model choice, Claude Code requirement, Groq migration
- skills/e2e-hvac-premium-SKILL.md — simulator operating manual, model requirement, node instructions rule
- skills/syntharra-retell-SKILL.md — premium prompt fix patterns, booking step order, em-dash encoding
- FAILURES.md — corrected simulator rate limit lesson
- docs/TASKS.md — next action updated
- tools/openai-agent-simulator-premium.py — llama-4-scout, node instructions restored, rate limit fixes

## State at session close
- Premium TESTING flow: all 6 core_flow fixes applied and published
- Simulator: ready to run in Claude Code (llama-4-scout, full prompt, Groq key in vault)
- Next: git pull → run all 7 groups → fix failures → promote TESTING to MASTER
