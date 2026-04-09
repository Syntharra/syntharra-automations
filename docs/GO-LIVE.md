# Go-Live Checklist

> Hold all items here until first paying client lands. Check off each item when done.
> Verified by: Dan manually + smoke test call on MASTER.

---

## Blockers (must resolve before charging anyone)

- [ ] **Stripe live mode** — add live secret key to vault, swap test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` for live equivalent. See TASKS.md P1.
- [ ] **MASTER phone number bound** — `+18129944371` must be bound to MASTER agent in Retell dashboard (Manage > Phone Numbers). ⚠️ Dan action required.
- [ ] **Test call on MASTER** — dial `+18129944371`, confirm: code-node flow end-to-end, `is_lead`/`urgency`/`is_spam` custom analysis fields populate, Brevo email lands in lead inbox, Slack fan-out skipped cleanly when no webhook present.

---

## Ready (wire in when first client lands)

- [x] **Client-update form** — `https://n8n.syntharra.com/webhook/client-update` live with Syntharra branding (matches Slack setup page). "Update My Settings" button in dashboard header links to it with agentId pre-filled. Dashboard SHA `8f3640813fccd2047268a011f4fa91b69d2badad`.
- [ ] **Telnyx SMS** — waiting on Telnyx AI evaluation approval. Once approved: replace `SMS Stub (Telnyx TODO)` node in HVAC Call Processor with real Telnyx HTTP node.
- [ ] **Weekly client report cron** — `tools/weekly_client_report.py` is written and tested. Deploy cron (`TZ=America/New_York python tools/weekly_client_report.py --tz America/New_York` Sunday 18:00) once second client lands. Firing into the void with one client is fine but pointless.
- [ ] **Monthly minutes cron** — `tools/monthly_minutes.py` replaces `z1DNTjvTDAkExsX8` (archived). Deploy 1st-of-month cron once live clients exist.
- [ ] **Usage alert cron** — `tools/usage_alert.py` written 2026-04-09. Deploy daily cron once live clients exist.

---

## Dashboard — client-update button ✅ DONE (2026-04-09)

"Update My Settings" violet button added to `dashboard.html` header. Hidden until a valid `agentId` is present in URL. Opens `https://n8n.syntharra.com/form/client-update?agentId=<agent_id>` in new tab. SHA `121430c096cc132334a476196a2b7015af101d05`.

**Future:** wire n8n form to read `agentId` URL param and pre-populate the Agent ID field so clients don't have to type it.

---

## Post-launch (first 30 days)

- [ ] Rotate dashboard password from `syntharra2024` to something stronger — update in `dashboard.html` and give new password to client.
- [ ] Deploy weekly report cron once second client lands.
- [ ] Confirm HubSpot deal moves to "Active" stage on first real onboarding.
- [ ] Verify `monthly_billing_snapshot` writes cleanly on first billing cycle.
