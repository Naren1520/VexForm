"""Deterministic CAD-IR execution against the trusted OCC operation engine."""
from __future__ import annotations

import math
from typing import Any
from app.cad.features.registry import FEATURE_REGISTRY
from app.cad.ir.models import CADModel, CADFeature, Sketch
from app.cad.ir.validation import validate_cad_ir, extrusion_dimension_for
from app.cad.errors import CADExecutionError
from app.cad.topology import extract_topology, resolve_topology, topology_objects


def _graph_features(model: CADModel) -> list[CADFeature]:
    sketch_features = [
        CADFeature(
            id=sketch.id,
            type="sketch",
            parameters={"plane": sketch.plane, "entities": [{"type": entity.type, **entity.parameters} for entity in sketch.entities], "closed": sketch.closed},
            confidence=sketch.confidence,
            label=sketch.id,
        )
        for sketch in model.sketches
    ]
    return sketch_features + model.features


def topological_features(model: CADModel) -> list[CADFeature]:
    """Return features in dependency order, preserving source order where possible."""
    features = _graph_features(model)
    by_id = {feature.id: feature for feature in features}
    ordered: list[CADFeature] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(feature: CADFeature) -> None:
        if feature.id in visiting:
            raise ValueError(f"circular dependency involving '{feature.id}'")
        if feature.id in visited:
            return
        visiting.add(feature.id)
        for dependency in feature.depends_on:
            dependency_feature = by_id.get(dependency)
            if dependency_feature is None:
                raise ValueError(f"missing dependency '{dependency}' for '{feature.id}'")
            visit(dependency_feature)
        visiting.remove(feature.id)
        visited.add(feature.id)
        ordered.append(feature)

    for feature in features:
        visit(feature)
    return ordered


def _operation_for(feature: CADFeature) -> dict[str, Any]:
    handler = FEATURE_REGISTRY.get(feature.type)
    if handler is None:
        raise ValueError(f"unsupported CAD feature '{feature.type}' ({feature.id})")
    operation = handler(feature.parameters)
    operation["label"] = feature.label or feature.id
    return operation


def execute_cad_ir(model: CADModel) -> tuple[dict, list[dict]]:
    """Validate and execute CAD-IR, returning mesh data and an IR-derived tree."""
    shape, tree = execute_cad_ir_shape(model)
    from app.services.mesh_serialiser import serialise_mesh
    mesh_data = serialise_mesh(shape)
    return mesh_data, tree


def execute_cad_ir_shape(model: CADModel) -> tuple[Any, list[dict]]:
    """Execute CAD-IR and return the exact OCC B-Rep for export."""
    errors = validate_cad_ir(model)
    if errors:
        raise CADExecutionError("model", "INVALID_CAD_IR", "; ".join(errors))

    o = _occ_for_graph()
    shapes: dict[str, Any] = {}
    topology_maps: dict[str, dict[str, Any]] = {}
    topology_objects_by_feature: dict[str, dict[str, Any]] = {}
    current = None
    tree: list[dict] = []
    for feature in topological_features(model):
        if not feature.enabled:
            tree.append({"id": feature.id, "label": feature.label or feature.id, "status": "pending", "confidence": feature.confidence, "output_type": feature.output_type})
            continue
        try:
            result = _execute_feature(o, feature, shapes, current, topology_maps, topology_objects_by_feature)
            if feature.type != "sketch":
                result = _single_solid(o, result, feature.id)
            shapes[feature.id] = result
            topology_maps[feature.id] = extract_topology(
                result, feature.id, [dependency for dependency in feature.depends_on if dependency in topology_maps]
            )
            topology_objects_by_feature[feature.id] = topology_objects(result)
            if feature.type not in {"sketch"}:
                current = result
            output_type = "wire" if feature.type == "sketch" and result.ShapeType() == 5 else "face" if feature.type == "sketch" else "solid"
            tree.append({"id": feature.id, "label": feature.label or feature.id, "status": "success", "confidence": feature.confidence, "output_type": output_type, "topology": topology_maps[feature.id], "evidence": feature.evidence})
        except CADExecutionError:
            raise
        except Exception as exc:
            raise CADExecutionError(feature.id, "EXECUTION_FAILED", str(exc)) from exc
    if current is None:
        raise CADExecutionError("model", "NO_SOLID", "CAD-IR produced no solid feature")
    current = _validate_brep(o, current)
    return current, tree


