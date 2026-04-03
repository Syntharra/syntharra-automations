# Session Log — 2026-04-04 — Premium simulator fixed

## Root cause of rate limit failures
Premium prompt was 24,748 chars (~6,000 tokens) because fetch_agent_prompt() was appending
all 18 node instruction texts on top of the global prompt. Standard simulator worked because
its flow has fewer/shorter nodes (~10k chars total). With 12 API calls per scenario and
6k tokens each, the 12k TPM limit was hit on scenario #1 every time.

## Fix applied
- Stripped node instructions from fetch_agent_prompt() — returns global_prompt only (~10,359 chars)
- Reverted model to llama-3.3-70b-versatile (same as standard — proven to work)
- Removed MODEL_FAST / dual-model complexity (unnecessary)
- Kept rate limit fixes: 1s inter-call sleep, 5s inter-scenario sleep, retries=6

## Simulator now matches standard config exactly
Same model, same prompt structure, same retry logic. Standard ran 80/80. Premium should run clean.

## Next session
- git pull in Claude Code
- Run all 7 groups: core_flow → personalities → info_collection → pricing_traps → edge_cases → boundary_safety → premium_specific
- Groq key from Supabase vault (service_name='Groq')
