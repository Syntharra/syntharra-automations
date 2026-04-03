#!/bin/bash
# Syntharra E2E Test Runner — TESTING agents only
# Usage: ./tools/claude-code/run-e2e.sh [standard|premium]
TIER=${1:-standard}
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

echo "======================================"
echo "Syntharra E2E — Tier: $TIER"
echo "$(date -u '+%Y-%m-%d %H:%M UTC')"
echo "======================================"

if [ "$TIER" = "standard" ]; then
    SCRIPT="$REPO_ROOT/shared/e2e-test.py"
elif [ "$TIER" = "premium" ]; then
    SCRIPT="$REPO_ROOT/shared/e2e-test-premium.py"
else
    echo "ERROR: tier must be standard or premium"
    exit 1
fi

if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: script not found: $SCRIPT"
    exit 1
fi

python3 "$SCRIPT"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "PASS — safe to push to production"
else
    echo "FAIL — do NOT push to production"
fi
exit $EXIT_CODE
