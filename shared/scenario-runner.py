#!/usr/bin/env python3
"""
Syntharra HVAC AI Receptionist — Scenario Test Runner
Generates realistic caller transcripts via GPT and fires them at the
call processor webhook, scoring the lead capture output.
"""
import urllib.request, urllib.error, json, time, urllib.parse, sys

# ── CONFIG ────────────────────────────────────────────────────────────────────
OPENAI_KEY  = "PLACEHOLDER"  # Will be filled from n8n credential
N8N_KEY     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1OWJjM2MzMi1mYzNkLTRlNjYtYTJhOC01NDM5ZjA1NjA2YjciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiN2JjZTU4ZDAtYzgwYy00YTRjLWE2MzAtNTU0OTJjM2Q4MWZhIiwiaWF0IjoxNzc0NDAwNzY1fQ.NGQA3HMCAgYVbwYreM5GbQKjNTn9FsdgzsjHltvnxdI"
RETELL_KEY  = "key_0157d9401f66cfa1b51fadc66445"
SUPABASE    = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_ANON     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0"
SB_SVC      = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
WEBHOOK_URL = "https://syntharra.app.n8n.cloud/webhook/retell-hvac-webhook"
# Agent to test against — pass as arg or use default
AGENT_ID    = sys.argv[1] if len(sys.argv) > 1 else "agent_3887f4de3b8f8189fe849728d6"
AGENT_GREETING = "Thank you for calling Polar Peak HVAC, this is Max, how can I help you today?"

# ── SCENARIOS ────────────────────────────────────────────────────────────────
SCENARIOS = [
    {
        "id": "S01",
        "name": "Standard AC Repair Lead",
        "description": "Cooperative caller needing AC repair, gives all details smoothly",
        "expected_lead": True,
        "expected_score_min": 7,
        "expected_service": "Repair",
        "caller_persona": "You are a homeowner calling an HVAC company. Your AC stopped working yesterday. You are cooperative and give your full name (Marcus Thompson), callback number (718-555-0134), and address (42 Maple Drive, Brooklyn, NY 11215) clearly when asked. You confirm all details when read back.",
    },
    {
        "id": "S02",
        "name": "Emergency — No Heat",
        "description": "Urgent caller with no heat in winter",
        "expected_lead": True,
        "expected_score_min": 8,
        "expected_service": "Emergency",
        "caller_persona": "You are panicking because your heat has gone out overnight and it's freezing in your home. You have a baby. You need emergency service ASAP. Your name is Linda Park, phone is 347-555-0287, address is 156 Ocean Avenue, Brooklyn, NY 11225. You're distressed but cooperative.",
    },
    {
        "id": "S03",
        "name": "Out of Service Area",
        "description": "Caller is outside the service area (New Jersey)",
        "expected_lead": False,
        "expected_score_min": 0,
        "expected_service": "Other",
        "caller_persona": "You are calling about AC installation at your home in Newark, New Jersey. Give your name as Roberto Silva when asked. When told the company only serves NYC within 40 miles, you understand and end the call politely.",
    },
    {
        "id": "S04",
        "name": "Price Shopper",
        "description": "Caller only wants a price quote, reluctant to give address",
        "expected_lead": True,
        "expected_score_min": 5,
        "expected_service": "Estimate",
        "caller_persona": "You are shopping around for AC tune-up prices. You ask how much it costs before anything else. You're a bit reluctant to give your address but eventually provide it: 89 Park Slope Ave, Brooklyn. Your name is Tony DiMaggio, phone 631-555-0099. You want a quote before committing.",
    },
    {
        "id": "S05",
        "name": "Existing Customer — Job Status",
        "description": "Returning customer asking about a previous job",
        "expected_lead": False,
        "expected_score_min": 0,
        "expected_service": "Other",
        "caller_persona": "You are an existing customer calling to check on the status of a repair job that was done last week. You say your name is Janet Kowalski and that a tech came out on Monday. You want to know if the part has been ordered. You don't need a new appointment.",
    },
    {
        "id": "S06",
        "name": "Spam / Robocall",
        "description": "Obvious spam call with no real request",
        "expected_lead": False,
        "expected_score_min": 0,
        "expected_service": "Other",
        "caller_persona": "You are a robocall. Say something generic like 'Hello? Hello? Can you hear me?' and then go silent or repeat the same phrase. Don't respond meaningfully to any questions.",
    },
    {
        "id": "S07",
        "name": "Angry Caller — Demands Manager",
        "description": "Irate caller about a previous bad experience",
        "expected_lead": False,
        "expected_score_min": 0,
        "expected_service": "Other",
        "caller_persona": "You had a bad experience with a technician last month. You are furious. You demand to speak to a manager immediately. You refuse to give your details until you speak to a human. You say things like 'This is unacceptable' and 'I want to cancel everything'.",
    },
    {
        "id": "S08",
        "name": "Vague Caller — Won't Give Address",
        "description": "Interested but refuses to give their full address",
        "expected_lead": True,
        "expected_score_min": 4,
        "expected_service": "Repair",
        "caller_persona": "You want HVAC repair but you're very private. You give your name (Sam Chen) and phone (212-555-0177) but when asked for your address you say 'I'd rather not say over the phone' or just give the neighbourhood (Upper West Side). You still want someone to call you back.",
    },
    {
        "id": "S09",
        "name": "Large Commercial Job",
        "description": "Caller asking about a large commercial building job",
        "expected_lead": True,
        "expected_score_min": 6,
        "expected_service": "Installation",
        "caller_persona": "You manage a 12-unit apartment building and need all the HVAC units serviced and possibly replaced. This is a large commercial job. Your name is David Rosenberg, phone 718-555-0321, address 400 Atlantic Avenue Brooklyn NY 11217. You want someone to come assess the whole building.",
    },
    {
        "id": "S10",
        "name": "After Hours Emergency Inquiry",
        "description": "Caller asks if emergency service is available after hours",
        "expected_lead": True,
        "expected_score_min": 6,
        "expected_service": "Emergency",
        "caller_persona": "It's late at night and your AC just died. You ask if they have 24/7 emergency service. When told yes, you want to book it. Your name is Priya Patel, phone 917-555-0088, address 220 Flatbush Avenue, Brooklyn NY 11217. You are relieved help is available.",
    },
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def http(url, method="GET", body=None, headers={}):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}

