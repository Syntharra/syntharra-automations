# Session Log — 2026-04-03 — Jotform 429 Fix

## Summary
Short session. Diagnosed and fixed Jotform 429 that was persisting from earlier session testing.

## Root Cause
Jotform free tier resets at midnight UTC, not rolling 24h. E2E burst testing from earlier in the day burned through the daily quota. The 429 was self-resolving in ~2 hours — no emergency.

Secondary issue: backup poller at 15min was consuming 192 calls/day, leaving less headroom on test-heavy days.

## Changes Made
| What | Where | Detail |
|---|---|---|
| Poll interval 15min → 60min | n8n `LF8ZSYyQbmjV4rN0` | Reduces poller calls 192 → 48/day |
| Graceful 429 skip handler | n8n `LF8ZSYyQbmjV4rN0` | Returns `rate_limited/skipped` instead of erroring |
| Lookup window 30min → 60min | n8n `LF8ZSYyQbmjV4rN0` | Matches new poll interval |
| FAILURES.md row added | GitHub | Root cause documented |
| Infrastructure skill updated | GitHub | Jotform limits + n8n SDK forbidden patterns |

## Learnings
- Jotform 429 with no Retry-After = daily quota exhaustion, not per-minute throttle
- n8n SDK forbids `new` expressions — must use factory functions (`workflow()`, `trigger()`, `node()`)
- Always `validate_workflow` before `update_workflow`

## Open Items (unchanged)
- Personalities fix (move to node-leadcapture instruction)
- Run personalities-run3 + remaining simulator groups
- Wire +18129944371 to Standard Template
- Live smoke test
