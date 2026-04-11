#!/usr/bin/env python3
"""
test_pilot_lifecycle.py — Pure-logic unit tests for pilot_lifecycle.process_pilot.

All network-touching helpers (supabase_get, supabase_post, supabase_patch,
brevo_send, stripe_call, retell_call, emit_marketing_event) are replaced with
in-memory fakes via direct module-attribute monkey-patching. Nothing touches
the network.

Run:
    python tools/test_pilot_lifecycle.py
"""
from __future__ import annotations
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

# Stub env vars BEFORE importing pilot_lifecycle so env() calls don't exit.
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
os.environ.setdefault("BREVO_API_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_xyz")
os.environ.setdefault("RETELL_API_KEY", "test-key")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot_lifecycle as pl  # noqa: E402


# --------------------------------------------------------------------------
# Fake world state — re-initialized in setUp
# --------------------------------------------------------------------------

class FakeWorld:
    def __init__(self) -> None:
        self.email_sends: list[dict] = []   # rows written to pilot_email_sends
        self.marketing_events: list[dict] = []
        self.supabase_patches: list[tuple[str, dict]] = []
        self.stripe_calls: list[tuple[str, str, dict]] = []
        self.retell_calls: list[tuple[str, str, dict]] = []
        self.brevo_sends: list[tuple[str, str, dict]] = []


world = FakeWorld()


# --- Fakes that replace pl.* helpers ---

def fake_supabase_get(path: str) -> list[dict]:
    # We emulate the `already_sent` check: look up pilot_email_sends
    if "/rest/v1/pilot_email_sends" in path:
        # Crudely parse "client_agent_id=eq.X" and "email_key=eq.Y" out of the path
        agent = _parse_eq(path, "client_agent_id")
        key = _parse_eq(path, "email_key")
        return [
            {"id": 1}
            for row in world.email_sends
            if row["client_agent_id"] == agent and row["email_key"] == key
        ]
    return []


def _parse_eq(path: str, field: str) -> str:
    import urllib.parse as up
    token = f"{field}=eq."
    i = path.find(token)
    if i < 0:
        return ""
    rest = path[i + len(token):]
    j = rest.find("&")
    raw = rest if j < 0 else rest[:j]
    return up.unquote(raw)


def fake_supabase_post(path: str, body: dict) -> dict:
    if "pilot_email_sends" in path:
        world.email_sends.append(body)
        return {"id": len(world.email_sends)}
    if "marketing_events" in path:
        world.marketing_events.append(body)
        return {"id": "fake"}
    return {}


def fake_supabase_patch(path: str, body: dict) -> dict:
    world.supabase_patches.append((path, body))
    return {}


def fake_brevo_send(template_slug: str, to_email: str, params: dict) -> str:
    world.brevo_sends.append((template_slug, to_email, params))
    return f"fake-msg-{len(world.brevo_sends)}"


def fake_stripe_call(method: str, path: str, body=None) -> dict:
    world.stripe_calls.append((method, path, body or {}))
    if method == "GET" and path.startswith("/v1/customers/"):
        return {"invoice_settings": {"default_payment_method": "pm_fake_123"}}
    if method == "POST" and path == "/v1/subscriptions":
        return {"id": "sub_fake_xyz", "status": "active"}
    return {"id": "fake"}


def fake_retell_call(method: str, path: str, body=None) -> dict:
    world.retell_calls.append((method, path, body or {}))
    return {"ok": True}


def fake_emit_marketing_event(event_type: str, props: dict) -> None:
    world.marketing_events.append({"event_type": event_type, **props})


# --- Fake http that also blocks any real outbound call just in case ---

def fake_http_json(method: str, url: str, headers: dict, body=None, timeout: int = 60):
    raise AssertionError(f"unexpected real HTTP call: {method} {url}")


# --------------------------------------------------------------------------
# Test helpers
# --------------------------------------------------------------------------

