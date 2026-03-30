---
name: syntharra-stripe
description: >
  Complete reference for all Syntharra Stripe work — products, prices, coupons, webhooks,
  checkout server, invoices, and the live mode cutover checklist.
  ALWAYS load this skill when: working on Stripe checkout, adding or changing prices or coupons,
  debugging the checkout server, handling Stripe webhooks, setting up invoices, preparing for
  live mode, or any task involving Stripe payments, subscriptions, or billing.
  This is the single source of truth for all Stripe configuration at Syntharra.
---

# Syntharra — Stripe Reference

> ⚠️ Currently in **TEST MODE**. No real payments processed yet.

---

## Credentials

- **Secret key:** query `syntharra_vault` → `service_name = 'stripe_secret'`
- **Webhook signing secret:** query `syntharra_vault` → `service_name = 'stripe_webhook_secret'`
- **Checkout server:** `checkout.syntharra.com`
- **Checkout repo:** `Syntharra/syntharra-checkout` (keep separate from syntharra-automations — never merge)

---

## Products

| Plan | Product ID |
|---|---|
| Standard | `prod_UC0hZtntx3VEg2` |
| Premium | `prod_UC0mYC90fSItcq` |

---

## Price IDs (TEST MODE)

| Plan | Billing | Price ID | Amount |
|---|---|---|---|
| Standard | Monthly | `price_1TDckaECS71NQsk8DdNsWy1o` | $497/mo |
| Standard | Annual | `price_1TDckiECS71NQsk8fqDio8pw` | $414/mo |
| Standard | Setup fee | `price_1TEKKrECS71NQsk8Mw3Z8CoC` | $1,499 |
| Premium | Monthly | `price_1TDclGECS71NQsk8OoLoMV0q` | $997/mo |
| Premium | Annual | `price_1TDclPECS71NQsk8S9bAPGoJ` | $831/mo |
| Premium | Setup fee | `price_1TEKKvECS71NQsk8vWGjHLUP` | $2,499 |

Annual = 2 months free.

---

## Discount Codes (TEST MODE)

> All codes must be recreated in live mode with same names — IDs will change.
> Full doc: `syntharra-automations/docs/discount-codes.md`

| Code | Coupon ID | Discount | Use Case |
|---|---|---|---|
| `FOUNDING-STANDARD` | `gzp8vnD7` | $1,499 off (once) | Waives Standard setup fee |
| `FOUNDING-PREMIUM` | `RsOnUuo4` | $2,499 off (once) | Waives Premium setup fee |
| `CLOSER-250` | `mGTTQZOw` | $250 off (once) | Sales closer |
| `CLOSER-500` | `GJiRoaMY` | $500 off (once) | Sales closer |
| `CLOSER-750` | `fUzLNIgz` | $750 off (once) | Sales closer |
| `CLOSER-1000` | `3wraC3tQ` | $1,000 off (once) | Sales closer |

`allow_promotion_codes: true` is set in `server.js`.

---

## Webhook

| Item | Value |
|---|---|
| URL | `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` |
| Event | `checkout.session.completed` |
| Webhook ID | `we_1TEJXzECS71NQsk8eOMIs8JE` |
| Signing secret | query `syntharra_vault` → `service_name = 'stripe_webhook_secret'` |
| n8n workflow triggered | Stripe Workflow `xKD3ny6kfHL0HHXq` |

---

## Checkout Server (`server.js`)

| Item | Value |
|---|---|
| Repo | `Syntharra/syntharra-checkout` |
| URL | `checkout.syntharra.com` |
| Served from | `public/index.html` |
| Railway service ID | `e3df3e6d-6824-498f-bb4a-fdb6598f7638` |
| Railway env ID | `5303bcf8-43a4-4a95-8e0c-75909094e02e` |

### Key `server.js` settings
- `allow_promotion_codes: true` — discount codes work at checkout
- `invoice_creation` block present — every checkout generates branded invoice PDF
- **`invoice_creation` is incompatible with `mode: 'subscription'`** — subscriptions auto-create invoices; this param is only valid for `mode: 'payment'`. Don't add it to subscription sessions.

### Railway deployment
Railway does NOT always auto-deploy on GitHub push. Trigger manually if needed:
```
POST https://backboard.railway.com/graphql/v2
Authorization: Bearer {railway_token}
mutation { serviceInstanceRedeploy(serviceId: "e3df3e6d-...", environmentId: "5303bcf8-...") }
```

---

## Branded Invoices ✅ (Complete)

- Dashboard branding: Syntharra logo, `#6C63FF`, `#00D4FF`
- Automatic email receipts enabled (successful payments + renewals)
- Invoice footer added
- Logo variant for invoices: `syntharra-logo-swapped-v2.png` (bars purple, "Syntharra" black, "AI SOLUTIONS" purple)

---

## Stripe Workflow (n8n)

**Workflow ID:** `xKD3ny6kfHL0HHXq`

Flow:
```
checkout.session.completed
    ↓
Extract Session Data (JS — builds emailHtml + dynamic Jotform URL)
    ↓
Save to Supabase (stripe_payment_data table)
    ↓
Send Welcome Email (via SMTP2GO)
    ↓
Send Internal Notification → onboarding@syntharra.com
```