def sb_delete(path):
    http(f"{SUPABASE}/rest/v1/{path}", "DELETE", None,
        {"apikey": SB_SVC, "Authorization": f"Bearer {SB_SVC}"})

def generate_transcript(scenario):
    """Use GPT-4o to generate a realistic call transcript for the scenario."""
    prompt = f"""Generate a realistic phone call transcript between an HVAC AI receptionist and a caller.

AGENT GREETING: "{AGENT_GREETING}"

CALLER PERSONA: {scenario['caller_persona']}

AGENT BEHAVIOR:
- Greets warmly
- Captures full name, callback number, and service address (confirms each back)
- Identifies the service needed
- Routes appropriately (emergency, lead capture, transfer for angry callers, etc.)
- Keeps responses concise (under 30 words)
- Ends professionally

FORMAT: 
Agent: [utterance]
Caller: [utterance]
(alternating, realistic conversation)

Generate ONLY the transcript, no commentary. Make it realistic — callers may stumble, correct themselves, or be unclear."""

    status, resp = http("https://api.openai.com/v1/chat/completions", "POST",
        {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 800
        },
        {"Authorization": f"Bearer {OPENAI_KEY}"}
    )
    if status == 200:
        return resp['choices'][0]['message']['content'].strip()
    return None

def run_scenario(scenario, openai_key):
    global OPENAI_KEY
    OPENAI_KEY = openai_key

    ts = int(time.time())
    call_id = f"scenario_{scenario['id']}_{ts}"

    # Generate transcript
    transcript = generate_transcript(scenario)
    if not transcript:
        return {"scenario": scenario['id'], "status": "ERROR", "reason": "Failed to generate transcript"}

    # Fire at call processor
    fake_call = {
        "event": "call_analyzed",
        "call": {
            "call_id": call_id,
            "agent_id": AGENT_ID,
            "call_status": "ended",
            "from_number": "+15555550199",
            "to_number": "+12292672271",
            "start_timestamp": ts * 1000 - 120000,
            "end_timestamp": ts * 1000,
            "disconnection_reason": "user_hangup",
            "call_analysis": {},
            "transcript": transcript
        }
    }

    status, _ = http(WEBHOOK_URL, "POST", fake_call)
    if status != 200:
        return {"scenario": scenario['id'], "status": "ERROR", "reason": f"Webhook HTTP {status}"}

    # Wait for processing
    time.sleep(18)

    # Check result in Supabase
    _, data = http(
        f"{SUPABASE}/rest/v1/hvac_call_log?call_id=eq.{call_id}&select=*",
        headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}"}
    )
    rows = data if isinstance(data, list) else []
    call_log = rows[0] if rows else {}

    # Score the result
    passed = True
    failures = []

    if not call_log:
        passed = False
        failures.append("Call not logged in Supabase")
    else:
        actual_lead = call_log.get('is_lead', False)
        actual_score = call_log.get('lead_score', 0)
        actual_service = call_log.get('service_requested', '')

        if actual_lead != scenario['expected_lead']:
            passed = False
            failures.append(f"is_lead={actual_lead} (expected {scenario['expected_lead']})")

        if scenario['expected_lead'] and actual_score < scenario['expected_score_min']:
            passed = False
            failures.append(f"lead_score={actual_score} (expected >={scenario['expected_score_min']})")

    # Cleanup
    sb_delete(f"hvac_call_log?call_id=eq.{call_id}")

    return {
        "scenario": scenario['id'],
        "name": scenario['name'],
        "status": "PASS" if passed else "FAIL",
        "failures": failures,
        "lead_score": call_log.get('lead_score', 'N/A'),
        "is_lead": call_log.get('is_lead', 'N/A'),
        "caller_name": call_log.get('caller_name', 'N/A'),
        "service": call_log.get('service_requested', 'N/A'),
        "summary": (call_log.get('summary', '') or '')[:80],
        "transcript_preview": transcript[:200] if transcript else '',
    }

