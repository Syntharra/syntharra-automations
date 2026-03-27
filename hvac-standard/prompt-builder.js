// ============================================================
// Build Retell Prompt v6, Supabase Edition
// ============================================================
// v6 changes:
//   - Separate Emergency Transfer node (13 nodes total)
//   - transfer_phone (q48) = general transfer destination
//   - emergency_phone (q21) = emergency transfer, falls back to transfer_phone
//   - Fixed duplicate full name step in lead capture
//   - Richer verify_emergency prompt with data collection
//   - Improved identify_call instruction and edge labels
//   - Added finetune examples to callback node
//   - Improved general_questions to use global prompt pricing
// ============================================================

const data = $input.first().json;

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
const testMode           = false;

// === Voice selection ===
const voiceMap = { female: 'retell-Sloane', male: 'retell-Nico' };
const voiceId = voiceMap[voiceGender] || 'retell-Sloane';

// === Transfer numbers ===
// General transfer: transfer_phone (q48) from Jotform, fallback to lead_phone
const rawTransferPhone = transferPhone || leadPhone;
const transferNumber = rawTransferPhone
  ? (rawTransferPhone.startsWith('+') ? rawTransferPhone : `+1${rawTransferPhone.replace(/\D/g, '')}`)
  : '+10000000000';

// Emergency transfer: emergency_phone (q21) if provided, otherwise same as general transfer
const rawEmergencyPhone = emergencyPhone || rawTransferPhone;
const emergencyTransferNumber = rawEmergencyPhone
  ? (rawEmergencyPhone.startsWith('+') ? rawEmergencyPhone : `+1${rawEmergencyPhone.replace(/\D/g, '')}`)
  : transferNumber;

// Display version of emergency number for the agent to speak
const emergencyDisplayNumber = emergencyPhone || transferPhone || companyPhone || '';

// ============================================================
// BUILD PRICING RESPONSE INSTRUCTIONS
// ============================================================
let shareableFees = '';
if (diagnosticFee) shareableFees += `\n- Diagnostic/Service Call Fee: ${diagnosticFee} (gets applied to the repair if the customer proceeds)`;
if (standardFees) shareableFees += `\n- Additional Set Fees: ${standardFees}`;

let pricingInstructions = '';
if (pricingPolicy === 'We provide free quotes on-site') {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "We provide free on-site quotes so our team can give you\n  an accurate price based on your specific situation. Let me grab\n  your details so we can get someone out to you."\n- NEVER provide general service, repair, or installation prices.\n- NEVER guess or estimate costs for any service.`;
  if (shareableFees) pricingInstructions += `\n\nThe ONLY fees you may mention (because the company has explicitly provided them):${shareableFees}\n\nOnly mention these if the caller specifically asks about them. Do NOT volunteer pricing.`;
} else if (pricingPolicy === 'We charge a diagnostic fee then quote') {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "We do have a ${diagnosticFee || 'service call'} fee for\n  the initial visit, and that gets applied to the repair if you\n  choose to move forward with us. Our technician will give you a\n  full quote once they've assessed the situation."\n- NEVER provide general repair or installation prices.\n- NEVER guess or estimate costs beyond the set fees listed below.`;
  if (shareableFees) pricingInstructions += `\n\nSet fees you may share when asked:${shareableFees}`;
} else {
  pricingInstructions = `When callers ask about pricing or cost:\n- Say: "Our team will go over all the pricing with you so you get\n  the most accurate information. Let me grab your details so we\n  can get that set up for you."\n- NEVER provide any prices, estimates, or cost ranges over the phone.\n- NEVER guess or estimate costs for any service.`;
  if (shareableFees) pricingInstructions += `\n\nException, the ONLY fees you may mention:${shareableFees}\n\nOnly mention these if the caller specifically asks. Do NOT volunteer pricing.`;
}

