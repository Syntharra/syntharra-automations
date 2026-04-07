date | area | what failed | root cause | fix applied | skill updated
2026-04-07 | n8n SDK | update_workflow rejects multi-path Switch + complex Code patches | SDK validator stricter than n8n REST API | fall back to staged JSON for manual import; next session use raw REST PUT with X-N8N-API-KEY | yes (next session: cache n8n key in env)
2026-04-07 | Postgres ALTER batch | search_path ALTER on ensure_call_log_partition | function never deployed; audit recommendation was speculative | re-ran batch excluding missing function; 3 valid functions pinned | no
2026-04-07 | n8n REST fallback (Premium retry) | n8n_api_key not readable from agent context | vault read scope mismatch | Dan needs to wire key into env or run patch manually | no
