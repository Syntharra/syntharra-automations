#!/usr/bin/env python3
"""
fetch_vault.py — Fetch a single credential from `syntharra_vault`.

Usage:
  python tools/fetch_vault.py "<service_name>" <key_type>

Example:
  export N8N_API_KEY=$(python tools/fetch_vault.py "n8n Railway" api_key)

Bootstrap requirement: SUPABASE_URL and SUPABASE_SERVICE_KEY must be exported
in the current shell (typically via `source .env.local`). If you don't have a
`.env.local`, ask Dan to drop it in the repo root or fetch values from the
Supabase MCP and write them yourself.

Prints ONLY the credential value to stdout (no surrounding whitespace) so it
can be safely interpolated into env-var assignments.
"""
import json
import os
import sys
import urllib.parse
import urllib.request


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: fetch_vault.py <service_name> <key_type>")
    service_name, key_type = sys.argv[1], sys.argv[2]

    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")
    if not base_url or not service_key:
        sys.exit("SUPABASE_URL + SUPABASE_SERVICE_KEY must be set (source .env.local)")

    qs = urllib.parse.urlencode({
        "service_name": f"eq.{service_name}",
        "key_type": f"eq.{key_type}",
        "select": "key_value",
    })
    req = urllib.request.Request(
        f"{base_url}/rest/v1/syntharra_vault?{qs}",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
        },
    )
    with urllib.request.urlopen(req) as resp:
        rows = json.loads(resp.read().decode())

    if not rows:
        sys.exit(f"vault row not found: service={service_name!r} key={key_type!r}")

    # Print without trailing newline so $(...) interpolation is clean.
    sys.stdout.write(rows[0]["key_value"])


if __name__ == "__main__":
    main()
