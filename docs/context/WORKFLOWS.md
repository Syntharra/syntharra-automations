# Syntharra — n8n Workflows
> Load when: working on n8n, editing workflows, debugging pipelines

## n8n Instance
- URL: `https://n8n.syntharra.com`
- API key: ends in `NqU` (Railway env) — old Cloud key ends in `xdI` (invalid)
- Auto-Enable MCP workflow: `AU8DD5r6i6SlYFnb` (runs every 6h)

## Active Workflows (15)
| Workflow | ID | Trigger |
|---|---|---|
| Stripe Webhook | `ydzfhitWiF5wNzEy` | checkout.session.completed |
| Standard Onboarding | `k0KeQxWb3j3BbQEk` | Jotform Standard form |
| Standard Call Processor | `Kg576YtPM9yEacKn` | Retell post-call webhook |
| Premium Onboarding | `KXDSMVKSf59tAtal` | Jotform Premium form |
| Premium Call Processor | `STQ4Gt3rH8ptlvMi` | Retell post-call webhook |
| Premium Dispatcher | `kVKyPQO7cXKUJFbW` | Post call-processor |
| Minutes Calculator | `9SuchBjqhFmLbH8o` | Monthly schedule |
| Usage Alert Monitor | `lQsYJWQeP5YPikam` | Daily schedule |
| Weekly Lead Report | `mFuiB4pyXyWSIM5P` | Sunday 6pm per-client TZ |
| Nightly GitHub Backup | `EAHgqAfQoCDumvPU` | Nightly |
| Email Digest | `4aulrlX1v8AtWwvC` | Scheduled (9 inboxes, Groq AI) |
| Publish Retell | `sBFhshlsz31L6FV8` | Manual |
| Auto-Enable MCP | `AU8DD5r6i6SlYFnb` | Every 6h |
| Scenario Runner v4 | `94QmMVGdEDl2S9MF` | Manual |
| Scenario Sub-workflow | `rlf1dHVcTlzUbPX7` | Called by runner |

## Inactive / Confirm Before Delete
- Integration Hub: `8WYFy093XA6UKB7L` — confirm with Dan before deleting
- 17 other inactive/superseded workflows pending Dan's deletion decision

## Webhook URLs (n8n)
| Purpose | Path |
|---|---|
| Standard call processor | `/webhook/hvac-std-call-processor` |
| Premium call processor | `/webhook/hvac-prem-call-processor` |
| Stripe | `/webhook/syntharra-stripe-webhook` |
| Jotform onboarding | `/webhook/jotform-hvac-onboarding` |

## Rules
- n8n PUT workflow: only send `name`, `nodes`, `connections`, `settings.executionOrder` — extra fields cause errors
- After edits: always click Publish to make active version live
- NEVER POST to webhooks for health checks — use HEAD only (POST triggers real execution)
