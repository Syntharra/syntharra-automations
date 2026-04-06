# Retell Git-IaC Migration Plan
**Project:** Syntharra — Retell Conversation Flow → GitHub + Python Pipeline
**Owner:** Dan Blackmore
**Author:** Claude (Cowork session)
**Date created:** 2026-04-06
**Status:** Draft — ready to execute in new session
**Current baseline to protect:** Standard MASTER `conversation_flow_34d169608460` v24 — **100% pass rate**

---

## 1. Executive Summary

### 1.1 What we're doing
Migrating Syntharra's Retell HVAC Standard and Premium agents from an in-Retell shared sub-agent component library to a **GitHub-native Infrastructure-as-Code (IaC) pipeline**. Flow definitions and reusable components will live as versioned JSON/YAML files in the `syntharra-automations` repo. A Python build script will compile them into full Retell conversation flows with **inline conversation nodes** instead of runtime sub-agents.

### 1.2 Why
The current architecture has three unfixable problems:
1. **Runtime cost + latency** — every shared sub-agent is a separate LLM invocation per call. Standard stacks 12 handoffs per conversation. Audible dead air on phone calls and multiplied billing.
2. **No staging layer** — editing a shared component hits every live agent instantly. No way to test a fix before it goes live.
3. **No rollback** — Retell has internal versioning but no diff review, no atomic "revert all clients to yesterday's known-good state."

### 1.3 What we keep
- ✅ Edit-once, propagate-to-all-agents (build script loops through agent registry)
- ✅ Per-vertical customization (manifest overrides)
- ✅ Proven 100% baseline (we snapshot it first, promote only after TESTING passes)

### 1.4 What we gain
- ✅ Staging layer (build + test before live)
- ✅ Git history, diff review, atomic rollback via `git revert`
- ✅ Zero runtime sub-agent overhead (inline conversation nodes)
- ✅ Per-client cohort rollout (promote to 5 clients, monitor, then the rest)
- ✅ Self-healing optimizer loop writes to Git, not to live flows

### 1.5 What we risk
- Single point of failure in the build script — must be bulletproof
- Discipline required: Retell dashboard becomes read-only for flow edits
- 1–2 days of tooling build time (pre-launch, this is the ideal window)

---

## 2. Current State (verified 2026-04-06)

### 2.1 Agents that exist
| Agent | ID | Flow ID | Version | Status |
|---|---|---|---|---|
| Standard MASTER | `agent_4afbfdb3fcb1ba9569353af28d` | `conversation_flow_34d169608460` | v24 | **LIVE, 100% baseline** |
| Premium TESTING | `agent_2cffe3d86d7e1990d08bea068f` | `conversation_flow_2ded0ed4f808` | v11 | Testing queued tonight |
| Demo Male | `agent_b9d169e5290c609a8734e0bb45` | `llm_1c567ee6b304c925ba78af4ce32f` | v6 | Legacy retell-llm |
| Demo Female | `agent_2723c07c83f65c71afd06e1d50` | `llm_1c567ee6b304c925ba78af4ce32f` | v6 | Legacy retell-llm |

### 2.2 Agents that DO NOT exist (CLAUDE.md incorrect)
- `Premium MASTER` (`agent_9822f440f5c3a13bc4d283ea90`) — returns 404
- `Standard TESTING` (`agent_731f6f4d59b749a0aa11c26929`) — returns 404

**Action:** update CLAUDE.md and REFERENCE.md to reflect reality.

### 2.3 Shared components (confirmed by component_id match)
11 components are **genuinely shared** between Standard and Premium TESTING flows:

| Component name | Component ID | Used by Standard | Used by Premium |
|---|---|---|---|
| identify_call_node | `conversation_flow_component_ebac0db129f3` | ✅ | ✅ |
| nonemergency_leadcapture / fallback_leadcapture | `conversation_flow_component_33ab8b82f1fc` | ✅ | ✅ (aliased) |
| verify_emergency_node | `conversation_flow_component_174275fc7751` | ✅ | ✅ |
| callback_node | `conversation_flow_component_ab7909b654e2` | ✅ | ✅ |
| existing_customer_node | `conversation_flow_component_d8eff9881e16` | ✅ | ✅ |
| general_questions_node | `conversation_flow_component_d46848148d1d` | ✅ | ✅ |
| spam_robocall_node | `conversation_flow_component_2cc95ba461b7` | ✅ | ✅ |
| transfer_failed_node | `conversation_flow_component_335da5e7364e` | ✅ | ✅ |
| Ending | `conversation_flow_component_827d612a2cb9` | ✅ | ✅ |
| call_style_detector | `conversation_flow_component_ff58734c21bb` | ✅ | ✅ |
| validate_phone | `conversation_flow_component_3b788e86e755` | ✅ | ✅ |

