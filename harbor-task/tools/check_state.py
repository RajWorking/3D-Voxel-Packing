#!/usr/bin/env python3
"""
Usage: python3 check_state.py

Displays current workspace state: placed/unplaced objects and bounding box.
Read-only — never modifies workspace.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from common import load_workspace, all_placed_pts, compute_bbox


def main():
    ws   = load_workspace()
    pts  = all_placed_pts(ws)
    dims, vol = compute_bbox(pts)

    placed   = sorted(ws["placed"].keys())
    unplaced = sorted(ws["unplaced"])

    print("=== Workspace State ===")
    if pts:
        print(f"Bounding box   : {dims[0]} x {dims[1]} x {dims[2]} = {vol}")
        print(f"Total voxels   : {len(pts)}")
    else:
        print("Bounding box   : none (no objects placed yet)")
        print("Total voxels   : 0")
    print(f"Placed   ({len(placed):2d}) : {', '.join(placed) if placed else '—'}")
    print(f"Unplaced ({len(unplaced):2d}) : {', '.join(unplaced) if unplaced else '—'}")


if __name__ == "__main__":
    main()
