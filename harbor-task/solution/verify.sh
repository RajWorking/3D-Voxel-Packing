#!/usr/bin/env bash
# Builds the task Docker image, runs solve.sh inside it, then runs the
# verifier and asserts score = 1.0000.
#
# Usage (from repo root):
#   bash harbor-task/solution/verify.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TASK_DIR="$REPO_ROOT/harbor-task"
IMAGE="harbor-task-verify"

echo "=== Building image ==="
docker build \
  -t "$IMAGE" \
  -f "$TASK_DIR/environment/Dockerfile" \
  "$TASK_DIR"

echo ""
echo "=== Running solve + verify ==="
docker run --rm \
  -v "$TASK_DIR/solution:/solution:ro" \
  -v "$TASK_DIR/tests:/tests:ro" \
  "$IMAGE" \
  bash -c "
    set -e
    bash /solution/solve.sh
    echo ''
    echo '=== Verifier output ==='
    python3 /tests/verifier.py /home/user/solution.json /task/objects.json
    echo ''
    echo '=== Score ==='
    cat /tmp/score.txt
    echo ''
    SCORE=\$(grep '^score=' /tmp/score.txt | cut -d= -f2)
    if [ \"\$SCORE\" = \"1.0000\" ]; then
      echo 'PASS: reward = 1'
    else
      echo \"FAIL: reward = \$SCORE (expected 1.0000)\"
      exit 1
    fi
  "
