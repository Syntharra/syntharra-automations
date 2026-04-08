# Retell Agent Infrastructure as Code (Git-IaC)

**Canonical source of truth for all Retell agent configuration at Syntharra. Locked in 2026-04-06.**

> Premium tier retired 2026-04-08 — single product at $697/mo.

## Core Principle
**The Retell dashboard is NOT the source of truth. This directory is.**

All changes to the HVAC Standard MASTER agent flow through this directory exclusively.

## Canonical Workflow
1. Edit manifest or components in `manifests/` or `components/`
2. Build: `python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json`
3. Round-trip verify: `python scripts/diff.py`
4. Patch clone, publish for test
5. Run scenario tests: `python scripts/run_clone_tests.py --agent standard`
6. On green, promote: `python scripts/promote.py --agent standard_master --built build/hvac-standard.built.json`
7. Tag release: `git tag release-hvac-standard-vN-<change>`

## MASTER Agents (Read-Only outside promote.py)

| Agent | ID | Flow |
|---|---|---|
| HVAC Standard MASTER | `agent_4afbfdb3fcb1ba9569353af28d` | `conversation_flow_34d169608460` |

## Prohibited
- Direct Retell dashboard edits to MASTER agents
- Direct Retell API PATCH calls to MASTER outside `promote.py`
- Hand-editing flow JSON in `/retell-agents/` (reference archive only)

## Rollback
```
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master
```

## See Also
- `CLAUDE.md` — binding rules
- `EXECUTION_PLAYBOOK.md` — full playbook
- `../docs/ARCHITECTURE.md` — canonical architecture
