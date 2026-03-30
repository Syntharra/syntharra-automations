# Session Log — 2026-03-30 (Email Branding + MCP + Supabase Cleanup)

## Summary
Full standardisation of Syntharra logo across all outbound client emails, creation of Auto-Enable MCP workflow, and Supabase test data cleanup.

---

## 1. Logo Standardisation — All Client Emails

### Problem
- Onboarding emails were using `https://i.postimg.cc/zBSrKLDb/company-logo-link.png` (postimage hosted, blurry, off-brand)
- Several emails had no logo at all
- No consistency across email types

### Standard adopted
All emails now use the approved icon+text LOGO block (from `_shared.js`):
- Icon: `https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png` (36×36px)
- Text: "Syntharra" (Inter 16px bold, `#0f0f1a`) + "GLOBAL AI SOLUTIONS" (Inter 7.5px, `#6C63FF`, uppercase)
- Rendered as HTML table — crisp at any DPI, no image blurriness

### Files updated
| File | Change |
|---|---|
| `hvac-premium/email-templates/welcome-email-builder.js` | Replaced flat PNG with standard LOGO block |
| `hvac-premium/email-templates/setup-email-builder.js` | Replaced flat PNG with standard LOGO block |
| `oauth-server/server.js` | Replaced flat PNG with standard LOGO block |
| `hvac-standard/n8n-workflows/k0KeQxWb3j3BbQEk_Standard_Onboarding.json` | Added LOGO_ROW (had no logo at all) |
| `hvac-standard/n8n-workflows/OyDCyiOjG0twguXq_Standard_Call_Processor.json` | Added LOGO_ROW to Route Notifications |
| `shared/n8n-workflows/ydzfhitWiF5wNzEy_Stripe_Workflow.json` | Full rebrand — replaced old purple header block |
| `hvac-premium/n8n-workflows/KXDSMVKSf59tAtal_Premium_Onboarding.json` | Updated (premium welcome + setup) |
| `hvac-premium/n8n-workflows/premium-onboarding_KXDSMVKSf59tAtal.json` | Synced from above |
| `hvac-standard/n8n-workflows/standard-onboarding_k0KeQxWb3j3BbQEk.json` | Synced from above |

### Live n8n status (confirmed via MCP)
- ✅ Stripe Workflow (`xKD3ny6kfHL0HHXq`) — Extract Session Data has new LOGO
- ✅ Standard Onboarding (`4Hx7aRdzMl5N0uJP`) — Build Welcome Email HTML has new LOGO
- ✅ Standard Call Processor (`Kg576YtPM9yEacKn`) — Route Notifications has new LOGO
- ✅ Premium Onboarding (`kz1VmwNccunRMEaF`) — Send Welcome Email has new LOGO
- ⚠️  Premium Onboarding `Send Setup Emails` node — patched in GitHub JSON but NOT yet pushed live to n8n (MCP SDK broken for update_workflow). Manual fix needed: open node, add ICON_URL/LOGO constants, inject `${LOGO}` row after `<table width="580"`.

### Also confirmed already correct
- `marketing/emails/templates/stripe-welcome.js` ✅
- `marketing/emails/templates/youre-live.js` ✅
- `marketing/emails/templates/call-alert.js` ✅
- `marketing/emails/templates/usage-alert.js` ✅
- `marketing/emails/ai-readiness-email-node.js` ✅
- `marketing/emails/free-report-email-node.js` ✅

---

## 2. Auto-Enable MCP Workflow

### Problem
Every new Claude session requires manually enabling "Available in MCP" on each n8n workflow. With 19+ workflows this is tedious and easy to forget.

### Solution
Created workflow `Auto-Enable MCP on All Workflows` (ID: `wkr57qBkTDFmqmo8`) on n8n Cloud.

- **Trigger:** Every 6 hours (schedule)
- **Logic:** Fetches all workflows via n8n API → checks `settings.availableInMCP` → PUTs update for any that are off
- **API used:** `https://syntharra.app.n8n.cloud/api/v1/workflows`
- **Status:** Active ✅
- **First run result:** All 21 workflows already had MCP enabled (toggled manually earlier in session)
- Note: n8n MCP SDK `create_workflow` tool was broken (`builder.regenerateNodeIds is not a function`) — workflow created via direct REST API POST instead

---

## 3. Supabase Test Data Cleanup

### Problem
Weekly report, usage alert, and call processor workflows were querying Supabase tables populated with test/scenario data, triggering constant outgoing emails consuming SMTP2GO allowance with no real clients.

### Data deleted
| Table | Rows deleted | Kept |
|---|---|---|
| `hvac_call_log` | 16 (all test scenarios) | nothing |
| `hvac_standard_agent` | 3 (all "HVAC Company" test agents) | Arctic Breeze HVAC (`agent_4afbfdb3fcb1ba9569353af28d`) |
| `stripe_payment_data` | 1 (test mode payment) | nothing |
| `client_subscriptions` | 0 (was empty) | — |
| `billing_cycles` | 0 (was empty) | — |
| `overage_charges` | 0 (was empty) | — |

### Result
Emails from automated workflows should stop immediately. Tables will only populate with real client data going forward.

---

## Commits this session
- `7efcde0` — fix: replace flat email-logo.png with standard icon+text LOGO block
- `4ce3f68` — feat: standardise logo across all client-facing emails

