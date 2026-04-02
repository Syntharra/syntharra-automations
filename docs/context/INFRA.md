# Syntharra — Infrastructure
> Load when: working on Railway, deployments, env vars, DNS, URLs
> Keys stored in Supabase `syntharra_vault` — never hardcode here

## Railway
- API token: stored in vault as `service_name='Railway', key_type='api_token'`
- GraphQL API: `https://backboard.railway.com/graphql/v2`
- All services auto-deploy from `main` branch (~60s)

## Services
| Service | URL | Status |
|---|---|---|
| n8n | `https://n8n.syntharra.com` | Active |
| Checkout | `https://checkout.syntharra.com` | Active |
| Admin | `https://admin.syntharra.com` | Active |
| OAuth | `https://auth.syntharra.com` | Active |
| Ops monitor | `syntharra-ops-monitor-production.up.railway.app` | **PAUSED** |

## Ops Monitor
- Service ID: `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`
- Paused: 2026-03-30 (test-mode alert spam)
- Unpause: `mutation { sleepApplication(serviceId: "7ce0f943...", sleep: false) }`

## GitHub
- Token: stored in vault as `service_name='GitHub', key_type='personal_access_token'`
- Push pattern: GET file → extract SHA → PUT with base64 content + SHA
- NEVER commit raw token strings — GitHub secret scanning will block the push

## SMTP2GO
- API key: stored in vault as `service_name='SMTP2GO', key_type='api_key'`
- All n8n email nodes use SMTP2GO REST API (Railway blocks SMTP ports)

## Telnyx (SMS — pending)
- Account active, identity verified, $5 credit loaded
- Awaiting AI evaluation approval before purchasing toll-free number
- `SMS_ENABLED=false` in Railway env until approved

## Admin Dashboard
- Repo: `Syntharra/syntharra-admin`
- Basic auth: `admin` / `syntharra2026`
- AI assistant: Groq `llama-3.3-70b-versatile` (env: `GROQ_API_KEY`)
- Always fetch fresh SHA before editing — never use cached values
