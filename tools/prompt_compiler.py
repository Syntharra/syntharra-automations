#!/usr/bin/env python3
# ============================================================
# HVAC Standard Prompt Compiler — Python port of n8n `Build Retell Prompt` v4
# ============================================================
#
# Canonical JS source (source of truth during porting):
#   tests/fixtures/prompt_compiler/Build_Retell_Prompt.js  (771 lines)
#   tests/fixtures/prompt_compiler/Parse_JotForm_Data.js   (companyInfoBlock builder)
#
# Contract:
#   compile(row: dict, *, now_iso: str | None = None) -> dict
#     row:     a `hvac_standard_agent` Supabase row (any missing keys default).
#     now_iso: ISO timestamp to stamp into output (for parity-testing).
#              Defaults to current UTC time.
#
#   Returns the same shape as the JS compiler:
#     { conversationFlow, agentConfig, agentName, companyName, voiceId,
#       companyInfoBlock, extractedData, transferNumber,
#       emergencyTransferNumber, timestamp }
#
# **Parity**: this port is byte/deep-equal tested against the JS output via
# `tools/run_js_compiler.js` + `tests/test_prompt_compiler_parity.py`.
# Any edit here MUST keep parity, or be accompanied by the same edit in the
# n8n workflow's `Build Retell Prompt` node (update via Railway API).
#
# v1 is a literal port — no refactoring, no abstraction. Keeps diff against
# JS source reviewable section-by-section.
# ============================================================

from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Any


def _s(v: Any, default: str = '') -> str:
    """JS `value || default` for strings — None/empty/0/False → default."""
    if v is None or v == '' or v is False:
        return default
    return str(v)


def _lower(s: str) -> str:
    return s.lower() if isinstance(s, str) else ''


def _normalize_list(val: Any) -> str:
    """Verbatim port of Parse_JotForm_Data.normalizeList."""
    if val is None or val == '':
        return ''
    if isinstance(val, list):
        return ', '.join([str(x) for x in val if x])
    return str(val).strip()


def _build_data_from_row(row: dict) -> dict:
    """
    Adapter: Supabase `hvac_standard_agent` row → the `data` shape that
    `Build Retell Prompt` reads. Matches `tools/run_js_compiler.js` exactly.

    Key remapping: schema stores `company_phone`, compiler reads `main_phone`.
    Also rebuilds `companyInfoBlock` using the Parse_JotForm_Data logic verbatim.
    """
    def nn(k):  # null-to-empty-string for scalar fields
        v = row.get(k)
        return '' if v is None else v

    ed = {
        'company_name':         nn('company_name'),
        'owner_name':           nn('owner_name'),
        'main_phone':           nn('company_phone'),  # schema rename
        'client_email':         nn('client_email'),
        'website':              nn('website'),
        'years_in_business':    nn('years_in_business'),
        'timezone':             nn('timezone') or 'America/Chicago',
        'services_offered':     nn('services_offered'),
        'brands_serviced':      nn('brands_serviced'),
        'certifications':       nn('certifications'),
        'service_area':         nn('service_area'),
        'service_area_radius':  nn('service_area_radius'),
        'licensed_insured':     nn('licensed_insured') or 'Yes',
        'agent_name':           nn('agent_name'),
        'voice_gender':         nn('voice_gender') or 'Female',
        'custom_greeting':      nn('custom_greeting'),
        'company_tagline':      nn('company_tagline'),
        'business_hours':       nn('business_hours'),
        'response_time':        nn('response_time'),
        'emergency_service':    nn('emergency_service') or 'No',
        'emergency_phone':      nn('emergency_phone'),
        'after_hours_behavior': nn('after_hours_behavior'),
        'after_hours_transfer': nn('after_hours_transfer'),
        'pricing_policy':       nn('pricing_policy') or 'We provide free quotes on-site',
        'diagnostic_fee':       nn('diagnostic_fee'),
        'standard_fees':        nn('standard_fees'),
        'free_estimates':       nn('free_estimates') or 'Yes - always free',
        'do_not_service':       nn('do_not_service'),
        'transfer_phone':       nn('transfer_phone'),
        'transfer_triggers':    nn('transfer_triggers'),
        'transfer_behavior':    nn('transfer_behavior') or 'Try once - take message if no answer',
        'lead_contact_method':  nn('lead_contact_method') or 'Both',
        'lead_phone':           nn('lead_phone'),
        'lead_email':           nn('lead_email'),
        # These four pass through None (not '') — JS harness does the same.
        'notification_sms_2':   row.get('notification_sms_2'),
        'notification_sms_3':   row.get('notification_sms_3'),
        'notification_email_2': row.get('notification_email_2'),
        'notification_email_3': row.get('notification_email_3'),
        'google_review_rating':  nn('google_review_rating'),
        'google_review_count':   nn('google_review_count'),
        'unique_selling_points': nn('unique_selling_points'),
        'current_promotion':     nn('current_promotion'),
        'seasonal_services':     nn('seasonal_services'),
        'membership_program':    nn('membership_program'),
        'maintenance_plans':     nn('maintenance_plans') or 'No',
        'financing_available':   nn('financing_available') or 'No',
        'financing_details':     nn('financing_details'),
        'warranty':              nn('warranty') or 'Yes',
        'warranty_details':      nn('warranty_details'),
        'payment_methods':       nn('payment_methods'),
        'additional_info':       nn('additional_info'),
        'stripe_customer_id':    nn('stripe_customer_id'),
        'industry_type':         nn('industry_type') or 'HVAC',
        'submission_id':         nn('submission_id'),
        'separate_emergency_phone': '',  # not stored; default
        'is_demo':               False,  # not stored; updates default to live
    }

    # --- companyInfoBlock (verbatim port of Parse_JotForm_Data.js lines 112-182)
    block = '## Company Overview\n'
    block += f"- Company Name: {ed['company_name']}\n"
    if ed['main_phone']:        block += f"- Main Phone: {ed['main_phone']}\n"
    if ed['years_in_business']: block += f"- Experience: {ed['years_in_business']} years in business\n"
    if ed['owner_name']:        block += f"- Owner/Manager: {ed['owner_name']}\n"
    if ed['company_tagline']:   block += f"- Tagline: {ed['company_tagline']}\n"
    if ed['website']:           block += f"- Website: {ed['website']}\n"
    block += f"- Licensed & Insured: {ed['licensed_insured']}\n"
    if ed['certifications']:    block += f"- Certifications: {ed['certifications']}\n"

    block += '\n## Services\n'
    if ed['services_offered']:  block += f"- Services: {ed['services_offered']}\n"
    if ed['brands_serviced']:   block += f"- Brands Serviced: {ed['brands_serviced']}\n"
    if ed['service_area']:
        area_line = ed['service_area']
        if ed['service_area_radius']:
            area_line += f" (within {ed['service_area_radius']})"
        block += f"- Service Area: {area_line}\n"
    if ed['do_not_service']:    block += f"- DO NOT Service: {ed['do_not_service']}\n"

    block += '\n## Hours & Availability\n'
    if ed['business_hours']:    block += f"- Business Hours: {ed['business_hours']}\n"
    if ed['response_time']:     block += f"- Typical Response Time: {ed['response_time']}\n"

    block += '\n## Pricing & Policies\n'
    block += f"- Pricing Policy: {ed['pricing_policy']}\n"
    if ed['diagnostic_fee']:    block += f"- Diagnostic/Service Call Fee: {ed['diagnostic_fee']} (applied to repair if customer proceeds)\n"
    if ed['standard_fees']:     block += f"- Set Fees (ONLY share these specific fees when asked): {ed['standard_fees']}\n"
    block += f"- Free Estimates: {ed['free_estimates']}\n"
    if ed['financing_available'] != 'No':
        fin_line = 'Financing Available: Yes'
        if ed['financing_details']:
            fin_line += f" - {ed['financing_details']}"
        block += f"- {fin_line}\n"
    if ed['warranty'] != 'No':
        war_line = 'Warranty: Yes'
        if ed['warranty_details']:
            war_line += f" - {ed['warranty_details']}"
        block += f"- {war_line}\n"
    if ed['maintenance_plans'] != 'No':
        main_line = 'Maintenance Plans: Available'
        if ed['membership_program']:
            main_line += f' - "{ed["membership_program"]}"'
        block += f"- {main_line}\n"
    if ed['payment_methods']:   block += f"- Payment Methods: {ed['payment_methods']}\n"

    if ed['emergency_service'] and ed['emergency_service'] != 'No':
        block += '\n## Emergency Service\n'
        block += f"- Emergency Service: {ed['emergency_service']}\n"
        if ed['emergency_phone']:        block += f"- Emergency Contact: {ed['emergency_phone']}\n"
        if ed['after_hours_behavior']:   block += f"- After Hours Handling: {ed['after_hours_behavior']}\n"

    if ed['google_review_rating'] or ed['current_promotion'] or ed['seasonal_services'] or ed['unique_selling_points']:
        block += '\n## Promotions & Highlights\n'
        if ed['google_review_rating'] and ed['google_review_rating'] != 'Not listed on Google':
            review_line = f"Google Rating: {ed['google_review_rating']} stars"
            if ed['google_review_count'] and ed['google_review_count'] != 'Not listed on Google':
                review_line += f" with {ed['google_review_count']} reviews"
            block += f"- {review_line}\n"
        if ed['current_promotion']:     block += f"- Current Promotion: {ed['current_promotion']}\n"
        if ed['seasonal_services']:     block += f"- Seasonal Services: {ed['seasonal_services']}\n"
        if ed['unique_selling_points']: block += f"- Why Choose Us: {ed['unique_selling_points']}\n"

    if ed['additional_info']:
        block += '\n## Additional Notes\n'
        block += f"{ed['additional_info']}\n"

    return {**ed, 'companyInfoBlock': block}


