# Railway cron deploy: pilot_lifecycle.py

> Daily state-machine runner for Syntharra Phase 0 pilots. Runs at **00:00 UTC daily**. Mirror of the existing `monthly_minutes.py` / `usage_alert.py` Railway cron pattern (see `tools/deploy_billing_crons.py`).

## What the cron does

On each run, `tools/pilot_lifecycle.py` queries `client_subscriptions WHERE pilot_mode=true` (see `tools/pilot_lifecycle.py:341-348`) and walks every pilot row through the 14-day state machine:

1. **Day 3 / 7 / 12** — sends the corresponding Brevo engagement template (`pilot-day-3`, `pilot-day-7`, `pilot-day-12`) and emits a `pilot_day_{N}_sent` marketing event. Engagement block at `tools/pilot_lifecycle.py:504-526`.
2. **Day 14 terminal transition** (`tools/pilot_lifecycle.py:528-539`):
   - If `payment_method_added_at IS NOT NULL` → `convert_pilot_to_paid()` creates a Stripe subscription on `STRIPE_HVAC_STANDARD_PRICE_ID`, PATCHes the row to `status='active'`, `pilot_mode=false`, sends `pilot-converted`.
   - Otherwise → `expire_pilot()` PATCHes `status='expired'`, attempts a Retell agent pause via `PATCH /update-agent/{id}` with `agent_level_dynamic_variables: {pilot_expired: "true"}`, sends `pilot-expired`.
3. **Day 16 / 30** — if `status='expired'`, sends `pilot-winback-16` or `pilot-winback-30`. Winback block at `tools/pilot_lifecycle.py:542-562`.

Every email is gated on a `pilot_email_sends` row (unique `(client_agent_id, email_key)` — see `already_sent()` at `tools/pilot_lifecycle.py:300-307` and `record_email_send()` at `310-321`). **Running the cron twice on the same day is safe** — duplicate sends are suppressed by the dedup row, and the terminal state transitions are guarded by the `status='pilot'` check at line 510/529.

## Schedule

- **Cron expression:** `0 0 * * *` (daily at 00:00 UTC)
- **Timezone:** UTC (Railway cron is UTC-only — no `TZ=` prefix needed since the state machine uses UTC day boundaries via `datetime.now(timezone.utc)` at `tools/pilot_lifecycle.py:121-122`)
- **Why 00:00 UTC:** the docstring at `tools/pilot_lifecycle.py:6-7` specifies this. Running at day-boundary UTC means "day N" rollovers happen consistently regardless of client timezone, and the first engagement email fires at the earliest possible wall-clock moment after a pilot's calendar day increments.
- **Why not collide with `monthly_minutes.py` (09:00 UTC) or `usage_alert.py` (08:00 UTC):** 9-hour gap, zero overlap.

## Env vars required

All values live in `syntharra_vault` (Supabase table). See `tools/pilot_lifecycle.py:34-39` for the authoritative list.

| Env var | Required | Vault row (`service_name`, `key_type`) | Notes |
|---|---|---|---|
| `SUPABASE_URL` | REQUIRED | hardcoded: `https://hgheyqwnrcvwtgngqdnq.supabase.co` | Same value as billing crons. |
| `SUPABASE_SERVICE_KEY` | REQUIRED | `Supabase`, `service_role_key` | Service-role JWT. |
| `BREVO_API_KEY` | REQUIRED | `Brevo`, `api_key` | For transactional email sends. |
| `STRIPE_SECRET_KEY` | REQUIRED | `Stripe`, `secret_key_test` (Phase 0) → `secret_key_live` at Stripe flip | `sk_test_...` during Phase 0. Update when Stripe live mode unblocks — **also update `STRIPE_HVAC_STANDARD_PRICE_ID` constant at `tools/pilot_lifecycle.py:68`**. |
| `RETELL_API_KEY` | REQUIRED | `Retell AI`, `api_key` | Used by `expire_pilot()` to PATCH the agent's dynamic variables. |

**No Telnyx env vars are read by this script.** `pilot_lifecycle.py` does not import or reference Telnyx anywhere (verified via grep — 0 matches). Telnyx provisioning is gated in the n8n onboarding workflow `4Hx7aRdzMl5N0uJP`, not here. Related safety note: the `expire_pilot()` Retell-pause call at `tools/pilot_lifecycle.py:465-470` is wrapped in a `try/except RuntimeError` that logs a `[WARN]` and continues — so even if the Retell `update-agent` shape turns out to be wrong (TODO at lines 461-464), the email send and status PATCH still complete. **However: there is no explicit "skip if Retell key missing" guard** — if `RETELL_API_KEY` is absent, `env()` at line 97-101 will `sys.exit()` at startup. Treat `RETELL_API_KEY` as hard-required for this cron.

