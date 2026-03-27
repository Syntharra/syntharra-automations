# HVAC Standard Conversation Flow v6

## Nodes (13)

1. greeting_node — fires custom greeting from Jotform
2. identify_call_node — routes to correct node based on call reason (7 finetune sets)
3. nonemergency_leadcapture_node — collects issue, name, number, address
4. verify_emergency_node — confirms emergency, routes to emergency transfer or priority lead (2 finetune sets)
5. callback_node — handles callers returning a missed call (1 finetune set)
6. existing_customer_node — handles existing customers, no lookup, transfer or callback
7. general_questions_node — answers FAQ from company info, uses global prompt pricing rules
8. spam_robocall_node — ends spam calls immediately
9. Transfer Call — cold transfer to client's transfer_phone (q48)
10. Emergency Transfer — cold transfer to emergency_phone (q21), falls back to transfer_phone
11. transfer_failed_node — captures details if either transfer fails
12. Ending — offers further help or closes
13. End Call — ends call warmly

## Transfer Number Logic
- Transfer Call node → transfer_phone (q48) from Jotform, fallback to lead_phone
- Emergency Transfer node → emergency_phone (q21) if provided, otherwise same as transfer_phone
- Both transfer failed paths route to the same transfer_failed_node

## Data Collection Order (Lead Capture)
1. Issue/service description first
2. Full name (first and last)
3. Callback number
4. Address (minimum suburb or ZIP)
5. Additional notes (optional)

## Emergency Flow
1. identify_call routes to verify_emergency
2. verify_emergency confirms: true emergency → Emergency Transfer, not emergency → priority lead capture
3. Emergency Transfer uses emergency_phone (q21) or falls back to transfer_phone (q48)
4. If emergency transfer fails → transfer_failed_node → capture details
