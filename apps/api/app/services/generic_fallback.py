"""Generic pure-Python fallback mesh builders — one per shape type.

Used when OCC is not available. Each function returns (mesh_data_dict, tree_list).
All builders use only math — no dependencies.
"""
from __future__ import annotations
import math
from typing import Any


# ── Low-level mesh primitives ──────────────────────────────────────────────────

class MeshBuilder:
    def __init__(self):
        self.verts: list[float] = []
        self.idx: list[int] = []
        self.norms: list[float] = []

    def add_v(self, x, y, z, nx, ny, nz) -> int:
        self.verts.extend([x, y, z])
        self.norms.extend([nx, ny, nz])
        return len(self.verts) // 3 - 1

    def add_tri(self, a, b, c):
        self.idx.extend([a, b, c])

    def add_quad(self, a, b, c, d):
        self.add_tri(a, b, c)
        self.add_tri(a, c, d)

    def merge(self, other: "MeshBuilder"):
        off = len(self.verts) // 3
        self.verts.extend(other.verts)
        self.norms.extend(other.norms)
        self.idx.extend(i + off for i in other.idx)

    def to_mesh_data(self) -> dict:
        xs = self.verts[0::3]
        ys = self.verts[1::3]
        zs = self.verts[2::3]
        bb = {
            "min": [min(xs, default=0), min(ys, default=0), min(zs, default=0)],
            "max": [max(xs, default=1), max(ys, default=1), max(zs, default=1)],
        }
        return {"vertices": self.verts, "indices": self.idx, "normals": self.norms, "bounding_box": bb}


def _cylinder(cx, cy, zb, zt, outer_r, inner_r=0.0, n=48) -> MeshBuilder:
    """Hollow or solid cylinder."""
    mb = MeshBuilder()
    rings: dict[str, list[int]] = {"bo": [], "to": [], "bi": [], "ti": []}

    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        rings["bo"].append(mb.add_v(cx + outer_r*ca, cy + outer_r*sa, zb,  ca, sa, 0))
        rings["to"].append(mb.add_v(cx + outer_r*ca, cy + outer_r*sa, zt,  ca, sa, 0))
        if inner_r > 0:
            rings["bi"].append(mb.add_v(cx + inner_r*ca, cy + inner_r*sa, zb, -ca, -sa, 0))
            rings["ti"].append(mb.add_v(cx + inner_r*ca, cy + inner_r*sa, zt, -ca, -sa, 0))

    for i in range(n):
        j = (i + 1) % n
        mb.add_quad(rings["bo"][i], rings["bo"][j], rings["to"][j], rings["to"][i])

    if inner_r > 0:
        for i in range(n):
            j = (i + 1) % n
            mb.add_quad(rings["bi"][i], rings["ti"][i], rings["ti"][j], rings["bi"][j])
            mb.add_quad(rings["to"][i], rings["ti"][i], rings["ti"][j], rings["to"][j])
            mb.add_quad(rings["bo"][i], rings["bo"][j], rings["bi"][j], rings["bi"][i])
    else:
        # Solid caps
        center_top = mb.add_v(cx, cy, zt, 0, 0,  1)
        center_bot = mb.add_v(cx, cy, zb, 0, 0, -1)
        for i in range(n):
            j = (i + 1) % n
            t0 = mb.add_v(cx + outer_r*math.cos(2*math.pi*i/n), cy + outer_r*math.sin(2*math.pi*i/n), zt, 0, 0,  1)
            t1 = mb.add_v(cx + outer_r*math.cos(2*math.pi*j/n), cy + outer_r*math.sin(2*math.pi*j/n), zt, 0, 0,  1)
            b0 = mb.add_v(cx + outer_r*math.cos(2*math.pi*i/n), cy + outer_r*math.sin(2*math.pi*i/n), zb, 0, 0, -1)
            b1 = mb.add_v(cx + outer_r*math.cos(2*math.pi*j/n), cy + outer_r*math.sin(2*math.pi*j/n), zb, 0, 0, -1)
            mb.add_tri(center_top, t0, t1)
            mb.add_tri(center_bot, b1, b0)
    return mb


