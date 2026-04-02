# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Premium E2E complete, 89/89 passing

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests
- Standard: 75/75 ✅ — run: `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — run: `python3 shared/e2e-test-premium.py`

## Completed This Session
- Premium E2E test: 89/89 all passing
- Premium call processor bug FIXED: was using `n8n-nodes-base.filter` (crashed silently)
  → Rebuilt from Standard base with `n8n-nodes-base.if` filter — now working
- Premium Parse Lead Data fixed: GPT returns nested JSON with section headers
  → Added section-header flattener (ci, cc, lq, ad extractions)
- Premium webhook path confirmed: `/webhook/jotform-hvac-premium-onboarding`
  (different from Standard `/webhook/jotform-hvac-onboarding`)
- e2e-hvac-premium skill created — pushed to skills/
- CLAUDE.md skill table needs updating with e2e-hvac-premium entry

## Skills Available (upload to Claude settings)
- `skills/syntharra-brand/SKILL.md` — brand standard
- `skills/e2e-hvac-standard/SKILL.md` — Standard E2E test reference
- `skills/e2e-hvac-premium/SKILL.md` — Premium E2E test reference ← NEW

## GitHub Structure (key files)
| Path | What it is |
|---|---|
| `shared/e2e-test.py` | Standard E2E test |
| `shared/e2e-test-premium.py` | Premium E2E test ← NEW |
| `skills/e2e-hvac-standard/SKILL.md` | Standard E2E skill |
| `skills/e2e-hvac-premium/SKILL.md` | Premium E2E skill ← NEW |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | 12-node Standard template |
| `docs/context/` | AGENTS, WORKFLOWS, SUPABASE, INFRA, STRIPE, ARTIFACTS, LAUNCH |

## Open Action Items
- [ ] Phone +18129944371 UNASSIGNED in Retell — wire to Arctic Breeze
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?
- [ ] Dan to upload e2e-hvac-premium skill to Claude settings
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium entry

## Blocked
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Next Session — Start With
1. "Start session" → fetch CLAUDE.md + TASKS.md
2. Wire +18129944371 → Arctic Breeze agent
3. Resolve Mia agent
4. Upload e2e-hvac-premium skill to Claude

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
