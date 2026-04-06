# Open Tasks — Syntharra
_Updated: 2026-04-06 | Under 40 lines | Open work only_

## Pre-Launch
- [ ] Ops monitor Railway redeploy — queued builds not processing. Manual redeploy needed in Railway dashboard to apply Brevo email.js changes. Service: 7ce0f943.
- [ ] Stripe go-live: activate account → recreate products/prices/coupons/webhook → update to sk_live_
- [ ] Telnyx SMS approval pending — placeholder in ops monitor

## Agent / Testing
- [ ] E2E test suite run before launch — both Standard and Premium pipelines

## Infrastructure
- [ ] n8n workflow labelling audit — ensure all workflows labelled before launch
- [ ] Archived workflows (3x Premium Integration Handler) — contain dead SMTP2GO emailSend nodes. Low priority — not executing.

## Marketing
- [ ] First cold email batch — system built (n8n + SMTP2GO→Brevo), not yet activated
- [ ] Google Ads campaigns — landing pages live, campaigns not yet running
