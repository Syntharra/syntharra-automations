#!/usr/bin/env python3
"""
generate_sitemap.py — Syntharra sitemap generator
Reads all .html files from ../syntharra-website/ and writes sitemap.xml.

Usage:
    python tools/generate_sitemap.py

Priority rules:
    - index.html          → 1.0
    - vs-*.html           → 0.8  (competitor comparison pages)
    - *hvac-*.html        → 0.8  (city / HVAC-specific pages)
    - lp/*.html           → 0.8  (landing pages)
    - blog/*.html         → 0.6
    - everything else     → 0.6

Excluded from sitemap (non-indexable pages):
    - dashboard.html
    - setup-in-progress.html
    - unsubscribe.html
    - preview.html
    - template.html
    - index-backup.html
    - _template/ directory
"""

import os
import glob
from pathlib import Path
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR     = Path(__file__).parent
WEBSITE_DIR    = (SCRIPT_DIR / ".." / ".." / "syntharra-website").resolve()
SITEMAP_OUT    = WEBSITE_DIR / "sitemap.xml"
ROBOTS_OUT     = WEBSITE_DIR / "robots.txt"
BASE_URL       = "https://syntharra.com"
LASTMOD        = date.today().isoformat()          # e.g. 2026-04-11
CHANGEFREQ     = "weekly"

# Pages to exclude from sitemap entirely
EXCLUDE_FILES = {
    "dashboard.html",
    "setup-in-progress.html",
    "unsubscribe.html",
    "preview.html",
    "template.html",
    "index-backup.html",
}

EXCLUDE_DIRS = {"_template"}


def get_priority(rel_path: str) -> str:
    """Return sitemap priority string for a given relative path."""
    name = os.path.basename(rel_path)
    parts = Path(rel_path).parts

    if rel_path == "index.html":
        return "1.0"

    # Skip files inside excluded dirs
    if any(part in EXCLUDE_DIRS for part in parts):
        return None  # signal to skip

    # Competitor comparison pages (vs-*.html at root level)
    if name.startswith("vs-") and len(parts) == 1:
        return "0.8"

    # HVAC city/service pages (hvac-*.html or *-hvac-*.html at root level)
    if ("hvac" in name) and len(parts) == 1:
        return "0.8"

    # best-hvac-answering-service.html
    if name == "best-hvac-answering-service.html":
        return "0.8"

    # Landing pages (lp/)
    if parts[0] == "lp":
        return "0.8"

    # Blog posts
    if parts[0] == "blog":
        return "0.6"

    # Everything else
    return "0.6"


def build_url_entry(rel_path: str) -> str | None:
    """Build a <url> XML block for the given relative path."""
    name = os.path.basename(rel_path)

    # Excluded files
    if name in EXCLUDE_FILES:
        return None

    priority = get_priority(rel_path)
    if priority is None:
        return None

    # Build canonical URL
    if rel_path == "index.html":
        loc = f"{BASE_URL}/"
    else:
        # Forward-slash the path (important on Windows)
        url_path = rel_path.replace("\\", "/")
        loc = f"{BASE_URL}/{url_path}"

    return (
        f"  <url>"
        f"<loc>{loc}</loc>"
        f"<lastmod>{LASTMOD}</lastmod>"
        f"<changefreq>{CHANGEFREQ}</changefreq>"
        f"<priority>{priority}</priority>"
        f"</url>"
    )


def collect_html_files() -> list[str]:
    """Return sorted list of relative .html paths found under WEBSITE_DIR."""
    all_files = []
    for path in WEBSITE_DIR.rglob("*.html"):
        # Get relative path from website root
        rel = path.relative_to(WEBSITE_DIR)
        rel_str = str(rel)
        # Skip files in excluded directories
        parts = Path(rel_str).parts
        if any(part in EXCLUDE_DIRS for part in parts):
            continue
        all_files.append(rel_str)

    # Sort: index.html first, then root-level files, then subdirectories
    def sort_key(p):
        parts = Path(p).parts
        depth = len(parts)
        name = parts[-1]
        if p == "index.html":
            return (0, "", "")
        if depth == 1:
            return (1, "", name)
        return (2, parts[0], name)

    all_files.sort(key=sort_key)
    return all_files


def write_sitemap(entries: list[str]) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.extend(entries)
    lines.append("</urlset>")
    content = "\n".join(lines) + "\n"
    SITEMAP_OUT.write_text(content, encoding="utf-8")
    print(f"[OK] sitemap.xml written: {SITEMAP_OUT}")
    print(f"     {len(entries)} URLs included")


def ensure_robots_txt() -> None:
    """Create robots.txt if it doesn't already exist."""
    if ROBOTS_OUT.exists():
        # Verify it already references the sitemap; if not, warn
        content = ROBOTS_OUT.read_text(encoding="utf-8")
        if "sitemap.xml" not in content.lower():
            print(f"[WARN] robots.txt exists but has no Sitemap directive — please add:")
            print(f"       Sitemap: {BASE_URL}/sitemap.xml")
        else:
            print("[OK] robots.txt already exists and references sitemap")
        return

    robots_content = f"""# Syntharra robots.txt
# AI Receptionist for trade businesses - syntharra.com

User-agent: *
Allow: /
Disallow: /dashboard.html
Disallow: /setup-in-progress.html
Disallow: /unsubscribe.html
Disallow: /preview.html
Disallow: /template.html
Disallow: /_template/
Disallow: /index-backup.html

# AI crawlers - explicitly allowed (AEO/GEO)
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    ROBOTS_OUT.write_text(robots_content, encoding="utf-8")
    print(f"[CREATED] robots.txt: {ROBOTS_OUT}")


def main():
    print(f"Syntharra Sitemap Generator")
    print(f"Website dir : {WEBSITE_DIR}")
    print(f"Lastmod     : {LASTMOD}")
    print()

    html_files = collect_html_files()
    print(f"Found {len(html_files)} HTML files:")
    for f in html_files:
        print(f"  {f}")
    print()

    entries = []
    skipped = []
    for f in html_files:
        entry = build_url_entry(f)
        if entry:
            entries.append(entry)
        else:
            skipped.append(f)

    if skipped:
        print(f"Excluded from sitemap ({len(skipped)} files):")
        for s in skipped:
            print(f"  {s}")
        print()

    write_sitemap(entries)
    ensure_robots_txt()


if __name__ == "__main__":
    main()
