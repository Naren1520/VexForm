"""Generic OCC geometry primitives used by all shape builders.

Every shape module imports from here rather than duplicating OCC boilerplate.
"""
from __future__ import annotations
import math
import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── OCC lazy loader ────────────────────────────────────────────────────────────

def occ():
    from OCC.Core.BRepPrimAPI import (
        BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox,
        BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCone,
        BRepPrimAPI_MakeTorus,
    )
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
    from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCC.Core.BRepCheck import BRepCheck_Analyzer
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_EDGE, TopAbs_COMPOUND
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec, gp_Ax1
    from OCC.Core.TopLoc import TopLoc_Location
    from OCC.Core.BRep import BRep_Tool
    return dict(
        MakeCylinder=BRepPrimAPI_MakeCylinder,
        MakeBox=BRepPrimAPI_MakeBox,
        MakeSphere=BRepPrimAPI_MakeSphere,
        MakeCone=BRepPrimAPI_MakeCone,
        MakeTorus=BRepPrimAPI_MakeTorus,
        Fuse=BRepAlgoAPI_Fuse,
        Cut=BRepAlgoAPI_Cut,
        Transform=BRepBuilderAPI_Transform,
        MakeFillet=BRepFilletAPI_MakeFillet,
        BRepCheck=BRepCheck_Analyzer,
        Mesh=BRepMesh_IncrementalMesh,
        TopAbs_SOLID=TopAbs_SOLID,
        TopAbs_FACE=TopAbs_FACE,
        TopAbs_EDGE=TopAbs_EDGE,
        TopExp_Explorer=TopExp_Explorer,
        gp_Ax2=gp_Ax2,
        gp_Pnt=gp_Pnt,
        gp_Dir=gp_Dir,
        gp_Trsf=gp_Trsf,
        gp_Vec=gp_Vec,
        gp_Ax1=gp_Ax1,
        TopLoc_Location=TopLoc_Location,
        BRep_Tool=BRep_Tool,
    )


# ── Core helpers ───────────────────────────────────────────────────────────────

def node(nid: str, label: str, status: str = "success") -> dict:
    return {"id": nid, "label": label, "status": status}


def assert_done(op, name: str):
    if not op.IsDone():
        raise RuntimeError(f"{name}: IsDone() returned False")
    s = op.Shape()
    if s is None or s.IsNull():
        raise RuntimeError(f"{name}: produced null shape")
    return s


def cylinder(o, r: float, h: float, ax2=None):
    if ax2:
        return o["MakeCylinder"](ax2, r, h).Shape()
    return o["MakeCylinder"](r, h).Shape()


def box(o, dx: float, dy: float, dz: float, corner=None):
    if corner:
        return o["MakeBox"](corner, dx, dy, dz).Shape()
    return o["MakeBox"](dx, dy, dz).Shape()


def sphere(o, r: float, center=None):
    if center:
        ax2 = o["gp_Ax2"](center, o["gp_Dir"](0, 0, 1))
        return o["MakeSphere"](ax2, r).Shape()
    return o["MakeSphere"](r).Shape()


def translate(o, shape, dx: float, dy: float, dz: float):
    t = o["gp_Trsf"]()
    t.SetTranslation(o["gp_Vec"](dx, dy, dz))
    return o["Transform"](shape, t, True).Shape()


def fuse(o, base, tool, name: str = "fuse"):
    return assert_done(o["Fuse"](base, tool), name)


def cut(o, base, tool, name: str = "cut"):
    return assert_done(o["Cut"](base, tool), name)


def bolt_holes_cut(o, solid, bolt_r: float, count: int,
                   circle_r: float, z_start: float, depth: float,
                   label_prefix: str) -> tuple[Any, list[dict]]:
    """Cut `count` equally-spaced bolt holes arranged on a bolt circle."""
    tree = []
    for i in range(count):
        angle = i * (2 * math.pi / count)
        hx = circle_r * math.cos(angle)
        hy = circle_r * math.sin(angle)
        hole = cylinder(o, bolt_r, depth + 2)
        hole = translate(o, hole, hx, hy, z_start)
        solid = cut(o, solid, hole, f"{label_prefix}_{i}")
    tree.append(node(f"{label_prefix}s", label_prefix.replace("_", " ").title() + "s"))
    return solid, tree


def validate_shape(o, solid):
    """Extract the first SOLID from a compound if needed, then run BRepCheck."""
    if solid.ShapeType() != o["TopAbs_SOLID"]:
        from OCC.Core.TopAbs import TopAbs_SOLID as _S
        exp = o["TopExp_Explorer"](solid, _S)
        if exp.More():
            solid = exp.Current()
        else:
            raise RuntimeError("No solid found in resulting compound")
    checker = o["BRepCheck"](solid)
    if not checker.IsValid():
        raise RuntimeError("BRepCheck: shape is not valid (self-intersections or non-manifold)")
    return solid


def serialise(shape) -> dict:
    from app.services.mesh_serialiser import serialise_mesh
    return serialise_mesh(shape)
