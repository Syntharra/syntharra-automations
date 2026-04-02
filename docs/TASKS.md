# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-03 — Admin dashboard removed. HubSpot CRM integrated.

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — `python3 shared/e2e-test-premium.py`

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 Loop+prompt fixes live |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 Prompt fixes live |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Completed This Session (2026-04-03)
- [x] HubSpot API key stored in Supabase vault (service_name='HubSpot', key_type='api_key')
- [x] Railway token updated in vault
- [x] Admin dashboard deprecated — README updated in syntharra-admin repo
- [x] CLAUDE.md updated — admin removed, HubSpot CRM section added
- [x] docs/context/HUBSPOT.md created — full CRM integration reference
- [x] skills/syntharra-hubspot-SKILL.md created
- [x] INFRA.md updated — admin deprecated, HubSpot env vars documented
- [x] WORKFLOWS.md updated — HubSpot integration noted on all 5 workflows
- [x] 5 n8n workflows patched + activated with HubSpot nodes:
  - Website Lead → upsert contact + create deal (Lead stage)
  - Stripe → upsert contact + create deal (Paid Client stage)
  - Jotform Standard → update contact + create deal (Active stage)
  - Jotform Premium → update contact + create deal (Active stage)
  - Call Processor → log call note to client contact

## Dan Action Required
- [ ] **Add `HUBSPOT_API_KEY` env var to n8n Railway service** (1 env var, 2 mins)
  - Railway dashboard → Syntharra project → syntharra-n8n service → Variables
  - Value: fetch from Supabase vault (service_name='HubSpot', key_type='api_key')
  - Pipeline + stage IDs baked into workflows — no other env vars needed
- [ ] **Pause syntharra-admin Railway service** manually in Railway dashboard
  - Railway → Syntharra project → syntharra-admin → Settings → Danger Zone → Suspend

## Open Action Items (pre-launch)
- [ ] Run core_flow agent simulator group again (expect 80%+)
- [ ] Run all 6 groups, target 90%+ overall
- [ ] Promote Standard TESTING → MASTER once verified
- [ ] Wire +18129944371 to Standard Template agent
- [ ] Live smoke test (Dan available ~2 days)

## Pre-Go-Live Security
- [ ] Move `syntharra-checkout/env` sk_test_ key to Railway env vars before switching to sk_live_

## Blocked
- Live smoke test — Dan unavailable ~2 days
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live
- HubSpot pipeline stage IDs — need Dan to create pipeline in HubSpot UI first

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
5. Confirm HubSpot pipeline IDs in Railway env vars
