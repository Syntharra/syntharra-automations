#!/usr/bin/env python3
"""
fix_vs_pages.py — P0/P1 cleanup for 19 HVAC competitor comparison pages.

Operates on the sibling syntharra-website repo. Applies these changes to each
vs-*.html file:

  1. Replace "14-day" / "14 day" trial copy with "200-minute" pilot language
     (P0-4). Protects the unrelated "14-day money-back" phrase (competitor fact).
  2. Remove CRM / calendar integration claims about Syntharra (Dan confirmed
     NO integrations exist). Surgical per-file fixes for vs-answerforce.html,
     the only file that has explicit false claims. Leaves factual statements
     about competitor integrations and Syntharra-lacks-X statements alone.
  3. Check for legacy $497/$997 pricing (P0) — currently none, but fail loudly
     if any reappear.
  4. Inject Product + BreadcrumbList JSON-LD schema blocks just before the
     existing FAQPage block (or in <head> for files without any prior JSON-LD).
     Marker-guarded for idempotency (P1-3, P1-20).
  5. Append a cross-linking "other-comparisons" footer section listing the
     other 18 vs-* pages. Marker-guarded (P2-17).
  6. Append matching CSS rules inside the existing single <style> block.
  7. Sanity-check: exactly one <style> block, every JSON-LD block parses, no
     forbidden trial/pricing strings remain.

Run once, commit locally in the website repo, do not push.

Usage:
    python tools/fix_vs_pages.py [--check]

    --check  Dry-run: compute all changes in memory and print per-file summary
             but do not write to disk.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_AUTOMATIONS = Path(__file__).resolve().parent.parent
REPO_WEBSITE = REPO_AUTOMATIONS.parent / "syntharra-website"

# slug (without .html) -> display name used in schema + cross-links.
VS_PAGES: dict[str, str] = {
    "vs-abby-connect": "Abby Connect",
    "vs-answer24": "Answer24",
    "vs-answerconnect": "AnswerConnect",
    "vs-answerforce": "AnswerForce",
    "vs-answering-service-care": "Answering Service Care",
    "vs-answering-service": "Traditional Answering Service",
    "vs-davinci-virtual": "Davinci Virtual",
    "vs-gabbyville": "Gabbyville",
    "vs-map-communications": "MAP Communications",
    "vs-moneypenny": "Moneypenny",
    "vs-nexa": "Nexa",
    "vs-no-more-phone-tag": "No More Phone Tag",
    "vs-patlive": "PATLive",
    "vs-posh": "Posh",
    "vs-ruby-receptionists": "Ruby Receptionists",
    "vs-smith-ai": "Smith.ai",
    "vs-specialty-answering": "Specialty Answering Service",
    "vs-unicom": "Unicom Teleservices",
    "vs-voicenation": "VoiceNation",
}

# ---------------------------------------------------------------------------
# Trial copy replacements (order matters — long/specific phrases first)
# ---------------------------------------------------------------------------

# Placeholder used to protect "14-day money-back" (a factual claim about the
# Abby Connect competitor, NOT a Syntharra trial claim).
PROTECT_MONEYBACK = "\u0001MONEY_BACK_PROTECTED\u0001"

COPY_REPLACEMENTS: list[tuple[str, str]] = [
    # Grid cells with "14 days free" / "14 days" span
    ('<span class="yes">14 days free</span>', '<span class="yes">200 minutes free</span>'),
    ('<span class="yes">14 days</span>', '<span class="yes">200 minutes</span>'),

    # Sentence-initial "14 days. 200 minutes." across every Final CTA block.
    ("14 days. 200 minutes.", "200 minutes."),

    # FAQ body phrasings
    ("After 14 days, compare:", "After the 200-minute pilot, compare:"),
    ("After 14 days, compare", "After the 200-minute pilot, compare"),
    ("After 14 days you'll", "After the 200-minute pilot you'll"),
    ("after 14 days the pilot is catching", "after the 200-minute pilot is catching"),
    ("After 14 days the pilot is catching", "After the 200-minute pilot is catching"),
    ("after 14 days, compare", "after the 200-minute pilot, compare"),
    ("after 14 days", "after the 200-minute pilot"),
    ("for 14 days.", "through the 200-minute pilot."),
    ("for 14 days ", "through the 200-minute pilot "),
    ("in parallel for 14 days", "in parallel through the 200-minute pilot"),
    ("speed over 14 days", "speed over the 200-minute pilot"),
    ("billing over 14 days", "billing over the 200-minute pilot"),
    ("cost over 14 days", "cost over the 200-minute pilot"),
    ("dispatch speed over 14 days", "dispatch speed over the 200-minute pilot"),
    ("accuracy over 14 days", "accuracy over the 200-minute pilot"),
    ("over 14 days", "over the 200-minute pilot"),
    ("14 days and compare data", "the 200-minute pilot and compare data"),
    ("14 days and compare", "the 200-minute pilot and compare"),
    ("14 days and see what", "the 200-minute pilot and see what"),
    ("14 days and you'll have data", "the 200-minute pilot and you'll have data"),
    ("14 days you'll have hard data", "the 200-minute pilot and you'll have hard data"),
    ("14-day picture of", "200-minute snapshot of"),

    # Long CTAs / meta patterns
    ("Try the free 14-day pilot \u2192", "Try the free 200-minute pilot \u2192"),
    ("Start my free 14-day pilot \u2192", "Start my free 200-minute pilot \u2192"),
    ("the free 14-day pilot", "the free 200-minute pilot"),
    ("Free 14-day pilot", "Free 200-minute pilot"),
    ("free 14-day pilot", "free 200-minute pilot"),
    ("14-day pilot", "200-minute pilot"),
    ("14 day pilot", "200-minute pilot"),
    ("14-day trial", "200-minute trial"),
    ("14 day trial", "200-minute trial"),

    # Final catch-all
    ("14-day", "200-minute"),
    ("14 day", "200-minute"),
]

# ---------------------------------------------------------------------------
# CRM / integration surgical fixes (per-file)
# ---------------------------------------------------------------------------

# These are literal (old, new) tuples applied only to the named file. They
# fix false claims about Syntharra integrating with specific CRMs / calendars.
# Competitor-factual claims (e.g. "Unicom has no Jobber/HCP integration") are
# left alone because they're accurate statements about the competitor.

SURGICAL_FIXES: dict[str, list[tuple[str, str]]] = {
    "vs-answerforce.html": [
        # Grid row: "Appointment booking — Syntharra: Native booking into your
        # calendar, confirmation SMS to caller". The entire row is a false
        # Syntharra claim; remove the whole <tr>.
        (
            '                            <tr>\n'
            '                                <td class="label">Appointment booking</td>\n'
            '                                <td>Calendar integration on higher tiers</td>\n'
            '                                <td class="col-syntharra">Native booking into your calendar, confirmation SMS to caller</td>\n'
            '                            </tr>\n',
            '',
        ),
        # "Syntharra integrates with calendars and SMS today" — false; we have
        # no calendar integration. Rewrite to reflect lead capture + handoff.
        (
            "<strong>CRM sync into Jobber, Housecall Pro, ServiceTitan.</strong> AnswerForce has mature field-service CRM integrations. Syntharra integrates with calendars and SMS today; deeper CRM sync is on the 2026 roadmap.",
            "<strong>CRM sync into Jobber, Housecall Pro, ServiceTitan.</strong> AnswerForce has mature field-service CRM integrations. Syntharra captures every lead and delivers an instant SMS + email handoff today; native CRM sync is on the 2026 roadmap.",
        ),
        # FAQ answer that falsely claims Syntharra syncs into Google
        # Calendar / iCloud / Outlook. Rewrite to honest capture + SMS handoff.
        (
            "That's real and Syntharra can't match it today. If you live inside Jobber or Housecall Pro and need tight CRM sync for every call, AnswerForce has the more mature integration right now. Syntharra syncs appointments directly into Google Calendar / iCloud / Outlook, sends SMS dispatches in real time, and pushes full transcripts into your dashboard \u2014 but native deep links into Jobber and ServiceTitan are on the 2026 roadmap rather than shipping today.",
            "That's real and Syntharra can't match it today. If you live inside Jobber or Housecall Pro and need tight CRM sync for every call, AnswerForce has the more mature integration right now. Syntharra captures every lead and delivers an instant SMS + email handoff with the full transcript and AI summary \u2014 you get the notification and you book the job. Native CRM integrations are on the 2026 roadmap rather than shipping today.",
        ),
        # JSON-LD FAQ answer mirror of the above.
        (
            "AnswerForce has more mature deep CRM integrations today. Syntharra syncs appointments into Google Calendar / iCloud / Outlook, sends SMS dispatches, and pushes transcripts to the dashboard. Native deep links into Jobber, Housecall Pro, and ServiceTitan are on the 2026 roadmap.",
            "AnswerForce has more mature deep CRM integrations today. Syntharra captures every lead and delivers an instant SMS + email handoff with the full transcript and AI summary \u2014 you get the notification and you book the job. Native CRM integrations are on the 2026 roadmap.",
        ),
    ],
}

# ---------------------------------------------------------------------------
# Forbidden post-fix checks
# ---------------------------------------------------------------------------

# After cleanup, none of these Syntharra-specific false claims should remain.
# Competitor-factual mentions are caught by a narrower allow-list further down.
FORBIDDEN_AFTER_FIX: list[str] = [
    "$497",
    "$997",
    "14-day pilot",
    "14 day pilot",
    "14-day trial",
    "14 day trial",
    # Copy-level false Syntharra integration claims.
    "Syntharra syncs appointments directly into Google Calendar",
    "Syntharra syncs appointments into Google Calendar",
    "Native booking into your calendar, confirmation SMS",
    "Syntharra books into your CRM",
    "Syntharra books appointments",
]

# ---------------------------------------------------------------------------
# Schema templates
# ---------------------------------------------------------------------------

PRODUCT_SCHEMA_SENTINEL = "<!-- Product schema (added by fix_vs_pages.py) -->"
BREADCRUMB_SCHEMA_SENTINEL = "<!-- BreadcrumbList schema (added by fix_vs_pages.py) -->"
OTHER_COMPARISONS_SENTINEL = '<section class="other-comparisons">'
CSS_SENTINEL = "/* Cross-linking styles (added by fix_vs_pages.py) */"

PRODUCT_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Syntharra HVAC Standard",
    "description": "AI receptionist built for HVAC contractors. Answers calls 24/7, captures every lead, delivers instant SMS and email handoff.",
    "brand": {"@type": "Brand", "name": "Syntharra"},
    "offers": {
        "@type": "Offer",
        "price": "697",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "url": "https://syntharra.com/start.html",
    },
}


def build_product_block() -> str:
    body = json.dumps(PRODUCT_SCHEMA, indent=4)
    return (
        f'    {PRODUCT_SCHEMA_SENTINEL}\n'
        '    <script type="application/ld+json">\n'
        f'{body}\n'
        '    </script>\n'
    )


def build_breadcrumb_block(slug: str, display: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://syntharra.com/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Compare",
                "item": "https://syntharra.com/best-hvac-answering-service.html",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": f"Syntharra vs {display}",
                "item": f"https://syntharra.com/{slug}.html",
            },
        ],
    }
    body = json.dumps(data, indent=4)
    return (
        f'    {BREADCRUMB_SCHEMA_SENTINEL}\n'
        '    <script type="application/ld+json">\n'
        f'{body}\n'
        '    </script>\n'
    )


# ---------------------------------------------------------------------------
# Cross-linking section
# ---------------------------------------------------------------------------

OTHER_COMPARISONS_CSS = """
/* Cross-linking styles (added by fix_vs_pages.py) */
.other-comparisons { padding: 48px 32px; background: #FAFAFA; border-top: 1px solid #E5E7EB; }
.other-comparisons h2 { font-size: 22px; font-weight: 700; color: #1A1A2E; margin-bottom: 24px; text-align: center; }
.other-comparisons-list { list-style: none; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px 16px; max-width: 900px; margin: 0 auto; padding: 0; }
.other-comparisons-list a { color: #6C63FF; text-decoration: none; font-size: 14px; font-weight: 500; padding: 6px 10px; border-radius: 6px; transition: background 0.15s; }
.other-comparisons-list a:hover { background: rgba(108,99,255,0.08); }
"""


def build_other_comparisons_section(current_slug: str) -> str:
    items: list[str] = []
    for slug, display in VS_PAGES.items():
        if slug == current_slug:
            continue
        items.append(f'      <li><a href="/{slug}.html">{display}</a></li>')
    lis = "\n".join(items)
    return (
        '    <!-- Other comparisons (added by fix_vs_pages.py) -->\n'
        '    <section class="other-comparisons">\n'
        '      <div class="container">\n'
        '        <h2>Compare Syntharra to other providers</h2>\n'
        '        <ul class="other-comparisons-list">\n'
        f'{lis}\n'
        '        </ul>\n'
        '      </div>\n'
        '    </section>\n\n'
    )


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

def apply_copy_replacements(text: str) -> tuple[str, int]:
    # Protect "14-day money-back" (Abby Connect's money-back guarantee) from
    # the 14-day → 200-minute catch-all.
    protected = text.replace("14-day money-back", PROTECT_MONEYBACK)

    total = 0
    for old, new in COPY_REPLACEMENTS:
        if old in protected:
            total += protected.count(old)
            protected = protected.replace(old, new)

    final = protected.replace(PROTECT_MONEYBACK, "14-day money-back")
    return final, total


def apply_surgical_fixes(text: str, fname: str) -> tuple[str, int]:
    """Apply per-file CRM/false-claim fixes. Returns (text, edits_applied)."""
    edits = 0
    for old, new in SURGICAL_FIXES.get(fname, []):
        if old in text:
            text = text.replace(old, new, 1)
            edits += 1
    return text, edits


def inject_schema_blocks(text: str, slug: str, display: str) -> tuple[str, bool, bool]:
    """Insert Product + BreadcrumbList JSON-LD just BEFORE the existing
    FAQPage JSON-LD block. If no existing JSON-LD exists, insert before
    </body>. Marker-guarded for idempotency."""

    product_added = PRODUCT_SCHEMA_SENTINEL not in text
    breadcrumb_added = BREADCRUMB_SCHEMA_SENTINEL not in text

    if not product_added and not breadcrumb_added:
        return text, False, False

    product_block = build_product_block() if product_added else ""
    breadcrumb_block = build_breadcrumb_block(slug, display) if breadcrumb_added else ""
    insertion = product_block + breadcrumb_block

    # Prefer inserting immediately before the existing FAQPage script.
    faq_match = re.search(
        r'([ \t]*)<script type="application/ld\+json">\s*\n?\s*\{\s*"@context": "https://schema.org",\s*"@type": "FAQPage"',
        text,
    )
    if faq_match:
        insert_at = faq_match.start()
        new_text = text[:insert_at] + insertion + text[insert_at:]
        return new_text, product_added, breadcrumb_added

    # Fallback: insert just before </body>.
    if "</body>" not in text:
        raise ValueError("No </body> tag and no FAQPage JSON-LD — cannot inject schema")
    new_text = text.replace("</body>", insertion + "</body>", 1)
    return new_text, product_added, breadcrumb_added


def inject_css(text: str) -> tuple[str, bool]:
    if CSS_SENTINEL in text:
        return text, False
    if "</style>" not in text:
        raise ValueError("No </style> tag found — unexpected structure")
    # Insert immediately before the first </style> close tag. Matches the
    # existing fix_city_pages.py pattern.
    injected = text.replace("</style>", OTHER_COMPARISONS_CSS + "\n    </style>", 1)
    return injected, True


def inject_section(text: str, slug: str) -> tuple[str, bool]:
    if OTHER_COMPARISONS_SENTINEL in text:
        return text, False
    m = re.search(r"(\n[ \t]*)<footer\b", text)
    if not m:
        raise ValueError("No <footer> tag found — unexpected structure")
    section_html = build_other_comparisons_section(slug)
    insert_at = m.start()
    return text[:insert_at] + "\n" + section_html + text[insert_at:], True


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_style_count(text: str, file_label: str) -> list[str]:
    errors = []
    open_count = text.count("<style")
    close_count = text.count("</style>")
    if open_count != 1:
        errors.append(f"{file_label}: expected 1 <style> block, found {open_count}")
    if close_count != 1:
        errors.append(f"{file_label}: expected 1 </style> block, found {close_count}")
    return errors


def validate_jsonld(text: str, file_label: str) -> list[str]:
    errors: list[str] = []
    ld_pattern = re.compile(
        r'<script type="application/ld\+json">(.*?)</script>',
        flags=re.DOTALL,
    )
    has_product = False
    has_breadcrumb = False
    for i, m in enumerate(ld_pattern.finditer(text)):
        block = m.group(1).strip()
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError as e:
            errors.append(f"{file_label} JSON-LD block #{i}: {e}")
            continue
        if isinstance(parsed, dict):
            t = parsed.get("@type")
            if t == "Product":
                has_product = True
                offers = parsed.get("offers") or {}
                if str(offers.get("price")) != "697":
                    errors.append(
                        f"{file_label} Product block: unexpected price "
                        f"{offers.get('price')!r}"
                    )
            elif t == "BreadcrumbList":
                has_breadcrumb = True
            if "aggregateRating" in parsed:
                errors.append(
                    f"{file_label} JSON-LD block #{i}: aggregateRating must not be present"
                )
            if "review" in parsed:
                errors.append(
                    f"{file_label} JSON-LD block #{i}: review must not be present"
                )
    if not has_product:
        errors.append(f"{file_label}: Product JSON-LD missing after injection")
    if not has_breadcrumb:
        errors.append(f"{file_label}: BreadcrumbList JSON-LD missing after injection")
    return errors


def validate_no_forbidden(text: str, file_label: str) -> list[str]:
    errors = []
    for term in FORBIDDEN_AFTER_FIX:
        if term in text:
            errors.append(f"{file_label}: forbidden text still present: {term!r}")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(path: Path, slug: str, display: str, write: bool) -> dict:
    original = path.read_text(encoding="utf-8")
    text = original

    text, copy_replacements = apply_copy_replacements(text)
    text, surgical_edits = apply_surgical_fixes(text, path.name)
    text, product_added, breadcrumb_added = inject_schema_blocks(text, slug, display)
    text, css_added = inject_css(text)
    text, section_added = inject_section(text, slug)

    file_label = path.name
    errors: list[str] = []
    errors += validate_style_count(text, file_label)
    errors += validate_jsonld(text, file_label)
    errors += validate_no_forbidden(text, file_label)

    changed = text != original
    if write and changed and not errors:
        path.write_text(text, encoding="utf-8")

    return {
        "file": file_label,
        "slug": slug,
        "copy_replacements": copy_replacements,
        "surgical_edits": surgical_edits,
        "product_added": product_added,
        "breadcrumb_added": breadcrumb_added,
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
    print(f"Processing {len(VS_PAGES)} comparison pages...\n")

    missing: list[str] = []
    results: list[dict] = []
    all_errors: list[str] = []

    for slug, display in VS_PAGES.items():
        fname = f"{slug}.html"
        path = REPO_WEBSITE / fname
        if not path.exists():
            missing.append(fname)
            continue
        result = process_file(path, slug, display, write=write)
        results.append(result)
        all_errors.extend(result["errors"])

    print(
        f"{'file':<36} {'copy':<5} {'surg':<5} {'prod':<5} {'brdc':<5} {'css':<5} {'sect':<5} {'err':<4}"
    )
    print("-" * 78)
    for r in results:
        err_marker = str(len(r["errors"])) if r["errors"] else "-"
        print(
            f"{r['file']:<36} "
            f"{r['copy_replacements']:<5} "
            f"{r['surgical_edits']:<5} "
            f"{('yes' if r['product_added'] else '-'):<5} "
            f"{('yes' if r['breadcrumb_added'] else '-'):<5} "
            f"{('yes' if r['css_added'] else '-'):<5} "
            f"{('yes' if r['section_added'] else '-'):<5} "
            f"{err_marker:<4}"
        )

    print()
    print(f"Files processed: {len(results)}/{len(VS_PAGES)}")
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
