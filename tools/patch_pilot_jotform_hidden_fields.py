#!/usr/bin/env python3
"""
patch_pilot_jotform_hidden_fields.py — One-shot recovery script.

Adds the 7 hidden tracking fields to a partially-created pilot Jotform when
build_pilot_jotform.py failed mid-run. Idempotent: skips fields that already
exist on the form.

Usage:
  source .env.local
  python tools/patch_pilot_jotform_hidden_fields.py <FORM_ID>
"""
import json
import os
import sys
import urllib.parse
import urllib.request

JOTFORM_API = "https://api.jotform.com"

HIDDEN_FIELDS = [
    "stx_asset_id",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "pilot_mode",
]


def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env: {k}")
    return v


def api(method, path, form_data=None):
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
    if len(sys.argv) != 2:
        sys.exit("Usage: patch_pilot_jotform_hidden_fields.py <FORM_ID>")
    form_id = sys.argv[1]

    existing = api("GET", f"/form/{form_id}/questions")["content"]
    existing_names = {q.get("name", "") for q in existing.values()}

    for offset, name in enumerate(HIDDEN_FIELDS):
        if name in existing_names:
            print(f"  skip (exists): {name}", file=sys.stderr)
            continue
        payload = {
            "question[type]": "control_textbox",
            "question[text]": name,
            "question[name]": name,
            "question[hidden]": "Yes",
            "question[order]": str(100 + offset),
        }
        if name == "pilot_mode":
            payload["question[defaultValue]"] = "true"
        result = api("POST", f"/form/{form_id}/questions", form_data=payload)
        new_qid = (result.get("content") or {}).get("qid", "?")
        print(f"  added: {name} (qid={new_qid})", file=sys.stderr)

    print("", file=sys.stderr)
    print("Final question list:", file=sys.stderr)
    final = api("GET", f"/form/{form_id}/questions")["content"]
    for qid, q in sorted(final.items(), key=lambda kv: int(kv[0])):
        print(f"  qid={qid:>3}  type={q.get('type','?'):<20}  name={q.get('name','')}", file=sys.stderr)


if __name__ == "__main__":
    main()
