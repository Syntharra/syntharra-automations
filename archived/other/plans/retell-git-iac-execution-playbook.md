# Retell Git-IaC Migration — Full Execution Playbook

**Owner:** Dan Blackmore, Syntharra
**Date authored:** 2026-04-06
**Status:** CANONICAL — this is the forward strategy for all Retell agent creation and modification at Syntharra.
**Repo:** `Syntharra/syntharra-automations`

---

## 0. READ THIS FIRST — Canonical Policy (Binding)

This document supersedes any prior guidance about the Retell "shared library components" model. From this point forward, Syntharra manages Retell agents as **Infrastructure-as-Code via Git + Python build scripts**. The Retell dashboard is not the source of truth. GitHub is.

**Seven binding rules — no exceptions:**

1. **No manual Retell dashboard edits to MASTER agents.** MASTER flows are modified only by the `promote.py` / `build_agent.py` pipeline in `retell-iac/scripts/`.
2. **No new shared Retell sub-agent components** (`conversation_flow_component_*`). Reusability lives at build time in `retell-iac/components/` JSON files, compiled inline into each flow.
3. **`spanish_routing_node` is removed** from both Standard and Premium. Do not migrate, recreate, or reference it.
4. **MASTER is read-only** outside the explicit promotion phase (`promote.py`). Every test, experiment, or build targets a CLONE.
5. **The 100% Standard MASTER baseline is sacred.** `Git tag baseline-100-percent-20260406` must exist and be verifiable before any promotion. Rollback must be dry-run-tested before any MASTER PATCH.
6. **All Retell assets are versioned in Git.** Flow templates, components, manifests, snapshots, and build outputs live in `retell-iac/`. Any asset not in Git does not exist.
7. **Every phase gates on explicit Dan approval.** No session auto-advances past a phase boundary.

**Key IDs (as of 2026-04-06):**
- Standard MASTER agent: `agent_4afbfdb3fcb1ba9569353af28d`
- Standard MASTER flow: `conversation_flow_34d169608460` (v24, 100% baseline)
- Premium TESTING agent: `agent_2cffe3d86d7e1990d08bea068f`
- Premium MASTER: does not yet exist — will be created via IaC after Standard promotes
- Baseline Git tag: `baseline-100-percent-20260406` (to be created in Phase 0)

**Read before every session in this plan:**
1. This document (`docs/plans/retell-git-iac-execution-playbook.md`)
2. `retell-iac/CLAUDE.md` (canonical policy)
3. `retell-iac/agent_configs/clone_registry.json` (once Phase 0 is done)

---

## Execution Model

The migration runs across **four gated sessions**. Each session corresponds to one phase block. At the end of each block, the session reports results and STOPS. Dan approves before the next session starts.

```
Phase 0 ─▶ Phase 1+2 ─▶ Phase 3+4 ─▶ Phase 5
 Snapshot    Extract +    Full E2E     Promote
 + Clone    Build + RT    Test Clone   Clone→MASTER
```

Run the four session prompts below in order, one per fresh chat. Each prompt is self-contained and references this playbook.

---

## SESSION PROMPT 1 — Phase 0: Snapshot + Clone Creation

```
Execute Phase 0 of the Retell Git-IaC Migration Playbook.

Read first (in this order):
1. retell-iac/CLAUDE.md (canonical policy — binding)
2. docs/plans/retell-git-iac-execution-playbook.md (full plan)
Both in Syntharra/syntharra-automations.

Hard rules for this session:
- Standard MASTER (agent_4afbfdb3fcb1ba9569353af28d, flow conversation_flow_34d169608460) is READ-ONLY. No PATCH, no publish, no component edits.
- Spanish routing is removed. Do not migrate spanish_routing_node.
- All write operations target a NEW clone agent, never MASTER.

Tasks:

1. SNAPSHOT
   - GET Standard MASTER flow (current published version, expected v24) in full
   - GET all 11 shared conversation_flow_component_* referenced by MASTER by ID
   - GET agent config for agent_4afbfdb3fcb1ba9569353af28d
   - Save raw JSON to retell-iac/snapshots/2026-04-06_baseline-100/
     - flow.json
     - components/{component_id}.json
     - agent.json
     - manifest.txt (list of files + sha256 of each)
   - Push to GitHub
   - Create Git tag: baseline-100-percent-20260406 (annotated, message: "Standard MASTER 100% baseline — pre Git-IaC migration")

2. CLONE
   - Create new conversation flow in Retell by POSTing a new flow then PATCHing it with the exact JSON body from the snapshot (strip read-only fields: flow_id, version, last_modification_timestamp)
   - Name: "HVAC Standard CLONE (Git-IaC candidate)"
   - Create new agent "HVAC Standard CLONE" pointing at the cloned flow, using the same voice/model/config as MASTER agent.json
   - Assign a non-production test phone number (use an unused Retell number, NOT +18129944371)
   - Publish the clone
   - Make ONE manual test call via Retell web test interface or API to confirm the clone answers

3. REGISTER
   - Write retell-iac/agent_configs/clone_registry.json:
     {
       "standard_clone": {
         "agent_id": "<new>",
         "flow_id": "<new>",
         "phone_number": "<new>",
         "created": "2026-04-06",
         "purpose": "Git-IaC candidate — pre-promotion staging",
         "baseline_tag": "baseline-100-percent-20260406"
       }
     }
   - Push to GitHub

Report:
- Snapshot file list + sha256s
- Git tag confirmation
- Clone agent_id, flow_id, phone number
- Manual test call outcome
- Confirmation that MASTER was not touched

STOP after reporting. Wait for Dan's approval before Phase 1.
```

