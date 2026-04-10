# Agent Testing System — Design
_Written 2026-04-10. Pick up in a fresh session._

---

## The Real Question

The pipeline is:

```
Retell call  →  post-call analysis (gpt-4.1-mini)  →  webhook  →  n8n filter  →  email + SMS
```

We already test Layer 3 (n8n filter → email/SMS) with `tools/test_call_processor.py` — 30 scenarios, 90/90.

The untested gap is **Layer 2**: does Retell's post-call analysis correctly classify calls?  
(`is_lead`, `urgency`, `is_spam` — the fields n8n reads to decide who gets notified)

If gpt-4.1-mini mis-classifies a call (says `is_lead: false` when it should be `true`), the client never gets the SMS/email — silently dropped. That's the real risk.

We also have a secondary gap: **email delivery confirmation** — n8n execution succeeds ≠ Brevo actually delivered the email.

---

## What We Do NOT Need to Test

- Sophie's conversation routing (Retell handles entirely — out of our control)
- Supabase writes from call processor (there are none — lean fan-out)
- n8n execution routing by field values — covered by `test_call_processor.py`

---

## Testing Architecture (3 Layers)

### Layer 1 — Post-Call Analysis Quality (FREE)
**Goal:** Verify gpt-4.1-mini classifies transcripts correctly.

**How:** Pull the post-call analysis prompt from the MASTER agent config, feed synthetic transcripts to it via `claude -p` (free — Claude subscription, not API). Compare actual JSON output vs expected.

**Why this works:** Retell's post-call analysis is just a prompt run against the transcript. We can replicate it locally for zero cost.

**Swarm opportunity:** Each scenario is independent. Run 20 scenarios in parallel using 5 swarm agents × 4 scenarios each. Total wall-clock time ~30s instead of 5+ minutes serial.

### Layer 2 — n8n Routing Verification (FREE)
**Status:** DONE — `tools/test_call_processor.py`, 30 scenarios, 90/90 pass.

**What it confirms:** If a webhook arrives with `is_lead: true`, n8n execution succeeds. Does NOT confirm email arrived.

### Layer 3 — Email Delivery Confirmation (CHEAP)
**Goal:** Confirm Brevo actually sent the email to the client address.

**How:** Use a controlled test inbox (daniel@syntharra.com or a Syntharra alias), fire a call processor test with that address, then check the inbox via Gmail MCP tool. Single scenario — not all 30.

**Why not all 30:** One confirmed delivery proves the Brevo integration is live. The n8n execution status already tells us the HTTP request was made. Brevo logs any hard bounce.

---

## Scenario Suite (25 scenarios — focused)

The old 91-scenario suite was testing Sophie's *conversation routing*. That's Retell's problem now. Our 25 scenarios test the post-call analysis *classification* only.

### Group A — Should Trigger Notification (15 scenarios)
n8n expects: `is_lead=true` or `urgency=emergency`

| # | Scenario | Expected |
|---|---|---|
| 1 | New customer, AC not cooling, wants quote | `is_lead=true, urgency=normal` |
| 2 | Furnace dead in winter, family inside | `is_lead=true, urgency=emergency` |
| 3 | Elderly caller, heat not working, elderly home | `is_lead=true, urgency=emergency` |
| 4 | Caller has infant, AC out in summer heat | `is_lead=true, urgency=emergency` |
| 5 | Commercial building, wants maintenance contract | `is_lead=true, urgency=normal` |
| 6 | Caller mentions competitor couldn't fix it | `is_lead=true, urgency=normal` |
| 7 | New homeowner, wants full HVAC inspection | `is_lead=true, urgency=normal` |
| 8 | Caller unsure if they want service but gave address + phone | `is_lead=true, urgency=normal` |
| 9 | Carbon monoxide detector went off near furnace | `is_lead=true, urgency=emergency` |
| 10 | Rental property owner, needs tenant's unit fixed ASAP | `is_lead=true, urgency=high` |
| 11 | AC making loud banging noise, wants it looked at | `is_lead=true, urgency=normal` |
| 12 | Caller says "it's an emergency" explicitly | `is_lead=true, urgency=emergency` |
| 13 | Caller gave only name + problem, no address yet | `is_lead=true, urgency=normal` |
| 14 | Existing customer reporting new issue (distinct from billing) | `is_lead=true, urgency=normal` |
| 15 | Spanish-speaking caller, clear HVAC repair request | `is_lead=true, urgency=normal` |

### Group B — Should NOT Trigger (7 scenarios)
n8n expects: `is_lead=false, urgency=none/low`

| # | Scenario | Expected |
|---|---|---|
| 16 | Telemarketer trying to sell the company something | `is_lead=false, is_spam=true` |
| 17 | Robocall / dead air, no real caller | `is_lead=false, is_spam=true` |
| 18 | Wrong number, caller hung up after "hello" | `is_lead=false` |
| 19 | Caller asking for directions to office | `is_lead=false` |
| 20 | Existing client asking about their invoice (billing only) | `is_lead=false` |
| 21 | Prank call / incoherent | `is_lead=false, is_spam=true` |
| 22 | Caller explicitly says "just curious, not ready yet, don't call me" | `is_lead=false` |

### Group C — Edge Cases (3 scenarios)
| # | Scenario | Expected |
|---|---|---|
| 23 | Caller is spam BUT mentions emergency (smoke smell) | `is_lead=true, urgency=emergency` ← safety override |
| 24 | Very short call — caller gave name + phone + said "AC broken" then hung up | `is_lead=true` |
| 25 | Caller mentions competitor explicitly (e.g. "ARS couldn't fix it") | `is_lead=true` (competitor mention = warm lead) |

