# Retell Architecture - Canonical

**Status:** Git-IaC (as of 2026-04-06). This doc supersedes all prior Retell architecture notes.

## Source of Truth
GitHub is canonical. Retell dashboard is display-only. All changes flow: edit manifest/component → `build_agent.py` → diff → PATCH clone → test → `promote.py` → MASTER.

## Key Changes from Legacy
- Flows are no longer edited in the Retell dashboard.
- Shared `conversation_flow_component_*` objects are extracted into `retell-iac/components/*.json`.
- Manifest YAML lists all components + overrides + `excluded_nodes`.
- Spanish routing node is **removed** from both Standard and Premium (multilingual handled natively by Retell).
- Only `promote.py` may write to MASTER agents.

## Agents

| Role | Agent ID | Flow ID | Phone |
|---|---|---|---|
| Standard MASTER | agent_4afbfdb3fcb1ba9569353af28d | conversation_flow_34d169608460 | +18129944371 |
| Standard CLONE (iac test) | agent_201b8d1e9eee10303e79710bc9 | (clone flow) | — |
| Premium MASTER | agent_9822f440f5c3a13bc4d283ea90 | (master flow) | — |
| Premium CLONE (iac test) | agent_eb8195c21ba2ef79e2c6d8d3c5 | conversation_flow_746a02ffa4ac | — |

## Workflow
```
edit manifests/hvac-standard.yaml
  -> python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.json
  -> python scripts/diff.py build/hvac-standard.json snapshots/<baseline>/flow.json
  -> PATCH clone via run_clone_tests.py
  -> run E2E on clone
  -> python scripts/promote.py --agent standard_master --built build/hvac-standard.json
```

## Rollback
```
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master
```

## Baseline Tags
- `baseline-100-percent-20260406` — Standard MASTER v24, 19 nodes, 100% scenarios passing

## Binding Rules
See `retell-iac/CLAUDE.md` for the 7 binding rules.
