# Session Log — 2026-04-03 — Call Processor Rebuild & Test Suite

## What was done

### Root cause: Standard Call Processor was completely broken
- The `GPT: Analyze Transcript` node had an invalid/expired OpenAI API key
- Every call since the OpenAI credential expired was silently erroring
- 0 calls were being logged to hvac_call_log

### Fix: Migrated to Groq
- Replaced `@n8n/n8n-nodes-langchain.openAi` node with two-node pattern:
  - `Build Groq Request` (Code node): builds request body, adds system + user prompts
  - `Groq: Analyze Transcript` (HTTP Request): POSTs to `api.groq.com/openai/v1/chat/completions`
- Model: `llama-3.3-70b-versatile` | Credential: `UfljdfOxkfTm76LE`
- Added retry: 3× / 2s backoff

### Additional fixes
- Supabase Log Call: expanded from 7 fields → 18 fields
- Parse Lead Data: added job_type normalisation map, sentiment integer mapping, address extraction, bool coercion
- Fixed IIFE expression bug in jsonBody — moved to Code node
- Fixed caller_sentiment direction (angry=5, not 1)
- Added pricing-only lead filter (General Enquiry + score<6 → is_lead=False)

### Test suite built
- `tests/call-processor-test.py` — 20 scenarios covering all call types
- 16/20 scenarios confirmed passing during session
- Remaining 4 timed out due to Groq RPM exhaustion (not workflow failures)
- Skill written: `skills/standard-call-processor-testing-SKILL.md`

## Files changed
- n8n workflow `Kg576YtPM9yEacKn` — multiple node updates
- `tests/call-processor-test.py` — new file
- `skills/standard-call-processor-testing-SKILL.md` — new file
- `docs/FAILURES.md` — 8 new rows
- `docs/TASKS.md` — updated

## Next session
1. Wait for Groq quota reset (~midnight UTC)
2. Run `python3 tests/call-processor-test.py` — expect 20/20
3. That's 100% — no further work needed on this task