// ============================================================
// BUILD TRANSFER RULES
// ============================================================
const triggerList = transferTriggers.split(',').map(t => t.trim()).filter(Boolean);
let transferRules = `## CALL TRANSFER PROTOCOL\n\n`;
transferRules += `General transfer destination: ${transferNumber}\n`;
transferRules += `Emergency transfer destination: ${emergencyTransferNumber}\n`;
transferRules += `Transfer behavior: ${transferBehavior}\n\n`;
transferRules += `Transfer the call ONLY when one of these conditions is met:\n`;
triggerList.forEach((t, i) => { transferRules += `${i + 1}. ${t}\n`; });
transferRules += `\nFor ALL other situations, collect the caller's information and let them know someone will follow up.`;
if (transferBehavior === 'Always take a message - never transfer') {
  transferRules += `\n\nIMPORTANT: NEVER transfer calls. Always collect caller information and confirm someone from the team will call back.`;
}
if (ownerName) {
  transferRules += `\n\n### Owner/Manager Reference\nIf a caller asks to speak with the owner or manager, their name is ${ownerName}. Say: "${ownerName} isn't available right now, but I can take a message and have them call you back, or I can transfer you to our team."`;
}

// ============================================================
// BUILD DO NOT SERVICE SECTION
// ============================================================
let doNotServiceSection = '';
if (doNotService) {
  doNotServiceSection = `\n\n\n## SERVICES WE DO NOT PROVIDE\n\nThe following items are outside our scope of service:\n${doNotService}\n\nIf a caller requests any of these, politely explain:\n"I appreciate you reaching out, but unfortunately that's not something we service. I'd recommend reaching out to a specialist for that. Is there anything else I can help you with?"\n\nDo NOT attempt to collect lead information for out-of-scope requests.\n`;
}

// ============================================================
// BUILD PROMOTIONS / SELLING POINTS SECTION
// ============================================================
let promotionsSection = '';
if (currentPromotion || seasonalServices || uniqueSellingPts || (googleReviewRating && googleReviewRating !== 'Not listed on Google')) {
  promotionsSection = `\n\n\n## PROMOTIONS & VALUE PROPOSITIONS\n\n`;
  if (googleReviewRating && googleReviewRating !== 'Not listed on Google') {
    let reviewLine = `We have a ${googleReviewRating}-star rating on Google`;
    if (googleReviewCount && googleReviewCount !== 'Not listed on Google') reviewLine += ` with ${googleReviewCount.toLowerCase().replace('under ', 'nearly ')} reviews`;
    promotionsSection += `### Google Reviews\n${reviewLine}.\nMention this naturally when a caller is comparing options or seems uncertain.\n\n`;
  }
  if (currentPromotion) promotionsSection += `### Current Promotion\n${currentPromotion}\nMention this naturally when a caller asks about the relevant service.\n\n`;
  if (uniqueSellingPts) promotionsSection += `### Why Choose ${companyName}\n${uniqueSellingPts}\nUse these points when a caller seems to be comparing options. Weave them in naturally.\n\n`;
  if (seasonalServices) promotionsSection += `### Seasonal Services\n${seasonalServices}\nMention the relevant seasonal service if it matches what the caller needs.\n\n`;
}

