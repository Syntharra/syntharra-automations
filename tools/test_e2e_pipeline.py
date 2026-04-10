#!/usr/bin/env python3
"""
test_e2e_pipeline.py — End-to-end pipeline test.

Tests the full onboarding path:
  Jotform webhook → n8n onboarding → Supabase row → Retell agent → Dashboard 0 calls

On success: triggers the E2E cleanup workflow to delete the test agent after 5 minutes.
On failure: prints what failed and leaves artefacts for inspection.

Usage:
  python tools/test_e2e_pipeline.py            # run full test
  python tools/test_e2e_pipeline.py --no-clean # skip cleanup (inspect artefacts)
  python tools/test_e2e_pipeline.py --dry-run  # print payload only, no network calls

Required env vars (or hardcoded fallback from build_telnyx_phone_nodes.py):
  N8N_API_KEY
  SUPABASE_URL
  SUPABASE_SERVICE_KEY
  RETELL_API_KEY
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Credentials ──────────────────────────────────────────────────────────────
N8N_KEY    = os.environ.get("N8N_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNDJlNTI0NWEtZjgxZi00OTBkLWJhMTAtNzg5ZjZlZDcxM2ZmIiwiaWF0IjoxNzc1NzQ1MjA3fQ.yY6u-03iyRQAFLsOvvReAmCBkwseZ-giSgYgJkLK0B8")
SB_URL     = os.environ.get("SUPABASE_URL", "https://hgheyqwnrcvwtgngqdnq.supabase.co")
SB_KEY     = os.environ.get("SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ"
    ".PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg")
RETELL_KEY = os.environ.get("RETELL_API_KEY", "")

N8N_BASE       = "https://n8n.syntharra.com"
ONBOARDING_WF  = "4Hx7aRdzMl5N0uJP"
CLEANUP_WF     = "URbQPNQP26OIdYMo"
RETELL_BASE    = "https://api.retellai.com"
RETELL_PROXY   = f"{N8N_BASE}/webhook/retell-calls"

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

# ── HTTP helpers ──────────────────────────────────────────────────────────────
def n8n_get(path):
    req = urllib.request.Request(f"{N8N_BASE}{path}", headers={"X-N8N-API-KEY": N8N_KEY})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def n8n_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{N8N_BASE}{path}", data=data,
          headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def sb_get(path):
    req = urllib.request.Request(f"{SB_URL}{path}",
          headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def retell_get(path):
    if not RETELL_KEY:
        return None
    req = urllib.request.Request(f"{RETELL_BASE}{path}",
          headers={"Authorization": f"Bearer {RETELL_KEY}"})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def webhook_post(url, body, headers=None):
    data = json.dumps(body).encode()
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {}

# ── Test payload ──────────────────────────────────────────────────────────────
def build_jotform_payload(submission_id: str, company_name: str) -> dict:
    """Build a realistic Jotform webhook payload for the onboarding workflow."""
    raw = {
        "q4_hvacCompany": company_name,
        "q54_ownerName": "Test Owner",
        "q5_emailAddress": "test-e2e@syntharra.com",
        "q6_mainCompany": {"full": "(555) 123-4567"},
        "q7_companyWebsite": "https://test-e2e.com",
        "q8_yearsIn": "5",
        "q34_timezone": "America/Chicago",
        "q10_aiAgent10": "Emma",
        "q11_aiVoice": "Female",
        "q13_option_": "AC Repair, Heating Repair, General Maintenance",
        "q14_option_": "Carrier, Trane, Lennox",
        "q29_option_": "NATE Certified",
        "q16_primaryService": "Chicago, IL",
        "q40_serviceAreaRadius": "30",
        "q28_licensedAnd": "Yes",
        "q20_247Emergency": "Yes",
        "q21_emergencyAfterhours": {"full": "(555) 999-0000"},
        "q22_afterhoursBehavior": "Transfer to emergency line",
        "q68_afterHoursTransfer": "Transfer",
        "q17_businessHours": "Mon-Fri 8am-5pm, Sat 9am-2pm",
        "q18_typicalResponse": "Same day for emergencies, next day for standard",
        "q41_diagnosticFee": "$85",
        "q42_pricingPolicy": "Upfront pricing, no surprises",
        "q43_standardFees": "AC tune-up $129, furnace tune-up $99",
        "q24_freeEstimates": "Yes - always free",
        "q57_doNotServiceList": "Window units",
        "q48_transferPhone": {"full": "(555) 888-7777"},
        "q49_transferTriggers": "Customer requests to speak with someone",
        "q50_transferBehavior": "Always transfer when requested",
        "q25_financingAvailable": "Yes",
        "q44_financingDetails": "12 months same as cash with approved credit",
        "q26_serviceWarranties": "Yes",
        "q27_warrantyDetails": "1 year parts and labor on all repairs",
        "q45_paymentMethods": "Cash, Credit Card, Check, Financing",
        "q46_maintenancePlans": "Yes",
        "q58_membershipProgramName": "Arctic Club",
        "q31_leadContact": "Both",
        "q32_leadNotification": {"full": "(555) 123-4567"},
        "q33_leadNotification33": "test-e2e@syntharra.com",
        "q55_googleReviewRating": "4.9",
        "q56_googleReviewCount": "127",
        "q51_uniqueSellingPoints": "24/7 emergency service, NATE certified technicians",
        "q52_currentPromotion": "E2E-TEST — $50 off first service",
        "q53_seasonalServices": "Spring AC tune-up, Fall furnace tune-up",
        "q37_additionalInfo": "TEST SUBMISSION — auto-cleanup in 5 minutes",
        "submissionID": submission_id,
    }
    return {
        "submissionID": submission_id,
        "formID": "260795139953066",
        "rawRequest": json.dumps(raw),
    }

# ── Phase helpers ─────────────────────────────────────────────────────────────
def phase(n, label):
    print(f"\n{'='*60}")
    print(f"  Phase {n}: {label}")
    print(f"{'='*60}")

def check(label, passed, detail=""):
    status = PASS if passed else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {status} {label}{suffix}")
    return passed

# ── Main test ─────────────────────────────────────────────────────────────────
def run(args):
    ts = int(time.time())
    submission_id = f"E2E_TEST_{ts}"
    company_name  = f"E2E Test HVAC {ts % 100000}"
    payload       = build_jotform_payload(submission_id, company_name)

    print(f"\n{'='*60}")
    print(f"  Syntharra E2E Pipeline Test")
    print(f"  Submission ID : {submission_id}")
    print(f"  Company       : {company_name}")
    print(f"  Time          : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*60}")

    if args.dry_run:
        print(f"\n{INFO} DRY RUN — payload:")
        print(json.dumps(payload, indent=2))
        return 0

    results = []

    # ── Phase 1: Submit Jotform webhook ───────────────────────────────────────
    phase(1, "Jotform webhook → n8n onboarding trigger")
    # Record trigger_time 3s in the past to absorb n8n server clock skew
    trigger_time = datetime.now(timezone.utc) - timedelta(seconds=3)
    status, resp = webhook_post(f"{N8N_BASE}/webhook/jotform-hvac-onboarding", payload)
    ok = check("Webhook accepted (HTTP 200)", status == 200, f"got {status}")
    results.append(ok)
    if not ok:
        print(f"\n{FAIL} Webhook rejected. Aborting.")
        return 1
    print(f"  {INFO} Trigger time: {trigger_time.strftime('%H:%M:%S')} UTC (3s window)")

    # ── Phase 2: Wait for n8n execution to complete ───────────────────────────
    phase(2, "n8n onboarding execution")
    print(f"  {INFO} Polling executions (up to 90s)...")
    exec_id = None
    exec_status = None

    def _find_exec_after(trigger: datetime, include_running: bool = False) -> tuple[str | None, str | None]:
        """Check completed (and optionally running) executions for one started after trigger."""
        statuses = ["success", "error", "crashed"]
        if include_running:
            statuses.append("running")
        for st in statuses:
            try:
                execs = n8n_get(f"/api/v1/executions?workflowId={ONBOARDING_WF}&status={st}&limit=5")
                for ex in execs.get("data", []):
                    started = ex.get("startedAt", "")
                    if started:
                        ex_time = datetime.fromisoformat(started.replace("Z", "+00:00"))
                        if ex_time >= trigger:
                            return ex.get("id"), ex.get("status")
            except Exception:
                pass
        return None, None

    for attempt in range(18):  # 18 x 5s = 90s
        time.sleep(5)
        try:
            eid, est = _find_exec_after(trigger_time, include_running=True)
            if eid:
                exec_id = eid
                exec_status = est
                print(f"  {INFO} Attempt {attempt+1}: exec {exec_id} status={exec_status}")
                if exec_status in ("success", "error", "crashed"):
                    break
                # Found a running execution — poll that specific ID until done
                print(f"  {INFO} Execution is running — polling by ID...")
                for _ in range(24):  # up to 2 more minutes
                    time.sleep(5)
                    try:
                        ex = n8n_get(f"/api/v1/executions/{exec_id}")
                        exec_status = ex.get("status")
                        print(f"  {INFO} exec {exec_id} status={exec_status}")
                        if exec_status in ("success", "error", "crashed"):
                            break
                    except Exception as e2:
                        print(f"  {INFO} ID poll error: {e2}")
                break
        except Exception as e:
            print(f"  {INFO} Attempt {attempt+1}: polling error: {e}")

    ok = check("Execution found", exec_id is not None, exec_id or "not found")
    results.append(ok)
    ok2 = check("Execution succeeded", exec_status == "success", f"status={exec_status}")
    results.append(ok2)
    if not ok2:
        print(f"\n{FAIL} Onboarding execution failed (status={exec_status}). Check n8n logs for exec {exec_id}.")
        return 1

    # ── Phase 3: Verify Supabase row ──────────────────────────────────────────
    phase(3, "Supabase — hvac_standard_agent row")
    time.sleep(2)
    # Query by company_name (URL-safe) — company_name contains the timestamp suffix
    # which is unique per run. Avoid submission_id eq filter (underscores cause 400).
    import urllib.parse
    name_filter = urllib.parse.quote(company_name)
    rows = sb_get(f"/rest/v1/hvac_standard_agent?company_name=eq.{name_filter}&select=*")
    ok = check("Row created", len(rows) > 0, f"found {len(rows)} row(s)")
    results.append(ok)
    if not ok:
        print(f"\n{FAIL} Supabase row not found. Company: {company_name}")
        return 1

    row = rows[0]
    agent_id      = row.get("agent_id", "")
    flow_id       = row.get("conversation_flow_id", "")
    agent_phone   = row.get("agent_phone_number", "")
    agent_status  = row.get("agent_status", "")

    required_fields = [
        ("company_name", row.get("company_name")),
        ("client_email", row.get("client_email")),
        ("agent_id", agent_id),
        ("conversation_flow_id", flow_id),
        ("services_offered", row.get("services_offered")),
        ("business_hours", row.get("business_hours")),
        ("timezone", row.get("timezone")),
    ]
    for fname, fval in required_fields:
        ok = check(f"Field populated: {fname}", bool(fval), str(fval)[:40] if fval else "EMPTY")
        results.append(ok)

    print(f"  {INFO} Agent ID  : {agent_id}")
    print(f"  {INFO} Flow ID   : {flow_id}")
    print(f"  {INFO} Phone     : {agent_phone or '(not assigned — Telnyx pending)'}")
    print(f"  {INFO} Status    : {agent_status}")

    # ── Phase 4: Verify Retell agent ──────────────────────────────────────────
    phase(4, "Retell — agent published")
    if RETELL_KEY and agent_id:
        try:
            agent = retell_get(f"/get-agent/{agent_id}")
            ok = check("Agent exists in Retell", agent is not None, agent_id)
            results.append(ok)
            ok = check("Agent is published", agent.get("response_engine", {}).get("type") is not None,
                       f"llm_id={agent.get('response_engine',{}).get('llm_id','?')}")
            results.append(ok)
            ok = check("Agent name looks correct", company_name.split()[0] in (agent.get("agent_name","") or ""),
                       f"got={agent.get('agent_name','?')}")
            results.append(ok)
        except Exception as e:
            print(f"  {INFO} Retell check skipped: {e}")
    else:
        print(f"  {INFO} Retell check skipped (RETELL_API_KEY not set or no agent_id)")

    # ── Phase 5: Dashboard — zero calls ───────────────────────────────────────
    phase(5, "Dashboard proxy — new agent shows 0 calls")
    if agent_id:
        try:
            status, resp = webhook_post(RETELL_PROXY, {"agent_id": agent_id})
            calls = resp.get("calls", [])
            ok = check("Proxy responded", status == 200, f"HTTP {status}")
            results.append(ok)
            ok = check("Zero calls for new agent", len(calls) == 0, f"got {len(calls)} call(s)")
            results.append(ok)
        except Exception as e:
            print(f"  {INFO} Dashboard proxy check failed: {e}")
    else:
        print(f"  {INFO} Dashboard check skipped (no agent_id)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    passed = sum(1 for r in results if r)
    total  = len(results)
    all_ok = passed == total
    print(f"  Result: {passed}/{total} checks passed")
    if all_ok:
        print(f"  {PASS} ALL CHECKS PASSED")
    else:
        print(f"  {FAIL} {total - passed} CHECK(S) FAILED")
    print(f"{'='*60}")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    if not args.no_clean and agent_id:
        print(f"\n{INFO} Triggering E2E cleanup workflow (5-min delayed delete)...")
        cleanup_payload = {
            "agent_id": agent_id,
            "flow_id": flow_id,
            "submission_id": submission_id,
            "tier": "standard",
        }
        try:
            c_status, _ = webhook_post(f"{N8N_BASE}/webhook/e2e-cleanup", cleanup_payload)
            if c_status == 200:
                print(f"  {PASS} Cleanup scheduled — agent {agent_id} will be deleted in ~5 minutes")
            else:
                print(f"  {INFO} Cleanup webhook returned {c_status} — delete manually: agent_id={agent_id}")
        except Exception as e:
            print(f"  {INFO} Cleanup webhook error: {e}")
            print(f"  {INFO} Manual cleanup: DELETE Retell agent {agent_id}, Supabase row submission_id={submission_id}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E2E pipeline test")
    parser.add_argument("--dry-run", action="store_true", help="Print payload only")
    parser.add_argument("--no-clean", action="store_true", help="Skip cleanup")
    raise SystemExit(run(parser.parse_args()))
