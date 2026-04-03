"""
SYNTHARRA — Standard Call Processor Test Suite
================================================
Tests the HVAC Standard call processor (n8n workflow Kg576YtPM9yEacKn)
in isolation, across 20 realistic call scenarios.

Webhook: https://n8n.syntharra.com/webhook/retell-hvac-webhook
Table:   hvac_call_log

Run: python3 call-processor-test.py
"""

import urllib.request, urllib.error, json, time, sys

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
N8N_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZGU0MmJjZDAtNGU4ZC00ZDFmLWJlNDMtYzQzMDRjMjBjNjk1IiwiaWF0IjoxNzc0ODQ1ODc3fQ.SRjfEwRpZGBh5dnmNvp2PotTZ3e6OCejy2NFgM5uNqU"
SUPABASE = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_ANON  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0"
SB_SVC   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"

# Must be a real, active agent_id in hvac_standard_agent for lookup to work
AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"
WEBHOOK  = "https://n8n.syntharra.com/webhook/retell-hvac-webhook"
CP_WF_ID = "Kg576YtPM9yEacKn"

TS = int(time.time())
results = {}

def log(msg): print(msg)

def http(url, method="GET", body=None, headers={}):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e: return e.code, {}
    except Exception as ex: return 0, {}

def sb(path, method="GET", body=None, service=False):
    key = SB_SVC if service else SB_ANON
    _, data = http(f"{SUPABASE}/rest/v1/{path}", method, body,
        {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "return=representation"})
    return data if isinstance(data, list) else []

def sb_delete(path):
    key = SB_SVC
    req = urllib.request.Request(f"{SUPABASE}/rest/v1/{path}",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=15) as r: return r.status
    except: return 0

def make_call(scenario_id, transcript, from_num="+16315550100", duration=90):
    """Build a fake Retell post-call webhook payload."""
    call_id = f"test_cp_{TS}_{scenario_id:02d}"
    return call_id, {
        "event": "call_analyzed",
        "call": {
            "call_id":              call_id,
            "agent_id":             AGENT_ID,
            "call_status":          "ended",
            "from_number":          from_num,
            "to_number":            "+18129944371",
            "start_timestamp":      int(time.time()*1000) - (duration * 1000),
            "end_timestamp":        int(time.time()*1000),
            "disconnection_reason": "user_hangup",
            "call_analysis":        {},
            "transcript":           transcript
        }
    }

def fire_and_wait(call_id, payload, wait=20):
    """POST to webhook, wait for Groq processing, return Supabase row."""
    s, _ = http(WEBHOOK, "POST", payload)
    if s != 200:
        return None, f"webhook HTTP {s}"
    time.sleep(wait)
    rows = sb(f"hvac_call_log?call_id=eq.{call_id}&select=*")
    return (rows[0] if rows else None), None

def check(scenario_id, name, passed, detail=""):
    key = f"#{scenario_id:02d} {name}"
    results[key] = passed
    icon = "✅" if passed else "❌"
    print(f"    {icon} {name}" + (f"  → {detail}" if detail else ""))
    return passed

# ─────────────────────────────────────────────────────────────
# SCENARIO DEFINITIONS
# 20 scenarios covering all call types + edge cases
# ─────────────────────────────────────────────────────────────

