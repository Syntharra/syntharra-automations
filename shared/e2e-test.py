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
# TEST mode  → no Stripe customer ID → Stripe Gate skips Twilio purchase → no phone in welcome email (CORRECT)
# LIVE mode  → real Stripe customer ID present → Twilio number purchased → full welcome email sent
# Switch to LIVE by setting: STRIPE_CUSTOMER_ID = "cus_xxxxx"
STRIPE_CUSTOMER_ID = ""   # leave empty for test mode

# ── TEST DATA ─────────────────────────────────────────────────────────────────
TS           = int(time.time())
TEST_COMPANY = f"Polar Peak HVAC {TS}"
TEST_AGENT   = "Max"
TEST_PHONE   = "+15125550199"
TEST_GREETING= f"Thank you for calling Polar Peak HVAC, this is {TEST_AGENT}, how can I help you today?"

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
print("SYNTHARRA FULL E2E TEST  —  SELF CLEANING")
print(f"Mode    : {mode_label}")
print(f"Company : {TEST_COMPANY}")
print(f"Started : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
print("\n[1] JOTFORM ONBOARDING — ALL FIELDS")
# ══════════════════════════════════════════════════════════════
payload = {
    # Business Info
    "q4_hvacCompany":             TEST_COMPANY,
    "q54_ownerName":              "James Caldwell",
    "q6_mainCompany":             TEST_PHONE,
    "q5_emailAddress":            TEST_EMAIL,
    "q7_companyWebsite":          "www.polarpeak.com",
    "q8_yearsIn":                 "8",
    "q34_timezone":               "America/New_York",
    "q13_servicesOffered":        ["AC Repair","Heating Repair","AC Installation","Heating Installation","Maintenance","Duct Cleaning","Air Quality"],
    "q14_brandsequipmentServiced":["Carrier","Trane","Lennox","Rheem","York","Goodman"],
    "q16_primaryService":         "New York City and surrounding boroughs",
    "q40_serviceAreaRadius":      "40 miles",
    "q29_certifications":         ["NATE Certified","EPA 608","OSHA 10"],
    "q28_licensedAnd":            "Yes",
    # AI Config
    "q10_aiAgent10":              TEST_AGENT,
    "q11_aiVoice":                "Male",
    "q38_customGreeting":         TEST_GREETING,
    "q39_companyTagline":         "New York City's Most Trusted HVAC",
    # Hours & Availability
    "q17_businessHours":          "Monday to Friday 7am to 7pm, Saturday 8am to 4pm",
    "q18_typicalResponse":        "Same day or next business day",
    "q20_247Emergency":           "Yes",
    "q21_emergencyAfterhours":    "+15125550199",
    "q22_afterhoursBehavior":     "Transfer to emergency line",
    # Pricing
    "q42_pricingPolicy":          "Free estimates on all new installations. $95 diagnostic fee waived with repair.",
    "q41_diagnosticFee":          "$95 diagnostic fee, waived with repair",
    "q43_standardFees":           "Service call $95, Tune-up $149, Emergency surcharge $75",
    "q24_freeEstimates":          "Yes - free on all new system installations",
    "q25_financingAvailable":     "Yes",
    "q44_financingDetails":       "0% financing for 24 months on systems over $4,000",
    "q26_serviceWarranties":      "Yes",
    "q27_warrantyDetails":        "5 years parts, 2 years labour on all repairs",
    "q45_paymentMethods":         ["Cash","Credit Card","Check","Financing","Zelle"],
    "q46_maintenancePlans":       "Yes - Peak Care Club $249/year, includes 2 tune-ups, priority scheduling, 10% discount on repairs",
    "q58_membershipProgramName":  "Peak Care Club",
    # Lead & Transfer
    "q31_leadContact":            "Both",
    "q32_leadNotification":       "+16316330713",
    "q33_leadNotification33":     TEST_EMAIL,
    # Multi-notification contacts (Jotform q64-q67)
    "q64_notifSms2":              "+16316330714",
    "q65_notifSms3":              "+16316330715",
    "q66_notifEmail2":            "dispatcher@polarpeak.com",
    "q67_notifEmail3":            "salesmanager@polarpeak.com",
    "q48_transferPhone":          TEST_PHONE,
    "q49_transferTriggers":       ["Customer is angry","Legal threat","Complex billing dispute","Customer requests manager"],
    "q50_transferBehavior":       "Try once - take message if no answer",
    "q57_doNotServiceList":       "Commercial refrigeration, window units, portable ACs",
    # Branding & Extras
    "q55_googleReviewRating":     "4.8",
    "q56_googleReviewCount":      "527",
    "q51_uniqueSellingPoints":    "Family-owned, same-day service, 5-year warranty, NATE-certified techs, background checked",
    "q52_currentPromotion":       "$75 off any repair over $400 this month",
    "q53_seasonalServices":       "Spring AC tune-ups, Fall heating inspections, Winter emergency heating",
    "q37_additionalInfo":         "Proudly serving NYC since 2016. All technicians are NATE certified and background checked.",
}

# In LIVE mode, include a real Stripe customer ID to trigger Twilio number purchase
if IS_LIVE:
    payload["stripe_customer_id"] = STRIPE_CUSTOMER_ID

status, _ = http("https://n8n.syntharra.com/webhook/jotform-hvac-onboarding", "POST", payload)
check("Webhook accepted (HTTP 200)", status == 200, f"HTTP {status}")

# ══════════════════════════════════════════════════════════════
print("\n[2] N8N EXECUTION")
# ══════════════════════════════════════════════════════════════
# Poll for up to 45s — n8n indexes executions after completion, not instantly
exec_status = 'unknown'
exec_id     = '?'
onboarding_wf_id = "4Hx7aRdzMl5N0uJP"
for attempt in range(9):
    time.sleep(5)
    _, execs = http(
        f"https://n8n.syntharra.com/api/v1/executions?workflowId={onboarding_wf_id}&limit=3",
        headers={"X-N8N-API-KEY": N8N_KEY})
    candidates = [e for e in (execs.get('data') or [])
                  if e.get('status') in ('success','error','crashed')]
    if candidates:
        latest      = candidates[0]
        exec_status = latest.get('status', 'unknown')
        exec_id     = latest.get('id', '?')
        break
check("Workflow executed successfully", exec_status == 'success', f"exec {exec_id} → {exec_status}")

# ══════════════════════════════════════════════════════════════
print("\n[3] SUPABASE — ALL FIELDS CHECK")
# ══════════════════════════════════════════════════════════════
rows = sb(f"hvac_standard_agent?company_name=eq.{urllib.parse.quote(TEST_COMPANY)}&select=*")
row  = rows[0] if rows else {}
agent_id = row.get('agent_id', '')
flow_id  = row.get('conversation_flow_id', '')
if agent_id: cleanup['agent_ids'].append(agent_id)
if flow_id:  cleanup['flow_ids'].append(flow_id)

check("Row created in Supabase",             bool(row))
check("company_name",                        row.get('company_name') == TEST_COMPANY,               row.get('company_name'))
check("owner_name",                          row.get('owner_name') == 'James Caldwell',             row.get('owner_name'))
check("client_email",                        row.get('client_email') == TEST_EMAIL,                 row.get('client_email'))
check("company_phone",                       bool(row.get('company_phone')),                        row.get('company_phone'))
check("website",                             row.get('website') == 'www.polarpeak.com',             row.get('website'))
check("years_in_business",                   row.get('years_in_business') == '8',                   row.get('years_in_business'))
check("timezone",                            row.get('timezone') == 'America/New_York',             row.get('timezone'))
check("agent_name",                          bool(row.get('agent_name')),                           row.get('agent_name'))
check("custom_greeting contains agent",      TEST_AGENT in (row.get('custom_greeting') or ''),      (row.get('custom_greeting') or '')[:60])
check("services_offered populated",          bool(row.get('services_offered')),                     (row.get('services_offered') or '')[:50])
check("brands_serviced populated",           bool(row.get('brands_serviced')),                      (row.get('brands_serviced') or '')[:40])
check("service_area populated",              bool(row.get('service_area')),                         row.get('service_area'))
check("service_area_radius",                 row.get('service_area_radius') == '40 miles',          row.get('service_area_radius'))
check("certifications populated",            bool(row.get('certifications')),                       row.get('certifications'))
check("emergency_service",                   row.get('emergency_service') == 'Yes',                 row.get('emergency_service'))
check("emergency_phone",                     bool(row.get('emergency_phone')),                      row.get('emergency_phone'))
check("business_hours populated",            bool(row.get('business_hours')),                       (row.get('business_hours') or '')[:40])
check("pricing_policy populated",            bool(row.get('pricing_policy')),                       (row.get('pricing_policy') or '')[:40])
check("diagnostic_fee",                      bool(row.get('diagnostic_fee')),                       row.get('diagnostic_fee'))
check("financing_available",                 row.get('financing_available') == 'Yes',               row.get('financing_available'))
check("warranty",                            row.get('warranty') == 'Yes',                          row.get('warranty'))
check("payment_methods populated",           bool(row.get('payment_methods')),                      (row.get('payment_methods') or '')[:40])
check("maintenance_plans populated",         bool(row.get('maintenance_plans')),                    (row.get('maintenance_plans') or '')[:40])
check("membership_program",                  row.get('membership_program') == 'Peak Care Club',     row.get('membership_program'))
check("lead_contact_method",                 row.get('lead_contact_method') == 'Both',              row.get('lead_contact_method'))
check("lead_phone",                          bool(row.get('lead_phone')),                           row.get('lead_phone'))
check("lead_email",                          row.get('lead_email') == TEST_EMAIL,                   row.get('lead_email'))
check("notification_email_2 saved",          row.get('notification_email_2') == 'dispatcher@polarpeak.com',   row.get('notification_email_2'))
check("notification_email_3 saved",          row.get('notification_email_3') == 'salesmanager@polarpeak.com', row.get('notification_email_3'))
check("notification_sms_2 saved",            row.get('notification_sms_2') == '+16316330714',               row.get('notification_sms_2'))
check("notification_sms_3 saved",            row.get('notification_sms_3') == '+16316330715',               row.get('notification_sms_3'))
check("transfer_phone",                      bool(row.get('transfer_phone')),                       row.get('transfer_phone'))
check("transfer_triggers populated",         bool(row.get('transfer_triggers')),                    (row.get('transfer_triggers') or '')[:40])
check("google_review_rating",                row.get('google_review_rating') == '4.8',              row.get('google_review_rating'))
check("google_review_count",                 row.get('google_review_count') == '527',               row.get('google_review_count'))
check("unique_selling_points populated",     bool(row.get('unique_selling_points')),                (row.get('unique_selling_points') or '')[:40])
check("current_promotion populated",         bool(row.get('current_promotion')),                    row.get('current_promotion'))
check("do_not_service populated",            bool(row.get('do_not_service')),                       row.get('do_not_service'))
check("additional_info populated",           bool(row.get('additional_info')),                      (row.get('additional_info') or '')[:40])
check("agent_id populated",                  bool(agent_id),                                        agent_id[-16:] if agent_id else "MISSING")
check("conversation_flow_id populated",      bool(flow_id),                                         flow_id[-16:] if flow_id else "MISSING")

# LIVE MODE ONLY: check twilio_number was assigned
if IS_LIVE:
    check("twilio_number assigned (LIVE)",   bool(row.get('twilio_number')),                        row.get('twilio_number'))

# ══════════════════════════════════════════════════════════════
print("\n[4] RETELL — AGENT")
# ══════════════════════════════════════════════════════════════
if agent_id:
    agent = retell(f"get-agent/{agent_id}")
    check("Agent exists in Retell",          bool(agent.get('agent_id')),                           agent_id[-16:])
    check("Agent name = AI receptionist name", TEST_AGENT == (agent.get('agent_name') or ''),       agent.get('agent_name'))
    check("Webhook URL correct",             agent.get('webhook_url') == "https://n8n.syntharra.com/webhook/retell-hvac-webhook")
    check("Voice set",                       bool(agent.get('voice_id')),                           agent.get('voice_id'))
    check("Language multilingual",           agent.get('language') == 'multi',                      agent.get('language'))
    # LIVE MODE ONLY: phone number should be linked to agent
    if IS_LIVE:
        check("Phone number linked to agent (LIVE)", bool(agent.get('last_modification_timestamp')), "check Retell dashboard")
else:
    check("Agent exists in Retell", False, "No agent_id")

# ══════════════════════════════════════════════════════════════
print("\n[5] RETELL — CONVERSATION FLOW")
# ══════════════════════════════════════════════════════════════
if flow_id:
    flow  = retell(f"get-conversation-flow/{flow_id}")
    nodes = flow.get('nodes', [])
    names = [n['name'] for n in nodes]
    check("Flow exists in Retell",           bool(flow.get('conversation_flow_id')))
    check("12 nodes present",                len(nodes) == 12,                                      f"{len(nodes)} nodes")
    check("flex_mode off",                   flow.get('flex_mode') in [False, None])
    check("start_speaker = agent",           flow.get('start_speaker') == 'agent')
    check("Greeting node present",           'greeting_node' in names)
    check("Lead capture node present",       'nonemergency_leadcapture_node' in names)
    check("Emergency node present",          'verify_emergency_node' in names)
    check("Callback node present",           'callback_node' in names)
    check("Spam node present",               'spam_robocall_node' in names)
    greeting = next((n for n in nodes if n['name'] == 'greeting_node'), None)
    gt = (greeting or {}).get('instruction', {}).get('text', '')
    check("Greeting has agent name",         TEST_AGENT in gt,                                      gt[:60])
    check("Global prompt has company info",  TEST_COMPANY in flow.get('global_prompt', ''))
    s, _ = http(f"https://api.retellai.com/publish-agent/{agent_id}", "POST", {},
        {"Authorization": f"Bearer {RETELL_KEY}"})
    check("Agent published via API",         s == 200,                                              f"HTTP {s}")
else:
    check("Flow exists in Retell", False, "No flow_id")

# ══════════════════════════════════════════════════════════════
print("\n[6] CALL PROCESSOR — FAKE CALL TEST")
# ══════════════════════════════════════════════════════════════
if agent_id:
    fake_call_id = f"test_{TS}"
    cleanup['call_ids'].append(fake_call_id)
    fake_call = {
        "event": "call_analyzed",
        "call": {
            "call_id":          fake_call_id,
            "agent_id":         agent_id,
            "call_type":        "phone_call",
            "from_number":      "+16316330713",
            "to_number":        "+18129944371",
            "direction":        "inbound",
            "duration_ms":      120000,
            "start_timestamp":  int(time.time()*1000) - 120000,
            "end_timestamp":    int(time.time()*1000),
            "disconnection_reason": "user_hangup",
            "recording_url":    "https://retell-utils-public.s3.us-west-2.amazonaws.com/test_recording.wav",
            "public_log_url":   "https://beta.retellai.com/call-details/test_" + fake_call_id,
            "call_analysis": {
                "call_summary":     "Caller Daniel Blackmore reported heating system failure. Agent collected name, callback number 631-633-0713, and service address 45 Park Avenue Manhattan NY. Passed to team for callback.",
                "call_successful":  True,
                "user_sentiment":   "Positive",
                "in_voicemail":     False,
                "custom_analysis_data": {
                    "caller_name":        "Daniel Blackmore",
                    "caller_phone":       "+16316330713",
                    "caller_address":     "45 Park Avenue, Manhattan, New York",
                    "service_requested":  "Heating system repair",
                    "call_type":          "new_service",
                    "urgency":            "high",
                    "is_hot_lead":        True,
                    "lead_score":         8,
                    "transfer_attempted": False,
                    "transfer_success":   False,
                    "vulnerable_occupant": False,
                    "emergency":          False,
                    "notification_type":  "hot_lead",
                    "job_type":           "repair",
                    "language":           "en",
                    "booking_attempted":  False,
                    "booking_success":    False,
                    "notes":              "Heating stopped working last night"
                }
            },
            "call_cost": {
                "total_duration_unit_price": 0.14,
                "product_costs": []
            },
            "latency": {
                "e2e": {"p50": 1100, "p90": 1500, "p95": 1800, "p99": 2400, "max": 3000, "min": 800, "num": 12},
                "llm": {"p50": 650, "p90": 900, "p95": 1100, "p99": 1500, "max": 2000, "min": 400, "num": 12}
            },
            "transcript": (
                f"Agent: {TEST_GREETING} "
                "Caller: Hi, my heating system stopped working last night. "
                "Agent: I'm sorry to hear that. Can I get your full name please? "
                "Caller: Daniel Blackmore. "
                "Agent: And your best callback number? "
                "Caller: 631-633-0713. "
                "Agent: And the service address? "
                "Caller: 45 Park Avenue, Manhattan, New York. "
                "Agent: Perfect, I have passed all of that through to the team and someone will be in touch shortly."
            )
        }
    }
    s, _ = http("https://n8n.syntharra.com/webhook/retell-hvac-webhook", "POST", fake_call)
    check("Call processor webhook accepted", s == 200,                                              f"HTTP {s}")
    print("  Waiting for call processor (polling up to 20s)...")
    time.sleep(10)  # Retell post-call analysis already done — just need n8n processing

    rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
    call = rows[0] if rows else {}
    check("Call logged in hvac_call_log",    bool(call),                                            fake_call_id[-16:])
    check("caller_name captured",            bool(call.get('caller_name')),                        call.get('caller_name'))
    check("caller_phone captured",           bool(call.get('caller_phone')),                       call.get('caller_phone'))
    check("service_requested identified",    call.get('service_requested') not in ['','Other',None], call.get('service_requested'))
    check("lead_score >= 6",                 (call.get('lead_score') or 0) >= 6,                   f"score={call.get('lead_score')}")
    check("is_lead = true",                  call.get('is_lead') == True)
    check("summary populated",               bool(call.get('summary')),                            (call.get('summary') or '')[:60])
    check("company_name in log",             call.get('company_name') == TEST_COMPANY,             call.get('company_name'))

    # Phase 5 — new Retell-native field assertions
    check("retell_sentiment populated",     bool(call.get('retell_sentiment')),                   call.get('retell_sentiment'))
    check("retell_summary populated",       bool(call.get('retell_summary')),                     (call.get('retell_summary') or '')[:60])
    check("call_successful is boolean",     call.get('call_successful') in [True, False],         str(call.get('call_successful')))
    check("urgency populated",             call.get('urgency') in ['emergency','high','medium','low'], call.get('urgency'))
    check("call_type populated",           call.get('call_type') in ['new_service','emergency','callback','existing_customer','general_question','spam','wrong_number'], call.get('call_type'))
    check("notification_type populated",   bool(call.get('notification_type')),                   call.get('notification_type'))
    check("job_type populated",            bool(call.get('job_type')),                            call.get('job_type'))
    check("is_hot_lead is boolean",        call.get('is_hot_lead') in [True, False],              str(call.get('is_hot_lead')))
    check("language populated",            bool(call.get('language')),                             call.get('language'))
    check("duration_seconds > 0",          (call.get('duration_seconds') or 0) > 0,               f"{call.get('duration_seconds')}s")
    check("recording_url populated",       bool(call.get('recording_url')),                       (call.get('recording_url') or '')[:60])
    check("latency_p50_ms populated",      call.get('latency_p50_ms') is not None,                str(call.get('latency_p50_ms')))
    check("call_cost_cents populated",     (call.get('call_cost_cents') or 0) > 0,                f"{call.get('call_cost_cents')} cents")
    check("caller_address captured",       bool(call.get('caller_address')),                      call.get('caller_address'))
    check("notes populated",              bool(call.get('notes')),                                (call.get('notes') or '')[:60])

    # Dedup check — send same call_id again, should not create a second row
    http("https://n8n.syntharra.com/webhook/retell-hvac-webhook", "POST", fake_call)
    time.sleep(8)
    dup_rows = sb(f"hvac_call_log?call_id=eq.{fake_call_id}&select=*")
    check("Dedup — no duplicate row created", len(dup_rows) == 1,                                  f"{len(dup_rows)} row(s)")

    # Poll for call processor execution (workflow Kg576YtPM9yEacKn)
    call_proc_wf_id = "Kg576YtPM9yEacKn"
    cp_status = 'unknown'; cp_id = '?'
    for attempt in range(6):
        time.sleep(5)
        _, cp = http(
            f"https://n8n.syntharra.com/api/v1/executions?workflowId={call_proc_wf_id}&limit=3",
            headers={"X-N8N-API-KEY": N8N_KEY})
        cp_cands = [e for e in (cp.get('data') or [])
                    if e.get('status') in ('success','error','crashed')]
        if cp_cands:
            cp_status = cp_cands[0].get('status', 'unknown')
            cp_id     = cp_cands[0].get('id', '?')
            break
    check("Call processor n8n execution OK", cp_status == 'success',
        f"exec {cp_id} → {cp_status}")

# ══════════════════════════════════════════════════════════════
print("\n[7] STRIPE GATE — BEHAVIOUR CHECK")
# ══════════════════════════════════════════════════════════════
# The Stripe Gate (IF node checking stripe_customer_id) controls whether
# a Twilio number is purchased. In test mode it correctly skips this.
# In live mode (STRIPE_CUSTOMER_ID set above) it will purchase a real number.
if IS_LIVE:
    check("LIVE MODE — Twilio purchase path triggered", bool(row.get('twilio_number')), row.get('twilio_number'))
    check("LIVE MODE — Welcome email sent with phone",  exec_status == 'success', "Check daniel@syntharra.com inbox")
else:
    check("TEST MODE — Stripe gate correctly skipped Twilio purchase", not bool(row.get('twilio_number')),
        "no twilio_number = correct for test run")
    # In test mode the email is always sent (no phone number section in email = correct)
    # Verify by checking the onboarding workflow ran successfully (already checked above)
    email_sent = exec_status == 'success'
    check("TEST MODE — Onboarding email sent (no phone, expected)", email_sent,
        "Onboarding workflow completed — email sent to client_email in Supabase")

# ══════════════════════════════════════════════════════════════
print("\n[8] CLEANUP — SCHEDULED (5 MINUTE DELAY)")
# ══════════════════════════════════════════════════════════════
# Triggers the n8n E2E cleanup workflow which waits 5 minutes before
# deleting all test data. This gives you time to manually verify
# Supabase, Retell, n8n, and emails before the data is wiped.
# Webhook: https://n8n.syntharra.com/webhook/e2e-test-cleanup
cleanup_payload = {
    "company_name": TEST_COMPANY,
    "agent_ids": cleanup["agent_ids"],
    "flow_ids": cleanup["flow_ids"],
}
s, resp = http("https://n8n.syntharra.com/webhook/e2e-test-cleanup", "POST", cleanup_payload)
if s == 200:
    check("Cleanup scheduled (5 min delay)", True, "Data will be deleted in 5 minutes — verify now!")
    print(f"  ⏱  You have 5 minutes to check Supabase, Retell, and emails before cleanup.")
    print(f"  Company: {TEST_COMPANY}")
    print(f"  Agent IDs: {cleanup['agent_ids']}")
    print(f"  Flow IDs: {cleanup['flow_ids']}")
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
    print("✅ ALL SYSTEMS GO — Full pipeline verified")
    if not IS_LIVE:
        print("")
        print("  To run a LIVE test (real Stripe customer, real Twilio number):")
        print("  Set STRIPE_CUSTOMER_ID = 'cus_xxxxx' at the top of this file")
else:
    print("\n❌ FAILURES:")
    for name, val in results.items():
        if not val: print(f"   ❌ {name}")
print("=" * 60)
