#!/usr/bin/env python3
"""
Usage: python3 finalize.py

Writes /home/user/solution.json from current workspace state.
Requires all objects to be placed.
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))
from common import load_workspace, all_placed_pts, compute_bbox

SOLUTION_PATH = "/home/user/solution.json"


def main():
    ws = load_workspace()

    if ws["unplaced"]:
        print(f"ERROR: cannot finalize — {len(ws['unplaced'])} object(s) still unplaced:")
        print(f"  {', '.join(sorted(ws['unplaced']))}")
        print("Place all objects before calling finalize.py.")
        sys.exit(1)

    # Build solution in verifier-expected format
    solution = {name: {"pos": pts} for name, pts in ws["placed"].items()}

    with open(SOLUTION_PATH, "w") as f:
        json.dump(solution, f, indent=2)

    pts = all_placed_pts(ws)
    dims, vol = compute_bbox(pts)

    print("=== Finalized Solution ===")
    print(f"All {len(ws['placed'])} objects placed.")
    print(f"Bounding box: {dims[0]} x {dims[1]} x {dims[2]}")
    print(f"Volume: {vol}")
    print(f"Total voxels: {len(pts)}")
    print(f"Solution written to {SOLUTION_PATH}")
    print()
    print(f"Box [{dims[0]}, {dims[1]}, {dims[2]}]")
    print(f"Volume: {vol}")


if __name__ == "__main__":
    main()
