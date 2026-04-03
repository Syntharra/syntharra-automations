# Syntharra — Claude Code Entry Point
> Read this file first at the start of every Claude Code session.
> Same engineer, same rules, same memory as the chat sessions.

## On start — run this
```bash
python3 tools/claude-code/session-start.py
```

## You are the same engineer
CLAUDE.md is the master brief. All non-negotiables carry over exactly.
TESTING agents only. E2E must pass before any production push.
3-strike stop rule applies. Max 10 self-healing iterations.

## Session close checklist
```bash
./tools/claude-code/session-end.sh "topic-description"
```
This enforces: E2E passed, changes pushed, TASKS.md updated, session log written.

## Available tools
| Script | Purpose |
|---|---|
| `tools/claude-code/session-start.py` | Load context, print open tasks |
| `tools/claude-code/session-end.sh` | Enforce close checklist, push session log |
| `tools/claude-code/run-e2e.sh` | Run E2E test suite (TESTING only) |
| `tools/claude-code/self-heal.sh` | Self-healing loop (TESTING only, max 10 iter) |
| `tools/claude-code/verify-push.sh` | Confirm GitHub push landed |
