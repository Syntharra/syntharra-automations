#!/usr/bin/env python3
"""
patch_onboarding_workflow_pilot_welcome.py

Phase 0 Day 3 followup. Patches the `Send Welcome Email` Code node in the
HVAC Standard onboarding workflow (`4Hx7aRdzMl5N0uJP`) to skip the existing
"you're live at $697/mo" tier-aware paid welcome for pilots, and instead
send the Brevo pilot-welcome template (ID 7) immediately.

Why a SECOND patcher and not the Day 2 one:
  Day 2's patch_onboarding_workflow_add_pilot_branch.py is hardcoded to the
  Reconcile: Check Stripe Payment node. This script targets Send Welcome Email
  with a different pilot block. Both are idempotent via marker comments and
  both keep the paid path byte-identical below the pilot block.

Idempotent: re-running is a no-op once the marker is present.

Modes:
  --dry-run   Print line counts + first 20 lines of new jsCode. No network.
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
# Live workflow now contains the Day 2 Reconcile patch — pull fresh, do not
# reuse the pre-pilot-branch backup.
PRE_BACKUP_PATH  = Path("docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-pre-welcome-patch.json")
POST_BACKUP_PATH = Path("docs/audits/n8n-backups-20260411/4Hx7aRdzMl5N0uJP-post-welcome-patch.json")

TARGET_NODE = "Send Welcome Email"
PILOT_MARKER = "// === Phase 0 pilot welcome block === //"


PILOT_BLOCK = '''// === Phase 0 pilot welcome block === //
// Inserted 2026-04-11 (Day 3 followup). Reaches back to JotForm Webhook
// Trigger to read pilot_mode. If true, sends Brevo template id 7 (pilot-
// welcome) immediately and returns. Otherwise falls through to the existing
// paid "you're live $697/mo" tier-aware welcome below — byte-identical.
let _pilotMode = false;
try {
  const _wh = $('JotForm Webhook Trigger').first().json;
  const _wb = _wh.body || _wh;
  let _rq = {};
  if (_wb && _wb.rawRequest) {
    try { _rq = JSON.parse(_wb.rawRequest); } catch(e) {}
  }
  _pilotMode = String(({ ..._wb, ..._rq }).pilot_mode || '').toLowerCase() === 'true';
} catch(e) {
  _pilotMode = false;
}

if (_pilotMode) {
  // Phase 0 pilot welcome: send Brevo template id 7 with pilot params, return.
  const _sb0  = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
  const _sbk0 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg';
  const _vr0  = await this.helpers.httpRequest({
    method: 'GET',
    url: _sb0 + '/rest/v1/syntharra_vault?service_name=eq.Brevo&key_type=eq.api_key&select=key_value',
    headers: { apikey: _sbk0, Authorization: 'Bearer ' + _sbk0 },
    json: true,
  });
  const _BREVO_KEY0 = _vr0 && _vr0[0] && _vr0[0].key_value;
  if (!_BREVO_KEY0) {
    return [{ json: { ...$input.first().json, _welcome_sent: false, _welcome_error: 'pilot: Brevo key not in vault', pilot_mode: true } }];
  }
  const _in0       = $input.first().json;
  const _email0    = _in0.lead_email || _in0.client_email || _in0.email || '';
  const _company0  = _in0.company_name || 'your company';
  const _agentId0  = _in0.agent_id || _in0.retell_agent_id || '';
  const _phone0    = _in0.telnyx_number || _in0.twilio_from || _in0.twilio_number || _in0.agent_phone_number || '';
  if (!_email0) {
    return [{ json: { ..._in0, _skip: true, _reason: 'pilot missing email', _welcome_sent: false, pilot_mode: true } }];
  }
  const _params0 = {
    first_name: 'there',
    company_name: _company0,
    minutes_used: 0,
    minutes_remaining: 200,
    minutes_allotted: 200,
    days_remaining: 14,
    add_card_url:       'https://syntharra.com/add-card?a='   + _agentId0,
    dashboard_url:      'https://syntharra.com/dashboard.html?a=' + _agentId0,
    pilot_phone_number: _phone0,
    unsubscribe_url: '{{unsubscribe}}',
  };
  try {
    await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.brevo.com/v3/smtp/email',
      headers: { 'api-key': _BREVO_KEY0, 'accept': 'application/json', 'content-type': 'application/json' },
      json: true,
      body: {
        sender:     { name: 'Syntharra', email: 'daniel@syntharra.com' },
        to:         [{ email: _email0, name: _company0 }],
        templateId: 7,
        params:     _params0,
      },
    });
    console.log('[PILOT] welcome (templateId=7) sent to', _email0, 'agent=', _agentId0);
    return [{ json: { ..._in0, _welcome_sent: true, pilot_mode: true, _welcome_template_id: 7 } }];
  } catch (e) {
    console.log('[PILOT] welcome failed:', e.message);
    return [{ json: { ..._in0, _welcome_sent: false, _welcome_error: e.message, pilot_mode: true } }];
  }
}
// === Phase 0 pilot welcome block end === //

'''


def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}  (did you `source .env.local`?)")
    return v


def n8n_api(method, path, body=None, raw=False):
    url = f"{N8N_BASE}{path}"
    headers = {"X-N8N-API-KEY": env("N8N_API_KEY"), "Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode() if raw else json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", errors="replace")
        sys.exit(f"n8n API {method} {path} -> HTTP {e.code}: {body_txt[:1000]}")


def fetch_live_workflow():
    return n8n_api("GET", f"/api/v1/workflows/{WORKFLOW_ID}")


def patch_jscode(old_code: str) -> tuple[str, bool]:
    """Insert PILOT_BLOCK at the top of jsCode, after the leading
    comment/blank lines. Returns (new_code, was_already_patched)."""
    if PILOT_MARKER in old_code:
        return old_code, True
    lines = old_code.split("\n")
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

    print(f"Fetching live workflow {WORKFLOW_ID}...", file=sys.stderr)
    wf = fetch_live_workflow()
    PRE_BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRE_BACKUP_PATH.write_text(json.dumps(wf, indent=2), encoding="utf-8")
    print(f"  pre-patch backup -> {PRE_BACKUP_PATH}", file=sys.stderr)

    node = find_node(wf, TARGET_NODE)
    if not node:
        sys.exit(f"Target node {TARGET_NODE!r} not found in live workflow")

    old_code = node["parameters"]["jsCode"]
    new_code, already = patch_jscode(old_code)
    if already:
        print(f"NOTE: pilot welcome block already present in {TARGET_NODE!r}; nothing to do.", file=sys.stderr)
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
        return

    # Apply
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

    # Save post-patch backup for byte-diff verification
    post_wf = fetch_live_workflow()
    POST_BACKUP_PATH.write_text(json.dumps(post_wf, indent=2), encoding="utf-8")
    print(f"  post-patch backup -> {POST_BACKUP_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
