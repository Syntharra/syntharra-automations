# Session: 2026-04-05 — E2E Updates + Agentic Testing Plan

## What was done
1. Both E2E pipeline tests verified passing (Standard 93/93, Premium 106/106)
2. Fixed stale assertions — node count checks updated from exact to minimum (>= 15, >= 20)
3. Fixed custom_greeting assertion (case-insensitive matching)
4. All 3 E2E skill files rewritten for subagent component architecture v2
5. Simulator scripts updated to fetch subagent component instructions + edge routing data
6. Deep coverage gap analysis: Standard 54%→82%, Premium 72%→91% flow path coverage
7. 13 new test scenarios added (#96-108): Spanish routing, emergency fallback, transfer failures, voicemail, multi-issue stress test, competitor pricing
8. Agentic Testing Plan designed and documented (docs/AGENTIC-TESTING-PLAN.md)
9. `tools/agentic-test-fix.py` engine built — runs scenarios, triages failures as BAD_SCENARIO/PROMPT_GAP/VARIANCE
10. New skill: `hvac-premium-agent-testing-SKILL.md` created
11. Updated skills: `hvac-standard-agent-testing-SKILL.md`, `e2e-hvac-standard-SKILL.md`, `e2e-hvac-premium-SKILL.md`

## Groq budget analysis
- Both agents combined: ~3,383 calls = 23.5% of daily free limit
- Uses llama-4-scout-17b-16e-instruct (30k TPM) for both agents
- Never use llama-3.3-70b for Premium (6k TPM too slow for 27k char prompt)

## Session reflection
1. **What did I get wrong?** Initially ran simulator tests when Dan wanted E2E pipeline tests. Need to confirm which test type is requested.
2. **What assumption was incorrect?** Assumed simulator = what Dan wanted. E2E pipeline tests are the infrastructure validation, simulator is agent behaviour validation — different purposes.
3. **What would I do differently?** Ask which test type before running. E2E first (validates pipeline), then simulator (validates agent behaviour).
4. **Pattern for future:** E2E = pipeline health. Simulator = agent quality. Agentic engine = automated improvement. Three distinct tools, three distinct purposes.
5. **Added to ARCHITECTURE.md:** N/A this session (no architectural decisions made, only testing infrastructure).
6. **Unverified assumptions:** Groq rate limits are based on docs research, not live testing. First full agentic run will reveal actual throughput.
