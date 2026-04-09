#!/usr/bin/env python3
"""Build + PUT the lean HVAC Call Processor workflow to Railway n8n.

Design: turn a Retell `call_analyzed` event into real-time lead notifications.
No Supabase writes (Retell is source of truth). Fan-out to:
  - Email (Brevo) → lead_email + optional notification_email_2/3
  - Slack (incoming webhook) → only if client opted in (slack_webhook_url set)
  - SMS stub → Telnyx when approved

On-brand Syntharra voice: professional, modern, no gimmicks.
"""
import json, os, sys, urllib.request, urllib.error

# ---- Credentials
def vault_key(service, key_type):
    # Session-local: read from env if injected, else hard-fail (vault MCP preferred for live)
    env = os.environ.get(f"{service.upper()}_{key_type.upper()}")
    if env: return env
    raise SystemExit(f"set env {service.upper()}_{key_type.upper()}")

N8N_BASE = "https://n8n.syntharra.com/api/v1"
WORKFLOW_ID = "Kg576YtPM9yEacKn"
# Credentials are injected at runtime. Never hardcode.
# Required env vars before running:
#   N8N_API_KEY              — syntharra_vault: 'n8n Railway' / api_key
#   SUPABASE_URL             — syntharra_vault: 'Supabase' / project_url (or hardcode your own)
#   SUPABASE_SERVICE_KEY     — syntharra_vault: 'Supabase' / service_role_key (baked into workflow HTTP nodes)
#   BREVO_API_KEY            — syntharra_vault: 'Brevo' / api_key (baked into workflow HTTP nodes)
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://hgheyqwnrcvwtgngqdnq.supabase.co")
BREVO_KEY = os.environ.get("BREVO_API_KEY", "")
if not SUPABASE_KEY or not BREVO_KEY:
    raise SystemExit(
        "Missing env vars. Fetch from syntharra_vault and export:\n"
        "  SUPABASE_SERVICE_KEY, BREVO_API_KEY, N8N_API_KEY\n"
        "See docstring for field mapping."
    )

# ---- Nodes

def node(name, node_type, params, position, type_version=1, node_id=None):
    import uuid
    return {
        "parameters": params,
        "id": node_id or str(uuid.uuid4()),
        "name": name,
        "type": node_type,
        "typeVersion": type_version,
        "position": position,
    }

# Node 1: Webhook (POST /retell-hvac-webhook) — path preserved from previous version
n_webhook = node(
    "Retell Webhook",
    "n8n-nodes-base.webhook",
    {"httpMethod": "POST", "path": "retell-hvac-webhook", "responseMode": "onReceived", "options": {}},
    [220, 400],
    type_version=1,
    node_id="62ff2087-3075-446f-b97d-43ccf97a2326",  # preserve so Retell webhook URL stays valid
)

