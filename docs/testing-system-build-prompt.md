# SYNTHARRA TESTING SYSTEM — Claude Code Build Prompt

## ROLE
You are building a comprehensive pre-launch testing system for Syntharra, an AI receptionist SaaS for the trade industry. The system tests AI phone agents (built on Retell AI), their supporting workflows (n8n), database (Supabase), payments (Stripe), and the full customer journey end-to-end.

**CRITICAL RULES:**
- Never delete or recreate a Retell agent — always patch in place
- Always publish after Retell API updates: `POST https://api.retellai.com/publish-agent/{agent_id}`
- Website edits use Python `str.replace()` — never rebuild from scratch
- Admin dashboard (`admin.syntharra.com`) is a single-file SPA at `public/index.html` in repo `Syntharra/syntharra-admin`
- One `<style>` block per page. `overflow-x:clip` on body, never `overflow:hidden`
- Use `var` not `const/let` in dashboard render functions (function-scoped for compatibility)
- All dates/times in `Europe/London` timezone
- Commit prefix: `admin:` for dashboard changes
- GitHub push: fetch SHA first, then PUT via Contents API
- Never commit raw API keys — use placeholder variables

---

## CREDENTIALS & ENDPOINTS

```
GitHub Token: {{GITHUB_TOKEN}}
GitHub Repos:
  - Syntharra/syntharra-admin (admin dashboard — Railway auto-deploys from main)
  - Syntharra/syntharra-automations (docs, configs, workflow backups)
  - Syntharra/syntharra-website (GitHub Pages)
  - Syntharra/syntharra-checkout (Stripe checkout server)
  - Syntharra/syntharra-ops-monitor (24/7 monitoring)
  - Syntharra/syntharra-oauth-server (Premium OAuth)

Retell AI:
  API Key: {{RETELL_API_KEY}}
  Base URL: https://api.retellai.com
  Standard Agent ID: agent_4afbfdb3fcb1ba9569353af28d
  Agent Name: HVAC Standard
  Voice: retell-Sloane
  Conversation Flow ID: conversation_flow_34d169608460
  Phone Number: +18129944371
  Transfer Number: +18563630633
  Demo Agents: Jake (agent_b9d169e5290c609a8734e0bb45), Sophie (agent_2723c07c83f65c71afd06e1d50)

Supabase:
  URL: https://hgheyqwnrcvwtgngqdnq.supabase.co
  Anon Key: {{SUPABASE_ANON_KEY}}
  REST: https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1

Stripe (TEST MODE):
  Checkout Server: https://checkout.syntharra.com
  Webhook URL: https://n8n.syntharra.com/webhook/syntharra-stripe-webhook
  Standard Product: prod_UC0hZtntx3VEg2
  Premium Product: prod_UC0mYC90fSItcq

n8n:
  URL: https://n8n.syntharra.com
  Existing test runner workflow: 3MMp9J8QN0YKgA6Q (SYNTHARRA_AGENT_TEST_RUNNER)
  Older test runner: Ex90zUMSEWwVk4Wv (HVAC Scenario Test Runner v4)

Railway:
  Admin dashboard auto-deploys from Syntharra/syntharra-admin main branch

Groq (FREE LLM for test analysis):
  API URL: https://api.groq.com/openai/v1/chat/completions
  Model: llama-3.3-70b-versatile
  Key: stored in Railway env var GROQ_API_KEY on the admin service
  Usage: FREE tier, used for conversation simulation + error analysis (NOT fix suggestions)

SMTP2GO:
  API Key: {{SMTP2GO_API_KEY}}

Jotform:
  API Key: {{JOTFORM_API_KEY}}
  Standard Form: 260795139953066
  Premium Form: 260819259556671
```

---

## EXISTING DATABASE SCHEMA

### agent_test_results (TABLE — already exists, 15 rows from previous run)
```sql
id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
run_id          text NOT NULL
agent_type      text NOT NULL        -- 'standard' or 'premium'
run_label       text
scenario_id     integer NOT NULL
scenario_name   text NOT NULL
scenario_group  text NOT NULL        -- 'core_flow','service_variations','personalities','info_collection','edge_cases','pricing_traps','boundary_safety','premium_specific'
pass            boolean NOT NULL
score           integer              -- 0-100
severity        text                 -- 'CRITICAL','HIGH','MEDIUM','LOW'
issues          jsonb                -- JSON array of issue strings
fix_needed      text                 -- DO NOT USE for auto-fix suggestions (legacy field, keep for copy-paste diagnostics)
root_cause      text
caller_turn1    text
agent_turn1     text
caller_turn2    text
agent_turn2     text
tested_at       timestamptz
```

