# Retell Publisher

Headless browser service (Puppeteer) that logs into Retell and publishes agents via the dashboard UI.

## Why this exists

The Retell API does not expose a publish endpoint for conversation flows. Every time we update a flow via API it creates an unpublished draft. This service automates the publish click.

## Deploy on Railway

1. Connect this folder to a new Railway service
2. Set environment variables:
   - RETELL_EMAIL — your Retell login email
   - RETELL_PASSWORD — your Retell password  
   - API_SECRET — a secret token to authenticate requests
3. Railway will build via Dockerfile automatically

## Usage

POST /publish-retell-agent
Authorization: Bearer {API_SECRET}
{ "agent_id": "agent_xxx" }
