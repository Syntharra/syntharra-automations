# Syntharra — Stripe
> Load when: working on Stripe, checkout, billing, pricing

## Status: TEST MODE ⚠️
Checkout server: `syntharra-checkout-production.up.railway.app`
Signing secret: `whsec_D7eMVF0vdm2KRrVkZLzrhTihYeMbloQO`
Webhook ID: `we_1TEJXzECS71NQsk8eOMIs8JE`
Webhook event: `checkout.session.completed`

## Products
| Plan | Product ID |
|---|---|
| Standard | `prod_UC0hZtntx3VEg2` |
| Premium | `prod_UC0mYC90fSItcq` |

## Prices (TEST MODE)
| Plan | Billing | Price | ID |
|---|---|---|---|
| Standard | Monthly | $497/mo | `price_1TDckaECS71NQsk8DdNsWy1o` |
| Standard | Annual | $414/mo | `price_1TDckiECS71NQsk8fqDio8pw` |
| Standard | Setup | $1,499 | `price_1TEKKrECS71NQsk8Mw3Z8CoC` |
| Premium | Monthly | $997/mo | `price_1TDclGECS71NQsk8OoLoMV0q` |
| Premium | Annual | $831/mo | `price_1TDclPECS71NQsk8S9bAPGoJ` |
| Premium | Setup | $2,499 | `price_1TEKKvECS71NQsk8vWGjHLUP` |

## Coupons (TEST MODE — same code names in live mode, IDs will change)
| Code | ID | Discount |
|---|---|---|
| FOUNDING-STANDARD | `gzp8vnD7` | $1,499 off once |
| FOUNDING-PREMIUM | `RsOnUuo4` | $2,499 off once |
| CLOSER-250 | `mGTTQZOw` | $250 off once |
| CLOSER-500 | `GJiRoaMY` | $500 off once |
| CLOSER-750 | `fUzLNIgz` | $750 off once |
| CLOSER-1000 | `3wraC3tQ` | $1,000 off once |

## Go-Live Checklist
1. Activate Stripe account
2. Switch to live mode
3. Recreate all products, prices, coupons (same names — IDs will change)
4. Recreate webhook in live mode
5. Update Railway env `STRIPE_SECRET_KEY` → `sk_live_`
6. Update n8n webhook signing secret

## Known Rules
- `invoice_creation` is incompatible with `mode: 'subscription'` — subscriptions auto-create invoices
- `allow_promotion_codes: true` already in server.js