# Node 2: IF — only act on call_analyzed + (is_lead OR urgency=emergency)
n_filter = node(
    "Filter: Lead or Emergency",
    "n8n-nodes-base.if",
    {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [
                {
                    "id": "c1",
                    "leftValue": "={{ $json.body.event }}",
                    "rightValue": "call_analyzed",
                    "operator": {"type": "string", "operation": "equals"}
                },
                {
                    "id": "c2",
                    "leftValue": "={{ !!$json.body.call?.call_analysis?.custom_analysis_data?.is_lead || $json.body.call?.call_analysis?.custom_analysis_data?.urgency === 'emergency' }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "true", "singleValue": True}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    [440, 400],
    type_version=2,
)

# Node 3: HTTP GET Supabase client lookup
n_lookup = node(
    "Lookup Client",
    "n8n-nodes-base.httpRequest",
    {
        "method": "GET",
        "url": f"={SUPABASE_URL}/rest/v1/hvac_standard_agent?agent_id=eq.{{{{ $('Retell Webhook').item.json.body.call.agent_id }}}}&select=company_name,owner_name,lead_phone,lead_email,notification_email_2,notification_email_3,slack_webhook_url,timezone,company_phone",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "apikey", "value": SUPABASE_KEY},
                {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
            ]
        },
        "options": {}
    },
    [660, 400],
    type_version=4.2,
)

# Node 4: Code — build branded notification payload
build_code = r"""// Build Syntharra-branded lead notification payload
const clients = $input.first().json;
const client = Array.isArray(clients) ? clients[0] : clients;
if (!client || !client.company_name) {
  throw new Error('Client not found for agent_id');
}

const call = $('Retell Webhook').item.json.body.call;
const analysis = call.call_analysis || {};
const custom = analysis.custom_analysis_data || {};

const callerName = (call.collected_dynamic_variables || {}).caller_name || 'Unknown caller';
const callerPhone = call.from_number || 'No number';
const summary = analysis.call_summary || 'No summary available.';
const urgency = (custom.urgency || 'normal').toLowerCase();
const isEmergency = urgency === 'emergency';
const transcript = call.transcript || '';
const callDuration = call.duration_ms ? Math.round(call.duration_ms / 1000) : 0;
const callTime = new Date(call.start_timestamp || Date.now()).toISOString();
const dashboardUrl = `https://syntharra.com/dashboard.html?a=${encodeURIComponent(call.agent_id)}`;
const callbackHref = `tel:${callerPhone.replace(/[^0-9+]/g, '')}`;

// Collect email recipients (dedupe + drop empty)
const emails = [client.lead_email, client.notification_email_2, client.notification_email_3]
  .filter(e => e && e.trim()).filter((v, i, a) => a.indexOf(v) === i);

// Urgency display
const urgencyBadge = isEmergency ? '🔥 EMERGENCY' : urgency === 'high' ? '⚡ HIGH' : '📞 LEAD';
const urgencyColor = isEmergency ? '#dc2626' : urgency === 'high' ? '#ea580c' : '#2563eb';

// --- Email HTML (Syntharra-branded — matches client-update form design system) ---
const emailSubject = isEmergency
  ? `🔥 EMERGENCY — ${callerName} (${callerPhone})`
  : `New Lead — ${callerName} (${callerPhone})`;

const _logoBars = `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse"><tr><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:13px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:19px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:26px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom"><div style="width:5px;height:33px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td></tr></table>`;

const emailHtml = `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F2F1FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:#0D0D1A">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F1FF;padding:40px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #E8E6FF;box-shadow:0 8px 40px rgba(108,99,255,.10),0 1px 3px rgba(0,0,0,.04)">
<tr><td style="height:4px;background:linear-gradient(90deg,#6C63FF,#8B7FFF,#A78BFA);font-size:0;line-height:0">&nbsp;</td></tr>
<tr><td style="padding:24px 40px;border-bottom:1px solid #E8E6FF;background:#ffffff">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="padding-right:11px;vertical-align:middle">${_logoBars}</td>
<td style="vertical-align:middle">
<div style="font-size:16px;font-weight:700;color:#0D0D1A;letter-spacing:-0.02em;line-height:1">Syntharra</div>
<div style="font-size:12px;color:#6B7280;margin-top:5px;line-height:1">Lead notification for ${client.company_name}</div>
</td></tr></table>
</td></tr>
<tr><td style="padding:32px 40px;background:#ffffff">
<div style="margin-bottom:20px"><span style="display:inline-block;background:${urgencyColor};color:#ffffff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">${urgencyBadge}</span></div>
<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 6px;letter-spacing:-0.02em">${callerName}</h1>
<div style="font-size:14px;color:#6B7280;margin-bottom:24px">${callerPhone} &middot; ${callDuration}s call</div>
<a href="${callbackHref}" style="display:inline-block;background:${urgencyColor};color:#ffffff;text-decoration:none;padding:13px 24px;border-radius:10px;font-weight:600;font-size:15px">Call back now</a>
<div style="margin-top:24px;padding:16px 18px;background:#F0EEFF;border-radius:10px;border-left:3px solid #6C63FF">
<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#6B7280;font-weight:600;margin-bottom:8px">Summary</div>
<div style="font-size:14px;line-height:1.6;color:#1A1A2E">${summary}</div>
</div>
<div style="margin-top:20px"><a href="${dashboardUrl}" style="color:#6C63FF;text-decoration:none;font-size:14px;font-weight:500">View transcript in your dashboard &rarr;</a></div>
</td></tr>
<tr><td style="padding:18px 40px;border-top:1px solid #E8E6FF;background:#ffffff">
<div style="font-size:12px;color:#6B7280;text-align:center;line-height:1.7">Syntharra AI Receptionist &nbsp;&middot;&nbsp; <a href="https://syntharra.com" style="color:#6C63FF;text-decoration:none">syntharra.com</a></div>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>`;

// --- Slack blocks (Syntharra-branded) ---
const slackBlocks = {
  text: `${urgencyBadge} New lead: ${callerName} (${callerPhone})`,
  blocks: [
    {
      type: "header",
      text: { type: "plain_text", text: `${urgencyBadge}  ${callerName}`, emoji: true }
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*Phone*\n<${callbackHref}|${callerPhone}>` },
        { type: "mrkdwn", text: `*Duration*\n${callDuration}s` },
      ]
    },
    {
      type: "section",
      text: { type: "mrkdwn", text: `*Summary*\n${summary}` }
    },
    {
      type: "actions",
      elements: [
        { type: "button", text: { type: "plain_text", text: "Call back now" }, url: callbackHref, style: isEmergency ? "danger" : "primary" },
        { type: "button", text: { type: "plain_text", text: "View in Syntharra" }, url: dashboardUrl }
      ]
    },
    { type: "context", elements: [{ type: "mrkdwn", text: `Syntharra AI Receptionist · ${client.company_name}` }] }
  ]
};

return [{
  json: {
    client_company: client.company_name,
    emails,
    slack_webhook_url: client.slack_webhook_url || null,
    email_subject: emailSubject,
    email_html: emailHtml,
    slack_payload: slackBlocks,
    is_emergency: isEmergency,
    urgency,
    caller_name: callerName,
    caller_phone: callerPhone,
    summary,
    // SMS stub (TELNYX-TODO): once Telnyx is approved, this payload is sent to SMS recipients
    sms_stub: {
      to: [client.lead_phone, client.notification_sms_2, client.notification_sms_3].filter(Boolean),
      body: `${urgencyBadge} ${callerName} ${callerPhone} — ${summary.slice(0, 120)}`
    }
  }
}];
"""
n_build = node(
    "Build Payload",
    "n8n-nodes-base.code",
    {"mode": "runOnceForAllItems", "jsCode": build_code},
    [880, 400],
    type_version=2,
)

# Node 5: Brevo send email (one per recipient array — handled via send multi in jsCode)
# Use Brevo transactional API directly
BREVO_API = "https://api.brevo.com/v3/smtp/email"
n_email = node(
    "Send Lead Email (Brevo)",
    "n8n-nodes-base.httpRequest",
    {
        "method": "POST",
        "url": BREVO_API,
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "accept", "value": "application/json"},
                {"name": "content-type", "value": "application/json"},
                {"name": "api-key", "value": BREVO_KEY}  # injected from BREVO_API_KEY env var (vault-sourced at runtime)
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": (
            "={{ { "
            "'sender': { 'name': 'Syntharra', 'email': 'leads@syntharra.com' }, "
            "'to': $json.emails.map(e => ({ 'email': e })), "
            "'subject': $json.email_subject, "
            "'htmlContent': $json.email_html "
            "} }}"
        ),
        "options": {}
    },
    [1100, 300],
    type_version=4.2,
)

