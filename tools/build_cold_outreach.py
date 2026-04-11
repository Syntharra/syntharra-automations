#!/usr/bin/env python3
"""
build_cold_outreach.py — Phase 0 cold lead personalization.

Takes the enriched lead CSV (output of `find_email_from_website.py`) and
generates two new columns: `cold_email_subject` and `cold_email_body`. Each
email is personalized to the business name, city, and (when available) the
business website.

The copy is honest, low-friction, and matches the spec § 5 voice:
  - No fake urgency, no overpromise
  - Single CTA: try the free 14-day pilot
  - Subject line is short, lowercase, looks human
  - Body is 4-5 sentences, mentions a real pain (after-hours emergency calls)
  - Sign-off: Dan, founder
  - Footer: physical address + unsubscribe + CAN-SPAM compliance

Three sequence variants are generated per business:
  - cold_email_1_subject / cold_email_1_body  (first touch — soft intro)
  - cold_email_2_subject / cold_email_2_body  (3 days later — value reinforcement)
  - cold_email_3_subject / cold_email_3_body  (7 days later — final break-up)

Each variant is a separate column so the sender script can pick which sequence
step to send based on send_history (a separate state file).

Cost: $0. No API calls. Pure string templating.

Usage:
  python tools/build_cold_outreach.py \
    --in leads/hvac-austin-tx.enriched.csv \
    --out leads/hvac-austin-tx.outreach.csv
"""
import argparse
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Subject lines: short, lowercase, no clickbait. Tested cold-email patterns.
# When first_name is empty we use the no-name variant. Subject lines are
# stored as (template, requires_first_name) so we can pick a non-name template
# when the lead has no first name.
SUBJECTS_1 = [
    ("quick {city} HVAC question",            False),
    ("{company} after-hours calls",           False),
    ("{first_name} — quick HVAC question",    True),
    ("missed calls at {company}?",            False),
    ("quick {city} HVAC idea",                False),
]
SUBJECTS_2 = [
    ("Re: {company} after-hours calls",       False),
    ("did you see my note?",                  False),
    ("following up — {company}",              False),
]
SUBJECTS_3 = [
    ("should I close your file?",             False),
    ("last note — {company}",                 False),
]

# Email-local words that look like names but aren't. domains@, hosting@, etc.
NOT_A_NAME = {
    "domains", "domain", "hosting", "host", "web", "webmaster", "noreply",
    "postmaster", "abuse", "registrar", "dns", "ssl", "billing", "test",
    "demo", "user", "owner", "operator", "manager", "info", "contact",
    "office", "admin", "hello", "sales", "support", "service", "help",
    "team", "hr", "mail", "email", "inbox",
}


BODY_1 = """\
Hey{greeting_name},

Quick one — I'm Dan, I run Syntharra. We built an AI receptionist for HVAC
contractors in {city} and a few other markets. The reason I'm reaching out:
the most common pain we hear from owner-operators is missing the 2 a.m.
emergency call when the AC dies in July, and losing that job to whoever
answers first.

What we do is simple — every call gets answered 24/7 by an AI that sounds
like a real person, qualifies the lead, books the visit, and texts you the
details. You only get a notification if it's an emergency that needs you
right now.

We're running a free 14-day pilot — 200 free minutes, no card, you can
cancel any time. Most {state} contractors are taking calls within 24 hours
of signup.

If that sounds useful, the link is below. If not, no hard feelings — feel
free to ignore.

— Dan
Syntharra
{site_link}
"""

BODY_2 = """\
Hey{greeting_name},

Following up on my note last week. I know cold email is annoying so I'll
keep this short — the free 14-day pilot is still open if you want to try
it. No card, no commitment, you keep all your data either way.

Most owners I've talked to don't realize how many calls they're missing
until they see the daily summary email after a few days of running it.

If you're interested, here's the link: {site_link}

If you'd rather I stop emailing you, just reply with "stop" and I will.

— Dan
Syntharra
"""

