"""
Standard Call Processor — Full 20-Scenario Test Suite
Uses SB_SVC to bypass RLS, staggers call IDs, polls up to 45s per scenario.
"""
import urllib.request, json, time, sys

N8N_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZGU0MmJjZDAtNGU4ZC00ZDFmLWJlNDMtYzQzMDRjMjBjNjk1IiwiaWF0IjoxNzc0ODQ1ODc3fQ.SRjfEwRpZGBh5dnmNvp2PotTZ3e6OCejy2NFgM5uNqU"
SUPABASE = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_SVC   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"
WEBHOOK  = "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
TS       = int(time.time())
results  = {}

def http(url, method="GET", body=None, headers={}):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e: return e.code, {}
    except Exception: return 0, {}

def sb(path):
    _, d = http(f"{SUPABASE}/rest/v1/{path}",
        headers={"apikey": SB_SVC, "Authorization": f"Bearer {SB_SVC}"})
    return d if isinstance(d, list) else []

def sb_del(cid):
    urllib.request.urlopen(urllib.request.Request(
        f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{cid}",
        headers={"apikey": SB_SVC, "Authorization": f"Bearer {SB_SVC}",
                 "Content-Type": "application/json"}, method="DELETE"), timeout=10)

def fire(sid, transcript, wait=40):
    cid = f"cptest_{TS}_{sid:02d}"
    payload = {"event": "call_analyzed", "call": {
        "call_id": cid, "agent_id": AGENT_ID, "call_status": "ended",
        "from_number": "+16315550100", "to_number": "+18129944371",
        "start_timestamp": int(time.time()*1000)-90000,
        "end_timestamp": int(time.time()*1000),
        "disconnection_reason": "user_hangup", "call_analysis": {},
        "transcript": transcript
    }}
    s, _ = http(WEBHOOK, "POST", payload)
    if s != 200: return None, f"webhook {s}"
    # Poll up to wait seconds
    for _ in range(wait // 5):
        time.sleep(5)
        rows = sb(f"hvac_call_log?call_id=eq.{cid}&select=*")
        if rows: return rows[0], cid
    return None, cid

def chk(sid, name, passed, detail=""):
    key = f"#{sid:02d} {name}"
    results[key] = passed
    print(f"    {'✅' if passed else '❌'} {name}" + (f"  → {detail}" if detail else ""))
    return passed

def af(sid, row, field, rule):
    v = row.get(field)
    if rule[0] == "present":   return chk(sid, f"{field} present", bool(v), str(v)[:50] if v else "MISSING")
    if rule[0] == "contains":  return chk(sid, f"{field} contains '{rule[1]}'", rule[1].lower() in str(v or "").lower(), str(v)[:50])
    if rule[0] == "eq":        return chk(sid, f"{field}=={rule[1]}", v==rule[1], str(v))
    if rule[0] == "gte":       return chk(sid, f"{field}>={rule[1]}", (v or 0)>=rule[1], f"{v}")
    if rule[0] == "truthy":    return chk(sid, f"{field} truthy", bool(v), str(v)[:50])
    if rule[0] == "is_int":    return chk(sid, f"{field} is int", isinstance(v, int), str(v))
    return False

SCENARIOS = [
  # id, name, transcript, assertions
  (1, "Standard repair lead",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: My AC stopped working this morning, it makes a clicking noise. Agent: I'm sorry. Name? Caller: Mike Johnson. Agent: Number? Caller: 631-555-0199. Agent: Address? Caller: 22 Oak Street, Brooklyn, New York. Agent: Team will be in touch shortly.",
   {"caller_name":("contains","Johnson"), "caller_phone":("present",), "caller_address":("present",),
    "service_requested":("present",), "job_type":("contains","Repair"),
    "lead_score":("gte",6), "is_lead":("eq",True), "summary":("present",)}),

  (2, "New install quote",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: I want to replace my old furnace with a new heat pump system. Agent: Name? Caller: Sarah Chen. Agent: Number? Caller: 718-555-0312. Agent: Address? Caller: 48 Maple Avenue Queens New York. Agent: Team will call you for a quote.",
   {"caller_name":("contains","Chen"), "job_type":("contains","Install"),
    "lead_score":("gte",6), "is_lead":("eq",True)}),

  (3, "Emergency — elderly, no heat",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: We have no heat at all and there is an elderly person in the house, it is absolutely freezing. Agent: This is urgent. Any gas smell or burning? Caller: No nothing like that. Agent: Name? Caller: Robert Hall. Agent: Number? Caller: 212-555-0788. Agent: Address? Caller: 10 Fifth Avenue Manhattan. Agent: Marked urgent, team will contact you ASAP.",
   {"urgency":("contains","mergency"), "vulnerable_occupant":("truthy",),
    "lead_score":("gte",7), "is_lead":("eq",True)}),

  (4, "Maintenance tune-up",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: I want to book an annual maintenance check for my HVAC system before summer. Agent: Of course. Name? Caller: Amanda Torres. Agent: Number? Caller: 917-555-0022. Agent: Address? Caller: 15 Central Park West New York. Agent: All set, team will reach out.",
   {"service_requested":("present",), "job_type":("contains","Maintenance"), "is_lead":("eq",True)}),

  (5, "Existing customer follow-up",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: Hi, a technician came out last week to fix my AC unit and it has stopped working again. Agent: I am very sorry to hear that. Name? Caller: David Park. Agent: Number? Caller: 646-555-0441. Agent: Address? Caller: 77 West 23rd Street Manhattan. Agent: Flagged as priority follow-up.",
   {"caller_name":("contains","Park"), "is_lead":("eq",True), "summary":("present",)}),

  (6, "Wrong number",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: Oh sorry I was trying to reach the pizza delivery place. Agent: No problem, this is Arctic Breeze HVAC. Caller: Oops sorry about that, bye.",
   {"is_lead":("eq",False), "summary":("present",)}),

  (7, "Spam robocall",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: This is an automated message regarding your vehicle extended warranty. Please press one. Agent: This appears to be an automated robocall. We only assist with HVAC services. Goodbye.",
   {"is_lead":("eq",False)}),

  (8, "Out of service area",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: Hi I need air conditioning repair. I am located in Los Angeles California. Agent: Our service area covers New York City and surrounding boroughs only. We would not be able to service Los Angeles. Caller: Oh okay thanks anyway.",
   {"is_lead":("eq",False), "summary":("present",)}),

  (9, "Live transfer — gas emergency",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: There is a very strong gas smell in my house right now, this is an emergency. Agent: This is a safety emergency. I am connecting you to our emergency line immediately. Agent initiated live transfer to emergency contact number. Caller: Thank you please hurry.",
   {"urgency":("present",), "transfer_attempted":("truthy",), "summary":("present",)}),

  (10, "Caller hangs up before address",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: I need someone for my air conditioner. Agent: Of course. Name? Caller: Tom. Agent: Number? Caller: 516-555-0100. Agent: And the service address? Caller: Actually I will call back another time. Bye.",
   {"caller_name":("present",), "caller_phone":("present",), "summary":("present",)}),

  (11, "High-value commercial",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: We manage a twenty unit apartment building and need a quote for full HVAC replacement across all units. Agent: That sounds like a significant project. Company name? Caller: Sunrise Property Management. Agent: Contact? Caller: James Whitfield. Agent: Number? Caller: 212-555-0900. Agent: Address? Caller: 300 East 45th Street Manhattan. Agent: Noted as a large commercial project.",
   {"lead_score":("gte",8), "is_lead":("eq",True), "caller_name":("present",)}),

  (12, "Pricing enquiry only",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: How much do you charge for a diagnostic visit? Agent: Our team will be happy to go over exact pricing when they call you back. Caller: Can you give me a ballpark? Agent: I am not able to quote specific fees but the team can discuss all options. Caller: Okay I will think about it. Bye.",
   {"summary":("present",), "lead_score":("gte",0)}),

  (13, "Phonetic phone number",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: My heat pump is making a loud grinding noise. Agent: Name? Caller: Kevin Lee. Agent: Number? Caller: Six one seven, five five five, zero one zero two. Agent: So that is 617-555-0102? Caller: Correct. Agent: Address? Caller: 55 Boylston Street Boston. Agent: Team will call you.",
   {"caller_phone":("present",), "caller_name":("contains","Lee"), "is_lead":("eq",True)}),

  (14, "Frustrated repeat customer",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: I am absolutely furious. Your company has been out here twice and my AC is still not working. Agent: I sincerely apologise. Name? Caller: Gary Mitchell. Agent: Number? Caller: 404-555-0350. Agent: Address? Caller: 88 Peachtree Street Atlanta Georgia. Agent: Flagging as urgent priority callback.",
   {"caller_name":("contains","Mitchell"), "is_lead":("eq",True), "caller_sentiment":("is_int",)}),

  (15, "Vendor call",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: Hi I am calling from Carrier parts distribution about your wholesale account with us. Agent: Thanks for calling. I will take your name and number and have the right person get back to you. Caller: Sure it is Mark Davies, 800-555-0900.",
   {"is_lead":("eq",False), "summary":("present",)}),

  (16, "Job applicant",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: I saw your job posting for an HVAC technician and I would like to apply. Agent: Thank you for your interest. For job applications please visit our website. I can take your contact details to pass along. Caller: Sure, Jenny Wu, 206-555-0222.",
   {"is_lead":("eq",False), "summary":("present",)}),

  (17, "Dedup — verify no duplicate row",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: My AC is leaking water. Agent: Name? Caller: Lisa Brown. Agent: Number? Caller: 312-555-0200. Agent: Address? Caller: 120 South Michigan Chicago Illinois. Agent: Team will call you.",
   {"is_lead":("eq",True), "_dedup": True}),

  (18, "Very short call — no info",
   "Agent: Thank you for calling Arctic Breeze HVAC. Caller: Hello? Agent: Hello, how can I help? Caller: [silence]",
   {"summary":("present",)}),

  (19, "Emergency with vulnerable + transfer",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: My elderly mother lives alone and she has no heat. She has a medical condition and the house is freezing cold. Agent: This is urgent. Is there any gas smell? Caller: No. Agent: I am connecting you to our emergency line now. Agent initiated transfer to emergency number. Caller: Thank you.",
   {"vulnerable_occupant":("truthy",), "transfer_attempted":("truthy",),
    "urgency":("contains","mergency"), "is_lead":("eq",True)}),

  (20, "Caller gives only phone, no address",
   "Agent: Arctic Breeze HVAC, Sophie. Caller: Hi my HVAC needs servicing. Agent: Name? Caller: Nina Patel. Agent: Number? Caller: 303-555-0410. Agent: And the service address? Caller: I would prefer to give the address when someone calls me. Agent: No problem, I will pass your name and number to the team.",
   {"caller_name":("contains","Patel"), "caller_phone":("present",), "is_lead":("eq",True)}),
]

print("=" * 65)
print("SYNTHARRA — Standard Call Processor Test Suite v1")
print(f"Run TS  : {TS}")
print(f"Webhook : {WEBHOOK}")
print(f"Scenarios: {len(SCENARIOS)}")
print("=" * 65)

cleanup_ids = []

for sid, name, transcript, expect in SCENARIOS:
    print(f"\n[{sid:02d}] {name}")
    row, cid_or_err = fire(sid, transcript, wait=40)
    cid = f"cptest_{TS}_{sid:02d}"
    cleanup_ids.append(cid)

    if row is None:
        chk(sid, "row logged in hvac_call_log", False, "no row after 40s")
        continue

    chk(sid, "row logged", True)
    for field, rule in expect.items():
        if field.startswith("_"): continue
        af(sid, row, field, rule)

    # Dedup check
    if expect.get("_dedup"):
        # re-fire same call_id
        http(WEBHOOK, "POST", {"event": "call_analyzed", "call": {
            "call_id": cid, "agent_id": AGENT_ID, "call_status": "ended",
            "from_number": "+16315550100", "to_number": "+18129944371",
            "start_timestamp": int(time.time()*1000)-90000,
            "end_timestamp": int(time.time()*1000),
            "disconnection_reason": "user_hangup", "call_analysis": {}, "transcript": transcript
        }})
        time.sleep(15)
        dups = sb(f"hvac_call_log?call_id=eq.{cid}&select=id")
        chk(sid, "dedup: only 1 row after re-send", len(dups) == 1, f"{len(dups)} row(s)")

    # Print debug line
    print(f"    [addr={row.get('caller_address','')} | job={row.get('job_type')} | sent={row.get('caller_sentiment')} | vuln={row.get('vulnerable_occupant')}]")

# Cleanup
print(f"\n[CLEANUP] Removing {len(cleanup_ids)} test rows...")
deleted = 0
for cid in cleanup_ids:
    try:
        sb_del(cid); deleted += 1
    except: pass
print(f"  Deleted {deleted}/{len(cleanup_ids)}")

# Summary
total  = len(results)
passed = sum(1 for v in results.values() if v)
failed = total - passed
pct    = 100 * passed // total if total else 0
print(f"\n{'=' * 65}")
print(f"RESULT: {passed}/{total} assertions passed  ({pct}%)  |  {failed} failed")
if failed == 0:
    print("✅  ALL SCENARIOS PASSED — 100%")
else:
    print("\n❌  FAILURES:")
    for k, v in results.items():
        if not v: print(f"   ❌ {k}")
print("=" * 65)
