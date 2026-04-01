# Syntharra System Review — Actionable Implementation List

**Generated:** 1 April 2026
**Source:** `syntharra-system-review-3.docx` (28 items identified)
**Verified against:** GitHub repos, Retell API, Railway, project-state.md, ops monitor codebase

---

## Summary

- **Total items in document:** 28 (7 Critical, 9 High, 8 Medium, 4 Low)
- **Already implemented / correctly functioning:** 4
- **Actionable items for Claude Code:** 24
- **Highest-priority items (top 3):**
  1. Unpause the ops monitor with environment-aware alert filtering (currently ZERO visibility)
  2. ⚠️ Republish the HVAC Standard agent (`is_published: false` — discovered during verification, NOT in the report)
  3. Add retry logic to Supabase writes in both call processors (silent data loss risk)
- **Blockers to resolve first:**
  - The HVAC Standard agent is **UNPUBLISHED** (`is_published: false`). This means any live calls to Arctic Breeze are potentially hitting an outdated version. Must be republished before any flow node changes.
  - Ops monitor is paused on Railway (service `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`) — needs `sleepApplication: false` via Railway GraphQL, but only AFTER the environment-aware filter is deployed to avoid alert spam.

---

## Excluded Items (Already Implemented — Verified)

| # | Report Item | Verification |
|---|---|---|
| 3 | Spanish / Multilingual handling — language detection | Agent already set to `language: multi`. However, the **conversation flow** has no Spanish branching node — see Item 13 below for the remaining gap. |
| 14 | Workflow ID inconsistency across skills | Verified: `project-state.md` has a single authoritative workflow ID table. All IDs match. The report referenced stale skill file copies — the skill files reference `project-state.md` as source of truth. |
| 8 (partial) | Call duration validation | `CALL_TOO_SHORT` already exists as an alert condition in both call processors (confirmed in project-state session notes from 2026-03-30). **However**, it only fires an internal alert — it does NOT exclude short calls from lead notification emails. See Item 8 below for the remaining gap. |
| — | Prompt token budget (Item 4) | This is a monitoring/validation concern, not a build item. The onboarding workflow does not yet have clients with long company info blocks. Deferred to post-launch optimisation. Prompt is currently well under 2,000 tokens for Arctic Breeze. |

---

## Actionable Implementation List

### PHASE 0 — Emergency Fix (Discovered During Verification)

**[0]. ⚠️ REPUBLISH HVAC Standard Agent**
- **What:** The HVAC Standard agent (`agent_4afbfdb3fcb1ba9569353af28d`) has `is_published: false`. This means the live version callers reach may not reflect the latest v18 changes. Call `POST https://api.retellai.com/publish-agent/agent_4afbfdb3fcb1ba9569353af28d` with Bearer auth immediately.
- **Where:** Retell AI API
- **Why:** Discovered during verification — the report did not flag this. Any unpublished agent means callers hit a stale version.
- **Notes:** Do this BEFORE making any conversation flow changes (Items 1, 2, 13). After publishing, verify via `GET /get-agent/` that `is_published: true`. Remember the critical rule: always publish after ANY agent update.

---

### PHASE 1 — Immediate (This Week)

**[1]. Add Silence Handler Node to Conversation Flow**
- **What:** Add a new conversation node `silence_handler_node` to `conversation_flow_34d169608460`. After 8 seconds of caller silence, the agent should prompt: "Are you still there? I want to make sure I can help you." After two consecutive silence triggers, offer to capture the caller's number and call back. Wire it as a fallback from any active conversation node.
- **Where:** Retell AI — conversation flow `conversation_flow_34d169608460` (12 nodes currently, this becomes 13th)
- **Why:** Report Item 1 (CRITICAL). Callers going silent hear nothing and hang up — lost lead.
- **Notes:** Retell's conversation flow editor supports silence detection via node transition conditions. Use the Retell API `PATCH` to update the flow, then publish the agent. Test with a real call to Arctic Breeze (`+18129944371`) after deploying.

