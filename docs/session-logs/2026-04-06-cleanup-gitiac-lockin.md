# Session Log — 2026-04-06 — Cleanup + Git-IaC Lock-In

## Objective
Tidy everything post-crash. Clean test data. Audit workflows. Lock Git-IaC (`retell-iac/`) as canonical Retell agent management. Verify architecture scales to 1000+ clients.

## Done
- Retell: 4 canonical agents verified; Std TESTING + orphan flow already deleted prior session. Gotcha: list-agents returns one row per version.
- Supabase: 29 test clients, 74 test calls, 1 orphan transcript_analysis row purged. agent_test_scenarios (115) preserved.
- n8n: 37 workflows audited, all active. Flags: 73Y0MHVBu05bIm5p review, 6LXpGffcWSvL6RxW MCP disabled.
- Git-IaC locked in via direct REST API (MCP 403 workaround): retell-iac/README.md, docs/SCALE-REVIEW-1000-CLIENTS.md, ARCHITECTURE.md, TASKS.md, FAILURES.md, retell-agents/README.md, CLAUDE.md.

## Scale review
Sound for 1000+ clients. #1 blocker: no automated path to push prompt updates to cloned clients. Ship Phases 6-8 before client #50.

## Critical follow-ups
1. Phases 6-8 fleet rollout (3w, blocks #50)
2. Ops monitor Railway redeploy
3. Stripe go-live
4. Telnyx approval
5. n8n queue mode + workers before #100
6. Partition hvac_call_log, add indexes, Supabase PITR

## Reflection
1. Wasted cycles on GitHub MCP 403 — should have pivoted to vault PAT + REST on first failure.
2. Wrong assumption: Retell list-agents returns unique agents (it returns versions). Documented.
3. Next time: MCP 403 → immediate REST fallback.
4. Pattern: GH_TOKEN from syntharra_vault + requests to api.github.com works every time.
5. ARCHITECTURE.md now documents Git-IaC as canonical + hidden scale bottleneck = update-after-clone (Phases 6-8).
6. No unverified assumptions this session — all writes confirmed by status code.
