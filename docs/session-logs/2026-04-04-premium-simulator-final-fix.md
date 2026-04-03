# Session Log — 2026-04-04 — Premium simulator fixed (final)

## Problem
Groq llama-3.3-70b-versatile has 12,000 TPM limit.
Premium simulator prompt = global_prompt (~10k chars) + 18 node instruction texts = ~24,748 chars total (~6,000 tokens).
With 12 API calls per scenario: 6,000 × 12 = 72,000 tokens/scenario needed. Hard rate limit hit every time.
Standard simulator worked because standard flow has fewer/shorter nodes (~10k chars total, ~2,500 tokens).

## Wrong fix (reverted)
Stripping node instructions to reduce prompt size — WRONG.
Node instructions define how the agent behaves at each stage of the call.
Testing without them means testing an incomplete agent. Invalid results.

## Correct fix
Switch to meta-llama/llama-4-scout-17b-16e-instruct — 30,000 TPM (2.5x headroom).
Full prompt + all node instructions fit cleanly within the limit.
No content stripped. Test is valid.

## Rule going forward
- Standard simulator: llama-3.3-70b is fine (small prompt)
- Premium simulator: must use llama-4-scout or higher TPM model (large prompt)
- NEVER strip node instructions — they are required for valid behaviour testing
- If TPM limit hit: upgrade model TPM, not reduce prompt content

## Simulator state
- Model: meta-llama/llama-4-scout-17b-16e-instruct (30k TPM)
- Prompt: full global prompt + all node instructions (correct)
- Rate limit fixes: 1s inter-call sleep, 5s inter-scenario sleep, retries=6
- Ready for Claude Code run
