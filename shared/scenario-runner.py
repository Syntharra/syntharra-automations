#!/usr/bin/env python3
"""
Syntharra HVAC AI Receptionist — Scenario Test Runner v3
25 scenarios covering edge cases, accents, after-hours, commercial,
vulnerable occupants, repeat callers, and communication difficulties.
Keyless — uses n8n's stored OpenAI credential.

Usage: python3 scenario-runner.py [agent_id]
"""
import urllib.request, urllib.error, json, time, sys, datetime

TRANSCRIPT_WEBHOOK = "https://syntharra.app.n8n.cloud/webhook/generate-scenario-transcript"
CALL_WEBHOOK       = "https://syntharra.app.n8n.cloud/webhook/retell-hvac-webhook"
SUPABASE_URL       = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_SVC_KEY         = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
AGENT_ID           = sys.argv[1] if len(sys.argv) > 1 else "agent_a942732251d9f719ce5aa92c92"
GREETING           = "Thank you for calling Arctic Breeze HVAC, this is Sarah, how can I help you today?"
WAIT_SECS          = 22

# id, name, persona, expect_lead, expect_tier, expect_vuln, expect_job
SCENARIOS = [
  # ── CORE LEADS ────────────────────────────────────────────────────────────
  ("S01","Standard AC Repair",
   "Cooperative homeowner. AC stopped cooling yesterday. Full name: Marcus Thompson. Phone: 718-555-0134. Address: 150 Court Street Brooklyn NY 11201. Give all details clearly.",
   True,"Standard",False,"Residential"),

  ("S02","Emergency — No Heat, Baby at Home",
   "Panicking. Heat went out overnight. 3-month-old baby at home. EMERGENCY. Name: Linda Park. Phone: 347-555-0287. Address: 78 Ocean Avenue Brooklyn NY 11225. Very distressed.",
   True,"Emergency",True,"Residential"),

  ("S03","Standard Maintenance Tune-up",
   "Calm homeowner wanting annual AC tune-up. No urgency at all, any time works. Name: Patricia Wong. Phone: 347-555-0477. Address: 220 Flatbush Avenue Brooklyn NY 11217.",
   True,"Standard",False,"Residential"),

  ("S04","Urgent — System Down, Needs Today",
   "AC completely broken, needs someone TODAY, working from home, extremely hot. Name: James Rodriguez. Phone: 646-555-0312. Address: 892 Manhattan Avenue Brooklyn NY 11222.",
   True,"Urgent",False,"Residential"),

  ("S05","Commercial — Restaurant Urgent",
   "Manager of a restaurant. AC is down, opening in 2 hours, needs emergency commercial service. Name: Marco Rossi. Phone: 646-555-0888. Address: 234 West Broadway Manhattan NY 10013.",
   True,"Urgent",False,"Commercial"),

  ("S06","Multi-Unit — Apartment Building",
   "Property manager of a 12-unit apartment building. Multiple units have no AC. Large commercial job. Name: David Rosenberg. Phone: 718-555-0321. Address: 400 Atlantic Avenue Brooklyn NY 11217.",
   True,"Urgent",False,"Multi-Unit"),

  ("S07","Price Shopper — Wants Quote",
   "Shopping around for AC tune-up prices. Asks cost first. Reluctant but eventually gives details. Name: Tony DiMaggio. Phone: 631-555-0099. Address: Park Slope Brooklyn.",
   True,"Standard",False,"Residential"),

  ("S08","Elderly Caller — Slow, Needs Patience",
   "78-year-old caller. Speaks slowly, loses train of thought occasionally. Wants AC service. Very polite. Name: Dorothy Walsh. Phone: 718-555-0611. Address: 55 Bay Ridge Avenue Brooklyn NY 11209.",
   True,"Standard",False,"Residential"),

  ("S09","After Hours — 3am AC Failure",
   "Calling at 3am. AC completely failed. Hot summer night. Has two young children. Needs help now. Name: Priya Patel. Phone: 917-555-0088. Address: 220 Flatbush Avenue Brooklyn NY 11217.",
   True,"Emergency",False,"Residential"),

  ("S10","Emergency — Elderly Alone, No Heat",
   "Calling for elderly mother who is alone at home with no heat. Winter. Mother is 82 and frail. Very worried. Name: Robert Chen (calling for mother). Phone: 718-555-0290. Address: 1840 East 14th Street Brooklyn NY 11229.",
   True,"Emergency",True,"Residential"),

  # ── NON-LEADS ─────────────────────────────────────────────────────────────
  ("S11","Spam — Robocall",
   "Robocall. Say 'Hello? Press 1 to lower your business insurance rates. You have been selected.' Repeat similar phrases. Do not respond to HVAC questions.",
   False,"Standard",False,"Residential"),

  ("S12","Complaint — Furious About Previous Job",
   "Furious about a repair done last month that made things worse. Wants a REFUND. NOT requesting new work. Demands a manager. Name: John Smith.",
   False,"Standard",False,"Residential"),

  ("S13","Existing Customer — Status Check",
   "Existing customer. Technician came last Tuesday to fix AC. Calling to check if the part has arrived. Not requesting new work. Name: Janet Kowalski.",
   False,"Standard",False,"Residential"),

  ("S14","Wrong Number",
   "Thinks they called their doctor's office. Realises mistake very quickly. Apologises and hangs up. Does not give name or any details.",
   False,"Standard",False,"Residential"),

  ("S15","Hangs Up Mid-Call",
   "Calls about a furnace issue. Gives name James Briggs. Starts giving phone number then says 'actually I'll call back' and hangs up before completing any details.",
   False,"Standard",False,"Residential"),

  # ── EDGE CASES & COMMUNICATION CHALLENGES ────────────────────────────────
  ("S16","Heavy Russian Accent",
   "Strong Russian accent, occasionally repeats yourself or uses wrong word. AC repair needed. Name: Dmitri Volkov. Phone: 718-555-0442. Address: 1840 East 14th Street Brooklyn NY 11229. Patient and tries hard to communicate.",
   True,"Standard",False,"Residential"),

  ("S17","Heavy Spanish Accent, Limited English",
   "Spanish is your first language. Limited English. Speak slowly, use simple words, occasionally switch to Spanish then correct yourself. AC not working. Name: Maria Gonzalez. Phone: 347-555-0661. Address: 456 Grand Avenue Brooklyn NY 11238.",
   True,"Standard",False,"Residential"),

  ("S18","Bad Phone Connection",
   "Very bad phone connection. Caller keeps cutting out mid-sentence. Has to repeat things 2-3 times. AC repair needed urgently. Name: Kevin Murphy. Phone: 718-555-0183. Address: 12 Shore Road Brooklyn NY 11209.",
   True,"Standard",False,"Residential"),

  ("S19","Vague Caller — Refuses Full Address",
   "Wants HVAC repair but very private about address. Gives name Sam Chen and phone 212-555-0177. When asked for address gives only neighbourhood: Upper West Side Manhattan. Still wants callback.",
   True,"Standard",False,"Residential"),

  ("S20","Angry Caller — Calms Down and Books",
   "Initially very angry — shouting, frustrated. But when handled calmly, gradually cooperates and wants to book a repair. Name: Tom Bradley. Phone: 718-555-0502. Address: 88 Prospect Park West Brooklyn NY 11215. Ends cooperatively.",
   True,"Standard",False,"Residential"),

  ("S21","Same Day Emergency — Medical Equipment",
   "Caller's AC broke and they have medical equipment at home that requires cool temperature (medication needs refrigeration). This is a medical emergency. Name: Helen Carter. Phone: 718-555-0381. Address: 320 Ocean Parkway Brooklyn NY 11218.",
   True,"Emergency",True,"Residential"),

  ("S22","Commercial — Office Building After Hours",
   "Office building manager. AC failed after hours, server room overheating, major IT risk. Needs someone immediately. Name: Steve Park. Phone: 212-555-0740. Address: 45 Broadway Manhattan NY 10006.",
   True,"Urgent",False,"Commercial"),

  ("S23","Caller With Dementia — Confused",
   "Elderly caller who seems confused. Repeats themselves. Not sure why they called. Eventually it becomes clear the AC is not working at their home. Needs gentle handling. No clear name given. Phone: 718-555-0299.",
   True,"Standard",True,"Residential"),

  ("S24","Installation Enquiry — New Home",
   "Just moved into a new home. Needs a completely new HVAC system installed. Large job. Name: Jennifer Walsh. Phone: 917-555-0177. Address: 67 Lincoln Place Brooklyn NY 11217. No urgency, wants a quote.",
   True,"Standard",False,"Residential"),

  ("S25","Telemarketer Pretending to Be Customer",
   "Starts as if calling about AC service but quickly pivots to trying to sell something. 'Actually I wanted to tell you about our extended warranty program for HVAC companies.' Clearly a sales call not a service request.",
   False,"Standard",False,"Residential"),
]

