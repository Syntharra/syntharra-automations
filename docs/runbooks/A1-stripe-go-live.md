# A1 — Stripe Go-Live Runbook
> Target repo path: docs/runbooks/A1-stripe-go-live.md
> Use when: Dan has activated Stripe and is ready to flip to live mode.
> Estimated execution: 30 min once `sk_live_` is in hand.

## Pre-flight (Dan only)
- [ ] Stripe account fully activated
- [ ] Live mode toggle ON
- [ ] `sk_live_...` generated and shared with Claude securely
- [ ] Real card available for $1 smoke test

## Execution

### 1. Dry-run migration
```bash
export STRIPE_TEST_KEY=sk_test_...
export STRIPE_LIVE_KEY=sk_live_...
python tools/stripe_live_migration.py --dry-run
```
Expect: 2 products, 6 prices, 6 coupons, 1 webhook to create. Eyeball before continuing.

### 2. Execute
```bash
python tools/stripe_live_migration.py --execute
```
**Capture the webhook signing secret immediately** — Stripe shows it once.

### 3. Store secrets in vault
```sql
UPDATE syntharra_vault SET key_value = 'sk_live_...'
WHERE service_name = 'Stripe' AND key_type = 'secret_key_live';

INSERT INTO syntharra_vault (service_name, key_type, key_value)
VALUES ('stripe_webhook_secret_live', 'signing_secret', 'whsec_...')
ON CONFLICT (service_name, key_type) DO UPDATE SET key_value = EXCLUDED.key_value;
```

### 4. Update Railway env on syntharra-checkout (service e3df3e6d)
- `STRIPE_SECRET_KEY` → `sk_live_...`
- `STRIPE_WEBHOOK_SECRET` → `whsec_...`
Auto-redeploys ~60s.

### 5. Update n8n Stripe webhook handler credential
Repoint `STRIPE_WEBHOOK_SECRET` credential to live signing secret.

### 6. Patch docs/context/STRIPE.md
Replace TEST table with new live IDs. Status → LIVE ✅.

### 7. End-to-end smoke test
1. Open `https://checkout.syntharra.com/?plan=standard&billing=monthly`
2. Real card, complete checkout
3. Verify: Stripe shows live charge → n8n webhook fires → HubSpot deal in "Paid Client" → welcome email received
4. **Refund the $1**

## Done when
Live charge succeeded, webhook fired, HubSpot deal created, refund processed, STRIPE.md updated.

## Rollback
Revert `STRIPE_SECRET_KEY` on Railway to test key. Live objects can stay (harmless).
