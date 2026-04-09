# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

- ~~**Re-register MASTER agent in Retell**~~ — ✅ Done 2026-04-09. MASTER: `agent_b46aef9fd327ec60c657b7a30a` / `conversation_flow_19684fe03b61`. TESTING: `agent_41e9758d8dc956843110e29a25` / `conversation_flow_bc8bb3565dbf`. All docs, vault, client_agents, hooks updated. ⚠️ **Dan must bind `+18129944371` to new MASTER in Retell dashboard** (Manage > Phone Numbers).
- **Build `tools/usage_alert.py`** — ✅ Done 2026-04-09. Run daily: `python tools/usage_alert.py`. Reads billing_cycles, queries Retell list-calls, sends 80%/100% Brevo alerts, sets flags idempotently. Deploy on cron once live clients exist.
- **Extract prompt compiler + ship client-update CLI** — the single biggest unlock for the edit-after-onboarding lifecycle. Build order:
  1. `tools/prompt_compiler.py` — Python port of the n8n `Build Retell Prompt` 769-line JS code node. Single function `compile(client_row: dict) -> {global_prompt, flow_fields, agent_fields}`. Takes a `hvac_standard_agent` row, returns what to PATCH into Retell. **Parity-test against a snapshot of current MASTER's compiled prompt** — Python output must byte-match the JS output given the same input row before it's trusted.
  2. `tools/update_client_agent.py` — CLI: `python tools/update_client_agent.py --agent_id agent_xxx --set lead_phone="555-1234" --set current_promotion="Spring tune-up $79" [--dry-run] [--email]`. Flow: read Supabase → apply --set → compile → diff vs live Retell → PATCH `update-conversation-flow` + `update-agent` → publish → write row back → print one-line undo command.
  3. **Do NOT touch the n8n onboarding workflow yet.** Onboarding keeps using its own JS compiler until the Python one has been used in production for real updates and proven correct. Converge in a later session.
  4. Test on a fresh clone of MASTER (`retell-iac/scripts/register.py` to spawn one), not on MASTER itself. Smoke with a harmless change (`--set current_promotion="TEST $1 off"`). Revert.
  5. Budget: ~5.5h. Plan doc shape already agreed in session 2026-04-09. Explicitly out-of-scope for v1: auth, client UI, settings page, bulk updates, change history table, rollback beyond the printed undo line, any side effects (Stripe/HubSpot/welcome email).
- **Test call on MASTER `+18129944371`** — confirm code-node architecture swap + Call Processor fan-out work live. Validates (a) code-node flow end-to-end, (b) `is_lead`/`urgency`/`is_spam` custom analysis fields populate, (c) Brevo email lands in lead inbox, (d) Slack fan-out skipped cleanly when no webhook present.
- **Telnyx SMS swap** — once Telnyx AI approval lands, replace the `SMS Stub (Telnyx TODO)` node in HVAC Call Processor with a real HTTP node calling Telnyx messaging API. Stub payload is already built in `Build Payload`.

## P1 — 3-tier pricing end-to-end test (next session)

Run in order. All test-mode. Grab a Stripe test card (4242 4242 4242 4242).

### 1. Checkout page
- [ ] Visit `syntharra.com/checkout` (or staging URL) — 3 cards render, "Most Popular" on Professional
- [ ] Monthly/Annual toggle — all 3 cards update prices + annual year totals
- [ ] Annual prices: Starter $330/mo ($3,967/yr), Pro $581/mo ($6,970/yr), Biz $914/mo ($10,970/yr)
- [ ] Overage lines: $0.25/min, $0.18/min, $0.12/min
- [ ] $997 Activation Fee shown on all cards (no crossed-out price)
- [ ] Enterprise section shows, CTA → `sales@syntharra.com`
- [ ] CTA on each card fires Stripe checkout (test mode, correct price_id hits `/create-checkout-session`)
- [ ] Mobile: no horizontal scroll, cards stack cleanly

### 2. Stripe checkout → welcome email
- [ ] Complete a test checkout for each tier (Starter monthly is fine as a smoke test)
- [ ] `stripe_payment_data` row appears in Supabase with correct `tier`, `overage_rate`, `minutes`
- [ ] Welcome email arrives (Brevo) — plan name, minutes, overage rate correct, Jotform link appended `?tier=starter` / `?tier=professional` / `?tier=business`

### 3. Jotform → onboarding workflow
- [ ] Open Jotform link from welcome email (tier pre-fills if hidden field configured)
- [ ] Submit form → n8n `4Hx7aRdzMl5N0uJP` fires
- [ ] `reconcile_jotform_stripe` node finds Stripe record by email, PATCHes `client_subscriptions` with correct tier/overage_rate/billing_cycle
- [ ] `client_subscriptions` row in Supabase shows correct values

### 4. "You're Live" email
- [ ] Email sends after onboarding completes
- [ ] "Your Plan" card shows correct tier name, minutes, overage rate
- [ ] Starter: no WhatsApp section
- [ ] Professional/Business: WhatsApp section present (pending WhatsApp number being set)

### 5. Dashboard
- [ ] `dashboard.html?a=<agent_id>` loads, company info correct
- [ ] Minutes used / included minutes shown (if populated)
- [ ] Overage rate visible (if dashboard surfaces it)

### 6. Usage alert
- [ ] Run `python tools/usage_alert.py` manually against a test subscription
- [ ] Alert email shows correct `$X.XX/min` overage rate for that tier (not hardcoded 0.18)

