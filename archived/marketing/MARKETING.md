# Syntharra — Agentic Marketing System
> This is a standalone system. It is NOT a task in TASKS.md — it has its own roadmap and state.
> Owner: Dan Blackmore | System: Cowork Marketing Plugin (18-agent architecture)

---

## What this is
A fully agentic marketing team built as a Cowork plugin. It runs as an autonomous multi-agent system
with 18 specialist sub-agents orchestrated by a Marketing Manager agent. It operates independently
of the Syntharra product pipeline (Retell, n8n, Supabase). Think of it as a separate company function
that happens to share the same GitHub repo for now.

## Current State
| Component | Status |
|---|---|
| APEX Blueprint (9-section strategy) | ✅ DELIVERED |
| 18-agent architecture design | ✅ DELIVERED |
| 12-week HVAC launch calendar | ✅ DELIVERED |
| Cost model + projections | ✅ DELIVERED |
| Cowork plugin (14 files) | ✅ DELIVERED — `marketing/cowork-plugin/` |
| 7 agents as skill files | ✅ DELIVERED |
| 4 plugin commands | ✅ DELIVERED |
| MCP connectors | ✅ DELIVERED |
| Startup checklist | ✅ DELIVERED |

## Next: n8n Backend Workflows (6 new agents)
These 6 agents need n8n workflows + Supabase tables before they can operate:

| Agent | Function | Priority |
|---|---|---|
| SEO Agent | Organic search, content indexing | 1 |
| Paid Acquisition Agent | Google/Meta ad management | 2 |
| Email Nurture Agent | Drip sequences, follow-up | 3 |
| Competitor Intelligence Agent | Market monitoring | 4 |
| Brand Guardian Agent | Brand safety + compliance | 5 |
| Retention/Expansion Agent | Upsell, churn prevention | 6 |

## Plugin Setup (Dan action items)
- [ ] Set up social accounts (LinkedIn, Instagram, Facebook)
- [ ] Install Cowork plugin from `marketing/cowork-plugin/`
- [ ] Run `/syntharra-marketing:startup` to initialise

## File Locations
- Plugin files: `marketing/cowork-plugin/` (14 files)
- Blueprint: `docs/agentic-marketing-blueprint.md` (or session log 2026-04-03)
- Skill files: `skills/syntharra-marketing-SKILL.md`, `skills/syntharra-marketing-manager/`
- Strategy: `docs/growth-engine-strategy.md`, `docs/lead-machine-master-plan.md`

## Design Principles
- Single-point-of-failure from short-form video eliminated — multi-channel by design
- Multi-touch attribution across all channels
- 18 agents, each owning one domain — no cross-contamination
- APEX Analysis Framework used for all strategic documents in this system
