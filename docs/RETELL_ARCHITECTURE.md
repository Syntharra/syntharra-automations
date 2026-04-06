# Retell Agents — Architecture Pointer

As of 2026-04-06, all Syntharra Retell agent work uses the Git-IaC pipeline.

**Read these first, in order:**
1. [`retell-iac/CLAUDE.md`](../retell-iac/CLAUDE.md) — canonical policy and binding rules
2. [`docs/plans/retell-git-iac-migration-plan.md`](./plans/retell-git-iac-migration-plan.md) — full migration plan, phases, acceptance criteria

**Old model (deprecated):** shared Retell sub-agent components referenced by `component_id`. Do not use.

**New model:** component JSON files + manifest YAMLs → `build_agent.py` → inline conversation nodes → `promote.py` with test gate and Git-tagged rollback.

**Spanish routing:** removed from Standard and Premium. Do not recreate.
