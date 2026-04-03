# Session Log — 2026-04-03 — Agentic Learning Workflows

## What was built
- Daily Transcript Analysis (`ofoXmXwjW9WwGvL6`) — rebuilt to full pipeline using Retell built-in call_analysis + Groq
- Weekly Health Score (`ALFSzzp3htAEjwkJ`) — rebuilt with real metrics + Slack digest
- Zero extra cost — uses Groq (already in stack), no Anthropic API key needed

## Self-improvement loop
1. Call ends → Retell webhook → hvac_call_log
2. 2am daily: Groq analyses each call for quality, loops, frustration, missed leads
3. Results saved to transcript_analysis table
4. Issues auto-written to FAILURES.md on GitHub
5. Next session: I read FAILURES.md → already know what broke → faster fixes

## Live tests
- Groq analysis pipeline: ✅ end-to-end tested
- Real call call_a2b8861017b2eca scored 100/100 ✅
- Slack digest sent and approved ✅
- transcript_analysis table: 2 rows confirmed ✅

## Key learnings
- transcript_analysis real columns differ from SQL scaffold — see infra skill
- client_health_scores has no ON CONFLICT — use DELETE+INSERT pattern
- Vault key for Slack: service_name='Slack', key_type='webhook_url'
