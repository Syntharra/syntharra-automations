# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

- **Test call on MASTER `+18129944371`** — confirm code-node architecture swap + Call Processor fan-out work live. Validates (a) code-node flow end-to-end, (b) `is_lead`/`urgency`/`is_spam` custom analysis fields populate, (c) Brevo email lands in lead inbox, (d) Slack fan-out skipped cleanly when no webhook present.
- **Telnyx SMS swap** — once Telnyx AI approval lands, replace the `SMS Stub (Telnyx TODO)` node in HVAC Call Processor with a real HTTP node calling Telnyx messaging API. Stub payload is already built in `Build Payload`.

## P1

- **Stripe live mode** — add live secret key to vault, create $697/mo live price (test price created: `price_1TK5b1ECS71NQsk8Ru3Gyybl`)
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
