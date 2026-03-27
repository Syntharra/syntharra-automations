# SYNTHARRA — CHAT HANDOFF DOCUMENT
## Full Context Summary — Premium Integration System

### WHO I AM
My name is Daniel. I am the owner of Syntharra, a global AI Solutions company that specialises in providing AI Receptionists to trade industry businesses worldwide (HVAC, plumbing, cleaning, electricians, landscaping, etc.).
- Email: daniel@syntharra.com
- Timezone: GMT
- Tech stack: n8n, Supabase, Jotform, Retell AI, GitHub Pages, Stripe

---

### THE TWO PRODUCTS
- **Standard Plan** — Lead capture only. Jotform → Retell AI agent → n8n call transcripts → GPT lead scoring → SMS/email alerts. Already built for HVAC.
- **Premium Plan** — Everything in Standard PLUS: CRM integration, calendar booking, scheduling, rescheduling, cancellation, client alerts.

---

### PREMIUM INTEGRATION SYSTEM — FULL DESIGN

#### How It Works
1. Premium client submits Jotform onboarding form
2. Selects CRM and Calendar from dropdowns
3. If OAuth → email with 1-click auth link → approve access → tokens stored encrypted in Supabase → integration live
4. If API key → branded setup guide email → submit API key via secure form → validated and stored encrypted
5. n8n daily health check at 6:00 AM GMT testing all active integrations
6. Broken connection → auto email reconnect alert to client
7. Daniel receives daily status report at 6:00 AM GMT

---

### SUPABASE DATABASE — 5 TABLES

#### clients
Master record for every Premium client. One row per business. Created on Jotform submit.
- Key columns: `id`, `company_name`, `contact_email`, `industry`, `plan` (standard/premium), `retell_agent_id`, `retell_llm_id`, `onboarding_status` (pending → integration_pending → active)

#### integrations
One row per platform per client. Core credentials table.
- Key columns: `client_id`, `integration_type` (crm/calendar), `platform`, `auth_method` (oauth/apikey), `access_token` (encrypted), `refresh_token` (encrypted), `api_key` (encrypted), `token_expiry`, `auth_status` (pending/active/broken/expired), `failure_count`, `last_failure_reason`

#### auth_sessions
Temporary rows for OAuth login attempts. UUID state token linking callback to client. 30-min expiry. Single-use.

#### health_check_log
Audit trail of daily health checks. One row per integration per day. Values: ok, refreshed, failed.

#### guide_sends
Records every API key setup guide email sent. Prevents duplicates. Tracks `guide_version`.

---

### PLATFORM REGISTRY

#### CRMs — OAuth
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

#### CRMs — API Key
| Platform | Trade Fit |
|---|---|
| ServiceTitan | ⭐⭐⭐⭐⭐ |
| Housecall Pro | ⭐⭐⭐⭐⭐ |
| FieldEdge | ⭐⭐⭐⭐ |
| Workiz | ⭐⭐⭐⭐ |
| Freshsales | ⭐⭐ |

#### Calendars — OAuth
Google Calendar ✅ PRIORITY 1 | Outlook/M365 ✅ | GoHighLevel Calendar ✅ | Calendly ✅ | Acuity ❌ HTTP | Setmore ❌ HTTP | Square Appointments ❌ HTTP

#### Calendars — API Key
Cal.com | SimplyBook.me | BookingKoala

---

### 6 N8N WORKFLOWS TO BUILD

1. **premium-onboarding-intake** — Jotform trigger → creates client + integration records → sends OAuth invite or API key guide email
2. **oauth-callback-handler** — handles OAuth redirect, exchanges code for tokens, encrypts, stores in Supabase
3. **token-refresh-handler** — sub-workflow, refreshes near-expiry tokens, flags broken on failure
4. **broken-connection-alert** — emails client, logs failure, generates fresh re-auth link
5. **daily-health-check** — cron 0 6 * * * GMT, tests all active integrations, sends Daniel daily HTML status report
6. **api-key-submission-handler** — receives API key, validates against platform, stores encrypted

---

### OAUTH SERVER (auth.syntharra.com)
Node.js/Express. Three endpoints:
- `GET /connect` — generates OAuth URL, redirects client
- `GET /callback` — exchanges code for tokens, encrypts, stores, returns success page
- `POST /submit-api-key` — receives API keys, passes to n8n

Security: AES-256-CBC encryption, single-use state tokens, 30-min session expiry.

---

### 4 EMAIL TEMPLATES
All use: #0D0D0D background, #C9A84C gold accent, white text, Helvetica Neue.
1. `oauth-invite-email.html` — "Connect Your [Platform] — 1 Click"
2. `apikey-invite-email.html` — "Setup Guide Inside"
3. `integration-success-email.html` — "✅ [Platform] Connected Successfully!"
4. `reconnect-alert-email.html` — "⚠️ Action Required — Reconnect Your [Platform]"

---

### PRIORITY BUILD ORDER
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

*Last updated: 2026-03-27*
*Syntharra — AI Receptionist for the Trades | daniel@syntharra.com | GMT*
