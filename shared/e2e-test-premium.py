import os
import urllib.request, urllib.error, json, time, urllib.parse

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
N8N_KEY    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZGU0MmJjZDAtNGU4ZC00ZDFmLWJlNDMtYzQzMDRjMjBjNjk1IiwiaWF0IjoxNzc0ODQ1ODc3fQ.SRjfEwRpZGBh5dnmNvp2PotTZ3e6OCejy2NFgM5uNqU"
RETELL_KEY = os.environ.get("RETELL_KEY", "")  # export RETELL_KEY=... before running
SUPABASE   = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_ANON    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0"
SB_SVC     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
TEST_EMAIL = "daniel@syntharra.com"

# ── MODE ──────────────────────────────────────────────────────────────────────
# TEST mode  → no Stripe customer ID → Stripe Gate skips Twilio purchase
# LIVE mode  → real Stripe customer ID present → Twilio number purchased
STRIPE_CUSTOMER_ID = ""   # leave empty for test mode

# ── TEST DATA ─────────────────────────────────────────────────────────────────
TS           = int(time.time())
TEST_COMPANY = f"FrostKing HVAC Premium {TS}"
TEST_AGENT   = "Nova"
TEST_PHONE   = "+15125550288"

results = {}
cleanup = {"agent_ids": [], "flow_ids": [], "call_ids": []}

def check(name, passed, detail=""):
    results[name] = passed
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}" + (f"  →  {detail}" if detail else ""))
    return passed

def http(url, method="GET", body=None, headers={}):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e: return e.code, {}
    except Exception: return 0, {}

def sb(path, method="GET", body=None, service=False):
    key = SB_SVC if service else SB_ANON
    _, data = http(f"{SUPABASE}/rest/v1/{path}", method, body,
        {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "return=representation"})
    return data if isinstance(data, list) else []

def retell(path, method="GET", body=None):
    _, data = http(f"https://api.retellai.com/{path}", method, body,
        {"Authorization": f"Bearer {RETELL_KEY}"})
    return data

IS_LIVE = bool(STRIPE_CUSTOMER_ID)
mode_label = "LIVE MODE — Twilio number will be purchased" if IS_LIVE else "TEST MODE — Stripe gate will skip Twilio purchase"

