# Session Log — 2026-04-02 — Skills Auto-Sync via GitHub

## Change
Eliminated the /mnt/skills/user/ dependency entirely.
Skills are now fetched directly from GitHub at session start — always current, zero upload step.

## How it works
```python
def load_skill(name):
    return fetch(f"skills/{name}-SKILL.md")

# Load only what the task needs:
retell_skill = load_skill("syntharra-retell")
```

## Token impact (measured)
- Average skill: ~3,156 tokens
- Typical session (2 skills): ~10,000 tokens total = 5% of context window
- Cost: ~$0.03/session — negligible

## What Dan needs to do
Delete all skills from Claude.ai project settings — they are now dead weight.
Claude.ai → this project → Settings → Knowledge — delete each skill file.

## Files changed
- CLAUDE.md (skills section rewritten — fetch pattern documented)
- docs/LEARNING.md (structural gap marked resolved)
- docs/FAILURES.md (skill sync fix logged)
- docs/TASKS.md (upload action items removed, replaced with delete instruction)
