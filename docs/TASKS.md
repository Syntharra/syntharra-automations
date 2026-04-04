# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Retell enhancement sprint. Phases 0-7 complete. Phase 8 awaiting Dan approval.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### Retell Enhancement Sprint — READY TO EXECUTE 🚀
> Prompt: docs/prompts/retell-enhancement-prompt.md (v2.4, 911 lines)
> Run in: Claude Code
- [x] Phase 0: Pre-flight ✅
- [x] Phase 1: Premium DEMO clone → `agent_80d6270ab39ed3169f997cb035` / `conversation_flow_82e70e18fef3` ✅
- [x] Phase 2: All Retell features configured on both agents ✅
- [x] Phase 3: Code node added via API ✅ | Extract Dynamic Variable = DAN UI TASK
- [x] Phase 4A: Phone fallback set to +18563630633, pinned to v20 ✅
- [ ] Phase 4B: DAN TASK — 5 alerting rules + 5 analytics charts in Retell dashboard
- [x] Phase 5: Both n8n call processors rewired — GPT/Groq removed, Retell fields mapped directly ✅
- [x] Phase 6: Simulated webhook tests — Standard 37/37 ✅, Premium 40/40 ✅
- [x] Phase 7: E2E tests passing — Standard 87/90 ✅, Premium 103/106 ✅ (3 known infra failures each)
- [ ] Phase 8: Dan review → apply DEMO config to Premium TESTING → MASTER promotion

### Post-Enhancement Sprint
- [ ] Update onboarding workflows: set fallback_number = lead_phone on new client phone provision
- [ ] Telnyx SMS: post-call confirmation SMS via n8n (pending Telnyx approval)
- [x] Update E2E skills + testing skills for new field types and assertions ✅
- [ ] 3-5 live smoke calls to +18129944371

### Next Sprint — Flow Improvements
- [ ] Global nodes: add "callback request" handler to both flows (catches it from any node)
- [ ] Components: package lead capture, emergency detection, callback as reusable sub-flows
- [ ] Logic Split nodes: evaluate for cleaner urgent/emergency routing
- [ ] Finetune examples: add per-node after collecting real call data

### Marketing — see docs/MARKETING.md
- [ ] Build n8n workflows for 6 new blueprint agents
- [ ] Set up Supabase tables for expanded agent architecture

### Housekeeping
- [ ] Label 1 active unlabelled n8n workflow: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)

---

## Completed
- Standard HVAC testing: 80/80 ✅ | 75/75 ✅ | 20/20 ✅
- Premium E2E: 89/89 ✅
- HubSpot CRM: LIVE ✅
- Marketing Blueprint (APEX): DELIVERED ✅
- Supabase cleanup: dropped agent_test_results + view, added 2 columns ✅
- Retell Enhancement Sprint prompt: v2.4 designed and verified ✅
