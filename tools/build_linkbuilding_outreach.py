#!/usr/bin/env python3
"""
build_linkbuilding_outreach.py — Phase 0 SEO/link-building outreach generator.

Given a hardcoded list of HVAC-adjacent high-authority websites (associations,
trade publications, blogs, directories, equipment suppliers), generates a
personalized 2-touch outreach sequence per target. Output is JSON + a plain-
text companion file for Dan's manual review-and-send workflow.

The goal is legitimate backlinks or guest-post opportunities to accelerate
SEO ranking for the 9 /vs-X.html comparison pages (and 15 city-landing pages
shipping next). These are not cold sales emails — they are partnership /
contribution pitches to real humans at real organizations.

Mirrors the structure and voice of `build_affiliate_outreach.py`:
  - String templates only, no API calls, Python stdlib only
  - CAN-SPAM footer identical to cold/affiliate outreach
  - Deterministic per-target output (no randomness) so reruns are reproducible
  - No fabricated claims — we're Phase 0, ~0 customers, "just launched"
  - No fake urgency, no fake testimonials

Output shape (JSON):
  {
    "generated_at": "2026-04-11T17:30:00Z",
    "count": 30,
    "targets": [
      {
        "slug": "acca",
        "site_name": "ACCA",
        "site_url": "https://acca.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "https://acca.org/contact",
        "angle": "...",
        "tracking_url": "https://syntharra.com/partners?ref=acca&...",
        "sequence": [
          {"touch": 1, "day_offset": 0, "subject": "...", "body": "..."},
          {"touch": 2, "day_offset": 7, "subject": "Re: ...", "body": "..."}
        ]
      },
      ...
    ]
  }

The companion .txt file contains every rendered email (N targets × 2 touches)
in human-readable form for Dan to read before sending.

IMPORTANT — Dan must spot-check the target list before sending:
  - Every target in LINKBUILDING_TARGETS is marked `# RESEARCH_UNVERIFIED`.
  - URLs were compiled from general HVAC-industry knowledge; some may be
    stale, moved, or the org may no longer accept outreach of this form.
  - Obvious wrongs (404s, orgs that clearly don't do guest posts, defunct
    blogs) should be deleted from LINKBUILDING_TARGETS before running the
    real send.
  - Personalization "angle" strings are plausible but NOT evidence of a
    specific recent post — review each before sending.

TODO (Day 5+ work, out of scope for this tool):
  - The tracking URL https://syntharra.com/partners?ref={slug} does NOT yet
    resolve. Dan needs to either build /partners or repurpose /affiliate
    before any of these emails are actually sent. This generator just stamps
    the URL into the copy; it does not create or register anything.
  - Three `/vs-X.html` comparison-page URLs are cited in each touch-1 email
    as reference examples. They're stamped with Syntharra's real URLs — Dan
    should confirm they're live before sending.

Cost: $0. No API calls. Pure string templating.

Usage:
  python tools/build_linkbuilding_outreach.py
  python tools/build_linkbuilding_outreach.py --preview
  python tools/build_linkbuilding_outreach.py --tier 1
  python tools/build_linkbuilding_outreach.py --category blog
  python tools/build_linkbuilding_outreach.py --output-dir leads/
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Target list
# --------------------------------------------------------------------------- #
# Every entry is RESEARCH_UNVERIFIED. Dan must spot-check each site's actual
# contact page and remove obviously-wrong targets before sending. The angle
# strings are plausible but have NOT been confirmed against the target's
# current content.
LINKBUILDING_TARGETS = [
    # ---------- Tier 1 — HVAC Associations (highest authority) ---------- #
    {
        "slug": "acca",
        "site_name": "ACCA (Air Conditioning Contractors of America)",
        "site_url": "https://acca.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "https://acca.org/contact",  # RESEARCH_UNVERIFIED
        "angle": "ACCA Now member resources / partner listing for HVAC contractor software",
    },
    {
        "slug": "bpi",
        "site_name": "BPI (Building Performance Institute)",
        "site_url": "https://bpi.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "https://bpi.org/contact-us",  # RESEARCH_UNVERIFIED
        "angle": "BPI contractor-facing resources for building-performance pros",
    },
    {
        "slug": "smacna",
        "site_name": "SMACNA (Sheet Metal and Air Conditioning Contractors' National Association)",
        "site_url": "https://smacna.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "SMACNA contractor member resources",
    },
    {
        "slug": "rses",
        "site_name": "RSES (Refrigeration Service Engineers Society)",
        "site_url": "https://rses.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "RSES member-facing contractor software resources",
    },
    {
        "slug": "phcc",
        "site_name": "PHCC (Plumbing-Heating-Cooling Contractors Association)",
        "site_url": "https://phccweb.org",
        "category": "association",
        "authority_tier": 1,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "PHCC member resources / contractor partner listing",
    },

    # ---------- Tier 2 — HVAC Trade Publications ---------- #
    {
        "slug": "achr-news",
        "site_name": "ACHR News",
        "site_url": "https://achrnews.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest contribution on AI in HVAC — the 2 a.m. test for owner-operators",
    },
    {
        "slug": "contracting-business",
        "site_name": "Contracting Business Magazine",
        "site_url": "https://contractingbusiness.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest article on phone-coverage economics for residential HVAC shops",
    },
    {
        "slug": "hpac-engineering",
        "site_name": "HPAC Engineering",
        "site_url": "https://hpac.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest article on the business-ops side of HVAC engineering firms",
    },
    {
        "slug": "hvac-insider",
        "site_name": "HVAC Insider",
        "site_url": "https://hvacinsider.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "industry-contributor post on voice AI for HVAC phones",
    },
    {
        "slug": "pmmag",
        "site_name": "Plumbing & Mechanical",
        "site_url": "https://pmmag.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest piece on contractor phone economics (HVAC-adjacent PHC audience)",
    },
    {
        "slug": "contractormag",
        "site_name": "Contractor Magazine",
        "site_url": "https://contractormag.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest article on small-shop phone coverage economics",
    },
    {
        "slug": "rses-journal",
        "site_name": "RSES Journal",
        "site_url": "https://rses.org/journal",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "contributor article for RSES Journal on owner-operator operations",
    },
    {
        "slug": "hvac-business-magazine",
        "site_name": "HVAC Business Magazine",
        "site_url": "https://hvacbusiness.com",
        "category": "news",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "guest column for HVAC Business readers on call-capture and booking rates",
    },

    # ---------- Tier 2 — HVAC Blogs ---------- #
    {
        "slug": "hvac-talk",
        "site_name": "HVAC-Talk.com",
        "site_url": "https://hvac-talk.com",
        "category": "blog",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "the business-side threads about phones ringing after-hours",
    },
    {
        "slug": "hvacrschool",
        "site_name": "HVAC School (Bryan Orr)",
        "site_url": "https://hvacrschool.com/articles",
        "category": "blog",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "the written HVAC School content around business-of-HVAC topics",
    },
    {
        "slug": "wrench-group",
        "site_name": "The Wrench Group resources",
        "site_url": "https://thewrenchgroup.com/resources",
        "category": "blog",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "contractor-resources section — AI phone tooling for member shops",
    },
    {
        "slug": "concord-carpenter",
        "site_name": "Concord Carpenter (Rob Robillard)",
        "site_url": "https://concordcarpenter.com",
        "category": "blog",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "the trades-business content you publish for owner-operators",
    },

    # ---------- Tier 3 — Directories & review sites ---------- #
    {
        "slug": "angi-hvac",
        "site_name": "Angi HVAC category",
        "site_url": "https://www.angi.com/categories/heating-cooling",
        "category": "directory",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Angi HVAC service provider / contractor software listing",
    },
    {
        "slug": "houzz-hvac",
        "site_name": "Houzz HVAC professionals",
        "site_url": "https://www.houzz.com/professionals/hvac-contractors",
        "category": "directory",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Houzz HVAC professional services directory / software partner listing",
    },
    {
        "slug": "thumbtack-hvac",
        "site_name": "Thumbtack HVAC category",
        "site_url": "https://www.thumbtack.com/k/hvac-contractors/near-me/",
        "category": "directory",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Thumbtack HVAC contractor software / partner listing",
    },
    {
        "slug": "bbb-hvac",
        "site_name": "Better Business Bureau HVAC category",
        "site_url": "https://www.bbb.org/us/categories/hvac-contractors",
        "category": "directory",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "BBB HVAC category page listing for contractor-facing tools",
    },
    {
        "slug": "yelp-hvac",
        "site_name": "Yelp HVAC category",
        "site_url": "https://www.yelp.com/search?cflt=hvac",
        "category": "directory",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Yelp HVAC services / business-tools listing",
    },

    # ---------- Tier 2 — HVAC Equipment Suppliers (B2B blogs) ---------- #
    {
        "slug": "johnson-supply",
        "site_name": "Johnson Supply",
        "site_url": "https://johnsonsupply.com",
        "category": "equipment_supplier",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "contractor-facing resources / partner page for Johnson Supply customers",
    },
    {
        "slug": "ferguson-hvac",
        "site_name": "Ferguson HVAC",
        "site_url": "https://ferguson.com/hvac",
        "category": "equipment_supplier",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Ferguson HVAC contractor-resources content hub",
    },
    {
        "slug": "grainger-hvac",
        "site_name": "Grainger HVAC industry content",
        "site_url": "https://grainger.com",
        "category": "equipment_supplier",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "Grainger industry content hub — contractor software for HVAC customers",
    },

    # ---------- Tier 3 — Small HVAC blogs (easier wins) ---------- #
    {
        "slug": "hvacguy",
        "site_name": "HVAC Guy blog",
        "site_url": "https://hvacguy.com",
        "category": "blog",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "homeowner-facing content that points readers at local HVAC pros",
    },
    {
        "slug": "word-of-advice-hvac",
        "site_name": "Word of Advice HVAC (blog)",
        "site_url": "https://wordofadvice.tv/blog",
        "category": "blog",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "the written content cross-linked from the Word of Advice TV channel",
    },
    {
        "slug": "hvac-warehouse",
        "site_name": "HVAC Warehouse blog",
        "site_url": "https://hvacwarehouse.com/blog",
        "category": "blog",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "contractor-facing blog content for HVAC Warehouse's customer base",
    },
    {
        "slug": "hvac-troubleshooting-hub",
        "site_name": "HVAC Troubleshooting Hub",
        "site_url": "https://hvactroubleshootinghub.com",
        "category": "blog",
        "authority_tier": 3,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "the diagnostic content that brings qualified-call-ready readers to HVAC shops",
    },
    {
        "slug": "hvac-school-cross",
        "site_name": "HVAC School (written + YouTube cross-promotion)",
        "site_url": "https://hvacrschool.com",
        "category": "blog",
        "authority_tier": 2,
        "contact_url_or_unknown": "unknown",  # RESEARCH_UNVERIFIED
        "angle": "HVAC School written resources — business-of-HVAC guest piece",
    },
]


# --------------------------------------------------------------------------- #
# Subject-line patterns (per-category)
# --------------------------------------------------------------------------- #
SUBJECTS_TOUCH_1 = {
    "association":       "Partner / member-resource idea for {site_short}",
    "news":              "Guest article pitch for {site_short}",
    "blog":              "Quick collaboration idea for {site_short}",
    "directory":         "Submission for {site_short} — Syntharra (HVAC AI receptionist)",
    "equipment_supplier":"Partner resource idea for {site_short}",
}

SUBJECT_TOUCH_2_PREFIX = "Re: "


# --------------------------------------------------------------------------- #
# Reference comparison pages cited in touch 1 (stamped into each email as
# "happy to send as reference"). Dan should confirm these are live before
# sending — they're Phase 0 comparison pages shipped last sprint.
# --------------------------------------------------------------------------- #
REFERENCE_COMPARISON_PAGES = [
    "https://syntharra.com/vs-ruby-receptionists.html",
    "https://syntharra.com/vs-smith-ai.html",
    "https://syntharra.com/best-hvac-answering-service.html",
]


# --------------------------------------------------------------------------- #
# Body templates — per-category touch 1
# --------------------------------------------------------------------------- #
# All bodies end with a shared closing block (reference links + signature +
# CAN-SPAM footer) added by the renderer. The per-category body is just the
# opener through the ask.

BODY_1_ASSOCIATION = """\
{greeting}

