# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — Full pipeline audit + test hygiene complete. 90/90 E2E ✅.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### E2E Test — Extend for new fields
- [ ] Add q72/q68/q69/q73 fields to E2E test Jotform payload
- [ ] Add Supabase assertions for greeting_style, after_hours_transfer, separate_emergency_phone

### Premium Pipeline — TESTING ONLY (no MASTER agent exists yet)
- [ ] Complete Premium agent testing — must reach 95%+ pass rate before MASTER promotion
- [ ] Fix bookable_job_types mapping in Premium onboarding workflow
- [ ] Run Premium E2E test (102/106 was last result — 3 known infra + 1 bookable_job_types)
- [ ] Verify Premium onboarding email matches Standard quality
- [ ] Only after all above: promote Premium TESTING → MASTER

### Retell Enhancement Sprint — Phase 8 pending
- [ ] Phase 4B: DAN TASK — 5 alerting rules + 5 analytics charts in Retell dashboard
- [ ] Phase 8: Dan review → apply DEMO config to Premium TESTING → MASTER promotion

### Post-Launch
- [ ] Update onboarding workflows: set fallback_number = lead_phone on new client phone provision
- [ ] Telnyx SMS: post-call confirmation SMS via n8n (pending Telnyx approval)
- [ ] 3-5 live smoke calls to +18129944371

### Housekeeping
- [ ] Label unlabelled n8n workflow: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)

### Marketing — see docs/MARKETING.md
- [ ] Build n8n workflows for 6 new blueprint agents
- [ ] Set up Supabase tables for expanded agent architecture

---

## Completed
- Full Jotform → Parse → Supabase field audit ✅ (2026-04-04)
- Fixed 4 missing Jotform fields: q68, q69, q72, q73 ✅
- Fixed transfer number priority using q69 gate ✅
- Fixed email builder field names (twilio_number, transfer_phone) ✅
- Purged all Polar Peak references from E2E test ✅
- Universal suppression gate (timestamp pattern) ✅
- Jotform Backup Polling: added Stripe gate, updated test patterns ✅
- Standard E2E: 90/90 ✅ (2026-04-04 22:05 UTC)
- Onboarding email: full onboarding pack ✅
- HubSpot: Update Deal (Active) wired into onboarding ✅
- Junk cleanup: HVAC Company rows purged (1741 deleted) ✅
