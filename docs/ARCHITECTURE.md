# Syntharra — Architecture Decision Record (ADR)
> Created: 2026-04-03 | Owner: Claude (senior autonomous engineer)
>
> This file captures the REASONING behind architectural choices — not just what we built,
> but WHY, what we considered, what we traded off, and when the decision should be revisited.
>
> DECISIONS.md records what was decided (one-liner).
> ARCHITECTURE.md records why it was decided (full reasoning).
>
> Format per entry:
>   ## [date] — [area]: [decision title]
>   **Problem:** what we were solving
>   **Options considered:** what alternatives existed
>   **Chose:** what we went with
>   **Because:** the actual reasoning
>   **Trade-offs accepted:** what we gave up
>   **Revisit if:** condition that would change this decision

---

## Pre-2026 — Voice AI: Retell over Bland / Vapi

**Problem:** Needed a voice AI platform that could handle inbound calls for trade businesses with natural conversation quality.

**Options considered:** Bland AI, Vapi, Retell AI

**Chose:** Retell AI

**Because:** Retell had the best conversation quality in direct testing across all three. Trade businesses have callers with strong accents, noisy environments, and urgent emotional states — Retell handled these better. Retell also has a structured conversation flow (node-based) that maps naturally to the branching call logic (emergency → lead capture → existing customer etc). Bland and Vapi use more freeform prompt-only approaches that are harder to make deterministic for production call handling.

**Trade-offs accepted:** Retell is more expensive per minute than Bland. Locked into Retell's API for agent management — can't easily switch without recreating all agent configs.

**Revisit if:** Bland/Vapi conversation quality matches Retell AND their pricing advantage becomes material at scale (1000+ client minutes/mo).

---

## Pre-2026 — Infrastructure: Railway over Vercel / Heroku

**Problem:** Needed hosting for n8n (workflow engine) and supporting services.

**Options considered:** Vercel, Heroku, Railway, self-hosted VPS

**Chose:** Railway

**Because:** n8n requires a persistent filesystem (SQLite/Postgres for workflow state, execution history). Vercel is serverless/stateless — n8n cannot run on it. Heroku has persistent dynos but is significantly more expensive. Railway gives persistent services, Postgres, Redis, and easy env var management in one platform at a competitive price. The Railway GraphQL API also allows programmatic service management (pause/restart/deploy) without manual dashboard steps.

**Trade-offs accepted:** Railway blocks all SMTP ports (25, 465, 587, 2525) — forces SMTP2GO REST API for all email. Railway auto-deploy on GitHub push is unreliable — sometimes need to trigger via API mutation.

**Revisit if:** Railway pricing increases significantly at scale, or if n8n is replaced by a hosted workflow engine.

---

## Pre-2026 — Email: SMTP2GO over SendGrid / Mailgun

**Problem:** Needed transactional email delivery for automated workflows (welcome emails, call summaries, alerts).

**Options considered:** SendGrid, Mailgun, SMTP2GO, AWS SES

**Chose:** SMTP2GO

**Because:** SMTP2GO has reliable deliverability with simpler API and good pricing for transactional volume. More importantly: Railway blocks all SMTP ports — SMTP2GO's REST API works over HTTPS port 443 which Railway allows. This constraint ruled out anything requiring direct SMTP connection.

**Trade-offs accepted:** Less ecosystem tooling than SendGrid. SMTP2GO is less well-known so less documentation/community support.

**Revisit if:** Deliverability issues emerge, or email volume grows to where SES economics make sense (>100k/mo).

---

## Pre-2026 — Database: Supabase over Firebase / PlanetScale

**Problem:** Needed a database for client config, call logs, subscriptions, and vault.

**Options considered:** Firebase (Firestore), PlanetScale, Supabase, Railway Postgres only

**Chose:** Supabase

