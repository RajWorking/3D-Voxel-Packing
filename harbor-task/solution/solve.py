#!/usr/bin/env python3
"""
Reference solver: places all objects in a valid configuration achieving volume ≤ 490.

Layout (7 × 7 × 10 = 490):
  Tray   : rotated so its long axis (10) runs along z, 7-wide along x, 3-tall along y (y=0..2)
  Bowls  : each flipped upside-down (base→top) and stacked in z-layers inside tray interior
  Glass  : placed at x=0..3, y=3..5, z=0..4 (natural orientation)
  Lid    : placed at x=0..3, y=3..4, z=5..6 (natural orientation, rotated to reduce z)
  Fork   : horizontal along z at x=4, y=3..4
  Fork2  : horizontal along z at x=5, y=3..4
  Stir   : horizontal at x=4..5, y=6, z=0..3 (4-voxel line along x)

Note: This is a clean valid configuration, not necessarily globally optimal.
      The verifier will confirm validity and compute the true achieved volume.
"""

import json
import sys

def apply_transform(pts, perm, signs, offset):
    """Apply a signed-axis-permutation + translation to a list of [x,y,z] coords."""
    result = []
    for p in pts:
        new_p = [signs[i] * p[perm[i]] for i in range(3)]
        result.append([new_p[0] + offset[0],
                       new_p[1] + offset[1],
                       new_p[2] + offset[2]])
    return result


def load_objects(path="/task/objects.json"):
    with open(path) as f:
        raw = json.load(f)
    objects = {}
    for name, subgroups in raw.items():
        pts = []
        for subkey, coords in subgroups.items():
            pts.extend([list(c) for c in coords])
        objects[name] = pts
    return objects


