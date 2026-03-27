# HVAC Standard Conversation Flow v6.1

## Nodes (13)

1. greeting_node — fires custom greeting from Jotform
2. identify_call_node — routes to correct node based on call reason (7 finetune sets)
3. nonemergency_leadcapture_node — collects issue, name, number, address
4. verify_emergency_node — confirms emergency, routes to emergency transfer or priority lead (2 finetune sets)
5. callback_node — handles callers returning a missed call (1 finetune set, routes to lead capture if new issue)
6. existing_customer_node — handles existing customers, no lookup, transfer or callback
7. general_questions_node — answers FAQ using global prompt pricing rules
8. spam_robocall_node — ends spam calls immediately
9. Transfer Call — WARM transfer to transfer_phone (q48), agent whispers call summary to human
10. Emergency Transfer — WARM transfer to emergency_phone (q21), agent whispers emergency brief to human
11. transfer_failed_node — captures details if either transfer fails
12. Ending — offers further help or closes
13. End Call — ends call warmly

## Transfer Number Logic
- Transfer Call → transfer_phone (q48), fallback to lead_phone
- Emergency Transfer → emergency_phone (q21), fallback to transfer_phone

## Warm Transfer Whisper
- General: "Hi, I have [name] on the line calling about [issue]. They seem [calm/frustrated/urgent]."
- Emergency: "Emergency call from [name] at [address]. They have [no heat/gas leak/flooding]. Connecting them now."
- The AI agent speaks this whisper to the human who answers BEFORE connecting the caller

## Data Collection Order (Lead Capture)
1. Issue/service description
2. Full name (first and last)
3. Callback number
4. Address (minimum suburb or ZIP)
5. Additional notes (optional)

## Emergency Flow
1. identify_call routes to verify_emergency
2. verify_emergency confirms: true emergency → Emergency Transfer, not emergency → priority lead capture
3. Emergency Transfer warm-whispers to the emergency team, then connects caller
4. If transfer fails → capture name + number → close
