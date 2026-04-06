# Session Log — 2026-04-06 — SMTP2GO → Brevo Migration (Complete)

## Summary
Completed full migration from SMTP2GO to Brevo across all systems. Zero active SMTP2GO references remaining.

## Work Completed

### n8n Workflows (48 audited)
- **Weekly Newsletter (6LXpGffcWSvL6RxW)** — Node label "Send via SMTP2GO" renamed "Send via Brevo" (code was already Brevo)
- **HVAC Prem Onboarding (kz1VmwNccunRMEaF)**
  - `Send Welcome Email` — Fixed corrupt Brevo body format (SMTP2GO body structure was left in — PDFs were NOT attaching). Fixed: `to`, `attachment`, `content` fields all corrected.
  - `Send Internal Notification` → Converted from Brevo email to `onboarding@syntharra.com` **→ Slack `chat.postMessage` to C0AQP081RCN**. Node renamed `Slack: Premium Client Onboarded`.
  - `Send Google OAuth Email` — Stale comment `// Send email via SMTP2GO` → `// Send email via Brevo`
  - `Send Welcome Email` — Historical comment `// SMTP2GO removed` cleaned

### Ops Monitor (syntharra-ops-monitor GitHub repo)
- `src/monitors/email.js` — Check name "SMTP2GO service" → "Brevo service", status URL → `status.brevo.com`, credential env var → `BREVO_API_KEY`
- `src/utils/alertManager.js` — Full migration: SMTP2GO REST API → Brevo REST API (`api.brevo.com/v3/smtp/email`, `api-key` header, correct response schema). `smtp2goApiKey` → `brevoApiKey`.
- `.env.example` — SMTP2GO block replaced with `BREVO_API_KEY=your_brevo_api_key_here`
- `BREVO_API_KEY` set in Railway env vars for ops monitor service (service ID `7ce0f943`)

### Archived workflows (NOT fixed — cannot edit archived)
- 3x `Premium — Integration Connected Handler` (SziSvI1zl49cs3cQ, OXuB3WR23fg0MmEu, IS5eC0SEzIv76TPQ)
- These have `Alert Onboarding Team`, `Alert Unexpected Status`, `Send Holding Email to Client` as native emailSend nodes using SMTP2GO credential
- **Dead code — archived, not executing. No operational risk.**
- Replacement Code nodes written locally but cannot be pushed (Railway returns "Cannot update archived workflow")

## Final Audit Result
- **Active workflows with SMTP2GO: 0 / 48** ✅
- **Archived workflows with SMTP2GO: 3** (dead code)

## Pending
- Ops monitor Railway deployment is **QUEUED** (not yet running new code). Builds triggered but queued — service may need manual redeploy from Railway dashboard to pick up Brevo changes. Current dashboard still shows "SMTP2GO service: Operational" from old deployed binary.
- Standard Onboarding internal emails already disabled (DISABLED since 2026-04-03, replaced by Slack).

## Session Reflection
1. **What did I get wrong?** Tried Railway `ServiceInstanceRedeployInput` mutation which doesn't exist — correct mutation is bare `serviceInstanceRedeploy`. Wasted one API call.
2. **Wrong assumption?** Assumed `syntharra-ops-monitor` GitHub repo was 404 because MCP returned 404 — it's actually a private repo the MCP token couldn't access. Raw API with token worked fine.
3. **Do differently?** When MCP returns 404 for a repo, immediately try raw GitHub API with token before concluding the repo doesn't exist.
4. **Pattern emerged?** n8n archived workflows return "Cannot update an archived workflow" — always check `isArchived` before attempting to edit. For SMTP2GO in archived workflows: document as dead code, don't attempt to fix.
5. **Architecture decisions?** None requiring ARCHITECTURE.md update.
6. **Verified patterns?** Brevo body format confirmed: `sender: {name,email}`, `to: [{email}]`, `htmlContent`, `attachment: [{name,content}]`. Slack `chat.postMessage` confirmed working in Prem Onboarding. Ops monitor Railway service ID: `7ce0f943`.
