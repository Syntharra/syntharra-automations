# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Standard E2E 90/90 ✅. Onboarding email fixed. Slack fixed.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### Retell Enhancement Sprint — Phase 8 pending
- [ ] Phase 4B: DAN TASK — 5 alerting rules + 5 analytics charts in Retell dashboard
- [ ] Phase 8: Dan review → apply DEMO config to Premium TESTING → MASTER promotion

### Premium Pipeline
- [ ] Run Premium E2E test (102/106 was last result — 3 known infra + 1 bookable_job_types)
- [ ] Fix bookable_job_types mapping in Premium onboarding workflow
- [ ] Verify Premium onboarding email (similar to Standard pack — check ONBOARDING-PACK.md)

### Post-Launch
- [ ] Update onboarding workflows: set fallback_number = lead_phone on new client phone provision
- [ ] Telnyx SMS: post-call confirmation SMS via n8n (pending Telnyx approval)
- [ ] 3-5 live smoke calls to +18129944371

### Housekeeping
- [ ] Label unlabelled n8n workflow: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)
- [ ] Clean up junk Retell agents/flows created by double-execution bug (now fixed)

### Marketing — see docs/MARKETING.md
- [ ] Build n8n workflows for 6 new blueprint agents
- [ ] Set up Supabase tables for expanded agent architecture

---

## Completed
- Standard E2E: 90/90 ✅ (2026-04-04 20:21 UTC)
- Onboarding email: replaced placeholder with full onboarding pack ✅
- Internal email suppression: universal test gate on all email nodes ✅
- Slack: Agent Live: fixed syntax error + execution mode ✅
- Validate: Token Budget loop removed (was creating junk agents) ✅
- Call forwarding PDF: hosted at syntharra.com/syntharra-call-forwarding-guide.pdf ✅
- Artifacts folder: onboarding pack saved, outdated templates archived ✅
- HubSpot: Update Deal (Active) wired into onboarding happy path ✅
- HubSpot Code nodes: rewritten from $env to direct API key ✅
- Junk cleanup: 364 agents, 375 flows, 353 Supabase rows ✅
