"""
Shared geometry and workspace I/O for all placement tools.
Transform semantics match verifier.py's all_48_transforms exactly.
"""
import json
import os

OBJECTS_PATH   = "/task/objects.json"
WORKSPACE_PATH = "/home/user/workspace.json"

PERM_MAP = {"x": 0, "y": 1, "z": 2}


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_perm(s):
    """'xzy' → [0,2,1]. Raises ValueError on invalid input."""
    if len(s) != 3 or set(s) != {"x", "y", "z"}:
        raise ValueError(f"invalid perm '{s}' — must be a permutation of 'xyz'")
    return [PERM_MAP[c] for c in s]


def parse_signs(s):
    """'++-' → [1,1,-1]. Raises ValueError on invalid input."""
    if len(s) != 3 or not all(c in "+-" for c in s):
        raise ValueError(f"invalid signs '{s}' — must be 3 chars of '+' or '-'")
    return [1 if c == "+" else -1 for c in s]


# ── Geometry ──────────────────────────────────────────────────────────────────

def apply_transform(pts, perm, signs):
    """
    Apply signed axis permutation to a list of (x,y,z) tuples.
    new[i] = signs[i] * pt[perm[i]]
    Does NOT normalize or translate.
    """
    return [[signs[0]*p[perm[0]], signs[1]*p[perm[1]], signs[2]*p[perm[2]]] for p in pts]


def normalize_to_origin(pts):
    """Shift so minimum on each axis is 0."""
    if not pts:
        return pts
    min_x = min(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    min_z = min(p[2] for p in pts)
    return [[p[0]-min_x, p[1]-min_y, p[2]-min_z] for p in pts]


def translate(pts, ox, oy, oz):
    return [[p[0]+ox, p[1]+oy, p[2]+oz] for p in pts]


def compute_bbox(all_pts):
    """Returns ((dx,dy,dz), volume) or ((0,0,0), 0) if empty."""
    if not all_pts:
        return (0, 0, 0), 0
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    zs = [p[2] for p in all_pts]
    dx = max(xs) - min(xs) + 1
    dy = max(ys) - min(ys) + 1
    dz = max(zs) - min(zs) + 1
    return (dx, dy, dz), dx * dy * dz


def build_final_pts(pts, perm, signs, ox, oy, oz):
    """Full pipeline: transform → normalize → translate."""
    transformed = apply_transform(pts, perm, signs)
    normalized  = normalize_to_origin(transformed)
    return translate(normalized, ox, oy, oz)


# ── Object loading ────────────────────────────────────────────────────────────

def load_objects(path=OBJECTS_PATH):
    """Returns {name: [[x,y,z], ...]} — all subgroups merged."""
    with open(path) as f:
        raw = json.load(f)
    return {name: [list(c) for grp in subgroups.values() for c in grp]
            for name, subgroups in raw.items()}


# ── Workspace I/O ─────────────────────────────────────────────────────────────

def load_workspace(objects_path=OBJECTS_PATH, workspace_path=WORKSPACE_PATH):
    """
    Load workspace. Auto-initializes if missing or malformed.
    Returns {"placed": {name: [[x,y,z]...]}, "unplaced": [name,...]}
    """
    if os.path.exists(workspace_path):
        try:
            with open(workspace_path) as f:
                ws = json.load(f)
            if "placed" in ws and "unplaced" in ws:
                return ws
            import sys
            print("WARNING: workspace.json malformed, reinitializing.", file=sys.stderr)
        except (json.JSONDecodeError, OSError):
            import sys
            print("WARNING: workspace.json unreadable, reinitializing.", file=sys.stderr)

    objects = load_objects(objects_path)
    ws = {"placed": {}, "unplaced": sorted(objects.keys())}
    save_workspace(ws, workspace_path)
    return ws


def save_workspace(ws, workspace_path=WORKSPACE_PATH):
    """Atomic write via temp file."""
    tmp = workspace_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ws, f, indent=2)
    os.replace(tmp, workspace_path)


# ── Display helpers ───────────────────────────────────────────────────────────

def all_placed_pts(ws):
    return [p for pts in ws["placed"].values() for p in pts]


def print_placement_summary(ws):
    pts = all_placed_pts(ws)
    dims, vol = compute_bbox(pts)
    placed   = sorted(ws["placed"].keys())
    unplaced = sorted(ws["unplaced"])
    if pts:
        print(f"Bounding box: {dims[0]} x {dims[1]} x {dims[2]} = {vol}")
    else:
        print("Bounding box: none (no objects placed yet)")
    print(f"Placed   ({len(placed)}): {', '.join(placed) if placed else '—'}")
    print(f"Unplaced ({len(unplaced)}): {', '.join(unplaced) if unplaced else '—'}")
