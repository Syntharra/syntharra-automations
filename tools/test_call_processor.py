#!/usr/bin/env python3
"""
test_call_processor.py — Call processor (Kg576YtPM9yEacKn) integration test.

Fires fake Retell post-call webhooks at the call processor and verifies the
execution succeeds for lead and emergency scenarios.

Does NOT verify email delivery (Brevo has no read API) — verifies n8n execution
status instead. SMS is a stub (Telnyx pending approval) — verified as no-op pass.

Usage:
  python tools/test_call_processor.py              # run all scenarios
  python tools/test_call_processor.py --scenario 1 # run one scenario
  python tools/test_call_processor.py --dry-run    # print payloads only

Required env vars (or hardcoded fallback):
  N8N_API_KEY
  SUPABASE_URL / SUPABASE_SERVICE_KEY  (to resolve a valid agent_id)
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

N8N_KEY = os.environ.get("N8N_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNDJlNTI0NWEtZjgxZi00OTBkLWJhMTAtNzg5ZjZlZDcxM2ZmIiwiaWF0IjoxNzc1NzQ1MjA3fQ.yY6u-03iyRQAFLsOvvReAmCBkwseZ-giSgYgJkLK0B8")
SB_URL  = os.environ.get("SUPABASE_URL", "https://hgheyqwnrcvwtgngqdnq.supabase.co")
SB_KEY  = os.environ.get("SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ"
    ".PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg")

N8N_BASE        = "https://n8n.syntharra.com"
PROCESSOR_WF    = "Kg576YtPM9yEacKn"
WEBHOOK_URL     = f"{N8N_BASE}/webhook/retell-hvac-webhook"

# TESTING agent — exists in hvac_standard_agent (use MASTER as fallback)
TESTING_AGENT_ID = "agent_41e9758d8dc956843110e29a25"

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

# ── Test scenarios ────────────────────────────────────────────────────────────
def make_call(call_id_suffix: str, agent_id: str, is_lead: bool,
              urgency: str, call_type: str, lead_score: int,
              caller_name: str = "Test Caller",
              caller_phone: str = "5551234567",
              caller_address: str = "123 Test St, Chicago IL 60601",
              service_requested: str = "AC repair",
              job_type: str = "repair",
              is_spam: bool = False,
              vulnerable_occupant: bool = False,
              transfer_attempted: bool = False,
              summary_override: str = "",
              event_override: str = "call_analyzed") -> dict:
    ts = int(time.time())
    summary = summary_override or f"Test call — {call_type}. Caller: {caller_name}."
    return {
        "event": event_override,
        "call": {
            "call_id": f"test_{call_id_suffix}_{ts}",
            "agent_id": agent_id,
            "from_number": "+15551234567",
            "to_number": "+18129944371",
            "duration_ms": 120000,
            "start_timestamp": ts * 1000 - 120000,
            "transcript": f"Sophie: Thank you for calling Arctic Breeze HVAC. Customer: {summary}",
            "recording_url": "",
            "public_log_url": f"https://beta.retellai.com/call/test_{call_id_suffix}_{ts}",
            "disconnection_reason": "user_hangup",
            "collected_dynamic_variables": {"caller_name": caller_name},
            "call_analysis": {
                "call_summary": summary,
                "call_successful": True,
                "user_sentiment": "Neutral",
                "custom_analysis_data": {
                    "is_lead": is_lead,
                    "urgency": urgency,
                    "is_spam": is_spam,
                    "caller_name": caller_name,
                    "caller_phone": caller_phone,
                    "caller_address": caller_address,
                    "service_requested": service_requested,
                    "job_type": job_type,
                    "lead_score": lead_score,
                    "call_type": call_type,
                    "vulnerable_occupant": vulnerable_occupant,
                    "transfer_attempted": transfer_attempted,
                    "transfer_success": False,
                    "emergency": urgency == "emergency",
                    "is_hot_lead": is_lead and lead_score >= 8,
                    "notification_type": "emergency" if urgency == "emergency" else "hot_lead",
                    "notes": "TEST — automated pipeline verification",
                    "language": "en",
                    "booking_attempted": False,
                    "booking_success": False,
                },
            },
        },
    }


# ── Scenario definitions ──────────────────────────────────────────────────────
# expect_email=True  → is_lead=True OR urgency=emergency  → passes filter → execution succeeds
# expect_email=False → neither flag → filtered at IF node → execution still succeeds (dead branch)
#
# Filter logic (from workflow):
#   event == "call_analyzed"
#   AND (is_lead == true OR urgency == "emergency")

SCENARIOS = [
    # ── Category A: Should trigger notification (email + optional Slack) ──────
    {
        "id": 1,
        "name": "Standard repair lead — AC stopped working",
        "is_lead": True, "urgency": "high", "call_type": "new_service", "lead_score": 7,
        "caller_name": "Mike Johnson", "caller_phone": "6315550199",
        "caller_address": "22 Oak Street, Brooklyn NY",
        "service_requested": "AC repair", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 2,
        "name": "New installation quote — furnace to heat pump",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 8,
        "caller_name": "Sarah Chen", "caller_phone": "7185550312",
        "caller_address": "48 Maple Avenue, Queens NY",
        "service_requested": "Heat pump installation", "job_type": "install",
        "expect_email": True,
    },
    {
        "id": 3,
        "name": "Emergency — elderly, no heat, vulnerable occupant",
        "is_lead": False, "urgency": "emergency", "call_type": "emergency", "lead_score": 9,
        "caller_name": "Robert Hall", "caller_phone": "2125550788",
        "caller_address": "10 Fifth Avenue, Manhattan NY",
        "service_requested": "Emergency heating repair", "job_type": "repair",
        "vulnerable_occupant": True,
        "expect_email": True,
    },
    {
        "id": 4,
        "name": "Annual maintenance booking",
        "is_lead": True, "urgency": "low", "call_type": "maintenance", "lead_score": 5,
        "caller_name": "Amanda Torres", "caller_phone": "9175550022",
        "caller_address": "15 Central Park West, New York NY",
        "service_requested": "Annual HVAC tune-up", "job_type": "maintenance",
        "expect_email": True,
    },
    {
        "id": 5,
        "name": "Live transfer — gas emergency",
        "is_lead": False, "urgency": "emergency", "call_type": "emergency", "lead_score": 2,
        "caller_name": "Unknown Caller", "caller_phone": "5551239999",
        "service_requested": "Gas leak emergency", "job_type": "emergency",
        "transfer_attempted": True,
        "expect_email": True,
    },
    {
        "id": 6,
        "name": "High-value commercial — 20-unit apartment complex",
        "is_lead": True, "urgency": "high", "call_type": "commercial", "lead_score": 10,
        "caller_name": "James Whitfield", "caller_phone": "2125550900",
        "caller_address": "300 East 45th Street, Manhattan NY",
        "service_requested": "Full building HVAC replacement", "job_type": "install",
        "expect_email": True,
    },
    {
        "id": 7,
        "name": "Caller hangs up early — partial lead captured",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 5,
        "caller_name": "Tom Walsh", "caller_phone": "5165550100",
        "caller_address": "", "service_requested": "HVAC repair", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 8,
        "name": "Angry existing customer — repeat callback needed",
        "is_lead": True, "urgency": "high", "call_type": "callback", "lead_score": 7,
        "caller_name": "Gary Mitchell", "caller_phone": "4045550350",
        "caller_address": "88 Peachtree Street, Atlanta GA",
        "service_requested": "Warranty callback — AC still broken", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 9,
        "name": "No address given — name and phone only",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 6,
        "caller_name": "Nina Patel", "caller_phone": "3035550410",
        "caller_address": "", "service_requested": "HVAC service", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 10,
        "name": "Complex urgent commercial — restaurant walk-in failure",
        "is_lead": True, "urgency": "emergency", "call_type": "commercial", "lead_score": 9,
        "caller_name": "Maria Santos", "caller_phone": "7185550441",
        "caller_address": "44 West Broadway, Tribeca, Manhattan NY 10007",
        "service_requested": "Commercial refrigerator compressor repair", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 11,
        "name": "Phonetic phone number — heat pump grinding noise",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 7,
        "caller_name": "Kevin Lee", "caller_phone": "6175550102",
        "caller_address": "55 Boylston Street, Boston MA",
        "service_requested": "Heat pump repair", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 12,
        "name": "Borderline service area — Hoboken NJ",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 6,
        "caller_name": "Paul Russo", "caller_phone": "2015550733",
        "caller_address": "Hoboken, NJ",
        "service_requested": "HVAC repair", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 13,
        "name": "Both flags — hot lead AND emergency",
        "is_lead": True, "urgency": "emergency", "call_type": "emergency", "lead_score": 10,
        "caller_name": "Lisa Brown", "caller_phone": "3125550200",
        "caller_address": "120 South Michigan Avenue, Chicago IL",
        "service_requested": "Emergency AC failure", "job_type": "repair",
        "expect_email": True,
    },
    {
        "id": 14,
        "name": "Low lead score but is_lead=true — still notifies",
        "is_lead": True, "urgency": "low", "call_type": "new_service", "lead_score": 4,
        "caller_name": "Dan Smith", "caller_phone": "5551110000",
        "service_requested": "General inquiry", "job_type": "repair",
        "expect_email": True,  # is_lead=True always triggers, regardless of score
    },
    {
        "id": 15,
        "name": "Heating failure mid-winter — no vulnerable occupant",
        "is_lead": False, "urgency": "emergency", "call_type": "emergency", "lead_score": 8,
        "caller_name": "James Park", "caller_phone": "7735551234",
        "caller_address": "500 Lake Shore Drive, Chicago IL",
        "service_requested": "Emergency furnace repair", "job_type": "repair",
        "expect_email": True,
    },

    # ── Category B: Should be filtered — neither is_lead nor urgency=emergency ─
    {
        "id": 16,
        "name": "Wrong number — takeaway restaurant",
        "is_lead": False, "urgency": "none", "call_type": "wrong_number", "lead_score": 0,
        "is_spam": False,
        "expect_email": False,
    },
    {
        "id": 17,
        "name": "Spam robocall — Google Business suspension",
        "is_lead": False, "urgency": "none", "call_type": "spam", "lead_score": 0,
        "is_spam": True,
        "expect_email": False,
    },
    {
        "id": 18,
        "name": "Out of service area — Los Angeles",
        "is_lead": False, "urgency": "none", "call_type": "out_of_area", "lead_score": 0,
        "caller_address": "Los Angeles, CA",
        "expect_email": False,
    },
    {
        "id": 19,
        "name": "Pricing enquiry — no booking intent",
        "is_lead": False, "urgency": "low", "call_type": "inquiry", "lead_score": 2,
        "caller_name": "Generic Caller",
        "expect_email": False,
    },
    {
        "id": 20,
        "name": "Short call — silence / no response",
        "is_lead": False, "urgency": "none", "call_type": "abandoned", "lead_score": 0,
        "summary_override": "Caller did not respond. Agent could not determine intent.",
        "expect_email": False,
    },
    {
        "id": 21,
        "name": "Vendor / supplier call",
        "is_lead": False, "urgency": "none", "call_type": "vendor", "lead_score": 0,
        "caller_name": "Mark Davies",
        "expect_email": False,
    },
    {
        "id": 22,
        "name": "Job applicant",
        "is_lead": False, "urgency": "none", "call_type": "job_inquiry", "lead_score": 0,
        "caller_name": "Jenny Wu",
        "expect_email": False,
    },
    {
        "id": 23,
        "name": "Urgency=high but is_lead=false — filtered",
        "is_lead": False, "urgency": "high", "call_type": "inquiry", "lead_score": 3,
        "caller_name": "Test High Urgency",
        "expect_email": False,  # urgency=high does NOT trigger — only emergency does
    },
    {
        "id": 24,
        "name": "Urgency=normal, is_lead=false — filtered",
        "is_lead": False, "urgency": "normal", "call_type": "inquiry", "lead_score": 2,
        "expect_email": False,
    },
    {
        "id": 25,
        "name": "Competitor inquiry — no lead",
        "is_lead": False, "urgency": "none", "call_type": "competitor", "lead_score": 0,
        "caller_name": "Competitor Rep",
        "expect_email": False,
    },

    # ── Category C: Edge cases ─────────────────────────────────────────────────
    {
        "id": 26,
        "name": "Edge: wrong event type (call_started) — filtered",
        "is_lead": True, "urgency": "emergency", "call_type": "new_service", "lead_score": 9,
        "event_override": "call_started",
        "expect_email": False,  # filter requires event=call_analyzed
    },
    {
        "id": 27,
        "name": "Edge: maximum lead score (10) — notifies",
        "is_lead": True, "urgency": "high", "call_type": "new_service", "lead_score": 10,
        "caller_name": "Premium Lead", "caller_phone": "5559991234",
        "service_requested": "Full system replacement", "job_type": "install",
        "expect_email": True,
    },
    {
        "id": 28,
        "name": "Edge: minimum fields, lead=true — notifies",
        "is_lead": True, "urgency": "normal", "call_type": "new_service", "lead_score": 6,
        "caller_name": "", "caller_phone": "", "caller_address": "",
        "expect_email": True,  # filter passes on is_lead alone, even with empty fields
    },
    {
        "id": 29,
        "name": "Edge: lead_score=0 but urgency=emergency — notifies",
        "is_lead": False, "urgency": "emergency", "call_type": "emergency", "lead_score": 0,
        "caller_name": "Anonymous Emergency",
        "expect_email": True,  # emergency overrides lead_score
    },
    {
        "id": 30,
        "name": "Edge: is_spam=true AND is_lead=true — notifies (lead wins)",
        "is_lead": True, "urgency": "high", "call_type": "new_service", "lead_score": 7,
        "is_spam": True,
        "caller_name": "Possible Spam Lead",
        "expect_email": True,  # workflow filter only checks is_lead/urgency, not is_spam
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def webhook_post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
          headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {}

def n8n_get(path):
    req = urllib.request.Request(f"{N8N_BASE}{path}", headers={"X-N8N-API-KEY": N8N_KEY})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def get_agent_id_for_test() -> str:
    """Find a valid agent_id in hvac_standard_agent to use for call processor test."""
    try:
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/hvac_standard_agent?select=agent_id&limit=1",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
        )
        rows = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if rows:
            return rows[0]["agent_id"]
    except Exception:
        pass
    return TESTING_AGENT_ID

def poll_execution(trigger_time: datetime, timeout_s: int = 60) -> tuple[str | None, str | None]:
    """Poll n8n executions for the call processor workflow. Returns (exec_id, status).

    Handles clock skew (n8n server may be ~300ms behind local clock) by using
    trigger_time already adjusted by caller. Also handles running executions by
    tracking the specific exec ID until it completes.
    """
    def _find_exec(include_running: bool = False) -> tuple[str | None, str | None]:
        statuses = ["success", "error", "crashed"]
        if include_running:
            statuses.append("running")
        for st in statuses:
            try:
                execs = n8n_get(f"/api/v1/executions?workflowId={PROCESSOR_WF}&status={st}&limit=5")
                for ex in execs.get("data", []):
                    started = ex.get("startedAt", "")
                    if started:
                        ex_time = datetime.fromisoformat(started.replace("Z", "+00:00"))
                        if ex_time >= trigger_time:
                            return ex.get("id"), ex.get("status")
            except Exception:
                pass
        return None, None

    for _ in range(timeout_s // 3):
        time.sleep(3)
        eid, est = _find_exec(include_running=True)
        if eid:
            if est in ("success", "error", "crashed"):
                return eid, est
            # Running — poll by ID until done
            for _ in range(40):  # up to ~2 more minutes
                time.sleep(3)
                try:
                    ex = n8n_get(f"/api/v1/executions/{eid}")
                    est = ex.get("status")
                    if est in ("success", "error", "crashed"):
                        return eid, est
                except Exception:
                    pass
            return eid, est  # timed out waiting for running exec
    return None, None

def check(label, passed, detail=""):
    status = PASS if passed else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {status} {label}{suffix}")
    return passed

# ── Main ──────────────────────────────────────────────────────────────────────
def run(args):
    print(f"\n{'='*60}")
    print(f"  Call Processor Integration Test")
    print(f"  Workflow: {PROCESSOR_WF}")
    print(f"  Webhook : {WEBHOOK_URL}")
    print(f"  Time    : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*60}")

    agent_id = get_agent_id_for_test()
    print(f"\n{INFO} Using agent_id: {agent_id}")

    scenarios = SCENARIOS
    if args.scenario:
        scenarios = [s for s in SCENARIOS if s["id"] == args.scenario]
        if not scenarios:
            print(f"{FAIL} Scenario {args.scenario} not found")
            return 1

    overall_results = []

    for sc in scenarios:
        print(f"\n{'─'*60}")
        print(f"  Scenario {sc['id']}: {sc['name']}")
        print(f"  Expect email: {sc['expect_email']}")
        print(f"{'─'*60}")

        payload = make_call(
            f"sc{sc['id']}",
            agent_id,
            sc["is_lead"],
            sc["urgency"],
            sc["call_type"],
            sc["lead_score"],
            caller_name=sc.get("caller_name", "Test Caller"),
            caller_phone=sc.get("caller_phone", "5551234567"),
            caller_address=sc.get("caller_address", "123 Test St, Chicago IL 60601"),
            service_requested=sc.get("service_requested", "AC repair"),
            job_type=sc.get("job_type", "repair"),
            is_spam=sc.get("is_spam", False),
            vulnerable_occupant=sc.get("vulnerable_occupant", False),
            transfer_attempted=sc.get("transfer_attempted", False),
            summary_override=sc.get("summary_override", ""),
            event_override=sc.get("event_override", "call_analyzed"),
        )

        if args.dry_run:
            print(json.dumps(payload, indent=2))
            continue

        # Subtract 3s to absorb n8n server clock skew vs local clock
        trigger_time = datetime.now(timezone.utc) - timedelta(seconds=3)
        status, resp = webhook_post(WEBHOOK_URL, payload)
        ok = check("Webhook accepted", status == 200, f"HTTP {status}")
        overall_results.append(ok)
        if not ok:
            print(f"  {INFO} Response: {resp}")
            continue

        # Poll for execution
        print(f"  {INFO} Polling execution (up to 30s)...")
        exec_id, exec_status = poll_execution(trigger_time)

        ok = check("Execution found", exec_id is not None, exec_id or "not found")
        overall_results.append(ok)
        if not ok:
            continue

        if sc["expect_email"]:
            ok = check("Execution succeeded (email path)", exec_status == "success",
                       f"status={exec_status}")
        else:
            # Filtered scenarios: workflow still succeeds, but stops at IF node
            ok = check("Execution completed (filtered — no email expected)",
                       exec_status in ("success",), f"status={exec_status}")
        overall_results.append(ok)
        print(f"  {INFO} Exec ID: {exec_id} | Status: {exec_status}")

        if sc["expect_email"]:
            print(f"  {INFO} Email: Brevo delivery not auto-verifiable — check inbox at test-e2e@syntharra.com")
            print(f"  {INFO} SMS  : Telnyx stub (no-op) — expected to pass silently")

        time.sleep(2)  # brief gap between scenarios

    if args.dry_run:
        return 0

    print(f"\n{'='*60}")
    passed = sum(1 for r in overall_results if r)
    total  = len(overall_results)
    all_ok = passed == total
    print(f"  Result: {passed}/{total} checks passed")
    if all_ok:
        print(f"  {PASS} ALL SCENARIOS PASSED")
    else:
        print(f"  {FAIL} {total - passed} CHECK(S) FAILED")
    print(f"{'='*60}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call processor integration test")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scenario", type=int, help="Run a single scenario by ID")
    raise SystemExit(run(parser.parse_args()))
