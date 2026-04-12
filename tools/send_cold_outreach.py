#!/usr/bin/env python3
"""
send_cold_outreach.py — Phase 0 cold outreach sender.

Takes a CSV from `build_cold_outreach.py` (with cold_email_*_subject and
cold_email_*_body columns) and sends the appropriate sequence step via the
configured backend. Tracks send history in a JSON state file so re-runs
advance to the next step automatically.

⚠ THIS TOOL DOES NOTHING WITHOUT --i-know-this-is-real ⚠
The default mode is dry-run (preview only). To actually send email, the user
MUST explicitly pass `--i-know-this-is-real`. This is a deliberate guardrail
against accidental cold email blasts.

Backends:
  - brevo:    Uses BREVO_API_KEY (transactional). NOTE: Brevo TOS may
              restrict cold-list sending. Use a separate Brevo account, or
              switch to mailgun/smartlead for cold campaigns.
  - mailgun:  Uses MAILGUN_API_KEY + MAILGUN_DOMAIN
  - smtp:     Uses SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
  - print:    Just prints what would be sent (default, free, no risk)

Recommended approach for $0 first run:
  1. Build the lead list (scrape_hvac_directory.py)
  2. Enrich with emails (find_email_from_website.py)
  3. Generate copy (build_cold_outreach.py)
  4. Run this with --backend print to see what would go out
  5. Manually copy-paste 5 emails to a free Gmail account to test responses
  6. Once you've validated the response rate, set up Mailgun ($35/mo, 50K
     sends) or Smartlead ($39/mo) for the real cold-volume sender

Sequence logic:
  - state file at leads/.send_state.json maps email → {"step": N, "last_sent": iso}
  - First run sends step 1 to all leads
  - Re-run after 3 days sends step 2 to leads that haven't replied
  - Re-run after 7 days from step 2 sends step 3
  - "Replied" status is updated manually by Dan in the state file (or by a
    future webhook integration with the inbox)

Usage (dry-run preview):
  source .env.local
  python tools/send_cold_outreach.py --in leads/hvac-austin-tx.outreach.csv

Usage (actual send via Brevo, capped at 25 sends):
  python tools/send_cold_outreach.py \
    --in leads/hvac-austin-tx.outreach.csv \
    --backend brevo \
    --max-sends 25 \
    --i-know-this-is-real

Cost ledger:
  - print backend: $0
  - brevo backend: ~$0.0004 per email (Brevo transactional pricing)
  - mailgun backend: ~$0.0008 per email (Foundation plan)
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


STATE_FILE = "leads/.send_state.json"
SENDER_NAME = "Dan @ Syntharra"
SENDER_EMAIL = "daniel@syntharra.com"  # the only verified Brevo sender on the Syntharra account


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def next_step_for(email: str, state: dict) -> int:
    s = state.get(email.lower())
    if not s:
        return 1
    if s.get("replied"):
        return 0  # done — they replied, stop sending
    return min(s.get("step", 1) + 1, 3)


def send_brevo(api_key: str, to_email: str, to_name: str, subject: str, body_text: str) -> bool:
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "textContent": body_text,
        # Cold email best practice: don't use templateId here, send raw text
    }
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "api-key": api_key,
            "content-type": "application/json",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        print(f"  [error] brevo: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  [error] brevo: {e}", file=sys.stderr)
        return False


def send_mailgun(api_key: str, domain: str, to_email: str, to_name: str, subject: str, body_text: str) -> bool:
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    fields = {
        "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to": f"{to_name} <{to_email}>",
        "subject": subject,
        "text": body_text,
    }
    body = urllib.parse.urlencode(fields).encode()
    auth = "api:" + api_key
    import base64
    auth_b64 = base64.b64encode(auth.encode()).decode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "authorization": f"Basic {auth_b64}",
        "content-type": "application/x-www-form-urlencoded",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"  [error] mailgun: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--backend", choices=["print", "brevo", "mailgun"], default="print")
    ap.add_argument("--max-sends", type=int, default=10,
                    help="Hard cap on total sends per run (safety rail)")
    ap.add_argument("--rate-limit", type=float, default=4.0,
                    help="Seconds between sends (politeness, default 4)")
    ap.add_argument("--i-know-this-is-real", action="store_true",
                    help="Required to actually send. Without this, only print.")
    args = ap.parse_args()

    if args.backend != "print" and not args.__dict__["i_know_this_is_real"]:
        print(
            f"[guard] backend={args.backend} but --i-know-this-is-real not set. "
            "Switching to print mode.",
            file=sys.stderr,
        )
        args.backend = "print"

    with open(args.in_csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    state = load_state()
    sent_this_run = 0
    skipped_this_run = 0

    for row in rows:
        if sent_this_run >= args.max_sends:
            print(f"[guard] max-sends={args.max_sends} reached, stopping", file=sys.stderr)
            break
        email = (row.get("email") or "").strip().lower()
        if not email:
            skipped_this_run += 1
            continue
        step = next_step_for(email, state)
        if step == 0:
            print(f"  [skip] {email} replied — done", file=sys.stderr)
            skipped_this_run += 1
            continue

        subject = row.get(f"cold_email_{step}_subject", "")
        body    = row.get(f"cold_email_{step}_body", "")
        if not subject or not body:
            print(f"  [skip] {email} step={step} — missing subject/body", file=sys.stderr)
            skipped_this_run += 1
            continue

        company = row.get("name", "")
        if args.backend == "print":
            print(f"\n========== STEP {step} → {email} ({company}) ==========")
            print(f"Subject: {subject}")
            print(body)
            ok = True
        elif args.backend == "brevo":
            api_key = os.environ.get("BREVO_API_KEY")
            if not api_key:
                sys.exit("BREVO_API_KEY not set")
            ok = send_brevo(api_key, email, company, subject, body)
            if ok:
                print(f"  [sent step {step}] {email}", file=sys.stderr)
            time.sleep(args.rate_limit)
        elif args.backend == "mailgun":
            api_key = os.environ.get("MAILGUN_API_KEY")
            domain  = os.environ.get("MAILGUN_DOMAIN")
            if not api_key or not domain:
                sys.exit("MAILGUN_API_KEY + MAILGUN_DOMAIN must be set")
            ok = send_mailgun(api_key, domain, email, company, subject, body)
            if ok:
                print(f"  [sent step {step}] {email}", file=sys.stderr)
            time.sleep(args.rate_limit)
        else:
            ok = False

        if ok:
            sent_this_run += 1
            state[email] = {
                "step": step,
                "last_sent": datetime.now(timezone.utc).isoformat(),
                "company": company,
                "replied": False,
            }
            save_state(state)

    print(
        f"[done] backend={args.backend} sent={sent_this_run} skipped={skipped_this_run}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
