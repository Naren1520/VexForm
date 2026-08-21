"""Deterministic, feature-relative topology metadata and reference resolution."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.cad.errors import CADExecutionError


@dataclass(frozen=True)
class TopologyReference:
    feature_id: str
    topology_type: str
    reference: str

    def as_dict(self) -> dict[str, str]:
        return {"feature_id": self.feature_id, "topology_type": self.topology_type, "reference": self.reference}


def _shape_type_name(shape: Any) -> str:
    return {0: "compound", 1: "compsolid", 2: "solid", 3: "shell", 4: "face", 5: "wire", 6: "edge", 7: "vertex"}.get(shape.ShapeType(), "shape")


def _point_dict(point: Any) -> list[float]:
    return [round(float(point.X()), 6), round(float(point.Y()), 6), round(float(point.Z()), 6)]


def _explore(shape: Any, kind: Any) -> list[Any]:
    from OCC.Core.TopExp import TopExp_Explorer
    explorer = TopExp_Explorer(shape, kind)
    values = []
    while explorer.More():
        values.append(explorer.Current())
        explorer.Next()
    return values


def _face_signature(face: Any) -> dict[str, Any]:
    from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
    from OCC.Core.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Cone, GeomAbs_Sphere, GeomAbs_Torus
    from OCC.Core.GProp import GProp_GProps
    from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
    adaptor = BRepAdaptor_Surface(face, True)
    kind = adaptor.GetType()
    surface_types = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder", GeomAbs_Cone: "cone", GeomAbs_Sphere: "sphere", GeomAbs_Torus: "torus"}
    properties = GProp_GProps()
    brepgprop_SurfaceProperties(face, properties)
    center = properties.CentreOfMass()
    signature: dict[str, Any] = {
        "surface_type": surface_types.get(kind, str(kind)),
        "area": round(float(properties.Mass()), 6),
        "centroid": _point_dict(center),
    }
    if kind == GeomAbs_Plane:
        signature["normal"] = _point_dict(adaptor.Plane().Axis().Direction())
    elif kind == GeomAbs_Cylinder:
        signature["radius"] = round(float(adaptor.Cylinder().Radius()), 6)
        signature["axis"] = _point_dict(adaptor.Cylinder().Axis().Direction())
    return signature


def _edge_signature(edge: Any) -> dict[str, Any]:
    from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
    from OCC.Core.GProp import GProp_GProps
    from OCC.Core.BRepGProp import brepgprop_LinearProperties
    adaptor = BRepAdaptor_Curve(edge)
    properties = GProp_GProps()
    brepgprop_LinearProperties(edge, properties)
    center = properties.CentreOfMass()
    return {
        "curve_type": str(adaptor.GetType()),
        "length": round(float(properties.Mass()), 6),
        "centroid": _point_dict(center),
    }


def _vertex_signature(vertex: Any) -> dict[str, Any]:
    from OCC.Core.BRep import BRep_Tool
    return {"point": _point_dict(BRep_Tool.Pnt(vertex))}


def extract_topology(shape: Any, feature_id: str, derived_from: list[str] | None = None) -> dict[str, Any]:
    """Extract deterministic metadata; public references are never OCC indices."""
    from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
    faces = _explore(shape, TopAbs_FACE)
    edges = _explore(shape, TopAbs_EDGE)
    vertices = _explore(shape, TopAbs_VERTEX)
    face_items = [{"reference": f"face:{feature_id}:surface:{index + 1:02d}", "signature": _face_signature(face)} for index, face in enumerate(faces)]
    edge_items = [{"reference": f"edge:{feature_id}:curve:{index + 1:02d}", "signature": _edge_signature(edge)} for index, edge in enumerate(edges)]
    vertex_items = [{"reference": f"vertex:{feature_id}:point:{index + 1:02d}", "signature": _vertex_signature(vertex)} for index, vertex in enumerate(vertices)]
    return {
        "shape_type": _shape_type_name(shape),
        "faces": face_items,
        "edges": edge_items,
        "vertices": vertex_items,
        "lineage": {"source_feature": feature_id, "derived_from": derived_from or []},
    }


def topology_objects(shape: Any) -> dict[str, list[Any]]:
    """Return the OCC objects keyed by the same deterministic references as metadata."""
    from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
    return {
        "faces": _explore(shape, TopAbs_FACE),
        "edges": _explore(shape, TopAbs_EDGE),
        "vertices": _explore(shape, TopAbs_VERTEX),
    }


def find_faces(shape: Any) -> list[Any]:
    from OCC.Core.TopAbs import TopAbs_FACE
    return _explore(shape, TopAbs_FACE)


def find_edges(shape: Any) -> list[Any]:
    from OCC.Core.TopAbs import TopAbs_EDGE
    return _explore(shape, TopAbs_EDGE)


def find_vertices(shape: Any) -> list[Any]:
    from OCC.Core.TopAbs import TopAbs_VERTEX
    return _explore(shape, TopAbs_VERTEX)


def get_topology_signature(topology_item: dict[str, Any]) -> dict[str, Any]:
    return dict(topology_item.get("signature", {}))


def match_topology(topology: dict[str, Any], query: dict[str, Any], tolerance: float = 1e-5) -> list[dict[str, Any]]:
    topology_type = query.get("topology_type", query.get("topology", "face"))
    return [item for item in topology.get(f"{topology_type}s", []) if _matches(item, query.get("signature", query), tolerance)]


def shape_metrics(shape: Any) -> dict[str, float | int]:
    """Return deterministic B-Rep regression metrics for a generated shape."""
    from OCC.Core.GProp import GProp_GProps
    from OCC.Core.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
    from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
    volume = GProp_GProps()
    surface = GProp_GProps()
    brepgprop_VolumeProperties(shape, volume)
    brepgprop_SurfaceProperties(shape, surface)
    return {
        "volume": float(volume.Mass()),
        "surface_area": float(surface.Mass()),
        "solid_count": len(_explore(shape, TopAbs_SOLID)),
        "face_count": len(_explore(shape, TopAbs_FACE)),
        "edge_count": len(_explore(shape, TopAbs_EDGE)),
        "vertex_count": len(_explore(shape, TopAbs_VERTEX)),
    }


def _distance(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def _matches(item: dict[str, Any], query: dict[str, Any], tolerance: float) -> bool:
    signature = item.get("signature", {})
    for key, expected in query.items():
        actual = signature.get(key)
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if abs(float(actual) - float(expected)) > tolerance:
                return False
        elif isinstance(expected, list) and isinstance(actual, list):
            if _distance(actual, expected) > tolerance:
                return False
        elif expected != actual:
            return False
    return True


def resolve_topology(topology: dict[str, list[dict[str, Any]]], request: dict[str, Any], feature_id: str) -> Any:
    """Resolve semantic or signature references and reject ambiguity."""
    topology_type = request.get("topology_type") or request.get("topology") or "face"
    if topology_type not in {"face", "edge", "vertex"}:
        raise CADExecutionError(feature_id, "TOPOLOGY_NOT_FOUND", f"unsupported topology type '{topology_type}'")
    items = topology.get(f"{topology_type}s", [])
    reference = str(request.get("reference", ""))
    if reference.startswith(f"{topology_type}:"):
        matches = [item for item in items if item["reference"] == reference]
    elif reference in {"top", "bottom", "side_01", "side_02", "side_03", "side_04"} and topology_type == "face":
        candidates = [item for item in items if item["signature"].get("surface_type") == "plane"]
        candidates.sort(key=lambda item: item["signature"].get("centroid", [0, 0, 0]))
        if reference == "top":
            matches = [max(candidates, key=lambda item: item["signature"].get("centroid", [0, 0, 0])[2])] if candidates else []
        elif reference == "bottom":
            matches = [min(candidates, key=lambda item: item["signature"].get("centroid", [0, 0, 0])[2])] if candidates else []
        else:
            matches = candidates[int(reference[-2:]) - 1:int(reference[-2:])] if len(candidates) >= int(reference[-2:]) else []
    else:
        matches = [item for item in items if _matches(item, request.get("signature", request), float(request.get("tolerance", 1e-5)))]
    if not matches:
        raise CADExecutionError(feature_id, "TOPOLOGY_NOT_FOUND", f"no {topology_type} matches reference '{reference}'")
    if len(matches) > 1:
        raise CADExecutionError(feature_id, "AMBIGUOUS_TOPOLOGY_REFERENCE", f"multiple {topology_type}s match reference '{reference}'")
    return matches[0]
