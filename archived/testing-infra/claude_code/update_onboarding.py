import json, subprocess, os

N8N_KEY = os.environ.get('N8N_KEY', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
SMTP2GO_KEY = os.environ.get('SMTP2GO_KEY', '')

# Load existing workflow
with open('C:/Users/danie/OneDrive/Desktop/Syntharra/claude_code/onboarding_wf.json') as f:
    wf = json.load(f)

# NODE A — Map integration type + parse booking fields
node_a_code = f"""// NODE A — Map Integration Type + Parse Booking Fields
const webhookData = $('JotForm Premium Webhook Trigger').item.json.body;
const formData = (webhookData && webhookData.body) ? webhookData.body : webhookData;
const prevData = $input.first().json;

// Get scheduling platform from Jotform
const scheduling_platform = String(formData.q85_schedulingPlatform || formData['q85_scheduling_platform'] || formData.q85_schedulingplatform || '').trim();

// Map to integration type
let integration_type = 'manual';
const p = scheduling_platform;
if (p.includes('Google')) integration_type = 'google';
else if (p.includes('Outlook') || p.includes('Microsoft')) integration_type = 'outlook';
else if (p.includes('Jobber')) integration_type = 'jobber';
else if (p.includes('Calendly')) integration_type = 'calendly';
else if (p.includes('Acuity')) integration_type = 'acuity';
else if (p.includes('HubSpot')) integration_type = 'hubspot';
else if (p.includes('Apple') || p.includes("don't")) integration_type = 'google';

// Parse booking fields
const slot_duration_raw = String(formData.q87_slotDuration || formData['q87_slot_duration'] || '60').trim();
const slot_duration_minutes = parseInt(slot_duration_raw) || 60;

const buffer_time_raw = String(formData.q90_bufferTime || formData['q90_buffer_time'] || '30').trim();
const buffer_time_minutes = parseInt(buffer_time_raw) || 30;

const min_notice_raw = String(formData.q88_minNotice || formData['q88_min_notice'] || '2 hours').trim();
const min_notice_map = {{
  '1 hour': 1, '2 hours': 2, '4 hours': 4,
  'Same day OK': 0, '1 day': 24, '2 days': 48
}};
const min_notice_hours = min_notice_map[min_notice_raw] || 2;

const booking_hours = String(formData.q89_bookingHours || formData['q89_booking_hours'] || '').trim();

let bookable_job_types_raw = formData.q86_bookableJobTypes || formData['q86_bookable_job_types'] || [];
if (!Array.isArray(bookable_job_types_raw)) bookable_job_types_raw = [bookable_job_types_raw];
const bookable_job_types = bookable_job_types_raw.filter(Boolean);

const confirmation_method = String(formData.q91_confirmationMethod || formData['q91_confirmation_method'] || 'Both Email & SMS').trim();
const cal_agreement = String(formData.q92_calAgreement || formData['q92_cal_agreement'] || '').trim();

return [{{ json: {{
  ...prevData,
  scheduling_platform,
  integration_type,
  slot_duration_minutes,
  buffer_time_minutes,
  min_notice_hours,
  booking_hours,
  bookable_job_types,
  booking_confirmation_method: confirmation_method,
  cal_agreement
}} }}];"""

# NODE B — Update Supabase with booking fields
node_b_code = f"""// NODE B — Update Supabase with booking fields
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const d = $input.first().json;

const updateBody = {{
  scheduling_platform: d.scheduling_platform,
  integration_type: d.integration_type,
  slot_duration_minutes: d.slot_duration_minutes,
  buffer_time_minutes: d.buffer_time_minutes,
  min_notice_hours: d.min_notice_hours,
  booking_hours: d.booking_hours,
  bookable_job_types: JSON.stringify(d.bookable_job_types),
  booking_confirmation_method: d.booking_confirmation_method,
  cal_agreement: d.cal_agreement,
  agent_status: 'pending_integration'
}};

await fetch(
  SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + d.agent_id,
  {{
    method: 'PATCH',
    headers: {{
      apikey: SUPABASE_KEY,
      Authorization: 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      Prefer: 'return=representation'
    }},
    body: JSON.stringify(updateBody)
  }}
);

return [{{ json: d }}];"""

# NODE D — Google OAuth Email
node_d_code = f"""// NODE D — Send Google Calendar OAuth Email
const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const OAUTH_URL = 'https://syntharra-oauth-server-production.up.railway.app';
const d = $input.first().json;
const firstName = (d.owner_name || 'there').split(' ')[0];

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = '<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="' + ICON_URL + '" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td><div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;color:#0f0f1a">Syntharra</div></td></tr><tr><td><div style="font-family:Inter,sans-serif;font-size:7.5px;font-weight:600;color:#6C63FF;text-transform:uppercase;letter-spacing:1.2px">GLOBAL AI SOLUTIONS</div></td></tr></table></td></tr></table>';

const connectUrl = OAUTH_URL + '/auth/google?agent_id=' + d.agent_id;
const html = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden"><div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div><div style="padding:32px 36px">' + LOGO + '<h2 style="color:#1A1A2E;margin:24px 0 16px">Hi ' + firstName + ',</h2><p style="color:#6B7280;font-size:15px;line-height:1.6">Your AI receptionist is built and ready. The last step is connecting your Google Calendar so your AI knows when you are available and can book jobs automatically.</p><div style="text-align:center;margin:24px 0"><a href="' + connectUrl + '" style="display:inline-block;background:#6C63FF;color:#ffffff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px">Connect Google Calendar &rarr;</a></div><p style="color:#6B7280;font-size:14px;line-height:1.6"><strong>What happens when you connect:</strong></p><ul style="color:#6B7280;font-size:14px;line-height:1.8"><li>Your AI checks your real availability before offering any slots</li><li>Bookings appear directly in your Google Calendar</li><li>Customers get instant confirmation &mdash; no back and forth</li></ul><p style="color:#6B7280;font-size:14px">This takes under 2 minutes.</p><p style="color:#6B7280;font-size:14px;margin-top:16px">Questions? <a href="mailto:support@syntharra.com" style="color:#6C63FF">support@syntharra.com</a></p></div></div></div>';

await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: [d.client_email],
    subject: 'Connect Google Calendar - One Last Step',
    html_body: html
  }})
}});

// Update agent_status to oauth_sent
await fetch(
  SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + d.agent_id,
  {{
    method: 'PATCH',
    headers: {{
      apikey: SUPABASE_KEY,
      Authorization: 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{ agent_status: 'oauth_sent' }})
  }}
);

return [{{ json: {{ ...d, oauth_email_sent: 'google' }} }}];"""

# NODE E — Outlook OAuth Email
node_e_code = f"""// NODE E — Send Outlook OAuth Email
const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const OAUTH_URL = 'https://syntharra-oauth-server-production.up.railway.app';
const d = $input.first().json;
const firstName = (d.owner_name || 'there').split(' ')[0];

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = '<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="' + ICON_URL + '" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td><div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;color:#0f0f1a">Syntharra</div></td></tr><tr><td><div style="font-family:Inter,sans-serif;font-size:7.5px;font-weight:600;color:#6C63FF;text-transform:uppercase;letter-spacing:1.2px">GLOBAL AI SOLUTIONS</div></td></tr></table></td></tr></table>';

const connectUrl = OAUTH_URL + '/auth/outlook?agent_id=' + d.agent_id;
const html = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden"><div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div><div style="padding:32px 36px">' + LOGO + '<h2 style="color:#1A1A2E;margin:24px 0 16px">Hi ' + firstName + ',</h2><p style="color:#6B7280;font-size:15px;line-height:1.6">Your AI receptionist is built and ready. The last step is connecting your Outlook Calendar so your AI knows when you are available and can book jobs automatically.</p><div style="text-align:center;margin:24px 0"><a href="' + connectUrl + '" style="display:inline-block;background:#6C63FF;color:#ffffff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px">Connect Outlook Calendar &rarr;</a></div><p style="color:#6B7280;font-size:14px;line-height:1.6"><strong>What happens when you connect:</strong></p><ul style="color:#6B7280;font-size:14px;line-height:1.8"><li>Your AI checks your real availability before offering any slots</li><li>Bookings appear directly in your Outlook Calendar</li><li>Customers get instant confirmation &mdash; no back and forth</li></ul><p style="color:#6B7280;font-size:14px">This takes under 2 minutes.</p><p style="color:#6B7280;font-size:14px;margin-top:16px">Questions? <a href="mailto:support@syntharra.com" style="color:#6C63FF">support@syntharra.com</a></p></div></div></div>';

await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: [d.client_email],
    subject: 'Connect Outlook Calendar - One Last Step',
    html_body: html
  }})
}});

await fetch(
  SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + d.agent_id,
  {{
    method: 'PATCH',
    headers: {{
      apikey: SUPABASE_KEY,
      Authorization: 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{ agent_status: 'oauth_sent' }})
  }}
);

return [{{ json: {{ ...d, oauth_email_sent: 'outlook' }} }}];"""

# NODE F — Placeholder email for manual/other integrations
node_f_code = f"""// NODE F — Placeholder Email + Internal Note
const SMTP2GO_KEY = '{SMTP2GO_KEY}';
const d = $input.first().json;
const firstName = (d.owner_name || 'there').split(' ')[0];

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = '<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="' + ICON_URL + '" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td><div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;color:#0f0f1a">Syntharra</div></td></tr><tr><td><div style="font-family:Inter,sans-serif;font-size:7.5px;font-weight:600;color:#6C63FF;text-transform:uppercase;letter-spacing:1.2px">GLOBAL AI SOLUTIONS</div></td></tr></table></td></tr></table>';

const clientHtml = '<div style="background:#F7F7FB;padding:40px 0"><div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden"><div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div><div style="padding:32px 36px">' + LOGO + '<h2 style="color:#1A1A2E;margin:24px 0 16px">Hi ' + firstName + ',</h2><p style="color:#6B7280;font-size:15px;line-height:1.6">Your AI receptionist is being set up. Our team will contact you within 1 business day to complete your ' + d.scheduling_platform + ' integration.</p><p style="color:#6B7280;font-size:15px;line-height:1.6">Questions? <a href="mailto:support@syntharra.com" style="color:#6C63FF">support@syntharra.com</a></p></div></div></div>';

// Send client email
await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: [d.client_email],
    subject: 'Your AI Is Being Configured - We Will Be In Touch',
    html_body: clientHtml
  }})
}});

// Send internal note
await fetch('https://api.smtp2go.com/v3/email/send', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json', 'api-key': SMTP2GO_KEY }},
  body: JSON.stringify({{
    sender: 'noreply@syntharra.com',
    to: ['onboarding@syntharra.com'],
    subject: 'Manual setup needed - ' + d.company_name + ' / ' + d.scheduling_platform,
    html_body: '<p>Manual integration setup required.</p><p>Company: ' + d.company_name + '</p><p>Platform: ' + d.scheduling_platform + '</p><p>Agent ID: ' + d.agent_id + '</p>'
  }})
}});

return [{{ json: {{ ...d, placeholder_email_sent: true }} }}];"""

# Add new nodes to existing workflow
new_nodes = [
    {
        "parameters": {"jsCode": node_a_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2400, 512],
        "id": "na1",
        "name": "Map Integration Type"
    },
    {
        "parameters": {"jsCode": node_b_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2720, 512],
        "id": "nb1",
        "name": "Update Booking Fields"
    },
    {
        "parameters": {
            "rules": {
                "values": [
                    {"conditions": {"conditions": [{"leftValue": "={{ $json.integration_type }}", "rightValue": "google", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "google"},
                    {"conditions": {"conditions": [{"leftValue": "={{ $json.integration_type }}", "rightValue": "outlook", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "outlook"},
                    {"conditions": {"conditions": [{"leftValue": "={{ $json.integration_type }}", "rightValue": "google", "operator": {"type": "string", "operation": "notEquals"}}]}, "renameOutput": True, "outputKey": "other"}
                ]
            },
            "options": {"fallbackOutput": "extra"}
        },
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.2,
        "position": [3040, 512],
        "id": "sw1",
        "name": "Route by Integration"
    },
    {
        "parameters": {"jsCode": node_d_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3360, 300],
        "id": "nd1",
        "name": "Send Google OAuth Email"
    },
    {
        "parameters": {"jsCode": node_e_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3360, 512],
        "id": "ne1",
        "name": "Send Outlook OAuth Email"
    },
    {
        "parameters": {"jsCode": node_f_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3360, 720],
        "id": "nf1",
        "name": "Send Placeholder Email"
    }
]

wf['nodes'].extend(new_nodes)

# Add new connections
wf['connections']['Send Setup Emails'] = {
    "main": [[{"node": "Map Integration Type", "type": "main", "index": 0}]]
}
wf['connections']['Map Integration Type'] = {
    "main": [[{"node": "Update Booking Fields", "type": "main", "index": 0}]]
}
wf['connections']['Update Booking Fields'] = {
    "main": [[{"node": "Route by Integration", "type": "main", "index": 0}]]
}
wf['connections']['Route by Integration'] = {
    "main": [
        [{"node": "Send Google OAuth Email", "type": "main", "index": 0}],
        [{"node": "Send Outlook OAuth Email", "type": "main", "index": 0}],
        [{"node": "Send Placeholder Email", "type": "main", "index": 0}],
        [{"node": "Send Placeholder Email", "type": "main", "index": 0}]
    ]
}

# Prepare update payload (only nodes and connections needed)
update_payload = {
    "nodes": wf['nodes'],
    "connections": wf['connections'],
    "settings": wf.get('settings', {})
}

with open('C:/Users/danie/OneDrive/Desktop/Syntharra/claude_code/onboarding_update.json', 'w') as f:
    json.dump(update_payload, f)

# Update the workflow
result = subprocess.run([
    'curl', '-s', '-X', 'PUT',
    'https://n8n.syntharra.com/api/v1/workflows/kz1VmwNccunRMEaF',
    '-H', f'X-N8N-API-KEY: {N8N_KEY}',
    '-H', 'Content-Type: application/json',
    '-d', '@C:/Users/danie/OneDrive/Desktop/Syntharra/claude_code/onboarding_update.json'
], capture_output=True, text=True, timeout=30)

resp = json.loads(result.stdout)
print(f"Workflow ID: {resp.get('id', 'ERROR')}")
print(f"Name: {resp.get('name', '')}")
print(f"Nodes: {len(resp.get('nodes', []))}")
if 'message' in resp:
    print(f"Error: {resp['message']}")
