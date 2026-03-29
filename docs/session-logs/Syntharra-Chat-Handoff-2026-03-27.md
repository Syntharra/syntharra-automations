# Syntharra Chat Handoff — 2026-03-27

## Quick Reference

### Active n8n Workflows (all SMTP2GO, zero Gmail/Twilio)

| Workflow | ID | Active | Purpose |
|---|---|---|---|
| Standard Onboarding | k0KeQxWb3j3BbQEk | ✅ | Jotform → Supabase → Retell agent creation |
| Standard Call Processor | OyDCyiOjG0twguXq | ✅ | Retell webhook → parse → Supabase + notifications |
| Stripe Workflow | ydzfhitWiF5wNzEy | ✅ | checkout.session.completed → Supabase → emails |
| Weekly Lead Report | mFuiB4pyXyWSIM5P | ✅ | Weekly lead summary email |
| Minutes Calculator | 9SuchBjqhFmLbH8o | ✅ | Monthly minute usage tracking |
| Usage Alert | lQsYJWQeP5YPikam | ✅ | 80%/100% minute usage warnings |
| Publish Retell | sBFhshlsz31L6FV8 | ✅ | Publish agent after API updates |
| Scenario Runner v4 | 94QmMVGdEDl2S9MF | ✅ | E2E test runner |
| Scenario Sub-workflow | rlf1dHVcTlzUbPX7 | ✅ | Process single test scenario |
| Transcript Generator | dHO8O0QHBZJyzytn | ✅ | Scenario transcript processing |
| Welcome Email (Manual) | Rd5HiN7v2SRwNmiY | ✅ | Backup manual welcome email |
| Premium Onboarding | KXDSMVKSf59tAtal | ✅ | Premium client onboarding (13 nodes) |
| Premium Call Processor | UhxfrDaEeYUk4jAD | ✅ | Premium call handling (repeat caller) |
| Premium Dispatcher | kVKyPQO7cXKUJFbW | ✅ | Google Cal + Jobber integration |
| Integration Hub | 8WYFy093XA6UKB7L | ✅ | Premium integration orchestrator |
| Nightly GitHub Backup | EAHgqAfQoCDumvPU | ✅ | Auto-backup to GitHub |

### Retell Agents (LIVE)

| Agent | ID | Type |
|---|---|---|
| HVAC Standard | agent_4afbfdb3fcb1ba9569353af28d | Production |
| Jake (Demo Male) | agent_b9d169e5290c609a8734e0bb45 | Demo |
| Sophie (Demo Female) | agent_2723c07c83f65c71afd06e1d50 | Demo |

- Conversation flow: `conversation_flow_34d169608460`
- NOTE: Standard agent ID changed from `agent_d180e1bd5b9b724c8f616a0415` to `agent_4afbfdb3fcb1ba9569353af28d`

### Supabase
- Project: `hgheyqwnrcvwtgngqdnq.supabase.co`
- Key tables: `hvac_standard_agent`, `hvac_call_log`, `stripe_payment_data`, `client_subscriptions`, `billing_cycles`, `overage_charges`, `website_leads`

### Stripe (TEST MODE)
- Checkout: `checkout.syntharra.com`
- Products: Standard `prod_UC0hZtntx3VEg2` | Premium `prod_UC0mYC90fSItcq`
- Webhook: `we_1TEJXzECS71NQsk8eOMIs8JE`

### Email: All SMTP2GO
- API key: `api-0BE30DA64A074BC79F28BE6AEDC9DB9E`
- From: `noreply@syntharra.com` / "Syntharra AI"

### OAuth Server
- Repo: `Syntharra/syntharra-oauth-server`
- Deployed on Railway

### Dashboard
- LIVE at `syntharra.com/dashboard.html?agent_id=X`

---

## Pending Items (next session)

1. **Google Cloud OAuth** — Create credentials, add GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET to Railway env vars, deploy guide needed
2. **Telnyx SMS** — Waiting on AI evaluation approval; when approved, provide API key + toll-free number to activate (SMS_ENABLED=false currently)
3. **Stripe live mode** — Recreate all products/prices/coupons/webhook in live mode before launch
4. **Amazon SES** — DNS verification stalled (Squarespace CNAME prefix issue), migrated to SMTP2GO instead
5. **Sales pitch pack** — VSL package uploaded but no work started
6. **Weekly usage reports** — Enhancement to existing minutes/usage system
7. **More CRM integrations** — Expand beyond Jobber

---

## Key Rules (always follow)

- Never delete/recreate a Retell agent — patch in place
- Always publish after Retell agent updates
- Always push to GitHub after sessions with changes
- Commas not dashes in agent prompts
- n8n edits require manual Publish to go live
- Jotform: use REST API directly, NOT MCP OAuth connector
- `overflow-x: clip` not `overflow: hidden` on html/body