def _occ_for_graph() -> dict[str, Any]:
    from app.services.program_executor import _occ
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections, BRepOffsetAPI_MakePipe
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.gp import gp_Circ, gp_Ax1
    from OCC.Core.gp import gp_Elips
    from OCC.Core.GC import GC_MakeArcOfCircle
    from OCC.Core.BRepTools import breptools_OuterWire
    return {**_occ(), "Edge": BRepBuilderAPI_MakeEdge, "Wire": BRepBuilderAPI_MakeWire, "Face": BRepBuilderAPI_MakeFace,
            "Prism": BRepPrimAPI_MakePrism, "Revol": BRepPrimAPI_MakeRevol, "Loft": BRepOffsetAPI_ThruSections,
            "Pipe": BRepOffsetAPI_MakePipe, "Tool": BRep_Tool, "Circ": gp_Circ, "Axis": gp_Ax1,
            "OuterWire": breptools_OuterWire, "Ellipse": gp_Elips, "Arc": GC_MakeArcOfCircle}


def _point(o: dict, coords: list | tuple, plane: str) -> Any:
    x, y = float(coords[0]), float(coords[1])
    if plane.upper() == "XZ":
        return o["Pnt"](x, 0, y)
    if plane.upper() == "YZ":
        return o["Pnt"](0, x, y)
    return o["Pnt"](x, y, 0)


def _as_wire(o: dict, shape: Any) -> Any:
    if shape.ShapeType() == 5:
        return shape
    if shape.ShapeType() == 4:
        return o["OuterWire"](shape)
    raise ValueError("feature does not contain a wire or face profile")


def _build_sketch(o: dict, parameters: dict) -> Any:
    plane = str(parameters.get("plane", "XY"))
    edges = []
    for entity in parameters.get("entities", []):
        kind = entity.get("type")
        if kind == "polyline":
            points = entity.get("points", [])
            for start, end in zip(points, points[1:]):
                edges.append(o["Edge"](_point(o, start, plane), _point(o, end, plane)).Edge())
        elif kind == "line":
            edges.append(o["Edge"](_point(o, entity["start"], plane), _point(o, entity["end"], plane)).Edge())
        elif kind == "circle":
            center = _point(o, entity.get("center", [0, 0]), plane)
            normal = o["Dir"](0, 1, 0) if plane.upper() == "XZ" else o["Dir"](1, 0, 0) if plane.upper() == "YZ" else o["Dir"](0, 0, 1)
            edges.append(o["Edge"](o["Circ"](o["Ax2"](center, normal), float(entity["radius"]))).Edge())
        elif kind == "arc":
            edges.append(o["Edge"](o["Arc"](
                _point(o, entity["start"], plane),
                _point(o, entity["mid"], plane),
                _point(o, entity["end"], plane),
            ).Value()).Edge())
        elif kind == "ellipse":
            center = _point(o, entity.get("center", [0, 0]), plane)
            normal = o["Dir"](0, 1, 0) if plane.upper() == "XZ" else o["Dir"](1, 0, 0) if plane.upper() == "YZ" else o["Dir"](0, 0, 1)
            edges.append(o["Edge"](o["Ellipse"](o["Ax2"](center, normal), float(entity["major_radius"]), float(entity["minor_radius"]))).Edge())
        else:
            raise ValueError(f"sketch entity '{kind}' is not implemented")
    if not edges:
        raise ValueError("sketch has no executable edges")
    wire_builder = o["Wire"]()
    for edge in edges:
        wire_builder.Add(edge)
    wire = wire_builder.Wire()
    if parameters.get("closed"):
        return o["Face"](wire).Shape()
    return wire


