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
> DO NOT START until Premium TESTING → MASTER promotion is complete
> Full implementation prompt: docs/prompts/retell-enhancement-prompt.md
- [ ] Phase 0: Pre-flight checks — verify both MASTER agents healthy, backup to retell-agents/
- [ ] Phase 1: Sync TESTING agents to clean MASTER copies (PATCH in place, never recreate)
- [ ] Phase 2: Configure post_call_analysis_data via API on both TESTING agents (replaces GPT)
- [ ] Phase 3: Dan adds Extract Dynamic Variable nodes in UI (Standard + Premium TESTING flows)
- [ ] Phase 4: Dan adds Code node (phone validation) in UI (both flows)
- [ ] Phase 5: Check SMS eligibility on +18129944371 → add SMS confirmation node to Premium only
- [ ] Phase 6: Simplify n8n call processors — remove GPT, map Retell webhook fields to Supabase
- [ ] Phase 7: Re-run E2E — Standard first, then Premium — both must be green
- [ ] Phase 8: Dan review → explicit go-ahead → promote changes to MASTER
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
