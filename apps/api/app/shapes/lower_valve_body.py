"""Lower Valve Body shape registration.

This module registers the Lower Valve Body as a shape type in the registry.
The actual geometry builders live in their existing locations — this is the
glue that connects them to the generic pipeline.
"""
from __future__ import annotations

from app.shapes.registry import FieldDef, SectionDef, ShapeDefinition


# ── Field definitions ──────────────────────────────────────────────────────────

_FIELDS = [
    FieldDef("overall_height",                     "Overall Height",                    "mm",  "float", 10, 500),
    FieldDef("outer_body_diameter",                "Outer Body Diameter",               "mm",  "float", 10, 300),
    FieldDef("main_bore_upper_diameter",           "Main Bore Upper Ø",                 "mm",  "float", 1,  298),
    FieldDef("main_bore_lower_inner_diameter",     "Main Bore Lower Inner Ø",           "mm",  "float", 1,  298),
    FieldDef("main_bore_lower_outer_step_diameter","Main Bore Lower Outer Step Ø",      "mm",  "float", 1,  298),
    FieldDef("side_port_bore_diameter",            "Side Port Bore Ø",                  "mm",  "float", 1,  200),
    FieldDef("top_flange_outer_diameter",          "Top Flange Outer Ø",                "mm",  "float", 10, 500),
    FieldDef("top_flange_bolt_hole_diameter",      "Top Flange Bolt Hole Ø",            "mm",  "float", 1,  50),
    FieldDef("top_flange_bolt_hole_depth",         "Top Flange Bolt Hole Depth",        "mm",  "float", 1,  100),
    FieldDef("top_flange_bolt_hole_count",         "Top Flange Bolt Hole Count",        "",    "int",   1,  24),
    FieldDef("top_flange_counterbore_diameter",    "Top Flange Counterbore Ø",          "mm",  "float", 1,  100),
    FieldDef("top_flange_counterbore_depth",       "Top Flange Counterbore Depth",      "mm",  "float", 0,  50),
    FieldDef("bottom_flange_outer_diameter",       "Bottom Flange Outer Ø (body)",      "mm",  "float", 10, 500),
    FieldDef("bottom_flange_bolt_circle_diameter", "Bottom Flange Bolt Circle Ø",       "mm",  "float", 10, 500),
    FieldDef("bottom_flange_outer_flange_diameter","Bottom Flange Overall Ø",           "mm",  "float", 10, 500),
    FieldDef("bottom_flange_bolt_hole_diameter",   "Bottom Flange Bolt Hole Ø",         "mm",  "float", 1,  50),
    FieldDef("bottom_flange_bolt_hole_count",      "Bottom Flange Bolt Hole Count",     "",    "int",   1,  24),
    FieldDef("bottom_flange_counterbore_diameter", "Bottom Flange Counterbore Ø",       "mm",  "float", 1,  100),
    FieldDef("bottom_flange_counterbore_depth",    "Bottom Flange Counterbore Depth",   "mm",  "float", 0,  50),
    FieldDef("side_port_flange_outer_diameter",    "Side Port Flange Outer Ø",          "mm",  "float", 1,  200),
    FieldDef("side_port_bolt_hole_diameter",       "Side Port Bolt Hole Ø",             "mm",  "float", 1,  50),
    FieldDef("side_port_bolt_hole_spacing",        "Side Port Bolt Hole Spacing",       "mm",  "float", 1,  200),
    FieldDef("side_port_angle_degrees",            "Side Port Angle",                   "°",   "float", 0,  359),
    FieldDef("side_port_offset_from_top",          "Side Port Offset from Top",         "mm",  "float", 1,  500),
    FieldDef("unspecified_fillet_radius",          "Unspecified Fillet Radius",         "mm",  "float", 0.1, 20),
    FieldDef("internal_step_chamfer",              "Internal Step Chamfer",             "mm",  "float", 0.1, 20),
    FieldDef("other_chamfer",                      "Other Chamfer",                     "mm",  "float", 0.1, 20),
    FieldDef("material",                           "Material",                          "",    "string"),
]