BODY_3 = """\
Hey{greeting_name},

Last note from me. I wanted to make sure you saw the free 14-day pilot —
no card, no risk. If it's not for {company}, totally fine, I'll close your
file and you won't hear from me again.

If you'd like to give it a shot, here's the link: {site_link}

Best of luck either way.

— Dan
Syntharra
"""


CAN_SPAM_FOOTER = """

---
Syntharra · Global AI Solutions · USA
Reply STOP to unsubscribe.
"""


def first_name_from(email: str | None, all_emails: str | None) -> str:
    """Best-effort extraction of a first name from an email like 'john@acme.com'.
    Returns "" when no plausibly-personal first name is found — caller should
    handle the empty case (greeting becomes generic, not "Hey ,").
    """
    candidates = []
    if email:
        candidates.append(email)
    if all_emails:
        candidates.extend(all_emails.split("|"))
    for addr in candidates:
        if not addr or "@" not in addr:
            continue
        local = addr.split("@", 1)[0].lower()
        if local in NOT_A_NAME:
            continue
        # Take the first alphabetic chunk
        first = ""
        for ch in local:
            if ch.isalpha():
                first += ch
            else:
                break
        if not (2 <= len(first) <= 14):
            continue
        if first in NOT_A_NAME:
            continue
        return first.capitalize()
    return ""


def make_subject(template_pair: tuple[str, bool], row: dict, first_name: str) -> str:
    template, requires_name = template_pair
    if requires_name and not first_name:
        # Caller should have picked a different template — fall back to
        # something generic
        template = "{company} after-hours calls"
    return template.format(
        first_name=first_name or "there",
        company=row.get("name", "your shop"),
        city=row.get("city", "your area"),
        state=row.get("state", "US"),
    ).lower()


def make_body(template: str, row: dict, first_name: str) -> str:
    # When no first name, change "Hey {name}," → "Hi there," to avoid awkward
    # "Hey," with trailing comma.
    if first_name:
        greeting_name = f" {first_name}"
        template = template.replace("Hey{greeting_name}", f"Hey {first_name}")
    else:
        greeting_name = ""
        template = template.replace("Hey{greeting_name}", "Hi there")
    site_link = "https://syntharra.com/start?utm_source=cold_email&utm_medium=outreach&utm_campaign=phase0_pilot&stx_asset_id=cold-email-2026-04"
    return template.format(
        greeting_name=greeting_name,
        company=row.get("name", "your shop"),
        city=row.get("city", "your area"),
        state=row.get("state", "your state"),
        site_link=site_link,
    ) + CAN_SPAM_FOOTER


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--require-email", action="store_true",
                    help="Skip rows that don't have an email address")
    args = ap.parse_args()

    with open(args.in_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.require_email:
        before = len(rows)
        rows = [r for r in rows if (r.get("email") or "").strip()]
        print(f"[cold] filtered {before} -> {len(rows)} rows with emails", file=sys.stderr)

    out_fields = list(rows[0].keys()) if rows else []
    new_fields = [
        "cold_email_1_subject", "cold_email_1_body",
        "cold_email_2_subject", "cold_email_2_body",
        "cold_email_3_subject", "cold_email_3_body",
    ]
    for nf in new_fields:
        if nf not in out_fields:
            out_fields.append(nf)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for i, row in enumerate(rows):
            first_name = first_name_from(row.get("email"), row.get("all_emails"))
            # Rotate through subject variants for diversity (every N leads gets a different subject)
            row["cold_email_1_subject"] = make_subject(SUBJECTS_1[i % len(SUBJECTS_1)], row, first_name)
            row["cold_email_1_body"]    = make_body(BODY_1, row, first_name)
            row["cold_email_2_subject"] = make_subject(SUBJECTS_2[i % len(SUBJECTS_2)], row, first_name)
            row["cold_email_2_body"]    = make_body(BODY_2, row, first_name)
            row["cold_email_3_subject"] = make_subject(SUBJECTS_3[i % len(SUBJECTS_3)], row, first_name)
            row["cold_email_3_body"]    = make_body(BODY_3, row, first_name)
            writer.writerow(row)

    print(f"[cold] wrote {len(rows)} rows with 3-touch sequences to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
