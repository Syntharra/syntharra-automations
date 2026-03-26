#!/usr/bin/env python3
"""
Syntharra HVAC AI Receptionist — Scenario Test Runner v2
Uses n8n's stored OpenAI credential for transcript generation.
No API keys needed.

Usage:
  python3 scenario-runner-v2.py [agent_id]
  python3 scenario-runner-v2.py agent_a942732251d9f719ce5aa92c92
"""
import urllib.request, urllib.error, json, time, sys, datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
TRANSCRIPT_WEBHOOK = "https://syntharra.app.n8n.cloud/webhook/generate-scenario-transcript"
CALL_WEBHOOK       = "https://syntharra.app.n8n.cloud/webhook/retell-hvac-webhook"
SUPABASE_URL       = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_SVC_KEY         = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
AGENT_ID           = sys.argv[1] if len(sys.argv) > 1 else "agent_a942732251d9f719ce5aa92c92"
AGENT_GREETING     = "Thank you for calling Arctic Breeze HVAC, this is Sarah, how can I help you today?"
PROCESS_WAIT_SECS  = 22   # wait for GPT + geocoding + Supabase log

# ── SCENARIOS ─────────────────────────────────────────────────────────────────
SCENARIOS = [
  # id, name, persona, expect_lead, min_score, expect_service
  ("S01","Standard AC Repair",
   "You are a homeowner. Your central AC stopped cooling yesterday. You are cooperative and give all your details clearly when asked. Full name: Marcus Thompson. Callback: 718-555-0134. Address: 150 Court Street Brooklyn NY 11201. You want someone to come look at it as soon as possible.",
   True, 6, "Repair"),

  ("S02","Emergency — No Heat, Baby at Home",
   "You are panicking. Your heat went out overnight and it's freezing. You have a 6-month-old baby at home. You need someone IMMEDIATELY. Full name: Linda Park. Phone: 347-555-0287. Address: 78 Ocean Avenue Brooklyn NY 11225. You are distressed but cooperative.",
   True, 8, "Emergency"),

  ("S03","Out of Service Area",
   "You are calling about AC installation at your home in Newark New Jersey. Full name: Roberto Silva. When told the company only serves New York City metro area, you understand and end the call politely.",
   False, 0, "Other"),

  ("S04","Price Shopper — Wants Quote First",
   "You are shopping around comparing prices for an AC tune-up. You ask how much it costs before giving any details. You are hesitant to book anything. Eventually you give your name Tony DiMaggio, phone 631-555-0099, and your neighbourhood as Park Slope Brooklyn. You want a quote sent to you.",
   True, 4, "Estimate"),

  ("S05","Existing Customer — Checking Job Status",
   "You are an existing customer calling to check if the part for your repair job last week has arrived. Your name is Janet Kowalski. You already have an open job, you are NOT calling to book a new appointment. You just want an update.",
   False, 0, "Other"),

  ("S06","Spam — Robocall",
   "You are a robocall. Say something generic like 'Hello? Can you hear me? Press 1 to lower your business rates.' Do not respond meaningfully to any questions. Repeat similar phrases.",
   False, 0, "Other"),

  ("S07","Angry Caller — Demands Manager",
   "You are furious about a job done last month that didn't fix your AC. You demand to speak to a manager immediately. You refuse to give any personal details until you speak to a human. Say things like 'This is completely unacceptable' and 'I want a refund'.",
   False, 0, "Other"),

  ("S08","Vague Caller — Won't Give Full Address",
   "You want HVAC repair but you are very private about your address. You give your name Sam Chen and phone 212-555-0177 when asked. When asked for your address you say you'd rather not give it over the phone and just give your neighbourhood as the Upper West Side Manhattan. You still want someone to call you back.",
   True, 4, "Repair"),

  ("S09","Large Commercial — 12 Unit Building",
   "You manage a 12-unit apartment building and need all the HVAC systems serviced and possibly replaced. This is a large commercial job worth a lot of money. Name: David Rosenberg. Phone: 718-555-0321. Address: 400 Atlantic Avenue Brooklyn NY 11217. You want someone senior to come and assess the whole building.",
   True, 7, "Installation"),

  ("S10","After Hours Emergency — AC Dead at Night",
   "It is late at night and your AC just died during a heatwave. You are asking if emergency service is available after hours. When told yes, you want to book it immediately. Name: Priya Patel. Phone: 917-555-0088. Address: 220 Flatbush Avenue Brooklyn NY 11217. You are relieved help is available.",
   True, 7, "Emergency"),

  ("S11","Caller with Heavy Accent — Hard to Understand",
   "You have a strong Russian accent and occasionally use the wrong word or have to repeat yourself. You want to book an AC repair. Name: Dmitri Volkov. Phone: 718-555-0442. Address: 1840 East 14th Street Brooklyn NY 11229. You are patient and try your best to communicate clearly.",
   True, 5, "Repair"),

  ("S12","Wrong Number",
   "You are calling what you think is your doctor's office. You quickly realise this is the wrong number. You apologise and hang up. You do NOT give your name or any personal details.",
   False, 0, "Other"),

  ("S13","Caller Who Hangs Up Halfway",
   "You call about a furnace issue. You give your name James Briggs and start to give your phone number but then say 'Actually, I'll call back later' and end the call abruptly before completing any details.",
   False, 0, "Other"),

  ("S14","Senior Citizen — Confused but Cooperative",
   "You are an elderly person, about 78 years old. You speak slowly and sometimes lose your train of thought. You want your air conditioner serviced. You eventually give your name as Dorothy Walsh, phone 718-555-0611, and address 55 Bay Ridge Avenue Brooklyn NY 11209 after some gentle prompting. You are very polite.",
   True, 5, "Maintenance"),

  ("S15","Caller Requesting Immediate Same-Day Service",
   "You are hosting a party tonight and your AC just broke. You are stressed and need someone TODAY without fail. Name: Michael Greene. Phone: 646-555-0388. Address: 892 Manhattan Avenue Brooklyn NY 11222. You are firm but not rude. You make clear same-day is a hard requirement.",
   True, 8, "Emergency"),
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def http(url, method="GET", body=None, headers={}):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type":"application/json",**headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}

def sb_delete(call_id):
    http(f"{SUPABASE_URL}/rest/v1/hvac_call_log?call_id=eq.{call_id}",
        "DELETE", None, {
            "apikey": SB_SVC_KEY,
            "Authorization": f"Bearer {SB_SVC_KEY}"
        })

def generate_transcript(scenario_id, persona):
    """Call n8n webhook — uses stored OpenAI credential, no key needed."""
    status, resp = http(TRANSCRIPT_WEBHOOK, "POST", {
        "agent_greeting": AGENT_GREETING,
        "caller_persona": persona
    })
    if status == 200:
        t = resp.get("transcript","").strip()
        if t: return t
    return None

def run_scenario(s):
    sid, name, persona, expect_lead, min_score, expect_service = s
    ts = int(time.time())
    call_id = f"scenario_{sid}_{ts}"

    # 1. Generate transcript via n8n (uses stored OpenAI key)
    transcript = generate_transcript(sid, persona)
    if not transcript:
        return {**_base(s,call_id), "status":"ERROR", "reason":"Transcript generation failed"}

    # 2. Fire at call processor
    fake_call = {
        "event": "call_analyzed",
        "call": {
            "call_id": call_id,
            "agent_id": AGENT_ID,
            "call_status": "ended",
            "from_number": "+15555550199",
            "to_number": "+18129944371",
            "start_timestamp": ts*1000 - 180000,
            "end_timestamp": ts*1000,
            "disconnection_reason": "user_hangup",
            "call_analysis": {},
            "transcript": transcript
        }
    }
    status, _ = http(CALL_WEBHOOK, "POST", fake_call)
    if status != 200:
        return {**_base(s,call_id), "status":"ERROR", "reason":f"Webhook HTTP {status}"}

    # 3. Wait for pipeline to complete
    time.sleep(PROCESS_WAIT_SECS)

    # 4. Check Supabase
    _, rows = http(
        f"{SUPABASE_URL}/rest/v1/hvac_call_log?call_id=eq.{call_id}&select=*",
        headers={"apikey": SB_SVC_KEY, "Authorization": f"Bearer {SB_SVC_KEY}"}
    )
    log = (rows[0] if isinstance(rows, list) and rows else {})

    # 5. Score
    failures = []
    if not log:
        failures.append("Not logged in Supabase")
    else:
        actual_lead  = log.get("is_lead", False)
        actual_score = log.get("lead_score", 0) or 0
        if actual_lead != expect_lead:
            failures.append(f"is_lead={actual_lead} (expected {expect_lead})")
        if expect_lead and actual_score < min_score:
            failures.append(f"lead_score={actual_score} (expected >={min_score})")

    # 6. Cleanup
    sb_delete(call_id)

    return {
        "scenario": sid,
        "name": name,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "is_lead": log.get("is_lead","—"),
        "lead_score": log.get("lead_score","—"),
        "service": log.get("service_requested","—"),
        "urgency": log.get("urgency","—"),
        "caller_name": log.get("caller_name","—"),
        "summary": (log.get("summary","") or "")[:90],
        "transcript_preview": transcript[:150] if transcript else ""
    }

def _base(s, call_id):
    sid, name, *_ = s
    return {"scenario":sid,"name":name,"call_id":call_id,"failures":[]}

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run_all():
    print("=" * 70)
    print("  SYNTHARRA — HVAC AI RECEPTIONIST SCENARIO TEST RUNNER v2")
    print(f"  Agent   : {AGENT_ID}")
    print(f"  Started : {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Scenarios: {len(SCENARIOS)}")
    print(f"  Mode    : Keyless — using n8n stored OpenAI credential")
    print("=" * 70)

    results = []
    for s in SCENARIOS:
        sid, name = s[0], s[1]
        print(f"\n[{sid}] {name}")
        result = run_scenario(s)
        results.append(result)
        icon = "✅" if result["status"] == "PASS" else ("❌" if result["status"] == "FAIL" else "⚠️ ")
        print(f"  {icon} {result['status']}"
              f"  |  lead={result['is_lead']}"
              f"  score={result['lead_score']}"
              f"  service={result['service']}"
              f"  urgency={result['urgency']}")
        if result["caller_name"] not in ("—",""):
            print(f"     caller: {result['caller_name']}")
        if result.get("summary"):
            print(f"     summary: {result['summary']}")
        for f in result["failures"]:
            print(f"     ↳ FAIL: {f}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print("\n" + "=" * 70)
    print(f"  RESULT: {passed}/{len(results)} passed  |  {failed} failed  |  {errors} errors")
    if failed == 0 and errors == 0:
        print("  ✅ ALL SCENARIOS PASSED")
    else:
        if failed:
            print(f"\n  ❌ FAILED:")
            for r in results:
                if r["status"] == "FAIL":
                    print(f"    [{r['scenario']}] {r['name']}")
                    for f in r["failures"]:
                        print(f"       → {f}")
        if errors:
            print(f"\n  ⚠️  ERRORS:")
            for r in results:
                if r["status"] == "ERROR":
                    print(f"    [{r['scenario']}] {r['name']} — {r.get('reason','')}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_all()
