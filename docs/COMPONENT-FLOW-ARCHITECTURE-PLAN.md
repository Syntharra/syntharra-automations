# Sub-Flow Component Architecture Plan — DEFINITIVE

> **Status:** Plan only — not yet implemented
> **Date:** 2026-04-05
> **Verified by:** API testing against Retell production endpoints

---

## Current State

We have **12 single-node Library Components**, each containing one node. Every client flow (Standard 19 nodes, Premium 24 nodes) references these via `type: "subagent"` with `component_id`. The build code also contains a **COMPONENTS object** with 11-12 functions that generate inline instruction text for non-component nodes.

**Problem:** Updating an instruction means updating the COMPONENTS object in build code AND rebuilding every client flow. The Library Components are referenced but the build code also duplicates instruction logic inline. We want "update once, deploy everywhere."

---

## Verified API Constraints (tested 2026-04-05)

These are hard facts, not assumptions. Every one was tested against the live Retell API.

### Node types ALLOWED inside Library Components

| Type | Tested | Notes |
|------|--------|-------|
| `conversation` | ✅ 201 | Multi-node conversation components work |
| `subagent` | ✅ 201 | Nested component references work (component-in-component) |
| `extract_dynamic_variables` | ✅ 201 | Can extract structured data inside a component |
| `end` | ✅ Listed | Exit node for component completion |

### Node types NOT ALLOWED inside Library Components

| Type | Tested | Error |
|------|--------|-------|
| `code` | ❌ 400 | "must match exactly one schema in oneOf" |
| `transfer_call` | ❌ 400 | Not an allowed type inside components |
| `tool_call` | ❌ 400 | Not an allowed type inside components |

### Subagent node schema (in parent flows)

Fields accepted: `component_id`, `instruction`, `name`, `edges`, `id`, `type`, `is_start`, `display_position`, `finetune_transition_examples`

Fields NOT accepted: `start_node_id` — ❌ tested, causes 400

### How code components work as subagents

When a single-node code Library Component (e.g., `validate_phone`) is referenced as `type: "subagent"` in a parent flow, the subagent node carries additional fields: `code`, `else_edge`, `speak_during_execution`, `wait_for_result`. These are inherited from the component.

### Multi-node component entry point

When a parent flow references a multi-node component via `type: "subagent"`, execution starts at the **first node in the component's nodes array** (the node at index 0). There is no `start_node_id` on the subagent node.

The flow-level `components` array has `start_node_id` but this is for inline/embedded components created in the Retell UI editor, not for Library Components referenced via subagent.

### Nested components

A multi-node Library Component CAN contain `type: "subagent"` nodes that reference other Library Components. This means we can include validate_phone (code component) inside a larger conversation component by referencing it as a nested subagent.

---

## Revised Architecture Design

Given the constraints above, the original plan needs significant revision. Code nodes and transfer nodes cannot live inside components. But nested subagent references work, which is the key workaround.

### Design Principles

1. **Only conversation + subagent + extract + end nodes inside components** — everything else stays in parent flow
2. **Code components stay as single-node Library Components** — referenced via nested subagent inside multi-node components
3. **Transfer nodes stay in parent flow** — they can't go inside components
4. **Global nodes stay in parent flow** — they're flow-level constructs
5. **First node in array = entry point** — design component node order accordingly

---

### Component 1: INTAKE COMPONENT (shared Standard + Premium)

**Purpose:** Routes the call and detects caller style.

**Internal nodes (2):**

| Index | Node ID | Type | Description |
|-------|---------|------|-------------|
| 0 | `node-identify-call` | `conversation` | Listen and route by call purpose |
| 1 | `node-style-detector` | `subagent` | References `conversation_flow_component_ff58734c21bb` (call_style_detector code component) |

**Internal edges:**
- `identify_call` → `style_detector`: "Service request, repair, maintenance, booking, or any new service request"

