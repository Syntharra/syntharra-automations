"""
Standard Call Processor — Full 20-Scenario Test
Fire with 12s spacing to stay within Groq free-tier RPM limit.
"""
import urllib.request, json, time

SUPABASE = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_ANON  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0"
SB_SVC   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
WEBHOOK  = "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"
INTER_CALL_DELAY = 12   # seconds between fires — stays within Groq ~30 RPM free tier

def http(url, method="GET", body=None, headers={}):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e: return e.code, {}
    except Exception: return 0, {}

def fire_wait(cid, payload, max_wait=40):
    s, _ = http(WEBHOOK, "POST", payload)
    if s != 200: return None, f"webhook HTTP {s}"
    polls = max_wait // 5
    for _ in range(polls):
        time.sleep(5)
        _, rows = http(f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}&select=*",
            headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}"})
        if isinstance(rows, list) and rows: return rows[0], None
    return None, f"timeout {max_wait}s"

def clean(cid):
    req = urllib.request.Request(f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}",
        headers={"apikey": SB_SVC, "Authorization": f"Bearer {SB_SVC}",
                 "Content-Type": "application/json"}, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10): pass
    except: pass

def mkp(ts, sid, t):
    cid = f"cp20_{ts}_{sid:02d}"
    return cid, {"event": "call_analyzed", "call": {
        "call_id": cid, "agent_id": AGENT_ID, "call_status": "ended",
        "from_number": "+16315550100", "to_number": "+18129944371",
        "start_timestamp": int(time.time()*1000)-90000,
        "end_timestamp": int(time.time()*1000),
        "disconnection_reason": "user_hangup", "call_analysis": {},
        "transcript": t
    }}

R = {}
def chk(sid, label, ok, detail=""):
    R[f"#{sid:02d} {label}"] = ok
    print(f"    {'✅' if ok else '❌'} {label}" + (f"  → {detail}" if detail else ""))

def af(row, field, rule, sid):
    v = row.get(field)
    if rule[0] == "present":    chk(sid, f"{field} present", bool(v), str(v)[:45] if v else "MISSING")
    elif rule[0] == "eq":       chk(sid, f"{field}=={rule[1]}", v == rule[1], str(v))
    elif rule[0] == "gte":      chk(sid, f"{field}>={rule[1]}", (int(v) if v is not None else 0) >= rule[1], f"={v}")
    elif rule[0] == "contains": chk(sid, f"{field}~'{rule[1]}'", rule[1].lower() in str(v or "").lower(), str(v)[:45])
    elif rule[0] == "truthy":   chk(sid, f"{field} truthy", bool(v), str(v))

TS = int(time.time())