def http(url, method="GET", body=None, headers={}):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type":"application/json",**headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex: return 0, {"error": str(ex)}

def sb_delete(call_id):
    http(f"{SUPABASE_URL}/rest/v1/hvac_call_log?call_id=eq.{call_id}",
        "DELETE", None, {"apikey": SB_SVC_KEY, "Authorization": f"Bearer {SB_SVC_KEY}"})

def run_scenario(s):
    sid, name, persona, exp_lead, exp_tier, exp_vuln, exp_job = s
    ts = int(time.time())
    call_id = f"scenario_{sid}_{ts}"

    # Generate transcript via n8n OpenAI node
    status, resp = http(TRANSCRIPT_WEBHOOK, "POST", {
        "agent_greeting": GREETING, "caller_persona": persona})
    transcript = resp.get("transcript","").strip() if status == 200 else ""
    if not transcript:
        return {**_base(s), "status":"ERROR","reason":f"No transcript (HTTP {status})"}

    # Fire at call processor
    http(CALL_WEBHOOK, "POST", {"event":"call_analyzed","call":{
        "call_id":call_id,"agent_id":AGENT_ID,"call_status":"ended",
        "from_number":"+16316330713","to_number":"+18129944371",
        "start_timestamp":ts*1000-180000,"end_timestamp":ts*1000,
        "disconnection_reason":"user_hangup","call_analysis":{},"transcript":transcript
    }})

    time.sleep(WAIT_SECS)

    _, rows = http(f"{SUPABASE_URL}/rest/v1/hvac_call_log?call_id=eq.{call_id}&select=*",
        headers={"apikey":SB_SVC_KEY,"Authorization":f"Bearer {SB_SVC_KEY}"})
    log = rows[0] if isinstance(rows,list) and rows else {}

    failures = []
    if not log:
        failures.append("Not logged in Supabase")
    else:
        if log.get("is_lead") != exp_lead:
            failures.append(f"is_lead={log.get('is_lead')} (expected {exp_lead})")
        if log.get("call_tier") != exp_tier:
            failures.append(f"call_tier={log.get('call_tier')} (expected {exp_tier})")
        if exp_vuln and not log.get("vulnerable_occupant"):
            failures.append(f"vulnerable_occupant=False (expected True)")
        if log.get("job_type") != exp_job:
            failures.append(f"job_type={log.get('job_type')} (expected {exp_job})")

    sb_delete(call_id)

    return {
        "scenario": sid, "name": name,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "is_lead": log.get("is_lead","—"), "call_tier": log.get("call_tier","—"),
        "lead_score": log.get("lead_score","—"), "job_type": log.get("job_type","—"),
        "vulnerable": log.get("vulnerable_occupant","—"),
        "sentiment": log.get("caller_sentiment","—"),
        "caller_name": log.get("caller_name","—"),
        "summary": (log.get("summary","") or "")[:80],
    }

