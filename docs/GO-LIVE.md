# Go-Live Checklist — Syntharra

> **Single source of truth for pre-launch status.**
> Ask Claude: "What's left before we go live?" → Claude reads this file.
> Check items off as they're completed. Do not split tasks across other docs.

_Last updated: 2026-04-10_

---

## Status: PRE-LAUNCH — Test mode. No live billing. No live clients.

---

## 🔴 Hard Blockers (nothing goes live until these are done)

- [ ] **Stripe live mode** — Dan must activate Stripe account, switch to live mode, then:
  1. Recreate 7 prices in live mode: 3 monthly + 3 annual + 1 activation fee (same names, new IDs)
  2. Recreate the Stripe webhook in live mode pointing to `https://n8n.syntharra.com/webhook/stripe`
  3. Add live prices to `syntharra_vault` (same key_type names, e.g. `price_starter_monthly`)
  4. Update n8n Stripe webhook workflow `xKD3ny6kfHL0HHXq` PLANS map with live price IDs
  5. Update Railway n8n env var `STRIPE_SECRET_KEY` → `sk_live_...`
  6. Update `STRIPE_SECRET_KEY` in all 3 billing cron services once deployed (or set to `sk_live_` from the start)

- [ ] **Stripe webhook signature verification** — `Verify Stripe Signature` node is bypassed (test-only). Before go-live:
  1. Set Railway n8n env var `NODE_FUNCTION_ALLOW_BUILTIN=crypto`
  2. Restore full HMAC verification in workflow `xKD3ny6kfHL0HHXq`
  3. Signing secret already in vault: `service_name='Stripe', key_type='webhook_signing_secret'`

- [ ] **MASTER phone number bound** — `+18129944371` must be manually bound to MASTER agent `agent_b46aef9fd327ec60c657b7a30a` in Retell dashboard → Manage → Phone Numbers. ⚠️ Dan action — cannot be automated.

- [ ] **Test call on MASTER** — dial `+18129944371` and confirm all of:
  - Code-node flow runs end-to-end without errors
  - `is_lead` / `urgency` / `is_spam` custom analysis fields populate in Retell call detail
  - Brevo lead email lands in the lead inbox
  - Slack fan-out skips cleanly when no webhook is configured (no error)

---

## 🟡 Deploy on First Client (before charging anyone)

### Telnyx phone chain
- [ ] **Add Telnyx vault entries** — Dan must add to `syntharra_vault`:
  1. `service_name='Telnyx', key_type='api_key'` — from portal.telnyx.com
  2. `service_name='Telnyx', key_type='retell_sip_connection_id'` — from Retell dashboard → Phone Numbers → SIP
  Once added, the 5-node Telnyx chain in onboarding workflow `4Hx7aRdzMl5N0uJP` activates automatically.

### Billing cron services (Railway)
All three scripts are written, tested dry-run, and correct. Deploy via one command — see §Cron Deployment below.

- [ ] **Deploy `syntharra-usage-alert`** — daily 08:00 UTC, mid-month 80%/100% usage alerts at each client's plan rate
- [ ] **Deploy `syntharra-monthly-billing`** — 2nd of month 09:00 UTC, pulls Retell calls → calculates overage → charges Stripe → sends usage email
- [ ] **Deploy `syntharra-weekly-report`** — Sunday 18:00 UTC, branded weekly call stats for each client (part of the $1,000/mo value add)

### Infrastructure
- [ ] **Unpause ops monitor** — Railway service `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`. Paused to prevent test-mode spam.
- [ ] **Set `PRE_LAUNCH_MODE=false`** — in ops monitor `retell.js` Railway env vars.

### Telnyx SMS
- [ ] **Telnyx SMS swap** — waiting on Telnyx AI evaluation approval. Once approved: replace `SMS Stub (Telnyx TODO)` node in HVAC Call Processor `Kg576YtPM9yEacKn` with real Telnyx HTTP node. Stub payload is already built in `Build Payload`.

---

## 🟢 Already Done (for reference, do not re-do)

