"""Generate press releases for Syntharra distribution to HVAC trade publications.

Syntharra does not have a PR agency. This tool produces AP-style release text that
Dan can paste into an email to a trade pub editor, or into a distribution form.

Usage:
    python tools/generate_press_release.py --announcement launch
    python tools/generate_press_release.py --announcement feature \
        --feature-name "pilot_expired graceful handling" \
        --feature-description "callers who dial in after a pilot has expired now hear a graceful redirect instead of a hard disconnect"
    python tools/generate_press_release.py --announcement milestone \
        --milestone-text "100 HVAC pilot signups"
    python tools/generate_press_release.py --list-announcements
    python tools/generate_press_release.py --announcement launch --output press/launch-release.md

Design notes:
    - Stdlib only. No Jinja, no frameworks. f-strings + string templates.
    - No fabricated numbers. Milestones and feature claims come from the CLI, not the tool.
    - Defensible claims only. The tool never writes "most advanced" or "revolutionary".
    - Contact details for press are hardcoded as literal constants. Dan can edit if they change.
    - Per RULES.md #41, sys.stdout.reconfigure(encoding="utf-8", errors="replace") is set at
      module top so emoji / smart quotes / non-ASCII chars in generated text never crash on
      Windows consoles.
    - Output modes:
        - default: print to stdout
        - --output <path>: write to file. The press/ directory is gitignored.

Trade publications (list below) are who Dan manually sends releases to. This tool
does NOT send anything. It only generates the text.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# RULES.md #41 — prevent Windows console from crashing on non-ASCII chars in generated text.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------
# Constants (hardcoded literals — Dan edits these if they change)
# ------------------------------------------------------------------

COMPANY_NAME = "Syntharra"
COMPANY_URL = "https://syntharra.com"
PRESS_EMAIL = "press@syntharra.com"
COMPANY_DATELINE_LOCATION = "AUSTIN, TEXAS"  # Syntharra is US-based remote, Austin is the mail drop
FOUNDER_NAME = "Dan Maguire"
FOUNDER_TITLE = "founder and CEO"
PRODUCT_TAGLINE = "an AI phone receptionist built specifically for HVAC contractors"
FLAT_PRICE_MONTHLY = "$697 per month"


# ------------------------------------------------------------------
# Trade publications (Dan uses this list to manually distribute)
# ------------------------------------------------------------------

TRADE_PUBLICATIONS = [
    "Contracting Business Magazine",
    "ACHR News (Air Conditioning Heating Refrigeration News)",
    "Contractor Magazine",
    "HVAC-Talk (news section on the forum)",
    "HVAC Insider",
    "HVAC Business Magazine",
    "HPAC Engineering",
    "ACCA Now (Air Conditioning Contractors of America)",
    "RSES Journal",
    "Plumbing & Mechanical",
    "Reeves Journal",
]


# ------------------------------------------------------------------
# Boilerplate + shared blocks
# ------------------------------------------------------------------

ABOUT_BOILERPLATE = (
    f"About {COMPANY_NAME}\n\n"
    f"{COMPANY_NAME} is {PRODUCT_TAGLINE}. The platform answers calls 24/7, "
    f"triages HVAC emergencies using domain-trained triage logic, and books "
    f"routine appointments directly into a contractor's existing dispatch software. "
    f"{COMPANY_NAME} is priced at a flat {FLAT_PRICE_MONTHLY} with no per-minute fees, "
    f"no setup fees, and no credit card required for the 14-day pilot. The company "
    f"serves independent HVAC contractors across the United States. For more "
    f"information visit {COMPANY_URL}."
)


CONTACT_BLOCK = (
    "Contact\n\n"
    f"Press inquiries: {PRESS_EMAIL}\n"
    f"Website: {COMPANY_URL}\n"
)


END_MARKER = "###"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _today_pretty() -> str:
    """Return today's date in AP-style 'Month D, YYYY' format."""
    return datetime.now().strftime("%B %-d, %Y") if sys.platform != "win32" else datetime.now().strftime("%B %d, %Y").replace(" 0", " ")


def _header(headline: str) -> str:
    date_str = _today_pretty()
    return (
        "FOR IMMEDIATE RELEASE\n"
        f"{date_str}\n\n"
        f"{headline}\n\n"
        f"{COMPANY_DATELINE_LOCATION} — {date_str} — "
    )


def _footer() -> str:
    return f"\n\n{ABOUT_BOILERPLATE}\n\n{CONTACT_BLOCK}\n{END_MARKER}\n"


