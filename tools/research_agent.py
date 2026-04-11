#!/usr/bin/env python3
"""
research_agent.py — daily viral-content research for the HVAC niche.

Writes findings to `marketing_intelligence` (schema from 20260412_content_team_schema.sql).
Consumed by content_writer.py to seed weekly video scripts.

v1 scope (2026-04-12):
  - Reddit unauthenticated JSON API across 4 HVAC-adjacent subs
  - YouTube search: gracefully skipped unless YouTube/api_key is in vault
  - Google Trends: deferred (pytrends is a third-party dep; repo is stdlib-only)

Graceful degradation: any source that fails or has missing creds is skipped
with a warning. The agent never crashes on missing auth — it just produces
fewer findings for that run.

Usage:
  source .env.local
  python tools/research_agent.py                 # full run, all sources
  python tools/research_agent.py --source reddit # single source
  python tools/research_agent.py --dry-run       # print findings, don't write
  python tools/research_agent.py --limit 10      # per-sub result cap

Requires env: SUPABASE_URL, SUPABASE_SERVICE_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Reddit — subs where HVAC owners + small contractors hang out.
REDDIT_SUBS = ["HVAC", "hvacadvice", "Contractor", "smallbusiness"]

# YouTube search queries targeting pain points HVAC owners feel.
# Only used if a Data API key is later vaulted under YouTube/api_key.
YOUTUBE_QUERIES = [
    "HVAC business missed calls",
    "HVAC answering service",
    "HVAC contractor after hours calls",
    "AI receptionist HVAC",
    "HVAC lead generation",
]

USER_AGENT = "Syntharra-ResearchAgent/1.0 (contact: daniel@syntharra.com)"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fetch_vault(service_name: str, key_type: str) -> str | None:
    """Fetch a credential from syntharra_vault. Returns None if not found.

    Matches the pattern used by tools/marketing_brain.py.
    """
    if not (SUPABASE_URL and SUPABASE_KEY):
        return None
    qs = urllib.parse.urlencode({
        "service_name": f"eq.{service_name}",
        "key_type": f"eq.{key_type}",
        "select": "key_value",
        "limit": 1,
    })
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/syntharra_vault?{qs}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read().decode())
    except Exception as e:
        print(f"[vault] fetch error for {service_name}/{key_type}: {e}", file=sys.stderr)
        return None
    if not rows:
        return None
    return rows[0].get("key_value")


def supabase_insert(table: str, rows: list[dict]) -> int:
    """Bulk insert rows into a Supabase table via PostgREST. Returns insert count."""
    if not rows:
        return 0
    if not (SUPABASE_URL and SUPABASE_KEY):
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=json.dumps(rows).encode(),
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 201, 204):
            raise RuntimeError(f"Insert failed: {r.status} {r.read().decode()}")
    return len(rows)


# ---------------------------------------------------------------------------
# Reddit — unauthenticated public JSON endpoint
# ---------------------------------------------------------------------------


def scrape_reddit(limit_per_sub: int = 25) -> list[dict]:
    """Pull this week's top posts from each HVAC-adjacent sub.

    Uses Reddit's public JSON endpoint (no OAuth needed). Reddit requires a
    real User-Agent string — random/empty UAs get rate-limited to 429.
    """
    findings: list[dict] = []
    for sub in REDDIT_SUBS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit={limit_per_sub}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[reddit] r/{sub} HTTP {e.code}: {e.reason}", file=sys.stderr)
            # Polite backoff on rate limit
            if e.code == 429:
                time.sleep(5)
            continue
        except Exception as e:
            print(f"[reddit] r/{sub} error: {e}", file=sys.stderr)
            continue

        children = data.get("data", {}).get("children", [])
        sub_count = 0
        for child in children:
            p = child.get("data", {})
            if p.get("stickied") or p.get("over_18"):
                continue
            title = (p.get("title") or "").strip()
            if not title:
                continue
            ups = int(p.get("ups") or 0)
            num_comments = int(p.get("num_comments") or 0)
            engagement = round(num_comments / max(ups, 1), 4)
            # Confidence: more upvotes + more comments = higher. Capped at 0.95.
            confidence = min(0.95, 0.4 + (ups / 1000) * 0.5 + min(engagement, 0.5) * 0.1)

            findings.append({
                "source": "reddit",
                "query": f"r/{sub}/top/week",
                "title": title[:500],
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "view_count": ups,
                "engagement_rate": engagement,
                "hook": title[:200],
                "angle": (p.get("selftext") or "")[:500],
                "raw_data": {
                    "subreddit": sub,
                    "author": p.get("author"),
                    "created_utc": p.get("created_utc"),
                    "num_comments": num_comments,
                    "flair": p.get("link_flair_text"),
                    "is_self": p.get("is_self"),
                },
                "confidence": round(confidence, 2),
            })
            sub_count += 1

        print(f"[reddit] r/{sub}: {sub_count} posts")
        # Reddit asks for <= 1 req/sec from unauthenticated clients. Be polite.
        time.sleep(1.1)

    return findings


# ---------------------------------------------------------------------------
# YouTube — optional, graceful skip if no API key
# ---------------------------------------------------------------------------


def scrape_youtube(limit_per_query: int = 10) -> list[dict]:
    """Search YouTube for HVAC business content. Skipped if no API key."""
    api_key = fetch_vault("YouTube", "api_key")
    if not api_key:
        print("[youtube] SKIP — no YouTube/api_key in vault", file=sys.stderr)
        return []

    findings: list[dict] = []
    for q in YOUTUBE_QUERIES:
        qs = urllib.parse.urlencode({
            "part": "snippet",
            "type": "video",
            "order": "viewCount",
            "q": q,
            "maxResults": limit_per_query,
            "key": api_key,
        })
        url = f"https://www.googleapis.com/youtube/v3/search?{qs}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"[youtube] {q!r} error: {e}", file=sys.stderr)
            continue

        count = 0
        for item in data.get("items", []):
            vid_id = item.get("id", {}).get("videoId")
            if not vid_id:
                continue
            sn = item.get("snippet", {})
            findings.append({
                "source": "youtube",
                "query": q,
                "title": (sn.get("title") or "")[:500],
                "url": f"https://youtube.com/watch?v={vid_id}",
                "view_count": None,  # Requires videos endpoint for stats; not in v1
                "engagement_rate": None,
                "hook": (sn.get("title") or "")[:200],
                "angle": (sn.get("description") or "")[:500],
                "raw_data": {
                    "video_id": vid_id,
                    "channel": sn.get("channelTitle"),
                    "published_at": sn.get("publishedAt"),
                },
                "confidence": 0.60,
            })
            count += 1

        print(f"[youtube] {q!r}: {count} results")

    return findings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["reddit", "youtube", "all"], default="all")
    ap.add_argument("--dry-run", action="store_true", help="Don't write to Supabase")
    ap.add_argument("--limit", type=int, default=25, help="Per-source item cap")
    args = ap.parse_args()

    if not args.dry_run and not (SUPABASE_URL and SUPABASE_KEY):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY not set. "
              "Run `source .env.local` or pass --dry-run.", file=sys.stderr)
        return 2

    started = datetime.now(timezone.utc)
    print(f"Research Agent run @ {started.isoformat()}")

    all_findings: list[dict] = []

    if args.source in ("reddit", "all"):
        print("\n--- Reddit ---")
        try:
            findings = scrape_reddit(limit_per_sub=args.limit)
            all_findings.extend(findings)
            print(f"[reddit] total: {len(findings)}")
        except Exception as e:
            print(f"[reddit] fatal: {e}", file=sys.stderr)

    if args.source in ("youtube", "all"):
        print("\n--- YouTube ---")
        try:
            findings = scrape_youtube(limit_per_query=min(args.limit, 10))
            all_findings.extend(findings)
            print(f"[youtube] total: {len(findings)}")
        except Exception as e:
            print(f"[youtube] fatal: {e}", file=sys.stderr)

    print(f"\n=== Total findings: {len(all_findings)} ===")

    if args.dry_run:
        for f in all_findings[:8]:
            print(f"  [{f['source']}] {f['title'][:72]}  (conf {f['confidence']})")
        if len(all_findings) > 8:
            print(f"  ... and {len(all_findings) - 8} more")
        return 0

    if not all_findings:
        print("No findings to write. Exiting cleanly.")
        return 0

    inserted = supabase_insert("marketing_intelligence", all_findings)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(f"Inserted {inserted} rows into marketing_intelligence in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
