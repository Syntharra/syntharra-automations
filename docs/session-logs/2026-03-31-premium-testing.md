# Session Log — Premium Agent Testing

**Date:** 2026-03-31
**Goal:** Improve Premium agent pass rate using same methodology as Standard

---

## Starting State
- Flow: conversation_flow_dba336752525 v24
- Last batch: test_batch_2fa56b3367f4 — 40% real pass rate (2/5)
- Stub tools active on all 4 flow tools

## What Was Done

### Diagnostics
- Ran full 8-case batch at v24 → 4/5 = 80% (already improved from 40% due to prior work)
- Split emergency vs non-emergency batches to isolate failure
- Read full flow JSON to identify root causes

### Root Causes Found
1. **CO alarm not routing to emergency** — `identify_call` emergency edge only listed "gas smell", not "carbon monoxide/CO alarm"
2. **`Say:` prefix in `check_availability_node`** — instruction text used `Say: "Let me just check..."` which can cause agent to literally say "Say:"
3. **No CRITICAL RULES in global prompt** — Premium agent lacked the explicit never-break rules that fixed Standard from 58% → 73%

### Fixes Applied (v24 → v26)
1. Added `carbon monoxide, CO alarm, CO detector, smoke smell, flooding` to emergency edge condition and finetune examples in `identify_call_node`
2. Changed `Say: "Let me just check..."` → `Tell the caller: "Let me just check..."` in `check_availability_node`
3. Added to global prompt:
   - CRITICAL RULES section (one question per turn, no diagnosis, no Say:, CO/gas as immediate emergency, detail readback, Mike Thornton, abuse protocol)
   - PROACTIVE INFORMATION SHARING section (financing, warranty, promo, diagnostic fee)
   - IF CALLER RELUCTANT section (scripted privacy objection response)

### Results
| Batch | Version | Pass | Fail | Error | Real Rate |
|---|---|---|---|---|---|
| test_batch_2fa56b3367f4 | v24 | 2 | 3 | 3 | 40% |
| test_batch_fa72e4c1e3ec | v24 | 4 | 1 | 3 | 80% |
| test_batch_59808d6e0e8d | v26 | 5 | 0 | 3 | **100%** |

## New Test Case IDs (v26)
| ID | Scenario |
|---|---|
| test_case_0cb558b0ea41 | Prem - 1. Standard AC repair - cooperative caller |
| test_case_b6eb250edfc2 | Prem - 2. Heating repair request |
| test_case_b84712310670 | Prem - 3. New AC installation inquiry |
| test_case_4b23d55c2a6b | Prem - 4. Maintenance tune-up request |
| test_case_1066e6042749 | Prem - 5. Duct cleaning request |
| test_case_182ef55f6496 | Prem - 6. Emergency - AC failure extreme heat |
| test_case_082d55250d47 | Prem - 7. Emergency - gas smell |
| test_case_c310d79fa4c2 | Prem - 8. Emergency - carbon monoxide alarm |

## State Left In
- Flow v26 published and active
- Stub tools still on all 4 tools (live URL: https://n8n.syntharra.com/webhook/retell-integration-dispatch)
- **Restore live tools before going live** — PATCH all 4 tools back to live URL then publish

## Skills Updated
- skills/syntharra-testing/SKILL.md — sha 2bb322ab
