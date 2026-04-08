#!/bin/bash
# Syntharra Self-Healing Loop — TESTING agent only, max 10 iterations
# Usage: ./tools/claude-code/self-heal.sh [standard|premium]
TIER=${1:-standard}
MAX_ITER=10
ITER=0
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

echo "======================================"
echo "Syntharra Self-Heal — Tier: $TIER"
echo "Max iterations: $MAX_ITER — TESTING only"
echo "======================================"

while [ $ITER -lt $MAX_ITER ]; do
    ITER=$((ITER + 1))
    echo "--- Iteration $ITER / $MAX_ITER ---"

    if bash "$REPO_ROOT/tools/claude-code/run-e2e.sh" "$TIER"; then
        echo "PASS after $ITER iteration(s). Self-heal complete."
        exit 0
    fi

    echo "Tests failing. Running self-healing-loop.py..."
    if [ -f "$REPO_ROOT/tools/self-healing-loop.py" ]; then
        python3 "$REPO_ROOT/tools/self-healing-loop.py" --tier "$TIER" --iteration "$ITER"
    else
        echo "ERROR: self-healing-loop.py not found"
        exit 1
    fi
done

echo "STOPPED: $MAX_ITER iterations reached without full pass."
echo "Manual review required. Do NOT push to production. Report to Dan."
exit 1