def _base(s):
    return {"scenario":s[0],"name":s[1],"failures":[]}

def run_all():
    print("=" * 70)
    print("  SYNTHARRA HVAC — SCENARIO TEST RUNNER v3")
    print(f"  Agent    : {AGENT_ID}")
    print(f"  Started  : {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Scenarios: {len(SCENARIOS)} (25 total)")
    print(f"  Mode     : Keyless — n8n stored OpenAI credential")
    print("=" * 70)

    results = []
    for s in SCENARIOS:
        sid, name = s[0], s[1]
        exp_lead, exp_tier, exp_vuln, exp_job = s[3], s[4], s[5], s[6]
        print(f"\n[{sid}] {name}")
        print(f"  Expect: lead={exp_lead} tier={exp_tier} vuln={exp_vuln} job={exp_job}")
        result = run_scenario(s)
        results.append(result)
        icon = "✅" if result["status"]=="PASS" else ("❌" if result["status"]=="FAIL" else "⚠️ ")
        print(f"  {icon} {result['status']} | lead={result['is_lead']} tier={result['call_tier']} score={result['lead_score']} job={result['job_type']} vuln={result['vulnerable']} mood={result['sentiment']}")
        if result.get("caller_name","—") != "—":
            print(f"     caller: {result['caller_name']}")
        if result.get("summary"):
            print(f"     {result['summary']}")
        for f in result["failures"]:
            print(f"     ↳ FAIL: {f}")

    passed = sum(1 for r in results if r["status"]=="PASS")
    failed = sum(1 for r in results if r["status"]=="FAIL")
    errors = sum(1 for r in results if r["status"]=="ERROR")

    print("\n" + "=" * 70)
    print(f"  RESULT: {passed}/{len(results)} passed | {failed} failed | {errors} errors")
    if failed == 0 and errors == 0:
        print("  ✅ ALL SCENARIOS PASSED")
    else:
        if failed:
            print("\n  ❌ FAILED:")
            for r in results:
                if r["status"]=="FAIL":
                    print(f"    [{r['scenario']}] {r['name']}")
                    for f in r["failures"]: print(f"       → {f}")
        if errors:
            print("\n  ⚠️  ERRORS:")
            for r in results:
                if r["status"]=="ERROR":
                    print(f"    [{r['scenario']}] {r['name']} — {r.get('reason','')}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_all()
