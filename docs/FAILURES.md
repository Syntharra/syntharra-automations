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
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | core_flow run1: 47% pass rate | Loop detection not working; routing to wrong node on repeat questions | Loop fix + prompt tightening applied to TESTING agent | syntharra-retell |
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
| 2026-04-02 | GitHub API | Used `/orgs/{org}/repos` endpoint — returned 404 for org accounts | GitHub org accounts use `/user/repos?affiliation=owner,organization_member` — the org repos endpoint requires the token to be an org member, not just an org-level token | Always use `/user/repos?affiliation=owner,organization_member` to list all accessible repos | syntharra-infrastructure |
| 2026-04-02 | Agent Simulator | pricing_traps run1: 50% pass rate | Agent gave vague pricing answers instead of firm $497/$997 | Pricing rules made explicit in prompt | syntharra-retell |
| 2026-04-02 | Skills | Skills in /mnt went stale when repo was updated — required manual re-upload | Claude.ai project skills (/mnt) have no API — only uploadable via UI | Eliminated /mnt entirely — skills now fetched direct from GitHub at session start | CLAUDE.md |
| 2026-04-02 | Skills | Downloading `skills/{name}/SKILL.md` saved as `SKILL.md` — no skill name in filename, caused confusion in Claude.ai uploads (skill 1, skill 2, skill 3) | GitHub raw download uses the filename, not the folder name | Restructured to flat `skills/{name}-SKILL.md` — download now gives correct name automatically | CLAUDE.md |
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
| 2026-04-03 | Railway API | Railway token returned Not Authorized on GraphQL /v2 endpoint | Token stored in vault was a project-scoped token, not a personal account token. Railway personal tokens are created at Account Settings → API Tokens, not inside a project | Updated vault with new token. Railway dashboard pause is a manual fallback for service management | syntharra-infrastructure |
| 2026-04-03 | HubSpot integration | n8n workflows had no HubSpot nodes — all client data was siloed in Supabase only | Admin dashboard was removed; HubSpot CRM adopted as replacement. Workflows had never had CRM output | Added HubSpot upsert/deal/note nodes to 5 workflows. All non-blocking (try/catch) so HubSpot errors never break pipeline | syntharra-hubspot |

---
### 2026-04-03 | Agent Simulator | core_flow failures (runs 3–8)

**What failed:** core_flow group 53% → 100% over 6 runs
**Root causes & fixes:**
1. Close language — Sophie paraphrased "someone will be in touch" instead of scripted "I've scheduled a callback." Fix: explicit SCRIPTED WORDS instruction in leadcapture mandatory final step.
2. Emergency routing — verify_emergency step 5 routed no-heat directly to lead capture without offering transfer. Fix: added extreme-urgency detection (freezing/elderly/dangerous = offer transfer; matter-of-fact cold = high-priority lead capture).
3. Wrong number — Sophie dismissed with "we only handle HVAC." Fix: added WRONG NUMBER branch to identify_call_node with redirect to Google/411.
4. Callback probe — Sophie asked "anything specific?" after caller said "just a general callback." Fix: MINIMAL INFO RULE in leadcapture.
5. Out-of-area re-ask bug — Sophie re-asked name/number already collected when address was out of area. Fix: "only collect REMAINING details" rule in SERVICE AREA section.
6. Urgency assessment order — evaluator wanted system-status question BEFORE safety check. Fix: restored 2-step sequence (is system completely down? → any burning/gas smell?).
**Skill updated:** syntharra-retell-SKILL.md (see prompt engineering notes section)

---
### 2026-04-03 | Agent Simulator | personalities group — global prompt too long

**What failed:** personalities 47% in both run1 and run2 despite adding personality section to global prompt
**Root cause:** Global prompt now ~37k chars. Personality instructions appended at END are below the model's effective attention window. Instructions not followed.
**Fix (pending):** Move personality handling INTO node-leadcapture instruction text where it will be in active context during info collection.
**Skill updated:** N/A — fix not yet applied
| 2026-04-03 | Jotform Monitor | HTTP 429 — Jotform API Unreachable (CRITICAL alert) | Monitor fetched each form's submissions twice per run (staleness loop + orphan detection loop) → doubled API calls, hit Jotform rate limit | Cache formSubmissions in first pass, reuse in orphan block — 3 calls/run instead of 5 | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | Railway Checkout status 'unknown' (WARNING alert fires every 5 min) | Railway GQL API changed: `input:` filter deprecated in 2025-Q4; also transient states (DEPLOYING/BUILDING) treated as failures | Updated query to use `where: { serviceId: { equals: ... } }` + `orderBy: CREATED_AT DESC`; TRANSIENT states now suppressed | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | Railway query returned 'unknown' even after first fix attempt | `where:`/`orderBy:` args don't exist in Railway GQL schema. Real schema uses `input:` (correct) but `first:1` without status filter returns oldest deployment (REMOVED), not newest | Add `status: { notIn: [REMOVED, REMOVING, SKIPPED] }` to input — `first:1` then reliably returns most recent active deployment. Verified live returns SUCCESS | syntharra-infrastructure |
| 2026-04-03 | Infrastructure Monitor | RAILWAY_TOKEN not set as env var on ops monitor service | Token was in Supabase vault but never injected into Railway ops monitor service variables | Set via Railway GraphQL `variableUpsert` mutation directly — no manual dashboard step needed | syntharra-infrastructure |
| 2026-04-03 | Jotform Monitor | HTTP 429 persisted after first fix (duplicate calls removed) | /user ping itself counted against rate limit quota — already rate-limited from burst, /user is redundant when form fetches confirm connectivity | Removed /user ping entirely; first successful form fetch = connected; 429 now bails with WARNING not CRITICAL | syntharra-infrastructure |
| 2026-04-03 | PDF build | Logo rendering broken — icon too far from wordmark, left-aligned not centred | ReportLab Table ALIGN centres the wrapper but not inner content; must use canvas.drawCentredString with manual x calculation | Rewrote on_page() to use canvas API directly with measured string widths | yes — syntharra-email |
| 2026-04-03 | PDF build | Attempted logo fix produced different PDF layout entirely | build_final.py diverged from original structure; cover page changed | Kept all original content, only stripped logo/icon references | no |
| 2026-04-03 | GitHub API | Archiving file failed with "sha wasn't supplied" | File already existed in archive from partial first attempt; need SHA to overwrite | Checked existence first, supplied SHA on retry | no |
| 2026-04-03 | Jotform Monitor | 429 persisted — reported as 'still erroring' | Quota burned by burst E2E testing earlier same day (resets midnight UTC, ~2hrs away). Independently: backup poller was running every 15min = 192 API calls/day headroom consumed faster during test days | Changed backup poll interval 15min → 60min (48 calls/day); added graceful 429 skip-and-retry logic in code node | syntharra-infrastructure |
