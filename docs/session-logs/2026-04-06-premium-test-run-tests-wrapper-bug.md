# Session Log — 2026-04-06 — Premium Test / run_tests.py Wrapper Bug

## Summary
Attempted to run Premium agent test (108 scenarios, gate ≥95/108) for promotion to MASTER.
Full day's Groq TPD budget (500K tokens/day, qwen/qwen3-32b) was consumed before Premium could run.

## What Was Done
- Fixed `promote.py` — created `promote_premium.py` to handle Premium MASTER agent not existing yet
- Created `run_premium_only.py` to bypass the broken run_tests.py wrapper
- Identified and documented the run_tests.py wrapper bug (silently ignores --agent flag)
- Updated FAILURES.md, REFERENCE.md, TASKS.md on GitHub
- Updated auto-memory with all learnings

## Critical Bug Discovered: run_tests.py --agent flag is BROKEN
**Root cause:** `run_tests.py` is a wrapper hardcoded to run STANDARD TESTING SUITE first, then Premium.
The `--agent premium` flag is silently ignored by the wrapper's sequence selection logic.
Only the underlying `tools/agentic-test-fix.py` engine respects the flag.

**Impact:** Entire day's TPD budget wasted on two Standard runs. Premium never ran.

**Fix created:** `C:\Users\danie\syntharra-tests\run_premium_only.py`
- Downloads agentic-test-fix.py from GitHub
- Sets credentials as env vars
- Runs: `python <tmpfile> --agent premium`
- Bypasses run_tests.py entirely

## Other Bugs Fixed
- `promote.py` 404 on Premium MASTER: agent doesn't exist yet in Retell
  - Fix: `promote_premium.py` creates it via POST /create-agent on first run

## Errors Hit But Not Resolved
- Slack send_message: "Internal Server Error" on all channels/DMs (read works, send broken)
  - Affects all automated notifications
  - Workaround: Gmail draft as fallback

## Files Updated on GitHub
- `docs/FAILURES.md` — new entry for run_tests.py wrapper bug
- `docs/REFERENCE.md` — ⚠️ Known Script Gotchas section, run_premium_only.py + promote_premium.py added, Groq TPD model corrected
- `docs/TASKS.md` — Premium test task updated with correct script, Slack fix added to P1

## Files Created Locally (C:\Users\danie\syntharra-tests\)
- `run_premium_only.py` — correct way to run Premium test
- `promote_premium.py` — correct way to promote Premium TESTING → MASTER

## Next Steps
1. After midnight UTC (Groq TPD resets): `python C:\Users\danie\syntharra-tests\run_premium_only.py`
2. Check `tests/results/` for timestamped Premium JSON result
3. If ≥95/108: `python C:\Users\danie\syntharra-tests\promote_premium.py` (dry run first, then `--live`)
4. Fix Slack send_message broken state

## Mandatory Reflection
1. **What did I get wrong?** Recommended `run_tests.py --agent premium` without reading the wrapper to verify the flag was respected. Assumed it worked.
2. **What assumption was incorrect?** That wrapper scripts pass CLI flags through to the underlying engine. They don't always. run_tests.py has hardcoded sequence logic.
3. **What would I do differently?** Read any wrapper script before recommending it. Verify flag handling with a --dry-run or by inspecting the code.
4. **What pattern emerged?** Always grep or read wrapper scripts for how they handle the --agent / flag arguments before recommending them. A flag that the underlying tool supports may not be passed through by the wrapper.
5. **What was added to learnings?** agentic_testing_learnings.md items 7, 8, 9. New feedback memory: feedback_run_tests_wrapper.md.
6. **Did I do anything unverified?** Yes — assumed run_tests.py respected --agent. Should have verified before recommending it twice.