def _box(x0, y0, z0, x1, y1, z1) -> MeshBuilder:
    """Axis-aligned box."""
    mb = MeshBuilder()
    def face(corners, nx, ny, nz):
        vi = [mb.add_v(*c, nx, ny, nz) for c in corners]
        mb.add_quad(*vi)

    face([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],  0, 0,  1)  # +Z
    face([(x0,y0,z0),(x0,y1,z0),(x1,y1,z0),(x1,y0,z0)],  0, 0, -1)  # -Z
    face([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],  1, 0,  0)  # +X
    face([(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)], -1, 0,  0)  # -X
    face([(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)],  0, 1,  0)  # +Y
    face([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],  0,-1,  0)  # -Y
    return mb


def _bolt_holes_visual(parent: MeshBuilder, count: int, circle_r: float,
                        hole_r: float, z_top: float, depth: float):
    """Subtract-approximated bolt holes by adding dark cylinders (visual only, no boolean)."""
    for i in range(count):
        a = 2 * math.pi * i / count
        cx = circle_r * math.cos(a)
        cy = circle_r * math.sin(a)
        hole = _cylinder(cx, cy, z_top - depth, z_top + 0.5, hole_r * 0.6, 0, n=16)
        parent.merge(hole)


# ── Per-shape builders ─────────────────────────────────────────────────────────

