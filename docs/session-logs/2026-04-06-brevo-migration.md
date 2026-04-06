# Session Log — 2026-04-06 — Brevo Email Migration

## Summary
Completed full project-wide migration from SMTP2GO to Brevo as the transactional email provider.
All 24 email-sending code nodes across 48 n8n workflows updated to Brevo API format.
Zero active SMTP2GO references remain in any workflow.

---

## Context
Dan switched to Brevo and provided the API key. Migration was split across two sessions due to
n8n MCP SDK validation errors blocking the first attempt. Second session used direct n8n REST API
(PUT /api/v1/workflows/{id}) bypassing the MCP tool entirely — all updates succeeded.

---

## Brevo API Key
Stored in Supabase vault: `service_name='Brevo', key_type='api_key'`
Key prefix: `xkeysib-ebae964c8f...` (full value in vault)

---

## Workflows Updated

| Workflow ID | Name | Nodes Updated |
|---|---|---|
| QY1ZFtPJFsU5h6wQ | Website Lead → AI Readiness Score Email | 1 (prev session) |
| hFU0ZeHae7EttCDK | Website Lead → Free Report Email | 1 (prev session) |
| lXqt5anbJgsAMP7O | Send Welcome Email (Manual) | 1 (prev session) |
| 5vphecmEhxnwFz2X | Premium — Daily Token Refresh | 2 (prev session) |
| ptDdy38HKt9DUOAV | Premium — Send You're Live Email | 1 |
| Wa3pHRMwSjbZHqMC | Usage Alert Monitor (80% & 100%) | 1 |
| xKD3ny6kfHL0HHXq | Stripe Workflow | 2 |
| a0IAwwUJP4YgwgjG | Premium — Integration Connected Handler | 5 |
| 4Hx7aRdzMl5N0uJP | HVAC AI Receptionist - JotForm Onboarding | 3 |
| 6LXpGffcWSvL6RxW | Weekly Newsletter - Syntharra | 1 |
| kz1VmwNccunRMEaF | HVAC Prem Onboarding | 7 |

**Total: 24 code nodes updated across 11 workflows. 48/48 workflows verified clean.**

---

## API Format Change (SMTP2GO → Brevo)

### Old (SMTP2GO)
```javascript
await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://api.smtp2go.com/v3/email/send',
  headers: { 'Content-Type': 'application/json' },
  body: {
    api_key: 'api-0BE30DA64A074BC79F28BE6AEDC9DB9E',
    sender: 'noreply@syntharra.com',
    to: [recipientEmail],
    subject: 'Subject',
    html_body: html
  },
  json: true
});
```

### New (Brevo)
```javascript
const BREVO_KEY = 'xkeysib-...'; // or use env/vault
await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://api.brevo.com/v3/smtp/email',
  headers: { 'api-key': BREVO_KEY, 'Content-Type': 'application/json' },
  body: {
    sender: { name: 'Syntharra AI', email: 'noreply@syntharra.com' },
    to: [{ email: recipientEmail }],
    subject: 'Subject',
    htmlContent: html
  },
  json: true
});
```

Key differences:
- Auth: header `api-key` (not body `api_key`)
- URL: `api.brevo.com/v3/smtp/email`
- sender: object `{ name, email }` (not string)
- to: array of objects `[{ email: '...' }]` (not strings)
- Body key: `htmlContent` (not `html_body`)

---

## Edge Cases Handled

1. **SMTP2GO_KEY variable references** — Some nodes used `if (!SMTP2GO_KEY)` guards.
   All `SMTP2GO_KEY` → `BREVO_KEY` (would have caused early returns without this fix).

2. **fetch() calls** — Outlook OAuth and Placeholder nodes used `await fetch()` directly.
   Converted to `await this.helpers.httpRequest()` with Brevo format.

3. **Commented-out code** — Some nodes had SMTP2GO in inactive comments. Updated for consistency.

4. **`_reason: 'Sending via SMTP2GO'`** → `'Sending via Brevo'` in Premium Onboarding.

---

## Verification
Final scan: `✅ Zero active SMTP2GO references across all 48 workflows. 24 Brevo nodes confirmed.`

---

## Session Reflection

**What was done inefficiently?**
First agent wave (MCP-based) failed for 4/8 workflows — n8n MCP SDK validation errors.
Should have gone direct REST API from the start.

**Wrong assumption?**
Initial scan by topic "email" missed Weekly Newsletter and Premium Onboarding.
Always run full 48-workflow scan before declaring done.

**Do differently next time?**
1. Start with full workflow scan before targeting specific IDs
2. Use direct REST API for n8n updates (not MCP tool)
3. Run full verification scan at end

---

## Open Tasks Carried Forward
- Update syntharra-email skill in GitHub with Brevo patterns
- Cold email docs: reference Brevo not SMTP2GO
