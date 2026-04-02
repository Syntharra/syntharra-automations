# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — E2E 75/75, master template + skill complete

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Test: 75/75 ✅ PERFECT — run anytime: `python3 shared/e2e-test.py`

## Completed This Session
- Full E2E test run — 75/75 all passing
- All notification fields fixed (Parse → Merge → Supabase: q64/q65/q66/q67)
- Conversation flow fixed: 10 → 12 nodes (callback + spam_robocall restored)
- E2E timing bugs fixed: polling loops replace flat sleeps, correct workflow IDs
- Master template system: `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`
- Archive: n8n node code snapshots in `retell-agents/archive/`
- Skill: `skills/e2e-hvac-standard/SKILL.md`
- Docs: `docs/e2e-test-reference.md`
- Everything pushed to GitHub, clean and organised

## Open Action Items (needs Dan input)
- [ ] Phone +18129944371 UNASSIGNED in Retell — wire to Arctic Breeze agent
- [ ] Agent "Mia" (agent_f3b9ae34726aa973c7d0bd82b6) — keep or delete?
- [ ] Dan to paste theme factory .skill from Claude Code when at PC

## Blocked
- Telnyx SMS — awaiting AI evaluation approval ($5 loaded)
- Ops monitor — PAUSED, unpause at go-live

## GitHub Structure (key files)
| Path | What it is |
|---|---|
| `shared/e2e-test.py` | E2E test script — run this |
| `docs/e2e-test-reference.md` | Quick-reference for E2E |
| `skills/e2e-hvac-standard/SKILL.md` | Full E2E skill |
| `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md` | Standard agent master template |
| `retell-agents/archive/` | n8n node code snapshots |
| `docs/context/` | AGENTS, WORKFLOWS, SUPABASE, INFRA, STRIPE, ARTIFACTS, LAUNCH |

## Next Session — Start With
1. "Start session" → fetch CLAUDE.md + TASKS.md
2. Wire +18129944371 to Arctic Breeze in Retell
3. Resolve Mia agent
4. Dan pastes theme factory skill

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