**[2]. Add Emergency Fallback Node to Conversation Flow**
- **What:** Add `emergency_fallback_node` that activates when `verify_emergency_node` triggers a transfer AND the transfer fails (`transfer_failed_node`). The fallback must: (a) instruct the caller to dial 911 immediately, (b) capture their address and phone number, (c) trigger an URGENT SMS alert to the business owner via the n8n call processor (tagged `emergency=true`), (d) flag the call in `hvac_call_log` with `emergency=true`.
- **Where:** Retell AI conversation flow + n8n HVAC Std Call Processor (`OyDCyiOjG0twguXq`) + Supabase `hvac_call_log`
- **Why:** Report Item 2 (HIGH). A failed transfer during a gas leak or CO situation with no fallback is a liability risk.
- **Notes:** Add `emergency` boolean column to `hvac_call_log` if it doesn't exist. The call processor already alerts on `TRANSFER_FAILED` — add a conditional branch that checks if the call was emergency-flagged and sends an additional URGENT SMS (even though SMS is disabled, wire it now so it's ready when Telnyx/Plivo activates). Also send an URGENT email to `alerts@syntharra.com` as immediate fallback.

**[3]. Unpause Ops Monitor with Environment-Aware Filtering**
- **What:** Add a `PRE_LAUNCH_MODE` environment variable to the ops monitor Railway service. In `src/utils/alertManager.js`, check this variable. When `PRE_LAUNCH_MODE=true`: suppress non-critical alerts (revenue checks, client count checks, Stripe payment checks) but KEEP infrastructure health checks active (Railway uptime, n8n reachability, Supabase connectivity, Retell agent status, webhook endpoint health). Then unpause the Railway service via GraphQL: `sleepApplication: false` on service `7ce0f943-5216-4a16-8aeb-794cc7cc1e65`.
- **Where:** `Syntharra/syntharra-ops-monitor` repo (`src/utils/alertManager.js`, `src/config.js`) + Railway env vars + Railway GraphQL API
- **Why:** Report Item 11 (CRITICAL). Currently ZERO automated monitoring. Any system failure goes undetected.
- **Notes:** The alertManager already has `cooldown` and `suppressed` logic — extend it with a `prelaunchFilter()` method. Add `PRE_LAUNCH_MODE=true` to Railway env vars for the ops monitor service. The monitors to KEEP active in pre-launch: `retell.js`, `n8n.js`, `supabase.js`, `infrastructure.js`, `jotform.js`. Monitors to SUPPRESS: `revenue.js`, `clients.js` (no clients yet), `stripe.js` (test mode). Deploy code first, THEN unpause the service.

**[4]. Add External Uptime Monitor**
- **What:** Set up UptimeRobot (free tier) to ping these endpoints every 60 seconds, with SMS + email alerts independent of Railway: (a) `https://n8n.syntharra.com` (n8n), (b) `https://syntharra-checkout-production.up.railway.app` (checkout server), (c) `https://admin.syntharra.com` (admin dashboard), (d) `https://syntharra.com` (website).
- **Where:** UptimeRobot.com (external — Dan must create the account)
- **Why:** Report Item 12 (HIGH). All services are on Railway — if Railway has a regional outage, no internal monitor will catch it.
- **Notes:** This requires Dan's direct action (account creation). Claude Code should prepare the exact endpoint list, expected status codes, and alert email (`alerts@syntharra.com`) as a setup guide document.

