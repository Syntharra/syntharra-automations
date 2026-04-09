> Premium tier retired 2026-04-08. Single product — $697/mo. Standard only.

# retell-iac — Canonical Policy

**Source of truth for all Retell agent configuration at Syntharra.**
The Retell dashboard is NOT the source of truth. This directory is.

## Binding Rules

1. **No manual dashboard edits to MASTER agents.** MASTER flows are modified ONLY by `scripts/promote.py`.
2. **No new shared `conversation_flow_component_*` objects.** Reusability lives at build time in `components/` JSON, inlined into each flow by `build_agent.py`.
3. **`spanish_routing_node` is removed everywhere.** Retell native multilingual handles Spanish inline — no dedicated routing node in any agent.
4. **MASTER is read-only** outside `promote.py` runs. Every test, experiment, and build targets a CLONE.
5. **Baseline tags are immutable.** `baseline-100-percent-20260406` is the Standard MASTER 100% snapshot. Rollback is tag-based.
6. **All Retell assets live in Git** (`retell-iac/`). Anything not in Git does not exist.
7. **Every phase requires explicit Dan approval** before advancing. No session auto-promotes.

## Layout

```
retell-iac/
├── CLAUDE.md                 # this file
├── agent_configs/
│   └── clone_registry.json   # live clone agent IDs + phones (Standard only)
├── snapshots/
│   └── 2026-04-06_baseline-100/       # Standard MASTER 100% (tagged)
├── components/               # inlined-at-build component bodies
│   ├── *.json                # Standard shared (11)
│   └── orphans/              # Standard non-subagent inline nodes
├── flows/
│   └── hvac-standard.template.json
├── manifests/
│   └── hvac-standard.yaml
├── scripts/
│   ├── build_agent.py        # manifest → built flow JSON
│   ├── diff.py               # normalized flow diff
│   ├── promote.py            # build → MASTER (the only MASTER writer)
│   ├── rollback.py           # baseline tag → MASTER
│   └── run_clone_tests.py    # scenario suite against clones
└── build/                    # gitignored build outputs
```

## Standard workflow for any change

1. Edit `components/<name>.json` or `manifests/hvac-standard.yaml` on a feature branch.
2. `python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json`
3. PATCH the Standard CLONE with the built JSON, publish.
4. Run `python scripts/run_clone_tests.py --agent standard`.
5. Write a parity report to `docs/reports/YYYY-MM-DD-<change>.md`.
6. On green: `python scripts/promote.py --agent standard_master --built build/hvac-standard.built.json`
7. Git tag `release-hvac-standard-vN-<change>`.
8. On any smoke failure: `python scripts/rollback.py --tag <previous-release-tag> --agent standard_master`.

## Rollback

```
export RETELL_API_KEY=... GITHUB_TOKEN=...
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master --dry-run
# verify output targets the correct flow_id
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master
```

## Canonical Agents (updated 2026-04-09)

| Agent | agent_id | flow_id | Phone | Notes |
|---|---|---|---|---|
| **Standard TESTING (authoritative current)** | `agent_6e7a2ae03c2fbd7a251fafcd00` | `conversation_flow_90da7ca2b270` | _(none)_ | Modern `code`-node architecture. Autolayout-fixed 2026-04-09. Pending promotion to MASTER. |
| Standard MASTER (legacy — stale) | `agent_4afbfdb3fcb1ba9569353af28d` | `conversation_flow_34d169608460` | `+18129944371` | Uses legacy `subagent` node type. Will be replaced by TESTING on next promotion. |

> **The `retell-iac/components/` directory is stale** — its component JSON files describe the legacy `subagent` shape. They do not match the current Standard TESTING flow, which uses flat `code` nodes with inline bodies. Do NOT rebuild Standard from IaC manifests until the components are rewritten to match the new architecture. Use the Retell API / snapshots as the current source of truth.
