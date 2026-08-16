"""Pydantic models for the Lower Valve Body parameter set."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class LowerValveBodyParams(BaseModel):
    overall_height: float = Field(gt=0, description="Total height of the valve body in mm")
    outer_body_diameter: float = Field(gt=0, description="Outer diameter of the main cylindrical body in mm")
    main_bore_upper_diameter: float = Field(gt=0, description="Upper bore diameter in mm")
    main_bore_lower_inner_diameter: float = Field(gt=0, description="Lower bore inner diameter in mm")
    main_bore_lower_outer_step_diameter: float = Field(gt=0, description="Lower bore outer step diameter in mm")
    side_port_bore_diameter: float = Field(gt=0, description="Side port bore diameter in mm")
    top_flange_outer_diameter: float = Field(gt=0, description="Top flange outer diameter in mm")
    top_flange_bolt_hole_diameter: float = Field(gt=0, description="Top flange bolt hole diameter in mm")
    top_flange_bolt_hole_depth: float = Field(gt=0, description="Top flange bolt hole depth in mm")
    top_flange_bolt_hole_count: int = Field(gt=0, description="Number of top flange bolt holes")
    top_flange_counterbore_diameter: float = Field(gt=0, description="Top flange counterbore diameter in mm")
    top_flange_counterbore_depth: float = Field(gt=0, description="Top flange counterbore depth in mm")
    bottom_flange_outer_diameter: float = Field(gt=0, description="Bottom flange outer diameter (body level) in mm")
    bottom_flange_bolt_circle_diameter: float = Field(gt=0, description="Bottom flange bolt circle diameter in mm")
    bottom_flange_outer_flange_diameter: float = Field(gt=0, description="Bottom flange overall outer diameter in mm")
    bottom_flange_bolt_hole_diameter: float = Field(gt=0, description="Bottom flange bolt hole diameter in mm")
    bottom_flange_bolt_hole_count: int = Field(gt=0, description="Number of bottom flange bolt holes")
    bottom_flange_counterbore_diameter: float = Field(gt=0, description="Bottom flange counterbore diameter in mm")
    bottom_flange_counterbore_depth: float = Field(gt=0, description="Bottom flange counterbore depth in mm")
    side_port_flange_outer_diameter: float = Field(gt=0, description="Side port flange outer diameter in mm")
    side_port_bolt_hole_diameter: float = Field(gt=0, description="Side port bolt hole diameter in mm")
    side_port_bolt_hole_spacing: float = Field(gt=0, description="Side port bolt hole spacing in mm")
    side_port_angle_degrees: float = Field(ge=0, lt=360, description="Side port angle from main axis in degrees")
    side_port_offset_from_top: float = Field(gt=0, description="Side port boss offset from top of body in mm")
    unspecified_fillet_radius: float = Field(gt=0, description="Default fillet radius for unspecified edges in mm")
    internal_step_chamfer: float = Field(gt=0, description="Chamfer size for internal step edge in mm")
    other_chamfer: float = Field(gt=0, description="Chamfer size for other edges in mm")
    material: str = Field(description="Material specification (e.g., HT150)")

    model_config = {"extra": "ignore"}