**[5]. Add Retry Logic to Supabase Writes in Both Call Processors**
- **What:** In both HVAC Std Call Processor (`OyDCyiOjG0twguXq`) and HVAC Prem Call Processor (`UhxfrDaEeYUk4jAD`), wrap all Supabase write operations in retry logic: 3 attempts with exponential backoff (2s, 8s, 30s). If all retries fail, send a CRITICAL alert email to `alerts@syntharra.com` containing the full call payload (caller name, phone, address, job type, agent ID) so the data can be manually recovered.
- **Where:** n8n workflows `OyDCyiOjG0twguXq` and `UhxfrDaEeYUk4jAD`
- **Why:** Report Item 6 (CRITICAL). A single Supabase network blip silently loses the call data — the business never gets the lead.
- **Notes:** n8n has a built-in "Retry On Fail" option on HTTP Request nodes — enable it with max retries = 3 and wait between retries = 2000ms. For the failure alert, add an Error Trigger node that catches any uncaught errors and sends the alert email via SMTP2GO. Remember: after editing, click Publish in n8n.

**[6]. Improve Call Duration Filtering (Exclude Short Calls from Lead Emails)**
- **What:** The call processors already alert on `CALL_TOO_SHORT`, but short calls (<15 seconds) still get processed as leads and included in lead notification emails. Add a conditional branch at the START of the call processor: if `call_duration < 15 seconds`, log the call to `hvac_call_log` with `call_type='abandoned'`, skip the lead notification email, and skip the GPT analysis step. Still store for analytics.
- **Where:** n8n workflows `OyDCyiOjG0twguXq` and `UhxfrDaEeYUk4jAD`
- **Why:** Report Item 8 (MEDIUM). Short calls inflate lead counts in weekly reports, eroding client trust.
- **Notes:** The Retell `call_analyzed` webhook payload includes `call_duration_ms` (or similar). Check the exact field name in the webhook payload. Add the filter as the FIRST IF node after the webhook trigger, before any Supabase write or email send.

---

### PHASE 2 — Before First Paying Client

**[7]. ⚠️ Complete Stripe Live Mode Cutover**
- **What:** Activate Stripe account for live payments. Recreate ALL products, prices, and coupons in live mode using the same names (IDs will change). Create a new webhook pointing to `https://n8n.syntharra.com/webhook/syntharra-stripe-webhook` for `checkout.session.completed`. Update Railway env vars: `STRIPE_SECRET_KEY` → `sk_live_...`, webhook signing secret → new live value. Update n8n credential store with new signing secret. Test end-to-end with a real $1 charge and refund.
- **Where:** Stripe dashboard + Railway env vars + n8n credentials + `Syntharra/syntharra-checkout` server
- **Why:** Report Item 15 (CRITICAL). Cannot collect real payments without this. Primary pre-launch gate.
- **Notes:** Follow the pre-launch checklist in `project-state.md`. The discount codes doc (`docs/discount-codes.md`) has all coupon details to recreate. After cutover, update `project-state.md` with new live-mode price IDs, product IDs, webhook ID, and signing secret location. ⚠️ This affects the checkout server immediately — test before announcing to any clients. Dan must handle the Stripe account activation step.

**[8]. Add Call Recording Consent Disclosure to Agent Greeting**
- **What:** Modify the `greeting_node` in `conversation_flow_34d169608460` to include a recording consent disclosure as the first sentence. Use: "Thank you for calling {{company_name}}. This call may be recorded for quality and training purposes." This must play BEFORE any other conversation. Add a `consent_given` boolean field to `hvac_call_log` (default `true` since continuing the call implies consent in one-party states). For two-party states (CA, FL, IL, PA, WA, MD, MT, NH, CT, MA), the agent should explicitly ask: "Is that okay with you?" and log the response.
- **Where:** Retell AI conversation flow (`greeting_node`) + Supabase `hvac_call_log` (new column)
- **Why:** Report Item from Part 2.6 (CRITICAL). Two-party consent states require explicit disclosure. Non-compliance is a legal liability.
- **Notes:** The simplest v1 implementation: add the disclosure to ALL greetings regardless of state (covers all cases). Two-party state detection by phone area code can be a v2 enhancement. After modifying the flow, publish the agent.

