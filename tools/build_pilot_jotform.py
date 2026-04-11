#!/usr/bin/env python3
"""
build_pilot_jotform.py — Clone the existing HVAC Standard Jotform as the pilot fork.

Source form: 260795139953066 (HVAC Standard onboarding)

Target: a new form with:
  - All fields from source (clone preserves them)
  - Title changed to "Start your free 14-day Syntharra pilot"
  - 7 new hidden tracking fields: stx_asset_id, utm_source, utm_medium,
    utm_campaign, utm_content, utm_term, pilot_mode
  - Webhook stays pointed at the same n8n workflow path (n8n branches internally
    on the pilot_mode hidden field via the new "Is Pilot?" IF node added in Task 15)

Idempotent-ish: it clones every run, so it will create a new form each time.
The intent is one-shot — record the new form ID in docs/REFERENCE.md and
delete the script invocation history afterward.

Usage:
  source .env.local
  python tools/build_pilot_jotform.py

Output: prints the new form ID to stdout. Webhook config is reported but the
n8n webhook path is NOT modified — the clone inherits the source form's webhook
which already points to 4Hx7aRdzMl5N0uJP.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

SOURCE_FORM_ID = "260795139953066"
JOTFORM_API = "https://api.jotform.com"


def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}  (did you `source .env.local`?)")
    return v


def api(method, path, form_data=None):
    """Jotform REST: query string for GET, urlencoded body for POST/PUT."""
    api_key = env("JOTFORM_API_KEY")
    url = f"{JOTFORM_API}{path}?apiKey={api_key}"
    body = None
    headers = {}
    if form_data is not None:
        if method == "GET":
            url += "&" + urllib.parse.urlencode(form_data)
        else:
            body = urllib.parse.urlencode(form_data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", errors="replace")
        sys.exit(f"Jotform API {method} {path} → HTTP {e.code}: {body_txt}")


def main():
    # 1. Clone the source form
    print(f"Cloning Jotform {SOURCE_FORM_ID}...", file=sys.stderr)
    result = api("POST", f"/form/{SOURCE_FORM_ID}/clone")
    if result.get("responseCode") != 200:
        sys.exit(f"Unexpected clone response: {json.dumps(result)[:500]}")
    new_form_id = result["content"]["id"]
    print(f"  New form ID: {new_form_id}", file=sys.stderr)

    # 2. Update title
    api("POST", f"/form/{new_form_id}/properties", form_data={
        "properties[title]": "Start your free 14-day Syntharra pilot"
    })
    print("  Title updated.", file=sys.stderr)

    # 3. Add hidden tracking fields via POST /form/{id}/questions (plural).
    #    Jotform assigns the qid; we read it back from the response.
    hidden_fields = [
        "stx_asset_id",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "pilot_mode",
    ]
    for offset, name in enumerate(hidden_fields):
        # control_textbox with hidden=Yes is the standard pattern for tracking
        # params (control_hidden type is not always accepted by the public API).
        payload = {
            "question[type]": "control_textbox",
            "question[text]": name,
            "question[name]": name,
            "question[hidden]": "Yes",
            "question[order]": str(100 + offset),
        }
        if name == "pilot_mode":
            payload["question[defaultValue]"] = "true"
        result = api("POST", f"/form/{new_form_id}/questions", form_data=payload)
        new_qid = (result.get("content") or {}).get("qid", "?")
        print(f"  Added hidden field: {name} (qid={new_qid})", file=sys.stderr)

    # 4. Verify webhooks (clone inherits from source)
    webhooks = api("GET", f"/form/{new_form_id}/webhooks")
    print(f"  Webhooks: {json.dumps(webhooks.get('content', {}))}", file=sys.stderr)

    print("", file=sys.stderr)
    print(f"=== Pilot form created: {new_form_id} ===", file=sys.stderr)
    print(f"URL: https://form.jotform.com/{new_form_id}", file=sys.stderr)
    print("Add to docs/REFERENCE.md under the Jotform section.", file=sys.stderr)

    # The new form ID goes to stdout for shell capture: ID=$(python tools/...)
    print(new_form_id)


if __name__ == "__main__":
    main()
