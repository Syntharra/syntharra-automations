# Syntharra Automations

Operational automation code for the Syntharra AI Receptionist platform.

## Structure

```
syntharra-automations/
  shared/
    retell-publisher/     # Headless browser service to publish Retell agents
    supabase-migrations/  # All Supabase schema migrations
    n8n-workflows/        # Exported n8n workflow JSON files
  hvac-standard/
    prompt-builder.js     # n8n Build Retell Prompt node code
    conversation-flow.json # Master conversation flow structure
    call-processor.js     # n8n call processor node code
  hvac-premium/           # Coming soon
  plumbing-standard/      # Coming soon
```

## Repos
- `syntharra-checkout` — Pricing page + Stripe checkout only (Railway)
- `syntharra-automations` — All operational automation code (this repo)
- `syntharra-website` — Public website
