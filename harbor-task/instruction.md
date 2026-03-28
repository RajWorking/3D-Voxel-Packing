# Task: 3D Voxel Bin-Packing

You are given a set of rigid 3D objects defined as collections of integer-coordinate voxels. Your goal is to pack all objects so the axis-aligned bounding box enclosing all voxels has **minimum volume**.

## Objects

Read the object definitions from `/task/objects.json`. Each top-level key is an object name. Each object contains one or more named sub-groups, each mapping to a list of `[x, y, z]` integer coordinates. Sub-group names are labels only — treat all coordinates within an object as a single rigid body.

## Allowed Transformations (per object)

You may apply any combination of:
- **Rotation**: 90° increments around any axis
- **Reflection**: Flip along any axis
- **Translation**: Shift to any non-negative integer position

This covers all 48 symmetries of a cube (signed axis permutations). The relative distances between voxels within an object must be preserved exactly — no deformation.

## Constraints

1. No two distinct objects may share any `[x, y, z]` point.
2. Every object in `objects.json` must be placed.
3. All output coordinates must be ≥ 0.

## Objective

Minimize:
```
Volume = (max_x − min_x + 1) × (max_y − min_y + 1) × (max_z − min_z + 1)
```
taken over all voxels of all objects combined.

---

## Tools

You have 5 tools in `/task/tools/`. Call them with `python3`.

### 1. `check_state.py` — view current workspace
```
python3 /task/tools/check_state.py
```
Shows placed objects, unplaced objects, and current bounding box. Also initializes the workspace on first call.

### 2. `inspect_object.py` — preview an object's shape
```
python3 /task/tools/inspect_object.py <name>
python3 /task/tools/inspect_object.py <name> <perm> <signs>
```
Without transform: shows canonical voxels and bounding box.
With transform: shows what the object looks like after that transform (normalized to origin, before offset). Use this to plan orientations before placing.

### 3. `place_object.py` — place an object in the workspace
```
python3 /task/tools/place_object.py <name> <perm> <signs> <ox> <oy> <oz>
```
Applies the transform, normalizes to origin, then shifts by `(ox, oy, oz)`. Checks for collisions against all placed objects.
- **Success**: updates workspace, prints new bounding box.
- **Collision**: prints which objects/voxels conflict. Workspace unchanged.

### 4. `remove_object.py` — undo a placement
```
python3 /task/tools/remove_object.py <name>
```
Moves the object back to unplaced. Use this to backtrack and try a different orientation or position.

### 5. `finalize.py` — write the solution
```
python3 /task/tools/finalize.py
```
Requires all objects to be placed. Writes `/home/user/solution.json` and prints final volume.

---

## Transform Format

**`perm`** — which axis maps where (3 chars, each of `x`/`y`/`z` exactly once):

| perm | meaning |
|------|---------|
| `xyz` | identity (no swap) |
| `xzy` | swap y and z |
| `yxz` | swap x and y |
| `yzx` | x→y, y→z, z→x |
| `zxy` | x→z, y→x, z→y |
| `zyx` | swap x and z |

**`signs`** — whether to flip each axis (3 chars of `+`/`-`):
- `+++` no flip
- `++-` flip z
- `-++` flip x
- etc.

**Semantics**: for each voxel `[x, y, z]`:
```
new[0] = signs[0] * point[perm[0]]
new[1] = signs[1] * point[perm[1]]
new[2] = signs[2] * point[perm[2]]
```
Then normalize so the minimum on each axis is 0. Then add `(ox, oy, oz)`.

**Example**: `perm=xzy signs=++-` means:
```
new_x =  x      (perm[0]='x', signs[0]='+')
new_y =  z      (perm[1]='z', signs[1]='+')  ← y and z swapped
new_z = -y      (perm[2]='y', signs[2]='-')  ← then z flipped
```

---

## Scoring

Score = `reference_volume / achieved_volume`, capped at 1.0. Lower volume is better.
