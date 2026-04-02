# Syntharra — Failure Log & Self-Teaching Record
> Updated whenever a test fails, a bug is found, or a fix is applied.
> Claude reads this at session start to avoid repeating known mistakes.
> Format: date | area | what failed | root cause | fix applied | skill updated

## How to use this file
- Claude appends a row every time something breaks and is fixed
- Claude scans this before working in any area that has prior failures
- Skill files get updated after any fix — this log is the audit trail

---

## Failure Log

| Date | Area | What Failed | Root Cause | Fix Applied | Skill Updated |
|------|------|-------------|------------|-------------|---------------|
| 2026-04-02 | Agent Simulator | core_flow run1: 47% pass rate | Loop detection not working; routing to wrong node on repeat questions | Loop fix + prompt tightening applied to TESTING agent | syntharra-retell |
| 2026-04-02 | Agent Simulator | pricing_traps run1: 50% pass rate | Agent gave vague pricing answers instead of firm $497/$997 | Pricing rules made explicit in prompt | syntharra-retell |
| 2026-04-02 | Agent Simulator | core_flow run2: 13% pass rate | Rate limited by OpenAI — not an agent failure | Evaluator notes: ignore this run | — |
| 2026-04-02 | Evaluator | Transfer scenarios scored as FAIL | Evaluator couldn't detect transfer in text sim | Fixed: evaluator now accepts "agent initiated transfer" as PASS | e2e-hvac-standard |

---

## Patterns (updated as log grows)
- Rate limit runs: always check OpenAI quota before running full simulator batches
- Transfer scenarios: confirm evaluator is using latest scoring logic before any run
