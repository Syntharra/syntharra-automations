#!/usr/bin/env python3
"""
test_email_delivery.py — Layer 3: Email delivery confirmation.

Fires one real call processor webhook (lead scenario) to an agent whose lead_email
is daniel@syntharra.com, waits 30s, then uses `claude -p` to check Gmail via MCP
for an email from Brevo in the last 5 minutes.

Single scenario — proves the Brevo integration is live end-to-end.

Usage:
  python tools/test_email_delivery.py
  python tools/test_email_delivery.py --wait 60   # extend Gmail poll window
  python tools/test_email_delivery.py --dry-run   # print payload only

Notes:
  - Uses agent_9cb7cb7259ed42205734e36365 (Syntharra Test HVAC, lead_email=daniel@syntharra.com)
  - n8n execution success is also checked (not just email arrival)
  - Gmail check uses `claude -p` with Gmail MCP configured in this Claude Code install
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Constants ────────────────────────────────────────────────────────────────
N8N_KEY = os.environ.get("N8N_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNDJlNTI0NWEtZjgxZi00OTBkLWJhMTAtNzg5ZjZlZDcxM2ZmIiwiaWF0IjoxNzc1NzQ1MjA3fQ.yY6u-03iyRQAFLsOvvReAmCBkwseZ-giSgYgJkLK0B8")

N8N_BASE     = "https://n8n.syntharra.com"
PROCESSOR_WF = "Kg576YtPM9yEacKn"
WEBHOOK_URL  = f"{N8N_BASE}/webhook/retell-hvac-webhook"

# Agent whose lead_email resolves to daniel@syntharra.com in Supabase
TEST_AGENT_ID = "agent_9cb7cb7259ed42205734e36365"
TEST_EMAIL    = "daniel@syntharra.com"

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"


# ── Helpers ──────────────────────────────────────────────────────────────────

def webhook_post(url: str, body: dict) -> tuple[int, dict]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
          headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {}


def n8n_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{N8N_BASE}{path}", headers={"X-N8N-API-KEY": N8N_KEY}
    )
    return json.loads(urllib.request.urlopen(req, timeout=15).read())


def poll_execution(trigger_time: datetime, timeout_s: int = 60) -> tuple[str | None, str | None]:
    """Poll n8n for the call processor execution after trigger_time."""
    def _find():
        for st in ("success", "error", "crashed", "running"):
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
        eid, est = _find()
        if eid:
            if est in ("success", "error", "crashed"):
                return eid, est
            # still running — wait for completion
            for _ in range(20):
                time.sleep(3)
                try:
                    ex = n8n_get(f"/api/v1/executions/{eid}")
                    est = ex.get("status")
                    if est in ("success", "error", "crashed"):
                        return eid, est
                except Exception:
                    pass
            return eid, est
    return None, None


def build_lead_payload() -> dict:
    ts = int(time.time())
    return {
        "event": "call_analyzed",
        "call": {
            "call_id": f"test_email_delivery_{ts}",
            "agent_id": TEST_AGENT_ID,
            "from_number": "+15551110001",
            "to_number": "+18129944371",
            "duration_ms": 90000,
            "start_timestamp": ts * 1000 - 90000,
            "transcript": "SOPHIE: Thank you for calling. CALLER: My AC stopped working, I need someone out today.",
            "recording_url": "",
            "public_log_url": f"https://beta.retellai.com/call/test_email_delivery_{ts}",
            "disconnection_reason": "user_hangup",
            "collected_dynamic_variables": {"caller_name": "Test Lead Email"},
            "call_analysis": {
                "call_summary": "Test lead — AC not working, email delivery verification.",
                "call_successful": True,
                "user_sentiment": "Neutral",
                "custom_analysis_data": {
                    "is_lead": True,
                    "urgency": "normal",
                    "is_spam": False,
                    "caller_name": "Test Lead Email",
                    "caller_phone": "5551110001",
                    "caller_address": "123 Test Lane, Chicago IL",
                    "service_requested": "AC repair",
                    "job_type": "repair",
                    "lead_score": 7,
                    "call_type": "new_service",
                    "vulnerable_occupant": False,
                    "transfer_attempted": False,
                    "transfer_success": False,
                    "emergency": False,
                    "is_hot_lead": False,
                    "notification_type": "lead",
                    "notes": "TEST — email delivery verification run",
                    "language": "en",
                    "booking_attempted": False,
                    "booking_success": False,
                },
            },
        },
    }


def check_gmail_via_claude(wait_seconds: int) -> tuple[bool, str]:
    """Use claude -p with Gmail MCP to check for Brevo email arrival."""
    prompt = (
        f"Search Gmail for emails received in the last {wait_seconds + 60} seconds "
        f"sent to {TEST_EMAIL} about an HVAC lead or call notification. "
        f"The sender will be Brevo (noreply@syntharra.com or similar Brevo sending domain). "
        f"Use the gmail_search_messages tool to search. "
        f"Reply with ONLY one of these two strings: "
        f"EMAIL_FOUND if you found such an email, or EMAIL_NOT_FOUND if you did not."
    )
    import platform
    on_windows = platform.system() == "Windows"
    try:
        base = ["cmd", "/c", "claude"] if on_windows else ["claude"]
        cmd = base + ["-p", prompt, "--allowedTools", "mcp__claude_ai_Gmail__gmail_search_messages"]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace"
        )
        output = result.stdout.strip()
        if "EMAIL_FOUND" in output:
            return True, output
        return False, output
    except subprocess.TimeoutExpired:
        return False, "claude -p timed out checking Gmail"
    except FileNotFoundError:
        return False, "`claude` CLI not found"


def run(args: argparse.Namespace) -> int:
    print(f"\n{'='*62}")
    print(f"  Email Delivery Test — Layer 3")
    print(f"  Test agent : {TEST_AGENT_ID}")
    print(f"  Target inbox: {TEST_EMAIL}")
    print(f"  Webhook    : {WEBHOOK_URL}")
    print(f"{'='*62}")

    payload = build_lead_payload()

    if args.dry_run:
        print(f"\n{INFO} DRY RUN — payload:")
        print(json.dumps(payload, indent=2))
        return 0

    results = []

    # Step 1: Fire webhook
    print(f"\n{INFO} Firing test lead webhook...")
    trigger_time = datetime.now(timezone.utc) - timedelta(seconds=3)
    status, resp = webhook_post(WEBHOOK_URL, payload)
    ok = status == 200
    results.append(ok)
    label = f"HTTP {status}"
    print(f"  {'[PASS]' if ok else '[FAIL]'} Webhook accepted ({label})")
    if not ok:
        print(f"  {FAIL} Webhook failed — aborting email delivery test")
        return 1

    # Step 2: Poll n8n execution
    print(f"\n{INFO} Polling n8n execution (up to 30s)...")
    exec_id, exec_status = poll_execution(trigger_time, timeout_s=30)
    ok_exec = exec_id is not None and exec_status == "success"
    results.append(ok_exec)
    print(f"  {'[PASS]' if ok_exec else '[FAIL]'} n8n execution (id={exec_id}, status={exec_status})")

    # Step 3: Wait for Brevo to deliver
    wait = args.wait
    print(f"\n{INFO} Waiting {wait}s for Brevo to deliver email...")
    time.sleep(wait)

    # Step 4: Check Gmail via claude -p MCP
    print(f"\n{INFO} Checking Gmail via claude -p Gmail MCP...")
    found, detail = check_gmail_via_claude(wait)
    results.append(found)
    print(f"  {'[PASS]' if found else '[FAIL]'} Email arrived in {TEST_EMAIL}")
    if not found:
        print(f"       Detail: {detail}")
        print(f"  {INFO} If email is delayed, check Brevo dashboard for delivery status")

    # Summary
    passed = sum(results)
    total  = len(results)
    print(f"\n{'='*62}")
    print(f"  Result: {passed}/{total} checks passed")
    if passed == total:
        print(f"  {PASS} LAYER 3 PASSED — email delivery confirmed end-to-end")
    else:
        print(f"  {FAIL} LAYER 3 FAILED — check Brevo dashboard + Gmail spam folder")
    print(f"{'='*62}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email delivery confirmation test (Layer 3)")
    parser.add_argument("--wait", type=int, default=30, help="Seconds to wait for delivery (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Print payload only, no real calls")
    raise SystemExit(run(parser.parse_args()))
