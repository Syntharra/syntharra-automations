#!/usr/bin/env python3
"""
marketing_brain.py — Syntharra autonomous marketing orchestrator.

Weekly cron (Monday 08:00 UTC) that runs a full 5-phase cycle:
  Phase 1 — REVIEW   : last week's performance from Supabase
  Phase 2 — PLAN     : generate cold email, Reddit, LinkedIn, short-form plans
  Phase 3 — PROPOSE  : post plan to #marketing-team, wait for Dan's 'go'
  Phase 4 — EXECUTE  : run the approved plan
  Phase 5 — TRACK    : log everything to marketing_campaigns

Usage:
  source .env.local
  python tools/marketing_brain.py              # full weekly cycle
  python tools/marketing_brain.py --dry-run    # show plan, do not send anything
  python tools/marketing_brain.py --force-execute  # skip approval wait
  python tools/marketing_brain.py --review-only    # show last week's perf only

Requires env: SUPABASE_URL, SUPABASE_SERVICE_KEY
Vault keys fetched at runtime: Slack/bot_token, Brevo/api_key,
  Reddit/client_id + client_secret + refresh_token, LinkedIn/access_token
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# Add tools/ dir to sys.path so we can import sibling helpers
# (content_preview_mode) regardless of whether this script is run from
# repo root or the tools/ directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_preview_mode import is_cold_email_enabled  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPABASE_HOST = "hgheyqwnrcvwtgngqdnq.supabase.co"
SLACK_CHANNEL = "#marketing-team"

# Priority city rotation (used when no performance data yet)
CITY_PRIORITY_LIST = [
    {"city": "Phoenix", "state": "AZ"},
    {"city": "Houston", "state": "TX"},
    {"city": "Tampa", "state": "FL"},
    {"city": "Dallas", "state": "TX"},
    {"city": "Atlanta", "state": "GA"},
    {"city": "Las Vegas", "state": "NV"},
    {"city": "Orlando", "state": "FL"},
    {"city": "Austin", "state": "TX"},
    {"city": "Miami", "state": "FL"},
    {"city": "Nashville", "state": "TN"},
]

# Default subject line variants (seeded before we have AB data)
DEFAULT_SUBJECT_VARIANTS = [
    "partnership_idea_v2",
    "missed_call_cost_v1",
    "after_hours_growth_v1",
]

# ---------------------------------------------------------------------------
# Content templates
# ---------------------------------------------------------------------------

REDDIT_VARIANTS = {
    "missed_call_story_v1": {
        "title": "Question for HVAC shop owners — how do you handle the 2am emergency call?",
        "body": (
            "Running a small HVAC shop and the 2am calls have been killing me. "
            "Last Tuesday I missed one while I was asleep — turned out to be a "
            "restaurant with a walk-in cooler going down. They went with the "
            "competitor who picked up.\n\n"
            "I've been looking at a few options: hiring an answering service "
            "($300-500/mo, hit-or-miss quality), forwarding to my cell every night "
            "(burned out in 6 weeks), or trying an AI receptionist.\n\n"
            "What do you guys do? Has anyone found something that actually works "
            "without costing a fortune?\n\n"
            "---\n"
            "*Full disclosure: I ended up trying Syntharra after a few months of "
            "testing options — happy to share what I found if anyone's curious.*"
        ),
        "subreddit": "HVAC",
    },
    "cost_calculator_v1": {
        "title": "I ran the numbers on what missed after-hours calls cost my shop last year. It was embarrassing.",
        "body": (
            "Did this exercise recently and wanted to share because I think most "
            "of us underestimate the real cost.\n\n"
            "Average emergency service call: ~$400-600 revenue\n"
            "Average maintenance plan upsell rate from emergency: 30%\n"
            "Maintenance plan value: ~$2,400/year\n\n"
            "So each missed emergency call isn't $500. It's potentially $1,200+ "
            "when you factor in the lost maintenance contract.\n\n"
            "I was missing ~3-4 calls/month after hours. That's $50K+ in annual "
            "revenue walking out the door.\n\n"
            "Has anyone else done this math? What did you find? How do you handle "
            "after-hours coverage?"
        ),
        "subreddit": "Contractor",
    },
    "competitor_question_v1": {
        "title": "Has anyone compared different answering services for HVAC? Looking at a few options",
        "body": (
            "Doing due diligence on after-hours coverage options. Currently looking at:\n\n"
            "- Traditional answering services (Ruby, etc.) — ~$300-500/mo\n"
            "- Scheduling software with voicemail — often callers just hang up\n"
            "- AI receptionists (Syntharra, others) — ~$700/mo but supposedly handles "
            "triage and booking automatically\n"
            "- Just using an on-call rotation with my techs\n\n"
            "Anyone have real experience with any of these? Especially interested in "
            "how they handle the 'is this actually an emergency or can it wait until "
            "Monday' triage conversation.\n\n"
            "Budget isn't the main concern — I want something that converts callers "
            "to booked jobs, not just takes a message."
        ),
        "subreddit": "hvacadvice",
    },
}

LINKEDIN_VARIANTS = {
    "owner_operator_pain_v1": {
        "text": (
            "The HVAC owner who ran out of his own birthday party to take a service call.\n\n"
            "True story from a contractor I spoke with last month.\n\n"
            "It was a Saturday night. His wife's surprise party for him. Forty people. "
            "His phone rang — unknown number, 9pm. He stepped outside 'for two minutes'.\n\n"
            "The call was real. Walk-in cooler at a diner. He coordinated the dispatch, "
            "handled the emergency, got back inside an hour later.\n\n"
            "He told me he doesn't regret taking the call. He regrets that he had to.\n\n"
            "There's a version of running an HVAC business where you're not the "
            "24/7 answering service. Where the phone gets picked up — by something "
            "that actually knows what a refrigerant leak sounds like versus a "
            "thermostat that needs a battery.\n\n"
            "That's what we built at Syntharra.\n\n"
            "If you run an HVAC shop and the after-hours calls are eating you alive, "
            "I'd love to show you what it looks like. DM me.\n\n"
            "#HVAC #SmallBusiness #Entrepreneurship"
        ),
    },
    "ai_receptionist_explainer_v1": {
        "text": (
            "What if your phone never went to voicemail again?\n\n"
            "Not forwarded to an answering service that reads from a script.\n"
            "Not a chatbot that says 'please hold'.\n\n"
            "An AI that:\n"
            "✓ Answers in under 3 rings, 24/7\n"
            "✓ Asks the right triage questions (refrigerant leak vs. thermostat issue)\n"
            "✓ Books the appointment directly in your scheduling system\n"
            "✓ Sends the customer a confirmation text\n"
            "✓ Texts you a summary so you wake up to booked jobs, not voicemails\n\n"
            "The average HVAC contractor misses 3-5 after-hours calls per month.\n"
            "At $500-600 average job value + maintenance plan conversions, "
            "that's $30,000-50,000 walking out the door every year.\n\n"
            "We built Syntharra specifically for HVAC. One flat price: $697/month.\n"
            "No per-call fees. No upsells. Just a phone that always gets answered.\n\n"
            "Curious what it sounds like? Drop a comment or DM me.\n\n"
            "#HVAC #AIReceptionist #ContractorLife #SmallBusiness"
        ),
    },
}

SHORT_FORM_VARIANTS = {
    "birthday_party_hook": {
        "hook": "I ran out of my own birthday party for a service call. Then I built this.",
        "script": (
            "[Hook — 0-3s]\n"
            "I ran out of my own birthday party to take an HVAC service call.\n\n"
            "[Problem — 3-10s]\n"
            "Show of hands: how many HVAC owners have missed a family event "
            "because your phone rang?\n\n"
            "[Solution demo — 10-25s]\n"
            "Now I have this. [demo: phone rings, AI answers, 'Hi, this is Sarah "
            "with Phoenix Heating and Cooling, how can I help you tonight?'] "
            "It handles triage, books the job, texts me a summary.\n\n"
            "[CTA — 25-30s]\n"
            "Link in bio to hear it live. $697/month, HVAC specific."
        ),
        "platform": "TikTok/Reels",
    },
    "2am_call_hook": {
        "hook": "It's 2am. Your AC breaks. You call the first 3 HVAC guys on Google. Which one do you hire?",
        "script": (
            "[Hook — 0-3s]\n"
            "It's 2am. Your AC breaks. You call the first 3 HVAC guys on Google.\n\n"
            "[Answer — 3-8s]\n"
            "The one who picks up. Every time.\n\n"
            "[Proof — 8-20s]\n"
            "80% of callers who get voicemail call the next number on the list. "
            "They don't leave a message. They don't wait until morning. "
            "They hire your competitor who answered.\n\n"
            "[Demo — 20-28s]\n"
            "[Show phone call being answered by AI] That's Syntharra. "
            "AI receptionist, built for HVAC.\n\n"
            "[CTA — 28-30s]\n"
            "Link in bio."
        ),
        "platform": "TikTok/Reels",
    },
    "math_hook": {
        "hook": "How much does one missed HVAC emergency call cost you? Here's the math.",
        "script": (
            "[Hook — 0-3s]\n"
            "How much does one missed HVAC emergency call actually cost?\n\n"
            "[Math — 3-20s]\n"
            "Most people say $500. Here's the real number.\n"
            "Emergency call: $500 revenue.\n"
            "Maintenance plan conversion rate: 30%.\n"
            "Maintenance plan value: $2,400/year.\n"
            "Real cost of that missed call: $1,200.\n"
            "Missing 3 per month: $43,000 per year.\n\n"
            "[Solution — 20-28s]\n"
            "Syntharra answers every call, 24/7, for $697/month. "
            "That's $8,364/year to stop losing $43,000.\n\n"
            "[CTA — 28-30s]\n"
            "The math writes itself. Link in bio."
        ),
        "platform": "TikTok/Reels",
    },
}

# ---------------------------------------------------------------------------
# Vault / Supabase helpers
# ---------------------------------------------------------------------------


def get_sb_credentials():
    """Return (base_url, service_key) from environment."""
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        sys.exit("SUPABASE_URL + SUPABASE_SERVICE_KEY must be set (source .env.local)")
    return url, key


def fetch_vault(service_name: str, key_type: str) -> str | None:
    """Fetch a credential from syntharra_vault. Returns None if not found."""
    base_url, service_key = get_sb_credentials()
    qs = urllib.parse.urlencode({
        "service_name": f"eq.{service_name}",
        "key_type": f"eq.{key_type}",
        "select": "key_value",
    })
    req = urllib.request.Request(
        f"{base_url}/rest/v1/syntharra_vault?{qs}",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            rows = json.loads(resp.read().decode())
        if rows:
            return rows[0]["key_value"]
    except Exception as exc:
        print(f"[WARN] vault fetch failed ({service_name}/{key_type}): {exc}", file=sys.stderr)
    return None


def sb_get(table: str, params: dict, sb_key: str) -> list:
    """Generic Supabase REST GET."""
    base_url, _ = get_sb_credentials()
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{base_url}/rest/v1/{table}?{qs}",
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"[WARN] sb_get {table} failed: {exc}", file=sys.stderr)
        return []


def sb_post(table: str, payload: dict, sb_key: str) -> dict | None:
    """Generic Supabase REST POST (insert)."""
    base_url, _ = get_sb_credentials()
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}/rest/v1/{table}",
        data=data,
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"[WARN] sb_post {table} failed: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Blog publisher trigger + run logger
# ---------------------------------------------------------------------------

N8N_BASE = "https://n8n.syntharra.com"
BLOG_PUBLISHER_WF_ID = "j8hExewOREmRp3Oq"


def trigger_n8n_blog_publisher() -> bool:
    """
    Trigger one blog post publish via the n8n Blog Auto-Publisher workflow.
    Calls POST /api/v1/workflows/{id}/run on the n8n Railway instance.
    Returns True on success, False on failure.
    Requires n8n Railway api_key in syntharra_vault.
    """
    n8n_key = fetch_vault("n8n Railway", "api_key")
    if not n8n_key:
        print("  [WARN] n8n api_key not in vault — blog trigger skipped", file=sys.stderr)
        return False
    url = f"{N8N_BASE}/api/v1/workflows/{BLOG_PUBLISHER_WF_ID}/run"
    req = urllib.request.Request(
        url, data=b"{}", method="POST",
        headers={"X-N8N-API-KEY": n8n_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            exec_id = result.get("executionId") or result.get("data", {}).get("executionId")
            print(f"  [Blog] Triggered blog publisher — execution {exec_id}")
            return True
    except Exception as exc:
        print(f"  [WARN] Blog publisher trigger failed: {exc}", file=sys.stderr)
        return False


def log_brain_run(
    run_at: str,
    status: str,
    plan: dict,
    results: list,
    sb_key: str,
) -> None:
    """
    Write a summary row to marketing_brain_log in Supabase.
    Table columns: run_at, status, plan (jsonb), results (jsonb).
    Silently skips if the table doesn't exist yet.
    """
    row = {
        "run_at": run_at,
        "status": status,
        "plan": json.dumps(plan),
        "results": json.dumps(results),
    }
    result = sb_post("marketing_brain_log", row, sb_key)
    if result and isinstance(result, list) and result:
        print(f"  [Log] Run logged → id={result[0].get('id')}")
    else:
        print("  [Log] marketing_brain_log write skipped (table may not exist yet)")


# ---------------------------------------------------------------------------
# Phase 1 — REVIEW
# ---------------------------------------------------------------------------


def get_top_intelligence(sb_key: str, limit: int = 10) -> list[dict]:
    """
    Read top-confidence rows from marketing_intelligence written by research_agent.py.
    Returns a list of findings sorted by confidence desc, capped at `limit`.
    Gracefully returns [] if the table doesn't exist or has no rows yet.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    rows = sb_get("marketing_intelligence", {
        "created_at": f"gte.{cutoff}",
        "confidence": "gte.0.6",
        "select": "source,title,url,hook,angle,confidence,view_count",
        "order": "confidence.desc",
        "limit": str(limit),
    }, sb_key)
    return rows if isinstance(rows, list) else []


