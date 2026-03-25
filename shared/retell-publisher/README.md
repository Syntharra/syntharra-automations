# Retell Publisher Service

Headless browser service (Puppeteer) that logs into Retell and publishes agents via the dashboard UI.

## Deploy to Railway

1. Connect this repo to Railway
2. Set root directory to `shared/retell-publisher`
3. Add environment variables:
   - `RETELL_EMAIL` — Retell login email
   - `RETELL_PASSWORD` — Retell password  
   - `PUBLISHER_SECRET` — Secret token for auth
4. Deploy

## API

### POST /publish-retell-agent
```json
{ "agent_id": "agent_xxx" }
```
Headers: `Authorization: Bearer {PUBLISHER_SECRET}`

### GET /health
Returns `{ "status": "ok" }`
