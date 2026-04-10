#!/usr/bin/env python3
"""
Inject Telnyx phone-purchase nodes into onboarding workflow 4Hx7aRdzMl5N0uJP.

Adds 5 nodes between "Write Client Data to Supabase" and "Publish Retell Agent":
  1. Code: Fetch Telnyx Creds      — reads api_key + retell_sip_connection_id from vault
  2. Telnyx: Search Available Numbers — GET /v2/available_phone_numbers by area code
  3. Telnyx: Order Phone Number       — POST /v2/number_orders (picks first result)
  4. Telnyx: Bind to Retell SIP       — PATCH /v2/phone_numbers/{id} with SIP connection
  5. Code: Extract Phone Result       — merges E.164 phone into downstream data

Pre-requisites (vault entries needed before the chain will execute):
  service_name='Telnyx', key_type='api_key'               — Telnyx API key (Bearer token)
  service_name='Telnyx', key_type='retell_sip_connection_id' — Retell SIP connection ID

Usage:
  python tools/build_telnyx_phone_nodes.py          # dry-run (validates only)
  python tools/build_telnyx_phone_nodes.py --deploy  # deploy to n8n
"""
import json, sys, urllib.request, urllib.error

# ── Credentials ───────────────────────────────────────────────────────────────
# n8n API key — read from syntharra_vault at session start
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZWNlYWE0YS02ODgzLTQzNDAtODQxMy0zMjQ2MGY3YTk5MGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNDJlNTI0NWEtZjgxZi00OTBkLWJhMTAtNzg5ZjZlZDcxM2ZmIiwiaWF0IjoxNzc1NzQ1MjA3fQ.yY6u-03iyRQAFLsOvvReAmCBkwseZ-giSgYgJkLK0B8"
WORKFLOW_ID = "4Hx7aRdzMl5N0uJP"

# Supabase — same URL/key used by all existing onboarding workflow nodes
SB_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SB_KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
          ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ"
          ".PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg")

# ── n8n REST helpers ──────────────────────────────────────────────────────────
def n8n_get(wf_id):
    req = urllib.request.Request(
        f"https://n8n.syntharra.com/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": N8N_KEY},
    )
    return json.loads(urllib.request.urlopen(req).read())

