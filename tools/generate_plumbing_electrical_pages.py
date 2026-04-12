#!/usr/bin/env python3
"""
generate_plumbing_electrical_pages.py
Generate plumbing + electrical answering service landing pages for all 145 cities.
Pushes directly to Syntharra/syntharra-website via GitHub API.

Usage:
  python tools/generate_plumbing_electrical_pages.py            # all cities, both verticals
  python tools/generate_plumbing_electrical_pages.py --plumbing  # plumbing only
  python tools/generate_plumbing_electrical_pages.py --electrical # electrical only
  python tools/generate_plumbing_electrical_pages.py --dry-run   # print filenames only
  python tools/generate_plumbing_electrical_pages.py --skip-existing
"""
from __future__ import annotations
import argparse
import base64
import json
import sys
import time
import urllib.request
import urllib.error
import os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── Credentials ───────────────────────────────────────────────────────────────
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO  = "Syntharra/syntharra-website"
API   = f"https://api.github.com/repos/{REPO}/contents"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Syntharra-PageGen/2.0",
}

# ── Complete city list (145 cities matching live HVAC pages) ──────────────────
CITIES = [
    {"slug": "abilene",         "name": "Abilene",          "state": "TX"},
    {"slug": "akron",           "name": "Akron",             "state": "OH"},
    {"slug": "albany",          "name": "Albany",            "state": "NY"},
    {"slug": "albuquerque",     "name": "Albuquerque",       "state": "NM"},
    {"slug": "amarillo",        "name": "Amarillo",          "state": "TX"},
    {"slug": "anaheim",         "name": "Anaheim",           "state": "CA"},
    {"slug": "arlington",       "name": "Arlington",         "state": "TX"},
    {"slug": "atlanta",         "name": "Atlanta",           "state": "GA"},
    {"slug": "augusta",         "name": "Augusta",           "state": "GA"},
    {"slug": "aurora",          "name": "Aurora",            "state": "CO"},
    {"slug": "austin",          "name": "Austin",            "state": "TX"},
    {"slug": "bakersfield",     "name": "Bakersfield",       "state": "CA"},
    {"slug": "baltimore",       "name": "Baltimore",         "state": "MD"},
    {"slug": "baton-rouge",     "name": "Baton Rouge",       "state": "LA"},
    {"slug": "beaumont",        "name": "Beaumont",          "state": "TX"},
    {"slug": "birmingham",      "name": "Birmingham",        "state": "AL"},
    {"slug": "boise",           "name": "Boise",             "state": "ID"},
    {"slug": "boston",          "name": "Boston",            "state": "MA"},
    {"slug": "bridgeport",      "name": "Bridgeport",        "state": "CT"},
    {"slug": "brownsville",     "name": "Brownsville",       "state": "TX"},
    {"slug": "buffalo",         "name": "Buffalo",           "state": "NY"},
    {"slug": "cape-coral",      "name": "Cape Coral",        "state": "FL"},
    {"slug": "chandler",        "name": "Chandler",          "state": "AZ"},
    {"slug": "charleston-sc",   "name": "Charleston",        "state": "SC"},
    {"slug": "charlotte",       "name": "Charlotte",         "state": "NC"},
    {"slug": "chattanooga",     "name": "Chattanooga",       "state": "TN"},
    {"slug": "chesapeake",      "name": "Chesapeake",        "state": "VA"},
    {"slug": "chicago",         "name": "Chicago",           "state": "IL"},
    {"slug": "chula-vista",     "name": "Chula Vista",       "state": "CA"},
    {"slug": "cincinnati",      "name": "Cincinnati",        "state": "OH"},
    {"slug": "cleveland",       "name": "Cleveland",         "state": "OH"},
    {"slug": "colorado-springs","name": "Colorado Springs",  "state": "CO"},
    {"slug": "columbia-sc",     "name": "Columbia",          "state": "SC"},
    {"slug": "columbus",        "name": "Columbus",          "state": "OH"},
    {"slug": "corpus-christi",  "name": "Corpus Christi",    "state": "TX"},
    {"slug": "dallas",          "name": "Dallas",            "state": "TX"},
    {"slug": "dayton",          "name": "Dayton",            "state": "OH"},
    {"slug": "denton",          "name": "Denton",            "state": "TX"},
    {"slug": "denver",          "name": "Denver",            "state": "CO"},
    {"slug": "des-moines",      "name": "Des Moines",        "state": "IA"},
    {"slug": "detroit",         "name": "Detroit",           "state": "MI"},
    {"slug": "el-paso",         "name": "El Paso",           "state": "TX"},
    {"slug": "fontana",         "name": "Fontana",           "state": "CA"},
    {"slug": "fort-lauderdale", "name": "Fort Lauderdale",   "state": "FL"},
    {"slug": "fort-worth",      "name": "Fort Worth",        "state": "TX"},
    {"slug": "fresno",          "name": "Fresno",            "state": "CA"},
    {"slug": "garland",         "name": "Garland",           "state": "TX"},
    {"slug": "gilbert",         "name": "Gilbert",           "state": "AZ"},
    {"slug": "glendale-az",     "name": "Glendale",          "state": "AZ"},
    {"slug": "glendale-ca",     "name": "Glendale",          "state": "CA"},
    {"slug": "grand-prairie",   "name": "Grand Prairie",     "state": "TX"},
    {"slug": "grand-rapids",    "name": "Grand Rapids",      "state": "MI"},
    {"slug": "greenville-sc",   "name": "Greenville",        "state": "SC"},
    {"slug": "hampton-va",      "name": "Hampton",           "state": "VA"},
    {"slug": "hartford",        "name": "Hartford",          "state": "CT"},
    {"slug": "henderson",       "name": "Henderson",         "state": "NV"},
    {"slug": "houston",         "name": "Houston",           "state": "TX"},
    {"slug": "huntington-beach","name": "Huntington Beach",  "state": "CA"},
    {"slug": "huntsville",      "name": "Huntsville",        "state": "AL"},
    {"slug": "indianapolis",    "name": "Indianapolis",      "state": "IN"},
    {"slug": "irvine",          "name": "Irvine",            "state": "CA"},
    {"slug": "irving",          "name": "Irving",            "state": "TX"},
    {"slug": "jacksonville",    "name": "Jacksonville",      "state": "FL"},
    {"slug": "jersey-city",     "name": "Jersey City",       "state": "NJ"},
    {"slug": "kansas-city",     "name": "Kansas City",       "state": "MO"},
    {"slug": "killeen",         "name": "Killeen",           "state": "TX"},
    {"slug": "knoxville",       "name": "Knoxville",         "state": "TN"},
    {"slug": "laredo",          "name": "Laredo",            "state": "TX"},
    {"slug": "las-cruces",      "name": "Las Cruces",        "state": "NM"},
    {"slug": "las-vegas",       "name": "Las Vegas",         "state": "NV"},
    {"slug": "lexington",       "name": "Lexington",         "state": "KY"},
    {"slug": "lincoln",         "name": "Lincoln",           "state": "NE"},
    {"slug": "little-rock",     "name": "Little Rock",       "state": "AR"},
    {"slug": "long-beach",      "name": "Long Beach",        "state": "CA"},
    {"slug": "los-angeles",     "name": "Los Angeles",       "state": "CA"},
    {"slug": "louisville",      "name": "Louisville",        "state": "KY"},
    {"slug": "lubbock",         "name": "Lubbock",           "state": "TX"},
    {"slug": "macon",           "name": "Macon",             "state": "GA"},
    {"slug": "madison",         "name": "Madison",           "state": "WI"},
    {"slug": "mcallen",         "name": "McAllen",           "state": "TX"},
    {"slug": "memphis",         "name": "Memphis",           "state": "TN"},
    {"slug": "mesa",            "name": "Mesa",              "state": "AZ"},
    {"slug": "miami",           "name": "Miami",             "state": "FL"},
    {"slug": "midland",         "name": "Midland",           "state": "TX"},
    {"slug": "milwaukee",       "name": "Milwaukee",         "state": "WI"},
    {"slug": "minneapolis",     "name": "Minneapolis",       "state": "MN"},
    {"slug": "mobile",          "name": "Mobile",            "state": "AL"},
    {"slug": "montgomery",      "name": "Montgomery",        "state": "AL"},
    {"slug": "moreno-valley",   "name": "Moreno Valley",     "state": "CA"},
    {"slug": "nashville",       "name": "Nashville",         "state": "TN"},
    {"slug": "new-orleans",     "name": "New Orleans",       "state": "LA"},
    {"slug": "newark",          "name": "Newark",            "state": "NJ"},
    {"slug": "newport-news",    "name": "Newport News",      "state": "VA"},
    {"slug": "norfolk",         "name": "Norfolk",           "state": "VA"},
    {"slug": "odessa",          "name": "Odessa",            "state": "TX"},
    {"slug": "oklahoma-city",   "name": "Oklahoma City",     "state": "OK"},
    {"slug": "omaha",           "name": "Omaha",             "state": "NE"},
    {"slug": "orlando",         "name": "Orlando",           "state": "FL"},
    {"slug": "oxnard",          "name": "Oxnard",            "state": "CA"},
    {"slug": "pasadena-tx",     "name": "Pasadena",          "state": "TX"},
    {"slug": "philadelphia",    "name": "Philadelphia",      "state": "PA"},
    {"slug": "phoenix",         "name": "Phoenix",           "state": "AZ"},
    {"slug": "pittsburgh",      "name": "Pittsburgh",        "state": "PA"},
    {"slug": "plano",           "name": "Plano",             "state": "TX"},
    {"slug": "portland",        "name": "Portland",          "state": "OR"},
    {"slug": "providence",      "name": "Providence",        "state": "RI"},
    {"slug": "provo",           "name": "Provo",             "state": "UT"},
    {"slug": "pueblo",          "name": "Pueblo",            "state": "CO"},
    {"slug": "raleigh",         "name": "Raleigh",           "state": "NC"},
    {"slug": "reno",            "name": "Reno",              "state": "NV"},
    {"slug": "richmond",        "name": "Richmond",          "state": "VA"},
    {"slug": "riverside",       "name": "Riverside",         "state": "CA"},
    {"slug": "rochester",       "name": "Rochester",         "state": "NY"},
    {"slug": "rockford",        "name": "Rockford",          "state": "IL"},
    {"slug": "sacramento",      "name": "Sacramento",        "state": "CA"},
    {"slug": "salt-lake-city",  "name": "Salt Lake City",    "state": "UT"},
    {"slug": "san-antonio",     "name": "San Antonio",       "state": "TX"},
    {"slug": "san-diego",       "name": "San Diego",         "state": "CA"},
    {"slug": "san-francisco",   "name": "San Francisco",     "state": "CA"},
    {"slug": "san-jose",        "name": "San Jose",          "state": "CA"},
    {"slug": "santa-ana",       "name": "Santa Ana",         "state": "CA"},
    {"slug": "savannah",        "name": "Savannah",          "state": "GA"},
    {"slug": "scottsdale",      "name": "Scottsdale",        "state": "AZ"},
    {"slug": "seattle",         "name": "Seattle",           "state": "WA"},
    {"slug": "shreveport",      "name": "Shreveport",        "state": "LA"},
    {"slug": "sioux-falls",     "name": "Sioux Falls",       "state": "SD"},
    {"slug": "sparks",          "name": "Sparks",            "state": "NV"},
    {"slug": "spokane",         "name": "Spokane",           "state": "WA"},
    {"slug": "spokane-valley",  "name": "Spokane Valley",    "state": "WA"},
    {"slug": "st-louis",        "name": "St. Louis",         "state": "MO"},
    {"slug": "stockton",        "name": "Stockton",          "state": "CA"},
    {"slug": "syracuse",        "name": "Syracuse",          "state": "NY"},
    {"slug": "tacoma",          "name": "Tacoma",            "state": "WA"},
    {"slug": "tallahassee",     "name": "Tallahassee",       "state": "FL"},
    {"slug": "tampa",           "name": "Tampa",             "state": "FL"},
    {"slug": "tempe",           "name": "Tempe",             "state": "AZ"},
    {"slug": "toledo",          "name": "Toledo",            "state": "OH"},
    {"slug": "tucson",          "name": "Tucson",            "state": "AZ"},
    {"slug": "tyler",           "name": "Tyler",             "state": "TX"},
    {"slug": "virginia-beach",  "name": "Virginia Beach",    "state": "VA"},
    {"slug": "waco",            "name": "Waco",              "state": "TX"},
    {"slug": "wichita",         "name": "Wichita",           "state": "KS"},
    {"slug": "winston-salem",   "name": "Winston-Salem",     "state": "NC"},
    {"slug": "worcester",       "name": "Worcester",         "state": "MA"},
    {"slug": "yonkers",         "name": "Yonkers",           "state": "NY"},
]