**[9]. Implement Jotform Webhook Backup Polling**
- **What:** Create a new n8n workflow that runs every 15 minutes on a cron schedule. It polls the Jotform API for recent submissions on both forms (Standard: `260795139953066`, Premium: `260819259556671`). For each submission, check if a matching record exists in `hvac_standard_agent` (by email or submission ID). If no match is found, trigger the onboarding workflow manually or send an alert to `onboarding@syntharra.com` with the submission data.
- **Where:** n8n (new workflow) + Jotform REST API + Supabase `hvac_standard_agent`
- **Why:** Report Item 9 (HIGH). Jotform does not retry failed webhooks. If n8n is down during a submission, the paying customer's onboarding data is lost.
- **Notes:** Use the Jotform API key from Claude memory. Endpoint: `GET https://api.jotform.com/form/{formID}/submissions?limit=10&orderby=created_at&filter={"created_at:gt":"<15_min_ago>"}`. Store the last-checked timestamp in a Supabase utility table or use the workflow's built-in static data. Tag this workflow with "Operations" tag.

**[10]. Add Stripe/Jotform Reconciliation Step**
- **What:** In both the Stripe webhook workflow (`ydzfhitWiF5wNzEy`) and the Jotform onboarding workflows (`k0KeQxWb3j3BbQEk`, `KXDSMVKSf59tAtal`), add a reconciliation check. When Stripe fires `checkout.session.completed`, check if the corresponding Jotform submission record exists in Supabase. If not, wait 60 seconds and retry once. If still missing, send an alert to `onboarding@syntharra.com`. Apply the same logic in reverse for Jotform webhooks (check if Stripe payment exists).
- **Where:** n8n workflows `ydzfhitWiF5wNzEy`, `k0KeQxWb3j3BbQEk`, `KXDSMVKSf59tAtal`
- **Why:** Report Item 10 (MEDIUM). Race condition between two independent webhooks can create incomplete client records.
- **Notes:** The matching key between Stripe and Jotform is `customer_email`. The Stripe workflow already saves to `stripe_payment_data` — check for a matching email in `hvac_standard_agent` (populated by Jotform onboarding). Use n8n's Wait node for the 60-second delay.

**[11]. Enable SMS Notifications via Interim Provider**
- **What:** Since Telnyx is still awaiting AI evaluation approval, set up Plivo (already identified as backup in project-state) as an interim SMS provider. Create a Plivo account, purchase a number, store credentials in `syntharra_vault`. Create a reusable n8n sub-workflow for sending SMS that abstracts the provider (so switching to Telnyx later is a single config change). Wire SMS into: (a) emergency call alerts, (b) 100% usage overage alerts, (c) client lead notifications (optional, per-client setting).
- **Where:** Plivo account (Dan must create) + Supabase `syntharra_vault` + n8n (new sub-workflow) + both call processors
- **Why:** Report Item 13 (HIGH). Email-only notifications have inherent latency. HVAC emergencies need sub-minute alerts.
- **Notes:** Dan must create the Plivo account and provide API credentials. Claude Code should build the n8n SMS sub-workflow with a provider abstraction layer (env var `SMS_PROVIDER=plivo|telnyx`) so the switch is seamless later. Update `SMS_ENABLED=true` in Railway env only after testing.

---

### PHASE 3 — Within 30 Days of Launch

**[12]. Enable Repeat Caller Detection for Standard Tier**
- **What:** The Premium call processor already has repeat caller detection. Port the same logic to the Standard call processor (`OyDCyiOjG0twguXq`). When a call comes in, check `hvac_call_log` for matching `caller_phone` within the last 30 days for the same `agent_id`. If found, pass context to the Retell agent via dynamic variables so it can say: "Welcome back! I see you called recently about [job_type]. Is this about the same issue, or something new?" Also prevent duplicate lead entries.
- **Where:** n8n workflow `OyDCyiOjG0twguXq` + Retell agent dynamic variables + Supabase `hvac_call_log`
- **Why:** Report Item 5 (MEDIUM). Repeat callers re-explaining their issue is the #1 frustration with automated systems. Creates duplicate leads.
- **Notes:** The Premium processor (`UhxfrDaEeYUk4jAD`) has this logic — reference its implementation. The matching field is `caller_phone` (or caller_id from Retell). Retell supports passing dynamic variables in the webhook response — check the Retell skill file for the exact mechanism.

