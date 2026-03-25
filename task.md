# 3D Voxel Bin-Packing: Minimum Bounding Box

## Task Description

You are given a set of rigid 3D objects, each represented as a collection of integer-coordinate voxels (unit cubes at lattice points). Your goal is to pack all objects together so that the axis-aligned bounding box enclosing all voxels has the **minimum possible volume**.

### Objects

The objects are defined in `objects.json`. Each object is a named dictionary whose values are lists of `[x, y, z]` integer coordinates:

```json
{
  "tray": {
    "base_z0": [[0,0,0], [1,0,0], ...],
    "rim_z1":  [[0,0,1], ...],
    "rim_z2":  [[0,0,2], ...]
  },
  "bowl1": { ... },
  ...
}
```

The sub-keys (`base_z0`, `rim_z1`, etc.) are semantic labels only — they describe the original orientation. When you output your solution, you must merge all sub-parts into a single flat list of coordinates per object.

### Allowed Operations

For each object you may apply **any combination** of:

| Operation | Detail |
|-----------|--------|
| **Rotation** | 90° increments around any axis (x, y, z) |
| **Reflection** | Flip along any axis |
| **Translation** | Shift to any integer position |

These are equivalent to the 48 symmetries of a cube (the hyperoctahedral group): all signed axis permutations. The relative distances between an object's voxels must be preserved exactly — no stretching, shearing, or deformation.

### Constraints

1. **No deformation**: The transformed point set for each object must be congruent to its original point set under a rigid voxel transformation.
2. **No overlap**: No two objects (from different named entries) may share any `[x, y, z]` coordinate.
3. **No self-overlap**: The voxels within a single transformed object must remain distinct (they already are, but translations must not create internal collisions).
4. **Integer coordinates only**: All output coordinates must be non-negative integers.

### Objective

Minimize the volume of the axis-aligned bounding box:

```
Volume = (max_x - min_x + 1) × (max_y - min_y + 1) × (max_z - min_z + 1)
```

where `min_x`, `max_x`, etc. are taken over **all voxels of all objects combined**.

### Output Format

Write your solution as a JSON file at `/home/user/solution.json`:

```json
{
    "tray": {
        "pos": [[x1,y1,z1], [x2,y2,z2], ...]
    },
    "bowl1": {
        "pos": [[x1,y1,z1], ...]
    },
    "bowl2": { "pos": [...] },
    "bowl3": { "pos": [...] },
    "bowl4": { "pos": [...] },
    "glass": { "pos": [...] },
    "fork":  { "pos": [...] },
    "fork2": { "pos": [...] },
    "stir":  { "pos": [...] },
    "lid":   { "pos": [...] }
}
```

Also print a summary line to stdout:
```
Box [X, Y, Z]
Volume: V
```

where `[X, Y, Z]` are the bounding box dimensions and `V = X × Y × Z`.

### Scoring

- **Invalid solution** (overlaps, missing objects, deformed objects): score = 0
- **Valid solution**: score = `reference_volume / achieved_volume` (higher is better, capped at 1.0)

The reference volume is **490** (7×7×10), corresponding to known solutions from GPT-4.5 and Gemini 1.5 Pro. A score of 1.0 means you matched or beat the reference; anything below means your bounding box is larger.

### Object Inventory

| Object | Voxel Count | Natural Bounding Box |
|--------|------------|----------------------|
| tray   | 130        | 7 × 10 × 3 = 210    |
| bowl1  | 25         | 7 × 7 × 3 = 147     |
| bowl2  | 25         | 7 × 7 × 3 = 147     |
| bowl3  | 25         | 7 × 7 × 3 = 147     |
| bowl4  | 25         | 7 × 7 × 3 = 147     |
| glass  | 52         | 4 × 3 × 5 = 60      |
| fork   | 7          | 2 × 2 × 5 = 20      |
| fork2  | 7          | 2 × 2 × 5 = 20      |
| stir   | 4          | 1 × 1 × 4 = 4       |
| lid    | 22         | 4 × 3 × 2 = 24      |
| **Total** | **322** | —                  |

**Hint**: The 4 bowls are identical and can be oriented/stacked to reduce footprint. The tray has a large hollow interior; fitting objects inside the tray's rim cavity may dramatically reduce the bounding box.
