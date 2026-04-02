# Syntharra — Tasks & Continuity
> Updated at END of every chat. Load at START after CLAUDE.md. Keep under 60 lines.
> Last updated: 2026-04-02 — Fixed ops monitor pre-launch suppression bug (case-sensitive system name)

## Status: PRE-LAUNCH | Stripe TEST MODE | 32 active workflows

## E2E Tests (pipeline)
- Standard: 75/75 ✅ — run: `python3 shared/e2e-test.py`
- Premium:  89/89 ✅ — run: `python3 shared/e2e-test-premium.py`

## Agent Simulator (NEW)
- Script: `shared/simulator.py`
- Cost: ~$0.002/scenario (vs $0.15 on Retell — 98% cheaper)
- Model: gpt-4o-mini (OpenAI)
- Requires: OpenAI API key (not yet in vault — Dan to provide)
- Usage:
  - All 80 standard scenarios: `python3 shared/simulator.py --key sk-... --scenarios all`
  - Specific IDs:              `python3 shared/simulator.py --key sk-... --scenarios 81,82,89,92`
  - By group:                  `python3 shared/simulator.py --key sk-... --group pricing_traps`
- Results pushed to GitHub: `tests/results/simulator-run-*.json`
- Add OpenAI key to vault: INSERT INTO syntharra_vault (service_name, key_type, key_value) VALUES ('OpenAI', 'api_key', 'sk-...')

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard Template | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — do not touch |
| HVAC Premium Template | `agent_9822f440f5c3a13bc4d283ea90` | ✅ MASTER — do not touch |
| HVAC Standard (TESTING) | `agent_731f6f4d59b749a0aa11c26929` | 🧪 All fixes applied |
| HVAC Premium (TESTING) | `agent_2cffe3d86d7e1990d08bea068f` | 🧪 All fixes applied |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

## Open Action Items
- [ ] Dan: provide OpenAI API key → add to vault → run simulator
- [ ] Run simulator on all 80 standard scenarios (est. ~$0.16 total)
- [ ] Fix failures, iterate, target 90%+ pass rate
- [ ] Promote Standard TESTING → MASTER once verified
- [ ] Repeat for Premium TESTING
- [ ] Wire +18129944371 to Standard Template agent
- [ ] Live smoke test (Dan available in 2-3 days)
- [ ] Update CLAUDE.md skill table with e2e-hvac-premium entry

## Blocked
- Simulator: needs OpenAI API key
- Live smoke test — Dan unavailable 2-3 days
- Telnyx SMS — awaiting AI evaluation approval
- Ops monitor — PAUSED, unpause at go-live
  - ✅ Fixed: pre-launch suppression was case-sensitive (Clients vs clients) — emails were leaking through

## Go-Live Gate
1. Stripe live mode → recreate products/prices/coupons
2. Update Railway STRIPE_SECRET_KEY → sk_live_
3. Update n8n webhook signing secret
4. Unpause ops monitor + enable SMS (Telnyx)
