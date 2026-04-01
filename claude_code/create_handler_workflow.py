import json, subprocess, os

SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
SMTP2GO_KEY = os.environ.get('SMTP2GO_KEY', '')
N8N_KEY = os.environ.get('N8N_KEY', '')

LOGO_JS = 'const ICON_URL = "https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png";\nconst LOGO = \'<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="\' + ICON_URL + \'" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td><div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;color:#0f0f1a">Syntharra</div></td></tr><tr><td><div style="font-family:Inter,sans-serif;font-size:7.5px;font-weight:600;color:#6C63FF;text-transform:uppercase;letter-spacing:1.2px">GLOBAL AI SOLUTIONS</div></td></tr></table></td></tr></table>\';'

fetch_code = f"""const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const body = $input.first().json.body;
const agent_id = body.agent_id;
const integration_type = body.integration_type;
const platform = body.platform;
const res = await fetch(
  SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + agent_id + '&select=agent_id,company_name,client_email,owner_name,scheduling_platform,integration_type,integration_status',
  {{ headers: {{ apikey: SUPABASE_KEY, Authorization: 'Bearer ' + SUPABASE_KEY }} }}
);
const rows = await res.json();
const client = rows[0] || {{}};
const fullName = client.owner_name || 'there';
const firstName = fullName.split(' ')[0];
return [{{ json: {{
  agent_id, integration_type, platform,
  company_name: client.company_name || '',
  owner_name: client.owner_name || '',
  owner_first_name: firstName,
  client_email: client.client_email || '',
  scheduling_platform: client.scheduling_platform || platform,
  integration_status: client.integration_status || 'unknown'
}} }}];"""

insert_code = f"""const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const d = $input.first().json;
await fetch(SUPABASE_URL + '/rest/v1/syntharra_activation_queue', {{
  method: 'POST',
  headers: {{
    apikey: SUPABASE_KEY,
    Authorization: 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json',
    Prefer: 'return=representation'
  }},
  body: JSON.stringify({{
    agent_id: d.agent_id, company_name: d.company_name,
    owner_name: d.owner_name, owner_email: d.client_email,
    scheduling_platform: d.scheduling_platform,
    integration_type: d.integration_type,
    integration_status: 'connected'
  }})
}});
return [{{ json: d }}];"""

internal_alert_code = f"""const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const d = $input.first().json;
const now = new Date().toLocaleString('en-US', {{ dateStyle: 'long', timeStyle: 'short' }});
{LOGO_JS}
const html = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden"><div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div><div style="padding:32px 36px">' + LOGO + '<h2 style="color:#1A1A2E;margin:24px 0 16px">New Premium Client Connected</h2><table style="width:100%;color:#1A1A2E;font-size:14px;line-height:2.2"><tr><td><strong>Company:</strong></td><td>' + d.company_name + '</td></tr><tr><td><strong>Owner:</strong></td><td>' + d.owner_name + '</td></tr><tr><td><strong>Platform:</strong></td><td>' + d.scheduling_platform + '</td></tr><tr><td><strong>Integration:</strong></td><td>' + d.integration_type + '</td></tr><tr><td><strong>Agent ID:</strong></td><td>' + d.agent_id + '</td></tr><tr><td><strong>Connected at:</strong></td><td>' + now + '</td></tr></table><h3 style="color:#1A1A2E;margin:24px 0 8px">Next steps:</h3><ol style="color:#6B7280;font-size:14px;line-height:1.8"><li>Check activation queue in admin dashboard</li><li>Run a test booking on the demo line</li><li>Once happy, activate</li></ol><div style="text-align:center;margin:24px 0"><a href="https://admin.syntharra.com" style="display:inline-block;background:#6C63FF;color:#ffffff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px">View Activation Queue</a></div></div></div></div>';
await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: ['onboarding@syntharra.com'],
    subject: 'Premium Client Ready - ' + d.company_name,
    html_body: html
  }})
}});
return [{{ json: d }}];"""