SCENARIOS = [

    # ── CORE LEADS ───────────────────────────────────────────
    {
        "id": 1, "name": "Standard service repair lead",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie, how can I help? "
            "Caller: Hi, my AC stopped working this morning. It's making a weird clicking noise. "
            "Agent: I'm sorry to hear that. Can I get your full name please? "
            "Caller: Mike Johnson. "
            "Agent: And the best callback number? "
            "Caller: 631-555-0199. "
            "Agent: Service address? "
            "Caller: 22 Oak Street, Brooklyn, New York. "
            "Agent: I've got all that noted. Our team will be in touch shortly."
        ),
        "expect": {
            "caller_name":       ("contains", "Johnson"),
            "caller_phone":      ("present",),
            "caller_address":    ("contains", "Brooklyn"),
            "service_requested": ("present",),
            "job_type":          ("contains", "Repair"),
            "lead_score":        ("gte", 6),
            "is_lead":           ("eq", True),
            "summary":           ("present",),
        }
    },
    {
        "id": 2, "name": "New install / quote request",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie, how can I help? "
            "Caller: I'm looking to replace my old furnace with a new heat pump system. "
            "Agent: Great, we can definitely help with that. What's your name? "
            "Caller: Sarah Chen. "
            "Agent: Callback number? "
            "Caller: 718-555-0312. "
            "Agent: And the installation address? "
            "Caller: 48 Maple Avenue, Queens, New York. "
            "Agent: I've passed that to the team and they'll call to arrange a quote."
        ),
        "expect": {
            "caller_name":       ("contains", "Chen"),
            "job_type":          ("contains", "Install"),
            "lead_score":        ("gte", 6),
            "is_lead":           ("eq", True),
        }
    },
    {
        "id": 3, "name": "Emergency — no heat in winter",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: We have no heat at all and it's freezing inside, there's an elderly person in the house. "
            "Agent: Understood, this is urgent. Is there any smell of gas or burning? "
            "Caller: No, nothing like that. "
            "Agent: I have that noted as a priority. Name please? "
            "Caller: Robert Hall. "
            "Agent: Best number? "
            "Caller: 212-555-0788. "
            "Agent: Address? "
            "Caller: 10 Fifth Avenue Manhattan. "
            "Agent: Marked urgent. Our team will contact you as soon as possible."
        ),
        "expect": {
            "urgency":           ("contains", "mergency"),
            "vulnerable_occupant": ("truthy",),
            "lead_score":        ("gte", 7),
            "is_lead":           ("eq", True),
        }
    },
    {
        "id": 4, "name": "Existing customer — follow-up",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi, I had a technician out last week to fix my AC and it's not working again. "
            "Agent: I'm sorry about that. Can I get your name? "
            "Caller: David Park. "
            "Agent: And your number? "
            "Caller: 646-555-0441. "
            "Agent: Service address? "
            "Caller: 77 West 23rd, Manhattan. "
            "Agent: I've flagged this as a follow-up and the team will call you back shortly."
        ),
        "expect": {
            "caller_name":       ("contains", "Park"),
            "is_lead":           ("eq", True),
            "summary":           ("present",),
        }
    },
    {
        "id": 5, "name": "Maintenance / tune-up request",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: I'd like to book an annual maintenance check for my HVAC system. "
            "Agent: Of course. Name? "
            "Caller: Amanda Torres. "
            "Agent: Phone number? "
            "Caller: 917-555-0022. "
            "Agent: Address? "
            "Caller: 15 Central Park West New York. "
            "Agent: All set, the team will reach out to schedule."
        ),
        "expect": {
            "service_requested": ("present",),
            "job_type":          ("contains", "Maintenance"),
            "is_lead":           ("eq", True),
        }
    },

    # ── EDGE CASES ────────────────────────────────────────────
    {
        "id": 6, "name": "Caller hangs up before address",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi I need someone to look at my AC. "
            "Agent: Sure, can I get your name? "
            "Caller: Tom. "
            "Agent: And your callback number? "
            "Caller: 516-555-0100. "
            "Agent: And the service address? "
            "Caller: Actually I'll call back later. "
        ),
        "expect": {
            "caller_name":       ("present",),
            "caller_phone":      ("present",),
            "summary":           ("present",),
        }
    },
    {
        "id": 7, "name": "Wrong number / non-HVAC call",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: Oh sorry, I was trying to reach the pizza place. "
            "Agent: No problem, it seems you may have dialled the wrong number. This is Arctic Breeze HVAC. "
            "Caller: Oops, my bad. Thanks, bye."
        ),
        "expect": {
            "is_lead":           ("eq", False),
            "summary":           ("present",),
        }
    },
    {
        "id": 8, "name": "Spam / robocall",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: This is an automated message about your car's extended warranty. "
            "Agent: Thank you, this appears to be an automated call. We only assist with HVAC service requests. Goodbye."
        ),
        "expect": {
            "is_lead":           ("eq", False),
        }
    },
    {
        "id": 9, "name": "Out-of-service-area caller",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi, I need AC repair. I'm in Los Angeles. "
            "Agent: I appreciate you calling. Our service area covers New York City and surrounding boroughs only. "
            "We wouldn't be able to service Los Angeles, unfortunately. "
            "Caller: Oh okay, no worries."
        ),
        "expect": {
            "is_lead":           ("eq", False),
            "summary":           ("present",),
        }
    },
    {
        "id": 10, "name": "Live transfer triggered",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC, this is Sophie. "
            "Caller: This is an emergency, the gas smell is very strong and I need someone now. "
            "Agent: This is a safety emergency. I'm connecting you to our emergency line right now. "
            "[Agent initiated live transfer to emergency number] "
            "Caller: Thank you, please hurry."
        ),
        "expect": {
            "urgency":           ("present",),
            "transfer_attempted": ("truthy",),
            "summary":           ("present",),
        }
    },

    # ── LEAD QUALITY SCORING ──────────────────────────────────
    {
        "id": 11, "name": "High-value commercial caller",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi, we run a 20-unit apartment complex and need a quote for full HVAC replacement across all units. "
            "Agent: That sounds like a significant project. Company name? "
            "Caller: Sunrise Property Management. "
            "Agent: And the contact person? "
            "Caller: James Whitfield. "
            "Agent: Best number? "
            "Caller: 212-555-0900. "
            "Agent: Property address? "
            "Caller: 300 East 45th Street, Manhattan. "
            "Agent: I've noted this as a large commercial project and the team will call you promptly."
        ),
        "expect": {
            "lead_score":        ("gte", 8),
            "is_lead":           ("eq", True),
            "caller_name":       ("present",),
        }
    },
    {
        "id": 12, "name": "Pricing enquiry — no booking intent",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: How much do you charge for a diagnostic? "
            "Agent: Our team will be able to give you exact pricing when they call you back. "
            "Caller: Can't you just give me a rough idea? "
            "Agent: I completely understand. I'm not able to quote exact fees but the team can discuss all pricing when they reach you. "
            "Caller: Okay I'll think about it. Bye."
        ),
        "expect": {
            "is_lead":           ("eq", False),
            "summary":           ("present",),
        }
    },
    {
        "id": 13, "name": "Caller provides phonetic phone number",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi, my heat pump is making a loud noise. "
            "Agent: I can help with that. Name? "
            "Caller: Kevin Lee. "
            "Agent: Best number? "
            "Caller: Six one seven, five five five, zero one zero two. "
            "Agent: Let me confirm — 617-555-0102? "
            "Caller: That's correct. "
            "Agent: And address? "
            "Caller: 55 Boylston Street, Boston. "
            "Agent: All noted, team will be in touch."
        ),
        "expect": {
            "caller_phone":      ("present",),
            "caller_name":       ("contains", "Lee"),
            "is_lead":           ("eq", True),
        }
    },
    {
        "id": 14, "name": "Duplicate call — same call_id resent",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: My AC is leaking water everywhere. "
            "Agent: I can help. Name? "
            "Caller: Lisa Brown. "
            "Agent: Number? "
            "Caller: 312-555-0200. "
            "Agent: Address? "
            "Caller: 120 South Michigan, Chicago. "
            "Agent: Got it, team will call you soon."
        ),
        "expect": {
            "is_lead":   ("eq", True),
            "dedup":     True,   # special flag: re-send same call_id, expect no new row
        }
    },
    {
        "id": 15, "name": "Very short call — no data collected",
        "transcript": (
            "Agent: Thank you for calling Arctic Breeze HVAC. "
            "Caller: [silence] "
            "Agent: Hello? Is anyone there? "
        ),
        "expect": {
            "is_lead":   ("eq", False),
            "summary":   ("present",),
        }
    },

    # ── FIELD ACCURACY ────────────────────────────────────────
    {
        "id": 16, "name": "caller_sentiment — frustrated caller",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: I'm absolutely furious. Your company came out twice and the AC still isn't fixed. "
            "Agent: I sincerely apologise. Let me make sure the right team member calls you back. Name? "
            "Caller: Gary Mitchell. "
            "Agent: Number? "
            "Caller: 404-555-0350. "
            "Agent: Address? "
            "Caller: 88 Peachtree, Atlanta. "
            "Agent: I've flagged this as an urgent priority callback."
        ),
        "expect": {
            "caller_sentiment":  ("present",),
            "caller_name":       ("contains", "Mitchell"),
            "is_lead":           ("eq", True),
        }
    },
    {
        "id": 17, "name": "geocode_status populated",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: I need someone to check my heat exchanger. It keeps tripping the breaker. "
            "Agent: Sure. Name? "
            "Caller: Paul Harris. "
            "Agent: Number? "
            "Caller: 502-555-0180. "
            "Agent: Address? "
            "Caller: 1400 South Third Street, Louisville, Kentucky. "
            "Agent: Perfect, all noted and team will call you."
        ),
        "expect": {
            "geocode_status":    ("present",),
            "caller_address":    ("present",),
            "is_lead":           ("eq", True),
        }
    },
    {
        "id": 18, "name": "Caller gives no address — only phone",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi my HVAC unit needs service. "
            "Agent: Of course. Name? "
            "Caller: Nina Patel. "
            "Agent: Number? "
            "Caller: 303-555-0410. "
            "Agent: And the service address? "
            "Caller: I'd rather just give the address when someone calls. "
            "Agent: No problem at all. I'll pass your name and number to the team."
        ),
        "expect": {
            "caller_name":   ("contains", "Patel"),
            "caller_phone":  ("present",),
            "is_lead":       ("eq", True),
        }
    },
    {
        "id": 19, "name": "Vendor / supplier call",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi I'm calling from Carrier distribution about your parts account. "
            "Agent: Thanks for calling. I'll take your name and number and have the right person call you back. "
            "Caller: Sure, it's Mark Davies, 800-555-0900. "
            "Agent: Got it, someone from the team will reach out."
        ),
        "expect": {
            "is_lead":   ("eq", False),
            "summary":   ("present",),
        }
    },
    {
        "id": 20, "name": "Job applicant",
        "transcript": (
            "Agent: Arctic Breeze HVAC, this is Sophie. "
            "Caller: Hi I saw your job posting for an HVAC technician. I'd like to apply. "
            "Agent: Thanks for your interest. For job applications, please visit our website. "
            "I can take your name and number to pass along to the team. "
            "Caller: Sure, Jenny Wu, 206-555-0222. "
            "Agent: Great, I'll pass that along."
        ),
        "expect": {
            "is_lead":   ("eq", False),
            "summary":   ("present",),
        }
    },
]