### `stripe_payment_data` table fields
`stripe_customer_id`, `subscription_id`, `session_id`, `customer_email`, `customer_name`, `plan_name`, `plan_billing`, `plan_amount`, `minutes`, `setup_fee_price_id`, `payment_status`, `jotform_sent`, `signup_date`

---

## Live Mode Cutover Checklist

When ready to go live — do ALL of these in one session:

- [ ] Activate Stripe account (complete identity verification if not done)
- [ ] Switch dashboard to live mode
- [ ] Recreate all products (Standard, Premium) — same names, new IDs
- [ ] Recreate all prices (6 total) — same amounts, new IDs
- [ ] Recreate all coupons (6 total) — same code names, new IDs
- [ ] Recreate webhook → get new signing secret
- [ ] Update Railway env `STRIPE_SECRET_KEY` → `sk_live_...`
- [ ] Update Railway n8n env with new webhook signing secret
- [ ] Update `syntharra_vault` table: `stripe_secret` + `stripe_webhook_secret` → live values
- [ ] Test a real checkout end-to-end before announcing live

---

---

## 🔑 Syntharra Vault — Credential Access

ALL Syntharra API keys and secrets are stored in the Supabase table `syntharra_vault`.

- **Project URL:** `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- **Table:** `syntharra_vault`
- **Query by:** `service_name` + `key_type` fields → retrieve `key_value`
- **Auth:** Supabase service role key — stored in vault as `service_name = 'Supabase'`, `key_type = 'service_role_key'`
- **NEVER** store keys in skill files, session logs, GitHub, or project memory

### REST Lookup Pattern
```
GET https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/syntharra_vault?service_name=eq.{SERVICE_NAME}&key_type=eq.{KEY_TYPE}&select=key_value
Headers:
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
```

### JavaScript Lookup Pattern (n8n / Node.js)
```javascript
async function getVaultKey(serviceName, keyType) {
  const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.${serviceName}&key_type=eq.${keyType}&select=key_value`,
    { headers: { apikey: SERVICE_ROLE_KEY, Authorization: `Bearer ${SERVICE_ROLE_KEY}` } }
  );
  const data = await res.json();
  return data[0]?.key_value;
}

// Examples:
const retellKey    = await getVaultKey('Retell AI', 'api_key');
const n8nUrl       = await getVaultKey('n8n Railway', 'instance_url');
const stripeMonthly = await getVaultKey('Stripe', 'price_standard_monthly');
```

### Known service_name / key_type Values

| service_name | key_type | What it is |
|---|---|---|
| `n8n Railway` | `instance_url` | `https://n8n.syntharra.com` |
| `n8n Railway` | `api_key` | n8n Railway API key |
| `Retell AI` | `api_key` | Retell API key |
| `Retell AI` | `agent_id_arctic_breeze` | Test HVAC agent ID |
| `Retell AI` | `agent_id_demo_jake` | Demo agent Jake |
| `Retell AI` | `agent_id_demo_sophie` | Demo agent Sophie |
| `Retell AI` | `conversation_flow_id` | Live conversation flow |
| `Retell AI` | `phone_number` | Arctic Breeze phone |
| `Supabase` | `project_url` | Supabase project URL |
| `Supabase` | `service_role_key` | Full admin key |
| `GitHub` | `personal_access_token` | GitHub PAT |
| `Stripe` | `product_id_standard` | Standard product ID |
| `Stripe` | `product_id_premium` | Premium product ID |
| `Stripe` | `price_standard_monthly` | $497/mo price ID |
| `Stripe` | `price_standard_annual` | $414/mo price ID |
| `Stripe` | `price_standard_setup` | $1,499 setup price ID |
| `Stripe` | `price_premium_monthly` | $997/mo price ID |
| `Stripe` | `price_premium_annual` | $831/mo price ID |
| `Stripe` | `price_premium_setup` | $2,499 setup price ID |
| `Stripe` | `coupon_founding_standard` | FOUNDING-STANDARD coupon |
| `Stripe` | `coupon_founding_premium` | FOUNDING-PREMIUM coupon |
| `Stripe` | `webhook_url` | Stripe webhook URL |
| `Stripe` | `webhook_id` | Stripe webhook ID |
| `Jotform` | `api_key` | Jotform API key |
| `Jotform` | `form_id_standard` | Standard onboarding form ID |
| `Jotform` | `form_id_premium` | Premium onboarding form ID |
| `Jotform` | `webhook_standard_new` | Railway n8n webhook URL |
| `SMTP2GO` | `api_key` | SMTP2GO API key |
| `Railway` | `api_token` | Railway API token |
| `Railway` | `project_id` | Syntharra project ID |
| `Railway` | `service_id_n8n` | n8n service ID |
| `Railway` | `service_id_checkout` | Checkout service ID |
| `Railway` | `service_id_ops_monitor` | Ops monitor service ID |

---

## 🔄 Auto-Update Rule

Only update this skill when something **fundamental** changes — not during routine work:
- ✅ New product or price created → add to tables
- ✅ New discount code added → add to coupons table
- ✅ Live mode cutover complete → update all IDs + remove TEST MODE warning
- ✅ Webhook URL changes → update immediately
- ✅ `server.js` gains a new critical pattern → document it
- ❌ Do NOT update for routine checkout page design changes or copy tweaks
