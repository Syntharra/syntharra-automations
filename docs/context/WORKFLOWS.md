# Syntharra — n8n Workflows
> Load when: working on n8n, editing workflows, debugging pipelines
> **Source of truth: queried directly from n8n on 2026-04-02. 32 active workflows.**

## n8n Instance
- URL: `https://n8n.syntharra.com`
- API key: ends in `NqU` (Railway env) — old Cloud key ends in `xdI` (invalid)

---

## Standard Pipeline (7)
| Workflow | ID | Trigger |
|---|---|---|
| Stripe Webhook | `xKD3ny6kfHL0HHXq` | checkout.session.completed |
| Standard Onboarding (Jotform) | `4Hx7aRdzMl5N0uJP` | Jotform Standard form webhook |
| Standard Call Processor | `Kg576YtPM9yEacKn` | Retell post-call webhook |
| Monthly Minutes Calculator | `z1DNTjvTDAkExsX8` | Monthly schedule |
| Usage Alert Monitor | `Wa3pHRMwSjbZHqMC` | Daily schedule |
| Weekly Lead Report | `iLPb6ByiytisqUJC` | Sunday 6pm per-client TZ |
| Send Welcome Email (Manual) | `lXqt5anbJgsAMP7O` | Manual trigger |

## Premium Pipeline (11)
| Workflow | ID | Trigger |
|---|---|---|
| Premium Onboarding | `kz1VmwNccunRMEaF` | Jotform Premium form webhook |
| Premium Call Processor | `STQ4Gt3rH8ptlvMi` | Retell post-call webhook |
| Premium Integration Dispatcher | `73Y0MHVBu05bIm5p` | Post call-processor |
| Premium Dispatcher — Google Calendar | `rGrnCr5mPFP2TIc7` | Called by dispatcher |
| Premium Dispatcher — Outlook | `La99yvfmWg6AuvM2` | Called by dispatcher |
| Premium Dispatcher — Calendly | `b9xRG7wtqCZ5fdxo` | Called by dispatcher |
| Premium Dispatcher — Jobber | `BxnR17qUfAb5BZCz` | Called by dispatcher |
| Premium Dispatcher — HubSpot | `msEy13eRz66LPxW6` | Called by dispatcher |
| Premium — Integration Connected Handler | `a0IAwwUJP4YgwgjG` | OAuth callback |
| Premium — Send You're Live Email | `ptDdy38HKt9DUOAV` | Called by activation |
| Premium — Daily Token Refresh | `5vphecmEhxnwFz2X` | Daily 02:00 UTC |

## Shared Infrastructure (9)
| Workflow | ID | Trigger |
|---|---|---|
| Nightly GitHub Backup | `44WfbVmJ7Zihcwgs` | Nightly |
| Auto-Enable MCP on All Workflows | `AU8DD5r6i6SlYFnb` | Every 6h |
| Email Digest — Daily 6am GMT | `4aulrlX1v8AtWwvC` | Daily 6am GMT |
| Publish Retell Agent | `13cOIXxvj83NfDqQ` | Manual |
| E2E Test Cleanup — 5 Min Delayed Delete | `URbQPNQP26OIdYMo` | Webhook (5min delay) |
| Jotform Webhook Backup Polling | `LF8ZSYyQbmjV4rN0` | Every 15min |
| Daily Transcript Analysis + Jailbreak Monitor | `ofoXmXwjW9WwGvL6` | Daily schedule |
| Nightly PII Retention Cleanup | `ngK02cSgGmvawCot` | Nightly |
| Weekly Client Health Score Calculator | `ALFSzzp3htAEjwkJ` | Weekly |

## Marketing — Built, Pre-Launch (5)
> Active but not receiving real traffic yet. Ready to go at launch.

| Workflow | ID | Trigger |
|---|---|---|
| Website Lead → AI Readiness Score Email | `QY1ZFtPJFsU5h6wQ` | Website lead webhook |
| Website Lead → Free Report Email | `hFU0ZeHae7EttCDK` | Website lead webhook |
| Weekly Newsletter | `6LXpGffcWSvL6RxW` | Weekly schedule |
| Newsletter Unsubscribe Webhook | `Eo8wwvZgeDm5gA9d` | Webhook |
| Blog Auto-Publisher | `j8hExewOREmRp3Oq` | Schedule / manual |

---

## Recently Archived (do not reference)
| Workflow | ID | Reason |
|---|---|---|
| SYNTHARRA_TEST_RUNNER | `HeG3aJQBXyRPKSXA` | Scenario testing removed — Supabase tables deleted |
| [TEST STUB] Retell Tool Dispatcher | `UKEoUeNqYvDDJv79` | Development stub — never wired to live agent |

## Webhook Paths (n8n.syntharra.com)
| Purpose | Path |
|---|---|
| Standard call processor | `/webhook/hvac-std-call-processor` |
| Premium call processor | `/webhook/hvac-prem-call-processor` |
| Stripe | `/webhook/syntharra-stripe-webhook` |
| Jotform Standard onboarding | `/webhook/jotform-hvac-onboarding` |

## Rules
- n8n PUT endpoint: only send `name`, `nodes`, `connections`, `settings.executionOrder` — extra fields error
- Always click Publish after any edits to make active version live
- NEVER POST to webhooks for health checks — HEAD only (POST triggers real execution)
- This file must be updated from live n8n query, not from memory or project-state.md