**Because:** Relational data (client config, agent IDs, subscriptions) maps poorly to Firestore's document model. Supabase gives Postgres (relational), a built-in REST API (no ORM needed in n8n HTTP nodes), Row Level Security for vault access, and a free tier that covers pre-launch comfortably. The Supabase vault table pattern (`syntharra_vault`) gives a consistent, auditable way to store and retrieve API keys without hardcoding them.

**Trade-offs accepted:** Supabase free tier has connection limits — at scale, need to upgrade. Supabase is a single point of failure for all credential lookups.

**Revisit if:** Supabase pricing becomes prohibitive at scale, or connection pooling becomes a bottleneck.

---

## 2026-03 — Agent Architecture: One Agent Per Client (Cloned)

**Problem:** Multiple HVAC clients need their own AI receptionist with their own company name, phone number, and business info.

**Options considered:**
1. Single shared agent with dynamic variables injected per call
2. One agent per client, cloned from template

**Chose:** One agent per client, cloned from template

**Because:** Phone number binding in Retell is per-agent — one number can only be assigned to one agent. A shared agent would require the correct company info to be injected at call time via dynamic variables, which adds latency and a point of failure (what if the lookup fails mid-call?). Per-client agents are isolated — one client's prompt fix can't accidentally affect another client. Cloning from a template agent means all clients start from a known-good baseline, and template improvements can be propagated selectively.

**Trade-offs accepted:** Agent sprawl at scale (500 clients = 500 agents). Propagating prompt improvements requires updating each agent individually. More complex to manage programmatically.

**Revisit if:** Retell introduces multi-tenant agent features, or agent count reaches a level where bulk prompt management becomes operationally painful.

---

## 2026-03 — Data Model: Single Table for Standard + Premium Clients

**Problem:** Standard and Premium clients have overlapping config fields (agent_id, company_name, phone) but Premium has extras (notification_email_2/3, Google Calendar OAuth).

**Options considered:**
1. Separate tables (`hvac_standard_agent`, `hvac_premium_agent`)
2. Single table with plan_type column and nullable Premium-only fields

**Chose:** Single table (`hvac_standard_agent`) with plan_type column

**Because:** Simplifies all reporting and cross-plan queries — no JOINs needed. The Premium-only fields are nullable and clearly labelled (notification_email_2, notification_sms_2, etc). When expanding to new verticals (plumbing, electrical), the same table pattern works — just add a vertical column. Confirmed by Dan 2026-04-02.

**Trade-offs accepted:** Table name (`hvac_standard_agent`) is misleading for Premium clients — historical naming, not worth migrating. Nullable columns add some schema noise.

**Revisit if:** Premium config diverges significantly from Standard (10+ Premium-only columns), at which point a separate table makes query clarity worth the JOIN cost.

---

## 2026-03 — Retell: Never Delete/Recreate Agents — Always Patch

**Problem:** Agents need to be updated frequently (prompt changes, voice changes, flow updates).

**Decision:** Never DELETE or RECREATE a Retell agent. Always PATCH in place.

**Because:** A Retell agent_id is the foreign key connecting: Retell (phone number binding), Supabase (client config row), n8n call processor (routes by agent_id), and call history. Deleting an agent destroys the phone number binding AND all call history — Retell has no versioning or backup. Recreating creates a new agent_id that doesn't match the Supabase row, breaking the call processor routing. The PATCH API (`PATCH /update-agent/{id}`) updates any field without touching the phone binding or history.

**Trade-offs accepted:** If an agent gets into a broken state that can't be fixed via patch (hasn't happened yet), recovery is complex.

**Revisit if:** Retell introduces versioning/backup features that make recreation recoverable.

---

## 2026-04 — Prompt Architecture: Code Node for Caller Style Detection

**Problem:** Global prompt was 15,339 chars. Personality handling instructions at the bottom of the prompt were being ignored by the LLM (below effective attention window). Personality pass rate was stuck at ~47%.

**Options considered:**
1. Move personality table to top of global prompt
2. Inject personality instructions into each call node
3. Use a Retell code node to detect caller style and inject a short, targeted note into the active node

