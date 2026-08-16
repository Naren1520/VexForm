"""Reference dimension set for the Lower Valve Body (Globe Valve, HT150 cast iron).

All dimensions are in millimeters as specified in the engineering blueprint.
"""
from app.models.params import LowerValveBodyParams

LOWER_VALVE_BODY_REFERENCE = LowerValveBodyParams(
    overall_height=118.0,
    outer_body_diameter=36.0,
    main_bore_upper_diameter=28.0,
    main_bore_lower_inner_diameter=26.0,
    main_bore_lower_outer_step_diameter=28.0,
    side_port_bore_diameter=20.0,
    top_flange_outer_diameter=40.0,
    top_flange_bolt_hole_diameter=7.0,
    top_flange_bolt_hole_depth=6.0,
    top_flange_bolt_hole_count=4,
    top_flange_counterbore_diameter=13.0,
    top_flange_counterbore_depth=1.0,
    bottom_flange_outer_diameter=36.0,
    bottom_flange_bolt_circle_diameter=52.0,
    bottom_flange_outer_flange_diameter=65.0,
    bottom_flange_bolt_hole_diameter=7.0,
    bottom_flange_bolt_hole_count=4,
    bottom_flange_counterbore_diameter=13.0,
    bottom_flange_counterbore_depth=1.0,
    side_port_flange_outer_diameter=34.0,
    side_port_bolt_hole_diameter=7.0,
    side_port_bolt_hole_spacing=52.0,
    side_port_angle_degrees=135.0,
    side_port_offset_from_top=58.0,
    unspecified_fillet_radius=1.0,
    internal_step_chamfer=1.5,
    other_chamfer=1.0,
    material="HT150",
)

# All parameter keys for extraction normalisation
REFERENCE_KEYS: tuple[str, ...] = tuple(LOWER_VALVE_BODY_REFERENCE.model_fields.keys())