# ─────────────────────────────────────────────────────────────
# ASSERTIONS ENGINE
# ─────────────────────────────────────────────────────────────

def assert_field(row, field, rule, scenario_id, label=None):
    val = row.get(field)
    tag = label or field
    if rule[0] == "present":
        return check(scenario_id, f"{tag} present", bool(val), str(val)[:40] if val else "MISSING")
    elif rule[0] == "contains":
        return check(scenario_id, f"{tag} contains '{rule[1]}'", rule[1].lower() in str(val or "").lower(), str(val)[:40])
    elif rule[0] == "eq":
        return check(scenario_id, f"{tag} == {rule[1]}", val == rule[1], f"{val}")
    elif rule[0] == "gte":
        return check(scenario_id, f"{tag} >= {rule[1]}", (val or 0) >= rule[1], f"score={val}")
    elif rule[0] == "truthy":
        return check(scenario_id, f"{tag} truthy", bool(val), str(val)[:40])
    return False

# ─────────────────────────────────────────────────────────────
# MAIN RUN
# ─────────────────────────────────────────────────────────────

print("=" * 60)
print("SYNTHARRA — Standard Call Processor Test Suite")
print(f"Webhook : {WEBHOOK}")
print(f"Agent   : {AGENT_ID}")
print(f"Run TS  : {TS}")
print(f"Started : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print("=" * 60)

call_ids_to_cleanup = []

for sc in SCENARIOS:
    sid  = sc["id"]
    name = sc["name"]
    exp  = sc["expect"]

    print(f"\n[{sid:02d}] {name}")

    call_id, payload = make_call(sid, sc["transcript"])
    call_ids_to_cleanup.append(call_id)

    row, err = fire_and_wait(call_id, payload, wait=22)

    if err:
        check(sid, "webhook accepted", False, err)
        continue

    if not row:
        check(sid, "row logged in hvac_call_log", False, "no row found after 22s")
        # still check fields to surface all failures
        continue

    check(sid, "row logged in hvac_call_log", True, call_id[-12:])

    # Assert every expected field
    for field, rule in exp.items():
        if field == "dedup":
            continue  # handled separately below
        assert_field(row, field, rule, sid)

    # Special: dedup test
    if exp.get("dedup"):
        http(WEBHOOK, "POST", payload)  # resend exact same call_id
        time.sleep(12)
        dup_rows = sb(f"hvac_call_log?call_id=eq.{call_id}&select=*")
        check(sid, "dedup — only 1 row after duplicate send", len(dup_rows) == 1, f"{len(dup_rows)} row(s)")

# ─────────────────────────────────────────────────────────────
# CLEANUP — delete all test rows
# ─────────────────────────────────────────────────────────────
print("\n[CLEANUP] Deleting test rows from hvac_call_log...")
deleted = 0
for cid in call_ids_to_cleanup:
    status = sb_delete(f"hvac_call_log?call_id=eq.{cid}")
    if status in (200, 204): deleted += 1
print(f"  Deleted {deleted}/{len(call_ids_to_cleanup)} rows.")

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for v in results.values() if v)
failed = total - passed

print("\n" + "=" * 60)
print(f"RESULT: {passed}/{total} assertions passed  |  {failed} failed")
if failed == 0:
    print("✅ ALL CALL PROCESSOR SCENARIOS PASSED")
else:
    print("\n❌ FAILURES:")
    for name, val in results.items():
        if not val: print(f"   ❌ {name}")
print("=" * 60)
