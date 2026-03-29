# Session Log — 2026-03-29

## Summary
Major website overhaul session. Built out full marketing infrastructure, lead generation system, and newsletter automation.

## What was built

### Blog Content (12 new articles)
- ai-receptionist-roi-calculator.html (Jan 2025)
- after-hours-calls-trade-business.html (Dec 2024)
- hvac-emergency-call-handling.html (Nov 2024)
- plumbing-lead-capture.html (Oct 2024)
- electrical-contractor-scheduling.html (Sep 2024)
- trade-business-customer-experience.html (Aug 2024)
- ai-vs-hiring-receptionist.html (Jul 2024)
- google-business-profile-trades.html (Jun 2024)
- cost-of-missed-calls-contractors.html (May 2024)
- hvac-spring-checklist.html (Apr 2024)
- plumbing-business-growth-strategies.html (Mar 2024)
- why-contractors-lose-to-competitors.html (Feb 2024)
Total blog library: 20 articles

### New Pages Built
- how-it-works.html — 5-step onboarding walkthrough
- about.html — Company story, values, mission
- calculator.html — Standalone missed revenue calculator (lead magnet)
- plan-quiz.html — "Which plan is right?" quiz (lead magnet)
- faq.html — Comprehensive FAQ, 30+ questions, 6 categories, search, moved from homepage
- ai-readiness.html — Standalone AI readiness quiz (lead magnet)
- hvac.html — HVAC industry landing page
- plumbing.html — Plumbing industry landing page
- electrical.html — Electrical industry landing page
- lp/hvac-answering-service.html — Google Ads landing page (noindex)
- lp/plumbing-answering-service.html — Google Ads landing page (noindex)
- lp/electrical-answering-service.html — Google Ads landing page (noindex)

### Branding & Design Updates
- Blog author sections: replaced lightbulb emoji with Syntharra logo (favicon-white.svg) across all 20 articles
- Case studies page: redesigned with violet top-strips, hover effects, CTA per card, italic disclaimer
- Homepage: fixed AI readiness quiz (dark→light theme), fixed calculator mobile clipping, scaled up header logo text
- Demo page: updated to standard Syntharra branding with hamburger menu
- All new pages: standard header, footer, hamburger menu
- og-image.png created for social sharing
- Country count updated from 30+ to 10+
- Pricing removed from all public navigation and FAQ

### Navigation
- Canonical menu standardised across ALL 36+ pages
- Menu sections: Product, Learn, Industries, Company
- Homepage desktop nav + mobile menu updated
- All footers updated
- CRITICAL RULE documented: menu must be identical on every page

### SEO & Lead Generation
- FAQPage schema on faq.html (34 Q&A pairs)
- Article schema on 11 blog posts
- Service schema on 3 industry pages
- Content upgrades (email-gated) on 5 key blog articles
- Context-aware exit-intent popups on 5 pages
- Blog subscribe wired to Supabase + n8n webhook

### Newsletter Automation (n8n)
- Weekly Newsletter workflow: VyNQeu7dVP3jynBJ (needs Publish + Active in n8n dashboard)
- Unsubscribe webhook: ejZV2qATduPdK4Eu (active)
- Content pool: 14 articles, 15 tips, 5 CTAs (auto-rotates weekly)
- Template: Option B Quick Digest, light theme, HTML bars logo
- Sends via SMTP2GO API (same pattern as Stripe welcome emails)
- From: noreply@syntharra.com
- Unsubscribe link functional

### Files Added
- favicon-white.svg (white logo for dark backgrounds)
- og-image.png / og-image.svg (social share preview)
- email-logo.png (email header logo — PNG fallback)
- CLAUDE.md (comprehensive agent handbook at repo root)

## Key Decisions
- Pricing is NOT public — removed from all nav, FAQ, and footers
- Country count: 10+ (not 30+)
- Blog author: always Syntharra logo, never emoji
- Newsletter: Option B Quick Digest style
- Email logo: HTML table bars work on Outlook/desktop, slightly degraded on Gmail mobile — accepted
- FAQ language support: English, Spanish, French, German, Portuguese, Japanese, Hindi, Italian

## Action Items for Dan
1. n8n: Publish + Activate "Weekly Newsletter - Syntharra" workflow
2. n8n: Verify "Newsletter Unsubscribe Webhook" is active
3. Stripe: Switch TEST → LIVE before launch
4. n8n: Change daniel@ → support@ in notification workflows before launch
