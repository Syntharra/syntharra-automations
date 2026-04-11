#!/usr/bin/env python3
"""
build_affiliate_outreach.py — Phase 0 HVAC-YouTuber affiliate outreach generator.

Given a hardcoded list of HVAC YouTubers (see HVAC_YOUTUBERS below), generates a
personalized 3-touch affiliate outreach sequence per target. Each sequence is
3 emails spaced over 12 days, with subject lines and bodies that reference the
creator's channel specifically. Output is JSON + a plain-text companion file
for Dan's manual review-and-send workflow.

Mirrors the structure and voice of `build_cold_outreach.py`:
  - String templates only, no API calls, Python stdlib only
  - CAN-SPAM footer identical to cold outreach
  - Deterministic subject-line variety (hash of slug, not random.random) so
    reruns produce identical output
  - No fabricated numbers in body copy (the one ~$2,500/signup math is
    30% * 12 * $697 ~= $2,509 — see comment inline)
  - No fake testimonials. Pitch-only.

Output shape (JSON):
  {
    "generated_at": "2026-04-11T17:30:00Z",
    "count": 8,
    "affiliates": [
      {
        "slug": "hvac-school",
        "channel_name": "HVAC School",
        "creator_name": "Bryan Orr",
        "channel_url": "https://...",
        "tracking_url": "https://syntharra.com/affiliate?ref=...",
        "sequence": [
          {"touch": 1, "day_offset": 0,  "subject": "...", "body": "..."},
          {"touch": 2, "day_offset": 5,  "subject": "Re: ...", "body": "..."},
          {"touch": 3, "day_offset": 12, "subject": "Last note from Syntharra", "body": "..."}
        ]
      },
      ...
    ]
  }

The companion .txt file contains all 24 emails (8 creators * 3 touches) rendered
in human-readable form.

TODO (Day 6+ work, out of scope for this tool):
  - The tracking URL https://syntharra.com/affiliate?ref={slug} does NOT yet
    resolve. Dan needs to build the affiliate landing page + tracking logic
    before any of these emails are actually sent. This generator just stamps
    the URL into the copy; it does not create or register it anywhere.

Cost: $0. No API calls. Pure string templating.

Usage:
  python tools/build_affiliate_outreach.py
  python tools/build_affiliate_outreach.py --preview   # print to stdout, no file writes
  python tools/build_affiliate_outreach.py --output-dir leads/
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Target list
# --------------------------------------------------------------------------- #
# Personalization hooks below need per-email manual verification before send —
# they're written to be plausible (based on each channel's known focus) but
# they are NOT claims that we've watched a specific recent video. Dan will
# review and tweak each hook before any email actually leaves. Every hook is
# marked `# UNVERIFIED`.
HVAC_YOUTUBERS = [
    {
        "slug": "hvac-school",
        "channel_name": "HVAC School",
        "creator_name_or_unknown": "Bryan Orr",
        "channel_url": "https://www.youtube.com/@HVACS",
        "audience_hook": "serious HVAC techs who want to understand the physics",
        "personalization_hook": "I've been following your refrigerant charging deep-dives for a while now.",  # UNVERIFIED
    },
    {
        "slug": "ac-service-tech",
        "channel_name": "AC Service Tech LLC",
        "creator_name_or_unknown": "Craig Migliaccio",
        "channel_url": "https://www.youtube.com/@acservicetech",
        "audience_hook": "field techs and HVAC business owners",
        "personalization_hook": "Your 'common HVAC repairs' playlist is genuinely the most useful free training I've pointed new Syntharra customers at.",  # UNVERIFIED
    },
    {
        "slug": "word-of-advice-tv",
        "channel_name": "Word of Advice TV",
        "creator_name_or_unknown": None,
        "channel_url": "https://www.youtube.com/@wordofadvicetv",
        "audience_hook": "owner-operators and techs moving into residential HVAC",
        "personalization_hook": "I appreciated your recent video on when to walk away from a repair — that judgment call is exactly the moment our AI tries to capture upstream on the call.",  # UNVERIFIED
    },
    {
        "slug": "quality-hvac",
        "channel_name": "Quality HVAC",
        "creator_name_or_unknown": "Joshua Griffin",
        "channel_url": "https://www.youtube.com/@qualityhvacr",
        "audience_hook": "commercial HVAC refrigeration techs",
        "personalization_hook": "Your commercial refrigeration troubleshooting content is niche in the best way.",  # UNVERIFIED
    },
    {
        "slug": "hvac-shop-talk",
        "channel_name": "HVAC Shop Talk",
        "creator_name_or_unknown": None,
        "channel_url": "https://www.youtube.com/@HVACShopTalk",
        "audience_hook": "HVAC business owners talking shop, business-of-HVAC angle",
        "personalization_hook": "Your business-side content — pricing, hiring, phones ringing at 2 a.m. — is exactly the conversation our product lives in.",  # UNVERIFIED
    },
    {
        "slug": "hvac-guide-for-homeowners",
        "channel_name": "HVAC Guide for Homeowners",
        "creator_name_or_unknown": None,
        "channel_url": "https://www.youtube.com/@HVAC_GUIDE",
        "audience_hook": "homeowners researching HVAC — drives qualified calls into contractor shops",
        "personalization_hook": "Your homeowner-focused content drives qualified calls into HVAC shops — and the shops that get those calls are exactly our customer base.",  # UNVERIFIED
    },
    {
        "slug": "hvac-tactical",
        "channel_name": "HVAC Tactical",
        "creator_name_or_unknown": None,
        "channel_url": "https://www.youtube.com/@HVACTactical",
        "audience_hook": "HVAC techs learning diagnostics",
        "personalization_hook": "I watched your series on reading pressure gauges — genuinely the clearest teaching I've seen on the topic.",  # UNVERIFIED
    },
    {
        "slug": "stephen-rardon-heating-and-air",
        "channel_name": "Stephen Rardon Heating and Air",
        "creator_name_or_unknown": "Stephen Rardon",
        "channel_url": "https://www.youtube.com/@stephenrardonheatingandair",
        "audience_hook": "small owner-operators running lean",
        "personalization_hook": "Your small-shop-running-lean content resonates with exactly the owner-operators we built Syntharra for.",  # UNVERIFIED
    },
]


# --------------------------------------------------------------------------- #
# Subject-line patterns (deterministic per-creator choice)
# --------------------------------------------------------------------------- #
# Three first-touch subject patterns. Pick one per creator via hash(slug) so
# reruns are reproducible and the list doesn't look batch-sent. Matches the
# spirit of build_cold_outreach.py's i % len(SUBJECTS_1) rotation but seeded
# by slug instead of index (so reordering the list doesn't reshuffle subjects).
SUBJECT_PATTERNS_TOUCH_1 = [
    "Partnership idea for {channel_name}",
    "Affiliate offer for HVAC creators",
    "Quick question about {channel_name}",
]


# --------------------------------------------------------------------------- #
# Body templates
# --------------------------------------------------------------------------- #
# Math check for the ~$2,500 line: 30% * 12 months * $697/mo = $2,509.20.
# Rounded to ~$2,500 in the copy. This is the ONLY number in the body copy —
# everything else is claim-free.
BODY_1 = """\
{greeting}

