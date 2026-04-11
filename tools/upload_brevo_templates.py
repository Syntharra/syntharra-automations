#!/usr/bin/env python3
"""
upload_brevo_templates.py — Upload shared/email-templates/pilot-*.html to Brevo.

For every file matching `shared/email-templates/pilot-*.html`, POST it to
Brevo's `/v3/smtp/templates` endpoint using the subject line embedded in an
HTML comment at the top of the file:

    <!--subject: Your AI is live. Here's what it's already doing. -->

Prints the resulting Brevo template IDs so they can be copied into
  - docs/REFERENCE.md
  - tools/pilot_lifecycle.py BREVO_TEMPLATE_IDS constant

Usage:
    export BREVO_API_KEY=$(python tools/fetch_vault.py "Brevo" api_key)
    python tools/upload_brevo_templates.py --dry-run   # list files + subjects
    python tools/upload_brevo_templates.py             # upload all

Stdlib only.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request


TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "shared", "email-templates"
)
# Brevo requires the sender to be a verified Sender Identity (or come from an
# authenticated domain). As of 2026-04-11 the only verified sender on the
# Syntharra Brevo account is daniel@syntharra.com (verified via GET /v3/senders).
# If you add founders@/support@/reports@ in the Brevo dashboard, switch back.
# The transactional send call can override `sender` per email if needed.
SENDER = {"name": "Syntharra", "email": "daniel@syntharra.com"}
BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/templates"
SUBJECT_RE = re.compile(r"<!--\s*subject:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL)


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def discover_files() -> list[str]:
    pattern = os.path.join(TEMPLATE_DIR, "pilot-*.html")
    files = sorted(glob.glob(pattern))
    return files


def extract_subject(html: str, fallback: str) -> str:
    m = SUBJECT_RE.search(html)
    if not m:
        print(f"  [WARN] no <!--subject: --> found in {fallback}; using fallback")
        return f"Syntharra — {fallback}"
    return m.group(1).strip()


def _brevo_headers() -> dict:
    return {
        "api-key": env("BREVO_API_KEY"),
        "Content-Type": "application/json",
        "accept": "application/json",
    }


def find_existing(template_name: str) -> int | None:
    """Idempotency check: GET /v3/smtp/templates and return the ID of any
    template whose name matches `template_name`. Returns None if no match.
    Brevo paginates at 50 items max per page; we walk pages until we find or
    exhaust."""
    offset = 0
    page_size = 50
    while True:
        url = f"{BREVO_ENDPOINT}?limit={page_size}&offset={offset}&sort=desc"
        req = urllib.request.Request(url, headers=_brevo_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            sys.exit(f"Brevo list failed: {e.code} {e.read().decode()[:500]}")
        templates = data.get("templates") or []
        for t in templates:
            if t.get("name") == template_name:
                return int(t.get("id"))
        if len(templates) < page_size:
            return None
        offset += page_size


def upload(template_name: str, subject: str, html: str) -> dict:
    """Idempotent upload: if a template with this exact name already exists,
    return its existing id (no PUT, no POST). Otherwise POST a new one. This
    means re-running the script after a partial failure is safe."""
    existing = find_existing(template_name)
    if existing is not None:
        return {"id": existing, "_source": "existing"}

    payload = {
        "sender": SENDER,
        "templateName": template_name,
        "subject": subject,
        "htmlContent": html,
        "isActive": True,
    }
    req = urllib.request.Request(
        BREVO_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=_brevo_headers(),
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
            data["_source"] = "created"
            return data
    except urllib.error.HTTPError as e:
        sys.exit(f"Brevo upload failed for {template_name}: {e.code} {e.read().decode()[:500]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="List files and subjects; do not upload")
    args = ap.parse_args()

    files = discover_files()
    if not files:
        sys.exit(f"No pilot-*.html files found in {TEMPLATE_DIR}")
    print(f"Found {len(files)} template(s):")

    results: list[dict] = []
    for path in files:
        slug = os.path.splitext(os.path.basename(path))[0]  # e.g. pilot-day-3
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        subject = extract_subject(html, slug)
        print(f"  - {slug}: {subject!r}")
        if args.dry_run:
            continue
        data = upload(template_name=slug, subject=subject, html=html)
        template_id = data.get("id")
        source = data.get("_source", "?")
        results.append({"slug": slug, "template_id": template_id, "subject": subject, "source": source})
        print(f"    -> Brevo ID: {template_id}  ({source})")

    if args.dry_run:
        print("\n[DRY-RUN] No uploads performed.")
        return

    print("\n=== COPY INTO docs/REFERENCE.md ===")
    for r in results:
        print(f"Brevo template {r['slug']}: {r['template_id']}")

    print("\n=== COPY INTO tools/pilot_lifecycle.py BREVO_TEMPLATE_IDS ===")
    for r in results:
        print(f'    "{r["slug"]}": {r["template_id"]},')
    print("\nDone.")


if __name__ == "__main__":
    main()