### 2.4 Orphan nodes (component_id = None — NOT in library)
These are the highest-priority migration targets — they are drift-in-waiting.

**Standard:**
- Emergency Detection (global) ⚠️ critical

**Premium TESTING:**
- Emergency Detection (global) ⚠️ critical
- check_availability_node
- confirm_booking_node
- reschedule_node
- cancel_appointment_node
- emergency_fallback_node
- spanish_routing_node

### 2.5 Flow-level config
- **Model:** `cascading gpt-4.1` (NOT Groq — good)
- **Tools count:** 0 at flow level
- **Start node:** `node-greeting` (conversation type)
- **Knowledge base IDs:** present
- **Global prompt:** present (must be preserved verbatim in migration)

---

## 3. Target Architecture

### 3.1 Repo layout
```
syntharra-automations/
└── retell-iac/
    ├── components/
    │   ├── shared/
    │   │   ├── identify_call.json
    │   │   ├── leadcapture.json
    │   │   ├── verify_emergency.json
    │   │   ├── callback.json
    │   │   ├── existing_customer.json
    │   │   ├── general_questions.json
    │   │   ├── spam_robocall.json
    │   │   ├── transfer_failed.json
    │   │   ├── ending.json
    │   │   ├── call_style_detector.json
    │   │   ├── validate_phone.json
    │   │   └── emergency_detection.json
    │   ├── hvac/
    │   │   ├── hvac_emergency_keywords.json
    │   │   ├── hvac_leadcapture_overrides.json
    │   │   └── hvac_general_questions.json
    │   ├── premium/
    │   │   ├── booking_capture.json
    │   │   ├── check_availability.json
    │   │   ├── confirm_booking.json
    │   │   ├── reschedule.json
    │   │   ├── cancel_appointment.json
    │   │   └── spanish_routing.json
    │   └── README.md
    ├── manifests/
    │   ├── hvac-standard.yaml
    │   ├── hvac-premium.yaml
    │   └── schema.json
    ├── flow_templates/
    │   ├── standard_template.json
    │   └── premium_template.json
    ├── agent_configs/
    │   ├── standard_master.json
    │   ├── premium_master.json
    │   └── client_registry.json
    ├── snapshots/
    │   ├── 2026-04-06_baseline-100/
    │   │   ├── standard_flow_v24.json
    │   │   ├── premium_testing_v11.json
    │   │   ├── components/*.json
    │   │   └── agents/*.json
    │   └── README.md
    ├── scripts/
    │   ├── snapshot.py
    │   ├── extract_components.py
    │   ├── build_agent.py
    │   ├── diff.py
    │   ├── promote.py
    │   ├── rollback.py
    │   ├── run_tests.py
    │   └── lib/
    │       ├── retell_client.py
    │       ├── flow_builder.py
    │       ├── manifest_loader.py
    │       └── validator.py
    ├── tests/
    │   ├── test_flow_builder.py
    │   ├── test_round_trip.py
    │   └── fixtures/
    ├── .env.example
    ├── requirements.txt
    └── README.md
```

### 3.2 Component file schema
Each component is a self-contained JSON file:
```json
{
  "id": "identify_call",
  "version": "1.0.0",
  "description": "Routes incoming calls to the right handler based on call reason",
  "applies_to": ["hvac", "plumbing", "electrical", "cleaning"],
  "start_node": "identify_call_start",
  "nodes": [
    {
      "id": "identify_call_start",
      "type": "conversation",
      "instruction": {"type": "prompt", "text": "..."},
      "edges": [ { "destination": "${EXIT}", "condition": "..." } ]
    }
  ],
  "exit_points": ["to_lead_capture", "to_emergency", "to_callback", "to_transfer", "to_end"],
  "metadata": {
    "last_edited": "2026-04-06",
    "last_editor": "dan",
    "test_coverage": "100%"
  }
}
```
Key design choices:
- `${EXIT}` placeholder → build script resolves to the correct destination in the parent flow
- `applies_to` → safety check — build fails if you include a component in a manifest for a vertical it doesn't support
- `version` → semver per component, for diff tracking

