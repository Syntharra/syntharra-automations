# Session Log — 2026-03-30 — Onboarding Pack

## Summary
Built the complete client onboarding pack system for Standard and Premium HVAC clients.

## Files Created / Updated

### New files
- `onboarding-packs/build_faq_pdf.py` — ReportLab PDF generator (13 pages, 9 sections)
- `onboarding-packs/build_sample_emails.py` — sample email renderer for testing
- `onboarding-packs/ONBOARDING-PACK.md` — documentation

### Updated files
- `hvac-premium/email-templates/welcome-email-builder.js` — v2 with Premium badge, integration status, WhatsApp block (commented)

## Key Decisions
1. **Existing Standard email unchanged** — the `Build Welcome Email HTML` node in workflow `4Hx7aRdzMl5N0uJP` stays as-is. PDF attaches alongside it.
2. **Premium email sends first** (with agent go-live), integration OAuth emails send in parallel. Ensures AI is live immediately.
3. **WhatsApp block** fully coded in Premium builder, commented out. Enable when number ready: set `WHATSAPP_NUMBER` and uncomment `whatsappSection`.
4. **Integration badges** = "Instructions sent" (purple `#6C63FF`) not "Connected" — accurate at send time.
5. **Weekly report** confirmed fires at 6pm Sunday in each client's local timezone — no change needed.

## PDF Structure (13 pages)
1. Cover (full logo, dark title block, stat strip)
2. Table of Contents
3–4. Section 1: Call Forwarding (iPhone, Android, carrier codes, VoIP)
5. Section 1 continued (carrier cards)
6. Section 2: How It Works
7–8. Section 3: FAQs (14 questions, 3 categories)
9. Sections 4+5: Dashboard & Notifications
10. Sections 6+7: Making Changes & Billing
11–12. Section 8: Premium Integrations (Calendar, CRM, API keys)
13. Section 9: Getting Support

## Next Steps
- Wire PDF attachment into n8n `Send Setup Instructions Email` node (both Standard + Premium)
- Enable WhatsApp block when number is ready
- Stripe live mode cutover