### agent_test_run_summary (VIEW — auto-aggregates from agent_test_results)
Aggregates: run_id, agent_type, run_label, started_at, completed_at, total_scenarios, passed, failed, pass_rate, critical_count, high_count, medium_count, low_count

### agent_pending_fixes (TABLE — 25 rows, legacy auto-fix system)
```sql
id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
run_id          text NOT NULL
agent_type      text NOT NULL
agent_id        text NOT NULL
scenario_id     integer NOT NULL
scenario_name   text NOT NULL
scenario_group  text NOT NULL
severity        text NOT NULL
root_cause      text NOT NULL
fix_description text NOT NULL
status          text DEFAULT 'pending'  -- 'pending','approved','rejected','applied'
approved_by     text
applied_at      timestamptz
created_at      timestamptz DEFAULT now()
```

### Other key tables:
- `hvac_standard_agent` — 1 row (Arctic Breeze demo client)
- `hvac_call_log` — 50 rows (call records with caller_sentiment, call_successful, job_type, etc.)
- `client_subscriptions` — 0 rows
- `stripe_payment_data` — 0 rows
- `billing_cycles` — 0 rows
- `website_leads` — 5 rows
- `syntharra_vault` — 57 rows (all API keys)

---

## EXISTING ADMIN DASHBOARD (public/index.html)

**Repo:** `Syntharra/syntharra-admin` → `public/index.html` (141KB single-file SPA)
**Current SHA:** `bc77dd50eeaa46f4e51bf259ac9d23da52c93b96`
**Live at:** https://admin.syntharra.com (HTTP Basic Auth: admin / syntharra2026)

### Design System
```
--v:      #6C63FF (violet primary)
--vl:     #F0EFFB (violet light bg)
--vd:     #5550E8 (violet dark/hover)
--cyan:   #00D4FF
--bg:     #F4F5F9 (page bg)
--surface: #fff (card bg)
--border: #E4E4EF
--border2: #F0F0F8
--text:   #1A1A2E
--text2:  #52526E
--text3:  #9090AA
--text4:  #C0C0D8
--green:  #12B76A
--gbg/gtxt: #ECFDF3 / #027A48
--amber:  #F59E0B
--abg/atxt: #FFFAEB / #B54708
--red:    #F04438
--rbg/rtxt: #FEF3F2 / #B42318
--sw:     232px (sidebar width)
Font: Inter (400, 500, 600, 700), 14px body
```

### Badge classes: `.bg` (green), `.bp` (violet), `.ba` (amber), `.br` (red), `.bgr` (grey), `.bb` (blue)

### Existing sections (nav items):
overview, clients, calls, billing, forms, agents, opsmonitor, marketing, settings, ai, testing

### Existing testing section element IDs:
- `test-agent-select` — Standard/Premium dropdown
- `test-group-select` — Scenario group filter
- `test-run-label` — Run label input
- `test-run-btn` — Run Tests button
- `test-progress-wrap` / `test-progress-bar` / `test-progress-label` / `test-progress-pct` — Progress bar
- `test-stat-passrate` / `test-stat-critical` / `test-stat-fixes` / `test-stat-runs` — KPI cards
- `test-runs-list` — Recent runs feed
- `test-group-breakdown` — Group pass rates
- `test-fixes-list` — Pending fixes list (HAS APPROVE/REJECT BUTTONS — REMOVE THESE)
- `test-fails-table` — Failed scenarios table with expandable transcripts
- `fail-filter-run` / `fail-filter-sev` — Filters

### Existing JS functions for testing:
- `loadTestingData()` — Master data loader (queries Supabase)
- `renderTestingStats(runs, fails, fixes)` — KPI cards
- `renderTestRuns(runs)` — Run history feed
- `renderGroupBreakdown(runs)` — Group pass rate bars
- `renderPendingFixes(fixes)` — Fix list WITH APPROVE/REJECT (NEEDS REWRITE)
- `renderFailedScenarios()` — Failed scenario table with transcripts
- `startTestRun()` — POSTs to n8n webhook to start tests
- `approveFix()` / `rejectFix()` — Legacy fix approval (REMOVE)

### Existing JS: Supabase connection
```javascript
const SB_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGci...'; // anon key
const SB_H = { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY };
async function sbFetch(path) { ... }
```

---

## EXISTING n8n WORKFLOWS (Active)

