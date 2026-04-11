#!/usr/bin/env python3
"""
marketing_digest.py — Weekly (or N-day) marketing funnel rollup for Syntharra.

Reads from Supabase (marketing_events + client_subscriptions) and an optional
local cold-outreach send-state file and produces a compact text / JSON / Slack
blocks summary of the funnel for the last N days:

    TOP of funnel   — organic traffic (marketing_events: page_view / scroll_depth /
                      cta_click / vsl_*_pct), grouped by asset_id
    MIDDLE          — pilot signups (client_subscriptions.status='pilot') +
                      cold outreach sends (leads/.send_state.json)
    BOTTOM          — paid conversions (status='active' with
                      payment_method_added_at within window)
    SUMMARY         — totals, week-over-week deltas, implied conversion rates,
                      back-of-envelope CAC

Strictly read-only. Python stdlib only (urllib.request + json).

Usage:
    source .env.local
    python tools/marketing_digest.py                  # default: --since 7d --output text
    python tools/marketing_digest.py --since 1d       # daily digest
    python tools/marketing_digest.py --since 30d
    python tools/marketing_digest.py --output json    # machine-readable
    python tools/marketing_digest.py --output slack   # Slack blocks JSON to stdout
    python tools/marketing_digest.py --post-to-slack  # actually POST to #daily-digest

Required env vars (from .env.local / syntharra_vault):
    SUPABASE_URL             https://hgheyqwnrcvwtgngqdnq.supabase.co
    SUPABASE_SERVICE_KEY     service_role JWT
    SLACK_BOT_TOKEN          required only for --post-to-slack

Schema notes (verified against supabase/schema_LIVE.md 2026-04-11):
  marketing_events:       created_at, event_type, asset_id, session_id,
                          utm_source, metadata (jsonb)
  client_subscriptions:   status, pilot_mode, created_at, payment_method_added_at,
                          first_touch_asset_id, last_touch_asset_id,
                          first_touch_utm (jsonb), last_touch_utm (jsonb)

The prompt described flat `first_touch_utm_source` / `last_touch_utm_source`
columns but the live schema stores UTMs as a single jsonb blob
(`first_touch_utm`, `last_touch_utm`). This tool reads the jsonb and extracts
`source` / `medium` / `campaign` on the Python side.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# RULES.md #41 — safe Unicode stdout on Windows consoles
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------

SLACK_DEFAULT_CHANNEL = "#daily-digest"

# Rough cost model for the CAC computation. These are back-of-envelope figures
# used only when real spend data is not available. Refine later by pulling from
# a cost ledger table if one gets built.
COST_PER_EMAIL_USD = 0.0004  # Brevo transactional cold-send blended rate


# --------------------------------------------------------------------------
# env / http
# --------------------------------------------------------------------------

def env(name: str, required: bool = True) -> str:
    v = os.environ.get(name, "")
    if required and not v:
        sys.exit(f"Missing env var: {name}")
    return v


def http_json(method: str, url: str, headers: dict, body=None, timeout: int = 30) -> tuple[int, object]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")[:500]
        except Exception:
            err_body = ""
        return e.code, {"error": err_body}
    except urllib.error.URLError as e:
        return 0, {"error": f"urlerror: {e}"}


# --------------------------------------------------------------------------
# Supabase helpers
# --------------------------------------------------------------------------

def sb_headers() -> dict:
    k = env("SUPABASE_SERVICE_KEY")
    return {
        "apikey": k,
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json",
    }


def sb_select(path: str) -> list[dict]:
    """GET a PostgREST path (starts with '/rest/v1/...'). Returns [] on failure."""
    url = env("SUPABASE_URL").rstrip("/") + path
    status, data = http_json("GET", url, sb_headers())
    if status != 200:
        # Do not crash the whole digest on a single query failure — we want a
        # best-effort rollup even if one section can't load.
        print(f"[warn] supabase query failed {status}: {path} {data}", file=sys.stderr)
        return []
    return data if isinstance(data, list) else []


# --------------------------------------------------------------------------
# window helpers
# --------------------------------------------------------------------------

_SINCE_RE = re.compile(r"^(\d+)([dh])$")


def parse_since(token: str) -> timedelta:
    """Accept '7d', '1d', '24h', '72h'. Default on failure = 7 days."""
    m = _SINCE_RE.match(token.strip().lower())
    if not m:
        sys.exit(f"--since must look like Nd or Nh (got: {token})")
    n, unit = int(m.group(1)), m.group(2)
    return timedelta(days=n) if unit == "d" else timedelta(hours=n)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def pct(num: float, denom: float) -> str:
    if denom <= 0:
        return "—"
    return f"{(num / denom) * 100:.1f}%"


def delta(cur: int, prev: int) -> str:
    if prev == 0 and cur == 0:
        return "—"
    if prev == 0:
        return f"+{cur} new"
    diff = cur - prev
    sign = "+" if diff >= 0 else ""
    pc = (diff / prev) * 100
    return f"{sign}{diff} ({sign}{pc:.0f}%)"


# --------------------------------------------------------------------------
# section fetchers
# --------------------------------------------------------------------------

def fetch_marketing_events(window_start: datetime, window_end: datetime) -> list[dict]:
    path = (
        "/rest/v1/marketing_events"
        f"?created_at=gte.{urllib.parse.quote(iso(window_start))}"
        f"&created_at=lt.{urllib.parse.quote(iso(window_end))}"
        "&select=event_type,asset_id,session_id,created_at"
        "&limit=10000"
    )
    return sb_select(path)


def fetch_new_pilots(window_start: datetime, window_end: datetime) -> list[dict]:
    path = (
        "/rest/v1/client_subscriptions"
        "?status=eq.pilot"
        f"&created_at=gte.{urllib.parse.quote(iso(window_start))}"
        f"&created_at=lt.{urllib.parse.quote(iso(window_end))}"
        "&select=agent_id,company_name,created_at,pilot_started_at,"
        "first_touch_asset_id,last_touch_asset_id,first_touch_utm,last_touch_utm"
        "&limit=1000"
    )
    return sb_select(path)


def fetch_new_conversions(window_start: datetime, window_end: datetime) -> list[dict]:
    path = (
        "/rest/v1/client_subscriptions"
        "?status=eq.active"
        f"&payment_method_added_at=gte.{urllib.parse.quote(iso(window_start))}"
        f"&payment_method_added_at=lt.{urllib.parse.quote(iso(window_end))}"
        "&select=agent_id,company_name,payment_method_added_at,"
        "first_touch_asset_id,last_touch_asset_id,first_touch_utm,last_touch_utm"
        "&limit=1000"
    )
    return sb_select(path)


# --------------------------------------------------------------------------
# aggregators
# --------------------------------------------------------------------------

def aggregate_traffic(events: list[dict]) -> dict:
    """Group marketing_events by (asset_id, event_type) and derive totals."""
    by_asset: dict[str, dict[str, int]] = {}
    totals: dict[str, int] = {}
    for e in events:
        et = (e.get("event_type") or "").lower()
        aid = e.get("asset_id") or "(none)"
        totals[et] = totals.get(et, 0) + 1
        slot = by_asset.setdefault(aid, {})
        slot[et] = slot.get(et, 0) + 1

    # Top pages by page_view
    top_pages = sorted(
        (
            {
                "asset_id": aid,
                "page_views": counts.get("page_view", 0),
                "cta_clicks": counts.get("cta_click", 0),
                "scroll_depth": counts.get("scroll_depth", 0),
                "vsl_events": sum(v for k, v in counts.items() if k.startswith("vsl_")),
                "ctr": (
                    counts.get("cta_click", 0) / counts.get("page_view", 1)
                    if counts.get("page_view", 0) > 0
                    else 0.0
                ),
            }
            for aid, counts in by_asset.items()
            if counts.get("page_view", 0) > 0
        ),
        key=lambda r: (-r["page_views"], r["asset_id"]),
    )

    return {
        "events_total": len(events),
        "by_type": totals,
        "page_views": totals.get("page_view", 0),
        "cta_clicks": totals.get("cta_click", 0),
        "scroll_depth_events": totals.get("scroll_depth", 0),
        "vsl_events": sum(v for k, v in totals.items() if k.startswith("vsl_")),
        "top_pages": top_pages[:5],
    }


def _utm_source(row: dict, touch: str) -> str:
    """Extract utm_source from the first_touch_utm / last_touch_utm jsonb blob."""
    blob = row.get(f"{touch}_touch_utm") or {}
    if isinstance(blob, str):
        try:
            blob = json.loads(blob)
        except Exception:
            blob = {}
    if isinstance(blob, dict):
        return blob.get("source") or blob.get("utm_source") or "(direct)"
    return "(direct)"


def aggregate_attribution(rows: list[dict]) -> list[dict]:
    """Bucket subscriptions by (first_touch_asset_id, first_touch_utm_source, last_touch_asset_id)."""
    buckets: dict[tuple, int] = {}
    for r in rows:
        key = (
            r.get("first_touch_asset_id") or "(none)",
            _utm_source(r, "first"),
            r.get("last_touch_asset_id") or "(none)",
        )
        buckets[key] = buckets.get(key, 0) + 1
    out = [
        {
            "first_touch_asset_id": k[0],
            "first_touch_utm_source": k[1],
            "last_touch_asset_id": k[2],
            "count": v,
        }
        for k, v in buckets.items()
    ]
    out.sort(key=lambda x: -x["count"])
    return out


# --------------------------------------------------------------------------
# cold outreach state file
# --------------------------------------------------------------------------

STATE_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "leads",
    ".send_state.json",
)


def aggregate_outreach(window_start: datetime) -> dict:
    """Scan leads/.send_state.json for sends newer than window_start.

    The state file is written by tools/send_cold_outreach.py and is a flat
    dict of `{email: {step, last_sent, company, replied}}`. It does NOT tag
    entries with a per-tool origin (cold_outreach vs affiliate_outreach),
    so the rollup reports the total send count only. Leaves a hook for a
    future `source` field if send_cold_outreach grows one.
    """
    if not os.path.exists(STATE_FILE_PATH):
        return {"exists": False, "total_sends": 0, "by_step": {}, "by_source": {}}

    try:
        with open(STATE_FILE_PATH, encoding="utf-8") as f:
            state = json.load(f)
    except Exception as exc:
        return {"exists": True, "error": str(exc), "total_sends": 0, "by_step": {}, "by_source": {}}

    total = 0
    by_step: dict[str, int] = {}
    by_source: dict[str, int] = {}
    replied = 0
    for email, meta in state.items():
        if not isinstance(meta, dict):
            continue
        last_sent = meta.get("last_sent")
        if not last_sent:
            continue
        try:
            ts = datetime.fromisoformat(last_sent.replace("Z", "+00:00"))
        except Exception:
            continue
        if ts < window_start:
            continue
        total += 1
        step_key = f"step_{meta.get('step', 1)}"
        by_step[step_key] = by_step.get(step_key, 0) + 1
        source = meta.get("source", "cold_outreach")
        by_source[source] = by_source.get(source, 0) + 1
        if meta.get("replied"):
            replied += 1

    return {
        "exists": True,
        "total_sends": total,
        "total_in_file": len(state),
        "by_step": by_step,
        "by_source": by_source,
        "replied": replied,
    }


# --------------------------------------------------------------------------
# master rollup
# --------------------------------------------------------------------------

def build_digest(window_days: int) -> dict:
    now = datetime.now(timezone.utc)
    window = timedelta(days=window_days)
    current_start = now - window
    prior_start = current_start - window
    prior_end = current_start

    # --- current window ---
    events = fetch_marketing_events(current_start, now)
    traffic = aggregate_traffic(events)

    pilots = fetch_new_pilots(current_start, now)
    pilot_attribution = aggregate_attribution(pilots)

    conversions = fetch_new_conversions(current_start, now)
    conversion_attribution = aggregate_attribution(conversions)

    outreach = aggregate_outreach(current_start)

    # --- prior window (just totals for deltas) ---
    prior_events = fetch_marketing_events(prior_start, prior_end)
    prior_traffic = aggregate_traffic(prior_events)
    prior_pilots = fetch_new_pilots(prior_start, prior_end)
    prior_conversions = fetch_new_conversions(prior_start, prior_end)

    # --- cost + CAC back-of-envelope ---
    est_cost_usd = outreach.get("total_sends", 0) * COST_PER_EMAIL_USD
    cac = None
    if len(conversions) > 0 and est_cost_usd > 0:
        cac = est_cost_usd / len(conversions)

    return {
        "generated_at": now.isoformat(),
        "window_days": window_days,
        "window_start": current_start.isoformat(),
        "window_end": now.isoformat(),
        "traffic": traffic,
        "pilots": {
            "count": len(pilots),
            "prev_count": len(prior_pilots),
            "attribution": pilot_attribution,
            "rows": pilots,
        },
        "outreach": outreach,
        "conversions": {
            "count": len(conversions),
            "prev_count": len(prior_conversions),
            "attribution": conversion_attribution,
            "rows": conversions,
        },
        "summary": {
            "page_views": traffic["page_views"],
            "prev_page_views": prior_traffic["page_views"],
            "pilots": len(pilots),
            "paid": len(conversions),
            "view_to_pilot_rate": pct(len(pilots), traffic["page_views"]),
            "pilot_to_paid_rate": pct(len(conversions), len(pilots)),
            "est_cost_usd": round(est_cost_usd, 2),
            "cac_usd": round(cac, 2) if cac is not None else None,
        },
    }


# --------------------------------------------------------------------------
# text renderer
# --------------------------------------------------------------------------

BAR = "=" * 47


def _fmt_week_label(digest: dict) -> str:
    start = datetime.fromisoformat(digest["window_start"])
    end = datetime.fromisoformat(digest["window_end"])
    # "Apr 5-11 2026" style
    if start.month == end.month:
        return f"{start.strftime('%b %d')}–{end.strftime('%d %Y')}"
    return f"{start.strftime('%b %d')}–{end.strftime('%b %d %Y')}"


def render_text(digest: dict) -> str:
    t = digest["traffic"]
    p = digest["pilots"]
    o = digest["outreach"]
    c = digest["conversions"]
    s = digest["summary"]

    next_actions: list[str] = []

    lines: list[str] = []
    lines.append(BAR)
    lines.append(f"Syntharra Marketing Digest — Week of {_fmt_week_label(digest)}")
    lines.append(BAR)
    lines.append("")

    # --- TOP: traffic ---
    lines.append(f"TOP OF FUNNEL — Organic Traffic (last {digest['window_days']}d)")
    pv_delta = delta(t["page_views"], s["prev_page_views"])
    ctr = pct(t["cta_clicks"], t["page_views"])
    lines.append(f"  Total page views: {t['page_views']:<20} (vs {s['prev_page_views']} prior, {pv_delta})")
    lines.append(f"  Total CTA clicks: {t['cta_clicks']:<20} (CTR: {ctr})")
    lines.append(f"  Scroll-depth events: {t['scroll_depth_events']}")
    lines.append(f"  VSL play events: {t['vsl_events']}")
    lines.append("")
    lines.append("  Top 5 pages by traffic:")
    if not t["top_pages"]:
        lines.append(
            "    (no traffic yet — marketing-tracker.js not firing OR pages not indexed)"
        )
        next_actions.append(
            "No new traffic — verify marketing-tracker.js is firing on live pages"
        )
    else:
        for page in t["top_pages"]:
            ctr_str = pct(page["cta_clicks"], page["page_views"])
            lines.append(
                f"    {page['asset_id'][:40]:<40}  "
                f"pv={page['page_views']:<4}  clicks={page['cta_clicks']:<3}  ctr={ctr_str}"
            )
    lines.append("")

    # --- MIDDLE: cold outreach ---
    lines.append(f"MIDDLE OF FUNNEL — Cold Outreach (last {digest['window_days']}d)")
    if not o.get("exists"):
        lines.append("  No send state file found — cold outreach not yet run.")
        next_actions.append(
            "No cold outreach sent yet — first batch recommended (see tools/send_cold_outreach.py)"
        )
    elif o.get("error"):
        lines.append(f"  [warn] could not read send state: {o.get('error')}")
    else:
        lines.append(
            f"  Sends in window: {o['total_sends']}  "
            f"(total tracked in state file: {o.get('total_in_file', 0)})"
        )
        if o.get("replied"):
            lines.append(f"  Replies: {o['replied']}")
        if o["by_step"]:
            steps = ", ".join(f"{k}={v}" for k, v in sorted(o["by_step"].items()))
            lines.append(f"  By step: {steps}")
        if o["by_source"]:
            sources = ", ".join(f"{k}={v}" for k, v in sorted(o["by_source"].items()))
            lines.append(f"  By source: {sources}")
        if o["total_sends"] == 0:
            next_actions.append(
                "No outreach sends in window — reactivate cold sequence if campaigns are live"
            )
    lines.append("")

    # --- MIDDLE: pilots ---
    lines.append(f"MIDDLE OF FUNNEL — Pilot Signups (last {digest['window_days']}d)")
    pilot_delta = delta(p["count"], p["prev_count"])
    lines.append(f"  New pilots: {p['count']:<20} (vs {p['prev_count']} prior, {pilot_delta})")
    if p["attribution"]:
        lines.append("  Attribution:")
        for row in p["attribution"][:10]:
            lines.append(
                f"    first={row['first_touch_asset_id'][:30]:<30}  "
                f"src={row['first_touch_utm_source'][:15]:<15}  "
                f"last={row['last_touch_asset_id'][:30]:<30}  "
                f"n={row['count']}"
            )
    else:
        lines.append("  (no pilots yet)")
        if p["prev_count"] == 0:
            next_actions.append(
                "Zero pilot signups this week — top of funnel not converting"
            )
    lines.append("")

    # --- BOTTOM: conversions ---
    lines.append(f"BOTTOM OF FUNNEL — Paid Conversions (last {digest['window_days']}d)")
    conv_delta = delta(c["count"], c["prev_count"])
    lines.append(f"  Converted: {c['count']:<20} (vs {c['prev_count']} prior, {conv_delta})")
    if c["attribution"]:
        lines.append("  Attribution:")
        for row in c["attribution"][:10]:
            lines.append(
                f"    first={row['first_touch_asset_id'][:30]:<30}  "
                f"src={row['first_touch_utm_source'][:15]:<15}  "
                f"last={row['last_touch_asset_id'][:30]:<30}  "
                f"n={row['count']}"
            )
    if s["cac_usd"] is not None:
        lines.append(f"  Week CAC: ${s['cac_usd']:.2f}   (est spend ${s['est_cost_usd']:.2f} / {c['count']} paid)")
    else:
        if s["est_cost_usd"] > 0:
            lines.append(
                f"  Week CAC: — (spend ${s['est_cost_usd']:.2f}, 0 conversions)"
            )
        else:
            lines.append("  Week CAC: — (no spend / no conversions)")
    lines.append("")

    # --- SUMMARY ---
    lines.append("SUMMARY")
    lines.append(f"  Traffic → Pilot rate : {s['view_to_pilot_rate']}  ({s['pilots']} / {s['page_views']})")
    lines.append(f"  Pilot → Paid rate    : {s['pilot_to_paid_rate']}  ({s['paid']} / {s['pilots']})")
    lines.append("")

    # --- NEXT ACTIONS ---
    if next_actions:
        lines.append("NEXT ACTIONS")
        for a in next_actions:
            lines.append(f"  \u30fb {a}")
        lines.append("")

    lines.append(BAR)

    return "\n".join(lines)


# --------------------------------------------------------------------------
# slack blocks renderer
# --------------------------------------------------------------------------

def render_slack_blocks(digest: dict) -> dict:
    t = digest["traffic"]
    p = digest["pilots"]
    o = digest["outreach"]
    c = digest["conversions"]
    s = digest["summary"]

    header_text = f"Marketing Digest — {_fmt_week_label(digest)}"
    fallback = (
        f"Traffic {t['page_views']} pv · Pilots {p['count']} · "
        f"Paid {c['count']} · CAC "
        f"{'$' + format(s['cac_usd'], '.2f') if s['cac_usd'] is not None else '—'}"
    )

    fields = [
        {"type": "mrkdwn", "text": f"*Page views*\n{t['page_views']}  ({delta(t['page_views'], s['prev_page_views'])})"},
        {"type": "mrkdwn", "text": f"*CTA clicks*\n{t['cta_clicks']}  ({pct(t['cta_clicks'], t['page_views'])})"},
        {"type": "mrkdwn", "text": f"*New pilots*\n{p['count']}  ({delta(p['count'], p['prev_count'])})"},
        {"type": "mrkdwn", "text": f"*Paid conversions*\n{c['count']}  ({delta(c['count'], c['prev_count'])})"},
        {"type": "mrkdwn", "text": f"*View→Pilot*\n{s['view_to_pilot_rate']}"},
        {"type": "mrkdwn", "text": f"*Pilot→Paid*\n{s['pilot_to_paid_rate']}"},
    ]

    top_pages_text = (
        "\n".join(
            f"• `{row['asset_id'][:40]}` — {row['page_views']} pv, {row['cta_clicks']} clicks ({pct(row['cta_clicks'], row['page_views'])})"
            for row in t["top_pages"]
        )
        or "_(no traffic yet — marketing-tracker.js not firing OR pages not indexed)_"
    )

    outreach_text: str
    if not o.get("exists"):
        outreach_text = "_No send state file — cold outreach not yet run._"
    elif o.get("error"):
        outreach_text = f"_warn: could not read send state: {o.get('error')}_"
    else:
        steps_str = ", ".join(f"{k}={v}" for k, v in sorted(o.get("by_step", {}).items())) or "—"
        outreach_text = (
            f"Sends in window: *{o['total_sends']}*  ·  replies: *{o.get('replied', 0)}*\n"
            f"By step: {steps_str}"
        )

    cac_text = (
        f"*Est spend:* ${s['est_cost_usd']:.2f}  ·  "
        + (f"*CAC:* ${s['cac_usd']:.2f}" if s["cac_usd"] is not None else "*CAC:* —")
    )

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": header_text, "emoji": True}},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Syntharra marketing funnel · window: {digest['window_days']}d",
                }
            ],
        },
        {"type": "divider"},
        {"type": "section", "fields": fields},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Top pages by traffic*\n" + top_pages_text}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Cold outreach*\n" + outreach_text}},
        {"type": "section", "text": {"type": "mrkdwn", "text": cac_text}},
    ]

    return {"text": fallback, "blocks": blocks}


# --------------------------------------------------------------------------
# slack posting
# --------------------------------------------------------------------------

def post_to_slack(payload: dict, channel: str) -> tuple[int, object]:
    token = env("SLACK_BOT_TOKEN")
    body = {"channel": channel, **payload}
    return http_json(
        "POST",
        "https://slack.com/api/chat.postMessage",
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        body,
    )


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Weekly marketing funnel rollup for Syntharra"
    )
    ap.add_argument(
        "--since",
        default="7d",
        help="Window size: Nd or Nh (default: 7d)",
    )
    ap.add_argument(
        "--output",
        choices=("text", "json", "slack"),
        default="text",
        help="Output format (default: text)",
    )
    ap.add_argument(
        "--post-to-slack",
        action="store_true",
        help=f"POST the digest to Slack (default channel {SLACK_DEFAULT_CHANNEL})",
    )
    ap.add_argument(
        "--slack-channel",
        default=SLACK_DEFAULT_CHANNEL,
        help=f"Slack channel for --post-to-slack (default: {SLACK_DEFAULT_CHANNEL})",
    )
    args = ap.parse_args()

    window = parse_since(args.since)
    # Normalize to integer days for display; 1h windows are edge-case.
    window_days = max(1, int(round(window.total_seconds() / 86400)))

    digest = build_digest(window_days)

    if args.post_to_slack:
        payload = render_slack_blocks(digest)
        status, data = post_to_slack(payload, args.slack_channel)
        ok = status == 200 and isinstance(data, dict) and data.get("ok")
        print(
            f"[slack] channel={args.slack_channel} status={status} ok={ok}",
            file=sys.stderr,
        )
        if not ok:
            print(f"[slack] response: {data}", file=sys.stderr)
            return 1

    if args.output == "text":
        print(render_text(digest))
    elif args.output == "json":
        print(json.dumps(digest, indent=2, default=str))
    elif args.output == "slack":
        print(json.dumps(render_slack_blocks(digest), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
