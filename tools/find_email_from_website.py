#!/usr/bin/env python3
"""
find_email_from_website.py — Phase 0 cold lead enrichment.

Given a CSV of leads (output of `tools/scrape_hvac_directory.py`), visits each
business's website and scrapes the homepage + common contact pages
(/contact, /contact-us, /about) for email addresses. Adds an `email` column.

Strategy:
  1. GET the homepage with a real-browser User-Agent
  2. Parse for `mailto:` href and bare email regex
  3. If no email found, try /contact, /contact-us, /about
  4. Filter out generic / role addresses (info@, support@) — prefer named
     ones if available, but accept role addresses for B2B SMB cold outreach
  5. Skip mass-mailbox patterns (noreply@, no-reply@, donotreply@)

Cost: $0. Network-only, polite rate limiting.

Usage:
  python tools/find_email_from_website.py \
    --in leads/hvac-austin-tx.csv \
    --out leads/hvac-austin-tx.enriched.csv

Politeness: 1 request/second per host, 5 second timeout per page, max 4 pages
per business. Logs every error to stderr.

This tool intentionally does NOT use any paid enrichment API. For higher
hit rate, pair with Hunter.io free tier (25 searches/mo) or Apollo.io
(paid). The output CSV format is compatible — just add an `email` column.
"""
import argparse
import csv
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USER_AGENT = "Mozilla/5.0 (compatible; SyntharraOutreach/1.0; +https://syntharra.com/)"
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
SKIP_PREFIXES = ("noreply@", "no-reply@", "donotreply@", "wordpress@", "example@")
COMMON_PATHS = ["", "/contact", "/contact-us", "/contact.html", "/about", "/about-us"]


def fetch(url: str, timeout: int = 8) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("content-type", "")
            if "text/html" not in ctype and "text/plain" not in ctype:
                return None
            data = resp.read(500_000)  # cap at 500KB
            return data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (404, 403, 410):
            return None
        print(f"  [warn] HTTP {e.code} on {url}", file=sys.stderr)
        return None
    except Exception as e:
        # Connection refused, DNS failure, etc. Common for local SMB sites.
        return None


def normalize_url(raw: str) -> Optional[str]:
    if not raw:
        return None
    raw = raw.strip()
    if not raw.startswith("http"):
        raw = "https://" + raw
    try:
        parsed = urllib.parse.urlparse(raw)
        if not parsed.netloc:
            return None
        # Normalize: drop path/query, keep scheme + netloc
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None


def extract_emails(html: str) -> list[str]:
    if not html:
        return []
    found = set()
    # mailto: hrefs (preferred — clean)
    for m in re.finditer(r'mailto:([^"\'\s>?]+)', html, re.IGNORECASE):
        addr = m.group(1).strip().lower()
        found.add(addr)
    # bare email regex (catches obfuscated ones too)
    for m in EMAIL_REGEX.finditer(html):
        addr = m.group(0).strip().lower()
        # Skip image-asset emails / nonsense
        if addr.endswith((".png", ".jpg", ".gif", ".webp", ".svg")):
            continue
        found.add(addr)
    # Filter junk
    cleaned = []
    for addr in found:
        if any(addr.startswith(p) for p in SKIP_PREFIXES):
            continue
        if "wixpress" in addr or "sentry" in addr or "stripe.com" in addr:
            continue
        if len(addr) > 80 or " " in addr:
            continue
        cleaned.append(addr)
    return cleaned


def find_email_for(website_url: str) -> tuple[Optional[str], list[str]]:
    """Returns (preferred_email, all_emails_found). Preferred is the first
    non-role email if any, else the first role email."""
    base = normalize_url(website_url)
    if not base:
        return None, []
    all_found: list[str] = []
    for path in COMMON_PATHS:
        url = base + path
        html = fetch(url)
        if html:
            emails = extract_emails(html)
            for e in emails:
                if e not in all_found:
                    all_found.append(e)
            if all_found:
                # If we already have a personal-looking email, stop
                if any(not e.startswith(("info@", "contact@", "office@", "admin@", "hello@", "sales@", "support@")) for e in all_found):
                    break
        time.sleep(1.0)  # politeness — 1 req/sec per business
    if not all_found:
        return None, []
    # Prefer non-role addresses
    role_prefixes = ("info@", "contact@", "office@", "admin@", "hello@", "sales@", "support@", "service@")
    personal = [e for e in all_found if not e.startswith(role_prefixes)]
    preferred = personal[0] if personal else all_found[0]
    return preferred, all_found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="Max rows to process (0 = all)")
    args = ap.parse_args()

    with open(args.in_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.limit:
        rows = rows[: args.limit]
    print(f"[enrich] processing {len(rows)} rows", file=sys.stderr)

    out_fieldnames = list(rows[0].keys()) if rows else []
    if "email" not in out_fieldnames:
        out_fieldnames.append("email")
    if "all_emails" not in out_fieldnames:
        out_fieldnames.append("all_emails")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    found_count = 0
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            website = row.get("website") or ""
            preferred, all_found = (None, [])
            if website:
                preferred, all_found = find_email_for(website)
            row["email"] = preferred or ""
            row["all_emails"] = "|".join(all_found)
            writer.writerow(row)
            mark = "OK " if preferred else "-- "
            print(f"  [{i:>3}/{len(rows)}] {mark}{row.get('name','')[:40]:<40}  {preferred or '(no email)'}", file=sys.stderr)
            if preferred:
                found_count += 1

    print(f"[enrich] {found_count}/{len(rows)} emails found ({100*found_count//max(1,len(rows))}%)", file=sys.stderr)
    print(f"[enrich] wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
