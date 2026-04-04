# Syntharra — Tasks & Continuity
> Updated: 2026-04-05 — Premium E2E 106/106 ✅. bookable_job_types fix applied.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## Open Work

### E2E Test — Extend for new fields
- [ ] Add q72/q68/q69/q73 fields to E2E test Jotform payload
- [ ] Add Supabase assertions for greeting_style, after_hours_transfer, separate_emergency_phone

### Premium Pipeline — TESTING ONLY (no MASTER agent exists yet)
- [x] Fix bookable_job_types mapping in Premium onboarding workflow ✅ (2026-04-05)
- [x] Run Premium E2E test — 106/106 ✅ (2026-04-05)
- [ ] Complete Premium agent scenario testing (simulator) — must reach 95%+ pass rate
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
