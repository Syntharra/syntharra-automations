date | area | what failed | root cause | fix applied | skill updated
2026-04-07 | n8n SDK | update_workflow rejects multi-path Switch + complex Code patches | SDK validator stricter than REST API | use raw REST PUT with X-N8N-API-KEY | yes (syntharra-infrastructure)
2026-04-07 | Postgres ALTER batch | search_path ALTER on ensure_call_log_partition | function never deployed | re-ran excluding missing function | no
2026-04-07 | syntharra_vault upsert | ON CONFLICT failed | no unique constraint matching pair | DELETE + INSERT pattern | yes
2026-04-07 | n8n raw REST PUT | initial PUT 400 with extra fields | n8n PUT only accepts name/nodes/connections/settings | strip body to allowed keys | yes
2026-04-07 | Slack credential discovery | n8n public API has no /credentials endpoint | n8n API limitation | use bot token + chat.postMessage HTTP nodes | yes
2026-04-07 | RLS audit | 4 sensitive tables had no RLS + 17 anon USING(true) policies wide open | initial migrations skipped policy hardening | enable RLS + drop anon + srv_all_* replacements; preserve website_leads INSERT | yes