# Node 6: IF slack_webhook_url set
n_slack_gate = node(
    "Has Slack?",
    "n8n-nodes-base.if",
    {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [
                {
                    "id": "s1",
                    "leftValue": "={{ !!$('Build Payload').item.json.slack_webhook_url }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "true", "singleValue": True}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    [1100, 500],
    type_version=2,
)

# Node 7: POST Slack incoming webhook
n_slack_post = node(
    "Post to Client Slack",
    "n8n-nodes-base.httpRequest",
    {
        "method": "POST",
        "url": "={{ $('Build Payload').item.json.slack_webhook_url }}",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ $('Build Payload').item.json.slack_payload }}",
        "options": {}
    },
    [1320, 500],
    type_version=4.2,
)

# Node 8: SMS stub — Code node that logs TELNYX-TODO, does nothing active yet
sms_stub_code = """// TELNYX-TODO: wire real SMS send once Telnyx AI evaluation is approved.
// Until then, this node is a no-op that passes through the stub payload so downstream
// observability can see what would have been sent.
const p = $('Build Payload').item.json;
console.log('[TELNYX-TODO] Would send SMS:', JSON.stringify(p.sms_stub));
return [{ json: { sms_pending: true, sms_stub: p.sms_stub } }];
"""
n_sms_stub = node(
    "SMS Stub (Telnyx TODO)",
    "n8n-nodes-base.code",
    {"mode": "runOnceForAllItems", "jsCode": sms_stub_code},
    [1100, 700],
    type_version=2,
)

nodes = [n_webhook, n_filter, n_lookup, n_build, n_email, n_slack_gate, n_slack_post, n_sms_stub]

# Connections
connections = {
    "Retell Webhook": {
        "main": [[{"node": "Filter: Lead or Emergency", "type": "main", "index": 0}]]
    },
    "Filter: Lead or Emergency": {
        "main": [
            [{"node": "Lookup Client", "type": "main", "index": 0}],  # true branch
            []  # false branch — drop silently
        ]
    },
    "Lookup Client": {
        "main": [[{"node": "Build Payload", "type": "main", "index": 0}]]
    },
    "Build Payload": {
        "main": [[
            {"node": "Send Lead Email (Brevo)", "type": "main", "index": 0},
            {"node": "Has Slack?", "type": "main", "index": 0},
            {"node": "SMS Stub (Telnyx TODO)", "type": "main", "index": 0},
        ]]
    },
    "Has Slack?": {
        "main": [
            [{"node": "Post to Client Slack", "type": "main", "index": 0}],  # true
            []  # false
        ]
    }
}

workflow_body = {
    "name": "HVAC Call Processor - Retell Webhook (lean fan-out)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"},
    "staticData": None,
}

# ---- PUT to Railway n8n
def main():
    key = vault_key("n8n", "api_key")
    H = {"X-N8N-API-KEY": key, "Accept": "application/json", "Content-Type": "application/json"}
    data = json.dumps(workflow_body).encode('utf-8')
    req = urllib.request.Request(f"{N8N_BASE}/workflows/{WORKFLOW_ID}", headers=H, data=data, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            r = json.loads(resp.read().decode())
            print(f"PUT /workflows/{WORKFLOW_ID} -> {resp.status}")
            print(f"  name: {r.get('name')}")
            print(f"  nodes: {len(r.get('nodes', []))}")
    except urllib.error.HTTPError as e:
        print(f"FAILED: {e.code}")
        print(e.read().decode()[:2000])
        sys.exit(1)

    # Activate
    req2 = urllib.request.Request(f"{N8N_BASE}/workflows/{WORKFLOW_ID}/activate", headers=H, method="POST")
    try:
        with urllib.request.urlopen(req2, timeout=30) as resp:
            print(f"activate -> {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"activate failed: {e.code} {e.read().decode()[:300]}")

if __name__ == "__main__":
    main()
