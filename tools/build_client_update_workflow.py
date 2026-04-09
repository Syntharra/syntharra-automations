#!/usr/bin/env python3
"""
build_client_update_workflow.py — Create (or replace) the n8n client-update form workflow.

Run once to create. Re-run to replace (uses fixed workflow ID if env var N8N_CLIENT_UPDATE_ID set,
otherwise creates new and prints the ID for REFERENCE.md).

Required env vars:
  N8N_API_KEY            — from syntharra_vault
  SUPABASE_SERVICE_KEY   — from syntharra_vault
  SUPABASE_URL           — https://hgheyqwnrcvwtgngqdnq.supabase.co
  RETELL_API_KEY         — from syntharra_vault

Optional:
  N8N_CLIENT_UPDATE_ID   — if set, PUT (update) that workflow ID instead of POST (create new)
"""
import json, os, sys, uuid, urllib.request, urllib.error

N8N_BASE = "https://n8n.syntharra.com/api/v1"
ONBOARDING_WF_ID = "4Hx7aRdzMl5N0uJP"  # source of Build Retell Prompt JS

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://hgheyqwnrcvwtgngqdnq.supabase.co").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
RETELL_KEY   = os.environ.get("RETELL_API_KEY", "")
N8N_KEY      = os.environ.get("N8N_API_KEY", "")

for name, val in [("N8N_API_KEY", N8N_KEY), ("SUPABASE_SERVICE_KEY", SUPABASE_KEY), ("RETELL_API_KEY", RETELL_KEY)]:
    if not val:
        sys.exit(f"Missing env var: {name}")