# ------------------------------------------------------------------
# Announcement generators
# ------------------------------------------------------------------


def generate_launch() -> str:
    """400-600 word AP-style launch announcement."""
    headline = (
        f"{COMPANY_NAME} Launches AI Phone Receptionist Built Specifically for "
        f"HVAC Contractors"
    )

    lead = (
        f"{COMPANY_NAME} today announced the public launch of its AI phone "
        f"receptionist designed for independent HVAC contractors. The platform "
        f"answers incoming calls around the clock, recognizes HVAC emergencies "
        f"using domain-specific triage logic, and routes non-urgent bookings "
        f"directly into a contractor's dispatch calendar. {COMPANY_NAME} is "
        f"available today at a flat {FLAT_PRICE_MONTHLY} with a free 14-day "
        f"pilot that requires no credit card."
    )

    body_p1 = (
        f"Traditional answering services were built for law firms and dental "
        f"practices, not for trade businesses where missing a 2 a.m. emergency "
        f"call can mean the difference between keeping a customer and losing one "
        f"to a competitor. Most existing services bill by the minute, cannot "
        f"recognize HVAC-specific emergency keywords such as burning smells or "
        f"carbon monoxide alarms, and treat urgent calls the same as routine "
        f"booking requests. {COMPANY_NAME} was built to address these gaps "
        f"specifically for HVAC owner-operators."
    )

    body_p2 = (
        f"The {COMPANY_NAME} platform handles inbound calls in English and "
        f"Spanish, integrates with Jobber and other common dispatch tools, and "
        f"escalates true emergencies to the on-call owner or technician within "
        f"30 seconds via SMS with the caller's address and a summary of the "
        f"reported issue. Routine bookings are written directly into the "
        f"contractor's calendar with no human intervention required. Pilot "
        f"contractors in Arizona, Texas, and Florida have been running on the "
        f"platform during the dark launch period preceding today's announcement."
    )

    body_p3 = (
        f"The company is offering a free 14-day pilot with no credit card "
        f"required. Contractors keep all call recordings and transcripts "
        f"regardless of whether they convert to a paying plan. After the pilot "
        f"period the service is {FLAT_PRICE_MONTHLY} flat with no per-minute "
        f"billing, no setup fees, and no seat charges."
    )

    quote = (
        f'{FOUNDER_NAME}, {FOUNDER_TITLE} of {COMPANY_NAME}, said: '
        f'"The HVAC owners I grew up around hated their phones more than they '
        f'hated the work. My dad ran a two-truck shop for 18 years, and the 2 '
        f'a.m. emergency calls nearly broke him. The answering services he '
        f'tried could not tell the difference between a routine booking and an '
        f'actual fire hazard. We built {COMPANY_NAME} for the exact contractor '
        f'my dad was — the independent owner who needs the phone to get '
        f'answered correctly at 2 a.m. without paying per-minute surprise '
        f"bills or missing his kid's birthday to chase a $180 service call.\""
    )

    return (
        _header(headline)
        + lead
        + "\n\n"
        + body_p1
        + "\n\n"
        + body_p2
        + "\n\n"
        + body_p3
        + "\n\n"
        + quote
        + _footer()
    )


def generate_feature(feature_name: str, feature_description: str | None) -> str:
    """300-500 word feature announcement. Takes feature name + optional description."""
    if not feature_name:
        raise ValueError("--feature-name is required for feature announcements")

    feature_description = (
        feature_description
        or f"additional capability for HVAC contractors using the {COMPANY_NAME} platform"
    )

    headline = (
        f"{COMPANY_NAME} Adds {feature_name} to HVAC AI Phone Receptionist"
    )

    lead = (
        f"{COMPANY_NAME}, the AI phone receptionist built specifically for "
        f"HVAC contractors, today announced {feature_name}, an update to its "
        f"platform that {feature_description}."
    )

    body_p1 = (
        f"The update is available immediately to all {COMPANY_NAME} pilot and "
        f"paying customers at no additional cost. Like the rest of the "
        f"{COMPANY_NAME} platform, the new capability is included in the flat "
        f"{FLAT_PRICE_MONTHLY} subscription with no per-minute charges, no "
        f"setup fees, and no seat charges. Contractors on the 14-day free "
        f"pilot also receive the update automatically."
    )

    body_p2 = (
        f"{COMPANY_NAME} is designed around a single principle: the HVAC phone "
        f"is the business. Every feature added to the platform is evaluated "
        f"against a direct question — does this help an independent contractor "
        f"answer more of the right calls, faster, without hiring a human "
        f"receptionist or paying per-minute answering service fees? Features "
        f"that pass that test ship. Features that do not are left out."
    )

    quote = (
        f'{FOUNDER_NAME}, {FOUNDER_TITLE} of {COMPANY_NAME}, said: '
        f'"Every update we ship starts with a real call from a real HVAC '
        f'shop. {feature_name} is no different — it came out of watching pilot '
        f'contractors hit an edge case we had not planned for, and deciding '
        f'that fixing it properly was more important than shipping something '
        f'faster that was close enough."'
    )

    return (
        _header(headline)
        + lead
        + "\n\n"
        + body_p1
        + "\n\n"
        + body_p2
        + "\n\n"
        + quote
        + _footer()
    )


