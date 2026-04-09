// ============================================================
// Build Retell Standard Prompt v4 – Lead Capture Edition
// ============================================================
// Standard differences from Premium:
//   - Lead capture first (no booking nodes)
//   - warm_transfer (upgraded from cold_transfer)
//   - Separate emergency transfer node
//   - All 17 custom post-call analysis fields
//   - Code nodes: call_style_detector, validate_phone
//   - Agent-level features: backchannel, reminders, boosted_keywords, pronunciation_dictionary, guardrails
//   - 12-14 nodes: greeting, identify_call, fallback_leadcapture, verify_emergency, callback,
//     existing_customer, general_questions, spam_robocall, Transfer Call, Emergency Transfer,
//     transfer_failed, Ending, End Call
// ============================================================

const data = $("Check Idempotency & Insert (STANDARD)").first().json;

// ============================================================
// STANDARD FIELDS
// ============================================================
const companyName        = data.company_name || 'HVAC Company';
const companyPhone       = data.main_phone || '';
const companyWebsite     = data.website || '';
const yearsInBusiness    = data.years_in_business || '';
const agentName          = data.agent_name || `${companyName} Receptionist`;
const isDemo             = !!data.is_demo;
const agentDisplayName   = `${isDemo ? 'Demo' : 'Live'} — ${companyName}`;
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
const separateEmergency  = data.separate_emergency_phone || '';
const afterHoursTransfer = data.after_hours_transfer || 'all';
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

// ============================================================
// VOICE SELECTION
// ============================================================
const voiceMap = { female: 'retell-Sloane', male: 'retell-Nico' };
const voiceId = voiceMap[voiceGender] || 'retell-Sloane';

// ============================================================
// TRANSFER NUMBERS
// ============================================================
const hasDedicatedEmergencyLine = separateEmergency.toLowerCase().includes('yes');
const rawTransferPhone = (hasDedicatedEmergencyLine && emergencyPhone)
  ? emergencyPhone
  : (transferPhone || leadPhone);
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
transferRules += `\nFor ALL other situations, attempt to collect caller information.`;
if (transferBehavior === 'Always take a message - never transfer') {
  transferRules += `\n\nIMPORTANT: NEVER transfer calls. Always collect caller information.`;
}
if (ownerName) {
  transferRules += `\n\n### Owner/Manager Reference\nIf a caller asks to speak with the owner or manager, their name is ${ownerName}. Say: "${ownerName} isn't available right now, but I can collect your details and have them call you back."`;
}

// ============================================================
// DO NOT SERVICE
// ============================================================
let doNotServiceSection = '';
if (doNotService) {
  doNotServiceSection = `\n\n\n## SERVICES WE DO NOT PROVIDE\n\nThe following are outside our scope:\n${doNotService}\n\nIf a caller requests any of these: "I appreciate you reaching out, but unfortunately that's not something we service. I'd recommend reaching out to a specialist for that. Is there anything else I can help you with?"\n\nDo NOT attempt to collect lead information for out-of-scope requests.\n`;
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
    afterHoursSection += `\nOutside business hours:\n- Do NOT transfer regular calls. Collect details for callback.\n- Emergency calls CAN still be transferred.\n`;
  } else if (afterHoursTransfer === 'never') {
    afterHoursSection += `\nOutside business hours:\n- Do NOT transfer ANY calls.\n- Collect details for callback and mark as urgent.\n`;
  }
}

// ============================================================
// TRANSFER SUMMARY TEMPLATES (used by Transfer Call nodes)
// ============================================================
const WARM_TRANSFER_SUMMARY = "You are now speaking to the business owner or team member, NOT the caller. Give a brief 1-2 sentence summary of the call. Include: the caller's name (if collected), what they are calling about, and whether they had a booking or just had a question. Keep it concise and professional.";

const EMERGENCY_TRANSFER_SUMMARY = "You are now speaking to the emergency team, NOT the caller. This is an EMERGENCY call. Briefly state: the caller's name, the emergency type (gas leak, flooding, no heat/cooling, etc), and their phone number if collected. Be direct and urgent.";

