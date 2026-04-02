# Syntharra — n8n Workflows
> Audited live from n8n on 2026-04-02. 32 active workflows.
> Source of truth: always query n8n directly, never rely on memory for IDs.
> Note: n8n REST API does not support setting description via PUT on this version.
>       Descriptions are maintained in this file only. Set manually in n8n UI if needed.

## n8n Instance
- URL: `https://n8n.syntharra.com`
- API key: ends in `NqU` (Railway env)
- Rules: PUT accepts only name/nodes/connections/settings.executionOrder — no extra fields
- Always click Publish after edits. NEVER POST to webhooks for health checks — HEAD only.

---

## Standard Pipeline (7)

| ID | Name | Description |
|---|---|---|
| `xKD3ny6kfHL0HHXq` | Stripe Workflow | Listens for Stripe checkout.session.completed. Saves payment data to Supabase, sends branded welcome email to client, fires internal notification to onboarding@syntharra.com. |
| `4Hx7aRdzMl5N0uJP` | HVAC AI Receptionist - JotForm Onboarding | Triggered by Jotform Standard submission. Creates client record in Supabase, provisions Retell agent, sends You're Live email, notifies onboarding@syntharra.com. |
| `Kg576YtPM9yEacKn` | HVAC Call Processor - Retell Webhook | Receives Retell post-call webhook for Standard clients. Parses transcript, scores lead, geocodes address, logs to hvac_call_log, fires internal alert on errors only. |
| `z1DNTjvTDAkExsX8` | Monthly Minutes Calculator & Overage Billing | Runs monthly per client. Calculates minutes used vs plan allowance, records billing cycle in Supabase, triggers overage charge if applicable. |
| `Wa3pHRMwSjbZHqMC` | Usage Alert Monitor (80% & 100% Warnings) | Monitors all client minute usage daily. Sends 80% and 100% warning emails to clients and admin alerts to admin@syntharra.com. |
| `iLPb6ByiytisqUJC` | HVAC Weekly Lead Report | Runs every Sunday at 6pm per-client timezone. Fetches week's call data and sends branded weekly lead report to each client. |
| `lXqt5anbJgsAMP7O` | Send Welcome Email (Manual) | Manual trigger to resend the welcome email to a specific client. Used when initial delivery fails or client requests a resend. |

## Premium Pipeline (11)

| ID | Name | Description |
|---|---|---|
| `kz1VmwNccunRMEaF` | HVAC Prem Onboarding | Triggered by Jotform Premium submission. Creates Premium client record in Supabase, sends integration setup email with OAuth links for Google Calendar or Outlook. |
| `STQ4Gt3rH8ptlvMi` | HVAC Premium Call Processor | Receives Retell post-call webhook (`/webhook/retell-hvac-premium-webhook`) for Premium clients. Rebuilt 2026-04-02 from Standard base (fixed `filter` node crash). Parses transcript via GPT, flattens nested JSON response, scores lead, logs to hvac_call_log with call_tier=Premium. |
| `73Y0MHVBu05bIm5p` | Premium Integration Dispatcher | Routes Premium call booking actions to the correct platform dispatcher (Google Calendar, Outlook, Calendly, Jobber, or HubSpot) based on client's connected integration. |
| `rGrnCr5mPFP2TIc7` | Premium Dispatcher — Google Calendar | Handles get_slots and create_booking for Google Calendar. Fetches availability and creates events via Google Calendar API using stored OAuth tokens from vault. |
| `La99yvfmWg6AuvM2` | Premium Dispatcher — Outlook | Handles get_slots, create_booking, cancel_booking for Outlook/Microsoft 365 via Microsoft Graph API. Refreshes tokens from vault on expiry. |
| `b9xRG7wtqCZ5fdxo` | Premium Dispatcher — Calendly | Webhook dispatcher for Calendly. get_slots via event_type_available_times; create_booking creates a one-time scheduling link. Logs to hvac_call_log. |
| `BxnR17qUfAb5BZCz` | Premium Dispatcher — Jobber | Webhook dispatcher for Jobber. get_slots computed from business hours; create_booking creates a Jobber request via GraphQL. Logs to hvac_call_log. |
| `msEy13eRz66LPxW6` | Premium Dispatcher — HubSpot | Webhook dispatcher for HubSpot. get_slots from meeting link + business hours fallback; create_booking finds/creates contact and creates CRM meeting object. |
| `a0IAwwUJP4YgwgjG` | Premium — Integration Connected Handler | Handles OAuth integration callbacks. Inserts activation queue record, sends setup emails, runs auto-activation test booking, triggers You're Live email or routes to manual review. |
| `ptDdy38HKt9DUOAV` | Premium — Send You're Live Email | Triggered by auto-activation or manual activation. Fetches client details, sends polished You're Live email, logs activation event to hvac_call_log. |
| `5vphecmEhxnwFz2X` | Premium — Daily Token Refresh | Runs daily at 02:00 UTC. Checks all Premium OAuth client token expiry, refreshes tokens expiring within 2 days. On failure marks token_expired and sends reconnect email. |