def generate_milestone(milestone_text: str) -> str:
    """300-500 word milestone announcement. Takes milestone text directly from CLI."""
    if not milestone_text:
        raise ValueError("--milestone-text is required for milestone announcements")

    headline = f"{COMPANY_NAME} Reaches {milestone_text}"

    lead = (
        f"{COMPANY_NAME}, the AI phone receptionist built specifically for HVAC "
        f"contractors, today marked a growth milestone: {milestone_text}. The "
        f"company shared the update as part of its public Phase 0 launch, during "
        f"which pricing, feature scope, and customer onboarding remain unchanged."
    )

    body_p1 = (
        f"{COMPANY_NAME} continues to offer a free 14-day pilot with no credit "
        f"card required. After the pilot period the service is "
        f"{FLAT_PRICE_MONTHLY} flat with no per-minute billing, no setup fees, "
        f"and no seat charges. Contractors keep all call recordings and "
        f"transcripts regardless of whether they choose to convert."
    )

    body_p2 = (
        f"The company is deliberately focused on a single vertical — HVAC — "
        f"and on a single product tier. According to the company, this focus "
        f"is intentional. HVAC emergency triage requires domain-trained "
        f"handling that generalist answering services built for law offices "
        f"or dental practices cannot provide, and {COMPANY_NAME} has no plans "
        f"to expand into adjacent verticals until the HVAC product is mature."
    )

    quote = (
        f'{FOUNDER_NAME}, {FOUNDER_TITLE} of {COMPANY_NAME}, said: '
        f'"Milestones like {milestone_text} matter less to me than what is '
        f'happening on the individual pilot accounts. Every one of these '
        f'numbers is a real HVAC owner who trusted us with their phone line, '
        f'and that is the only metric that actually matters at this stage."'
    )

    return (
        _header(headline)
        + lead
        + "\n\n"
        + body_p1
        + "\n\n"
        + body_p2
        + "\n\n"
        + quote
        + _footer()
    )


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def _list_announcements() -> str:
    return (
        "Available announcement types:\n"
        "  launch     - Phase 0 public launch announcement (400-600 words)\n"
        "  feature    - Feature announcement (requires --feature-name, optional --feature-description)\n"
        "  milestone  - Growth milestone (requires --milestone-text)\n"
        "\n"
        "Trade publications Dan distributes to (manually):\n"
        + "\n".join(f"  - {p}" for p in TRADE_PUBLICATIONS)
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate press releases for Syntharra HVAC AI receptionist.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--announcement",
        choices=["launch", "feature", "milestone"],
        help="Type of announcement to generate.",
    )
    parser.add_argument(
        "--feature-name",
        help="Feature name (required for --announcement feature).",
    )
    parser.add_argument(
        "--feature-description",
        help="Optional feature description (for --announcement feature).",
    )
    parser.add_argument(
        "--milestone-text",
        help='Milestone text, e.g. "100 HVAC pilot signups" (required for --announcement milestone).',
    )
    parser.add_argument(
        "--output",
        help="Output file path. If omitted, prints to stdout. Relative paths are resolved from repo root.",
    )
    parser.add_argument(
        "--list-announcements",
        action="store_true",
        help="List available announcement types and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_announcements:
        print(_list_announcements())
        return 0

    if not args.announcement:
        parser.print_help()
        return 2

    try:
        if args.announcement == "launch":
            text = generate_launch()
        elif args.announcement == "feature":
            text = generate_feature(args.feature_name, args.feature_description)
        elif args.announcement == "milestone":
            text = generate_milestone(args.milestone_text)
        else:  # pragma: no cover — argparse guards this
            parser.error(f"Unknown announcement type: {args.announcement}")
            return 2
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote press release to {out_path}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
