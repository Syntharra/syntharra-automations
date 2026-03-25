# Retell Publisher Service

Headless browser service that logs into Retell and publishes agents via the UI.

## Deploy on Railway

1. Connect this folder to a new Railway service
2. Set environment variables:
   - `RETELL_EMAIL` — your Retell login email
   - `RETELL_PASSWORD` — your Retell password  
   - `PUBLISHER_SECRET` — random secret for API auth
3. Railway will build via Dockerfile automatically

## Usage

```bash
POST /publish-retell-agent
Authorization: Bearer {PUBLISHER_SECRET}
Content-Type: application/json

{ "agent_id": "agent_xxx" }
```

Returns `{ "success": true, "agent_id": "agent_xxx" }`

## Note
This service is used by n8n workflow "Publish Retell Agent" automatically
after every agent update. You should not need to call it manually.
