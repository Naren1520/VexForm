"""Shape registry — maps shape_type strings to builder + validator + schema."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class FieldDef:
    """Describes a single parameter field for the frontend."""
    key: str
    label: str
    unit: str = "mm"          # display unit
    field_type: str = "float"  # "float" | "int" | "string"
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    description: str = ""


@dataclass
class SectionDef:
    """A collapsible group of fields in the param panel."""
    label: str
    keys: list[str]


@dataclass
class ShapeDefinition:
    """Everything VexForm needs to support one shape type."""
    shape_type: str                  # e.g. "lower_valve_body"
    display_name: str                # e.g. "Lower Valve Body"
    fields: list[FieldDef]           # ordered list of all params
    sections: list[SectionDef]       # how to group fields in UI
    feature_tree_order: list[str]    # ordered Boolean op IDs
    # Callables — injected by each shape module
    build_fn: Callable               # (params_dict) → (mesh_data, tree)
    validate_fn: Callable            # (params_dict) → ValidationResult
    fallback_build_fn: Callable      # (params_dict) → (mesh_data, tree)
    # Gemini extraction config
    gemini_prompt_detail: str        # shape-specific section appended to base prompt
    reference_values: dict[str, Any] = field(default_factory=dict)  # for deviation scoring


class ShapeRegistry:
    """Singleton registry of all known shape types."""

    def __init__(self):
        self._shapes: dict[str, ShapeDefinition] = {}

    def register(self, defn: ShapeDefinition) -> None:
        self._shapes[defn.shape_type] = defn
        logger.info(f"Registered shape: {defn.shape_type} ({defn.display_name})")

    def get(self, shape_type: str) -> Optional[ShapeDefinition]:
        return self._shapes.get(shape_type)

    def list_types(self) -> list[str]:
        return list(self._shapes.keys())

    def list_display_names(self) -> dict[str, str]:
        return {k: v.display_name for k, v in self._shapes.items()}

    def schema_for(self, shape_type: str) -> Optional[dict]:
        """Return serialisable schema for a shape (for the frontend)."""
        defn = self.get(shape_type)
        if not defn:
            return None
        return {
            "shape_type": defn.shape_type,
            "display_name": defn.display_name,
            "fields": [
                {
                    "key": f.key,
                    "label": f.label,
                    "unit": f.unit,
                    "field_type": f.field_type,
                    "min_val": f.min_val,
                    "max_val": f.max_val,
                    "description": f.description,
                }
                for f in defn.fields
            ],
            "sections": [
                {"label": s.label, "keys": s.keys}
                for s in defn.sections
            ],
            "feature_tree_order": defn.feature_tree_order,
            "reference_values": defn.reference_values,
        }


# Module-level singleton
_registry: Optional[ShapeRegistry] = None


def get_registry() -> ShapeRegistry:
    global _registry
    if _registry is None:
        _registry = ShapeRegistry()
        _bootstrap_registry(_registry)
    return _registry


def _bootstrap_registry(registry: ShapeRegistry) -> None:
    """Import shape modules and register them into the provided registry."""
    from app.shapes import lower_valve_body as _lvb
    _lvb.register_shape(registry)
    # All other common shapes (box, plate, shaft, flange, gear, bracket, etc.)
    from app.shapes import common_shapes as _cs
    _cs.register_all(registry)