I run Syntharra — we just launched an AI phone receptionist built specifically
for HVAC contractors. The reason I'm reaching out: we're looking for ways to
actually serve the {site_short} community, not just advertise to it.

Specifically, I'm hoping to explore {angle}. Would it be appropriate to
submit Syntharra as a member-facing resource, a partner listing, or a
contributor to any upcoming content? I'd rather come in through the front
door than buy a banner ad.

Honest context: we're Phase 0. We're not claiming hundreds of customers. We
just built something we think solves a real pain — owner-operators losing
the 2 a.m. "my AC is dead" call to whoever answers first — and we're looking
for the right organizations to learn from and serve.
"""

BODY_1_NEWS = """\
{greeting}

I'm Dan — I run Syntharra. We just launched an AI phone receptionist built
specifically for HVAC contractors, and I'd love to pitch a guest article for
{site_short}.

The angle I had in mind: {angle}. Working title: "The 2 a.m. test — what
phones ringing at 2 a.m. really cost an owner-operator HVAC shop." It'd be
an honest, numbers-first piece on call-coverage economics (not a Syntharra
ad). I can pull real industry numbers on missed-call rates, average service-
call value, and the conversion math between them.

Is that the kind of contributor piece {site_short} accepts? If the pitch
needs to go through a specific editor or form, happy to route it properly —
just let me know.
"""

BODY_1_BLOG = """\
{greeting}