### 7. Overage charges
- [ ] `python tools/monthly_minutes.py` — verify overage calculation uses `client_subscriptions.overage_rate`
- [ ] Confirm Stripe charge amount matches minutes × rate for the correct tier

### Blockers before test session
- [x] **Backend `/create-checkout-session`** — ✅ verified 2026-04-09: handles all 6 plan strings, price IDs match n8n PLANS map exactly.
- [x] **Jotform hidden `tier` field** — ✅ done 2026-04-09: field `tier` (qid 77) set to hidden, pre-fills from `?tier=X` URL param.

## P1 — Stripe live mode

- **Stripe live mode** — provide live secret key, replicate all 7 prices (3 monthly + 3 annual + activation fee) in live mode, update `syntharra_vault` entries and the PLANS map in n8n `xKD3ny6kfHL0HHXq`. Old single-price test ID `price_1TK5b1ECS71NQsk8Ru3Gyybl` is now superseded by the 6 tier-specific test prices in vault.
- **Who's hand-editing MASTER?** — 5 unpublished Retell revisions (v22→v27) accumulated on MASTER despite `retell-iac/CLAUDE.md` Rule 1. Find and close the loophole.

## Completed (2026-04-09 — late session, notification + infra pass)

- ~~Promote Standard TESTING → MASTER~~ — full architecture swap complete. MASTER flow v28, 19 code/conversation nodes, no `subagent`. Pre-promotion snapshot `retell-iac/snapshots/2026-04-09_master-pre-promote/`.
- ~~Rewrite `retell-iac/components/`~~ — `scripts/split_snapshot.py` regenerates template+components+manifest from any live snapshot. Byte-identical parity verified. Legacy archived.
- ~~MASTER custom post-call analysis fields~~ — `is_lead`, `urgency`, `is_spam` declared + published.
- ~~n8n onboarding naming patch (L25/L683)~~ — applied via Railway API. Agent names now prefixed `Demo —` or `Live —`.
- ~~Kill cloud n8n MCP~~ — all `mcp__claude_ai_n8n__*` entries purged from settings; CLAUDE.md rule added.
- ~~n8n API key rotation + vault~~ — leaked key scrubbed from settings; new key in vault.
- ~~n8n workflow audit~~ — 56 workflows catalogued, verdict table at `docs/audits/2026-04-09-n8n-workflow-audit.md`.
- ~~Archive 7 obsolete workflows~~ — 6 Premium + Weekly Newsletter. Deactivated + renamed + Dan UI-archived.
- ~~HVAC Call Processor rewrite~~ — 11 → 8 nodes, lean fan-out, Syntharra-branded email + Slack + SMS stub. Brevo key inlined from vault. Generator: `tools/build_call_processor_workflow.py`.
- ~~Optional Slack field in Jotform~~ — `slackIncoming` (qid 76) added to Section 5; onboarding `Parse JotForm Data` maps to `slack_webhook_url`.
- ~~Slack workspace cleanup~~ — 22 → 7 channels; bot token vaulted; 15 clutter channels archived; `#daily-digest` created.
- ~~Weekly client report script~~ — `tools/weekly_client_report.py`. Per-TZ bucket invocation. Deploy deferred to first multi-client launch.

## Completed (2026-04-09 — earlier)

- ~~Update website pricing page~~ — `plan-quiz.html` updated: single product $697/mo, Premium tier removed, quiz always returns Standard, JSON-LD updated
- ~~Update n8n onboarding workflow~~ — Premium onboarding (`kz1VmwNccunRMEaF`) deactivated; Standard workflow has no Premium branch
- ~~Update welcome email template~~ — `Send Welcome Email` node: removed "Standard Tier" comment, removed unused `PLAN_NAME` + dead `hasCRM`/`hasCal` vars
- ~~Move Brevo API key to Supabase vault~~ — `Send Setup Instructions Email` + `Send Welcome Email` nodes now fetch from `syntharra_vault` (Brevo/api_key)
- ~~Dashboard full redesign~~ — `syntharra-website/dashboard.html` rewritten: a11y, dark mode, sentiment breakdown, CSV export, virtualisation, demo mode (`?demo=1`), lead copy button, triage flag, 7-day sparkline
- ~~Dashboard silent-empty bug fix~~ — created `public.client_dashboard_info` SECURITY DEFINER view exposing 4 safe columns; anon can now read company/agent/service_area without touching the RLS-protected base table
- ~~Drop 15 hvac_call_log tables + call_processor_dlq~~ — using Retell's built-in call history now; 9 rows from pre-partition backed up to `backup_hvac_call_log_prepart_20260409`
- ~~Diagnose + fix Retell auto-layout / fine-tuning error~~ — `call_style_detector` component was missing `edges[]`; added via IaC source + new clone for validation. Pending Dan's promotion.

## Notes

- n8n webhook `/webhook/agent-test-runner` is INACTIVE (404). Do not retry.
- Dashboard URL: `https://syntharra.com/dashboard.html?a=<agent_id>`
- Retell proxy: `POST https://n8n.syntharra.com/webhook/retell-calls` `{ "agent_id": "..." }` — LIVE (n8n workflow `Y1EptXhOPAmosMbs`)
- Jotform Standard form `260795139953066` — already Standard-only, no tier field exists
- Stripe test price `price_1TK5b1ECS71NQsk8Ru3Gyybl` = $697/mo on `prod_UC0hZtntx3VEg2`. Old prices archived.