def _execute_feature(o: dict, feature: CADFeature, shapes: dict[str, Any], current: Any,
                     topology_maps: dict[str, dict[str, Any]], topology_objects_by_feature: dict[str, dict[str, Any]]) -> Any:
    from app.services.program_executor import _make_box, _make_cylinder, _fuse, _cut, _apply_fillet, _apply_chamfer
    p = feature.parameters
    if feature.type == "sketch":
        return _build_sketch(o, p)
    if feature.type in {"box", "cylinder", "cone", "sphere", "torus"}:
        operation = {"op": feature.type, **p}
        if feature.type == "box":
            shape = _make_box(o, float(p["sx"]), float(p["sy"]), float(p["sz"]), float(p.get("x", 0)), float(p.get("y", 0)), float(p.get("z", 0)), bool(p.get("centered", True)))
        elif feature.type == "cylinder":
            radius = p.get("r", p.get("radius"))
            if radius is None:
                diameter = p.get("diameter", p.get("outer_diameter"))
                if diameter is not None:
                    radius = float(diameter) / 2
            height = p.get("h", p.get("height", p.get("length")))
            if radius is None or height is None:
                raise CADExecutionError(feature.id, "INVALID_CYLINDER", "cylinder requires a radius or diameter and a height")
            shape = _make_cylinder(o, float(radius), float(height), float(p.get("x", 0)), float(p.get("y", 0)), float(p.get("z", 0)), float(p.get("dx_dir", 0)), float(p.get("dy_dir", 0)), float(p.get("dz_dir", 1)))
        else:
            from app.services.program_executor import execute_program
            shape, _ = execute_program([operation])
        return shape if current is None else _fuse(o, current, shape)
    if feature.type in {"extrude", "rib"}:
        source_id = _source_feature_id(feature, "profile")
        distance_value = extrusion_dimension_for(p)
        distance = float(distance_value) if distance_value is not None else 0.0
        if source_id is None or source_id not in shapes:
            if distance <= 0:
                raise CADExecutionError(feature.id, "INVALID_PROFILE", "extrusion requires a valid sketch/profile dependency and an explicit extent")
            direct_shape = _direct_extrusion(o, p, distance)
            if direct_shape is None:
                raise CADExecutionError(feature.id, "INVALID_PROFILE", "extrusion profile is missing; provide a sketch dependency or explicit circular/rectangular profile dimensions")
            return direct_shape
        source = shapes[source_id]
        if source.ShapeType() not in {4, 5}:
            direct_shape = _direct_extrusion(o, p, distance)
            if direct_shape is not None:
                return _fuse(o, source, direct_shape)
            profile = _highest_solid_face(source)
            if profile is not None and distance > 0:
                direction = p.get("direction", [0, 0, 1])
                vector = o["Vec"](*(float(value) * distance for value in direction))
                prism = o["Prism"](profile, vector, True)
                if prism.IsDone() and not prism.Shape().IsNull():
                    return _fuse(o, source, prism.Shape())
            raise CADExecutionError(
                feature.id,
                "INVALID_PROFILE",
                f"extrusion profile '{source_id}' must be a face or wire, not a {source.ShapeType()} shape",
            )
        direction = p.get("direction", [0, 0, 1])
        vector = o["Vec"](*(float(value) * distance for value in direction))
        prism = o["Prism"](source, vector, True)
        if not prism.IsDone() or prism.Shape().IsNull():
            raise CADExecutionError(feature.id, "INVALID_EXTRUSION", "extrusion produced an invalid shape")
        return prism.Shape()
    if feature.type == "revolve":
        source_id = _source_feature_id(feature, "profile")
        if source_id is None or source_id not in shapes:
            raise CADExecutionError(feature.id, "INVALID_REVOLVE", "revolve requires a valid sketch/profile dependency")
        source = shapes[source_id]
        axis = p.get("axis", {})
        origin = axis.get("origin", [0, 0, 0]); direction = axis.get("direction", [0, 1, 0])
        angle = math.radians(float(p.get("angle", 360)))
        return o["Revol"](source, o["Axis"](o["Pnt"](*origin), o["Dir"](*direction)), angle, True).Shape()
    if feature.type == "loft":
        loft = o["Loft"](True, bool(p.get("ruled", False)), 1e-6)
        for dependency in feature.depends_on:
            loft.AddWire(_as_wire(o, shapes[dependency]))
        loft.Build()
        return _assert_shape(loft.Shape(), "loft")
    if feature.type == "sweep":
        profile_id = _source_feature_id(feature, "profile", 0)
        path_id = _source_feature_id(feature, "path", 1)
        if profile_id is None or path_id is None or profile_id not in shapes or path_id not in shapes:
            raise CADExecutionError(feature.id, "INVALID_SWEEP", "sweep requires valid profile and path dependencies")
        profile_shape = shapes[profile_id]
        profile = profile_shape if profile_shape.ShapeType() == 4 else _as_wire(o, profile_shape)
        path = _as_wire(o, shapes[path_id])
        return _assert_shape(o["Pipe"](path, profile).Shape(), "sweep")
    if feature.type == "cut":
        base_id = _source_feature_id(feature, "base", 0)
        if base_id is None or base_id not in shapes:
            raise CADExecutionError(feature.id, "INVALID_CUT", "cut requires a valid base dependency")
        tool_ids = feature.depends_on[1:]
        explicit_tool_id = _source_feature_id(feature, "tool", 1)
        if explicit_tool_id is not None and explicit_tool_id not in tool_ids:
            tool_ids = [explicit_tool_id, *tool_ids]
        if not tool_ids:
            radius = _parameter_number(p, {"r", "radius"})
            if radius is None:
                diameter = _parameter_number(p, {"diameter", "bore_diameter", "inner_diameter", "hole_diameter", "port_diameter"})
                if diameter is not None:
                    radius = float(diameter) / 2
            height = extrusion_dimension_for(p) or 20
            if radius is None:
                if "bore" not in feature.id.lower() and "hole" not in feature.id.lower():
                    raise CADExecutionError(feature.id, "INVALID_CUT", "cut requires a tool dependency or a radius/diameter")
                tool = _inferred_bore_tool(o, shapes[base_id])
                return _cut(o, shapes[base_id], tool)
            tool = _make_cylinder(
                o,
                float(radius),
                float(height),
                float(p.get("x", 0)),
                float(p.get("y", 0)),
                float(p.get("z", 0)),
                float(p.get("dx_dir", 0)),
                float(p.get("dy_dir", 0)),
                float(p.get("dz_dir", 1)),
            )
            return _cut(o, shapes[base_id], tool)
        result = shapes[base_id]
        for tool_id in tool_ids:
            if tool_id not in shapes:
                raise CADExecutionError(feature.id, "INVALID_CUT", f"cut tool dependency '{tool_id}' was not produced")
            tool = shapes[tool_id]
            if tool.ShapeType() == 5:
                tool = o["Face"](tool).Shape()
            if tool.ShapeType() in {4, 5}:
                distance_value = extrusion_dimension_for(p)
                if distance_value is None:
                    raise CADExecutionError(feature.id, "INVALID_CUT", f"profile tool '{tool_id}' requires a cut depth or distance")
                direction = p.get("direction", [0, 0, 1])
                vector = o["Vec"](*(float(value) * float(distance_value) for value in direction))
                prism = o["Prism"](tool, vector, True)
                if not prism.IsDone() or prism.Shape().IsNull():
                    raise CADExecutionError(feature.id, "INVALID_CUT", f"profile tool '{tool_id}' could not be extruded")
                tool = prism.Shape()
            result = _cut(o, result, tool)
        return result
    if feature.type in {"pattern", "circular_pattern", "linear_pattern"}:
        if current is None:
            raise CADExecutionError(feature.id, "INVALID_PATTERN", "pattern requires a prior solid")
        radius = _parameter_number(p, {"r", "radius", "hole_radius"})
        if radius is None:
            diameter = _parameter_number(p, {"diameter", "hole_diameter", "bolt_diameter"})
            if diameter is not None:
                radius = diameter / 2
        if radius is None:
            radius = 2.0
        depth = extrusion_dimension_for(p) or 20.0
        count = int(_parameter_number(p, {"count", "quantity", "instances"}) or 4)
        count = max(count, 1)
        pattern_kind = str(p.get("pattern_type", p.get("mode", "circular"))).lower()
        result = current
        if "rect" in pattern_kind or feature.type == "linear_pattern":
            columns = int(_parameter_number(p, {"columns", "cols"}) or count)
            rows = int(_parameter_number(p, {"rows"}) or 1)
            column_spacing = _parameter_number(p, {"column_spacing", "col_spacing", "spacing"}) or 20.0
            row_spacing = _parameter_number(p, {"row_spacing"}) or column_spacing
            center_x = float(p.get("x", 0)); center_y = float(p.get("y", 0)); start_z = float(p.get("z", -1))
            locations = [
                (center_x + (column - (columns - 1) / 2) * column_spacing,
                 center_y + (row - (rows - 1) / 2) * row_spacing)
                for row in range(rows) for column in range(columns)
            ]
        else:
            pitch_radius = _parameter_number(p, {"pattern_radius", "circle_radius", "bolt_circle_radius", "r_circle"}) or 25.0
            start_angle = math.radians(float(p.get("start_angle", 0)))
            center_x = float(p.get("x", 0)); center_y = float(p.get("y", 0)); start_z = float(p.get("z", -1))
            locations = [
                (center_x + pitch_radius * math.cos(start_angle + index * 2 * math.pi / count),
                 center_y + pitch_radius * math.sin(start_angle + index * 2 * math.pi / count))
                for index in range(count)
            ]
        for x, y in locations:
            result = _cut(o, result, _make_cylinder(o, radius, depth + 2, x, y, start_z))
        return result
    if feature.type in {"hole", "cut_cylinder", "pocket", "cut_box", "cut_sphere"}:
        if current is None:
            raise ValueError("subtractive feature requires a prior solid")
        op = "cut_cylinder" if feature.type in {"hole", "cut_cylinder"} else "cut_box" if feature.type in {"pocket", "cut_box"} else "cut_sphere"
        from app.services.program_executor import _make_cylinder, _make_box
        if op == "cut_cylinder":
            radius = p.get("r")
            if radius is None:
                diameter = p.get("diameter")
                if diameter is None:
                    raise CADExecutionError(feature.id, "INVALID_CUT", "cylindrical cut requires a radius or diameter")
                radius = float(diameter) / 2
            tool = _make_cylinder(o, float(radius), float(p.get("h", p.get("depth", 20))), float(p.get("x", 0)), float(p.get("y", 0)), float(p.get("z", 0)), float(p.get("dx_dir", 0)), float(p.get("dy_dir", 0)), float(p.get("dz_dir", 1)))
        elif op == "cut_box":
            tool = _make_box(o, float(p["sx"]), float(p["sy"]), float(p["sz"]), float(p.get("x", 0)), float(p.get("y", 0)), float(p.get("z", 0)), bool(p.get("centered", True)))
        else:
            from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
            tool = BRepPrimAPI_MakeSphere(float(p["r"])).Shape()
        return _cut(o, current, tool)
    if feature.type in {"fillet", "fillet_edges"}:
        return _finish_with_references(o, feature, current, topology_maps, topology_objects_by_feature, "fillet")
    if feature.type in {"chamfer", "chamfer_edges"}:
        return _finish_with_references(o, feature, current, topology_maps, topology_objects_by_feature, "chamfer")
    if feature.type == "shell":
        return _shell_with_references(o, feature, current, topology_maps, topology_objects_by_feature)
    if feature.type == "draft":
        return _draft_with_references(o, feature, current, topology_maps, topology_objects_by_feature)
    raise CADExecutionError(feature.id, "UNSUPPORTED_FEATURE", f"feature '{feature.type}' has no trusted OCC handler")


