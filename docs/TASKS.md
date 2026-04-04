# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Retell enhancement sprint redesigned. Premium testing cancelled in favour of combined approach.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### Retell Enhancement Sprint — READY TO EXECUTE 🚀
> Prompt: docs/prompts/retell-enhancement-prompt.md (v2.4, 911 lines)
> Run in: Claude Code
- [ ] Phase 0: Pre-flight + add disconnection_reason/transcript columns (DONE in this session)
- [ ] Phase 1: Sync Standard TESTING to MASTER, create Premium DEMO clone
- [ ] Phase 2: PATCH all Retell features (guardrails, boost keywords, pronunciation, backchannel, reminders, tuning, post_call_analysis, webhook filter)
- [ ] Phase 3: Dan UI — add Extract Dynamic Variable + Code nodes to Standard TESTING + Premium DEMO flows
- [ ] Phase 4A: Configure fallback numbers + geo restrictions on phone number
- [ ] Phase 4B: Dan dashboard — create 5 alerting rules + 5 analytics charts + verify guardrails
- [ ] Phase 5: Update both n8n call processors — remove GPT, map Retell webhook fields to Supabase
- [ ] Phase 6: Test calls on both agents, verify all 49 fields populate correctly
- [ ] Phase 7: Update E2E assertions, run both suites green
- [ ] Phase 8: Dan review → apply DEMO config to Premium TESTING → MASTER promotion

### Post-Enhancement Sprint
- [ ] Update onboarding workflows: set fallback_number = lead_phone on new client phone provision
- [ ] Telnyx SMS: post-call confirmation SMS via n8n (pending Telnyx approval)
- [ ] Update E2E skills + testing skills for new field types and assertions
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
