"""Generic OCC construction program executor.

Gemini outputs a JSON "construction program" — a list of geometric operations.
This module executes that program against OCC to produce a solid model.

The program is a list of steps, each with an "op" field:

Additive ops (always produce a new solid or modify current):
  cylinder   r, h, [x, y, z, dx, dy, dz]
  box        dx, dy, dz, [x, y, z]
  sphere     r, [x, y, z]
  cone       r1, r2, h, [x, y, z]
  torus      r_major, r_minor, [x, y, z]

Boolean ops (modify current solid):
  fuse       — fuse current solid with last-added tool
  cut        — cut last-added tool from current solid

Convenience compound ops (internally expand to primitives + booleans):
  add_cylinder     r, h, [x, y, z]  — fuse a cylinder onto the solid
  cut_cylinder     r, h, [x, y, z]  — cut a cylinder from the solid
  add_box          dx, dy, dz, [x, y, z]
  cut_box          dx, dy, dz, [x, y, z]
  bolt_circle      r_hole, count, r_circle, z, depth  — cut N bolt holes
  fillet_edges     radius, [max_edges]
  chamfer_edges    size, [max_edges]

Example program (flanged bushing):
[
  {"op": "cylinder",     "r": 40,  "h": 60,  "label": "Outer body"},
  {"op": "cut_cylinder", "r": 20,  "h": 62,  "x": 0, "y": 0, "z": -1, "label": "Bore"},
  {"op": "add_cylinder", "r": 70,  "h": 12,  "x": 0, "y": 0, "z": 60, "label": "Flange"},
  {"op": "cut_cylinder", "r": 20,  "h": 14,  "x": 0, "y": 0, "z": 59, "label": "Flange bore"},
  {"op": "bolt_circle",  "r_hole": 7, "count": 6, "r_circle": 55, "z": 59, "depth": 14, "label": "Bolt holes"}
]
"""
from __future__ import annotations
import math
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── OCC lazy imports ───────────────────────────────────────────────────────────

def _occ():
    from OCC.Core.BRepPrimAPI import (
        BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox,
        BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCone,
        BRepPrimAPI_MakeTorus,
    )
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
    from OCC.Core.BRepCheck import BRepCheck_Analyzer
    from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_EDGE
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
    from OCC.Core.GeomAbs import GeomAbs_Circle
    from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
    return dict(
        Cyl=BRepPrimAPI_MakeCylinder, Box=BRepPrimAPI_MakeBox,
        Sphere=BRepPrimAPI_MakeSphere, Cone=BRepPrimAPI_MakeCone,
        Torus=BRepPrimAPI_MakeTorus,
        Fuse=BRepAlgoAPI_Fuse, Cut=BRepAlgoAPI_Cut,
        Xform=BRepBuilderAPI_Transform,
        Fillet=BRepFilletAPI_MakeFillet,
        Chamfer=BRepFilletAPI_MakeChamfer,
        Check=BRepCheck_Analyzer,
        TopAbs_SOLID=TopAbs_SOLID, TopAbs_EDGE=TopAbs_EDGE,
        Explorer=TopExp_Explorer,
        Ax2=gp_Ax2, Pnt=gp_Pnt, Dir=gp_Dir, Trsf=gp_Trsf, Vec=gp_Vec,
        GeomAbs_Circle=GeomAbs_Circle, Curve=BRepAdaptor_Curve,
    )

# ── Helpers ────────────────────────────────────────────────────────────────────

def _assert_done(op, name):
    if not op.IsDone():
        raise RuntimeError(f"{name}: IsDone() returned False")
    s = op.Shape()
    if s is None or s.IsNull():
        raise RuntimeError(f"{name}: null shape")
    return s


def _translate(o, shape, x, y, z):
    if x == 0 and y == 0 and z == 0:
        return shape
    t = o["Trsf"]()
    t.SetTranslation(o["Vec"](x, y, z))
    return o["Xform"](shape, t, True).Shape()


def _make_cylinder(o, r, h, x=0, y=0, z=0, dx=0, dy=0, dz=1):
    """Cylinder with optional position and direction."""
    norm = math.sqrt(dx*dx + dy*dy + dz*dz)
    if norm < 1e-9:
        dx, dy, dz = 0, 0, 1
    else:
        dx /= norm; dy /= norm; dz /= norm

    if dx == 0 and dy == 0 and dz == 1 and x == 0 and y == 0 and z == 0:
        return o["Cyl"](r, h).Shape()

    ax2 = o["Ax2"](o["Pnt"](x, y, z), o["Dir"](dx, dy, dz))
    return o["Cyl"](ax2, r, h).Shape()


def _make_box(o, dx, dy, dz, x=0, y=0, z=0, centered=False):
    if centered:
        x -= dx / 2; y -= dy / 2
    s = o["Box"](dx, dy, dz).Shape()
    return _translate(o, s, x, y, z)


