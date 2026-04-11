#!/usr/bin/env python3
"""
patch_onboarding_workflow_add_pilot_branch.py

Adds Phase 0 pilot handling to the HVAC Standard onboarding workflow
(`4Hx7aRdzMl5N0uJP`) by patching the `Reconcile: Check Stripe Payment` Code
node's jsCode in-place. NO new nodes, NO connection changes.

Why this approach (deviation from plan Task 15):
  The plan assumed `client_subscriptions` was written by an HTTP node near
  the webhook trigger, and proposed inserting an IF + Set Pilot Defaults
  branch after the webhook. Inspection of the live workflow on 2026-04-11
  revealed `client_subscriptions` is actually written by the
  `Reconcile: Check Stripe Payment` Code node (deep in the pipeline, after
  HubSpot deal update). The IF+Set approach would have done nothing useful.
  The correct surgical patch is to add a pilot detection block at the top
  of Reconcile's jsCode that:
    (a) reaches back to the webhook to read `pilot_mode` + tracking fields
    (b) on pilot: skips the 60s Stripe wait, writes client_subscriptions with
        status='pilot' + pilot_* columns + tracking, returns
    (c) on non-pilot: falls through to existing paid-path code (byte-identical)
  This is byte-identical for paid path verification (the regression gate).

Inputs:
  - Backup file: docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json

Modes:
  --dry-run   Print the new jsCode + line count delta. No network call.
  --apply     PUT updated workflow to n8n via Railway REST API.

Required env vars (source .env.local):
  N8N_API_KEY
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

WORKFLOW_ID = "4Hx7aRdzMl5N0uJP"
N8N_BASE = "https://n8n.syntharra.com"
BACKUP_PATH = Path("docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-pilot-branch.json")
TARGET_NODE = "Reconcile: Check Stripe Payment"
PILOT_MARKER = "// === Phase 0 pilot block === //"


PILOT_BLOCK = '''// === Phase 0 pilot block === //
// Inserted 2026-04-11. Reaches back to JotForm Webhook Trigger to read the
// `pilot_mode` hidden field. If true, writes client_subscriptions with
// status='pilot' + pilot_* columns + tracking, then returns immediately
// (skipping the 60s Stripe wait + Stripe lookup). Otherwise falls through to
// the existing paid-path reconciliation below — byte-identical.
let _isPilot = false;
let _trackingFields = {
  stx_asset_id: null,
  utm_source: null,
  utm_medium: null,
  utm_campaign: null,
  utm_content: null,
  utm_term: null,
};
try {
  const _wh = $('JotForm Webhook Trigger').first().json;
  const _wb = _wh.body || _wh;
  let _rq = {};
  if (_wb && _wb.rawRequest) {
    try { _rq = JSON.parse(_wb.rawRequest); } catch(e) {}
  }
  const _merged = { ..._wb, ..._rq };
  _isPilot = String(_merged.pilot_mode || '').toLowerCase() === 'true';
  _trackingFields = {
    stx_asset_id: _merged.stx_asset_id || null,
    utm_source:   _merged.utm_source   || null,
    utm_medium:   _merged.utm_medium   || null,
    utm_campaign: _merged.utm_campaign || null,
    utm_content:  _merged.utm_content  || null,
    utm_term:     _merged.utm_term     || null,
  };
} catch(e) {
  _isPilot = false;
}

if (_isPilot) {
  const _d0 = $input.first().json;
  const _email0 = (_d0.email || _d0.notification_email || _d0.client_email || '').toLowerCase();
  const _agentId0 = _d0.agent_id || _d0.retell_agent_id || '';
  const _now0 = new Date();
  const _pilotEnds0 = new Date(_now0.getTime() + 14*24*60*60*1000);
  const _SBURL0 = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const _SBKEY0 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg';
  const _SBHEAD0 = { apikey: _SBKEY0, Authorization: 'Bearer ' + _SBKEY0 };
  const _utm0 = {
    source:   _trackingFields.utm_source,
    medium:   _trackingFields.utm_medium,
    campaign: _trackingFields.utm_campaign,
    content:  _trackingFields.utm_content,
    term:     _trackingFields.utm_term,
  };
  if (_agentId0) {
    await this.helpers.httpRequest({
      method: 'POST',
      url: _SBURL0 + '/rest/v1/client_subscriptions',
      headers: { ..._SBHEAD0, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
      body: {
        agent_id: _agentId0,
        plan_type: 'standard',
        client_email: _email0,
        company_name: _d0.company_name || null,
        tier: 'standard',
        billing_cycle: 'monthly',
        pilot_mode: true,
        status: 'pilot',
        pilot_started_at: _now0.toISOString(),
        pilot_ends_at:    _pilotEnds0.toISOString(),
        pilot_minutes_allotted: 200,
        pilot_minutes_used: 0,
        first_touch_asset_id: _trackingFields.stx_asset_id,
        last_touch_asset_id:  _trackingFields.stx_asset_id,
        first_touch_utm: _utm0,
        last_touch_utm:  _utm0,
      },
      json: true,
    });
    console.log('[PILOT] Inserted client_subscriptions for', _agentId0, 'pilot_ends_at=', _pilotEnds0.toISOString());
  } else {
    console.log('[PILOT] No agent_id, skipping client_subscriptions insert');
  }
  return [{ json: {
    ..._d0,
    stripe_reconciliation: 'pilot_skipped',
    tier: 'standard',
    pilot_mode: true,
    status: 'pilot',
    pilot_ends_at: _pilotEnds0.toISOString(),
  } }];
}
// === Phase 0 pilot block end === //

'''


def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}  (did you `source .env.local`?)")
    return v


def n8n_api(method, path, body=None):
    url = f"{N8N_BASE}{path}"
    headers = {"X-N8N-API-KEY": env("N8N_API_KEY"), "Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", errors="replace")
        sys.exit(f"n8n API {method} {path} -> HTTP {e.code}: {body_txt[:1000]}")


def load_backup():
    if not BACKUP_PATH.exists():
        sys.exit(f"Backup missing at {BACKUP_PATH} -- run Task 14 first.")
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def patch_jscode(old_code: str) -> tuple[str, bool]:
    """Insert PILOT_BLOCK at the top of jsCode, after the first comment line.
    Returns (new_code, was_already_patched)."""
    if PILOT_MARKER in old_code:
        return old_code, True

    lines = old_code.split("\n")
    # Find the first non-comment, non-blank line. Insert the block before it,
    # but keep the original opening comment line at the top for context.
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//") or not stripped:
            continue
        insert_at = i
        break

    new_lines = lines[:insert_at] + PILOT_BLOCK.split("\n") + lines[insert_at:]
    return "\n".join(new_lines), False


def find_node(wf, name):
    for n in wf["nodes"]:
        if n["name"] == name:
            return n
    return None


def main():
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true", help="print new jsCode, no network")
    grp.add_argument("--apply", action="store_true", help="PUT to n8n Railway")
    args = ap.parse_args()

    wf = load_backup()
    node = find_node(wf, TARGET_NODE)
    if not node:
        sys.exit(f"Target node {TARGET_NODE!r} not found in backup")

    old_code = node["parameters"]["jsCode"]
    new_code, already = patch_jscode(old_code)
    if already:
        print(f"NOTE: pilot block already present in {TARGET_NODE!r}; nothing to do.", file=sys.stderr)
        return

    old_lines = len(old_code.split("\n"))
    new_lines = len(new_code.split("\n"))
    delta = new_lines - old_lines

    print(f"Target node: {TARGET_NODE!r}", file=sys.stderr)
    print(f"Old jsCode: {old_lines} lines / {len(old_code)} chars", file=sys.stderr)
    print(f"New jsCode: {new_lines} lines / {len(new_code)} chars", file=sys.stderr)
    print(f"Delta:      +{delta} lines", file=sys.stderr)
    print("", file=sys.stderr)

    if args.dry_run:
        print("DRY RUN -- showing first 20 lines of new jsCode:", file=sys.stderr)
        for line in new_code.split("\n")[:20]:
            print(f"  | {line}", file=sys.stderr)
        print("  ...", file=sys.stderr)
        print("", file=sys.stderr)
        print("Pilot block inserted between line 1 (existing comment) and the original code start.", file=sys.stderr)
        print("Paid path bytes are unchanged below the pilot block.", file=sys.stderr)
        return

    # Apply: build PUT payload
    node["parameters"]["jsCode"] = new_code
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData") or None,
    }
    print(f"PUT /api/v1/workflows/{WORKFLOW_ID} ...", file=sys.stderr)
    result = n8n_api("PUT", f"/api/v1/workflows/{WORKFLOW_ID}", body=payload)
    print(f"Updated workflow id: {result.get('id')}", file=sys.stderr)
    print(f"Total nodes:         {len(result.get('nodes', []))}", file=sys.stderr)
    print(f"Active:              {result.get('active')}", file=sys.stderr)
    print("", file=sys.stderr)
    if not result.get("active"):
        print("[!] Workflow appears inactive -- run /activate next", file=sys.stderr)


if __name__ == "__main__":
    main()
