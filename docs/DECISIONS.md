# Decisions — Syntharra Automations

> **The "why" behind architecture choices.**
> Not rules. Not failures. The reasoning that shaped the system.
> When making adjacent decisions, read this first — it tells you the intent, not just the state.
> Updated when significant decisions are made. Read at every session start.

_Last updated: 2026-04-11_

---

## D1 — Single product: HVAC Standard at $697/mo (2026-04-09)

**Decision:** Retired Premium tier. One agent, one onboarding flow, one price point.

**Why:** Complexity tax was too high pre-revenue. Two tiers = two test suites, two onboarding workflows, two prompt branches — double maintenance, double failure surface with zero paying clients. Ship one thing perfectly, not two things adequately.

**Implications:**
- Never build per-tier logic. Any new feature is Standard-only until there's a real reason to fork.
- Never suggest "we could add a Premium version." That conversation is post-revenue.
- All Supabase `client_subscriptions` rows use `plan_type = 'standard'`. CHECK constraint enforces this.
- Premium agent IDs in REFERENCE.md are legacy artifacts — the product is Standard.

---

## D2 — Retell owns call data. Supabase owns billing state. (2026-04-09)

**Decision:** No per-call storage in Supabase. Dashboard reads Retell directly via `list-calls`. Monthly billing reads Retell at invoice time. Supabase holds only: client configs, subscriptions, billing cycles, overage charges, website leads, and one immutable `monthly_billing_snapshot` rollup per client per month.

**Why:** Per-call Supabase storage was a speculative data warehouse play that added 17 tables, RLS complexity, and partition maintenance — before a single paying client asked for it. Retell's `list-calls` API covers billing windows. The snapshot is the only durable copy needed for dispute defense.

**Implications:**
- Never add a Supabase table to store call-level data. Call data = read from Retell at request time.
- `monthly_billing_snapshot`: written once at invoice time, never updated.
- Dashboard call data path: `POST /webhook/retell-calls` → n8n proxy (`Y1EptXhOPAmosMbs`) → Retell API.

---

## D3 — Scale-to-1000 invariant: repo holds MASTER only, Supabase holds clients (2026-04-09)

**Decision:** The repo never contains per-client files. All client-specific data lives in Supabase (`client_agents`, `client_integrations`, `syntharra_vault`).

**Why:** At 1000 clients, per-client repo files make `git clone` unusable and code review impossible. MASTER template = every client inherits improvements automatically. Customisation is data, not code.

**Implications:**
- Writing `clients/acme-hvac.json` or any per-client file → stop. That's a Supabase row.
- New client customisation options → new column in `client_agents`, not a new file.

---

## D4 — n8n self-hosted on Railway only. n8n MCP permanently banned. (2026-04-09)

**Decision:** Syntharra's only n8n instance is `https://n8n.syntharra.com` (Railway). The `mcp__claude_ai_n8n__*` MCP tools are banned — they talk to a cloud n8n account we don't use and produce phantom results.

**Why:** Early sessions hit the cloud instance via MCP, making changes with no effect on our actual Railway workflows. The leaked API key was scrubbed and rotated. Parallel access to two n8n instances = non-deterministic outcomes.

**Implications:**
- All n8n ops: `https://n8n.syntharra.com/api/v1/...` with `X-N8N-API-KEY` from vault.
- No `DELETE /api/v1/workflows/{id}` ever — hard delete, no recovery (see D9).

---

## D5 — Phase 0 pilot: 200-minute free trial, not 14-day (2026-04-11)

**Decision:** Pilot is scoped to 200 minutes of AI receptionist time. Expires at 200 minutes OR Day 14, whichever comes first.

**Why:** HVAC call volume varies wildly. A slow week = 14-day trial with almost no calls = the client never sees the product work. 200 minutes guarantees meaningful exposure. It's also a clean upsell moment — client burns through minutes and wants more.

**Funnel:** `syntharra.com/start` → VSL → JotForm `261002359315044` → 200-min pilot → $697/mo

**Implications:**
- Never build a "14-day calendar trial." The product is 200 minutes.
- `pilot_mode` hidden field in JotForm distinguishes pilot from paid signups.
- `tools/pilot_lifecycle.py`: `create_pilot`, `convert_pilot_to_paid`, `expire_pilot`, `send_winback`.
- Brevo email sequence: Day 0, 3, 7, 12, 14, 16, 30 (days since signup, not minutes).

---

## D6 — Cold email paused behind COLD_EMAIL_ENABLED flag (2026-04-11)

**Decision:** Cold outbound email is built but gated. Will not run until `COLD_EMAIL_ENABLED=true` in Railway env.

