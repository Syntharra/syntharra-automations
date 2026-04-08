// ============================================================
// Build Retell Premium Prompt v1 â€” Booking + CRM Edition
// ============================================================
// Premium differences from Standard:
//   - Booking-first primary path (date, time, job type, duration)
//   - Calendar integration awareness (Google Calendar / Calendly / Jobber / ServiceTitan / Housecall Pro / custom)
//   - CRM push awareness (Jobber, ServiceTitan, Housecall Pro, custom)
//   - Reschedule and cancel appointment nodes
//   - Lead capture as fallback only (calendar unavailable / caller declines booking)
//   - 15-node conversation flow
//   - post_call_analysis_data includes booking_attempted, booking_success, appointment_date, appointment_time, job_type_booked
// ============================================================

const data = $input.first().json;

// ============================================================
// STANDARD FIELDS (inherited from standard)
// ============================================================
const companyName        = data.company_name || 'HVAC Company';
const companyPhone       = data.main_phone || '';
const companyWebsite     = data.website || '';
const yearsInBusiness    = data.years_in_business || '';
const agentName          = data.agent_name || `${companyName} Receptionist`;
const voiceGender        = (data.voice_gender || 'female').toLowerCase();
const servicesOffered    = data.services_offered || '';
const brandsServiced     = data.brands_serviced || '';
const serviceArea        = data.service_area || '';
const serviceAreaRadius  = data.service_area_radius || '';
const businessHours      = data.business_hours || '';
const responseTime       = data.response_time || '';
const emergency247       = data.emergency_service || 'No';
const emergencyPhone     = data.emergency_phone || '';
const afterHoursBehavior = data.after_hours_behavior || '';
const freeEstimates      = data.free_estimates || 'Yes - always free';
const diagnosticFee      = data.diagnostic_fee || '';
const pricingPolicy      = data.pricing_policy || 'We provide free quotes on-site';
const standardFees       = data.standard_fees || '';
const financingAvailable = data.financing_available || 'No';
const financingDetails   = data.financing_details || '';
const warranty           = data.warranty || 'Yes';
const warrantyDetails    = data.warranty_details || '';
const licensedInsured    = data.licensed_insured || 'Yes';
const certifications     = data.certifications || '';
const paymentMethods     = data.payment_methods || '';
const maintenancePlans   = data.maintenance_plans || 'No';
const leadContactMethod  = data.lead_contact_method || 'Both';
const leadPhone          = data.lead_phone || '';
const leadEmail          = data.lead_email || '';
const customGreeting     = data.custom_greeting || '';
const companyTagline     = data.company_tagline || '';
const transferPhone      = data.transfer_phone || '';
const transferTriggers   = data.transfer_triggers || 'Caller requests a live person, Emergency situation';
const transferBehavior   = data.transfer_behavior || 'Try once - take message if no answer';
const uniqueSellingPts   = data.unique_selling_points || '';
const currentPromotion   = data.current_promotion || '';
const seasonalServices   = data.seasonal_services || '';
const additionalNotes    = data.additional_info || '';
const companyInfoBlock   = data.companyInfoBlock || '';
const ownerName          = data.owner_name || '';
const googleReviewRating = data.google_review_rating || '';
const googleReviewCount  = data.google_review_count || '';
const doNotService       = data.do_not_service || '';
const membershipProgram  = data.membership_program || '';
const industryType       = data.industry_type || 'HVAC';
const afterHoursTransfer = data.after_hours_transfer || 'all';

// ============================================================
// PREMIUM FIELDS
// ============================================================
const crmPlatform            = data.crm_platform || '';           // Jobber, ServiceTitan, Housecall Pro, custom, none
const calendarPlatform       = data.calendar_platform || '';      // Google Calendar, Calendly, Jobber, ServiceTitan, Housecall Pro, custom
const bookingSlotDuration    = data.booking_slot_duration || '60'; // minutes per job slot
const bookingLeadTime        = data.booking_lead_time || '2';     // minimum hours before booking
const bookableJobTypes       = data.bookable_job_types || servicesOffered; // which job types can be booked online
const bookingConfirmMethod   = data.booking_confirm_method || 'email'; // email, sms, both
const calendarWebhookUrl     = data.calendar_webhook_url || '';   // n8n webhook to check/create calendar events
const crmWebhookUrl          = data.crm_webhook_url || '';        // n8n webhook to push contact/job to CRM
const availableTimeSlots     = data.available_time_slots || 'Morning (8am-12pm), Afternoon (12pm-5pm)'; // general windows
const bookingBufferMinutes   = data.booking_buffer_minutes || '30'; // buffer between jobs

// ============================================================
// VOICE SELECTION
// ============================================================
const voiceMap = { female: 'retell-Sloane', male: 'retell-Nico' };
const voiceId = voiceMap[voiceGender] || 'retell-Sloane';

// ============================================================
// TRANSFER NUMBERS
// ============================================================
const rawTransferPhone = transferPhone || leadPhone;
const transferNumber = rawTransferPhone
  ? (rawTransferPhone.startsWith('+') ? rawTransferPhone : `+1${rawTransferPhone.replace(/\D/g, '')}`)
  : '+10000000000';

const rawEmergencyPhone = emergencyPhone || rawTransferPhone;
const emergencyTransferNumber = rawEmergencyPhone
  ? (rawEmergencyPhone.startsWith('+') ? rawEmergencyPhone : `+1${rawEmergencyPhone.replace(/\D/g, '')}`)
  : transferNumber;

const emergencyDisplayNumber = emergencyPhone || transferPhone || companyPhone || '';

// ============================================================
// PRICING INSTRUCTIONS
// ============================================================
let shareableFees = '';
if (diagnosticFee) shareableFees += `\n- Diagnostic/Service Call Fee: ${diagnosticFee} (applied to repair if customer proceeds)`;
if (standardFees) shareableFees += `\n- Additional Set Fees: ${standardFees}`;