### 3.3 Manifest schema (per-agent)
```yaml
# manifests/hvac-standard.yaml
agent_name: "HVAC Standard"
agent_id: "agent_4afbfdb3fcb1ba9569353af28d"
flow_template: "standard_template.json"
vertical: "hvac"
tier: "standard"
model: "gpt-4.1"
model_type: "cascading"

global_prompt_file: "prompts/hvac_standard_global.md"

components:
  - id: identify_call
    source: shared/identify_call.json
    overrides:
      emergency_keywords: hvac/hvac_emergency_keywords.json
  - id: leadcapture
    source: shared/leadcapture.json
    overrides:
      fields: hvac/hvac_leadcapture_overrides.json
  - id: verify_emergency
    source: shared/verify_emergency.json
  # ... etc

flow_structure:
  start: greeting
  transitions:
    greeting -> identify_call
    identify_call -> [leadcapture, verify_emergency, callback, existing_customer, general_questions, transfer]
    verify_emergency -> [emergency_transfer, leadcapture]
    # ... etc

test_suite: "scenarios/hvac_standard_100.json"
baseline_pass_rate: 100
minimum_pass_rate: 95  # promote.py refuses to promote if tests fall below this
```

### 3.4 Build process (manifest → flow JSON)
1. Load manifest YAML
2. Load flow template (standard_template.json)
3. For each component in manifest: load source JSON, apply overrides, inline its nodes into the template with prefixed IDs (e.g. `identify_call__start`)
4. Resolve all `${EXIT}` placeholders using the `flow_structure.transitions` mapping
5. Validate resulting flow JSON against Retell's schema
6. Validate no orphaned edges, no unreachable nodes, no duplicate IDs
7. Output: single flow JSON ready to PATCH to Retell

### 3.5 Promotion pipeline
```
EDIT → BUILD → TEST → DIFF → PROMOTE → VERIFY → COMMIT
 │        │       │      │       │         │        │
 Git    build   run     show   PATCH to  call 3   tag in
 edit   script  100     diff   TESTING   canaries Git
        →JSON   scenarios      then      via
                against        MASTER    recorded
                TESTING                  scenarios
```

---

## 4. Phased Migration Plan

### PHASE 0 — Safety Net (new session, 30 minutes, read-only)
**Goal:** Guarantee we can always return to the 100% baseline.

**Steps:**
1. Create `retell-iac/` directory structure in `syntharra-automations` repo.
2. Run `snapshot.py` which:
   - Pulls Standard MASTER flow (v24) → `snapshots/2026-04-06_baseline-100/standard_flow_v24.json`
   - Pulls Premium TESTING flow (v11) → `snapshots/2026-04-06_baseline-100/premium_testing_v11.json`
   - Pulls all 11 shared components by ID → `snapshots/2026-04-06_baseline-100/components/*.json`
   - Pulls all agent configs → `snapshots/2026-04-06_baseline-100/agents/*.json`
   - Pulls Retell knowledge base configs
3. Commit to GitHub with message: `baseline: snapshot 100% Standard MASTER v24 + Premium TESTING v11`
4. Create Git tag `baseline-100-percent-20260406`
5. Verify snapshot by running a round-trip read: download tagged files, compare field-by-field to live Retell state. Must be byte-identical.

**Acceptance criteria:**
- [ ] All files present in `snapshots/2026-04-06_baseline-100/`
- [ ] Git tag created and pushed
- [ ] Round-trip verification passes
- [ ] No Retell writes occurred during phase

**Rollback:** N/A — this phase is read-only.

**Blocks next phase until:** Tag exists on remote GitHub. Human-verified.

---

### PHASE 1 — Component Extraction (new session, 2–3 hours, read-only)
**Goal:** Convert the 11 shared components + 7 orphan nodes into clean JSON files matching the target schema. No changes to Retell.