def n8n_get(path: str) -> dict:
    req = urllib.request.Request(f"{N8N_BASE}{path}", headers={"X-N8N-API-KEY": N8N_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def n8n_post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{N8N_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def n8n_put(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{N8N_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_build_retell_prompt_js() -> str:
    """Copy Build Retell Prompt JS from the live onboarding workflow."""
    wf = n8n_get(f"/workflows/{ONBOARDING_WF_ID}")
    for node in wf.get("nodes", []):
        if node.get("name") == "Build Retell Prompt":
            js = node.get("parameters", {}).get("jsCode", "")
            if js:
                print(f"  Fetched Build Retell Prompt JS ({len(js):,} chars)")
                return js
    sys.exit("Could not find 'Build Retell Prompt' node in onboarding workflow")


def nid() -> str:
    return str(uuid.uuid4())


EDITABLE_FIELDS = [
    "company_name", "company_tagline", "owner_name", "website", "years_in_business",
    "certifications", "licensed_insured", "services_offered", "brands_serviced",
    "service_area", "service_area_radius", "do_not_service", "business_hours",
    "response_time", "after_hours_behavior", "after_hours_transfer", "emergency_service",
    "emergency_phone", "pricing_policy", "diagnostic_fee", "standard_fees",
    "free_estimates", "financing_available", "financing_details", "warranty",
    "warranty_details", "maintenance_plans", "membership_program", "payment_methods",
    "lead_contact_method", "lead_phone", "lead_email", "transfer_phone",
    "transfer_triggers", "transfer_behavior", "current_promotion", "seasonal_services",
    "unique_selling_points", "google_review_rating", "google_review_count",
    "company_phone", "custom_greeting", "additional_info",
]


def build_workflow(build_retell_js: str) -> dict:
    # ---- Node IDs (fixed so workflow is re-runnable without creating duplicate URLs)
    ID_FORM     = "form-trigger-client-update-v1"
    ID_FETCH    = "sb-fetch-row-v1"
    ID_APPLY    = "apply-field-update-v1"
    ID_COMPILE  = "build-retell-prompt-v1"
    ID_BRANCH   = "preview-branch-v1"
    ID_PATCH    = "retell-patch-flow-v1"
    ID_PUBLISH  = "retell-publish-v1"
    ID_UPDATE   = "sb-update-row-v1"
    ID_RESPOND  = "form-respond-v1"
    ID_RESPOND_PREVIEW = "form-respond-preview-v1"

    field_options = [{"option": f} for f in EDITABLE_FIELDS]

    nodes = [
        # 1 — Form Trigger
        {
            "id": ID_FORM,
            "name": "Client Update Form",
            "type": "n8n-nodes-base.formTrigger",
            "typeVersion": 2,
            "position": [240, 400],
            "parameters": {
                "formTitle": "Update Client Agent",
                "formDescription": "Update HVAC Standard agent settings. Changes are applied live immediately (unless Preview mode selected).",
                "path": "client-update",
                "responseMode": "lastNode",
                "formFields": {
                    "values": [
                        {
                            "fieldLabel": "Agent ID",
                            "fieldType": "text",
                            "placeholder": "agent_xxxxxxxxxxxxxxxxxxxxxxxx",
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "Field to Update",
                            "fieldType": "dropdown",
                            "fieldOptions": {"values": field_options},
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "New Value",
                            "fieldType": "textarea",
                            "placeholder": "Enter the new value",
                            "requiredField": True,
                        },
                        {
                            "fieldLabel": "Mode",
                            "fieldType": "dropdown",
                            "fieldOptions": {"values": [
                                {"option": "Apply — write changes live"},
                                {"option": "Preview — show diff only, no writes"},
                            ]},
                            "requiredField": True,
                        },
                    ]
                },
            },
        },

        # 2 — Supabase: fetch current row
        {
            "id": ID_FETCH,
            "name": "Supabase: Fetch Agent Row",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [460, 400],
            "parameters": {
                "method": "GET",
                "url": f"={SUPABASE_URL}/rest/v1/hvac_standard_agent",
                "sendQuery": True,
                "queryParameters": {"parameters": [
                    {"name": "agent_id", "value": "=eq.{{ $json['Agent ID'] }}"},
                    {"name": "select", "value": "*"},
                ]},
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                ]},
                "options": {},
            },
        },

        # 3 — Code: apply the field update in memory
        {
            "id": ID_APPLY,
            "name": "Apply Field Update",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 400],
            "parameters": {
                "jsCode": """
const formData = $('Client Update Form').first().json;
const rows = $input.first().json;
const rowArray = Array.isArray(rows) ? rows : [rows];
if (!rowArray.length) throw new Error('No hvac_standard_agent row found for agent_id: ' + formData['Agent ID']);
const row = rowArray[0];
const field = formData['Field to Update'];
const newValue = formData['New Value'];
const mode = formData['Mode'] || '';
const isDryRun = mode.startsWith('Preview');
const oldValue = row[field];
const updatedRow = { ...row, [field]: newValue };
return [{ json: { row: updatedRow, field, newValue, oldValue, agentId: row.agent_id, flowId: row.conversation_flow_id, isDryRun } }];
""".strip(),
            },
        },

        # 4 — Code: Build Retell Prompt (full JS copy from onboarding workflow)
        {
            "id": ID_COMPILE,
            "name": "Build Retell Prompt",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 400],
            "parameters": {
                "jsCode": build_retell_js,
            },
        },

        # 5 — IF: branch on isDryRun (Preview vs Apply)
        # true output (index 0) → Preview respond (no writes)
        # false output (index 1) → PATCH flow
        {
            "id": ID_BRANCH,
            "name": "Preview or Apply?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [1120, 400],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "preview-check",
                            "leftValue": "={{ $('Apply Field Update').first().json.isDryRun }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true"},
                        }
                    ],
                    "combinator": "and",
                },
            },
        },

        # 6a — Respond: Preview (no writes, shows old/new diff)
        {
            "id": ID_RESPOND_PREVIEW,
            "name": "Respond: Preview",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1340, 240],
            "parameters": {
                "respondWith": "text",
                "responseBody": "={{ 'PREVIEW ONLY — No changes made.\\nField: ' + $(\\'Apply Field Update\\').first().json.field + '\\nOld: ' + $(\\'Apply Field Update\\').first().json.oldValue + '\\nNew: ' + $(\\'Apply Field Update\\').first().json.newValue }}",
            },
        },

        # 6b — HTTP: PATCH Retell conversation flow (Apply path only)
        {
            "id": ID_PATCH,
            "name": "Retell: PATCH Flow",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1340, 560],
            "parameters": {
                "method": "PATCH",
                "url": "={{ 'https://api.retellai.com/update-conversation-flow/' + $('Apply Field Update').first().json.flowId }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {RETELL_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify($json.conversationFlow) }}",
                "options": {"response": {"response": {"responseFormat": "json"}}},
            },
        },

        # 7 — HTTP: Publish agent
        {
            "id": ID_PUBLISH,
            "name": "Retell: Publish Agent",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1560, 560],
            "parameters": {
                "method": "POST",
                "url": "={{ 'https://api.retellai.com/publish-agent/' + $('Apply Field Update').first().json.agentId }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {RETELL_KEY}"},
                ]},
                "options": {"response": {"response": {"responseFormat": "text"}}},
            },
        },

        # 8 — HTTP: Update Supabase row
        {
            "id": ID_UPDATE,
            "name": "Supabase: Update Row",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [1780, 560],
            "parameters": {
                "method": "PATCH",
                "url": f"={SUPABASE_URL}/rest/v1/hvac_standard_agent",
                "sendQuery": True,
                "queryParameters": {"parameters": [
                    {"name": "agent_id", "value": "={{ 'eq.' + $('Apply Field Update').first().json.agentId }}"},
                ]},
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"},
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ [$('Apply Field Update').first().json.field]: $('Apply Field Update').first().json.newValue }) }}",
                "options": {},
            },
        },

        # 9 — Form response (Apply path)
        {
            "id": ID_RESPOND,
            "name": "Respond to Form",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [2000, 560],
            "parameters": {
                "respondWith": "text",
                "responseBody": "={{ 'Done. Updated ' + $(\\'Apply Field Update\\').first().json.field + ' on ' + $(\\'Apply Field Update\\').first().json.agentId }}",
            },
        },
    ]

    # Connections:
    # Form → Fetch → Apply → Compile → Branch
    #   Branch true (index 0) → Respond: Preview
    #   Branch false (index 1) → PATCH → Publish → Update → Respond to Form
    connections = {
        "Client Update Form":        {"main": [[{"node": "Supabase: Fetch Agent Row",  "type": "main", "index": 0}]]},
        "Supabase: Fetch Agent Row":  {"main": [[{"node": "Apply Field Update",         "type": "main", "index": 0}]]},
        "Apply Field Update":         {"main": [[{"node": "Build Retell Prompt",        "type": "main", "index": 0}]]},
        "Build Retell Prompt":        {"main": [[{"node": "Preview or Apply?",          "type": "main", "index": 0}]]},
        "Preview or Apply?": {
            "main": [
                [{"node": "Respond: Preview",        "type": "main", "index": 0}],  # true → preview
                [{"node": "Retell: PATCH Flow",      "type": "main", "index": 0}],  # false → apply
            ]
        },
        "Retell: PATCH Flow":         {"main": [[{"node": "Retell: Publish Agent",     "type": "main", "index": 0}]]},
        "Retell: Publish Agent":      {"main": [[{"node": "Supabase: Update Row",      "type": "main", "index": 0}]]},
        "Supabase: Update Row":       {"main": [[{"node": "Respond to Form",           "type": "main", "index": 0}]]},
    }

    return {
        "name": "Client Agent Update Form",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


def main() -> None:
    print("Fetching Build Retell Prompt JS from onboarding workflow...")
    build_js = fetch_build_retell_prompt_js()

    print("Building workflow JSON...")
    wf = build_workflow(build_js)

    existing_id = os.environ.get("N8N_CLIENT_UPDATE_ID")
    if existing_id:
        print(f"Updating existing workflow {existing_id}...")
        payload = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
        result = n8n_put(f"/workflows/{existing_id}", payload)
        wf_id = result["id"]
        print(f"Updated: {wf_id}")
    else:
        print("Creating new workflow...")
        result = n8n_post("/workflows", wf)
        wf_id = result["id"]
        print(f"Created: {wf_id}")
        print(f"\nAdd to REFERENCE.md:")
        print(f"  Client Update Form: `{wf_id}` — https://n8n.syntharra.com/form/client-update")

    # Activate
    try:
        req = urllib.request.Request(
            f"{N8N_BASE}/workflows/{wf_id}/activate",
            headers={"X-N8N-API-KEY": N8N_KEY},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
            print(f"Active: {d.get('active')}")
    except Exception as e:
        print(f"[WARN] activate failed (may already be active): {e}")

    print(f"\nForm URL: https://n8n.syntharra.com/form/client-update")


if __name__ == "__main__":
    main()
