# Evaluation Framework: 3D Voxel Bin-Packing

## Task Summary

Models are given a set of voxel-based 3D objects and must pack them to minimize the bounding box
volume using only rigid transformations (rotations, reflections, translations).

---

## Metrics

### 1. Validity (Binary — primary pass/fail)

| Check | Description | Weight |
|-------|-------------|--------|
| **Object completeness** | All named objects from input are present in solution | Hard gate |
| **Voxel count** | Each object has the exact same number of voxels as the original | Hard gate |
| **No deformation** | Each object's voxel set is congruent to the original under a rigid transform (verified by testing all 48 hyperoctahedral symmetries) | Hard gate |
| **No overlap** | No two objects share a voxel coordinate | Hard gate |
| **Non-negative coords** | All coordinates ≥ 0 | Hard gate |

A solution fails the entire task if **any** hard gate is violated.

### 2. Volume Score (Continuous — quality metric)

```
volume_score = min(1.0, reference_volume / achieved_volume)
```

- **`reference_volume`**: set in `task.toml`; the volume a competent baseline solution achieves
- **`achieved_volume`**: `(max_x − min_x + 1) × (max_y − min_y + 1) × (max_z − min_z + 1)` over all placed voxels
- Score = 1.0 if the model matches or beats the reference; lower scores for larger bounding boxes

### 3. Voxel Efficiency (Diagnostic)

```
efficiency = total_voxels / achieved_volume
```

- `total_voxels` is the sum of voxel counts across all input objects (computed at runtime)
- A perfect pack would achieve efficiency = 1.0 (physically impossible given concave/irregular shapes)
- This metric is diagnostic — it quantifies how much empty space the model wastes

### 4. Format Compliance (Binary)

| Check | Criterion |
|-------|-----------|
| Valid JSON | `solution.json` is parseable |
| Correct schema | Every object has a `"pos"` key with a list of `[x,y,z]` triples |
| All objects keyed | Same top-level keys as input, no more, no less |

A format failure prevents validity checking and scores 0.

---

## Scoring Summary

| Metric | Type | Range | Notes |
|--------|------|-------|-------|
| `valid` | Boolean | pass/fail | Primary Harbor exit code |
| `volume` | Integer | > 0 | Achieved bounding box volume |
| `volume_score` | Float | 0.0–1.0 | Quality relative to reference volume |
| `efficiency` | Float | 0.0–1.0 | total_voxels / volume |

---

## Capability Gap This Measures

This task probes **3D spatial reasoning under combinatorial constraint**:

1. **Rotation awareness**: Can the model correctly enumerate and apply rigid 3D transforms to voxel objects?
2. **Packing intuition**: Can the model recognize geometric opportunities (nesting, stacking, gap-filling) to reduce total footprint?
3. **Constraint propagation**: Can the model track and verify its own placement decisions for overlap across all objects simultaneously?
4. **Optimization drive**: Does the model search for better configurations rather than stopping at the first valid placement?

### Why This Is a Meaningful Capability Gap

- Language models have no native 3D spatial geometry module; they must simulate geometric reasoning symbolically over coordinate lists.
- The objects have **irregular, non-convex shapes**, making naive axis-aligned packing suboptimal — the model must reason about orientation trade-offs.
- The task has a **verifiable ground truth** (any valid packing with volume ≤ N), making failures unambiguous and interpretable.
- Failure modes decompose cleanly: deformed shapes → misunderstood transforms; overlaps → failed constraint tracking; large volumes → no optimization search.
- The task is **instance-agnostic** in structure — the same verifier and scoring apply regardless of which objects are given, making it reusable across dataset variants.

---

## Known Baselines (Current Instance)

| Model | Volume | Score | Layout |
|-------|--------|-------|--------|
| GPT-4.5 | 490 | 1.00 | 7×7×10 |
| Gemini 1.5 Pro | 490 | 1.00 | 7×10×7 |
| Optimal (estimated) | < 490 | > 1.00 | open problem |

The true optimal is an open research question (3D bin-packing is NP-hard).

---

## Inter-Rater / Verifier Reliability

The verifier (`tests/verifier.py`) is fully deterministic:
- Rigid-transform check uses exhaustive search over all 48 symmetries — no false positives or negatives.
- Overlap check uses a hash set — O(N) exact.
- Volume computation is exact integer arithmetic.

There is **no subjective component**; two runs on the same output always agree.