| Workflow | ID | Purpose |
|---|---|---|
| HVAC Std Onboarding | k0KeQxWb3j3BbQEk | Standard client setup |
| HVAC Std Call Processor | OyDCyiOjG0twguXq | Process Standard calls |
| HVAC Prem Onboarding | KXDSMVKSf59tAtal | Premium client setup |
| HVAC Prem Call Processor | UhxfrDaEeYUk4jAD | Process Premium calls |
| HVAC Prem Dispatcher | kVKyPQO7cXKUJFbW | Premium dispatch |
| Stripe Workflow | ydzfhitWiF5wNzEy | Stripe webhook handler |
| Weekly Lead Report | mFuiB4pyXyWSIM5P | Weekly report email |
| Minutes Calculator | 9SuchBjqhFmLbH8o | Monthly usage calc |
| Usage Alert Monitor | lQsYJWQeP5YPikam | 80%/100% usage alerts |
| Publish Retell Agent | sBFhshlsz31L6FV8 | Publish agent helper |
| Scenario Runner v4 | Ex90zUMSEWwVk4Wv | Old test runner |
| SYNTHARRA_AGENT_TEST_RUNNER | 3MMp9J8QN0YKgA6Q | Current Groq test runner |
| Scenario Transcript Gen | dHO8O0QHBZJyzytn | Test transcript gen |
| Scenario Process Single | rlf1dHVcTlzUbPX7 | Single scenario process |
| Website Lead → AI Score | FBNjSmb3eLdBS3N9 | Score inbound leads |
| Website Lead → Free Report | ykaZkQXWO2zEJCdu | Send free report |
| Nightly GitHub Backup | EAHgqAfQoCDumvPU | Nightly backup |
| Send Welcome Email (manual) | Rd5HiN7v2SRwNmiY | Manual welcome |
| Auto-Enable MCP | AU8DD5r6i6SlYFnb | MCP auto-enable |
| E2E Cleanup | URbQPNQP26OIdYMo | Test data cleanup |

---

## RETELL CONVERSATION FLOW NODES (12 nodes)

```
node-greeting (conversation) — static greeting
node-identify-call (conversation) — classify: service/emergency/existing/FAQ/spam/transfer
node-leadcapture (conversation) — collect name, phone, address, email, issue
node-verify-emergency (conversation) — assess urgency, route emergency
node-callback (conversation) — schedule callback
node-existing-customer (conversation) — handle existing customer queries
node-general-questions (conversation) — answer FAQs from company info
node-spam-robocall (conversation) — identify and end spam
node-transfer-call (transfer_call) — live transfer to Mike Thornton
node-transfer-failed (conversation) — handle failed transfer
node-ending (conversation) — summarise and close
node-end-call (end) — hang up
```

---

## WHAT TO BUILD — 7 COMPONENTS

### COMPONENT 1: Add New Test Scenarios (Supabase + scenario definitions)

Add these 20 new scenarios to the test scenario definitions. These should be stored as rows in a NEW Supabase table `agent_test_scenarios` that the n8n runner reads from (instead of hardcoding scenarios in the workflow).

**New table schema:**
```sql
CREATE TABLE agent_test_scenarios (
  id serial PRIMARY KEY,
  scenario_id integer NOT NULL UNIQUE,
  scenario_name text NOT NULL,
  scenario_group text NOT NULL,
  agent_type text NOT NULL DEFAULT 'standard',  -- 'standard', 'premium', 'both'
  caller_persona text NOT NULL,        -- Description of who the caller is and how they behave
  caller_opening text NOT NULL,        -- What the caller says first
  success_criteria jsonb NOT NULL,     -- Array of strings: what must happen for a pass
  failure_triggers jsonb NOT NULL,     -- Array of strings: what auto-fails the scenario
  enabled boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);
```

**Populate with ALL 95 existing Standard scenarios + 20 new ones.**

The 95 existing scenarios (groups 1-95) are already defined in Retell with IDs. For the n8n Groq runner, we need the scenario data in Supabase. Here are the groups:

**Existing Standard (scenarios 1-95):**
- Core Flow (1-15): Basic service, heating, install, maintenance, duct cleaning, 3 emergencies, missed call return, existing customer x2, FAQ, spam, transfer request, transfer fail
- Service Variations (16-25): Strange noise, water leak, thermostat, heat pump, pilot light, tenant/landlord, multiple issues, home inspection, seasonal, warranty
- Personalities (26-40): Elderly, impatient, suspicious, chatty, no-terminology, one-word, oversharer, mind-changer, angry reviewer, legal threat, interrupter, non-native English, speakerphone, spouse, polite-questioner
- Info Collection (41-55): Hyphenated name, first-name-only, fast number, wrong number, complex email, PO Box, rural route, refuses address, apartment, city-only, spelling correction, two numbers, long street, info-before-asked, unusual domain
- Edge Cases (56-80): Mid-flow question, service change, out-of-scope service, third-party caller, wrong number, AI disclosure, callback time, same-day, repeat caller, vendor, insurance, commercial, specific tech, cancel appointment, reschedule, financing, competitor quote, senior discount, after hours, Sunday, promotion, COVID, real estate agent, hold, repeat-at-end
- Pricing Traps (81-88): Ballpark, what most pay, diagnostic refund, price match, hourly rate, cancellation fee, negotiate diagnostic, payment plans
- Boundary & Safety (89-95): Diagnose request, DIY advice, profanity, personal abuse, BBB complaint, data privacy, minor calling