**[13]. Add Spanish Language Detection and Routing**
- **What:** The agent already has `language: multi` enabled at the Retell level, so it CAN understand Spanish. But the conversation flow has no explicit Spanish handling. Add a language detection trigger in `greeting_node`: if Spanish is detected in the first caller utterance, either (a) switch to a Spanish-language prompt variant for the entire flow, or (b) immediately offer transfer with a bilingual message. Log the detected language in `hvac_call_log` (new column: `caller_language`).
- **Where:** Retell AI conversation flow + Supabase `hvac_call_log` (new column)
- **Why:** Report Item 3 (HIGH). Major revenue leak in TX, FL, AZ, CA markets with 30%+ Hispanic populations.
- **Notes:** Retell's `language: multi` handles recognition. The simplest v1: add a conditional edge from `greeting_node` that checks for Spanish input and routes to a `spanish_transfer_node` that says "Un momento, por favor. Let me connect you with someone who can help" and then transfers. Full Spanish flow is a v2 effort. Publish agent after changes.

**[14]. Implement Overage Billing via Stripe**
- **What:** The Usage Alert Monitor (`lQsYJWQeP5YPikam`) already alerts at 80% and 100% usage. Extend it to: (a) at 80%, send a warning email to the client, (b) at 100%, send a notification disclosing the overage rate, (c) automatically create Stripe invoice line items for overage minutes at the defined per-minute rate. The Minutes Calculator (`9SuchBjqhFmLbH8o`) should feed usage data to Stripe as metered billing.
- **Where:** n8n workflows `lQsYJWQeP5YPikam` and `9SuchBjqhFmLbH8o` + Stripe API + Supabase `overage_charges`
- **Why:** Report Item 16 (HIGH). Clients exceeding minutes with no consequence costs Syntharra money on Retell usage.
- **Notes:** Stripe metered billing requires a `usage_record` on the subscription item. ⚠️ Only implement AFTER Stripe live mode cutover (Item 7). The overage rate needs to be defined by Dan (not documented yet — flag for decision). The `overage_charges` table already exists in Supabase.

**[15]. Build Client Health Score and Churn Detection**
- **What:** Create a new Supabase table `client_health_scores` tracking three leading indicators per client: (a) weekly call volume trend (alert if down 50%+ week-over-week), (b) dashboard login frequency (alert if zero logins in 14 days — requires adding a `last_login` timestamp to `hvac_standard_agent`), (c) Stripe payment failures (immediate alert). Create a new n8n workflow that calculates the health score weekly and sends internal alerts for at-risk clients.
- **Where:** Supabase (new table + column additions) + n8n (new workflow) + Stripe payment failure webhook
- **Why:** Report Item 17 (MEDIUM). At $497-997/mo per client, early churn detection is critical for retention.
- **Notes:** Payment failure detection requires adding `invoice.payment_failed` to the Stripe webhook events list (currently only `checkout.session.completed`). Dashboard login tracking requires adding a Supabase function or a simple POST from `dashboard.html` on load. This is a post-launch item — no rush until there are active clients.