def _fuse(o, base, tool):
    return _assert_done(o["Fuse"](base, tool), "Fuse")


def _cut(o, base, tool):
    return _assert_done(o["Cut"](base, tool), "Cut")


def _apply_fillet(o, solid, radius, max_edges=20):
    try:
        fb = o["Fillet"](solid)
        exp = o["Explorer"](solid, o["TopAbs_EDGE"])
        added = 0
        while exp.More() and added < max_edges:
            fb.Add(radius, exp.Current())
            added += 1
            exp.Next()
        if added > 0:
            fb.Build()
            if fb.IsDone() and not fb.Shape().IsNull():
                return fb.Shape()
    except Exception as e:
        logger.debug(f"Fillet failed: {e}")
    return solid


def _apply_chamfer(o, solid, size, max_edges=12):
    try:
        cb = o["Chamfer"](solid)
        exp = o["Explorer"](solid, o["TopAbs_EDGE"])
        added = 0
        while exp.More() and added < max_edges:
            cb.Add(size, exp.Current())
            added += 1
            exp.Next()
        if added > 0:
            cb.Build()
            if cb.IsDone() and not cb.Shape().IsNull():
                return cb.Shape()
    except Exception as e:
        logger.debug(f"Chamfer failed: {e}")
    return solid


def _validate_solid(o, solid):
    """Extract first solid from compound if needed."""
    if solid.ShapeType() != o["TopAbs_SOLID"]:
        from OCC.Core.TopAbs import TopAbs_SOLID as _S
        exp = o["Explorer"](solid, _S)
        if exp.More():
            return exp.Current()
    return solid


# ── Main executor ──────────────────────────────────────────────────────────────

