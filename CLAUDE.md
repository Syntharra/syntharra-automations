# CLAUDE.md — Syntharra Automations Agent Handbook

> **This is the master context file for any AI agent (Claude Code or otherwise) working on Syntharra's automation stack.**
> Read this file AND `docs/project-state.md` before doing anything.

---

## What is Syntharra?

Syntharra is a global AI Solutions company that builds AI phone receptionists for trade businesses (HVAC, plumbing, electrical, cleaning, pest control). The core product is a fully automated AI receptionist built on Retell AI. Current focus: HVAC contractors in the USA.

**Owner:** Dan Blackmore (Founder & CEO)
**Status:** Pre-launch (test mode). Primary gate: Stripe live mode cutover.

---

## First Actions Every Session

1. Read `docs/project-state.md` — this is the live source of truth for all system state
2. Get credentials from Supabase vault (never hardcode keys — always read from vault)
3. At the END of every session that changes anything: update `docs/project-state.md` and push a session log to `docs/session-logs/YYYY-MM-DD-description.md`

---

## Credentials — Always Read From Vault

**Supabase:**
- URL: `https://hgheyqwnrcvwtgngqdnq.supabase.co`
- Service role key: stored in vault as `service_name=Supabase, key_type=service_role_key`
- REST pattern: `GET /rest/v1/syntharra_vault?service_name=eq.{NAME}&key_type=eq.{TYPE}&select=key_value`
- Headers always needed: `apikey: {KEY}` AND `Authorization: Bearer {KEY}`

**GitHub:**
- Token: `{{GITHUB_TOKEN}} — available in vault as service_name=GitHub, key_type=personal_access_token`
- Repos: `Syntharra/syntharra-website`, `Syntharra/syntharra-automations`, `Syntharra/syntharra-admin`, `Syntharra/syntharra-checkout`, `Syntharra/syntharra-ops-monitor`
- Push pattern: GET file SHA first, then PUT with base64 content + SHA
- NEVER commit raw token strings — GitHub secret scanning will block the push

**n8n:**
- Instance: `https://n8n.syntharra.com`
- API key: vault `service_name=n8n Railway, key_type=api_key`
- REST API: `GET/POST/PATCH https://n8n.syntharra.com/api/v1/workflows/{id}`
- Activate: `POST /api/v1/workflows/{id}/activate`
- Header: `X-N8N-API-KEY: {key}`
- n8n PUT workflow: only send `name`, `nodes`, `connections`, `settings` — extra fields cause errors

**Retell AI:**
- API key: vault `service_name=Retell AI, key_type=api_key`
- Base URL: `https://api.retellai.com`
- Arctic Breeze agent ID: vault `service_name=Retell AI, key_type=agent_id_arctic_breeze`
- CRITICAL: NEVER delete or recreate a Retell agent — agent_id is the foreign key tying everything together
- ALWAYS call `POST /publish-agent/{agent_id}` immediately after any agent update

**Groq:**
- API key: read from Supabase vault (`service_name=Groq, key_type=api_key`) — never hardcode
- URL: `https://api.groq.com/openai/v1/chat/completions`
- Model: `llama-3.3-70b-versatile`

**SMTP2GO:**
- API key: vault `service_name=SMTP2GO, key_type=api_key`
- Used for ALL email sending in n8n workflows

**Stripe:**
- Currently TEST MODE — do not switch to live without Dan's explicit instruction
- All price/product IDs in vault under `service_name=Stripe`

**Jotform:**
- API key: vault `service_name=Jotform, key_type=api_key`
- Standard form ID: vault `service_name=Jotform, key_type=form_id_standard`
- Premium form ID: vault `service_name=Jotform, key_type=form_id_premium`
- Use REST API directly — Jotform MCP OAuth connector is broken

---

## Supabase Tables

| Table | Purpose |
|---|---|
| `hvac_standard_agent` | Standard client records |
| `hvac_premium_agent` | Premium client records |
| `hvac_call_log` | All call records |
| `stripe_payment_data` | Stripe payment events |
| `client_subscriptions` | Active subscriptions |
| `billing_cycles` | Monthly billing cycles |
| `overage_charges` | Usage overage charges |
| `syntharra_vault` | All credentials (source of truth) |
| `agent_test_results` | Agent test run results |
| `agent_pending_fixes` | Approved fix queue for agents |

---

## n8n Workflows (Active)

| Workflow | ID | Purpose |
|---|---|---|
| HVAC Standard Onboarding | `4Hx7aRdzMl5N0uJP` | Triggered by Jotform, creates Retell agent |
| HVAC Premium Onboarding | `kz1VmwNccunRMEaF` | Premium onboarding flow |
| Premium Integration Dispatcher | `73Y0MHVBu05bIm5p` | Routes Premium calls |
| Email Digest Daily | `4aulrlX1v8AtWwvC` | Daily ops digest |
| SYNTHARRA_AGENT_TEST_RUNNER | `3MMp9J8QN0YKgA6Q` | Runs agent test scenarios via Groq |
| SYNTHARRA_FIX_APPROVER | `ZAAtRETIIVZSMMDk` | Applies approved prompt fixes to Retell |

---

## Retell Agents

