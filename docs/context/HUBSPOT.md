# Syntharra — HubSpot CRM
> Created 2026-04-03. Replaced the admin dashboard.
> Load when: working on CRM integration, n8n HubSpot nodes, lead/client data flows.

## Access
- URL: `https://app.hubspot.com`
- API base: `https://api.hubapi.com`
- Auth: Private App token — `Authorization: Bearer {api_key}`
- API key: `syntharra_vault` (service_name='HubSpot', key_type='api_key')
- OAuth client_id/client_secret: also in vault (used by Premium Dispatcher workflow)

## Deal Pipeline — "Syntharra Sales"
| Stage | Meaning | Set by |
|---|---|---|
| Lead | Website form submission | Website Lead n8n workflow |
| Demo Booked | Demo call scheduled | Manual or future automation |
| Paid Client | Stripe payment confirmed | Stripe n8n workflow |
| Active | Jotform onboarding complete + agent live | Jotform onboarding n8n workflow |

## Object IDs — Confirmed Live (2026-04-03)
- Pipeline ID: `default` (renamed to "Syntharra Sales")
- Stage IDs:
  | Stage | ID |
  |---|---|
  | Lead | `appointmentscheduled` |
  | Demo Booked | `qualifiedtobuy` |
  | Paid Client | `presentationscheduled` |
  | Active | `closedwon` |

## Key API Endpoints
```
# Contacts
POST /crm/v3/objects/contacts          — create contact
PATCH /crm/v3/objects/contacts/{id}    — update contact
POST /crm/v3/objects/contacts/search   — find by email

# Deals
POST /crm/v3/objects/deals             — create deal
PATCH /crm/v3/objects/deals/{id}       — update deal (stage, amount)

# Associations (link contact to deal)
PUT /crm/v3/associations/contacts/{contactId}/deals/{dealId}/contact_to_deal

# Notes (log call activity)
POST /crm/v3/objects/notes             — create note
PUT /crm/v3/associations/notes/{noteId}/contacts/{contactId}/note_to_contact

# Pipelines
GET /crm/v3/pipelines/deals            — list all pipelines + stage IDs
```

## n8n Integration Pattern (all workflows use this)
```javascript
// 1. Upsert contact by email
POST /crm/v3/objects/contacts/search
{ filterGroups: [{ filters: [{ propertyName: "email", operator: "EQ", value: email }] }] }
→ if found: PATCH contact | if not found: POST contact

// 2. Create/update deal
POST /crm/v3/objects/deals
{ properties: { dealname, dealstage, pipeline, amount, closedate } }

// 3. Associate contact → deal
PUT /crm/v3/associations/contacts/{contactId}/deals/{dealId}/contact_to_deal

// 4. Add note (for call logs)
POST /crm/v3/objects/notes
{ properties: { hs_note_body, hs_timestamp } }
PUT /crm/v3/associations/notes/{noteId}/contacts/{contactId}/note_to_contact
```

## Workflows That Push to HubSpot
| n8n Workflow | What it sends | When |
|---|---|---|
| Website Lead → AI Readiness Score | Create contact (Lead stage) | Website demo form submit |
| Stripe Workflow | Update deal → Paid Client stage | Stripe checkout.session.completed |
| HVAC AI Receptionist - Jotform Onboarding (Standard) | Update deal → Active stage | Jotform Standard submit |
| HVAC Prem Onboarding | Update deal → Active stage | Jotform Premium submit |
| HVAC Call Processor | Add note to contact (call summary, lead score) | Post-call webhook |

## Properties Mapped
| Supabase / system field | HubSpot property |
|---|---|
| company_name | company |
| client_email | email |
| lead_phone | phone |
| plan_type | custom: plan_type (Standard / Premium) |
| stripe_customer_id | custom: stripe_customer_id |
| agent_id | custom: retell_agent_id |
| lead_score (call log) | note body |
| call summary | note body |

## Custom Properties (create once in HubSpot UI → Contacts)
- `plan_type` — Single-line text — Standard or Premium
- `stripe_customer_id` — Single-line text
- `retell_agent_id` — Single-line text

## What HubSpot Does NOT Replace
- Supabase `hvac_standard_agent` — still the operational source of truth for Retell agent config
- Supabase `hvac_call_log` — still the call record store (AI analysis, geocoding, PII retention)
- HubSpot is the sales/relationship layer only — not the ops layer
