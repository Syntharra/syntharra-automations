import json, urllib.request, urllib.error, os

N8N_KEY    = os.environ.get('N8N_KEY', '')
GROQ_KEY   = os.environ.get('GROQ_KEY', '')
SB_KEY     = os.environ.get('SB_KEY', '')
RETELL_KEY = os.environ.get('RETELL_KEY', '')
WF2_ID     = "ZAAtRETIIVZSMMDk"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
SB_URL     = "https://hgheyqwnrcvwtgngqdnq.supabase.co"
RETELL_URL = "https://api.retellai.com"

def groq_hdr():
    return {"parameters": [
        {"name": "Authorization", "value": "Bearer " + GROQ_KEY},
        {"name": "Content-Type",  "value": "application/json"}
    ]}

def sb_read_hdr():
    return {"parameters": [
        {"name": "apikey",        "value": SB_KEY},
        {"name": "Authorization", "value": "Bearer " + SB_KEY}
    ]}

def sb_patch_hdr():
    return {"parameters": [
        {"name": "apikey",        "value": SB_KEY},
        {"name": "Authorization", "value": "Bearer " + SB_KEY},
        {"name": "Content-Type",  "value": "application/json"},
        {"name": "Prefer",        "value": "return=minimal"}
    ]}

def retell_get_hdr():
    return {"parameters": [
        {"name": "Authorization", "value": "Bearer " + RETELL_KEY}
    ]}

def retell_write_hdr():
    return {"parameters": [
        {"name": "Authorization", "value": "Bearer " + RETELL_KEY},
        {"name": "Content-Type",  "value": "application/json"}
    ]}

