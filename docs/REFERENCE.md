# Syntharra — Reference Data
> Static reference: agent IDs, flow IDs, simulator commands, workflow counts.
> This file does not track tasks — see TASKS.md for open work.
> Updated when IDs change or new agents are added.

---

## 🏛️ Standard Onboarding & Agent Creation (CANONICAL as of 2026-04-06)

This is the ONLY supported path for creating a new client agent. Any deviation must be documented and approved.

1. **Source of truth** = `retell-iac/` on `main`. Agent flows are built from YAML manifests + JSON templates, never hand-edited in the Retell UI.
2. **Standard client** → cloned from `agent_4afbfdb3fcb1ba9569353af28d` (Standard MASTER, flow `conversation_flow_34d169608460`).
3. **Premium client** → cloned from `agent_2cffe3d86d7e1990d08bea068f` (Premium MASTER = Premium TESTING, interim. Flow `conversation_flow_2ded0ed4f808`).
4. **Clone trigger** = Jotform submission → n8n onboarding workflow:
   - Standard: `HVAC AI Receptionist - JotForm Onboarding (Supabase)` (`4Hx7aRdzMl5N0uJP`)
   - Premium: `HVAC Prem Onboarding` (`kz1VmwNccunRMEaF`)
5. **Onboarding pipeline steps** (both tiers):
   Jotform webhook → Parse fields → Build Retell prompt → Create Retell LLM → Clone Retell agent (from master above) → Merge LLM + agent data → Write to `hvac_standard_agent` Supabase → Stripe payment reconcile → Purchase phone number (see §Phone Purchase) → Publish Retell agent → HubSpot deal update → Slack notify → `You're Live` email.
6. **Phone Purchase**: Twilio-only right now. Swap to Telnyx when credential is vaulted (see §Telnyx Migration). No other provider.
7. **Spanish handling**: excluded from flows — Retell native multilingual handles Spanish callers inline. `spanish_routing_node` intentionally stripped at build time via `retell-iac/manifests/*.yaml` `excluded` list.
8. **MASTER safety**: never patch MASTER agents directly in Retell. Always (a) edit the manifest/template in `retell-iac/`, (b) run `scripts/build_agent.py` + `scripts/diff.py` round-trip, (c) `scripts/promote.py` gated on round-trip clean.
9. **Backups**: every MASTER change must tag a baseline in `retell-iac/snapshots/YYYY-MM-DD_<label>/` before promotion.
10. **No bypasses**: direct Retell API PATCHes to MASTER agents, direct n8n node edits that skip git, or manual Supabase writes to `hvac_standard_agent` are all prohibited outside of emergency rollback.

See `docs/ONBOARDING_STANDARD.md` for full expanded spec.

---

## ⚠️ Known Script Gotchas

| Script | Gotcha | Safe Alternative |
|---|---|---|
| `run_tests.py --agent premium` | **BROKEN** — silently ignores `--agent` flag. Always runs STANDARD TESTING SUITE first regardless. Wastes ~200K TPD tokens before Premium starts. Discovered 2026-04-06. | Use `run_premium_only.py` instead |
| `promote.py --agent premium` | Not needed yet — Premium TESTING is acting as interim Premium MASTER (2026-04-06). Promotion to a distinct MASTER deferred until post-launch. | Point clones at `agent_2cffe3d86d7e1990d08bea068f` |

---

## Agent Registry
| Agent | ID | Status |
|---|---|---|
| HVAC Standard (MASTER) | `agent_4afbfdb3fcb1ba9569353af28d` | ✅ MASTER — LIVE (promoted 2026-04-06, flow v22, 90/91 98%). Clone source for Standard clients. |
| HVAC Premium (MASTER = TESTING, interim) | `agent_2cffe3d86d7e1990d08bea068f` | ✅ Acting as Premium MASTER until post-launch split. Clone source for Premium clients. |
| Demo Female / Sophie | `agent_2723c07c83f65c71afd06e1d50` | ✅ Live |
| Demo Male / Jake | `agent_b9d169e5290c609a8734e0bb45` | ✅ Live |

> Note: Premium MASTER and TESTING are the same agent (`agent_2cffe3d86d7e1990d08bea068f`) until Dan greenlights a split post-launch.

## Conversation Flow Registry
| Flow | ID | Bound to |
|---|---|---|
| HVAC Standard (MASTER) | `conversation_flow_34d169608460` | Standard MASTER agent |
| HVAC Standard (TESTING) | `conversation_flow_5b98b76c8ff4` | Unbound — Standard TESTING agent deleted post-promotion |
| HVAC Premium (MASTER/TESTING) | `conversation_flow_2ded0ed4f808` | Premium MASTER (interim — same agent as TESTING) |

## Phone Numbers
- **+18129944371** — only active line. Used for live sales calls + demos while burning down ~$20 Twilio credit. Will be replaced by Telnyx numbers once Telnyx is live.
- (Old demo line `+12292672271` deleted in Twilio 2026-04-06 — do not reference.)

