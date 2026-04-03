# Session Log — 2026-04-03 — HubSpot Full Build-Out

## Summary
Completed full HubSpot property schema, company records, all lead capture wired,
affiliate flow added, enriched data flowing on all pipelines.

## Done

### Properties Created
**Contacts (11 custom):** plan_type, stripe_customer_id, retell_agent_id, lead_source,
contact_type, trade_vertical, subscription_status, recommended_plan,
monthly_call_volume, agent_live_date, business_timezone

**Deals (3 custom):** plan_type, deal_source, mrr

**Companies (6 custom):** retell_agent_id, plan_type, trade_vertical,
subscription_status, agent_live_date, monthly_call_volume

### Pipeline Cleaned
- Removed stray "Contract Sent" stage (was not fully archived previously)
- Final pipeline: Lead → Demo Booked → Paid Client → Active (4 stages only)

### Workflows Enriched
All HubSpot nodes updated to pass new properties:
- lead_source (mapped from source string)
- contact_type (lead vs client vs affiliate)
- trade_vertical (auto-detected from services_offered)
- mrr (497 or 997 based on plan)
- deal_source
- agent_live_date (set on Jotform onboarding)
- subscription_status

### Company Auto-Creation
Jotform Standard + Premium onboarding now auto-creates/upserts Company record
and associates it to the contact. Properties: plan_type, trade_vertical,
retell_agent_id, subscription_status, agent_live_date.

### Affiliate Flow
- New n8n workflow: Affiliate Application — HubSpot Contact (ID: syGlWx8TlbYlPZU4)
- affiliate.html updated to fire /webhook/affiliate-apply after Supabase save
- Creates contact with contact_type=affiliate, lead_source=affiliate

### Historical Leads Synced
- xskllxmarksman@gmail.com — contact updated + deal created
- blackmore_daniel@ymail.com — contact created + deal created
- daniel@syntharra.com skipped (non-negotiable rule)

### Total Active HubSpot Touchpoints: 9 workflows
Website Lead (AI Readiness) → Website Lead (Free Report) → Website Lead (Index/Calc/Quiz) →
Affiliate Application → Stripe Payment → Jotform Standard → Jotform Premium →
Call Processor Standard → Call Processor Premium

## Files Changed
- docs/context/HUBSPOT.md — full property reference, all 9 workflows
- docs/context/WORKFLOWS.md — affiliate workflow added, counts updated
- skills/syntharra-hubspot-SKILL.md — (update pending in next push)
- syntharra-website/affiliate.html — n8n webhook wired in
