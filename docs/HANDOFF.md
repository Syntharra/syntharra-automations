# HANDOFF — Premium Agent core_flow Fixes

> **Date:** 2026-04-04
> **Previous session:** Applied all Standard improvements to Premium TESTING flow. Ran core_flow group.
> **This session:** Fix 6 core_flow failures, re-run, then continue remaining groups.

---

## Current state

### Premium TESTING flow (conversation_flow_2ded0ed4f808) — improvements applied ✅
All 9 Standard improvements in place and verified:
- Code node (call_style_detector) — node-call-style-detector, wired from identify_call
- Wrong number + vendor handling
- MINIMAL INFO rule
- WhatsApp + commercial caller handling
- Scripted close in fallback_leadcapture
- Emergency 2-step sequence
- Service area remaining-only rule
- caller_style_note injection in booking_capture + fallback_leadcapture

### core_flow result: 9/15 (60%) ❌

| # | Scenario | Result | Failure reason |
|---|---|---|---|
| 1 | Basic service request | ✅ | — |
| 2 | Emergency - no heat in winter | ✅ | — |
| 3 | Quote request | ✅ | — |
| 4 | Existing customer follow-up | ✅ | — |
| 5 | FAQ - hours inquiry | ❌ | Agent repeated same info multiple times |
| 6 | Request live person immediately | ✅ | — |
| 7 | AC making strange noise | ❌ | Agent pushed to book when caller only wanted callback |
| 8 | Heating system not working | ✅ | — |
| 9 | Spam robocall | ✅ | — |
| 10 | Wrong number | ✅ | — |
| 11 | Maintenance request | ❌ | Confirmed details before capturing service type |
| 12 | No cooling with burning smell | ✅ | — |
| 13 | Callback requested | ❌ | Repeated callback confirmation details multiple times |
| 14 | Ductwork cleaning inquiry | ❌ | Gave pricing info instead of redirecting to team |
| 15 | End of call - caller decides to wait | ❌ | Over-eager close, kept encouraging caller to call back |

---

## What to do this session

### Step 1 — Fix the 6 failures

**Fix 1 — Repetition bug (#5, #13, #15)**
Node: general_questions_node + confirm_booking_node + ending_node
Issue: Agent re-states info already confirmed, or over-closes
Fix: Add to relevant nodes — "State each piece of information ONCE only. Do not repeat what has already been confirmed. Close with a single warm goodbye — do not repeat it."

**Fix 2 — Booking push (#7)**
Node: booking_capture_node
Issue: Premium agent defaults to booking even when caller explicitly says callback only
Fix: Add explicit rule — "If caller says they only want a callback and does NOT want to book right now, respect that immediately. Route to fallback_leadcapture. Do NOT push booking after caller declines."

**Fix 3 — Service type order (#11)**
Node: booking_capture_node
Issue: Agent confirms details before knowing what service is needed
Fix: Enforce order — Step 1 is always service type. Cannot move to name/address until service is confirmed.

**Fix 4 — Pricing redirect (#14)**
Node: general_questions_node
Issue: Agent gives pricing details when asked
Fix: Pricing section already in global prompt — likely a node-level gap. Add to general_questions_node: "NEVER quote prices, estimates, or cost ranges. For any pricing question: 'Our team will go over all pricing at the appointment.'"

**Fix 5 — Over-eager close (#15)**
Node: ending_node
Issue: Agent over-encourages caller to call back, repeats farewell
Fix: Add to ending_node — "Say goodbye ONCE. Do not repeat farewells or encourage the caller to call back multiple times. One warm close, then end."

### Step 2 — Re-run core_flow (5 at a time, 3 batches)
Target: 14/15+ before moving on

### Step 3 — Continue remaining groups
Run in this order, 5 at a time:
1. info_collection (15 scenarios)
2. personalities (15 scenarios)
3. pricing_traps (8 scenarios)
4. edge_cases (15 scenarios)
5. boundary_safety (12 scenarios)
6. premium_specific (15 scenarios)

---

## Key IDs
| Resource | ID |
|---|---|
| TESTING Agent | `agent_2cffe3d86d7e1990d08bea068f` |
| TESTING Flow | `conversation_flow_2ded0ed4f808` |
| MASTER Agent | `agent_9822f440f5c3a13bc4d283ea90` |
| MASTER Flow | `conversation_flow_1dd3458b13a7` |
| Simulator | `tools/openai-agent-simulator-premium.py` |

## Simulator pattern (NEVER run more than 5 at once)
```python
fetch_scenarios("core_flow", start=0, count=5)   # batch 1
fetch_scenarios("core_flow", start=5, count=5)   # batch 2
fetch_scenarios("core_flow", start=10, count=5)  # batch 3
```
Pause after each batch. Report. Ask Dan to continue before next batch.
