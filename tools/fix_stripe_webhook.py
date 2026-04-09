"""
Replace all fetch() calls in Handle Checkout.Session.Completed with $helpers.httpRequest.
Set node typeVersion to 2 (required for $helpers).
Inline Brevo key to remove vault lookup fetch.
"""
import json, urllib.request

N8N_KEY = "n8n-api-key-from-syntharra_vault"
WORKFLOW_ID = "xKD3ny6kfHL0HHXq"
SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
SUPABASE_KEY = "supabase-service-role-key-from-syntharra_vault"
BREVO_KEY = "brevo-api-key-from-syntharra_vault"
BASE = "https://n8n.syntharra.com/api/v1"

NEW_CHECKOUT_CODE = f"""// Type guard
if (!$json.body || $json.body.type !== 'checkout.session.completed') {{
  return [];
}}

const SUPABASE_URL = '{SUPABASE_URL}';
const SUPABASE_KEY = '{SUPABASE_KEY}';
const BREVO_KEY    = '{BREVO_KEY}';
const JOTFORM_BASE = 'https://form.jotform.com/260795139953066';

const PLANS = {{
  'price_1TKNdcECS71NQsk8AmypDclD': {{ tier:'starter',      name:'Starter',      billing:'Monthly', amount:'$397/mo',    minutes:350,  overageRate:0.25 }},
  'price_1TKNdgECS71NQsk8aUhrMbWI': {{ tier:'starter',      name:'Starter',      billing:'Annual',  amount:'$3,967/yr',  minutes:350,  overageRate:0.25 }},
  'price_1TKNdjECS71NQsk8GQNOx7Fd': {{ tier:'professional', name:'Professional', billing:'Monthly', amount:'$697/mo',    minutes:700,  overageRate:0.18 }},
  'price_1TKNdlECS71NQsk824wcVkeV': {{ tier:'professional', name:'Professional', billing:'Annual',  amount:'$6,970/yr',  minutes:700,  overageRate:0.18 }},
  'price_1TKNdnECS71NQsk8iQFNDTgv': {{ tier:'business',     name:'Business',     billing:'Monthly', amount:'$1,097/mo',  minutes:1400, overageRate:0.12 }},
  'price_1TKNdpECS71NQsk8SBnDoeca': {{ tier:'business',     name:'Business',     billing:'Annual',  amount:'$10,970/yr', minutes:1400, overageRate:0.12 }},
}};

const session        = $json.body.data.object;
const customerId     = session.customer || '';
const subscriptionId = session.subscription || '';
const sessionId      = session.id || '';
const customerEmail  = (session.customer_details && session.customer_details.email) || '';
const customerName   = (session.customer_details && session.customer_details.name)  || 'Valued Client';
let   priceId        = (session.metadata && session.metadata.price_id) || '';
const plan           = PLANS[priceId] || PLANS['price_1TKNdjECS71NQsk8GQNOx7Fd'];
const jotformUrl     = JOTFORM_BASE + '?tier=' + plan.tier;
const signupDate     = new Date(session.created * 1000).toLocaleDateString('en-AU', {{ day:'2-digit', month:'long', year:'numeric' }});

// 1. Save to Supabase stripe_payment_data
await $helpers.httpRequest({{
  method: 'POST',
  url: SUPABASE_URL + '/rest/v1/stripe_payment_data',
  headers: {{
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
  }},
  body: JSON.stringify({{
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
  }}),
}});
console.log('[CHECKOUT] Saved to stripe_payment_data');

// 2. Send welcome email via Brevo
if (customerEmail) {{
  const emailHtml = `<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;background:#F2F1FF;padding:40px 20px">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:18px;padding:40px;border:1px solid #E8E6FF">
<div style="height:4px;background:linear-gradient(90deg,#6C63FF,#A78BFA);border-radius:4px;margin-bottom:24px"></div>
<h2 style="color:#0D0D1A">Welcome to Syntharra, ${{customerName}}!</h2>
<p style="color:#6B7280">Your <strong>${{plan.name}}</strong> plan is confirmed.</p>
<div style="background:#F8F7FF;border-radius:12px;padding:16px;margin:20px 0;font-size:13px;color:#4A4A6A">
  Plan: <strong>${{plan.name}} (${{plan.billing}})</strong><br>
  Included minutes: <strong>${{plan.minutes}}/month</strong><br>
  Overage rate: <strong>$${{plan.overageRate.toFixed(2)}}/min</strong>
</div>
<div style="text-align:center;margin:24px 0">
  <a href="${{jotformUrl}}" style="background:#6C63FF;color:#fff;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:700">Complete Setup Form &rarr;</a>
</div>
<p style="font-size:12px;color:#6B7280;text-align:center">Live within 1 business day of form submission.</p>
</div></body></html>`;

  await $helpers.httpRequest({{
    method: 'POST',
    url: 'https://api.brevo.com/v3/smtp/email',
    headers: {{ 'api-key': BREVO_KEY, 'Content-Type': 'application/json' }},
    body: JSON.stringify({{
      sender:      {{ name: 'Syntharra', email: 'support@syntharra.com' }},
      to:          [{{ email: customerEmail, name: customerName }}],
      subject:     'Welcome to Syntharra — Complete Your Setup',
      htmlContent: emailHtml,
    }}),
  }});
  console.log('[CHECKOUT] Welcome email sent to', customerEmail);
}}

return [{{ json: {{
  eventType: 'checkout.session.completed',
  customerId, subscriptionId, sessionId, customerEmail, customerName,
  tier: plan.tier, planName: plan.name, minutes: plan.minutes,
  jotformUrl,
}} }}];
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

for n in wf["nodes"]:
    if n["name"] == "Handle Checkout.Session.Completed":
        n["typeVersion"] = 2
        n["parameters"]["jsCode"] = NEW_CHECKOUT_CODE
        print("  [OK] Handle Checkout.Session.Completed -> $helpers.httpRequest, typeVersion 2")

put_body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData"),
}
result = api("PUT", f"/workflows/{WORKFLOW_ID}", put_body)
print(f"  [OK] Saved -- updatedAt: {result.get('updatedAt','?')}")
