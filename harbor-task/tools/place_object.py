#!/usr/bin/env python3
"""
Usage: python3 place_object.py <name> <perm> <signs> <ox> <oy> <oz>

Applies the transform to <name>, normalizes to origin, adds offset (ox,oy,oz),
checks for collisions, and if clear updates the workspace.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from common import (load_objects, load_workspace, save_workspace,
                    parse_perm, parse_signs, build_final_pts,
                    compute_bbox, all_placed_pts, print_placement_summary)


def main():
    if len(sys.argv) != 7:
        print("Usage: place_object.py <name> <perm> <signs> <ox> <oy> <oz>")
        sys.exit(1)

    name       = sys.argv[1]
    perm_str   = sys.argv[2]
    signs_str  = sys.argv[3]

    # Parse offsets
    try:
        ox, oy, oz = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    except ValueError:
        print(f"ERROR: ox/oy/oz must be integers, got: {sys.argv[4]} {sys.argv[5]} {sys.argv[6]}")
        sys.exit(1)
    if ox < 0 or oy < 0 or oz < 0:
        print(f"ERROR: offsets must be non-negative integers, got: ox={ox} oy={oy} oz={oz}")
        sys.exit(1)

    # Parse transform
    try:
        perm  = parse_perm(perm_str)
        signs = parse_signs(signs_str)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Load objects
    try:
        objects = load_objects()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if name not in objects:
        print(f"ERROR: object '{name}' not found in objects.json")
        print(f"Available: {', '.join(sorted(objects.keys()))}")
        sys.exit(1)

    # Load workspace
    ws = load_workspace()

    if name in ws["placed"]:
        print(f"ERROR: object '{name}' is already placed. Use remove_object.py first.")
        sys.exit(1)

    # Compute final positions
    final_pts = build_final_pts(objects[name], perm, signs, ox, oy, oz)

    # Build occupied set from all already-placed voxels
    occupied = {}  # (x,y,z) → object_name
    for placed_name, pts in ws["placed"].items():
        for p in pts:
            occupied[tuple(p)] = placed_name

    # Check collisions
    collisions = []
    for p in final_pts:
        key = tuple(p)
        if key in occupied:
            collisions.append((p, occupied[key]))

    if collisions:
        print(f"ERROR: collision placing '{name}'")
        shown = collisions[:5]
        for pt, other in shown:
            print(f"  collides with '{other}' at {pt}")
        if len(collisions) > 5:
            print(f"  ... and {len(collisions)-5} more collision(s)")
        print("Workspace not modified.")
        sys.exit(1)

    # No collision — update workspace
    ws["placed"][name] = final_pts
    ws["unplaced"] = [n for n in ws["unplaced"] if n != name]
    save_workspace(ws)

    # Report
    dims, vol = compute_bbox(all_placed_pts(ws))
    xs = [p[0] for p in final_pts]
    ys = [p[1] for p in final_pts]
    zs = [p[2] for p in final_pts]
    print(f"PLACED {name}")
    print(f"  Transform : perm={perm_str} signs={signs_str} offset=({ox},{oy},{oz})")
    print(f"  Voxels    : {len(final_pts)}")
    print(f"  Range     : x=[{min(xs)},{max(xs)}] y=[{min(ys)},{max(ys)}] z=[{min(zs)},{max(zs)}]")
    print(f"  Bounding box so far: {dims[0]} x {dims[1]} x {dims[2]} = {vol}")
    print_placement_summary(ws)


if __name__ == "__main__":
    main()