let pricingInstructions = '';
if (pricingPolicy === 'We provide free quotes on-site') {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "We provide free on-site quotes so our team can give you an accurate price based on your specific situation. Let me get a time booked for you."\n- NEVER provide general service, repair, or installation prices.\n- NEVER guess or estimate costs for any service.`;
  if (shareableFees) pricingInstructions += `\n\nThe ONLY fees you may mention:${shareableFees}\n\nOnly mention these if the caller specifically asks. Do NOT volunteer pricing.`;
} else if (pricingPolicy === 'We charge a diagnostic fee then quote') {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "We do have a ${diagnosticFee || 'service call'} fee for the initial visit, which gets applied to the repair if you choose to move forward. Our technician will give you a full quote once they've assessed the situation."\n- NEVER provide general repair or installation prices.`;
  if (shareableFees) pricingInstructions += `\n\nSet fees you may share when asked:${shareableFees}`;
} else {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "Our team will go over all the pricing with you at the appointment so you get the most accurate information."\n- NEVER provide any prices, estimates, or cost ranges over the phone.`;
  if (shareableFees) pricingInstructions += `\n\nException, the ONLY fees you may mention:${shareableFees}`;
}

// ============================================================
// TRANSFER RULES
// ============================================================
const triggerList = transferTriggers.split(',').map(t => t.trim()).filter(Boolean);
let transferRules = `## CALL TRANSFER PROTOCOL\n\n`;
transferRules += `General transfer destination: ${transferNumber}\n`;
transferRules += `Emergency transfer destination: ${emergencyTransferNumber}\n`;
transferRules += `Transfer behavior: ${transferBehavior}\n\n`;
transferRules += `Transfer the call ONLY when one of these conditions is met:\n`;
triggerList.forEach((t, i) => { transferRules += `${i + 1}. ${t}\n`; });
transferRules += `\nFor ALL other situations, attempt to book an appointment or collect caller information.`;
if (transferBehavior === 'Always take a message - never transfer') {
  transferRules += `\n\nIMPORTANT: NEVER transfer calls. Always book an appointment or collect caller information.`;
}
if (ownerName) {
  transferRules += `\n\n### Owner/Manager Reference\nIf a caller asks to speak with the owner or manager, their name is ${ownerName}. Say: "${ownerName} isn't available right now, but I can book you in or take a message and have them call you back."`;
}

// ============================================================
// BOOKING SYSTEM SECTION
// ============================================================
const bookingSection = `## BOOKING SYSTEM\n\nYou have the ability to book appointments directly during this call. This is your PRIMARY function for service and repair calls â€” always attempt to book before offering a callback.\n\nCalendar platform: ${calendarPlatform || 'integrated calendar'}\n${crmPlatform ? `CRM platform: ${crmPlatform}` : ''}\nAvailable time windows: ${availableTimeSlots}\nJob slot duration: ${bookingSlotDuration} minutes\nMinimum booking lead time: ${bookingLeadTime} hours\n\n### Bookable job types:\n${bookableJobTypes}\n\n### Booking flow:\n1. Identify what service is needed and confirm it is bookable\n2. Ask for their preferred date: "What date works best for you?"\n3. Ask for preferred time window: "And would morning or afternoon suit you better?"\n4. Confirm details: name, address, callback number, job type\n5. Check availability for that slot (tool call)\n6. If available: confirm booking and provide reference\n7. If unavailable: offer next 2 available slots\n8. Always confirm the booking back: date, time window, what the team will be coming for\n\n### After booking:\n- Confirmation will be sent via ${bookingConfirmMethod}\n- Say: "You'll receive a confirmation shortly. Is there anything else I can help with?"\n\n### Booking fallback (only if booking unavailable or caller declines):\n- Collect standard lead capture details\n- Say: "No problem, I'll pass your details to the team and they'll call you back to confirm a time."\n\n### Reschedule requests:\n- Verify name and original appointment date\n- Collect new preferred date/time\n- Check availability and confirm new slot\n\n### Cancellation requests:\n- Verify name and appointment date\n- Confirm cancellation\n- Offer to rebook: "Would you like to book a new time while we're on the call?"`;

// ============================================================
// DO NOT SERVICE
// ============================================================
let doNotServiceSection = '';
if (doNotService) {
  doNotServiceSection = `\n\n\n## SERVICES WE DO NOT PROVIDE\n\nThe following are outside our scope:\n${doNotService}\n\nIf a caller requests any of these: "I appreciate you reaching out, but unfortunately that's not something we service. I'd recommend reaching out to a specialist for that. Is there anything else I can help you with?"\n\nDo NOT attempt to book or collect lead information for out-of-scope requests.\n`;
}

// ============================================================
// PROMOTIONS
// ============================================================
let promotionsSection = '';
if (currentPromotion || seasonalServices || uniqueSellingPts || (googleReviewRating && googleReviewRating !== 'Not listed on Google')) {
  promotionsSection = `\n\n\n## PROMOTIONS & VALUE PROPOSITIONS\n\n`;
  if (googleReviewRating && googleReviewRating !== 'Not listed on Google') {
    let reviewLine = `We have a ${googleReviewRating}-star rating on Google`;
    if (googleReviewCount && googleReviewCount !== 'Not listed on Google') reviewLine += ` with ${googleReviewCount.toLowerCase().replace('under ', 'nearly ')} reviews`;
    promotionsSection += `### Google Reviews\n${reviewLine}.\nMention this naturally when a caller is comparing options.\n\n`;
  }
  if (currentPromotion) promotionsSection += `### Current Promotion\n${currentPromotion}\n\n`;
  if (uniqueSellingPts) promotionsSection += `### Why Choose ${companyName}\n${uniqueSellingPts}\n\n`;
  if (seasonalServices) promotionsSection += `### Seasonal Services\n${seasonalServices}\n\n`;
}

// ============================================================
// PAYMENT SECTION
// ============================================================
let paymentSection = '';
if (paymentMethods) {
  paymentSection = `\nWhen callers ask about payment methods:\n- Say: "We accept ${paymentMethods}."`;
  if (financingAvailable === 'Yes' && financingDetails) paymentSection += `\n- If they ask about financing: "Yes, we offer financing, ${financingDetails}."`;
  else if (financingAvailable === 'Yes') paymentSection += `\n- If they ask about financing: "Yes, we do offer financing options. Our team can go over the details with you."`;
  if (maintenancePlans !== 'No') {
    let maintLine = `\n- If they ask about maintenance plans: "Yes, we do offer maintenance plans`;
    if (membershipProgram) maintLine += `, our ${membershipProgram} program`;
    maintLine += `. Our team can go over the details and pricing with you."`;
    paymentSection += maintLine;
  }
}

// ============================================================
// AFTER HOURS
// ============================================================
let afterHoursSection = '';
if (businessHours && afterHoursTransfer !== 'all') {
  afterHoursSection = `\n\n\n## AFTER-HOURS BEHAVIOR\n\nBusiness hours: ${businessHours}\n`;
  if (afterHoursTransfer === 'emergency_only') {
    afterHoursSection += `\nOutside business hours:\n- Do NOT transfer regular calls. Attempt to book a next-available slot or collect details.\n- Emergency calls CAN still be transferred.\n`;
  } else if (afterHoursTransfer === 'never') {
    afterHoursSection += `\nOutside business hours:\n- Do NOT transfer ANY calls.\n- Attempt to book a next-available slot or collect details and mark as urgent.\n`;
  }
}

// ============================================================
// GLOBAL PROMPT
// ============================================================
let globalPrompt = `## ROLE\nYou are ${agentName}, a virtual AI receptionist for ${companyName}.${companyTagline ? ' ' + companyTagline + '.' : ''}\nYou are warm, professional and concise. Speak naturally, one topic at a time. Address callers by first name once you have it.\n\nYou have full booking capability. For service and repair calls, your primary job is to get an appointment booked â€” not just take a message.\n\nIf asked if you are a real person: "I'm a virtual assistant, but I can book your appointment right now."\n\n## STYLE\n- One question at a time, always wait for the answer\n- Match the caller's energy. Calm if calm, reassuring if stressed\n- Never rush. Be patient with elderly callers\n- Vary your language naturally\n- Do not over-apologise. One brief apology per issue is enough. Move quickly to solving the problem rather than dwelling on the inconvenience\n- If the caller speaks a language other than English, switch to their language completely. Mirror their language for all responses, confirmations, closings, and follow-up questions. Your greeting can start in English, but once you detect their language, continue entirely in that language for the rest of the call\n\n## CONFIRMING DETAILS\nSlow down when collecting contact info. Confirm each piece back before moving on.\n- Phone: read back in groups "512, 555, 0192, is that right?"\n- Name: spell uncommon names letter by letter\n- Address: confirm street and suburb "123 Main Street, Austin, is that right?"\n- Email: read back slowly using dot, at, dash\n- Date/Time: always confirm back "So that's Thursday the 15th, afternoon â€” correct?"\n- If anything is unclear, ask them to spell it. Never guess.\n\n## TRANSCRIPTION\nIf you cannot understand something: "I'm sorry, I didn't quite catch that, could you say that again?" Never guess at names, addresses or emails.\n\n## COMPANY INFORMATION\n\n{{COMPANY_INFO_BLOCK}}\n\nUse the information above to answer any company-specific questions. If a question is NOT covered above, do NOT guess. Say: "That's a great question, one of our team members will be able to answer that when they call you back."\n\n\n\n## PRICING & QUOTING\n\n${pricingInstructions}\n\n\n\n${bookingSection}\n\n\n\n${transferRules}\n\n\n\n## PAYMENT & FINANCING\n${paymentSection || `When callers ask about payment methods:\n- Say: "Our team can go over payment options with you at the appointment."`}\n\n\n${promotionsSection}\n${doNotServiceSection}${afterHoursSection}\n## VOICEMAIL DETECTION\n\nIf you hear a beep, a voicemail greeting, or an automated message system:\n- Do NOT leave a message\n- End the call immediately and silently\n- This is not a real caller\n\n\n\n## CRITICAL RULES â€” NEVER BREAK THESE\n\n- NEVER ask more than one question at a time\n- NEVER make up prices, estimates, or timeframes unless explicitly listed in company information\n- NEVER diagnose ${industryType} problems or recommend specific repairs\n- NEVER promise availability without checking the calendar\n- NEVER guess answers to company-specific questions not found in company information\n- NEVER continue a conversation with obvious spam or robocalls, end politely\n- NEVER transfer a call unless it matches a transfer trigger or is a confirmed emergency\n- ALWAYS attempt to book an appointment before offering a callback\n- ALWAYS confirm booking details back to the caller before ending the call\n- ALWAYS be warm, calm, and professional regardless of caller frustration\n- ALWAYS try to understand what the caller means even if unclear\n- NEVER apologise more than once in the same call. One sincere acknowledgment is enough, then move to solving the problem\n\n\n\n## IF CALLER IS RELUCTANT TO SHARE INFORMATION\n\n"I completely understand, this information simply helps our team prepare for your visit. We never share your details with third parties."\n\n\n\n## ERROR HANDLING\n\n### Didn't hear or understand:\n"I apologise, I didn't quite catch that, could you repeat that for me?"\n\n### Calendar unavailable:\n"I'm having a little trouble with the booking system right now. Let me take your details and our team will call you back to confirm a time very shortly."\n\n### Don't know the answer:\n"That's a great question. I want to make sure you get the right answer, can I grab your details so someone from our team can call you back?"\n\n\n\n## SPECIAL SCENARIOS\n\n### Angry or Upset Callers\n1. Stay calm and lower your tone slightly\n2. Acknowledge: "I can hear how frustrated you are and I sincerely apologise for that."\n3. Redirect: "Let me get an appointment booked for you right now and get this sorted."\n4. If abuse continues: "I do want to help you, but I need us to work together respectfully. How can I best assist you today?"\n\n### Silent Callers\n- After 3 seconds: "Hello, are you there?"\n- After 5 more seconds: "I'm having trouble hearing you, can you hear me okay?"\n- If no response: end the call politely\n\n### Threats or Safety Concerns\nStay calm, do not engage or argue. Note any relevant details and flag the call immediately for human review.\n\n\n\n## CAPTURING DETAILS\nWhen collecting any detail that could be misheard, slow down noticeably.\n- Phone numbers: read back in groups, "512, 555, 0192, is that right?"\n- Emails: spell each part, "J-O-H-N dot S-M-I-T-H at gmail dot com, correct?"\n- Unusual street names: ask them to spell it out\n- Names: always get first and last name, confirm spelling for uncommon names\n- Appointment times: always read back day and time window together`;

// ============================================================
// BUILD GREETING
// ============================================================
const greetingText = customGreeting
  ? customGreeting
  : `Hello this is ${agentName} from ${companyName}`;

// ============================================================
// BUILD CONVERSATION FLOW (15 NODES)
// ============================================================
const conversationFlow = {
  // â”€â”€ TOOLS (custom functions for calendar/CRM integration) â”€â”€
  tools: [
    {
      type: "custom",
      name: "check_availability",
      tool_id: "tool_check_availability",
      description: "Check calendar availability for a given date and time window. Call this when the caller wants to book an appointment and you need to verify the slot is open.",
      url: "https://n8n.syntharra.com/webhook/retell-integration-dispatch",
      method: "POST",
      parameters: {
        type: "object",
        required: ["action", "date", "time_window"],
        properties: {
          action: { type: "string", const: "check_availability" },
          date: { type: "string", description: "The requested date in YYYY-MM-DD format" },
          time_window: { type: "string", description: "morning or afternoon" }
        }
      },
      speak_during_execution: true,
      speak_during_execution_instruction: { type: "static_text", text: "Let me just check that for you now." },
      wait_for_result: true,
      timeout_ms: 30000
    },
    {
      type: "custom",
      name: "create_booking",
      tool_id: "tool_create_booking",
      description: "Create an appointment booking in the calendar and CRM. Call this after the caller confirms all booking details.",
      url: "https://n8n.syntharra.com/webhook/retell-integration-dispatch",
      method: "POST",
      parameters: {
        type: "object",
        required: ["action", "date", "time_window", "caller_name", "caller_phone", "caller_address", "job_type"],
        properties: {
          action: { type: "string", const: "create_booking" },
          date: { type: "string", description: "Appointment date YYYY-MM-DD" },
          time_window: { type: "string", description: "morning or afternoon" },
          caller_name: { type: "string", description: "Full name of the caller" },
          caller_phone: { type: "string", description: "Callback phone number" },
          caller_address: { type: "string", description: "Service address" },
          job_type: { type: "string", description: "Type of service needed" }
        }
      },
      speak_during_execution: true,
      speak_during_execution_instruction: { type: "static_text", text: "Perfect, let me book that in for you now." },
      wait_for_result: true,
      timeout_ms: 30000
    },
    {
      type: "custom",
      name: "reschedule_booking",
      tool_id: "tool_reschedule",
      description: "Reschedule an existing appointment to a new date and time.",
      url: "https://n8n.syntharra.com/webhook/retell-integration-dispatch",
      method: "POST",
      parameters: {
        type: "object",
        required: ["action", "new_date", "new_time_window"],
        properties: {
          action: { type: "string", const: "reschedule_booking" },
          caller_name: { type: "string", description: "Name of the caller" },
          original_date: { type: "string", description: "Original appointment date" },
          new_date: { type: "string", description: "New date YYYY-MM-DD" },
          new_time_window: { type: "string", description: "morning or afternoon" }
        }
      },
      speak_during_execution: true,
      speak_during_execution_instruction: { type: "static_text", text: "Let me update that for you now." },
      wait_for_result: true,
      timeout_ms: 30000
    },
    {
      type: "custom",
      name: "cancel_booking",
      tool_id: "tool_cancel",
      description: "Cancel an existing appointment.",
      url: "https://n8n.syntharra.com/webhook/retell-integration-dispatch",
      method: "POST",
      parameters: {
        type: "object",
        required: ["action", "caller_name"],
        properties: {
          action: { type: "string", const: "cancel_booking" },
          caller_name: { type: "string", description: "Name of the caller" },
          appointment_date: { type: "string", description: "Date of the appointment to cancel" }
        }
      },
      speak_during_execution: true,
      speak_during_execution_instruction: { type: "static_text", text: "Let me cancel that for you now." },
      wait_for_result: true,
      timeout_ms: 30000
    }
  ],
  name: `${companyName} - ${industryType} Premium Receptionist Flow`,
  start_speaker: "agent",
  model_choice: { type: "cascading", model: "gpt-4.1", high_priority: false },
  global_prompt: globalPrompt.replace("{{COMPANY_INFO_BLOCK}}", companyInfoBlock),
  tool_call_strict_mode: true,
  knowledge_base_ids: [],
  kb_config: { top_k: 3, filter_score: 0.6 },
  flex_mode: false,
  is_transfer_cf: false,
  nodes: [
    // â”€â”€ NODE 1: Greeting â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-greeting", name: "greeting_node", type: "conversation",
      instruction: { type: "static_text", text: greetingText },
      edges: [{ id: "edge-greeting-to-identify", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 558, y: 462 }
    },

    // â”€â”€ NODE 2: Identify Call â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-identify-call", name: "identify_call_node", type: "conversation", start_speaker: "agent",
      instruction: { type: "prompt", text: "Listen and identify the reason for the call. Route to the correct node immediately without asking unnecessary questions." },
      edges: [
        { id: "edge-to-booking", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Repair, service, maintenance, tune-up, inspection, quote, estimate, installation, replacement, new system â€” any new service request that can be booked" } },
        { id: "edge-to-reschedule", destination_node_id: "node-reschedule", transition_condition: { type: "prompt", prompt: "Reschedule, change appointment, move appointment, different time" } },
        { id: "edge-to-cancel", destination_node_id: "node-cancel-appointment", transition_condition: { type: "prompt", prompt: "Cancel appointment, cancel booking, no longer need the appointment" } },
        { id: "edge-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency, urgent, no cooling, no heat, water leak, burning smell, gas smell" } },
        { id: "edge-to-callback", destination_node_id: "node-callback", transition_condition: { type: "prompt", prompt: "Returning a missed call, got a call from this number, calling back" } },
        { id: "edge-to-existing-customer", destination_node_id: "node-existing-customer", transition_condition: { type: "prompt", prompt: "Existing customer, question about appointment, invoice, technician, job status" } },
        { id: "edge-to-general-questions", destination_node_id: "node-general-questions", transition_condition: { type: "prompt", prompt: "General question about services, hours, pricing, area, credentials" } },
        { id: "edge-to-transfer-live", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Wants to speak to a real person, manager, owner, or specific person" } },
        { id: "edge-to-spam", destination_node_id: "node-spam-robocall", transition_condition: { type: "prompt", prompt: "Robocall, spam, automated message, silence after greeting" } }
      ],
      finetune_transition_examples: [
        { id: "fe-booking-service", destination_node_id: "node-booking-capture", transcript: [{ role: "user", content: "My AC isn't working\nI need a repair\nI want to book a service\nCan someone come out\nI need a tune-up\nI want to schedule maintenance\nI need an installation quote\nI want to get my system checked" }, { role: "agent", content: "I can book that for you right now" }] },
        { id: "fe-reschedule", destination_node_id: "node-reschedule", transcript: [{ role: "user", content: "I need to reschedule my appointment\nCan I move my booking\nI need a different time\nCan we change my appointment" }] },
        { id: "fe-cancel", destination_node_id: "node-cancel-appointment", transcript: [{ role: "user", content: "I want to cancel my appointment\nPlease cancel my booking\nI don't need the appointment anymore\nCancel my service" }] },
        { id: "fe-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "no cooling\nno heating\nsystem not working\nwater leaking\nburning smell\nI smell gas\nurgent repair" }] },
        { id: "fe-callback", destination_node_id: "node-callback", transcript: [{ role: "user", content: "I missed a call from this number\nSomeone called me from here\nI am calling back\nReturning your call" }] },
        { id: "fe-existing", destination_node_id: "node-existing-customer", transcript: [{ role: "user", content: "calling about my appointment\nwhere is the technician\nquestion about my invoice\ncalling about my quote" }] },
        { id: "fe-transfer-live", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "Let me speak to someone\nI want to talk to a real person\nCan I speak to a human\nI want to talk to the manager" }] },
        { id: "fe-spam", destination_node_id: "node-spam-robocall", transcript: [{ role: "user", content: "Hello\nHello\nHello" }] }
      ],
      display_position: { x: 1110, y: 366 }
    },


    // NODE 2b: Call Style Detector (code node)
    {
      id: "node-call-style-detector", name: "call_style_detector", type: "code",
      code: `const turns = (typeof metadata !== 'undefined' && metadata && metadata.transcript) ? metadata.transcript : [];
const callerTurns = turns.filter(t => t.role === 'user');
const callerText = callerTurns.map(t => (t.content || '')).join(' ').toLowerCase();
const turnCount = callerTurns.length;
const totalWords = callerText.split(/\\s+/).filter(Boolean).length;
let note = '';
if (/hate.*(ai|robot|bot)|another robot|real person|actual person/.test(callerText)) {
  note = 'CALLER STYLE - Anti-AI: Say ONCE warmly: Totally fair, I will make this quick and get you sorted. Execute perfectly. Never mention being AI again.';
} else if (/pardon|say that again|could you repeat|speak slowly|i forgot|where was i/.test(callerText)) {
  note = 'CALLER STYLE - Elderly or confused: Slow your pace. Very short sentences. Confirm each piece before moving on. Re-anchor if lost: No problem, we were just getting your [last item].';
} else if (/please hurry|my dog|elderly parent|heart condition|dangerous|please help/.test(callerText)) {
  note = 'CALLER STYLE - Distressed: Open with: I am so sorry, let us get this sorted right now. Flag URGENT in team handoff. Move efficiently but warmly.';
} else if (/funny (story|thing|how)|reminds me|speaking of|my neighbor|my kids|by the way|anyway,|so yeah|right\\?/.test(callerText) || (turnCount >= 2 && totalWords > 45 && !/refrigerant|seer|tonnage|compressor|capacitor/.test(callerText))) {
  note = 'CALLER STYLE - Chatty caller going off on tangents. CRITICAL RULE: After EVERY caller turn, respond with ONLY the next question. No affirmations, no social comments, no echoing. Just ask the next required question immediately.';
} else if (/refrigerant|seer|tonnage|compressor|subcooling|superheat|short cycling|capacitor|evaporator/.test(callerText)) {
  note = 'CALLER STYLE - Technical expert: Acknowledge FIRST: Sounds like you know your system well, our technician will appreciate that when they come out. Then capture info. NEVER confirm their diagnosis. When closing say: Our technician will assess everything on-site.';
} else if (callerTurns.some(t => (t.content || '').includes('...') || ((t.content || '').trim().length < 10 && (t.content || '').trim().length > 0)) && turnCount >= 2) {
  note = 'CALLER STYLE - Unclear speech: Ask for each missing piece explicitly: I caught [X], could you give me the rest? NEVER guess or complete partial information. Phonetic readback for numbers.';
} else if (/hold on|one sec|sorry.*kids|sorry.*noise|hang on|be right back|just a (sec|moment|minute)/.test(callerText)) {
  note = 'CALLER STYLE - Distracted: Be patient with every interruption. Each time they return, re-anchor: No problem, so we were just getting your [last item we were on].';
} else if (turnCount >= 2 && callerTurns.every(t => (t.content || '').split(/\\s+/).filter(Boolean).length <= 5)) {
  note = 'CALLER STYLE - Brief answers: Accept every short answer without asking for more. Match their brevity. Confirm each one and move straight to next question.';
}
return { caller_style_note: note };`,
      speak_during_execution: false,
      wait_for_result: true,
      edges: [],
      else_edge: { id: "edge-premium-style-else", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Else" } },
      display_position: { x: 1386, y: 726 }
    },


    // â”€â”€ NODE 3: Booking Capture â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-booking-capture", name: "booking_capture_node", type: "conversation",
      instruction: { type: "prompt", text: `You are booking an appointment. Collect the following in order, one question at a time:\n\n1. What service is needed? If not already stated, ask: "What can we help you with today?" Let them describe fully.\n\n2. Full name (first and last). If first name only, ask for last name. Confirm spelling for uncommon names.\n\n3. Service address. Confirm back what you heard. Ask for city/suburb if not given.\n\n4. Best callback number. Read back in groups: "512, 555, 0192 â€” is that right?"\n\n5. Email address (optional but encouraged). Ask: \"And what is the best email address for the booking confirmation?\" If they decline or say they do not have one, that is fine, move on.\n\n6. Preferred date. Ask: "What date works best for you?"\n\n7. Preferred time window. Ask: "And would morning (8am to 12pm) or afternoon (12pm to 5pm) suit you better?"\n\nOnce all details collected, use the check_availability tool to check the calendar.\n\nTransition to check_availability_node after collecting all booking details.\n\n## EMERGENCY DETECTION\nAt all times, listen for emergency signals (system completely stopped, gas smell, flooding, burning smell). If detected: IMMEDIATELY route to verify_emergency_node.\n\n## PRICING\nIf the caller asks about cost during booking:\n${pricingInstructions}\nThen continue with booking capture.\n\n## BOOKING FALLBACK\nIf the caller says they just want a callback rather than booking now: collect name, phone, service description, and address, then route to fallback_leadcapture_node.` },
      edges: [
        { id: "edge-booking-to-availability", destination_node_id: "node-check-availability", transition_condition: { type: "prompt", prompt: "All booking details collected, check calendar availability" } },
        { id: "edge-booking-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency signals detected" } },
        { id: "edge-booking-to-fallback", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Caller declines booking, prefers callback only" } }
      ],
      finetune_transition_examples: [
        { id: "fe-booking-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "Actually it completely stopped\nI smell gas\nWater is flooding\nThere is smoke from the unit" }] },
        { id: "fe-booking-fallback", destination_node_id: "node-fallback-leadcapture", transcript: [{ role: "user", content: "I don't want to book right now\nJust have someone call me\nI'll sort out the time later\nJust take my details" }] }
      ],
      display_position: { x: 1662, y: 726 }
    },

    // â”€â”€ NODE 4: Check Availability â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-check-availability", name: "check_availability_node", type: "conversation",
      instruction: { type: "prompt", text: `Check calendar availability for the requested date and time window.\n\nSay: "Let me just check that for you now." (brief pause)\n\nUse the check_availability tool call with:\n- date: requested date\n- time_window: morning or afternoon\n- job_type: service type\n- duration_minutes: ${bookingSlotDuration}\n\nIf the slot IS available:\n- Route to confirm_booking_node\n\nIf the slot is NOT available:\n- Say: "That slot is actually taken, but I have [next available option 1] and [next available option 2]. Which of those works for you?"\n- Once caller selects, route to confirm_booking_node with the new slot\n\nIf the calendar system is unavailable (tool error):\n- Say: "I'm having a little trouble with the booking system right now. Let me take your details and our team will call you back to confirm a time very shortly."\n- Route to fallback_leadcapture_node` },
      edges: [
        { id: "edge-availability-to-confirm", destination_node_id: "node-confirm-booking", transition_condition: { type: "prompt", prompt: "Slot available or alternative selected, proceed to confirm" } },
        { id: "edge-availability-to-fallback", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Calendar unavailable, system error, caller cannot find suitable slot" } }
      ],
      display_position: { x: 2214, y: 726 }
    },

    // â”€â”€ NODE 5: Confirm Booking â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-confirm-booking", name: "confirm_booking_node", type: "conversation",
      instruction: { type: "prompt", text: `Confirm the booking with the caller.\n\nRead back ALL details:\n"Perfect. Just to confirm â€” I have your appointment booked for [date], [time window], at [address]. Our team will be coming to [service description]. The best number to reach you is [phone]. Is all of that correct?"\n\nOnce confirmed:\n- Use the create_booking tool to save the appointment to the calendar${crmPlatform ? ` and push the contact/job to ${crmPlatform}` : ''}\n- Say: "You're all booked in. You'll receive a confirmation ${bookingConfirmMethod === 'both' ? 'by email and SMS' : `by ${bookingConfirmMethod}`} shortly. Is there anything else I can help you with today?"\n\nRoute to ending_node.` },
      edges: [
        { id: "edge-confirm-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Booking confirmed and saved, wrap up" } },
        { id: "edge-confirm-back-to-availability", destination_node_id: "node-check-availability", transition_condition: { type: "prompt", prompt: "Caller wants to change the date or time" } }
      ],
      display_position: { x: 2766, y: 726 }
    },

    // â”€â”€ NODE 6: Reschedule â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-reschedule", name: "reschedule_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller wants to reschedule an existing appointment.\n\n1. Get their full name: "Can I get your full name please?"\n2. Get original appointment date: "And what date was your original appointment for?"\n3. Get preferred new date and time window\n4. Use check_availability tool to verify the new slot\n5. If available: confirm the reschedule â€” read back old date and new date/time\n6. Use reschedule_booking tool to update the calendar${crmPlatform ? ` and update ${crmPlatform}` : ''}\n7. Say: "Done â€” you're rescheduled to [new date], [time window]. You'll receive an updated confirmation shortly."\n8. Route to ending_node` },
      edges: [
        { id: "edge-reschedule-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Reschedule confirmed" } },
        { id: "edge-reschedule-to-fallback", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Cannot find appointment, cannot access calendar, caller needs team to call back" } }
      ],
      display_position: { x: 1662, y: 1200 }
    },

    // â”€â”€ NODE 7: Cancel Appointment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-cancel-appointment", name: "cancel_appointment_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller wants to cancel an appointment.\n\n1. Get their full name\n2. Get the appointment date: "Can you confirm what date the appointment was for?"\n3. Confirm the cancellation: "Just to confirm, you'd like to cancel your [service] appointment on [date]. Is that right?"\n4. Use cancel_booking tool to remove from calendar${crmPlatform ? ` and update ${crmPlatform}` : ''}\n5. Say: "Done, your appointment has been cancelled. Would you like to rebook at a time that suits you better?"\n6. If yes: route to booking_capture_node\n7. If no: route to ending_node` },
      edges: [
        { id: "edge-cancel-to-rebook", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Caller wants to rebook after cancellation" } },
        { id: "edge-cancel-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Cancellation confirmed, no rebook" } }
      ],
      display_position: { x: 1662, y: 1500 }
    },

    // â”€â”€ NODE 8: Fallback Lead Capture â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-fallback-leadcapture", name: "fallback_leadcapture_node", type: "conversation",
      instruction: { type: "prompt", text: `Booking is not possible right now. Collect standard lead details as a fallback.\n\nCollect in order:\n1. Service needed (if not already known)\n2. Full name (first and last)\n3. Best callback number (read back in groups)\n4. Service address (confirm back)\n5. Email address (optional). Ask: \"And what is the best email for us to send updates to?\" If they decline, move on.\n6. Any additional notes\n\nOnce all collected, read everything back:\n"Just to confirm, I have your name as [name], best number [phone], and you need [service] at [address]. Is that all correct?"\n\nClose: "Perfect. I have recorded all of that and someone from our team will be in touch with you shortly to confirm a time."\n\nRoute to ending_node.` },
      edges: [
        { id: "edge-fallback-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "All details confirmed, close" } },
        { id: "edge-fallback-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency signals detected" } }
      ],
      display_position: { x: 2214, y: 1500 }
    },

    // â”€â”€ NODE 9: Verify Emergency â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-verify-emergency", name: "verify_emergency_node", type: "conversation",
      instruction: { type: "prompt", text: `Stay calm and reassuring. This caller has an urgent situation.\n\n1. Acknowledge immediately: "I completely understand, let me get you sorted right away."\n2. Is this a true emergency right now? No cooling in extreme heat, no heat in freezing temps, water leak, burning smell, gas smell?\n3. If YES:\n   - Quickly get name and callback number if not already collected\n   - Say: "I am going to transfer you to our emergency line now. The number is ${emergencyDisplayNumber} in case we get disconnected."\n   - Transfer immediately\n4. If NOT a true emergency (urgent but can wait):\n   - Say: "I understand this feels urgent. Let me get you booked in as the next available slot so the team can get to you as quickly as possible."\n   - Route to booking_capture_node as priority` },
      edges: [
        { id: "edge-emergency-yes", destination_node_id: "node-emergency-transfer", transition_condition: { type: "prompt", prompt: "Confirmed emergency, transfer now" } },
        { id: "edge-emergency-no", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Urgent but not emergency, book as priority" } }
      ],
      finetune_transition_examples: [
        { id: "fe-emergency-yes", destination_node_id: "node-emergency-transfer", transcript: [{ role: "user", content: "Yes it's an emergency\nI have no heat and it's freezing\nI smell gas\nWater is flooding\nYes we need someone now" }] },
        { id: "fe-emergency-no", destination_node_id: "node-booking-capture", transcript: [{ role: "user", content: "Not really an emergency but I need it fixed soon\nIt's not urgent but it's been out for a couple days\nNot really, it's just not working well" }] }
      ],
      display_position: { x: 2766, y: 1470 }
    },

    // â”€â”€ NODE 10: Callback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-callback", name: "callback_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller is returning a missed call.\n\nSay: "Thanks for calling back! We may have been trying to reach you about a service enquiry."\n\nAsk: "Do you know what it was regarding?" Let them explain if they know.\n\nThen collect:\n1. Full name (first and last)\n2. Confirm their number: "Is the best number to reach you still the one you're calling from?"\n\nIf they describe a new service need: route to booking_capture_node to attempt a booking.\n\nClose: "Perfect, I have let the team know you called and someone will be in touch shortly."` },
      edges: [
        { id: "edge-callback-to-booking", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Caller describes a service need, attempt booking" } },
        { id: "edge-callback-end", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details captured, no new service need, close" } }
      ],
      display_position: { x: 1662, y: 2100 }
    },

    // â”€â”€ NODE 11: Existing Customer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-existing-customer", name: "existing_customer_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller is an existing customer with a question about their job, appointment, invoice, or technician.\n\nIMPORTANT: You cannot look up appointment details, job status, invoices, or account information from here.\n\nSay: "I don't have access to job details from here, but I can get the right person to call you back or transfer you now."\n\nAsk which they prefer.\n\nIf callback: collect full name, best number (confirm back), and brief description of their enquiry.\nConfirm: "Just to confirm, I have [name], [number], and your enquiry is about [description]. Is that correct?"\nClose: "Perfect, I have passed all of that through to the team and someone will be in touch shortly."\n\nIf transfer now: route to transfer_call_node.` },
      edges: [
        { id: "edge-existing-resolved", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Enquiry noted, close" } },
        { id: "edge-existing-transfer", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller insists on speaking to someone now" } }
      ],
      display_position: { x: 2214, y: 2100 }
    },

    // â”€â”€ NODE 12: General Questions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-general-questions", name: "general_questions_node", type: "conversation",
      instruction: { type: "prompt", text: `Answer using company information in the global prompt only. Keep answers brief, one point at a time.\n\nPricing questions: Use the pricing rules from the global prompt.\n\nCannot answer from company info: "Great question, let me get someone to call you back with that." Then collect name and number.\n\nAfter answering always ask: "Is there anything else, or would you like to book someone to come out?"` },
      edges: [
        { id: "edge-general-answered", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Question answered, no booking needed" } },
        { id: "edge-general-to-booking", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Caller wants to book or get a quote" } },
        { id: "edge-general-transfer", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller needs further help beyond FAQ" } }
      ],
      display_position: { x: 1662, y: 2700 }
    },

    // â”€â”€ NODE 13: Spam / Robocall â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-spam-robocall", name: "spam_robocall_node", type: "conversation",
      instruction: { type: "static_text", text: "Say: \"Thank you for calling, have a great day.\" Then end the call." },
      edges: [{ id: "edge-spam-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 1662, y: 3000 }
    },

    // â”€â”€ NODE 14: Transfer Call â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-transfer-call", name: "Transfer Call", type: "transfer_call",
      instruction: { type: "prompt", text: "Say: \"Let me get someone on the line for you right now, just one moment.\" Then transfer." },
      transfer_destination: { type: "predefined", number: transferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: "You are now speaking to the business owner or team member, NOT the caller. Give a brief 1-2 sentence summary of the call. Include: the caller's name (if collected), what they are calling about, and whether they had a booking or just had a question. Keep it concise and professional." }, enable_bridge_audio_cue: true },
      edge: { id: "edge-transfer-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3318, y: 2238 }
    },

    // â”€â”€ NODE 14b: Emergency Transfer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-emergency-transfer", name: "Emergency Transfer", type: "transfer_call",
      instruction: { type: "prompt", text: `Say: "I am transferring you to our emergency line right now. The number is ${emergencyDisplayNumber} in case we get disconnected. Stay on the line." Then transfer immediately.` },
      transfer_destination: { type: "predefined", number: emergencyTransferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: "You are now speaking to the emergency team, NOT the caller. This is an EMERGENCY call. Give a brief summary: the caller's name, what the emergency is, and their address if collected. Be urgent and concise." }, enable_bridge_audio_cue: true },
      edge: { id: "edge-emergency-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3318, y: 1470 }
    },

    // â”€â”€ NODE 15: Transfer Failed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-transfer-failed", name: "transfer_failed_node", type: "conversation",
      instruction: { type: "prompt", text: `Say: "I'm sorry, I wasn't able to connect you right now. Let me take your details and have someone call you back as soon as possible."

Collect name and callback number only (do NOT re-ask if already provided).
⚠️ SCRIPTED CLOSE — USE EXACT WORDS: "Perfect, I've got your details noted. Someone from our team will call you back shortly."
Then route to ending. Do NOT restart the booking flow.` },
      edges: [
        { id: "edge-transfer-failed-to-booking", destination_node_id: "node-booking-capture", transition_condition: { type: "prompt", prompt: "Caller still wants to book" } },
        { id: "edge-transfer-failed-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details taken, close" } }
      ],
      display_position: { x: 3870, y: 2238 }
    },

    // â”€â”€ NODE 16: Ending â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-ending", name: "Ending", type: "conversation",
      instruction: { type: "static_text", text: `Is there anything else I can help you with today?

## CLOSE RULE
When the caller says goodbye or there is nothing more to help with: say goodbye ONCE warmly and end. Do NOT repeat the farewell. Do NOT encourage the caller to call back multiple times. One clean close.` },
      edges: [
        { id: "edge-ending-to-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Nothing else. Close: \"Have a great day, take care!\"" } },
        { id: "edge-ending-to-restart", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Caller has another question or request" } }
      ],
      display_position: { x: 4422, y: 2190 }
    },


    // NODE 18: Validate Phone (code node)
    {
      id: "node-validate-phone", name: "validate_phone", type: "code",
      code: `const raw = (typeof dv !== 'undefined' && dv && dv.caller_phone) ? dv.caller_phone : '';
const digits = raw.replace(/\\D/g, '');
let phone_normalized = raw, phone_valid = false, phone_flag = '';
if (digits.length === 10) { phone_normalized = '+1' + digits; phone_valid = true; }
else if (digits.length === 11 && digits.startsWith('1')) { phone_normalized = '+' + digits; phone_valid = true; }
else if (digits.length < 7) { phone_flag = 'incomplete_number'; }
else { phone_flag = 'unusual_format'; phone_valid = true; }
return { phone_normalized, phone_valid, phone_flag };`,
      speak_during_execution: false,
      wait_for_result: true,
      edges: [],
      else_edge: { id: "edge-validate-phone-else", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Else" } },
      display_position: { x: 900, y: 1400 }
    },


    // â”€â”€ NODE 17: End Call â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
      id: "node-end-call", name: "End Call", type: "end",
      instruction: { type: "prompt", text: "End the call warmly." },
      display_position: { x: 4974, y: 2238 }
    }
  ],
  starting_node_id: "node-greeting"
};

