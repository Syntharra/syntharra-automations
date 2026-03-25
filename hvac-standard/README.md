# HVAC Standard AI Receptionist

Standard tier AI receptionist for HVAC trade businesses.

## Features
- Inbound call handling via Retell AI
- Lead capture and scoring via GPT-4
- Email and SMS lead notifications
- Call logging to Supabase
- Automated agent provisioning via Jotform → n8n → Retell

## Onboarding Flow
1. Client pays via Stripe checkout (syntharra-checkout repo)
2. Client completes Jotform onboarding form
3. n8n HVAC Standard Onboarding workflow fires
4. Retell agent created, Supabase record written, welcome email sent

## Supabase Table
hvac_standard_agent — one row per client, stores all agent config

## Retell Agent Config
- Voice: Sloane (Female)
- Language: Multilingual
- Mode: Rigid (follows conversation flow strictly)
- Webhook: syntharra.app.n8n.cloud/webhook/retell-hvac-webhook
