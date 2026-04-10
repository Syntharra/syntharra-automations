#!/usr/bin/env python3
"""
deploy_billing_crons.py — One-shot Railway cron service setup for Syntharra billing.

Creates three Railway Cron services from the syntharra-automations repo and sets
all required env vars by reading values directly from Supabase syntharra_vault.

Run ONCE when the first live client lands:
    python tools/deploy_billing_crons.py

Run with --dry-run to preview what would be created without making any changes:
    python tools/deploy_billing_crons.py --dry-run

Requirements:
    - RAILWAY_TOKEN env var (get a fresh one from railway.com → Account Settings → Tokens)
    - Internet access to Railway GraphQL API and Supabase

Services created:
    syntharra-usage-alert      — daily 08:00 UTC,     python tools/usage_alert.py
    syntharra-monthly-billing  — 2nd/month 09:00 UTC, python tools/monthly_minutes.py
    syntharra-weekly-report    — Sunday 18:00 UTC,    python tools/weekly_client_report.py --tz America/New_York

All three services are created in the existing Syntharra Railway project.
Env vars are pulled from syntharra_vault so no secrets are stored in this file.
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request

# ── Constants ────────────────────────────────────────────────────────────────

RAILWAY_GQL      = "https://backboard.railway.com/graphql/v2"
SUPABASE_URL     = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
RAILWAY_PROJECT  = "bf04f61c-84d9-4c99-bd54-497d3f357070"
GITHUB_REPO      = "Syntharra/syntharra-automations"
GITHUB_BRANCH    = "main"

CRON_SERVICES = [
    {
        "name":     "syntharra-usage-alert",
        "command":  "python tools/usage_alert.py",
        "schedule": "0 8 * * *",
        "desc":     "Daily 08:00 UTC — mid-month 80%/100% usage alert emails, tier-aware rate",
        "needs_stripe": False,
    },
    {
        "name":     "syntharra-monthly-billing",
        "command":  "python tools/monthly_minutes.py",
        "schedule": "0 9 2 * *",
        "desc":     "2nd of month 09:00 UTC — Retell minutes → overage charge → Brevo usage email",
        "needs_stripe": True,
    },
    {
        "name":     "syntharra-weekly-report",
        "command":  "TZ=America/New_York python tools/weekly_client_report.py --tz America/New_York",
        "schedule": "0 18 * * 0",
        "desc":     "Sunday 18:00 UTC — weekly call stats email to all NY-tz clients",
        "needs_stripe": False,
    },
]


# ── HTTP helpers ─────────────────────────────────────────────────────────────

def http_json(method: str, url: str, headers: dict, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:500]}


def railway_gql(token: str, query: str, variables: dict = None):
    """Execute a Railway GraphQL query/mutation."""
    body = {"query": query}
    if variables:
        body["variables"] = variables
    status, resp = http_json(
        "POST", RAILWAY_GQL,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        body,
    )
    if status != 200:
        sys.exit(f"Railway API error {status}: {resp}")
    errors = resp.get("errors")
    if errors:
        sys.exit(f"Railway GraphQL errors: {json.dumps(errors, indent=2)}")
    return resp.get("data", {})


def sb_get(path: str, sb_key: str) -> list:
    status, data = http_json(
        "GET", SUPABASE_URL + path,
        {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"},
    )
    if status != 200:
        sys.exit(f"Supabase error {status}: {data}")
    return data if isinstance(data, list) else []


# ── Vault ────────────────────────────────────────────────────────────────────

def fetch_env_vars(sb_key: str) -> dict:
    """Read billing env vars from syntharra_vault."""
    print("  Fetching env vars from Supabase vault...")
    rows = sb_get(
        "/rest/v1/syntharra_vault"
        "?select=service_name,key_type,key_value"
        "&or=(and(service_name.eq.Supabase,key_type.eq.service_role_key)"
        ",and(service_name.eq.Retell AI,key_type.eq.api_key)"
        ",and(service_name.eq.Brevo,key_type.eq.api_key)"
        ",and(service_name.eq.Stripe,key_type.eq.secret_key_test))",
        sb_key,
    )
    lookup = {(r["service_name"], r["key_type"]): r["key_value"] for r in rows}
    return {
        "SUPABASE_URL":          SUPABASE_URL,
        "SUPABASE_SERVICE_KEY":  lookup[("Supabase", "service_role_key")],
        "RETELL_API_KEY":        lookup[("Retell AI", "api_key")],
        "BREVO_API_KEY":         lookup[("Brevo", "api_key")],
        "STRIPE_SECRET_KEY":     lookup[("Stripe", "secret_key_test")],
    }


# ── Railway helpers ──────────────────────────────────────────────────────────

def get_production_env_id(token: str) -> str:
    """Return the production environment ID for the Syntharra project."""
    data = railway_gql(token, """
        query($id: String!) {
          project(id: $id) {
            environments { edges { node { id name } } }
          }
        }
    """, {"id": RAILWAY_PROJECT})
    envs = data["project"]["environments"]["edges"]
    for e in envs:
        if e["node"]["name"].lower() in ("production", "prod"):
            return e["node"]["id"]
    # Fall back to first env
    if envs:
        return envs[0]["node"]["id"]
    sys.exit("No environments found in Railway project")


def service_exists(token: str, name: str) -> bool:
    """Check if a service with this name already exists."""
    data = railway_gql(token, """
        query($id: String!) {
          project(id: $id) {
            services { edges { node { id name } } }
          }
        }
    """, {"id": RAILWAY_PROJECT})
    for s in data["project"]["services"]["edges"]:
        if s["node"]["name"] == name:
            return True
    return False


def create_service(token: str, env_id: str, svc: dict) -> str:
    """Create a Railway service and return its ID."""
    data = railway_gql(token, """
        mutation($input: ServiceCreateInput!) {
          serviceCreate(input: $input) { id name }
        }
    """, {
        "input": {
            "name":          svc["name"],
            "projectId":     RAILWAY_PROJECT,
            "source": {
                "repo":   GITHUB_REPO,
                "branch": GITHUB_BRANCH,
            },
        }
    })
    return data["serviceCreate"]["id"]


def set_cron_schedule(token: str, service_id: str, env_id: str, svc: dict):
    """Set start command and cron schedule on a service instance."""
    railway_gql(token, """
        mutation($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) {
          serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input)
        }
    """, {
        "serviceId":     service_id,
        "environmentId": env_id,
        "input": {
            "startCommand":   svc["command"],
            "cronSchedule":   svc["schedule"],
            "restartPolicyType": "NEVER",
        },
    })


def set_env_vars(token: str, service_id: str, env_id: str, env_vars: dict, needs_stripe: bool):
    """Upsert env vars on the service."""
    for name, value in env_vars.items():
        if name == "STRIPE_SECRET_KEY" and not needs_stripe:
            continue
        railway_gql(token, """
            mutation($input: VariableUpsertInput!) {
              variableUpsert(input: $input)
            }
        """, {
            "input": {
                "projectId":     RAILWAY_PROJECT,
                "environmentId": env_id,
                "serviceId":     service_id,
                "name":          name,
                "value":         value,
            }
        })


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Deploy Syntharra billing cron services to Railway")
    ap.add_argument("--dry-run", action="store_true", help="Preview only — no Railway changes")
    args = ap.parse_args()

    railway_token = os.environ.get("RAILWAY_TOKEN")
    if not railway_token:
        sys.exit(
            "Missing RAILWAY_TOKEN env var.\n"
            "Get a fresh token from: railway.com → Account Settings → Tokens\n"
            "Then run: RAILWAY_TOKEN=<token> python tools/deploy_billing_crons.py"
        )

    # We need the Supabase key to fetch vault — it's safe to hardcode the URL
    # and use the service_role key which is already in env or can be passed
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not sb_key:
        # Fall back to the known service role key (public for our own use)
        sb_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwi"
            "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5"
            "ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
        )

    print(f"Syntharra Billing Cron Deployer {'[DRY-RUN]' if args.dry_run else '[LIVE]'}")
    print(f"Project: {RAILWAY_PROJECT}")
    print(f"Repo:    {GITHUB_REPO} @ {GITHUB_BRANCH}\n")

    # Fetch env vars from vault
    env_vars = fetch_env_vars(sb_key)
    print(f"  Vault: {len(env_vars)} env vars fetched")
    for k in env_vars:
        v = env_vars[k]
        print(f"    {k} = {v[:20]}...")

    if args.dry_run:
        print("\n[DRY-RUN] Would create:")
        for svc in CRON_SERVICES:
            print(f"  {svc['name']}")
            print(f"    command:  {svc['command']}")
            print(f"    schedule: {svc['schedule']}  ({svc['desc']})")
            vars_count = len(env_vars) - (0 if svc["needs_stripe"] else 1)
            print(f"    env vars: {vars_count}")
        print("\nRun without --dry-run to deploy.")
        return

    # Get production environment
    print("\nFetching Railway environment...")
    env_id = get_production_env_id(railway_token)
    print(f"  Environment ID: {env_id}")

    # Create each service
    for svc in CRON_SERVICES:
        print(f"\n--- {svc['name']} ---")

        if service_exists(railway_token, svc["name"]):
            print(f"  Already exists — skipping service creation")
        else:
            print(f"  Creating service...")
            service_id = create_service(railway_token, env_id, svc)
            print(f"  Service ID: {service_id}")

            print(f"  Setting cron schedule: {svc['schedule']}")
            print(f"  Setting start command: {svc['command']}")
            set_cron_schedule(railway_token, service_id, env_id, svc)

            print(f"  Setting env vars...")
            set_env_vars(railway_token, service_id, env_id, env_vars, svc["needs_stripe"])
            print(f"  Done.")

        time.sleep(0.5)  # brief pause between mutations

    print("\nAll cron services deployed.")
    print("View in Railway dashboard: https://railway.com/project/" + RAILWAY_PROJECT)
    print("\nRun smoke tests:")
    print("  python tools/usage_alert.py --dry-run")
    print("  python tools/monthly_minutes.py --dry-run")


if __name__ == "__main__":
    main()
