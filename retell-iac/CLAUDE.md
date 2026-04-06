# Retell Agent Architecture — CANONICAL (2026-04-06)

**This file is authoritative. It overrides any older guidance about Retell agents, shared sub-agent components, or "library components" in this repo.**

## The rule

All Syntharra Retell agents (HVAC Standard, HVAC Premium, future verticals) are built, edited, tested, and promoted via the **Git-IaC pipeline** in `retell-iac/`. This is the only approved method.

Full plan: [`docs/plans/retell-git-iac-migration-plan.md`](./plans/retell-git-iac-migration-plan.md)

## What this replaces

The previous model used **shared Retell sub-agent components** — reusable nodes defined inside Retell, referenced by `component_id` from multiple flows. Editing one propagated to all agents automatically.

**That model is deprecated** because:
- Runtime cost: every sub-agent handoff = separate LLM invocation + latency
- No staging: edits went live instantly across all agents
- No rollback: Retell has versioning but no diff review or atomic revert
- No per-vertical customization without duplicating components

## What replaces it

**Component JSON files + manifest YAMLs in Git → build script → inline conversation nodes in Retell at build time.**

```
retell-iac/
  components/shared/*.json    ← edit once, all agents get it on next build
  components/hvac/*.json      ← HVAC-specific overrides
  components/premium/*.json   ← Premium-tier components
  manifests/hvac-standard.yaml ← which components + overrides for this agent
  manifests/hvac-premium.yaml
  scripts/build_agent.py      ← manifest → full flow JSON → PATCH Retell
  scripts/promote.py          ← build + test + diff + PATCH MASTER
  scripts/rollback.py         ← revert to any tagged snapshot
```

## Binding rules for every session

1. **Do not edit Retell agents in the Retell dashboard.** All edits → `retell-iac/` files → `build_agent.py` → `promote.py`.
2. **Do not create new shared Retell sub-agent components.** Reusability lives in Git, not Retell.
3. **Spanish routing is removed from Standard and Premium.** Do not recreate `spanish_routing_node`.
4. **MASTER agents are read-only** outside of a successful `promote.py` run.
5. **Every change = Git commit.** No commit = no change.
6. **New verticals = new manifest file**, not new dashboard work.
7. **Self-healing optimizer writes to component files in Git**, never to live Retell flows.

## Current state (as of 2026-04-06)

- Standard MASTER (`agent_4afbfdb3fcb1ba9569353af28d`) — **100% test baseline, flow v24** — to be snapshot-tagged as `baseline-100-percent-20260406` in Phase 0 of the plan.
- Premium TESTING (`agent_2cffe3d86d7e1990d08bea068f`) — flow v11 — Premium test queued.
- Premium MASTER — **does not exist yet** (will be created fresh from Git-IaC in Phase 6).
- Standard TESTING (`agent_731f6f4d59b749a0aa11c26929`) — **does not exist** (404). Old ID in CLAUDE.md is stale. New TESTING agent will be built in Phase 3.
- Demo Male / Demo Female — use legacy `retell-llm` (not conversation flows). Separate migration, out of scope for now.

## What to do first in any new session touching Retell

1. Read this file.
2. Read `docs/plans/retell-git-iac-migration-plan.md` to find the current phase.
3. Execute only the next approved phase. Do not jump ahead.
4. Every phase has acceptance criteria and sign-off gates — respect them.
5. No writes to MASTER until Phase 4 parity test passes.

## If something seems to contradict this

This file wins. Older CLAUDE.md guidance, memory entries, or skill files referencing "shared sub-agent components" or "library components in Retell" are stale — ignore and update them.
