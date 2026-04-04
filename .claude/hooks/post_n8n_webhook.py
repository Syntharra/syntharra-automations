#!/usr/bin/env python3
"""
Hook: PostToolUse → bash (runs AFTER — catches violations in output for awareness)
Actually implemented as PreToolUse to BLOCK before execution.
Blocks any bash command that POSTs to an n8n webhook URL (health checks must be HEAD).
Exit 2 = block. Exit 0 = allow.
"""
import sys, json, re

N8N_WEBHOOK_PATTERN = r"n8n\.syntharra\.com/webhook"
POST_SIGNALS = [
    "requests.post(", 
    'method.*POST',
    "curl.*-X POST",
    "curl.*--data",
    "-d '",
    '--data-raw',
]

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")

    if re.search(N8N_WEBHOOK_PATTERN, command):
        for signal in POST_SIGNALS:
            if re.search(signal, command):
                print(f"\n🚫 HOOK BLOCKED: POST to n8n webhook detected")
                print("   Health checks MUST use HEAD requests only.")
                print("   POSTing to production webhooks triggers live workflows.")
                print("   Use: requests.head(url) or curl -X HEAD <url>")
                sys.exit(2)

except Exception:
    sys.exit(0)

sys.exit(0)
