# Syntharra Automations

Operational code for all Syntharra AI Receptionist products.

## Structure

```
syntharra-automations/
  hvac-standard/          HVAC Standard AI Receptionist
    prompt-builder.js     n8n prompt builder node code
    conversation-flow.json  Retell conversation flow definition
    call-processor.js     n8n call processor node code
  hvac-premium/           HVAC Premium (coming soon)
  plumbing-standard/      Plumbing Standard (coming soon)
  shared/
    retell-publisher/     Headless browser service to publish Retell agents
    supabase/             Database migrations
    n8n-workflows/        Exported n8n workflow JSONs
    prompt-templates/     Master prompt templates per product
```

## Separate Repositories

- `syntharra-checkout` — Pricing page + Stripe checkout (Railway)
- `syntharra-website` — Marketing website
- `syntharra-automations` — This repo, all operational automation code