TESTS = [
    (1,  "Standard repair lead",
     "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie, how can I help you today? Caller: Hi there, my air conditioning unit completely stopped working this morning. It is making a loud clicking noise and is not cooling the house at all. Agent: I am sorry to hear that. Can I get your full name please? Caller: Sure, Mike Johnson. Agent: And your best callback number? Caller: 631-555-0199. Agent: And the service address? Caller: 22 Oak Street, Brooklyn, New York. Agent: Perfect, I have all of that noted. Our team will be in touch with you shortly.",
     {"caller_name":("contains","Johnson"), "caller_phone":("present",), "caller_address":("present",),
      "service_requested":("present",), "job_type":("contains","Repair"), "lead_score":("gte",6), "is_lead":("eq",True)}),

    (2,  "New installation quote",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hi, I am looking to replace my old gas furnace with a new high-efficiency heat pump system. Agent: Great, we can definitely help with that. What is your name? Caller: Sarah Chen. Agent: And a callback number? Caller: 718-555-0312. Agent: And the property address? Caller: 48 Maple Avenue, Queens, New York. Agent: I have passed that to the team and they will call you to arrange a quote.",
     {"caller_name":("contains","Chen"), "job_type":("contains","Install"), "lead_score":("gte",6), "is_lead":("eq",True)}),

    (3,  "Emergency elderly no heat",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: This is an emergency. We have absolutely no heat in the house and there is an elderly person here who has a heart condition and cannot tolerate the cold at all. Agent: I understand this is a serious emergency. Is there any smell of gas or burning in the house? Caller: No, nothing like that, just no heat. Agent: Okay. Name please? Caller: Robert Hall. Agent: Callback number? Caller: 212-555-0788. Agent: And the address? Caller: 10 Fifth Avenue, Manhattan, New York. Agent: I have marked this as an emergency priority and the team will contact you as soon as possible.",
     {"urgency":("contains","mergency"), "vulnerable_occupant":("truthy",), "lead_score":("gte",7), "is_lead":("eq",True)}),

    (4,  "Maintenance booking",
     "Agent: Arctic Breeze HVAC, this is Sophie, how can I help? Caller: Hello, I would like to schedule an annual maintenance check and tune-up for my HVAC system before summer. Agent: Of course, we can arrange that. Name? Caller: Amanda Torres. Agent: Number? Caller: 917-555-0022. Agent: Address? Caller: 15 Central Park West, New York. Agent: All set, the team will reach out to you to schedule.",
     {"service_requested":("present",), "job_type":("contains","Maintenance"), "is_lead":("eq",True)}),

    (5,  "Wrong number",
     "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. Caller: Oh, I am so sorry, I was trying to reach the takeaway restaurant on the corner. Agent: No problem at all, you have reached Arctic Breeze HVAC. Easy mistake to make. Caller: My apologies, goodbye.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (6,  "Spam robocall",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Attention business owner, this is an automated message. Your Google Business listing has been suspended. Press 1 to speak with a representative. Agent: This appears to be an automated spam call. We only assist with HVAC service requests. Goodbye.",
     {"is_lead":("eq",False)}),

    (7,  "Out of service area",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hi, I need urgent air conditioning repair. I am located in Los Angeles, California. Agent: Thank you for calling. Unfortunately our service area covers only New York City and the surrounding boroughs. We would not be able to assist with a location in Los Angeles. Caller: Understood, thank you anyway.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (8,  "Live transfer gas emergency",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Help, there is a very strong gas smell throughout my entire house right now. This is a serious emergency. Agent: This is a safety emergency. I am connecting you to our emergency line right now immediately. The agent initiated a live transfer to the emergency number. Caller: Please hurry, thank you.",
     {"urgency":("present",), "transfer_attempted":("truthy",), "summary":("present",)}),

    (9,  "Caller hangs up early",
     "Agent: Arctic Breeze HVAC, this is Sophie, how can I help? Caller: Hi, my HVAC system has broken down. Agent: I am sorry to hear that. Can I get your name? Caller: Tom Walsh. Agent: And a callback number? Caller: 516-555-0100. Agent: And the service address? Caller: Actually something has come up, I have to go. I will call back tomorrow.",
     {"caller_name":("present",), "caller_phone":("present",), "summary":("present",)}),

    (10, "High-value commercial",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Good morning. We own and manage a 20-unit apartment complex and we need a comprehensive quote for replacing all HVAC units across the entire building. Agent: That sounds like a significant project. Company name? Caller: Sunrise Property Management. Agent: Contact person? Caller: James Whitfield. Agent: Phone number? Caller: 212-555-0900. Agent: Address? Caller: 300 East 45th Street, Manhattan, New York. Agent: I have noted this as a large commercial project and the team will prioritise calling you.",
     {"lead_score":("gte",8), "is_lead":("eq",True), "caller_name":("present",)}),

    (11, "Phonetic phone number",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hi, my heat pump is making a very loud grinding noise. Agent: Name? Caller: Kevin Lee. Agent: And your best callback number? Caller: Six one seven, five five five, zero one zero two. Agent: Let me confirm that, 617-555-0102? Caller: Yes that is correct. Agent: And the address? Caller: 55 Boylston Street, Boston. Agent: Perfect, all noted and the team will call you.",
     {"caller_phone":("present",), "caller_name":("contains","Lee"), "is_lead":("eq",True)}),

    (12, "Pricing enquiry, no booking intent",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hi, I just want to know how much you charge for a standard diagnostic visit. Agent: Our team will be able to discuss all pricing details when they call you back. Caller: Can you not just give me a rough figure? Agent: I am not able to quote specific prices but the team will cover everything when they reach you. Caller: Alright, I will think about it and maybe call back. Goodbye.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (13, "Short call, silence",
     "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie, how can I help? Caller: [silence] Agent: Hello, is anyone there? I cannot hear you.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (14, "Angry existing customer",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: I am absolutely furious right now. Your company has sent a technician to my house twice already and my air conditioning is still not working. I am seriously considering disputing the charge. Agent: I am truly sorry for the inconvenience and frustration. Let me make sure the right person calls you back urgently. Name? Caller: Gary Mitchell. Agent: Number? Caller: 404-555-0350. Agent: Address? Caller: 88 Peachtree Street, Atlanta, Georgia. Agent: Flagged as urgent priority callback.",
     {"caller_name":("contains","Mitchell"), "is_lead":("eq",True), "caller_sentiment":("gte",4)}),

    (15, "No address given",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hi there, my HVAC system needs servicing. Agent: Of course. Name? Caller: Nina Patel. Agent: Callback number? Caller: 303-555-0410. Agent: And the service address? Caller: I would prefer to give the address directly to the technician when they call. Agent: No problem at all, I will pass your name and number to the team and they will be in touch.",
     {"caller_name":("contains","Patel"), "caller_phone":("present",), "is_lead":("eq",True)}),

    (16, "Vendor supplier",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hello, I am calling from Carrier distribution. I wanted to discuss your parts and equipment account with us and talk about some new pricing. Agent: Thank you for calling. I will take your name and number and have the right person from our team give you a call back. Caller: Sure, my name is Mark Davies and the number is 800-555-0900. Agent: Great, I have noted that.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (17, "Job applicant",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hello, I recently came across your job posting for an HVAC service technician and I am very interested in applying for the position. Agent: That is great to hear, thank you for your interest. For job applications please visit our careers page on our website. I can also take your name and contact number to pass along to our hiring team if you would like. Caller: Yes please, my name is Jenny Wu and my number is 206-555-0222. Agent: Thank you Jenny, I have noted that.",
     {"is_lead":("eq",False), "summary":("present",)}),

    (18, "Dedup same call_id",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: My air conditioning is leaking water and causing damage to the floor. Agent: Name? Caller: Lisa Brown. Agent: Number? Caller: 312-555-0200. Agent: Address? Caller: 120 South Michigan Avenue, Chicago. Agent: The team will call you very soon.",
     {"is_lead":("eq",True), "dedup": True}),

    (19, "Borderline service area",
     "Agent: Arctic Breeze HVAC, this is Sophie. Caller: Hello, I am based in Hoboken, New Jersey. Do you service that area? Agent: We primarily cover New York City and the surrounding boroughs. Hoboken is very close and may well fall within our service radius. Our team will be able to confirm the exact coverage when they call you. Caller: That sounds good. My name is Paul Russo and my contact number is 201-555-0733. Agent: Thank you Paul, all noted.",
     {"caller_name":("contains","Russo"), "caller_phone":("present",), "is_lead":("eq",True)}),

    (20, "Complex address, urgent commercial",
     "Agent: Arctic Breeze HVAC, this is Sophie, how can I help? Caller: Hi yes, we own a restaurant and our walk-in refrigerator compressor has completely failed. We have health inspectors coming tomorrow and this is extremely urgent. We need a technician today if at all possible. Agent: I completely understand the urgency. Name? Caller: Chef Maria Santos. Agent: Callback number? Caller: 718-555-0441. Agent: And the address? Caller: Yes, the restaurant is at 44 West Broadway, Tribeca, Manhattan, New York, zip code 10007. Agent: I have marked this as an urgent commercial priority.",
     {"caller_name":("present",), "caller_address":("present",), "lead_score":("gte",7), "is_lead":("eq",True)}),
]

print("=" * 64)
print("STANDARD CALL PROCESSOR — FINAL 20-SCENARIO TEST")
print(f"Started: {time.strftime('%H:%M:%S UTC', time.gmtime())}")
print(f"Spacing: {INTER_CALL_DELAY}s between calls")
print("=" * 64)

for i, (sid, name, transcript, expect) in enumerate(TESTS):
    if i > 0:
        time.sleep(INTER_CALL_DELAY)

    print(f"\n[{sid:02d}] {name}")
    cid, payload = mkp(TS, sid, transcript)
    row, err = fire_wait(cid, payload)

    if err:
        chk(sid, "row logged", False, err)
        continue

    chk(sid, "row logged", True)
    for field, rule in expect.items():
        if field == "dedup": continue
        af(row, field, rule, sid)

    if expect.get("dedup"):
        # Re-fire same call_id — expect no duplicate
        http(WEBHOOK, "POST", payload)
        time.sleep(18)
        _, dup = http(f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}&select=call_id",
            headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}"})
        n = len(dup) if isinstance(dup, list) else 0
        chk(sid, "dedup: 1 row only after re-fire", n == 1, f"{n} row(s)")

    clean(cid)

total  = len(R)
passed = sum(1 for v in R.values() if v)
failed = total - passed

print(f"\n{'=' * 64}")
print(f"RESULT: {passed}/{total}  ({100*passed//total if total else 0}%)")
if failed == 0:
    print("✅  ALL 20 SCENARIOS PASSED — 100%")
else:
    print(f"\n❌  {failed} failure(s):")
    for k, v in R.items():
        if not v: print(f"   ❌ {k}")
print("=" * 64)
