"""Trusted CAD feature registry.

Handlers return validated operation descriptors; they never execute generated code.
"""
from __future__ import annotations
from collections.abc import Callable
from typing import Any

FEATURE_REGISTRY: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}


def register_feature(name: str):
    def decorator(handler: Callable[[dict[str, Any]], dict[str, Any]]):
        FEATURE_REGISTRY[name] = handler
        return handler
    return decorator


def _primitive(op: str):
    def handler(parameters: dict[str, Any]) -> dict[str, Any]:
        return {"op": op, **parameters}
    return handler


for _name in ("box", "cylinder", "cone", "sphere", "torus"):
    FEATURE_REGISTRY[_name] = _primitive(_name)

FEATURE_REGISTRY.update({
    "sketch": _primitive("sketch"),
    "extrude": _primitive("extrude"),
    "revolve": _primitive("revolve"),
    "sweep": _primitive("sweep"),
    "loft": _primitive("loft"),
    "shell": _primitive("shell"),
    "rib": _primitive("rib"),
    "draft": _primitive("draft"),
    "add_cylinder": _primitive("add_cylinder"),
    "add_box": _primitive("add_box"),
    "cut_cylinder": _primitive("cut_cylinder"),
    "cut_box": _primitive("cut_box"),
    "cut_sphere": _primitive("cut_sphere"),
    "hole": _primitive("cut_cylinder"),
    "pocket": _primitive("cut_box"),
    "bolt_circle": _primitive("bolt_circle"),
    "rectangular_hole_pattern": _primitive("rectangular_hole_pattern"),
    "fillet": _primitive("fillet"),
    "fillet_edges": _primitive("fillet"),
    "chamfer": _primitive("chamfer"),
    "chamfer_edges": _primitive("chamfer"),
    "union": _primitive("union"),
    "fuse": _primitive("fuse"),
    "cut": _primitive("cut"),
    "intersection": _primitive("intersection"),
    "translate": _primitive("translate"),
    "rotate": _primitive("rotate"),
    "mirror": _primitive("mirror"),
    "linear_pattern": _primitive("linear_pattern"),
    "circular_pattern": _primitive("circular_pattern"),
    "pattern": _primitive("pattern"),
})