// ============================================================
// BUILD PAYMENT METHODS SECTION
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
// GLOBAL PROMPT
// ============================================================
let globalPrompt = `## ROLE\nYou are ${agentName}, a virtual AI receptionist for ${companyName}.${companyTagline ? ' ' + companyTagline + '.' : ''}\nYou are warm, professional and concise. Speak naturally, one topic at a time. Address callers by first name once you have it.\n\nIf asked if you are a real person: "I'm a virtual assistant, but I'm here to make sure you get exactly the help you need."\n\n## STYLE\n- One question at a time, always wait for the answer\n- Match the caller's energy. Calm if calm, reassuring if stressed\n- Never rush. Be patient with elderly callers\n- Vary your language naturally\n\n## CONFIRMING DETAILS\nSlow down when collecting contact info. Confirm each piece back before moving on.\n- Phone: read back in groups "512, 555, 0192, is that right?"\n- Name: spell uncommon names letter by letter\n- Address: confirm street and suburb "123 Main Street, Austin, is that right?"\n- Email: read back slowly using dot, at, dash\n- ZIP: digit by digit\nIf anything is unclear, ask them to spell it. Never guess.\n\n## TRANSCRIPTION\nIf you cannot understand something: "I'm sorry, I didn't quite catch that, could you say that again?" Never guess at names, addresses or emails.\n\n## COMPANY INFORMATION\n\n{{COMPANY_INFO_BLOCK}}\n\nUse the information above to answer any company-specific questions\nsuch as service areas, hours of operation, services offered, and\ncontact details. If a question about the company is NOT covered\nabove, do NOT guess or make up information. Say:\n"That's a great question, one of our team members will be able\nto answer that when they call you back."\n\n\n\n## PRICING & QUOTING\n\n${pricingInstructions}\n\n\n\n${transferRules}\n\n\n\n## PAYMENT & FINANCING\n${paymentSection || `When callers ask about payment methods:\n- Say: "Our team can go over payment options with you at the appointment."`}\n\n\n${promotionsSection}\n${doNotServiceSection}\n## CRITICAL RULES, NEVER BREAK THESE\n\n- NEVER ask more than one question at a time\n- NEVER make up prices, estimates, or timeframes unless explicitly listed in company information\n- NEVER diagnose ${industryType} problems or recommend specific repairs\n- NEVER promise availability or same-day service unless explicitly stated in company information\n- NEVER guess answers to company-specific questions not found in company information\n- NEVER continue a conversation with obvious spam or robocalls, end politely\n- NEVER transfer a call unless it matches a transfer trigger or is a confirmed emergency\n- ALWAYS collect lead information before ending any legitimate call\n- ALWAYS confirm information back to the caller before ending the call\n- ALWAYS be warm, calm, and professional regardless of caller frustration\n- ALWAYS try to understand what the caller means even if unclear, never mention transcription errors\n\n\n\n## IF CALLER IS RELUCTANT TO SHARE INFORMATION\n\n"I completely understand, this information simply helps our team follow up with you accurately. We never share your details with third parties."\n\n\n\n## ERROR HANDLING\n\n### Didn't hear or understand:\n"I apologise, I didn't quite catch that, could you repeat that for me?"\n\n### Don't know the answer:\n"That's a great question. I want to make sure you get the right answer, can I grab your details so someone from our team can call you back?"\n\n### Caller can't hear you:\n"I'm sorry about that, is this any better?" Speak slightly louder and more clearly.\n\n\n\n## SPECIAL SCENARIOS\n\n### Angry or Upset Callers\n1. Stay calm and lower your tone slightly\n2. Acknowledge: "I can hear how frustrated you are and I sincerely apologise for that."\n3. Redirect: "Let me see how I can help sort this out for you right now."\n4. If abuse continues: "I do want to help you, but I need us to work together respectfully. How can I best assist you today?"\n\n### Silent Callers\n- After 3 seconds: "Hello, are you there?"\n- After 5 more seconds: "I'm having trouble hearing you, can you hear me okay?"\n- If no response after a further 5 seconds: end the call politely\n\n### Threats or Safety Concerns\nStay calm, do not engage or argue. Note any relevant details and flag the call immediately for human review after it ends.\n`;

// Capturing details section
const capturingSection = `\n\n## CAPTURING DETAILS\nWhen collecting any detail that could be misheard, slow down noticeably.\n- Phone numbers: read back in groups, "512, 555, 0192, is that right?"\n- Emails: spell each part, "J-O-H-N dot S-M-I-T-H at gmail dot com, correct?"\n- Unusual street names: ask them to spell it out\n- Names: always get first and last name, confirm spelling for uncommon names\n- If you have confirmed something twice and the caller is still unclear, say: "No problem, our team will confirm all the details when they call you back" and move on`;
globalPrompt += capturingSection;

// ============================================================
// BUILD GREETING
// ============================================================
const greetingText = customGreeting
  ? customGreeting
  : `Hello this is ${agentName} from ${companyName}`;