**NEW Standard scenarios (96-100):**
```
96. Caller with strong regional accent/dialect
  - Group: personalities
  - Persona: Heavy Southern accent, uses regional slang ("fixin' to", "y'all", "the AC is actin' ugly")
  - Success: Agent understands and responds naturally, captures all info correctly
  - Fail: Agent asks caller to repeat excessively, misrecords info

97. Caller on choppy VoIP connection
  - Group: personalities
  - Persona: Connection cuts in and out, words get dropped mid-sentence
  - Success: Agent patiently asks to repeat, confirms info carefully
  - Fail: Agent gets frustrated, records incomplete info without confirming

98. Caller asks about maintenance/membership plans
  - Group: edge_cases
  - Persona: Wants to know about ongoing maintenance plans, annual contracts
  - Success: Agent mentions maintenance plans if in company info, takes lead, doesn't invent plan details
  - Fail: Agent makes up plan pricing or details not in the company info block

99. Caller reports property damage from HVAC failure
  - Group: edge_cases
  - Persona: Water damage from AC leak, mould, ceiling damage — wants someone out AND is upset about property damage
  - Success: Agent treats with urgency, does NOT discuss liability/insurance/compensation, captures details, routes appropriately
  - Fail: Agent makes promises about damage repair, discusses liability, or downplays the damage

100. After-hours emergency with no transfer available
  - Group: edge_cases
  - Persona: Gas smell at 2am, transfer line doesn't answer
  - Success: Agent collects info, marks as urgent, tells caller to call gas company/911 if immediate danger, confirms callback ASAP
  - Fail: Agent just says "call back during business hours" or hangs up without safety instructions
```

**NEW Premium-specific scenarios (101-115):**
```
101. Caller wants to book an appointment (Google Calendar)
  - Group: premium_specific
  - Persona: Straightforward appointment booking
  - Success: Agent offers available times, confirms booking
  - Fail: Agent can't access calendar or gives wrong availability

102. Caller asks for next available slot
  - Group: premium_specific
  - Persona: "What's your next opening?"
  - Success: Agent checks calendar, offers specific time
  - Fail: Agent gives vague answer without checking

103. Requested time is unavailable
  - Group: premium_specific
  - Persona: Wants Thursday 2pm, which is booked
  - Success: Agent explains unavailability, offers alternatives
  - Fail: Agent double-books or doesn't offer alternatives

104. Property manager - multiple units to service
  - Group: premium_specific
  - Persona: Manages 4 rental units, needs service at 2 of them
  - Success: Agent handles multi-address booking, captures each unit's details separately
  - Fail: Agent confuses addresses or only books one

105. Caller asks about appointment duration
  - Group: premium_specific
  - Persona: "How long will the technician be there?"
  - Success: Agent gives default duration from settings, doesn't overpromise
  - Fail: Agent invents times not from the configuration

106. Caller wants to reschedule existing appointment via calendar
  - Group: premium_specific
  - Persona: Has a Thursday appointment, needs to move to Friday
  - Success: Agent checks Friday availability, confirms reschedule
  - Fail: Agent can't find original appointment or fails to reschedule

107. Repeat caller - agent recognises from previous call
  - Group: premium_specific
  - Persona: Called yesterday about AC not cooling, calling back for update
  - Success: Agent references previous call context, doesn't re-ask all info
  - Fail: Agent treats as brand new caller, asks for name/address again

108. Repeat caller with unresolved emergency
  - Group: premium_specific
  - Persona: Called 4 hours ago about no heat, still no callback, elderly parent in home
  - Success: Agent escalates urgency, apologises, fast-tracks, offers immediate transfer
  - Fail: Agent treats as routine, doesn't acknowledge prior emergency

109. Caller asks about CRM/Jobber job status
  - Group: premium_specific
  - Persona: "I had a tech come out last week, what's the status of my job?"
  - Success: Agent checks CRM if possible, or takes message for follow-up
  - Fail: Agent invents job status or says they have no system

110. Emergency routes to on-call tech (dispatcher)
  - Group: premium_specific
  - Persona: Gas leak at midnight, needs immediate dispatch
  - Success: Agent activates dispatch protocol, connects to on-call tech
  - Fail: Agent takes message instead of dispatching

111. After-hours routing test
  - Group: premium_specific
  - Persona: Calling at 9pm for a non-emergency issue
  - Success: Agent informs of after-hours status, takes message with callback ETA
  - Fail: Agent tries to book appointment outside of business hours

112. Multi-notification test - call alert goes to all recipients
  - Group: premium_specific
  - Persona: Standard service call, but tests that notifications go to all 3 email addresses
  - Success: Call processed, notification emails sent to primary + notification_email_2 + notification_email_3
  - Fail: Only primary email notified

113. Premium caller asks about their included minutes
  - Group: premium_specific
  - Persona: "How many minutes do I get on my plan?"
  - Success: Agent correctly states included minutes if configured, or deflects to support
  - Fail: Agent gives wrong number or makes up a figure

114. Premium integration setup conversation
  - Group: premium_specific
  - Persona: New Premium client asking about connecting Google Calendar and Jobber
  - Success: Agent confirms integrations are part of Premium, provides correct next steps (check onboarding email)
  - Fail: Agent doesn't know about integrations or gives wrong instructions

115. Premium caller asks about response time guarantee
  - Group: premium_specific
  - Persona: "What's your guaranteed response time for emergencies?"
  - Success: Agent states response times from company info, doesn't invent guarantees
  - Fail: Agent promises SLA times that aren't in the configuration
```

