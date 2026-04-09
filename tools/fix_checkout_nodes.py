"""
Fix checkout handler data flow.

Root cause: HTTP Request nodes replace $json with their API response.
The email node was firing AFTER Supabase, so $json was the empty Supabase
response by the time it ran — hence "to": [{}] and missing htmlContent.

Fix:
  1. Handle Checkout (Code) — adds event_id to return
  2. Send Email (HTTP Request) — fires FIRST, $json is Handle Checkout output
  3. Save to Supabase (HTTP Request) — uses $('Handle Checkout...').item.json refs
  4. Mark Checkout Processed (HTTP Request) — same node ref for event_id

Shared Mark Processed node left untouched (used by other event handlers).
"""
import json, urllib.request

N8N_KEY = "n8n-api-key-from-syntharra_vault"
WORKFLOW_ID = "xKD3ny6kfHL0HHXq"
SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SUPABASE_KEY = "supabase-service-role-key-from-syntharra_vault"
BREVO_KEY = "brevo-api-key-from-syntharra_vault"
BASE = "https://n8n.syntharra.com/api/v1"

# Ref string for node name — used in Supabase and Mark Processed expressions
CHECKOUT_NODE = "Handle Checkout.Session.Completed"

NEW_CHECKOUT_CODE = r"""// Type guard
if (!$json.body || $json.body.type !== 'checkout.session.completed') {
  return [];
}

const PLANS = {
  'price_1TKNdcECS71NQsk8AmypDclD': { tier:'starter',      name:'Starter',      billing:'Monthly', amount:'$397/mo',    minutes:350,  overageRate:0.25 },
  'price_1TKNdgECS71NQsk8aUhrMbWI': { tier:'starter',      name:'Starter',      billing:'Annual',  amount:'$3,967/yr',  minutes:350,  overageRate:0.25 },
  'price_1TKNdjECS71NQsk8GQNOx7Fd': { tier:'professional', name:'Professional', billing:'Monthly', amount:'$697/mo',    minutes:700,  overageRate:0.18 },
  'price_1TKNdlECS71NQsk824wcVkeV': { tier:'professional', name:'Professional', billing:'Annual',  amount:'$6,970/yr',  minutes:700,  overageRate:0.18 },
  'price_1TKNdnECS71NQsk8iQFNDTgv': { tier:'business',     name:'Business',     billing:'Monthly', amount:'$1,097/mo',  minutes:1400, overageRate:0.12 },
  'price_1TKNdpECS71NQsk8SBnDoeca': { tier:'business',     name:'Business',     billing:'Annual',  amount:'$10,970/yr', minutes:1400, overageRate:0.12 },
};

const session        = $json.body.data.object;
const customerId     = session.customer || '';
const subscriptionId = session.subscription || '';
const sessionId      = session.id || '';
const eventId        = $json.body.id || '';
const customerEmail  = (session.customer_details && session.customer_details.email) || '';
const customerName   = (session.customer_details && session.customer_details.name)  || 'Valued Client';
const priceId        = (session.metadata && session.metadata.price_id) || '';
const plan           = PLANS[priceId] || PLANS['price_1TKNdjECS71NQsk8GQNOx7Fd'];
const jotformUrl     = 'https://form.jotform.com/260795139953066?tier=' + plan.tier;
const signupDate     = new Date(session.created * 1000).toLocaleDateString('en-AU', { day:'2-digit', month:'long', year:'numeric' });

const brevoHtml = `<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;background:#F2F1FF;padding:40px 20px">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:18px;padding:40px;border:1px solid #E8E6FF">
<div style="height:4px;background:linear-gradient(90deg,#6C63FF,#A78BFA);border-radius:4px;margin-bottom:24px"></div>
<h2 style="color:#0D0D1A">Welcome to Syntharra, ${customerName}!</h2>
<p style="color:#6B7280">Your <strong>${plan.name}</strong> plan is confirmed.</p>
<div style="background:#F8F7FF;border-radius:12px;padding:16px;margin:20px 0;font-size:13px;color:#4A4A6A">
  Plan: <strong>${plan.name} (${plan.billing})</strong><br>
  Included minutes: <strong>${plan.minutes}/month</strong><br>
  Overage rate: <strong>$${plan.overageRate.toFixed(2)}/min</strong>
</div>
<div style="text-align:center;margin:24px 0">
  <a href="${jotformUrl}" style="background:#6C63FF;color:#fff;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:700">Complete Setup Form &rarr;</a>
</div>
<p style="font-size:12px;color:#6B7280;text-align:center">Live within 1 business day of form submission.</p>
</div></body></html>`;

return [{ json: {
  event_id:               eventId,
  stripe_customer_id:     customerId,
  stripe_subscription_id: subscriptionId,
  stripe_session_id:      sessionId,
  customer_email:         customerEmail,
  customer_name:          customerName,
  plan_name:              plan.name,
  plan_billing:           plan.billing,
  plan_amount:            plan.amount,
  tier:                   plan.tier,
  minutes:                String(plan.minutes),
  overage_rate:           plan.overageRate,
  payment_status:         session.payment_status || '',
  jotform_sent:           true,
  signup_date:            signupDate,
  jotform_url:            jotformUrl,
  brevo_html:             brevoHtml,
  eventType:              'checkout.session.completed',
} }];
"""

def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

print("Fetching workflow...")
wf = api("GET", f"/workflows/{WORKFLOW_ID}")

