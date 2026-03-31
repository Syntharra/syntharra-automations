# Deep Call Log Analysis — Real Calls
**Date:** 31 March 2026  
**Calls analysed:** 9 (8 with transcripts, 1 error)

---

## CRITICAL ISSUE #1: "Say:" prefix STILL appearing in live calls

**Affected calls:** #2, #5, #7 (3 out of 8 transcribed calls = 37.5%)

The agent is literally speaking the words "Say:" followed by the instruction text. This is the transfer_failed node — it's reading the raw instruction instead of following it.

**Evidence:**
- Call 2: `Agent: Say: "I'm sorry, I wasn't able to connect you right now. Let me take your name and number..."`
- Call 5: `Agent: Say: "I'm sorry, I wasn't able to connect you right now. Let me take your name and number..."`
- Call 7: `Agent: Say: "I'm sorry, I wasn't able to connect you right now. Let me take your name and number..."`

**Root cause:** We fixed the transfer_failed node in THIS session — but the old static_text version with "Say:" is still being used on these older calls. HOWEVER, the Transfer Call node's transfer_failed fallback might be using a DIFFERENT text than the node itself. The Transfer Call node (type: transfer_call) has its own built-in failure message that fires when the transfer fails, SEPARATE from the transfer_failed_node.

**FIX:** Need to check the Transfer Call node's configuration — it likely has its own "transfer_failed_message" or similar field that still contains the "Say:" prefix text. The transfer_failed_node we fixed is only reached via an edge, but the Transfer Call node's BUILT-IN failure handling fires first.

---

## CRITICAL ISSUE #2: Transfer always failing

**Affected calls:** #1, #2, #5, #7 (every call that attempted transfer)

Every single transfer attempt fails. The agent tries to transfer, it doesn't connect, and falls back to collecting details. This means:
- Emergency calls can't be transferred
- Angry callers can't be transferred  
- Anyone requesting a live person can't be transferred

**Root cause:** The transfer destination is +15125550192 — which is the Arctic Breeze DEMO number, not a real phone line. Since Arctic Breeze is our test company, there's nobody to answer. This is EXPECTED for testing, but it means:
1. The transfer failure path is being exercised on every transfer attempt
2. The "Say:" bug in the failure message is hitting callers every time

**FIX:** This is not a bug for production (real clients will have real transfer numbers). But for testing, we should make the transfer_failed path seamless.

---

## HIGH ISSUE #3: Agent asks multiple questions in one turn

**Affected calls:** #1, #6

- Call 1: "Just to check, is it no cooling at all right now, and is it extremely hot inside? Any water leaks, burning smell, or gas smell coming from the unit?" (3 questions in one turn)
- Call 6: "is it completely not cooling at all, or are you also noticing anything like water leaking, a burning smell, or maybe a gas odor?" (multiple sub-questions)

**Root cause:** The verify_emergency node asks the agent to check for emergency indicators, and it bundles them all into one question. The "one question at a time" rule in the global prompt is being overridden by the emergency check logic.

**FIX:** Update verify_emergency node to ask ONE question: "Is your system completely not working at all right now?" Then ONLY if yes, follow up with safety: "Are you noticing any burning smell, gas smell, or water leaking?" Two turns, not one.

---

## HIGH ISSUE #4: Agent not doing final summary

**Affected calls:** #1, #4, #6

- Call 1: Collected name and number but ended without summarising
- Call 4: Collected all details, asked "anything else?" but never summarised back
- Call 6: Collected details but kept going back and forth on address without final summary

**Root cause:** The leadcapture node has the summary instruction but the agent is moving to the Ending node ("Is there anything else?") BEFORE doing the summary. The summary should happen at the END of lead capture, BEFORE transitioning to Ending.

**FIX:** The leadcapture instruction says summary is mandatory but the edge to node-ending fires before the agent completes it. Need to add a transition condition that requires summary completion, or make the summary part of the Ending node itself.

---

## HIGH ISSUE #5: Address confirmation loop

**Affected calls:** #6, #8

- Call 6: "Brighties Pass" → "Brody's Pat" → "Brady's Pat" — 3 attempts, agent kept mishearing
- Call 8: "Brady's pass" → "Bradley's Pat" → "Brady's path" → "B R I D I E S path" — 4 attempts

The agent keeps getting the address wrong and the caller has to correct it multiple times, creating frustration.

**Root cause:** This is a speech-to-text issue (in real calls), but in text simulation it shows that the agent is reformatting what the caller says incorrectly. The agent changes "Pat" to "Pass" to "Path" inconsistently. It needs to repeat EXACTLY what the caller said, or ask them to spell it.

**FIX:** Add to leadcapture node: "When confirming addresses, repeat the EXACT words the caller used. Do not paraphrase or reformat. If unclear, ask them to spell the street name."

---

## MEDIUM ISSUE #6: Callback node asks too many questions

**Affected call:** #3

- Call 3: Agent asked "Can I get your name and the best number to reach you at?" — two questions in one turn
- Caller said "Yeah. K." and hung up

**Root cause:** The callback node instruction bundles name + number into one ask. Should be separate.

**FIX:** Already addressed in our fix #7 (callback node tightened), but need to verify the latest version is active.

---

## MEDIUM ISSUE #7: Agent hangup on completed calls

**Affected calls:** #4, #8

Both calls show agent_hangup as disconnection reason but were otherwise successful. This may be the agent ending the call after the caller says goodbye, which is correct behaviour — but Retell logs it as agent_hangup rather than user_hangup.

**FIX:** This is likely not a real issue — the agent is properly ending the call. But monitor for cases where agent_hangup happens mid-conversation.

---

## Summary of Fixes Needed

| # | Severity | Issue | Fix Location |
|---|---|---|---|
| 1 | CRITICAL | "Say:" prefix in transfer failure | Transfer Call node built-in failure message |
| 2 | INFO | Transfers always fail | Expected for demo — not a production issue |
| 3 | HIGH | Multiple questions in one turn (emergency) | verify_emergency node instruction |
| 4 | HIGH | No final summary before ending | leadcapture → Ending transition logic |
| 5 | HIGH | Address confirmation loop/reformatting | leadcapture node — exact repeat instruction |
| 6 | MEDIUM | Callback bundles questions | callback node — already fixed, verify active |
| 7 | LOW | Agent hangup on complete calls | Monitor only |
