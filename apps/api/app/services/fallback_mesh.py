"""Fallback mesh generator using pure Python when OpenCascade is not available.

Produces a simplified Lower Valve Body approximation using parametric math.
This is used when pythonocc-core is not installed (e.g., dev environments without conda).
The geometry is NOT as accurate as the OCC pipeline but demonstrates the 3D viewer.
"""
import math
from typing import List


def _circle_points(cx: float, cy: float, cz: float,
                   radius: float, n: int, axis: str = 'z') -> List[List[float]]:
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        if axis == 'z':
            pts.append([cx + radius * math.cos(angle), cy + radius * math.sin(angle), cz])
        elif axis == 'x':
            pts.append([cx, cy + radius * math.cos(angle), cz + radius * math.sin(angle)])
        elif axis == 'y':
            pts.append([cx + radius * math.cos(angle), cy, cz + radius * math.sin(angle)])
    return pts


def build_cylinder_mesh(
    cx: float, cy: float, z_bottom: float, z_top: float,
    outer_r: float, inner_r: float = 0.0, n_seg: int = 32
) -> tuple[list[float], list[int], list[float]]:
    """Build a hollow cylinder (tube) mesh with open ends."""
    vertices: list[float] = []
    indices: list[int] = []

    def add_vertex(x, y, z, nx, ny, nz):
        vertices.extend([x, y, z])
        return len(vertices) // 3 - 1

    ring_bot_out, ring_top_out = [], []
    ring_bot_in,  ring_top_in  = [], []

    for i in range(n_seg):
        angle = 2 * math.pi * i / n_seg
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Outer surface
        ring_bot_out.append(add_vertex(
            cx + outer_r * cos_a, cy + outer_r * sin_a, z_bottom,
            cos_a, sin_a, 0))
        ring_top_out.append(add_vertex(
            cx + outer_r * cos_a, cy + outer_r * sin_a, z_top,
            cos_a, sin_a, 0))

        if inner_r > 0:
            # Inner surface (normals pointing inward)
            ring_bot_in.append(add_vertex(
                cx + inner_r * cos_a, cy + inner_r * sin_a, z_bottom,
                -cos_a, -sin_a, 0))
            ring_top_in.append(add_vertex(
                cx + inner_r * cos_a, cy + inner_r * sin_a, z_top,
                -cos_a, -sin_a, 0))

    # Outer wall quads
    for i in range(n_seg):
        j = (i + 1) % n_seg
        indices.extend([ring_bot_out[i], ring_top_out[i], ring_top_out[j]])
        indices.extend([ring_bot_out[i], ring_top_out[j], ring_bot_out[j]])

    # Inner wall quads (reversed winding)
    if inner_r > 0:
        for i in range(n_seg):
            j = (i + 1) % n_seg
            indices.extend([ring_bot_in[i], ring_top_in[j], ring_top_in[i]])
            indices.extend([ring_bot_in[i], ring_bot_in[j], ring_top_in[j]])

        # Top annular cap
        for i in range(n_seg):
            j = (i + 1) % n_seg
            indices.extend([ring_top_out[i], ring_top_in[i], ring_top_in[j]])
            indices.extend([ring_top_out[i], ring_top_in[j], ring_top_out[j]])

        # Bottom annular cap
        for i in range(n_seg):
            j = (i + 1) % n_seg
            indices.extend([ring_bot_out[i], ring_bot_in[j], ring_bot_in[i]])
            indices.extend([ring_bot_out[i], ring_bot_out[j], ring_bot_in[j]])

    # Extract normals from vertices
    normals = []
    for i in range(0, len(vertices), 3):
        # Normal is already encoded -recompute from position for simplicity
        nx, ny = vertices[i] - cx, vertices[i+1] - cy
        length = math.sqrt(nx*nx + ny*ny) or 1.0
        normals.extend([nx/length, ny/length, 0.0])

    return vertices, indices, normals


def build_fallback_lower_valve_body(params: dict) -> tuple[dict, list[dict]]:
    """Build a simplified but representative Lower Valve Body mesh without OCC.

    Returns (mesh_data_dict, feature_tree_list).
    """
    h    = params.get('overall_height', 118.0)
    od   = params.get('outer_body_diameter', 36.0) / 2
    bore = params.get('main_bore_upper_diameter', 28.0) / 2
    tf_r = params.get('top_flange_outer_diameter', 40.0) / 2
    bf_r = params.get('bottom_flange_outer_flange_diameter', 65.0) / 2
    sp_r = params.get('side_port_flange_outer_diameter', 34.0) / 2
    sp_bore = params.get('side_port_bore_diameter', 20.0) / 2
    sp_off  = params.get('side_port_offset_from_top', 58.0)
    sp_ang  = math.radians(params.get('side_port_angle_degrees', 135.0))

    all_verts: list[float] = []
    all_idx:   list[int]   = []
    all_norms: list[float] = []

    tree: list[dict] = []

    def merge(verts, idx, norms, label, node_id):
        offset = len(all_verts) // 3
        all_verts.extend(verts)
        all_idx.extend([i + offset for i in idx])
        all_norms.extend(norms)
        tree.append({"id": node_id, "label": label, "status": "success"})

    # 1. Main body cylinder (hollow)
    v, i, n = build_cylinder_mesh(0, 0, 0, h, od, bore * 0.95, n_seg=48)
    merge(v, i, n, "Base Cylinder", "base_cylinder")

    # 2. Top flange
    v, i, n = build_cylinder_mesh(0, 0, h, h + 8, tf_r, bore * 0.95, n_seg=48)
    merge(v, i, n, "Top Flange Extrusion", "top_flange_extrusion")

    # 3. Bottom flange
    v, i, n = build_cylinder_mesh(0, 0, -6, 0, bf_r, bore * 0.85, n_seg=48)
    merge(v, i, n, "Bottom Flange Extrusion", "bottom_flange_extrusion")

    # 4. Side port boss
    boss_z   = h - sp_off
    boss_cx  = math.cos(sp_ang) * (od + 12)
    boss_cy  = math.sin(sp_ang) * (od + 12)
    v, i, n = build_cylinder_mesh(boss_cx, boss_cy, boss_z - sp_r, boss_z + sp_r,
                                   sp_r, sp_bore * 0.9, n_seg=32)
    merge(v, i, n, "Side Port Boss", "side_port_boss")

    # Add stub feature nodes for the cuts (they would be OCC operations)
    for node_id, label in [
        ("upper_bore_cut",         "Upper Bore Cut"),
        ("lower_bore_cut",         "Lower Bore Cut"),
        ("side_port_bore_cut",     "Side Port Bore Cut"),
        ("top_bolt_holes_cut",     "Top Bolt Holes Cut"),
        ("top_counterbores_cut",   "Top Counterbores Cut"),
        ("bottom_bolt_holes_cut",  "Bottom Bolt Holes Cut"),
        ("bottom_counterbores_cut","Bottom Counterbores Cut"),
        ("side_port_bolt_holes_cut","Side Port Bolt Holes Cut"),
        ("fillets",                "Fillets"),
        ("chamfers",               "Chamfers"),
    ]:
        tree.append({"id": node_id, "label": label,
                     "status": "pending"})  # pending = not executed in fallback

    # Compute bounding box
    xs = all_verts[0::3]
    ys = all_verts[1::3]
    zs = all_verts[2::3]
    bb = {
        "min": [min(xs), min(ys), min(zs)],
        "max": [max(xs), max(ys), max(zs)],
    }

    mesh_data = {
        "vertices": all_verts,
        "indices":  all_idx,
        "normals":  all_norms,
        "bounding_box": bb,
    }

    return mesh_data, tree
