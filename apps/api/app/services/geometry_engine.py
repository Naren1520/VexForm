import math
import time
import logging
from typing import List, Tuple

from app.models.params import LowerValveBodyParams
from app.models.errors import ValidationError

logger = logging.getLogger(__name__)


class GeometryError(RuntimeError):
    def __init__(self, operation_name: str, detail: str = ""):
        self.operation_name = operation_name
        super().__init__(f"{operation_name}: {detail}" if detail else operation_name)


# ── Feature tree node (simple dict for serialisation) ──────────────────────────

def _node(node_id: str, label: str, status: str) -> dict:
    return {"id": node_id, "label": label, "status": status}


def _assert_done(op, name: str):
    """Raise GeometryError if a Boolean operation failed."""
    try:
        done = op.IsDone()
    except Exception as exc:
        raise GeometryError(name, f"IsDone() raised: {exc}") from exc
    if not done:
        raise GeometryError(name, "IsDone() returned False")
    shape = op.Shape()
    if shape is None or shape.IsNull():
        raise GeometryError(name, "produced a null shape")
    return shape


# ── OCC imports (lazy -expensive, only loaded when engine is invoked) ─────────

def _occ_imports():
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
    from OCC.Core.BRepCheck import BRepCheck_Analyzer
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_EDGE
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
    from OCC.Core.TopLoc import TopLoc_Location
    from OCC.Core.BRep import BRep_Tool
    return {
        "BRepPrimAPI_MakeCylinder": BRepPrimAPI_MakeCylinder,
        "BRepAlgoAPI_Fuse": BRepAlgoAPI_Fuse,
        "BRepAlgoAPI_Cut": BRepAlgoAPI_Cut,
        "BRepBuilderAPI_Transform": BRepBuilderAPI_Transform,
        "BRepFilletAPI_MakeFillet": BRepFilletAPI_MakeFillet,
        "BRepFilletAPI_MakeChamfer": BRepFilletAPI_MakeChamfer,
        "BRepCheck_Analyzer": BRepCheck_Analyzer,
        "BRepMesh_IncrementalMesh": BRepMesh_IncrementalMesh,
        "TopAbs_SOLID": TopAbs_SOLID,
        "TopAbs_FACE": TopAbs_FACE,
        "TopAbs_EDGE": TopAbs_EDGE,
        "TopExp_Explorer": TopExp_Explorer,
        "gp_Ax2": gp_Ax2,
        "gp_Pnt": gp_Pnt,
        "gp_Dir": gp_Dir,
        "gp_Trsf": gp_Trsf,
        "gp_Vec": gp_Vec,
        "TopLoc_Location": TopLoc_Location,
        "BRep_Tool": BRep_Tool,
    }


def _make_cylinder(occ, radius: float, height: float,
                   ax2=None) -> object:
    """Create a cylinder solid, optionally positioned with a custom gp_Ax2."""
    if ax2 is None:
        return occ["BRepPrimAPI_MakeCylinder"](radius, height).Shape()
    else:
        return occ["BRepPrimAPI_MakeCylinder"](ax2, radius, height).Shape()


def _translate(occ, shape, dx: float, dy: float, dz: float) -> object:
    """Translate a shape by (dx, dy, dz)."""
    trsf = occ["gp_Trsf"]()
    trsf.SetTranslation(occ["gp_Vec"](dx, dy, dz))
    builder = occ["BRepBuilderAPI_Transform"](shape, trsf, True)
    return builder.Shape()


def _fuse(occ, base, tool, name: str) -> object:
    op = occ["BRepAlgoAPI_Fuse"](base, tool)
    return _assert_done(op, f"BRepAlgoAPI_Fuse: {name}")


def _cut(occ, base, tool, name: str) -> object:
    op = occ["BRepAlgoAPI_Cut"](base, tool)
    return _assert_done(op, f"BRepAlgoAPI_Cut: {name}")