def make_pilot(*,
               agent_id: str = "agent_test_1",
               started_days_ago: int,
               status: str = "pilot",
               setup_intent: bool = False,
               payment_method_added: bool = False,
               customer_id: str = "cus_fake_1",
               minutes_used: int = 47,
               minutes_allotted: int = 200,
               first_touch_asset: str = "asset-test") -> dict:
    started = datetime(2026, 4, 1, tzinfo=timezone.utc) - timedelta(days=0)
    # "started_days_ago" is interpreted relative to the test's fixed `today`
    today = datetime(2026, 4, 15, tzinfo=timezone.utc)  # arbitrary fixed
    pilot_start = today - timedelta(days=started_days_ago)
    return {
        "agent_id": agent_id,
        "company_name": "Test HVAC Co",
        "owner_name": "Dan Smith",
        "client_email": "dan@test-hvac.example",
        "pilot_started_at": pilot_start.isoformat(),
        "pilot_ends_at": (pilot_start + timedelta(days=14)).isoformat(),
        "pilot_minutes_allotted": minutes_allotted,
        "pilot_minutes_used": minutes_used,
        "payment_method_added_at": pilot_start.isoformat() if payment_method_added else None,
        "stripe_setup_intent_succeeded": setup_intent,
        "status": status,
        "stripe_customer_id": customer_id,
        "stripe_subscription_id": None,
        "first_touch_asset_id": first_touch_asset,
        "first_touch_utm": None,
    }


FIXED_TODAY = datetime(2026, 4, 15, tzinfo=timezone.utc)