def get_last_week_performance(sb_key: str) -> dict:
    """
    Read marketing_campaigns + campaign_results for last 7 days.
    Returns a dict with per-city and per-variant metrics.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    campaigns = sb_get("marketing_campaigns", {
        "created_at": f"gte.{cutoff}",
        "select": "id,city,state,channel,subject_variant,status,created_at",
    }, sb_key)

    results = sb_get("campaign_results", {
        "campaign_id": f"in.({','.join(str(c['id']) for c in campaigns)})" if campaigns else "is.null",
        "select": "campaign_id,opens,replies,clicks,sent_at",
    }, sb_key) if campaigns else []

    # Index results by campaign_id
    results_by_campaign: dict[str, dict] = {}
    for r in results:
        results_by_campaign[r["campaign_id"]] = r

    # Aggregate by city
    city_stats: dict[str, dict] = {}
    variant_stats: dict[str, dict] = {}

    for c in campaigns:
        city_key = f"{c.get('city', 'Unknown')}, {c.get('state', '')}"
        if city_key not in city_stats:
            city_stats[city_key] = {"sent": 0, "opens": 0, "replies": 0, "clicks": 0, "campaigns": []}
        city_stats[city_key]["campaigns"].append(c["id"])

        r = results_by_campaign.get(c["id"], {})
        city_stats[city_key]["sent"] += 1
        city_stats[city_key]["opens"] += r.get("opens", 0)
        city_stats[city_key]["replies"] += r.get("replies", 0)
        city_stats[city_key]["clicks"] += r.get("clicks", 0)

        sv = c.get("subject_variant", "unknown")
        if sv not in variant_stats:
            variant_stats[sv] = {"sent": 0, "opens": 0, "replies": 0}
        variant_stats[sv]["sent"] += 1
        variant_stats[sv]["opens"] += r.get("opens", 0)
        variant_stats[sv]["replies"] += r.get("replies", 0)

    # Compute rates
    for city, s in city_stats.items():
        s["open_rate"] = round(s["opens"] / s["sent"], 3) if s["sent"] else 0
        s["reply_rate"] = round(s["replies"] / s["sent"], 3) if s["sent"] else 0

    for sv, s in variant_stats.items():
        s["open_rate"] = round(s["opens"] / s["sent"], 3) if s["sent"] else 0
        s["reply_rate"] = round(s["replies"] / s["sent"], 3) if s["sent"] else 0

    return {
        "period_start": cutoff,
        "total_campaigns": len(campaigns),
        "city_stats": city_stats,
        "variant_stats": variant_stats,
        "raw_campaigns": campaigns,
    }


def score_city_performance(performance: dict) -> list[str]:
    """Return city strings ranked by reply_rate descending."""
    city_stats = performance.get("city_stats", {})
    ranked = sorted(city_stats.items(), key=lambda x: x[1]["reply_rate"], reverse=True)
    return [city for city, _ in ranked]


def score_variant_performance(sb_key: str) -> list[dict]:
    """Return content_variants sorted by score descending."""
    rows = sb_get("content_variants", {
        "select": "id,variant_name,channel,score,metadata",
        "order": "score.desc",
        "limit": "20",
    }, sb_key)
    return rows if rows else []


# ---------------------------------------------------------------------------
# Phase 2 — PLAN
# ---------------------------------------------------------------------------


def _pick_cities(performance: dict, count: int = 3) -> list[dict]:
    """Pick top cities by reply_rate, fall back to priority list if no data."""
    ranked = score_city_performance(performance)
    city_stats = performance.get("city_stats", {})

    selected = []
    used = set()

    # Use top ranked cities with positive reply_rate first
    for city_str in ranked:
        if len(selected) >= count:
            break
        stats = city_stats.get(city_str, {})
        if stats.get("reply_rate", 0) > 0:
            parts = city_str.split(", ")
            selected.append({"city": parts[0], "state": parts[1] if len(parts) > 1 else ""})
            used.add(city_str)

    # Fill from priority list
    for entry in CITY_PRIORITY_LIST:
        if len(selected) >= count:
            break
        key = f"{entry['city']}, {entry['state']}"
        if key not in used:
            selected.append(entry)
            used.add(key)

    return selected[:count]


def _pick_subject_variant(performance: dict) -> str:
    """Pick the best-performing subject variant, or default."""
    variant_stats = performance.get("variant_stats", {})
    if not variant_stats:
        return DEFAULT_SUBJECT_VARIANTS[0]
    best = max(variant_stats.items(), key=lambda x: x[1].get("open_rate", 0))
    if best[1].get("open_rate", 0) > 0:
        return best[0]
    return DEFAULT_SUBJECT_VARIANTS[0]


def generate_weekly_plan(
    performance: dict,
    variants: list,
    intelligence: list | None = None,
) -> dict:
    """
    Generate the structured weekly marketing plan.

    Returns a dict with cold_email, reddit, linkedin, short_form, rationale.
    If `intelligence` is provided (from research_agent / marketing_intelligence table),
    the top signals are included in the plan rationale and short-form hooks.
    """
    intelligence = intelligence or []
    cities = _pick_cities(performance, count=3)
    best_subject = _pick_subject_variant(performance)

    # Build rationale string
    city_stats = performance.get("city_stats", {})
    variant_stats = performance.get("variant_stats", {})
    rationale_parts = []

    if city_stats:
        best_city = max(city_stats.items(), key=lambda x: x[1].get("reply_rate", 0))
        worst_city = min(city_stats.items(), key=lambda x: x[1].get("reply_rate", 0))
        rationale_parts.append(
            f"{best_city[0]} led with {best_city[1]['reply_rate']*100:.0f}% reply rate; "
            f"{worst_city[0]} had {worst_city[1]['reply_rate']*100:.0f}% — rotating out if replaced."
        )
    else:
        rationale_parts.append("No prior data — using city priority rotation (Phoenix, Houston, Tampa).")

    if variant_stats:
        sv_ranked = sorted(variant_stats.items(), key=lambda x: x[1].get("open_rate", 0), reverse=True)
        top_sv = sv_ranked[0]
        rationale_parts.append(
            f"Subject variant '{top_sv[0]}' had {top_sv[1]['open_rate']*100:.0f}% open rate "
            f"— using this week."
        )
    else:
        rationale_parts.append(f"No variant data — defaulting to '{best_subject}'.")

    # Reddit: rotate through subreddits
    week_num = datetime.now(timezone.utc).isocalendar()[1]
    reddit_variant_keys = list(REDDIT_VARIANTS.keys())
    reddit_plan = []
    subreddits = ["HVAC", "Contractor", "hvacadvice"]
    for i, sub in enumerate(subreddits):
        variant_key = reddit_variant_keys[(week_num + i) % len(reddit_variant_keys)]
        reddit_plan.append({
            "subreddit": sub,
            "post_variant": variant_key,
            "title": REDDIT_VARIANTS[variant_key]["title"],
        })

    # LinkedIn: rotate variants
    linkedin_keys = list(LINKEDIN_VARIANTS.keys())
    linkedin_plan = [
        {"post_variant": linkedin_keys[week_num % len(linkedin_keys)]},
        {"post_variant": linkedin_keys[(week_num + 1) % len(linkedin_keys)]},
    ]

    # Short-form scripts
    sf_keys = list(SHORT_FORM_VARIANTS.keys())
    short_form_plan = []
    for i in range(3):
        key = sf_keys[(week_num + i) % len(sf_keys)]
        short_form_plan.append({
            "script_variant": key,
            "hook": SHORT_FORM_VARIANTS[key]["hook"],
            "platform": SHORT_FORM_VARIANTS[key]["platform"],
        })

    # Incorporate top intelligence signals into rationale + short-form hooks
    top_signals = intelligence[:3] if intelligence else []
    if top_signals:
        sig_titles = [s["title"][:80] for s in top_signals]
        rationale_parts.append(
            f"Top research signals this week: {'; '.join(sig_titles)}"
        )
        # Override first short-form hook with the highest-confidence signal hook
        best_signal = top_signals[0]
        if short_form_plan and best_signal.get("hook"):
            short_form_plan[0]["hook"] = best_signal["hook"][:200]
            short_form_plan[0]["intelligence_source"] = best_signal.get("url", "")

    return {
        "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "cold_email": [
            {
                "city": c["city"],
                "state": c["state"],
                "count": 5,
                "subject_variant": best_subject,
            }
            for c in cities
        ],
        "reddit": reddit_plan,
        "linkedin": linkedin_plan,
        "short_form": short_form_plan,
        "intelligence_signals": top_signals,
        "rationale": " ".join(rationale_parts),
    }


# ---------------------------------------------------------------------------
# Phase 3 — PROPOSE
# ---------------------------------------------------------------------------


def _format_slack_plan(plan: dict, performance: dict) -> str:
    """Build the readable Slack approval message."""
    week_of = plan.get("week_of", "this week")
    total = performance.get("total_campaigns", 0)
    city_stats = performance.get("city_stats", {})
    variant_stats = performance.get("variant_stats", {})

    lines = [
        f":brain: *Syntharra Marketing Brain — Week of {week_of}*",
        "",
        "*Last Week Performance Summary*",
    ]

    if total == 0:
        lines.append("  No campaigns ran last week (first run or cold start).")
    else:
        lines.append(f"  Total campaigns tracked: {total}")
        if city_stats:
            lines.append("  By city (reply rate):")
            for city, s in sorted(city_stats.items(), key=lambda x: x[1]["reply_rate"], reverse=True):
                lines.append(
                    f"    • {city}: {s['reply_rate']*100:.0f}% reply | "
                    f"{s['open_rate']*100:.0f}% open | {s['sent']} sent"
                )
        if variant_stats:
            lines.append("  Subject variants (open rate):")
            for sv, s in sorted(variant_stats.items(), key=lambda x: x[1]["open_rate"], reverse=True):
                lines.append(f"    • `{sv}`: {s['open_rate']*100:.0f}% open, {s['reply_rate']*100:.0f}% reply")

    lines += [
        "",
        "*This Week's Plan*",
        "",
        ":email: *Cold Email Campaigns (15 total)*",
    ]
    for ce in plan.get("cold_email", []):
        lines.append(f"  • {ce['city']}, {ce['state']} — {ce['count']} emails | subject: `{ce['subject_variant']}`")

    lines += ["", ":mega: *Reddit Posts (3)*"]
    for rp in plan.get("reddit", []):
        lines.append(f"  • r/{rp['subreddit']}: \"{rp['title'][:80]}…\"  (variant: `{rp['post_variant']}`)")

    lines += ["", ":linkedin: *LinkedIn Posts (2)*"]
    for lp in plan.get("linkedin", []):
        lines.append(f"  • Variant: `{lp['post_variant']}`")

    lines += ["", ":clapper: *Short-Form Scripts (3 — Dan to film)*"]
    for sf in plan.get("short_form", []):
        lines.append(f"  • `{sf['script_variant']}`: \"{sf['hook']}\"")

    lines += [
        "",
        f":bulb: *Rationale:* {plan.get('rationale', 'N/A')}",
        "",
        "---",
        ":white_check_mark: *Reply `go` to approve and execute this plan.*",
        ":x: *Reply `stop` to cancel.*",
        "_Auto-approves in 48 hours if no reply._",
    ]

    return "\n".join(lines)


def post_plan_to_slack(plan: dict, performance: dict, token: str) -> str:
    """Post formatted plan to #marketing-team. Returns message_ts."""
    text = _format_slack_plan(plan, performance)

    # Resolve channel ID from name
    channels_req = urllib.request.Request(
        "https://slack.com/api/conversations.list?types=public_channel,private_channel&limit=200",
        headers={"Authorization": f"Bearer {token}"},
    )
    channel_id = None
    try:
        with urllib.request.urlopen(channels_req) as resp:
            data = json.loads(resp.read().decode())
        target = SLACK_CHANNEL.lstrip("#")
        for ch in data.get("channels", []):
            if ch.get("name") == target:
                channel_id = ch["id"]
                break
    except Exception as exc:
        print(f"[WARN] Slack channel list failed: {exc}", file=sys.stderr)

    if not channel_id:
        print(f"[WARN] Could not resolve {SLACK_CHANNEL} — using name directly", file=sys.stderr)
        channel_id = SLACK_CHANNEL

    payload = json.dumps({"channel": channel_id, "text": text}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
        if result.get("ok"):
            ts = result.get("ts", "")
            print(f"[INFO] Plan posted to Slack at ts={ts}")
            return ts
        else:
            print(f"[WARN] Slack post failed: {result.get('error')}", file=sys.stderr)
    except Exception as exc:
        print(f"[WARN] Slack post error: {exc}", file=sys.stderr)
    return ""


def check_for_approval(channel: str, plan_ts: str, token: str) -> bool:
    """
    Poll the Slack thread for Dan's 'go' (approve) or 'stop' (cancel) reply.
    Polls every 30 minutes for up to 48 hours.
    Returns True if approved (or auto-approved), False if stopped.
    """
    if not plan_ts:
        print("[WARN] No plan_ts — auto-approving.", file=sys.stderr)
        return True

    deadline = time.time() + 48 * 3600
    poll_interval = 30 * 60  # 30 minutes
    warning_sent = False

    # Resolve channel id if needed
    channel_id = channel

    while time.time() < deadline:
        time.sleep(min(poll_interval, deadline - time.time()))

        req = urllib.request.Request(
            f"https://slack.com/api/conversations.replies?channel={channel_id}&ts={plan_ts}",
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
            messages = data.get("messages", [])
            for msg in messages[1:]:  # skip the original post
                text = msg.get("text", "").lower().strip()
                if "go" in text.split():
                    print("[INFO] Approval received from Slack.")
                    return True
                if "stop" in text.split():
                    print("[INFO] Stop received from Slack — aborting.")
                    return False
        except Exception as exc:
            print(f"[WARN] Slack poll error: {exc}", file=sys.stderr)

        # Send 2h warning before auto-approve
        remaining = deadline - time.time()
        if remaining < 2 * 3600 and not warning_sent:
            _post_slack_warning(channel_id, plan_ts, token)
            warning_sent = True

    print("[INFO] 48h elapsed — auto-approving plan.")
    _post_slack_auto_approve(channel_id, plan_ts, token)
    return True


def _post_slack_warning(channel_id: str, thread_ts: str, token: str):
    text = (
        ":hourglass: *Marketing Brain:* 2 hours until auto-approve. "
        "Reply `go` to approve or `stop` to cancel."
    )
    _slack_reply(channel_id, thread_ts, text, token)


def _post_slack_auto_approve(channel_id: str, thread_ts: str, token: str):
    text = (
        ":white_check_mark: *Marketing Brain:* 48h elapsed with no reply. "
        "Auto-approving and executing the plan now."
    )
    _slack_reply(channel_id, thread_ts, text, token)


def _slack_reply(channel_id: str, thread_ts: str, text: str, token: str):
    payload = json.dumps({
        "channel": channel_id,
        "thread_ts": thread_ts,
        "text": text,
    }).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req):
            pass
    except Exception as exc:
        print(f"[WARN] Slack reply failed: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Phase 4 — EXECUTE
# ---------------------------------------------------------------------------


def execute_cold_email_campaign(city_plan: dict, sb_key: str, brevo_key: str) -> dict:
    """
    Run the full scrape → enrich → build → send pipeline for one city.
    Returns a result dict with status and counts.
    """
    city = city_plan["city"]
    state = city_plan["state"]
    count = city_plan.get("count", 5)
    subject_variant = city_plan.get("subject_variant", DEFAULT_SUBJECT_VARIANTS[0])

    safe_city = city.lower().replace(" ", "-")
    leads_path = f"leads/hvac-{safe_city}-{state.lower()}.csv"
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    result = {
        "city": city,
        "state": state,
        "subject_variant": subject_variant,
        "leads_scraped": 0,
        "emails_enriched": 0,
        "emails_sent": 0,
        "status": "pending",
        "error": None,
    }

    # Step 1: scrape (if leads file doesn't exist or is stale)
    leads_full = os.path.join(repo_root, leads_path)
    if not os.path.exists(leads_full):
        print(f"[INFO] Scraping HVAC leads for {city}, {state}…")
        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(repo_root, "tools", "scrape_hvac_directory.py"),
                "--city", city,
                "--state", state,
                "--out", leads_path,
            ],
            capture_output=True, text=True, cwd=repo_root,
        )
        if proc.returncode != 0:
            result["error"] = f"scrape failed: {proc.stderr[:300]}"
            result["status"] = "failed"
            return result
    else:
        print(f"[INFO] Using cached leads file: {leads_path}")

    # Step 2: enrich with emails
    enriched_path = leads_path.replace(".csv", "-enriched.csv")
    enriched_full = os.path.join(repo_root, enriched_path)
    if not os.path.exists(enriched_full):
        print(f"[INFO] Enriching emails for {city}, {state}…")
        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(repo_root, "tools", "find_email_from_website.py"),
                "--in", leads_path,
                "--out", enriched_path,
                "--limit", str(count),
            ],
            capture_output=True, text=True, cwd=repo_root,
        )
        if proc.returncode != 0:
            result["error"] = f"enrich failed: {proc.stderr[:300]}"
            result["status"] = "failed"
            return result

    # Count enriched leads
    try:
        with open(enriched_full) as f:
            result["emails_enriched"] = max(0, sum(1 for _ in f) - 1)
    except Exception:
        pass

    # Step 3: build sequences
    sequence_path = leads_path.replace(".csv", f"-sequence-{subject_variant}.csv")
    print(f"[INFO] Building cold outreach sequence for {city}, {state}…")
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "build_cold_outreach.py"),
            "--in", enriched_path,
            "--out", sequence_path,
            "--variant", subject_variant,
        ],
        capture_output=True, text=True, cwd=repo_root,
    )
    if proc.returncode != 0:
        result["error"] = f"build failed: {proc.stderr[:300]}"
        result["status"] = "failed"
        return result

    # Step 4: send via Brevo
    print(f"[INFO] Sending cold outreach for {city}, {state}…")
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "send_cold_outreach.py"),
            "--in", sequence_path,
            "--backend", "brevo",
            "--i-know-this-is-real",
        ],
        capture_output=True, text=True, cwd=repo_root,
        env={**os.environ, "BREVO_API_KEY": brevo_key},
    )
    if proc.returncode != 0:
        result["error"] = f"send failed: {proc.stderr[:300]}"
        result["status"] = "failed"
        return result

    # Parse sent count from stdout (best-effort)
    for line in proc.stdout.splitlines():
        if "sent" in line.lower():
            for tok in line.split():
                if tok.isdigit():
                    result["emails_sent"] = int(tok)
                    break

    result["status"] = "sent"
    return result