**Chose:** Code node (`call_style_detector`) inserted between identify_call and leadcapture

**Because:** Option 1 still results in a huge prompt that the LLM must carry the full weight of on every turn. Option 2 requires updating every node when personality handling changes. Option 3 keeps the detection logic in code (deterministic regex + heuristics), produces a short `caller_style_note` string (30-50 chars), and injects it at the TOP of the leadcapture node where the LLM will actually see it. Result: 76% prompt reduction (15,339 → 3,601 chars), ~1,400 tokens per call (was ~3,800), personality pass rate 47% → 87%+.

**Trade-offs accepted:** Code node is UI-only creatable (can't create via REST API as of 2026-04-03 — whitelist hasn't been updated). Must be patched via API after UI creation. Adds one node to the flow (minor latency).

**Revisit if:** Retell improves LLM context handling so long prompts are reliably followed, making the code node unnecessary.

---

## 2026-04 — CRM: HubSpot over Custom Admin Dashboard

**Problem:** Pre-launch had a custom-built admin dashboard (`syntharra-admin` repo) for tracking clients, calls, and pipeline. Too much maintenance overhead for a single-person operation pre-revenue.

**Options considered:**
1. Keep maintaining custom dashboard
2. Move to HubSpot (existing tool, already familiar)
3. Airtable or Notion as lightweight CRM

**Chose:** HubSpot

**Because:** HubSpot's free CRM tier covers all pre-launch needs (contacts, deals, pipeline stages, notes). The custom admin dashboard required ongoing development and had no mobile access. HubSpot has a documented API that n8n can write to directly — all workflows can push contact + deal data automatically. This gives Dan a real-time CRM view without any dashboard maintenance burden. HubSpot also has email sequences, meeting booking, and analytics built in — useful for go-to-market.

**Trade-offs accepted:** HubSpot free tier has limits (5 email sequences, etc). All client data now lives in two places (Supabase for agent config, HubSpot for CRM) — requires keeping them in sync. HubSpot nodes added to all workflows are non-blocking (try/catch) so HubSpot outages don't break the pipeline.

**Revisit if:** HubSpot pricing becomes significant at scale, or if the Supabase + HubSpot sync becomes a maintenance burden.

---

## 2026-04 — Skills: GitHub-Fetched over /mnt Upload

**Problem:** Skills stored in Claude.ai project (/mnt/skills/user) went stale when the GitHub repo was updated. Required manual re-upload via UI — no API to push updates programmatically.

**Options considered:**
1. Keep /mnt skills, build a reminder system to re-upload
2. Fetch skills directly from GitHub at session start
3. Embed skills in CLAUDE.md

**Chose:** Fetch from GitHub at session start

**Because:** GitHub has an API — skills can be updated programmatically from any session and are immediately available next session without any manual step. /mnt has no API. Option 3 (embedding in CLAUDE.md) would make CLAUDE.md too large and mix reference data with operating instructions.

**Trade-offs accepted:** Each session requires GitHub API calls to fetch skills (adds ~2-3 seconds startup). Network dependency — if GitHub is down, skills can't be loaded (extremely rare).

**Revisit if:** Claude.ai introduces a programmatic API for /mnt project files.

---

## 2026-04 — Docs: Small Context Files over One Large project-state.md

**Problem:** Originally had a single large `project-state.md` file (~12,000 tokens) loaded every session. Most sessions only needed 500-1,000 tokens of context.

**Options considered:**
1. Keep single large file
2. Split into domain-specific context files, load only what's needed

**Chose:** Split into `docs/context/` files (AGENTS.md, WORKFLOWS.md, STRIPE.md, etc, each ~500 tokens)

**Because:** Loading 12,000 tokens of context for a Retell-only task wastes context window and slows down response quality (more noise). Each domain file is ~40 lines. For any given task, only 1-3 files are needed (~500-1,500 tokens total). This also means context files can be updated independently without touching unrelated data.

