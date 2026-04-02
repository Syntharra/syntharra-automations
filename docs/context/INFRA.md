# Syntharra — Infrastructure
> Audited live from Railway API on 2026-04-02. Update from live API, not memory.
> Load when: Railway services, deployments, env vars, URLs, DNS
> Keys: stored in syntharra_vault — never put raw values in this file

## Railway Project: "Syntharra"
- API token: in `syntharra_vault` (service_name='Railway', key_type='api_token') — active token begins `1eb854a8`
- GraphQL API: `https://backboard.railway.com/graphql/v2`
- Auto-deploy: all services deploy from `main` branch of their GitHub repo (~60s)

## Railway Services (7 total — verified live)
| Service ID | Name | URL | Status |
|---|---|---|---|
| `c40f1306-0544-4915-a304-f33fdb8d4385` | syntharra-n8n | `https://n8n.syntharra.com` | Active |
| `e3df3e6d-6824-498f-bb4a-fdb6598f7638` | syntharra-checkout | `https://checkout.syntharra.com` | Active |
| `6a542e9d-9dff-4968-b908-6077e12ba96b` | syntharra-admin | `https://admin.syntharra.com` | Active |
| `48325e36-a234-46cc-896f-e9b0b3a30bcf` | syntharra-oauth-server | `https://auth.syntharra.com` | Active |
| `7ce0f943-5216-4a16-8aeb-794cc7cc1e65` | syntharra-ops-monitor | `syntharra-ops-monitor-production.up.railway.app` | **PAUSED** |
| `9285c656-12b4-44f5-8338-9b569c5e42dc` | n8n-redis | Internal (n8n queue backing store) | Active |
| `97e13df6-6a68-435e-95db-47fd03c10fe3` | n8n-postgres | Internal (n8n database) | Active |

## Ops Monitor
- Service ID: `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`
- Paused: 2026-03-30 (test-mode alert spam prevention)
- Unpause at go-live via Railway dashboard or GraphQL API

## GitHub Repos
| Repo | Deploys to Railway |
|---|---|
| `Syntharra/syntharra-admin` | syntharra-admin |
| `Syntharra/syntharra-checkout` | syntharra-checkout |
| `Syntharra/syntharra-oauth-server` | syntharra-oauth-server |
| `Syntharra/syntharra-ops-monitor` | syntharra-ops-monitor |
| `Syntharra/syntharra-website` | GitHub Pages (not Railway) |
| `Syntharra/syntharra-automations` | No deploy — ops/skills/docs only |
| `Syntharra/syntharra-artifacts` | No deploy — Claude artifacts only |
- NEVER merge syntharra-checkout into syntharra-automations
- NEVER commit raw API tokens to any repo — GitHub secret scanning blocks the push

## Email — SMTP2GO
- API key: in `syntharra_vault` (service_name='SMTP2GO', key_type='api_key')
- Used in ALL n8n email nodes
- Railway blocks SMTP ports — always use SMTP2GO REST API, never nodemailer

## SMS — Telnyx (PENDING)
- Account active, identity verified, $5 credit loaded
- Blocked: awaiting AI evaluation approval before purchasing toll-free number
- `SMS_ENABLED=false` in Railway n8n env vars until approved
- Do NOT use Twilio — Telnyx is chosen provider (Plivo as backup only)

## Admin Dashboard
> ⚠️ DEPRECATED 2026-04-03 — replaced by HubSpot CRM.
> Pause/delete `syntharra-admin` Railway service manually in dashboard.
> Repo `Syntharra/syntharra-admin` archived for reference only.

## HubSpot CRM
- URL: `https://app.hubspot.com`
- API key: in `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- Required Railway env var on n8n service: `HUBSPOT_API_KEY` (set from vault value)
- Optional pipeline stage env vars (set after creating pipeline in HubSpot UI):
  - `HUBSPOT_PIPELINE_ID` — deal pipeline ID
  - `HUBSPOT_STAGE_LEAD` — stage ID for website leads
  - `HUBSPOT_STAGE_PAID_CLIENT` — stage ID after Stripe payment
  - `HUBSPOT_STAGE_ACTIVE` — stage ID after agent goes live

## n8n
- URL: `https://n8n.syntharra.com`
- API key: ends in `NqU` (Railway env) — old Cloud key ends in `xdI` (invalid)
- Backed by n8n-postgres + n8n-redis (both Railway internal services)
- Auto-Enable MCP workflow `AU8DD5r6i6SlYFnb` runs every 6h