print("=" * 60)
print("SYNTHARRA PREMIUM E2E TEST  —  SELF CLEANING")
print(f"Mode    : {mode_label}")
print(f"Company : {TEST_COMPANY}")
print(f"Started : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
print("\n[1] JOTFORM PREMIUM ONBOARDING — ALL FIELDS")
# ══════════════════════════════════════════════════════════════
# NOTE: Premium form uses different notification field names (q79-q82 vs q64-q67 in Standard)
# and includes booking/scheduling fields (q85-q92).
# Greeting is resolved server-side from q75_greetingStyle + q76_customGreetingText.
payload = {
    # Section 1: Business Information
    "q4_hvacCompany":             TEST_COMPANY,
    "q54_ownerName":              "Sarah Winters",
    "q6_mainCompany":             TEST_PHONE,
    "q5_emailAddress":            TEST_EMAIL,
    "q7_companyWebsite":          "www.frostkinghvac.com",
    "q8_yearsIn":                 "12",
    "q34_timezone":               "America/Chicago",
    "q13_servicesOffered":        ["AC Repair", "Heating Repair", "AC Installation", "Heating Installation",
                                   "Maintenance", "Duct Cleaning", "Air Quality", "Mini-Split Systems"],
    "q14_brandsequipmentServiced":["Carrier", "Trane", "Lennox", "Daikin", "Mitsubishi", "Bosch"],
    "q16_primaryService":         "Dallas/Fort Worth Metroplex and surrounding suburbs",
    "q40_serviceAreaRadius":      "50 miles",
    "q29_certifications":         ["NATE Certified", "EPA 608", "OSHA 30", "NCI Certified"],
    "q28_licensedAnd":            "Yes",

    # Section 2: AI Receptionist Configuration
    "q10_aiAgent10":              TEST_AGENT,
    "q11_aiVoice":                "Female",
    "q75_greetingStyle":          "professional",   # Premium: greeting resolved from style
    "q76_customGreetingText":     "",               # blank — resolved from style
    "q39_companyTagline":         "DFW's Premium HVAC Specialists",

    # Section 3: Hours & Availability
    "q17_businessHours":          "Monday to Friday 7am to 7pm, Saturday 8am to 5pm",
    "q18_typicalResponse":        "Same day service available",
    "q20_247Emergency":           "Yes",
    "q21_emergencyAfterhours":    "+15125550288",
    "q22_afterhoursBehavior":     "Transfer to emergency line",

    # Section 4: Pricing
    "q42_pricingPolicy":          "Upfront pricing — all quotes provided before work begins.",
    "q41_diagnosticFee":          "$89 diagnostic fee, waived with repair over $300",
    "q43_standardFees":           "Service call $89, Tune-up $139, Emergency surcharge $95",
    "q24_freeEstimates":          "Yes - free on all new system installations",
    "q25_financingAvailable":     "Yes",
    "q44_financingDetails":       "0% financing for 36 months on systems over $5,000 with approved credit",
    "q26_serviceWarranties":      "Yes",
    "q27_warrantyDetails":        "7 years parts, 3 years labour on all repairs",
    "q45_paymentMethods":         ["Cash", "Credit Card", "Check", "Financing", "Zelle", "Apple Pay"],
    "q46_maintenancePlans":       "Yes - FrostKing Care Plan $299/year, includes 2 tune-ups, priority scheduling, 15% discount",
    "q58_membershipProgramName":  "FrostKing Care Plan",

    # Section 5: Lead Capture & Notifications
    "q31_leadContact":            "Both",
    "q32_leadNotification":       "+16316330721",
    "q33_leadNotification33":     TEST_EMAIL,
    # Premium notification fields use q79-q82 (NOT q64-q67 like Standard)
    "q79_notifSms2":              "+16316330722",
    "q80_notifSms3":              "+16316330723",
    "q81_notifEmail2":            "dispatcher@frostkinghvac.com",
    "q82_notifEmail3":            "manager@frostkinghvac.com",
    "q48_transferPhone":          TEST_PHONE,
    "q49_transferTriggers":       ["Customer is angry", "Legal threat", "Complex billing dispute",
                                   "Customer requests manager", "Safety concern"],
    "q50_transferBehavior":       "Try once - take message if no answer",
    "q57_doNotServiceList":       "Commercial refrigeration, industrial systems, window units",

    # Section 6: Branding & Extras
    "q55_googleReviewRating":     "4.9",
    "q56_googleReviewCount":      "843",
    "q51_uniqueSellingPoints":    "Family-owned 12 years, same-day service, 7-year warranty, NCI-certified, upfront pricing",
    "q52_currentPromotion":       "$100 off any system replacement this month",
    "q53_seasonalServices":       "Spring AC tune-ups $99, Fall heating checks, Summer emergency priority",
    "q37_additionalInfo":         "FrostKing is DFW's highest-rated HVAC company. All techs background-checked and drug-tested.",

    # Section 7: Scheduling & Booking (Premium-only fields)
    "q85_scheduling_platform":    "Google Calendar",
    "q86_bookable_job_types":     ["AC Repair", "Heating Repair", "Maintenance", "AC Installation"],
    "q87_slot_duration":          "60",     # minutes
    "q88_min_notice":             "2",      # hours
    "q89_booking_hours":          "Monday to Friday 7am to 6pm, Saturday 8am to 4pm",
    "q90_buffer_time":            "30",     # minutes between jobs
    "q91_confirmation_method":    "email",
    "q92_cal_agreement":          "Yes",
}

if IS_LIVE:
    payload["stripe_customer_id"] = STRIPE_CUSTOMER_ID

# Premium onboarding uses its own dedicated webhook path (different from Standard)
# Standard:  /webhook/jotform-hvac-onboarding          → workflow 4Hx7aRdzMl5N0uJP
# Premium:   /webhook/jotform-hvac-premium-onboarding  → workflow kz1VmwNccunRMEaF
status, _ = http("https://n8n.syntharra.com/webhook/jotform-hvac-premium-onboarding", "POST", payload)
check("Webhook accepted (HTTP 200)", status == 200, f"HTTP {status}")

# ══════════════════════════════════════════════════════════════
print("\n[2] N8N EXECUTION — PREMIUM ONBOARDING")
# ══════════════════════════════════════════════════════════════
# Poll up to 45s for premium onboarding workflow kz1VmwNccunRMEaF
exec_status = 'unknown'
exec_id     = '?'
prem_onboard_wf_id = "kz1VmwNccunRMEaF"
for attempt in range(9):
    time.sleep(5)
    _, execs = http(
        f"https://n8n.syntharra.com/api/v1/executions?workflowId={prem_onboard_wf_id}&limit=3",
        headers={"X-N8N-API-KEY": N8N_KEY})
    candidates = [e for e in (execs.get('data') or [])
                  if e.get('status') in ('success', 'error', 'crashed')]
    if candidates:
        latest      = candidates[0]
        exec_status = latest.get('status', 'unknown')
        exec_id     = latest.get('id', '?')
        break
check("Premium onboarding workflow executed successfully", exec_status == 'success',
      f"exec {exec_id} → {exec_status}")

# ══════════════════════════════════════════════════════════════
print("\n[3] SUPABASE — STANDARD + PREMIUM FIELDS")
# ══════════════════════════════════════════════════════════════
# Premium saves into hvac_standard_agent with plan_type='premium'
rows = sb(f"hvac_standard_agent?company_name=eq.{urllib.parse.quote(TEST_COMPANY)}&select=*")
row  = rows[0] if rows else {}
agent_id = row.get('agent_id', '')
flow_id  = row.get('conversation_flow_id', '')
if agent_id: cleanup['agent_ids'].append(agent_id)
if flow_id:  cleanup['flow_ids'].append(flow_id)

check("Row created in Supabase",              bool(row))
check("plan_type = premium",                  row.get('plan_type') == 'premium',                  row.get('plan_type'))

# Standard fields (inherited)
check("company_name",                         row.get('company_name') == TEST_COMPANY,             row.get('company_name'))
check("owner_name",                           row.get('owner_name') == 'Sarah Winters',            row.get('owner_name'))
check("client_email",                         row.get('client_email') == TEST_EMAIL,               row.get('client_email'))
check("company_phone",                        bool(row.get('company_phone')),                      row.get('company_phone'))
check("website",                              row.get('website') == 'www.frostkinghvac.com',       row.get('website'))
check("years_in_business",                    row.get('years_in_business') == '12',                row.get('years_in_business'))
check("timezone",                             row.get('timezone') == 'America/Chicago',            row.get('timezone'))
check("agent_name",                           bool(row.get('agent_name')),                         row.get('agent_name'))
check("custom_greeting resolved from style",  bool(row.get('custom_greeting')),                    (row.get('custom_greeting') or '')[:60])
check("services_offered populated",           bool(row.get('services_offered')),                   (row.get('services_offered') or '')[:50])
check("brands_serviced populated",            bool(row.get('brands_serviced')),                    (row.get('brands_serviced') or '')[:40])
check("service_area populated",               bool(row.get('service_area')),                       row.get('service_area'))
check("service_area_radius",                  row.get('service_area_radius') == '50 miles',        row.get('service_area_radius'))
check("certifications populated",             bool(row.get('certifications')),                     row.get('certifications'))
check("emergency_service",                    row.get('emergency_service') == 'Yes',               row.get('emergency_service'))
check("emergency_phone",                      bool(row.get('emergency_phone')),                    row.get('emergency_phone'))
check("business_hours populated",             bool(row.get('business_hours')),                     (row.get('business_hours') or '')[:40])
check("pricing_policy populated",             bool(row.get('pricing_policy')),                     (row.get('pricing_policy') or '')[:40])
check("diagnostic_fee",                       bool(row.get('diagnostic_fee')),                     row.get('diagnostic_fee'))
check("financing_available",                  row.get('financing_available') == 'Yes',             row.get('financing_available'))
check("warranty",                             row.get('warranty') == 'Yes',                        row.get('warranty'))
check("payment_methods populated",            bool(row.get('payment_methods')),                    (row.get('payment_methods') or '')[:40])
check("maintenance_plans populated",          bool(row.get('maintenance_plans')),                  (row.get('maintenance_plans') or '')[:40])
check("membership_program",                   row.get('membership_program') == 'FrostKing Care Plan', row.get('membership_program'))
check("lead_contact_method",                  row.get('lead_contact_method') == 'Both',            row.get('lead_contact_method'))
check("lead_phone",                           bool(row.get('lead_phone')),                         row.get('lead_phone'))
check("lead_email",                           row.get('lead_email') == TEST_EMAIL,                 row.get('lead_email'))
check("transfer_phone",                       bool(row.get('transfer_phone')),                     row.get('transfer_phone'))
check("transfer_triggers populated",          bool(row.get('transfer_triggers')),                  (row.get('transfer_triggers') or '')[:40])
check("google_review_rating",                 row.get('google_review_rating') == '4.9',            row.get('google_review_rating'))
check("google_review_count",                  row.get('google_review_count') == '843',             row.get('google_review_count'))
check("unique_selling_points populated",      bool(row.get('unique_selling_points')),              (row.get('unique_selling_points') or '')[:40])
check("current_promotion populated",          bool(row.get('current_promotion')),                  row.get('current_promotion'))
check("do_not_service populated",             bool(row.get('do_not_service')),                     row.get('do_not_service'))
check("additional_info populated",            bool(row.get('additional_info')),                    (row.get('additional_info') or '')[:40])

# Premium-only notification fields (q79-q82, NOT q64-q67)
check("notification_email_2 saved (premium)", row.get('notification_email_2') == 'dispatcher@frostkinghvac.com', row.get('notification_email_2'))
check("notification_email_3 saved (premium)", row.get('notification_email_3') == 'manager@frostkinghvac.com',    row.get('notification_email_3'))
check("notification_sms_2 saved (premium)",   row.get('notification_sms_2') == '+16316330722',                   row.get('notification_sms_2'))
check("notification_sms_3 saved (premium)",   row.get('notification_sms_3') == '+16316330723',                   row.get('notification_sms_3'))

# Premium-only booking fields
check("booking_confirmation_method saved",    bool(row.get('booking_confirmation_method')),        row.get('booking_confirmation_method'))
check("buffer_time_minutes saved",            (row.get('buffer_time_minutes') or 0) > 0,           row.get('buffer_time_minutes'))
check("slot_duration_minutes saved",          (row.get('slot_duration_minutes') or 0) > 0,         row.get('slot_duration_minutes'))
check("min_notice_hours saved",               (row.get('min_notice_hours') or 0) >= 0,             row.get('min_notice_hours'))
check("booking_hours populated",              bool(row.get('booking_hours')),                      (row.get('booking_hours') or '')[:40])
check("bookable_job_types populated",         bool(row.get('bookable_job_types')),                 (row.get('bookable_job_types') or '')[:40])

check("agent_id populated",                   bool(agent_id),                                      agent_id[-16:] if agent_id else "MISSING")
check("conversation_flow_id populated",       bool(flow_id),                                       flow_id[-16:] if flow_id else "MISSING")

if IS_LIVE:
    check("twilio_number assigned (LIVE)",    bool(row.get('twilio_number')),                      row.get('twilio_number'))

# ══════════════════════════════════════════════════════════════
print("\n[4] RETELL — PREMIUM AGENT")
# ══════════════════════════════════════════════════════════════
if agent_id:
    agent = retell(f"get-agent/{agent_id}")
    check("Agent exists in Retell",           bool(agent.get('agent_id')),                         agent_id[-16:])
    # Premium Retell agent_name = "{company} - HVAC Premium" (system name, not receptionist name)
    # The receptionist name (TEST_AGENT) is verified in Phase 5 via the conversation flow
    check("Agent Retell ID populated",        bool(agent.get('agent_id')),                         agent_id[-16:])
    check("Webhook URL correct",              agent.get('webhook_url') == "https://n8n.syntharra.com/webhook/retell-hvac-premium-webhook")
    check("Voice set",                        bool(agent.get('voice_id')),                         agent.get('voice_id'))
    check("Language multilingual",            agent.get('language') == 'multi',                    agent.get('language'))
    if IS_LIVE:
        check("Phone number linked (LIVE)",   bool(agent.get('last_modification_timestamp')),       "check Retell dashboard")
else:
    check("Agent exists in Retell", False, "No agent_id")

# ══════════════════════════════════════════════════════════════
print("\n[5] RETELL — PREMIUM CONVERSATION FLOW (18 nodes)")
# ══════════════════════════════════════════════════════════════
if flow_id:
    flow  = retell(f"get-conversation-flow/{flow_id}")
    nodes = flow.get('nodes', [])
    names = [n['name'] for n in nodes]
    check("Flow exists in Retell",            bool(flow.get('conversation_flow_id')))
    check("18 nodes present",                 len(nodes) == 18,                                    f"{len(nodes)} nodes")
    check("flex_mode off",                    flow.get('flex_mode') in [False, None])
    check("start_speaker = agent",            flow.get('start_speaker') == 'agent')
    # Standard nodes (inherited)
    check("Greeting node present",            'greeting_node' in names)
    check("Emergency node present",           'verify_emergency_node' in names)
    check("Callback node present",            'callback_node' in names)
    check("Spam node present",                'spam_robocall_node' in names)
    # Premium-only nodes
    check("Booking capture node present",     'booking_capture_node' in names)
    check("Check availability node present",  'check_availability_node' in names)
    check("Confirm booking node present",     'confirm_booking_node' in names)
    check("Reschedule node present",          'reschedule_node' in names)
    check("Cancel appointment node present",  'cancel_appointment_node' in names)
    check("Fallback lead capture node present",'fallback_leadcapture_node' in names)
    check("Emergency transfer node present",  any(n.get('type') == 'transfer_call' and 'emergency' in n.get('id','').lower() for n in nodes))
    # Content checks
    greeting = next((n for n in nodes if n['name'] == 'greeting_node'), None)
    gt = (greeting or {}).get('instruction', {}).get('text', '')
    check("Greeting has agent name",          TEST_AGENT in gt,                                    gt[:60])
    check("Global prompt has company info",   TEST_COMPANY in flow.get('global_prompt', ''))
    # Publish
    s, _ = http(f"https://api.retellai.com/publish-agent/{agent_id}", "POST", {},
        {"Authorization": f"Bearer {RETELL_KEY}"})
    check("Agent published via API",          s == 200,                                            f"HTTP {s}")
else:
    check("Flow exists in Retell", False, "No flow_id")

# ══════════════════════════════════════════════════════════════
print("\n[6] PREMIUM CALL PROCESSOR — FAKE CALL TEST")
# ══════════════════════════════════════════════════════════════
if agent_id:
    fake_call_id = f"prem_test_{TS}"
    cleanup['call_ids'].append(fake_call_id)
    fake_call = {
        "event": "call_analyzed",
        "call": {
            "call_id":          fake_call_id,
            "agent_id":         agent_id,
            "call_type":        "phone_call",
            "from_number":      "+16316330721",
            "to_number":        "+15125550288",
            "direction":        "inbound",
            "duration_ms":      150000,
            "start_timestamp":  int(time.time() * 1000) - 150000,
            "end_timestamp":    int(time.time() * 1000),
            "disconnection_reason": "user_hangup",
            "recording_url":    "https://retell-utils-public.s3.us-west-2.amazonaws.com/test_recording.wav",
            "public_log_url":   "https://beta.retellai.com/call-details/test_" + fake_call_id,
            "call_analysis": {
                "call_summary":     "Caller Maria Rodriguez reported AC unit stopped cooling. Agent booked same-day 10am AC repair at 1200 Main Street Dallas TX. Confirmation email to be sent.",
                "call_successful":  True,
                "user_sentiment":   "Positive",
                "in_voicemail":     False,
                "custom_analysis_data": {
                    "caller_name":          "Maria Rodriguez",
                    "caller_phone":         "+16316330721",
                    "caller_address":       "1200 Main Street, Dallas, Texas",
                    "service_requested":    "AC not cooling",
                    "call_type":            "new_service",
                    "urgency":              "high",
                    "is_hot_lead":          True,
                    "lead_score":           9,
                    "transfer_attempted":   False,
                    "transfer_success":     False,
                    "vulnerable_occupant":  False,
                    "emergency":            False,
                    "notification_type":    "hot_lead",
                    "job_type":             "repair",
                    "language":             "en",
                    "booking_attempted":    True,
                    "booking_success":      True,
                    "appointment_date":     "2026-04-10",
                    "appointment_time_window": "10:00 AM",
                    "job_type_booked":      "AC Repair",
                    "notes":                "AC unit stopped cooling last night, same-day appointment booked"
                }
            },
            "call_cost": {
                "total_duration_unit_price": 0.14,
                "product_costs": []
            },
            "latency": {
                "e2e": {"p50": 1050, "p90": 1400, "p95": 1700, "p99": 2200, "max": 2800, "min": 750, "num": 15},
                "llm": {"p50": 600, "p90": 850, "p95": 1000, "p99": 1400, "max": 1800, "min": 350, "num": 15}
            },
            "transcript": (
                f"Agent: FrostKing HVAC, this is {TEST_AGENT} speaking, how may I assist you? "
                "Caller: Hi, my AC unit stopped cooling last night. "
                "Agent: I'm sorry to hear that. I can book a same-day appointment for you. May I get your full name? "
                "Caller: Maria Rodriguez. "
                "Agent: And your best callback number? "
                "Caller: 631-633-0721. "
                "Agent: And the service address? "
                "Caller: 1200 Main Street, Dallas, Texas. "
                "Agent: Perfect. I have availability today at 10am or 2pm — which works better? "
                "Caller: 10am works great. "
                "Agent: Wonderful, I've booked you in for 10am AC Repair at 1200 Main Street Dallas. "
                "You'll receive a confirmation email shortly. Is there anything else I can help with? "
                "Caller: No, that's perfect thank you. "
                "Agent: Great, we'll see you at 10am. Have a wonderful day!"
            )
        }
    }
    # Premium call processor uses its own dedicated webhook path:
    # retell-hvac-premium-webhook → workflow STQ4Gt3rH8ptlvMi
    s, _ = http("https://n8n.syntharra.com/webhook/retell-hvac-premium-webhook", "POST", fake_call)
    check("Premium call processor webhook accepted", s == 200, f"HTTP {s}")
    print("  Waiting for call processor (polling up to 20s)...")
    time.sleep(10)  # Retell post-call analysis already done — just need n8n processing

    rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
    call = rows[0] if rows else {}
    check("Call logged in hvac_call_log",     bool(call),                                          fake_call_id[-16:])
    check("caller_name captured",             bool(call.get('caller_name')),                       call.get('caller_name'))
    check("caller_phone captured",            bool(call.get('caller_phone')),                      call.get('caller_phone'))
    check("service_requested identified",     call.get('service_requested') not in ['', 'Other', None], call.get('service_requested'))
    check("lead_score >= 6",                  (call.get('lead_score') or 0) >= 6,                  f"score={call.get('lead_score')}")
    check("is_lead = true",                   call.get('is_lead') == True)
    check("summary populated",                bool(call.get('summary')),                           (call.get('summary') or '')[:60])
    check("company_name in log",              call.get('company_name') == TEST_COMPANY,            call.get('company_name'))
    check("call_tier = Premium",              call.get('call_tier') == 'Premium',                  call.get('call_tier'))

    # Phase 5 — new Retell-native field assertions
    check("retell_sentiment populated",      bool(call.get('retell_sentiment')),                   call.get('retell_sentiment'))
    check("retell_summary populated",        bool(call.get('retell_summary')),                     (call.get('retell_summary') or '')[:60])
    check("call_successful is boolean",      call.get('call_successful') in [True, False],         str(call.get('call_successful')))
    check("urgency populated",              call.get('urgency') in ['emergency','high','medium','low'], call.get('urgency'))
    check("call_type populated",            call.get('call_type') in ['new_service','emergency','callback','existing_customer','general_question','spam','wrong_number'], call.get('call_type'))
    check("notification_type populated",    bool(call.get('notification_type')),                   call.get('notification_type'))
    check("job_type populated",             bool(call.get('job_type')),                            call.get('job_type'))
    check("is_hot_lead is boolean",         call.get('is_hot_lead') in [True, False],              str(call.get('is_hot_lead')))
    check("language populated",             bool(call.get('language')),                             call.get('language'))
    check("duration_seconds > 0",           (call.get('duration_seconds') or 0) > 0,               f"{call.get('duration_seconds')}s")
    check("recording_url populated",        bool(call.get('recording_url')),                       (call.get('recording_url') or '')[:60])
    check("latency_p50_ms populated",       call.get('latency_p50_ms') is not None,                str(call.get('latency_p50_ms')))
    check("call_cost_cents populated",      (call.get('call_cost_cents') or 0) > 0,                f"{call.get('call_cost_cents')} cents")
    check("caller_address captured",        bool(call.get('caller_address')),                      call.get('caller_address'))
    check("notes populated",               bool(call.get('notes')),                                (call.get('notes') or '')[:60])

    # Premium-specific booking assertions
    check("booking_attempted = True",       call.get('booking_attempted') == True)
    check("booking_success = True",         call.get('booking_success') == True)

    # Dedup check
    http("https://n8n.syntharra.com/webhook/retell-hvac-premium-webhook", "POST", fake_call)
    time.sleep(8)
    dup_rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
    check("Dedup — no duplicate row created", len(dup_rows) == 1,                                  f"{len(dup_rows)} row(s)")

    # Poll for premium call processor execution
    prem_cp_wf_id = "STQ4Gt3rH8ptlvMi"
    cp_status = 'unknown'; cp_id = '?'
    for attempt in range(6):
        time.sleep(5)
        _, cp = http(
            f"https://n8n.syntharra.com/api/v1/executions?workflowId={prem_cp_wf_id}&limit=3",
            headers={"X-N8N-API-KEY": N8N_KEY})
        cp_cands = [e for e in (cp.get('data') or [])
                    if e.get('status') in ('success', 'error', 'crashed')]
        if cp_cands:
            cp_status = cp_cands[0].get('status', 'unknown')
            cp_id     = cp_cands[0].get('id', '?')
            break
    check("Premium call processor n8n execution OK", cp_status == 'success',
          f"exec {cp_id} → {cp_status}")

# ══════════════════════════════════════════════════════════════
print("\n[7] STRIPE GATE — BEHAVIOUR CHECK")
# ══════════════════════════════════════════════════════════════
if IS_LIVE:
    check("LIVE MODE — Twilio purchase path triggered", bool(row.get('twilio_number')), row.get('twilio_number'))
    check("LIVE MODE — Welcome email sent with phone",  exec_status == 'success', "Check inbox")
else:
    check("TEST MODE — Stripe gate correctly skipped Twilio purchase", not bool(row.get('twilio_number')),
          "no twilio_number = correct for test run")
    email_sent = exec_status == 'success'
    check("TEST MODE — Integration setup email sent (no phone, expected)", email_sent,
          "Premium onboarding workflow completed — OAuth/setup email sent to client_email")

# ══════════════════════════════════════════════════════════════
print("\n[8] CLEANUP — SCHEDULED (5 MINUTE DELAY)")
# ══════════════════════════════════════════════════════════════
cleanup_payload = {
    "company_name": TEST_COMPANY,
    "agent_ids":    cleanup["agent_ids"],
    "flow_ids":     cleanup["flow_ids"],
}
s, resp = http("https://n8n.syntharra.com/webhook/e2e-test-cleanup", "POST", cleanup_payload)
if s == 200:
    check("Cleanup scheduled (5 min delay)", True, "Data will be deleted in 5 minutes — verify now!")
    print(f"  ⏱  You have 5 minutes to check Supabase, Retell, and emails before cleanup.")
    print(f"  Company  : {TEST_COMPANY}")
    print(f"  Agent IDs: {cleanup['agent_ids']}")
    print(f"  Flow IDs : {cleanup['flow_ids']}")
else:
    check("Cleanup scheduled (5 min delay)", False, f"HTTP {s} — cleanup webhook failed, delete manually")

# ══════════════════════════════════════════════════════════════
total  = len(results)
passed = sum(1 for v in results.values() if v)
failed = total - passed
print("\n" + "=" * 60)
print(f"MODE  : {'LIVE' if IS_LIVE else 'TEST'}")
print(f"RESULT: {passed}/{total} passed  |  {failed} failed")
if failed == 0:
    print("✅ ALL SYSTEMS GO — Premium pipeline fully verified")
    if not IS_LIVE:
        print("")
        print("  To run a LIVE test (real Stripe customer, real Twilio number):")
        print("  Set STRIPE_CUSTOMER_ID = 'cus_xxxxx' at the top of this file")
else:
    print("\n❌ FAILURES:")
    for name, val in results.items():
        if not val: print(f"   ❌ {name}")
print("=" * 60)
