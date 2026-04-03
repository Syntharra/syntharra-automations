#!/bin/bash
# Syntharra Session End Enforcer
# Usage: ./tools/claude-code/session-end.sh "topic-description"
TOPIC=${1:-"general"}
DATE=$(date -u '+%Y-%m-%d')
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
LOG_DIR="$REPO_ROOT/docs/session-logs"
LOG_FILE="$LOG_DIR/$DATE-$TOPIC.md"

echo "======================================"
echo "Syntharra Session End Checklist"
echo "$TIMESTAMP"
echo "======================================"

mkdir -p "$LOG_DIR"

if [ ! -f "$LOG_FILE" ]; then
cat > "$LOG_FILE" << TEMPLATE
# Session Log — $DATE — $TOPIC

## Summary


## Changes Made


## Decisions Made


## Test Results
- E2E Standard: [pass/fail/not run]
- E2E Premium: [pass/fail/not run]

## Open Items


## Next Session Priority

TEMPLATE
echo "Session log template created: $LOG_FILE"
echo "Fill in before pushing."
fi

echo ""
echo "Checklist:"
echo "  1. E2E tests passed or not required? [y/n]"
read -r C1
echo "  2. All changes pushed to GitHub? [y/n]"
read -r C2
echo "  3. TASKS.md updated? [y/n]"
read -r C3
echo "  4. FAILURES.md updated if anything broke? [y/n]"
read -r C4
echo "  5. ARCHITECTURE.md updated if architectural decision made? [y/n]"
read -r C5

if [[ "$C1" != "y" ]] || [[ "$C2" != "y" ]] || [[ "$C3" != "y" ]]; then
    echo "Checklist incomplete. Complete all items before closing."
    exit 1
fi

echo ""
echo "Push session log to GitHub? [y/n]"
read -r PUSH_LOG

if [[ "$PUSH_LOG" == "y" ]]; then
    TOKEN=${GITHUB_TOKEN:-""}
    if [ -z "$TOKEN" ]; then
        echo "GITHUB_TOKEN not set. Push manually:"
        echo "  git add $LOG_FILE && git commit -m 'docs: session log $DATE $TOPIC' && git push"
        exit 0
    fi
    python3 "$REPO_ROOT/tools/claude-code/push-log.py" "$LOG_FILE" "$DATE" "$TOPIC"
fi

# Send Slack notification if webhook is set
if [ -n "$SLACK_WEBHOOK_OPS" ]; then
    python3 "$REPO_ROOT/tools/claude-code/slack_notify.py" "#claude-code" ":memo:" "Session Complete — $TOPIC" "Date=$DATE" "Log=docs/session-logs/$DATE-$TOPIC.md"
fi
echo "Session closed. All good."