// ============================================================
// BUILD CONVERSATION FLOW (13 NODES)
// ============================================================
const conversationFlow = {
  name: `${companyName} - ${industryType} Receptionist Flow`,
  start_speaker: "agent",
  model_choice: { type: "cascading", model: "gpt-4.1", high_priority: false },
  global_prompt: globalPrompt.replace("{{COMPANY_INFO_BLOCK}}", companyInfoBlock),
  tool_call_strict_mode: true,
  knowledge_base_ids: [],
  kb_config: { top_k: 3, filter_score: 0.6 },
  flex_mode: false,
  is_transfer_cf: false,
  nodes: [
    {
      id: "node-greeting", name: "greeting_node", type: "conversation",
      instruction: { type: "static_text", text: greetingText },
      edges: [{ id: "edge-greeting-to-identify", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 558, y: 462 }
    },
    {
      id: "node-identify-call", name: "identify_call_node", type: "conversation", start_speaker: "agent",
      instruction: { type: "prompt", text: "Listen and identify the reason for the call. Route to the correct node immediately without asking unnecessary questions." },
      edges: [
        { id: "edge-to-leadcapture-service", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Repair, service, maintenance, tune-up, inspection" } },
        { id: "edge-to-leadcapture-quote", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Quote, estimate, installation, replacement, new system" } },
        { id: "edge-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency, urgent, no cooling, no heat, water leak, burning smell, gas smell" } },
        { id: "edge-to-callback", destination_node_id: "node-callback", transition_condition: { type: "prompt", prompt: "Returning a missed call, got a call from this number, calling back" } },
        { id: "edge-to-existing-customer", destination_node_id: "node-existing-customer", transition_condition: { type: "prompt", prompt: "Existing customer, question about appointment, invoice, technician, job status" } },
        { id: "edge-to-general-questions", destination_node_id: "node-general-questions", transition_condition: { type: "prompt", prompt: "General question about services, hours, pricing, area, credentials" } },
        { id: "edge-to-transfer-live", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Wants to speak to a real person, manager, owner, or specific person" } },
        { id: "edge-to-spam", destination_node_id: "node-spam-robocall", transition_condition: { type: "prompt", prompt: "Robocall, spam, automated message, silence after greeting" } }
      ],
      finetune_transition_examples: [
        { id: "fe-service-repair", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "My AC isn't working\nMy heater broke down\nI need a repair\nMy system won't turn on\nIt's blowing warm air\nMy unit is making a loud noise\nI need someone to come fix my AC\nMy furnace stopped working\nI need a tune-up\nCan someone come check my system" }, { role: "agent", content: "I can help with that" }] },
        { id: "fe-quote-install", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "I want a quote\nI need an estimate\nHow much does a new system cost\nI want to install a new AC\nI need to replace my furnace\nI'm looking for a new unit\nWhat would a new system run me\nI want to upgrade my AC\nCan I get a quote on a heat pump" }, { role: "agent", content: "Absolutely, let me get some details" }] },
        { id: "fe-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "no cooling\nno heating\nsystem not working\nAC not working\nheater not working\nleaking unit\nwater leaking\nburning smell\nloud noise\nbroken system\nurgent repair\nemergency repair\nI smell gas\nno air coming out\nmy pipes are freezing" }, { role: "agent", content: "Sounds like you have an emergency" }] },
        { id: "fe-callback", destination_node_id: "node-callback", transcript: [{ role: "user", content: "Yeah I just missed a call from this number\nSomeone called me from here\nI am calling back\nI got a voicemail from you guys\nYou guys called me earlier\nReturning your call\nI saw a missed call" }, { role: "agent", content: "Thanks for calling back" }] },
        { id: "fe-existing-customer", destination_node_id: "node-existing-customer", transcript: [{ role: "user", content: "calling about my appointment\nchecking appointment time\ntechnician arrival\nwhere is the technician\nfollowing up on a quote\ncalling about my quote\nchecking on my job\ncalling about service appointment\nquestion about invoice\nquestion about billing\npayment question\ncalling back about earlier service" }, { role: "agent", content: "Sure" }] },
        { id: "fe-transfer-live", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "Let me speak to someone\nI want to talk to a real person\nCan I speak to a human\nTransfer me\nPut me through to someone\nI don't want to talk to a bot\nLet me speak to the owner\nI want to talk to the manager\nGet me your supervisor\nIs the boss available\nJust forget it\nThis is useless\nNever mind" }] },
        { id: "fe-spam", destination_node_id: "node-spam-robocall", transcript: [{ role: "user", content: "Hello\nHello\nHello" }, { role: "agent", content: "Routing to spam handler" }] }
      ],
      display_position: { x: 1110, y: 366 }
    },
    {
      id: "node-leadcapture", name: "nonemergency_leadcapture_node", type: "conversation",
      instruction: { type: "prompt", text: `Collect the following in order, one question at a time. Do not move to the next until the caller has answered.\n\n1. What is the issue or service needed? If the caller hasn't already explained, ask: "What can we help you with today?" Let them describe the problem fully before moving on.\n\n2. Full name, first and last. Ask: "Can I get your full name please?" If they give only a first name, ask: "And your last name?" Confirm spelling for uncommon names.\n\n3. Best callback number. Read it back in groups to confirm: "So that is 512, 555, 0192, is that right?"\n\n4. Service address. A full address is ideal but not required.\n- After the caller gives any address details, ALWAYS confirm back what you heard.\n- If they give a street address but no city or ZIP, ask: "And what city or suburb is that in?"\n- If the address is unclear, say: "Could you spell out the street name for me just to make sure I have that right?"\n- If the caller won't give a full address, say: "No problem at all, could I at least get the suburb, city, or ZIP code? That helps our team plan the visit."\n- A suburb, city, or ZIP code alone is acceptable.\n\n5. Any additional notes or details.\n\n\n\n## PRICING RESPONSES\n\nIf the caller asks "how much?" or "what does it cost?" during data capture:\n${pricingInstructions}\n\nThen continue with data capture.\n\n\n\n## EMERGENCY DETECTION\n\nAt all times during the call, listen for emergency signals:\n- System completely stopped, significant leaking, burning smell\n- No heat in freezing conditions, gas smell\n\nIF detected: IMMEDIATELY route to verify_emergency_node.\n\n\n\n## CONFIRMATION\n\nOnce all details are collected, read everything back to the caller:\n"Just to confirm, I have your name as [name], best number [phone], and you need [service] at [address]. Is that all correct?"\n\n\n\n## CLOSING\n\n"Perfect, I have recorded all of that and someone from our team will be in touch with you shortly."` },
      edges: [
        { id: "edge-leadcapture-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency signals detected" } },
        { id: "edge-leadcapture-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "All details confirmed, close" } }
      ],
      finetune_transition_examples: [{ id: "fe-leadcapture-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "Actually it completely stopped working\nThere is no air at all\nI smell something burning\nWater is pouring out\nI think I smell gas" }] }],
      display_position: { x: 2190, y: 726 }
    },
    {
      id: "node-verify-emergency", name: "verify_emergency_node", type: "conversation",
      instruction: { type: "prompt", text: `Stay calm and reassuring. This caller has an urgent situation.\n\n1. Acknowledge immediately: "I completely understand, let me get you sorted right away."\n2. Is this a true emergency right now? No cooling in extreme heat, no heat in freezing temps, water leak, burning smell, gas smell?\n3. If YES emergency:\n   - If not already collected, quickly get their name and callback number first.\n   - Say: "I am going to transfer you to our emergency line now. The number is ${emergencyDisplayNumber} in case we get disconnected."\n   - Then transfer immediately.\n4. If NOT a true emergency (urgent but can wait):\n   - Say: "I understand this feels urgent. Let me get your details through to the team as a priority so they can get to you as quickly as possible."\n   - Route back to lead capture as a priority lead.` },
      edges: [
        { id: "edge-emergency-yes", destination_node_id: "node-emergency-transfer", transition_condition: { type: "prompt", prompt: "Confirmed emergency, transfer now" } },
        { id: "edge-emergency-no", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Urgent but not emergency, capture as priority lead" } }
      ],
      finetune_transition_examples: [
        { id: "fe-emergency-yes", destination_node_id: "node-emergency-transfer", transcript: [{ role: "user", content: "Yes it's an emergency\nI have no heat and it's freezing\nI smell gas\nWater is flooding my basement\nThere is smoke coming from the unit\nYes we need someone now" }] },
        { id: "fe-emergency-no", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "No it's not an emergency but I need it fixed soon\nIt's not urgent but it's been out for a couple days\nNo emergency but I'd like someone today if possible\nNot really, it's just not working well" }] }
      ],
      display_position: { x: 2742, y: 1470 }
    },
    {
      id: "node-callback", name: "callback_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller is returning a missed call.\n\nSay: "Thanks for calling back! We may have been trying to reach you about a service enquiry."\n\nAsk: "Do you know what it was regarding?" Let them explain if they know.\n\nThen collect:\n1. Full name, first and last\n2. Confirm their number: "Is the best number to reach you still the one you're calling from?"\n\nIf they describe a new issue, route to lead capture.\n\nClose: "Perfect, I have let the team know you called and someone will be in touch shortly."` },
      edges: [
        { id: "edge-callback-end", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details captured, close" } },
        { id: "edge-callback-to-leadcapture", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Caller describes a new issue that needs lead capture" } }
      ],
      finetune_transition_examples: [
        { id: "fe-callback-new-issue", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "Actually I need to book a repair\nI wanted to schedule a service\nI need someone to come out\nI think my AC needs fixing\nI wanted to get a quote" }] }
      ],
      display_position: { x: 1662, y: 3000 }
    },
    {
      id: "node-existing-customer", name: "existing_customer_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller is an existing customer with a question about their job, appointment, invoice, or technician.\n\nIMPORTANT: You cannot look up appointments, job status, invoices, or any account information. Do not attempt to do so.\n\nSay: "I don't have access to job details from here, but I can get the right person to call you back or transfer you now."\n\nAsk which they prefer: transfer now or callback.\n\nIf callback: collect full name, best number (confirm back), and brief description of their enquiry.\nConfirm: "Just to confirm, I have [name], [number], and your enquiry is about [description]. Is that correct?"\nClose: "Perfect, I have passed all of that through to the team at ${companyName} and someone will be in touch shortly."` },
      edges: [
        { id: "edge-existing-resolved", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Enquiry noted, close" } },
        { id: "edge-existing-unresolved", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller insists on speaking to someone now" } }
      ],
      display_position: { x: 2742, y: 6 }
    },
    {
      id: "node-general-questions", name: "general_questions_node", type: "conversation",
      instruction: { type: "prompt", text: `Answer using company information in the global prompt only. Keep answers brief, one point at a time.\n\nPricing questions: Use the pricing rules from the global prompt. Share only the specific fees listed there. Never estimate or guess.\n\nCannot answer from company info: "Great question, let me get someone to call you back with that." Then collect name and number.\n\nAfter answering always ask: "Is there anything else, or would you like to book someone to come out?"` },
      edges: [
        { id: "edge-general-answered", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Question answered, no booking needed" } },
        { id: "edge-general-lead", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Caller wants to book or get a quote" } },
        { id: "edge-general-further-help", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller needs further help beyond FAQ" } }
      ],
      finetune_transition_examples: [
        { id: "fe-general-further-help", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "I need more help\nThis doesn't answer my question\nCan someone call me back about this\nI need a specialist\nI want to speak to someone who can help" }] },
        { id: "fe-general-lead", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "I want to book\nCan someone come out\nI want to get a quote\nHow much would it cost\nI think I need a repair\nWhen can someone come out\nYes let's do that\nOkay I'd like to schedule something" }] }
      ],
      display_position: { x: 1662, y: 2190 }
    },
    {
      id: "node-spam-robocall", name: "spam_robocall_node", type: "conversation",
      instruction: { type: "static_text", text: "Say: \"Thank you for calling, have a great day.\" Then end the call." },
      edges: [{ id: "edge-spam-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 1662, y: 3300 }
    },
    {
      id: "node-transfer-call", name: "Transfer Call", type: "transfer_call",
      instruction: { type: "prompt", text: "Say: \"Let me get someone on the line for you right now, just one moment.\" Then transfer." },
      transfer_destination: { type: "predefined", number: transferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: "You are now speaking to the business owner or team member, NOT the caller. Give a brief 1-2 sentence summary of the call. Include: the caller's name (if collected), what they are calling about, and their urgency level. Example: \"Hi, I have [name] on the line calling about [issue]. They seem [calm/frustrated/urgent].\" Keep it concise and professional. Once you have briefed them, the caller will be connected." }, enable_bridge_audio_cue: true },
      edge: { id: "edge-transfer-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3294, y: 2238 }
    },
    {
      id: "node-emergency-transfer", name: "Emergency Transfer", type: "transfer_call",
      instruction: { type: "prompt", text: `Say: "I am transferring you to our emergency line right now. The number is ${emergencyDisplayNumber} in case we get disconnected. Stay on the line." Then transfer immediately.` },
      transfer_destination: { type: "predefined", number: emergencyTransferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: "You are now speaking to the emergency team, NOT the caller. This is an EMERGENCY call. Give a brief summary: the caller's name, what the emergency is (no heat, gas smell, water leak, etc.), and their address if collected. Example: \"Emergency call from [name] at [address]. They have [no heat/gas leak/flooding]. Connecting them now.\" Be urgent and concise." }, enable_bridge_audio_cue: true },
      edge: { id: "edge-emergency-transfer-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3294, y: 1470 }
    },
    {
      id: "node-transfer-failed", name: "transfer_failed_node", type: "conversation",
      instruction: { type: "static_text", text: "Say:\n\"I'm sorry, I wasn't able to connect you right now. Let me take your name and number and have someone call you back as soon as possible.\" Collect name and callback number, confirm back, then close." },
      edges: [{ id: "edge-transfer-failed-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details taken, close" } }],
      display_position: { x: 3846, y: 2166 }
    },
    {
      id: "node-ending", name: "Ending", type: "conversation",
      instruction: { type: "static_text", text: "Is there anything else I can help you with today?" },
      edges: [
        { id: "edge-ending-to-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Nothing else. Close: \"Have a great day, take care!\"" } },
        { id: "edge-ending-to-restart", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Caller has another question or request" } }
      ],
      display_position: { x: 4398, y: 2190 }
    },
    {
      id: "node-end-call", name: "End Call", type: "end",
      instruction: { type: "prompt", text: "End the call warmly." },
      display_position: { x: 4950, y: 2238 }
    }
  ],
  starting_node_id: "node-greeting"
};

// ============================================================
// AGENT CONFIGURATION
// ============================================================
const agentConfig = {
  agent_name: `${companyName} - HVAC Standard`,
  voice_id: voiceId,
  language: "multi",
  webhook_url: "https://syntharra.app.n8n.cloud/webhook/retell-hvac-webhook",
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
    { type: "system-presets", name: "user_sentiment", description: "Evaluate user's sentiment, mood and satisfaction level." }
  ]
};

