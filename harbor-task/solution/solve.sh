#!/usr/bin/env bash
# Reference solver for the 3D Voxel Bin-Packing task.
# Uses the workspace tools in /task/tools/ to place objects and finalize.
#
# Objects (from /task/objects.json):
#   bowl1..5      — identical hollow bowl rings, 12 × 4 × 6 each (normalized)
#   ball          — sphere-like shape,           8 × 6 × 6       (hollow at z=2,3 center)
#   donut1        — flat ring,                   8 × 4 × 1
#   donut2        — flat ring,                   6 × 4 × 1
#   chocolate     — solid flat rectangle,        6 × 4 × 1
#   match_box1..4 — identical solid boxes,       3 × 2 × 3 each
#
# Reference volume: 24 × 8 × 6 = 1152
#
# Tool usage:
#   python3 /task/tools/place_object.py <name> <perm> <signs> <ox> <oy> <oz>
#   python3 /task/tools/inspect_object.py <name> [perm signs]
#   python3 /task/tools/check_state.py
#   python3 /task/tools/remove_object.py <name>
#   python3 /task/tools/finalize.py
#
# Transform format:
#   perm  — axis permutation, e.g. "xyz" (identity), "xzy" (swap y/z), "zyx" (swap x/z)
#   signs — flip per axis,    e.g. "+++" (none),    "++-" (flip z),   "-++" (flip x)

set -euo pipefail

place() { python3 /task/tools/place_object.py "$@"; }

python3 /task/tools/check_state.py
echo

# ── Ball ──────────────────────────────────────────────────────────────────────
place ball  xyz +++ 2 0 0

# ── Bowls (12 × 4 × 6 each) ───────────────────────────────────────────────────
place bowl1 xyz +++ 1 5 0
place bowl2 xyz +++ 1 7 0
place bowl3 yxz +++ 10 0 0
place bowl4 yxz +++ 12 0 0
place bowl5 yxz -++ 0 0 0

# ── Flat objects ──────────────────────────────────────────────────────────────
place donut1    zxy +++ 16 2 0
place donut2    yzx +++ 5 9 0
place chocolate xzy +++ 4 11 0

# ── Match boxes (3 × 2 × 3 each) ──────────────────────────────────────────────
place match_box1 xyz +++ 14 0 0
place match_box2 xyz +++ 14 10 0
place match_box3 xyz +++ 14 0 3
place match_box4 xyz +++ 14 10 3

echo
python3 /task/tools/finalize.py
