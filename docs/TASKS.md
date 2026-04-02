# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Mia deleted, Arctic Breeze refs purged

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests
- Standard: 75/75 ✅ — run: `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — run: `python3 shared/e2e-test-premium.py`

## Completed This Session
- Mia agent DELETED from Retell (agent_f3b9ae34726aa973c7d0bd82b6) ✅
- Arctic Breeze references removed from AGENTS.md and LAUNCH.md ✅
  → HVAC Standard agent is now "HVAC Standard Template" — generic, not client-named
  → Phone +18129944371 still UNASSIGNED (next action)

## Skills Available (upload to Claude settings)
- `skills/syntharra-brand/SKILL.md` — brand standard
- `skills/e2e-hvac-standard/SKILL.md` — Standard E2E test reference
- `skills/e2e-hvac-premium/SKILL.md` — Premium E2E test reference

## GitHub Structure (key files)
| Path | What it is |
|---|---|
| `shared/e2e-test.py` | Standard E2E test |
| `shared/e2e-test-premium.py` | Premium E2E test |
| `skills/e2e-hvac-standard/SKILL.md` | Standard E2E skill |
| `skills/e2e-hvac-premium/SKILL.md` | Premium E2E skill |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | 12-node Standard template |
| `docs/context/` | AGENTS, WORKFLOWS, SUPABASE, INFRA, STRIPE, ARTIFACTS, LAUNCH |

## Open Action Items
- [ ] Wire +18129944371 to HVAC Standard Template agent in Retell
- [ ] Dan to upload e2e-hvac-premium skill to Claude settings
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium entry

## Blocked
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Next Session — Start With
1. Wire +18129944371 → HVAC Standard Template agent
2. Live smoke test (call the number + submit Jotform)
3. Stripe live mode flip when ready

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