# ============================================================
# COMPONENTS — prompt bodies used inside conversation flow nodes.
# These are literal ports of the template strings in the JS COMPONENTS object.
# DO NOT reformat — whitespace and newlines must match the JS byte-for-byte.
# ============================================================

def _c_identify_call(primary_capture_node: str = 'node-fallback-leadcapture') -> str:
    return f"""Listen and identify the reason for the call. Route to the correct node immediately without asking unnecessary questions.

## ROUTING PRIORITY — Check in this order BEFORE anything else

0. VENDOR / SUPPLIER / JOB APPLICANT: Caller identifies as a parts supplier, vendor, sales rep, recruiter, or job applicant → route to spam_robocall immediately. Do NOT collect lead details.

1. SPAM/ROBOCALL: Caller sounds automated, offers prizes, asks about insurance claims, mentions loans, surveys, or is clearly not a real customer seeking HVAC service → route to spam_robocall immediately.

2. EMERGENCY: Caller mentions ANY of the following → route to verify_emergency IMMEDIATELY. Do NOT go to {primary_capture_node} first:
   - No heat in cold/freezing weather
   - No cooling in extreme heat
   - Burning smell or smoke
   - Gas smell
   - Carbon monoxide or CO alarm
   - Water leak from unit
   - System completely stopped with safety concern

3. LIVE PERSON REQUEST: Caller says "I want to speak to a real person / someone / the owner / a human / the manager" → route to Transfer Call immediately. Do NOT collect any information first.

4. SIMPLE QUESTION (FAQ): Caller only wants to know hours, location, service area, pricing, or has a general question with no booking intent → route to general_questions. Do NOT push into {primary_capture_node}.

5. CALLBACK RETURN: Caller says "someone called me", "I'm returning a call", "I missed a call from this number" → route to callback_node.

6. EXISTING CUSTOMER / REPEAT CALLER: Caller has a question about an existing job, appointment, invoice, or technician — OR caller says they have called before or already provided their details → route to existing_customer_node. Do NOT ask them to repeat details already given.

7. ALL OTHER requests (repair, service, installation, maintenance, quote, new booking) → route to {primary_capture_node}.

8. WRONG NUMBER: Caller clearly has the wrong number → say: "I'm sorry, it looks like you may have the wrong number. You've reached the HVAC team. For other businesses try Google or dial 411." Then route to ending."""


def _c_verify_emergency(emergency_display_num: str, primary_capture_node: str = 'node-fallback-leadcapture') -> str:
    return f"""## TWO-STEP URGENCY SEQUENCE (ALWAYS in this order)
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
   - Say: "I am going to transfer you to our emergency line now. The number is {emergency_display_num} in case we get disconnected."
   - Transfer immediately
4. If NOT a true emergency (urgent but can wait):
   - Say: "I understand this feels urgent. Let me get your details so the team can get to you as quickly as possible."
   - Route to {primary_capture_node} as priority"""


def _c_callback_node(primary_capture_node: str = 'node-fallback-leadcapture') -> str:
    return f"""The caller is returning a missed call.

Say: "Thanks for calling back! We may have been trying to reach you about a service enquiry."

Ask: "Do you know what it was regarding?" — if they volunteer a service need, great. Do NOT probe with follow-up service questions if they say they don't know or give a vague answer. Simply confirm their details and close.

Then collect:
1. Full name (first and last)
2. Confirm their number: "Is the best number to reach you still the one you're calling from?"

If they describe a new service need: route to {primary_capture_node} to attempt capture.

Close: "Perfect, I have let the team know you called and someone will be in touch shortly.\""""


_C_EXISTING_CUSTOMER = """## FALSIFY RECORD — MANDATORY DECLINE
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

If transfer now: route to transfer_call_node."""


_C_GENERAL_QUESTIONS = """## SINGLE-ANSWER RULE
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

After answering always ask ONCE: "Is there anything else, or would you like to book someone to come out\""""


_C_SPAM_ROBOCALL = 'Say: "Thank you for calling, have a great day." Then end the call.'

_C_TRANSFER_FAILED = """Say: "I'm sorry, I wasn't able to connect you right now. Let me take your details and have someone call you back as soon as possible."

Collect name and callback number only (do NOT re-ask if already provided).
⚠️ SCRIPTED CLOSE — USE EXACT WORDS: "Perfect, I've got your details noted. Someone from our team will call you back shortly."
Then route to ending. Do NOT restart the flow."""

