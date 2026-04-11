#!/usr/bin/env python3
"""
Syntharra SEO Fixes - Part 2
- faq.html: fix og:title, og:image, complete Twitter card
- All other pages with GitHub icon: replace og:image
- 25 city pages: trim titles to <=60 chars + fix og:image + trim descriptions
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, base64, time, re

TOKEN = "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"
REPO  = "Syntharra/syntharra-website"
API   = f"https://api.github.com/repos/{REPO}/contents"
H     = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

ICON = "https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png"
OG   = "https://www.syntharra.com/og-image.png"

def fetch(filename):
    r = requests.get(f"{API}/{filename}", headers=H)
    if r.status_code != 200:
        raise Exception(f"Fetch {filename}: {r.status_code} {r.text[:120]}")
    d = r.json()
    return d["sha"], base64.b64decode(d["content"]).decode("utf-8")

def push(filename, content, sha, msg):
    payload = {
        "message": msg,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    r = requests.put(f"{API}/{filename}", headers=H, json=payload)
    ok = r.status_code in (200, 201)
    print(f"  [{'PUSHED' if ok else 'FAILED'}] {filename} [{r.status_code}]")
    if not ok:
        print(f"    Error: {r.text[:300]}")
    time.sleep(1.5)
    return ok

def sub(content, old, new, label):
    if old not in content:
        print(f"  [WARN] NOT FOUND: {label}")
        return content
    print(f"  [OK] replaced: {label}")
    return content.replace(old, new, 1)


# ───────────────────────────────────────────────────────────────────────
# 1. faq.html — fix og:title, fix og:image, complete Twitter card
# ───────────────────────────────────────────────────────────────────────
print("\n=== 1. faq.html ===")
sha, c = fetch("faq.html")

# Fix og:title ("FAQ | Syntharra" -> keyword-rich)
c = sub(c,
    'content="FAQ | Syntharra"',
    'content="HVAC AI Answering Service FAQ | Syntharra"',
    "faq og:title enrich")

# Fix og:image (GitHub icon -> branded og-image)
if ICON in c:
    c = c.replace(ICON, OG)
    print("  [OK] replaced: faq og:image")

# Add og:image:width/height right after og:image tag
if 'og:image:width' not in c:
    c = c.replace(
        f'<meta property="og:image" content="{OG}">',
        (f'<meta property="og:image" content="{OG}">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">')
    )
    print("  [OK] added: faq og:image:width/height")

# Complete Twitter card (currently only has twitter:card, missing title/description/image)
if 'twitter:title' not in c:
    c = sub(c,
        '<meta name="twitter:card" content="summary_large_image">',
        ('<meta name="twitter:card" content="summary_large_image">\n'
         '<meta name="twitter:title" content="HVAC AI Answering Service FAQ | Syntharra">\n'
         '<meta name="twitter:description" content="Every question answered about Syntharra\'s AI receptionist'
         ' -- pricing, setup, integrations, call handling, and 24/7 availability.">\n'
         '<meta name="twitter:image" content="https://www.syntharra.com/og-image.png">'),
        "faq twitter card complete")

push("faq.html", c, sha, "seo(P0): fix og:title, fix og:image, complete Twitter card")


# ───────────────────────────────────────────────────────────────────────
# 2. Other pages with GitHub icon og:image (scan individually)
# ───────────────────────────────────────────────────────────────────────
print("\n=== 2. Remaining pages with icon og:image ===")

ICON_PAGES = [
    "hvac.html",
    "plumbing.html",
    "electrical.html",
    "about.html",
    "calculator.html",
    "ai-readiness.html",
    "affiliate.html",
    "plan-quiz.html",
    "careers.html",
    # comparison pages
    "vs-answering-service.html",
    "best-hvac-answering-service.html",
]

for filename in ICON_PAGES:
    try:
        sha, c = fetch(filename)
        if ICON not in c:
            print(f"  [SKIP] {filename} -- icon not present")
            continue
        orig = c
        c = c.replace(ICON, OG)
        # Add width/height if og:image:width missing
        if 'og:image:width' not in c:
            c = c.replace(
                f'<meta property="og:image" content="{OG}">',
                (f'<meta property="og:image" content="{OG}">\n'
                 '<meta property="og:image:width" content="1200">\n'
                 '<meta property="og:image:height" content="630">')
            )
        assert c != orig, f"{filename}: no changes made"
        push(filename, c, sha, "seo(P0): replace icon og:image with branded 1200x630 og-image.png")
    except AssertionError as e:
        print(f"  [WARN] {e}")
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")


# ───────────────────────────────────────────────────────────────────────
# 3. 25 city pages — trim title to <=60 chars + fix og:image + trim description
# ───────────────────────────────────────────────────────────────────────
print("\n=== 3. City pages (25) ===")

CITIES = [
    "albuquerque", "atlanta", "austin", "birmingham", "charlotte",
    "columbus", "dallas", "denver", "el-paso", "fort-worth",
    "houston", "indianapolis", "jacksonville", "las-vegas", "memphis",
    "miami", "nashville", "new-orleans", "oklahoma-city", "orlando",
    "phoenix", "raleigh", "san-antonio", "tampa", "tucson",
]

EM_DASH = "\u2014"  # unicode em dash used in city page titles

ok_count = 0
fail_count = 0

for city in CITIES:
    filename = f"hvac-answering-service-{city}.html"
    try:
        sha, c = fetch(filename)
        orig = c
        changed = []

        # Fix title: "{City} HVAC Answering Service — 24/7 AI from $697/mo | Syntharra"
        #         -> "{City} HVAC Answering Service | 24/7 AI | Syntharra"
        old_title_suffix = f" {EM_DASH} 24/7 AI from $697/mo | Syntharra"
        new_title_suffix = " | 24/7 AI | Syntharra"
        if old_title_suffix in c:
            c = c.replace(old_title_suffix, new_title_suffix)
            changed.append("title trimmed")

        # Fix meta description: remove ", 700 minutes" to trim to <=160 chars
        if ", 700 minutes" in c:
            c = c.replace(", 700 minutes", "")
            changed.append("description trimmed")

        # Fix og:image
        if ICON in c:
            c = c.replace(ICON, OG)
            changed.append("og:image fixed")

        # Add og:image dimensions if missing
        if OG in c and 'og:image:width' not in c:
            c = c.replace(
                f'<meta property="og:image" content="{OG}">',
                (f'<meta property="og:image" content="{OG}">\n'
                 '<meta property="og:image:width" content="1200">\n'
                 '<meta property="og:image:height" content="630">')
            )
            changed.append("og:image dims added")

        if c == orig:
            print(f"  [SKIP] {filename} -- no changes needed")
            continue

        push(filename, c, sha,
             f"seo: trim title/desc, fix og:image [{', '.join(changed)}]")
        ok_count += 1

    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")
        fail_count += 1

print(f"\n  City pages: {ok_count} pushed, {fail_count} errors")
print("\n=== Part 2 complete. Run seo_fixes_p3.py for city hub page. ===")