## Pre-deploy checklist

- [ ] Verify unit tests pass: `python tools/test_pilot_lifecycle.py` (14 tests — see `tools/test_pilot_lifecycle.py:176-298`)
- [ ] Verify `--dry-run` exits 0 locally against prod Supabase:
      ```
      export SUPABASE_URL=https://hgheyqwnrcvwtgngqdnq.supabase.co
      export SUPABASE_SERVICE_KEY=$(python tools/fetch_vault.py "Supabase" service_role_key)
      export BREVO_API_KEY=$(python tools/fetch_vault.py "Brevo" api_key)
      export STRIPE_SECRET_KEY=$(python tools/fetch_vault.py "Stripe" secret_key_test)
      export RETELL_API_KEY=$(python tools/fetch_vault.py "Retell AI" api_key)
      python tools/pilot_lifecycle.py --dry-run
      ```
- [ ] Verify `BREVO_TEMPLATE_IDS` at `tools/pilot_lifecycle.py:76-86` still matches live Brevo IDs — spot-check by listing templates with `tools/upload_brevo_templates.py` (idempotent find-by-name) or the Brevo dashboard.
- [ ] Verify `STRIPE_HVAC_STANDARD_PRICE_ID` at `tools/pilot_lifecycle.py:68` is current (still test-mode `price_1TKxruECS71NQsk8yspZnj2B` as of 2026-04-11 per STATE.md — will change at Stripe live flip).
- [ ] Confirm no active pilots would hit a terminal transition in the first 24h post-deploy. Query: `SELECT agent_id, pilot_started_at, (CURRENT_DATE - pilot_started_at::date) AS days_in FROM client_subscriptions WHERE pilot_mode=true` — flag any with `days_in >= 13`.
- [ ] Confirm `pilot_email_sends` table exists in prod Supabase (created in Day 3 schema migration — verify with `SELECT count(*) FROM pilot_email_sends`).

## Railway deploy steps

> **I could not find a repo-specific pattern that describes Railway's exact cron service config shape for a brand-new service creation.** The existing `railway.toml` (9-line header comment) documents that each cron is created as a *separate Railway service pointing to this repo* with a start command and cron schedule, and `tools/deploy_billing_crons.py:163-197` shows the GraphQL mutations used for the billing crons (`serviceCreate` + `serviceInstanceUpdate` with `startCommand` + `cronSchedule` + `restartPolicyType: NEVER`). The cleanest path is to reuse `deploy_billing_crons.py` as a template and add a fourth service entry. **Dan, please confirm the preferred approach before running.**

### Option A (recommended): extend `tools/deploy_billing_crons.py`

This mirrors the exact pattern the 3 existing billing crons were deployed with.

1. Add a 4th entry to the `CRON_SERVICES` list at `tools/deploy_billing_crons.py:37-59`:
   ```python
   {
       "name":     "syntharra-pilot-lifecycle",
       "command":  "python tools/pilot_lifecycle.py",
       "schedule": "0 0 * * *",
       "desc":     "Daily 00:00 UTC — Phase 0 pilot state machine (day 3/7/12/14/16/30)",
       "needs_stripe": True,
   },
   ```
2. Extend `fetch_env_vars()` at `tools/deploy_billing_crons.py:105-124` to include `RETELL_API_KEY` in the lookup set (the billing crons all need it, but the existing filter only adds it because `Retell AI` is already in the `or=(...)` — **verify**: line 112 shows `Retell AI` IS already fetched, so no change needed). The existing `env_vars` dict at line 118-124 already passes `RETELL_API_KEY`, so the pilot-lifecycle service will inherit it automatically.
3. Run dry-run: `RAILWAY_TOKEN=<fresh-token> python tools/deploy_billing_crons.py --dry-run` and confirm the output shows a 4th entry `syntharra-pilot-lifecycle`.
4. Run live: `RAILWAY_TOKEN=<fresh-token> python tools/deploy_billing_crons.py`. The `service_exists()` check at line 148-160 makes this idempotent — the existing 3 services will be skipped.
5. Verify in Railway dashboard → project `bf04f61c-84d9-4c99-bd54-497d3f357070` that `syntharra-pilot-lifecycle` appears with `cronSchedule=0 0 * * *` and `startCommand=python tools/pilot_lifecycle.py`.

