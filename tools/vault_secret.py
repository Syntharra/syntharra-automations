#!/usr/bin/env python3
"""
vault_secret.py — Upsert a credential into `syntharra_vault`.

Usage:
  source .env.local
  python tools/vault_secret.py "<service_name>" <key_type> <key_value>

Example:
  python tools/vault_secret.py "Telnyx" "api_key" "KEY_..."
  python tools/vault_secret.py "Slack" "bot_token" "xoxb-..."
  python tools/vault_secret.py "Stripe" "webhook_signing_secret" "whsec_..."

If a row with (service_name, key_type) already exists it is UPDATED.
If not, it is INSERTED.

Bootstrap requirement: SUPABASE_URL and SUPABASE_SERVICE_KEY must be
exported in the current shell (typically via `source .env.local`).

Security note: the key_value arg is visible in process listings.
For secrets, prefer piping via stdin or use the Supabase dashboard directly.
"""
import json
import os
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    if len(sys.argv) != 4:
        sys.exit(
            "Usage: vault_secret.py <service_name> <key_type> <key_value>\n"
            "Example: vault_secret.py 'Telnyx' 'api_key' 'KEY_...'"
        )
    service_name, key_type, key_value = sys.argv[1], sys.argv[2], sys.argv[3]

    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_KEY", "")
    )
    if not base_url or not service_key:
        sys.exit("SUPABASE_URL + SUPABASE_SERVICE_KEY must be set (source .env.local)")

    # PostgREST upsert: POST with Prefer: resolution=merge-duplicates
    # The unique constraint on (service_name, key_type) handles the merge.
    payload = json.dumps([{
        "service_name": service_name,
        "key_type":     key_type,
        "key_value":    key_value,
    }]).encode()

    req = urllib.request.Request(
        f"{base_url}/rest/v1/syntharra_vault",
        data=payload,
        headers={
            "apikey":          service_key,
            "Authorization":   f"Bearer {service_key}",
            "Content-Type":    "application/json",
            "Prefer":          "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        sys.exit(f"Supabase error {e.code}: {body}")

    if status in (200, 201):
        masked = key_value[:8] + "..." if len(key_value) > 8 else "***"
        print(f"[vault] upserted: service={service_name!r} key={key_type!r} value={masked}")
    else:
        sys.exit(f"Unexpected status {status}")


if __name__ == "__main__":
    main()
