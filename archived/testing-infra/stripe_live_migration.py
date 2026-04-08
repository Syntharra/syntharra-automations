"""
Stripe TEST -> LIVE migration script. Track A1 prep.
Target repo path: tools/stripe_live_migration.py

USAGE:
    export STRIPE_TEST_KEY=sk_test_...
    export STRIPE_LIVE_KEY=sk_live_...
    python tools/stripe_live_migration.py --dry-run
    python tools/stripe_live_migration.py --execute

WHAT IT DOES:
1. Reads current TEST products / prices / coupons (source of truth)
2. Creates matching objects in LIVE with same names / amounts / metadata
3. Idempotent: skips anything already present in live with the same name
4. Creates webhook endpoint in LIVE pointing to n8n
5. Prints exact env vars to set on Railway syntharra-checkout

SAFETY:
- Dry-run by default (no flag = error, must pick --dry-run or --execute)
- Will NOT touch test mode
- Will NOT push to GitHub
"""
import os, sys, json, argparse
import stripe

WEBHOOK_URL = "https://n8n.syntharra.com/webhook/syntharra-stripe-webhook"
WEBHOOK_EVENTS = ["checkout.session.completed", "customer.subscription.updated",
                  "customer.subscription.deleted", "invoice.payment_failed"]

EXPECTED_PRODUCTS = {
    "Standard": "prod_UC0hZtntx3VEg2",
    "Premium":  "prod_UC0mYC90fSItcq",
}
EXPECTED_PRICES = [
    ("Standard", "Monthly", 49700, "month"),
    ("Standard", "Annual",  41400, "month"),
    ("Standard", "Setup",  149900, None),
    ("Premium",  "Monthly", 99700, "month"),
    ("Premium",  "Annual",  83100, "month"),
    ("Premium",  "Setup",  249900, None),
]
EXPECTED_COUPONS = [
    ("FOUNDING-STANDARD", 149900),
    ("FOUNDING-PREMIUM",  249900),
    ("CLOSER-250",         25000),
    ("CLOSER-500",         50000),
    ("CLOSER-750",         75000),
    ("CLOSER-1000",       100000),
]

def log(msg, dry):
    print(f"[{'DRY' if dry else 'LIVE'}] {msg}")

def find_product_by_name(name):
    for p in stripe.Product.list(limit=100, active=True).auto_paging_iter():
        if p.name == name: return p
    return None

def find_coupon_by_name(name):
    for c in stripe.Coupon.list(limit=100).auto_paging_iter():
        if (c.name or c.id) == name: return c
    return None

def migrate(dry):
    test_key = os.environ["STRIPE_TEST_KEY"]
    live_key = os.environ["STRIPE_LIVE_KEY"]
    if not live_key.startswith("sk_live_"): sys.exit("STRIPE_LIVE_KEY must start with sk_live_")
    if not test_key.startswith("sk_test_"): sys.exit("STRIPE_TEST_KEY must start with sk_test_")

    new_ids = {"products": {}, "prices": {}, "coupons": {}, "webhook": None}

    # PRODUCTS
    for plan, test_id in EXPECTED_PRODUCTS.items():
        stripe.api_key = test_key
        src = stripe.Product.retrieve(test_id)
        log(f"product {plan}: source name='{src.name}'", dry)
        stripe.api_key = live_key
        existing = find_product_by_name(src.name)
        if existing:
            log(f"  -> exists in live: {existing.id} (skip)", dry)
            new_ids["products"][plan] = existing.id
            continue
        if dry:
            new_ids["products"][plan] = "WOULD_CREATE"
        else:
            created = stripe.Product.create(name=src.name, description=src.description,
                                            metadata=dict(src.metadata or {}))
            new_ids["products"][plan] = created.id
            log(f"  -> created: {created.id}", dry)

    # PRICES
    for plan, kind, amount, interval in EXPECTED_PRICES:
        stripe.api_key = live_key
        prod_id = new_ids["products"].get(plan)
        if not prod_id or prod_id == "WOULD_CREATE":
            log(f"price {plan}/{kind}: skipped (no live product yet)", dry)
            continue
        nickname = f"{plan} {kind}"
        existing = None
        for p in stripe.Price.list(product=prod_id, limit=100, active=True).auto_paging_iter():
            if p.nickname == nickname and p.unit_amount == amount:
                existing = p; break
        if existing:
            log(f"price {nickname}: exists {existing.id} (skip)", dry)
            new_ids["prices"][nickname] = existing.id
            continue
        params = dict(product=prod_id, unit_amount=amount, currency="usd", nickname=nickname)
        if interval: params["recurring"] = {"interval": interval}
        if dry:
            new_ids["prices"][nickname] = "WOULD_CREATE"
            log(f"price {nickname}: would create ${amount/100} {interval or 'one-time'}", dry)
        else:
            created = stripe.Price.create(**params)
            new_ids["prices"][nickname] = created.id
            log(f"price {nickname}: created {created.id}", dry)

    # COUPONS
    for code, amount_off in EXPECTED_COUPONS:
        stripe.api_key = live_key
        existing = find_coupon_by_name(code)
        if existing:
            log(f"coupon {code}: exists {existing.id} (skip)", dry)
            new_ids["coupons"][code] = existing.id
            continue
        if dry:
            new_ids["coupons"][code] = "WOULD_CREATE"
            log(f"coupon {code}: would create ${amount_off/100} off once", dry)
        else:
            created = stripe.Coupon.create(name=code, amount_off=amount_off, currency="usd", duration="once")
            stripe.PromotionCode.create(coupon=created.id, code=code)
            new_ids["coupons"][code] = created.id
            log(f"coupon {code}: created {created.id} + promo code", dry)

    # WEBHOOK
    stripe.api_key = live_key
    existing_wh = None
    for wh in stripe.WebhookEndpoint.list(limit=100).auto_paging_iter():
        if wh.url == WEBHOOK_URL: existing_wh = wh; break
    if existing_wh:
        log(f"webhook: exists {existing_wh.id} (skip)", dry)
        new_ids["webhook"] = existing_wh.id
    else:
        if dry:
            new_ids["webhook"] = "WOULD_CREATE"
            log(f"webhook: would create -> {WEBHOOK_URL}", dry)
        else:
            wh = stripe.WebhookEndpoint.create(url=WEBHOOK_URL, enabled_events=WEBHOOK_EVENTS)
            new_ids["webhook"] = wh.id
            log(f"webhook: created {wh.id}", dry)
            print(f"\n*** WEBHOOK SIGNING SECRET (store in vault NOW, only shown once) ***")
            print(f"    {wh.secret}\n")

    print("\n========== NEW LIVE IDs ==========")
    print(json.dumps(new_ids, indent=2))
    print("\n========== NEXT MANUAL STEPS ==========")
    print("1. Store webhook signing secret in syntharra_vault")
    print("2. Set Railway env on syntharra-checkout (e3df3e6d): STRIPE_SECRET_KEY=sk_live_..., STRIPE_WEBHOOK_SECRET=whsec_...")
    print("3. Patch docs/context/STRIPE.md with new IDs")
    print("4. Real $1 charge test on checkout.syntharra.com, then refund")

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    migrate(dry=args.dry_run)

if __name__ == "__main__":
    main()
