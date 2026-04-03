# TASKS.md — Syntharra Automations
> Updated 2026-04-03

## Status Legend: ✅ Done | 🔄 In Progress | ⏳ Pending | 🚫 Blocked

## Active Sprint

### ✅ Slack Integration (completed 2026-04-03)
All 6 workflows wired to Slack. Internal email nodes paused in place.
Workflows: xKD3ny6kfHL0HHXq, 4Hx7aRdzMl5N0uJP, Wa3pHRMwSjbZHqMC, Kg576YtPM9yEacKn, STQ4Gt3rH8ptlvMi, kz1VmwNccunRMEaF

### ⏳ Claude Code — Agentic Automation (NEXT)
Build Claude Code integration for session-based agentic tasks.
See: CLAUDE_CODE.md, tools/claude-code/
Requires: Anthropic API key in vault (service_name='anthropic', key_type='api_key')
Cost: ~$0.05/run on Sonnet 4 (claude-sonnet-4-20250514)
Files already scaffolded: session-start.py, run-e2e.sh, self-heal.sh, session-end.sh

### ⏳ Item 4 — Scheduled Autonomous Work
n8n cron + Claude API for daily autonomous checks (transcript analysis, health scores)
Blocked on: Anthropic API key in vault

### ⏳ Live Smoke Test
First real Stripe payment → Jotform → agent live → Slack notification chain
Dan to trigger when ready

### ⏳ Telnyx SMS
Replace Twilio stub in call processors with live Telnyx when approval received
AI evaluation approval pending

### ⏳ Agent Simulator — Remaining Test Groups
boundary_safety and info_collection groups untested
social engineering (#74) and falsify record (#76) fixes needed in Global Prompt

### ⏳ Ops Monitor
Paused — unpause at go-live

## Agents (DO NOT TOUCH MASTERS)
- Std MASTER: agent_4afbfdb3fcb1ba9569353af28d
- Prem MASTER: agent_9822f440f5c3a13bc4d283ea90
- Std TESTING: agent_731f6f4d59b749a0aa11c26929
- Prem TESTING: agent_2cffe3d86d7e1990d08bea068f
