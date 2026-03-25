# Syntharra Automations

All operational automation code for the Syntharra AI Receptionist platform.

## Structure

```
syntharra-automations/
  hvac-standard/          HVAC Standard AI Receptionist
    prompt-builder.js     n8n prompt builder node code
    conversation-flow.json  Retell conversation flow structure
  hvac-premium/           HVAC Premium AI Receptionist (coming soon)
  plumbing-standard/      Plumbing Standard (coming soon)
  shared/
    retell-publisher/     Headless browser service to publish Retell agents
    supabase/             Database migrations
    n8n-workflows/        Exported n8n workflow JSONs
```

## Key Services

- **Retell Publisher** — Node.js/Puppeteer service deployed on Railway that auto-publishes Retell agents after API updates
- **HVAC Standard Call Processor** — n8n workflow that processes Retell webhooks, scores leads via GPT, sends email/SMS notifications
- **HVAC Standard Onboarding** — n8n workflow triggered by Jotform, creates Retell agent, writes to Supabase

## Infrastructure

- **n8n**: syntharra.app.n8n.cloud
- **Supabase**: hgheyqwnrcvwtgngqdnq.supabase.co  
- **Retell AI**: AI voice agent platform
- **Railway**: Hosting for checkout server and publisher service