# ── Shared CSS (identical to HVAC pages) ─────────────────────────────────────
PAGE_CSS = """:root{
  --violet:#6C63FF; --violet-2:#8B85FF; --violet-d:#5A52E0;
  --ink:#0E0E1A; --ink-2:#1A1A2E; --body:#4A4A6A; --muted:#8A8AA8;
  --bg:#F7F7FB; --card:#FFFFFF; --border:#E8E8F0; --line:#EFEFF6;
  --green:#10B981; --red:#EF4444; --amber:#F59E0B;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{overflow-x:clip}
body{font-family:'Inter',system-ui,sans-serif;color:var(--ink-2);background:var(--bg);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.container{max-width:980px;margin:0 auto;padding:0 24px}
#header{position:sticky;top:0;z-index:50;backdrop-filter:saturate(180%) blur(14px);background:rgba(247,247,251,.78);border-bottom:1px solid var(--line)}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;max-width:1560px;margin:0 auto}
.nav-cta{background:var(--violet);color:#fff !important;padding:10px 18px;border-radius:11px;font-weight:600;box-shadow:0 6px 24px -8px rgba(108,99,255,.55);transition:all .2s}
.nav-cta:hover{background:var(--violet-d);transform:translateY(-1px)}
.logo-section{display:inline-flex;align-items:center;gap:12px;text-decoration:none}
footer{padding:56px 0 32px;background:#fff;border-top:1px solid var(--line)}
.footer-content{max-width:980px;margin:0 auto;padding:0 24px}
.footer-bottom{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.footer-copyright{font-size:12px;color:var(--muted)}
.footer-links{list-style:none;display:flex;gap:20px;padding:0;margin:0}
.footer-links a{font-size:12px;color:var(--muted);text-decoration:none}
.footer-links a:hover{color:var(--violet)}
.hero{padding:60px 0 24px;text-align:center}
.hero-tag{display:inline-block;font-size:11px;font-weight:700;color:var(--violet);letter-spacing:.16em;text-transform:uppercase;background:rgba(108,99,255,.08);padding:6px 14px;border-radius:20px;margin-bottom:18px}
.hero h1{font-size:clamp(30px,4.4vw,46px);font-weight:800;line-height:1.12;letter-spacing:-.02em;color:var(--ink);margin-bottom:18px}
.hero h1 .accent{background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:18px;color:var(--body);max-width:720px;margin:0 auto 26px;line-height:1.55}
.hero-cta{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%);color:#fff;padding:16px 32px;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;box-shadow:0 12px 36px -10px rgba(108,99,255,.55);transition:all .2s}
.hero-cta:hover{transform:translateY(-2px);box-shadow:0 16px 44px -10px rgba(108,99,255,.7)}
.hero-fineprint{display:block;margin-top:14px;font-size:12px;color:var(--muted)}
.compare{padding:32px 0}
.compare-card{background:var(--card);border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:0 8px 32px -8px rgba(14,14,26,.06)}
.compare-card::before{content:"";display:block;height:4px;background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%)}
.compare-card-inner{padding:28px 32px}
.compare-card h2{font-size:22px;font-weight:800;color:var(--ink);margin-bottom:6px;letter-spacing:-.015em}
.compare-card-sub{font-size:13px;color:var(--muted);margin-bottom:22px}
table.compare-table{width:100%;border-collapse:collapse;font-size:14px}
.compare-table th,.compare-table td{padding:14px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
.compare-table th{font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}
.compare-table th.col-syntharra,.compare-table td.col-syntharra{background:rgba(108,99,255,.04);color:var(--ink)}
.compare-table td.label{font-weight:600;color:var(--ink-2);width:32%}
.compare-table .yes{color:var(--green);font-weight:700}
.section{padding:36px 0}
.section h2{font-size:24px;font-weight:800;color:var(--ink);margin-bottom:14px;letter-spacing:-.015em}
.section p{font-size:15px;color:var(--body);margin-bottom:14px;line-height:1.7}
.section blockquote{margin:18px 0;padding:14px 18px;border-left:3px solid var(--violet);background:rgba(108,99,255,.03);font-style:italic;font-size:14px;color:var(--ink-2);border-radius:0 10px 10px 0}
.section blockquote cite{display:block;margin-top:8px;font-style:normal;font-size:12px;color:var(--muted);font-weight:600}
.faq{padding:32px 0}
.faq h2{font-size:24px;font-weight:800;color:var(--ink);text-align:center;margin-bottom:24px;letter-spacing:-.015em}
.faq-list{display:flex;flex-direction:column;gap:12px}
.faq-item{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 22px}
.faq-q{font-size:15px;font-weight:700;color:var(--ink);margin-bottom:6px}
.faq-a{font-size:14px;color:var(--body);line-height:1.6}
.final-cta{padding:48px 0 64px;text-align:center}
.final-cta h2{font-size:26px;font-weight:800;color:var(--ink);margin-bottom:12px;letter-spacing:-.015em}
.final-cta p{font-size:15px;color:var(--body);margin-bottom:24px;max-width:560px;margin-left:auto;margin-right:auto}
@media(max-width:680px){
  .container{padding:0 18px}
  .compare-card-inner{padding:22px 18px}
  .compare-table th,.compare-table td{padding:10px 6px;font-size:13px}
}"""

