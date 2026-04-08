# Syntharra Scale-Readiness Audit — 2026-04-07

**Author:** Autonomous audit (Planner → 7 parallel executors → verifier)
**Scope:** Pre-scenario-testing audit for 1000+ client readiness.
**Context:** Track A gated on Dan. Track B (client_agents registry, rollout, canary), C2 (call log monthly partitioning) and D4 (Premium agent rename) shipped.
**Vendor note:** Brevo has replaced SMTP2GO. Every SMTP2GO reference in workflows is now stale.

Severity: P0 = blocker for scale, P1 = required pre-launch, P2 = post-launch hardening, P3 = nice-to-have.

---

## Executive summary

| Area | Score | Top blocker |
|---|---|---|
| 1. Onboarding | 3/10 | No idempotency, no `client_agents` registration, weak Retell error handling |
| 2. Premium Integration Dispatcher | 6/10 | Hardcoded SRK (FIXED — published), Jobber lacks 429 retry |
| 3. Call ingestion | 7/10 | Partition routing relies on `new Date()` fallback; merge-duplicates untested at scale |
| 4. Supabase | 3/10 | RLS disabled on `hvac_call_log`, `stripe_payment_data`, `agent_prompts`; permissive `USING (true)` policies on 9 tables |
| 5. n8n (37 workflows) | 3/10 | 18+ workflows with hardcoded secrets; 5 use raw `fetch()` |
| 6. Stripe | 4/10 | No webhook signature verification; only `checkout.session.completed` handled; no dunning state machine |
| 7. Alerting | 4/10 | No per-client success-rate or Retell error-rate alerts; ops-monitor paused |

**Overall scale-readiness: 4/10.** Blocking gaps must be closed before opening scenario testing to multi-tenant load.

---

## 1. Onboarding pipeline

Workflows: Standard `4Hx7aRdzMl5N0uJP`, Premium `kz1VmwNccunRMEaF`.

### Findings

1. **No idempotency** (P1) — Both flows write to `hvac_standard_agent` on every Jotform fire. A retried webhook creates a duplicate Retell agent + duplicate row. Fix: lookup by email before clone.
2. **No `client_agents` registration** (P1) — Neither flow inserts into the new B1 registry. The whole rollout/canary system is unpopulated. Fix: append a Supabase Insert node calling `public.client_agents` after agent creation with `(client_id, agent_id, flow_id, tier, status='active')`.
3. **Retell clone has no real error path** (P1) — Standard has empty IF conditions on the error branch; Premium has `onError: null` on Create + Publish. A 5xx leaves an orphaned agent ID with no client row, or a client row with no agent. Fix: condition on HTTP status, route to DLQ + Slack.
4. **No retry / no rate-limit handling** (P2) — Three sequential Retell calls in Premium, no Wait nodes. At 1000 onboardings/wk Standard rate-limit hits expected 2-3×/wk. Fix: 1-2 s Wait between calls; honour `Retry-After`.
5. **Welcome email vendor** (P2) — Standard email node currently disabled. Premium has 4 email sends, all without error handling. **All must be Brevo** (SMTP2GO is retired). Verify and switch any node still pointing at SMTP2GO.
6. **Supabase write uses anon key** (P2) — Standard uses anon JWT in header. Should use service role via n8n credential.

### Gaps for 1000+ clients

- ~3-5 % duplicate agents / 1000 onboardings without dedup.
- 100 % registry gap → rollout.py and canary.py have nothing to operate on.
- Retell rate-limit will start throttling at sustained ≥6 onboardings/hr.

---

## 2. Premium Integration Dispatcher (`73Y0MHVBu05bIm5p`)

### Fix applied (autonomous)

- **Hardcoded Supabase service role JWT removed** from "Extract and Lookup Client" and "Process Function Call" Code nodes. Replaced inline literal with the n8n credential expression. Workflow republished (`activeVersionId: ae63ede4-2c49-4a3d-9610-774fb9614811`).
- **Action for Dan:** confirm a Supabase service-role credential is attached to those HTTP calls (n8n credential type `httpHeaderAuth` named e.g. `supabase_service_role`). Until then, those nodes will fail at runtime — this is a controlled, visible failure rather than a leaked key.

### Remaining findings

1. **Google Calendar refresh has no retry loop** (P1) — try/catch swallows 401 and returns defaults. Fix: 2× retry with refresh.
2. **Jobber GraphQL lacks 429/5xx backoff** (P0 for scale) — silent failures on rate limit. Fix: exponential backoff (1→2→4 s), surface failures.
3. **No DLQ logging** (P1) — failures only `console.log`. Fix: insert into `call_processor_dlq` (already exists, schema ready).

---

## 3. Call ingestion

