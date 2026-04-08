# A2 — Ops Monitor Redeploy Runbook
> Target repo path: docs/runbooks/A2-ops-monitor-redeploy.md
> Service: `syntharra-ops-monitor` (Railway service `7ce0f943`), currently PAUSED.
> ~30 min execution.

## Pre-flight (BEFORE unpausing)

### 1. Verify env vars set
Required: `RETELL_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SLACK_WEBHOOK_URL`, `N8N_BASE_URL=https://n8n.syntharra.com`

### 2. Verify HEAD-only health checks (NEVER POST)
Grep service code for any `requests.post(` / `axios.post(` against n8n webhook URLs. **Non-negotiable: HEAD only.** Fix any POST before unpausing.

### 3. Confirm Slack webhook alive
```bash
curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' \
  -d '{"text":"🟢 Ops monitor redeploy pre-flight"}'
```

## Unpause via Railway API
```bash
curl -X POST https://backboard.railway.com/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceUpdate(serviceId:\"7ce0f943\", input:{ paused: false }) }"}'
```
Wait ~60s.

## Smoke tests
1. Tail logs — confirm HEAD requests to n8n webhooks (no POSTs)
2. Archive a watched workflow → wait one cycle → confirm Slack alert → un-archive
3. `SELECT created_at, target, status FROM infra_health_checks ORDER BY created_at DESC LIMIT 20;` — confirm new rows every cycle

## Done when
Service running, HEAD-only checks, Slack alert proven, `infra_health_checks` rows growing, dashboard green 24h.

## Rollback
Re-pause via Railway. Read-only — no corruption risk.
