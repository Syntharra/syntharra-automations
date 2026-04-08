# Syntharra n8n Migration Guide
## n8n Cloud → Railway Self-Hosted

### Overview
This guide covers migrating from syntharra.app.n8n.cloud to a self-hosted
n8n instance on Railway. The self-hosted instance provides unlimited
executions at ~$28-33/month vs n8n Cloud's execution caps.

---

### Pre-Migration Checklist (DO NOW — before you need to switch)

- [ ] Create Railway project: `syntharra-n8n`
- [ ] Add Postgres plugin (Railway one-click)
- [ ] Add Redis plugin (Railway one-click)
- [ ] Deploy n8n service from this repo
- [ ] Generate encryption key: `openssl rand -hex 32`
- [ ] Set all environment variables in Railway dashboard
- [ ] Verify n8n boots and you can access the UI
- [ ] Set up custom domain: n8n.syntharra.com → Railway service
- [ ] Test a simple workflow (HTTP trigger → respond)

### Migration Day Steps

1. **Export all workflows from n8n Cloud**
   - n8n Cloud UI → Settings → Export all workflows (JSON)
   - Or use n8n API:
     ```bash
     curl -H "X-N8N-API-KEY: YOUR_CLOUD_API_KEY" \
       https://syntharra.app.n8n.cloud/api/v1/workflows \
       -o workflows-backup.json
     ```

2. **Export credentials**
   - n8n does NOT export credential secrets via API
   - You'll need to manually re-enter credentials on the new instance:
     - Retell API key
     - Supabase credentials
     - Stripe webhook signing secret
     - SMTP2GO credentials
     - Jotform API key
     - GitHub token
     - Google Calendar OAuth (Premium)
     - Jobber OAuth (Premium)

3. **Import workflows to Railway instance**
   - n8n UI → Import from file → Select exported JSON
   - Or use API:
     ```bash
     curl -X POST -H "X-N8N-API-KEY: YOUR_RAILWAY_API_KEY" \
       -H "Content-Type: application/json" \
       -d @workflows-backup.json \
       https://n8n.syntharra.com/api/v1/workflows
     ```

4. **Re-enter all credentials**
   - Go through each credential and enter the values
   - Test each workflow individually

5. **Update webhook URLs everywhere**
   This is the critical step. Every external service pointing to
   syntharra.app.n8n.cloud must be updated:

   - **Stripe webhook**: Update in Stripe Dashboard
     - Old: `https://syntharra.app.n8n.cloud/webhook/syntharra-stripe-webhook`
     - New: `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook`

   - **Jotform webhook**: Update in Jotform form settings
     - Old: `https://syntharra.app.n8n.cloud/webhook/jotform-hvac-onboarding`
     - New: `https://n8n.syntharra.com/webhook/jotform-hvac-onboarding`

   - **Retell AI**: Update any webhook/callback URLs in Retell dashboard

   - **Any other external triggers** pointing to n8n cloud

6. **Activate all workflows on Railway instance**
   - Go through each workflow → Toggle Active
   - REMEMBER: Click Publish after any changes

7. **Deactivate all workflows on n8n Cloud**
   - Don't delete yet — keep as backup for 1 billing cycle

8. **Test end-to-end**
   - Trigger a test Stripe checkout
   - Make a test call to the Retell agent
   - Submit a test Jotform
   - Verify Supabase data is being written
   - Check that emails are sending

9. **Cancel n8n Cloud subscription**
   - Only after 1-2 weeks of confirmed stability on Railway

---

### Custom Domain Setup

Option A: Subdomain (recommended)
- Add CNAME record: `n8n.syntharra.com` → Railway service URL
- Configure in Railway: Settings → Networking → Custom Domain

Option B: Keep using Railway-generated URL
- Less professional but zero DNS config
- URL format: `syntharra-n8n-production.up.railway.app`

---

### Backup Strategy

The nightly backup workflow (ID: EAHgqAfQoCDumvPU) should be updated to
also backup the self-hosted instance. Consider:
- Daily Postgres dump to cloud storage
- Workflow export via n8n API to GitHub (syntharra-automations)

---

### Cost Projection

| Clients | n8n Cloud Plan | Cloud Cost | Railway Cost |
|---------|---------------|------------|--------------|
| 0-5     | Starter       | $20/mo     | ~$28-33/mo   |
| 5-15    | Pro           | $50/mo     | ~$28-33/mo   |
| 15-30   | Pro (tight)   | $50/mo     | ~$28-33/mo   |
| 30+     | Business      | $667/mo    | ~$35-45/mo   |

Railway becomes cheaper than n8n Cloud once you exceed ~5 clients.
The savings become dramatic at scale.

---

### Rollback Plan

If Railway has issues:
1. Re-activate workflows on n8n Cloud (still there as backup)
2. Revert webhook URLs to syntharra.app.n8n.cloud
3. Services restore within minutes
