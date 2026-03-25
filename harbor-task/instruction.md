# Task: 3D Voxel Bin-Packing

You are given a set of rigid 3D objects defined as collections of integer-coordinate voxels. Your goal is to pack all objects so the axis-aligned bounding box enclosing all voxels has **minimum volume**.

## Objects

Read the object definitions from `/task/objects.json`. Each top-level key is an object name. Each object contains named sub-groups (e.g., `base_z0`, `rim_z1`) listing `[x, y, z]` coordinates. The sub-group names are descriptive only — treat all coordinates within an object as a single rigid body.

## Allowed Transformations (per object)

You may apply any combination of:
- **Rotation**: 90° increments around any axis
- **Reflection**: Flip along any axis
- **Translation**: Shift to any non-negative integer position

This covers all 48 symmetries of a cube (signed axis permutations). The relative distances between voxels within an object must be preserved exactly.

## Constraints

1. **No deformation**: Each object's transformed voxels must be congruent (same shape, different placement) to its original voxels.
2. **No overlap**: No two distinct objects may share any `[x, y, z]` point.
3. **All objects required**: Every object in `objects.json` must appear in your solution.
4. **Non-negative coordinates**: All output coordinates must be ≥ 0.

## Objective

Minimize:
```
Volume = (max_x − min_x + 1) × (max_y − min_y + 1) × (max_z − min_z + 1)
```
taken over all voxels of all objects combined.

## Output

Write your solution to `/home/user/solution.json` in this exact format:

```json
{
    "tray":  { "pos": [[x,y,z], ...] },
    "bowl1": { "pos": [[x,y,z], ...] },
    "bowl2": { "pos": [[x,y,z], ...] },
    "bowl3": { "pos": [[x,y,z], ...] },
    "bowl4": { "pos": [[x,y,z], ...] },
    "glass": { "pos": [[x,y,z], ...] },
    "fork":  { "pos": [[x,y,z], ...] },
    "fork2": { "pos": [[x,y,z], ...] },
    "stir":  { "pos": [[x,y,z], ...] },
    "lid":   { "pos": [[x,y,z], ...] }
}
```

Each `"pos"` list must contain all voxels of that object (all sub-groups merged into one flat list).

Also print to stdout:
```
Box [X, Y, Z]
Volume: V
```

where `[X, Y, Z]` are the bounding box dimensions (extent in each axis) and `V = X × Y × Z`.

## Strategy Hints

- The 4 bowls (`bowl1`–`bowl4`) are identical — consider how they can nest or share space.
- The `tray` has a hollow interior when viewed from above; objects may fit inside its rim.
- The `lid` and `glass` have the same 4×3 footprint — they might stack or interlock.
- The `stir` is just a 4-voxel line — it fits in small gaps.
- Orient objects along their shortest axis to reduce total height/width.

Think step-by-step: (1) determine each object's transformed bounding box for candidate orientations, (2) plan a layout, (3) assign concrete coordinates, (4) verify no overlaps, (5) compute volume, (6) write solution.
