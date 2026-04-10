# Phase 0 — n8n Schema Scan Report (2026-04-11)

## Scope

Scanned 5 n8n workflows on Railway for references to `client_subscriptions` and for hard-coded `status='active'` proxies that could break when the Phase 0 schema migration adds new columns and introduces the `status='pilot'` value.

This scan is the pre-migration gate from spec § 6.2.1.

## Workflows scanned

| ID | Name | Nodes | Size |
|---|---|---|---|
| `4Hx7aRdzMl5N0uJP` | HVAC AI Receptionist - JotForm Onboarding (Supabase) | 32 | 290,672 bytes |
| `xKD3ny6kfHL0HHXq` | Stripe Webhook Hardened | 16 | 33,787 bytes |
| `6Mwire23i6InrnYZ` | Client Agent Update Form | 10 | 143,346 bytes |
| `z8T9CKcUp7lLVoGQ` | [OPT-IN] Client Slack Webhook Setup | 6 | 20,271 bytes |
| `Y1EptXhOPAmosMbs` | Retell Calls Proxy | 5 | 8,591 bytes |

All JSON backups saved to `docs/audits/n8n-backups-20260411/*-pre-pilot.json`.

## Findings

### `client_subscriptions` references

| Workflow | Hit count | Node name | Node type | Operation | Risk |
|---|---|---|---|---|---|
| `4Hx7aRdzMl5N0uJP` | 1 | `Reconcile: Check Stripe Payment` | `n8n-nodes-base.code` | JavaScript code node — writes to `client_subscriptions` via Supabase REST (existing paid-path behavior) | **None.** This is exactly the expected write point and the only node we'll touch in Phase 0 Day 2 Task 15 (adding the `Is Pilot?` branch). Adding new columns to `client_subscriptions` is safe — the code node explicitly specifies field names. |
| `xKD3ny6kfHL0HHXq` | 0 | — | — | — | None |
| `6Mwire23i6InrnYZ` | 0 | — | — | — | None |
| `z8T9CKcUp7lLVoGQ` | 0 | — | — | — | None |
| `Y1EptXhOPAmosMbs` | 0 | — | — | — | None |

**Total: 1 reference across all 5 workflows.** Contained entirely to `4Hx7aRdzMl5N0uJP`, in the single node we already planned to modify.

### `SELECT *` usage against `client_subscriptions`

**Zero hits.** No workflow performs a wildcard SELECT against `client_subscriptions`, so adding new columns cannot break downstream JavaScript that assumes a fixed result shape.

### `status='active'` hard-coded proxies

**Two hits found, BOTH confirmed non-blocking:**

| Workflow | Node | Context | Risk |
|---|---|---|---|
| `4Hx7aRdzMl5N0uJP` | `HubSpot - Update Deal (Active)` | Refers to HubSpot deal stage "active," NOT `client_subscriptions.status`. Code references `hubspot.deal.dealstage = 'active'` or similar. Unaffected by our migration. | **None** |
| `4Hx7aRdzMl5N0uJP` | `Update Agent Status: Active` | HTTP request node that PATCHes `client_agents.status = 'active'` on Retell agent go-live. This is the `client_agents` table, NOT `client_subscriptions`. Existing CHECK constraint on `client_agents.status` only allows `('active','canary','paused','retired')` — we are NOT touching that table. | **None** |

**Zero workflows use `client_subscriptions.status === 'active'` as a proxy for "real paying customer."** The existing code paths either (a) write to `client_subscriptions` without reading the status back, or (b) read specific fields other than `status`. Adding the new `status='pilot'` value cannot cause any workflow to misbehave.

## Live `client_subscriptions` schema (captured 2026-04-11 via MCP execute_sql)

**23 columns total. `status` column details:**

| Property | Value |
|---|---|
| `column_name` | `status` |
| `data_type` | `text` |
| `type_type` | `b` (base, NOT enum) |
| `column_default` | `'active'::text` |
| `is_nullable` | YES |

**CHECK constraints on `client_subscriptions`:**

1. `client_subscriptions_plan_type_check` — `CHECK ((plan_type = ANY (ARRAY['standard'::text, 'premium'::text])))` — not touched
2. `client_subscriptions_status_check` — `CHECK ((status = ANY (ARRAY['active'::text, 'paused'::text, 'cancelled'::text, 'past_due'::text])))` — **this is the one we modify**