// ============================================================
// EXTRACTED DATA FOR DOWNSTREAM NODES
// ============================================================
const extractedData = {
  company_name: companyName, company_phone: companyPhone, website: companyWebsite,
  years_in_business: yearsInBusiness, agent_name: `${companyName} - HVAC Standard`, voice_gender: voiceGender,
  voice_id: voiceId, services_offered: servicesOffered, brands_serviced: brandsServiced,
  service_area: serviceArea, service_area_radius: serviceAreaRadius, business_hours: businessHours,
  response_time: responseTime, emergency_service: emergency247, emergency_phone: emergencyPhone,
  after_hours_behavior: afterHoursBehavior, free_estimates: freeEstimates, diagnostic_fee: diagnosticFee,
  pricing_policy: pricingPolicy, standard_fees: standardFees, financing_available: financingAvailable,
  financing_details: financingDetails, warranty: warranty, warranty_details: warrantyDetails,
  licensed_insured: licensedInsured, certifications: certifications, payment_methods: paymentMethods,
  maintenance_plans: maintenancePlans, lead_contact_method: leadContactMethod, lead_phone: leadPhone,
  lead_email: leadEmail, notification_email_2: data.notification_email_2 || '', notification_email_3: data.notification_email_3 || '', notification_sms_2: data.notification_sms_2 || '', notification_sms_3: data.notification_sms_3 || '', custom_greeting: customGreeting, company_tagline: companyTagline,
  transfer_phone: transferPhone || leadPhone, transfer_triggers: transferTriggers,
  transfer_behavior: transferBehavior, unique_selling_points: uniqueSellingPts,
  current_promotion: currentPromotion, seasonal_services: seasonalServices,
  additional_info: additionalNotes, owner_name: ownerName, google_review_rating: googleReviewRating,
  google_review_count: googleReviewCount, do_not_service: doNotService,
  membership_program: membershipProgram, client_email: data.client_email || '',
  timezone: data.timezone || 'America/Chicago', industry_type: industryType
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
