# Session Log — 2026-04-02 — Simulator Build + Loop Fixes + OpenAI Vault

## Summary
Built OpenAI-powered agent simulator (~$0.002/scenario vs $0.15 Retell).
Fixed Retell loop detection root causes. Added OpenAI key to vault.
Ran first simulator tests — identified evaluator scoring issue with transfers.

## OpenAI Key
- Added to syntharra_vault: service_name='OpenAI', key_type='api_key'
- Confirmed single clean entry

## Loop Fixes Applied to Standard TESTING Flow
Four structural fixes — all pushed and published:
1. catch-all edge on identify_call → leadcapture (ambiguous callers had nowhere to go)
2. Ending node hard close — one exchange max, no re-routing
3. general_questions loop guard — 2+ questions without booking intent → collect and close
4. leadcapture refusal handling — caller refuses info twice → graceful close

## Prompt Fixes Applied
- identify_call routing rewritten: EMERGENCY is now check #1 (was check #2)
- Emergency edge condition strengthened: includes "no heat", "no cooling", "burning smell" etc
- Pricing rules tightened: no comparison pricing, no engaging back-and-forth
- Callback node: no "anything else to pass along" question
- Service area: out-of-bounds handling added to leadcapture

## Simulator (tools/openai-agent-simulator.py)
- Model: gpt-4o-mini
- Groups: core_flow, personalities, info_collection, pricing_traps, edge_cases, boundary_safety
- Usage: GITHUB_TOKEN=... RETELL_KEY=... python3 tools/openai-agent-simulator.py --key sk-... --group core_flow
- Rate limit retry: 3 attempts, 20s backoff
- Evaluator context: transfer/emergency scored on INTENT not physical completion
- Results pushed to tests/results/

## Test Results This Session
| Run | Group | Pass | Total | Rate | Cost |
|---|---|---|---|---|---|
| pricing-traps-run1 | pricing_traps | 4 | 8 | 50% | $0.07 |
| core-flow-run1 | core_flow | 7 | 15 | 47% | $0.10 |
| core-flow-run2 | core_flow | 2 | 15 | 13% | $0.04 (rate limited) |

## Key Finding
Core flow failures #2, #6, #12 — Sophie's BEHAVIOUR is correct (she transfers).
Evaluator was marking FAIL because physical transfer can't complete in text sim.
Fixed: evaluator now accepts "agent initiated/offered transfer" as PASS.

## Next Session — Start With
1. Fetch CLAUDE.md + TASKS.md
2. Run: GITHUB_TOKEN=... RETELL_KEY=... python3 tools/openai-agent-simulator.py --key <from vault> --group core_flow --label core-flow-run3
3. Then run all remaining groups: personalities, info_collection, pricing_traps, edge_cases, boundary_safety
4. Fix any genuine failures, iterate until 90%+
5. Promote TESTING → MASTER once verified
