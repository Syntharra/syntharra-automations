# TASKS

> Single product: HVAC Standard at $697/mo. Premium retired 2026-04-08.

## P0

- **Retell MASTER promote** — Dan to verify auto-layout fix on CLONE `agent_1d8d85fd2c1c21ede61c68b88c` in Retell UI, then run `build_agent.py → diff.py → promote.py`. **Warning:** MASTER is at v27 unpublished with 5 revisions of drift since v22 — those will be overwritten. Pre-fix baseline saved at `retell-iac/snapshots/2026-04-09_pre-fix/`. After promote, delete the test clone.
- **n8n onboarding naming patch** — Dan to paste 3-line diff into `Build Retell Prompt` code node of workflow `4Hx7aRdzMl5N0uJP`:
  - L25: add `const isDemo = !!data.is_demo;` and `const agentDisplayName = \`${isDemo ? 'Demo' : 'Live'} — ${companyName}\`;`
  - L683: change `agent_name: \`${agentName}\`,` → `agent_name: agentDisplayName,`

## P1

- **Stripe live mode** — add live secret key to vault, create $697/mo live price (test price created: `price_1TK5b1ECS71NQsk8Ru3Gyybl`)
- **Who's hand-editing MASTER?** — 5 unpublished Retell revisions (v22→v27) accumulated on MASTER despite `retell-iac/CLAUDE.md` Rule 1. Find and close the loophole.

## Completed (2026-04-09)

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