client_email_code = f"""const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const d = $input.first().json;
{LOGO_JS}
const html = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden"><div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div><div style="padding:32px 36px">' + LOGO + '<h2 style="color:#1A1A2E;margin:24px 0 16px">Hi ' + d.owner_first_name + ',</h2><p style="color:#6B7280;font-size:15px;line-height:1.6">Your ' + d.scheduling_platform + ' account is now connected to your Syntharra AI Receptionist.</p><p style="color:#6B7280;font-size:15px;line-height:1.6">We are running a final check to make sure everything is working perfectly. You will receive your live confirmation within a few hours.</p><p style="color:#6B7280;font-size:15px;line-height:1.6">Questions? Contact us at <a href="mailto:support@syntharra.com" style="color:#6C63FF">support@syntharra.com</a></p><p style="color:#1A1A2E;font-weight:600;margin-top:24px">The Syntharra Team</p></div></div></div>';
await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: [d.client_email],
    subject: d.scheduling_platform + ' Connected - Almost Live!',
    html_body: html
  }})
}});
return [{{ json: {{ ...d, emails_sent: true }} }}];"""

unexpected_code = f"""const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const d = $input.first().json;
const now = new Date().toLocaleString('en-US', {{ dateStyle: 'long', timeStyle: 'short' }});
const html = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;padding:32px 36px"><h2 style="color:#EF4444">Unexpected Integration Webhook</h2><p><strong>Agent ID:</strong> ' + d.agent_id + '</p><p><strong>Company:</strong> ' + d.company_name + '</p><p><strong>Received Status:</strong> ' + d.integration_status + '</p><p><strong>Timestamp:</strong> ' + now + '</p></div></div>';
await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: ['alerts@syntharra.com'],
    subject: 'Unexpected integration webhook - ' + d.company_name,
    html_body: html
  }})
}});
return [{{ json: d }}];"""

wf = {
  "name": "Premium \u2014 Integration Connected Handler",
  "nodes": [
    {"parameters": {"path": "integration-connected", "httpMethod": "POST", "responseMode": "onReceived", "options": {}}, "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [240, 300], "id": "wh1", "name": "Integration Connected Webhook", "webhookId": "integration-connected"},
    {"parameters": {"jsCode": fetch_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [500, 300], "id": "fc1", "name": "Fetch Client + Extract Name"},
    {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "rightValue": ""}, "conditions": [{"id": "1", "leftValue": "={{ $json.integration_status }}", "rightValue": "connected", "operator": {"type": "string", "operation": "equals"}}], "combinator": "and"}}, "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [760, 300], "id": "if1", "name": "Is Connected?"},
    {"parameters": {"jsCode": insert_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1020, 200], "id": "aq1", "name": "Insert Activation Queue"},
    {"parameters": {"jsCode": internal_alert_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1280, 200], "id": "ea1", "name": "Send Internal Alert"},
    {"parameters": {"jsCode": client_email_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1540, 200], "id": "ce1", "name": "Send Client Holding Email"},
    {"parameters": {"jsCode": unexpected_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1020, 500], "id": "ua1", "name": "Alert Unexpected Status"}
  ],
  "connections": {
    "Integration Connected Webhook": {"main": [[{"node": "Fetch Client + Extract Name", "type": "main", "index": 0}]]},
    "Fetch Client + Extract Name": {"main": [[{"node": "Is Connected?", "type": "main", "index": 0}]]},
    "Is Connected?": {"main": [[{"node": "Insert Activation Queue", "type": "main", "index": 0}], [{"node": "Alert Unexpected Status", "type": "main", "index": 0}]]},
    "Insert Activation Queue": {"main": [[{"node": "Send Internal Alert", "type": "main", "index": 0}]]},
    "Send Internal Alert": {"main": [[{"node": "Send Client Holding Email", "type": "main", "index": 0}]]}
  },
  "settings": {"executionOrder": "v1"}
}

with open('/tmp/n8n_wf.json', 'w') as f:
    json.dump(wf, f)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://n8n.syntharra.com/api/v1/workflows',
    '-H', f'X-N8N-API-KEY: {N8N_KEY}',
    '-H', 'Content-Type: application/json',
    '-d', '@/tmp/n8n_wf.json'
], capture_output=True, text=True, timeout=30)

resp = json.loads(result.stdout)
print(f"Workflow ID: {resp.get('id', 'ERROR')}")
print(f"Name: {resp.get('name', '')}")
if 'message' in resp:
    print(f"Error: {resp['message']}")