| Agent | ID | Purpose |
|---|---|---|
| Arctic Breeze HVAC | `agent_4afbfdb3fcb1ba9569353af28d` | Live Standard demo agent |
| Demo Jake | `agent_b9d169e5290c609a8734e0bb45` | Demo agent |
| Demo Sophie | `agent_2723c07c83f65c71afd06e1d50` | Demo agent |

- Arctic Breeze phone: `+18129944371`
- Transfer number: `+18563630633`
- Live conversation flow: `conversation_flow_34d169608460`

---

## Key Technical Rules

### n8n
- **NEVER use `fetch()` inside n8n Code nodes** — not available in the sandbox. Use HTTP Request nodes instead.
- After any workflow edit, always activate/publish it
- n8n PUT endpoint only accepts: `name`, `nodes`, `connections`, `settings.executionOrder`
- To activate a workflow: `POST /api/v1/workflows/{id}/activate`

### Retell
- Never delete or recreate an agent — patch in place always
- Always publish after any update: `POST /publish-agent/{agent_id}`
- Agent prompts: always use commas instead of dashes for better AI readability

### GitHub
- Never commit raw API keys or tokens — use placeholder variables
- Always fetch current SHA before updating existing files
- Omit SHA for new files
- Use `raw.githubusercontent.com` URLs for reliable file content retrieval

### Email
- ALL emails must be LIGHT THEME — white card backgrounds, dark text, purple accents
- Never use `daniel@syntharra.com` in any workflow or website content
- Support contact always `support@syntharra.com`
- Email provider: SMTP2GO (not nodemailer — Railway blocks SMTP ports)

### Admin Dashboard (`syntharra-admin` repo)
- Single `<style>` block — never add a second
- Use `overflow-x:clip` not `overflow:hidden` on body
- Edit with str.replace — never rewrite the whole file
- Railway auto-deploys from main branch in ~60 seconds

---

## Agent Testing System

Located in:
- Scenarios: `tests/agent-test-scenarios.json` (95 scenarios)
- Test runner workflow: n8n ID `3MMp9J8QN0YKgA6Q`
- Fix approver workflow: n8n ID `ZAAtRETIIVZSMMDk`
- Results in Supabase: `agent_test_results`, `agent_pending_fixes`
- Dashboard: `admin.syntharra.com` → Agent Testing tab

The test loop:
1. POST to `https://n8n.syntharra.com/webhook/agent-test-runner` with `{agent_type, groups, run_label}`
2. Groq simulates 4-turn conversations for each scenario
3. Groq evaluates each conversation → pass/fail + severity
4. Results saved to Supabase
5. Failed scenarios generate fix proposals saved as `pending` in `agent_pending_fixes`
6. Dan approves fixes in admin dashboard → POST to `/webhook/apply-agent-fix`
7. Fix applied to Retell agent prompt, agent published

---

## Brand

| Item | Value |
|---|---|
| Primary colour | `#6C63FF` (violet) |
| Accent | `#00D4FF` (cyan) |
| Logo | 4 ascending bars, flat `#6C63FF` |
| Font | Inter |
| Support email | `support@syntharra.com` |

---

## Pricing (NOT public)

| Plan | Monthly | Annual | Setup | Minutes |
|---|---|---|---|---|
| Standard | $497/mo | $414/mo | $1,499 | 475/mo |
| Premium | $997/mo | $831/mo | $2,499 | 1,000/mo |

---

## Claude Code Setup (One-Time)

When setting up Claude Code for Syntharra, create `~/.claude.json` with these MCP servers.
Get all key values from the Supabase vault first.

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest",
               "--supabase-url", "https://hgheyqwnrcvwtgngqdnq.supabase.co",
               "--supabase-key", "{{SUPABASE_SERVICE_ROLE_KEY}}"]
    },
    "n8n": {
      "command": "npx",
      "args": ["-y", "n8n-mcp-server"],
      "env": {
        "N8N_HOST": "https://n8n.syntharra.com",
        "N8N_API_KEY": "{{N8N_API_KEY}}"
      }
    },
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"],
      "env": {
        "RAILWAY_API_TOKEN": "{{RAILWAY_API_TOKEN}}"
      }
    },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp-server"],
      "env": {
        "STRIPE_SECRET_KEY": "{{STRIPE_SECRET_KEY}}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "{{GITHUB_TOKEN}}"
      }
    }
  }
}
```

Vault lookups for each key:
- `SUPABASE_SERVICE_ROLE_KEY` → `service_name=Supabase, key_type=service_role_key`
- `N8N_API_KEY` → `service_name=n8n Railway, key_type=api_key`
- `RAILWAY_API_TOKEN` → `service_name=Railway, key_type=api_token`
- `STRIPE_SECRET_KEY` → `service_name=Stripe, key_type=secret_key`
- `GITHUB_TOKEN` → `service_name=GitHub, key_type=personal_access_token`

Note: Jotform has no working MCP — use REST API directly with key from vault.
Note: Groq has no MCP — use HTTP calls directly with key from vault.

---

## Session End Checklist

Before ending any session that changed something:
1. Update `docs/project-state.md` with what changed
2. Push session log to `docs/session-logs/YYYY-MM-DD-brief-description.md`
3. Verify any n8n workflows are activated
4. Verify any Retell agents are published
5. Confirm all GitHub pushes succeeded
