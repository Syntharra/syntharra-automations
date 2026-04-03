# Syntharra — Claude Code Operating Rules
> Claude Code reads this file at session start.
> It is the execution-layer companion to CLAUDE.md.
> All rules in CLAUDE.md apply here without exception.

## Role of Claude Code in this project
Claude Code is the **execution and verification layer**:
- Run E2E tests automatically after any agent or workflow change
- Self-healing loop: test → diagnose → fix → re-test → repeat until green
- Enforce session log push at close
- Verify GitHub pushes completed

Claude Code does NOT make architectural decisions, strategic choices, or design calls.
Those happen in the Claude.ai chat. Claude Code executes and verifies what was decided there.

## Session startup
Always run first — gets full project context:
```bash
python3 tools/session-start.py
```

## After any Retell agent or prompt change
```bash
python3 tools/post-change-verify.py --scope standard
# or
python3 tools/post-change-verify.py --scope premium
```

## Session close — mandatory, no exceptions
```bash
python3 tools/session-close.py --topic "your-topic-here"
```

## Hard limits — burned in, not negotiable
| Rule | Detail |
|---|---|
| TESTING only | Never touch MASTER agents (Standard: agent_4afbfdb3fcb1ba9569353af28d / Premium: agent_9822f440f5c3a13bc4d283ea90) |
| E2E gate | No production push without passing E2E |
| Loop cap | Self-healing loop max 10 iterations then stop + report |
| Fail limit | 3 consecutive failures on any step = stop, surface to Dan |
| No deletes | Never delete or recreate a Retell agent |
| Read first | Always fetch current file before any edit |
| Session log | Must push docs/session-logs/ entry before closing |
| No rewrites | Always str_replace on fetched content, never overwrite from scratch |

## Agent quick reference
| Agent | ID | Rule |
|---|---|---|
| Standard MASTER | agent_4afbfdb3fcb1ba9569353af28d | NEVER TOUCH |
| Premium MASTER | agent_9822f440f5c3a13bc4d283ea90 | NEVER TOUCH |
| Standard TESTING | agent_731f6f4d59b749a0aa11c26929 | All test work here |
| Premium TESTING | agent_2cffe3d86d7e1990d08bea068f | All test work here |
