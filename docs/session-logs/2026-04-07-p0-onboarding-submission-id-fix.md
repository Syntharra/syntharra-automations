# 2026-04-07 - P0 n8n onboarding submission_id regression fix

## Problem
Both onboarding workflows crashed at Check Idempotency Insert Code node:
Cannot read properties of undefined (reading submission_id) [line 2]
- Standard: 4Hx7aRdzMl5N0uJP (webhook jotform-hvac-onboarding)
- Premium:  kz1VmwNccunRMEaF (webhook jotform-hvac-premium-onboarding)
Was full-green 2026-04-06. Blocks all new client onboarding.

## Root cause
Not JotForm schema drift. The upstream Parse JotForm Data Code node returns a
flat extractedData object that does NOT forward submission_id. The idempotency
node was reading $input.first().json.body.submission_id - but $input.first().json
IS the parse output (flat, no .body, no submission_id), so .body was undefined
and the read threw.

## Fix
Rewrote both idempotency Code nodes to reach back to the webhook trigger via
$(JotForm Webhook Trigger).first().json and defensively walk .body nesting,
trying submission_id / submissionID / submission keys. Premium uses
$(JotForm Premium Webhook Trigger) (different webhook node name).
Patched via raw REST PUT (n8n SDK validator too strict per prior FAILURE entry).

## Verification
Smoke POST to both webhooks with q4_hvacCompany + submission_id:
- Standard exec 1985 - CLEARED idempotency, failed later at Query Client Agents (STANDARD): Credentials not found
- Premium  exec 1987 - CLEARED idempotency, failed later at Query Client Agents (PREMIUM): Credentials not found

P0 regression RESOLVED. Downstream credential issue is a separate ticket.

## Open follow-ups
- Re-bind Supabase credentials on Query Client Agents (STANDARD + PREMIUM) nodes
- Run shared/e2e-test.py + shared/e2e-test-premium.py on Windows to confirm full-green
- Optional: patch Parse JotForm Data to forward submission_id into extractedData

## Reflection
- Wrong initial hypothesis (JotForm schema drift). The break was inside the n8n
  graph between Parse and Idempotency. Should have traced upstream chain first.
- n8n get_workflow_details returns 200K+ char JSON - patch via scripts, not MCP reads.
- $(NodeName).first().json is the right pattern when upstream normalizer strips fields.
