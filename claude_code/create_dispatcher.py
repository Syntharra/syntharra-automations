import json, subprocess, os

N8N_KEY = os.environ.get('N8N_KEY', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

# Fetch client + check token expiry
fetch_and_check_code = f"""// Fetch client config + check token expiry
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const body = $input.first().json.body;
const action = body.action;
const agent_id = body.agent_id;

const res = await fetch(
  SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + agent_id + '&select=oauth_access_token,oauth_refresh_token,oauth_token_expiry,google_calendar_id,booking_hours,slot_duration_minutes,buffer_time_minutes,min_notice_hours',
  {{ headers: {{ apikey: SUPABASE_KEY, Authorization: 'Bearer ' + SUPABASE_KEY }} }}
);
const rows = await res.json();
const client = rows[0] || {{}};

const needsRefresh = client.oauth_token_expiry && new Date(client.oauth_token_expiry) < new Date();

return [{{ json: {{
  action,
  agent_id,
  caller_name: body.caller_name || '',
  caller_phone: body.caller_phone || '',
  job_type: body.job_type || '',
  selected_slot: body.selected_slot || '',
  access_token: client.oauth_access_token || '',
  refresh_token: client.oauth_refresh_token || '',
  token_expiry: client.oauth_token_expiry || '',
  google_calendar_id: client.google_calendar_id || 'primary',
  booking_hours: client.booking_hours || 'Mon-Fri 8am-5pm',
  slot_duration_minutes: client.slot_duration_minutes || 60,
  buffer_time_minutes: client.buffer_time_minutes || 30,
  min_notice_hours: client.min_notice_hours || 2,
  needsRefresh
}} }}];"""

# Refresh token node
refresh_code = f"""// Refresh Google OAuth token if expired
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const d = $input.first().json;

if (!d.needsRefresh) {{
  return [{{ json: d }}];
}}

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || '';

const tokenRes = await fetch('https://oauth2.googleapis.com/token', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
  body: new URLSearchParams({{
    grant_type: 'refresh_token',
    refresh_token: d.refresh_token,
    client_id: GOOGLE_CLIENT_ID,
    client_secret: GOOGLE_CLIENT_SECRET
  }}).toString()
}});
const tokens = await tokenRes.json();

if (tokens.access_token) {{
  d.access_token = tokens.access_token;
  const newExpiry = new Date(Date.now() + (tokens.expires_in || 3600) * 1000).toISOString();
  d.token_expiry = newExpiry;

  await fetch(
    SUPABASE_URL + '/rest/v1/hvac_standard_agent?agent_id=eq.' + d.agent_id,
    {{
      method: 'PATCH',
      headers: {{
        apikey: SUPABASE_KEY,
        Authorization: 'Bearer ' + SUPABASE_KEY,
        'Content-Type': 'application/json'
      }},
      body: JSON.stringify({{
        oauth_access_token: tokens.access_token,
        oauth_token_expiry: newExpiry
      }})
    }}
  );
}}

return [{{ json: d }}];"""

# Get slots logic
get_slots_code = """// Get free slots from Google Calendar
const d = $input.first().json;

// Fetch busy times from Google Calendar FreeBusy API
const now = new Date();
const timeMax = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

const freeBusyRes = await fetch('https://www.googleapis.com/calendar/v3/freeBusy', {
  method: 'POST',
  headers: {
    Authorization: 'Bearer ' + d.access_token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    timeMin: now.toISOString(),
    timeMax: timeMax.toISOString(),
    timeZone: 'UTC',
    items: [{ id: d.google_calendar_id }]
  })
});
const freeBusy = await freeBusyRes.json();

const busyPeriods = (freeBusy.calendars && freeBusy.calendars[d.google_calendar_id])
  ? freeBusy.calendars[d.google_calendar_id].busy || []
  : [];

// Parse booking hours (e.g. "Mon-Fri 8am-5pm, Sat 9am-1pm")
function parseBookingHours(bh) {
  const dayMap = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  const result = {};
  if (!bh) return result;
  const parts = bh.split(',').map(s => s.trim());
  for (const part of parts) {
    const match = part.match(/([A-Za-z]+)(?:-([A-Za-z]+))?\\s+(\\d+(?::\\d+)?\\s*[ap]m)\\s*-\\s*(\\d+(?::\\d+)?\\s*[ap]m)/i);
    if (!match) continue;
    const startDay = dayMap[match[1].slice(0,3)] ?? -1;
    const endDay = match[2] ? (dayMap[match[2].slice(0,3)] ?? startDay) : startDay;
    function parseTime(t) {
      const m2 = t.match(/(\\d+)(?::(\\d+))?\\s*([ap]m)/i);
      if (!m2) return 0;
      let h = parseInt(m2[1]);
      const min = m2[2] ? parseInt(m2[2]) : 0;
      if (m2[3].toLowerCase() === 'pm' && h !== 12) h += 12;
      if (m2[3].toLowerCase() === 'am' && h === 12) h = 0;
      return h * 60 + min;
    }
    const startMin = parseTime(match[3]);
    const endMin = parseTime(match[4]);
    for (let day = startDay; day <= endDay; day++) {
      result[day] = { start: startMin, end: endMin };
    }
  }
  return result;
}

const schedule = parseBookingHours(d.booking_hours);
const slotDuration = d.slot_duration_minutes || 60;
const buffer = d.buffer_time_minutes || 30;
const minNoticeMs = (d.min_notice_hours || 2) * 60 * 60 * 1000;
const earliestSlot = new Date(now.getTime() + minNoticeMs);

const freeSlots = [];
const slotTimes = [];

for (let dayOffset = 0; dayOffset < 7 && freeSlots.length < 6; dayOffset++) {
  const date = new Date(now);
  date.setUTCDate(date.getUTCDate() + dayOffset);
  const dayOfWeek = date.getUTCDay();

  const daySchedule = schedule[dayOfWeek];
  if (!daySchedule) continue;

  const dayStart = new Date(date);
  dayStart.setUTCHours(0, 0, 0, 0);

  let cursor = dayStart.getTime() + daySchedule.start * 60000;
  const dayEnd = dayStart.getTime() + daySchedule.end * 60000;

  while (cursor + slotDuration * 60000 <= dayEnd && freeSlots.length < 6) {
    const slotStart = new Date(cursor);
    const slotEnd = new Date(cursor + slotDuration * 60000);

    if (slotStart < earliestSlot) {
      cursor += 30 * 60000;
      continue;
    }

    // Check for conflicts with busy periods (including buffer)
    const bufferedStart = cursor - buffer * 60000;
    const bufferedEnd = cursor + slotDuration * 60000 + buffer * 60000;
    let conflict = false;
    for (const busy of busyPeriods) {
      const busyStart = new Date(busy.start).getTime();
      const busyEnd = new Date(busy.end).getTime();
      if (bufferedStart < busyEnd && bufferedEnd > busyStart) {
        conflict = true;
        cursor = busyEnd + buffer * 60000;
        break;
      }
    }

    if (!conflict) {
      const opts = { weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'UTC' };
      freeSlots.push(slotStart.toLocaleString('en-US', opts));
      slotTimes.push(slotStart.toISOString());
      cursor += slotDuration * 60000;
    }
  }
}

return [{ json: { success: true, slots: freeSlots, slot_times: slotTimes } }];"""

# Create booking logic
create_booking_code = f"""// Create Google Calendar event
const SUPABASE_URL = 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const d = $input.first().json;

const startTime = new Date(d.selected_slot);
const endTime = new Date(startTime.getTime() + d.slot_duration_minutes * 60000);

const eventRes = await fetch(
  'https://www.googleapis.com/calendar/v3/calendars/' + encodeURIComponent(d.google_calendar_id) + '/events',
  {{
    method: 'POST',
    headers: {{
      Authorization: 'Bearer ' + d.access_token,
      'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{
      summary: d.job_type + ' \u2014 ' + d.caller_name,
      description: 'Booked by Syntharra AI\\nCustomer: ' + d.caller_name + '\\nPhone: ' + d.caller_phone + '\\nJob: ' + d.job_type,
      start: {{ dateTime: d.selected_slot, timeZone: 'UTC' }},
      end: {{ dateTime: endTime.toISOString(), timeZone: 'UTC' }}
    }})
  }}
);
const event = await eventRes.json();

// Log booking to hvac_call_log
await fetch(SUPABASE_URL + '/rest/v1/hvac_call_log', {{
  method: 'POST',
  headers: {{
    apikey: SUPABASE_KEY,
    Authorization: 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json'
  }},
  body: JSON.stringify({{
    agent_id: d.agent_id,
    caller_name: d.caller_name,
    caller_phone: d.caller_phone,
    booking_id: event.id || '',
    booking_platform: 'google',
    booking_time: d.selected_slot,
    job_type: d.job_type
  }})
}});

return [{{ json: {{ success: true, booking_id: event.id || '', confirmation_time: d.selected_slot }} }}];"""

# Cancel booking response
cancel_code = """// Cancel booking \u2014 transfer to office
return [{ json: { success: false, message: 'Please transfer to office to cancel' } }];"""

wf = {
  "name": "Premium Dispatcher \u2014 Google Calendar",
  "nodes": [
    {"parameters": {"path": "dispatcher-google", "httpMethod": "POST", "responseMode": "lastNode", "options": {}}, "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [240, 400], "id": "wh1", "name": "Dispatcher Webhook", "webhookId": "dispatcher-google"},
    {"parameters": {"jsCode": fetch_and_check_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [520, 400], "id": "fc1", "name": "Fetch Client Config"},
    {"parameters": {"jsCode": refresh_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [800, 400], "id": "rt1", "name": "Refresh Token If Needed"},
    {
      "parameters": {
        "rules": {
          "values": [
            {"conditions": {"conditions": [{"leftValue": "={{ $json.action }}", "rightValue": "get_slots", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "get_slots"},
            {"conditions": {"conditions": [{"leftValue": "={{ $json.action }}", "rightValue": "create_booking", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "create_booking"},
            {"conditions": {"conditions": [{"leftValue": "={{ $json.action }}", "rightValue": "cancel_booking", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "cancel_booking"}
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3.2,
      "position": [1080, 400],
      "id": "sw1",
      "name": "Route by Action"
    },
    {"parameters": {"jsCode": get_slots_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1360, 200], "id": "gs1", "name": "Get Free Slots"},
    {"parameters": {"jsCode": create_booking_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1360, 400], "id": "cb1", "name": "Create Booking"},
    {"parameters": {"jsCode": cancel_code}, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1360, 600], "id": "cn1", "name": "Cancel Response"}
  ],
  "connections": {
    "Dispatcher Webhook": {"main": [[{"node": "Fetch Client Config", "type": "main", "index": 0}]]},
    "Fetch Client Config": {"main": [[{"node": "Refresh Token If Needed", "type": "main", "index": 0}]]},
    "Refresh Token If Needed": {"main": [[{"node": "Route by Action", "type": "main", "index": 0}]]},
    "Route by Action": {
      "main": [
        [{"node": "Get Free Slots", "type": "main", "index": 0}],
        [{"node": "Create Booking", "type": "main", "index": 0}],
        [{"node": "Cancel Response", "type": "main", "index": 0}]
      ]
    }
  },
  "settings": {"executionOrder": "v1"}
}

with open('C:/Users/danie/OneDrive/Desktop/Syntharra/claude_code/dispatcher_wf.json', 'w') as f:
    json.dump(wf, f)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://n8n.syntharra.com/api/v1/workflows',
    '-H', f'X-N8N-API-KEY: {N8N_KEY}',
    '-H', 'Content-Type: application/json',
    '-d', '@C:/Users/danie/OneDrive/Desktop/Syntharra/claude_code/dispatcher_wf.json'
], capture_output=True, text=True, timeout=30)

resp = json.loads(result.stdout)
wf_id = resp.get('id', 'ERROR')
print(f"Workflow ID: {wf_id}")
print(f"Name: {resp.get('name', '')}")
print(f"Nodes: {len(resp.get('nodes', []))}")
if 'message' in resp:
    print(f"Error: {resp['message']}")

# Activate
if wf_id != 'ERROR':
    result2 = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://n8n.syntharra.com/api/v1/workflows/{wf_id}/activate',
        '-H', f'X-N8N-API-KEY: {N8N_KEY}'
    ], capture_output=True, text=True, timeout=30)
    resp2 = json.loads(result2.stdout)
    print(f"Active: {resp2.get('active', False)}")
