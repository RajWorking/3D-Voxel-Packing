#!/usr/bin/env bash
# Harbor test script for 3D Voxel Bin-Packing task.
# Exits 0 (pass) if the agent's solution is a valid packing, 1 (fail) otherwise.

set -euo pipefail

SOLUTION="/home/user/solution.json"
OBJECTS="/task/objects.json"
VERIFIER="/tests/verifier.py"
REWARD="/logs/verifier/reward.txt"

# Check that the agent produced a solution file
if [[ ! -f "$SOLUTION" ]]; then
    echo "[FAIL] No solution file found at $SOLUTION"
    echo "0.0" > "$REWARD"
    exit 1
fi

# Run the verifier (writes score details to /tmp/score.txt)
python3 "$VERIFIER" "$SOLUTION" "$OBJECTS"
EXIT_CODE=$?

# Extract the float score and write to harbor's expected reward path
SCORE=$(grep '^score=' /tmp/score.txt | cut -d= -f2)
echo "${SCORE:-0.0}" > "$REWARD"

exit $EXIT_CODE