// ============================================================
// AGENT CONFIGURATION
// ============================================================
const agentConfig = {
  agent_name: `${companyName} - ${industryType} Premium`,
  voice_id: voiceId,
  language: "multi",
  webhook_url: "https://n8n.syntharra.com/webhook/retell-hvac-premium-webhook",
  ambient_sound: "call-center",
  ambient_sound_volume: 0.8,
  responsiveness: 0.9,
  enable_dynamic_responsiveness: true,
  interruption_sensitivity: 0.9,
  voice_temperature: 1,
  voice_speed: 1,
  enable_dynamic_voice_speed: true,
  volume: 1,
  max_call_duration_ms: 600000,
  allow_user_dtmf: true,
  opt_in_signed_url: false,
  post_call_analysis_data: [
    { type: "system-presets", name: "call_summary", description: "Write a 1-3 sentence summary of the call." },
    { type: "system-presets", name: "call_successful", description: "Evaluate whether the agent had a successful call." },
    { type: "system-presets", name: "user_sentiment", description: "Evaluate user's sentiment, mood and satisfaction level." },
    { type: "boolean", name: "booking_attempted", description: "Was a booking attempted during this call? Return true or false." },
    { type: "boolean", name: "booking_success", description: "Was a booking successfully created during this call? Return true or false." },
    { type: "string", name: "appointment_date", description: "If a booking was made or rescheduled, what date was booked? Format: YYYY-MM-DD or empty string." },
    { type: "string", name: "appointment_time_window", description: "If a booking was made, was it morning or afternoon? Return morning, afternoon, or empty string." },
    { type: "string", name: "job_type_booked", description: "If a booking was made, what type of job or service was booked? Short string or empty string." },
    { type: "string", name: "reschedule_or_cancel", description: "Was this call a reschedule, cancellation, or neither? Return reschedule, cancel, or neither." },
    { type: "string", name: "caller_name", description: "Full name of the caller if provided. Empty string if not." },
    { type: "string", name: "caller_phone", description: "Phone number of the caller if stated. Empty string if not." },
    { type: "string", name: "caller_email", description: "Email address of the caller if provided. Empty string if not." },
    { type: "string", name: "caller_address", description: "Service address if provided. Empty string if not." },
    { type: "string", name: "service_requested", description: "What service was requested. Short description." },
    { type: "string", name: "call_type", description: "Type of call: new_booking, reschedule, cancellation, emergency, callback, existing_customer, general_question, spam." },
    { type: "string", name: "urgency", description: "Urgency level: low, medium, high, emergency." },
    { type: "boolean", name: "is_hot_lead", description: "Is this a hot lead? True if lead score would be 7 or above." },
    { type: "number", name: "lead_score", description: "Lead score 0-10. Booking made=9-10. Booking attempted but failed=7-8. General inquiry=4-6. Spam=0." },
  ]
};