---

## SESSION PROMPT 2 — Phases 1–2: Extract + Build Script + Round-Trip on Clone

```
Continue the Retell Git-IaC Migration. Phase 0 complete — snapshot tagged, Standard CLONE live.

Read first:
1. retell-iac/CLAUDE.md
2. docs/plans/retell-git-iac-execution-playbook.md
3. retell-iac/agent_configs/clone_registry.json
4. retell-iac/snapshots/2026-04-06_baseline-100/ (source of truth)

Hard rules:
- Standard MASTER untouched. All PATCH writes go to the CLONE only.
- Spanish routing excluded. Do not extract or reference spanish_routing_node.
- Round-trip MUST be byte-identical (ignoring Retell auto-generated fields: node_id auto-suffixes, timestamps, version) before any clone PATCH happens.

PHASE 1 — Extract

1. Parse the snapshot flow.json. For each of the 11 shared sub-agent nodes, resolve the component_id to its component JSON file from the snapshot.
2. For each shared component, write retell-iac/components/{name}.json with schema:
   {
     "name": "...",
     "source_component_id": "conversation_flow_component_...",
     "type": "conversation",
     "instruction": {...},
     "global_prompt": "...",
     "edges": [...],
     "tools": [...],
     "model_config": {...}
   }
3. For the orphan nodes in Standard MASTER flow (Emergency Detection only — confirm by checking component_id == null), extract into retell-iac/components/orphans/{name}.json with the same schema.
4. Create retell-iac/flows/hvac-standard.template.json — the flow JSON with every node's body replaced by a placeholder: {"__COMPONENT__": "name"}. Preserve edges, start_node_id, global_prompt, model config, and all non-node structure exactly.
5. Create retell-iac/manifests/hvac-standard.yaml:
   agent: standard
   flow_template: flows/hvac-standard.template.json
   components:
     - name: <each library component>
       source: components/<name>.json
     - name: emergency_detection
       source: components/orphans/emergency_detection.json
   overrides: {}
   excluded:
     - spanish_routing_node
6. Create retell-iac/manifests/hvac-premium.yaml (same structure, includes the Premium-only orphans from the plan: check_availability, confirm_booking, reschedule, cancel_appointment, emergency_fallback; excludes spanish_routing_node). Leave overrides empty for now.
7. Push all of retell-iac/components/, retell-iac/flows/, retell-iac/manifests/ to GitHub.

PHASE 2 — Build + Round-Trip

1. Write retell-iac/scripts/lib/flow_builder.py:
   - load_manifest(path) -> dict
   - load_component(path) -> dict
   - build_flow(manifest) -> dict  (resolves placeholders, inlines component bodies into the flow template, applies overrides)
2. Write retell-iac/scripts/build_agent.py:
   - CLI: --manifest <path> --out <path>
   - Calls build_flow, writes result JSON
3. Write retell-iac/scripts/diff.py:
   - CLI: --a <path> --b <path>
   - Deep-compare two flow JSONs
   - Ignore: flow_id, version, last_modification_timestamp, any field ending _timestamp
   - Normalize: sort edges by (from_node, to_node), sort tools by name, sort node keys
   - Exit 0 if semantically identical, exit 1 with diff report if not
4. ROUND-TRIP TEST:
   - python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json
   - python scripts/diff.py --a snapshots/2026-04-06_baseline-100/flow.json --b build/hvac-standard.built.json
   - Must exit 0. If not, iterate on flow_builder.py / component extraction until clean. Do NOT touch the snapshot to make it match — the snapshot is frozen truth.
5. Push scripts/, build output ignored via .gitignore (build/ excluded).

PHASE 2.5 — Deploy to CLONE (not MASTER)

1. Take build/hvac-standard.built.json
2. PATCH the CLONE flow (flow_id from clone_registry.json) with this JSON — this replaces the v24 snapshot contents with the Git-IaC-built equivalent, which should be byte-identical post-normalization.
3. Publish clone agent
4. Manual smoke call to clone to confirm it still answers

Report:
- Component extraction count
- Manifest files created
- Round-trip diff result (must be clean)
- Clone flow patched + published confirmation
- Smoke call result
- Confirmation MASTER untouched

STOP. Wait for Dan's approval before Phase 3.
```

