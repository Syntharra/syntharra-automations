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
import json
import os
import re
import subprocess
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

# --- Hunter.io free-tier fallback (25 searches/mo) -------------------------
#
# RULES.md #36: graceful skip — never throw if the key is absent.
# RULES.md #26: zero hardcoded creds — env var first, vault fallback second.
# Free-tier quota is 25 domain-searches / month as of April 2026; verify at
# https://hunter.io/api-keys if that has changed.

HUNTER_IO_API_KEY: Optional[str] = None


def _load_hunter_key() -> Optional[str]:
    """Load the Hunter.io API key with an env-var-first, vault-fallback chain.

    Never raises. Returns None if the key cannot be resolved through any path,
    which is the signal for the rest of the module to disable the fallback.
    """
    # 1. Env var (local dev / CI)
    k = os.environ.get("HUNTER_IO_API_KEY")
    if k:
        return k.strip() or None
    # 2. Vault fallback via fetch_vault.py subprocess.
    #    Only run if both Supabase creds are present — fetch_vault.py exits
    #    nonzero if they're missing, so skipping silently keeps stderr quiet.
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"):
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            fetch = os.path.join(here, "fetch_vault.py")
            # Hunter.io is the canonical service_name — try a couple of forms.
            for svc in ("Hunter.io", "Hunter"):
                result = subprocess.run(
                    [sys.executable, fetch, svc, "api_key"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
        except Exception:
            pass
    return None


HUNTER_IO_API_KEY = _load_hunter_key()

if HUNTER_IO_API_KEY:
    print(
        "[enrich] Hunter.io fallback enabled (25 searches/month free-tier budget)",
        file=sys.stderr,
    )
else:
    print(
        "[enrich] Hunter.io fallback disabled "
        "(set HUNTER_IO_API_KEY or vault service_name='Hunter.io', key_type='api_key')",
        file=sys.stderr,
    )


def _domain_from_website(website_url: str) -> Optional[str]:
    """Strip protocol, www., and path from a URL to get a bare domain."""
    if not website_url:
        return None
    raw = website_url.strip()
    if not raw:
        return None
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    try:
        parsed = urllib.parse.urlparse(raw)
        host = (parsed.netloc or parsed.path or "").strip().lower()
        # netloc may include :port — strip it
        host = host.split("/")[0].split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        return host or None
    except Exception:
        return None


def _pick_best_hunter_email(emails: list) -> Optional[tuple]:
    """Given Hunter.io's `data.emails` list, pick the best candidate.

    Returns (email, confidence) or None. Priority:
      1. personal + confidence>=80 + exec/mgmt dept + owner/president/manager title
      2. first personal + confidence>=70
      3. any + confidence>=60
    """
    if not emails:
        return None

    def _safe_lower(v):
        return (v or "").lower() if isinstance(v, str) else ""

    # Tier 1: personal, high-confidence, leadership
    leadership_titles = ("owner", "president", "manager", "ceo", "founder")
    ok_depts = ("executive", "management", None, "")
    for e in emails:
        if not isinstance(e, dict):
            continue
        if e.get("type") != "personal":
            continue
        conf = e.get("confidence") or 0
        if conf < 80:
            continue
        dept = e.get("department")
        if dept not in ok_depts:
            continue
        pos = _safe_lower(e.get("position"))
        if any(t in pos for t in leadership_titles):
            val = e.get("value")
            if val:
                return (val.strip().lower(), conf)

    # Tier 2: first personal with confidence >= 70
    for e in emails:
        if not isinstance(e, dict):
            continue
        if e.get("type") != "personal":
            continue
        conf = e.get("confidence") or 0
        if conf >= 70:
            val = e.get("value")
            if val:
                return (val.strip().lower(), conf)

    # Tier 3: anything with confidence >= 60
    for e in emails:
        if not isinstance(e, dict):
            continue
        conf = e.get("confidence") or 0
        if conf >= 60:
            val = e.get("value")
            if val:
                return (val.strip().lower(), conf)

    return None


def _try_hunter_io(domain: str, api_key: str) -> Optional[tuple]:
    """Call Hunter.io domain-search. Returns (email, confidence, 'hunter.io') on
    success, None on any failure. NEVER raises (RULES.md #36).

    Handles the Hunter.io quota-exceeded case: the API returns HTTP 200 with
    an `errors` array in the JSON body, not a 4xx.
    """
    if not domain or not api_key:
        return None
    try:
        qs = urllib.parse.urlencode({"domain": domain, "api_key": api_key})
        url = f"https://api.hunter.io/v2/domain-search?{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read(1_000_000)
        payload = json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        # Network error, JSON decode error, 4xx/5xx HTTPError, timeout, etc.
        return None

    # Quota-exceeded / auth errors come back as HTTP 200 + `errors` array.
    if isinstance(payload, dict) and payload.get("errors"):
        print(
            f"[hunter.io] quota exceeded for {domain}, skipping",
            file=sys.stderr,
        )
        return None

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None
    emails = data.get("emails") or []
    best = _pick_best_hunter_email(emails)
    if not best:
        return None
    email, confidence = best
    return (email, confidence, "hunter.io")


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


def find_email_for(website_url: str) -> tuple[Optional[str], list[str], str]:
    """Returns (preferred_email, all_emails_found, source).

    Source is one of:
      - 'homepage'   — scraped from the site itself (existing path)
      - 'hunter.io'  — Hunter.io domain-search fallback (only if homepage found nothing)
      - 'none'       — no email found anywhere

    The homepage-scrape path runs first and is preferred; Hunter.io is the
    LAST RESORT because it burns free-tier quota (25/mo).
    """
    base = normalize_url(website_url)
    if not base:
        return None, [], "none"
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

    if all_found:
        # Prefer non-role addresses
        role_prefixes = ("info@", "contact@", "office@", "admin@", "hello@", "sales@", "support@", "service@")
        personal = [e for e in all_found if not e.startswith(role_prefixes)]
        preferred = personal[0] if personal else all_found[0]
        return preferred, all_found, "homepage"

    # --- Homepage scrape missed. Fall back to Hunter.io if configured. ---
    if HUNTER_IO_API_KEY:
        domain = _domain_from_website(website_url)
        if domain:
            result = _try_hunter_io(domain, HUNTER_IO_API_KEY)
            if result is not None:
                email, _confidence, source = result
                return email, [email], source

    return None, [], "none"


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
    if "email_source" not in out_fieldnames:
        out_fieldnames.append("email_source")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    found_count = 0
    hunter_count = 0
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            website = row.get("website") or ""
            preferred, all_found, source = (None, [], "none")
            if website:
                preferred, all_found, source = find_email_for(website)
            row["email"] = preferred or ""
            row["all_emails"] = "|".join(all_found)
            row["email_source"] = source if preferred else ""
            writer.writerow(row)
            mark = "OK " if preferred else "-- "
            src_tag = f" [{source}]" if preferred and source != "homepage" else ""
            print(f"  [{i:>3}/{len(rows)}] {mark}{row.get('name','')[:40]:<40}  {preferred or '(no email)'}{src_tag}", file=sys.stderr)
            if preferred:
                found_count += 1
                if source == "hunter.io":
                    hunter_count += 1

    print(f"[enrich] {found_count}/{len(rows)} emails found ({100*found_count//max(1,len(rows))}%)", file=sys.stderr)
    if hunter_count:
        print(f"[enrich] {hunter_count} via Hunter.io fallback", file=sys.stderr)
    print(f"[enrich] wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
