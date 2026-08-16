import math
from dataclasses import dataclass, field
from app.models.params import LowerValveBodyParams
from app.models.errors import ValidationError


@dataclass
class ValidationResult:
    has_errors: bool = False
    errors: list[ValidationError] = field(default_factory=list)

    def add_error(self, constraint: str, parameter: str | list[str],
                  submitted_value: float | list[float] | str | None, expected_bound: str) -> None:
        self.has_errors = True
        self.errors.append(ValidationError(
            constraint=constraint,
            parameter=parameter,
            submitted_value=submitted_value,
            expected_bound=expected_bound,
        ))


def validate_constraints(params: LowerValveBodyParams) -> ValidationResult:
    result = ValidationResult()

    bore_checks = [
        ("main_bore_upper_diameter", params.main_bore_upper_diameter, "outer_body_diameter", params.outer_body_diameter),
        ("main_bore_lower_inner_diameter", params.main_bore_lower_inner_diameter, "outer_body_diameter", params.outer_body_diameter),
        ("side_port_bore_diameter", params.side_port_bore_diameter, "side_port_flange_outer_diameter", params.side_port_flange_outer_diameter),
    ]
    for bore_name, bore_val, outer_name, outer_val in bore_checks:
        if bore_val >= outer_val:
            result.add_error("bore_less_than_outer_diameter", bore_name, bore_val, f"< {outer_name} ({outer_val})")

    depth_fields = {
        "top_flange_bolt_hole_depth": params.top_flange_bolt_hole_depth,
        "top_flange_counterbore_depth": params.top_flange_counterbore_depth,
        "bottom_flange_counterbore_depth": params.bottom_flange_counterbore_depth,
        "side_port_offset_from_top": params.side_port_offset_from_top,
        "overall_height": params.overall_height,
    }
    for fname, fval in depth_fields.items():
        if not math.isfinite(fval) or fval <= 0:
            result.add_error("depth_positive_finite", fname, fval, "> 0 and finite")
        elif fval > params.overall_height and fname != "overall_height":
            result.add_error("depth_within_body_height", fname, fval, f"<= overall_height ({params.overall_height})")

    side_port_bottom = params.side_port_offset_from_top + (params.side_port_bore_diameter / 2)
    if side_port_bottom > params.overall_height:
        result.add_error(
            "side_port_within_body",
            ["side_port_offset_from_top", "side_port_bore_diameter"],
            [params.side_port_offset_from_top, params.side_port_bore_diameter],
            f"side_port_offset_from_top + side_port_bore_diameter/2 <= overall_height ({params.overall_height}); got {side_port_bottom}",
        )

    counterbore_checks = [
        ("top_flange_counterbore_diameter", params.top_flange_counterbore_diameter, "top_flange_bolt_hole_diameter", params.top_flange_bolt_hole_diameter),
        ("bottom_flange_counterbore_diameter", params.bottom_flange_counterbore_diameter, "bottom_flange_bolt_hole_diameter", params.bottom_flange_bolt_hole_diameter),
    ]
    for cb_name, cb_val, bh_name, bh_val in counterbore_checks:
        if cb_val <= bh_val:
            result.add_error("counterbore_greater_than_hole", cb_name, cb_val, f"> {bh_name} ({bh_val})")

    for fname in params.model_fields:
        if fname == "material":
            continue
        if getattr(params, fname) is None:
            result.add_error("required_parameter_missing", fname, None, "must be provided (not null)")

    return result