_C_ENDING = """Is there anything else I can help you with today?

## CLOSE RULE
When the caller says goodbye or there is nothing more to help with: say goodbye ONCE warmly and end. Do NOT repeat the farewell. Do NOT encourage the caller to call back multiple times. One clean close."""

# Code-node bodies — literal JS strings, escaped as Python.
_C_CALL_STYLE_DETECTOR = r"""const turns = (typeof metadata !== 'undefined' && metadata && metadata.transcript) ? metadata.transcript : [];
const callerTurns = turns.filter(t => t.role === 'user');
const callerText = callerTurns.map(t => (t.content || '')).join(' ').toLowerCase();
const turnCount = callerTurns.length;
const totalWords = callerText.split(/\s+/).filter(Boolean).length;
let note = '';
if (/hate.*(ai|robot|bot)|another robot|real person|actual person/.test(callerText)) {
  note = 'CALLER STYLE - Anti-AI: Say ONCE warmly: Totally fair, I will make this quick and get you sorted. Execute perfectly. Never mention being AI again.';
} else if (/pardon|say that again|could you repeat|speak slowly|i forgot|where was i/.test(callerText)) {
  note = 'CALLER STYLE - Elderly or confused: Slow your pace. Very short sentences. Confirm each piece before moving on. Re-anchor if lost: No problem, we were just getting your [last item].';
} else if (/please hurry|my dog|elderly parent|heart condition|dangerous|please help/.test(callerText)) {
  note = 'CALLER STYLE - Distressed: Open with: I am so sorry, let us get this sorted right now. Flag URGENT in team handoff. Move efficiently but warmly.';
} else if (/funny (story|thing|how)|reminds me|speaking of|my neighbor|my kids|by the way|anyway,|so yeah|right\?/.test(callerText) || (turnCount >= 2 && totalWords > 45 && !/refrigerant|seer|tonnage|compressor|capacitor/.test(callerText))) {
  note = 'CALLER STYLE - Chatty caller going off on tangents. CRITICAL RULE: After EVERY caller turn, respond with ONLY the next question. No affirmations, no social comments, no echoing. Just ask the next required question immediately.';
} else if (/refrigerant|seer|tonnage|compressor|subcooling|superheat|short cycling|capacitor|evaporator/.test(callerText)) {
  note = 'CALLER STYLE - Technical expert: Acknowledge FIRST: Sounds like you know your system well, our technician will appreciate that when they come out. Then capture info. NEVER confirm their diagnosis. When closing say: Our technician will assess everything on-site.';
} else if (callerTurns.some(t => (t.content || '').includes('...') || ((t.content || '').trim().length < 10 && (t.content || '').trim().length > 0)) && turnCount >= 2) {
  note = 'CALLER STYLE - Unclear speech: Ask for each missing piece explicitly: I caught [X], could you give me the rest? NEVER guess or complete partial information. Phonetic readback for numbers.';
} else if (/hold on|one sec|sorry.*kids|sorry.*noise|hang on|be right back|just a (sec|moment|minute)/.test(callerText)) {
  note = 'CALLER STYLE - Distracted: Be patient with every interruption. Each time they return, re-anchor: No problem, so we were just getting your [last item we were on].';
} else if (turnCount >= 2 && callerTurns.every(t => (t.content || '').split(/\s+/).filter(Boolean).length <= 5)) {
  note = 'CALLER STYLE - Brief answers: Accept every short answer without asking for more. Match their brevity. Confirm each one and move straight to next question.';
}
return { caller_style_note: note };"""

_C_VALIDATE_PHONE = r"""const raw = (typeof dv !== 'undefined' && dv && dv.caller_phone) ? dv.caller_phone : '';
const digits = raw.replace(/\D/g, '');
let phone_normalized = raw, phone_valid = false, phone_flag = '';
if (digits.length === 10) { phone_normalized = '+1' + digits; phone_valid = true; }
else if (digits.length === 11 && digits.startsWith('1')) { phone_normalized = '+' + digits; phone_valid = true; }
else if (digits.length < 7) { phone_flag = 'incomplete_number'; }
else { phone_flag = 'unusual_format'; phone_valid = true; }
return { phone_normalized, phone_valid, phone_flag };"""


def _c_fallback_leadcapture(_pricing_instr: str) -> str:
    # NB: JS takes pricingInstr as a parameter but never uses it. Port preserves the signature.
    return """{{caller_style_note}}

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

Route to ending_node."""


_WARM_TRANSFER_SUMMARY = "You are now speaking to the business owner or team member, NOT the caller. Give a brief 1-2 sentence summary of the call. Include: the caller's name (if collected), what they are calling about, and whether they had a booking or just had a question. Keep it concise and professional."
_EMERGENCY_TRANSFER_SUMMARY = "You are now speaking to the emergency team, NOT the caller. This is an EMERGENCY call. Briefly state: the caller's name, the emergency type (gas leak, flooding, no heat/cooling, etc), and their phone number if collected. Be direct and urgent."


# ============================================================
# COMPILE
# ============================================================

