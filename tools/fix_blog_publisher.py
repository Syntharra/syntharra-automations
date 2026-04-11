#!/usr/bin/env python3
"""
fix_blog_publisher.py — Patches the n8n Blog Auto-Publisher workflow with:
1. Fix: Has Topics? IF condition ($json.length -> $input.all().length)
2. Fix: Build Full HTML uses www.syntharra.com not bare syntharra.com
3. Add: Dry-run gate (topics 2-5 go to Slack review, 6+ auto-publish)
4. Add: Slack notification on publish (and on dry-run)
"""
import json, os, sys, urllib.request

N8N_BASE = "https://n8n.syntharra.com"
WF_ID = "j8hExewOREmRp3Oq"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDI5NTM1MiwiZXhwIjoyMDg5ODcxMzUyfQ.PENNZ2K5syVFyU3Yn6FfYZP1JEtmanlV6nTrlGaeqsg"
SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co"


def n8n_get(path, n8n_key):
    req = urllib.request.Request(
        f"{N8N_BASE}{path}",
        headers={"X-N8N-API-KEY": n8n_key}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def n8n_put(path, data, n8n_key):
    # Only send fields n8n API accepts for workflow update
    payload = {
        "name": data.get("name"),
        "nodes": data.get("nodes"),
        "connections": data.get("connections"),
        "settings": data.get("settings", {}),
        "staticData": data.get("staticData"),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{N8N_BASE}{path}", data=body, method="PUT",
        headers={"X-N8N-API-KEY": n8n_key, "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} error body: {e.read().decode()[:500]}")
        raise


def main():
    n8n_key = os.environ.get("N8N_KEY", "")
    slack_hook = os.environ.get("SLACK_HOOK", "")
    if not n8n_key:
        sys.exit("N8N_KEY not set")
    if not slack_hook:
        sys.exit("SLACK_HOOK not set")

    print("Fetching workflow...")
    wf = n8n_get(f"/api/v1/workflows/{WF_ID}", n8n_key)
    print(f"Loaded: {wf['name']} ({len(wf['nodes'])} nodes)")

    nodes = wf["nodes"]
    node_by_id = {n["id"]: n for n in nodes}
    connections = wf["connections"]

    # ===========================================================
    # FIX 1: Has Topics? condition: $json.length -> $input.all().length
    # ===========================================================
    if_node = node_by_id.get("check-has-topic")
    if if_node:
        conds = if_node["parameters"]["conditions"]["conditions"]
        for c in conds:
            if c.get("leftValue") == "={{ $json.length }}":
                c["leftValue"] = "={{ $input.all().length }}"
                print("FIX 1: check-has-topic condition updated")
    else:
        print("WARN: check-has-topic node not found")

    # ===========================================================
    # FIX 2: build-html — use www.syntharra.com
    # ===========================================================
    build_node = node_by_id.get("build-html")
    if build_node:
        code = build_node["parameters"]["jsCode"]
        code = code.replace(
            "https://syntharra.com/favicon.svg",
            "https://www.syntharra.com/favicon.svg"
        )
        code = code.replace(
            "https://syntharra.com/og-image.png",
            "https://www.syntharra.com/og-image.png"
        )
        build_node["parameters"]["jsCode"] = code
        print("FIX 2: build-html www.syntharra.com URLs updated")
    else:
        print("WARN: build-html node not found")

    # ===========================================================
    # ADD 3: Dry Run Check Code node (after Base64 Encode)
    # ===========================================================
    dry_run_code = (
        "// Topics 2-5 are in the first-batch dry-run review window.\n"
        "// Topic 1 is already published manually; topics 6+ auto-publish.\n"
        "const d = $input.first().json;\n"
        "const topicId = parseInt(d.id, 10);\n"
        "const dryRun = (topicId >= 2 && topicId <= 5);\n"
        "return [{ json: { ...d, dry_run: dryRun } }];\n"
    )
    dry_run_node = {
        "id": "dry-run-check",
        "name": "Dry Run Check",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2020, 220],
        "parameters": {"jsCode": dry_run_code}
    }

    # ===========================================================
    # ADD 4: Dry Run Gate IF node
    # ===========================================================
    dry_run_gate_node = {
        "id": "dry-run-gate",
        "name": "Dry Run Gate",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [2240, 220],
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict"
                },
                "conditions": [{
                    "id": "dry-run-cond",
                    "leftValue": "={{ $json.dry_run }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equal"}
                }],
                "combinator": "and"
            },
            "options": {}
        }
    }

    # ===========================================================
    # ADD 5: Notify Slack Dry Run
    # ===========================================================
    slack_dry_body = (
        '={"text":"*[PENDING REVIEW] Blog post queued for Slack review*\\n\\n'
        '*{{ $json.title }}*\\n'
        'Tag: {{ $json.tag }} | Keyword: {{ $json.target_keyword }}\\n\\n'
        'This is topic #{{ $json.id }} (slug: `{{ $json.slug }}`). '
        'It has been marked `pending_review` in Supabase.\\n\\n'
        'To approve: set status=queued in Supabase blog_topics — '
        'it will auto-publish on the next cron run.\\n'
        'To skip: set status=skip."}'
    )
    slack_dry_node = {
        "id": "slack-dry-run",
        "name": "Notify Slack Dry Run",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2460, 120],
        "parameters": {
            "method": "POST",
            "url": slack_hook,
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": slack_dry_body,
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Content-Type", "value": "application/json"}
                ]
            }
        }
    }

    # ===========================================================
    # ADD 6: Mark Pending Review (Supabase PATCH)
    # ===========================================================
    mark_pending_node = {
        "id": "mark-pending-review",
        "name": "Mark Pending Review",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2680, 120],
        "parameters": {
            "method": "PATCH",
            "url": (
                "=https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/blog_topics"
                "?id=eq.{{ $('Dry Run Check').first().json.id }}"
            ),
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '{"status": "pending_review"}'
        }
    }

    # ===========================================================
    # ADD 7: Notify Slack Published
    # ===========================================================
    slack_pub_body = (
        '={"text":"*[PUBLISHED] New blog post is live*\\n\\n'
        '*{{ $json.title }}*\\n'
        'https://www.syntharra.com/blog/{{ $json.slug }}.html\\n\\n'
        '_Tag: {{ $json.tag }} | Keyword: {{ $json.target_keyword }}_"}'
    )
    slack_published_node = {
        "id": "slack-published",
        "name": "Notify Slack Published",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [3560, 300],
        "parameters": {
            "method": "POST",
            "url": slack_hook,
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": slack_pub_body,
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Content-Type", "value": "application/json"}
                ]
            }
        }
    }

    # Append new nodes
    wf["nodes"] = nodes + [
        dry_run_node, dry_run_gate_node, slack_dry_node,
        mark_pending_node, slack_published_node
    ]

    # ===========================================================
    # UPDATE CONNECTIONS
    # ===========================================================
    conns = wf["connections"]

    # Rewire: Base64 Encode → Dry Run Check (was → Push Article to GitHub)
    if "Base64 Encode" in conns:
        branch0 = conns["Base64 Encode"]["main"][0]
        branch0 = [e for e in branch0 if e["node"] != "Push Article to GitHub"]
        branch0.append({"node": "Dry Run Check", "type": "main", "index": 0})
        conns["Base64 Encode"]["main"][0] = branch0

    # Dry Run Check → Dry Run Gate
    conns["Dry Run Check"] = {
        "main": [[{"node": "Dry Run Gate", "type": "main", "index": 0}]]
    }

    # Dry Run Gate:
    #   branch[0] = true (dry_run=true) → Notify Slack Dry Run
    #   branch[1] = false (not dry_run) → Push Article to GitHub
    conns["Dry Run Gate"] = {
        "main": [
            [{"node": "Notify Slack Dry Run", "type": "main", "index": 0}],
            [{"node": "Push Article to GitHub", "type": "main", "index": 0}]
        ]
    }

    # Notify Slack Dry Run → Mark Pending Review
    conns["Notify Slack Dry Run"] = {
        "main": [[{"node": "Mark Pending Review", "type": "main", "index": 0}]]
    }

    # Rewire: Mark Topic Published → Notify Slack Published (was → Log Success)
    if "Mark Topic Published" in conns:
        branch0 = conns["Mark Topic Published"]["main"][0]
        branch0 = [e for e in branch0 if e["node"] != "Log Success"]
        branch0.append({"node": "Notify Slack Published", "type": "main", "index": 0})
        conns["Mark Topic Published"]["main"][0] = branch0

    # Notify Slack Published → Log Success
    conns["Notify Slack Published"] = {
        "main": [[{"node": "Log Success", "type": "main", "index": 0}]]
    }

    wf["connections"] = conns

    print(f"Total nodes after patch: {len(wf['nodes'])}")
    print("Uploading updated workflow...")
    result = n8n_put(f"/api/v1/workflows/{WF_ID}", wf, n8n_key)
    print(f"Done. Name={result.get('name')} Active={result.get('active')} Nodes={len(result.get('nodes',[]))}")


if __name__ == "__main__":
    main()