{personalization_hook}

I'm Dan — I run Syntharra. We build an AI phone receptionist for HVAC
contractors. One sentence: every call gets answered 24/7 by an AI that
sounds like a real person, qualifies the lead, books the visit, and only
pings the owner when it's a true emergency. The pain we solve is simple —
owner-operators losing the 2 a.m. "my AC is dead" call to whoever answers
first.

Why I'm reaching out: we're opening affiliate partnerships with 3-5 HVAC
creators in Q2 2026, and {channel_name} is on that shortlist because your
audience is {audience_hook} — basically our exact customer. The deal is
30% of first-year revenue per Syntharra customer you refer, via a tracking
link. Our product is $697/mo, so first-year commission works out to roughly
$2,500 per signup.

Would you be open to a 15-minute call to see if this makes sense for your
audience? No obligation, and if 30% isn't the right structure for your
channel we can talk about alternatives (flat per-signup, hybrid, whatever
works).

Tracking link I'd set up for you: {tracking_url}

— Dan Maguire
Founder, Syntharra
"""

BODY_2 = """\
{greeting}

Bumping this up in case it got buried. Short version: 30% affiliate on
Syntharra — $697/mo AI phone receptionist for HVAC contractors, so first-
year commission lands around $2,500 per signup. We're picking 3-5 creators
this quarter and {channel_name} is on the shortlist.

If it's a fit, I'd love a 15-minute call. If not, totally fine — just let
me know and I'll stop bumping.

Tracking link I'd set up for you: {tracking_url}

— Dan Maguire
Founder, Syntharra
"""

BODY_3 = """\
{greeting}

Not going to keep pestering you — this is my last note. Short version: the
affiliate offer is still open if you ever want to circle back, and if this
just isn't a good fit for {channel_name}, all good.

Appreciate the content you put out either way — my team actually uses it
for training.

Cheers,
— Dan Maguire
Founder, Syntharra
"""


CAN_SPAM_FOOTER = """

