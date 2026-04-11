#!/usr/bin/env python3
"""
fix_city_pages.py — P0 cleanup for 25 HVAC city landing pages.

Operates on the sibling syntharra-website repo. Applies these changes to each
hvac-answering-service-{city}.html file:

  1. Remove placeholder `+1-000-000-0000` telephone from LocalBusiness JSON-LD.
  2. Replace "14-day" / "14 day" copy with "200-minute" pilot language.
  3. Strip any CRM / calendar integration claims (Syntharra has none).
  4. Append a cross-linking "other-cities" footer section (SEO siloing fix).
  5. Append the matching CSS rules inside the existing single <style> block.
  6. Verify LocalBusiness JSON-LD has no fake price / aggregateRating.
  7. Sanity-check: exactly one <style> block and every JSON-LD block still parses.

Run once, commit locally in the website repo, do not push.

Usage:
    python tools/fix_city_pages.py [--check]

    --check  Dry-run: apply transforms in memory and print per-file diff summary
             but do not write to disk.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_AUTOMATIONS = Path(__file__).resolve().parent.parent
REPO_WEBSITE = REPO_AUTOMATIONS.parent / "syntharra-website"

CITY_SLUGS = [
    "albuquerque",
    "atlanta",
    "austin",
    "birmingham",
    "charlotte",
    "columbus",
    "dallas",
    "denver",
    "el-paso",
    "fort-worth",
    "houston",
    "indianapolis",
    "jacksonville",
    "las-vegas",
    "memphis",
    "miami",
    "nashville",
    "new-orleans",
    "oklahoma-city",
    "orlando",
    "phoenix",
    "raleigh",
    "san-antonio",
    "tampa",
    "tucson",
]

# Slug -> display name (handles multi-word slugs).
SPECIAL_CASE_NAMES = {
    "el-paso": "El Paso",
    "fort-worth": "Fort Worth",
    "las-vegas": "Las Vegas",
    "new-orleans": "New Orleans",
    "oklahoma-city": "Oklahoma City",
    "san-antonio": "San Antonio",
}


def slug_to_display(slug: str) -> str:
    if slug in SPECIAL_CASE_NAMES:
        return SPECIAL_CASE_NAMES[slug]
    return slug.title()


# ---------------------------------------------------------------------------
# CSS + section block templates
# ---------------------------------------------------------------------------

OTHER_CITIES_CSS = """
/* Cross-linking footer (added by fix_city_pages.py) */
.other-cities { padding: 48px 32px; background: #FAFAFA; border-top: 1px solid #E5E7EB; }
.other-cities h2 { font-size: 22px; font-weight: 700; color: #1A1A2E; margin-bottom: 8px; text-align: center; }
.other-cities p { font-size: 14px; color: #4A4A6A; text-align: center; margin-bottom: 24px; }
.other-cities-list { list-style: none; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px 16px; max-width: 900px; margin: 0 auto; padding: 0; }
.other-cities-list a { color: #6C63FF; text-decoration: none; font-size: 14px; font-weight: 500; padding: 6px 10px; border-radius: 6px; transition: background 0.15s; }
.other-cities-list a:hover { background: rgba(108,99,255,0.08); }
"""

# Sentinel so re-runs are idempotent.
CSS_SENTINEL = "/* Cross-linking footer (added by fix_city_pages.py) */"
SECTION_SENTINEL = '<section class="other-cities">'


def build_other_cities_section(current_slug: str) -> str:
    items: list[str] = []
    for slug in CITY_SLUGS:
        if slug == current_slug:
            continue
        display = slug_to_display(slug)
        items.append(
            f'      <li><a href="/hvac-answering-service-{slug}.html">{display}</a></li>'
        )
    lis = "\n".join(items)
    return (
        '    <section class="other-cities">\n'
        '      <div class="container">\n'
        '        <h2>HVAC answering service in other cities</h2>\n'
        '        <p>Syntharra serves HVAC contractors nationwide. Explore our other service areas:</p>\n'
        '        <ul class="other-cities-list">\n'
        f'{lis}\n'
        '        </ul>\n'
        '      </div>\n'
        '    </section>\n\n'
    )


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

# Order matters: long phrases before short ones so "14-day pilot" is replaced
# before a bare "14-day" would swallow it into the wrong text.
COPY_REPLACEMENTS: list[tuple[str, str]] = [
    # Meta/og/twitter descriptions
    (
        "Free 14-day pilot, no credit card, live in 24 hours.",
        "Free 200-minute pilot, no credit card, live in 24 hours.",
    ),
    # Hero sub paragraph
    ("free 14-day pilot.", "free 200-minute pilot."),
    # CTA buttons
    ("Try the free 14-day pilot \u2192", "Try the free 200-minute pilot \u2192"),
    ("Start my free 14-day pilot \u2192", "Start my free 200-minute pilot \u2192"),
    # Final CTA paragraph: "14 days. 200 minutes. ..."
    ("14 days. 200 minutes.", "200 minutes."),
    # FAQ body text
    ("After 14 days, compare:", "After the 200-minute pilot, compare:"),
    # JSON-LD FAQPage answers
    ("Compare after 14 days.", "Compare after the 200-minute pilot."),
    ("Compare transcripts after 14 days.", "Compare transcripts after the 200-minute pilot."),
    # Generic catch-all for any remaining "14-day" / "14 day" variants.
    ("14-day pilot", "200-minute pilot"),
    ("14 day pilot", "200-minute pilot"),
    ("14-day trial", "200-minute free trial"),
    ("14 day trial", "200-minute free trial"),
    ("14-day", "200-minute"),
    ("14 day", "200-minute"),
]

# Integration/CRM/calendar claims — Syntharra has none of these.
# Script treats each as a literal search. If a city page ever adds one, this
# will still fail verification (loudly) rather than silently passing.
FORBIDDEN_INTEGRATION_TERMS = [
    "ServiceTitan",
    "Housecall Pro",
    "Jobber",
    "HubSpot",
    "Calendly",
    "Outlook",
    "Google Calendar",
    "book into",
    "books appointments",
    "automated booking",
    "CRM integration",
    "calendar sync",
    "booked straight",
    "appointment booking",
]


def remove_fake_telephone(text: str) -> tuple[str, int]:
    """Remove the `"telephone": "+1-000-000-0000",` line from JSON-LD."""
    pattern = re.compile(
        r'^[ \t]*"telephone":\s*"\+1-000-000-0000",?\s*\n',
        flags=re.MULTILINE,
    )
    new_text, count = pattern.subn("", text)
    return new_text, count


def apply_copy_replacements(text: str) -> tuple[str, int]:
    total = 0
    for old, new in COPY_REPLACEMENTS:
        if old in text:
            occurrences = text.count(old)
            total += occurrences
            text = text.replace(old, new)
    return text, total


def inject_css(text: str) -> tuple[str, bool]:
    """Append CSS rules just before the closing </style> tag."""
    if CSS_SENTINEL in text:
        return text, False  # idempotent
    if "</style>" not in text:
        raise ValueError("No </style> tag found — unexpected structure")
    injected = text.replace("</style>", OTHER_CITIES_CSS + "\n    </style>", 1)
    return injected, True


def inject_section(text: str, slug: str) -> tuple[str, bool]:
    """Insert the cross-linking section just before the <footer> tag."""
    if SECTION_SENTINEL in text:
        return text, False  # idempotent
    # Match whatever whitespace precedes <footer>
    m = re.search(r'(\n[ \t]*)<footer\b', text)
    if not m:
        raise ValueError("No <footer> tag found — unexpected structure")
    section_html = build_other_cities_section(slug)
    # Insert directly before the matched <footer> (preserving the newline/indent).
    insert_at = m.start()
    new_text = text[:insert_at] + "\n" + section_html + text[insert_at:]
    return new_text, True


def validate_jsonld(text: str, file_label: str) -> list[str]:
    """Extract every JSON-LD block and confirm it parses. Returns error list."""
    errors: list[str] = []
    ld_pattern = re.compile(
        r'<script type="application/ld\+json">(.*?)</script>',
        flags=re.DOTALL,
    )
    for i, m in enumerate(ld_pattern.finditer(text)):
        block = m.group(1).strip()
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError as e:
            errors.append(f"{file_label} JSON-LD block #{i}: {e}")
            continue
        # Extra checks: no stray telephone / price / aggregateRating fields.
        if isinstance(parsed, dict):
            if parsed.get("telephone") == "+1-000-000-0000":
                errors.append(f"{file_label} JSON-LD block #{i}: fake telephone still present")
            if "aggregateRating" in parsed:
                errors.append(f"{file_label} JSON-LD block #{i}: aggregateRating must not be present")
            if "price" in parsed and str(parsed["price"]) not in ("697",):
                errors.append(
                    f"{file_label} JSON-LD block #{i}: unexpected price {parsed['price']!r}"
                )
    return errors


def validate_style_count(text: str, file_label: str) -> list[str]:
    open_count = text.count("<style")
    close_count = text.count("</style>")
    errors = []
    if open_count != 1:
        errors.append(f"{file_label}: expected 1 <style> block, found {open_count}")
    if close_count != 1:
        errors.append(f"{file_label}: expected 1 </style> block, found {close_count}")
    return errors


def validate_no_forbidden_terms(text: str, file_label: str) -> list[str]:
    errors = []
    for term in FORBIDDEN_INTEGRATION_TERMS:
        if term in text:
            errors.append(f"{file_label}: forbidden integration term still present: {term!r}")
    if "+1-000-000-0000" in text:
        errors.append(f"{file_label}: fake phone +1-000-000-0000 still present")
    if "14-day" in text or "14 day" in text:
        errors.append(f"{file_label}: '14-day' / '14 day' still present")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(path: Path, slug: str, write: bool) -> dict:
    original = path.read_text(encoding="utf-8")
    text = original

    text, phone_removed = remove_fake_telephone(text)
    text, copy_replacements = apply_copy_replacements(text)
    text, css_added = inject_css(text)
    text, section_added = inject_section(text, slug)

    # Pre-validation errors (from our own output).
    file_label = path.name
    errors: list[str] = []
    errors += validate_style_count(text, file_label)
    errors += validate_jsonld(text, file_label)
    errors += validate_no_forbidden_terms(text, file_label)

    changed = text != original

    if write and changed and not errors:
        path.write_text(text, encoding="utf-8")

    return {
        "file": file_label,
        "slug": slug,
        "phone_removed": phone_removed,
        "copy_replacements": copy_replacements,
        "css_added": css_added,
        "section_added": section_added,
        "changed": changed,
        "written": write and changed and not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: compute changes and report but do not write files.",
    )
    args = parser.parse_args()

    if not REPO_WEBSITE.exists():
        print(f"ERROR: website repo not found at {REPO_WEBSITE}", file=sys.stderr)
        return 2

    write = not args.check
    print(f"Mode: {'WRITE' if write else 'CHECK (dry-run)'}")
    print(f"Website repo: {REPO_WEBSITE}")
    print(f"Processing {len(CITY_SLUGS)} city pages...\n")

    missing: list[str] = []
    results: list[dict] = []
    all_errors: list[str] = []

    for slug in CITY_SLUGS:
        fname = f"hvac-answering-service-{slug}.html"
        path = REPO_WEBSITE / fname
        if not path.exists():
            missing.append(fname)
            continue
        result = process_file(path, slug, write=write)
        results.append(result)
        all_errors.extend(result["errors"])

    # Per-file summary
    print(
        f"{'file':<44} {'phone':<6} {'14d':<5} {'css':<5} {'sect':<5} {'errors':<6}"
    )
    print("-" * 75)
    for r in results:
        err_marker = str(len(r["errors"])) if r["errors"] else "-"
        print(
            f"{r['file']:<44} "
            f"{r['phone_removed']:<6} "
            f"{r['copy_replacements']:<5} "
            f"{('yes' if r['css_added'] else '-'):<5} "
            f"{('yes' if r['section_added'] else '-'):<5} "
            f"{err_marker:<6}"
        )

    print()
    print(f"Files processed: {len(results)}/{len(CITY_SLUGS)}")
    print(f"Files changed:   {sum(1 for r in results if r['changed'])}")
    print(f"Files written:   {sum(1 for r in results if r['written'])}")

    if missing:
        print(f"\nMISSING FILES ({len(missing)}):")
        for fname in missing:
            print(f"  {fname}")

    if all_errors:
        print(f"\nERRORS ({len(all_errors)}):")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("\nAll files clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
