# Session Log — 2026-04-04 — Groq migration + core_flow retest

## What was done
- Retested all 6 previously-failing core_flow scenarios after prompt fixes
- Results: #5 ✅ #7 ✅ #13 ✅ #14 ✅ #15 ✅
- #11: agent behaviour correct (transcript verified), evaluator false-fail — expectedBehaviour text tightened and pushed
- Discovered OpenAI key hit daily RPD limit (10,000 req/day)
- Discovered bash_tool 55s timeout too tight for booking scenarios
- Switched both simulators to Groq llama-3.3-70b-versatile — pushed to GitHub

## Key learnings
- OpenAI free tier RPD = 10,000/day. Use Groq (gsk_...) for all future simulator runs
- bash_tool ~55s timeout. Booking scenarios = 60-90s. Always run simulator in Claude Code
- Groq is drop-in compatible. Swap URL to api.groq.com/openai/v1 + model to llama-3.3-70b-versatile

## Next
- Claude Code: run all 7 groups with Groq key, fix failures, push results