---

## Implementation Plan

### Step 1 — Extract Post-Call Analysis Config (10 min)

Pull the post-call analysis block from MASTER agent via Retell API:

```bash
python -c "
import os, json, urllib.request
key = os.environ['RETELL_API_KEY']
req = urllib.request.Request(
    'https://api.retellai.com/v2/get-agent/agent_b46aef9fd327ec60c657b7a30a',
    headers={'Authorization': 'Bearer ' + key}
)
agent = json.loads(urllib.request.urlopen(req).read())
print(json.dumps(agent.get('post_call_analysis_data', {}), indent=2))
"
```

Save the output to `tools/fixtures/post_call_analysis_config.json`.

### Step 2 — Build Transcript Generator (tools/gen_transcripts.py)

Generate realistic transcripts for all 25 scenarios using `claude -p`:

```python
# pseudo-structure
def gen_transcript(scenario: str, context: str) -> str:
    prompt = f"""Generate a realistic HVAC customer service call transcript.
Sophie is the AI agent (professional, helpful).
Caller scenario: {scenario}
Context: {context}
Format: SOPHIE: ... / CALLER: ... alternating. 8-15 exchanges."""
    return run_claude_p(prompt)  # subprocess call to claude -p
```

Store generated transcripts in `tools/fixtures/transcripts/` — generated once, reused.

### Step 3 — Build Analysis Runner (tools/test_post_call_analysis.py)

For each transcript, call gpt-4.1-mini with the same prompt Retell uses:

```python
# Pull analysis config, format prompt, call claude -p with the actual model
# Extract JSON output, compare to expected classification
# PASS/FAIL per scenario
```

Use a swarm of 5 parallel subagents to run 5 groups of 5 scenarios each.  
Each subagent: `claude -p "Run post-call analysis for scenario {N}..."` via subprocess.

### Step 4 — Email Delivery Check (tools/test_email_delivery.py)

Single integration test:
1. Fire one call processor webhook with `email=daniel@syntharra.com` as client email
2. Wait 30s
3. Check Gmail via `mcp__claude_ai_Gmail__gmail_search_messages` for email from Brevo
4. PASS if found, FAIL if not found after 60s

### Step 5 — Wire it all together (tools/run_full_test_suite.py)

```
LAYER 1: Post-call analysis quality    (25 scenarios, parallel)
LAYER 2: n8n routing                   (tools/test_call_processor.py, 30 scenarios)
LAYER 3: Email delivery                (1 scenario, live Brevo check)

Total: ~2 minutes. Cost: $0.
```

---

## Swarm Design

For Layer 1 (25 parallel transcript evaluations):

```
ORCHESTRATOR
├── AGENT-A: scenarios 1-5  (lead/emergency group)
├── AGENT-B: scenarios 6-10 (lead group)
├── AGENT-C: scenarios 11-15 (lead/edge group)
├── AGENT-D: scenarios 16-21 (filter group)
└── AGENT-E: scenarios 22-25 (edge cases)
```

Each agent: `claude -p` subprocess with the transcript + analysis prompt. Collect results, aggregate pass/fail.

**Why swarm is worth it here:** 25 sequential `claude -p` calls at ~5s each = 2 minutes. Parallel = 30 seconds. Also: each agent is stateless, no shared state, perfect for parallel.

---

## Prompt Efficiency Rules

When test failures reveal Sophie says the wrong thing:

1. **Find the specific node** — not the whole agent. Check which code node produced the bad response.
2. **Minimum viable fix** — add one sentence to that node's instructions, not a paragraph. Test again.
3. **Max 10 words added per fix** — if you need more than 10 words, the logic is wrong, not just the phrasing.
4. **Never add instructions that duplicate existing instructions** — grep the existing prompt first.

The post-call analysis prompt (gpt-4.1-mini) is separate from Sophie's conversation prompt. Fixes to classification accuracy go in the post-call analysis config only.

---

## When Telnyx SMS Goes Live

Add Layer 4 to the suite:
1. Update `tools/test_call_processor.py` — replace the `is_sms_stub` assertion with a real check
2. Add a test that fires a webhook, waits 30s, then checks Telnyx delivery logs via API
3. Add this as 3 scenarios: emergency (should SMS), lead (should SMS), filtered (should not SMS)

The stub node in the call processor is marked `TELNYX-TODO` — swap it to a real HTTP node when the key is in vault.

---

## Files to Create (next session)

```
tools/
  gen_transcripts.py          — generate + cache 25 transcripts via claude -p
  test_post_call_analysis.py  — run analysis on transcripts, compare to expected
  test_email_delivery.py      — fire real webhook, check Gmail inbox
  run_full_test_suite.py      — orchestrate all 3 layers
  fixtures/
    post_call_analysis_config.json   — pulled from MASTER agent
    transcripts/                     — 25 generated transcript files
    scenarios.json                   — scenario definitions (25 rows)
```

---

## Success Criteria

| Layer | Pass condition |
|---|---|
| Post-call analysis | 24/25 scenarios classified correctly (95%+) |
| n8n routing | 30/30 (already 90/90) |
| Email delivery | 1/1 (Brevo email received in inbox) |

If post-call analysis < 95%, look at which scenarios fail and update the analysis prompt (not Sophie's prompt). Analysis prompt is in the MASTER agent's `post_call_analysis_data` block.

---

## Running in the New Session

```bash
# 1. Generate transcripts (once — cached after)
python tools/gen_transcripts.py

# 2. Run full suite
python tools/run_full_test_suite.py

# 3. Or run layers individually
python tools/test_post_call_analysis.py
python tools/test_call_processor.py
python tools/test_email_delivery.py
```