## Telnyx Migration (post-Twilio)
- Telnyx becomes the **permanent** phone provider the moment a Telnyx API key is added to Supabase vault (`service_name='Telnyx', key_type='api_key'`). Twilio usage stops at that point.
- Onboarding "Purchase Number" HTTP node swap:
  - Search: `GET https://api.telnyx.com/v2/available_phone_numbers?filter[country_code]=US&filter[locality]={client_city}&filter[features][]=voice&filter[features][]=sms`
  - Order: `POST https://api.telnyx.com/v2/number_orders` with `phone_numbers: [{phone_number: <selected>}]`
  - Bind to Retell SIP: `PATCH /v2/phone_numbers/{id}` setting `voice.connection_id` to the Retell SIP connection id.
  - Auth header: `Authorization: Bearer <vault key>` on all three calls.
- Once this swap is live, agent creation is fully automatic end-to-end — Jotform in, live phone number out, zero manual steps.
- Tracked in TASKS.md until built.

## Simulator — Premium
```
git pull && python3 tools/openai-agent-simulator-premium.py --key <groq_key> --group core_flow
```

## n8n Workflows
- Total: 47 | Active: 32 | Labelled: 37/47

## core_flow — Fix Status (Premium TESTING)
| # | Scenario | Status |
|---|---|---|
| #5 | FAQ - hours inquiry | ✅ FIXED |
| #7 | Booking push | Fix applied, retest pending |
| #11 | Service type order | Fix applied, retest pending |
| #13 | Callback repetition | Fix applied, retest pending |
| #14 | Pricing redirect | Fix applied, retest pending |
| #15 | Over-eager close | Fix applied, retest pending |

## Component Library (Subagent)
| Component | ID |
|---|---|
| call_style_detector | `conversation_flow_component_ff58734c21bb` |
| verify_emergency | `conversation_flow_component_174275fc7751` |
| booking_capture | `conversation_flow_component_ca04bba21560` |
| transfer_failed | `conversation_flow_component_335da5e7364e` |
| ending | `conversation_flow_component_827d612a2cb9` |
| existing_customer | `conversation_flow_component_d8eff9881e16` |
| spam_robocall | `conversation_flow_component_2cc95ba461b7` |
| identify_call | `conversation_flow_component_ebac0db129f3` |
| general_questions | `conversation_flow_component_d46848148d1d` |
| fallback_leadcapture | `conversation_flow_component_33ab8b82f1fc` |
| callback | `conversation_flow_component_ab7909b654e2` |
| validate_phone | `conversation_flow_component_3b788e86e755` |
| emergency_fallback | `conversation_flow_component_9d3c5c904347` |
| spanish_routing | `conversation_flow_component_731ee109f18a` |
| emergency_detection | `conversation_flow_component_24d9b49e1a30` |
| check_availability | `conversation_flow_component_dfe7bd5017e5` |
| confirm_booking | `conversation_flow_component_20ac85a7954c` |
| reschedule | `conversation_flow_component_4b3d107fd73a` |
| cancel_appointment | `conversation_flow_component_eb20b4cd1d8d` |

## Testing Tools

| Tool | Path | Purpose |
|---|---|---|
| Agentic Test Engine | `tools/agentic-test-fix.py` | Full scenario suite + triage + self-fix. Respects --agent flag correctly. |
| **Premium-Only Runner** | `C:\Users\danie\syntharra-tests\run_premium_only.py` | **USE THIS for Premium runs.** |
| Standard E2E | `shared/e2e-test.py` | Full pipeline E2E (93 assertions) |
| Premium E2E | `shared/e2e-test-premium.py` | Full pipeline E2E (106 assertions) |
| Scenarios | `tests/agent-test-scenarios.json` | 108 scenarios, 7 groups |

### Groq Budget — Agentic Test Engine (qwen/qwen3-32b)
- **Daily limit**: 500,000 TPD (resets midnight UTC)
- **Standard full run**: ~200K tokens
- **Premium full run**: ~270K tokens
- **⚠️ NEVER run Standard before Premium if you need Premium to complete**


## Retell Agents — AUTHORITATIVE (verified 2026-04-07 via list-agents)

| client_id | agent_id | flow_id | tier | status | notes |
|---|---|---|---|---|---|
| SYNTHARRA_MASTER_STD  | agent_4afbfdb3fcb1ba9569353af28d | conversation_flow_34d169608460 | std  | active | HVAC Standard MASTER |
| SYNTHARRA_MASTER_PREM | agent_2cffe3d86d7e1990d08bea068f | conversation_flow_2ded0ed4f808 | prem | active | HVAC Premium MASTER (provisional — confirm after scenario testing) |

**Removed (do NOT use — these IDs no longer exist on Retell):**
- agent_9822f440f5c3a13bc4d283ea90 (was claimed Premium MASTER)
- agent_731f6f4d59b749a0aa11c26929 (was claimed Standard TESTING)

Source of truth: Supabase `public.client_agents` table.
