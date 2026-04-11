#!/usr/bin/env python3
"""
stripe_pilot_setup.py — One-shot idempotent Stripe bootstrap for Phase 0 pilot.

Creates (or reuses) the HVAC Standard product, $697/mo recurring price, and
prints the IDs so they can be copied into docs/REFERENCE.md and into
tools/pilot_lifecycle.py's STRIPE_HVAC_STANDARD_PRICE_ID constant.

Marker metadata ensures re-runs do NOT create duplicates:
  product.metadata.syntharra_product = 'hvac_standard'
  price.metadata.syntharra_price     = 'hvac_standard_monthly'

Also prints a sanity-check example Setup Intent body that the backend dashboard
endpoint will use (usage='off_session', payment_method_types=['card']).

Usage:
    export STRIPE_SECRET_KEY=$(python tools/fetch_vault.py "Stripe" secret_key_test)
    python tools/stripe_pilot_setup.py --dry-run    # list actions, no writes
    python tools/stripe_pilot_setup.py              # create (idempotent)

Required env vars:
    STRIPE_SECRET_KEY  — Stripe test mode secret key (sk_test_...)
                         Phase 0 uses test mode; flip to live key only after
                         the Stripe live-mode migration is complete.

Stdlib only. Mirrors pattern from tools/monthly_minutes.py for Stripe REST.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


PRODUCT_MARKER_KEY = "syntharra_product"
PRODUCT_MARKER_VALUE = "hvac_standard"
PRICE_MARKER_KEY = "syntharra_price"
PRICE_MARKER_VALUE = "hvac_standard_monthly"
PRODUCT_NAME = "Syntharra HVAC Standard"
PRICE_AMOUNT_CENTS = 69700  # $697.00
PRICE_CURRENCY = "usd"
PRICE_INTERVAL = "month"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing env var: {name}")
    return v


def stripe_request(method: str, path: str, body=None) -> dict:
    url = "https://api.stripe.com" + path
    headers = {
        "Authorization": f"Bearer {env('STRIPE_SECRET_KEY')}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    raw = None
    if body is not None:
        raw = urllib.parse.urlencode(_flatten(body)).encode("utf-8")
    req = urllib.request.Request(url, data=raw, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Stripe {method} {path} → {e.code} {e.read().decode()[:500]}")


def _flatten(body: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for k, v in body.items():
        if isinstance(v, dict):
            for ik, iv in v.items():
                out.append((f"{k}[{ik}]", str(iv)))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                out.append((f"{k}[{i}]", str(item)))
        else:
            out.append((k, str(v)))
    return out


def find_existing_product() -> dict | None:
    """Use the Stripe search API to find a product with our marker."""
    qs = urllib.parse.urlencode({
        "query": f"metadata['{PRODUCT_MARKER_KEY}']:'{PRODUCT_MARKER_VALUE}'",
    })
    data = stripe_request("GET", f"/v1/products/search?{qs}")
    items = data.get("data") or []
    return items[0] if items else None


def find_existing_price(product_id: str) -> dict | None:
    qs = urllib.parse.urlencode({
        "query": f"metadata['{PRICE_MARKER_KEY}']:'{PRICE_MARKER_VALUE}' AND product:'{product_id}'",
    })
    data = stripe_request("GET", f"/v1/prices/search?{qs}")
    items = data.get("data") or []
    return items[0] if items else None


def create_product(dry_run: bool) -> dict:
    existing = find_existing_product()
    if existing:
        print(f"[product] reuse {existing['id']} ({existing.get('name')})")
        return existing
    if dry_run:
        print(f"[product] DRY-RUN would create name={PRODUCT_NAME!r}")
        return {"id": "prod_DRYRUN", "name": PRODUCT_NAME}
    body = {
        "name": PRODUCT_NAME,
        "metadata": {PRODUCT_MARKER_KEY: PRODUCT_MARKER_VALUE},
    }
    data = stripe_request("POST", "/v1/products", body)
    print(f"[product] CREATED {data['id']}")
    return data


def create_price(product_id: str, dry_run: bool) -> dict:
    existing = find_existing_price(product_id)
    if existing:
        print(f"[price]   reuse {existing['id']} ({existing.get('unit_amount')} {existing.get('currency')})")
        return existing
    if dry_run:
        print(f"[price]   DRY-RUN would create ${PRICE_AMOUNT_CENTS/100:.2f}/{PRICE_INTERVAL}")
        return {"id": "price_DRYRUN"}
    body = {
        "product": product_id,
        "unit_amount": PRICE_AMOUNT_CENTS,
        "currency": PRICE_CURRENCY,
        "recurring": {"interval": PRICE_INTERVAL},
        "metadata": {PRICE_MARKER_KEY: PRICE_MARKER_VALUE},
    }
    data = stripe_request("POST", "/v1/prices", body)
    print(f"[price]   CREATED {data['id']}")
    return data


def print_setup_intent_template() -> None:
    """Just log a reference body — we don't create a real SetupIntent here.
    The backend dashboard endpoint (§ 6.6) creates one per-user on demand.
    """
    print("\n[setup_intent] reference body for backend handler:")
    print(json.dumps({
        "usage": "off_session",
        "payment_method_types": ["card"],
        "customer": "<stripe_customer_id>",
        "metadata": {"source": "syntharra_pilot"},
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="Bootstrap Stripe product/price for HVAC Standard pilot")
    ap.add_argument("--dry-run", action="store_true", help="List what would be created; do not write")
    args = ap.parse_args()

    print(f"stripe_pilot_setup.py dry_run={args.dry_run}")

    product = create_product(args.dry_run)
    price = create_price(product["id"], args.dry_run)
    print_setup_intent_template()

    print("\n=== COPY INTO docs/REFERENCE.md ===")
    print(f"Stripe product (HVAC Standard): {product['id']}")
    print(f"Stripe price (HVAC Standard, $697/mo): {price['id']}")
    print("\n=== COPY INTO tools/pilot_lifecycle.py ===")
    print(f'STRIPE_HVAC_STANDARD_PRICE_ID = "{price["id"]}"')
    print("\nDone.")


if __name__ == "__main__":
    main()