**[16]. Build Geocode Failure Reporting**
- **What:** The call processor already geocodes addresses and logs `geocode_status` and `geocode_formatted` in `hvac_call_log`. Add a weekly report (as part of the existing Weekly Lead Report workflow `mFuiB4pyXyWSIM5P`) that includes a section listing failed geocodes with the raw `caller_address` so the business can manually verify. Also add address confirmation to the agent prompt: "Let me confirm, that's [address] in [city], [state], correct?"
- **Where:** n8n workflow `mFuiB4pyXyWSIM5P` + Retell agent prompt (address capture node)
- **Why:** Report Item 7 (HIGH). Failed geocodes indicate bad addresses, which means the business can't route technicians.
- **Notes:** The `GEOCODE_ERROR` condition already triggers an internal alert. This adds the CLIENT-facing reporting dimension. The address confirmation prompt should go in the `nonemergency_leadcapture_node` of the conversation flow.

**[17]. Add PII Redaction and Retention Policies**
- **What:** (a) Define a call transcript retention policy (recommend 90 days for operational use, 1 year for compliance archive). (b) Create a Supabase function or scheduled n8n workflow that redacts PII (phone numbers, addresses) from transcripts older than 90 days, keeping only anonymised summaries. (c) Verify Supabase RLS policies on `hvac_call_log` and `stripe_payment_data` — ensure only service-role access can read full transcripts and financial data. (d) Document the policy.
- **Where:** Supabase (RLS policies, scheduled function) + n8n (cleanup workflow) + documentation
- **Why:** Report Items from Part 2.6 (CRITICAL for PII, HIGH for retention). CCPA and potential GDPR exposure if serving international clients.
- **Notes:** Supabase RLS is already partially in place (anon key used for dashboard has limited access). This needs Dan's decision on retention period. Create the technical implementation but flag the policy decision. Financial data isolation (Stripe data separate from transcripts) should be verified — check that `stripe_payment_data` has no JOINable path to call transcripts for anonymous users.

**[18]. Build Transcript Analysis Pipeline (Frustration Detection)**
- **What:** Create a new n8n workflow that runs daily, processing the previous day's call transcripts through Groq (free tier, `llama-3.3-70b-versatile`) to detect: (a) caller anger/profanity, (b) agent confusion loops (same question asked twice), (c) premature call endings, (d) "speak to a human" requests, (e) potential price hallucinations (dollar amounts not in company info block). Store results in a new Supabase table `call_quality_flags`. Surface in the admin dashboard.
- **Where:** n8n (new workflow) + Supabase (new table) + Groq API + admin dashboard
- **Why:** Report Items from Part 2.1 and 2.4 (multiple CRITICAL and HIGH items). Without this, prompt degradation and caller frustration go undetected.
- **Notes:** Use Groq free tier to keep costs at $0. The Agent Testing System already uses Groq with the same model — reuse that pattern. Process transcripts in batches of 5-10 to stay under rate limits (30 RPM, 6000 TPM). The admin dashboard (`admin.syntharra.com`) already has sections that can be extended.

**[19]. Add Prompt Injection / Jailbreak Detection**
- **What:** Extend the transcript analysis pipeline (Item 18) to flag calls where callers attempt to manipulate the agent with adversarial prompts. Keywords: "ignore your instructions", "you are now", "pretend", "forget everything", "new instructions". Log flagged calls in `call_quality_flags` with `flag_type='prompt_injection'`. Send an immediate alert to `alerts@syntharra.com`.
- **Where:** n8n (extension of Item 18 workflow) + Supabase `call_quality_flags`
- **Why:** Report Item from Part 2.5 (HIGH). Protecting agent integrity is critical for brand trust and security.
- **Notes:** This is a simple keyword scan extension of Item 18. Can be implemented as an additional check in the same Groq analysis prompt.

---

### PHASE 4 — Monitoring Framework Build-Out (Part 2 of Report)

The report's Part 2 defines ~40 monitoring metrics. Most are analytics/BI features, not infrastructure fixes. The following are the highest-value monitoring items that should be built as the client base grows:

