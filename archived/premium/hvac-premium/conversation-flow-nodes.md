# HVAC Premium Conversation Flow v1.0

## Nodes (18)

1. greeting_node — static greeting, routes to identify
2. identify_call_node — routes based on caller intent (10 edges, finetune examples)
3. booking_capture_node — PRIMARY PATH: collects service, name, address, phone, date, time window. Emergency detection active. Pricing rules inline. Fallback to lead capture.
4. confirm_booking_node — reads back all details, confirms, offers further help
5. check_appointment_node — handles "when is my appointment" — cannot look up, takes details for callback
6. reschedule_node — gets name, old date, new date/time, confirms change
7. cancel_appointment_node — confirms cancellation, offers rebook
8. lead_fallback_node — collects standard lead details when booking not possible
9. verify_emergency_node — confirms true emergency vs urgent-but-can-wait (finetune examples)
10. callback_node — returning missed calls, routes to booking if service need
11. existing_customer_node — cannot look up accounts, offers callback or transfer
12. general_questions_node — FAQ from global prompt, routes to booking or transfer
13. spam_robocall_node — ends spam calls
14. Transfer Call — WARM transfer to transfer_phone, whisper summary to human
15. Emergency Transfer — WARM transfer to emergency_phone, whisper emergency brief
16. transfer_failed_node — captures details if transfer fails, offers booking
17. Ending — "anything else?" loops back or closes
18. End Call — ends warmly

## Key Differences from Standard
- Booking is the PRIMARY path (not lead capture)
- Check appointment node for existing booking queries
- Reschedule and cancel appointment nodes
- Lead capture is FALLBACK only (when booking fails)
- 17 post-call analysis fields (vs 3 in standard)
- Notification types: booking_confirmed, reschedule, cancellation, emergency, booking_failed_lead, hot_lead, general_lead, follow_up_required, info_only, spam

## Transfer Numbers
- Transfer Call → transfer_phone (from Jotform), fallback to lead_phone
- Emergency Transfer → emergency_phone (from Jotform), fallback to transfer_phone
- NOTE: Currently using placeholder +18563630633 — gets overwritten by prompt-builder at onboarding

## Data Collection (Booking Capture)
1. Service description
2. Full name (first and last)
3. Service address (with city/suburb)
4. Callback number (read back in groups)
5. Preferred date
6. Preferred time window (morning/afternoon)
