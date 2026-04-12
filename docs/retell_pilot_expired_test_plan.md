# Retell `pilot_expired` branch — test plan for Dan

> **Status as of 2026-04-11:** TESTING agent is live with the 20-node flow (new `node-pilot-expired` present). Flow version 3 on `conversation_flow_bc8bb3565dbf`. MASTER (`conversation_flow_19684fe03b61`) is UNCHANGED and still on 19 nodes — no client production impact.

## What changed on TESTING

The flow now has an extra node `node-pilot-expired` plus two new edges from `node-greeting`, both pointing at it:

1. **Edge 0 (priority 1):** `type=equation` — fires if `{{pilot_expired}}` equals `"true"`. This is the primary detection path.
2. **Edge 1 (priority 2):** `type=prompt` — fires if the LLM infers pilot expiration from the prompt. This is a belt-and-suspenders fallback in case the equation-type edge doesn't match the way I think it does.
3. **Edge 2 (priority 3):** `type=prompt` — the normal flow edge to `node-identify-call`. Fires when neither of the above hits.

The node itself delivers the apologetic pilot-ended message + a visit-to-reactivate CTA, then transitions to `node-end-call`. Source: `retell-iac/components/pilot_expired_node.json`.

**Important:** I deliberately did NOT pre-set `agent_level_dynamic_variables.pilot_expired='true'` on the TESTING agent. The agent's dynamic variables are empty, so by default callers follow the normal flow (edge 2 → `node-identify-call`). Dan toggles this manually when he wants to test the new branch.

## Why I can't verify this myself

Retell agents can only be tested via real calls (phone or browser-based web call). The audio output has to be heard by a human to confirm the pilot_expired message plays instead of the normal greeting. I can build the flow, PATCH it to TESTING, publish the agent, and verify the JSON is structurally correct — but I cannot make a phone call and listen to the response. That's Dan's 5-minute click test.

## The 5-minute click test

### Option A — Retell dashboard web test (recommended, cheapest)

1. Open the Retell dashboard: https://beta.retellai.com/dashboard
2. Navigate to **Agents** → find `agent_41e9758d8dc956843110e29a25` (Standard TESTING)
3. Click **Edit** → scroll to **Dynamic variables** (agent-level)
4. Add a variable: `pilot_expired` = `true`
5. Save
6. Click **Test Agent** (or **Web Call** — UI wording varies)
7. Say "hello" or just wait for the agent to speak first
8. **Expected:** the AI plays the pilot-expired message ("I apologize — it looks like your pilot trial has ended...") and routes to end call. Does NOT run the normal greeting + identify-call flow.
9. Go back to **Dynamic variables** and REMOVE `pilot_expired` (or set to `false`)
10. Click **Test Agent** again
11. **Expected:** the AI plays the normal greeting and runs the identify-call flow (HVAC intake as usual).

Test passes if both expected behaviors match. Test fails if:
- The pilot_expired message never plays when `pilot_expired=true` is set → the equation edge didn't fire; report back and I'll rewrite the equation to match Retell's actual syntax (it's speculative — the fallback prompt edge should catch it, but worth confirming).
- The pilot_expired message plays even when `pilot_expired` is unset → edge priority is broken, the prompt-type fallback is over-eager. Needs a rewrite.
- The normal flow breaks in any other way → rollback immediately (see below).

### Option B — Real phone call (only if you want to test via Telnyx)

Only works once Telnyx vault keys are in place. Skip for now.

## If the test passes — promote to MASTER

Once Dan confirms TESTING works both ways (normal flow + pilot_expired flow):

```
set -a && source .env.local && set +a
python retell-iac/scripts/promote.py --agent standard_master --built retell-iac/build/hvac-standard.built.json --dry-run
# verify the output shows target flow = conversation_flow_19684fe03b61
python retell-iac/scripts/promote.py --agent standard_master --built retell-iac/build/hvac-standard.built.json
```

Then tag the release:

```
git tag release-hvac-standard-v4-pilot-expired
git push --tags
```

Per `retell-iac/CLAUDE.md`: "Every phase requires explicit Dan approval before advancing. No session auto-promotes." This is why I built TESTING but did not promote.

## If the test fails — rollback

TESTING is isolated from MASTER, so there's no rollback needed at the MASTER level — nothing was promoted.

**To revert TESTING's flow to the pre-change version (19 nodes, no pilot_expired):**

```
git log --oneline -- retell-iac/components/pilot_expired_node.json retell-iac/flows/hvac-standard.template.json
# find the last commit before eee258c (the pilot_expired addition)
git checkout <prior-commit> -- retell-iac/components/pilot_expired_node.json retell-iac/flows/hvac-standard.template.json retell-iac/manifests/hvac-standard.yaml
python retell-iac/scripts/build_agent.py --manifest retell-iac/manifests/hvac-standard.yaml --out retell-iac/build/hvac-standard.built.json
# manually PATCH TESTING with the reverted flow (same pattern used earlier today to push the 20-node version)
git checkout HEAD -- retell-iac/components/pilot_expired_node.json retell-iac/flows/hvac-standard.template.json retell-iac/manifests/hvac-standard.yaml
```

Or simpler: ping me with the failure mode, and I'll iterate on the equation syntax and re-PATCH TESTING until it works.

## Production impact summary

- **MASTER agent (`agent_b46aef9fd327ec60c657b7a30a`):** unchanged. Still 19 nodes. Still on production flow version. Client clones built from MASTER today are unaffected.
- **TESTING agent (`agent_41e9758d8dc956843110e29a25`):** now on 20 nodes, flow version 3. Used only for this test.
- **Existing client clones:** unchanged. They were cloned from MASTER before this change, so they have the pre-pilot_expired 19-node flow. New client clones will also get the 19-node flow until Dan runs `promote.py`.
- **Pilot lifecycle cron (`tools/pilot_lifecycle.py`):** unchanged. It calls `PATCH /update-agent/{id}` to set `pilot_expired='true'` on specific pilot CLONE agents, not on MASTER — so even after promote.py lands, the feature only activates per-pilot when the cron expires them. Normal (non-pilot) clients never see the pilot_expired branch.

## Files involved (for reference)

- `retell-iac/components/pilot_expired_node.json` — the node itself
- `retell-iac/flows/hvac-standard.template.json` — template with the 3 greeting edges and the new node reference
- `retell-iac/manifests/hvac-standard.yaml` — manifest listing `pilot_expired_node` as a component
- `retell-iac/build/hvac-standard.built.json` — latest build output (20 nodes, synced with TESTING version 3)
- `retell-iac/scripts/build_agent.py` — builds the flow JSON from the manifest
- `retell-iac/scripts/promote.py` — the ONLY script allowed to write to MASTER

## Time to test

~5 minutes end-to-end. The dashboard web test is the fastest path.

---

Raise a thumbs-up in Slack or a "go ahead" note here once TESTING is verified and you want me to run `promote.py`. I'll do dry-run first, show the diff, then run for real.
