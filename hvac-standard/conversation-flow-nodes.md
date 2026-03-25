# HVAC Standard Conversation Flow

## Nodes

1. greeting_node — fires custom greeting from Jotform
2. identify_call_node — routes to correct node based on call reason
3. nonemergency_leadcapture_node — collects issue, name, number, address
4. verify_emergency_node — confirms emergency and transfers or captures lead
5. callback_node — handles callers returning a missed call
6. existing_customer_node — handles existing customers, no lookup, transfer or callback
7. general_questions_node — answers FAQ from company info
8. spam_robocall_node — ends spam calls immediately
9. Transfer Call — cold transfer to client's transfer number
10. transfer_failed_node — captures details if transfer fails
11. Ending — offers further help or closes
12. End Call — ends call warmly

## Data Collection Order (Lead Capture)
1. Issue/service description first
2. Full name (first and last)
3. Callback number
4. Address (minimum suburb or ZIP)
5. Additional notes (optional)
