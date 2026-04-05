# Open Tasks

> Under 40 lines. Reference data → REFERENCE.md. Marketing → MARKETING.md.

## Priority 1 — Pre-Launch Blockers
- [ ] Build `tools/agentic-test-fix.py` — core agentic test + self-fix engine (plan: docs/AGENTIC-TESTING-PLAN.md)
- [ ] Run agentic test suite on Standard TESTING (target: 85/91+)
- [ ] Run agentic test suite on Premium TESTING (target: 95/108+)
- [ ] Promote TESTING → MASTER agents after both suites green
- [ ] Build retell-integration-dispatch n8n workflow for Premium booking tool calls
- [ ] Publish both TESTING agents (is_published still false — needs Dan confirmation)
- [ ] Activate Stripe LIVE mode — recreate products/prices/coupons/webhook

## Priority 2 — Post-Launch
- [ ] Set up nightly regression test (n8n scheduled or cron)
- [ ] Telnyx SMS approval (pending)
- [ ] Unpause syntharra-ops-monitor on Railway
- [ ] Fix HubSpot Code node in call processors ($env access denied) — rewrite to HTTP Request

## Recently Completed (2026-04-05)
- [x] Subagent component library — 19 components created and deployed
- [x] Standard flow: 15→20 nodes, all subagent components wired
- [x] Premium flow: 20→26 nodes, all subagent components wired
- [x] Both E2E pipeline tests passing (Standard 93/93, Premium 106/106)
- [x] Simulator scripts updated — fetch component instructions + edge routing
- [x] 13 new test scenarios added (95→108 total)
- [x] All 3 E2E skill files updated for subagent architecture
- [x] AGENTIC-TESTING-PLAN.md designed and published
