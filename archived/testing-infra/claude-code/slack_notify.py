#!/usr/bin/env python3
"""
Syntharra — Slack notification helper for Claude Code sessions.
Usage: python3 tools/claude-code/slack_notify.py <channel> <emoji> <title> [key=value ...]
Example: python3 tools/claude-code/slack_notify.py '#claude-code' ':white_check_mark:' 'E2E Passed' 'Tier=Standard' 'Score=75/75'
"""
import os, sys, requests, json
from datetime import datetime, timezone

WEBHOOK = os.environ.get("SLACK_WEBHOOK_OPS", "")

def slack_send(channel, emoji, title, fields=None, text=None):
    if not WEBHOOK:
        print(f"[SLACK SKIP — no SLACK_WEBHOOK_OPS] {title}")
        return True  # don't fail if webhook not set

    blocks = [{"type": "header", "text": {"type": "plain_text", "text": title}}]

    if text:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})

    if fields:
        blocks.append({"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*{k}:*\n{v}"} for k, v in fields.items()
        ]})

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": ts}]})

    payload = {
        "channel": channel,
        "username": "Syntharra Ops",
        "icon_emoji": emoji,
        "blocks": blocks
    }

    r = requests.post(WEBHOOK, json=payload, timeout=10)
    if r.status_code == 200:
        print(f"[SLACK OK] {channel} — {title}")
        return True
    else:
        print(f"[SLACK FAIL] {r.status_code} — {r.text}")
        return False

def notify_e2e(tier, passed, failed, duration_s):
    emoji = ":white_check_mark:" if failed == 0 else ":x:"
    result = "PASSED" if failed == 0 else "FAILED"
    title = f"E2E {tier.title()} — {passed}/{passed+failed} {result}"
    slack_send("#claude-code", emoji, title, fields={
        "Passed": str(passed),
        "Failed": str(failed),
        "Duration": f"{duration_s}s",
        "Agent": "TESTING"
    })

def notify_session_start(topic):
    slack_send("#claude-code", ":rocket:", f"Session Started — {topic}",
               text="Claude Code session initialised. Context loaded.")

def notify_session_end(topic, changes, e2e_result="not run"):
    slack_send("#claude-code", ":memo:", f"Session Complete — {topic}", fields={
        "Changes": changes,
        "E2E": e2e_result,
        "Log": f"docs/session-logs/{datetime.now().strftime('%Y-%m-%d')}-{topic}.md"
    })

def notify_self_heal(tier, iteration, status):
    emoji = ":wrench:" if status == "fixing" else (":white_check_mark:" if status == "fixed" else ":warning:")
    title = f"Self-Heal {tier.title()} — Iter {iteration} — {status.upper()}"
    slack_send("#claude-code", emoji, title)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: slack_notify.py <channel> <emoji> <title> [Key=Value ...]")
        sys.exit(1)

    channel = sys.argv[1]
    emoji = sys.argv[2]
    title = sys.argv[3]
    fields = {}
    for arg in sys.argv[4:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            fields[k] = v

    slack_send(channel, emoji, title, fields=fields if fields else None)
