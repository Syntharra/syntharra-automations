# Syntharra Automations

Operational automation code for the Syntharra AI Receptionist platform.

## Structure

```
syntharra-automations/
  shared/
    retell-publisher/     # Headless browser service to publish Retell agents
    supabase-migrations/  # All Supabase schema migrations
    n8n-workflows/        # Exported n8n workflow JSON files
  hvac-standard/
    prompt-builder.js     # n8n Build Retell Prompt node code
    conversation-flow.json # Master conversation flow structure
    call-processor.js     # n8n call processor node code
  hvac-premium/           # Coming soon
  plumbing-standard/      # Coming soon
```

## Repos
- `syntharra-checkout` — Pricing page + Stripe checkout only (Railway)
- `syntharra-automations` — All operational automation code (this repo)
- `syntharra-website` — Public website

## Local Claude plugin launcher
Use the workspace launcher to start Claude with all local plugins found in `plugins/`.

- `start-claude-with-plugins.ps1` — PowerShell launcher that discovers `.claude-plugin` folders and passes `--plugin-dir` for each one.
- `start-claude-with-plugins.cmd` — Windows wrapper for double-click or shortcut launch.
- `.vscode/tasks.json` includes `Start Claude with local plugins` so you can run it from VS Code.

To launch:
1. Run `start-claude-with-plugins.cmd` from the repo root.
2. Or use the VS Code task named `Start Claude with local plugins`.

If you start Claude some other way, those local repo plugins will not be loaded automatically unless that process uses this launcher.
