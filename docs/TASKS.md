# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Brand skill + E2E skill complete, 75/75 E2E

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Test: 75/75 ✅ — run anytime: `python3 shared/e2e-test.py`

## Completed This Session
- E2E test: 75/75 all passing (timing bugs fixed, polling loops)
- All notification fields fixed end-to-end (Parse → Merge → Supabase)
- Conversation flow: 12 nodes locked as master template
- syntharra-brand skill created from theme factory — pushed to skills/ + brand-assets/
- e2e-hvac-standard skill created — pushed to skills/ + docs/
- CLAUDE.md skill table updated with both new skills
- Both skill files available for Dan to download + upload to Claude

## Skills Available (upload to Claude settings)
- `skills/syntharra-brand/SKILL.md` — brand standard
- `skills/e2e-hvac-standard/SKILL.md` — E2E test reference

## GitHub Structure (key files)
| Path | What it is |
|---|---|
| `shared/e2e-test.py` | E2E test — run this |
| `docs/e2e-test-reference.md` | E2E quick-reference |
| `skills/e2e-hvac-standard/SKILL.md` | E2E skill |
| `skills/syntharra-brand/SKILL.md` | Brand skill |
| `brand-assets/SYNTHARRA-BRAND-STANDARD.md` | Brand standard (standalone ref) |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | 12-node master template |
| `retell-agents/archive/` | n8n node code snapshots |
| `docs/context/` | AGENTS, WORKFLOWS, SUPABASE, INFRA, STRIPE, ARTIFACTS, LAUNCH |

## Open Action Items
- [ ] Phone +18129944371 UNASSIGNED in Retell — wire to Arctic Breeze
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?
- [ ] Dan to upload syntharra-brand + e2e-hvac-standard skills to Claude settings

## Blocked
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live

## Next Session — Start With
1. "Start session" → fetch CLAUDE.md + TASKS.md
2. Wire +18129944371 → Arctic Breeze agent
3. Resolve Mia agent
4. Confirm both new skills uploaded in Claude

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
