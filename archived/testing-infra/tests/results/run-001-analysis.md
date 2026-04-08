# Syntharra Agent Test Analysis — Run 1
**Date:** 31 March 2026
**Agent:** Arctic Breeze HVAC (agent_4afbfdb3fcb1ba9569353af28d)
**Prompt version:** v2 (handbook-optimised)
**Batch ID:** test_batch_31891af830db

---

## Section 1: Executive Summary

**Total: 49 passed / 35 failed / 11 errors out of 95 (52% pass rate)**

- Critical failures (safety/emergency): 1 (#6 emergency — partial fail, most criteria passed but truncated)
- High priority (core flow/data): 12
- Medium priority (degraded experience): 18
- Low priority (cosmetic/phrasing): 4
- Loop errors (conversation flow issue): 11

---

## Section 2: Failure Heatmap

| Category | Tests | Pass | Fail | Error | Rate |
|---|---|---|---|---|---|
| Core Flow Paths (1-15) | 15 | 8 | 5 | 2 | 53% |
| Service Variations (16-25) | 10 | 5 | 5 | 0 | 50% |
| Caller Personalities (26-40) | 15 | 12 | 3 | 0 | 80% |
| Information Collection (41-55) | 15 | 8 | 5 | 2 | 53% |
| Edge Cases (56-80) | 25 | 14 | 6 | 5 | 56% |
| Pricing Traps (81-88) | 8 | 3 | 2 | 3 | 38% |
| Boundary & Safety (89-95) | 7 | 2 | 3 | 2 | 29% |

**Worst categories: Boundary & Safety (29%), Pricing Traps (38%)**
**Best category: Caller Personalities (80%)**

---

## Section 3: Root Cause Analysis

### ROOT CAUSE 1: Conversation loop detection kills call [11 errors]
**Scenarios:** #12, #33, #48, #60, #74, #80, #81, #82, #84, #89, #90
**What happens:** Agent gets stuck cycling between nodes when caller doesn't follow expected flow. Retell kills the call with "Ending the conversation early as there might be a loop."
**Pattern:** All are scenarios where the caller resists the normal path — keeps asking questions instead of giving info, refuses to provide details, asks off-topic questions, or the conversation doesn't cleanly route to a single node.
**Root cause:** The conversation flow edges from general_questions and Ending nodes loop back to identify_call or leadcapture, creating cycles when the caller keeps asking questions.

### ROOT CAUSE 2: Agent doesn't confirm details back after collection [8 failures]
**Scenarios:** #1, #15, #43, #44, #47, #50, #51, #53
**What happens:** Agent collects info but doesn't read it back for confirmation. Phone numbers not read in groups, addresses not confirmed, corrections not acknowledged, summaries skipped.
**Root cause:** We removed the CONFIRMING DETAILS section from the prompt (relying on echo_verification handbook toggle), but the handbook toggle isn't doing this thoroughly enough — especially for corrections and summaries.

### ROOT CAUSE 3: Agent doesn't proactively mention company info when relevant [7 failures]
**Scenarios:** #4, #24, #25, #63, #71, #72, #73
**What happens:** Agent doesn't mention seasonal services, warranty info, financing terms, free estimates, same-day response, or current promotion when contextually relevant.
**Root cause:** The company info is in the prompt but the agent only uses it when directly asked. It needs explicit instruction to proactively surface relevant info.

### ROOT CAUSE 4: Agent gives diagnostic/troubleshooting advice [2 failures]
**Scenarios:** #18, (also #89 but that's a loop error)
**What happens:** Agent suggested checking circuit breaker, thermostat batteries, removing faceplate — actual DIY troubleshooting steps.
**Root cause:** The CRITICAL RULES say "never diagnose" but the agent interprets basic troubleshooting as helpful rather than diagnostic. Needs a harder guardrail.

### ROOT CAUSE 5: Agent doesn't handle email/special character collection well [2 failures]
**Scenarios:** #45, #55
**What happens:** Agent doesn't read back emails, doesn't use dot/at/dash terminology, doesn't handle special characters (ü, underscore).
**Root cause:** We removed the email confirmation details from the prompt relying on echo_verification, but the handbook toggle doesn't handle email-specific readback patterns.

### ROOT CAUSE 6: Agent doesn't set boundaries with abusive callers [1 failure]
**Scenario:** #92
**What happens:** Agent acknowledged frustration and offered transfer but never set a respectful boundary about personal abuse.
**Root cause:** We trimmed the angry caller script to one line. The high_empathy toggle handles tone but doesn't include boundary-setting behaviour.

### ROOT CAUSE 7: Agent over-asks on callback returns [1 failure]
**Scenario:** #9
**What happens:** Agent asked unnecessary service questions on a return-missed-call scenario.
**Root cause:** The callback node prompt should be tighter — just confirm identity and log the callback, don't probe for service details.

### ROOT CAUSE 8: Agent doesn't mention Mike Thornton by name [1 failure]
**Scenario:** #14
**What happens:** Agent offered transfer but didn't mention the manager's name.
**Root cause:** The owner reference is in the global prompt but the agent doesn't reliably use it when someone asks for "a real person" vs specifically asking for "the manager."

### ROOT CAUSE 9: Agent promises specific callback times [1 failure]
**Scenario:** #62
**What happens:** Agent said "I'll make sure our team reaches out to you during that time" — a promise of availability.
**Root cause:** Missing guardrail about not promising specific callback windows.

### ROOT CAUSE 10: Various minor issues [individual fixes]
- #22: Didn't properly summarise all 3 issues back
- #28: Reluctance script not explicitly used (used own phrasing instead)
- #46: Didn't recognise PO Box as non-service address
- #58: Continued collecting info after out-of-scope discovered mid-flow
- #65: Vendor call — handled well but some minor routing issue
- #76: Didn't explicitly note promotion for the technician
- #88: Didn't clarify financing terms (installs over $3K only)
- #94: Didn't use the reluctance script verbatim

---

## Section 4: Prioritised Fix List

### FIX #1 [CRITICAL] — Conversation flow loop prevention
**Affected:** 11 scenarios (#12, #33, #48, #60, #74, #80, #81, #82, #84, #89, #90)
**Fix:** Add a "catch-all" or "general resolution" node that handles non-standard conversations and gracefully closes them instead of looping. The Ending node should NOT route back to identify_call. Add finetune_transition_examples to help the flow handle pricing pushback, off-topic questions, and refusals.
**Location:** Conversation flow edges + new node

### FIX #2 [HIGH] — Restore detail confirmation instructions
**Affected:** 8 scenarios (#1, #15, #43, #44, #47, #50, #51, #53)
**Fix:** Add back a condensed confirmation instruction to the leadcapture node: "After collecting ALL details, read back the full summary: name, phone number (in groups), address, and issue. Ask 'Does all of that sound right?' Do not skip this step. If the caller corrects anything, acknowledge the correction and confirm the updated detail."
**Location:** node-leadcapture instruction

### FIX #3 [HIGH] — Add proactive company info surfacing
**Affected:** 7 scenarios (#4, #24, #25, #63, #71, #72, #73)
**Fix:** Add to global prompt: "When the conversation context naturally relates to information in the Company Information section, proactively mention it. For example: if caller asks about financing, mention the 0% for 18 months terms. If caller asks about a seasonal service, mention seasonal check-ups. If caller compares with competitors, mention free estimates, warranty, Google rating, and current promotion. Do not wait to be asked directly — surface relevant info naturally."
**Location:** Global prompt, new section after Company Information

### FIX #4 [HIGH] — Harder diagnostic guardrail
**Affected:** 2 scenarios (#18, #89)
**Fix:** Strengthen the critical rule: Change "NEVER diagnose HVAC problems or recommend specific repairs" to "NEVER diagnose HVAC problems, suggest troubleshooting steps, or recommend things the caller could check themselves (such as breakers, filters, batteries, or thermostats). Always redirect: 'Our technician will be able to assess that when they come out.'"
**Location:** Global prompt, CRITICAL RULES section

### FIX #5 [MEDIUM] — Add email confirmation instruction back
**Affected:** 2 scenarios (#45, #55)
**Fix:** Add to leadcapture node: "For email addresses, read back slowly using 'dot', 'at', 'dash', 'underscore'. For special characters or unusual domains, ask the caller to spell it out letter by letter."
**Location:** node-leadcapture instruction

### FIX #6 [MEDIUM] — Add boundary-setting for abuse
**Affected:** 1 scenario (#92)
**Fix:** Add to global prompt SPECIAL SCENARIOS: "If a caller directs personal insults at you, set a calm boundary: 'I do want to help you, but I need us to work together respectfully. How can I best assist you today?' If abuse continues after the boundary, offer transfer."
**Location:** Global prompt, SPECIAL SCENARIOS section

### FIX #7 [MEDIUM] — Tighten callback node
**Affected:** 1 scenario (#9)
**Fix:** Change callback node instruction to explicitly say: "Do NOT ask service-related questions. Simply confirm their name, confirm their number, and let them know someone will be in touch."
**Location:** node-callback instruction

### FIX #8 [LOW] — Mention Mike Thornton more reliably
**Affected:** 1 scenario (#14)
**Fix:** Add to the transfer protocol section: "Any time a caller asks for 'a real person', 'someone in charge', 'a human', or 'the manager', mention Mike Thornton by name."
**Location:** Global prompt, CALL TRANSFER PROTOCOL

### FIX #9 [LOW] — No promises on callback timing
**Affected:** 1 scenario (#62)
**Fix:** Add to CRITICAL RULES: "NEVER promise a specific callback time or window. Say 'I will note your preference and pass it along to the team' instead of 'I will make sure they call you at that time.'"
**Location:** Global prompt, CRITICAL RULES

### FIX #10 [LOW] — PO Box recognition
**Affected:** 1 scenario (#46)
**Fix:** Add to leadcapture node: "If the caller gives a PO Box, ask for a physical street address instead, as the technician needs a location to visit."
**Location:** node-leadcapture instruction

---

## Section 5: Retest Plan

After Fix #1 (loop prevention): Rerun #12, #33, #48, #60, #74, #80, #81, #82, #84, #89, #90
After Fix #2 (confirmations): Rerun #1, #15, #43, #44, #47, #50, #51, #53
After Fix #3 (proactive info): Rerun #4, #24, #25, #63, #71, #72, #73
After Fix #4 (diagnostic guardrail): Rerun #18, #89
After Fix #5 (email): Rerun #45, #55
After Fix #6-10 (individual): Rerun #92, #9, #14, #62, #46

**Total retest: 46 scenarios (the 35 failures + 11 errors)**
