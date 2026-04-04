# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Restructured. Reference data moved to REFERENCE.md. Marketing moved to MARKETING.md.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### Premium HVAC — IN PROGRESS 🔧
- [ ] Fix 6 core_flow failures on Premium TESTING flow
- [ ] Run remaining 6 simulator groups (personalities → info_collection → pricing_traps → edge_cases → boundary_safety → premium_specific)
- [ ] Target 95%+ across all groups, then promote TESTING → MASTER
- Simulator ready: `tools/openai-agent-simulator-premium.py` — see REFERENCE.md for run command

### Standard HVAC — Go-Live Gate
- [ ] 3–5 live smoke calls to +18129944371
- [ ] Unpause ops-monitor
- [ ] Set SMS_ENABLED=true
- All testing complete: 80/80 ✅ | 75/75 ✅ | 20/20 ✅

### Marketing — see docs/MARKETING.md
- [ ] Build n8n workflows for 6 new blueprint agents
- [ ] Set up Supabase tables for expanded agent architecture

### Retell Enhancement Sprint — POST-PREMIUM-PROMOTION ⏸️
> DO NOT START until Premium TESTING agent hits 95%+ and is promoted to MASTER
- [ ] Create new TESTING agents for Standard and Premium (separate from existing MASTER and current TESTING)
- [ ] Add Extract Dynamic Variable node to Standard flow (after nonemergency_leadcapture, before Ending)
- [ ] Add Extract Dynamic Variable node to Premium flow (same position)
- [ ] Add Code node (phone number format validation) to Standard + Premium flows
- [ ] Configure post_call_analysis_data on both MASTER agents via API (replace GPT extraction)
- [ ] Simplify Standard call processor (Kg576YtPM9yEacKn) — remove GPT node, map Retell webhook fields direct to Supabase
- [ ] Simplify Premium call processor (STQ4Gt3rH8ptlvMi) — same, remove GPT + JSON flattening node
- [ ] Update E2E tests to match new call processor field mapping
- [ ] Re-run Standard E2E after all changes to verify before go-live
- Reference prompt: docs/prompts/retell-enhancement-sprint.md

### Housekeeping
- [ ] Label 1 active unlabelled n8n workflow: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)
- [ ] Review 9 inactive duplicate workflows when convenient

---

## Completed This Sprint
- Standard HVAC: ALL TESTING ✅
- Premium E2E: 89/89 ✅
- HubSpot CRM: LIVE ✅
- Marketing Blueprint (APEX): DELIVERED ✅
- Cowork Marketing Plugin: DELIVERED ✅