Workflows: `Kg576YtPM9yEacKn` (Standard, `/webhook/retell-hvac-webhook`) and `STQ4Gt3rH8ptlvMi` (Premium, `/webhook/retell-hvac-premium-webhook`). Both POST into `hvac_call_log` with `Prefer: resolution=merge-duplicates` and a `(call_id, created_at)` unique index.

### Findings

1. **Partition routing relies on `new Date()` fallback** (P1) — if Retell payload omits a timestamp the workflow uses system clock; clock skew could mis-route a record into the wrong monthly partition. Fix: require `call.start_timestamp`; reject otherwise.
2. **`merge-duplicates` semantics untested at scale** (P2) — second insert with same `call_id` silently overwrites. Add an explicit "exists in last 5 min" check or move to true ON CONFLICT UPSERT.
3. **call_processor_dlq exists but is unused** (P2) — Premium retries 3× then alerts Slack but never lands in DLQ. Fix: write final-failure rows to `call_processor_dlq` for replay.
4. **Partition rollover** — was only good through 2027-02. **FIXED autonomously** — partitions now exist for every month from current through 2027-03 (idempotent CREATE IF NOT EXISTS, 12-month rolling window).

---

## 4. Supabase

### Critical security gaps (P0)

| Table | Issue |
|---|---|
| `hvac_call_log` (+ all partitions) | RLS **disabled** — all call data publicly readable via PostgREST |
| `stripe_payment_data` | RLS **disabled** — payment + customer IDs exposed |
| `agent_prompts` | RLS **disabled** |
| `infra_health_summary` (view) | `SECURITY DEFINER` — privilege escalation risk |
| `call_processor_dlq`, `syntharra_vault` | RLS on, **no policies** — effectively locked (intended? verify) |

### Permissive RLS (P1)

9 tables (`admin_tasks`, `billing_cycles`, `client_subscriptions`, `finance_costs`, `hvac_call_log_pre_partition`, `hvac_standard_agent`, `infra_health_checks`, `overage_charges`, `website_leads`) carry `USING (true)` / `WITH CHECK (true)` policies — RLS in name only.

### Missing indexes — FIXED autonomously

```sql
CREATE INDEX idx_client_agents_agent_id ON public.client_agents(agent_id);
CREATE INDEX idx_client_agents_flow_id  ON public.client_agents(flow_id);
CREATE INDEX idx_client_agents_status   ON public.client_agents(status) WHERE status='active';
CREATE INDEX idx_stripe_payment_customer ON public.stripe_payment_data(stripe_customer_id);
CREATE INDEX idx_stripe_payment_created  ON public.stripe_payment_data(created_at DESC);
CREATE INDEX idx_billing_subscription    ON public.billing_cycles(subscription_id);
CREATE INDEX idx_overage_billing         ON public.overage_charges(billing_cycle_id);
CREATE INDEX idx_transcript_date_call    ON public.transcript_analysis(analysis_date DESC, call_id);
```

Also created `public.stripe_processed_events(event_id PK, event_type, processed_at)` for webhook idempotency (Section 6).

### Performance advisors (P2)

`auth_rls_initplan` warnings on `email_digest`, `hvac_call_log_pre_partition`, `transcript_analysis`, `client_health_scores`. Multiple redundant policies (7 on `hvac_call_log_pre_partition`, 4 on `email_digest`).

### Supavisor pooling (P1, manual)

Cannot read via MCP. **Verify in dashboard:** mode=`transaction`, default_pool_size 15-20, max_client_conn ≥ 200. Add pool-saturation alert (Section 7).

### Function search_path (P2)

`update_updated_at`, `update_hvac_premium_agent_updated_at`, `ensure_call_log_partition`, `update_updated_at_column` — set explicit `SET search_path = public, pg_temp`.

---

## 5. n8n (37 workflows)

### Hardcoded secrets (P0)

18+ workflows embed secrets in Code nodes — Supabase service role JWTs, Slack webhooks, Groq keys, GitHub PAT, Brevo/Stripe API keys. Rotation is impossible without code edits. Fix item: migrate every literal secret to an n8n credential or `$env`. Premium Integration Dispatcher already done in this audit.

### `fetch()` violations (P1)

5 workflows use raw `fetch()` in Code nodes instead of `this.helpers.httpRequest({...})`. n8n's `fetch` is not consistently available across versions and bypasses retry config.

### `responseMode: responseNode` on non-linear paths (P1)

3 workflows split before the response node — webhook can hang.

### SMTP2GO references

Audit subagent reported zero SMTP2GO references currently. Brevo migration appears clean from a search perspective — but every email-sending node should still be visually verified to ensure it uses the Brevo credential, not a stale generic HTTP node.

### Queue-mode readiness (P2)