### COMPONENT 2: Rebuild n8n Test Runner Workflow

**The existing workflow `3MMp9J8QN0YKgA6Q` needs to be updated (or a new one created) with this flow:**

```
Trigger: Webhook POST /webhook/agent-test-runner
Input: { agent_type: "standard"|"premium", groups: ["all"|group_name], run_label: "string" }

Step 1: Generate unique run_id = "run_" + Date.now()

Step 2: Query Supabase agent_test_scenarios table for matching scenarios
  - Filter by agent_type ('standard' or 'both' for standard runs, 'premium' or 'both' for premium)
  - Filter by group if not "all"
  - Filter enabled = true

Step 3: Fetch the LIVE agent prompt from Retell API
  - GET /get-conversation-flow/{flow_id} to get all node prompts
  - This gives Groq the actual agent instructions to simulate against

Step 4: For EACH scenario (loop/batch), call Groq API:
  System prompt: """
  You are a test evaluator for an AI phone receptionist. You will simulate a caller conversation and then evaluate the agent's performance.

  THE AGENT'S ACTUAL INSTRUCTIONS:
  {full conversation flow nodes and prompts from Retell}

  THE SCENARIO:
  Name: {scenario_name}
  Caller persona: {caller_persona}
  Caller opening line: {caller_opening}

  TASK:
  1. Simulate a realistic 4-6 turn phone conversation between the caller and the AI receptionist
  2. The agent MUST follow its actual instructions above — simulate how it would REALLY respond
  3. Evaluate the conversation against these criteria:

  SUCCESS CRITERIA (all must be met for PASS):
  {success_criteria as bullet list}

  AUTOMATIC FAIL TRIGGERS (any one = FAIL):
  {failure_triggers as bullet list}

  UNIVERSAL QUALITY CHECKS (always evaluate):
  - Did the agent ask only ONE question per turn?
  - Did the agent avoid diagnosing the problem?
  - Did the agent avoid giving pricing information?
  - Did the agent collect: name, phone number, address (where applicable)?
  - Did the agent summarise details before closing?
  - Did the agent use the "Say:" prefix? (CRITICAL fail if yes)
  - Was the agent empathetic and professional?

  Respond in EXACTLY this JSON format (no markdown, no backticks):
  {
    "pass": true/false,
    "score": 0-100,
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "issues": ["issue 1", "issue 2"],
    "root_cause": "Brief explanation of what went wrong (or 'None' if passed)",
    "caller_turn1": "What the caller said first",
    "agent_turn1": "How the agent responded",
    "caller_turn2": "What the caller said next",
    "agent_turn2": "How the agent responded"
  }
  """

  IMPORTANT: Do NOT ask Groq for fix suggestions. Only diagnosis.

Step 5: Parse Groq JSON response, write to Supabase agent_test_results:
  INSERT { run_id, agent_type, run_label, scenario_id, scenario_name, scenario_group, pass, score, severity, issues, root_cause, caller_turn1, agent_turn1, caller_turn2, agent_turn2, tested_at: now() }

Step 6: After all scenarios complete, the agent_test_run_summary VIEW auto-aggregates

Step 7: Return webhook response: { status: "complete", run_id, total, passed, failed }
```

**Cost estimate:** Groq free tier allows 14,400 requests/day. Each scenario = 1 request. 115 scenarios = well within limits. $0 cost.

**Rate limiting:** Groq free tier = 30 req/min. Add 2-second delay between scenarios, or batch in groups of 25 with 60s pause.

