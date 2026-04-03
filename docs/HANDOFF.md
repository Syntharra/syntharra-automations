# HANDOFF — Premium Agent Behaviour Testing (Start Here)

> **Date:** 2026-04-04
> **Previous session:** Standard HVAC fully tested and complete (80/80 agent + 75/75 E2E + 20/20 call processor)
> **This session:** Test HVAC Premium agent behaviour — same approach as Standard

---

## Context

Standard is done. Premium shares the same base architecture but adds:
- **Live calendar booking** — agent books appointments in real-time during the call
- **Calendar integrations** — Google Calendar, Outlook, Calendly, Jobber, HubSpot
- **Higher price point** — $997/mo or $831/mo annual + $2,499 setup
- **More complex flows** — booking confirmation, slot selection, rescheduling paths

The Premium agent has been built and the E2E pipeline passes (89/89). What has NOT been done
is systematic agent behaviour testing — Sophie's conversation quality under the full Premium
scenario suite has never been run.

---

## What to do this session

### Step 1 — Load context
```python
claude_md   = fetch("CLAUDE.md")
tasks_md    = fetch("docs/TASKS.md")
failures_md = fetch("docs/FAILURES.md")
# Then load:
premium_skill    = load_skill("hvac-premium")
e2e_premium      = load_skill("e2e-hvac-premium")
retell_skill     = load_skill("syntharra-retell")
```

### Step 2 — Understand the Premium agent
- Load `docs/context/AGENTS.md` for current agent/flow IDs
- Review the Premium MASTER prompt vs Standard — identify what's different
- Check if Standard MASTER improvements (lean 4,053-char prompt, code node for caller style,
  all 12 node fixes) have been applied to Premium TESTING agent

### Step 3 — Sync Premium TESTING with Standard improvements
Standard MASTER was fully overhauled in the previous sessions (2026-04-02/03).
Premium TESTING (`agent_2cffe3d86d7e1990d08bea068f`) may be out of date.
Before testing: compare Premium TESTING prompt against Standard MASTER and apply equivalent fixes.

### Step 4 — Run agent simulator against Premium TESTING
```bash
python3 tools/openai-agent-simulator.py --agent agent_2cffe3d86d7e1990d08bea068f --group core_flow
```
Run all groups. Fix failures on TESTING. Target 95%+ before touching MASTER.

### Step 5 — Promote to MASTER once passing
- Patch `agent_9822f440f5c3a13bc4d283ea90` (MASTER) with verified changes
- Publish MASTER
- Update `skills/hvac-premium-SKILL.md`

---

## Key IDs — Premium

| Resource | ID |
|---|---|
| MASTER Agent | `agent_9822f440f5c3a13bc4d283ea90` |
| TESTING Agent | `agent_2cffe3d86d7e1990d08bea068f` |
| MASTER Flow | `conversation_flow_1dd3458b13a7` |
| TESTING Flow | `conversation_flow_2ded0ed4f808` |
| Onboarding workflow | `kz1VmwNccunRMEaF` |
| Call processor workflow | `STQ4Gt3rH8ptlvMi` |
| E2E test | `python3 shared/e2e-test-premium.py` (89/89 ✅) |

---

## What's different about Premium testing vs Standard

| Area | Standard | Premium |
|---|---|---|
| Core flow | Lead capture only | Lead capture + booking flow |
| Calendar | None | Real-time slot fetch + booking |
| Scenarios | 80 scenarios, 6 groups | Expect similar — booking scenarios added |
| Complexity | Sophie collects info + closes | Sophie collects info + confirms booking slot |
| Failure modes | Wrong routing, missed fields | Wrong routing + failed booking + slot confusion |

---

## Standard improvements to carry over to Premium

These were all fixed in Standard MASTER (2026-04-03) — check if Premium has them:

1. **Lean global prompt** (~4,000 chars) — remove bloat, move specifics to nodes
2. **Code node for caller style detection** — injects `caller_style_note` at leadcapture top
3. **Explicit scripted closing words** in leadcapture node
4. **Emergency routing** — extreme urgency (freezing/elderly) offers transfer; matter-of-fact = high-priority lead
5. **Wrong number branch** in identify_call_node
6. **MINIMAL INFO RULE** in leadcapture — no extra probing after caller says enough
7. **Out-of-area re-ask fix** — only collect REMAINING details
8. **Vendor/job applicant handling** in identify_call_node
9. **Pricing redirect** — no specific fees, redirect to team callback

---

## Standard test scores for reference

| Test | Score | Script |
|---|---|---|
| Agent behaviour | 80/80 ✅ | `tools/openai-agent-simulator.py` |
| E2E pipeline | 75/75 ✅ | `python3 shared/e2e-test.py` |
| Call processor | 20/20 ✅ | `python3 tests/call-processor-test.py` |