def execute_program(program: list[dict]) -> tuple[Any, list[dict]]:
    """Execute a construction program and return (TopoDS_Shape, feature_tree).

    Raises on fatal errors. Non-fatal step failures are logged and skipped.
    """
    o = _occ()
    solid = None
    tree: list[dict] = []
    t0 = time.perf_counter()

    def _node(step_id, label, status="success"):
        return {"id": step_id, "label": label, "status": status}

    for i, step in enumerate(program):
        if time.perf_counter() - t0 > 90:
            logger.warning("Construction program timeout at step %d", i)
            break

        op = step.get("op", "").lower().strip()
        label = step.get("label", op)
        step_id = f"step_{i:02d}_{op}"

        # ── Extract common positional params ───────────────────────────────
        x  = float(step.get("x",  0))
        y  = float(step.get("y",  0))
        z  = float(step.get("z",  0))
        dx = float(step.get("dx_dir", 0))
        dy = float(step.get("dy_dir", 0))
        dz = float(step.get("dz_dir", 1))

        try:
            # ── Primitives (start or replace solid) ───────────────────────
            if op == "cylinder":
                r = float(step["r"]); h = float(step["h"])
                shape = _make_cylinder(o, r, h, x, y, z, dx, dy, dz)
                solid = shape if solid is None else _fuse(o, solid, shape)
                tree.append(_node(step_id, label))

            elif op == "box":
                sx = float(step["sx"]); sy = float(step["sy"]); sz = float(step["sz"])
                centered = bool(step.get("centered", True))
                shape = _make_box(o, sx, sy, sz, x, y, z, centered)
                solid = shape if solid is None else _fuse(o, solid, shape)
                tree.append(_node(step_id, label))

            elif op == "sphere":
                r = float(step["r"])
                from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
                ax2 = gp_Ax2(gp_Pnt(x, y, z), gp_Dir(0, 0, 1))
                shape = o["Sphere"](ax2, r).Shape()
                solid = shape if solid is None else _fuse(o, solid, shape)
                tree.append(_node(step_id, label))

            elif op == "cone":
                r1 = float(step["r1"]); r2 = float(step["r2"]); h = float(step["h"])
                ax2 = o["Ax2"](o["Pnt"](x, y, z), o["Dir"](dx, dy, dz))
                shape = o["Cone"](ax2, r1, r2, h).Shape()
                solid = shape if solid is None else _fuse(o, solid, shape)
                tree.append(_node(step_id, label))

            elif op == "torus":
                r_maj = float(step["r_major"]); r_min = float(step["r_minor"])
                ax2 = o["Ax2"](o["Pnt"](x, y, z), o["Dir"](dx, dy, dz))
                shape = o["Torus"](ax2, r_maj, r_min).Shape()
                solid = shape if solid is None else _fuse(o, solid, shape)
                tree.append(_node(step_id, label))

            # ── Additive compound ops ──────────────────────────────────────
            elif op == "add_cylinder":
                if solid is None:
                    raise RuntimeError("add_cylinder requires an existing solid")
                r = float(step["r"]); h = float(step["h"])
                tool = _make_cylinder(o, r, h, x, y, z, dx, dy, dz)
                solid = _fuse(o, solid, tool)
                tree.append(_node(step_id, label))

            elif op == "add_box":
                if solid is None:
                    raise RuntimeError("add_box requires an existing solid")
                sx = float(step["sx"]); sy = float(step["sy"]); sz = float(step["sz"])
                centered = bool(step.get("centered", True))
                tool = _make_box(o, sx, sy, sz, x, y, z, centered)
                solid = _fuse(o, solid, tool)
                tree.append(_node(step_id, label))

            # ── Subtractive compound ops ───────────────────────────────────
            elif op == "cut_cylinder":
                if solid is None:
                    raise RuntimeError("cut_cylinder requires an existing solid")
                r = float(step["r"]); h = float(step["h"])
                tool = _make_cylinder(o, r, h, x, y, z, dx, dy, dz)
                solid = _cut(o, solid, tool)
                tree.append(_node(step_id, label))

            elif op == "cut_box":
                if solid is None:
                    raise RuntimeError("cut_box requires an existing solid")
                sx = float(step["sx"]); sy = float(step["sy"]); sz = float(step["sz"])
                centered = bool(step.get("centered", True))
                tool = _make_box(o, sx, sy, sz, x, y, z, centered)
                solid = _cut(o, solid, tool)
                tree.append(_node(step_id, label))

            elif op == "cut_sphere":
                if solid is None:
                    raise RuntimeError("cut_sphere requires an existing solid")
                r = float(step["r"])
                from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
                ax2 = gp_Ax2(gp_Pnt(x, y, z), gp_Dir(0, 0, 1))
                tool = o["Sphere"](ax2, r).Shape()
                solid = _cut(o, solid, tool)
                tree.append(_node(step_id, label))

            # ── Bolt / hole pattern ────────────────────────────────────────
            elif op == "bolt_circle":
                if solid is None:
                    raise RuntimeError("bolt_circle requires an existing solid")
                r_hole   = float(step["r_hole"])
                count    = int(step["count"])
                r_circle = float(step["r_circle"])
                depth    = float(step.get("depth", 20))
                z_start  = float(step.get("z", z))

                for j in range(count):
                    angle = j * (2 * math.pi / count)
                    hx = r_circle * math.cos(angle)
                    hy = r_circle * math.sin(angle)
                    hole = _make_cylinder(o, r_hole, depth + 2, hx, hy, z_start - 1)
                    solid = _cut(o, solid, hole)
                tree.append(_node(step_id, label))

            elif op == "rectangular_hole_pattern":
                # Grid pattern of holes
                if solid is None:
                    raise RuntimeError("rectangular_hole_pattern requires solid")
                r_hole  = float(step["r_hole"])
                cols    = int(step.get("cols", 2))
                rows    = int(step.get("rows", 2))
                col_sp  = float(step["col_spacing"])
                row_sp  = float(step["row_spacing"])
                depth   = float(step.get("depth", 20))
                z_start = float(step.get("z", z))

                for row in range(rows):
                    for col in range(cols):
                        hx = x + (col - (cols - 1) / 2) * col_sp
                        hy = y + (row - (rows - 1) / 2) * row_sp
                        hole = _make_cylinder(o, r_hole, depth + 2, hx, hy, z_start - 1)
                        solid = _cut(o, solid, hole)
                tree.append(_node(step_id, label))

            # ── Finish ops ─────────────────────────────────────────────────
            elif op == "fillet":
                if solid is None:
                    raise RuntimeError("fillet requires an existing solid")
                radius = float(step["radius"])
                max_e  = int(step.get("max_edges", 20))
                solid = _apply_fillet(o, solid, radius, max_e)
                tree.append(_node(step_id, label))

            elif op == "chamfer":
                if solid is None:
                    raise RuntimeError("chamfer requires an existing solid")
                size  = float(step["size"])
                max_e = int(step.get("max_edges", 12))
                solid = _apply_chamfer(o, solid, size, max_e)
                tree.append(_node(step_id, label))

            else:
                logger.warning(f"Unknown op '{op}' at step {i} — skipped")
                tree.append(_node(step_id, f"Unknown: {op}", "failed"))

        except Exception as exc:
            logger.error(f"Step {i} '{op}' failed: {exc}")
            tree.append(_node(step_id, label, "failed"))
            # Continue — don't abort the whole program on one bad step

    if solid is None:
        raise RuntimeError("Construction program produced no geometry")

    solid = _validate_solid(o, solid)
    logger.info(f"Program executed: {len(tree)} steps, {time.perf_counter()-t0:.2f}s")
    return solid, tree


def execute_program_to_mesh(program: list[dict]) -> tuple[dict, list[dict]]:
    """Execute program and serialise to mesh data. Returns (mesh_data, tree)."""
    from app.services.mesh_serialiser import serialise_mesh
    shape, tree = execute_program(program)
    return serialise_mesh(shape), tree