def build_lower_valve_body(
    params: LowerValveBodyParams,
) -> Tuple[object, List[dict]]:
    """Construct the Lower Valve Body solid model using Boolean operations.

    Returns (TopoDS_Shape, feature_tree_list).
    Raises GeometryError on any Boolean operation failure.
    Enforces a 60-second wall-clock limit.
    """
    t0 = time.perf_counter()
    occ = _occ_imports()
    tree: List[dict] = []

    r = params  # shorthand

    # Derived heights (from blueprint section A-A analysis)
    top_flange_height = 8.0          # 8mm flange plate above body shoulder
    bottom_flange_height = 6.0       # 6mm bottom flange plate
    side_boss_length = 25.0          # side port boss protrusion length
    side_port_bore_length = side_boss_length + r.outer_body_diameter  # punch all the way through

    # Bolt circle radii
    top_bolt_circle_r = (r.top_flange_outer_diameter / 2) * 0.70  # ~14mm radius
    bottom_bolt_circle_r = r.bottom_flange_bolt_circle_diameter / 2  # 26mm

    # ─── Step 1: Base cylinder ────────────────────────────────────────────────
    try:
        base = _make_cylinder(occ, r.outer_body_diameter / 2, r.overall_height)
        tree.append(_node("base_cylinder", "Base Cylinder", "success"))
        logger.debug("Step 1 complete: base cylinder")
    except Exception as exc:
        tree.append(_node("base_cylinder", "Base Cylinder", "failed"))
        raise GeometryError("BRepPrimAPI_MakeCylinder: base_cylinder", str(exc)) from exc

    # ─── Step 2: Top flange extrusion (fuse) ─────────────────────────────────
    try:
        top_flange = _make_cylinder(occ, r.top_flange_outer_diameter / 2, top_flange_height)
        top_flange = _translate(occ, top_flange, 0, 0, r.overall_height)
        solid = _fuse(occ, base, top_flange, "top_flange_extrusion")
        tree.append(_node("top_flange_extrusion", "Top Flange Extrusion", "success"))
        logger.debug("Step 2 complete: top flange")
    except GeometryError:
        tree.append(_node("top_flange_extrusion", "Top Flange Extrusion", "failed"))
        raise

    # ─── Step 3: Bottom flange extrusion (fuse) ──────────────────────────────
    try:
        bot_flange = _make_cylinder(occ, r.bottom_flange_outer_flange_diameter / 2, bottom_flange_height)
        bot_flange = _translate(occ, bot_flange, 0, 0, -bottom_flange_height)
        solid = _fuse(occ, solid, bot_flange, "bottom_flange_extrusion")
        tree.append(_node("bottom_flange_extrusion", "Bottom Flange Extrusion", "success"))
        logger.debug("Step 3 complete: bottom flange")
    except GeometryError:
        tree.append(_node("bottom_flange_extrusion", "Bottom Flange Extrusion", "failed"))
        raise

    # ─── Step 4: Side port boss (fuse) ───────────────────────────────────────
    # The side port is at 135° from the main axis (in the horizontal XZ plane)
    # offset from the top by side_port_offset_from_top
    try:
        angle_rad = math.radians(r.side_port_angle_degrees)
        # Boss direction vector in XZ plane
        boss_dx = math.sin(angle_rad)  # X component
        boss_dz = math.cos(angle_rad)  # Z component (but this is the horizontal axis)
        # Actually the side port extends radially outward at the given angle
        # The main axis is Z. Side port is horizontal at angle from X axis.
        boss_dir = occ["gp_Dir"](math.cos(angle_rad), math.sin(angle_rad), 0.0)
        boss_origin = occ["gp_Pnt"](0.0, 0.0, r.overall_height - r.side_port_offset_from_top)
        boss_ax2 = occ["gp_Ax2"](boss_origin, boss_dir)
        side_boss = _make_cylinder(occ, r.side_port_flange_outer_diameter / 2, side_boss_length, boss_ax2)
        solid = _fuse(occ, solid, side_boss, "side_port_boss")
        tree.append(_node("side_port_boss", "Side Port Boss", "success"))
        logger.debug("Step 4 complete: side port boss")
    except GeometryError:
        tree.append(_node("side_port_boss", "Side Port Boss", "failed"))
        raise

    # ─── Step 5: Upper bore cut ───────────────────────────────────────────────
    try:
        upper_bore = _make_cylinder(occ, r.main_bore_upper_diameter / 2, r.overall_height + top_flange_height + 2)
        upper_bore = _translate(occ, upper_bore, 0, 0, -1)
        solid = _cut(occ, solid, upper_bore, "upper_bore_cut")
        tree.append(_node("upper_bore_cut", "Upper Bore Cut", "success"))
        logger.debug("Step 5 complete: upper bore cut")
    except GeometryError:
        tree.append(_node("upper_bore_cut", "Upper Bore Cut", "failed"))
        raise

    # ─── Step 6: Lower bore cut (smaller diameter, from bottom) ──────────────
    try:
        lower_bore_height = r.overall_height / 2  # lower half has smaller bore
        lower_bore = _make_cylinder(occ, r.main_bore_lower_inner_diameter / 2, lower_bore_height + bottom_flange_height + 2)
        lower_bore = _translate(occ, lower_bore, 0, 0, -bottom_flange_height - 1)
        solid = _cut(occ, solid, lower_bore, "lower_bore_cut")
        tree.append(_node("lower_bore_cut", "Lower Bore Cut", "success"))
        logger.debug("Step 6 complete: lower bore cut")
    except GeometryError:
        tree.append(_node("lower_bore_cut", "Lower Bore Cut", "failed"))
        raise

    # ─── Step 7: Side port bore cut ──────────────────────────────────────────
    try:
        bore_origin = occ["gp_Pnt"](-side_boss_length, 0.0, r.overall_height - r.side_port_offset_from_top)
        bore_dir = occ["gp_Dir"](math.cos(angle_rad), math.sin(angle_rad), 0.0)
        bore_ax2 = occ["gp_Ax2"](bore_origin, bore_dir)
        side_bore = _make_cylinder(occ, r.side_port_bore_diameter / 2, side_port_bore_length, bore_ax2)
        solid = _cut(occ, solid, side_bore, "side_port_bore_cut")
        tree.append(_node("side_port_bore_cut", "Side Port Bore Cut", "success"))
        logger.debug("Step 7 complete: side port bore cut")
    except GeometryError:
        tree.append(_node("side_port_bore_cut", "Side Port Bore Cut", "failed"))
        raise

    # ─── Step 8: Top bolt holes cut ──────────────────────────────────────────
    try:
        for i in range(r.top_flange_bolt_hole_count):
            hole_angle = i * (2 * math.pi / r.top_flange_bolt_hole_count)
            hx = top_bolt_circle_r * math.cos(hole_angle)
            hy = top_bolt_circle_r * math.sin(hole_angle)
            hole = _make_cylinder(occ, r.top_flange_bolt_hole_diameter / 2, r.top_flange_bolt_hole_depth + 2)
            hole = _translate(occ, hole, hx, hy, r.overall_height + top_flange_height - r.top_flange_bolt_hole_depth)
            solid = _cut(occ, solid, hole, f"top_bolt_hole_{i}")
        tree.append(_node("top_bolt_holes_cut", "Top Bolt Holes Cut", "success"))
        logger.debug("Step 8 complete: top bolt holes")
    except GeometryError:
        tree.append(_node("top_bolt_holes_cut", "Top Bolt Holes Cut", "failed"))
        raise

    # ─── Step 9: Top counterbores cut ────────────────────────────────────────
    try:
        for i in range(r.top_flange_bolt_hole_count):
            hole_angle = i * (2 * math.pi / r.top_flange_bolt_hole_count)
            hx = top_bolt_circle_r * math.cos(hole_angle)
            hy = top_bolt_circle_r * math.sin(hole_angle)
            cb = _make_cylinder(occ, r.top_flange_counterbore_diameter / 2, r.top_flange_counterbore_depth + 1)
            cb = _translate(occ, cb, hx, hy, r.overall_height + top_flange_height - r.top_flange_counterbore_depth)
            solid = _cut(occ, solid, cb, f"top_counterbore_{i}")
        tree.append(_node("top_counterbores_cut", "Top Counterbores Cut", "success"))
        logger.debug("Step 9 complete: top counterbores")
    except GeometryError:
        tree.append(_node("top_counterbores_cut", "Top Counterbores Cut", "failed"))
        raise

    # ─── Step 10: Bottom bolt holes cut ──────────────────────────────────────
    try:
        for i in range(r.bottom_flange_bolt_hole_count):
            hole_angle = i * (2 * math.pi / r.bottom_flange_bolt_hole_count)
            hx = bottom_bolt_circle_r * math.cos(hole_angle)
            hy = bottom_bolt_circle_r * math.sin(hole_angle)
            hole = _make_cylinder(occ, r.bottom_flange_bolt_hole_diameter / 2, bottom_flange_height + 2)
            hole = _translate(occ, hole, hx, hy, -bottom_flange_height - 1)
            solid = _cut(occ, solid, hole, f"bottom_bolt_hole_{i}")
        tree.append(_node("bottom_bolt_holes_cut", "Bottom Bolt Holes Cut", "success"))
        logger.debug("Step 10 complete: bottom bolt holes")
    except GeometryError:
        tree.append(_node("bottom_bolt_holes_cut", "Bottom Bolt Holes Cut", "failed"))
        raise

    # ─── Step 11: Bottom counterbores cut ────────────────────────────────────
    try:
        for i in range(r.bottom_flange_bolt_hole_count):
            hole_angle = i * (2 * math.pi / r.bottom_flange_bolt_hole_count)
            hx = bottom_bolt_circle_r * math.cos(hole_angle)
            hy = bottom_bolt_circle_r * math.sin(hole_angle)
            cb = _make_cylinder(occ, r.bottom_flange_counterbore_diameter / 2, r.bottom_flange_counterbore_depth + 1)
            cb = _translate(occ, cb, hx, hy, -r.bottom_flange_counterbore_depth)
            solid = _cut(occ, solid, cb, f"bottom_counterbore_{i}")
        tree.append(_node("bottom_counterbores_cut", "Bottom Counterbores Cut", "success"))
        logger.debug("Step 11 complete: bottom counterbores")
    except GeometryError:
        tree.append(_node("bottom_counterbores_cut", "Bottom Counterbores Cut", "failed"))
        raise

    # ─── Step 12: Side port bolt holes cut ───────────────────────────────────
    try:
        # Two bolt holes perpendicular to the side port bore direction
        perp_dir_x = -math.sin(angle_rad)
        perp_dir_y = math.cos(angle_rad)
        half_spacing = r.side_port_bolt_hole_spacing / 2
        boss_center_x = (r.outer_body_diameter / 2 + side_boss_length / 2) * math.cos(angle_rad)
        boss_center_y = (r.outer_body_diameter / 2 + side_boss_length / 2) * math.sin(angle_rad)
        boss_center_z = r.overall_height - r.side_port_offset_from_top

        for sign in (-1, 1):
            bx = boss_center_x + sign * half_spacing * perp_dir_x
            by = boss_center_y + sign * half_spacing * perp_dir_y
            # Hole direction: along boss axis
            hole_dir = occ["gp_Dir"](math.cos(angle_rad), math.sin(angle_rad), 0.0)
            hole_origin = occ["gp_Pnt"](
                bx - side_boss_length * math.cos(angle_rad),
                by - side_boss_length * math.sin(angle_rad),
                boss_center_z - r.side_port_bolt_hole_diameter / 2,
            )
            hole_ax2 = occ["gp_Ax2"](hole_origin, hole_dir)
            sp_hole = _make_cylinder(occ, r.side_port_bolt_hole_diameter / 2, side_boss_length + 4, hole_ax2)
            solid = _cut(occ, solid, sp_hole, f"side_port_bolt_hole_{sign}")
        tree.append(_node("side_port_bolt_holes_cut", "Side Port Bolt Holes Cut", "success"))
        logger.debug("Step 12 complete: side port bolt holes")
    except GeometryError:
        tree.append(_node("side_port_bolt_holes_cut", "Side Port Bolt Holes Cut", "failed"))
        raise

    # ─── Steps 13–14: Fillets and chamfers ────────────────────────────────────
    # Note: OCC fillet/chamfer on complex Boolean solids can be unstable.
    # We apply them defensively and fall back gracefully if they fail.
    try:
        fillet_builder = occ["BRepFilletAPI_MakeFillet"](solid)
        # Collect all edges and apply R1mm fillet to short transition edges
        edge_explorer = occ["TopExp_Explorer"](solid, occ["TopAbs_EDGE"])
        edges_added = 0
        while edge_explorer.More():
            try:
                fillet_builder.Add(r.unspecified_fillet_radius, edge_explorer.Current())
                edges_added += 1
            except Exception:
                pass
            edge_explorer.Next()

        if edges_added > 0:
            fillet_builder.Build()
            if fillet_builder.IsDone() and not fillet_builder.Shape().IsNull():
                solid = fillet_builder.Shape()
                tree.append(_node("fillets", "Fillets", "success"))
                logger.debug("Step 13 complete: fillets applied")
            else:
                logger.warning("Fillet builder finished but shape is invalid; skipping fillets")
                tree.append(_node("fillets", "Fillets", "failed"))
        else:
            tree.append(_node("fillets", "Fillets", "failed"))
    except Exception as exc:
        logger.warning(f"Fillet operation failed (non-fatal): {exc}")
        tree.append(_node("fillets", "Fillets", "failed"))

    # Chamfers: skip if fillet already failed (shape may be unstable)
    try:
        chamfer_builder = occ["BRepFilletAPI_MakeChamfer"](solid)
        edge_explorer2 = occ["TopExp_Explorer"](solid, occ["TopAbs_EDGE"])
        edges_added = 0
        while edge_explorer2.More():
            try:
                chamfer_builder.Add(r.other_chamfer, edge_explorer2.Current())
                edges_added += 1
            except Exception:
                pass
            edge_explorer2.Next()

        if edges_added > 0:
            chamfer_builder.Build()
            if chamfer_builder.IsDone() and not chamfer_builder.Shape().IsNull():
                solid = chamfer_builder.Shape()
                tree.append(_node("chamfers", "Chamfers", "success"))
                logger.debug("Step 14 complete: chamfers applied")
            else:
                tree.append(_node("chamfers", "Chamfers", "failed"))
        else:
            tree.append(_node("chamfers", "Chamfers", "failed"))
    except Exception as exc:
        logger.warning(f"Chamfer operation failed (non-fatal): {exc}")
        tree.append(_node("chamfers", "Chamfers", "failed"))

    # ─── Step 15: Shape validation ───────────────────────────────────────────
    elapsed = time.perf_counter() - t0
    if elapsed > 60.0:
        raise GeometryError("build_lower_valve_body", f"exceeded 60-second timeout ({elapsed:.1f}s)")

    checker = occ["BRepCheck_Analyzer"](solid)
    # Note: IsValid() on a compound may be False even when sub-solids are valid.
    # We check validity after extracting the solid below if needed.
    is_valid = checker.IsValid()

    if solid.ShapeType() != occ["TopAbs_SOLID"]:
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_SOLID as _SOLID
        explorer = TopExp_Explorer(solid, _SOLID)
        if explorer.More():
            solid = explorer.Current()
            logger.info("Extracted solid from compound shape")
            checker2 = occ["BRepCheck_Analyzer"](solid)
            is_valid = checker2.IsValid()
        else:
            raise GeometryError(
                "BRepCheck_Analyzer",
                f"shape type is not TopAbs_SOLID (got {solid.ShapeType()}) and no solid found in compound",
            )

    if not is_valid:
        raise GeometryError(
            "BRepCheck_Analyzer",
            "shape is invalid (not manifold or has self-intersections)",
        )

    logger.info(f"Geometry built successfully in {elapsed:.2f}s")
    return solid, tree

