# Syntharra HVAC Standard — Key IDs
Last updated: 2026-03-27 03:03 UTC

## Retell
- Agent: agent_d180e1bd5b9b724c8f616a0415 (Arctic Breeze HVAC [HVAC-STD])
- Demo Sophie: agent_2723c07c83f65c71afd06e1d50
- Demo Jake (Male): agent_b9d169e5290c609a8734e0bb45
- LIVE Flow: conversation_flow_ed1ff4a600af (12 nodes, warm transfer, version 8)

## Phone Numbers
- +18129944371 → Arctic Breeze HVAC [HVAC-STD]
- +12292672271 → Demo Sophie

## n8n Workflows
- Call Processor: OyDCyiOjG0twguXq
- Onboarding: k0KeQxWb3j3BbQEk
- Stripe: ydzfhitWiF5wNzEy
- Transcript Generator: dHO8O0QHBZJyzytn
- Nightly Backup: EAHgqAfQoCDumvPU
- Scenario Runner v4 (main): 94QmMVGdEDl2S9MF
- Scenario Sub-workflow: rlf1dHVcTlzUbPX7

## Supabase
- Project: hgheyqwnrcvwtgngqdnq.supabase.co
- Table: hvac_standard_agent
- Table: hvac_call_log

## Telnyx
- SMS From Number: +19294510009
- Messaging Profile: 40019d2a-ee8f-4ac7-b105-02469f10820e

## Stripe (TEST MODE)
- Webhook: we_1TEJXzECS71NQsk8eOMIs8JE
- Std Monthly: price_1TDckaECS71NQsk8DdNsWy1o
- Std Annual: price_1TDckiECS71NQsk8fqDio8pw
- Std Setup: price_1TEKKrECS71NQsk8Mw3Z8CoC
- Prem Monthly: price_1TDclGECS71NQsk8OoLoMV0q
- Prem Annual: price_1TDclPECS71NQsk8S9bAPGoJ
- Prem Setup: price_1TEKKvECS71NQsk8vWGjHLUP

## Jotform
- Standard Form: 260795139953066
- Webhook: https://syntharra.app.n8n.cloud/webhook/jotform-hvac-onboarding

## Session fixes applied (2026-03-27)
- isHtml fixed on all 3 onboarding email nodes (Email Summary to Dan, Error Notification, Send Setup Instructions)
- Telnyx phone purchase nodes enabled and configured (replaced Twilio placeholders)
- Onboarding field mapping fixed (body.body double-nesting)
- Retell agent + flow published
- Phone numbers assigned: +18129944371 → Arctic Breeze, +12292672271 → Demo
- Scenario runner v4 created with sub-workflow architecture (ID: 94QmMVGdEDl2S9MF)
- Scenario sub-workflow created (ID: rlf1dHVcTlzUbPX7) — loop fix still needed

## Known pending items
- Scenario runner loop iteration (Run Single Scenario node not firing — wiring issue)
- Onboarding email investigation (execution shows success but Daniel not receiving)
- Phone numbers need Retell UI verification
- Switch Stripe to LIVE mode at launch
- Change internal emails daniel@ → support@ before launch
- SMS nodes pending Telnyx 10DLC registration
