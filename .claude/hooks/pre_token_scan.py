#!/usr/bin/env python3
"""
Hook: PreToolUse → bash
Scans bash commands for raw API token patterns before git push/commit.
Exit 2 = block. Exit 0 = allow.
"""
import sys, json, re

# Patterns that indicate a raw token is about to be committed
DANGEROUS_PATTERNS = [
    r"ghp_[A-Za-z0-9]{36}",          # GitHub PAT
    r"sk_live_[A-Za-z0-9]{24,}",     # Stripe live key
    r"sk_test_[A-Za-z0-9]{24,}",     # Stripe test key
    r"xoxb-[0-9]+-[A-Za-z0-9-]+",    # Slack bot token
    r"retellai_[A-Za-z0-9]{32,}",    # Retell key pattern
    r"key_[A-Za-z0-9]{20,}",         # Generic key pattern
]

GIT_WRITE_SIGNALS = ["git commit", "git push", "git add"]

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")

    # Only scan on git write operations
    is_git_write = any(sig in command for sig in GIT_WRITE_SIGNALS)
    if not is_git_write:
        sys.exit(0)

    for pattern in DANGEROUS_PATTERNS:
        match = re.search(pattern, command)
        if match:
            # Redact the match for safe display
            redacted = match.group()[:8] + "..." + match.group()[-4:]
            print(f"\n🚫 HOOK BLOCKED: Raw API token detected in git operation")
            print(f"   Pattern matched: {redacted}")
            print("   Store secrets in Supabase vault or Railway env vars only.")
            print("   Never commit tokens to GitHub.")
            sys.exit(2)

except Exception:
    sys.exit(0)

sys.exit(0)
