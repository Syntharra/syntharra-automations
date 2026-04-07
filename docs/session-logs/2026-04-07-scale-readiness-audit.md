# 2026-04-07 — Scale-readiness audit (continued)

Second batch of autonomous fixes after initial audit. Dan reminder: lean on Retell native analytics rather than hardening custom call processors.

## Applied
- SQL: pinned search_path on update_updated_at, update_updated_at_column, update_hvac_premium_agent_updated_at. Skipped ensure_call_log_partition (function does not exist in DB — remove from audit recommendation).
- SQL: created idx_hvac_call_log_call_id (unique-ish lookup hot path).
- n8n: 5 workflows had raw fetch() replaced with this.helpers.httpRequest — Eo8wwvZgeDm5gA9d (Newsletter Unsubscribe), b9xRG7wtqCZ5fdxo (Premium Dispatcher Calendly), BxnR17qUfAb5BZCz (Premium Dispatcher Jobber), msEy13eRz66LPxW6 (Premium Dispatcher HubSpot), PavRLBVQQpWrKUYs (Email Intelligence Inbox Scanner). 13 calls converted total.
- n8n: 6 monitoring workflows + 1 partition maintenance workflow created (DRAFT — see below).

## Created (DRAFT, awaiting Dan to wire credentials in UI then publish)
| ID | Name | Needs |
|---|---|---|
| l45IpkWypMDC96DJ | MON: Per-Client Call Success Rate | Slack creds + Supabase auth on HTTP node |
| n4wSnx4z1kJWmkqP | MON: Retell Error Rate Spike | Slack + Supabase auth |
| vIBQ2c13bWuhZGky | MON: n8n Critical Workflow Failures | Slack + n8n API bearer token |
| L3MyzOeXW37qZxdS | MON: Stripe Webhook Delivery Failures | Slack + Supabase auth |
| 4oeS60f5tpBopYHu | MON: Supabase Pool Saturation | Slack + Supabase auth (RPC get_connection_stats must be created) |
| VNwwajvBg68EdsJU | MON: Next-Month Partition Exists | Slack + Supabase auth (RPC partition_exists_next_month, create_next_partition needed) |
| YTNnym92HjdNKHul | MAINT: hvac_call_log Monthly Partition Pre-Creation | Postgres credential + Slack |

All 7 are . They will not run until Dan binds credentials in the n8n UI and publishes.

## Blocked
- Premium Integration Dispatcher (73Y0MHVBu05bIm5p) Jobber/Calendar retry hardening: n8n SDK update_workflow validation rejected the patch. Need manual UI edit. Helper functions (jobberCallWithRetry, gcalWithRefresh) drafted in audit notes.
- 14 unscanned n8n workflows for fetch() — onboarding + Stripe deliberately skipped (high-risk surface).

## Re-scoped per Dan
- DROPPED: hardening custom call processors Kg576YtPM9yEacKn / STQ4Gt3rH8ptlvMi.
- ADDED: research task — audit Retell post_call_analysis / call_analysis / transcript fields and map what custom processors duplicate. Plan to thin custom processing to a passthrough into hvac_call_log + Retell-native enrichment.

## Reflection
1. Wrong assumption: ensure_call_log_partition function exists. It does not — audit recommendation was based on function name found in another file, never deployed. Fixed by dropping from batch.
2. n8n SDK update_workflow is brittle — minimal-diff retry strategy needed for any Code-node-only edit. Workaround: Dan does manual UI edit OR we use n8n REST API directly with raw PUT.
3. Pattern: monitoring workflows created via SDK CANNOT bind named credentials — they must be wired in UI. Future workflow-creation tasks should output a credential-binding checklist alongside the workflow ID.
