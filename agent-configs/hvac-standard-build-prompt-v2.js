// ============================================================
// Build Retell Prompt v5, Supabase Edition
// ============================================================
// Removed Google Sheets settings dependency
// Transfer number: lead_phone default, emergency_phone override
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
const timezone           = data.timezone || 'America/Chicago';
const testMode           = false;

// === Voice selection ===
const voiceMap = { female: 'retell-Sloane', male: 'retell-Nico' };
const voiceId = voiceMap[voiceGender] || 'retell-Sloane';

// === Transfer number: use lead_phone by default, emergency_phone as override ===
const rawTransferPhone = emergencyPhone || leadPhone;
const transferNumber = rawTransferPhone
  ? (rawTransferPhone.startsWith('+') ? rawTransferPhone : `+1${rawTransferPhone.replace(/\D/g, '')}`)
  : '+10000000000';

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
transferRules += `Transfer destination: ${transferNumber}\n`;
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
let globalPrompt = `## ROLE\\nYou are ${agentName}, a virtual AI receptionist for ${companyName}.${companyTagline ? ' ' + companyTagline + '.' : ''}\\nWarm, professional and concise. One topic at a time. Use the caller's first name once you have it.\\nIf asked if you are real: \"I'm a virtual assistant here to make sure you get the right help.\"\\n\\n## STYLE\\n- One question at a time, wait for the answer before asking another\\n- Match the caller's energy. Reassuring if stressed, calm if calm\\n- Patient with elderly callers. Never rush\\n- Vary your language naturally\\n\\n\n\n## TIME AWARENESS\nThe current time is {{current_time_${timezone}}}. Use this to determine if the caller is reaching us during or outside business hours. Never guess the current date or time.\n\n## CONFIRMING DETAILS\\nSlow right down when collecting contact info. Confirm each piece back before moving on.\\n- Phone: read back in groups \"512, 555, 0192, is that right?\"\\n- Name: spell uncommon names letter by letter\\n- Address: confirm street and suburb back\\n- Email: read back slowly, character by character, using dot, at, dash\\n- ZIP: digit by digit\\nIf anything is unclear, ask them to spell it. Never guess.\\n\\n## TRANSCRIPTION\\nIf you cannot understand something: \"I'm sorry, could you say that again?\" Never guess at names, addresses or emails.\\n\\n## COMPANY INFORMATION\\n\n{{COMPANY_INFO_BLOCK}}\n\nOnly use the above to answer company questions. If not covered, say: \"Great question, one of our team will be able to answer that when they call you back.\"\\n\\n${pricingInstructions}\\n\\n${transferRules}\\n\\n${paymentSection}\\n\\n${promotionsSection}${doNotServiceSection}## RULES\\n- Never ask more than one question at a time\\n- Never give prices, estimates, or diagnose problems\\n- Never promise availability unless stated in company info\\n- Never guess company-specific answers\\n- Always collect lead info before ending a legitimate call\\n- Always confirm details back before closing\\n- Always stay warm and calm regardless of caller mood\\n\\n## HANDLING DIFFICULT SITUATIONS\\nReluctant to share info: \"I completely understand, this just helps our team reach you accurately.\"\\nAngry caller: Acknowledge, stay calm, redirect. If abusive: \"I do want to help, but I need us to work together respectfully.\"\\nSilence: After 3s \"Hello, are you there?\", after 8s total \"I'm having trouble hearing you.\", after 13s end the call politely.\\nCannot hear: \"I'm sorry about that, is this any better?\"\\n`;

// ============================================================
// BUILD GREETING
// ============================================================
const greetingText = customGreeting
  ? customGreeting
  : `Hello this is ${agentName} from ${companyName}`;

// ============================================================
// BUILD CONVERSATION FLOW NODES
// ============================================================

