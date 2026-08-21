"""Structural validation for CAD-IR before any OCC operation is attempted."""
from __future__ import annotations

import math
from app.cad.ir.models import CADModel

SUPPORTED_FEATURES = {
    "box", "cylinder", "cone", "sphere", "torus", "sketch", "extrude",
    "revolve", "sweep", "loft", "union", "fuse", "cut", "intersection",
    "common", "hole", "pocket", "fillet", "fillet_edges", "chamfer",
    "chamfer_edges", "shell", "rib", "draft", "translate", "rotate",
    "mirror", "linear_pattern", "circular_pattern", "pattern",
}


def validate_cad_ir(model: CADModel) -> list[str]:
    """Return actionable errors; an empty list means the graph is structurally valid."""
    errors: list[str] = []
    feature_ids = {feature.id for feature in model.features}
    sketch_ids = {sketch.id for sketch in model.sketches}
    all_ids = feature_ids | sketch_ids

    if model.units not in {"mm", "cm", "m", "in"}:
        errors.append(f"unsupported units: {model.units}")
    if len(feature_ids) != len(model.features):
        errors.append("feature IDs must be unique")
    if len(sketch_ids) != len(model.sketches):
        errors.append("sketch IDs must be unique")
    if feature_ids & sketch_ids:
        errors.append("feature and sketch IDs must be unique across the model")

    for sketch in model.sketches:
        errors.extend(_validate_sketch(sketch.id, {
            "entities": [{"type": entity.type, **entity.parameters} for entity in sketch.entities],
            "closed": sketch.closed,
        }))

    for feature in model.features:
        if not feature.enabled:
            continue
        if feature.type not in SUPPORTED_FEATURES:
            errors.append(f"unsupported feature type '{feature.type}' ({feature.id})")
        for dependency in feature.depends_on:
            if dependency not in all_ids:
                errors.append(f"missing dependency '{dependency}' for '{feature.id}'")
        for key, value in feature.parameters.items():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                errors.append(f"non-finite parameter '{key}' on '{feature.id}'")
            if isinstance(value, (int, float)) and value < 0 and key not in {
                "angle", "rotation", "x", "y", "z", "offset", "position",
            }:
                errors.append(f"negative parameter '{key}' on '{feature.id}'")
        if feature.type == "sketch":
            errors.extend(_validate_sketch(feature.id, feature.parameters))
        if feature.type == "extrude" and feature.parameters.get("distance", 0) == 0:
            errors.append(f"feature '{feature.id}' extrusion distance must be non-zero")
        if feature.type in {"hole", "cut_cylinder"} and "diameter" in feature.parameters:
            if float(feature.parameters["diameter"]) <= 0:
                errors.append(f"feature '{feature.id}' hole diameter must be positive")
        if feature.type in {"fillet", "fillet_edges"} and float(feature.parameters.get("radius", 0)) <= 0:
            errors.append(f"feature '{feature.id}' fillet radius must be positive")
        if feature.type in {"chamfer", "chamfer_edges"} and float(feature.parameters.get("size", 0)) <= 0:
            errors.append(f"feature '{feature.id}' chamfer size must be positive")

    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {feature.id: feature for feature in model.features}

    def visit(feature_id: str) -> None:
        if feature_id in visiting:
            errors.append(f"circular dependency involving '{feature_id}'")
            return
        if feature_id in visited or feature_id not in by_id:
            return
        visiting.add(feature_id)
        for dependency in by_id[feature_id].depends_on:
            visit(dependency)
        visiting.remove(feature_id)
        visited.add(feature_id)

    for feature in model.features:
        visit(feature.id)
    return list(dict.fromkeys(errors))


def _validate_sketch(feature_id: str, parameters: dict) -> list[str]:
    entities = parameters.get("entities", [])
    errors: list[str] = []
    if not isinstance(entities, list) or not entities:
        return [f"sketch '{feature_id}' has no entities"]
    points: list[tuple[float, float]] = []
    for index, entity in enumerate(entities):
        if not isinstance(entity, dict):
            errors.append(f"sketch '{feature_id}' entity {index} is not an object")
            continue
        entity_type = entity.get("type")
        if entity_type not in {"line", "arc", "circle", "ellipse", "polyline"}:
            errors.append(f"sketch '{feature_id}' has unsupported entity '{entity_type}'")
        for key in ("start", "end", "center", "radius"):
            value = entity.get(key)
            if isinstance(value, (int, float)) and not math.isfinite(value):
                errors.append(f"sketch '{feature_id}' has non-finite {key}")
        if entity_type == "circle" and entity.get("radius", 0) <= 0:
            errors.append(f"sketch '{feature_id}' circle radius must be positive")
        if entity_type in {"line", "arc"}:
            start = entity.get("start")
            end = entity.get("end")
            if isinstance(start, list) and len(start) == 2:
                points.append(tuple(start))
            if isinstance(end, list) and len(end) == 2:
                points.append(tuple(end))
            if start == end:
                errors.append(f"sketch '{feature_id}' entity {index} has zero length")
    if parameters.get("closed"):
        has_closed_entity = any(
            isinstance(entity, dict) and entity.get("type") in {"circle", "ellipse"}
            for entity in entities
        )
        if not has_closed_entity and (len(points) < 3 or points[0] != points[-1]):
            errors.append(f"sketch '{feature_id}' closed profile endpoints are not connected")
    return errors