_SECTIONS = [
    SectionDef("Main Body",   ["overall_height", "outer_body_diameter", "material"]),
    SectionDef("Main Bore",   ["main_bore_upper_diameter", "main_bore_lower_inner_diameter",
                               "main_bore_lower_outer_step_diameter"]),
    SectionDef("Top Flange",  ["top_flange_outer_diameter", "top_flange_bolt_hole_diameter",
                               "top_flange_bolt_hole_depth", "top_flange_bolt_hole_count",
                               "top_flange_counterbore_diameter", "top_flange_counterbore_depth"]),
    SectionDef("Bottom Flange", ["bottom_flange_outer_diameter", "bottom_flange_bolt_circle_diameter",
                                  "bottom_flange_outer_flange_diameter", "bottom_flange_bolt_hole_diameter",
                                  "bottom_flange_bolt_hole_count", "bottom_flange_counterbore_diameter",
                                  "bottom_flange_counterbore_depth"]),
    SectionDef("Side Port",   ["side_port_bore_diameter", "side_port_flange_outer_diameter",
                               "side_port_bolt_hole_diameter", "side_port_bolt_hole_spacing",
                               "side_port_angle_degrees", "side_port_offset_from_top"]),
    SectionDef("Fillets & Chamfers", ["unspecified_fillet_radius", "internal_step_chamfer", "other_chamfer"]),
]

_FEATURE_TREE_ORDER = [
    "base_cylinder", "top_flange_extrusion", "bottom_flange_extrusion",
    "side_port_boss", "upper_bore_cut", "lower_bore_cut", "side_port_bore_cut",
    "top_bolt_holes_cut", "top_counterbores_cut", "bottom_bolt_holes_cut",
    "bottom_counterbores_cut", "side_port_bolt_holes_cut", "fillets", "chamfers",
]

_GEMINI_DETAIL = """
You are analysing a Lower Valve Body (Globe Valve, Injector Assembly, typically HT150 cast iron).
Key features to look for:
- Main cylindrical body with top and bottom flanges
- Side port boss at an angle (typically 135°)
- Section A-A showing internal bores (upper bore ~Ø28, lower bore ~Ø26)
- Bolt hole patterns on top and bottom flanges (typically 4 holes)
- Side port marked "HB" (hydraulic bore) typically ~Ø20
- R1 fillet note, C1.5 and C1 chamfer notes
"""

_REFERENCE = {
    "overall_height": 118.0, "outer_body_diameter": 36.0,
    "main_bore_upper_diameter": 28.0, "main_bore_lower_inner_diameter": 26.0,
    "main_bore_lower_outer_step_diameter": 28.0, "side_port_bore_diameter": 20.0,
    "top_flange_outer_diameter": 40.0, "top_flange_bolt_hole_diameter": 7.0,
    "top_flange_bolt_hole_depth": 6.0, "top_flange_bolt_hole_count": 4,
    "top_flange_counterbore_diameter": 13.0, "top_flange_counterbore_depth": 1.0,
    "bottom_flange_outer_diameter": 36.0, "bottom_flange_bolt_circle_diameter": 52.0,
    "bottom_flange_outer_flange_diameter": 65.0, "bottom_flange_bolt_hole_diameter": 7.0,
    "bottom_flange_bolt_hole_count": 4, "bottom_flange_counterbore_diameter": 13.0,
    "bottom_flange_counterbore_depth": 1.0, "side_port_flange_outer_diameter": 34.0,
    "side_port_bolt_hole_diameter": 7.0, "side_port_bolt_hole_spacing": 52.0,
    "side_port_angle_degrees": 135.0, "side_port_offset_from_top": 58.0,
    "unspecified_fillet_radius": 1.0, "internal_step_chamfer": 1.5,
    "other_chamfer": 1.0, "material": "HT150",
}


# ── Builder wrappers ───────────────────────────────────────────────────────────

def _build(params_dict: dict):
    """OCC pipeline wrapper."""
    from app.models.params import LowerValveBodyParams
    from app.services.geometry_engine import build_lower_valve_body
    from app.services.mesh_serialiser import serialise_mesh
    p = LowerValveBodyParams(**params_dict)
    shape, tree = build_lower_valve_body(p)
    return serialise_mesh(shape), tree


def _fallback_build(params_dict: dict):
    from app.services.fallback_mesh import build_fallback_lower_valve_body
    return build_fallback_lower_valve_body(params_dict)


def _validate(params_dict: dict):
    from app.models.params import LowerValveBodyParams
    from app.services.validator import validate_constraints
    p = LowerValveBodyParams(**params_dict)
    return validate_constraints(p)


# ── Registration ───────────────────────────────────────────────────────────────

def register_shape(registry) -> None:
    """Called by the bootstrap in registry.py — do NOT call get_registry() here."""
    registry.register(ShapeDefinition(
        shape_type="lower_valve_body",
        display_name="Lower Valve Body",
        fields=_FIELDS,
        sections=_SECTIONS,
        feature_tree_order=_FEATURE_TREE_ORDER,
        build_fn=_build,
        validate_fn=_validate,
        fallback_build_fn=_fallback_build,
        gemini_prompt_detail=_GEMINI_DETAIL,
        reference_values=_REFERENCE,
    ))