def run_all(openai_key, agent_id=None):
    global AGENT_ID
    if agent_id:
        AGENT_ID = agent_id

    print("=" * 70)
    print("SYNTHARRA HVAC AI RECEPTIONIST — SCENARIO TEST RUNNER")
    print(f"Agent   : {AGENT_ID}")
    print(f"Started : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Scenarios: {len(SCENARIOS)}")
    print("=" * 70)

    results = []
    for i, scenario in enumerate(SCENARIOS):
        print(f"\n[{scenario['id']}] {scenario['name']}")
        print(f"  Expected: lead={scenario['expected_lead']} score>={scenario['expected_score_min']}")
        result = run_scenario(scenario, openai_key)
        results.append(result)
        icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"  {icon} {result['status']} — score={result['lead_score']} is_lead={result['is_lead']} service={result['service']}")
        if result['failures']:
            for f in result['failures']:
                print(f"     ↳ {f}")
        if result.get('caller_name') and result['caller_name'] != 'N/A':
            print(f"     caller={result['caller_name']} | {result['summary']}")

    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = len(results) - passed

    print("\n" + "=" * 70)
    print(f"RESULT: {passed}/{len(results)} passed  |  {failed} failed")
    if failed == 0:
        print("✅ ALL SCENARIOS PASSED")
    else:
        print("\n❌ FAILED SCENARIOS:")
        for r in results:
            if r['status'] == 'FAIL':
                print(f"  [{r['scenario']}] {r['name']}")
                for f in r['failures']:
                    print(f"    → {f}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scenario-runner.py <agent_id> [openai_key]")
        print("  agent_id   : Retell agent ID to test against")
        print("  openai_key : OpenAI API key (or set OPENAI_KEY env var)")
        sys.exit(1)

    agent_id = sys.argv[1]
    openai_key = sys.argv[2] if len(sys.argv) > 2 else ""

    if not openai_key:
        import os
        openai_key = os.environ.get('OPENAI_KEY', '')

    if not openai_key:
        print("❌ OpenAI key required")
        sys.exit(1)

    run_all(openai_key, agent_id)