- [x] **Checkout page** — `syntharra.com/checkout`. 3-tier cards (Starter/Professional/Business), monthly/annual toggle, activation fee on all, Enterprise section, mobile-responsive. SHA `4249ba66`.
- [x] **Stripe test prices** — 6 subscription + 1 activation fee price, all IDs in `syntharra_vault`.
- [x] **Stripe webhook** — `xKD3ny6kfHL0HHXq`. All 6 price IDs mapped, `stripe_payment_data` saved, tier-aware welcome email sent, JotForm link includes `?tier=X`.
- [x] **JotForm tier field** — hidden field `tier` (qid 77) pre-fills from `?tier=X` URL param.
- [x] **Reconcile node** — fetches `stripe_payment_data` by email, PATCHes `client_subscriptions` with correct tier/minutes/overage_rate/overage_rate_cents/billing_cycle.
- [x] **Billing pipeline tier-aware** — all 3 tiers verified 2026-04-10: Starter $0.25/min, Professional $0.18/min, Business $0.12/min throughout usage_alert + monthly_minutes + You're Live email.
- [x] **3 billing bugs fixed** (2026-04-10, commit 8c12711):
  - `monthly_minutes.py` was querying `overage_rate_cents` (default 25¢) not `overage_rate` decimal — would have overcharged Pro/Business
  - Reconcile node wasn't writing `overage_rate_cents` — column stayed at DB default 25
  - `usage_alert.py` was writing `cycle_start`/`cycle_end` (don't exist) — alert flags never persisted, alerts would re-fire daily
- [x] **Telnyx 5-node chain built** — deployed to onboarding workflow `4Hx7aRdzMl5N0uJP` 2026-04-10. Blocked on 2 vault entries (see above).
- [x] **HVAC Call Processor** — lean 8-node fan-out, Syntharra-branded email + Slack + SMS stub. Triggers on `is_lead OR urgency=emergency`.
- [x] **MASTER agent** — `agent_b46aef9fd327ec60c657b7a30a`, 19 nodes, modern code-node arch, published. Re-registered 2026-04-09.
- [x] **Client dashboard** — `syntharra.com/dashboard.html`. Dark mode, sentiment stats, CSV export, demo mode, sparkline, a11y.
- [x] **Client-update form** — `https://n8n.syntharra.com/webhook/client-update`. Branded form for post-onboarding edits.
- [x] **Weekly report script** — `tools/weekly_client_report.py`. Written and tested.
- [x] **Slack workspace** — 7 clean channels, bot token vaulted.

---

## Cron Deployment — One Command

When ready to deploy the billing crons (first client lands):

```bash
# Get a fresh Railway API token from: railway.com → Account Settings → Tokens
RAILWAY_TOKEN=<your-token> python tools/deploy_billing_crons.py --dry-run  # preview first
RAILWAY_TOKEN=<your-token> python tools/deploy_billing_crons.py             # deploy
```

The script (`tools/deploy_billing_crons.py`) reads all env vars directly from `syntharra_vault` and creates all 3 Railway cron services. No manual copy-paste required.

### Env vars set automatically by the script

| Var | Source |
|---|---|
| `SUPABASE_URL` | Hardcoded — `https://hgheyqwnrcvwtgngqdnq.supabase.co` |
| `SUPABASE_SERVICE_KEY` | vault: `Supabase / service_role_key` |
| `RETELL_API_KEY` | vault: `Retell AI / api_key` |
| `BREVO_API_KEY` | vault: `Brevo / api_key` |
| `STRIPE_SECRET_KEY` | vault: `Stripe / secret_key_test` → update to `secret_key_live` after Stripe goes live |

`syntharra-weekly-report` does not receive `STRIPE_SECRET_KEY`.

### Cron schedules

| Service | Schedule | Plain English |
|---|---|---|
| `syntharra-usage-alert` | `0 8 * * *` | Every day at 08:00 UTC |
| `syntharra-monthly-billing` | `0 9 2 * *` | 2nd of every month at 09:00 UTC |
| `syntharra-weekly-report` | `0 18 * * 0` | Every Sunday at 18:00 UTC |

**Why the 2nd?** Gives Retell ~24h to finalise any call records from the last day of the month before we pull totals.

---

## Post-Launch (first 30 days)

- [ ] After first real billing cycle: verify `monthly_billing_snapshot` row written and Stripe invoice created with correct amount.
- [ ] Add more timezone buckets to weekly report cron as clients in new time zones join.
- [ ] Confirm HubSpot deal moves to "Active" stage on first real onboarding.
- [ ] Rotate dashboard password from `syntharra2024` to something stronger — update in `dashboard.html`.
- [ ] Update `STRIPE_SECRET_KEY` in all 3 billing cron Railway services once Stripe switches to live mode.