def build_box(params: dict) -> tuple[dict, list[dict]]:
    length = float(params.get("length", 100))
    width  = float(params.get("width",  60))
    height = float(params.get("height", 40))
    wall   = float(params.get("wall_thickness", 0))

    mb = MeshBuilder()
    if wall > 0 and wall < min(length, width, height) / 2:
        # Hollow box — outer
        mb.merge(_box(-length/2, -width/2, 0, length/2, width/2, height))
        # No inner subtraction in pure python; just represent as solid
    else:
        mb.merge(_box(-length/2, -width/2, 0, length/2, width/2, height))

    tree = [
        {"id": "outer_box",    "label": "Outer Box",    "status": "success"},
        {"id": "fillets",      "label": "Fillets",      "status": "pending"},
        {"id": "chamfers",     "label": "Chamfers",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_plate(params: dict) -> tuple[dict, list[dict]]:
    length       = float(params.get("length", 120))
    width        = float(params.get("width",  80))
    thickness    = float(params.get("thickness", 10))
    hole_count   = int(params.get("hole_count", 4))
    hole_diameter= float(params.get("hole_diameter", 8))
    hole_circle_r= float(params.get("hole_circle_radius", 40))

    mb = _box(-length/2, -width/2, 0, length/2, width/2, thickness)
    # Visual bolt holes
    _bolt_holes_visual(mb, hole_count, hole_circle_r, hole_diameter/2, thickness, thickness)

    tree = [
        {"id": "plate_body",   "label": "Plate Body",   "status": "success"},
        {"id": "bolt_holes",   "label": "Bolt Holes",   "status": "pending"},
        {"id": "chamfers",     "label": "Chamfers",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_pipe_flange(params: dict) -> tuple[dict, list[dict]]:
    outer_r     = float(params.get("outer_diameter", 100)) / 2
    bore_r      = float(params.get("bore_diameter", 50)) / 2
    thickness   = float(params.get("thickness", 20))
    bolt_count  = int(params.get("bolt_hole_count", 8))
    bolt_r      = float(params.get("bolt_hole_diameter", 14)) / 2
    bolt_circle = float(params.get("bolt_circle_diameter", 80)) / 2

    mb = MeshBuilder()
    mb.merge(_cylinder(0, 0, 0, thickness, outer_r, bore_r))
    _bolt_holes_visual(mb, bolt_count, bolt_circle, bolt_r, thickness, thickness)

    tree = [
        {"id": "flange_body",  "label": "Flange Body",  "status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
        {"id": "bolt_holes",   "label": "Bolt Holes",   "status": "pending"},
        {"id": "chamfers",     "label": "Chamfers",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_shaft(params: dict) -> tuple[dict, list[dict]]:
    length   = float(params.get("length", 200))
    diameter = float(params.get("diameter", 30))
    step_d   = float(params.get("step_diameter", diameter * 0.75))
    step_pos = float(params.get("step_position", length * 0.4))
    key_w    = float(params.get("keyway_width", 0))

    mb = MeshBuilder()
    # Main body
    mb.merge(_cylinder(0, 0, 0, step_pos, diameter/2, 0))
    # Step section
    mb.merge(_cylinder(0, 0, step_pos, length, step_d/2, 0))

    tree = [
        {"id": "main_body",    "label": "Main Body",    "status": "success"},
        {"id": "step_section", "label": "Step Section", "status": "success"},
        {"id": "keyway",       "label": "Keyway",       "status": "pending" if key_w == 0 else "success"},
        {"id": "chamfers",     "label": "Chamfers",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_bushing(params: dict) -> tuple[dict, list[dict]]:
    outer_r  = float(params.get("outer_diameter", 40)) / 2
    inner_r  = float(params.get("inner_diameter", 25)) / 2
    length   = float(params.get("length", 30))

    mb = _cylinder(0, 0, 0, length, outer_r, inner_r)

    tree = [
        {"id": "bushing_body", "label": "Bushing Body", "status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
        {"id": "chamfers",     "label": "Chamfers",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_bracket(params: dict) -> tuple[dict, list[dict]]:
    base_l   = float(params.get("base_length", 100))
    base_w   = float(params.get("base_width",  60))
    base_t   = float(params.get("base_thickness", 8))
    rib_h    = float(params.get("rib_height", 60))
    rib_t    = float(params.get("rib_thickness", 8))
    hole_d   = float(params.get("hole_diameter", 10))
    hole_cnt = int(params.get("hole_count", 4))

    mb = MeshBuilder()
    # Base plate
    mb.merge(_box(-base_l/2, -base_w/2, 0, base_l/2, base_w/2, base_t))
    # Vertical rib
    mb.merge(_box(-rib_t/2, -base_w/2, base_t, rib_t/2, base_w/2, base_t + rib_h))
    _bolt_holes_visual(mb, hole_cnt, min(base_l, base_w)/2 * 0.65, hole_d/2, base_t, base_t)

    tree = [
        {"id": "base_plate",   "label": "Base Plate",   "status": "success"},
        {"id": "rib",          "label": "Rib",          "status": "success"},
        {"id": "bolt_holes",   "label": "Bolt Holes",   "status": "pending"},
        {"id": "fillets",      "label": "Fillets",      "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_gear(params: dict) -> tuple[dict, list[dict]]:
    pitch_r    = float(params.get("pitch_diameter", 80)) / 2
    face_width = float(params.get("face_width", 20))
    bore_r     = float(params.get("bore_diameter", 20)) / 2
    teeth      = int(params.get("tooth_count", 20))
    addendum   = float(params.get("addendum", pitch_r / teeth))
    dedendum   = float(params.get("dedendum", addendum * 1.25))

    mb = MeshBuilder()
    # Hub
    mb.merge(_cylinder(0, 0, 0, face_width, bore_r * 1.8, bore_r))
    # Approximate tooth ring as annular cylinder
    mb.merge(_cylinder(0, 0, 0, face_width,
                       pitch_r + addendum, pitch_r - dedendum * 0.5))

    tree = [
        {"id": "gear_hub",     "label": "Gear Hub",     "status": "success"},
        {"id": "tooth_ring",   "label": "Tooth Profile","status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
        {"id": "keyway",       "label": "Keyway",       "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_elbow(params: dict) -> tuple[dict, list[dict]]:
    pipe_r  = float(params.get("outer_diameter", 60)) / 2
    bore_r  = float(params.get("bore_diameter", 40)) / 2
    flange_r= float(params.get("flange_diameter", pipe_r * 1.6))
    flange_t= float(params.get("flange_thickness", 12))
    arm_len = float(params.get("arm_length", 80))
    angle   = float(params.get("elbow_angle_degrees", 90))

    mb = MeshBuilder()
    # Horizontal arm
    mb.merge(_cylinder(0, 0, 0, arm_len, pipe_r, bore_r))
    # Vertical arm (approximation — rotate 90° by offsetting)
    a = math.radians(angle)
    arm2_cx = arm_len * math.cos(a)
    arm2_cy = 0
    for step in range(1, 9):
        frac = step / 8
        ang = a * frac
        cx = arm_len * math.cos(ang)
        cy = arm_len * math.sin(ang)
        mb.merge(_cylinder(cx - pipe_r/2, cy - pipe_r/2,
                           -pipe_r/2, pipe_r/2,
                           pipe_r, bore_r * 0.9, n=20))
    # Flanges
    mb.merge(_cylinder(0, 0, -flange_t, 0, flange_r, bore_r))

    tree = [
        {"id": "elbow_body",   "label": "Elbow Body",   "status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
        {"id": "flanges",      "label": "Flanges",      "status": "success"},
    ]
    return mb.to_mesh_data(), tree


def build_t_fitting(params: dict) -> tuple[dict, list[dict]]:
    pipe_r  = float(params.get("outer_diameter", 60)) / 2
    bore_r  = float(params.get("bore_diameter", 40)) / 2
    arm_len = float(params.get("arm_length", 80))
    branch_r= float(params.get("branch_diameter", pipe_r * 2)) / 2

    mb = MeshBuilder()
    # Main run along Z axis
    mb.merge(_cylinder(0, 0, -arm_len, arm_len, pipe_r, bore_r))
    # Branch along X axis (perpendicular, pure python)
    mb.merge(_cylinder(0, 0, -branch_r, branch_r, branch_r, bore_r * 0.85, n=32))

    tree = [
        {"id": "main_run",     "label": "Main Run",     "status": "success"},
        {"id": "branch",       "label": "Branch",       "status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_housing(params: dict) -> tuple[dict, list[dict]]:
    length  = float(params.get("length", 150))
    width   = float(params.get("width",  100))
    height  = float(params.get("height",  80))
    wall    = float(params.get("wall_thickness", 8))
    bore_d  = float(params.get("bore_diameter", 50))
    bolt_cnt= int(params.get("bolt_hole_count", 4))
    bolt_d  = float(params.get("bolt_hole_diameter", 10))

    mb = MeshBuilder()
    # Outer shell (simplified as solid box)
    mb.merge(_box(-length/2, -width/2, 0, length/2, width/2, height))
    # Bore hole visual
    mb.merge(_cylinder(0, 0, -1, height + 1, bore_d/2 * 0.85, 0, n=40))
    _bolt_holes_visual(mb, bolt_cnt, min(length, width)/2 * 0.7, bolt_d/2, height, height/2)

    tree = [
        {"id": "housing_body", "label": "Housing Body", "status": "success"},
        {"id": "bore_cut",     "label": "Bore Cut",     "status": "pending"},
        {"id": "bolt_holes",   "label": "Bolt Holes",   "status": "pending"},
        {"id": "fillets",      "label": "Fillets",      "status": "pending"},
    ]
    return mb.to_mesh_data(), tree


def build_custom(params: dict) -> tuple[dict, list[dict]]:
    """Best-effort generic build when shape doesn't match any known type.

    Uses the most universal params: length/width/height → box,
    or outer_diameter/height → cylinder.
    """
    od = params.get("outer_diameter") or params.get("outer_body_diameter")
    h  = params.get("height") or params.get("overall_height") or params.get("length")

    mb = MeshBuilder()
    if od and h:
        inner_d = params.get("bore_diameter") or params.get("inner_diameter") or 0
        mb.merge(_cylinder(0, 0, 0, float(h), float(od)/2, float(inner_d)/2))
    else:
        l = float(params.get("length", 100))
        w = float(params.get("width", 60))
        ht = float(params.get("height", 40))
        mb.merge(_box(-l/2, -w/2, 0, l/2, w/2, ht))

    tree = [{"id": "body", "label": "Body", "status": "success"}]
    return mb.to_mesh_data(), tree


# ── Dispatch table ─────────────────────────────────────────────────────────────

_BUILDERS = {
    "box":           build_box,
    "plate":         build_plate,
    "pipe_flange":   build_pipe_flange,
    "shaft":         build_shaft,
    "bushing":       build_bushing,
    "bracket":       build_bracket,
    "gear":          build_gear,
    "elbow_fitting": build_elbow,
    "t_fitting":     build_t_fitting,
    "housing":       build_housing,
    "custom":        build_custom,
}


def build_generic_fallback(shape_type: str, params: dict) -> tuple[dict, list[dict]]:
    """Dispatcher: call the right fallback builder for a shape type."""
    fn = _BUILDERS.get(shape_type, build_custom)
    try:
        return fn(params)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(f"Fallback build failed for {shape_type}: {exc}; using generic box")
        return build_custom(params)
