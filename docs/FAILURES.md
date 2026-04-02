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
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | core_flow run1: 47% pass rate | Loop detection not working; routing to wrong node on repeat questions | Loop fix + prompt tightening applied to TESTING agent | syntharra-retell |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | pricing_traps run1: 50% pass rate | Agent gave vague pricing answers instead of firm $497/$997 | Pricing rules made explicit in prompt | syntharra-retell |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | core_flow run2: 13% pass rate | Rate limited by OpenAI — not an agent failure | Evaluator notes: ignore this run | — |
| 2026-04-02 | Security | Retell API key hardcoded in 4 public Python files | Key committed directly in e2e-test.py, auto-fix-loop.py, simulator.py, e2e-test-premium.py | Replaced with `os.environ.get("RETELL_KEY", "")` in all 4 files | — |
| 2026-04-02 | Security | Retell API key hardcoded in public AGENTS.md context file | Key written inline in docs/context/AGENTS.md (public repo) | Replaced with vault lookup instruction | — |
| 2026-04-02 | Security | Stripe webhook signing secret in public STRIPE.md | `whsec_...` committed to public repo | Replaced with vault lookup instruction | — |
| 2026-04-02 | Security | GitHub token hardcoded in ops-monitor/CLAUDE.md | Token written inline (private repo, but bad practice) | Replaced with Railway env var reference | — |
| 2026-04-02 | Evaluator | Transfer scenarios scored as FAIL | Evaluator couldn't detect transfer in text sim | Fixed: evaluator now accepts "agent initiated transfer" as PASS | e2e-hvac-standard |

---

## Patterns (updated as log grows)
- Rate limit runs: always check OpenAI quota before running full simulator batches
- Transfer scenarios: confirm evaluator is using latest scoring logic before any run