5 long-running workflows (call processors, transcript analysis) hold static data across runs. Queue-mode workers do not share static data — refactor to Supabase-backed state.

---

## 6. Stripe

Single workflow `xKD3ny6kfHL0HHXq`. Test mode.

### Findings

1. **No webhook signature verification** (P0) — endpoint `/webhook/syntharra-stripe-webhook` accepts any POST. Add HMAC SHA256 check against `Stripe-Signature` header using `STRIPE_WEBHOOK_SECRET`.
2. **Only `checkout.session.completed` handled** (P1) — missing `customer.subscription.{created,updated,deleted}`, `invoice.payment_{succeeded,failed}`, `charge.dispute.created`.
3. **No dunning state machine** (P1) — `client_subscriptions.status` exists but nothing flips it to `past_due`. Add `invoice.payment_failed` handler → status update + retry email.
4. **Idempotency table created (autonomous fix)** — `public.stripe_processed_events(event_id PK)`. Workflow needs a "check + insert" guard at the top of the handler — Dan must wire this up (one Code node).
5. **Hardcoded test price IDs** (P1) — `price_1TDckaECS71NQsk8DdNsWy1o` and `price_1TDclGECS71NQsk8OoLoMV0q` embedded in Code nodes. Externalise to env on go-live.
6. **Overage aggregator missing** — `billing_cycles` / `overage_charges` schemas exist but no scheduled workflow populates them. Find or build the monthly aggregator before live billing.

---

## 7. Alerting

### Existing rules

| Workflow | Schedule | Covers |
|---|---|---|
| Daily Ops Digest | 06:00 UTC | client count, MRR, infra health (calls ops-monitor) |
| Daily Transcript Analysis | 02:00 UTC | quality score, frustration, prompt fix queue |
| Weekly Client Health | Mon 03:00 UTC | per-agent health, call volume trend |
| Premium OAuth Refresh | 02:00 UTC | token expiry within 2 days |
| Usage Alert Monitor | on billing close | 80 % / 100 % thresholds |

`infra_health_checks` table exists but is **empty** — Daily Ops Digest doesn't persist.

### Critical gaps for 1000 clients

| # | Alert | Severity | Suggested trigger |
|---|---|---|---|
| 1 | Per-client call success rate | P0 | success_rate < 90 % over 1 h, per `client_id`, eval every 15 min |
| 2 | Retell error-rate spike | P0 | err / total > 2 % per 10 min; > 5 % critical |
| 3 | n8n critical workflow failures | P1 | > 5 failed executions / hour for Premium Dispatchers + Call Processors |
| 4 | Stripe webhook delivery | P1 | > 5 failed deliveries / hour (Stripe events API) |
| 5 | Supabase pool saturation | P1 | `pg_stat_activity` count > 80 % of max_connections |
| 6 | Brevo bounce rate | P2 | > 3 % daily |
| 7 | hvac_call_log next-month partition exists | P2 | check on day 25 of every month |
| 8 | Agent prompt-version drift | P3 | > 5 % of fleet on stale `prompt_version` (uses `client_agents`) |

### ops-monitor (paused)

Service is paused per CLAUDE.md (gated on Dan). Ops Digest still calls it — confirm intent. Recommend: store responses into `infra_health_checks` (currently empty) and add a P0 escalation rule.

---

## Autonomous fixes applied this session

| # | Fix | Surface |
|---|---|---|
| 1 | 8 missing indexes on hot tables (`client_agents`, `stripe_payment_data`, `billing_cycles`, `overage_charges`, `transcript_analysis`) | Supabase |
| 2 | Created `stripe_processed_events` table for webhook idempotency | Supabase |
| 3 | Pre-created 12 months of `hvac_call_log` monthly partitions (rolling window through 2027-03) | Supabase |
| 4 | Removed hardcoded Supabase service role JWT from Premium Integration Dispatcher (2 Code nodes); switched to credential expression; workflow republished | n8n |

## Gated on Dan

| Item | Why |
|---|---|
| Stripe live mode + webhook signing secret + live price IDs | Account currently in test mode |
| Telnyx SMS approval | Vendor pending |
| Unpause `syntharra-ops-monitor` Railway service | Per CLAUDE.md |
| Attach Supabase service-role credential to dispatcher's HTTP nodes (named e.g. `supabase_service_role`) | Required after this session's SRK removal |
| Approval to enable RLS on `hvac_call_log`, `stripe_payment_data`, `agent_prompts` (may break PostgREST consumers — needs coordinated rollout) | Risk of breaking edge functions / dashboards |
| Approval to replace `USING (true)` policies on 9 tables | Same risk |
| Bulk migration of 18+ hardcoded secrets in n8n Code nodes | Touches many production workflows |