**Steps:**
1. Write `extract_components.py`:
   - Input: snapshot from Phase 0
   - Output: `components/shared/*.json` + `components/premium/*.json` + `components/hvac/*.json`
2. For each of the 11 shared components:
   - Fetch full component definition from Retell (`GET /get-conversation-flow-component/{id}` or extract from flow)
   - Normalize into target schema
   - Resolve exit points to placeholder `${EXIT}` names
   - Write to `components/shared/{name}.json`
3. For each of the 7 orphan nodes:
   - Extract inline definition from the flow JSON
   - Convert to component schema
   - Write to appropriate directory (shared/ or premium/)
4. Write `flow_templates/standard_template.json` by stripping all sub-agent node bodies from the snapshot flow and replacing with `${COMPONENT:name}` placeholders.
5. Same for Premium → `premium_template.json`.
6. Create manifests:
   - `manifests/hvac-standard.yaml`
   - `manifests/hvac-premium.yaml`
7. Extract HVAC-specific override data (emergency keywords, leadcapture field list, FAQ content) into `components/hvac/*.json`.

**Acceptance criteria:**
- [ ] All 11 shared components as JSON files
- [ ] All 7 orphan nodes converted to component files
- [ ] Manifests reference all components
- [ ] Flow templates contain only placeholders, no inline content
- [ ] Schema validation passes on all files

**Rollback:** N/A — only creates new files in Git. No Retell changes.

**Blocks next phase until:** Schema validation passes AND Dan reviews the component inventory.

---

### PHASE 2 — Build Script + Round-Trip Verification (new session, 4–6 hours)
**Goal:** Prove the build script can reconstruct the 100% baseline flow byte-for-byte (semantically).

**Steps:**
1. Write `scripts/lib/flow_builder.py`:
   - Load manifest
   - Load components + overrides
   - Resolve placeholders
   - Assemble final flow JSON
2. Write `scripts/build_agent.py`:
   - CLI: `build_agent.py --manifest hvac-standard --output build/standard.json`
   - Calls flow_builder, writes output
3. Write `scripts/diff.py`:
   - Semantic JSON diff (ignoring fields Retell auto-generates: `version`, `updated_at`, node position coordinates)
   - Outputs unified diff to terminal, exit code non-zero if differences found
4. Run round-trip test:
   - `build_agent.py --manifest hvac-standard --output build/standard.json`
   - `diff.py build/standard.json snapshots/2026-04-06_baseline-100/standard_flow_v24.json`
   - **Must be semantically identical.** Every instruction text, every edge, every transition condition matches.
5. Fix build script until round-trip passes.
6. Repeat for Premium manifest.
7. Write unit tests in `tests/test_round_trip.py` and add to CI.

**Acceptance criteria:**
- [ ] `build_agent.py` produces flow JSON from manifest
- [ ] Round-trip diff is clean for BOTH Standard and Premium
- [ ] Unit tests pass
- [ ] No Retell writes have occurred

**Rollback:** N/A — still read/build-only.

**Blocks next phase until:** Round-trip passes on both manifests AND Dan signs off on the diff report.

---

### PHASE 3 — Create Real TESTING Agents (new session, 1 hour)
**Goal:** Stand up genuine staging agents so we never edit MASTER directly.

**Steps:**
1. Create two new Retell agents via API:
   - `Standard TESTING v2` — new agent, new flow built from `hvac-standard.yaml` manifest
   - `Premium TESTING v2` — new agent, new flow built from `hvac-premium.yaml` manifest
2. Configure phone numbers (use free Retell test numbers, not production lines)
3. Assign agent IDs to `agent_configs/client_registry.json` under `tier: testing`
4. Update CLAUDE.md and REFERENCE.md with correct IDs
5. Delete stale references to the non-existent old TESTING agents

**Acceptance criteria:**
- [ ] Two new TESTING agents exist in Retell
- [ ] They are the ONLY agents pointing at flows generated from the `retell-iac` manifests
- [ ] MASTER agents remain on their original `conversation_flow_34d169608460` (v24)
- [ ] Phone numbers are test-only, not production

**Rollback:** Delete the two new agents via Retell API. No impact on MASTER.

**Blocks next phase until:** TESTING agents respond to a manual test call end-to-end.

---