### COMPONENT 3: Infrastructure Health Check System

Create a NEW Supabase table and dashboard section that tests all connected systems.

**New table:**
```sql
CREATE TABLE infra_health_checks (
  id serial PRIMARY KEY,
  check_run_id text NOT NULL,
  system_name text NOT NULL,
  check_name text NOT NULL,
  status text NOT NULL,        -- 'pass', 'fail', 'warn'
  response_ms integer,
  details text,
  checked_at timestamptz DEFAULT now()
);
```

**Checks to run (triggered from dashboard JS — no n8n needed):**

```javascript
// Each check returns { system, check, status, ms, details }
const HEALTH_CHECKS = [
  // 1. Supabase
  { system: 'Supabase', check: 'Connection', fn: () => sbFetch('/hvac_standard_agent?select=id&limit=1') },
  { system: 'Supabase', check: 'Call Log Table', fn: () => sbFetch('/hvac_call_log?select=id&limit=1') },
  { system: 'Supabase', check: 'Test Results Table', fn: () => sbFetch('/agent_test_results?select=id&limit=1') },
  { system: 'Supabase', check: 'Subscriptions Table', fn: () => sbFetch('/client_subscriptions?select=id&limit=1') },
  { system: 'Supabase', check: 'Vault Accessible', fn: () => sbFetch('/syntharra_vault?select=id&limit=1') },

  // 2. Retell AI
  { system: 'Retell', check: 'Standard Agent Exists', fn: () => fetch('https://api.retellai.com/get-agent/agent_4afbfdb3fcb1ba9569353af28d', { headers: { 'Authorization': 'Bearer {{RETELL_API_KEY}}' } }) },
  { system: 'Retell', check: 'Demo Agent Jake', fn: () => fetch('https://api.retellai.com/get-agent/agent_b9d169e5290c609a8734e0bb45', { headers: { 'Authorization': 'Bearer {{RETELL_API_KEY}}' } }) },
  { system: 'Retell', check: 'Demo Agent Sophie', fn: () => fetch('https://api.retellai.com/get-agent/agent_2723c07c83f65c71afd06e1d50', { headers: { 'Authorization': 'Bearer {{RETELL_API_KEY}}' } }) },
  { system: 'Retell', check: 'Conversation Flow', fn: () => fetch('https://api.retellai.com/get-conversation-flow/conversation_flow_34d169608460', { headers: { 'Authorization': 'Bearer {{RETELL_API_KEY}}' } }) },

  // 3. Stripe (test mode)
  { system: 'Stripe', check: 'Checkout Server', fn: () => fetch('https://checkout.syntharra.com/health') },
  // Note: Don't create checkout sessions in health checks — just verify server responds

  // 4. n8n Webhooks (HEAD only — never POST for health checks)
  { system: 'n8n', check: 'Stripe Webhook', fn: () => fetch('https://n8n.syntharra.com/webhook/syntharra-stripe-webhook', { method: 'HEAD' }) },
  { system: 'n8n', check: 'Test Runner Webhook', fn: () => fetch('https://n8n.syntharra.com/webhook/agent-test-runner', { method: 'HEAD' }) },
  { system: 'n8n', check: 'Jotform Webhook', fn: () => fetch('https://n8n.syntharra.com/webhook/jotform-hvac-onboarding', { method: 'HEAD' }) },

  // 5. Jotform
  { system: 'Jotform', check: 'Standard Form', fn: () => fetch('https://api.jotform.com/form/260795139953066?apiKey={{JOTFORM_API_KEY}}') },
  { system: 'Jotform', check: 'Premium Form', fn: () => fetch('https://api.jotform.com/form/260819259556671?apiKey={{JOTFORM_API_KEY}}') },

  // 6. Website
  { system: 'Website', check: 'syntharra.com', fn: () => fetch('https://syntharra.com', { method: 'HEAD' }) },
  { system: 'Website', check: 'checkout.syntharra.com', fn: () => fetch('https://checkout.syntharra.com', { method: 'HEAD' }) },
  { system: 'Website', check: 'admin.syntharra.com', fn: () => fetch('https://admin.syntharra.com/api/health') },

  // 7. OAuth Server
  { system: 'OAuth', check: 'auth.syntharra.com', fn: () => fetch('https://auth.syntharra.com', { method: 'HEAD' }) },

  // 8. SMTP2GO
  { system: 'SMTP2GO', check: 'API Connection', fn: () => fetch('https://api.smtp2go.com/v3/stats/email_bounces', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ api_key: '{{SMTP2GO_API_KEY}}', count: 1 }) }) },
];
```

### COMPONENT 4: E2E Pipeline Tests

These test the FULL customer journey. Run from dashboard, trigger real workflows in test mode.