## Shared Infrastructure (9)

| ID | Name | Description |
|---|---|---|
| `44WfbVmJ7Zihcwgs` | Nightly GitHub Backup | Runs nightly. Exports all n8n workflow JSON files and pushes them to Syntharra/syntharra-automations as a versioned backup. |
| `AU8DD5r6i6SlYFnb` | Auto-Enable MCP on All Workflows | Runs every 6 hours. Calls n8n API to ensure availableInMCP=true on all workflows, keeping Claude MCP access active. |
| `4aulrlX1v8AtWwvC` | Email Digest — Daily 6am GMT | Runs daily at 6am GMT. Fetches unread emails from all 9 Syntharra inboxes, summarises with Groq AI (llama-3.3-70b), sends digest to admin@syntharra.com. |
| `13cOIXxvj83NfDqQ` | Publish Retell Agent | Manual trigger to publish a Retell agent via the Retell API. Always run after editing any agent — never leave an agent unpublished. |
| `URbQPNQP26OIdYMo` | E2E Test Cleanup — 5 Min Delayed Delete | Receives webhook trigger, waits 5 minutes, then deletes the specified test record from Supabase. Used by E2E pipeline tests to self-clean. |
| `LF8ZSYyQbmjV4rN0` | Jotform Webhook Backup Polling | Runs every 15 minutes. Polls Jotform for recent submissions and flags any missing from Supabase (catches missed webhooks). |
| `ofoXmXwjW9WwGvL6` | Daily Transcript Analysis + Jailbreak Monitor | Runs daily. Analyses call transcripts via Groq for quality issues, prompt injection attempts, and agent performance. Logs to transcript_analysis table. |
| `ngK02cSgGmvawCot` | Nightly PII Retention Cleanup | Runs nightly. Redacts PII from call records older than 90 days and removes old transcript analysis data per retention policy. |
| `ALFSzzp3htAEjwkJ` | Weekly Client Health Score Calculator | Runs weekly. Calculates health scores per client based on call volume trends and engagement signals. Stores results in client_health_scores. |

## Marketing — Pre-Launch (5)
> Active but not receiving real traffic yet. Ready to fire at launch.

| ID | Name | Description |
|---|---|---|
| `QY1ZFtPJFsU5h6wQ` | Website Lead → AI Readiness Score Email | Triggered by website demo form submission. Scores the lead's AI readiness via Groq and sends a personalised AI readiness score email via SMTP2GO. |
| `hFU0ZeHae7EttCDK` | Website Lead → Free Report Email | Triggered by website demo form submission. Sends a free HVAC AI guide PDF report to the lead via SMTP2GO. |
| `6LXpGffcWSvL6RxW` | Weekly Newsletter - Syntharra | Sends the weekly Syntharra newsletter to all subscribed contacts on schedule. Pre-launch — subscriber list not yet active. |
| `Eo8wwvZgeDm5gA9d` | Newsletter Unsubscribe Webhook | Webhook endpoint handling newsletter unsubscribe requests. Removes contact from mailing list in Supabase. |
| `j8hExewOREmRp3Oq` | Blog Auto-Publisher | Automatically publishes new blog posts to the Syntharra website on schedule or manual trigger. Pre-launch — not yet active. |

---

## Recently Archived (do not reference)

| ID | Name | Reason |
|---|---|---|
| `HeG3aJQBXyRPKSXA` | SYNTHARRA_TEST_RUNNER | Agent scenario testing removed — Supabase tables deleted |
| `UKEoUeNqYvDDJv79` | [TEST STUB] Retell Tool Dispatcher | Development stub — never wired to live agent |

---

## Webhook Paths (all on n8n.syntharra.com)

| Purpose | Path |
|---|---|
| Standard call processor | `/webhook/hvac-std-call-processor` |
| Premium call processor | `/webhook/hvac-prem-call-processor` |
| Stripe | `/webhook/syntharra-stripe-webhook` |
| Jotform Standard onboarding | `/webhook/jotform-hvac-onboarding` |
| E2E cleanup | `/webhook/e2e-test-cleanup` |

---

## API Note
n8n REST API PUT endpoint does NOT accept `description` as a field on this version.
Descriptions are maintained in this file. To set in n8n UI: open workflow → Settings → Description.
