# retell-iac/scripts — fleet management for 1000+ clients

## Files
- `register.py` — Adds a single client to `client_agents` Supabase registry. Called by onboarding workflow after Retell agent clone.
- `rollout.py` — Fleet-wide prompt update. Rate-limited (5 req/s default), exponential backoff, idempotent, fully logged.
- `canary.py` — 5% canary selection, 2h health window vs baseline, auto-revert on >5pp drop.

## Required env vars
```
SUPABASE_URL=https://hgheyqwnrcvwtgngqdnq.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
RETELL_API_KEY=...
SLACK_WEBHOOK_URL=...     # for canary.py alerts
ROLLOUT_RPS=5             # optional, default 5
```

## Standard rollout sequence (for any new prompt version)
```
# 1. Pick canary cohort (5% of fleet)
python canary.py --tag v2026.04.07 --tier std --pick

# 2. Push prompt to canary only
python rollout.py --tag v2026.04.07 --base-prompt prompts/std_v24.json --tier std --canary-only --execute

# 3. Wait 2h, then health check
python canary.py --tag v2026.04.07 --tier std --check
#   exit 0 = healthy, exit 1 = revert, exit 2 = insufficient volume

# 4a. If healthy: promote and run full fleet
python canary.py --tag v2026.04.07 --tier std --promote
python rollout.py --tag v2026.04.07 --base-prompt prompts/std_v24.json --tier std --execute

# 4b. If unhealthy: revert
python canary.py --tag v2026.04.07 --tier std --revert
```

## Why this scales to 1000+
- **Idempotent**: Re-running rollout.py picks up only rows not yet at target version.
- **Rate-limited**: Default 5 req/s × 4 calls/agent × 1000 agents ≈ 13 minutes for full fleet.
- **Backoff**: 429s do not crash the run.
- **Logged**: Every action recorded in `client_agents_rollout_log` for forensics.
- **Per-tier**: Standard and Premium roll out independently.
- **Canary-gated**: No prompt change ever touches >5% of fleet without 2h of real-call evidence.
- **Source of truth**: `client_agents` table is the single registry — no spreadsheets, no JSON files.