# Get Handle Checkout position for layout
checkout_pos = [1024, 720]
for n in wf["nodes"]:
    if n["name"] == CHECKOUT_NODE:
        checkout_pos = n.get("position", [1024, 720])
        break

# Remove old checkout chain nodes (clean slate)
wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in [
    "Save Checkout to Supabase",
    "Send Checkout Welcome Email",
    "Mark Checkout Processed",
]]

# 1. Update Handle Checkout code
for n in wf["nodes"]:
    if n["name"] == CHECKOUT_NODE:
        n["typeVersion"] = 2
        n["parameters"]["jsCode"] = NEW_CHECKOUT_CODE
        print(f"  [OK] {CHECKOUT_NODE} updated")
        break

# 2. Email node — fires FIRST, $json = Handle Checkout output
# Pattern matches working HVAC node: single quotes, direct $json refs
email_node = {
    "id": "send-checkout-email",
    "name": "Send Checkout Welcome Email",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [checkout_pos[0] + 220, checkout_pos[1]],
    "parameters": {
        "method": "POST",
        "url": "https://api.brevo.com/v3/smtp/email",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "accept",        "value": "application/json"},
                {"name": "content-type",  "value": "application/json"},
                {"name": "api-key",       "value": BREVO_KEY},
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        # Email fires when $json is Handle Checkout output — use direct $json refs
        "jsonBody": "={{ { 'sender': { 'name': 'Syntharra', 'email': 'support@syntharra.com' }, 'to': [{ 'email': $json.customer_email, 'name': $json.customer_name }], 'subject': 'Welcome to Syntharra - Complete Your Setup', 'htmlContent': $json.brevo_html } }}",
        "options": {},
    }
}

# 3. Supabase node — fires AFTER email, $json is Brevo response
# Must use node reference for all fields
sb_ref = f"$('Handle Checkout.Session.Completed').item.json"
supabase_node = {
    "id": "save-checkout-supabase",
    "name": "Save Checkout to Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [checkout_pos[0] + 440, checkout_pos[1]],
    "parameters": {
        "method": "POST",
        "url": f"{SUPABASE_URL}/rest/v1/stripe_payment_data",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "apikey",        "value": SUPABASE_KEY},
                {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                {"name": "Content-Type",  "value": "application/json"},
                {"name": "Prefer",        "value": "return=minimal"},
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        # $json is Brevo response here — must ref Handle Checkout node by name
        "jsonBody": (
            f"={{ {{ "
            f"'stripe_customer_id': {sb_ref}.stripe_customer_id, "
            f"'stripe_subscription_id': {sb_ref}.stripe_subscription_id, "
            f"'stripe_session_id': {sb_ref}.stripe_session_id, "
            f"'customer_email': {sb_ref}.customer_email, "
            f"'customer_name': {sb_ref}.customer_name, "
            f"'plan_name': {sb_ref}.plan_name, "
            f"'plan_billing': {sb_ref}.plan_billing, "
            f"'plan_amount': {sb_ref}.plan_amount, "
            f"'tier': {sb_ref}.tier, "
            f"'minutes': {sb_ref}.minutes, "
            f"'overage_rate': {sb_ref}.overage_rate, "
            f"'payment_status': {sb_ref}.payment_status, "
            f"'jotform_sent': true, "
            f"'signup_date': {sb_ref}.signup_date "
            f"}} }}"
        ),
        "options": {},
    }
}

# 4. Mark Checkout Processed — dedicated node for checkout path
# Shared Mark Processed left untouched for other event types
mark_node = {
    "id": "mark-checkout-processed",
    "name": "Mark Checkout Processed",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [checkout_pos[0] + 660, checkout_pos[1]],
    "parameters": {
        "method": "POST",
        "url": f"{SUPABASE_URL}/rest/v1/stripe_processed_events",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "apikey",        "value": SUPABASE_KEY},
                {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                {"name": "Content-Type",  "value": "application/json"},
                {"name": "Prefer",        "value": "return=minimal"},
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        # event_id from Handle Checkout output via node reference
        "jsonBody": f"={{ {{ 'event_id': {sb_ref}.event_id }} }}",
        "options": {},
    }
}

wf["nodes"].extend([email_node, supabase_node, mark_node])
print("  [OK] Added: Send Email, Save Supabase, Mark Checkout Processed")

# Connections for checkout path:
# Handle Checkout -> Send Email -> Save Supabase -> Mark Checkout Processed
conns = wf["connections"]
conns[CHECKOUT_NODE] = {
    "main": [[{"node": "Send Checkout Welcome Email", "type": "main", "index": 0}]]
}
conns["Send Checkout Welcome Email"] = {
    "main": [[{"node": "Save Checkout to Supabase", "type": "main", "index": 0}]]
}
conns["Save Checkout to Supabase"] = {
    "main": [[{"node": "Mark Checkout Processed", "type": "main", "index": 0}]]
}
# Mark Checkout Processed has no outbound connection (terminal)
if "Mark Checkout Processed" in conns:
    del conns["Mark Checkout Processed"]

print("  [OK] Connections: Checkout -> Email -> Supabase -> Mark Checkout Processed")

put_body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData"),
}
result = api("PUT", f"/workflows/{WORKFLOW_ID}", put_body)
print(f"  [OK] Saved - updatedAt: {result.get('updatedAt','?')}")
print("\nDone. Do another Stripe test checkout.")