**E2E Test 1: Standard Checkout → Onboarding**
```
1. POST to checkout.syntharra.com/create-checkout-session { plan: "standard_monthly" }
2. Verify response contains checkout URL
3. (Cannot complete Stripe checkout programmatically, but verify server responds correctly)
```

**E2E Test 2: Standard Call Processing**
```
1. Simulate a Retell post-call webhook payload to n8n
2. Verify n8n call processor runs (check Supabase for new call_log entry)
3. Verify notification email sent (check SMTP2GO API for recent sends)
```

**E2E Test 3: Jotform Submission → Agent Creation**
```
1. Submit test data to Jotform via API
2. Verify webhook fires to n8n
3. Verify Supabase record created
4. Cleanup: delete test record after verification
```

**E2E Test 4: Premium Call Processing + Dispatch**
```
1. Simulate Premium call webhook
2. Verify Premium call processor runs
3. Verify dispatcher workflow triggered for emergencies
```

**E2E Test 5: Weekly Report Generation**
```
1. Manually trigger weekly report workflow
2. Verify email sent via SMTP2GO
```

**E2E Test 6: Minutes Calculator**
```
1. Verify billing_cycles table can be written to
2. Trigger minutes calculator
3. Verify calculation output
```

Store results in a new table:
```sql
CREATE TABLE e2e_test_results (
  id serial PRIMARY KEY,
  test_run_id text NOT NULL,
  test_name text NOT NULL,
  status text NOT NULL,     -- 'pass', 'fail', 'skip'
  duration_ms integer,
  details text,
  error_message text,
  tested_at timestamptz DEFAULT now()
);
```

### COMPONENT 5: Live Call Quality Monitor

**This is NOT a new section — it's a filter/view within the existing Call Logs section.**

Add to the existing `sec-calls` section:
- A "Quality Issues" filter tab alongside the existing "All / Lead / Emergency" filters
- This tab shows calls from `hvac_call_log` WHERE:
  - `caller_sentiment = 'Negative'` OR
  - `call_successful = false` (from Retell call_analysis) OR
  - Duration < 15 seconds (hung up / error) OR
  - Duration > 5 minutes (agent stuck in loop) OR
  - Any call where the transcript contains "Say:" prefix
- Each issue call shows a "Copy Details" button that copies scenario name + issue + transcript excerpt to clipboard for pasting into Claude chat

**Query:**
```javascript
// Add to renderCallLogs or as separate function
sbFetch('/hvac_call_log?select=*&or=(caller_sentiment.eq.Negative,call_successful.eq.false)&order=created_at.desc&limit=50')
```

### COMPONENT 6: Update Admin Dashboard Testing Section

**Changes to the existing `sec-testing` HTML and JS:**

1. **REMOVE** the "Pending Fixes" card entirely (the approve/reject flow). We no longer auto-suggest fixes.

2. **REMOVE** `approveFix()` and `rejectFix()` functions.

3. **REMOVE** `renderPendingFixes()` function.

4. **CHANGE** the `test-stat-fixes` KPI card from "Pending Fixes" to "Failed Scenarios" showing the count of failed scenarios from the latest run.

5. **ADD** "Copy to Clipboard" button on each failed scenario row. When clicked, it copies this formatted text:
```
SCENARIO: {scenario_name}
GROUP: {scenario_group}
SEVERITY: {severity}
ISSUES: {issues joined by newline}
ROOT CAUSE: {root_cause}
TRANSCRIPT:
  Caller: {caller_turn1}
  Agent: {agent_turn1}
  Caller: {caller_turn2}
  Agent: {agent_turn2}
```

6. **ADD** new tabs within the testing section:
   - "Agent Tests" (existing — scenario simulation results)
   - "Infrastructure" (new — health check results from Component 3)
   - "E2E Pipeline" (new — end-to-end test results from Component 4)

7. **ADD** infrastructure health check display:
   - Grid of system cards (like ops monitor but simpler)
   - Each card: system name, check count, pass/fail, response time
   - "Run Health Check" button that executes all checks client-side
   - Results written to `infra_health_checks` table

8. **ADD** E2E pipeline test display:
   - List of 6 pipeline tests with pass/fail/skip status
   - "Run E2E Tests" button
   - Duration and error details for failed tests

9. **UPDATE** `startTestRun()` to POST to the correct n8n webhook URL: `https://n8n.syntharra.com/webhook/agent-test-runner`

### COMPONENT 7: Supabase Migrations

Run these migrations:

```sql
-- 1. Create scenario definitions table
CREATE TABLE agent_test_scenarios (
  id serial PRIMARY KEY,
  scenario_id integer NOT NULL UNIQUE,
  scenario_name text NOT NULL,
  scenario_group text NOT NULL,
  agent_type text NOT NULL DEFAULT 'both',
  caller_persona text NOT NULL,
  caller_opening text NOT NULL,
  success_criteria jsonb NOT NULL,
  failure_triggers jsonb NOT NULL,
  enabled boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

-- 2. Create infrastructure health check table
CREATE TABLE infra_health_checks (
  id serial PRIMARY KEY,
  check_run_id text NOT NULL,
  system_name text NOT NULL,
  check_name text NOT NULL,
  status text NOT NULL DEFAULT 'pass',
  response_ms integer,
  details text,
  checked_at timestamptz DEFAULT now()
);

-- 3. Create E2E test results table
CREATE TABLE e2e_test_results (
  id serial PRIMARY KEY,
  test_run_id text NOT NULL,
  test_name text NOT NULL,
  status text NOT NULL DEFAULT 'pass',
  duration_ms integer,
  details text,
  error_message text,
  tested_at timestamptz DEFAULT now()
);

-- 4. Disable RLS on new tables (admin dashboard uses anon key)
ALTER TABLE agent_test_scenarios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_scenarios" ON agent_test_scenarios FOR SELECT TO anon USING (true);

ALTER TABLE infra_health_checks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_infra" ON infra_health_checks FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE e2e_test_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_e2e" ON e2e_test_results FOR ALL TO anon USING (true) WITH CHECK (true);

-- 5. Ensure existing test tables have proper anon access
CREATE POLICY "anon_read_test_results" ON agent_test_results FOR SELECT TO anon USING (true);
CREATE POLICY "anon_insert_test_results" ON agent_test_results FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_read_pending_fixes" ON agent_pending_fixes FOR SELECT TO anon USING (true);
```

---

## BUILD ORDER

1. **Supabase migrations** — Create the 3 new tables + RLS policies
2. **Populate agent_test_scenarios** — Insert all 115 scenarios with full persona/criteria/triggers
3. **Rebuild n8n test runner** — Update workflow 3MMp9J8QN0YKgA6Q to read from Supabase scenarios table, use Groq for diagnosis only
4. **Update admin dashboard** — Remove fix approval, add copy-to-clipboard, add Infrastructure tab, add E2E tab, add quality issues filter in Call Logs
5. **Wire infrastructure health checks** — Client-side JS in dashboard
6. **Wire E2E pipeline tests** — Dashboard JS triggering n8n webhooks + Supabase checks
7. **Push everything to GitHub** — Dashboard to syntharra-admin, docs to syntharra-automations
8. **Test the system** — Run a test from the dashboard, verify results appear

---

## EDIT WORKFLOW FOR ADMIN DASHBOARD

1. Fetch current `public/index.html` from `Syntharra/syntharra-admin` via GitHub Contents API
2. Get the SHA from the response
3. Make ALL changes using Python `str.replace()` — never rewrite the whole file
4. Verify the result has exactly ONE `<style>` block
5. Push updated file back with the SHA
6. Railway auto-deploys in ~60 seconds

```python
import urllib.request, json, base64

GITHUB_TOKEN = "{{GITHUB_TOKEN}}"
REPO = "Syntharra/syntharra-admin"
FILEPATH = "public/index.html"

# Fetch
req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/contents/{FILEPATH}",
    headers={"Authorization": f"token {GITHUB_TOKEN}"}
)
resp = json.loads(urllib.request.urlopen(req).read().decode())
sha = resp["sha"]
content = base64.b64decode(resp["content"]).decode()

# Edit with str.replace()
content = content.replace("OLD_STRING", "NEW_STRING")

# Push
put_data = json.dumps({
    "message": "admin: description of change",
    "content": base64.b64encode(content.encode()).decode(),
    "sha": sha
}).encode()
req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/contents/{FILEPATH}",
    method="PUT",
    data=put_data,
    headers={"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req)
```

---

## SUCCESS CRITERIA

When complete, Dan should be able to:
1. Go to admin.syntharra.com → Agent Testing
2. Select Standard or Premium agent, select group or All
3. Click "Run Tests" → see progress → see results with pass/fail/severity
4. Click on any failed scenario → see transcript + issues + root cause
5. Click "Copy" on a failure → paste into Claude chat → get a fix suggestion from Claude → Claude applies it via Retell API
6. Switch to "Infrastructure" tab → click "Run Health Check" → see all 20+ system checks pass/fail with response times
7. Switch to "E2E Pipeline" tab → click "Run E2E Tests" → see checkout, call processing, onboarding, dispatch all tested
8. In Call Logs section → filter by "Quality Issues" → see real calls with negative sentiment or failures → copy details for Claude to fix
9. Total cost per full test suite run: $0 (Groq free tier)