def post_to_reddit(post_plan: dict, reddit_creds: dict) -> dict:
    """Post to Reddit via OAuth2 API."""
    variant_key = post_plan.get("post_variant", "missed_call_story_v1")
    variant = REDDIT_VARIANTS.get(variant_key, {})
    subreddit = post_plan.get("subreddit", variant.get("subreddit", "HVAC"))
    title = variant.get("title", post_plan.get("title", "Syntharra post"))
    body = variant.get("body", "")

    client_id = reddit_creds.get("client_id", "")
    client_secret = reddit_creds.get("client_secret", "")
    refresh_token = reddit_creds.get("refresh_token", "")

    if not all([client_id, client_secret, refresh_token]):
        return {"status": "skipped", "reason": "Reddit credentials not in vault"}

    # Get access token
    auth_data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()
    import base64
    creds_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token_req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=auth_data,
        headers={
            "Authorization": f"Basic {creds_b64}",
            "User-Agent": "Syntharra Marketing Bot/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(token_req) as resp:
            token_data = json.loads(resp.read().decode())
        access_token = token_data.get("access_token", "")
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}

    # Submit post
    submit_data = urllib.parse.urlencode({
        "api_type": "json",
        "kind": "self",
        "sr": subreddit,
        "title": title,
        "text": body,
        "nsfw": "false",
        "spoiler": "false",
    }).encode()
    submit_req = urllib.request.Request(
        "https://oauth.reddit.com/api/submit",
        data=submit_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "Syntharra Marketing Bot/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(submit_req) as resp:
            result = json.loads(resp.read().decode())
        errors = result.get("json", {}).get("errors", [])
        if errors:
            return {"status": "failed", "reason": str(errors)}
        url = result.get("json", {}).get("data", {}).get("url", "")
        print(f"[INFO] Reddit post submitted: {url}")
        return {"status": "posted", "url": url, "subreddit": subreddit, "variant": variant_key}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


def post_to_linkedin(post_plan: dict, linkedin_token: str) -> dict:
    """Post to LinkedIn via API v2."""
    if not linkedin_token:
        return {"status": "skipped", "reason": "LinkedIn token not in vault"}

    variant_key = post_plan.get("post_variant", "owner_operator_pain_v1")
    variant = LINKEDIN_VARIANTS.get(variant_key, {})
    text = variant.get("text", "")
    if not text:
        return {"status": "skipped", "reason": f"No text for variant {variant_key}"}

    # Get the author URN (person or organization)
    profile_req = urllib.request.Request(
        "https://api.linkedin.com/v2/me",
        headers={
            "Authorization": f"Bearer {linkedin_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    try:
        with urllib.request.urlopen(profile_req) as resp:
            profile = json.loads(resp.read().decode())
        author_urn = f"urn:li:person:{profile['id']}"
    except Exception as exc:
        return {"status": "failed", "reason": f"LinkedIn profile fetch failed: {exc}"}

    payload = json.dumps({
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }).encode()

    post_req = urllib.request.Request(
        "https://api.linkedin.com/v2/ugcPosts",
        data=payload,
        headers={
            "Authorization": f"Bearer {linkedin_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(post_req) as resp:
            result = json.loads(resp.read().decode())
        post_id = result.get("id", "")
        print(f"[INFO] LinkedIn post published: {post_id}")
        return {"status": "posted", "post_id": post_id, "variant": variant_key}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


def post_short_form_to_slack(scripts: list, token: str):
    """Share short-form scripts with Dan to film — can't auto-post video."""
    lines = [
        ":clapper: *Short-Form Scripts for Dan to Film This Week*",
        "_These need to be filmed manually. Camera on, 30 seconds each._",
        "",
    ]
    for sf in scripts:
        key = sf.get("script_variant", "")
        variant = SHORT_FORM_VARIANTS.get(key, {})
        script_text = variant.get("script", sf.get("hook", ""))
        lines += [
            f"*{key}* — _{sf.get('platform', 'TikTok/Reels')}_",
            f"Hook: {sf.get('hook', '')}",
            "```",
            script_text,
            "```",
            "",
        ]
    text = "\n".join(lines)

    payload = json.dumps({"channel": SLACK_CHANNEL, "text": text}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req):
            print("[INFO] Short-form scripts posted to Slack.")
    except Exception as exc:
        print(f"[WARN] Short-form Slack post failed: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Phase 5 — TRACK
# ---------------------------------------------------------------------------


def record_campaign(channel: str, details: dict, sb_key: str) -> str | None:
    """Insert a row into marketing_campaigns. Returns the new row id."""
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "channel": channel,
        "city": details.get("city"),
        "state": details.get("state"),
        "subject_variant": details.get("subject_variant") or details.get("post_variant") or details.get("script_variant"),
        "status": details.get("status", "sent"),
        "metadata": json.dumps({k: v for k, v in details.items() if k not in ("city", "state", "status")}),
        "created_at": now,
    }
    result = sb_post("marketing_campaigns", row, sb_key)
    if result and isinstance(result, list) and result:
        return result[0].get("id")
    return None


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_weekly_cycle(dry_run: bool = False, force_execute: bool = False, review_only: bool = False):
    """Run the full 5-phase weekly marketing cycle."""
    print(f"\n{'='*60}")
    print(f"Syntharra Marketing Brain — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")
    if dry_run:
        print("[DRY RUN] No emails, posts, or Supabase writes will occur.\n")

    _, sb_key = get_sb_credentials()

    # ------------------------------------------------------------------ #
    # Phase 1 — REVIEW                                                     #
    # ------------------------------------------------------------------ #
    print("\n--- Phase 1: REVIEW ---")
    performance = get_last_week_performance(sb_key)
    print(f"  Campaigns last 7 days: {performance['total_campaigns']}")
    city_stats = performance.get("city_stats", {})
    if city_stats:
        for city, s in sorted(city_stats.items(), key=lambda x: x[1]["reply_rate"], reverse=True):
            print(f"    {city}: {s['reply_rate']*100:.0f}% reply | {s['open_rate']*100:.0f}% open")
    else:
        print("  No campaign data yet — cold start.")

    variants = score_variant_performance(sb_key)
    print(f"  Content variants scored: {len(variants)}")

    # Read top-confidence signals from research_agent (daily Reddit/YouTube scrape)
    intelligence = get_top_intelligence(sb_key, limit=10)
    if intelligence:
        print(f"  Marketing intelligence signals (top {len(intelligence)}, conf ≥0.6):")
        for sig in intelligence[:5]:
            print(f"    [{sig['source']}] conf={sig['confidence']} — {sig['title'][:72]}")
    else:
        print("  No recent marketing intelligence — research_agent may not have run yet.")

    if review_only:
        print("\n[--review-only] Stopping after review.")
        return

    # ------------------------------------------------------------------ #
    # Phase 2 — PLAN                                                       #
    # ------------------------------------------------------------------ #
    print("\n--- Phase 2: PLAN ---")
    plan = generate_weekly_plan(performance, variants, intelligence=intelligence)
    cities_display = [c['city'] + ", " + c['state'] for c in plan['cold_email']]
    print(f"  Cities: {cities_display}")
    print(f"  Reddit: {[r['subreddit'] for r in plan['reddit']]}")
    print(f"  LinkedIn variants: {[lp['post_variant'] for lp in plan['linkedin']]}")
    print(f"  Short-form: {[sf['script_variant'] for sf in plan['short_form']]}")
    print(f"  Rationale: {plan['rationale']}")

    if dry_run:
        print("\n[DRY RUN] Plan generated. Stopping before Slack proposal.")
        print(json.dumps(plan, indent=2))
        return

    # ------------------------------------------------------------------ #
    # Phase 3 — PROPOSE                                                    #
    # ------------------------------------------------------------------ #
    print("\n--- Phase 3: PROPOSE ---")
    slack_token = fetch_vault("Slack", "bot_token")
    if not slack_token:
        print("[WARN] No Slack bot_token in vault — proceeding without approval step.")
        approved = True
        plan_ts = ""
        channel_id = SLACK_CHANNEL
    else:
        plan_ts = post_plan_to_slack(plan, performance, slack_token)
        channel_id = SLACK_CHANNEL  # will be resolved inside check_for_approval

        if force_execute:
            print("[--force-execute] Skipping approval wait.")
            approved = True
        else:
            print("  Waiting for Dan's 'go' reply (polling every 30 min, up to 48h)…")
            approved = check_for_approval(channel_id, plan_ts, slack_token)

    if not approved:
        print("\n[INFO] Plan cancelled by Dan. Exiting.")
        return

    # ------------------------------------------------------------------ #
    # Phase 4 — EXECUTE                                                    #
    # ------------------------------------------------------------------ #
    print("\n--- Phase 4: EXECUTE ---")
    brevo_key = fetch_vault("Brevo", "api_key") or ""
    reddit_creds = {
        "client_id": fetch_vault("Reddit", "client_id"),
        "client_secret": fetch_vault("Reddit", "client_secret"),
        "refresh_token": fetch_vault("Reddit", "refresh_token"),
    }
    linkedin_token = fetch_vault("LinkedIn", "access_token") or ""

    all_results = []

    # Cold email campaigns — gated on COLD_EMAIL_ENABLED env var.
    # Dan's 2026-04-11 decision: pause cold outbound, focus on organic
    # social content. Flip COLD_EMAIL_ENABLED=true in Railway env to resume.
    if is_cold_email_enabled():
        for city_plan in plan.get("cold_email", []):
            print(f"\n  [Email] {city_plan['city']}, {city_plan['state']}")
            result = execute_cold_email_campaign(city_plan, sb_key, brevo_key)
            all_results.append(("cold_email", result))
            print(f"    → status={result['status']} sent={result['emails_sent']} enriched={result['emails_enriched']}")
            if result.get("error"):
                print(f"    [ERR] {result['error']}")
    else:
        planned = len(plan.get("cold_email", []))
        print(f"\n  [Email] SKIP — COLD_EMAIL_ENABLED=false ({planned} city plans not executed)")

    # Reddit posts
    reddit_pending_credentials = not any(reddit_creds.values())
    if reddit_pending_credentials and slack_token:
        # Notify Dan via Slack
        note = (
            ":warning: *Reddit posting pending credentials* — scripts are ready but "
            "`Reddit/client_id`, `Reddit/client_secret`, `Reddit/refresh_token` "
            "need to be added to syntharra_vault. Ping Dan."
        )
        _slack_reply(SLACK_CHANNEL, plan_ts or "", note, slack_token)

    for rp in plan.get("reddit", []):
        print(f"\n  [Reddit] r/{rp['subreddit']} — {rp['post_variant']}")
        result = post_to_reddit(rp, reddit_creds)
        all_results.append(("reddit", {**rp, **result}))
        print(f"    → {result}")

    # LinkedIn posts
    if not linkedin_token and slack_token:
        note = (
            ":warning: *LinkedIn posting pending credentials* — "
            "`LinkedIn/access_token` needs to be added to syntharra_vault."
        )
        _slack_reply(SLACK_CHANNEL, plan_ts or "", note, slack_token)

    for lp in plan.get("linkedin", []):
        print(f"\n  [LinkedIn] {lp['post_variant']}")
        result = post_to_linkedin(lp, linkedin_token)
        all_results.append(("linkedin", {**lp, **result}))
        print(f"    → {result}")

    # Short-form scripts → Slack for Dan to film
    if slack_token:
        print("\n  [Short-form] Posting scripts to Slack for Dan to film…")
        post_short_form_to_slack(plan.get("short_form", []), slack_token)
    for sf in plan.get("short_form", []):
        all_results.append(("short_form", {**sf, "status": "scripts_posted_to_slack"}))

    # Blog publisher — trigger one post publish per weekly cycle
    print("\n  [Blog] Triggering n8n blog publisher…")
    if not dry_run:
        blog_triggered = trigger_n8n_blog_publisher()
        all_results.append(("blog", {"status": "triggered" if blog_triggered else "failed"}))
    else:
        print("  [Blog] DRY RUN — blog publisher trigger skipped")

    # ------------------------------------------------------------------ #
    # Phase 5 — TRACK                                                      #
    # ------------------------------------------------------------------ #
    run_at = datetime.now(timezone.utc).isoformat()
    print("\n--- Phase 5: TRACK ---")
    for channel, details in all_results:
        campaign_id = record_campaign(channel, details, sb_key)
        if campaign_id:
            print(f"  Logged {channel} campaign → id={campaign_id}")
        else:
            print(f"  [WARN] Failed to log {channel} campaign to Supabase")

    # Write marketing_brain_log entry
    if not dry_run:
        log_brain_run(
            run_at=run_at,
            status="complete",
            plan=plan,
            results=[{"channel": ch, **r} for ch, r in all_results],
            sb_key=sb_key,
        )

    # Final summary to Slack
    if slack_token:
        sent_count = sum(1 for ch, r in all_results if r.get("status") in ("sent", "posted"))
        summary = (
            f":white_check_mark: *Marketing Brain — Week of {plan['week_of']} complete.*\n"
            f"  • Cold emails: {sum(r.get('emails_sent', 0) for ch, r in all_results if ch == 'cold_email')} sent\n"
            f"  • Reddit posts: {sum(1 for ch, r in all_results if ch == 'reddit' and r.get('status') == 'posted')}/3\n"
            f"  • LinkedIn posts: {sum(1 for ch, r in all_results if ch == 'linkedin' and r.get('status') == 'posted')}/2\n"
            f"  • Short-form scripts: posted to this channel for filming\n"
            f"  • Blog post: {'triggered' if not dry_run else 'skipped (dry run)'}\n"
            f"  Total campaigns logged to Supabase: {len(all_results)}"
        )
        _slack_reply(SLACK_CHANNEL, plan_ts or "", summary, slack_token)

    print(f"\n{'='*60}")
    print("Weekly cycle complete.")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Syntharra Marketing Brain — autonomous weekly marketing orchestrator",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be planned/sent without executing",
    )
    parser.add_argument(
        "--force-execute", action="store_true",
        help="Skip approval wait (for testing)",
    )
    parser.add_argument(
        "--review-only", action="store_true",
        help="Show last week's performance and exit",
    )
    args = parser.parse_args()

    run_weekly_cycle(
        dry_run=args.dry_run,
        force_execute=args.force_execute,
        review_only=args.review_only,
    )


if __name__ == "__main__":
    main()
