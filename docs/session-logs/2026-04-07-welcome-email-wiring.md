# 2026-04-07 — Welcome Email Wiring (Std + Prem Onboarding)

## Scope
Wired canonical "Your AI Receptionist is Live" welcome email into both HVAC Standard (4Hx7aRdzMl5N0uJP) and HVAC Premium (kz1VmwNccunRMEaF) n8n onboarding workflows.

## Done
- Brevo vendor swap (was SMTP2GO): POST api.brevo.com/v3/smtp/email, header api-key, vault service_name='Brevo'.
- Standard: added Send Welcome Email Code node as parallel branch off Publish Retell Agent[0] alongside HubSpot Update Deal. Active.
- Premium: replaced existing Send Welcome Email body in place (preserved id/connections). Active.
- Email body: white SYNTHARRA wordmark on violet header, client greeting, 3-step Getting Started, green PDF-attached banner, dashboard CTA, agent ID pill.
- Live PDF fetch + base64 + Brevo attachment[].
- Graceful skip when lead_email or agent_phone_number missing (Telnyx gated on Stripe ID).
- Dashboard verified live.

## Logo Fix
First attempt used hosted email-logo.png which rendered as broken-image. Root cause: trusted repo file without rendering in browser. Fix: inline <p>SYNTHARRA</p> wordmark (28px/900/ls6px white). Verified via Chrome preview. Both workflows redeployed PUT 200 / activate 200.

## Pending
- Live E2E via JotForm webhook.
- Telnyx + Stripe live activation.
- n8n submission_id P0 (separate).

## Lessons
- Never claim image fix without rendering in a real browser.
- Inline HTML wordmarks > hosted PNGs for email.
- JSON-escaped match when patching embedded HTML in n8n PUT payloads.
- n8n MCP strips credentials; use raw REST PUT + activate.