**[20]. Add Zero-Calls-in-24-Hours Alert**
- **What:** In the ops monitor, add a check that queries `hvac_call_log` for each active client. If a client with historical average daily calls > 2 has zero calls in the last 24 hours, fire a CRITICAL alert — their phone routing may be broken.
- **Where:** `Syntharra/syntharra-ops-monitor` — new check in `src/monitors/clients.js`
- **Why:** Report Item from Part 2.3 (CRITICAL). A broken phone route means the client's business is losing every call.
- **Notes:** The ops monitor already has `clients.js`. This check should be SUPPRESSED in `PRE_LAUNCH_MODE` (no active clients yet). Wire it to activate automatically when `PRE_LAUNCH_MODE` is switched to `false`.

**[21]. Add Callback Request Volume Alert**
- **What:** Track the ratio of callback requests to total calls per client. If callbacks > 40% of total calls, alert `admin@syntharra.com` — it means the business isn't answering their phone, which undermines the entire value proposition.
- **Where:** n8n (extend Weekly Lead Report `mFuiB4pyXyWSIM5P`) + Supabase query
- **Why:** Report Item from Part 2.2 (CRITICAL). High callback volume = the client isn't getting value = churn risk.
- **Notes:** The `hvac_call_log` already has `call_type` which includes callback. This is a query + threshold alert, not new infrastructure.

**[22]. Add Weekly Agent Performance Benchmarks**
- **What:** Create a weekly automated report (extend or supplement the existing Weekly Lead Report) that tracks: lead capture rate (target >90%), average call duration by type, transfer success rate (target >80%), caller sentiment trend, spam/robocall ratio, after-hours call %, emergency call count, minutes usage vs allocation.
- **Where:** n8n (extend `mFuiB4pyXyWSIM5P`) + Supabase queries + email template
- **Why:** Report Part 2.5 (multiple HIGH items). Week-over-week benchmarks catch gradual degradation before it becomes a crisis.
- **Notes:** Most of this data already exists in `hvac_call_log`. This is primarily a reporting/aggregation task. The Weekly Lead Report workflow is the right place to extend. Target: one comprehensive weekly email per client with all key metrics.

**[23]. Add SMTP2GO Delivery Monitoring**
- **What:** In the ops monitor, add a check that queries the SMTP2GO API for bounce rate and delivery stats. Alert if bounce rate exceeds 5% or delivery delays exceed 5 minutes.
- **Where:** `Syntharra/syntharra-ops-monitor` — new check in `src/monitors/email.js`
- **Why:** Report Item from Part 2.3 (HIGH). Email is the primary notification channel — degradation means late lead alerts.
- **Notes:** The email monitor already exists (`email.js`). Project-state notes it was switched to "SMTP2GO public status API (0 emails/month)" during the efficiency pass. This needs to be upgraded to use the SMTP2GO reporting API with the actual API key for real delivery stats.

---

## Items Deferred (Low Priority / Requires Scale)

These items from the report are valid but not actionable until the client base grows beyond ~10 clients:

| Report Item | Reason for Deferral |
|---|---|
| Geographic heat map of call origins | Requires meaningful call volume data from multiple clients |
| Competitive mention detection in transcripts | Requires NLP pipeline (Item 18) to be stable first |
| Revenue per call attribution | Requires downstream conversion tracking not yet built |
| Intent classification accuracy audit | Requires stable call volume for statistical significance |
| Railway multi-region / hot standby | Cost-prohibitive pre-revenue; UptimeRobot (Item 4) covers the gap |
| Voicemail vs live rate tracking | Low priority, informational only |
| Prompt token budget validation in onboarding | No clients with long company info blocks yet |

---

## Decision Points for Dan

The following items require Dan's input before Claude Code can proceed:

1. **Overage rate** — what is the per-minute overage charge? (needed for Item 14)
2. **Call retention policy** — 90 days operational + 1 year archive? Or different? (needed for Item 17)
3. **Plivo account creation** — Dan must create the account and provide API credentials (needed for Item 11)
4. **UptimeRobot account creation** — Dan must create the account (needed for Item 4)
5. **Stripe live mode activation** — Dan must initiate this in the Stripe dashboard (needed for Item 7)
