# Go-Live Checklist

> Hold all items here until first paying client lands. Check off each item when done.
> Verified by: Dan manually + smoke test call on MASTER.

---

## Blockers (must resolve before charging anyone)

- [ ] **Stripe live mode** — add live secret key to vault, swap test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` for live equivalent. See TASKS.md P1.
- [ ] **MASTER phone number bound** — `+18129944371` must be bound to MASTER agent in Retell dashboard (Manage > Phone Numbers). ⚠️ Dan action required.
- [ ] **Test call on MASTER** — dial `+18129944371`, confirm: code-node flow end-to-end, `is_lead`/`urgency`/`is_spam` custom analysis fields populate, Brevo email lands in lead inbox, Slack fan-out skipped cleanly when no webhook present.
- [ ] **Stripe webhook signature verification** — `Verify Stripe Signature` node is bypassed (test-only). Before go-live: set `NODE_FUNCTION_ALLOW_BUILTIN=crypto` in Railway n8n env vars, then restore full HMAC verification in workflow `xKD3ny6kfHL0HHXq`. Secret already in vault (`Stripe / webhook_signing_secret`).

---

## Ready (wire in when first client lands)

- [x] **Client-update form** — `https://n8n.syntharra.com/webhook/client-update` live with Syntharra branding (matches Slack setup page). "Update My Settings" button in dashboard header links to it with agentId pre-filled. Dashboard SHA `8f3640813fccd2047268a011f4fa91b69d2badad`.
- [ ] **Telnyx SMS** — waiting on Telnyx AI evaluation approval. Once approved: replace `SMS Stub (Telnyx TODO)` node in HVAC Call Processor with real Telnyx HTTP node.
- [ ] **Weekly client report cron** — `tools/weekly_client_report.py` written and tested. Deploy once second client lands (firing with one client is pointless). See §Cron Setup below.
- [ ] **Monthly billing cron** — `tools/monthly_minutes.py`. Reads Retell calls, calculates overage per tier, charges Stripe at client's plan rate, sends usage email. See §Cron Setup below.
- [ ] **Usage alert cron** — `tools/usage_alert.py`. Daily mid-month 80%/100% usage emails, tier-aware rate per client. See §Cron Setup below.

---

## Cron Setup — Railway (deploy when first client lands)

All three billing scripts are ready. Deploy them as Railway Cron services from the
`Syntharra/syntharra-automations` repo. The `railway.toml` at repo root handles build config.

### Services to create in Railway

| Railway service name | Start command | Cron schedule | When to deploy |
|---|---|---|---|
| `syntharra-usage-alert` | `python tools/usage_alert.py` | `0 8 * * *` | First live client |
| `syntharra-monthly-billing` | `python tools/monthly_minutes.py` | `0 9 2 * *` | First live client |
| `syntharra-weekly-report` | `TZ=America/New_York python tools/weekly_client_report.py --tz America/New_York` | `0 18 * * 0` | Second live client |

**Schedule notes:**
- Usage alert: **daily 08:00 UTC** — checks month-to-date, sends at 80%/100% once each
- Monthly billing: **2nd of month 09:00 UTC** — not 1st, to give Retell time to finalise last-day calls
- Weekly report: **Sunday 18:00 local** — replicate with other `--tz` values as clients expand to new time zones

### Steps to create each service

1. Railway dashboard → New Service → GitHub repo → `Syntharra/syntharra-automations`
2. Set **Service Type** to **Cron Job**
3. Set **Cron Schedule** (see table above)
4. Set **Start Command** (see table above)
5. Add environment variables (see §Env Vars below)
6. Deploy — Railway will run it on schedule, exit cleanly, retry on failure

### Env vars required (set in Railway service → Variables)

Fetch all values from `syntharra_vault` in Supabase. All three services need:

| Env var | Vault lookup |
|---|---|
| `SUPABASE_URL` | `https://hgheyqwnrcvwtgngqdnq.supabase.co` (hardcoded) |
| `SUPABASE_SERVICE_KEY` | `service_name='Supabase', key_type='service_role_key'` |
| `RETELL_API_KEY` | `service_name='Retell AI', key_type='api_key'` |
| `BREVO_API_KEY` | `service_name='Brevo', key_type='api_key'` |
| `STRIPE_SECRET_KEY` | `service_name='Stripe', key_type='secret_key_test'` → swap for `secret_key_live` at go-live |

`syntharra-weekly-report` does not need `STRIPE_SECRET_KEY`.

### Smoke test before first real billing run

```bash
# From local machine with env vars exported:
python tools/usage_alert.py --dry-run
python tools/monthly_minutes.py --dry-run --month YYYY-MM
```

Both scripts are fully idempotent — a double-run skips already-processed records.
`monthly_billing_snapshot` guards against duplicate Stripe charges.

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