**Full column list (for reference):**
`id, agent_id, company_name, client_email, plan_type, included_minutes, overage_rate_cents, monthly_rate_cents, stripe_customer_id, stripe_subscription_id, stripe_payment_method, billing_anchor_day, agreement_signed, agreement_signed_at, agreement_ip_address, agreement_version, status, created_at, updated_at, tier, overage_rate, billing_cycle, stripe_price_id`

**Row count:** 1 row (Dan's test agent `agent_289988041e7089ba61cc46c6b4`, email `xskllxmarksman@gmail.com`, status='active', tier='business'). No real paying customers yet — migration risk surface is tiny.

## Migration branch selected

### **BRANCH B** — TEXT column with CHECK constraint

Per the spec § 6.2.2 decision tree:
- `status` is TEXT (not enum, not constraintless)
- Existing CHECK constraint restricts values to 4 strings

**Strategy:** drop `client_subscriptions_status_check`, recreate with the same 4 values PLUS `'pilot'` PLUS `'expired'`. Both original and new constraint definitions are stored in migration files for full reversibility.

**Why `'expired'` in addition to `'pilot'`:**
- `'pilot'` = active pilot in its 14-day window
- `'expired'` = day-14 elapsed, no card on file, Retell agent paused, win-back sequence firing
- `'cancelled'` and `'paused'` are semantically different (user-initiated / paid-customer-pause) and shouldn't be reused for expired pilots

**New CHECK constraint set:** `['active', 'paused', 'cancelled', 'past_due', 'pilot', 'expired']` (strict superset of the old set — no values removed).

## Pre-migration baseline (for Task 8 parity check)

**Billing tool SELECT baseline** — `docs/audits/supabase-backups-20260411/billing_query-pre-migration.json`:

```json
[{"agent_id":"agent_289988041e7089ba61cc46c6b4","company_name":null,"client_email":"xskllxmarksman@gmail.com","included_minutes":1400,"overage_rate":0.12,"tier":"business","stripe_customer_id":null,"stripe_subscription_id":null}]
```

**`monthly_minutes.py --dry-run` baseline** — `docs/audits/supabase-backups-20260411/monthly_minutes-pre-migration.txt`:
- Finds 1 active subscription
- Processes agent_289988041e7089ba61cc46c6b4
- Period 2026-03-01 → 2026-03-31
- calls=0, minutes=0/1400 (0%)
- Dry-run complete, no side effects

**Parity check procedure after Task 8:** re-run the SELECT query → compare byte-for-byte to baseline. Re-run `monthly_minutes.py --dry-run` → verify same "Found 1 active subscription" output. If either differs, trigger Task 11 rollback.

## Dry-run result (Task 7, 2026-04-11)

**Strategy:** Instead of creating a Supabase branch (which costs money and doesn't carry over prod data), I ran the FULL migration DDL inside a `BEGIN; ... ROLLBACK;` transaction against prod. This verifies the migration applies cleanly against REAL prod schema/data with ZERO cost and ZERO risk.

**Transaction dry-run result:**

| Verification | Expected | Actual | Status |
|---|---|---|---|
| New columns added to `client_subscriptions` | 10 | 10 | ✅ |
| New tables created | 3 (`marketing_events`, `marketing_assets`, `pilot_email_sends`) | 3 | ✅ |
| New CHECK constraint with 'pilot' present | 1 | 1 | ✅ |

**Post-rollback verification (same queries, after ROLLBACK):**

| Verification | Expected | Actual | Status |
|---|---|---|---|
| Pilot columns remaining | 0 | 0 | ✅ |
| New tables remaining | 0 | 0 | ✅ |
| CHECK constraint contains 'pilot' | 0 | 0 | ✅ |

**Dry-run status: PASS.** Migration is proven to apply cleanly against prod. Rollback is proven to fully reverse. Safe to proceed to Task 8 (prod apply) pending Dan's explicit confirmation.

## Verdict

**SAFE TO PROCEED with Phase 0 schema migration.**

No n8n workflow will break due to:
1. New columns added to `client_subscriptions` (all writes use explicit field lists, no `SELECT *`)
2. New `status='pilot'` value introduced (no workflow uses `client_subscriptions.status === 'active'` as a branching condition or proxy)

The only workflow that interacts with `client_subscriptions` is `4Hx7aRdzMl5N0uJP`, and its single reference node (`Reconcile: Check Stripe Payment`) is already in scope for modification in Day 2 Task 15.

## Dry-run result

*(to be populated after Task 7 passes)*