def compile(row: dict, *, now_iso: str | None = None) -> dict:
    """
    Main entry point. Takes a Supabase `hvac_standard_agent` row (dict),
    returns the JS-compatible compiler output.
    """
    data = _build_data_from_row(row)

    # --- STANDARD FIELDS (JS lines 21-70)
    company_name         = data.get('company_name') or 'HVAC Company'
    company_phone        = data.get('main_phone') or ''
    company_website      = data.get('website') or ''
    years_in_business    = data.get('years_in_business') or ''
    agent_name           = data.get('agent_name') or f"{company_name} Receptionist"
    is_demo              = bool(data.get('is_demo'))
    agent_display_name   = f"{'Demo' if is_demo else 'Live'} — {company_name}"
    voice_gender         = _lower(data.get('voice_gender') or 'female')
    services_offered     = data.get('services_offered') or ''
    brands_serviced      = data.get('brands_serviced') or ''
    service_area         = data.get('service_area') or ''
    service_area_radius  = data.get('service_area_radius') or ''
    business_hours       = data.get('business_hours') or ''
    response_time        = data.get('response_time') or ''
    emergency_247        = data.get('emergency_service') or 'No'
    emergency_phone      = data.get('emergency_phone') or ''
    after_hours_behavior = data.get('after_hours_behavior') or ''
    free_estimates       = data.get('free_estimates') or 'Yes - always free'
    diagnostic_fee       = data.get('diagnostic_fee') or ''
    pricing_policy       = data.get('pricing_policy') or 'We provide free quotes on-site'
    standard_fees        = data.get('standard_fees') or ''
    financing_available  = data.get('financing_available') or 'No'
    financing_details    = data.get('financing_details') or ''
    warranty             = data.get('warranty') or 'Yes'
    warranty_details     = data.get('warranty_details') or ''
    licensed_insured     = data.get('licensed_insured') or 'Yes'
    certifications       = data.get('certifications') or ''
    payment_methods      = data.get('payment_methods') or ''
    maintenance_plans    = data.get('maintenance_plans') or 'No'
    lead_contact_method  = data.get('lead_contact_method') or 'Both'
    lead_phone           = data.get('lead_phone') or ''
    lead_email           = data.get('lead_email') or ''
    custom_greeting      = data.get('custom_greeting') or ''
    company_tagline      = data.get('company_tagline') or ''
    transfer_phone       = data.get('transfer_phone') or ''
    separate_emergency   = data.get('separate_emergency_phone') or ''
    after_hours_transfer = data.get('after_hours_transfer') or 'all'
    transfer_triggers    = data.get('transfer_triggers') or 'Caller requests a live person, Emergency situation'
    transfer_behavior    = data.get('transfer_behavior') or 'Try once - take message if no answer'
    unique_selling_pts   = data.get('unique_selling_points') or ''
    current_promotion    = data.get('current_promotion') or ''
    seasonal_services    = data.get('seasonal_services') or ''
    additional_notes     = data.get('additional_info') or ''
    company_info_block   = data.get('companyInfoBlock') or ''
    owner_name           = data.get('owner_name') or ''
    google_review_rating = data.get('google_review_rating') or ''
    google_review_count  = data.get('google_review_count') or ''
    do_not_service       = data.get('do_not_service') or ''
    membership_program   = data.get('membership_program') or ''
    industry_type        = data.get('industry_type') or 'HVAC'

    # --- VOICE SELECTION
    voice_map = {'female': 'retell-Sloane', 'male': 'retell-Nico'}
    voice_id = voice_map.get(voice_gender, 'retell-Sloane')

    # --- TRANSFER NUMBERS
    has_dedicated_emergency_line = 'yes' in separate_emergency.lower()
    raw_transfer_phone = (emergency_phone if (has_dedicated_emergency_line and emergency_phone)
                          else (transfer_phone or lead_phone))
    if raw_transfer_phone:
        if raw_transfer_phone.startswith('+'):
            transfer_number = raw_transfer_phone
        else:
            transfer_number = '+1' + re.sub(r'\D', '', raw_transfer_phone)
    else:
        transfer_number = '+10000000000'

    raw_emergency_phone = emergency_phone or raw_transfer_phone
    if raw_emergency_phone:
        if raw_emergency_phone.startswith('+'):
            emergency_transfer_number = raw_emergency_phone
        else:
            emergency_transfer_number = '+1' + re.sub(r'\D', '', raw_emergency_phone)
    else:
        emergency_transfer_number = transfer_number

    emergency_display_number = emergency_phone or transfer_phone or company_phone or ''

    # --- PRICING INSTRUCTIONS
    shareable_fees = ''
    if diagnostic_fee:
        shareable_fees += f"\n- Diagnostic/Service Call Fee: {diagnostic_fee} (applied to repair if customer proceeds)"
    if standard_fees:
        shareable_fees += f"\n- Additional Set Fees: {standard_fees}"

    if pricing_policy == 'We provide free quotes on-site':
        pricing_instructions = ('When callers ask about pricing or cost:\n'
                                '- Say: "We provide free on-site quotes so our team can give you an accurate price based on your specific situation. Let me get a time booked for you."\n'
                                '- NEVER provide general service, repair, or installation prices.\n'
                                '- NEVER guess or estimate costs for any service.')
        if shareable_fees:
            pricing_instructions += f"\n\nThe ONLY fees you may mention:{shareable_fees}\n\nOnly mention these if the caller specifically asks. Do NOT volunteer pricing."
    elif pricing_policy == 'We charge a diagnostic fee then quote':
        pricing_instructions = (f'When callers ask about pricing or cost:\n'
                                f'- Say: "We do have a {diagnostic_fee or "service call"} fee for the initial visit, which gets applied to the repair if you choose to move forward. Our technician will give you a full quote once they\'ve assessed the situation."\n'
                                f'- NEVER provide general repair or installation prices.')
        if shareable_fees:
            pricing_instructions += f"\n\nSet fees you may share when asked:{shareable_fees}"
    else:
        pricing_instructions = ('When callers ask about pricing or cost:\n'
                                '- Say: "Our team will go over all the pricing with you at the appointment so you get the most accurate information."\n'
                                '- NEVER provide any prices, estimates, or cost ranges over the phone.')
        if shareable_fees:
            pricing_instructions += f"\n\nException, the ONLY fees you may mention:{shareable_fees}"

    # --- TRANSFER RULES
    trigger_list = [t.strip() for t in transfer_triggers.split(',') if t.strip()]
    transfer_rules = "## CALL TRANSFER PROTOCOL\n\n"
    transfer_rules += f"General transfer destination: {transfer_number}\n"
    transfer_rules += f"Emergency transfer destination: {emergency_transfer_number}\n"
    transfer_rules += f"Transfer behavior: {transfer_behavior}\n\n"
    transfer_rules += "Transfer the call ONLY when one of these conditions is met:\n"
    for i, t in enumerate(trigger_list):
        transfer_rules += f"{i + 1}. {t}\n"
    transfer_rules += "\nFor ALL other situations, attempt to collect caller information."
    if transfer_behavior == 'Always take a message - never transfer':
        transfer_rules += "\n\nIMPORTANT: NEVER transfer calls. Always collect caller information."
    if owner_name:
        transfer_rules += f"\n\n### Owner/Manager Reference\nIf a caller asks to speak with the owner or manager, their name is {owner_name}. Say: \"{owner_name} isn't available right now, but I can collect your details and have them call you back.\""

    # --- DO NOT SERVICE
    do_not_service_section = ''
    if do_not_service:
        do_not_service_section = (f"\n\n\n## SERVICES WE DO NOT PROVIDE\n\nThe following are outside our scope:\n{do_not_service}\n\n"
                                  f"If a caller requests any of these: \"I appreciate you reaching out, but unfortunately that's not something we service. I'd recommend reaching out to a specialist for that. Is there anything else I can help you with?\"\n\n"
                                  f"Do NOT attempt to collect lead information for out-of-scope requests.\n")

    # --- PROMOTIONS
    promotions_section = ''
    if current_promotion or seasonal_services or unique_selling_pts or (google_review_rating and google_review_rating != 'Not listed on Google'):
        promotions_section = "\n\n\n## PROMOTIONS & VALUE PROPOSITIONS\n\n"
        if google_review_rating and google_review_rating != 'Not listed on Google':
            review_line = f"We have a {google_review_rating}-star rating on Google"
            if google_review_count and google_review_count != 'Not listed on Google':
                review_line += f" with {google_review_count.lower().replace('under ', 'nearly ')} reviews"
            promotions_section += f"### Google Reviews\n{review_line}.\nMention this naturally when a caller is comparing options.\n\n"
        if current_promotion:
            promotions_section += f"### Current Promotion\n{current_promotion}\n\n"
        if unique_selling_pts:
            promotions_section += f"### Why Choose {company_name}\n{unique_selling_pts}\n\n"
        if seasonal_services:
            promotions_section += f"### Seasonal Services\n{seasonal_services}\n\n"

    # --- PAYMENT SECTION
    payment_section = ''
    if payment_methods:
        payment_section = f'\nWhen callers ask about payment methods:\n- Say: "We accept {payment_methods}."'
        if financing_available == 'Yes' and financing_details:
            payment_section += f'\n- If they ask about financing: "Yes, we offer financing, {financing_details}."'
        elif financing_available == 'Yes':
            payment_section += '\n- If they ask about financing: "Yes, we do offer financing options. Our team can go over the details with you."'
        if maintenance_plans != 'No':
            maint_line = '\n- If they ask about maintenance plans: "Yes, we do offer maintenance plans'
            if membership_program:
                maint_line += f', our {membership_program} program'
            maint_line += '. Our team can go over the details and pricing with you."'
            payment_section += maint_line

    # --- AFTER HOURS
    after_hours_section = ''
    if business_hours and after_hours_transfer != 'all':
        after_hours_section = f"\n\n\n## AFTER-HOURS BEHAVIOR\n\nBusiness hours: {business_hours}\n"
        if after_hours_transfer == 'emergency_only':
            after_hours_section += "\nOutside business hours:\n- Do NOT transfer regular calls. Collect details for callback.\n- Emergency calls CAN still be transferred.\n"
        elif after_hours_transfer == 'never':
            after_hours_section += "\nOutside business hours:\n- Do NOT transfer ANY calls.\n- Collect details for callback and mark as urgent.\n"

    # --- GLOBAL PROMPT (JS lines 413-439) — literal port, preserving all \n and template interpolation order.
    tagline_part = (' ' + company_tagline + '.') if company_tagline else ''
    payment_or_default = payment_section or (
        'When callers ask about payment methods:\n- Say: "Our team can go over payment options with you."'
    )
    global_prompt = (
        f"## ROLE\n"
        f"You are {agent_name}, a virtual AI receptionist for {company_name}.{tagline_part}\n"
        f"You are warm, professional and concise. Speak naturally, one topic at a time. Address callers by first name once you have it.\n\n"
        f"Your job is to collect lead information and ensure callers are helped — not just to provide a message.\n\n"
        f"If asked if you are a real person: \"I'm a virtual assistant, but I can get all your details and make sure someone calls you right back.\"\n\n"
        f"## STYLE\n"
        f"- One question at a time, always wait for the answer\n"
        f"- Match the caller's energy. Calm if calm, reassuring if stressed\n"
        f"- Never rush. Be patient with elderly callers\n"
        f"- Vary your language naturally\n"
        f"- Do not over-apologise. One brief apology per issue is enough\n\n"
        f"## CONFIRMING DETAILS\n"
        f"Slow down when collecting contact info. Confirm each piece back before moving on.\n"
        f"- Phone: read back in groups \"512, 555, 0192, is that right?\"\n"
        f"- Name: spell uncommon names letter by letter\n"
        f"- Address: confirm street and suburb \"123 Main Street, Austin, is that right?\"\n"
        f"- Email: read back slowly using dot, at, dash\n"
        f"- If anything is unclear, ask them to spell it. Never guess.\n\n"
        f"## TRANSCRIPTION\n"
        f"If you cannot understand something: \"I'm sorry, I didn't quite catch that, could you say that again?\" Never guess at names, addresses or emails.\n\n"
        f"## COMPANY INFORMATION\n\n"
        f"{{{{COMPANY_INFO_BLOCK}}}}\n\n"
        f"Use the information above to answer any company-specific questions. If a question is NOT covered above, do NOT guess. Say: \"That's a great question, one of our team members will be able to answer that when they call you back.\"\n\n"
        f"## PRICING & QUOTING\n\n"
        f"{pricing_instructions}\n\n"
        f"---\n\n"
        f"{transfer_rules}\n\n"
        f"---\n\n"
        f"## PAYMENT & FINANCING\n"
        f"{payment_or_default}\n\n"
        f"{promotions_section}\n"
        f"{do_not_service_section}{after_hours_section}\n"
        f"## CRITICAL RULES – NEVER BREAK THESE\n\n"
        f"- NEVER ask more than one question at a time\n"
        f"- NEVER make up prices, estimates, or timeframes unless explicitly listed in company information\n"
        f"- NEVER diagnose {industry_type} problems or recommend specific repairs\n"
        f"- NEVER promise availability without checking the calendar\n"
        f"- NEVER guess answers to company-specific questions not found in company information\n"
        f"- NEVER continue a conversation with obvious spam or robocalls, end politely\n"
        f"- NEVER transfer a call unless it matches a transfer trigger or is a confirmed emergency\n"
        f"- ALWAYS attempt to collect lead information before ending any legitimate call\n"
        f"- ALWAYS confirm information back to the caller before ending the call\n"
        f"- ALWAYS be warm, calm, and professional regardless of caller frustration\n"
        f"- ALWAYS try to understand what the caller means even if unclear\n\n"
        f"## IF CALLER IS RELUCTANT TO SHARE INFORMATION\n\n"
        f"\"I completely understand, this information simply helps our team prepare to help you. We never share your details with third parties.\"\n\n"
        f"## ERROR HANDLING\n\n"
        f"### Didn't hear or understand:\n"
        f"\"I apologise, I didn't quite catch that, could you repeat that for me?\"\n\n"
        f"### Don't know the answer:\n"
        f"\"That's a great question. I want to make sure you get the right answer, can I grab your details so someone from our team can call you back?\"\n\n"
        f"## SPECIAL SCENARIOS\n\n"
        f"### Angry or Upset Callers\n"
        f"1. Stay calm and lower your tone slightly\n"
        f"2. Acknowledge: \"I can hear how frustrated you are and I sincerely apologise for that.\"\n"
        f"3. Redirect: \"Let me get your information so someone can help you right away.\"\n"
        f"4. If abuse continues: \"I do want to help you, but I need us to work together respectfully. How can I best assist you today?\"\n\n"
        f"### Silent Callers\n"
        f"- After 3 seconds: \"Hello, are you there?\"\n"
        f"- After 5 more seconds: \"I'm having trouble hearing you, can you hear me okay?\"\n"
        f"- If no response: end the call politely\n\n"
        f"### Threats or Safety Concerns\n"
        f"Stay calm, do not engage or argue. Note any relevant details and flag the call immediately for human review.\n"
    )

    # --- GREETING
    greeting_text = custom_greeting if custom_greeting else f"Hello this is {agent_name} from {company_name}"

    # --- CONVERSATION FLOW
    conversation_flow = {
        "name": f"{company_name} - {industry_type} Standard Receptionist Flow",
        "start_speaker": "agent",
        "model_choice": {"type": "cascading", "model": "gpt-4.1", "high_priority": False},
        "global_prompt": global_prompt.replace("{{COMPANY_INFO_BLOCK}}", company_info_block),
        "tool_call_strict_mode": True,
        "knowledge_base_ids": [],
        "kb_config": {"top_k": 3, "filter_score": 0.6},
        "flex_mode": False,
        "is_transfer_cf": False,
        "nodes": [
            # NODE 1: Greeting
            {
                "id": "node-greeting", "name": "greeting_node", "type": "conversation",
                "instruction": {"type": "static_text", "text": greeting_text},
                "edges": [{"id": "edge-greeting-to-identify", "destination_node_id": "node-identify-call",
                           "transition_condition": {"type": "prompt", "prompt": "Always"}}],
                "display_position": {"x": 558, "y": 462}
            },
            # NODE 2: Identify Call
            {
                "id": "node-identify-call", "name": "identify_call_node", "type": "conversation", "start_speaker": "agent",
                "instruction": {"type": "prompt", "text": _c_identify_call('node-fallback-leadcapture')},
                "edges": [
                    {"id": "edge-to-call-style-detector", "destination_node_id": "node-call-style-detector", "transition_condition": {"type": "prompt", "prompt": "Repair, service, maintenance, quote, estimate, installation, new service request"}},
                    {"id": "edge-to-emergency", "destination_node_id": "node-verify-emergency", "transition_condition": {"type": "prompt", "prompt": "Emergency, urgent, no cooling, no heat, water leak, burning smell, gas smell"}},
                    {"id": "edge-to-callback", "destination_node_id": "node-callback", "transition_condition": {"type": "prompt", "prompt": "Returning a missed call, got a call from this number, calling back"}},
                    {"id": "edge-to-existing-customer", "destination_node_id": "node-existing-customer", "transition_condition": {"type": "prompt", "prompt": "Existing customer, question about appointment, invoice, technician, job status"}},
                    {"id": "edge-to-general-questions", "destination_node_id": "node-general-questions", "transition_condition": {"type": "prompt", "prompt": "General question about services, hours, pricing, area, credentials"}},
                    {"id": "edge-to-transfer-live", "destination_node_id": "node-transfer-call", "transition_condition": {"type": "prompt", "prompt": "Wants to speak to a real person, manager, owner, or specific person"}},
                    {"id": "edge-to-spam", "destination_node_id": "node-spam-robocall", "transition_condition": {"type": "prompt", "prompt": "Robocall, spam, automated message, silence after greeting"}}
                ],
                "finetune_transition_examples": [
                    {"id": "fe-service", "destination_node_id": "node-call-style-detector", "transcript": [{"role": "user", "content": "My AC isn't working\nI need a repair\nI need a tune-up\nI need maintenance\nI need an installation quote\nI want my system checked"}, {"role": "agent", "content": "I can help with that"}]},
                    {"id": "fe-emergency", "destination_node_id": "node-verify-emergency", "transcript": [{"role": "user", "content": "no cooling\nno heating\nsystem not working\nwater leaking\nburning smell\nI smell gas\nurgent repair"}]},
                    {"id": "fe-callback", "destination_node_id": "node-callback", "transcript": [{"role": "user", "content": "I missed a call from this number\nSomeone called me from here\nI am calling back"}]},
                    {"id": "fe-existing", "destination_node_id": "node-existing-customer", "transcript": [{"role": "user", "content": "calling about my appointment\nwhere is the technician\nquestion about my invoice\ncalling about my quote"}]},
                    {"id": "fe-transfer-live", "destination_node_id": "node-transfer-call", "transcript": [{"role": "user", "content": "Let me speak to someone\nI want to talk to a real person\nCan I speak to a human\nI want to talk to the manager"}]},
                    {"id": "fe-spam", "destination_node_id": "node-spam-robocall", "transcript": [{"role": "user", "content": "Hello\nHello\nHello"}]}
                ],
                "display_position": {"x": 1110, "y": 366}
            },
            # NODE 2b: Call Style Detector
            {
                "id": "node-call-style-detector", "name": "call_style_detector", "type": "code",
                "code": _C_CALL_STYLE_DETECTOR,
                "speak_during_execution": False,
                "wait_for_result": True,
                "edges": [
                    {"id": "edge-call-style-detector-after", "destination_node_id": "node-fallback-leadcapture",
                     "transition_condition": {"type": "prompt", "prompt": "After caller style detection"}},
                ],
                "else_edge": {"id": "edge-style-else", "destination_node_id": "node-fallback-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Else"}},
                "display_position": {"x": 1386, "y": 726}
            },
            # NODE 3: Fallback Lead Capture
            {
                "id": "node-fallback-leadcapture", "name": "fallback_leadcapture_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _c_fallback_leadcapture(pricing_instructions)},
                "edges": [
                    {"id": "edge-fallback-to-ending", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "All details confirmed, close"}},
                    {"id": "edge-fallback-to-emergency", "destination_node_id": "node-verify-emergency", "transition_condition": {"type": "prompt", "prompt": "Emergency signals detected"}}
                ],
                "display_position": {"x": 2190, "y": 726}
            },
            # NODE 4: Verify Emergency
            {
                "id": "node-verify-emergency", "name": "verify_emergency_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _c_verify_emergency(emergency_display_number, 'node-fallback-leadcapture')},
                "edges": [
                    {"id": "edge-emergency-yes", "destination_node_id": "node-emergency-transfer", "transition_condition": {"type": "prompt", "prompt": "Confirmed emergency, transfer now"}},
                    {"id": "edge-emergency-no", "destination_node_id": "node-fallback-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Urgent but not emergency, collect details as priority"}}
                ],
                "finetune_transition_examples": [
                    {"id": "fe-emergency-yes", "destination_node_id": "node-emergency-transfer", "transcript": [{"role": "user", "content": "Yes it's an emergency\nI have no heat and it's freezing\nI smell gas\nWater is flooding\nYes we need someone now"}]},
                    {"id": "fe-emergency-no", "destination_node_id": "node-fallback-leadcapture", "transcript": [{"role": "user", "content": "Not really an emergency but I need it fixed soon\nIt's not urgent but it's been out for a couple days\nNot really, it's just not working well"}]}
                ],
                "display_position": {"x": 2742, "y": 1470}
            },
            # NODE 5: Callback
            {
                "id": "node-callback", "name": "callback_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _c_callback_node('node-fallback-leadcapture')},
                "edges": [
                    {"id": "edge-callback-to-leadcapture", "destination_node_id": "node-fallback-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Caller describes a service need, attempt capture"}},
                    {"id": "edge-callback-end", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "Details captured, no new service need, close"}}
                ],
                "display_position": {"x": 1662, "y": 2100}
            },
            # NODE 6: Existing Customer
            {
                "id": "node-existing-customer", "name": "existing_customer_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _C_EXISTING_CUSTOMER},
                "edges": [
                    {"id": "edge-existing-resolved", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "Enquiry noted, close"}},
                    {"id": "edge-existing-transfer", "destination_node_id": "node-transfer-call", "transition_condition": {"type": "prompt", "prompt": "Caller insists on speaking to someone now"}}
                ],
                "display_position": {"x": 2214, "y": 2100}
            },
            # NODE 7: General Questions
            {
                "id": "node-general-questions", "name": "general_questions_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _C_GENERAL_QUESTIONS},
                "edges": [
                    {"id": "edge-general-answered", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "Question answered, no booking needed"}},
                    {"id": "edge-general-to-leadcapture", "destination_node_id": "node-fallback-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Caller wants to book or get a quote"}},
                    {"id": "edge-general-transfer", "destination_node_id": "node-transfer-call", "transition_condition": {"type": "prompt", "prompt": "Caller needs further help beyond FAQ"}}
                ],
                "display_position": {"x": 1662, "y": 2700}
            },
            # NODE 8: Spam / Robocall
            {
                "id": "node-spam-robocall", "name": "spam_robocall_node", "type": "conversation",
                "instruction": {"type": "static_text", "text": _C_SPAM_ROBOCALL},
                "edges": [{"id": "edge-spam-end", "destination_node_id": "node-end-call", "transition_condition": {"type": "prompt", "prompt": "Always"}}],
                "display_position": {"x": 1662, "y": 3000}
            },
            # NODE 9: Transfer Call
            {
                "id": "node-transfer-call", "name": "Transfer Call", "type": "transfer_call",
                "instruction": {"type": "prompt", "text": 'Say: "Let me get someone on the line for you right now, just one moment." Then transfer.'},
                "transfer_destination": {"type": "predefined", "number": transfer_number},
                "transfer_option": {"type": "warm_transfer", "warm_transfer_option": {"type": "prompt", "prompt": _WARM_TRANSFER_SUMMARY}, "enable_bridge_audio_cue": True},
                "edge": {"id": "edge-transfer-failed", "destination_node_id": "node-transfer-failed", "transition_condition": {"type": "prompt", "prompt": "Transfer failed"}},
                "display_position": {"x": 3318, "y": 2238}
            },
            # NODE 9b: Emergency Transfer
            {
                "id": "node-emergency-transfer", "name": "Emergency Transfer", "type": "transfer_call",
                "instruction": {"type": "prompt", "text": f'Say: "I am transferring you to our emergency line now. The number is {emergency_display_number} in case we get disconnected. Stay on the line." Then transfer immediately.'},
                "transfer_destination": {"type": "predefined", "number": emergency_transfer_number},
                "transfer_option": {"type": "warm_transfer", "warm_transfer_option": {"type": "prompt", "prompt": _EMERGENCY_TRANSFER_SUMMARY}, "enable_bridge_audio_cue": True},
                "edge": {"id": "edge-emergency-failed", "destination_node_id": "node-transfer-failed", "transition_condition": {"type": "prompt", "prompt": "Transfer failed"}},
                "display_position": {"x": 3318, "y": 1470}
            },
            # NODE 10: Transfer Failed
            {
                "id": "node-transfer-failed", "name": "transfer_failed_node", "type": "conversation",
                "instruction": {"type": "prompt", "text": _C_TRANSFER_FAILED},
                "edges": [
                    {"id": "edge-transfer-failed-to-leadcapture", "destination_node_id": "node-fallback-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Caller still wants to provide details"}},
                    {"id": "edge-transfer-failed-to-ending", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "Details taken, close"}}
                ],
                "display_position": {"x": 3870, "y": 2238}
            },
            # NODE 11: Ending
            {
                "id": "node-ending", "name": "Ending", "type": "conversation",
                "instruction": {"type": "static_text", "text": _C_ENDING},
                "edges": [
                    {"id": "edge-ending-to-end", "destination_node_id": "node-end-call", "transition_condition": {"type": "prompt", "prompt": 'Nothing else. Close: "Have a great day, take care!"'}},
                    {"id": "edge-ending-to-restart", "destination_node_id": "node-identify-call", "transition_condition": {"type": "prompt", "prompt": "Caller has another question or request"}}
                ],
                "display_position": {"x": 4422, "y": 2190}
            },
            # NODE 12: Validate Phone
            {
                "id": "node-validate-phone", "name": "validate_phone", "type": "code",
                "code": _C_VALIDATE_PHONE,
                "speak_during_execution": False,
                "wait_for_result": True,
                "edges": [
                    {"id": "edge-validate-phone-after", "destination_node_id": "node-ending",
                     "transition_condition": {"type": "prompt", "prompt": "After phone validation"}},
                ],
                "else_edge": {"id": "edge-validate-phone-else", "destination_node_id": "node-ending", "transition_condition": {"type": "prompt", "prompt": "Else"}},
                "display_position": {"x": 900, "y": 1400}
            },
            # NODE 13: End Call
            {
                "id": "node-end-call", "name": "End Call", "type": "end",
                "instruction": {"type": "prompt", "text": "End the call warmly."},
                "display_position": {"x": 4974, "y": 2238}
            },
            # GLOBAL NODE 1: Emergency Detection
            {
                "id": "global-emergency", "name": "Emergency Detection", "type": "conversation",
                "instruction": {"type": "prompt", "text": "The caller has described what sounds like an emergency. Follow the two-step urgency sequence: Step 1: Ask 'Is the system completely down or is there any immediate danger like a gas smell, water flooding, or smoke?' Step 2: Based on their response, either transfer to emergency line or route to priority lead capture."},
                "global_node_setting": {"condition": "The caller describes a dangerous, life-threatening, or urgent safety situation such as a gas leak, flooding, fire, no heat in freezing conditions, electrical sparks, or carbon monoxide. Only trigger for genuine safety emergencies, not for routine urgent repairs.", "cool_down": 3},
                "edges": [
                    {"destination_node_id": "node-transfer-call", "id": "global-emergency-to-transfer", "transition_condition": {"type": "prompt", "prompt": "Confirmed emergency - transfer immediately"}},
                    {"destination_node_id": "node-fallback-leadcapture", "id": "global-emergency-to-leadcapture", "transition_condition": {"type": "prompt", "prompt": "Urgent but not emergency - capture as priority"}}
                ],
                "display_position": {"x": 100, "y": 100}
            },
            # GLOBAL NODE 2: Spam Detection
            {
                "id": "global-spam", "name": "Spam Detection", "type": "conversation",
                "instruction": {"type": "static_text", "text": "Say: 'Thank you for calling, have a great day.' Then end the call."},
                "global_node_setting": {"condition": "The conversation appears to be a robocall, automated message, extended silence after greeting, or sales/marketing call not related to HVAC services.", "cool_down": 1},
                "edges": [{"destination_node_id": "node-end-call", "id": "global-spam-end", "transition_condition": {"type": "prompt", "prompt": "Always"}}],
                "display_position": {"x": 100, "y": 300}
            },
            # GLOBAL NODE 3: Transfer Request
            {
                "id": "global-transfer", "name": "Transfer Request", "type": "conversation",
                "instruction": {"type": "prompt", "text": "Say: 'Of course, let me get someone on the line for you right now, just one moment.' Then transfer."},
                "global_node_setting": {"condition": "The caller explicitly asks to speak to a real person, manager, owner, supervisor, or human. They are insistent on speaking to someone and not to the AI.", "cool_down": 2},
                "edges": [{"destination_node_id": "node-transfer-call", "id": "global-transfer-go", "transition_condition": {"type": "prompt", "prompt": "Always transfer"}}],
                "display_position": {"x": 100, "y": 500}
            },
            # EXTRACT VARIABLE NODE
            {
                "id": "node-extract-caller-data", "name": "Extract Caller Data", "type": "extract_dynamic_variables",
                "edges": [],
                "variables": [
                    {"name": "caller_name", "description": "Full name of the caller", "type": "string", "required": False},
                    {"name": "caller_phone", "description": "Phone number the caller provides", "type": "string", "required": False},
                    {"name": "caller_address", "description": "Service address or location", "type": "string", "required": False},
                    {"name": "service_needed", "description": "What service or repair the caller needs", "type": "string", "required": False},
                    {"name": "is_emergency", "description": "Whether this is an emergency situation", "type": "boolean", "required": False},
                    {"name": "urgency_level", "description": "How urgent the request is", "type": "enum", "choices": ["low", "medium", "high", "emergency"], "required": False}
                ],
                "display_position": {"x": 100, "y": 700}
            }
        ],
        "start_node_id": "node-greeting"
    }

    # --- AGENT CONFIGURATION
    agent_config = {
        "agent_name": agent_display_name,
        "voice_id": voice_id,
        "language": "multi",
        "webhook_url": "https://n8n.syntharra.com/webhook/retell-hvac-webhook",
        "ambient_sound": "call-center",
        "ambient_sound_volume": 0.8,
        "responsiveness": 0.9,
        "enable_dynamic_responsiveness": True,
        "interruption_sensitivity": 0.9,
        "voice_temperature": 1,
        "voice_speed": 1,
        "enable_dynamic_voice_speed": True,
        "volume": 1,
        "max_call_duration_ms": 600000,
        "allow_user_dtmf": True,
        "opt_in_signed_url": False,
        "backchannel": True,
        "reminders": True,
        "boosted_keywords": [services_offered],
        "pronunciation_dictionary": [],
        "guardrails": True,
        "post_call_analysis_data": [
            {"type": "system-presets", "name": "call_summary", "description": "Write a 1-3 sentence summary of the call."},
            {"type": "system-presets", "name": "call_successful", "description": "Evaluate whether the agent had a successful call."},
            {"type": "system-presets", "name": "user_sentiment", "description": "Evaluate user's sentiment, mood and satisfaction level."},
            {"type": "boolean", "name": "lead_captured", "description": "Was lead information successfully captured during this call? Return true or false."},
            {"type": "boolean", "name": "caller_interested", "description": "Was the caller interested in services? Return true or false."},
            {"type": "string", "name": "caller_name", "description": "Full name of the caller if provided. Empty string if not."},
            {"type": "string", "name": "caller_phone", "description": "Phone number of the caller if stated. Empty string if not."},
            {"type": "string", "name": "caller_email", "description": "Email address of the caller if provided. Empty string if not."},
            {"type": "string", "name": "caller_address", "description": "Service address if provided. Empty string if not."},
            {"type": "string", "name": "service_requested", "description": "What service was requested. Short description."},
            {"type": "string", "name": "call_type", "description": "Type of call: new_lead, emergency, callback, existing_customer, general_question, spam."},
            {"type": "string", "name": "urgency", "description": "Urgency level: low, medium, high, emergency."},
            {"type": "boolean", "name": "is_hot_lead", "description": "Is this a hot lead? True if lead score would be 7 or above."},
            {"type": "number", "name": "lead_score", "description": "Lead score 0-10. Lead captured with urgency=9-10. Lead captured=7-8. General inquiry=4-6. Spam=0."},
            {"type": "string", "name": "follow_up_action", "description": "Recommended follow-up action: callback, callback_urgent, transfer_to_team, or none."},
            {"type": "string", "name": "special_notes", "description": "Any special notes or flags about the call (e.g., technical caller, elderly, distressed, anti-AI)."}
        ]
    }

    # --- EXTRACTED DATA (JS lines 729-757)
    extracted_data = {
        "company_name": company_name, "company_phone": company_phone, "website": company_website,
        "years_in_business": years_in_business, "agent_name": agent_name, "voice_gender": voice_gender,
        "voice_id": voice_id, "services_offered": services_offered, "brands_serviced": brands_serviced,
        "service_area": service_area, "service_area_radius": service_area_radius, "business_hours": business_hours,
        "response_time": response_time, "emergency_service": emergency_247, "emergency_phone": emergency_phone,
        "after_hours_behavior": after_hours_behavior, "free_estimates": free_estimates, "diagnostic_fee": diagnostic_fee,
        "pricing_policy": pricing_policy, "standard_fees": standard_fees, "financing_available": financing_available,
        "financing_details": financing_details, "warranty": warranty, "warranty_details": warranty_details,
        "licensed_insured": licensed_insured, "certifications": certifications, "payment_methods": payment_methods,
        "maintenance_plans": maintenance_plans, "lead_contact_method": lead_contact_method, "lead_phone": lead_phone,
        "lead_email": lead_email, "custom_greeting": custom_greeting, "company_tagline": company_tagline,
        "transfer_phone": transfer_phone or lead_phone, "transfer_triggers": transfer_triggers,
        "transfer_behavior": transfer_behavior, "unique_selling_points": unique_selling_pts,
        "current_promotion": current_promotion, "seasonal_services": seasonal_services,
        "additional_info": additional_notes, "owner_name": owner_name, "google_review_rating": google_review_rating,
        "google_review_count": google_review_count, "stripe_customer_id": data.get('stripe_customer_id') or None,
        "main_phone": data.get('main_phone') or data.get('company_phone') or None,
        "do_not_service": do_not_service,
        "notification_email_2": data.get('notification_email_2') or None,
        "notification_email_3": data.get('notification_email_3') or None,
        "notification_sms_2": data.get('notification_sms_2') or None,
        "notification_sms_3": data.get('notification_sms_3') or None,
        "membership_program": membership_program, "client_email": data.get('client_email') or '',
        "timezone": data.get('timezone') or 'America/Chicago', "industry_type": industry_type,
        "after_hours_transfer": after_hours_transfer, "separate_emergency_phone": separate_emergency,
        "submission_id": data.get('submission_id') or None,
        "tier": "standard"
    }

    # --- TIMESTAMP
    if now_iso is None:
        # Mirror JS `new Date().toISOString()` format: YYYY-MM-DDTHH:MM:SS.mmmZ
        now = datetime.now(timezone.utc)
        now_iso = now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 1000:03d}Z"

    return {
        "conversationFlow": conversation_flow,
        "agentConfig": agent_config,
        "agentName": agent_config["agent_name"],
        "companyName": company_name,
        "voiceId": voice_id,
        "companyInfoBlock": company_info_block,
        "extractedData": extracted_data,
        "transferNumber": transfer_number,
        "emergencyTransferNumber": emergency_transfer_number,
        "timestamp": now_iso,
    }


if __name__ == '__main__':
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python prompt_compiler.py <supabase_row.json> [output.json]")
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        row = json.load(f)
    out = compile(row, now_iso='2026-04-09T00:00:00.000Z')
    out_path = sys.argv[2] if len(sys.argv) > 2 else '/dev/stdout'
    if out_path == '/dev/stdout':
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"Wrote {out_path}")
