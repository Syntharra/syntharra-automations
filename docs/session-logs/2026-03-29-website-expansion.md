# Session Log — March 29, 2026

## Summary
Major website expansion session. Built out the full Syntharra web presence from 14 pages to 30+ pages, added SEO infrastructure, lead generation system, and weekly newsletter automation.

## What was built

### New pages created
- `/how-it-works.html` — 5-step onboarding walkthrough with feature grid
- `/about.html` — Company story, mission, values, stats
- `/calculator.html` — Standalone missed revenue calculator (lead magnet, email-gated)
- `/plan-quiz.html` — "Which plan is right for me?" quiz (lead magnet, email-gated, recommends Standard/Premium)
- `/ai-readiness.html` — Standalone AI readiness quiz (lead magnet, email-gated)
- `/faq.html` — Comprehensive FAQ with 30+ questions in 6 categories, search, accordion
- `/hvac.html` — HVAC industry landing page
- `/plumbing.html` — Plumbing industry landing page
- `/electrical.html` — Electrical industry landing page
- `/lp/hvac-answering-service.html` — Google Ads landing page (noindex, no nav)
- `/lp/plumbing-answering-service.html` — Google Ads landing page (noindex, no nav)
- `/lp/electrical-answering-service.html` — Google Ads landing page (noindex, no nav)
- `/og-image.png` + `/og-image.svg` — Social share preview image
- `/favicon-white.svg` — White logo variant for dark backgrounds
- `/email-logo.png` — Email header logo (hosted PNG)

### Blog articles (12 new, 20 total)
Backdated Feb 2024 — Jan 2025, SEO-optimized across HVAC, plumbing, electrical, AI, growth, marketing, business, seasonal keywords.

### Case studies page redesigned
- Violet gradient top-strip on all cards
- CTA button on every card (varied copy)
- Italic fine-print disclaimer
- Hover effects, curly quotes, cleaner layout

### SEO infrastructure
- FAQPage schema on faq.html (34 Q&A pairs)
- Article schema on 11 blog posts
- Service schema on 3 industry pages
- All for Google rich results

### Lead generation system
- Blog content upgrades on 5 key articles (email-gated checklists/templates)
- Context-aware exit-intent popups on 5 pages (industry-specific hooks)
- All lead captures → Supabase website_leads + n8n webhook notification

### Newsletter automation
- n8n workflow: `VyNQeu7dVP3jynBJ` (Weekly Newsletter - Syntharra)
- n8n workflow: `ejZV2qATduPdK4Eu` (Newsletter Unsubscribe Webhook) — ACTIVE
- Option B "Quick Digest" format: 2 article cards, 3 quick wins, rotating CTA
- Content pool: 14 articles, 15 tips, 5 CTAs — auto-rotates weekly
- Sends via SMTP2GO API (same pattern as Stripe welcome emails)
- Unsubscribe webhook returns branded confirmation page
- Newsletter workflow needs: Publish + Active toggle in n8n dashboard
- Email template in: syntharra-automations/shared/email-templates/

### Site-wide fixes
- Canonical hamburger menu standardized across ALL 36+ pages
- Menu sections: Product, Learn, Industries, Company, Book a Call
- "vs Answering Services" renamed to "Why AI Wins" everywhere
- FAQ moved from homepage to standalone page
- Pricing removed from all public navigation and FAQ
- Country count updated from 30+ to 10+
- Blog author icon: Syntharra logo (favicon-white.svg), never emoji
- Homepage logo text scaled up to match bar height
- Demo page updated with standard branding + hamburger menu
- Homepage footer updated with standard logo + wordmark
- Calculator mobile fix (stacked email/button, font size)
- AI readiness quiz fixed from dark to light theme
- All email inputs fixed for visibility (white bg, dark text)

### Documentation updated
- CLAUDE.md at repo root — full agent handbook with canonical menu spec, brand guide, design patterns, SEO section, lead gen funnel, file map
- _template/BLOG_STANDARD.md — logo rule added
- _template/TEMPLATE.md — cross-references CLAUDE.md

## Key rules established
1. Hamburger menu IDENTICAL on every page — always copy, never build from scratch
2. When adding menu items, update ALL pages via script
3. Pricing is NOT public — never show dollar amounts
4. Blog author icon: always favicon-white.svg, never emoji
5. One <style> block per page — verify before push
6. Email templates: LIGHT THEME only (white cards, grey bg, dark text, purple accents)

## n8n workflows
- Weekly Newsletter (`VyNQeu7dVP3jynBJ`) — NEEDS PUBLISH + ACTIVE
- Newsletter Unsubscribe (`ejZV2qATduPdK4Eu`) — ACTIVE
- All other existing workflows unchanged

## Outstanding for next session
- Publish + activate newsletter workflow in n8n dashboard
- Switch Stripe TEST → LIVE before launch
- Change daniel@ → support@syntharra.com in n8n notification workflows
- Consider adding live chat widget (AI-powered)
- Consider video testimonial / founder video
- More SEO blog articles as needed