### PHASE 4 — Test Suite Against TESTING Agents (new session, 2–4 hours)
**Goal:** Confirm the rebuilt (inline, no sub-agents) flow matches or beats the 100% baseline.

**Steps:**
1. Point existing `run_tests.py` at the new Standard TESTING v2 agent
2. Run full 100-scenario test suite
3. If pass rate < 100:
   - Capture every failing scenario transcript
   - Analyze failure mode: is it (a) build script bug, (b) missing override, (c) sub-agent behavior we didn't replicate inline, (d) genuine regression?
   - Fix in the component source files, rebuild, re-test
   - Repeat until 100% OR until we document every remaining failure as an acceptable regression
4. Run full 15-scenario Premium test suite against Premium TESTING v2
5. Compare: pass rate, average call latency, cost per call
6. Produce migration report in `docs/reports/2026-04-XX-migration-parity.md`

**Acceptance criteria:**
- [ ] Standard TESTING v2 passes ≥ 100/100 scenarios (must match baseline)
- [ ] Premium TESTING v2 passes ≥ baseline pass rate
- [ ] Average call latency is LOWER than current (expected: 3–8s reduction)
- [ ] Cost per call is LOWER than current (expected: ~40% reduction)
- [ ] No regression categories identified

**Rollback:** TESTING agents are throwaway. Delete them if broken.

**Blocks next phase until:** Parity report is signed off by Dan. **This is the hard gate — MASTER is not touched until parity is proven.**

---

### PHASE 5 — Promote to MASTER (new session, 1 hour, touches production)
**Goal:** Swap Standard MASTER's flow to the new generated version.

**Steps:**
1. Re-verify Phase 0 snapshot is intact on disk + GitHub
2. Create new empty Retell conversation flow: "HVAC Standard v25 (Git-IaC)"
3. PATCH it with the output of `build_agent.py --manifest hvac-standard`
4. Publish the new flow
5. Update Standard MASTER agent to point at new flow ID
6. Immediately run smoke test: 5 live scenarios via test harness
7. If any fail → `rollback.py baseline-100-percent-20260406` → reverts Standard MASTER to original `conversation_flow_34d169608460`
8. If all pass → let it run for 2 hours with monitoring
9. Run full 100-scenario test suite against MASTER
10. Pass rate must be ≥ 100%. If not, rollback.
11. Tag Git: `release-hvac-standard-v25-git-iac`

**Acceptance criteria:**
- [ ] Standard MASTER on new flow
- [ ] 100/100 scenarios still pass on MASTER
- [ ] No increase in error rate from Retell call logs
- [ ] Rollback path tested at least once in a dry run

**Rollback plan (tested before promotion):**
```bash
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master
# This PATCHes Standard MASTER back to conversation_flow_34d169608460 and re-publishes
```

**Blocks next phase until:** 24 hours of stable operation on the new flow.

---

### PHASE 6 — Premium MASTER Creation (new session, 2 hours)
**Goal:** Premium MASTER does not exist yet. Create it properly from the new IaC pipeline.

**Steps:**
1. Build Premium flow from `hvac-premium.yaml`
2. Create new Retell agent `HVAC Premium` → `agent_xxx_premium_master`
3. Attach phone number for Premium line
4. Run 15-scenario Premium test suite against MASTER
5. Update CLAUDE.md, REFERENCE.md, memory files
6. Tag Git: `release-hvac-premium-v1-git-iac`

**Acceptance criteria:**
- [ ] Premium MASTER exists in Retell
- [ ] 100% Premium scenarios pass
- [ ] Reference docs updated

**Rollback:** Delete the agent. No existing Premium MASTER to restore to.

---

### PHASE 7 — Self-Healing Loop Integration (new session, 3–4 hours)
**Goal:** Wire the existing prompt optimizer into the new pipeline so it writes to Git, not live flows.

**Steps:**
1. Modify `auto-fix-loop.py` to:
   - Write proposed fixes to component source files
   - Run `build_agent.py` → `run_tests.py` on TESTING agents
   - Only if pass → commit to Git + call `promote.py`
2. Add safety gates: max 3 patches per round, auto-rollback on regression
3. Document the new optimizer workflow in `docs/optimizer-git-pipeline.md`

**Acceptance criteria:**
- [ ] Optimizer never writes directly to Retell
- [ ] Every optimizer run produces a Git commit
- [ ] Regressions auto-rollback