// Capturing details section — appended to global prompt
const capturingSection = `

## CAPTURING DETAILS
When collecting any detail that could be misheard, slow down noticeably.
- Phone numbers: read back in groups, "512, 555, 0192, is that right?"
- Emails: spell each part, "J-O-H-N dot S-M-I-T-H at gmail dot com, correct?"
- Unusual street names: ask them to spell it out
- Names: always get first and last name, confirm spelling for uncommon names
- If you have confirmed something twice and the caller is still unclear, say: "No problem, our team will confirm all the details when they call you back" and move on`;
globalPrompt += capturingSection;

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
      edges: [{ id: "edge-greeting-to-identify", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "All" } }],
      display_position: { x: 558, y: 462 }
    },
    {
      id: "node-identify-call", name: "identify_call_node", type: "conversation", start_speaker: "agent",
      instruction: { type: "prompt", text: "Identify the reason for the call" },
      edges: [
        { id: "edge-to-leadcapture-service", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Repair/Service/Maintenance" } },
        { id: "edge-to-leadcapture-quote", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Quote/Estimate/Price/Installation" } },
        { id: "edge-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency" } },
        { id: "edge-to-existing-customer", destination_node_id: "node-existing-customer", transition_condition: { type: "prompt", prompt: "Existing Customer" } },
        { id: "edge-to-general-questions", destination_node_id: "node-general-questions", transition_condition: { type: "prompt", prompt: "General Questions" } },
        { id: "edge-to-transfer-live", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Live Person/Owner/Specific Person" } },
        { id: "edge-to-callback", destination_node_id: "node-callback", transition_condition: { type: "prompt", prompt: "Returning a missed call, got a call from this number, calling back" } },
        { id: "edge-to-spam", destination_node_id: "node-spam-robocall", transition_condition: { type: "prompt", prompt: "Robocall, spam, automated message, silence after greeting" } }
      ],
      finetune_transition_examples: [
        { id: "fe-existing-customer", destination_node_id: "node-existing-customer", transcript: [{ role: "user", content: "calling about my appointment\nchecking appointment time\ntechnician arrival\nwhere is the technician\nfollowing up on a quote\ncalling about my quote\nchecking on my job\ncalling about service appointment\nquestion about invoice\nquestion about billing\npayment question\ncalling back about earlier service" }, { role: "agent", content: "Sure" }] },
        { id: "fe-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "no cooling\nno heating\nsystem not working\nAC not working\nheater not working\nleaking unit\nwater leaking\nburning smell\nloud noise\nbroken system\nurgent repair\nemergency repair" }, { role: "agent", content: "Sounds like you have an emergency" }] },
        { id: "fe-transfer-live", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "Let me speak to someone\nI want to talk to a real person\nCan I speak to a human\nTransfer me\nPut me through to someone\nI don't want to talk to a bot\nLet me speak to the owner\nI want to talk to the manager\nGet me your supervisor\nIs the boss available\nJust forget it\nThis is useless\nNever mind" }] },
        { id: "fe-quote-install", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "I want a quote\nI need an estimate\nWhat's the price\nHow much does it cost\nHow much do you charge\nI want to install\nI need a new system\nI want to replace my system" }] },
        { id: "fe-service-repair", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "My system is not working\nMy system is broken\nMy system won't turn on\nMy system keeps turning off\nMy system is not cooling\nMy system is not heating\nMy system is blowing warm air" }] },
        { id: "fe-callback", destination_node_id: "node-callback", transcript: [{ role: "user", content: "Yeah I just missed a call from this number\nSomeone called me from here\nI am calling back\nI got a voicemail from you guys" }] },
        { id: "fe-spam", destination_node_id: "node-spam-robocall", transcript: [{ role: "user", content: "Hello\nHello\nHello" }, { role: "agent", content: "Routing to spam handler" }] }
      ],
      display_position: { x: 1110, y: 366 }
    },
    {
      id: "node-leadcapture", name: "nonemergency_leadcapture_node", type: "conversation",
      instruction: { type: "prompt", text: `## CALL TYPE IDENTIFICATION\n\nAt the start of the call, listen carefully to identify whether the caller is:\n\nA. Requesting a SERVICE, REPAIR, or MAINTENANCE visit\nB. Requesting a QUOTE, INSTALLATION, ESTIMATE, or PRICE\n\nBoth call types follow the same data capture flow below.\n\n\n\n## PRICING RESPONSES\n\nIf the caller asks "how much?" or "what does it cost?" during data capture:\n${pricingInstructions}\n\nThen continue with data capture.\n\n\n\n## DATA CAPTURE FLOW\n\nCollect the following information for ALL call types:\n\n1. A short description of the issue, service, or installation needed\n2. The caller's full name\n3. The best phone number to reach them\n4. The caller's full name (first and last name).

- If they only give a first name, say:
  "And your last name?"
- Always confirm the full name back, spelling it out if it sounds unusual.

5. The service address. A full address is ideal but not required.

- After the caller gives any address details, ALWAYS confirm back what you heard.
- If they give a street address but no city or ZIP, ask:
  "And what city or suburb is that in?"
- If the address is unclear, say:
  "Could you spell out the street name for me just to make sure I have that right?"
- If the caller won't give a full address, say:
  "No problem at all, could I at least get the suburb, city, or ZIP code? That helps our team plan the visit."
- A suburb, city, or ZIP code alone is acceptable if the caller won't give more.""\n\n5. Any additional notes or details\n\n\n\n## EMERGENCY DETECTION\n\nAt all times during the call, listen for emergency signals:\n- System completely stopped, significant leaking, burning smell\n- No heat in freezing conditions, gas smell\n\nIF detected: IMMEDIATELY route to verify_emergency_node.\n\n\n\n## CONFIRMATION\n\nOnce all details are collected, confirm back to the caller.\n\n\n\n## CLOSING\n\n"Okay, I have recorded all of that information and someone from\nour team will be in touch with you soon."` },
      edges: [
        { id: "edge-leadcapture-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "If Emergency, go to" } },
        { id: "edge-leadcapture-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Confirm the details with the caller, then proceed" } }
      ],
      finetune_transition_examples: [{ id: "fe-leadcapture-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "no cooling\nno heating\nsystem not working\nAC not working\nburning smell\nurgent repair\nemergency repair" }] }],
      display_position: { x: 2190, y: 726 }
    },
    {
      id: "node-verify-emergency", name: "verify_emergency_node", type: "conversation",
      instruction: { type: "prompt", text: "Ask user if this is an emergency." },
      edges: [
        { id: "edge-emergency-yes", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "If this is an emergency" } },
        { id: "edge-emergency-no", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "If this is not an emergency" } }
      ],
      display_position: { x: 2742, y: 1470 }
    },
    {
      id: "node-existing-customer", name: "existing_customer_node", type: "conversation",
      instruction: { type: "prompt", text: `## EXISTING CUSTOMER ENQUIRY\n\nThe caller is an existing customer calling about a current or past job.\n\n## YOUR GOAL\n\nCollect details so the team at ${companyName} can follow up.\n\n## DATA CAPTURE\n\nAsk naturally, one question at a time:\n1. A short description of their enquiry\n2. The caller's full name\n3. The best phone number to reach them\n4. If relevant: service address, date of job, technician name, job/invoice number\n\n## CLOSING\n\nConfirm back: "Just to confirm, I have your name as [name], best phone number as [phone], and your enquiry is regarding [description]. Is that all correct?"\n\nThen: "Perfect, I have passed all of that through to the team at ${companyName} and someone will be in touch shortly."` },
      edges: [
        { id: "edge-existing-resolved", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Enquiry Resolved" } },
        { id: "edge-existing-unresolved", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Enquiry Not Resolved\n" } }
      ],
      display_position: { x: 2742, y: 6 }
    },
    {
      id: "node-general-questions", name: "general_questions_node", type: "conversation",
      instruction: { type: "prompt", text: `## GENERAL FAQ HANDLING\n\nUse the company information to answer general questions.\n\n### PRICING QUESTIONS\n${pricingInstructions}\n\n### PAYMENT QUESTIONS\n${paymentMethods ? `We accept: ${paymentMethods}.` : 'Our team can go over payment options at the appointment.'}\n${financingAvailable === 'Yes' ? (financingDetails ? `Financing: ${financingDetails}` : 'We offer financing options.') : ''}\n\n### If the Question Cannot Be Answered\n"That's a great question, I want to make sure you get the right answer. Can I grab your name and number so someone from our team can follow up?"\nProceed to lead capture.` },
      edges: [
        { id: "edge-general-answered", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Question Answered Correctly" } },
        { id: "edge-general-further-help", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Further Assistance/Help" } },
        { id: "edge-general-lead", destination_node_id: "node-leadcapture", transition_condition: { type: "prompt", prompt: "Lead Generated" } }
      ],
      finetune_transition_examples: [
        { id: "fe-general-further-help", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "I need more help\nThis doesn't answer my question\nCan someone call me back about this\nI need a specialist\nI want to speak to someone who can help" }] },
        { id: "fe-general-lead", destination_node_id: "node-leadcapture", transcript: [{ role: "user", content: "I want to book\nCan someone come out\nI want to get a quote\nHow much would it cost\nI think I need a repair\nWhen can someone come out\nYes let's do that" }] }
      ],
      display_position: { x: 1662, y: 2190 }
    },
    {
      id: "node-callback", name: "callback_node", type: "conversation",
      instruction: { type: "prompt", text: `The caller is returning a missed call.\n\nSay: "Thanks for calling back! We may have been trying to reach you about a service enquiry."\n\nAsk: "Do you know what it was regarding?" Let them explain if they know.\n\nCollect:\n1. Full name, first and last\n2. Confirm their number: "Is the best number to reach you still [from_number]?"\n\nClose: "Perfect, I have let the team know you called and someone will be in touch shortly."` },
      edges: [{ id: "edge-callback-end", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details captured, close" } }],
      display_position: { x: 1662, y: 3000 }
    },
    {
      id: "node-spam-robocall", name: "spam_robocall_node", type: "conversation",
      instruction: { type: "static_text", text: "Say: \"Thank you for calling, have a great day.\" Then end the call." },
      edges: [{ id: "edge-spam-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 1662, y: 3300 }
    },
    {
      id: "node-transfer-call", name: "Transfer Call", type: "transfer_call",
      instruction: { type: "prompt", text: "Transferring your call now." },
      transfer_destination: { type: "predefined", number: transferNumber },
      transfer_option: { type: "cold_transfer", cold_transfer_mode: "sip_invite", enable_bridge_audio_cue: true, agent_detection_timeout_ms: 30000, show_transferee_as_caller: false },
      edge: { id: "edge-transfer-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3294, y: 2238 }
    },
    {
      id: "node-transfer-failed", name: "transfer_failed_node", type: "conversation",
      instruction: { type: "static_text", text: "Say:\n\"I'm sorry, it looks like that call didn't go through. All of our agents must be on the phone at the moment, let me take down your Full name and Phone number so I can have someone get back to you right away\"" },
      edges: [{ id: "edge-transfer-failed-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Proceed to End" } }],
      display_position: { x: 3846, y: 2166 }
    },
    {
      id: "node-ending", name: "Ending", type: "conversation",
      instruction: { type: "static_text", text: "Is there anything else I can help you with today?" },
      edges: [
        { id: "edge-ending-to-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "If not, say:\n\"Hope you have a great day, take care!\"" } },
        { id: "edge-ending-to-restart", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "If yes, return to " } }
      ],
      display_position: { x: 4398, y: 2190 }
    },
    {
      id: "node-end-call", name: "End Call", type: "end",
      instruction: { type: "prompt", text: "Politely end the call" },
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
  webhook_url: "https://n8n.syntharra.com/webhook/retell-hvac-webhook",
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
  timezone: timezone, industry_type: industryType
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
  timestamp: new Date().toISOString()
};