# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Fully agentic setup complete. One structural gap remains (see LEARNING.md)

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — `python3 shared/e2e-test-premium.py`

## Agent Simulator
- Script: `tools/openai-agent-simulator.py`
- Cost: ~$0.002/scenario | Model: gpt-4o-mini
- OpenAI key: in vault (service_name='OpenAI', key_type='api_key')
- Run: `GITHUB_TOKEN=... RETELL_KEY=... python3 tools/openai-agent-simulator.py --key sk-... --group core_flow`
- Groups: core_flow(15), personalities(15), info_collection(15), pricing_traps(8), edge_cases(15), boundary_safety(12)
- Results → tests/results/

## Simulator Results So Far
| Run | Group | Pass Rate | Notes |
|---|---|---|---|
| pricing-traps-run1 | pricing_traps | 50% (4/8) | Pricing rules tightened after |
| core-flow-run1 | core_flow | 47% (7/15) | Loop + routing fixes applied after |
| core-flow-run2 | core_flow | 13% (2/15) | Rate limited — ignore |

## Key Finding — Evaluator Fixed
Failures #2, #6, #12 were evaluator scoring transfers as FAIL (can't complete in text sim).
Fixed: evaluator now accepts "agent initiated transfer" as PASS.
Sophie's actual behaviour on these scenarios was CORRECT.

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 Loop+prompt fixes live |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Prompt fixes live |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Completed This Session
- [x] Archived 26 stale docs/ files → docs/archive/
- [x] Created docs/FAILURES.md — agentic failure log
- [x] Created docs/LEARNING.md — self-improvement protocol  
- [x] Created docs/DECISIONS.md — architectural decision log (pre-seeded)
- [x] Fixed CLAUDE.md skill names (hvac-standard/premium → e2e-hvac-standard/premium)
- [x] Added syntharra-client-dashboard to CLAUDE.md skill table
- [x] Added Tools section to CLAUDE.md (simulator, auto-fix-loop, etc.)
- [x] Added freshness dates to 11 repo skills missing them
- [x] Backed up syntharra-client-dashboard from /mnt to repo
- [x] Flagged: 5 repo skills not in /mnt (need uploading to Claude.ai project)
- [x] Audited all 8 repos (previously only 2 visible)
- [x] SECURITY: Removed hardcoded Retell key from 4 Python files (public repo)
- [x] SECURITY: Removed Retell key from AGENTS.md (public repo)
- [x] SECURITY: Removed Stripe webhook secret from STRIPE.md (public repo)
- [x] SECURITY: Removed GitHub token from ops-monitor/CLAUDE.md
- [x] Added service URLs to CLAUDE.md for all repos
- [x] Added Security section to DECISIONS.md
- [x] Backed up syntharra-client-dashboard to repo
- [x] Removed 3 duplicate skills (admin-dashboard, e2e-test, docs/skills/syntharra-social-leads misplaced)
- [x] Removed stale n8n-backup-2026-03-28 (superseded by 03-30)
- [x] Removed duplicate newsletter template (old n8n.cloud URL syntax)
- [x] Removed 2 stale root-level docs
- [x] Logged GitHub API endpoint mistake in FAILURES.md + infrastructure skill
- [x] Updated LEARNING.md with full agentic status
- [x] Created docs/FAILURES.md — agentic failure log
- [x] Created docs/LEARNING.md — self-improvement protocol
- [x] Updated CLAUDE.md to load FAILURES.md every session

## Dan Action Required (for full agentic setup)
- [ ] Re-upload updated skills to Claude.ai project settings (repo versions are newer):
  - 🔴 syntharra-admin (+137 lines: env vars, auto-update rules)
  - 🔴 syntharra-ops (+132 lines: vault key list, auto-update rules)
  - 🔴 ai-receptionist (+41 lines: Retell publish API, output checklist)
  - 🟡 syntharra-infrastructure (+7 lines: correct GitHub API endpoint)
  - 🟡 syntharra-retell, syntharra-stripe, syntharra-email, syntharra-brand, syntharra-website (+2-4 lines each: freshness dates)
  - ➕ Upload new skills not yet in Claude.ai: hvac-standard, hvac-premium, syntharra-testing, syntharra-marketing-manager, syntharra-social-leads
  HOW: Claude.ai → this project → top-right menu → Settings → scroll to Skills → remove old → upload new SKILL.md from repo
- [ ] Upload to Claude.ai project settings: hvac-standard, hvac-premium, syntharra-testing, syntharra-marketing-manager, syntharra-social-leads
- [ ] Move syntharra-checkout/env Stripe key to Railway env var before go-live

## Open Action Items
- [ ] Run core_flow group again (evaluator now fixed) — expect 80%+
- [ ] Run all 6 groups, fix failures, target 90%+ overall
- [ ] Promote Standard TESTING → MASTER once verified
- [ ] Wire +18129944371 to Standard Template agent
- [ ] Live smoke test (Dan available ~2 days)
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium

## Pre-Go-Live Security
- [ ] Move `syntharra-checkout/env` sk_test_ key to Railway env vars before switching to sk_live_

## Blocked
- Live smoke test — Dan unavailable ~2 days
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
