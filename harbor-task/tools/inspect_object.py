#!/usr/bin/env python3
"""
Usage:
  python3 inspect_object.py <name>
  python3 inspect_object.py <name> <perm> <signs>

Without transform: shows canonical (normalized) voxels and bounding box.
With transform: shows post-transform voxels (normalized, before offset).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from common import (load_objects, parse_perm, parse_signs,
                    apply_transform, normalize_to_origin, compute_bbox)


def main():
    if len(sys.argv) not in (2, 4):
        print("Usage: inspect_object.py <name> [<perm> <signs>]")
        sys.exit(1)

    name = sys.argv[1]

    try:
        objects = load_objects()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if name not in objects:
        print(f"ERROR: object '{name}' not found in objects.json")
        print(f"Available: {', '.join(sorted(objects.keys()))}")
        sys.exit(1)

    pts = objects[name]

    if len(sys.argv) == 4:
        try:
            perm  = parse_perm(sys.argv[2])
            signs = parse_signs(sys.argv[3])
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        transformed = apply_transform(pts, perm, signs)
        normalized  = normalize_to_origin(transformed)
        label = f"perm={sys.argv[2]} signs={sys.argv[3]}"
        note  = "NOTE: normalized to origin — add (ox,oy,oz) when calling place_object.py"
    else:
        normalized = normalize_to_origin(pts)
        label = "canonical"
        note  = "NOTE: identity transform — add (ox,oy,oz) when calling place_object.py"

    dims, _ = compute_bbox(normalized)
    sorted_pts = sorted(map(tuple, normalized))

    print(f"=== {name} ({label}) ===")
    print(f"Voxels ({len(normalized)}):")
    # Print in rows of 8 for readability
    for i in range(0, len(sorted_pts), 8):
        row = sorted_pts[i:i+8]
        print("  " + "  ".join(f"[{p[0]},{p[1]},{p[2]}]" for p in row))
    print(f"Bounding box: {dims[0]} x {dims[1]} x {dims[2]}")
    print(note)


if __name__ == "__main__":
    main()
