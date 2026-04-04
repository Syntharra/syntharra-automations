# Session Log — 2026-04-04 — full-pipeline-audit-and-test-hygiene

## Summary
Long session. Started with a broken E2E (74/90) and ended with a clean system, 90/90,
no test pollution, and a fully audited Jotform → Supabase field map.

---

## What Was Done

1. **E2E 74/90 — diagnosed and fixed**
   All 16 failures were in Phases 4+5 (Retell agent/flow verification).
   Root cause: RETELL_KEY env var was set to a stale key. n8n uses a different valid key.
   Fix: embedded correct key as fallback in e2e-test.py. Re-ran: 90/90.

2. **Onboarding email missing phone numbers**
   Build Onboarding Pack HTML node used wrong field names:
   - `d.ai_phone_number` → should be `d.twilio_number`
   - `d.transfer_phone_number` → should be `d.transfer_phone`
   Fixed both. Confirmed in email preview.

3. **Transfer number logic wrong**
   Original code: `emergencyPhone || leadPhone` — completely ignored transfer_phone (q48).
   After two incorrect intermediate fixes (my fault — didn't read the full spec first):
   Correct logic: `q69 == "Yes" ? emergencyPhone : (transferPhone || leadPhone)`

4. **Full Jotform audit — 4 missing fields found**
   Compared all 55 live Jotform questions against Parse JotForm Data node.
   Missing:
   - `q73_customGreetingText` — real custom greeting (q38 is dead, was being read instead)
   - `q72_greetingStyle` — greeting tone (Standard/Warm/Professional/Custom)
   - `q68_afterHoursTransfer` — after-hours transfer behaviour
   - `q69_separateEmergencyPhone` — gate question for emergency override
   All 4 added to Parse node and Build Retell Prompt extractedData.

5. **Test data pollution — Polar Peak everywhere**
   E2E test payload had Polar Peak hardcoded in: website, 2 notification emails, membership
   program name, company name, greeting. Developer was receiving Polar Peak-branded emails
   on every test run. Fixed all 6 references. Test data is now fully generic.

6. **Email suppression gate — universalised**
   Named patterns (Polar Peak, FrostKing etc.) were incomplete and required manual updates.
   Replaced with universal timestamp pattern `/\d{9,10}$/` as primary catch-all.
   Named patterns kept as backup. Added to both email nodes in n8n.

7. **Jotform Backup Polling runaway**
   Poller re-fired onboarding webhook 1741 times creating junk HVAC Company rows.
   Root cause: in-flight Reconcile executions completing their 2-min wait, combined with
   test submissions leaking through the poller's pattern list.
   Fix: killed executions, deleted junk rows, added Stripe payment gate to poller,
   updated test patterns in poller to match n8n suppression gate.

8. **Final E2E: 90/90 ✅** — TestClient HVAC, clean run, no emails to inbox.

---

## Mandatory Reflection

### 1. What did I get wrong or do inefficiently?

**Transfer number logic — two wrong fixes before the right one.**
I changed the logic twice incorrectly before finding the q69 gate. The first wrong fix was
`transferPhone || leadPhone` (forgot emergency entirely). The second was back to
`emergencyPhone || transferPhone || leadPhone` (emergency always wins, ignores q69).
The correct answer required reading the Jotform form itself to find q69.

Root cause: I read the code comment ("use lead_phone, emergency_phone as override") and
treated it as the spec. It wasn't — it was an incomplete description. The Jotform form
is the spec. I should have looked there first.

**What I should have done:** When Dan said "emergency should only override if provided",
my first action should have been to fetch all Jotform questions and find the gate question.
Instead I made assumptions based on an incomplete code comment.

### 2. What assumption was wrong?

That `emergency_phone` was always intended to override the transfer destination.
The q69 question ("Do you use a separate emergency phone number?") exists precisely because
most clients do NOT have a separate emergency line — they use the same number for everything.
The override should only happen when the client explicitly opts in.

### 3. What would I do differently?

For any field prioritisation question: find all related Jotform questions first,
map the full intent, then write the code. Never use a code comment as the spec.

For test data: enforce the rule from day one that test data uses only generic domains
and names. The Polar Peak branding was in the test from the original build and no one
questioned it — it looked like client data, which is exactly the problem.

### 4. What patterns emerged that future-me needs to know?

**Pattern 1: Jotform form drift**
Every time a question is added to the form without updating Parse JotForm Data, there's
a silent data loss. No error is thrown. The field simply isn't captured. This has happened
at least twice now (the q64-q67 notification fields, and now q68/q69/q72/q73).
Mandatory rule going forward: form addition = Parse node update in same session.

**Pattern 2: Test pollution looks like real bugs**
When test runs leave noise (junk rows, stale emails, wrong keys in env vars), subsequent
debugging is confused by artifacts from previous sessions. This session wasted significant
time on things that weren't actually bugs. Clean test hygiene prevents this entirely.

**Pattern 3: The backup poller is a risk multiplier**
Any workflow that reads Jotform submissions and acts on them will amplify test pollution.
The Stripe gate is the correct fix — gate on real payment, not just on company name patterns.

### 5. What was added to ARCHITECTURE.md / skill files?

ARCHITECTURE.md:
- Universal timestamp suppression pattern decision + reasoning
- Jotform field audit protocol — why it's mandatory
- Transfer number priority — correct spec with q69 gate
- Backup poller — keep but gate on Stripe decision
- Test pollution lesson — how it compounds into false debugging signals
- "Read the code comment critically" lesson

e2e-hvac-standard skill: full rewrite — canonical test data values, suppression gate
rules, complete Jotform field map, RETELL_KEY sync rule, troubleshooting guide updated.

### 6. Did I do anything "because that's how it's done" that I haven't verified?

Yes — I initially treated the original transfer number logic as intentional design rather
than questioning it. The comment said "use lead_phone by default, emergency_phone as override"
and I took that at face value without checking whether it matched the Jotform form design.
The q69 gate makes it clear the original logic was incomplete, not intentional.

Going forward: any fallback/priority chain in the codebase should be cross-referenced against
the Jotform form questions before being treated as correct.
