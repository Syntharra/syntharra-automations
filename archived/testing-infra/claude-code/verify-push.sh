#!/bin/bash
# Verify a GitHub push actually landed
# Usage: ./tools/claude-code/verify-push.sh <repo> <file-path>
REPO=${1:-"syntharra-automations"}
FILE=${2:-"CLAUDE.md"}
TOKEN=${GITHUB_TOKEN:-""}

if [ -z "$TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

python3 - <<PYEOF
import requests, base64, os, sys
TOKEN = "${TOKEN}"
H = {"Authorization": f"token {TOKEN}"}
r = requests.get(f"https://api.github.com/repos/Syntharra/${REPO}/contents/${FILE}", headers=H).json()
if "sha" in r:
    content = base64.b64decode(r["content"]).decode()
    print(f"OK: {r['sha'][:12]} | {len(content)} chars")
else:
    print(f"FAIL: {r.get('message', 'unknown')}")
    sys.exit(1)
PYEOF