---

### PHASE 8 — Client Rollout Tooling (future, not blocking)
**Goal:** When we have multiple paying clients, promote fixes to them in cohorts.

**Steps:**
1. `client_registry.json` lists all client agent IDs + cohort assignment (canary, wave1, wave2, all)
2. `promote.py --cohort canary` updates 5% of clients first
3. Monitor for 24h via Retell logs
4. `promote.py --cohort wave1` etc.
5. Automated rollback per-cohort if error rates spike

**Acceptance criteria (when we have clients):**
- [ ] Cohort-based promotion works
- [ ] Per-client rollback possible
- [ ] Monitoring dashboard shows per-client version

---

## 5. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Build script produces subtly different flow → regression | Medium | **Critical** | Phase 2 round-trip must be byte-identical before proceeding |
| 2 | Inline nodes behave differently than sub-agents at runtime | Medium | High | Phase 4 parity test on TESTING before touching MASTER |
| 3 | Premium TESTING test (tonight) invalidated by our snapshot | Low | Medium | Snapshot is read-only — cannot affect tonight's test |
| 4 | Lost 100% baseline due to human error | Low | **Critical** | Git tag `baseline-100-percent-20260406` + snapshot files immutable |
| 5 | Retell API changes break the build script | Low | High | Version-pin Retell API, run daily round-trip test in CI |
| 6 | Someone edits flow in Retell dashboard bypassing Git | Medium | High | Write policy into CLAUDE.md + add daily drift-detection job |
| 7 | Orphan nodes (Emergency Detection etc.) have subtle behavior we miss | Medium | High | Extract them 1:1 in Phase 1, don't try to "improve" during extraction |
| 8 | Knowledge base IDs lost in migration | Low | High | Explicitly preserve in manifest, verify in round-trip diff |
| 9 | Global prompt stripped or altered | Low | **Critical** | Keep global_prompt as a separate file, never touched by build script |
| 10 | Cost of running test suite during development | Low | Low | Use Retell test mode calls where possible |

---

## 6. Rollback Procedures

### 6.1 Full rollback to 100% baseline
```bash
cd retell-iac
python scripts/rollback.py --tag baseline-100-percent-20260406 --agent standard_master --confirm
# Verifies tag exists
# Fetches flow JSON from snapshot
# PATCHes Standard MASTER back to conversation_flow_34d169608460
# Publishes
# Runs 10-scenario smoke test
# Reports status
```

### 6.2 Rollback a single component
```bash
python scripts/rollback.py --component identify_call --to-version 1.0.0
# Reverts the component file in Git
# Rebuilds affected flows
# Promotes to TESTING agents first
# Waits for human confirmation before promoting to MASTER
```

### 6.3 Emergency stop
If anything looks wrong mid-promotion:
1. In Retell dashboard, manually point Standard MASTER back to `conversation_flow_34d169608460` (v24)
2. Publish immediately
3. This is the nuclear option — takes 30 seconds and always works because we never delete the original flow

---

## 7. Success Metrics

Measured against the 100% Standard MASTER baseline:

| Metric | Current | Target (post-migration) |
|---|---|---|
| Test suite pass rate | 100/100 | **≥100/100** (must not regress) |
| Average call latency (greeting → first meaningful turn) | Current value (to capture in Phase 0) | **−30% to −50%** |
| Number of LLM invocations per call | ~12+ (sub-agent handoffs) | **1** (inline context) |
| Cost per call | Current value (to capture) | **−40%** |
| Time to promote a component fix | Undefined / manual | **< 10 minutes end-to-end** |
| Ability to rollback | Manual in dashboard | **< 60 seconds via script** |

---

## 8. File / Command Checklist (for execution in new session)

