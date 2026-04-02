# ⛔ SUPERSEDED — DO NOT USE THIS FILE

> **This file is no longer the source of truth. It is stale and will not be updated.**
>
> Last valid update: ~2026-03-31. Everything since then lives in the new context system.

## Session Rule (read this first)

If you are a Claude session and you read this file, **stop and follow this instead:**

1. Fetch `Syntharra/syntharra-automations/CLAUDE.md` — master brief
2. Fetch `Syntharra/syntharra-automations/docs/TASKS.md` — current state + next actions
3. Load only the relevant context files from `docs/context/`:
   - `AGENTS.md` — Retell agents, phone numbers, Jotform forms
   - `WORKFLOWS.md` — all 32 n8n workflow IDs (audited 2026-04-02)
   - `SUPABASE.md` — table names (Premium merged into Standard tables)
   - `INFRA.md` — Railway service IDs, URLs, all 7 services
   - `STRIPE.md` — price IDs, coupons (TEST MODE)
   - `ARTIFACTS.md` — Claude artifact file map
   - `LAUNCH.md` — pre-launch checklist

## Why this file was replaced

This file grew to 47,000+ characters and became impossible to keep accurate.
Stale data in this file was causing Claude to use wrong workflow IDs, wrong table names,
and wrong agent IDs. It has been replaced with small focused files that are
queried from live systems and kept under 80 lines each.

**Do not update this file. Do not read the content below. Fetch CLAUDE.md instead.**

---