def _direct_extrusion(o: dict, parameters: dict, distance: float) -> Any | None:
    """Build a primitive only when Gemini supplied an explicit profile description."""
    from app.services.program_executor import _make_box, _make_cylinder
    x, y, z = (float(parameters.get(key, 0)) for key in ("x", "y", "z"))
    diameter = _parameter_number(parameters, {
        "diameter", "outer_diameter", "branch_diameter", "flange_diameter",
        "port_diameter", "boss_diameter",
    })
    radius = _parameter_number(parameters, {"radius", "r", "branch_radius", "flange_radius", "port_radius"})
    if diameter is not None or radius is not None:
        value = float(radius) if radius is not None else float(diameter) / 2
        direction = parameters.get("direction", [
            parameters.get("dx_dir", 0),
            parameters.get("dy_dir", 0),
            parameters.get("dz_dir", 1),
        ])
        return _make_cylinder(o, value, distance, x, y, z,
                              float(direction[0]), float(direction[1]), float(direction[2]))
    width = _parameter_number(parameters, {
        "width", "sx", "length", "plate_length", "base_length",
        "top_head_length", "branch_width", "flange_width",
    })
    depth = _parameter_number(parameters, {
        "depth", "sy", "width", "plate_width", "base_width",
        "top_head_width", "branch_depth", "flange_depth",
    })
    if width is not None and depth is not None:
        return _make_box(o, float(width), float(depth), distance, x, y, z, bool(parameters.get("centered", True)))
    return None