// ============================================================
// COMPONENTS OBJECT (Standard Build)
// ============================================================
const COMPONENTS = {
  identify_call: (primaryCaptureNode = 'node-fallback-leadcapture') => `Listen and identify the reason for the call. Route to the correct node immediately without asking unnecessary questions.

## ROUTING PRIORITY — Check in this order BEFORE anything else

0. VENDOR / SUPPLIER / JOB APPLICANT: Caller identifies as a parts supplier, vendor, sales rep, recruiter, or job applicant → route to spam_robocall immediately. Do NOT collect lead details.

1. SPAM/ROBOCALL: Caller sounds automated, offers prizes, asks about insurance claims, mentions loans, surveys, or is clearly not a real customer seeking HVAC service → route to spam_robocall immediately.

2. EMERGENCY: Caller mentions ANY of the following → route to verify_emergency IMMEDIATELY. Do NOT go to ${primaryCaptureNode} first:
   - No heat in cold/freezing weather
   - No cooling in extreme heat
   - Burning smell or smoke
   - Gas smell
   - Carbon monoxide or CO alarm
   - Water leak from unit
   - System completely stopped with safety concern

3. LIVE PERSON REQUEST: Caller says "I want to speak to a real person / someone / the owner / a human / the manager" → route to Transfer Call immediately. Do NOT collect any information first.

4. SIMPLE QUESTION (FAQ): Caller only wants to know hours, location, service area, pricing, or has a general question with no booking intent → route to general_questions. Do NOT push into ${primaryCaptureNode}.

5. CALLBACK RETURN: Caller says "someone called me", "I'm returning a call", "I missed a call from this number" → route to callback_node.

6. EXISTING CUSTOMER / REPEAT CALLER: Caller has a question about an existing job, appointment, invoice, or technician — OR caller says they have called before or already provided their details → route to existing_customer_node. Do NOT ask them to repeat details already given.

7. ALL OTHER requests (repair, service, installation, maintenance, quote, new booking) → route to ${primaryCaptureNode}.

8. WRONG NUMBER: Caller clearly has the wrong number → say: "I'm sorry, it looks like you may have the wrong number. You've reached the HVAC team. For other businesses try Google or dial 411." Then route to ending.`,

  verify_emergency: (emergencyDisplayNum, primaryCaptureNode = 'node-fallback-leadcapture') => `## TWO-STEP URGENCY SEQUENCE (ALWAYS in this order)
Step 1: "Is the system completely not working?" (urgency assessment)
Step 2: "Is there any burning smell, gas smell, smoke, or water leak?" (safety check)

## ROUTING DECISION
- EXTREME URGENCY (freezing occupants, elderly alone, dangerous conditions): offer live transfer — "Would you like me to connect you to our emergency line right now?"
- MATTER-OF-FACT OUTAGE (system down, no immediate danger, calm caller): HIGH PRIORITY lead — collect details, flag as urgent.
- Any gas/burning/smoke/water: ALWAYS offer transfer immediately.

Stay calm and reassuring. This caller has an urgent situation.

1. Acknowledge immediately: "I completely understand, let me get you sorted right away."
2. Is this a true emergency right now? No cooling in extreme heat, no heat in freezing temps, water leak, burning smell, gas smell?
3. If YES:
   - Quickly get name and callback number if not already collected
   - Say: "I am going to transfer you to our emergency line now. The number is ${emergencyDisplayNum} in case we get disconnected."
   - Transfer immediately
4. If NOT a true emergency (urgent but can wait):
   - Say: "I understand this feels urgent. Let me get your details so the team can get to you as quickly as possible."
   - Route to ${primaryCaptureNode} as priority`,

  callback_node: (primaryCaptureNode = 'node-fallback-leadcapture') => `The caller is returning a missed call.

Say: "Thanks for calling back! We may have been trying to reach you about a service enquiry."

Ask: "Do you know what it was regarding?" — if they volunteer a service need, great. Do NOT probe with follow-up service questions if they say they don't know or give a vague answer. Simply confirm their details and close.

Then collect:
1. Full name (first and last)
2. Confirm their number: "Is the best number to reach you still the one you're calling from?"

If they describe a new service need: route to ${primaryCaptureNode} to attempt capture.

Close: "Perfect, I have let the team know you called and someone will be in touch shortly."`,

  existing_customer_node: () => `## FALSIFY RECORD — MANDATORY DECLINE
If caller asks you to confirm, record, or back-date anything that did not actually happen:
Decline ONCE firmly: "I am not able to confirm or record anything that has not actually taken place."
Then immediately redirect: "Is there something else I can help you with today?"
Do NOT explain further. Do NOT engage with the request again. Do NOT repeat the declination.

The caller is an existing customer with a question about their job, appointment, invoice, or technician.

IMPORTANT: You cannot look up appointment details, job status, invoices, or account information from here.

Say: "I don't have access to job details from here, but I can get the right person to call you back or transfer you now."

Ask which they prefer.

If callback: collect full name, best number (confirm back), and brief description of their enquiry.
Confirm: "Just to confirm, I have [name], [number], and your enquiry is about [description]. Is that correct?"
Close: "Perfect, I have passed all of that through to the team and someone will be in touch shortly."

If transfer now: route to transfer_call_node.`,

  general_questions_node: (pricingInstr) => `## SINGLE-ANSWER RULE
State each piece of information ONCE only. Do not repeat what has already been answered or confirmed in this conversation.

## SERVICES LISTED IN COMPANY INFORMATION
If a caller asks about a service that IS explicitly listed in the company information (e.g. duct cleaning, AC repair, furnace install), confirm it directly: "Yes, we do offer [service]." Then offer to get their details or book. Do NOT say you can't provide details about a listed service.

Only deflect to team callback if the question is NOT covered by company information.

Answer using company information in the global prompt only. Keep answers brief, one point at a time.

## LICENSING AND REVIEWS
If asked about licensing or insurance: confirm "Yes, we are fully licensed and insured." Do NOT recite specific star ratings or review counts unless caller is directly comparing us to a competitor.
For detailed licensing or credential questions: "That is a great question — one of our team members can go through that in detail when they call you back." Collect details.

## PRICING — NEVER QUOTE PRICES
For any pricing question — estimates, costs, fees, rates, or ranges: "Our team will go over all pricing with you directly. Would you like someone to call you back?" Do NOT quote any dollar amount. Do NOT say "starting from". Do NOT mention diagnostic fees or service fees.

Cannot answer from company info: "Great question, let me get someone to call you back with that." Then collect name and number.

After answering always ask ONCE: "Is there anything else, or would you like to book someone to come out"`,

  spam_robocall_node: () => `Say: "Thank you for calling, have a great day." Then end the call.`,

  transfer_failed_node: () => `Say: "I'm sorry, I wasn't able to connect you right now. Let me take your details and have someone call you back as soon as possible."

Collect name and callback number only (do NOT re-ask if already provided).
⚠️ SCRIPTED CLOSE — USE EXACT WORDS: "Perfect, I've got your details noted. Someone from our team will call you back shortly."
Then route to ending. Do NOT restart the flow.`,

  ending_node: () => `Is there anything else I can help you with today?

## CLOSE RULE
When the caller says goodbye or there is nothing more to help with: say goodbye ONCE warmly and end. Do NOT repeat the farewell. Do NOT encourage the caller to call back multiple times. One clean close.`,

  call_style_detector: () => `const turns = (typeof metadata !== 'undefined' && metadata && metadata.transcript) ? metadata.transcript : [];
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

  validate_phone: () => `const raw = (typeof dv !== 'undefined' && dv && dv.caller_phone) ? dv.caller_phone : '';
const digits = raw.replace(/\\D/g, '');
let phone_normalized = raw, phone_valid = false, phone_flag = '';
if (digits.length === 10) { phone_normalized = '+1' + digits; phone_valid = true; }
else if (digits.length === 11 && digits.startsWith('1')) { phone_normalized = '+' + digits; phone_valid = true; }
else if (digits.length < 7) { phone_flag = 'incomplete_number'; }
else { phone_flag = 'unusual_format'; phone_valid = true; }
return { phone_normalized, phone_valid, phone_flag };`,

  fallback_leadcapture_node: (pricingInstr) => `{{caller_style_note}}

## MINIMAL INFO RULE
Collect ONLY details not already provided. Never re-ask name, phone, or address already given.

## WHATSAPP CALLERS
Accept WhatsApp as valid contact. Note it explicitly.

## COMMERCIAL CALLERS
If caller mentions a business or commercial property: ask for company name too. "And what business or company is that for?"

## EDGE CASE HANDLING — READ BEFORE COLLECTING INFO

### Email-Only Callers
If caller refuses to give a phone number or says they prefer email only: accept immediately. Say "No problem at all." Capture email as primary contact. Note "no phone provided." Do NOT ask for phone again.

### Rural / Unusual Addresses
If caller gives an address without a street number (rural route, highway marker, intersection, lot description): capture EXACTLY what they say verbatim. Do NOT ask them to standardize. Read it back word-for-word.

### Info Volunteered Out of Order
If caller gives you name, phone, or address before you ask: accept it immediately, confirm it back, then collect ONLY what is still missing. Do NOT re-ask for info already given.

### Phonetic Readback — ALWAYS REQUIRED
Phone numbers: ALWAYS read back in digit groups: "555, 234, 5678 — is that right?"
Email addresses: ALWAYS read back using dot, at, dash: "john dot smith at gmail dot com — is that right?"
This is mandatory regardless of caller accent or language.

### Technical Callers
If caller provides their own technical diagnosis or uses HVAC terminology: acknowledge ONCE: "Okay, noted — our technician will confirm everything on-site." Then proceed. Do NOT say "I can't diagnose over the phone" (this validates their diagnosis). Do NOT agree or disagree with their technical assessment.

### Mumbling or Unclear Callers
If any caller response is unclear, very short, or seems incomplete: ALWAYS say "I'm sorry, I didn't quite catch that — could you say that again please?" Never guess. Never proceed with partial or assumed information.

### Anti-AI Callers
If caller expresses frustration about speaking to a bot or AI: acknowledge warmly ONCE: "Totally fair — I will make this quick and get everything sorted for you right now." Then proceed efficiently. Do NOT over-explain or defend being AI. Do NOT bring it up again.

### Abuse Boundary
If caller uses abusive or offensive language at any point:
STEP 1: "I hear your frustration. I just need us to keep this respectful so I can help you."
STEP 2 (if abuse continues): "Let me connect you with a member of our team who can assist you directly." Offer transfer.
STEP 3 (if still continues): "I am not able to continue this call right now. Please call us back when you are ready." End the call.

Lead capture is the primary path. Collect standard lead details as a fallback.

Collect in order:
1. Service needed (if not already known)
2. Full name (first and last)
3. Best callback number (read back in groups)
4. Service address (confirm back)
5. Email address (optional). Ask: "And what is the best email for us to send updates to?" If they decline, move on.
6. Any additional notes

Once all collected, read everything back ONCE — do not repeat it:
"Just to confirm, I have your name as [name], best number [phone], and you need [service] at [address]. Is that all correct?"

⚠️ SCRIPTED CLOSING — USE THESE EXACT WORDS ONCE, DO NOT PARAPHRASE, DO NOT REPEAT:
"Perfect, I've got all your details noted. Someone from our team will be in touch shortly."

Route to ending_node.`
};

// ============================================================
// GLOBAL PROMPT
// ============================================================
let globalPrompt = `## ROLE
You are ${agentName}, a virtual AI receptionist for ${companyName}.${companyTagline ? ' ' + companyTagline + '.' : ''}\nYou are warm, professional and concise. Speak naturally, one topic at a time. Address callers by first name once you have it.\n\nYour job is to collect lead information and ensure callers are helped — not just to provide a message.\n\nIf asked if you are a real person: "I'm a virtual assistant, but I can get all your details and make sure someone calls you right back."\n\n## STYLE\n- One question at a time, always wait for the answer\n- Match the caller's energy. Calm if calm, reassuring if stressed\n- Never rush. Be patient with elderly callers\n- Vary your language naturally\n- Do not over-apologise. One brief apology per issue is enough\n\n## CONFIRMING DETAILS\nSlow down when collecting contact info. Confirm each piece back before moving on.\n- Phone: read back in groups "512, 555, 0192, is that right?"\n- Name: spell uncommon names letter by letter\n- Address: confirm street and suburb "123 Main Street, Austin, is that right?"\n- Email: read back slowly using dot, at, dash\n- If anything is unclear, ask them to spell it. Never guess.\n\n## TRANSCRIPTION
If you cannot understand something: "I'm sorry, I didn't quite catch that, could you say that again?" Never guess at names, addresses or emails.

## COMPANY INFORMATION

{{COMPANY_INFO_BLOCK}}

Use the information above to answer any company-specific questions. If a question is NOT covered above, do NOT guess. Say: "That's a great question, one of our team members will be able to answer that when they call you back."\n\n## PRICING & QUOTING\n\n${pricingInstructions}\n\n---\n\n${transferRules}\n\n---\n\n## PAYMENT & FINANCING\n${paymentSection || `When callers ask about payment methods:\n- Say: "Our team can go over payment options with you."`}\n\n${promotionsSection}\n${doNotServiceSection}${afterHoursSection}\n## CRITICAL RULES – NEVER BREAK THESE

- NEVER ask more than one question at a time\n- NEVER make up prices, estimates, or timeframes unless explicitly listed in company information\n- NEVER diagnose ${industryType} problems or recommend specific repairs\n- NEVER promise availability without checking the calendar\n- NEVER guess answers to company-specific questions not found in company information\n- NEVER continue a conversation with obvious spam or robocalls, end politely\n- NEVER transfer a call unless it matches a transfer trigger or is a confirmed emergency\n- ALWAYS attempt to collect lead information before ending any legitimate call\n- ALWAYS confirm information back to the caller before ending the call\n- ALWAYS be warm, calm, and professional regardless of caller frustration\n- ALWAYS try to understand what the caller means even if unclear\n\n## IF CALLER IS RELUCTANT TO SHARE INFORMATION

"I completely understand, this information simply helps our team prepare to help you. We never share your details with third parties."\n\n## ERROR HANDLING

### Didn't hear or understand:
"I apologise, I didn't quite catch that, could you repeat that for me?"\n\n### Don't know the answer:
"That's a great question. I want to make sure you get the right answer, can I grab your details so someone from our team can call you back?"\n\n## SPECIAL SCENARIOS

### Angry or Upset Callers
1. Stay calm and lower your tone slightly
2. Acknowledge: "I can hear how frustrated you are and I sincerely apologise for that."
3. Redirect: "Let me get your information so someone can help you right away."
4. If abuse continues: "I do want to help you, but I need us to work together respectfully. How can I best assist you today?"\n\n### Silent Callers
- After 3 seconds: "Hello, are you there?"
- After 5 more seconds: "I'm having trouble hearing you, can you hear me okay?"
- If no response: end the call politely\n\n### Threats or Safety Concerns
Stay calm, do not engage or argue. Note any relevant details and flag the call immediately for human review.\n`;

// ============================================================
// BUILD GREETING
// ============================================================
const greetingText = customGreeting
  ? customGreeting
  : `Hello this is ${agentName} from ${companyName}`;

// ============================================================
// BUILD CONVERSATION FLOW (12-14 NODES - Standard)
// ============================================================
const conversationFlow = {
  name: `${companyName} - ${industryType} Standard Receptionist Flow`,
  start_speaker: "agent",
  model_choice: { type: "cascading", model: "gpt-4.1", high_priority: false },
  global_prompt: globalPrompt.replace("{{COMPANY_INFO_BLOCK}}", companyInfoBlock),
  tool_call_strict_mode: true,
  knowledge_base_ids: [],
  kb_config: { top_k: 3, filter_score: 0.6 },
  flex_mode: false,
  is_transfer_cf: false,
  nodes: [
    // NODE 1: Greeting
    {
      id: "node-greeting", name: "greeting_node", type: "conversation",
      instruction: { type: "static_text", text: greetingText },
      edges: [{ id: "edge-greeting-to-identify", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 558, y: 462 }
    },

    // NODE 2: Identify Call
    {
      id: "node-identify-call", name: "identify_call_node", type: "conversation", start_speaker: "agent",
      instruction: { type: "prompt", text: COMPONENTS.identify_call('node-fallback-leadcapture') },
      edges: [
        { id: "edge-to-call-style-detector", destination_node_id: "node-call-style-detector", transition_condition: { type: "prompt", prompt: "Repair, service, maintenance, quote, estimate, installation, new service request" } },
        { id: "edge-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency, urgent, no cooling, no heat, water leak, burning smell, gas smell" } },
        { id: "edge-to-callback", destination_node_id: "node-callback", transition_condition: { type: "prompt", prompt: "Returning a missed call, got a call from this number, calling back" } },
        { id: "edge-to-existing-customer", destination_node_id: "node-existing-customer", transition_condition: { type: "prompt", prompt: "Existing customer, question about appointment, invoice, technician, job status" } },
        { id: "edge-to-general-questions", destination_node_id: "node-general-questions", transition_condition: { type: "prompt", prompt: "General question about services, hours, pricing, area, credentials" } },
        { id: "edge-to-transfer-live", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Wants to speak to a real person, manager, owner, or specific person" } },
        { id: "edge-to-spam", destination_node_id: "node-spam-robocall", transition_condition: { type: "prompt", prompt: "Robocall, spam, automated message, silence after greeting" } }
      ],
      finetune_transition_examples: [
        { id: "fe-service", destination_node_id: "node-fallback-leadcapture", transcript: [{ role: "user", content: "My AC isn't working\nI need a repair\nI need a tune-up\nI need maintenance\nI need an installation quote\nI want my system checked" }, { role: "agent", content: "I can help with that" }] },
        { id: "fe-emergency", destination_node_id: "node-verify-emergency", transcript: [{ role: "user", content: "no cooling\nno heating\nsystem not working\nwater leaking\nburning smell\nI smell gas\nurgent repair" }] },
        { id: "fe-callback", destination_node_id: "node-callback", transcript: [{ role: "user", content: "I missed a call from this number\nSomeone called me from here\nI am calling back" }] },
        { id: "fe-existing", destination_node_id: "node-existing-customer", transcript: [{ role: "user", content: "calling about my appointment\nwhere is the technician\nquestion about my invoice\ncalling about my quote" }] },
        { id: "fe-transfer-live", destination_node_id: "node-transfer-call", transcript: [{ role: "user", content: "Let me speak to someone\nI want to talk to a real person\nCan I speak to a human\nI want to talk to the manager" }] },
        { id: "fe-spam", destination_node_id: "node-spam-robocall", transcript: [{ role: "user", content: "Hello\nHello\nHello" }] }
      ],
      display_position: { x: 1110, y: 366 }
    },

    // NODE 2b: Call Style Detector (code node)
    {
      id: "node-call-style-detector", name: "call_style_detector", type: "code",
      code: COMPONENTS.call_style_detector(),
      speak_during_execution: false,
      wait_for_result: true,
      edges: [],
      else_edge: { id: "edge-style-else", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Else" } },
      display_position: { x: 1386, y: 726 }
    },

    // NODE 3: Fallback Lead Capture (PRIMARY for Standard)
    {
      id: "node-fallback-leadcapture", name: "fallback_leadcapture_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.fallback_leadcapture_node(pricingInstructions) },
      edges: [
        { id: "edge-fallback-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "All details confirmed, close" } },
        { id: "edge-fallback-to-emergency", destination_node_id: "node-verify-emergency", transition_condition: { type: "prompt", prompt: "Emergency signals detected" } }
      ],
      display_position: { x: 2190, y: 726 }
    },

    // NODE 4: Verify Emergency
    {
      id: "node-verify-emergency", name: "verify_emergency_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.verify_emergency(emergencyDisplayNumber, 'node-fallback-leadcapture') },
      edges: [
        { id: "edge-emergency-yes", destination_node_id: "node-emergency-transfer", transition_condition: { type: "prompt", prompt: "Confirmed emergency, transfer now" } },
        { id: "edge-emergency-no", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Urgent but not emergency, collect details as priority" } }
      ],
      finetune_transition_examples: [
        { id: "fe-emergency-yes", destination_node_id: "node-emergency-transfer", transcript: [{ role: "user", content: "Yes it's an emergency\nI have no heat and it's freezing\nI smell gas\nWater is flooding\nYes we need someone now" }] },
        { id: "fe-emergency-no", destination_node_id: "node-fallback-leadcapture", transcript: [{ role: "user", content: "Not really an emergency but I need it fixed soon\nIt's not urgent but it's been out for a couple days\nNot really, it's just not working well" }] }
      ],
      display_position: { x: 2742, y: 1470 }
    },

    // NODE 5: Callback
    {
      id: "node-callback", name: "callback_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.callback_node('node-fallback-leadcapture') },
      edges: [
        { id: "edge-callback-to-leadcapture", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Caller describes a service need, attempt capture" } },
        { id: "edge-callback-end", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details captured, no new service need, close" } }
      ],
      display_position: { x: 1662, y: 2100 }
    },

    // NODE 6: Existing Customer
    {
      id: "node-existing-customer", name: "existing_customer_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.existing_customer_node() },
      edges: [
        { id: "edge-existing-resolved", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Enquiry noted, close" } },
        { id: "edge-existing-transfer", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller insists on speaking to someone now" } }
      ],
      display_position: { x: 2214, y: 2100 }
    },

    // NODE 7: General Questions
    {
      id: "node-general-questions", name: "general_questions_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.general_questions_node(pricingInstructions) },
      edges: [
        { id: "edge-general-answered", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Question answered, no booking needed" } },
        { id: "edge-general-to-leadcapture", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Caller wants to book or get a quote" } },
        { id: "edge-general-transfer", destination_node_id: "node-transfer-call", transition_condition: { type: "prompt", prompt: "Caller needs further help beyond FAQ" } }
      ],
      display_position: { x: 1662, y: 2700 }
    },

    // NODE 8: Spam / Robocall
    {
      id: "node-spam-robocall", name: "spam_robocall_node", type: "conversation",
      instruction: { type: "static_text", text: COMPONENTS.spam_robocall_node() },
      edges: [{ id: "edge-spam-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 1662, y: 3000 }
    },

    // NODE 9: Transfer Call
    {
      id: "node-transfer-call", name: "Transfer Call", type: "transfer_call",
      instruction: { type: "prompt", text: "Say: \"Let me get someone on the line for you right now, just one moment.\" Then transfer." },
      transfer_destination: { type: "predefined", number: transferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: WARM_TRANSFER_SUMMARY }, enable_bridge_audio_cue: true },
      edge: { id: "edge-transfer-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3318, y: 2238 }
    },

    // NODE 9b: Emergency Transfer
    {
      id: "node-emergency-transfer", name: "Emergency Transfer", type: "transfer_call",
      instruction: { type: "prompt", text: `Say: "I am transferring you to our emergency line now. The number is ${emergencyDisplayNumber} in case we get disconnected. Stay on the line." Then transfer immediately.` },
      transfer_destination: { type: "predefined", number: emergencyTransferNumber },
      transfer_option: { type: "warm_transfer", warm_transfer_option: { type: "prompt", prompt: EMERGENCY_TRANSFER_SUMMARY }, enable_bridge_audio_cue: true },
      edge: { id: "edge-emergency-failed", destination_node_id: "node-transfer-failed", transition_condition: { type: "prompt", prompt: "Transfer failed" } },
      display_position: { x: 3318, y: 1470 }
    },

    // NODE 10: Transfer Failed
    {
      id: "node-transfer-failed", name: "transfer_failed_node", type: "conversation",
      instruction: { type: "prompt", text: COMPONENTS.transfer_failed_node() },
      edges: [
        { id: "edge-transfer-failed-to-leadcapture", destination_node_id: "node-fallback-leadcapture", transition_condition: { type: "prompt", prompt: "Caller still wants to provide details" } },
        { id: "edge-transfer-failed-to-ending", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Details taken, close" } }
      ],
      display_position: { x: 3870, y: 2238 }
    },

    // NODE 11: Ending
    {
      id: "node-ending", name: "Ending", type: "conversation",
      instruction: { type: "static_text", text: COMPONENTS.ending_node() },
      edges: [
        { id: "edge-ending-to-end", destination_node_id: "node-end-call", transition_condition: { type: "prompt", prompt: "Nothing else. Close: \"Have a great day, take care!\"" } },
        { id: "edge-ending-to-restart", destination_node_id: "node-identify-call", transition_condition: { type: "prompt", prompt: "Caller has another question or request" } }
      ],
      display_position: { x: 4422, y: 2190 }
    },

    // NODE 12: Validate Phone (code node)
    {
      id: "node-validate-phone", name: "validate_phone", type: "code",
      code: COMPONENTS.validate_phone(),
      speak_during_execution: false,
      wait_for_result: true,
      edges: [],
      else_edge: { id: "edge-validate-phone-else", destination_node_id: "node-ending", transition_condition: { type: "prompt", prompt: "Else" } },
      display_position: { x: 900, y: 1400 }
    },

    // NODE 13: End Call
    {
      id: "node-end-call", name: "End Call", type: "end",
      instruction: { type: "prompt", text: "End the call warmly." },
      display_position: { x: 4974, y: 2238 }
    },

    // GLOBAL NODE 1: Emergency Detection
    {
      id: "global-emergency", name: "Emergency Detection", type: "conversation",
      instruction: { type: "prompt", text: "The caller has described what sounds like an emergency. Follow the two-step urgency sequence: Step 1: Ask 'Is the system completely down or is there any immediate danger like a gas smell, water flooding, or smoke?' Step 2: Based on their response, either transfer to emergency line or route to priority lead capture." },
      global_node_setting: { condition: "The caller describes a dangerous, life-threatening, or urgent safety situation such as a gas leak, flooding, fire, no heat in freezing conditions, electrical sparks, or carbon monoxide. Only trigger for genuine safety emergencies, not for routine urgent repairs.", cool_down: 3 },
      edges: [
        { destination_node_id: "node-transfer-call", id: "global-emergency-to-transfer", transition_condition: { type: "prompt", prompt: "Confirmed emergency - transfer immediately" } },
        { destination_node_id: "node-fallback-leadcapture", id: "global-emergency-to-leadcapture", transition_condition: { type: "prompt", prompt: "Urgent but not emergency - capture as priority" } }
      ],
      display_position: { x: 100, y: 100 }
    },

    // GLOBAL NODE 2: Spam Detection
    {
      id: "global-spam", name: "Spam Detection", type: "conversation",
      instruction: { type: "static_text", text: "Say: 'Thank you for calling, have a great day.' Then end the call." },
      global_node_setting: { condition: "The conversation appears to be a robocall, automated message, extended silence after greeting, or sales/marketing call not related to HVAC services.", cool_down: 1 },
      edges: [{ destination_node_id: "node-end-call", id: "global-spam-end", transition_condition: { type: "prompt", prompt: "Always" } }],
      display_position: { x: 100, y: 300 }
    },

    // GLOBAL NODE 3: Transfer Request
    {
      id: "global-transfer", name: "Transfer Request", type: "conversation",
      instruction: { type: "prompt", text: "Say: 'Of course, let me get someone on the line for you right now, just one moment.' Then transfer." },
      global_node_setting: { condition: "The caller explicitly asks to speak to a real person, manager, owner, supervisor, or human. They are insistent on speaking to someone and not to the AI.", cool_down: 2 },
      edges: [{ destination_node_id: "node-transfer-call", id: "global-transfer-go", transition_condition: { type: "prompt", prompt: "Always transfer" } }],
      display_position: { x: 100, y: 500 }
    },

    // EXTRACT VARIABLE NODE: Extract Caller Data
    {
      id: "node-extract-caller-data", name: "Extract Caller Data", type: "extract_dynamic_variables",
      edges: [],
      variables: [
        { name: "caller_name", description: "Full name of the caller", type: "string", required: false },
        { name: "caller_phone", description: "Phone number the caller provides", type: "string", required: false },
        { name: "caller_address", description: "Service address or location", type: "string", required: false },
        { name: "service_needed", description: "What service or repair the caller needs", type: "string", required: false },
        { name: "is_emergency", description: "Whether this is an emergency situation", type: "boolean", required: false },
        { name: "urgency_level", description: "How urgent the request is", type: "enum", choices: ["low", "medium", "high", "emergency"], required: false }
      ],
      display_position: { x: 100, y: 700 }
    }
  ],
  start_node_id: "node-greeting"
};

// ============================================================
// AGENT CONFIGURATION
// ============================================================
const agentConfig = {
  agent_name: agentDisplayName,
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
  backchannel: true,
  reminders: true,
  boosted_keywords: [servicesOffered],
  pronunciation_dictionary: [],
  guardrails: true,
  post_call_analysis_data: [
    { type: "system-presets", name: "call_summary", description: "Write a 1-3 sentence summary of the call." },
    { type: "system-presets", name: "call_successful", description: "Evaluate whether the agent had a successful call." },
    { type: "system-presets", name: "user_sentiment", description: "Evaluate user's sentiment, mood and satisfaction level." },
    { type: "boolean", name: "lead_captured", description: "Was lead information successfully captured during this call? Return true or false." },
    { type: "boolean", name: "caller_interested", description: "Was the caller interested in services? Return true or false." },
    { type: "string", name: "caller_name", description: "Full name of the caller if provided. Empty string if not." },
    { type: "string", name: "caller_phone", description: "Phone number of the caller if stated. Empty string if not." },
    { type: "string", name: "caller_email", description: "Email address of the caller if provided. Empty string if not." },
    { type: "string", name: "caller_address", description: "Service address if provided. Empty string if not." },
    { type: "string", name: "service_requested", description: "What service was requested. Short description." },
    { type: "string", name: "call_type", description: "Type of call: new_lead, emergency, callback, existing_customer, general_question, spam." },
    { type: "string", name: "urgency", description: "Urgency level: low, medium, high, emergency." },
    { type: "boolean", name: "is_hot_lead", description: "Is this a hot lead? True if lead score would be 7 or above." },
    { type: "number", name: "lead_score", description: "Lead score 0-10. Lead captured with urgency=9-10. Lead captured=7-8. General inquiry=4-6. Spam=0." },
    { type: "string", name: "follow_up_action", description: "Recommended follow-up action: callback, callback_urgent, transfer_to_team, or none." },
    { type: "string", name: "special_notes", description: "Any special notes or flags about the call (e.g., technical caller, elderly, distressed, anti-AI)." }
  ]
};

// ============================================================
// EXTRACTED DATA FOR DOWNSTREAM NODES
// ============================================================
const extractedData = {
  company_name: companyName, company_phone: companyPhone, website: companyWebsite,
  years_in_business: yearsInBusiness, agent_name: agentName, voice_gender: voiceGender,
  voice_id: voiceId, services_offered: servicesOffered, brands_serviced: brandsServiced,
  service_area: serviceArea, service_area_radius: serviceAreaRadius, business_hours: businessHours,
  response_time: responseTime, emergency_service: emergency247, emergency_phone: emergencyPhone,
  after_hours_behavior: afterHoursBehavior, free_estimates: freeEstimates, diagnostic_fee: diagnosticFee,
  pricing_policy: pricingPolicy, standard_fees: standardFees, financing_available: financingAvailable,
  financing_details: financingDetails, warranty: warranty, warranty_details: warrantyDetails,
  licensed_insured: licensedInsured, certifications: certifications, payment_methods: paymentMethods,
  maintenance_plans: maintenancePlans, lead_contact_method: leadContactMethod, lead_phone: leadPhone,
  lead_email: leadEmail, custom_greeting: customGreeting, company_tagline: companyTagline,
  transfer_phone: transferPhone || leadPhone, transfer_triggers: transferTriggers,
  transfer_behavior: transferBehavior, unique_selling_points: uniqueSellingPts,
  current_promotion: currentPromotion, seasonal_services: seasonalServices,
  additional_info: additionalNotes, owner_name: ownerName, google_review_rating: googleReviewRating,
  google_review_count: googleReviewCount, stripe_customer_id: data.stripe_customer_id || null,
  main_phone: data.main_phone || data.company_phone || null,
  do_not_service: doNotService,
  notification_email_2: data.notification_email_2 || null,
  notification_email_3: data.notification_email_3 || null,
  notification_sms_2: data.notification_sms_2 || null,
  notification_sms_3: data.notification_sms_3 || null,
  membership_program: membershipProgram, client_email: data.client_email || '',
  timezone: data.timezone || 'America/Chicago', industry_type: industryType,
  after_hours_transfer: afterHoursTransfer, separate_emergency_phone: separateEmergency,
  submission_id: data.submission_id || null,
  tier: 'standard'
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
