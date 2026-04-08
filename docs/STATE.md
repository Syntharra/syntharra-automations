# State — Syntharra Automations

_Last updated: 2026-04-08_

> **Auto-maintained header** — the `_Last updated_`, `## Last commit`, and `## Go-live checklist` lines are refreshed by `tools/session_end.py`. Do not hand-edit those. Everything else below is hand-curated; update it when reality changes.

## Last commit
35a20ff docs: wrap-up consolidation (retire 4 superseded docs, mark checklist canonical, log 403 incident)

## Go-live checklist
see docs/pre-launch-checklist.md

---

## What's live in production

- **HVAC Standard agent** — MASTER template at `retell-agents/HVAC-STANDARD-AGENT-TEMPLATE.md`. Currently at v4r1 quality ceiling ~85% on eval harness. 12 scenarios still failing.
- **HVAC Premium agent** — MASTER at `retell-agents/HVAC-PREMIUM-AGENT-TEMPLATE.md`. Running same agent as TESTING (split deferred to P1).
- **n8n onboarding workflows** — Standard `4Hx7aRdzMl5N0uJP`, Premium `kz1VmwNccunRMEaF`. Both received `submission_id` fix on 2026-04-07. Needs smoke-test verification at next session.
- **n8n call processors** — Standard + Premium variants, active.
- **Supabase schema** — RLS hardened 2026-04-07 (see FAILURES.md). `client_agents` table is the per-client source of truth.
- **OAuth server** — Railway-deployed. Google Calendar credentials still TODO before first paying client (see pre-launch-checklist §1).
- **Stripe** — still in test mode. Live-mode migration is a pre-launch blocker (see pre-launch-checklist §2).

## What's in flight

- **v4r1 Standard eval harness** — 12 failing scenarios (10, 16, 19, 22, 23, 28, 41, 60, 63, 66, 73, 75). Harness runs async on OpenAI gpt-4o-mini, concurrency 20, $5 cap. Resume next session.
- **n8n onboarding smoke test** — verify both workflows execute end-to-end with the `submission_id` fix live.
- **Arch consolidation** — canonical docs (this file, SESSION_START.md, RULES.md) landing tonight.

## What's blocked

- **Telnyx SMS activation** — waiting on Telnyx AI evaluation approval. Once received: buy toll-free, add to Supabase vault, flip `SMS_ENABLED=true` in call processors.
- **Premium MASTER/TESTING split** — deferred until Standard is green.
- **`run_tests.py --agent premium` flag** — broken, workaround is `run_premium_only.py`. See REFERENCE.md gotchas.

## Next session — pick up here

1. Run `python tools/session_start.py` to see the last session row and any new failures.
2. Verify n8n onboarding `submission_id` fix is live in both Standard `4Hx7aRdzMl5N0uJP` and Premium `kz1VmwNccunRMEaF`.
3. Resume v4r1 async eval harness on the 12 failing Standard scenarios.
4. If any scenario produces a new failure mode, log it in FAILURES.md and update RULES.md if it implies a standing rule.

## Architecture invariants (do not violate)

- **MASTER templates are the only thing in the repo.** Every per-client clone lives in Supabase `client_agents`.
- **IDs come from `docs/REFERENCE.md` only.** Never inline.
- **Never test on a live Retell agent.** Clone → TESTING → `retell-iac/scripts/promote.py` → live.
- **Every session ends with `tools/session_end.py`.** No exceptions.
- **Every new failure gets a FAILURES.md row.** Every row that implies a standing rule gets a RULES.md update in the same commit.
