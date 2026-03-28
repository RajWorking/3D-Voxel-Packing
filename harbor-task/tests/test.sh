#!/usr/bin/env bash
# Harbor test script for 3D Voxel Bin-Packing task.
# Exits 0 (pass) if the agent's solution is a valid packing, 1 (fail) otherwise.

set -euo pipefail

SOLUTION="/home/user/solution.json"
OBJECTS="/task/objects.json"
VERIFIER="/task/tests/verifier.py"

# Check that the agent produced a solution file
if [[ ! -f "$SOLUTION" ]]; then
    echo "[FAIL] No solution file found at $SOLUTION"
    echo "valid=false" > /tmp/score.txt
    echo "volume=0"    >> /tmp/score.txt
    echo "score=0.0"   >> /tmp/score.txt
    exit 1
fi

# Run the verifier and capture its exit code
python3 "$VERIFIER" "$SOLUTION" "$OBJECTS"
EXIT_CODE=$?

# Forward verifier exit code to Harbor
exit $EXIT_CODE
