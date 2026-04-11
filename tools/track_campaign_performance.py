#!/usr/bin/env python3
"""
track_campaign_performance.py — Pull Brevo transactional stats and sync them
into campaign_results + refresh content_variants.score.

Usage:
  python tools/track_campaign_performance.py [--lookback-days N]

Dependencies:
  - stdlib only (urllib.request, json, os, sys, datetime, argparse)
  - SUPABASE_URL + SUPABASE_SERVICE_KEY in env (source .env.local)
  - Brevo API key fetched from syntharra_vault at runtime

Flow:
  1. Fetch SUPABASE_SERVICE_KEY from env.
  2. Fetch Brevo API key from syntharra_vault (service='Brevo', key_type='api_key').
  3. Pull marketing_campaigns rows where status='sent' AND sent_at >= now()-lookback_days.
  4. For each campaign, extract brevo_message_id from content_json.
  5. Fetch matching events from Brevo GET /v3/smtp/statistics/events.
  6. Upsert into campaign_results (idempotent: skip rows already recorded for
     this campaign+metric+source combination within the same day).
  7. Call update_variant_scores() to recompute content_variants.score.

Brevo note:
  Transactional email events live at GET /v3/smtp/statistics/events
  with query params: messageId, startDate, endDate, event (repeatable).
  Supported event values: requests, delivered, softBounces, hardBounces,
  clicked, unsubscribed, opened, loaded, reply, blocked, spam, invalid.
  We map: opened→opened, clicked→clicked, reply→replied, delivered→delivered.

Idempotency:
  campaign_results has no unique constraint intentionally — Brevo may surface
  the same open event twice if a recipient opens multiple times (each is a
  real event). We use a "already recorded today" guard per campaign+metric
  to avoid double-counting pure re-runs of this script within one day.
  Same-day re-runs are safe because we DELETE existing rows for the same
  campaign+metric+source before inserting fresh ones from Brevo.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def sb_request(base_url: str, service_key: str, method: str, path: str,
               params: dict = None, body: dict = None) -> list | dict:
    """Make a Supabase REST API request. Returns parsed JSON."""
    url = f"{base_url.rstrip('/')}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else []
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode() if exc.fp else ""
        print(f"[ERROR] Supabase {method} {path} → HTTP {exc.code}: {body_text}",
              file=sys.stderr)
        raise


def fetch_vault_key(base_url: str, service_key: str,
                    service_name: str, key_type: str) -> str:
    """Retrieve a credential from syntharra_vault."""
    rows = sb_request(base_url, service_key, "GET", "/rest/v1/syntharra_vault",
                      params={
                          "service_name": f"eq.{service_name}",
                          "key_type": f"eq.{key_type}",
                          "select": "key_value",
                      })
    if not rows:
        sys.exit(f"[FATAL] syntharra_vault: no row for service={service_name!r} "
                 f"key_type={key_type!r}")
    return rows[0]["key_value"]


# ---------------------------------------------------------------------------
# Brevo helpers
# ---------------------------------------------------------------------------

BREVO_BASE = "https://api.brevo.com/v3"

# Map Brevo event names → our campaign_results metric values
BREVO_EVENT_MAP = {
    "delivered": "delivered",
    "opened":    "opened",
    "loaded":    "opened",    # Brevo "loaded" = image pixel fired (proxy for open)
    "clicked":   "clicked",
    "reply":     "replied",
}


def brevo_request(brevo_key: str, path: str, params: dict = None) -> dict | list:
    """Make a Brevo API GET request. Returns parsed JSON."""
    url = f"{BREVO_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    req = urllib.request.Request(
        url,
        headers={
            "api-key": brevo_key,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode() if exc.fp else ""
        print(f"[ERROR] Brevo GET {path} → HTTP {exc.code}: {body_text}",
              file=sys.stderr)
        raise


def get_brevo_stats(brevo_key: str, campaign_message_ids: list[str],
                    start_date: str, end_date: str) -> list[dict]:
    """
    Fetch transactional email events from Brevo for a list of messageIds.

    Brevo /v3/smtp/statistics/events accepts one messageId at a time, so we
    loop. Returns a flat list of dicts:
      { message_id, event, date, email }

    start_date / end_date: "YYYY-MM-DD" strings (Brevo format).
    """
    all_events = []
    wanted_events = list(BREVO_EVENT_MAP.keys())

    for message_id in campaign_message_ids:
        if not message_id:
            continue
        params = {
            "messageId": message_id,
            "startDate": start_date,
            "endDate": end_date,
            "event": wanted_events,  # urllib encodes list as repeated params
            "limit": 500,
        }
        try:
            data = brevo_request(brevo_key, "/smtp/statistics/events", params)
            events = data.get("events", []) if isinstance(data, dict) else data
            for ev in events:
                all_events.append({
                    "message_id": message_id,
                    "event":      ev.get("event", ""),
                    "date":       ev.get("date", ""),
                    "email":      ev.get("email", ""),
                })
        except urllib.error.HTTPError:
            print(f"[WARN] Brevo: failed to fetch events for messageId={message_id}. "
                  "Skipping.", file=sys.stderr)
            continue

    return all_events


# ---------------------------------------------------------------------------
# Core update logic
# ---------------------------------------------------------------------------

def update_performance(sb_url: str, sb_key: str, brevo_key: str,
                       lookback_days: int = 7) -> None:
    """
    Main sync: fetch recent sent campaigns, pull Brevo stats, upsert results.
    """
    now_utc = datetime.now(timezone.utc)
    since = (now_utc - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = (now_utc - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    end_date = now_utc.strftime("%Y-%m-%d")
    today_prefix = now_utc.strftime("%Y-%m-%d")

    print(f"[INFO] Fetching campaigns sent since {since} (lookback={lookback_days}d)")

    # 1. Pull sent campaigns from Supabase
    campaigns = sb_request(
        sb_url, sb_key, "GET", "/rest/v1/marketing_campaigns",
        params={
            "status": "eq.sent",
            "sent_at": f"gte.{since}",
            "select": "id,type,variant_id,target,content_json,sent_at",
        }
    )
    if not campaigns:
        print("[INFO] No sent campaigns in the lookback window. Nothing to do.")
        return

    print(f"[INFO] Found {len(campaigns)} sent campaign(s) to process.")

    # 2. Build messageId → campaign_id mapping
    msg_id_to_campaign: dict[str, str] = {}
    for c in campaigns:
        msg_id = (c.get("content_json") or {}).get("brevo_message_id")
        if msg_id:
            msg_id_to_campaign[msg_id] = c["id"]

    if not msg_id_to_campaign:
        print("[WARN] No campaigns have a brevo_message_id in content_json. "
              "Skipping Brevo pull. "
              "Set content_json.brevo_message_id when recording sent campaigns.")
        return

    # 3. Fetch Brevo events
    print(f"[INFO] Fetching Brevo stats for {len(msg_id_to_campaign)} message ID(s) "
          f"({start_date} → {end_date})")
    events = get_brevo_stats(brevo_key, list(msg_id_to_campaign.keys()),
                             start_date, end_date)
    print(f"[INFO] Brevo returned {len(events)} event(s).")

    if not events:
        print("[INFO] No Brevo events found. Variant scores unchanged.")
        return

    # 4. Group events by campaign_id + metric
    # { campaign_id: { metric: count } }
    aggregated: dict[str, dict[str, int]] = {}
    for ev in events:
        cid = msg_id_to_campaign.get(ev["message_id"])
        if not cid:
            continue
        metric = BREVO_EVENT_MAP.get(ev["event"])
        if not metric:
            continue
        aggregated.setdefault(cid, {}).setdefault(metric, 0)
        aggregated[cid][metric] += 1

    # 5. Delete today's existing brevo_webhook rows for these campaigns, then insert
    #    fresh ones (idempotent re-run within the same day).
    campaign_ids_with_data = list(aggregated.keys())
    if campaign_ids_with_data:
        # Supabase REST: DELETE with IN filter
        # We use a loop to avoid URL length issues with large sets.
        for cid in campaign_ids_with_data:
            sb_request(
                sb_url, sb_key, "DELETE", "/rest/v1/campaign_results",
                params={
                    "campaign_id": f"eq.{cid}",
                    "source":      "eq.brevo_webhook",
                    "recorded_at": f"gte.{today_prefix}T00:00:00Z",
                }
            )

    # 6. Insert aggregated metric rows
    rows_to_insert = []
    for cid, metrics in aggregated.items():
        for metric, count in metrics.items():
            rows_to_insert.append({
                "campaign_id": cid,
                "metric":      metric,
                "value":       count,
                "recorded_at": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source":      "brevo_webhook",
            })

    if rows_to_insert:
        sb_request(sb_url, sb_key, "POST", "/rest/v1/campaign_results",
                   body=rows_to_insert)
        print(f"[INFO] Inserted {len(rows_to_insert)} campaign_results row(s).")
    else:
        print("[INFO] No metric rows to insert after aggregation.")

    # 7. Also ensure each campaign has a 'sent' row (value=1) if not already
    #    recorded — Brevo doesn't always fire a 'sent' event via the events API.
    sent_rows = []
    for cid in campaign_ids_with_data:
        existing = sb_request(
            sb_url, sb_key, "GET", "/rest/v1/campaign_results",
            params={
                "campaign_id": f"eq.{cid}",
                "metric":      "eq.sent",
                "select":      "id",
                "limit":       "1",
            }
        )
        if not existing:
            sent_rows.append({
                "campaign_id": cid,
                "metric":      "sent",
                "value":       1,
                "source":      "brevo_webhook",
            })
    if sent_rows:
        sb_request(sb_url, sb_key, "POST", "/rest/v1/campaign_results",
                   body=sent_rows)
        print(f"[INFO] Inserted {len(sent_rows)} 'sent' sentinel row(s).")


def update_variant_scores(sb_url: str, sb_key: str) -> None:
    """
    Recompute content_variants.score from aggregated campaign_results.

    Score formula: (reply_count + pilot_signup_count * 5) / NULLIF(send_count, 0)

    We pull all campaigns + their results, join to variants, aggregate, then
    PATCH each content_variants row. All in Python to stay stdlib-only.
    """
    print("[INFO] Recomputing variant scores...")

    # Pull all variants that have at least one campaign
    variants = sb_request(
        sb_url, sb_key, "GET", "/rest/v1/content_variants",
        params={"select": "id,send_count,open_count,reply_count,"
                          "click_count,engagement_count,pilot_signup_count,score"}
    )
    if not variants:
        print("[INFO] No content_variants rows found. Skipping score update.")
        return

    # Pull campaigns with variant_id set
    campaigns = sb_request(
        sb_url, sb_key, "GET", "/rest/v1/marketing_campaigns",
        params={
            "variant_id": "not.is.null",
            "select": "id,variant_id",
        }
    )
    # Map campaign_id → variant_id
    cid_to_vid: dict[str, str] = {c["id"]: c["variant_id"] for c in campaigns}

    if not cid_to_vid:
        print("[INFO] No campaigns have variant_id. Skipping score update.")
        return

    # Pull all campaign_results for these campaigns
    all_results = sb_request(
        sb_url, sb_key, "GET", "/rest/v1/campaign_results",
        params={
            "campaign_id": f"in.({','.join(cid_to_vid.keys())})",
            "select": "campaign_id,metric,value",
        }
    )

    # Aggregate per variant_id
    # { variant_id: { metric: total_value } }
    agg: dict[str, dict[str, float]] = {}
    for row in all_results:
        vid = cid_to_vid.get(row["campaign_id"])
        if not vid:
            continue
        agg.setdefault(vid, {})
        metric = row["metric"]
        agg[vid][metric] = agg[vid].get(metric, 0) + float(row["value"])

    # Update each variant
    updated = 0
    for variant in variants:
        vid = variant["id"]
        metrics = agg.get(vid, {})

        send_count         = int(metrics.get("sent", 0))
        open_count         = int(metrics.get("opened", 0))
        reply_count        = int(metrics.get("replied", 0))
        click_count        = int(metrics.get("clicked", 0))
        pilot_signup_count = int(metrics.get("pilot_signup", 0))
        # engagement = opens + clicks + replies (a broader signal)
        engagement_count   = open_count + click_count + reply_count

        # Score formula
        if send_count > 0:
            score = (reply_count + pilot_signup_count * 5) / send_count
        else:
            score = 0.0

        # Only write if something changed (avoid no-op writes)
        changed = (
            variant["send_count"]         != send_count
            or variant["open_count"]      != open_count
            or variant["reply_count"]     != reply_count
            or variant["click_count"]     != click_count
            or variant["engagement_count"] != engagement_count
            or variant["pilot_signup_count"] != pilot_signup_count
            or abs(float(variant["score"]) - score) > 1e-9
        )
        if not changed:
            continue

        sb_request(
            sb_url, sb_key, "PATCH", "/rest/v1/content_variants",
            params={"id": f"eq.{vid}"},
            body={
                "send_count":         send_count,
                "open_count":         open_count,
                "reply_count":        reply_count,
                "click_count":        click_count,
                "engagement_count":   engagement_count,
                "pilot_signup_count": pilot_signup_count,
                "score":              round(score, 6),
            }
        )
        updated += 1

    print(f"[INFO] Updated scores for {updated}/{len(variants)} variant(s).")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pull Brevo transactional stats → campaign_results → variant scores."
    )
    parser.add_argument(
        "--lookback-days", type=int, default=7,
        help="How many days back to fetch Brevo events (default: 7)"
    )
    args = parser.parse_args()

    # Read Supabase creds from env
    sb_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")
    if not sb_url or not sb_key:
        sys.exit("[FATAL] SUPABASE_URL + SUPABASE_SERVICE_KEY must be set. "
                 "Run: source .env.local")

    # Fetch Brevo API key from vault
    print("[INFO] Fetching Brevo API key from syntharra_vault...")
    brevo_key = fetch_vault_key(sb_url, sb_key, "Brevo", "api_key")
    print("[INFO] Brevo key retrieved.")

    # Run the two stages
    update_performance(sb_url, sb_key, brevo_key, lookback_days=args.lookback_days)
    update_variant_scores(sb_url, sb_key)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()