Long-time reader. What drew me to reach out: your content around {angle}.
A lot of that overlaps with what we're building at Syntharra — we just
launched an AI phone receptionist for HVAC contractors, and the pain we're
trying to solve is exactly the 2 a.m. "my AC is dead" call that owner-
operators can't answer without burning out.

Any interest in a cross-link, a guest piece, or even just swapping notes?
If a guest article makes sense, I can write something genuinely useful for
your readers — no product pitch, just the honest business-of-HVAC math around
phone coverage.

Honest context: we're Phase 0. No inflated customer count, no testimonial
wall. Just a tool we think solves a real problem, looking for the right
people to learn from.
"""

BODY_1_DIRECTORY = """\
{greeting}

Short note — we'd like to add Syntharra to the {site_short} HVAC / contractor-
software category. We're an AI phone receptionist built specifically for HVAC
contractors (launched Phase 0 — we're not claiming we're a category leader,
we're just new and real).

Could you point me at the submission process? If there's a form, a paid
listing, or an editorial review path, I'll follow whichever is standard. I'd
rather do this the right way than scrape a listing in.
"""

BODY_1_EQUIPMENT = """\
{greeting}

I'm Dan — I run Syntharra. We just launched an AI phone receptionist built
specifically for HVAC contractors. The reason I'm reaching out to {site_short}:
you already serve the exact contractor base we're built for, and I wonder if
there's a way to include Syntharra in your contractor resources or partner
page.

Specifically, I'm interested in {angle}. I'm not pitching a co-branded promo
or anything fancy — just wondering if your contractor-resources section
accepts new entries, and what the process looks like. Happy to route through
whoever handles partner listings.

Honest context: we're Phase 0, ~0 paying customers, just shipped. But the
product is real and we're looking for the right kind of distribution — the
kind that actually helps your contractor customers.
"""

BODY_1_BY_CATEGORY = {
    "association":        BODY_1_ASSOCIATION,
    "news":               BODY_1_NEWS,
    "blog":               BODY_1_BLOG,
    "directory":          BODY_1_DIRECTORY,
    "equipment_supplier": BODY_1_EQUIPMENT,
}


# Shared closing block appended to every touch-1 body (before CAN-SPAM footer)
BODY_1_CLOSING = """\

Happy to send our comparison pages as reference:
  - {ref_1}
  - {ref_2}
  - {ref_3}

Tracking link for this outreach (so I can thank the right source if it
converts): {tracking_url}

— Dan Maguire
Founder, Syntharra
https://syntharra.com
"""


BODY_2 = """\
{greeting}

Bumping this in case it got buried. Short version: I run Syntharra, an AI
phone receptionist built specifically for HVAC contractors. I reached out
last week about {short_ask}.

Totally fine if this isn't the right time, or not the right fit — just let
me know and I won't bump again. If it is a fit, I'm still here.

Tracking link: {tracking_url}

— Dan Maguire
Founder, Syntharra
https://syntharra.com
"""


CAN_SPAM_FOOTER = """

---
Syntharra · Global AI Solutions · USA
Reply STOP to unsubscribe.
"""


SHORT_ASK_BY_CATEGORY = {
    "association":        "a member-resource / partner listing for HVAC contractors",
    "news":               "a guest article on HVAC phone-coverage economics",
    "blog":               "a guest post or cross-link collaboration",
    "directory":          "a listing for Syntharra in your HVAC category",
    "equipment_supplier": "a partner-resources / contractor-page listing",
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def tracking_url_for(slug: str) -> str:
    """Build the per-target tracking URL.

    Points at /partners which doesn't yet resolve (see TODO in docstring).
    """
    return (
        f"https://syntharra.com/partners?ref={slug}"
        f"&stx_asset_id=link-{slug}-2026-04"
    )


def site_short_for(site_name: str) -> str:
    """Short form of site name for subject lines — first token before paren."""
    return site_name.split(" (", 1)[0].strip()


def greeting_for_target(target: dict) -> str:
    """Return a greeting. We don't have names for link-building targets yet,
    so default to `Hi {site} team,` — Dan can patch in a real name pre-send.
    """
    return f"Hi {site_short_for(target['site_name'])} team,"


def render_touch_1(target: dict) -> dict:
    category = target["category"]
    site_short = site_short_for(target["site_name"])
    slug = target["slug"]

    subject_template = SUBJECTS_TOUCH_1.get(
        category, "Partnership idea for {site_short}"
    )
    subject = subject_template.format(site_short=site_short)

    body_template = BODY_1_BY_CATEGORY.get(category, BODY_1_BLOG)
    body_core = body_template.format(
        greeting=greeting_for_target(target),
        site_short=site_short,
        angle=target["angle"],
    )
    body_closing = BODY_1_CLOSING.format(
        ref_1=REFERENCE_COMPARISON_PAGES[0],
        ref_2=REFERENCE_COMPARISON_PAGES[1],
        ref_3=REFERENCE_COMPARISON_PAGES[2],
        tracking_url=tracking_url_for(slug),
    )
    body = body_core + body_closing + CAN_SPAM_FOOTER

    return {"touch": 1, "day_offset": 0, "subject": subject, "body": body}


def render_touch_2(target: dict, touch_1_subject: str) -> dict:
    slug = target["slug"]
    category = target["category"]
    short_ask = SHORT_ASK_BY_CATEGORY.get(category, "a partnership")

    subject = SUBJECT_TOUCH_2_PREFIX + touch_1_subject
    body = BODY_2.format(
        greeting=greeting_for_target(target),
        short_ask=short_ask,
        tracking_url=tracking_url_for(slug),
    ) + CAN_SPAM_FOOTER

    return {"touch": 2, "day_offset": 7, "subject": subject, "body": body}


def build_sequence(target: dict) -> list[dict]:
    t1 = render_touch_1(target)
    t2 = render_touch_2(target, t1["subject"])
    return [t1, t2]


def build_target_record(target: dict) -> dict:
    return {
        "slug": target["slug"],
        "site_name": target["site_name"],
        "site_url": target["site_url"],
        "category": target["category"],
        "authority_tier": target["authority_tier"],
        "contact_url_or_unknown": target["contact_url_or_unknown"],
        "angle": target["angle"],
        "tracking_url": tracking_url_for(target["slug"]),
        "sequence": build_sequence(target),
    }


def render_text_report(targets: list[dict]) -> str:
    """Human-readable dump of all emails for Dan's pre-send review."""
    lines = []
    lines.append("=" * 72)
    lines.append("SYNTHARRA LINK-BUILDING OUTREACH — HVAC-ADJACENT SITES")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    total_emails = sum(len(t["sequence"]) for t in targets)
    lines.append(
        f"Count: {len(targets)} targets × 2 touches = {total_emails} emails"
    )
    lines.append("=" * 72)
    lines.append("")
    lines.append("REMINDER: every target is RESEARCH_UNVERIFIED. Spot-check each")
    lines.append("site's actual contact page and remove obviously-wrong targets")
    lines.append("before sending a single email.")
    lines.append("")
    for t in targets:
        lines.append("")
        lines.append("#" * 72)
        lines.append(f"# {t['site_name']}  ({t['site_url']})")
        lines.append(f"# Category: {t['category']}  |  Tier: {t['authority_tier']}")
        lines.append(f"# Slug: {t['slug']}")
        lines.append(f"# Contact: {t['contact_url_or_unknown']}")
        lines.append(f"# Tracking: {t['tracking_url']}")
        lines.append(f"# Angle: {t['angle']}")
        lines.append("#" * 72)
        for step in t["sequence"]:
            lines.append("")
            lines.append(
                f"---------- TOUCH {step['touch']} "
                f"(day +{step['day_offset']}) ----------"
            )
            lines.append(f"Subject: {step['subject']}")
            lines.append("")
            lines.append(step["body"])
        lines.append("")
    return "\n".join(lines)


def filter_targets(targets: list[dict], tier: int | None, category: str | None) -> list[dict]:
    out = targets
    if tier is not None:
        out = [t for t in out if t["authority_tier"] == tier]
    if category is not None:
        out = [t for t in out if t["category"] == category]
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description=(
            "Generate 2-touch link-building outreach sequences for "
            "HVAC-adjacent high-authority sites."
        )
    )
    ap.add_argument(
        "--output-dir",
        default="leads",
        help="Directory to write the JSON + TXT files (default: leads/)",
    )
    ap.add_argument(
        "--preview",
        action="store_true",
        help="Print the text report to stdout instead of writing files",
    )
    ap.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help="Filter to targets at a specific authority tier (1=highest)",
    )
    ap.add_argument(
        "--category",
        choices=["association", "news", "blog", "directory", "equipment_supplier"],
        default=None,
        help="Filter to a single target category",
    )
    args = ap.parse_args()

    filtered = filter_targets(LINKBUILDING_TARGETS, args.tier, args.category)
    if not filtered:
        print(
            "[linkbuild] no targets matched filters "
            f"(tier={args.tier}, category={args.category})",
            file=sys.stderr,
        )
        sys.exit(1)

    records = [build_target_record(t) for t in filtered]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "count": len(records),
        "filters": {"tier": args.tier, "category": args.category},
        "targets": records,
    }

    if args.preview:
        print(render_text_report(records))
        return

    os.makedirs(args.output_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    json_path = os.path.join(args.output_dir, f"linkbuilding_outreach_{date_str}.json")
    txt_path = os.path.join(args.output_dir, f"linkbuilding_outreach_{date_str}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(render_text_report(records))

    total_emails = sum(len(r["sequence"]) for r in records)
    print(
        f"[linkbuild] wrote {len(records)} targets × 2 touches = "
        f"{total_emails} emails",
        file=sys.stderr,
    )
    print(f"[linkbuild]   json: {json_path}", file=sys.stderr)
    print(f"[linkbuild]   txt:  {txt_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