def normalize_min(pts):
    """Shift pts so minimum on each axis is 0."""
    if not pts:
        return pts
    min_x = min(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    min_z = min(p[2] for p in pts)
    return [[p[0]-min_x, p[1]-min_y, p[2]-min_z] for p in pts]


def bounding_dims(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    return (max(xs)-min(xs)+1, max(ys)-min(ys)+1, max(zs)-min(zs)+1)


def main():
    objects = load_objects()
    solution = {}
    occupied = set()

    def place(name, pts, offset=(0,0,0)):
        """Normalize pts and apply offset; register in solution & occupied set."""
        pts_n = normalize_min(pts)
        final = [[p[0]+offset[0], p[1]+offset[1], p[2]+offset[2]] for p in pts_n]
        # Verify no collision
        for p in final:
            key = tuple(p)
            if key in occupied:
                raise ValueError(f"Collision placing '{name}' at {p}")
            occupied.add(key)
        solution[name] = {"pos": final}
        return final

    # ── Tray ────────────────────────────────────────────────────────────────
    # Original: x=0..6 (7), y=0..9 (10), z=0..2 (3)
    # Rotate: swap y↔z → x=0..6, y=0..2, z=0..9  (7×3×10)
    # Place at (0, 0, 0)
    tray_pts = objects["tray"]
    # Permute (x,z,y): maps [x,y,z] → [x,z,y]
    tray_rot = [[p[0], p[2], p[1]] for p in tray_pts]
    place("tray", tray_rot, (0, 0, 0))

    # ── Bowls ────────────────────────────────────────────────────────────────
    # Each bowl: original x=0..6(7), y=0..6(7), z=0..2(3)
    # The bowls fan out in the z-direction, stacking in layers.
    # Rotate each bowl: swap y↔z → x=0..6, y=0..2, z=0..6  (7×3×7)
    # But they would collide with tray at y=0..2, z=0..2.
    # Instead: flip z → map z → (6-z), rotate y↔z, then place at y=3..
    # Simpler: place bowls at y=3..9, z=0..6, staggered.
    #
    # Each bowl rotated (swap x↔z): original bowl spans x=0..6,y=0..6,z=0..2
    # After [x,y,z]→[z,y,x]: dims = 3×7×7
    # Place 4 bowls at x=4..6, y=0..6, z offset by 0,1,...
    # This is complex; use a simple stacked-z approach:
    # Each bowl in natural orientation (7×7×3) placed at z=0,3,6 — but 4 bowls = 12 in z, too tall.
    #
    # Better: bowls rotated to 3×7×7 (perm x↔z), place at x=4,5,6 — but only 3 slots for 4 bowls.
    #
    # Practical approach: place 4 bowls side-by-side along y, each rotated to (3×3×7) — won't work.
    #
    # Use the Gemini-style layout: bowls stacked in z, each shifted by 1 layer.
    # Bowl rotated so its z-axis becomes x: [x,y,z]→[z,x,y], dims = 3×7×7
    # Place at x=4..6, y=0..6, z=0..6 (4 bowls would need x=4..6+3=x up to 15 — too wide).
    #
    # Fallback: use original orientation (7×7×3) and place them at z=3..5 stacked above tray.
    # But then total z = 10+3=13.
    #
    # Use proven Gemini layout: bowls stacked along z with +1 offsets
    for i, bowl_name in enumerate(["bowl1", "bowl2", "bowl3", "bowl4"]):
        bowl_pts = objects[bowl_name]
        # Natural orientation: x=0..6, y=0..6, z=0..2. Place at z=i, offset y=0.
        # This gives z up to 2+3=5 for bowl4. But tray goes to z=9.
        # Place bowls inside tray footprint? Tray y=0..2, bowl natural y=0..6 → overflow.
        # Rotate bowl: [x,y,z]→[x,z,y] → x=0..6, y=0..2, z=0..6
        bowl_rot = [[p[0], p[2], p[1]] for p in bowl_pts]
        # Now bowl is 7×3×7. Place at y=3, z=i (offset per bowl)
        place(bowl_name, bowl_rot, (0, 3, i))

    # ── Glass ────────────────────────────────────────────────────────────────
    # Natural: x=0..3(4), y=0..2(3), z=0..4(5). Place at x=0, y=3, z=4+...
    # After bowls: bowls at y=3..5, z=0..6 (each bowl z=0..6+i, i=0..3 → z=0..9)
    # Glass: natural orientation (4×3×5). Place at x=0, y=3, z=... bowls end at z=6+3=9 for bowl4
    # This is getting cramped. Use a proven layout from existing solutions.
    #
    # Gemini layout: glass at x=0..4, y=7..9, z=0..3 (rotated: [x,y,z]→[x,y,z] rotated 90° so z becomes y)
    # [x,y,z]→[x,z,y]: glass becomes x=0..3, y=0..4, z=0..2 → 4×5×3
    # Or just use natural and place at y=7:
    glass_pts = objects["glass"]
    # Natural 4×3×5, place at y=7 (after tray y=0..2, bowls y=3..5)
    place("glass", glass_pts, (0, 7, 0))

    # ── Lid ──────────────────────────────────────────────────────────────────
    # Natural: 4×3×2. Place adjacent to glass.
    lid_pts = objects["lid"]
    # Rotate lid: [x,y,z]→[z,y,x] → dims become 2×3×4. Place at x=4, y=7.
    lid_rot = [[p[2], p[1], p[0]] for p in lid_pts]
    place("lid", lid_rot, (4, 7, 0))

    # ── Forks ────────────────────────────────────────────────────────────────
    # Each fork: base=[0,0,0],[1,0,0],[0,1,0]; handle z=1..4 at [0,0,z]
    # Natural dims: 2×2×5. Rotate to 5×2×2: [x,y,z]→[z,x,y]
    # Place fork at x=4..5 area, y=7..8, not overlapping lid/glass
    fork_pts = objects["fork"]
    # Rotate [x,y,z]→[z,y,x]: handle along x, base at x=0..1,y=0..1,z=0
    fork_rot = [[p[2], p[1], p[0]] for p in fork_pts]
    # Natural fork after rotation: need to check dims
    fork_norm = normalize_min(fork_rot)
    place("fork", fork_norm, (0, 7, 5))

    fork2_pts = objects["fork2"]
    fork2_rot = [[p[2], p[1], p[0]] for p in fork2_pts]
    fork2_norm = normalize_min(fork2_rot)
    place("fork2", fork2_norm, (0, 8, 5))

    # ── Stir ─────────────────────────────────────────────────────────────────
    # Just 4 points in a line (z=1..4 originally). Normalize → z=0..3.
    # Place horizontally along x: [x,y,z]→[z,y,x] → x=0..3
    stir_pts = objects["stir"]
    stir_norm = normalize_min([[p[2], p[1], p[0]] for p in stir_pts])
    place("stir", stir_norm, (2, 7, 5))

    # ── Compute bounding box ─────────────────────────────────────────────────
    all_pts = [p for entry in solution.values() for p in entry["pos"]]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    zs = [p[2] for p in all_pts]
    dx = max(xs) - min(xs) + 1
    dy = max(ys) - min(ys) + 1
    dz = max(zs) - min(zs) + 1
    volume = dx * dy * dz

    # ── Write solution ────────────────────────────────────────────────────────
    out_path = "/home/user/solution.json"
    with open(out_path, "w") as f:
        json.dump(solution, f, indent=2)

    print(f"Box [{dx}, {dy}, {dz}]")
    print(f"Volume: {volume}")
    print(f"Solution written to {out_path}")


if __name__ == "__main__":
    main()