// ============================================================
// EXTRACTED DATA FOR DOWNSTREAM NODES
// ============================================================
const extractedData = {
  company_name: companyName, company_phone: companyPhone, website: companyWebsite,
  years_in_business: yearsInBusiness, agent_name: `${companyName} - ${industryType} Premium`, voice_gender: voiceGender,
  voice_id: voiceId, services_offered: servicesOffered, brands_serviced: brandsServiced,
  service_area: serviceArea, service_area_radius: serviceAreaRadius, business_hours: businessHours,
  response_time: responseTime, emergency_service: emergency247, emergency_phone: emergencyPhone,
  after_hours_behavior: afterHoursBehavior, free_estimates: freeEstimates, diagnostic_fee: diagnosticFee,
  pricing_policy: pricingPolicy, standard_fees: standardFees, financing_available: financingAvailable,
  financing_details: financingDetails, warranty: warranty, warranty_details: warrantyDetails,
  licensed_insured: licensedInsured, certifications: certifications, payment_methods: paymentMethods,
  maintenance_plans: maintenancePlans, lead_contact_method: leadContactMethod, lead_phone: leadPhone,
  lead_email: leadEmail,
  notification_email_2: data.notification_email_2 || '', notification_email_3: data.notification_email_3 || '',
  notification_sms_2: data.notification_sms_2 || '', notification_sms_3: data.notification_sms_3 || '',
  custom_greeting: customGreeting, company_tagline: companyTagline,
  transfer_phone: transferPhone || leadPhone, transfer_triggers: transferTriggers,
  transfer_behavior: transferBehavior, unique_selling_points: uniqueSellingPts,
  current_promotion: currentPromotion, seasonal_services: seasonalServices,
  additional_info: additionalNotes, owner_name: ownerName,
  google_review_rating: googleReviewRating, google_review_count: googleReviewCount,
  do_not_service: doNotService, membership_program: membershipProgram,
  client_email: data.client_email || '', timezone: data.timezone || 'America/Chicago',
  industry_type: industryType, after_hours_transfer: afterHoursTransfer,
  // Premium fields
  crm_platform: crmPlatform, calendar_platform: calendarPlatform,
  booking_slot_duration: bookingSlotDuration, booking_lead_time: bookingLeadTime,
  bookable_job_types: bookableJobTypes, booking_confirm_method: bookingConfirmMethod,
  calendar_webhook_url: calendarWebhookUrl, crm_webhook_url: crmWebhookUrl,
  available_time_slots: availableTimeSlots, booking_buffer_minutes: bookingBufferMinutes,
  tier: 'premium'
};

return {
  conversationFlow: conversationFlow,
  agentConfig: agentConfig,
  agentName: agentConfig.agent_name,
  companyName: companyName,
  voiceId: voiceId,
  companyInfoBlock: companyInfoBlock,
  extractedData: extractedData,
  transferNumber: transferNumber,
  emergencyTransferNumber: emergencyTransferNumber,
  timestamp: new Date().toISOString()
};
