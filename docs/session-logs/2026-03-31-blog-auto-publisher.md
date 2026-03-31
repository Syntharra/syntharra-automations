# Session Log: 2026-03-31 — Blog Auto-Publisher

## What Was Built
Full automated blog publishing system — zero cost, fully hands-off.

## Components
### Supabase
- New table: `blog_topics` (id, slug, title, tag, hero_emoji, hero_gradient, target_keyword, brief, status, created_at, published_at)
- Index: `blog_topics_status_idx` on status column
- 41 topics seeded across HVAC, Plumbing, Electrical, AI, Operations, Growth, Pest Control/Cleaning, Seasonal
- Migration applied via Supabase MCP

### n8n Workflow: Blog Auto-Publisher
- ID: `j8hExewOREmRp3Oq`
- Status: ACTIVE
- Schedule: Mon/Wed/Fri at 9:00 AM (cron: `0 9 * * 1,3,5`)
- Model: Groq `llama-3.3-70b-versatile` (free tier — existing API key)
- Pipeline: Fetch topic → Generate article → Parse response → Build brand-compliant HTML → Push article to GitHub → Update blog.html index card → Mark published in Supabase

### First Article Published (live test)
- Title: "Why HVAC companies lose 40% of their revenue after 5PM"
- URL: https://syntharra.com/blog/hvac-after-hours-answering.html
- Topic ID 1 marked as published in Supabase
- Blog card injected into blog.html

### GitHub
- Workflow JSON stored at: `syntharra-automations/blog/blog-auto-publisher.json` (secrets redacted)
- Schema SQL stored at: `syntharra-automations/blog/blog-topics-schema.sql`

## Cost
- $0 — Groq free tier (used existing `gsk_` key already in syntharra_vault)

## Adding More Topics
INSERT into blog_topics with status='queued'. Workflow auto-picks oldest queued row per run.
At 3x/week, 40 remaining topics = ~13 weeks of automated publishing.
