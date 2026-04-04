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
