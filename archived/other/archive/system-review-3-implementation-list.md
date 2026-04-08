# Syntharra System Review — Actionable Implementation List

**Prepared:** 1 April 2026  
**Source:** Syntharra System Review & Ops Monitoring Report (April 2026)  
**For:** Claude Code execution

---

## Summary

- **Total items in actionable list:** 19
- **Items excluded (already implemented or verified):** 9
- **Highest-priority items (top 3):**
  1. **Unpause ops monitor with environment-aware filtering** — currently ZERO monitoring across all systems
  2. **Add Supabase write retry logic** to both call processors — silent data loss on any transient failure
  3. **Add silence handler + emergency fallback nodes** to the Standard conversation flow — caller experience and safety liability
- **Blockers to resolve first:**
  - The ops monitor code has no `PRE_LAUNCH_MODE` or `STRIPE_MODE` variable — this must be added before unpausing, otherwise alert spam recurs
  - Standard agent is `is_published: false` (v18, 44% pass rate) — flow node additions should be made now but the agent remains unpublished until testing reaches 100%
  - Stripe live mode cutover is a Dan-only action (account activation, real card test) — Claude Code prepares everything, Dan flips the switch

---

## Excluded Items (Already Implemented — Verified)

| # | Report Item | Status |
|---|---|---|
| 1 | Call duration filtering (Issue #8) | ✅ Call processor already handles `CALL_TOO_SHORT` as error condition, sends alert to `alerts@syntharra.com` |
| 2 | Geocode failure alerting (Issue #7 — alerting part) | ✅ Call processor already fires alert on `GEOCODE_ERROR` condition |
| 3 | Workflow ID inconsistency (Issue #14) | ✅ Project-state.md IDs are authoritative and consistent — the report referenced older skill file copies that have since been reconciled |
| 4 | Usage Alert Monitor 80%/100% warnings (Issue #16 — alert part) | ✅ Workflow `lQsYJWQeP5YPikam` (Usage Alert Monitor) already exists and handles 80%/100% usage alerts |
| 5 | Stripe live mode cutover (Issue #15) | ✅ Already on pre-launch checklist — this is a Dan manual action, not a Claude Code task. Checklist is documented in project-state.md |
| 6 | Email migration away from daniel@ | ✅ Completed 2026-03-28 — all workflows and website use role addresses |
| 7 | Premium pipeline build | ✅ Premium onboarding, call processor, and dispatcher all active and tested (v26, 100% pass) |
| 8 | Agent language setting | ✅ Agent already set to `language: multi` — but see Item #14 below for the missing flow-level handling |
| 9 | Financial data isolation (Issue — Compliance) | ✅ Stripe payment data is in a separate `stripe_payment_data` table; no card numbers stored in any Syntharra system |

---

## Actionable Implementation List

### TIER 1 — IMMEDIATE (Infrastructure & Safety)

**[1]. Unpause Ops Monitor with Environment-Aware Alert Filtering**
- **What:** Add a `PRE_LAUNCH_MODE` environment variable check to the ops monitor's alertManager. When `PRE_LAUNCH_MODE=true`, suppress non-critical alerts (billing, revenue, client count alerts) while keeping infrastructure health checks live (Railway uptime, n8n reachability, Supabase connectivity, Retell agent status, webhook delivery). Then unpause the Railway service.
- **Where:** `Syntharra/syntharra-ops-monitor` repo — `src/utils/alertManager.js` and `src/config.js`. Railway service ID: `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`
- **Why:** Zero monitoring since March 30. Any failure goes undetected until a customer reports it. This is the single most important action.
- **Notes:** The service was paused via Railway `sleepApplication: true`. To unpause: Railway GraphQL API `mutation { serviceInstanceUpdate(serviceId: "7ce0f943-5216-4a16-8aeb-794cc7cc1e65", input: { ...) }` or redeploy. Add `PRE_LAUNCH_MODE=true` as Railway env var. When Stripe goes live, flip to `false`.

---

**[2]. Add External Uptime Monitor (Independent of Railway)**
- **What:** Set up UptimeRobot (free tier) or Better Uptime to ping 4 Railway endpoints every 60 seconds: (a) `https://n8n.syntharra.com` (n8n), (b) `https://syntharra-checkout-production.up.railway.app` (checkout), (c) `https://admin.syntharra.com/api/health` (admin dashboard), (d) ops monitor health endpoint. Configure SMS + email alerts to Dan's phone directly.
- **Where:** External service (UptimeRobot.com) — no code changes needed
- **Why:** If Railway has a regional outage, the ops monitor running ON Railway can't alert about it. External monitoring is the only way to detect total platform failure.
- **Notes:** This is a 10-minute manual setup. Free tier supports 50 monitors at 5-min intervals. Dan may need to do this himself, or Claude Code can prepare the list of endpoints and alert config.

---

**[3]. Add Supabase Write Retry Logic to Both Call Processors** ⚠️ CAUTION
- **What:** Wrap all Supabase write operations in the HVAC Standard Call Processor (`OyDCyiOjG0twguXq`) and HVAC Premium Call Processor (`UhxfrDaEeYUk4jAD`) with retry logic: 3 attempts with exponential backoff (2s, 8s, 30s). If all retries fail, send a CRITICAL alert to `alerts@syntharra.com` containing the full call payload (caller name, phone, address, job type, agent_id) so it can be manually recovered.
- **Where:** n8n workflows `OyDCyiOjG0twguXq` and `UhxfrDaEeYUk4jAD` — the Supabase insert/upsert nodes
- **Why:** Silent data loss on transient Supabase failures means a business owner never receives the lead notification, and the homeowner never gets a callback.
- **Notes:** ⚠️ Both workflows are ACTIVE and processing real calls (even in test mode). Edit carefully — use n8n's version history if available. The retry can be implemented as a Code node wrapping the Supabase HTTP request, or by using n8n's built-in retry mechanism on the HTTP Request node (if available in the Railway build version). Test with a simulated Supabase timeout before activating.

---

**[4]. Add Silence Handler Node to Standard Conversation Flow** ⚠️ CAUTION
- **What:** Add a silence detection instruction to the conversation flow. Since Retell's conversation flows use conversational nodes (not event-triggered nodes), the best approach is to add silence handling instructions to the `greeting_node` and key capture nodes. Specifically: instruct the agent that if the caller goes silent for 8+ seconds, say "Are you still there? I want to make sure I can help you." After two consecutive silences, offer to call back and capture their number. Also consider setting `end_call_after_silence_ms` on the agent config (e.g., 30000ms = 30 seconds as absolute max).
- **Where:** Retell conversation flow `conversation_flow_34d169608460` — update node prompts. Also update agent config via `PATCH https://api.retellai.com/update-agent/agent_4afbfdb3fcb1ba9569353af28d` to set `end_call_after_silence_ms`.
- **Why:** Callers who go silent (distracted, poor signal, put agent on hold) hear nothing, assume the line is dead, and hang up. Lost lead.
- **Notes:** ⚠️ Standard agent is currently `is_published: false` (v18, 44% pass rate, still in testing). Make the flow changes but do NOT publish until testing reaches target pass rate. After any flow edit, the agent version will increment. Always publish via `POST https://api.retellai.com/publish-agent/{agent_id}` when ready.

---

**[5]. Add Emergency Fallback Node to Conversation Flow** ⚠️ CAUTION
- **What:** Add a new `emergency_fallback` node to the conversation flow. This node activates when: (a) `verify_emergency_node` confirms an emergency AND (b) the live transfer fails (transfer_failed_node). The fallback must: (1) instruct the caller to dial 911 immediately, (2) capture their address and phone number, (3) trigger an URGENT notification to the business owner (initially email via alerts@, SMS when Telnyx/Plivo is enabled), (4) flag the call in `hvac_call_log` with `emergency=true`. Update the `transfer_failed_node` to route to this new node when the originating path was emergency.
- **Where:** Retell conversation flow `conversation_flow_34d169608460` — add new node, update edges from `transfer_failed_node`. n8n call processor to check for `emergency=true` flag and send priority notification.
- **Why:** If a live transfer fails during a genuine emergency (gas leak, CO alarm, flooding with electrical risk), the caller is left with a generic "sorry" message. Liability and safety risk.
- **Notes:** ⚠️ Same caution as Item 4 — agent is unpublished/in testing. The `verify_emergency_node` already exists. The new node sits between `transfer_failed` and `End Call` on the emergency path only. The n8n call processor already alerts on `TRANSFER_FAILED` — enhance it to detect `emergency=true` and escalate severity.

---

**[6]. Add Call Recording Consent Disclosure to Greeting Node**
- **What:** Add a recording disclosure statement to the `greeting_node` prompt. The agent must say something like: "Just so you know, this call may be recorded for quality purposes." This must fire on every call, regardless of state. For two-party consent states (CA, FL, IL, PA, WA, MD, MA, MT, NH, CT, OR), recording without disclosure is illegal.
- **Where:** Retell conversation flow `conversation_flow_34d169608460` — `greeting_node` prompt text
- **Why:** US two-party consent laws. Without disclosure, every recorded call in those states creates legal liability for both Syntharra and the HVAC business.
- **Notes:** Retell's `data_storage_setting` is currently `everything` (stores transcripts + recordings). The disclosure must be in the greeting before any substantive conversation begins. Keep it natural and brief — one sentence, not a legal paragraph. Consider making it configurable per client (some states are one-party and don't require it, but safest to always include).

---

### TIER 2 — BEFORE FIRST PAYING CLIENT

**[7]. Build Jotform Webhook Backup Polling Workflow**
- **What:** Create a new n8n workflow that runs every 15 minutes on a cron schedule. It polls the Jotform API (`GET https://api.jotform.com/form/{formID}/submissions?apiKey={key}&filter=...`) for recent submissions, cross-references against `hvac_standard_agent` in Supabase, and flags any submissions that don't have a matching agent record (indicating the webhook was missed). For unmatched submissions, trigger the onboarding flow manually or send an alert to `onboarding@syntharra.com`.
- **Where:** New n8n workflow. Jotform Standard form `260795139953066`, Premium form `260819259556671`. Supabase `hvac_standard_agent` table.
- **Why:** Jotform does not retry failed webhooks. If n8n is down during a submission, a paying customer's onboarding is silently lost — worst possible first impression.
- **Notes:** Use the Jotform REST API directly (not MCP connector — it's broken). API key stored in Claude project memory. The polling interval should be 15 minutes. Only check submissions from the last 30 minutes to avoid reprocessing old ones. Tag the workflow with "Operations" and "HVAC Standard".

---

**[8]. Add Stripe-Jotform Reconciliation Logic**
- **What:** Add a reconciliation step to both the Stripe workflow (`ydzfhitWiF5wNzEy`) and the Standard onboarding workflow (`k0KeQxWb3j3BbQEk`). After each webhook fires: check Supabase for the counterpart record (Stripe checks for Jotform submission; Jotform checks for Stripe payment). If the counterpart record doesn't exist, wait 60 seconds and retry once. If still missing after retry, send an internal alert to `onboarding@syntharra.com` with the partial data.
- **Where:** n8n workflows `ydzfhitWiF5wNzEy` and `k0KeQxWb3j3BbQEk` — add nodes after the initial data extraction
- **Why:** Stripe and Jotform webhooks fire independently with no ordering guarantee. If Stripe fires before Jotform (or vice versa), incomplete records are created. The welcome email might send before the agent is provisioned.
- **Notes:** The matching key between Stripe and Jotform is `customer_email`. Stripe session contains `customer_email`; Jotform submission contains email in the form fields. The 60-second wait handles most timing gaps.

---

**[9]. Enable SMS Notifications via Interim Provider** ⚠️ CAUTION
- **What:** Set up Plivo (the documented backup SMS provider) as an interim SMS channel while Telnyx AI evaluation is pending. Create a Plivo account, purchase a number, store credentials in `syntharra_vault`, and update the call processor notification logic to send SMS for emergency calls and high-value leads. Set `SMS_ENABLED=true` in Railway env vars once ready.
- **Where:** Plivo account setup (manual), `syntharra_vault` in Supabase, Railway env vars, n8n call processor workflows
- **Why:** Email has inherent latency. For HVAC emergencies (no heat in winter, no AC in summer), the business owner needs sub-minute notification via SMS.
- **Notes:** ⚠️ Plivo is the backup provider — NOT Twilio. If Telnyx approval comes through first, skip this and go directly with Telnyx. SMS should be the primary channel for: (a) emergency calls, (b) transfer failures, (c) high-value leads. Non-urgent leads still use email only.

---

**[10]. Add Call Duration Filter for Lead Count Accuracy**
- **What:** While the call processor already flags `CALL_TOO_SHORT` as an error condition, calls under 15 seconds are still counted in weekly lead reports and dashboard metrics. Add a filter to: (a) the Weekly Lead Report workflow (`mFuiB4pyXyWSIM5P`) to exclude calls with `call_type='abandoned'` or duration < 15s from lead counts, and (b) the client dashboard (`dashboard.html`) to show abandoned calls separately from real leads.
- **Where:** n8n workflow `mFuiB4pyXyWSIM5P` (Weekly Lead Report), client dashboard `dashboard.html`
- **Why:** Short calls inflate lead counts, making weekly reports unreliable. Business owners see 50 leads but only 30 are real.
- **Notes:** The call processor already tags these — this is about excluding them from downstream reporting, not detection. Check if `hvac_call_log` has a `call_type` or `duration` field that can be filtered on. The dashboard skill file (`syntharra-client-dashboard`) has the exact patterns for modifying dashboard.html.

---

**[11]. Geocode Failure Weekly Report**
- **What:** Create a weekly report (or add a section to the existing Weekly Lead Report) that lists all calls from the past 7 days where `geocode_status` indicates failure. Include the raw `caller_address` so the business can manually verify. Also add an address confirmation prompt to the agent's `nonemergency_leadcapture_node`: "Let me confirm, that's [address] in [city], [state], correct?"
- **Where:** n8n workflow `mFuiB4pyXyWSIM5P` (Weekly Lead Report) — add geocode failure section. Retell conversation flow `conversation_flow_34d169608460` — update `nonemergency_leadcapture_node` prompt.
- **Why:** Geocode failures mean the business can't route technicians efficiently. A pattern of failures may indicate the agent is collecting bad addresses.
- **Notes:** The `hvac_call_log` already has `geocode_status` and `geocode_formatted` columns. The call processor already alerts on individual `GEOCODE_ERROR` events — this adds a weekly summary view.

---

### TIER 3 — WITHIN 30 DAYS OF LAUNCH

**[12]. Enable Repeat Caller Detection for Standard Tier**
- **What:** Implement repeat caller detection in the Standard call processor (`OyDCyiOjG0twguXq`). When a call comes in, check `hvac_call_log` for matching `caller_id` (phone number) within the last 30 days. If found, pass the previous call's `job_type` and `caller_name` as dynamic variables to the agent. Update the greeting to say: "Welcome back! I see you called recently about [job_type]. Is this about the same issue, or something new?"
- **Where:** n8n workflow `OyDCyiOjG0twguXq`, Retell conversation flow — add conditional greeting path
- **Why:** Callers re-explaining their problem is the #1 frustration with automated phone systems. Also prevents duplicate lead entries.
- **Notes:** Premium call processor already has repeat caller detection wired. Use the same pattern. This is listed in the pre-launch checklist as a pending item. The matching should use `caller_id` (phone number) not name, as names can be spelled differently.

---

**[13]. Implement Overage Billing via Stripe Metered Billing**
- **What:** Connect the Monthly Minutes Calculator (`9SuchBjqhFmLbH8o`) to Stripe's metered billing system. When a client exceeds their allocation (475 min Standard, 1,000 min Premium), automatically create overage line items on their next Stripe invoice. Implement three tiers: (a) 80% usage — warning email (already handled by Usage Alert Monitor), (b) 100% usage — notification with overage rate disclosure, (c) overage — automatic Stripe invoice line items at the per-minute overage rate.
- **Where:** n8n workflow `9SuchBjqhFmLbH8o` (Minutes Calculator), Stripe API (invoice items), `overage_charges` Supabase table
- **Why:** Without enforcement, clients can exceed minutes with no consequence, costing Syntharra money on Retell usage.
- **Notes:** The `overage_charges` table already exists in Supabase. The Usage Alert Monitor (`lQsYJWQeP5YPikam`) already handles 80%/100% alerts. This adds the actual billing enforcement. ⚠️ Must be implemented AFTER Stripe goes live — metered billing requires live mode subscriptions.

---

**[14]. Add Spanish Language Detection and Routing**
- **What:** Add language detection logic to the `greeting_node` of the conversation flow. If Spanish is detected (caller speaks Spanish in first exchange), the agent should respond bilingually: "Un momento, por favor. Let me connect you with someone who can help." Then attempt live transfer. Log `language='es'` in `hvac_call_log` for business intelligence. For future: consider a full Spanish-language prompt variant.
- **Where:** Retell conversation flow `conversation_flow_34d169608460` — `greeting_node`, new `spanish_routing_node`. Supabase `hvac_call_log` — add `language` column if not present.
- **Why:** US HVAC businesses in TX, FL, AZ, CA serve large Spanish-speaking populations. English-only agent loses these leads to competitors.
- **Notes:** The agent's `language` setting is already `multi` (supports multilingual recognition). This is about adding flow-level handling — what to DO when Spanish is detected. Start with the simple transfer approach; full Spanish prompts can come later as a Premium upsell.

---

**[15]. Build Client Health Score Dashboard**
- **What:** Create a client health scoring system tracking three leading indicators: (a) weekly call volume trend (alert if down 50%+ week-over-week), (b) dashboard login frequency (alert if zero logins in 14 days — requires adding login tracking to dashboard.html), (c) Stripe payment failures (alert immediately via Stripe webhook `invoice.payment_failed`). Combine into a health score (green/yellow/red) visible on the admin dashboard.
- **Where:** Supabase — new `client_health_scores` table or view. Admin dashboard (`admin.syntharra.com`). n8n — new health score calculation workflow (weekly cron). Stripe — add `invoice.payment_failed` event to webhook.
- **Why:** At $497–997/mo per client, churn detection is critical. Without early warning, clients quietly cancel.
- **Notes:** Dashboard login tracking requires adding a Supabase write when the password gate is passed on `dashboard.html`. The admin dashboard skill (`syntharra-admin`) has patterns for adding new sections. This is a multi-system feature — build the Supabase schema first, then the calculation workflow, then the dashboard display.

---

**[16]. Build Transcript Analysis Pipeline**
- **What:** Create an n8n workflow that runs daily, pulling the previous day's call transcripts from `hvac_call_log`. Use Groq (free tier, already configured) to analyse each transcript for: (a) agent confusion loops (same question asked twice), (b) caller frustration indicators (profanity, "let me talk to a real person"), (c) price hallucination (agent states dollar amounts not in company info), (d) premature call endings. Store results in a new `transcript_analysis` Supabase table. Surface on admin dashboard.
- **Where:** New n8n workflow (daily cron). Supabase — new `transcript_analysis` table. Admin dashboard — new section.
- **Why:** Without transcript monitoring, prompt degradation and agent hallucination go undetected until clients complain.
- **Notes:** Use Groq `llama-3.3-70b-versatile` (free, existing key in vault). Process transcripts in batches to stay under Groq rate limits (30 RPM). The agent testing system already uses a similar pattern — reuse the Split In Batches + Wait architecture.

---

**[17]. Establish PII Redaction and Retention Policy**
- **What:** Define and implement a call transcript retention policy: (a) set a retention period (suggest 90 days for active clients, 30 days after cancellation), (b) create a nightly Supabase function or n8n workflow that deletes transcripts older than the retention period, (c) add PII detection that redacts phone numbers, addresses, and email addresses from transcript text stored in Supabase (replace with [PHONE], [ADDRESS], [EMAIL] tokens), (d) ensure Supabase RLS policies restrict transcript access to authenticated admin only.
- **Where:** Supabase — RLS policies on `hvac_call_log`, new cleanup function. n8n — new retention cleanup workflow (nightly cron).
- **Why:** Full transcripts contain names, phone numbers, addresses. CCPA, GDPR (if international expansion happens), and state laws may apply. Proactive compliance prevents future legal exposure.
- **Notes:** Supabase RLS policies may already exist — verify before adding. The PII redaction should happen at write time in the call processor, not retroactively. Consider keeping a `transcript_redacted` column alongside the raw transcript for the retention period.

---

**[18]. Add Prompt Token Budget Validation to Onboarding**
- **What:** Add a validation step in the onboarding workflow that measures the compiled prompt length (base prompt + company info block + all node instructions) after agent provisioning. If the total exceeds 2,000 tokens, log a warning and flag the agent for manual review. Consider moving rarely-needed FAQ content to a knowledge base retrieval step rather than injecting it all into the prompt.
- **Where:** n8n onboarding workflows `k0KeQxWb3j3BbQEk` (Standard) and `KXDSMVKSf59tAtal` (Premium) — add validation node after agent creation
- **Why:** Longer prompts increase Retell AI response latency, creating unnatural pauses. As company info blocks grow with more service areas, hours, and pricing notes, this becomes a real problem.
- **Notes:** Use a simple token estimation (word count × 1.3 ≈ tokens). This is a MEDIUM priority guard rail for scale — not urgent for the first few clients.

---

**[19]. Add Prompt Injection / Jailbreak Monitoring**
- **What:** Add a monitoring check to the transcript analysis pipeline (Item #16) that scans for adversarial prompt patterns in caller speech: "ignore your instructions", "you are now", "pretend", "system prompt", "developer mode". Flag these calls in a `security_alerts` Supabase table and send an immediate alert to `alerts@syntharra.com`.
- **Where:** Part of the transcript analysis pipeline (Item #16 dependency). Supabase — new `security_alerts` table or column in `transcript_analysis`.
- **Why:** As AI voice agents become more common, adversarial callers will attempt to manipulate them. Early detection prevents embarrassing or harmful agent behaviour.
- **Notes:** Depends on Item #16 being built first. This is a lightweight addition to the transcript analysis prompt — add a "security check" section to the Groq analysis request.

---

## Dependency Map

```
[1] Ops Monitor Unpause ──→ no dependencies (DO FIRST)
[2] External Uptime ──→ no dependencies (Dan manual setup)
[3] Retry Logic ──→ no dependencies
[4] Silence Handler ──→ no dependencies (but don't publish agent)
[5] Emergency Fallback ──→ depends on [4] (same flow edit session)
[6] Recording Consent ──→ depends on [4] (same flow edit session)
[7] Jotform Backup Polling ──→ no dependencies
[8] Stripe-Jotform Reconciliation ──→ no dependencies
[9] SMS via Plivo ──→ no dependencies (but may be superseded by Telnyx)
[10] Call Duration Filter ──→ no dependencies
[11] Geocode Report ──→ no dependencies
[12] Repeat Caller Detection ──→ no dependencies
[13] Overage Billing ──→ depends on Stripe live mode (Dan action)
[14] Spanish Language ──→ depends on [4,5,6] (batch flow edits)
[15] Client Health Score ──→ no dependencies
[16] Transcript Analysis ──→ no dependencies
[17] PII Redaction ──→ no dependencies
[18] Prompt Token Budget ──→ no dependencies
[19] Jailbreak Monitoring ──→ depends on [16]
```

## Recommended Execution Order

**Batch 1 (Items 1, 3, 4+5+6):** Ops monitor unpause + call processor hardening + all conversation flow edits in one session  
**Batch 2 (Items 7, 8, 10, 11):** Onboarding reliability + reporting accuracy  
**Batch 3 (Items 12, 14):** Caller experience improvements  
**Batch 4 (Items 15, 16, 17, 19):** Analytics, monitoring, and compliance  
**Standalone (Items 2, 9, 13, 18):** Independent tasks that can be done in any order

---

*End of Implementation List*