class PilotLifecycleTests(unittest.TestCase):

    def setUp(self) -> None:
        global world
        world = FakeWorld()
        # Re-bind module-level helpers to fakes
        pl.supabase_get = fake_supabase_get
        pl.supabase_post = fake_supabase_post
        pl.supabase_patch = fake_supabase_patch
        pl.brevo_send = fake_brevo_send
        pl.stripe_call = fake_stripe_call
        pl.retell_call = fake_retell_call
        pl.emit_marketing_event = fake_emit_marketing_event
        pl.http_json = fake_http_json

    # ---------- Engagement email tests ----------

    def test_day_3_trigger_sends_day_3_and_records(self):
        pilot = make_pilot(started_days_ago=3)
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(len(world.brevo_sends), 1)
        self.assertEqual(world.brevo_sends[0][0], "pilot-day-3")
        self.assertEqual(len(world.email_sends), 1)
        self.assertEqual(world.email_sends[0]["email_key"], "pilot-day-3")
        events = [e for e in world.marketing_events if e.get("event_type") == "pilot_day_3_sent"]
        self.assertEqual(len(events), 1)

    def test_day_3_replay_is_idempotent(self):
        pilot = make_pilot(started_days_ago=3)
        pl.process_pilot(pilot, FIXED_TODAY)
        pl.process_pilot(pilot, FIXED_TODAY)  # same day replay
        self.assertEqual(len(world.brevo_sends), 1, "second run must not resend")
        self.assertEqual(len(world.email_sends), 1)
        events = [e for e in world.marketing_events if e.get("event_type") == "pilot_day_3_sent"]
        self.assertEqual(len(events), 1)

    def test_day_7_trigger_sends_day_7(self):
        pilot = make_pilot(started_days_ago=7)
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends[0][0], "pilot-day-7")
        self.assertEqual(world.email_sends[0]["email_key"], "pilot-day-7")

    def test_day_12_trigger_sends_day_12(self):
        pilot = make_pilot(started_days_ago=12)
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends[0][0], "pilot-day-12")

    def test_pilot_younger_than_3_days_is_noop(self):
        pilot = make_pilot(started_days_ago=1)
        summary = pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends, [])
        self.assertIn("no-op", summary["actions"])

    # ---------- Day 14 convert path ----------

    def test_day_14_with_setup_intent_converts(self):
        pilot = make_pilot(started_days_ago=14, setup_intent=True, payment_method_added=True)
        pl.process_pilot(pilot, FIXED_TODAY)
        # Stripe called: GET customer + POST subscription
        stripe_methods = [(m, p) for m, p, _ in world.stripe_calls]
        self.assertIn(("GET", f"/v1/customers/{pilot['stripe_customer_id']}"), stripe_methods)
        self.assertIn(("POST", "/v1/subscriptions"), stripe_methods)
        # Subscription creation body included the price and customer
        sub_call = next(b for m, p, b in world.stripe_calls if p == "/v1/subscriptions")
        self.assertEqual(sub_call["customer"], pilot["stripe_customer_id"])
        self.assertEqual(sub_call["items"][0]["price"], pl.STRIPE_HVAC_STANDARD_PRICE_ID)
        # PATCH client_subscriptions to status=active, pilot_mode=false
        patch = next((p, b) for p, b in world.supabase_patches if "client_subscriptions" in p)
        self.assertEqual(patch[1]["status"], "active")
        self.assertFalse(patch[1]["pilot_mode"])
        self.assertEqual(patch[1]["stripe_subscription_id"], "sub_fake_xyz")
        # Email sent + marketing event
        self.assertEqual(world.brevo_sends[0][0], "pilot-converted")
        converted_events = [e for e in world.marketing_events if e.get("event_type") == "pilot_converted"]
        self.assertEqual(len(converted_events), 1)

    # ---------- Day 14 expire path ----------

    def test_day_14_without_setup_intent_expires(self):
        pilot = make_pilot(started_days_ago=14, setup_intent=False, payment_method_added=False)
        pl.process_pilot(pilot, FIXED_TODAY)
        # PATCH client_subscriptions: status='expired'
        patch = next((p, b) for p, b in world.supabase_patches if "client_subscriptions" in p)
        self.assertEqual(patch[1], {"status": "expired"})
        # Retell PATCH /update-agent/{id}
        self.assertTrue(any(m == "PATCH" and p.startswith("/update-agent/") for m, p, _ in world.retell_calls))
        retell_body = next(b for m, p, b in world.retell_calls if p.startswith("/update-agent/"))
        # Body shape: agent_level_dynamic_variables.pilot_expired == 'true'
        dv = retell_body.get("agent_level_dynamic_variables", {})
        self.assertEqual(dv.get("pilot_expired"), "true")
        # Brevo + marketing_event
        self.assertEqual(world.brevo_sends[0][0], "pilot-expired")
        expired_events = [e for e in world.marketing_events if e.get("event_type") == "pilot_expired"]
        self.assertEqual(len(expired_events), 1)

    # ---------- Winback tests ----------

    def test_day_16_expired_sends_winback_16(self):
        pilot = make_pilot(started_days_ago=16, status="expired")
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends[0][0], "pilot-winback-16")
        self.assertEqual(world.email_sends[0]["email_key"], "pilot-winback-16")
        events = [e for e in world.marketing_events if e.get("event_type") == "winback_day_16_sent"]
        self.assertEqual(len(events), 1)

    def test_day_30_expired_sends_winback_30(self):
        pilot = make_pilot(started_days_ago=30, status="expired")
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends[0][0], "pilot-winback-30")
        events = [e for e in world.marketing_events if e.get("event_type") == "winback_day_30_sent"]
        self.assertEqual(len(events), 1)

    def test_winback_replay_is_idempotent(self):
        pilot = make_pilot(started_days_ago=16, status="expired")
        pl.process_pilot(pilot, FIXED_TODAY)
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(len(world.brevo_sends), 1)

    # ---------- Edge cases ----------

    def test_pilot_at_200_minutes_still_follows_date_schedule(self):
        # Minute limit is n8n's responsibility — pilot_lifecycle only cares about dates.
        pilot = make_pilot(started_days_ago=3, minutes_used=200, minutes_allotted=200)
        pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends[0][0], "pilot-day-3")

    def test_expired_status_before_day_16_is_noop(self):
        pilot = make_pilot(started_days_ago=15, status="expired")
        summary = pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(world.brevo_sends, [])
        self.assertIn("no-op", summary["actions"])

    def test_dry_run_sends_nothing(self):
        pilot = make_pilot(started_days_ago=3)
        summary = pl.process_pilot(pilot, FIXED_TODAY, dry_run=True)
        self.assertEqual(world.brevo_sends, [])
        self.assertEqual(world.email_sends, [])
        self.assertTrue(any(a.startswith("dry:") for a in summary["actions"]))

    def test_missing_pilot_started_at_is_skipped(self):
        pilot = make_pilot(started_days_ago=3)
        pilot["pilot_started_at"] = None
        summary = pl.process_pilot(pilot, FIXED_TODAY)
        self.assertEqual(summary["action"], "skip_no_started_at")
        self.assertEqual(world.brevo_sends, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
