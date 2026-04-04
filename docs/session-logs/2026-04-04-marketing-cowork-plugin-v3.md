# Session Log: 2026-04-04 — Marketing Cowork Plugin (v3)

## Task
Rebuilt the marketing system as a proper Cowork plugin with each agent as its own skill.

## Changes from v2
- Added **Video Content agent** — TikTok, Instagram Reels, YouTube Shorts scripts with hook patterns, caption templates, recording tips
- Restructured as a **Cowork plugin** — plugin.json manifest, skills/, commands/, .mcp.json
- Added **"What You Need to Start" checklist** — social accounts + phone + CapCut. That's it.
- Added **4 commands**: startup, weekly-plan, report, batch-content

## Plugin Structure (14 files)
```
marketing/cowork-plugin/
├── .claude-plugin/plugin.json
├── .mcp.json
├── README.md
├── skills/
│   ├── prospector/SKILL.md
│   ├── outreach/SKILL.md
│   ├── content-engine/SKILL.md
│   ├── video-content/SKILL.md
│   ├── conversion-optimizer/SKILL.md
│   ├── intelligence/SKILL.md
│   └── competitor-watch/SKILL.md
└── commands/
    ├── startup.md
    ├── weekly-plan.md
    ├── report.md
    └── batch-content.md
```

## 7 Agents (Skills)
1. Prospector — finds HVAC businesses, scores, feeds pipeline
2. Outreach — 3-email cold sequences, personalized, CAN-SPAM compliant
3. Content Engine — blog (2/week), social (5/week), newsletter (bi-weekly)
4. Video Content — TikTok/Reels/Shorts scripts with hooks and captions
5. Conversion Optimizer — funnel analysis, A/B testing, landing pages
6. Intelligence — weekly brief directing all agents based on data
7. Competitor Watch — monthly competitive intelligence

## No Infrastructure Changes
Plugin/prompt work only. All files pushed to GitHub.