def n8n_put(wf_id, wf):
    # Rule 11: PUT payload: only name, nodes, connections, settings(executionOrder)
    body = json.dumps({
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": {"executionOrder": wf.get("settings", {}).get("executionOrder", "v1")},
    }).encode()
    req = urllib.request.Request(
        f"https://n8n.syntharra.com/api/v1/workflows/{wf_id}",
        data=body, method="PUT",
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

# ── Node code strings ─────────────────────────────────────────────────────────
# Pattern matches Send Setup Instructions Email / Send Welcome Email nodes:
# use this.helpers.httpRequest() for vault reads inside Code nodes.

FETCH_CREDS_CODE = (
    "// Fetch Telnyx credentials from syntharra_vault (same pattern as Send Welcome Email)\n"
    "const _sb = '" + SB_URL + "';\n"
    "const _sbk = '" + SB_KEY + "';\n"
    "\n"
    "const vaultRows = await this.helpers.httpRequest({\n"
    "  method: 'GET',\n"
    "  url: `${_sb}/rest/v1/syntharra_vault`\n"
    "       + '?service_name=eq.Telnyx&select=key_type,key_value',\n"
    "  headers: { apikey: _sbk, Authorization: `Bearer ${_sbk}` },\n"
    "  json: true,\n"
    "});\n"
    "\n"
    "const byType = Object.fromEntries(\n"
    "  (Array.isArray(vaultRows) ? vaultRows : []).map(r => [r.key_type, r.key_value])\n"
    ");\n"
    "const telnyxKey = byType['api_key'] || '';\n"
    "const sipConnectionId = byType['retell_sip_connection_id'] || '';\n"
    "\n"
    "// Graceful skip — vault entries not yet added. Workflow continues without phone purchase.\n"
    "if (!telnyxKey) {\n"
    "  return [{ json: {\n"
    "    _telnyx_skip: true,\n"
    "    _telnyx_reason: 'Telnyx vault entries missing — add api_key + retell_sip_connection_id to enable auto phone purchase',\n"
    "    telnyx_key: '',\n"
    "    sip_connection_id: '',\n"
    "    area_code: '888',\n"
    "    agent_phone_number: '',\n"
    "  }}];\n"
    "}\n"
    "\n"
    "// Derive area code from company_phone (NPA)\n"
    "const clientData = $('Write Client Data to Supabase').first().json;\n"
    "const digits = (clientData.company_phone || '').replace(/\\D/g, '');\n"
    "// Last 10 digits, first 3 = NPA; fallback 888\n"
    "const areaCode = digits.length >= 10 ? digits.slice(-10, -7) : '888';\n"
    "\n"
    "return [{\n"
    "  json: {\n"
    "    telnyx_key: telnyxKey,\n"
    "    sip_connection_id: sipConnectionId,\n"
    "    area_code: areaCode,\n"
    "    ...clientData,\n"
    "  }\n"
    "}];\n"
)

EXTRACT_CODE = (
    "// Extract E.164 phone from order response; merge with client data for downstream\n"
    "const orderResp = $('Telnyx: Order Phone Number').first().json;\n"
    "const phones = orderResp?.data?.phone_numbers || [];\n"
    "const phone   = phones[0]?.phone_number || '';  // e.g. +15125551234\n"
    "const phoneId = phones[0]?.id || '';\n"
    "\n"
    "const clientData = $('Write Client Data to Supabase').first().json;\n"
    "return [{\n"
    "  json: {\n"
    "    ...clientData,\n"
    "    agent_phone_number: phone,\n"
    "    telnyx_phone_id: phoneId,\n"
    "    _telnyx_provisioned: true,\n"
    "  }\n"
    "}];\n"
)

PASS_THROUGH_CODE = (
    "// Pass through agent data to downstream nodes.\n"
    "// Retell publish returns empty 200 so we read back from the Supabase write node.\n"
    "// Carry the Telnyx-provisioned phone number if available.\n"
    "const d = $('Write Client Data to Supabase').first().json;\n"
    "let agentPhone = '';\n"
    "try { agentPhone = $('Code: Extract Phone Result').first().json.agent_phone_number || ''; } catch(e) {}\n"
    "return { ...d, _published: true, agent_phone_number: agentPhone || d.agent_phone_number || '' };\n"
)

# ── New nodes ─────────────────────────────────────────────────────────────────
# Positioned at y=700 (below existing tracks).
# x-range 1846 → 3296 (5 nodes × ~350px).
# Existing nodes at x>=1996 will be shifted +1400 to make room.

TELNYX_NODES = [
    # 1. Fetch creds + prepare area code
    {
        "id": "telnyx-fetch-creds",
        "name": "Code: Fetch Telnyx Creds",
        "type": "n8n-nodes-base.code",
        "position": [1946, 700],
        "typeVersion": 2,
        "parameters": {
            "mode": "runOnceForAllItems",
            "language": "javaScript",
            "jsCode": FETCH_CREDS_CODE,
        },
    },
    # 2. Search available numbers in area code
    {
        "id": "telnyx-search",
        "name": "Telnyx: Search Available Numbers",
        "type": "n8n-nodes-base.httpRequest",
        "position": [2246, 700],
        "typeVersion": 4.2,
        "parameters": {
            "method": "GET",
            # Rule 30: expressions must start with =
            "url": ("={{ 'https://api.telnyx.com/v2/available_phone_numbers"
                    "?filter[country_code]=US"
                    "&filter[national_destination_code]=' + $input.first().json.area_code"
                    " + '&filter[features][]=voice&filter[features][]=sms&page[size]=5' }}"),
            "authentication": "none",
            # Rule 18: sendHeaders must be explicitly true
            "sendHeaders": True,
            "specifyHeaders": "keypair",
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization",
                     "value": "={{ 'Bearer ' + $input.first().json.telnyx_key }}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "options": {},
        },
    },
    # 3. Order the first available number
    {
        "id": "telnyx-order",
        "name": "Telnyx: Order Phone Number",
        "type": "n8n-nodes-base.httpRequest",
        "position": [2596, 700],
        "typeVersion": 4.2,
        "parameters": {
            "method": "POST",
            "url": "https://api.telnyx.com/v2/number_orders",
            "authentication": "none",
            "sendHeaders": True,
            "specifyHeaders": "keypair",
            "headerParameters": {
                "parameters": [
                    # Reach back to Fetch Creds node for the key (Rule 12 pattern)
                    {"name": "Authorization",
                     "value": "={{ 'Bearer ' + $('Code: Fetch Telnyx Creds').first().json.telnyx_key }}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "specifyBody": "string",
            # Pick first available number from search response
            "body": ("={{ '{\"phone_numbers\":[{\"phone_number\":\"'"
                     " + $input.first().json.data[0].phone_number + '\"}]}' }}"),
            "options": {},
        },
    },
    # 4. Bind the ordered number to Retell's SIP connection (Telnyx side)
    {
        "id": "telnyx-bind",
        "name": "Telnyx: Bind to Retell SIP",
        "type": "n8n-nodes-base.httpRequest",
        "position": [2946, 700],
        "typeVersion": 4.2,
        "parameters": {
            "method": "PATCH",
            # Phone number ID from the order response (data.phone_numbers[0].id)
            "url": ("={{ 'https://api.telnyx.com/v2/phone_numbers/'"
                    " + $input.first().json.data.phone_numbers[0].id }}"),
            "authentication": "none",
            "sendHeaders": True,
            "specifyHeaders": "keypair",
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization",
                     "value": "={{ 'Bearer ' + $('Code: Fetch Telnyx Creds').first().json.telnyx_key }}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "specifyBody": "string",
            # Set voice.connection_id to Retell's SIP connection (from vault)
            "body": ("={{ '{\"voice\":{\"connection_id\":\"'"
                     " + $('Code: Fetch Telnyx Creds').first().json.sip_connection_id"
                     " + '\"}}' }}"),
            "options": {},
        },
    },
    # 5. Extract phone number and merge with client data
    {
        "id": "telnyx-extract",
        "name": "Code: Extract Phone Result",
        "type": "n8n-nodes-base.code",
        "position": [3296, 700],
        "typeVersion": 2,
        "parameters": {
            "mode": "runOnceForAllItems",
            "language": "javaScript",
            "jsCode": EXTRACT_CODE,
        },
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────
def main(deploy: bool):
    wf = n8n_get(WORKFLOW_ID)
    print(f"Fetched: {wf['name']} — {len(wf['nodes'])} nodes")

    # 1. Shift all nodes at x >= 1996 rightward by +1400
    SHIFT_X = 1400
    SHIFT_THRESHOLD = 1996
    for n in wf["nodes"]:
        x, y = n.get("position", [0, 0])
        if x >= SHIFT_THRESHOLD:
            n["position"] = [x + SHIFT_X, y]
            print(f"  shifted {n['name']!r}  x:{x} -> {x + SHIFT_X}")

    # 2. Add Telnyx nodes
    wf["nodes"].extend(TELNYX_NODES)
    print(f"\nAdded {len(TELNYX_NODES)} Telnyx nodes — total now: {len(wf['nodes'])}")

    # 3. Rewire connections
    conns = wf["connections"]
    WCD = "Write Client Data to Supabase"

    # Remove: Write Client Data -> Publish Retell Agent
    if WCD in conns and conns[WCD].get("main"):
        before = len(conns[WCD]["main"][0])
        conns[WCD]["main"][0] = [
            d for d in conns[WCD]["main"][0] if d.get("node") != "Publish Retell Agent"
        ]
        after = len(conns[WCD]["main"][0])
        print(f"\nRemoved Write Client Data -> Publish Retell Agent  ({before} -> {after} outputs)")

    # Add: Write Client Data -> Code: Fetch Telnyx Creds
    if WCD not in conns:
        conns[WCD] = {"main": [[]]}
    conns[WCD].setdefault("main", [[]])[0].append(
        {"node": "Code: Fetch Telnyx Creds", "type": "main", "index": 0}
    )
    print("Added: Write Client Data -> Code: Fetch Telnyx Creds")

    # Chain the 5 Telnyx nodes
    chain = [
        ("Code: Fetch Telnyx Creds",          "Telnyx: Search Available Numbers"),
        ("Telnyx: Search Available Numbers",   "Telnyx: Order Phone Number"),
        ("Telnyx: Order Phone Number",         "Telnyx: Bind to Retell SIP"),
        ("Telnyx: Bind to Retell SIP",         "Code: Extract Phone Result"),
        ("Code: Extract Phone Result",         "Publish Retell Agent"),
    ]
    for src, dst in chain:
        conns.setdefault(src, {"main": [[]]})
        conns[src].setdefault("main", [[]])
        if not conns[src]["main"]:
            conns[src]["main"] = [[]]
        conns[src]["main"][0].append({"node": dst, "type": "main", "index": 0})
        print(f"Added: {src!r} -> {dst!r}")

    # 4. Update Pass Through Agent Data to carry phone
    for n in wf["nodes"]:
        if n["name"] == "Pass Through Agent Data":
            n["parameters"]["jsCode"] = PASS_THROUGH_CODE
            print("\nUpdated: Pass Through Agent Data — now carries agent_phone_number from Telnyx")
            break

    # 5. Validate: check no duplicate node names
    names = [n["name"] for n in wf["nodes"]]
    dupes = [n for n in set(names) if names.count(n) > 1]
    if dupes:
        print(f"\nERROR: Duplicate node names: {dupes}")
        sys.exit(1)

    print(f"\n=== DRY-RUN SUMMARY ===")
    print(f"  Total nodes: {len(wf['nodes'])}")
    print(f"  New Telnyx path:")
    telnyx_path = [
        "Write Client Data to Supabase",
        "Code: Fetch Telnyx Creds",
        "Telnyx: Search Available Numbers",
        "Telnyx: Order Phone Number",
        "Telnyx: Bind to Retell SIP",
        "Code: Extract Phone Result",
        "Publish Retell Agent",
    ]
    for i in range(len(telnyx_path) - 1):
        print(f"    {telnyx_path[i]!r} -> {telnyx_path[i+1]!r}")

    if not deploy:
        print("\nDRY RUN complete. Run with --deploy to push to n8n.")
        return

    print("\nDeploying...")
    result = n8n_put(WORKFLOW_ID, wf)
    print(f"PUT success: id={result.get('id')}, name={result.get('name')}, "
          f"nodes={len(result.get('nodes', []))}")


if __name__ == "__main__":
    deploy = "--deploy" in sys.argv
    main(deploy)
