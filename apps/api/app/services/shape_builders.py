"""OCC geometry builders for all registered shape types (except lower_valve_body).

Each function: (params_dict) → (mesh_data_dict, feature_tree_list)
Falls back gracefully to generic_fallback if any OCC step fails.
"""
from __future__ import annotations
import math
import logging
from app.services.generic_geometry import (
    occ, node, cylinder, box, translate, fuse, cut,
    bolt_holes_cut, validate_shape, serialise,
)

logger = logging.getLogger(__name__)


def _wrap(shape_type: str, params: dict, _build_fn):
    """Run an OCC builder; on failure fall back to the pure-python fallback."""
    try:
        return _build_fn(params)
    except Exception as exc:
        logger.warning(f"OCC build failed for {shape_type}: {exc}; using fallback")
        from app.services.generic_fallback import build_generic_fallback
        return build_generic_fallback(shape_type, params)


# ── Box ────────────────────────────────────────────────────────────────────────

def build_box_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        L = float(p.get("length", 100))
        W = float(p.get("width", 60))
        H = float(p.get("height", 40))
        wall = float(p.get("wall_thickness", 0))
        fillet_r = float(p.get("fillet_radius", 0))
        tree = []

        solid = box(o, L, W, H)
        solid = translate(o, solid, -L/2, -W/2, 0)
        tree.append(node("outer_box", "Outer Box"))

        if wall > 1 and wall < min(L, W, H) / 2 - 1:
            inner = box(o, L - wall*2, W - wall*2, H + 2)
            inner = translate(o, inner, -L/2 + wall, -W/2 + wall, -1)
            solid = cut(o, solid, inner, "hollow_cut")
            tree.append(node("hollow_cut", "Hollow Cut"))

        if fillet_r > 0.1:
            try:
                from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
                from OCC.Core.TopAbs import TopAbs_EDGE
                from OCC.Core.TopExp import TopExp_Explorer
                fb = BRepFilletAPI_MakeFillet(solid)
                exp = TopExp_Explorer(solid, TopAbs_EDGE)
                cnt = 0
                while exp.More() and cnt < 12:
                    fb.Add(fillet_r, exp.Current())
                    cnt += 1
                    exp.Next()
                fb.Build()
                if fb.IsDone() and not fb.Shape().IsNull():
                    solid = fb.Shape()
                    tree.append(node("fillets", "Fillets"))
            except Exception as e:
                logger.debug(f"Box fillet skipped: {e}")
                tree.append(node("fillets", "Fillets", "failed"))
        else:
            tree.append(node("fillets", "Fillets", "failed"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("box", params, _build)


# ── Plate ──────────────────────────────────────────────────────────────────────

def build_plate_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        L = float(p.get("length", 120))
        W = float(p.get("width", 80))
        T = float(p.get("thickness", 10))
        hole_cnt  = int(p.get("hole_count", 4))
        hole_d    = float(p.get("hole_diameter", 8))
        hole_cr   = float(p.get("hole_circle_radius", min(L, W) * 0.35))
        fillet_r  = float(p.get("fillet_radius", 0))
        tree = []

        solid = box(o, L, W, T)
        solid = translate(o, solid, -L/2, -W/2, 0)
        tree.append(node("plate_body", "Plate Body"))

        # Bolt holes
        for i in range(hole_cnt):
            angle = i * (2 * math.pi / hole_cnt)
            hx = hole_cr * math.cos(angle)
            hy = hole_cr * math.sin(angle)
            hole = cylinder(o, hole_d/2, T + 2)
            hole = translate(o, hole, hx, hy, -1)
            solid = cut(o, solid, hole, f"hole_{i}")
        if hole_cnt > 0:
            tree.append(node("bolt_holes", "Bolt Holes"))

        if fillet_r > 0.1:
            tree.append(node("fillets", "Fillets", "pending"))
        tree.append(node("chamfers", "Chamfers", "failed"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("plate", params, _build)


# ── Pipe Flange ────────────────────────────────────────────────────────────────

def build_pipe_flange_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        outer_r    = float(p.get("outer_diameter", 100)) / 2
        bore_r     = float(p.get("bore_diameter", 50)) / 2
        thickness  = float(p.get("thickness", 20))
        bolt_cnt   = int(p.get("bolt_hole_count", 8))
        bolt_r     = float(p.get("bolt_hole_diameter", 14)) / 2
        bolt_cr    = float(p.get("bolt_circle_diameter", outer_r * 1.6)) / 2
        hub_r      = float(p.get("hub_diameter", bore_r * 1.5))
        hub_h      = float(p.get("hub_height", 0))
        tree = []

        solid = cylinder(o, outer_r, thickness)
        tree.append(node("flange_body", "Flange Body"))

        if hub_h > 0:
            hub = cylinder(o, hub_r, thickness + hub_h)
            solid = fuse(o, solid, hub, "hub_fuse")
            tree.append(node("hub_extrusion", "Hub Extrusion"))

        bore_tool = cylinder(o, bore_r, thickness + hub_h + 2)
        bore_tool = translate(o, bore_tool, 0, 0, -1)
        solid = cut(o, solid, bore_tool, "bore_cut")
        tree.append(node("bore_cut", "Bore Cut"))

        if bolt_cnt > 0 and bolt_r > 0:
            solid, ht = bolt_holes_cut(o, solid, bolt_r, bolt_cnt, bolt_cr, -1, thickness + 2, "bolt_hole")
            tree.extend(ht)

        tree.append(node("chamfers", "Chamfers", "failed"))
        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("pipe_flange", params, _build)


# ── Shaft ──────────────────────────────────────────────────────────────────────

def build_shaft_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        length    = float(p.get("length", 200))
        diameter  = float(p.get("diameter", 30))
        step_d    = float(p.get("step_diameter", diameter * 0.75))
        step_pos  = float(p.get("step_position", length * 0.4))
        step2_d   = float(p.get("step2_diameter", 0))
        step2_pos = float(p.get("step2_position", 0))
        key_w     = float(p.get("keyway_width", 0))
        key_d     = float(p.get("keyway_depth", 0))
        tree = []

        solid = cylinder(o, diameter/2, step_pos)
        tree.append(node("main_body", "Main Body"))

        step = cylinder(o, step_d/2, length - step_pos)
        step = translate(o, step, 0, 0, step_pos)
        solid = fuse(o, solid, step, "step_fuse")
        tree.append(node("step_section", "Step Section"))

        if step2_d > 0 and step2_pos > step_pos:
            s2 = cylinder(o, step2_d/2, length - step2_pos)
            s2 = translate(o, s2, 0, 0, step2_pos)
            solid = fuse(o, solid, s2, "step2_fuse")
            tree.append(node("step2_section", "Step 2 Section"))

        if key_w > 0 and key_d > 0:
            # Keyway: rectangular slot along the shaft
            kl = min(step_pos, 60.0)
            keyway = box(o, kl, key_w, key_d * 2)
            keyway = translate(o, keyway, 0, -key_w/2, diameter/2 - key_d * 1.5)
            solid = cut(o, solid, keyway, "keyway_cut")
            tree.append(node("keyway", "Keyway"))
        else:
            tree.append(node("keyway", "Keyway", "failed"))

        tree.append(node("chamfers", "Chamfers", "failed"))
        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("shaft", params, _build)


# ── Bushing ────────────────────────────────────────────────────────────────────

def build_bushing_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        outer_r = float(p.get("outer_diameter", 40)) / 2
        inner_r = float(p.get("inner_diameter", 25)) / 2
        length  = float(p.get("length", 30))
        flange_r= float(p.get("flange_diameter", 0)) / 2
        flange_t= float(p.get("flange_thickness", 0))
        tree = []

        solid = cylinder(o, outer_r, length)
        bore = cylinder(o, inner_r, length + 2)
        bore = translate(o, bore, 0, 0, -1)
        solid = cut(o, solid, bore, "bore_cut")
        tree.append(node("bushing_body", "Bushing Body"))
        tree.append(node("bore_cut", "Bore Cut"))

        if flange_r > outer_r and flange_t > 0:
            fl = cylinder(o, flange_r, flange_t)
            fl = translate(o, fl, 0, 0, length)
            bore_fl = cylinder(o, inner_r, flange_t + 2)
            bore_fl = translate(o, bore_fl, 0, 0, length - 1)
            fl = cut(o, fl, bore_fl, "flange_bore")
            solid = fuse(o, solid, fl, "flange_fuse")
            tree.append(node("flange", "Flange"))

        tree.append(node("chamfers", "Chamfers", "failed"))
        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("bushing", params, _build)


# ── Bracket ────────────────────────────────────────────────────────────────────

def build_bracket_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        base_l  = float(p.get("base_length", 100))
        base_w  = float(p.get("base_width", 60))
        base_t  = float(p.get("base_thickness", 8))
        rib_h   = float(p.get("rib_height", 60))
        rib_t   = float(p.get("rib_thickness", 8))
        hole_d  = float(p.get("hole_diameter", 10))
        hole_cnt= int(p.get("hole_count", 4))
        hole_cr = float(p.get("hole_circle_radius", min(base_l, base_w) * 0.35))
        tree = []

        base = box(o, base_l, base_w, base_t)
        base = translate(o, base, -base_l/2, -base_w/2, 0)
        tree.append(node("base_plate", "Base Plate"))

        rib = box(o, rib_t, base_w, rib_h)
        rib = translate(o, rib, -rib_t/2, -base_w/2, base_t)
        solid = fuse(o, base, rib, "rib_fuse")
        tree.append(node("rib", "Rib"))

        if hole_cnt > 0 and hole_d > 0:
            solid, ht = bolt_holes_cut(o, solid, hole_d/2, hole_cnt, hole_cr, -1, base_t + 2, "bolt_hole")
            tree.extend(ht)

        tree.append(node("fillets", "Fillets", "failed"))
        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("bracket", params, _build)


# ── Gear ───────────────────────────────────────────────────────────────────────

def build_gear_occ(params: dict) -> tuple[dict, list[dict]]:
    """Spur gear approximated as a toothed disc via OCC torus-subtraction is expensive.
    We build a realistic gear profile using polygon extrusion instead."""
    def _build(p):
        o = occ()
        pitch_r   = float(p.get("pitch_diameter", 80)) / 2
        face_w    = float(p.get("face_width", 20))
        bore_r    = float(p.get("bore_diameter", 20)) / 2
        teeth     = max(int(p.get("tooth_count", 20)), 4)
        module    = float(p.get("module", pitch_r * 2 / teeth))
        addendum  = module
        dedendum  = module * 1.25
        key_w     = float(p.get("keyway_width", 0))
        key_dep   = float(p.get("keyway_depth", 0))
        tree = []

        # Gear disc (outer cylinder at addendum radius)
        solid = cylinder(o, pitch_r + addendum, face_w)
        tree.append(node("gear_disc", "Gear Disc"))

        # Cut tooth gaps (dedendum circles between teeth)
        gap_r = (2 * math.pi * pitch_r / teeth) * 0.3
        for i in range(teeth):
            angle = i * (2 * math.pi / teeth) + math.pi / teeth
            gx = (pitch_r - dedendum * 0.5) * math.cos(angle)
            gy = (pitch_r - dedendum * 0.5) * math.sin(angle)
            gap = cylinder(o, gap_r, face_w + 2)
            gap = translate(o, gap, gx, gy, -1)
            solid = cut(o, solid, gap, f"tooth_gap_{i}")
        tree.append(node("tooth_gaps", "Tooth Gaps"))

        # Bore
        if bore_r > 0:
            bore_tool = cylinder(o, bore_r, face_w + 2)
            bore_tool = translate(o, bore_tool, 0, 0, -1)
            solid = cut(o, solid, bore_tool, "bore_cut")
            tree.append(node("bore_cut", "Bore Cut"))

        # Keyway
        if key_w > 0 and key_dep > 0:
            kl = face_w + 2
            keyway = box(o, kl, key_w, key_dep * 2)
            keyway = translate(o, keyway, -1, -key_w/2, bore_r - key_dep)
            solid = cut(o, solid, keyway, "keyway_cut")
            tree.append(node("keyway", "Keyway"))
        else:
            tree.append(node("keyway", "Keyway", "failed"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("gear", params, _build)


# ── Elbow Fitting ──────────────────────────────────────────────────────────────

def build_elbow_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        pipe_r   = float(p.get("outer_diameter", 60)) / 2
        bore_r   = float(p.get("bore_diameter", 40)) / 2
        arm_len  = float(p.get("arm_length", 80))
        flange_r = float(p.get("flange_diameter", pipe_r * 1.6))
        flange_t = float(p.get("flange_thickness", 12))
        angle    = float(p.get("elbow_angle_degrees", 90))
        bolt_cnt = int(p.get("bolt_hole_count", 4))
        bolt_d   = float(p.get("bolt_hole_diameter", 10))
        tree = []

        # Horizontal arm
        arm1 = cylinder(o, pipe_r, arm_len)
        bore1 = cylinder(o, bore_r, arm_len + 2)
        bore1 = translate(o, bore1, 0, 0, -1)
        arm1 = cut(o, arm1, bore1, "arm1_bore")
        solid = arm1
        tree.append(node("arm1", "Arm 1"))

        # Second arm at angle
        a = math.radians(angle)
        dir_x, dir_z = math.cos(a), math.sin(a)
        ax2 = o["gp_Ax2"](
            o["gp_Pnt"](arm_len * dir_x, 0, arm_len * dir_z),
            o["gp_Dir"](-dir_z, 0, dir_x)
        )
        arm2 = cylinder(o, pipe_r, arm_len, ax2)
        bore2_ax2 = o["gp_Ax2"](
            o["gp_Pnt"](arm_len * dir_x - dir_z, 0, arm_len * dir_z + dir_x),
            o["gp_Dir"](-dir_z, 0, dir_x)
        )
        bore2 = cylinder(o, bore_r, arm_len + 2, bore2_ax2)
        arm2 = cut(o, arm2, bore2, "arm2_bore")
        solid = fuse(o, solid, arm2, "elbow_fuse")
        tree.append(node("arm2", "Arm 2"))

        # Flanges
        fl1 = cylinder(o, flange_r, flange_t)
        fl1 = translate(o, fl1, 0, 0, -flange_t)
        bore_fl1 = cylinder(o, bore_r, flange_t + 2)
        bore_fl1 = translate(o, bore_fl1, 0, 0, -flange_t - 1)
        fl1 = cut(o, fl1, bore_fl1, "fl1_bore")
        if bolt_cnt > 0:
            fl1, ht = bolt_holes_cut(o, fl1, bolt_d/2, bolt_cnt, flange_r * 0.75, -flange_t - 1, flange_t + 2, "fl1_bolt")
        solid = fuse(o, solid, fl1, "fl1_fuse")
        tree.append(node("flanges", "Flanges"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("elbow_fitting", params, _build)


# ── T-Fitting ──────────────────────────────────────────────────────────────────

def build_t_fitting_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        pipe_r   = float(p.get("outer_diameter", 60)) / 2
        bore_r   = float(p.get("bore_diameter", 40)) / 2
        arm_len  = float(p.get("arm_length", 80))
        branch_r = float(p.get("branch_diameter", pipe_r))
        branch_bore = float(p.get("branch_bore_diameter", bore_r))
        flange_r = float(p.get("flange_diameter", pipe_r * 1.5))
        flange_t = float(p.get("flange_thickness", 12))
        bolt_cnt = int(p.get("bolt_hole_count", 4))
        bolt_d   = float(p.get("bolt_hole_diameter", 10))
        tree = []

        # Main run
        run = cylinder(o, pipe_r, arm_len * 2)
        run = translate(o, run, 0, 0, -arm_len)
        bore_run = cylinder(o, bore_r, arm_len * 2 + 2)
        bore_run = translate(o, bore_run, 0, 0, -arm_len - 1)
        run = cut(o, run, bore_run, "run_bore")
        solid = run
        tree.append(node("main_run", "Main Run"))

        # Branch (perpendicular)
        branch_ax2 = o["gp_Ax2"](o["gp_Pnt"](0, 0, 0), o["gp_Dir"](1, 0, 0))
        branch = cylinder(o, branch_r, arm_len, branch_ax2)
        branch_bore_ax2 = o["gp_Ax2"](o["gp_Pnt"](-1, 0, 0), o["gp_Dir"](1, 0, 0))
        branch_b = cylinder(o, branch_bore, arm_len + 2, branch_bore_ax2)
        branch = cut(o, branch, branch_b, "branch_bore")
        solid = fuse(o, solid, branch, "branch_fuse")
        tree.append(node("branch", "Branch"))

        # Flanges on all 3 ends
        for off, ax_dir in [
            (-arm_len - flange_t, (0, 0, 1)),
            (arm_len, (0, 0, 1)),
        ]:
            fl = cylinder(o, flange_r, flange_t)
            fl = translate(o, fl, 0, 0, off)
            fl_bore = cylinder(o, bore_r, flange_t + 2)
            fl_bore = translate(o, fl_bore, 0, 0, off - 1)
            fl = cut(o, fl, fl_bore, "fl_bore")
            solid = fuse(o, solid, fl, "fl_fuse")
        tree.append(node("flanges", "Flanges"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("t_fitting", params, _build)


# ── Housing ────────────────────────────────────────────────────────────────────

def build_housing_occ(params: dict) -> tuple[dict, list[dict]]:
    def _build(p):
        o = occ()
        L       = float(p.get("length", 150))
        W       = float(p.get("width", 100))
        H       = float(p.get("height", 80))
        wall    = float(p.get("wall_thickness", 8))
        bore_d  = float(p.get("bore_diameter", 50))
        bolt_cnt= int(p.get("bolt_hole_count", 4))
        bolt_d  = float(p.get("bolt_hole_diameter", 10))
        bolt_cr = float(p.get("bolt_circle_diameter", min(L, W) * 0.6)) / 2
        split_h = float(p.get("split_height", H / 2))
        tree = []

        solid = box(o, L, W, H)
        solid = translate(o, solid, -L/2, -W/2, 0)
        tree.append(node("housing_body", "Housing Body"))

        # Bore
        bore_tool = cylinder(o, bore_d/2, H + 2)
        bore_tool = translate(o, bore_tool, 0, 0, -1)
        solid = cut(o, solid, bore_tool, "bore_cut")
        tree.append(node("bore_cut", "Bore Cut"))

        # Hollow interior (cavity)
        if wall > 0 and wall < min(L, W, H) / 4:
            cavity = box(o, L - wall*2, W - wall*2, H - wall)
            cavity = translate(o, cavity, -L/2 + wall, -W/2 + wall, wall)
            solid = cut(o, solid, cavity, "cavity_cut")
            tree.append(node("cavity", "Interior Cavity"))

        # Bolt holes on top face
        if bolt_cnt > 0:
            solid, ht = bolt_holes_cut(o, solid, bolt_d/2, bolt_cnt, bolt_cr, H - wall, wall + 2, "bolt_hole")
            tree.extend(ht)

        tree.append(node("fillets", "Fillets", "failed"))
        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("housing", params, _build)


# ── Custom (generic) ───────────────────────────────────────────────────────────

def build_custom_occ(params: dict) -> tuple[dict, list[dict]]:
    """Best-effort OCC build for unrecognised shapes."""
    def _build(p):
        o = occ()
        tree = []
        od = p.get("outer_diameter") or p.get("outer_body_diameter")
        h  = p.get("height") or p.get("overall_height") or p.get("length")

        if od and h:
            inner_d = p.get("bore_diameter") or p.get("inner_diameter") or 0
            od, h, inner_d = float(od), float(h), float(inner_d)
            solid = cylinder(o, od/2, h)
            if inner_d > 0 and inner_d < od:
                bore_tool = cylinder(o, inner_d/2, h + 2)
                bore_tool = translate(o, bore_tool, 0, 0, -1)
                solid = cut(o, solid, bore_tool, "bore_cut")
            tree.append(node("body", "Body"))
        else:
            L  = float(p.get("length", 100))
            W  = float(p.get("width", 60))
            Ht = float(p.get("height", 40))
            solid = box(o, L, W, Ht)
            solid = translate(o, solid, -L/2, -W/2, 0)
            tree.append(node("body", "Body"))

        solid = validate_shape(o, solid)
        return serialise(solid), tree

    return _wrap("custom", params, _build)


# ── Dispatch ───────────────────────────────────────────────────────────────────

OCC_BUILDERS = {
    "box":           build_box_occ,
    "plate":         build_plate_occ,
    "pipe_flange":   build_pipe_flange_occ,
    "shaft":         build_shaft_occ,
    "bushing":       build_bushing_occ,
    "bracket":       build_bracket_occ,
    "gear":          build_gear_occ,
    "elbow_fitting": build_elbow_occ,
    "t_fitting":     build_t_fitting_occ,
    "housing":       build_housing_occ,
    "custom":        build_custom_occ,
}
