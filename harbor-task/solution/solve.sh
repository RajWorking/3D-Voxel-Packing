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

# ── Bowls (12 × 4 × 6 each) ───────────────────────────────────────────────────
# 5 identical bowls — key challenge. Use inspect_object.py to find orientations
# that allow tight packing (e.g. rotate to 6×4×12 via perm="zyx" to stack along x).
place bowl1 xyz +++ 0 0 0    # natural orientation
place ball  xyz +++ 0 1 0    # between bowl1 (y=0..4) and bowl2 (y=6..)
place bowl2 xyz +-+ 0 6 0    # y-flipped, beside bowl1 in y

place bowl3 xyz +++ 12 0 0   # separate stack
place bowl4 xyz +++ 12 2 0   # on top of bowl3 along y
place bowl5 xyz +++ 12 4 0   # on top of bowl4 along y

# ── Flat objects (donut1: 8×4×1, donut2: 6×4×1, chocolate: 6×4×1) ────────────
# All 1-unit thick — can fill gaps on top of or beside the bowls.
place donut1    xyz +++ 0 0 0   # TODO: pick best orientation and offset
place donut2    xyz +++ 0 0 0   # TODO: pick best orientation and offset
place chocolate xyz +++ 0 0 0   # TODO: pick best orientation and offset

# ── Match boxes (3 × 2 × 3 each) ──────────────────────────────────────────────
# Small — good gap fillers. Can be rotated to 2×3×3 or 3×3×2 etc.
place match_box1 xyz +++ 0 0 0  # TODO: pick best orientation and offset
place match_box2 xyz +++ 0 0 0  # TODO: pick best orientation and offset
place match_box3 xyz +++ 0 0 0  # TODO: pick best orientation and offset
place match_box4 xyz +++ 0 0 0  # TODO: pick best orientation and offset

echo
python3 /task/tools/finalize.py
