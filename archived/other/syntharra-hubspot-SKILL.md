---
name: syntharra-hubspot
description: >
  Complete reference for all HubSpot CRM work at Syntharra.
  Load when: editing any n8n workflow that touches HubSpot, adding new HubSpot integrations,
  debugging CRM data sync, creating pipeline stages, mapping contact/deal properties,
  or working on the lead-to-client data flow.
---

> **Last verified: 2026-04-03** — HubSpot replaced admin dashboard. Add freshness date each time skill is confirmed current.

## Session Rules
At START of any HubSpot work:
1. Fetch `docs/context/HUBSPOT.md` from `syntharra-automations` for current pipeline IDs and stage IDs
2. Fetch `docs/context/WORKFLOWS.md` to see which n8n workflows touch HubSpot

At END of any HubSpot work:
1. Update `docs/context/HUBSPOT.md` with any new pipeline/stage IDs or property names
2. Update `docs/context/WORKFLOWS.md` if workflow logic changed
3. Push all to GitHub

---

## Auth Pattern (all n8n HTTP nodes)
```
URL: https://api.hubapi.com/...
Header: Authorization: Bearer {{$env.HUBSPOT_API_KEY}}
Header: Content-Type: application/json
```
API key is in Supabase vault: service_name='HubSpot', key_type='api_key'
Store in Railway n8n env as: `HUBSPOT_API_KEY`

---

## Upsert Contact (standard pattern used in all workflows)
```javascript
// Step 1: Search by email
POST https://api.hubapi.com/crm/v3/objects/contacts/search
{
  "filterGroups": [{
    "filters": [{ "propertyName": "email", "operator": "EQ", "value": "{{email}}" }]
  }],
  "properties": ["id","email","firstname","lastname","phone","company"]
}

// Step 2a: If found (results.total > 0) — update
PATCH https://api.hubapi.com/crm/v3/objects/contacts/{{results[0].id}}
{ "properties": { ...updatedFields } }

// Step 2b: If not found — create
POST https://api.hubapi.com/crm/v3/objects/contacts
{ "properties": { "email", "firstname", "lastname", "phone", "company", "plan_type" } }
```

---

## Create Deal
```javascript
POST https://api.hubapi.com/crm/v3/objects/deals
{
  "properties": {
    "dealname": "{{company_name}} — {{plan_type}}",
    "pipeline": "{{pipelineId}}",
    "dealstage": "{{stageId}}",
    "amount": "497" // or 997 for Premium
  }
}
```

## Associate Contact → Deal
```javascript
PUT https://api.hubapi.com/crm/v3/associations/contacts/{{contactId}}/deals/{{dealId}}/contact_to_deal
```
(No body required — PUT with empty body)

---

## Move Deal Stage
```javascript
PATCH https://api.hubapi.com/crm/v3/objects/deals/{{dealId}}
{ "properties": { "dealstage": "{{newStageId}}" } }
```

---

## Add Note to Contact (call log pattern)
```javascript
// Step 1: Create note
POST https://api.hubapi.com/crm/v3/objects/notes
{
  "properties": {
    "hs_note_body": "Call summary:\nCaller: {{caller_name}}\nService: {{service_requested}}\nLead score: {{lead_score}}\nSummary: {{summary}}",
    "hs_timestamp": "{{ISO8601 timestamp}}"
  }
}

// Step 2: Associate note to contact
PUT https://api.hubapi.com/crm/v3/associations/notes/{{noteId}}/contacts/{{contactId}}/note_to_contact
```

---

## Pipeline Stage IDs
> Fetch live from HubSpot when needed:
> GET https://api.hubapi.com/crm/v3/pipelines/deals
> Update this section once pipeline is created in HubSpot dashboard.

| Stage | ID |
|---|---|
| Lead | `appointmentscheduled` |
| Demo Booked | `qualifiedtobuy` |
| Paid Client | `presentationscheduled` |
| Active | `closedwon` |
| Pipeline ID | `default` |

---

## Custom Contact Properties (must exist in HubSpot before use)
Create at: HubSpot → Settings → Properties → Contact Properties → Create
| Internal name | Label | Type |
|---|---|---|
| `plan_type` | Plan Type | Single-line text |
| `stripe_customer_id` | Stripe Customer ID | Single-line text |
| `retell_agent_id` | Retell Agent ID | Single-line text |

---

## n8n Workflow Touchpoints
| Workflow | HubSpot action |
|---|---|
| Website Lead → AI Readiness Score | Upsert contact, create deal (Lead stage) |
| Stripe Workflow | Find contact by email, update deal → Paid Client |
| HVAC Jotform Onboarding (Standard) | Update deal → Active, set retell_agent_id |
| HVAC Prem Onboarding | Update deal → Active, set retell_agent_id |
| HVAC Call Processor | Add call note to contact |

---

## Railway Env Var Required
Add to n8n Railway service env vars:
`HUBSPOT_API_KEY` = (value from vault: service_name='HubSpot', key_type='api_key')

---

## What HubSpot Does NOT Replace
- Supabase remains source of truth for Retell agent config (`hvac_standard_agent`)
- Supabase `hvac_call_log` remains the call record store
- HubSpot = sales/relationship layer only

---

## Architecture Decisions

| Decision | Chose | Why | Revisit if |
|---|---|---|---|
| CRM choice | HubSpot over custom dashboard | Custom admin dashboard was maintenance overhead; HubSpot free tier covers all pre-launch needs; has API for n8n to write to automatically | HubSpot pricing becomes significant at scale |
| HubSpot write pattern | Non-blocking (try/catch) in all workflows | HubSpot outages must never break the call pipeline — CRM is a nice-to-have, not a pipeline dependency | — |
| Data split | Supabase for agent config, HubSpot for CRM | Supabase is the operational source of truth; HubSpot is the sales/relationship view | Sync complexity becomes a maintenance burden |
| Contact upsert | Search → update or create | Prevents duplicate contacts from repeat form submissions or retries | — |
