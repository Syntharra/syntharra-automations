# Syntharra n8n — Production Hardening Guide
# Railway Self-Hosted: Monitoring, Alerts, Backups, Auto-Recovery
# ================================================================

## 1. Health Check Endpoint

n8n exposes `/healthz` natively. Railway uses this to detect unhealthy
containers and auto-restart them.

Already configured in `railway.toml`:
```
healthcheckPath = "/healthz"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
```

This means: Railway pings `/healthz` every few seconds. If n8n stops
responding, Railway kills the container and restarts it automatically
(up to 5 retries). This handles most crash scenarios without any
human intervention.


## 2. External Uptime Monitoring (CRITICAL)

Railway's built-in health check restarts crashed containers, but it
won't alert you. You need external monitoring that checks from outside
and notifies you when something is down.

### Option A: Better Stack (recommended, free tier)
- Sign up at https://betterstack.com/uptime
- Free tier: 10 monitors, 3-minute check intervals
- Add these monitors:

  | Monitor | URL | Expected |
  |---------|-----|----------|
  | n8n health | `https://n8n.syntharra.com/healthz` | HTTP 200 |
  | Checkout server | `https://syntharra-checkout-production.up.railway.app/` | HTTP 200 |
  | Stripe webhook | `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` | HTTP 200 |

- Set up alerts: Email to daniel@syntharra.com + SMS (add phone later)
- Set escalation: if no acknowledgement in 15 min, re-alert

### Option B: UptimeRobot (alternative, free tier)
- Sign up at https://uptimerobot.com
- Free tier: 50 monitors, 5-minute check intervals
- Same monitors as above
- Alerts via email, Slack, webhook

### Option C: Self-hosted on Railway (n8n workflow)
We can build a simple n8n workflow that pings critical endpoints every
5 minutes and sends an alert email via SMTP2GO if anything fails.
This runs on the same Railway instance so it's not truly "external"
monitoring — use this as a SUPPLEMENT to Option A or B, not a replacement.


## 3. n8n Error Notifications

Add these env vars to get emailed when workflows fail:

```
N8N_EMAIL_MODE=smtp
N8N_SMTP_HOST=mail.smtp2go.com
N8N_SMTP_PORT=2525
N8N_SMTP_USER=syntharra-n8n
N8N_SMTP_PASS=<SMTP2GO_SMTP_PASSWORD>
N8N_SMTP_SENDER=noreply@syntharra.com
```

Then in n8n Settings > Workflow Settings > Error Workflow:
- Create an "Error Handler" workflow that catches all workflow failures
- Sends notification email to support@syntharra.com with:
  - Which workflow failed
  - Error message
  - Timestamp
  - Link to the failed execution


## 4. Database Backups

Railway Postgres does NOT auto-backup on the Pro plan. You must set
this up yourself.

### Daily Postgres Dump via n8n Workflow

Create a scheduled n8n workflow that runs daily at 03:00 UTC:

1. Execute Command node: `pg_dump` the database
2. Compress the output
3. Upload to:
   - Option A: GitHub (syntharra-automations/backups/) — free, versioned
   - Option B: Hetzner Storage Box (€3/mo for 1TB) — cheap, reliable
   - Option C: Backblaze B2 (free 10GB) — S3-compatible