# ── Logo SVG (shared) ─────────────────────────────────────────────────────────
LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="158" height="34" viewBox="0 0 158 34" role="img">
                    <g fill="#6C63FF">
                        <rect x="0"  y="21" width="4" height="9"  rx="1"/>
                        <rect x="7"  y="17" width="4" height="13" rx="1"/>
                        <rect x="14" y="13" width="4" height="17" rx="1"/>
                        <rect x="21" y="9"  width="4" height="21" rx="1"/>
                    </g>
                    <text x="37" y="21" font-family="Inter,Arial,sans-serif" font-weight="700" font-size="16" fill="#1A1A2E" letter-spacing="-0.48">Syntharra</text>
                    <text x="37" y="32" font-family="Inter,Arial,sans-serif" font-weight="500" font-size="8" fill="#6C63FF" letter-spacing="1.2">GLOBAL AI SOLUTIONS</text>
                </svg>'''

FOOTER_HTML = '''    <footer>
        <div class="footer-content">
            <div class="footer-bottom">
                <div class="footer-copyright">&copy; 2026 Syntharra &middot; Global AI Solutions. All rights reserved.</div>
                <ul class="footer-links">
                    <li><a href="/privacy.html">Privacy</a></li>
                    <li><a href="/terms.html">Terms</a></li>
                    <li><a href="mailto:support@syntharra.com">Support</a></li>
                </ul>
            </div>
        </div>
    </footer>'''


# ── Plumbing page generator ───────────────────────────────────────────────────
def build_plumbing_page(c: dict) -> str:
    name  = c["name"]
    state = c["state"]
    slug  = c["slug"]
    utm   = slug.replace("-", "_")

    title       = f"{name} Plumbing Answering Service \u2014 24/7 AI from $697/mo | Syntharra"
    description = (f"{name} plumbing answering service. 24/7 AI receptionist trained on plumbing scripts, "
                   f"flat $697/mo, 700 minutes. Free 200-minute pilot, no credit card, live in 24 hours.")
    canon       = f"https://www.syntharra.com/plumbing-answering-service-{slug}.html"

    faq_items = [
        {
            "q": f"Does the AI understand plumbing emergencies in {name}?",
            "a": (f"Yes. The AI is trained on plumbing terminology — burst pipe, water heater failure, "
                  f"sewer backup, drain clog, flooding basement, no hot water — and classifies calls by "
                  f"urgency instantly. It doesn\u2019t try to diagnose; it captures the symptom accurately "
                  f"so your technician arrives with the right information.")
        },
        {
            "q": "How fast does the AI dispatch after a call?",
            "a": ("Within 30 seconds of ending the call, your cell gets a text: customer name, address, "
                  "symptom description, and urgency level. You decide whether to roll a truck immediately "
                  "or schedule \u2014 the AI gives you the information to make that call in real time.")
        },
        {
            "q": "Can the AI tell the difference between an emergency and a routine job?",
            "a": ("Yes. The AI classifies calls as emergency (active flooding, burst pipe, no water at all) "
                  "vs. scheduled service (slow drain, dripping faucet, water heater making noise). Emergency "
                  "calls trigger an immediate dispatch text; scheduled calls are logged with contact details "
                  "for morning follow-up.")
        },
        {
            "q": f"How does the AI handle call surges during winter pipe-freeze events in {name}?",
            "a": ("The AI handles unlimited concurrent calls. When multiple homeowners call simultaneously "
                  "during a freeze event, all get answered instantly and dispatched in priority order \u2014 "
                  "active flooding and burst pipes first, then no-heat calls, then general service. No busy "
                  "signal, no voicemail, no dropped calls.")
        },
        {
            "q": "What does $697/month include for plumbing shops?",
            "a": ("700 minutes of answered calls per month, 24/7 including nights and weekends. Full call "
                  "transcript and AI summary per call. Emergency SMS dispatch within 30 seconds. Unlimited "
                  "concurrent calls \u2014 no busy signals during surges. Overage at $0.18/min if you exceed "
                  "700 minutes. No setup fee, no per-call charges, no contracts.")
        },
    ]

    faq_html = "\n".join(
        f'                <div class="faq-item"><div class="faq-q">{f["q"]}</div>'
        f'<div class="faq-a">{f["a"]}</div></div>'
        for f in faq_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/favicon.svg">
    <meta name="theme-color" content="#6C63FF">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canon}">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canon}">
    <meta property="og:title" content="{name} Plumbing Answering Service \u2014 24/7 AI from $697/mo">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://www.syntharra.com/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Syntharra">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{canon}">
    <meta name="twitter:title" content="{name} Plumbing Answering Service \u2014 24/7 AI from $697/mo">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://www.syntharra.com/og-image.png">

    <!-- JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Service",
      "name": "{name} Plumbing Answering Service",
      "provider": {{"@type": "Organization", "name": "Syntharra", "url": "https://www.syntharra.com"}},
      "areaServed": {{"@type": "City", "name": "{name}", "addressRegion": "{state}"}},
      "description": "{description}",
      "offers": {{"@type": "Offer", "price": "697", "priceCurrency": "USD", "billingIncrement": "month"}}
    }}
    </script>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
{PAGE_CSS}
    </style>
</head>
<body data-page="plumbing-answering-service-{slug}" data-asset-id="plumbing-{slug}-2026-04">
    <header id="header">
        <div class="header-inner">
            <a href="/" class="logo-section" aria-label="Syntharra \u2014 Global AI Solutions">
                {LOGO_SVG}
            </a>
            <a href="/start" class="nav-cta" data-cta="header">Start free pilot \u2192</a>
        </div>
    </header>

    <main>
        <section class="hero container">
            <div class="hero-tag">Plumbing answering service \u2014 {name}, {state}</div>
            <h1>{name} plumbers \u2014<br><span class="accent">your phone is answered.</span></h1>
            <p class="hero-sub">{name} plumbing contractors lose thousands every month to after-hours calls that go to voicemail. When a homeowner has a burst pipe or flooded basement at midnight, they call until someone answers. Syntharra is a 24/7 AI receptionist trained on plumbing scripts and {name} service areas. Flat $697/month, 700 minutes, free 200-minute pilot, no credit card.</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=plumbing-{slug}-2026-04" class="hero-cta" data-cta="hero">
                Try the free 200-minute pilot \u2192
            </a>
            <span class="hero-fineprint">200 minutes \u00b7 No credit card \u00b7 Live in 24 hours</span>
        </section>

        <section class="section container">
            <h2>Why {name} plumbers need a 24/7 AI answering service</h2>
            <p>Plumbing emergencies don\u2019t follow business hours. A burst pipe, a water heater that fails on a Sunday morning, a sewer backup on a holiday \u2014 these are the calls that determine whether a homeowner becomes your long-term customer or your competitor\u2019s. The contractor who answers first wins the job and the relationship.</p>
            <p>At $697/month flat \u2014 less than a single emergency service call \u2014 Syntharra answers every call in under one second, classifies the urgency (active flooding vs. slow drain), captures contact details and the symptom, and texts your cell within 30 seconds. No voicemail, no missed calls, no lost jobs.</p>
            <p>A single captured after-hours plumbing call typically covers 3\u20134 months of Syntharra\u2019s cost. The math is straightforward.</p>
        </section>

        <section class="compare container">
            <div class="compare-card">
                <div class="compare-card-inner">
                    <h2>What\u2019s included in the $697 flat</h2>
                    <p class="compare-card-sub">No per-call surcharges, no after-hours add-on, no setup fees. {name} plumbing shops, 200-minute pilot pricing.</p>
                    <table class="compare-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="col-syntharra">Included in $697/mo</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="label">Answer every call 24/7</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 midnight, weekends, holidays, burst-pipe emergencies, all included</td>
                            </tr>
                            <tr>
                                <td class="label">Trained on plumbing keywords</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 \u201cburst pipe,\u201d \u201cno hot water,\u201d \u201csewer backup,\u201d \u201cflooded basement,\u201d \u201cwater heater out\u201d</td>
                            </tr>
                            <tr>
                                <td class="label">Auto-dispatch emergencies</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 instant SMS to your cell within 30 seconds</td>
                            </tr>
                            <tr>
                                <td class="label">700 minutes/month</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 unlimited calls in budget; overage only $0.18/min</td>
                            </tr>
                            <tr>
                                <td class="label">Call transcripts + AI summary</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 full transcript, intent, urgency, lead flag per call</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <section class="section container">
            <h2>How it works in a {name} plumbing emergency</h2>
            <p>It\u2019s 1:30 a.m. A homeowner wakes up to water on the floor \u2014 a pipe under the kitchen sink has burst. They\u2019re in a panic. They grab their phone and start calling plumbers. You\u2019re on the list.</p>
            <p>The AI answers on the first ring \u2014 0.4 seconds, not a voicemail beep. It hears the urgency, classifies the call as <code>urgency=emergency</code>, <code>is_lead=true</code>. It responds calmly: <em>\u201cI understand how stressful that is. Let me get your details to a technician right away. Can I confirm your address and a callback number?\u201d</em> Within 30 seconds, your phone gets a text: customer name, address, symptom (burst pipe under kitchen sink), urgency level.</p>
            <p>You call back, confirm the visit, and turn the emergency into a long-term maintenance customer. The first shop on the list sent the call to voicemail and lost both the job and the relationship.</p>
        </section>

        <section class="faq container">
            <h2>{name} plumbing answering service \u2014 common questions</h2>
            <div class="faq-list">
{faq_html}
            </div>
        </section>

        <section class="final-cta container">
            <h2>Stop losing {name} after-hours leads to voicemail.</h2>
            <p>200 minutes. No credit card. Live in 24 hours. If the AI doesn\u2019t pay for itself, you walk away with every transcript and we never charge you.</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=plumbing-{slug}-2026-04" class="hero-cta" data-cta="footer" style="margin:0 auto">
                Start my free 200-minute pilot \u2192
            </a>
        </section>
    </main>

{FOOTER_HTML}
</body>
</html>"""


# ── Electrical page generator ─────────────────────────────────────────────────
def build_electrical_page(c: dict) -> str:
    name  = c["name"]
    state = c["state"]
    slug  = c["slug"]
    utm   = slug.replace("-", "_")

    title       = f"{name} Electrical Answering Service \u2014 24/7 AI from $697/mo | Syntharra"
    description = (f"{name} electrical answering service. 24/7 AI receptionist trained on electrical scripts, "
                   f"flat $697/mo, 700 minutes. Free 200-minute pilot, no credit card, live in 24 hours.")
    canon       = f"https://www.syntharra.com/electrical-answering-service-{slug}.html"

    faq_items = [
        {
            "q": f"Does the AI understand electrical emergencies in {name}?",
            "a": ("Yes. The AI is trained on electrical terminology \u2014 sparking outlet, breaker tripping, "
                  "power outage, no power to circuit, panel issue, burning smell from panel, EV charger "
                  "installation \u2014 and classifies calls by urgency instantly. It captures the symptom "
                  "accurately so your electrician arrives with the right context.")
        },
        {
            "q": "How fast does the AI dispatch after an electrical emergency call?",
            "a": ("Within 30 seconds of ending the call, your cell gets a text: customer name, address, "
                  "symptom description (e.g., \u201csparking outlet in kitchen, burning smell\u201d), and urgency level. "
                  "You decide whether to roll immediately or schedule \u2014 the AI gives you the information "
                  "to make that call in real time.")
        },
        {
            "q": "Can the AI tell the difference between a fire-risk emergency and a routine job?",
            "a": ("Yes. The AI classifies calls as emergency (sparking, burning smell, no power to whole "
                  "panel, tripped main breaker) vs. scheduled (outlet not working, light fixture replacement, "
                  "EV charger quote). Emergency calls trigger an immediate dispatch text; routine calls are "
                  "logged with contact details for morning follow-up.")
        },
        {
            "q": f"How does the AI handle storm-related power call surges in {name}?",
            "a": ("The AI handles unlimited concurrent calls. During storms when multiple homeowners call "
                  "about power issues simultaneously, all get answered instantly and dispatched in priority "
                  "order \u2014 fire-risk situations first (sparking, burning smell), then total power loss, "
                  "then partial outages. No busy signal, no voicemail, no dropped calls.")
        },
        {
            "q": "What does $697/month include for electrical contractors?",
            "a": ("700 minutes of answered calls per month, 24/7 including nights and weekends. Full call "
                  "transcript and AI summary per call. Emergency SMS dispatch within 30 seconds. Unlimited "
                  "concurrent calls \u2014 no busy signals during storms or outages. Overage at $0.18/min if "
                  "you exceed 700 minutes. No setup fee, no per-call charges, no contracts.")
        },
    ]

    faq_html = "\n".join(
        f'                <div class="faq-item"><div class="faq-q">{f["q"]}</div>'
        f'<div class="faq-a">{f["a"]}</div></div>'
        for f in faq_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/favicon.svg">
    <meta name="theme-color" content="#6C63FF">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canon}">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canon}">
    <meta property="og:title" content="{name} Electrical Answering Service \u2014 24/7 AI from $697/mo">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://www.syntharra.com/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Syntharra">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{canon}">
    <meta name="twitter:title" content="{name} Electrical Answering Service \u2014 24/7 AI from $697/mo">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://www.syntharra.com/og-image.png">

    <!-- JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Service",
      "name": "{name} Electrical Answering Service",
      "provider": {{"@type": "Organization", "name": "Syntharra", "url": "https://www.syntharra.com"}},
      "areaServed": {{"@type": "City", "name": "{name}", "addressRegion": "{state}"}},
      "description": "{description}",
      "offers": {{"@type": "Offer", "price": "697", "priceCurrency": "USD", "billingIncrement": "month"}}
    }}
    </script>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
{PAGE_CSS}
    </style>
</head>
<body data-page="electrical-answering-service-{slug}" data-asset-id="electrical-{slug}-2026-04">
    <header id="header">
        <div class="header-inner">
            <a href="/" class="logo-section" aria-label="Syntharra \u2014 Global AI Solutions">
                {LOGO_SVG}
            </a>
            <a href="/start" class="nav-cta" data-cta="header">Start free pilot \u2192</a>
        </div>
    </header>

    <main>
        <section class="hero container">
            <div class="hero-tag">Electrical answering service \u2014 {name}, {state}</div>
            <h1>{name} electricians \u2014<br><span class="accent">your phone is answered.</span></h1>
            <p class="hero-sub">{name} electrical contractors lose jobs every week to after-hours calls that go to voicemail. When a homeowner has sparking outlets or a tripped panel breaker at midnight, they call until someone answers. Syntharra is a 24/7 AI receptionist trained on electrical scripts and {name} service areas. Flat $697/month, 700 minutes, free 200-minute pilot, no credit card.</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=electrical-{slug}-2026-04" class="hero-cta" data-cta="hero">
                Try the free 200-minute pilot \u2192
            </a>
            <span class="hero-fineprint">200 minutes \u00b7 No credit card \u00b7 Live in 24 hours</span>
        </section>

        <section class="section container">
            <h2>Why {name} electricians need a 24/7 AI answering service</h2>
            <p>Electrical emergencies don\u2019t follow business hours. A sparking outlet, a main breaker that trips, power out to half the house on a Sunday night \u2014 these are the calls that determine whether a homeowner becomes your long-term customer or your competitor\u2019s. The electrician who answers first wins the job and the relationship.</p>
            <p>At $697/month flat, Syntharra answers every call in under one second, classifies the urgency (fire-risk emergency vs. routine service), captures contact details and the symptom, and texts your cell within 30 seconds. No voicemail, no missed calls, no lost jobs.</p>
            <p>A single captured after-hours electrical emergency call typically covers multiple months of Syntharra\u2019s cost. The math is straightforward.</p>
        </section>

        <section class="compare container">
            <div class="compare-card">
                <div class="compare-card-inner">
                    <h2>What\u2019s included in the $697 flat</h2>
                    <p class="compare-card-sub">No per-call surcharges, no after-hours add-on, no setup fees. {name} electrical shops, 200-minute pilot pricing.</p>
                    <table class="compare-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="col-syntharra">Included in $697/mo</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="label">Answer every call 24/7</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 midnight, weekends, storm outages, all included</td>
                            </tr>
                            <tr>
                                <td class="label">Trained on electrical keywords</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 \u201csparking outlet,\u201d \u201cbreaker tripping,\u201d \u201cno power,\u201d \u201cburning smell,\u201d \u201cpanel issue\u201d</td>
                            </tr>
                            <tr>
                                <td class="label">Auto-dispatch emergencies</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 instant SMS to your cell within 30 seconds</td>
                            </tr>
                            <tr>
                                <td class="label">700 minutes/month</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 unlimited calls in budget; overage only $0.18/min</td>
                            </tr>
                            <tr>
                                <td class="label">Call transcripts + AI summary</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 full transcript, intent, urgency, lead flag per call</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <section class="section container">
            <h2>How it works in a {name} electrical emergency</h2>
            <p>It\u2019s 11:45 p.m. A homeowner smells something burning near the outlet in the living room. They check the panel \u2014 a breaker tripped. They reset it, it trips again. They\u2019re worried. They grab their phone and start calling electricians. You\u2019re on the list.</p>
            <p>The AI answers on the first ring \u2014 0.4 seconds, not a voicemail beep. It hears the urgency, classifies the call as <code>urgency=emergency</code>, <code>is_lead=true</code>. It responds calmly: <em>\u201cI understand that\u2019s concerning. Let me get your details to a technician right away. Can I confirm your address and a callback number?\u201d</em> Within 30 seconds, your phone gets a text: customer name, address, symptom (breaker tripping + burning smell), urgency level.</p>
            <p>You call back, confirm the visit, and turn the emergency into a long-term service customer. The first shop on the list sent the call to voicemail and lost both the job and the relationship.</p>
        </section>

        <section class="faq container">
            <h2>{name} electrical answering service \u2014 common questions</h2>
            <div class="faq-list">
{faq_html}
            </div>
        </section>

        <section class="final-cta container">
            <h2>Stop losing {name} after-hours leads to voicemail.</h2>
            <p>200 minutes. No credit card. Live in 24 hours. If the AI doesn\u2019t pay for itself, you walk away with every transcript and we never charge you.</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=electrical-{slug}-2026-04" class="hero-cta" data-cta="footer" style="margin:0 auto">
                Start my free 200-minute pilot \u2192
            </a>
        </section>
    </main>

{FOOTER_HTML}
</body>
</html>"""


# ── GitHub API helpers ────────────────────────────────────────────────────────
def gh_get(path: str) -> dict:
    url = f"{API}/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise


def gh_put(path: str, content: str, message: str, sha: str | None = None) -> bool:
    url = f"{API}/{path}"
    payload: dict = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
    }
    if sha:
        payload["sha"] = sha
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code}: {e.read().decode()[:200]}")
        return False


def push_page(filename: str, html: str, skip_existing: bool) -> bool:
    existing = gh_get(filename)
    sha = existing.get("sha")
    if sha and skip_existing:
        print(f"  SKIP {filename} (exists)")
        return True
    msg = f"feat(seo): add {filename}"
    ok = gh_put(filename, html, msg, sha)
    status = "OK" if ok else "FAIL"
    print(f"  {status} → {filename}")
    return ok


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plumbing",      action="store_true", help="Plumbing pages only")
    parser.add_argument("--electrical",    action="store_true", help="Electrical pages only")
    parser.add_argument("--dry-run",       action="store_true", help="Print filenames, don't push")
    parser.add_argument("--skip-existing", action="store_true", help="Skip already-existing files")
    parser.add_argument("--start",         type=int, default=0,  help="Start at city index N (for resuming)")
    args = parser.parse_args()

    do_plumbing   = args.plumbing   or (not args.plumbing and not args.electrical)
    do_electrical = args.electrical or (not args.plumbing and not args.electrical)

    cities = CITIES[args.start:]
    total = len(cities) * (do_plumbing + do_electrical)
    print(f"Generating {total} pages for {len(cities)} cities "
          f"(plumbing={do_plumbing}, electrical={do_electrical})")
    print(f"Starting from index {args.start}")
    print()

    pushed = 0
    failed = 0

    for i, city in enumerate(cities, start=args.start):
        print(f"[{i+1}/{len(CITIES)}] {city['name']}, {city['state']}")

        if do_plumbing:
            filename = f"plumbing-answering-service-{city['slug']}.html"
            if args.dry_run:
                print(f"  DRY {filename}")
            else:
                html = build_plumbing_page(city)
                assert html.count("<style>") == 1, f"Multiple style blocks in {filename}"
                ok = push_page(filename, html, args.skip_existing)
                if ok:
                    pushed += 1
                else:
                    failed += 1
                time.sleep(0.8)

        if do_electrical:
            filename = f"electrical-answering-service-{city['slug']}.html"
            if args.dry_run:
                print(f"  DRY {filename}")
            else:
                html = build_electrical_page(city)
                assert html.count("<style>") == 1, f"Multiple style blocks in {filename}"
                ok = push_page(filename, html, args.skip_existing)
                if ok:
                    pushed += 1
                else:
                    failed += 1
                time.sleep(0.8)

    print()
    print(f"Done. Pushed: {pushed}  Failed: {failed}")
    if failed > 0:
        print("Re-run with --start N --skip-existing to retry failed cities.")


if __name__ == "__main__":
    main()