---

## SESSION PROMPT 3 — Phases 3–4: Full End-to-End Test of Clone

```
Continue the Retell Git-IaC Migration. Clone has been rebuilt via Git-IaC pipeline (inline nodes, no shared sub-agent references for the migrated set).

Read first:
1. retell-iac/CLAUDE.md
2. docs/plans/retell-git-iac-execution-playbook.md
3. retell-iac/agent_configs/clone_registry.json
4. Supabase: agent_test_scenarios (100 standard scenarios)
5. Standard MASTER baseline: best_prompt_r5_95%.json reference (94.7% was Round 5; the 100% baseline is the current published MASTER as tested most recently — use whichever is more recent in agent_test_results)

Hard rules:
- MASTER untouched. All test traffic hits the CLONE agent.
- Use run_premium_only.py pattern as the template if needed, BUT pointed at the standard clone — do NOT run the Premium suite here.
- Watch Groq TPD (qwen/qwen3-32b = 500K/day). If TPD is exhausted, stop and report.
- Do NOT use run_tests.py with --agent flags (known wrapper bug, see agentic_testing_learnings memory).

Tasks:

1. Point the test runner at CLONE:
   - Create retell-iac/scripts/run_clone_tests.py (minimal wrapper that explicitly hardcodes the clone agent_id from clone_registry.json — no CLI flags to avoid the wrapper bug)
   - Use POST /webhook/agent-test-runner in n8n OR direct Retell call invocation, whichever matches how the 100% MASTER baseline was tested
   - Pull the 100 scenarios from Supabase agent_test_scenarios WHERE agent_type = 'standard'

2. Execute full suite against CLONE:
   - Run all 100 scenarios
   - Store results in Supabase agent_test_results with a clear run_id like "clone_iac_run_1"
   - Capture for each call: scenario_id, pass/fail, reason, latency_ms, cost_usd
   - If failures occur mid-run, do NOT stop — collect all results first

3. Parity analysis:
   - Pass rate vs MASTER baseline (must be >= MASTER baseline pass count)
   - Mean latency vs MASTER (must be <= MASTER mean; inline nodes should reduce hops)
   - Mean cost/call vs MASTER (must be <= MASTER)
   - Per-scenario diff: any scenario that passed on MASTER but fails on CLONE is a blocker

4. If any regressions:
   - Diagnose root cause per regression: build bug? missing field in component extraction? override needed? genuine inline-vs-subagent behavior delta?
   - Fix in retell-iac/components/ OR retell-iac/manifests/hvac-standard.yaml (overrides block)
   - Rebuild: python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json
   - Re-run diff against snapshot (will now differ — document why, commit as intentional divergence)
   - PATCH clone flow, publish
   - Re-run ONLY the failed scenarios first, then full suite on final pass
   - Max 5 fix-retest loops. If still failing, stop and escalate.

5. Produce parity report at docs/reports/2026-04-XX-clone-parity.md:
   - Executive summary (pass/fail gate)
   - Pass rate comparison table
   - Latency comparison (p50, p95, mean)
   - Cost comparison
   - Per-scenario pass/fail matrix (collapsed, only regressions listed in full)
   - Fix log (what was changed and why)
   - Recommendation: PROMOTE / DO NOT PROMOTE

6. Push report to GitHub. Append one row to FAILURES.md per fix applied.

HARD GATE:
- CLONE pass count >= MASTER pass count (target: 100/100)
- CLONE mean latency <= MASTER mean latency
- CLONE mean cost <= MASTER mean cost
- Zero regressions vs MASTER

If gate fails: report results, recommend DO NOT PROMOTE, stop. Do not attempt promotion under any circumstance without explicit Dan approval.

If gate passes: report results with PROMOTE recommendation, STOP, wait for Dan's explicit go-ahead for Phase 5.
```

---

## SESSION PROMPT 4 — Phase 5: Promote Clone to MASTER

