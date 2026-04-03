# Session Log — 2026-04-03 — ops-monitor-alert-fixes

## Session Goal
Fix two active alert emails received by Dan:
1. [CRITICAL] Jotform API Unreachable — HTTP 429
2. [WARNING] Railway Checkout Deploy Issue — status: unknown

## Root Cause Analysis

### Issue 1: Jotform HTTP 429
- Monitor ran every 15 min, made 5 Jotform API calls per run
- Per-form staleness loop fetched /submissions for each form (2 calls)
- Orphan detection block RE-fetched the same /submissions (2 more calls)
- Plus 1 /user connectivity check = 5 calls/run × 4 runs/hour = 20 calls/hour
- Jotform free tier rate limit triggered → HTTP 429 → false CRITICAL alert

### Issue 2: Railway status 'unknown'
- Railway GraphQL API changed in 2025-Q4: `input:` filter on `deployments` deprecated
- Query returned 0 edges silently → `deploy` was undefined → `deploy?.status` = undefined
- Code used `deploy?.status || 'unknown'` as alert message and `deployOk = status === 'SUCCESS'`
- undefined ≠ 'SUCCESS' → alert fired every 5 minutes

## Fixes Applied

### jotform.js (syntharra-ops-monitor)
- Cache `formSubmissions` map during first fetch loop
- Orphan detection reuses cached map — zero additional Jotform API calls
- Total calls per run: 3 (1 /user + 1 per form) instead of 5
- Commit: b3364482b63efc4ee2eeab554a24cdcc2ac62de0

### infrastructure.js (syntharra-ops-monitor)  
- Updated Railway GQL query: `where: { serviceId: { equals: ... } }` + `orderBy: CREATED_AT DESC`
- Added TRANSIENT states set: DEPLOYING, INITIALIZING, BUILDING, QUEUED, WAITING
- Transient states treated as OK (not alertable)
- Only alerts on FAILED, CRASHED, or genuinely missing deployments
- Commit: 36d1c03ce162a58707e76a1ddf960effa7355651

## Files Changed
- `Syntharra/syntharra-ops-monitor` src/monitors/jotform.js
- `Syntharra/syntharra-ops-monitor` src/monitors/infrastructure.js
- `Syntharra/syntharra-automations` docs/FAILURES.md (2 rows appended)
- `Syntharra/syntharra-automations` docs/TASKS.md (updated)
- `Syntharra/syntharra-automations` docs/session-logs/2026-04-03-ops-monitor-alert-fixes.md (this file)

## Verification
- jotform.js: no duplicate fetch loop confirmed ✅
- infrastructure.js: old `input:` filter removed, TRANSIENT set present ✅
- Both committed and pushed to GitHub ✅

## Note on Ops Monitor
Service is currently PAUSED on Railway (intentional — test mode alert spam prevention).
Fixes will take effect when unpaused at go-live. Alert emails will stop once Railway
auto-deploys the updated code on unpause.