Recommended: GitHub for now (free, and you're already using it).
Migrate to Hetzner Storage Box when backups exceed 1GB.

### Backup Retention
- Keep 7 daily backups
- Keep 4 weekly backups (Sundays)
- Delete older backups automatically


## 5. Auto-Restart & Resilience

### Railway handles container-level restarts automatically.

For application-level resilience, add these n8n env vars:

```
# Limit Node.js memory to prevent OOM kills
NODE_OPTIONS=--max-old-space-size=1536

# Binary data to filesystem (prevents RAM bloat on large payloads)
N8N_DEFAULT_BINARY_DATA_MODE=filesystem

# Prune old execution data (prevents database bloat)
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168

# Queue mode for better concurrency handling
EXECUTIONS_MODE=queue
```

### Redis Persistence
Redis should be configured with AOF (Append Only File) persistence
so queued jobs survive a Redis restart:
```
REDIS_ARGS=--appendonly yes
```


## 6. Graceful Deploys (Zero Downtime)

When you push a new version of n8n, Railway does a rolling deploy:
it starts the new container, waits for the health check to pass,
then kills the old container. This means zero downtime during updates.

To ensure this works:
- Never change `N8N_ENCRYPTION_KEY` after initial setup
- Don't change database credentials during deploys
- Test workflow imports on a staging environment first


## 7. Railway Resource Alerts

Railway doesn't have built-in cost alerts yet. Monitor spending by:
- Checking Railway Dashboard > Usage weekly
- Setting a calendar reminder for billing day
- Railway shows real-time resource consumption per service

Tip: If n8n RAM usage creeps above 80% of your allocated memory,
it's time to bump it up before you get OOM killed.


## 8. Webhook Retry Safety Net

Your critical webhook sources all have built-in retry logic:

| Source | Retry Behaviour |
|--------|----------------|
| Stripe | Retries up to 72 hours, exponential backoff |
| Jotform | Retries for 24 hours |
| Retell | Retries with exponential backoff |

This means: even if n8n is down for an hour, you lose ZERO data.
Webhooks queue on the sender side and deliver when n8n comes back.

IMPORTANT: n8n must respond with HTTP 200 quickly. If your webhook
processing takes too long, the sender may retry and create duplicates.
Use the "Respond to Webhook" node early in your workflow, then
continue processing asynchronously.


## 9. Logging & Debugging

### Railway Logs
- Railway Dashboard > Service > Logs shows real-time stdout/stderr
- Logs retained for 30 days on Pro plan
- Filter by timestamp, severity

### n8n Execution History
- With `EXECUTIONS_DATA_SAVE_ON_ERROR=all`, all failed executions
  are saved with full input/output data
- Access via n8n UI > Executions
- Set `EXECUTIONS_DATA_MAX_AGE=168` (7 days) to prevent DB bloat


## 10. Security Hardening

### n8n Access
- Set up n8n user authentication (email + password) on first boot
- Consider: restrict n8n UI access to your IP via Railway's
  networking settings (not available on Pro, only Enterprise)
- Use a strong, unique password for the n8n admin account

### Database
- Use Railway's private networking for Postgres connections
  (service-to-service, not exposed to internet)
- This also eliminates egress costs for DB traffic

### Secrets
- All sensitive values stored in Railway env vars (encrypted at rest)
- Never commit secrets to GitHub
- `N8N_ENCRYPTION_KEY` encrypts all credentials stored in n8n —
  if you lose this key, all saved credentials become unrecoverable


## 11. Pre-Transition Checklist

Before flipping from n8n Cloud to Railway:

- [ ] Railway project created with n8n + Postgres + Redis
- [ ] All env vars set (use .env.template as reference)
- [ ] N8N_ENCRYPTION_KEY generated and saved securely
- [ ] Custom domain configured (n8n.syntharra.com)
- [ ] SSL working (Railway handles this automatically)
- [ ] Health check passing (`/healthz` returns 200)
- [ ] External monitoring set up (Better Stack or UptimeRobot)
- [ ] Error notification workflow created
- [ ] Test workflow deployed and executing successfully
- [ ] All credentials re-entered and tested
- [ ] All 15 active workflows imported and tested
- [ ] Stripe webhook URL updated in Stripe Dashboard
- [ ] Jotform webhook URL updated
- [ ] Retell callback URLs updated (if applicable)
- [ ] Daily backup workflow scheduled and tested
- [ ] Old n8n Cloud workflows deactivated (NOT deleted)
- [ ] Monitor for 48 hours before cancelling n8n Cloud