```
Continue the Retell Git-IaC Migration. CLONE has passed all 100 scenarios, parity report signed off, Dan has approved promotion.

Read first:
1. retell-iac/CLAUDE.md
2. docs/plans/retell-git-iac-execution-playbook.md (Phase 5 + rollback section)
3. The approved parity report in docs/reports/
4. retell-iac/agent_configs/clone_registry.json

Hard rules:
- This is the only session permitted to modify Standard MASTER.
- Rollback plan must be dry-run-verified BEFORE touching MASTER.
- If ANY smoke test fails post-promotion, rollback IMMEDIATELY without asking.

Tasks:

1. Pre-flight verification:
   - Re-pull baseline-100-percent-20260406 Git tag, verify sha256 of snapshot files matches manifest.txt
   - Re-run python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json
   - Confirm the clone's currently-published flow JSON matches build/hvac-standard.built.json (pull clone flow via Retell API and diff)
   - If any mismatch → STOP, something drifted, investigate

2. Write and dry-run the rollback script:
   - retell-iac/scripts/rollback.py
   - CLI: --tag <git-tag> --agent <standard_master|premium_master> [--dry-run]
   - Logic: checkout snapshot files from the git tag, PATCH the target MASTER flow with snapshots/<tag>/flow.json, publish
   - Run: python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master --dry-run
   - Must print exactly what it would do without making any API writes. Confirm the dry-run output targets MASTER flow conversation_flow_34d169608460 with the snapshotted JSON.

3. Promote (the only write to MASTER):
   - PATCH agent_4afbfdb3fcb1ba9569353af28d flow to use build/hvac-standard.built.json
     (This requires pushing the built flow JSON to the existing MASTER flow_id, NOT switching MASTER to the clone's flow_id — keep the MASTER flow_id stable so rollback targets the same resource)
   - Publish MASTER agent
   - Note the new MASTER flow version number

4. Immediate 5-scenario smoke test against MASTER phone number (+18129944371):
   - Run 5 representative scenarios: 1 emergency, 1 lead capture, 1 booking, 1 objection handling, 1 Spanish caller (should now fail-soft since spanish_routing removed — scenario expected outcome must be updated)
   - Any failure → immediate rollback: python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master
   - Report failure, stop, do not continue

5. Full suite validation on MASTER:
   - Run all 100 scenarios against MASTER
   - Required: 100/100 pass
   - Any regression vs the approved clone parity report → rollback immediately

6. Tag success:
   - Git tag: release-hvac-standard-v25-git-iac (annotated)
   - Update TASKS.md: mark Git-IaC Standard promotion complete
   - Update FAILURES.md only if issues arose
   - Update ARCHITECTURE.md: record that Standard MASTER is now Git-IaC-managed, shared component library deprecated for this agent

7. Do NOT delete the CLONE agent. It becomes the permanent staging target for future Standard changes. Update clone_registry.json with "role": "permanent_staging".

8. Monitor window:
   - State explicitly in the report: "MASTER is under 24-hour observation. Any production call anomaly reported by Dan in the next 24h triggers rollback."

Report:
- Pre-flight diff results
- Rollback dry-run output
- MASTER promotion confirmation (new version number)
- 5-scenario smoke results
- 100-scenario full suite results
- Git tags created
- Clone status (preserved as staging)
- MASTER untouched by anything outside this one promotion PATCH

End session with full push: session log, TASKS.md, REFERENCE.md (new MASTER version), FAILURES.md if applicable, ARCHITECTURE.md update.
```

---

## Future Change Workflow (Post-Migration)

Once Standard MASTER is on Git-IaC, all future changes follow this loop:

1. **Edit** the relevant file in `retell-iac/components/` or `retell-iac/manifests/hvac-standard.yaml` on a feature branch.
2. **Build** locally: `python scripts/build_agent.py --manifest manifests/hvac-standard.yaml --out build/hvac-standard.built.json`
3. **Deploy to CLONE**: PATCH the standard_clone flow with the built JSON. Publish.
4. **Test** against CLONE using the full 100-scenario suite. Must pass 100%.
5. **Parity report** to `docs/reports/`.
6. **Promote** via `promote.py` — PATCH MASTER flow, smoke test, full suite, Git tag `release-hvac-standard-vN-<change-name>`.
7. **Rollback** on any failure via `rollback.py --tag <previous-release-tag> --agent standard_master`.

Premium follows the identical loop once Premium MASTER is created (post-Standard promotion).

## Rollback Procedure (Emergency)

```
python retell-iac/scripts/rollback.py \
    --tag baseline-100-percent-20260406 \
    --agent standard_master
```

This script:
1. Checks out the snapshot `flow.json` from the specified Git tag
2. PATCHes the MASTER flow with the snapshot content
3. Publishes the MASTER agent
4. Verifies by pulling the live flow and diffing against the snapshot

Always `--dry-run` first. Always verify the dry-run output targets the correct flow_id.

---

## End-of-Session Protocol (Every Session)

Every session in this plan MUST end with:
1. Push session log to `docs/session-logs/YYYY-MM-DD-retell-iac-phaseN.md`
2. Update `docs/TASKS.md` (open work only, <40 lines)
3. Update `docs/REFERENCE.md` if IDs changed
4. Append to `docs/FAILURES.md` per bug fixed
5. Push ALL changed files to GitHub
6. Update auto-memory if significant decisions made

Failure to push = session not closed.
