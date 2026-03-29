#!/usr/bin/env python3
"""
Verifier for the 3D Voxel Bin-Packing task.

Usage:
    python3 verifier.py <solution.json> <objects.json>

Exit codes:
    0  — valid packing (pass)
    1  — invalid packing (fail)
    2  — parse / format error

Writes a score line to /tmp/score.txt:
    score=<float>   (reference_volume / achieved_volume, capped at 1.0)
    volume=<int>
    valid=<true|false>
"""

import json
import sys
from itertools import permutations, product

DEFAULT_REFERENCE_VOLUME = 17 * 12 * 6  # overridden by task.toml [scoring].reference_volume


def load_reference_volume(task_toml_path="/task/task.toml"):
    """Read reference_volume from task.toml if available, else use default."""
    try:
        with open(task_toml_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("reference_volume"):
                    return int(line.split("=")[1].strip())
    except (FileNotFoundError, ValueError, IndexError):
        pass
    return DEFAULT_REFERENCE_VOLUME


# ──────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ──────────────────────────────────────────────────────────────────────────────

def normalize(pts):
    """Translate a point set so its minimum coordinate on each axis is 0."""
    if not pts:
        return []
    min_x = min(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    min_z = min(p[2] for p in pts)
    return tuple(sorted((p[0]-min_x, p[1]-min_y, p[2]-min_z) for p in pts))


def all_48_transforms(pts):
    """
    Generate all 48 orientations of a point set (the hyperoctahedral group):
    6 axis permutations × 8 sign combinations, each normalized to origin.
    """
    seen = set()
    for perm in permutations([0, 1, 2]):
        for signs in product((-1, 1), repeat=3):
            transformed = [(signs[0]*p[perm[0]],
                            signs[1]*p[perm[1]],
                            signs[2]*p[perm[2]]) for p in pts]
            key = normalize(transformed)
            seen.add(key)
    return seen


def is_valid_transform(original_pts, solution_pts):
    """
    Return True if solution_pts is a valid rigid transformation of original_pts.
    Checks all 48 cube symmetries.
    """
    if len(original_pts) != len(solution_pts):
        return False
    orig_canonical = normalize(original_pts)
    sol_canonical  = normalize(solution_pts)
    return sol_canonical in all_48_transforms(list(orig_canonical))


# ──────────────────────────────────────────────────────────────────────────────
# Object loading
# ──────────────────────────────────────────────────────────────────────────────

def load_objects(path):
    """Load objects.json → {name: [list of (x,y,z) tuples]}."""
    with open(path) as f:
        raw = json.load(f)
    objects = {}
    for name, subgroups in raw.items():
        pts = []
        for coords in subgroups.values():
            for c in coords:
                pts.append(tuple(c))
        objects[name] = pts
    return objects


def load_solution(path):
    """Load solution.json → {name: [list of (x,y,z) tuples]}."""
    with open(path) as f:
        raw = json.load(f)
    solution = {}
    for name, entry in raw.items():
        if "pos" not in entry:
            raise ValueError(f"Object '{name}' missing 'pos' key in solution.")
        solution[name] = [tuple(c) for c in entry["pos"]]
    return solution


# ──────────────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────────────

def validate(objects, solution):
    errors = []

    # 1. All objects present
    missing = set(objects.keys()) - set(solution.keys())
    extra   = set(solution.keys()) - set(objects.keys())
    if missing:
        errors.append(f"Missing objects: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected objects: {sorted(extra)}")

    # 2. Per-object checks
    for name, orig_pts in objects.items():
        if name not in solution:
            continue
        sol_pts = solution[name]

        # 2a. Point count
        if len(sol_pts) != len(orig_pts):
            errors.append(
                f"'{name}': wrong voxel count — expected {len(orig_pts)}, got {len(sol_pts)}"
            )
            continue

        # 2b. No internal duplicates
        if len(set(sol_pts)) != len(sol_pts):
            errors.append(f"'{name}': contains duplicate voxels.")
            continue

        # 2c. Non-negative coordinates
        neg = [p for p in sol_pts if any(c < 0 for c in p)]
        if neg:
            errors.append(f"'{name}': {len(neg)} voxel(s) have negative coordinates.")

        # 2d. Valid rigid transform
        if not is_valid_transform(orig_pts, sol_pts):
            errors.append(
                f"'{name}': point set is not a valid rigid transformation of the original. "
                f"The shape was deformed or a non-90°/non-axis-aligned rotation was applied."
            )

    # 3. No inter-object overlaps
    all_points = {}
    for name, pts in solution.items():
        for p in pts:
            if p in all_points:
                errors.append(
                    f"Overlap at {p}: objects '{all_points[p]}' and '{name}' share a voxel."
                )
            else:
                all_points[p] = name

    return errors


# ──────────────────────────────────────────────────────────────────────────────
# Bounding box
# ──────────────────────────────────────────────────────────────────────────────

def bounding_box(solution):
    all_pts = [p for pts in solution.values() for p in pts]
    if not all_pts:
        return (0, 0, 0), 0
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    zs = [p[2] for p in all_pts]
    dx = max(xs) - min(xs) + 1
    dy = max(ys) - min(ys) + 1
    dz = max(zs) - min(zs) + 1
    return (dx, dy, dz), dx * dy * dz


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def write_score(valid, volume, score):
    with open("/tmp/score.txt", "w") as f:
        f.write(f"valid={str(valid).lower()}\n")
        f.write(f"volume={volume}\n")
        f.write(f"score={score:.4f}\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: verifier.py <solution.json> <objects.json>", file=sys.stderr)
        sys.exit(2)

    solution_path = sys.argv[1]
    objects_path  = sys.argv[2]

    # Load files
    try:
        objects  = load_objects(objects_path)
        solution = load_solution(solution_path)
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}", file=sys.stderr)
        write_score(False, 0, 0.0)
        sys.exit(2)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[ERROR] Parse error: {e}", file=sys.stderr)
        write_score(False, 0, 0.0)
        sys.exit(2)

    reference_volume = load_reference_volume()

    # Validate
    errors = validate(objects, solution)

    # Bounding box
    dims, volume = bounding_box(solution)
    score = min(1.0, reference_volume / volume) if volume > 0 else 0.0
    total_voxels = sum(len(pts) for pts in objects.values())

    # Report
    print("=" * 60)
    print(f"Bounding box : {dims[0]} × {dims[1]} × {dims[2]}")
    print(f"Volume       : {volume}")
    print(f"Score        : {score:.4f}  (reference={reference_volume})")
    print(f"Total voxels : {total_voxels}")
    print("=" * 60)

    if errors:
        print(f"\n[FAIL] {len(errors)} error(s) found:\n")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        write_score(False, volume, 0.0)
        sys.exit(1)
    else:
        print("\n[PASS] Solution is valid.")
        print(f"       Voxel efficiency: {total_voxels}/{volume} = {total_voxels/volume:.3f}")
        write_score(True, volume, score)
        sys.exit(0)


if __name__ == "__main__":
    main()
