# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — E2E 75/75, brand skill + master template complete

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Test: 75/75 ✅  —  `python3 shared/e2e-test.py`

## Skills Installed (Dan to upload to Claude settings)
- `syntharra-brand` — download: `skills/syntharra-brand/SKILL.md`
- `e2e-hvac-standard` — download: `skills/e2e-hvac-standard/SKILL.md`
> Both also available as downloadable files from this session

## GitHub Structure (key files)
| Path | What it is |
|---|---|
| `shared/e2e-test.py` | E2E test — run this |
| `docs/e2e-test-reference.md` | E2E quick-reference |
| `skills/e2e-hvac-standard/SKILL.md` | E2E skill (install in Claude) |
| `skills/syntharra-brand/SKILL.md` | Brand skill (install in Claude) |
| `brand-assets/syntharra-brand-standard.md` | Brand theme — source of truth |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | Standard agent master template |
| `retell-agents/archive/` | n8n node code snapshots (v5) |
| `docs/context/` | AGENTS, WORKFLOWS, SUPABASE, INFRA, STRIPE, LAUNCH |
| `syntharra-artifacts/brand/` | Brand files in artifacts repo |

## Open Action Items (needs Dan input)
- [ ] Upload `syntharra-brand-SKILL.md` to Claude settings
- [ ] Upload `e2e-hvac-standard-SKILL.md` to Claude settings
- [ ] Phone +18129944371 UNASSIGNED in Retell — wire to Arctic Breeze agent
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?

## Blocked
- Telnyx SMS — awaiting AI evaluation approval ($5 loaded)
- Ops monitor — PAUSED, unpause at go-live

## Next Session
1. "Start session" → fetch CLAUDE.md + TASKS.md
2. Wire +18129944371 to Arctic Breeze
3. Resolve Mia agent
4. Confirm skills installed in Claude

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
