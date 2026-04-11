#!/usr/bin/env python3
"""
run_outreach_campaign.py — One-command cold outreach pipeline for a city.

Replaces the 4-step manual sequence with a single command:
  python tools/run_outreach_campaign.py --city "Phoenix" --state AZ

Steps it runs in order:
  1. Scrape HVAC contractors from OpenStreetMap (scrape_hvac_directory.py)
  2. Find email addresses from contractor websites (find_email_from_website.py)
  3. Build 3-touch email sequences (build_cold_outreach.py)
  4. Preview the sequences (dry run — DO NOT send without Dan reviewing)

After preview, Dan reviews leads/CITY_cold_outreach.txt then runs:
  python tools/send_cold_outreach.py leads/CITY_cold_outreach.json --backend brevo

All work is saved to the leads/ directory. Idempotent — re-running skips
already-enriched contacts to avoid duplicate API hits.

Cost: $0. Uses OSM (free) + homepage scraping (free).
With Hunter.io (needs vault key): pass --hunter for ~75% email hit rate.

Usage:
  source .env.local
  python tools/run_outreach_campaign.py --city "Phoenix" --state AZ
  python tools/run_outreach_campaign.py --city "Nashville" --state TN --limit 30
  python tools/run_outreach_campaign.py --city "Dallas" --state TX --hunter
  python tools/run_outreach_campaign.py --list-cities   # show priority city queue

Output files (all in leads/):
  {slug}_hvac_leads.json          Raw scraped leads
  {slug}_hvac_leads_enriched.json Leads with email addresses
  {slug}_cold_outreach.json       Email sequences (JSON)
  {slug}_cold_outreach.txt        Human-readable preview

After reviewing the .txt file, send with:
  python tools/send_cold_outreach.py leads/{slug}_cold_outreach.json --backend brevo
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Priority order: warm/hot climates where AC is critical, major HVAC markets.
PRIORITY_CITIES = [
    {"city": "Phoenix",       "state": "AZ"},
    {"city": "Las Vegas",     "state": "NV"},
    {"city": "Houston",       "state": "TX"},
    {"city": "Dallas",        "state": "TX"},
    {"city": "Miami",         "state": "FL"},
    {"city": "Orlando",       "state": "FL"},
    {"city": "Tampa",         "state": "FL"},
    {"city": "Atlanta",       "state": "GA"},
    {"city": "Austin",        "state": "TX"},
    {"city": "San Antonio",   "state": "TX"},
    {"city": "Fort Worth",    "state": "TX"},
    {"city": "Jacksonville",  "state": "FL"},
    {"city": "Charlotte",     "state": "NC"},
    {"city": "Nashville",     "state": "TN"},
    {"city": "Memphis",       "state": "TN"},
    {"city": "Birmingham",    "state": "AL"},
    {"city": "New Orleans",   "state": "LA"},
    {"city": "Oklahoma City", "state": "OK"},
    {"city": "Tucson",        "state": "AZ"},
    {"city": "Albuquerque",   "state": "NM"},
    {"city": "El Paso",       "state": "TX"},
    {"city": "Denver",        "state": "CO"},
    {"city": "Raleigh",       "state": "NC"},
    {"city": "Indianapolis",  "state": "IN"},
    {"city": "Columbus",      "state": "OH"},
]


def slug(city: str) -> str:
    return city.lower().replace(" ", "_").replace("-", "_")


def run(cmd: list[str], label: str) -> int:
    """Run a subprocess. Return exit code."""
    print(f"\n[step] {label}")
    print(f"       {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"[warn] step exited with code {result.returncode} — continuing")
    return result.returncode


def leads_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(os.path.dirname(here), "leads")
    os.makedirs(d, exist_ok=True)
    return d


def main():
    ap = argparse.ArgumentParser(
        description="Run full cold outreach pipeline for one city."
    )
    ap.add_argument("--city", help="City name (e.g. 'Phoenix')")
    ap.add_argument("--state", help="2-letter state code (e.g. AZ)")
    ap.add_argument(
        "--limit", type=int, default=20,
        help="Max contractors to scrape (default 20)"
    )
    ap.add_argument(
        "--hunter", action="store_true",
        help="Use Hunter.io for email enrichment (needs vault key)"
    )
    ap.add_argument(
        "--list-cities", action="store_true",
        help="Print priority city queue and exit"
    )
    args = ap.parse_args()

    if args.list_cities:
        print("Priority city queue for cold outreach:")
        for i, c in enumerate(PRIORITY_CITIES, 1):
            print(f"  {i:2}. {c['city']}, {c['state']}")
        return

    if not args.city or not args.state:
        ap.error("--city and --state are required (or use --list-cities)")

    city = args.city
    state = args.state.upper()
    s = slug(city)
    d = leads_dir()

    raw_path      = os.path.join(d, f"{s}_hvac_leads.json")
    enriched_path = os.path.join(d, f"{s}_hvac_leads_enriched.json")
    outreach_path = os.path.join(d, f"{s}_cold_outreach.json")

    tools = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'=' * 60}")
    print(f"  Syntharra Cold Outreach Campaign")
    print(f"  City: {city}, {state}")
    print(f"  Limit: {args.limit} contacts")
    print(f"  Output: leads/{s}_*")
    print(f"{'=' * 60}")

    # ── Step 1: Scrape ──────────────────────────────────────────────────────
    run(
        [sys.executable, os.path.join(tools, "scrape_hvac_directory.py"),
         "--city", city, "--state", state,
         "--limit", str(args.limit),
         "--out", raw_path],
        f"Scraping HVAC contractors in {city}, {state}",
    )

    if not os.path.exists(raw_path):
        sys.exit(f"[error] Scrape produced no output at {raw_path}")

    # ── Step 2: Email enrichment ────────────────────────────────────────────
    enrich_cmd = [
        sys.executable, os.path.join(tools, "find_email_from_website.py"),
        raw_path, "--out", enriched_path,
    ]
    if args.hunter:
        enrich_cmd.append("--hunter")
    run(enrich_cmd, "Finding email addresses")

    enrich_src = enriched_path if os.path.exists(enriched_path) else raw_path

    # ── Step 3: Build sequences ─────────────────────────────────────────────
    run(
        [sys.executable, os.path.join(tools, "build_cold_outreach.py"),
         enrich_src, "--out", outreach_path],
        "Building 3-touch email sequences",
    )

    if not os.path.exists(outreach_path):
        sys.exit(f"[error] No outreach file at {outreach_path}")

    # ── Step 4: Preview ─────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    print(f"\n  Review the sequences before sending:")
    txt_path = outreach_path.replace(".json", ".txt")
    if os.path.exists(txt_path):
        print(f"    cat leads/{s}_cold_outreach.txt")
    print(f"\n  Send when ready:")
    print(f"    python tools/send_cold_outreach.py leads/{s}_cold_outreach.json --backend brevo")
    print(f"\n  Or preview without sending:")
    print(f"    python tools/send_cold_outreach.py leads/{s}_cold_outreach.json --backend print")
    print()


if __name__ == "__main__":
    main()
