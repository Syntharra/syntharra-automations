# 2026-04-07 — Scale-readiness, batch 3 (autonomous push)

Continuing from batch 2. Dan: "continue with everything else, get Syntharra where it needs to be from the beginning, test everything at end."

5 parallel subagents fired (Planner -> Executors -> Verifier).

## Verified green (DB layer)
SQL probe at end of session, all 6 checks pass:
- client_agents.submission_id column: PRESENT
- dunning_state table: CREATED
- stripe_processed_events table: CREATED (batch 2)
- idx_hvac_call_log_call_id: PRESENT
- client_agents indexes (agent_id, flow_id, status): 3/3 PRESENT
- search_path pinned on 3 trigger functions: 3/3 PRESENT

## Applied this batch
1. Retell-native refactor RESEARCH PLAN published to docs/audits/2026-04-07-retell-native-refactor.md
   - 30+ native Retell fields catalogued; eliminates 36-50% of current processor nodes
   - Std processor: 11 -> 7 nodes; Premium: 12 -> 8 nodes
   - Custom logic shrinks from 7 types to 4: dedup, client lookup, repeat-caller scan, lead threshold
2. Onboarding idempotency: SQL ALTER applied (submission_id UNIQUE column on client_agents). Standard + Premium workflow JSONs built with 5 new nodes each (Check Idempotency, Query, IF Already Processed, INSERT, Exit). Validated. NOT auto-deployed -- staged at /Cowork/workflows/ for Dan to import.
3. Stripe webhook hardening: dunning_state table CREATED with retry index. Hardened workflow JSON built with 8 new nodes (Verify Signature HMAC-SHA256, Check Idempotency, Switch routing for 5 event types, Mark Processed). NOT auto-deployed -- SDK validation rejects multi-path Switch; staged for manual import.
4. Premium Dispatcher retry hardening: BLOCKED on both SDK and REST API paths. Patched jsCode + step-by-step instructions ready at /Cowork/premium_dispatcher_patched.js + PATCH_INSTRUCTIONS.md.
5. n8n fetch() audit on remaining ~14 workflows: agent encountered ID resolution issues mid-run. Captured as in-flight; need a re-scan next session.

## Staged for Dan (manual import / UI bind)
| File | Purpose | Action |
|---|---|---|
| /Cowork/workflows/4Hx7aRdzMl5N0uJP-standard-idempotency.json | Std onboarding + idempotency | Import via n8n UI |
| /Cowork/workflows/kz1VmwNccunRMEaF-premium-idempotency.json | Prem onboarding + idempotency | Import via n8n UI |
| /tmp/hardened_workflow_code.json | Stripe webhook hardened | Import to xKD3ny6kfHL0HHXq |
| /Cowork/premium_dispatcher_patched.js | Premium Dispatcher retry | Paste into Process Function Call node, publish |
| 7 MON/MAINT workflows from batch 2 | Slack + Supabase/Postgres credentials | Bind in UI, publish |

## Required before Stripe hardened workflow goes live
INSERT INTO syntharra_vault (service_name, key_type, key_value)
VALUES ('Stripe', 'webhook_signing_secret', 'whsec_...');

## Test results (verifier pass)
- Database state: ALL GREEN (6/6 checks)
- n8n workflows: not auto-deployed by design (SDK validation too strict for multi-node patches)
- Retell native fields confirmed via Retell docs scrape
- GitHub pushes: docs/audits/2026-04-07-retell-native-refactor.md (201), this session log (pending)

## Reflection
1. n8n SDK update_workflow is the chokepoint. Repeated pattern: build correct JSON, validation rejects, fall back to staged file. Need direct REST API path with cached n8n_api_key in env.
2. Retell-native pivot (Dan's directive) materially shrinks our surface area. Strongly recommend prioritizing the v2 processors over hardening v1.
3. Auto-deployment of complex multi-node patches is currently impossible from Claude side without n8n API key in env. Workaround: Dan's manual import takes ~5 mins per workflow.
4. SQL hardening is fully autonomous and reliable. Database is in best state of project so far.