**Exit conditions (on parent flow's subagent node):**
- "Service request routed through style detector" → Capture/Booking Component
- "Emergency" → Emergency Component
- "Callback return" → Callback node (Support Component or standalone)
- "Existing customer" → Existing Customer node
- "General question / FAQ" → FAQ node
- "Spam / robocall" → Spam node
- "Transfer to human" → Transfer Call node (parent flow)

**Why this grouping:** identify_call always feeds into call_style_detector for service requests. The style detector sets `caller_style_note` which the next conversation node uses. Bundling them eliminates an edge hop and ensures style detection always runs.

**Limitation:** The style detector is a code node referenced as nested subagent. Need to verify the code/else_edge fields carry through when nested inside a component (vs. at flow level).

---

### Component 2: CAPTURE COMPONENT — Standard variant

**Purpose:** Collects lead information (no booking).

**Internal nodes (2):**

| Index | Node ID | Type | Description |
|-------|---------|------|-------------|
| 0 | `node-leadcapture` | `conversation` | Collect name, phone, address, service needed |
| 1 | `node-validate-phone` | `subagent` | References `conversation_flow_component_3b788e86e755` (validate_phone code component) |

**Internal edges:**
- `leadcapture` → `validate_phone`: "Phone number provided, ready to validate"

**Exit conditions:**
- "Details confirmed, phone validated" → Close Component
- "Emergency detected during capture" → Emergency Component (parent flow routing)

**Why this grouping:** Lead capture always needs phone validation. Currently these are 2 separate nodes with an edge between them. Bundling ensures validation always runs.

---

### Component 3: BOOKING COMPONENT — Premium variant

**Purpose:** Books an appointment with calendar integration.

**Internal nodes (4):**

| Index | Node ID | Type | Description |
|-------|---------|------|-------------|
| 0 | `node-booking-capture` | `conversation` | Collect booking details (service, name, phone, address, preferred time) |
| 1 | `node-check-availability` | `conversation` | Check calendar and confirm slot |
| 2 | `node-confirm-booking` | `conversation` | Read back and confirm all details |
| 3 | `node-validate-phone` | `subagent` | References `conversation_flow_component_3b788e86e755` |

**⚠️ BLOCKER: `tool_call` nodes not allowed inside components.** The Premium flow uses `tool_call` nodes for calendar integration (`check_availability`, `create_booking` tools). These CANNOT go inside the component.

**Options:**

**Option A — Calendar tools stay in parent flow:**
The Booking Component contains only the conversation nodes. When the component exits with "ready to check calendar," the parent flow handles the tool_call, then routes back into the component (or to a confirmation node).

**Problem:** You can't route BACK into a multi-node component at a specific node. Once you exit a component, re-entering starts at node 0 again.

**Option B — Booking Component is conversation-only, tools are separate:**
```
Parent: Intake → Booking Component (capture details) →
        check_availability (tool_call, parent) →
        confirm_booking (conversation, parent OR separate component) →
        validate_phone (subagent, parent) → Close
```
This reduces the Booking Component to just `booking_capture` (1 conversation node), which defeats the purpose.

**Option C — Keep booking nodes as separate inline/subagent nodes (no consolidation):**
The Premium booking path is too interleaved with tool_calls to consolidate. Keep `booking_capture`, `check_availability`, `confirm_booking` as separate nodes in the parent flow. Only consolidate the nodes that don't need tool_call interaction.

**RECOMMENDATION: Option C.** The booking path doesn't benefit from componentization because tool_calls break the flow. Focus consolidation effort on the Standard path and shared non-booking nodes instead.

---

### Component 4: EMERGENCY COMPONENT (shared)

**Purpose:** Verifies if situation is a true emergency.

**Internal nodes (1):**

| Index | Node ID | Type | Description |
|-------|---------|------|-------------|
| 0 | `node-verify-emergency` | `conversation` | Two-step urgency verification |

**Exit conditions:**
- "Confirmed emergency" → Emergency Transfer (transfer_call node, parent flow)
- "Urgent but not emergency" → Capture/Booking path

**Note:** This is already a single-node component (`conversation_flow_component_174275fc7751`). No change needed. It works as-is.

---

### Component 5: CLOSE COMPONENT (shared)

**Purpose:** Handles call wrapup.

**Internal nodes (2):**

| Index | Node ID | Type | Description |
|-------|---------|------|-------------|
| 0 | `node-ending` | `conversation` | "Anything else?" + warm close |
| 1 | `node-end` | `end` | Component exit |

**Exit conditions:**
- Component ends naturally → parent flow routes to End Call

**Why this grouping:** The ending conversation + end node always run together. Bundling means one component reference instead of two nodes.

---

### Components that stay UNCHANGED (single-node)

These nodes don't benefit from multi-node consolidation:

| Component | ID | Reason |
|-----------|-----|--------|
| `callback` | `conversation_flow_component_ab7909b654e2` | Standalone conversation, no downstream node always follows |
| `existing_customer` | `conversation_flow_component_d8eff9881e16` | Same — routes to ending but ending is a separate component |
| `general_questions` | `conversation_flow_component_d46848148d1d` | Same |
| `spam_robocall` | `conversation_flow_component_1672ee3d3b07` | Routes to end call, trivial node |
| `transfer_failed` | `conversation_flow_component_f22f9442d2b5` | Standalone fallback |
| `call_style_detector` | `conversation_flow_component_ff58734c21bb` | Code node — must stay as single-node component |
| `validate_phone` | `conversation_flow_component_3b788e86e755` | Code node — must stay as single-node component |

---

## What Actually Gets Consolidated

Given the API constraints, the realistic consolidation is:

### Standard Flow: 3 new multi-node components

| New Component | Replaces | Node Count | Benefit |
|---------------|----------|------------|---------|
| **Intake** (identify_call + nested style_detector) | 2 separate nodes | 2 | Style detection always runs for service requests |
| **Capture** (leadcapture + nested validate_phone) | 2 separate nodes | 2 | Phone validation always runs |
| **Close** (ending + end) | 2 separate nodes | 2 | Clean wrapup path |

**Standard parent flow: 19 nodes → ~15 nodes** (saves 4 nodes by consolidating 8 into 4 component references, but adds nothing new)

### Premium Flow: 2 new multi-node components

| New Component | Replaces | Node Count | Benefit |
|---------------|----------|------------|---------|
| **Intake** (shared with Standard) | 2 separate nodes | 2 | Same as Standard |
| **Close** (shared with Standard) | 2 separate nodes | 2 | Same as Standard |

**Premium parent flow: 24 nodes → ~22 nodes** (booking path stays inline due to tool_call constraint)

**Note:** Premium does NOT get a Capture Component because the Premium capture path involves booking → tool_calls → confirmation, which can't be componentized.

---

## Realistic Impact Assessment

### What this architecture DOES achieve:
- **"Update once, deploy everywhere"** for identify_call, call_style_detector, leadcapture, validate_phone, and ending instructions
- **Fewer nodes in parent flows** (~4 fewer for Standard, ~2 fewer for Premium)
- **Enforced coupling** of nodes that should always run together (e.g., capture + validate)
- **Single source of truth** for instruction text (in the Library Component, not duplicated in build code)

### What this architecture does NOT achieve:
- **Premium booking consolidation** — tool_call constraint prevents this
- **Dramatic parent flow simplification** — constraint means only conversation+subagent groupings work
- **Starting-node selection** for Support component — can't route to a specific node inside a multi-node component

### Honest assessment:
The biggest wins are **Intake** and **Capture** components. These consolidate node pairs that always run together. The remaining components either don't benefit (single-node already) or can't be consolidated (tool_call dependency). The architecture is sound but the scope is narrower than originally proposed.

---

## Implementation Order (when ready)

**Phase 1 — Capture Component (Standard only, highest value)**
1. Create new 2-node Library Component: `leadcapture` (conversation) + `validate_phone` (nested subagent)
2. Test: verify nested code-subagent works inside a component (this is unverified)
3. Replace Standard TESTING flow's 2 separate nodes with 1 subagent reference
4. Run Standard E2E test
5. If passing: update Standard build code

**Phase 2 — Intake Component (shared)**
1. Create new 2-node Library Component: `identify_call` (conversation) + `call_style_detector` (nested subagent)
2. Test in Standard TESTING first
3. Then test in Premium TESTING
4. Update both build codes

**Phase 3 — Close Component (shared)**
1. Create new 2-node Library Component: `ending` (conversation) + `end` (end)
2. Test in both TESTING flows
3. Update build codes

**Phase 4 — Build code refactor**
1. Remove COMPONENTS functions for nodes now inside Library Components
2. Update parent flow node definitions to reference new multi-node components
3. Run full E2E suite for both Standard and Premium
4. Deploy to production build workflows

---

## Critical Verification Needed Before Phase 1

**⚠️ UNVERIFIED: Nested code-subagent inside a multi-node component**

We confirmed:
- Multi-node conversation components work (✅)
- Nested subagent (referencing another component) inside a component works (✅)
- Code nodes as single-node Library Components work (✅)

We have NOT confirmed:
- A nested subagent referencing a CODE component (validate_phone) works correctly inside a multi-node Library Component
- Whether the `code`, `else_edge`, `speak_during_execution`, `wait_for_result` fields carry through the nested reference
- Whether code execution actually runs when nested 2 levels deep (flow → component → nested subagent → code component)

**This must be verified FIRST with a throwaway test before building any production components.**

---

## Decision Points for Dan

1. **Proceed with this narrower scope?** The API constraints mean we get 3 new multi-node components (not 5-6 as originally planned). The Premium booking path can't be consolidated. Is this still worth doing?

2. **Phase 1 first or skip to build code cleanup?** An alternative approach: instead of multi-node components, just ensure the build code generates subagent references to the existing 12 single-node components (which it already does). The "update once" benefit already exists for the 12 Library Components — the COMPONENTS object in build code is redundant for those nodes.

3. **Timeline:** Do this before launch, or after first clients are live? The migration requires rebuilding all client flows, which is trivial pre-launch (only TESTING agents) but risky post-launch.
