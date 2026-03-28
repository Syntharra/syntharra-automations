# SYNTHARRA — CHAT HANDOFF DOCUMENT
## Full Context Summary — Premium Integration System

### WHO I AM
My name is Daniel. I am the owner of Syntharra, a global AI Solutions company that specialises in providing AI Receptionists to trade industry businesses worldwide (HVAC, plumbing, cleaning, electricians, landscaping, etc.).
- Email: daniel@syntharra.com
- Timezone: GMT
- Communication: Voice on mobile
- Approach: Claude executes directly using MCP connections where possible

### Tech Stack
- **n8n** (self-hosted at syntharra.app.n8n.cloud) — all workflow automation
- **Supabase** — primary database for all client and integration data
- **Jotform** — client onboarding forms
- **Retell AI** — the AI phone agent platform
- **GitHub Pages** — Syntharra website
- **Stripe** — payments

---

## WHAT WE'VE BUILT

### The Two Products
- **Standard Plan** — Lead capture only. Client submits a Jotform → Apps Script creates a Retell AI agent → n8n receives call transcripts → GPT scores leads → SMS/email alerts sent to client. Already built for HVAC.
- **Premium Plan** — Everything in Standard PLUS: CRM integration, calendar booking, scheduling, rescheduling, cancellation, and client alerts. Designed in full.

---

## THE PREMIUM INTEGRATION SYSTEM — FULL DESIGN

### How It Works (Overview)
1. Premium client submits the Jotform onboarding form
2. They select which CRM and Calendar they use from dropdowns
3. If OAuth platform → they receive an email with a 1-click auth link → they approve access on their CRM/Calendar → tokens are stored encrypted in Supabase → integration goes live automatically
4. If API key platform → they receive a branded Syntharra setup guide by email with step-by-step instructions → they submit their API key via a secure form → key is validated and stored encrypted in Supabase
5. n8n runs a daily health check at 6:00 AM GMT testing every active integration
6. If a connection breaks → the client is automatically emailed a reconnect alert
7. Daniel receives a daily report email at 6:00 AM GMT to daniel@syntharra.com with full status of all client integrations

---

## SUPABASE DATABASE — 5 TABLES

### clients
Master record for every Syntharra Premium client. One row per business. Created when they submit the Jotform. Everything else links back here via client_id.

Key columns: `id`, `company_name`, `contact_email`, `industry`, `plan` (standard/premium), `retell_agent_id`, `retell_llm_id`, `onboarding_status` (pending → integration_pending → active)

### integrations
One row per platform per client. The core credentials table. Holds encrypted OAuth tokens or API keys for every CRM and Calendar a client has linked.

Key columns: `client_id`, `integration_type` (crm/calendar), `platform`, `auth_method` (oauth/apikey), `access_token` (encrypted), `refresh_token` (encrypted), `api_key` (encrypted), `token_expiry`, `auth_status` (pending/active/broken/expired), `failure_count`, `last_failure_reason`

### auth_sessions
Temporary rows for every OAuth login attempt. Hold a unique state token (UUID) linking the OAuth callback to the right client. Expire after 30 minutes. Single-use.

### health_check_log
Audit trail of every daily health check. One row per integration per day. Values: ok, refreshed, failed.

### guide_sends
Records every time a branded API key setup guide is emailed to a client. Prevents duplicate sends. Tracks guide_version.

---

## PLATFORM REGISTRY — ALL SUPPORTED PLATFORMS

### CRMs — OAuth
| Platform | Trade Fit | n8n Native |
|---|---|---|
| GoHighLevel | ⭐⭐⭐⭐⭐ | ✅ PRIORITY 1 |
| Jobber | ⭐⭐⭐⭐⭐ | ❌ HTTP node |
| HubSpot | ⭐⭐⭐ | ✅ Yes |
| Zoho CRM | ⭐⭐⭐ | ✅ Yes |
| Keap / Infusionsoft | ⭐⭐⭐ | ✅ Yes |
| Pipedrive | ⭐⭐ | ✅ Yes |
| Salesforce | ⭐⭐ | ✅ Yes |
| ServiceM8 | ⭐⭐⭐⭐ | ❌ HTTP node |

### CRMs — API Key
| Platform | Trade Fit |
|---|---|
| ServiceTitan | ⭐⭐⭐⭐⭐ |
| Housecall Pro | ⭐⭐⭐⭐⭐ |
| FieldEdge | ⭐⭐⭐⭐ |
| Workiz | ⭐⭐⭐⭐ |
| Freshsales | ⭐⭐ |

### Calendars — OAuth
Google Calendar ✅ PRIORITY 1 | Outlook/M365 ✅ | GoHighLevel Calendar ✅ | Calendly ✅ | Acuity ❌ HTTP | Setmore ❌ HTTP | Square Appointments ❌ HTTP

### Calendars — API Key
Cal.com | SimplyBook.me | BookingKoala

---

## 6 N8N WORKFLOWS TO BUILD

1. **premium-onboarding-intake** — Jotform trigger → creates client + integration records → sends OAuth invite or API key guide email
2. **oauth-callback-handler** — handles OAuth redirect, exchanges code for tokens, encrypts, stores in Supabase
3. **token-refresh-handler** — sub-workflow, refreshes near-expiry tokens, flags broken on failure
4. **broken-connection-alert** — emails client, logs failure, generates fresh re-auth link
5. **daily-health-check** — cron 0 6 * * * GMT, tests all active integrations, sends Daniel daily HTML status report to daniel@syntharra.com
6. **api-key-submission-handler** — receives API key, validates against platform, stores encrypted

---

## OAUTH SERVER (auth.syntharra.com)
Node.js/Express. Three endpoints:
- `GET /connect` — generates OAuth URL, redirects client
- `GET /callback` — exchanges code for tokens, encrypts, stores, returns success page
- `POST /submit-api-key` — receives API keys, passes to n8n

Security: AES-256-CBC encryption, single-use state tokens, 30-min session expiry.

---

## 4 EMAIL TEMPLATES
All use: #0D0D0D background, #C9A84C gold accent, white text, Helvetica Neue.

1. `oauth-invite-email.html` — "Connect Your [Platform] — 1 Click"
2. `apikey-invite-email.html` — "Setup Guide Inside"
3. `integration-success-email.html` — "✅ [Platform] Connected Successfully!"
4. `reconnect-alert-email.html` — "⚠️ Action Required — Reconnect Your [Platform]"

---

## PRIORITY BUILD ORDER

1. Supabase schema (5 tables)
2. platform-registry.js
3. Workflow 1: premium-onboarding-intake
4. OAuth server (auth.syntharra.com)
5. Workflow 2: oauth-callback-handler
6. Workflow 4: broken-connection-alert
7. Workflow 5: daily-health-check (6am GMT)
8. ServiceTitan + Housecall Pro guides
9. Workflow 3: token-refresh-handler
10. Workflow 6: api-key-submission-handler
11. All remaining guides
12. Jotform updates

---

## HOW TO USE IN A NEW CHAT
Paste this entire document into a new Claude chat, then say:

> "You now have full context on what we've been building. I want to continue from where we left off on the Syntharra Premium Integration System."

---

*Syntharra — AI Receptionist for the Trades | daniel@syntharra.com | GMT*
*Last updated: $(date -u +"%Y-%m-%d %H:%M UTC")*
