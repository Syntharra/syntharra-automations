# Retell Native Refactor — Thin Processor Spec

**Date:** 2026-04-07  
**Scope:** Reduce custom n8n call processors to minimal required logic by leveraging Retell's native post-call analysis fields.

---

## 1. Native Fields Available in Retell Webhook

### Directly Available (No Derivation)
- `call_id` — Unique call identifier
- `agent_id` — Agent/flow identifier
- `from_number`, `to_number` — Phone numbers
- `transcript` — Full text transcript
- `transcript_object` — Timestamped utterances
- `recording_url` — Audio file URL
- `public_log_url` — Retell dashboard link
- `disconnection_reason` — Enum (28+ types)
- `duration_ms` — Call length in milliseconds
- `latency` — Percentiles (p50, p90, p95, p99) across ASR, LLM, TTS, KB, E2E
- `call_cost` — Itemized cost structure
- `call_analysis` — Object containing:
  - `user_sentiment` — Enum (Negative, Positive, Neutral, Unknown)
  - `call_successful` — Boolean
  - `call_summary` — High-level summary text
- `custom_analysis_data` — Custom extraction schema (fully customizable in Retell UI)

### Scrubbed Versions (PII-removed)
- `scrubbed_transcript_with_tool_calls`
- `scrubbed_recording_url`

### Additional Metadata
- `metadata` — Custom key-value storage
- `llm_token_usage` — Token counts and averages
- `in_voicemail` — Boolean

---

## 2. Custom Derivations We Still Need

These are **NOT** available natively in Retell and must remain custom:

| Field | Source | Logic | Used For |
|---|---|---|---|
| `client_id` | `agent_id` → lookup `hvac_standard_agent` | SQL join by agent_id | Supabase insert, HubSpot routing |
| `company_name` | Client lookup result | From agent record | Lead card, notifications |
| `is_repeat_caller` | 30-day phone history | `SELECT COUNT(*) FROM hvac_call_log WHERE from_number=X AND call_timestamp >= NOW()-30d` | Repeat detection, skip duplicate follow-ups |
| `repeat_call_count` | Same phone history | Count result | Repeat tracking |
| `is_lead` | `custom_analysis_data.lead_score >= 5` AND NOT in spam/wrong_number | Threshold logic | Routing (log only if is_lead=true) |
| `call_cost_cents` | `call_cost.total_duration_unit_price * (duration_ms / 60000)` | Unit price × duration | Cost tracking |
| `duration_seconds` | `duration_ms / 1000` | Simple division | Readability, dashboards |

---

## 3. Minimum Viable Processor (Thin Spec)

Remove all field remapping; pass Retell fields through directly. Keep only:

1. **Idempotency Check** — Prevent duplicate inserts via call_id deduplication
2. **Client Resolution** — agent_id → Supabase hvac_standard_agent lookup
3. **Repeat Caller Scan** — 30-day phone history query
4. **Lead Threshold Filter** — Only insert if is_lead=true
5. **Partition-Aware Insert** — call_tier = 'Standard' or 'Premium', write to hvac_call_log
6. **Pass-Through Mapping** — All native Retell fields → Supabase columns as-is
7. **Notifications** — Slack, HubSpot (downstream business logic)

**Node Reduction Target:**
- Standard: 11 nodes → 7 nodes (remove Extract, Parse, re-extract logic)
- Premium: 12 nodes → 8 nodes

---

## 4. Refactored Node Structure (Standard)

```
Webhook: call_analyzed event
  ↓
Dedup Check: call_id exists in hvac_call_log?
  ├─ YES → response-only, exit
  └─ NO → continue
     ↓
Client Lookup: agent_id → hvac_standard_agent
  ↓
Repeat Caller: from_number last 30 days
  ↓
Is Lead?: lead_score >= 5 AND NOT [spam, wrong_number]
  ├─ FALSE → exit
  └─ TRUE → continue
     ↓
Supabase Insert: 
  - Pass native Retell fields directly
  - Add: client_id, company_name, is_repeat_caller, repeat_count
  - Add: call_tier='Standard'
     ↓
HubSpot Note + Slack Alert (parallel)
```

**Premium identical except call_tier='Premium' + client Slack webhook.**

---

## 5. Database Mapping (Pass-Through)

| Supabase Column | Retell Webhook Field | Transform |
|---|---|---|
| call_id | call_id | Direct |
| agent_id | agent_id | Direct |
| from_number | from_number | Direct |
| to_number | to_number | Direct |
| transcript | transcript | Direct |
| duration_seconds | duration_ms | duration_ms / 1000 |
| recording_url | recording_url | Direct |
| public_log_url | public_log_url | Direct |
| disconnection_reason | disconnection_reason | Direct |
| latency_p50_ms | latency.e2e.p50 | Direct |
| call_cost_cents | call_cost + duration_ms | (unit_price × ms/60000) × 100 |
| retell_sentiment | call_analysis.user_sentiment | Direct |
| call_successful | call_analysis.call_successful | Direct |
| retell_summary | call_analysis.call_summary | Direct |
| (all custom_analysis_data fields) | custom_analysis_data.* | Direct passthrough |
| client_id | (lookup) | agent_id → hvac_standard_agent |
| company_name | (lookup) | client_id result |
| is_repeat_caller | (query) | from_number 30d history |
| repeat_call_count | (query) | count result |
| is_lead | lead_score (custom_analysis_data) | score >= 5 AND NOT [spam, wrong_number] |
| call_tier | (hardcoded) | 'Standard' or 'Premium' |

---

## 6. Custom Analysis Data Strategy

**Current:** Workflows extract individual fields from `custom_analysis_data` and log them separately.

**Recommendation:** Store entire `custom_analysis_data` object as JSON in Supabase, then add **specific extraction columns** for frequently queried fields only:
- `caller_name`, `caller_phone`, `caller_address`
- `service_requested`, `job_type`, `urgency`
- `lead_score`, `is_hot_lead`
- `booking_success`, `appointment_date`

**Benefit:** Schema stays flexible for Retell prompt changes; no n8n re-config needed.

---

## 7. Estimated Improvements

| Metric | Current | Target | Reduction |
|---|---|---|---|
| Standard nodes | 11 | 7 | 36% |
| Premium nodes | 12 | 8 | 33% |
| Code nodes | 6 | 3 | 50% |
| Retell field re-mapping | 40+ lines | 0 | 100% |
| Custom logic required | 7 types | 4 types | 43% |

**Remaining custom logic:** Dedup check, client lookup, repeat scan, lead threshold, notifications.

---

## 8. Migration Path

1. Create new workflows (Standard-v2, Premium-v2) with thin spec
2. Deploy to test webhook path (webhook-test/*)
3. Run parallel validation: old vs. new output parity on 100 test calls
4. Swap prod webhooks (zero downtime via n8n versioning)
5. Archive old workflows after 7-day confirmation period

---

## 9. Post-Refactor: Future Enhancements

Once thin processors are live:
- Add Retell Analytics API polling for dashboards (vs. re-deriving in n8n)
- Leverage `latency.p95` and `llm_token_usage` for cost optimization alerts
- Use `transcript_object` timestamps for call heat map visualization
- Store `scrubbed_transcript_with_tool_calls` for HIPAA-compliant archives

---

**Prepared by:** Claude Agent  
**Status:** Research Complete — Ready for Implementation Phase  
**Next Step:** Build thin processor workflows and validate parity with existing output.
