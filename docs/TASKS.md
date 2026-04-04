# Syntharra — Tasks & Continuity
> Updated: 2026-04-04 — E2E tests fixed to 90/90 Standard. Critical email/Slack issues remain.
> Keep this file focused on open work only. Target: under 40 lines.

## Status: PRE-LAUNCH | Stripe TEST MODE

---

## URGENT — Fix Before Next E2E Run

### Emails still sending during E2E tests
- [ ] Audit ALL SMTP2GO send nodes across all workflows — list every node that calls smtp2go API
- [ ] Add universal test suppression gate to EVERY email send node (not just internal ones)
- [ ] The gate must match ALL test company patterns: Polar Peak, FrostKing, HVAC Company, CoolBreeze, V\d+
- [ ] Verify: run E2E test and confirm ZERO emails sent (check SMTP2GO dashboard)

### Slack notifications not working
- [ ] Verify Slack bot token is valid: POST test message to #ops-alerts
- [ ] If token works: test each Slack Code node individually (Standard CP, Premium CP, Standard Onboarding, Premium Onboarding)
- [ ] If token doesn't work: get fresh token from Slack app settings, update all Code nodes + vault

### Premium E2E test
- [ ] Run Premium E2E test (102/106 was last result — 3 known infra + 1 bookable_job_types)
- [ ] Fix bookable_job_types mapping in Premium onboarding workflow

---

## Open Work

### Retell Enhancement Sprint — Phase 8 pending
- [ ] Phase 4B: DAN TASK — 5 alerting rules + 5 analytics charts in Retell dashboard
- [ ] Phase 8: Dan review → apply DEMO config to Premium TESTING → MASTER promotion

### Post-Enhancement Sprint
- [ ] Update onboarding workflows: set fallback_number = lead_phone on new client phone provision
- [ ] Telnyx SMS: post-call confirmation SMS via n8n (pending Telnyx approval)
- [ ] 3-5 live smoke calls to +18129944371

### Skill Updates (overdue from this session)
- [ ] Update e2e-hvac-standard-SKILL.md — new polling logic, Supabase fallback, 90/90 status
- [ ] Update e2e-hvac-premium-SKILL.md — same polling fixes
- [ ] Update syntharra-infrastructure-SKILL.md — n8n $env blocking, node renaming rules
- [ ] Update syntharra-slack-SKILL.md — direct token pattern (not $env)
- [ ] Update syntharra-email-SKILL.md — universal test suppression gate requirement

### Marketing — see docs/MARKETING.md
- [ ] Build n8n workflows for 6 new blueprint agents
- [ ] Set up Supabase tables for expanded agent architecture

### Housekeeping
- [ ] Label 1 active unlabelled n8n workflow: `Google Keep → Groq → Slack To-Do List` (`5wxgBfJL7QeNP2ab`)

---

## Completed
- Standard E2E: 90/90 ✅ (2026-04-04)
- HubSpot Code nodes: rewritten from $env to direct API key ✅
- Junk cleanup: 364 agents, 375 flows, 353 Supabase rows ✅
- Jotform Backup Polling: fixed table + column + test exclusion + Slack alert ✅