### Option B (manual via Railway dashboard)

Use this if the GraphQL deploy path fails or you prefer the UI.

1. Open [Railway dashboard](https://railway.com/project/bf04f61c-84d9-4c99-bd54-497d3f357070) → Syntharra project.
2. Click **+ New Service** → **GitHub Repo** → select `Syntharra/syntharra-automations`, branch `main`.
3. Name the service `syntharra-pilot-lifecycle`.
4. **Settings → Deploy:**
   - Start Command: `python tools/pilot_lifecycle.py`
   - Cron Schedule: `0 0 * * *`
   - Restart Policy: **Never**
   - Builder: Nixpacks (auto-detected via `requirements.txt` — see `requirements.txt` which is intentionally empty; stdlib-only).
5. **Variables** tab → add (copy from any of the 3 existing billing cron services):
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `BREVO_API_KEY`
   - `STRIPE_SECRET_KEY`
   - `RETELL_API_KEY`
6. Click **Deploy**. First run will fire at the next 00:00 UTC boundary.

## Verification after first run

1. Railway dashboard → `syntharra-pilot-lifecycle` → **Deployments** → latest → **View Logs**. Expected log lines:
   - `pilot_lifecycle.py — today=YYYY-MM-DD dry_run=False`
   - `Found N pilot row(s) to evaluate.` (or `No pilot rows found.`)
   - Per-row: `[<agent_id>] <company_name> day=N status=pilot` then either action lines (`sent pilot-day-3`, `CONVERTED ...`, `EXPIRED ...`) or `no-op`
   - Final `Summary:` block with action counts
   - `Done.`
2. Verify exit code 0 (Railway shows green checkmark on the deployment).
3. **Idempotency check:** in the Railway dashboard, **Redeploy** the same build to trigger a second immediate run. Expect: zero duplicate sends, all actions show `no-op` (or only new actions if a day boundary crossed). Cross-check `SELECT client_agent_id, email_key, count(*) FROM pilot_email_sends GROUP BY 1,2 HAVING count(*) > 1` — must return zero rows.
4. Spot-check `marketing_events` for the expected `pilot_day_3_sent` / `pilot_day_7_sent` / `pilot_converted` / `pilot_expired` event types with `user_agent='pilot_lifecycle.py'`.

## Rollback plan

If the cron sends a bad email or triggers a bad state transition:

1. **Immediately pause the service** — Railway dashboard → `syntharra-pilot-lifecycle` → Settings → **Pause Service**. Future cron ticks will not fire.
2. **If a bad Stripe subscription was created:** cancel via Stripe dashboard (`sub_...` shown in `client_subscriptions.stripe_subscription_id`) and PATCH the row back to `pilot_mode=true, status='pilot', stripe_subscription_id=NULL`.
3. **If a bad email was sent:** no direct recall possible (Brevo SMTP is fire-and-forget). Send an apology from `daniel@syntharra.com` and insert a `pilot_email_sends` row manually to prevent re-send on the next run.
4. **If a pilot was wrongly expired:** PATCH `status='pilot'` back on the row, and confirm the `pilot_expired` Retell agent-level variable is cleared via `PATCH /update-agent/{id}` with `agent_level_dynamic_variables: {pilot_expired: "false"}`. Check the TODO at `tools/pilot_lifecycle.py:461-464` — the key name may need adjustment.
5. **Root-cause and fix the bug**, bump tests in `tools/test_pilot_lifecycle.py`, redeploy, then unpause the Railway service.

## Related

- `tools/monthly_minutes.py` — existing Railway cron using this pattern (`0 9 2 * *`)
- `tools/usage_alert.py` — existing Railway cron (`0 8 * * *`)
- `tools/weekly_client_report.py` — existing Railway cron (`0 18 * * 0`)
- `tools/deploy_billing_crons.py` — one-shot deployer for the 3 existing billing crons; **extend this for Option A above**
- `tools/pilot_lifecycle.py` — the code this deploys (611 lines)
- `tools/test_pilot_lifecycle.py` — 14 unit tests, all should pass before deploy
- `railway.toml` — Nixpacks builder config, `restartPolicyType = "NEVER"`
- `requirements.txt` — empty-on-purpose (stdlib only); exists so Nixpacks detects Python 3
- `docs/GO-LIVE.md` §Cron Deployment — one-command pattern for billing crons (reference for Option A)
- `docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md` §6.6, §7, §8 — pilot state machine spec
