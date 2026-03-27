# HVAC Premium Conversation Flow v1

## Nodes (18)

1. **greeting_node** — Custom greeting from Jotform
2. **identify_call_node** — Routes to correct node based on call reason (10 edges, 8 finetune sets)
   - → booking_capture (service/repair/maintenance/quote/estimate/installation)
   - → check_appointment (check existing appointment)
   - → reschedule (change appointment)
   - → cancel_appointment (cancel booking)
   - → verify_emergency (emergency/urgent)
   - → callback (returning missed call)
   - → existing_customer (invoice/technician/job status)
   - → general_questions (services/hours/pricing)
   - → transfer_call (wants real person)
   - → spam_robocall (automated/silence)
3. **booking_capture_node** — PRIMARY PATH. Collects: service needed, full name, callback number, service address, preferred date, preferred time window. Routes to check_availability or fallback.
4. **confirm_booking_node** — Reads back ALL booking details, confirms with caller, creates booking via tool call
5. **check_appointment_node** — Caller checking existing appointment. Collects name, looks up, provides status or routes to reschedule/cancel
6. **reschedule_node** — Reschedule flow: verify name + original date, collect new date/time, check availability, confirm
7. **cancel_appointment_node** — Cancel flow: verify name + date, confirm cancellation, offer to rebook
8. **lead_fallback_node** — FALLBACK when booking not possible. Collects: service, name, phone, address, notes. Standard lead capture.
9. **verify_emergency_node** — Confirms emergency. True emergency → Emergency Transfer. Urgent but not emergency → priority booking.
10. **callback_node** — Returning missed call. Collects name, confirms number. If new need → booking_capture.
11. **existing_customer_node** — Existing customer enquiry. No lookup. Offer callback or transfer.
12. **general_questions_node** — FAQ from global prompt. After answering, offers booking.
13. **spam_robocall_node** — Ends spam calls immediately.
14. **Transfer Call** — WARM transfer with agent whisper summarising the call.
15. **Emergency Transfer** — WARM transfer with urgent whisper brief.
16. **transfer_failed_node** — Captures details if transfer fails. Routes to booking or ending.
17. **Ending** — "Is there anything else I can help you with?" Routes to end or back to identify.
18. **End Call** — Ends call warmly.

## Key Differences from Standard
- Booking is the PRIMARY path (Standard only does lead capture)
- 5 extra nodes: booking_capture, confirm_booking, check_appointment, reschedule, cancel_appointment
- Lead capture is a FALLBACK (calendar error, caller declines booking, no slots)
- Identify node has 10 edges (Standard has 7)
- Post-call analysis includes booking fields
- Call processor has 10 notification types (Standard has 2: lead/non-lead)

## Transfer Number Logic
- Transfer Call → transfer_phone (from Jotform), fallback to lead_phone
- Emergency Transfer → emergency_phone (from Jotform), fallback to transfer_phone

## Data Collection Order (Booking)
1. Service needed
2. Full name (first and last)
3. Callback number (read back)
4. Service address (confirm back)
5. Preferred date
6. Preferred time window (morning/afternoon)

## Data Collection Order (Lead Fallback)
1. Service needed
2. Full name
3. Callback number
4. Service address
5. Additional notes