**Why:** Cold email at scale requires warmed sending domains, bounce handling, unsubscribe flow, CAN-SPAM compliance — none of which are built. Running cold email prematurely burns domain reputation. Priority is inbound SEO/content until the funnel works.

**Implications:**
- Do not enable without: warmed domain, unsubscribe flow, bounce handler, CAN-SPAM footer.
- Infrastructure exists (`tools/send_cold_outreach.py`, `tools/build_cold_outreach.py`) — it's paused, not removed.

---

## D7 — Social video parked until CRO business verification (2026-04-11)

**Decision:** TikTok Business, Meta (FB+IG), Higgsfield, Blotato all deferred. $0/mo committed.

**Why:** TikTok Business and Meta both require a CRO (Companies Registration Office) business ID for B2B advertising. Without it, ad accounts get rejected.

**Implications:**
- Plan exists at `docs/superpowers/plans/2026-04-11-autonomous-content-team-implementation.md` — preserve but don't build.
- YouTube via personal Google OAuth technically possible but deliberately deferred.

---

## D8 — Marketing is fully autonomous. Dan approves plans via Slack only. (2026-04-11)

**Decision:** Marketing content loop runs autonomously on cron. Dan approves plans via Slack. He does not manually trigger anything.

**Why:** An AI SaaS company whose own marketing requires human intervention every step defeats the product thesis.

**Implications:**
- Never build a "Dan presses button to publish" flow.
- `MARKETING_TEAM_ENABLED=false` gates actual posting until VSL+Stripe+Telnyx+CRO ready.
- All marketing tools check `is_marketing_enabled()` from `tools/content_preview_mode.py` before posting.

---

## D9 — No DELETE on n8n public API, ever (2026-04-09)

**Decision:** `DELETE /api/v1/workflows/{id}` permanently banned. Hard-delete, no recovery.

**Why:** Accidentally hard-deleted `rGrnCr5mPFP2TIc7` (Google Calendar dispatcher) while probing. Restored from a 30-second-old backup. The n8n UI "Archive" button uses an internal endpoint with soft-archive semantics — the public API DELETE does not.

**Archive procedure instead:** Backup JSON → deactivate → rename `[ARCHIVED-YYYY-MM-DD]` → ask Dan to click "Archive" in n8n UI.

---

## D10 — Stripe stays test mode until pre-launch checklist §2 (ongoing)

**Decision:** All Stripe objects are test-mode only until Dan provides the live secret key.

**Why:** Test-mode charges nothing real. Going live-mode without explicit authorisation either fails silently or charges real cards incorrectly.

**Implications:**
- Test product: `prod_UJb4pQDwyQ7lgW` / price: `price_1TKxruECS71NQsk8yspZnj2B`
- Live migration: create live-mode product+price, swap key in vault, update `pilot_lifecycle.py` price ID reference.
- Telnyx phone provisioning also blocked — both are Dan-owned pre-launch unblockers.

---

## Infrastructure decisions (pre-2026-04)

| Date | Area | Decision | Reason |
|---|---|---|---|
| Pre-2026 | Phone | Telnyx, replacing Twilio | Better pricing at scale. Twilio active during Telnyx evaluation approval. |
| Pre-2026 | Email delivery | Brevo (was SMTP2GO) | Reliable deliverability, transactional + marketing in one, simpler API |
| Pre-2026 | Hosting | Railway, NOT Vercel/Heroku | n8n needs persistent disk; Vercel is stateless-only |
| Pre-2026 | DB | Supabase | Postgres, built-in RLS, good API, free tier covers pre-launch |
| Pre-2026 | Voice AI | Retell AI, NOT Bland/Vapi | Best conversation quality for trade business use cases |
| Pre-2026 | Market | HVAC USA first | Largest trade vertical; standardised workflows make expansion fast |
| Pre-2026 | Checkout | Separate `syntharra-checkout` repo | Isolates billing code; pricing page updates don't touch main infra |
| 2026-04 | Docs | Old guides archived to docs/archive/ | Reduce context noise; completed guides add no active-session value |

## Security decisions

| Date | Area | Decision | Reason |
|---|---|---|---|
| 2026-04-02 | Secrets | All keys via `syntharra_vault` Supabase table | Prevents exposure in repos |
| 2026-04-02 | Repos | `syntharra-automations` + `syntharra-website` public; others private | automations/website need public read; no secrets stored in these files |
| 2026-04-09 | API dumps | Treat n8n/Retell full-object dumps as secret material | n8n workflow API embeds credentials inline in HTTP node headers |