def http_node(nid, name, method, url, hdr, body=None, x=0, y=0):
    p = {"method": method, "url": url, "sendHeaders": True,
         "headerParameters": hdr, "options": {}}
    if body:
        p["sendBody"] = True
        p["specifyBody"] = "json"
        p["jsonBody"] = body
    return {"id": nid, "name": name,
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": [x, y], "parameters": p}

nodes = []

# 1. Webhook: Apply Fix
nodes.append({
    "id": "fa-webhook", "name": "Webhook: Apply Fix",
    "type": "n8n-nodes-base.webhook", "typeVersion": 2,
    "position": [240, 300],
    "parameters": {"httpMethod": "POST", "path": "apply-agent-fix",
                   "responseMode": "responseNode", "options": {}},
    "webhookId": "apply-agent-fix-wh"
})

# 2. GET Pending Fix from Supabase
get_fix_url = ("={{ '" + SB_URL + "/rest/v1/agent_pending_fixes?id=eq.'"
               "+($json.body?$json.body.fix_id:$json.fix_id)+'&select=*' }}")
nodes.append(http_node(
    "get-fix","GET Pending Fix","GET",
    get_fix_url, sb_read_hdr(), None, 480, 300
))

# 3. Parse Fix Data (Code — no fetch, extracts and validates)
parse_code = (
    "const fixes = $input.first().json;\n"
    "const fixArr = Array.isArray(fixes) ? fixes : [fixes];\n"
    "if (!fixArr.length || !fixArr[0].id) throw new Error('Fix not found in Supabase');\n"
    "const fix = fixArr[0];\n\n"
    "const wh = $('Webhook: Apply Fix').first().json;\n"
    "const whBody = wh.body || wh;\n"
    "const approvedBy = whBody.approved_by || 'Dan';\n\n"
    "return [{json: {\n"
    "  fix_id:          fix.id,\n"
    "  agent_id:        fix.agent_id,\n"
    "  fix_description: fix.fix_description,\n"
    "  scenario_name:   fix.scenario_name,\n"
    "  approved_by:     approvedBy\n"
    "}}];\n"
)
nodes.append({
    "id": "parse-fix","name": "Parse Fix Data",
    "type": "n8n-nodes-base.code","typeVersion": 2,
    "position": [720, 300],
    "parameters": {"mode": "runOnceForEachItem","jsCode": parse_code}
})

# 4. GET Retell Agent
get_agent_url = "={{ '" + RETELL_URL + "/get-agent/'+$json.agent_id }}"
nodes.append(http_node(
    "get-agent","GET Retell Agent","GET",
    get_agent_url, retell_get_hdr(), None, 960, 300
))

# 5. Groq: Apply Fix to Prompt  (input = Retell agent obj with general_prompt)
apply_fix_body = ("={{ JSON.stringify({model:'llama-3.3-70b-versatile',max_tokens:4000,temperature:0.1,"
                  "messages:["
                  "{role:'system',content:'You are a precise prompt editor. Apply ONLY the specified fix to the agent prompt. Do not change anything else. Return ONLY the complete updated prompt text, no explanation, no markdown.'},"
                  "{role:'user',content:'CURRENT PROMPT:\\n'+$json.general_prompt"
                  "+'\\n\\nFIX TO APPLY: '+$('Parse Fix Data').item.json.fix_description"
                  "+'\\n\\nReturn the complete updated prompt with ONLY this fix applied.'}"
                  "]}) }}")
nodes.append(http_node(
    "groq-apply","Groq: Apply Fix","POST",GROQ_URL,groq_hdr(),apply_fix_body,1200,300
))

# 6. PATCH Retell Agent  (input = Groq response with updated prompt)
patch_url = "={{ '" + RETELL_URL + "/update-agent/'+$('Parse Fix Data').item.json.agent_id }}"
patch_body = "={{ JSON.stringify({general_prompt:$json.choices[0].message.content}) }}"
nodes.append(http_node(
    "patch-agent","PATCH Retell Agent","PATCH",
    patch_url, retell_write_hdr(), patch_body, 1440, 300
))

# 7. POST Publish Agent
pub_url = "={{ '" + RETELL_URL + "/publish-agent/'+$('Parse Fix Data').item.json.agent_id }}"
nodes.append(http_node(
    "publish-agent","POST Publish Agent","POST",
    pub_url, retell_write_hdr(), None, 1680, 300
))

# 8. PATCH Fix Status in Supabase
patch_fix_url = ("={{ '" + SB_URL + "/rest/v1/agent_pending_fixes?id=eq.'"
                 "+$('Parse Fix Data').item.json.fix_id }}")
patch_fix_body = ("={{ JSON.stringify({"
                  "status:'applied',"
                  "approved_by:$('Parse Fix Data').item.json.approved_by,"
                  "applied_at:new Date().toISOString()"
                  "}) }}")
nodes.append(http_node(
    "patch-fix","PATCH Fix Status","PATCH",
    patch_fix_url, sb_patch_hdr(), patch_fix_body, 1920, 300
))

# 9. Respond Success
nodes.append({
    "id": "fa-respond","name": "Respond Success",
    "type": "n8n-nodes-base.respondToWebhook","typeVersion": 1.1,
    "position": [2160, 300],
    "parameters": {
        "respondWith": "json",
        "responseBody": ("={{ JSON.stringify({"
                         "success:true,"
                         "message:'Fix applied and agent published',"
                         "fix_id:$('Parse Fix Data').item.json.fix_id,"
                         "agent_id:$('Parse Fix Data').item.json.agent_id"
                         "}) }}"),
        "options": {}
    }
})

connections = {
    "Webhook: Apply Fix": {"main":[[{"node":"GET Pending Fix","type":"main","index":0}]]},
    "GET Pending Fix":    {"main":[[{"node":"Parse Fix Data","type":"main","index":0}]]},
    "Parse Fix Data":     {"main":[[{"node":"GET Retell Agent","type":"main","index":0}]]},
    "GET Retell Agent":   {"main":[[{"node":"Groq: Apply Fix","type":"main","index":0}]]},
    "Groq: Apply Fix":    {"main":[[{"node":"PATCH Retell Agent","type":"main","index":0}]]},
    "PATCH Retell Agent": {"main":[[{"node":"POST Publish Agent","type":"main","index":0}]]},
    "POST Publish Agent": {"main":[[{"node":"PATCH Fix Status","type":"main","index":0}]]},
    "PATCH Fix Status":   {"main":[[{"node":"Respond Success","type":"main","index":0}]]}
}

workflow = {
    "name": "SYNTHARRA_FIX_APPROVER",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}

payload = json.dumps(workflow)
print("WF2 payload:", len(payload), "chars,", len(nodes), "nodes")

url = f"https://n8n.syntharra.com/api/v1/workflows/{WF2_ID}"
req = urllib.request.Request(
    url, data=payload.encode(),
    headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
        print("PUT OK \u2014 id:", resp.get("id"), "| name:", resp.get("name"), "| active:", resp.get("active"))
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"PUT ERROR {e.code}:", err[:1000])
