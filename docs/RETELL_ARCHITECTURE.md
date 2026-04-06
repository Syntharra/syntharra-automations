# Retell Architecture — Canonical Pointers

**As of 2026-04-06, Syntharra manages all Retell agents via Git-IaC.**

Read these in order:

1. [`retell-iac/CLAUDE.md`](../retell-iac/CLAUDE.md) — binding policy (7 rules)
2. [`docs/plans/retell-git-iac-execution-playbook.md`](plans/retell-git-iac-execution-playbook.md) — full 4-phase execution playbook with session prompts
3. [`retell-iac/agent_configs/clone_registry.json`](../retell-iac/agent_configs/clone_registry.json) — live clone + MASTER IDs (once Phase 0 complete)

**Shared Retell sub-agent components are DEPRECATED.** Reusability now lives at build time in `retell-iac/components/` compiled inline into each flow by `scripts/build_agent.py`.

**`spanish_routing_node` is REMOVED** from Standard and Premium.

**MASTER agents are read-only** outside the `promote.py` pipeline.