def _parameter_number(value: Any, names: set[str]) -> float | None:
    if isinstance(value, dict):
        label = str(value.get("name", value.get("key", value.get("parameter", "")))).lower().replace("-", "_").removesuffix("_mm")
        if label in names and isinstance(value.get("value"), (int, float)):
            return float(value["value"])
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_").removesuffix("_mm")
            if normalized in names and isinstance(item, (int, float)):
                return float(item)
            found = _parameter_number(item, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _parameter_number(item, names)
            if found is not None:
                return found
    return None


def _inferred_bore_tool(o: dict, shape: Any) -> Any:
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib_Add

    bounds = Bnd_Box()
    brepbndlib_Add(shape, bounds)
    xmin, ymin, zmin, xmax, ymax, zmax = bounds.Get()
    radius = max(min(xmax - xmin, ymax - ymin) * 0.2, 0.5)
    axis = o["Ax2"](
        o["Pnt"]((xmin + xmax) / 2, (ymin + ymax) / 2, zmin - 1),
        o["Dir"](0, 0, 1),
    )
    return o["Cyl"](axis, radius, max(zmax - zmin + 2, 2)).Shape()


def _highest_solid_face(shape: Any) -> Any | None:
    from OCC.Core.GProp import GProp_GProps
    from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
    from OCC.Core.TopAbs import TopAbs_FACE
    from OCC.Core.TopExp import TopExp_Explorer

    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    highest_face = None
    highest_z = float("-inf")
    while explorer.More():
        face = explorer.Current()
        properties = GProp_GProps()
        brepgprop_SurfaceProperties(face, properties)
        center = properties.CentreOfMass()
        if center.Z() > highest_z:
            highest_z = center.Z()
            highest_face = face
        explorer.Next()
    return highest_face


def _source_feature_id(feature: CADFeature, role: str, dependency_index: int = 0) -> str | None:
    """Resolve explicit profile/path references before positional dependencies."""
    parameters = feature.parameters
    for key in (f"{role}_id", role, f"{role}_reference", f"{role}_feature", f"{role}_feature_id", "source_feature_id", "source"):
        value = parameters.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for nested_key in ("feature_id", "id", "ref"):
                nested = value.get(nested_key)
                if isinstance(nested, str):
                    return nested
    return feature.depends_on[dependency_index] if len(feature.depends_on) > dependency_index else None


def _reference_items(feature: CADFeature, topology_type: str, topology_maps: dict[str, dict[str, Any]]) -> list[tuple[dict, Any]]:
    requests = feature.parameters.get("edges" if topology_type == "edge" else "faces", [])
    if not requests:
        return []
    result = []
    for request in requests:
        source_id = request.get("feature_id", feature.depends_on[0] if feature.depends_on else feature.id)
        metadata = topology_maps.get(source_id)
        if metadata is None:
            raise CADExecutionError(feature.id, "TOPOLOGY_NOT_FOUND", f"no topology map for feature '{source_id}'")
        item = resolve_topology(metadata, request, feature.id)
        result.append((item, source_id))
    return result


def _finish_with_references(o: dict, feature: CADFeature, current: Any, topology_maps: dict[str, dict[str, Any]], topology_objects_by_feature: dict[str, dict[str, Any]], operation: str) -> Any:
    references = _reference_items(feature, "edge", topology_maps)
    if not references:
        from app.services.program_executor import _apply_fillet, _apply_chamfer
        return _apply_fillet(o, current, float(feature.parameters["radius"]), int(feature.parameters.get("max_edges", 20))) if operation == "fillet" else _apply_chamfer(o, current, float(feature.parameters["size"]), int(feature.parameters.get("max_edges", 12)))
    builder = o["Fillet"](current) if operation == "fillet" else o["Chamfer"](current)
    amount = float(feature.parameters.get("radius", feature.parameters.get("size")))
    for item, source_id in references:
        reference = item["reference"]
        index = int(reference.rsplit(":", 1)[-1]) - 1
        edge = topology_objects_by_feature[source_id]["edges"][index]
        builder.Add(amount, edge)
    builder.Build()
    if not builder.IsDone() or builder.Shape().IsNull():
        raise CADExecutionError(feature.id, "INVALID_FILLET" if operation == "fillet" else "INVALID_CHAMFER", f"{operation} produced invalid topology")
    return builder.Shape()


def _shell_with_references(o: dict, feature: CADFeature, current: Any, topology_maps: dict[str, dict[str, Any]], topology_objects_by_feature: dict[str, dict[str, Any]]) -> Any:
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
    from OCC.Core.TopTools import TopTools_ListOfShape
    requests = feature.parameters.get("removed_faces", feature.parameters.get("faces", []))
    if not requests:
        raise CADExecutionError(feature.id, "INVALID_SHELL", "shell requires at least one removed face reference")
    faces = TopTools_ListOfShape()
    for request in requests:
        source_id = request.get("feature_id", feature.depends_on[0] if feature.depends_on else feature.id)
        metadata = topology_maps.get(source_id)
        if metadata is None:
            raise CADExecutionError(feature.id, "TOPOLOGY_NOT_FOUND", f"no topology map for feature '{source_id}'")
        item = resolve_topology(metadata, request, feature.id)
        index = int(item["reference"].rsplit(":", 1)[-1]) - 1
        faces.Append(topology_objects_by_feature[source_id]["faces"][index])
    builder = BRepOffsetAPI_MakeThickSolid()
    builder.MakeThickSolidByJoin(current, faces, -abs(float(feature.parameters["thickness"])), 1e-5)
    if not builder.IsDone() or builder.Shape().IsNull():
        raise CADExecutionError(feature.id, "INVALID_SHELL", "shell operation produced invalid topology")
    return builder.Shape()


def _draft_with_references(o: dict, feature: CADFeature, current: Any, topology_maps: dict[str, dict[str, Any]], topology_objects_by_feature: dict[str, dict[str, Any]]) -> Any:
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_DraftAngle
    from OCC.Core.gp import gp_Pln
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    references = _reference_items(feature, "face", topology_maps)
    if not references:
        raise CADExecutionError(feature.id, "INVALID_DRAFT", "draft requires at least one face reference")
    direction = feature.parameters.get("direction", [0, 0, 1])
    plane_origin = feature.parameters.get("plane_origin", [0, 0, 0])
    plane = gp_Pln(o["Pnt"](*plane_origin), o["Dir"](*direction))
    builder = BRepOffsetAPI_DraftAngle(current)
    for item, source_id in references:
        index = int(item["reference"].rsplit(":", 1)[-1]) - 1
        builder.Add(topology_objects_by_feature[source_id]["faces"][index], o["Dir"](*direction), math.radians(float(feature.parameters["angle"])), plane)
    builder.Build()
    if not builder.IsDone() or builder.Shape().IsNull():
        raise CADExecutionError(feature.id, "INVALID_DRAFT", "draft operation produced invalid topology")
    return builder.Shape()


def _assert_shape(shape: Any, operation: str) -> Any:
    if shape is None or shape.IsNull():
        raise ValueError(f"{operation} produced a null shape")
    return shape


def _validate_brep(o: dict, shape: Any) -> Any:
    checker = o["Check"](shape)
    if not checker.IsValid():
        raise CADExecutionError("model", "INVALID_TOPOLOGY", "BRepCheck_Analyzer rejected the generated shape")
    return _single_solid(o, shape, "model")


def _single_solid(o: dict, shape: Any, feature_id: str) -> Any:
    from OCC.Core.TopAbs import TopAbs_SOLID
    if shape.ShapeType() == TopAbs_SOLID:
        return shape
    explorer = o["Explorer"](shape, TopAbs_SOLID)
    solids = []
    while explorer.More():
        solids.append(explorer.Current())
        explorer.Next()
    if len(solids) == 1:
        return solids[0]
    if not solids:
        raise CADExecutionError(feature_id, "INVALID_BREP", "feature produced no solid")
    raise CADExecutionError(feature_id, "INVALID_BREP", f"feature produced {len(solids)} solids; expected one")