---
Syntharra · Global AI Solutions · USA
Reply STOP to unsubscribe.
"""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def tracking_url_for(slug: str) -> str:
    """Build the per-creator affiliate tracking URL.

    Contains only the slug — no PII (name, email, channel URL).
    """
    return (
        f"https://syntharra.com/affiliate?ref={slug}"
        f"&stx_asset_id=aff-{slug}-2026-04"
    )


def greeting_for(creator_name: str | None, channel_name: str) -> str:
    """Return `Hi {name},` if we have a real creator name, else team greeting."""
    if creator_name:
        first = creator_name.split()[0]
        return f"Hi {first},"
    return f"Hi {channel_name} team,"


def pick_touch_1_subject(slug: str, channel_name: str) -> str:
    """Deterministic subject-line pick so reruns match and the batch looks varied.

    Uses md5(slug)[0] (a hex digit 0-f) modulo the pattern count. Hex digit is
    a reasonable uniform-enough seed for this batch size (8 creators).
    """
    h = hashlib.md5(slug.encode()).hexdigest()
    idx = int(h[0], 16) % len(SUBJECT_PATTERNS_TOUCH_1)
    pattern = SUBJECT_PATTERNS_TOUCH_1[idx]
    return pattern.format(channel_name=channel_name)


def render_touch_1(target: dict) -> dict:
    slug = target["slug"]
    channel_name = target["channel_name"]
    creator_name = target["creator_name_or_unknown"]
    tracking_url = tracking_url_for(slug)

    subject = pick_touch_1_subject(slug, channel_name)
    body = BODY_1.format(
        greeting=greeting_for(creator_name, channel_name),
        personalization_hook=target["personalization_hook"],
        channel_name=channel_name,
        audience_hook=target["audience_hook"],
        tracking_url=tracking_url,
    ) + CAN_SPAM_FOOTER

    return {"touch": 1, "day_offset": 0, "subject": subject, "body": body}


def render_touch_2(target: dict, touch_1_subject: str) -> dict:
    slug = target["slug"]
    channel_name = target["channel_name"]
    creator_name = target["creator_name_or_unknown"]
    tracking_url = tracking_url_for(slug)

    subject = f"Re: {touch_1_subject}"
    body = BODY_2.format(
        greeting=greeting_for(creator_name, channel_name),
        channel_name=channel_name,
        tracking_url=tracking_url,
    ) + CAN_SPAM_FOOTER

    return {"touch": 2, "day_offset": 5, "subject": subject, "body": body}


def render_touch_3(target: dict) -> dict:
    channel_name = target["channel_name"]
    creator_name = target["creator_name_or_unknown"]

    subject = "Last note from Syntharra"
    body = BODY_3.format(
        greeting=greeting_for(creator_name, channel_name),
        channel_name=channel_name,
    ) + CAN_SPAM_FOOTER

    return {"touch": 3, "day_offset": 12, "subject": subject, "body": body}


def build_sequence(target: dict) -> list[dict]:
    t1 = render_touch_1(target)
    t2 = render_touch_2(target, t1["subject"])
    t3 = render_touch_3(target)
    return [t1, t2, t3]


def build_affiliate_record(target: dict) -> dict:
    return {
        "slug": target["slug"],
        "channel_name": target["channel_name"],
        "creator_name": target["creator_name_or_unknown"],
        "channel_url": target["channel_url"],
        "tracking_url": tracking_url_for(target["slug"]),
        "sequence": build_sequence(target),
    }


def render_text_report(affiliates: list[dict]) -> str:
    """Human-readable dump of all 24 emails for Dan's pre-send review."""
    lines = []
    lines.append("=" * 72)
    lines.append("SYNTHARRA AFFILIATE OUTREACH — HVAC YOUTUBER SEQUENCES")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Count: {len(affiliates)} creators × 3 touches = "
                 f"{sum(len(a['sequence']) for a in affiliates)} emails")
    lines.append("=" * 72)
    lines.append("")
    for a in affiliates:
        lines.append("")
        lines.append("#" * 72)
        lines.append(f"# {a['channel_name']}  ({a['channel_url']})")
        if a["creator_name"]:
            lines.append(f"# Creator: {a['creator_name']}")
        lines.append(f"# Slug: {a['slug']}")
        lines.append(f"# Tracking: {a['tracking_url']}")
        lines.append("#" * 72)
        for step in a["sequence"]:
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


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description="Generate 3-touch affiliate outreach sequences for HVAC YouTubers."
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
    args = ap.parse_args()

    affiliates = [build_affiliate_record(t) for t in HVAC_YOUTUBERS]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "count": len(affiliates),
        "affiliates": affiliates,
    }

    if args.preview:
        # Preview mode: print the text report to stdout, no file writes.
        print(render_text_report(affiliates))
        return

    os.makedirs(args.output_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    json_path = os.path.join(args.output_dir, f"affiliate_outreach_{date_str}.json")
    txt_path  = os.path.join(args.output_dir, f"affiliate_outreach_{date_str}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(render_text_report(affiliates))

    total_emails = sum(len(a["sequence"]) for a in affiliates)
    print(
        f"[affiliate] wrote {len(affiliates)} creators × 3 touches = "
        f"{total_emails} emails",
        file=sys.stderr,
    )
    print(f"[affiliate]   json: {json_path}", file=sys.stderr)
    print(f"[affiliate]   txt:  {txt_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