**Trade-offs accepted:** More files to maintain — easy to let them fall out of sync. Requires Claude to know which files to load for which tasks (handled by the routing table in CLAUDE.md).

**Revisit if:** Context file count exceeds 15-20, at which point the routing overhead may exceed the loading savings.

---

## 2026-04 — Lead Generation: Instantly.ai over Direct SMTP Sequences

**Problem:** Cold outbound email to HVAC businesses requires sending from a warm domain with deliverability protection, reply tracking, and automated follow-up sequences.

**Options considered:**
1. Build custom sequence logic in n8n with SMTP2GO
2. Use Instantly.ai (dedicated cold email platform)

**Chose:** Instantly.ai (pending — not yet built)

**Because:** Instantly.ai handles domain warming, sending reputation, automatic unsubscribe, reply detection, and sequence management — all critical for cold outbound that custom n8n logic would need to replicate. Using a secondary sending domain (getsyntharra.com or similar) via Instantly.ai protects the primary syntharra.com sending reputation if deliverability issues occur.

**Trade-offs accepted:** Additional $30/mo cost. Data lives in Instantly.ai, not Supabase — requires webhook integration for hot-lead detection. Dependency on a third-party platform.

**Revisit if:** Volume grows to where building in-house is cheaper, or Instantly.ai deliverability issues emerge.

---

## [2026-04-04] — Simulator: Why the premium simulator uses a different Groq model than standard

**Decision:** Premium agent simulator uses `meta-llama/llama-4-scout-17b-16e-instruct` (30k TPM). Standard uses `llama-3.3-70b-versatile` (12k TPM).

**Why:** The premium conversation flow has 18 nodes vs 12 for standard. The simulator must include ALL node instruction texts in the agent system prompt — they define how the agent behaves at each stage of the call and are as important to test as the global prompt. This makes the premium prompt ~24,748 chars (~6,000 tokens). With 12 API calls per scenario, `llama-3.3-70b` (12k TPM) is exhausted on scenario #1. `llama-4-scout` has 30k TPM and handles the full prompt cleanly.

**What was tried and rejected:** Stripping node instructions to reduce token count. Rejected — invalid test. Node instructions define booking flow, callback handling, emergency routing etc. Testing without them means testing an incomplete agent.

**Rule:** If TPM limit is hit on the simulator, upgrade the model's TPM — never reduce prompt content.

---

## [2026-04-04] — Simulator: Always run in Claude Code, never in this chat

**Decision:** All simulator runs happen in Claude Code, not in the Claude.ai chat interface.

**Why:** The bash_tool in Claude.ai chat has a hard ~55s execution timeout. A single booking scenario takes 60–90s (6–8 turns × 2 API calls × ~5s each). There is no way to run booking scenarios within the timeout regardless of optimisations. Claude Code has no timeout wall and can run all 95 scenarios unattended.

**Rule:** Never attempt to run the simulator inside this chat. Start Claude Code, git pull, run the group.

---

## [2026-04-04] — Simulator: Groq replaces OpenAI for all simulator runs

**Decision:** Both simulators (standard + premium) use Groq API (`api.groq.com/openai/v1`) instead of OpenAI.

**Why:** The OpenAI key (`sk-proj-...` in vault) is on a free tier with 10,000 requests/day (RPD). Running 95 Premium scenarios + 80 Standard scenarios = ~175 scenarios × ~15 API calls = ~2,600 calls. Two full test sessions exhausted the daily limit. Groq has 1,000 RPM and no daily RPD cap — it runs the same OpenAI-compatible API, just swap the URL and model name.

**Key in vault:** `service_name='Groq', key_type='api_key'` — starts with `gsk_`.

---

> ## How to add entries
> Add a new `## [date] — [area]: [title]` section above this line.
> Fill in all 6 fields. One paragraph each is enough.
> The goal: future Claude (and Dan) can read this and understand the system's shape without re-litigating it.
