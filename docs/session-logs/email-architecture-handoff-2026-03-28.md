# Syntharra Session Handoff — 2026-03-28 (Session 2: Email Architecture)

## What was done this session

### Email Architecture Rollout — COMPLETED ✅

Deployed 5 role-based email addresses across the entire Syntharra stack, removing `daniel@syntharra.com` from all customer-facing and workflow code.

#### New email addresses:
| Address | Purpose |
|---|---|
| `support@syntharra.com` | Customer-facing support (was already on website, now also in all n8n customer emails) |
| `feedback@syntharra.com` | Customer feedback (new — added to website footer on ALL 41 pages) |
| `careers@syntharra.com` | Job applications (was already on careers page) |
| `admin@syntharra.com` | Internal admin, contract notices, operational notifications |
| `onboarding@syntharra.com` | Internal onboarding notifications (Stripe, Standard, Premium) |

#### Website changes (41 pages updated):
- Added `feedback@syntharra.com` link to footer on all 21 main pages + 20 blog articles
- Legal pages (privacy, security, terms, service-agreement) got Contact + Feedback links added to their simpler footers
- `service-agreement.html`: replaced 2× `daniel@syntharra.com` with `admin@syntharra.com` (contract cancellation notice + error contact)
- `demo.html` left as-is (minimal footer, just links back to main site)

#### n8n workflow changes (8 workflows updated + published):
| Workflow | Change |
|---|---|
| HVAC Premium Onboarding (`KXDSMVKSf59tAtal`) | Internal notification: `daniel@` → `onboarding@` |
| HVAC Standard Onboarding (`k0KeQxWb3j3BbQEk`) | Email Summary to Dan + Error Notification: `daniel@` → `onboarding@` |
| Stripe Workflow (`ydzfhitWiF5wNzEy`) | Internal notification: `daniel@` → `onboarding@` |
| HVAC Standard Call Processor (`OyDCyiOjG0twguXq`) | Internal notification: `daniel@` → `admin@` |
| HVAC Premium Call Processor (`UhxfrDaEeYUk4jAD`) | Internal notification: `daniel@` → `admin@` |
| Scenario Test Runner (`94QmMVGdEDl2S9MF`) | Email Report: `daniel@` → `admin@` |
| Usage Alert Monitor (`lQsYJWQeP5YPikam`) | Customer email body (×4): `daniel@` → `support@` | Internal sendTo: `daniel@` → `admin@` |
| Monthly Minutes Calculator (`9SuchBjqhFmLbH8o`) | Customer email body "Questions? contact": `daniel@` → `support@` |

All 8 workflows re-published after changes.

#### Documentation updated:
- `syntharra-automations/docs/project-state.md` — new Email Architecture section with full mapping table + rules
- `syntharra-website/CLAUDE.md` — email address reference table added, migration task marked done

#### What was NOT changed (by design):
- `noreply@syntharra.com` sender address — stays as-is
- n8n credential metadata showing `Daniel Blackmore <daniel@syntharra.com>` — this is account-level, not visible to customers
- Weekly Lead Report, Free Report Email, AI Readiness Score Email, Send Welcome Email (Manual), Premium Integration Dispatcher — these only had `daniel@` in credential metadata, not in node logic
- `daniel@syntharra.com` still exists and is Dan's personal email — just no longer exposed anywhere

## Key rule for future sessions
`daniel@syntharra.com` must NEVER be added back to any workflow node, email template, or website content. See `docs/project-state.md` → Email Architecture section for the canonical mapping.