### Files to create
- [ ] `retell-iac/` directory
- [ ] `retell-iac/scripts/snapshot.py`
- [ ] `retell-iac/scripts/extract_components.py`
- [ ] `retell-iac/scripts/build_agent.py`
- [ ] `retell-iac/scripts/diff.py`
- [ ] `retell-iac/scripts/promote.py`
- [ ] `retell-iac/scripts/rollback.py`
- [ ] `retell-iac/scripts/run_tests.py`
- [ ] `retell-iac/scripts/lib/retell_client.py`
- [ ] `retell-iac/scripts/lib/flow_builder.py`
- [ ] `retell-iac/scripts/lib/manifest_loader.py`
- [ ] `retell-iac/scripts/lib/validator.py`
- [ ] `retell-iac/manifests/hvac-standard.yaml`
- [ ] `retell-iac/manifests/hvac-premium.yaml`
- [ ] `retell-iac/manifests/schema.json`
- [ ] `retell-iac/flow_templates/standard_template.json`
- [ ] `retell-iac/flow_templates/premium_template.json`
- [ ] `retell-iac/components/shared/*.json` (12 files)
- [ ] `retell-iac/components/hvac/*.json` (3 files)
- [ ] `retell-iac/components/premium/*.json` (6 files)
- [ ] `retell-iac/tests/test_round_trip.py`
- [ ] `retell-iac/tests/test_flow_builder.py`
- [ ] `retell-iac/requirements.txt`
- [ ] `retell-iac/README.md`
- [ ] `retell-iac/.env.example`

### Git tags to create
- [ ] `baseline-100-percent-20260406` (Phase 0)
- [ ] `retell-iac-scaffold-complete` (end of Phase 1)
- [ ] `retell-iac-round-trip-verified` (end of Phase 2)
- [ ] `retell-iac-testing-agents-live` (end of Phase 3)
- [ ] `retell-iac-parity-proven` (end of Phase 4)
- [ ] `release-hvac-standard-v25-git-iac` (end of Phase 5)
- [ ] `release-hvac-premium-v1-git-iac` (end of Phase 6)

### Retell writes (only in Phases 3, 5, 6)
- Phase 3: Create 2 new TESTING agents + 2 new flows (low risk, throwaway)
- Phase 5: Create 1 new flow for Standard MASTER, swap pointer, publish (medium risk, fully rollback-able)
- Phase 6: Create Premium MASTER agent + flow (low risk, greenfield)

---

## 9. Open Questions for Dan (resolve before Phase 0)

1. **GitHub repo location** — should `retell-iac/` go in `syntharra-automations` (recommended, central) or its own repo?
2. **Phone numbers for TESTING v2 agents** — use the existing demo line (+12292672271) or provision new Retell test numbers?
3. **Knowledge base** — Standard flow currently references `knowledge_base_ids`. Do we treat these as IaC-managed or leave them as shared Retell resources?
4. **CI/CD** — should round-trip tests run on every PR to `retell-iac/`? (Recommend: yes, via GitHub Actions.)
5. **Standard TESTING 404** — was the old agent deleted, or is the ID wrong? Needs investigating so we don't miss a lesson from how it was broken.
6. **How was 100% achieved** — if Standard TESTING doesn't exist, the 100% test must have run against MASTER directly. Confirm the test pipeline so we replicate it exactly against TESTING v2.

---

## 10. What to Do in the New Session

**First message to start with:**

> Dan: Execute Phase 0 of the Retell Git-IaC Migration Plan (`retell-git-iac-migration-plan.md` in the Cowork workspace). Read-only snapshot of the 100% Standard MASTER baseline plus Premium TESTING. Commit to `syntharra-automations` under `retell-iac/snapshots/2026-04-06_baseline-100/` and create Git tag `baseline-100-percent-20260406`. No Retell writes. Report when done, then wait for approval before Phase 1.

This gives the next Claude session a clean, narrow, unambiguous task that cannot break anything, with the full plan available for context.

---

## 11. Sign-off Gates

Each phase requires explicit Dan approval before proceeding:

- [ ] Phase 0 complete → Dan confirms snapshot verified → proceed to Phase 1
- [ ] Phase 1 complete → Dan reviews component inventory → proceed to Phase 2
- [ ] Phase 2 complete → Dan reviews round-trip diff → proceed to Phase 3
- [ ] Phase 3 complete → Dan test-calls new TESTING agents → proceed to Phase 4
- [ ] Phase 4 complete → Dan reviews parity report → **HARD GATE** → proceed to Phase 5
- [ ] Phase 5 complete → 24h stability → proceed to Phase 6
- [ ] Phase 6 complete → Premium MASTER live → proceed to Phase 7 (optimizer wiring)

**End of plan document.**
