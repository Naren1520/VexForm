"""Registration of all common shape types (everything except lower_valve_body).

Each shape defines its fields, sections, Gemini extraction prompt detail,
reference values, and wires up OCC + fallback builders.
"""
from __future__ import annotations
from app.shapes.registry import FieldDef, SectionDef, ShapeDefinition
from app.services.generic_geometry import node as _n


# ── Shared validator (permissive — just checks positive finite values) ─────────

def _generic_validate(params_dict: dict):
    """Lightweight validator for non-LVB shapes — ensures no null/NaN/negative dims."""
    import math
    from app.services.validator import ValidationResult

    result = ValidationResult()
    for key, val in params_dict.items():
        if key == "material":
            continue
        if val is None:
            result.add_error("required_parameter_missing", key, None, "must be provided (not null)")
        elif isinstance(val, (int, float)):
            if not math.isfinite(val):
                result.add_error("value_must_be_finite", key, val, "finite number")
            elif val <= 0:
                result.add_error("value_must_be_positive", key, val, "> 0")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# BOX
# ─────────────────────────────────────────────────────────────────────────────

def _make_box():
    fields = [
        FieldDef("length",          "Length",           "mm", "float", 1, 5000),
        FieldDef("width",           "Width",            "mm", "float", 1, 5000),
        FieldDef("height",          "Height",           "mm", "float", 1, 5000),
        FieldDef("wall_thickness",  "Wall Thickness",   "mm", "float", 0, 500,
                 "0 = solid; >0 = hollow box"),
        FieldDef("fillet_radius",   "Fillet Radius",    "mm", "float", 0, 50,
                 "Corner fillet radius; 0 = sharp"),
        FieldDef("material",        "Material",         "",   "string"),
    ]
    sections = [
        SectionDef("Dimensions", ["length", "width", "height"]),
        SectionDef("Features",   ["wall_thickness", "fillet_radius"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"length": 100.0, "width": 60.0, "height": 40.0,
           "wall_thickness": 0.0, "fillet_radius": 2.0, "material": "steel"}
    prompt = """
You are analysing a rectangular box / block component.
Extract: overall length, width, height, wall thickness if hollow, corner fillet radius, material.
"""
    def _build(p):
        from app.services.shape_builders import build_box_occ
        return build_box_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_box
        return build_box(p)

    return ShapeDefinition(
        shape_type="box", display_name="Box / Block",
        fields=fields, sections=sections,
        feature_tree_order=["outer_box", "hollow_cut", "fillets", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PLATE
# ─────────────────────────────────────────────────────────────────────────────

def _make_plate():
    fields = [
        FieldDef("length",           "Length",             "mm", "float", 1, 5000),
        FieldDef("width",            "Width",              "mm", "float", 1, 5000),
        FieldDef("thickness",        "Thickness",          "mm", "float", 1, 500),
        FieldDef("hole_count",       "Hole Count",         "",   "int",   0, 64),
        FieldDef("hole_diameter",    "Hole Diameter",      "mm", "float", 0, 200),
        FieldDef("hole_circle_radius","Hole Circle Radius","mm", "float", 0, 2000),
        FieldDef("fillet_radius",    "Corner Fillet",      "mm", "float", 0, 50),
        FieldDef("chamfer_size",     "Chamfer Size",       "mm", "float", 0, 20),
        FieldDef("material",         "Material",           "",   "string"),
    ]
    sections = [
        SectionDef("Dimensions", ["length", "width", "thickness"]),
        SectionDef("Bolt Holes",  ["hole_count", "hole_diameter", "hole_circle_radius"]),
        SectionDef("Finishes",    ["fillet_radius", "chamfer_size"]),
        SectionDef("Material",    ["material"]),
    ]
    ref = {"length": 120.0, "width": 80.0, "thickness": 10.0, "hole_count": 4,
           "hole_diameter": 8.0, "hole_circle_radius": 35.0,
           "fillet_radius": 0.0, "chamfer_size": 1.0, "material": "steel"}
    prompt = """
You are analysing a flat plate or mounting plate.
Extract: overall length, width, thickness, bolt/mounting hole count,
hole diameter, hole circle radius (PCD/2), corner fillet radius, chamfer size, material.
"""
    def _build(p):
        from app.services.shape_builders import build_plate_occ
        return build_plate_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_plate
        return build_plate(p)

    return ShapeDefinition(
        shape_type="plate", display_name="Flat Plate",
        fields=fields, sections=sections,
        feature_tree_order=["plate_body", "bolt_holes", "fillets", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PIPE FLANGE
# ─────────────────────────────────────────────────────────────────────────────

def _make_pipe_flange():
    fields = [
        FieldDef("outer_diameter",    "Outer Diameter",      "mm", "float", 10, 2000),
        FieldDef("bore_diameter",     "Bore Diameter",       "mm", "float", 1,  1990),
        FieldDef("thickness",         "Flange Thickness",    "mm", "float", 1,  500),
        FieldDef("hub_diameter",      "Hub Diameter",        "mm", "float", 0,  2000),
        FieldDef("hub_height",        "Hub Height",          "mm", "float", 0,  500),
        FieldDef("bolt_hole_count",   "Bolt Hole Count",     "",   "int",   0,  64),
        FieldDef("bolt_hole_diameter","Bolt Hole Diameter",  "mm", "float", 0,  100),
        FieldDef("bolt_circle_diameter","Bolt Circle Ø",     "mm", "float", 0,  1800),
        FieldDef("chamfer_size",      "Chamfer Size",        "mm", "float", 0,  20),
        FieldDef("material",          "Material",            "",   "string"),
    ]
    sections = [
        SectionDef("Flange",     ["outer_diameter", "bore_diameter", "thickness"]),
        SectionDef("Hub",        ["hub_diameter", "hub_height"]),
        SectionDef("Bolt Pattern",["bolt_hole_count", "bolt_hole_diameter", "bolt_circle_diameter"]),
        SectionDef("Finishes",   ["chamfer_size"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"outer_diameter": 100.0, "bore_diameter": 50.0, "thickness": 20.0,
           "hub_diameter": 0.0, "hub_height": 0.0,
           "bolt_hole_count": 8, "bolt_hole_diameter": 14.0, "bolt_circle_diameter": 80.0,
           "chamfer_size": 1.5, "material": "carbon steel"}
    prompt = """
You are analysing a pipe flange (weld neck, slip-on, blind, or similar).
Extract: outer diameter, bore/pipe diameter, flange thickness,
hub outer diameter and height (if raised hub present),
bolt hole count, bolt hole diameter, bolt circle diameter (PCD), chamfer size, material.
"""
    def _build(p):
        from app.services.shape_builders import build_pipe_flange_occ
        return build_pipe_flange_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_pipe_flange
        return build_pipe_flange(p)

    return ShapeDefinition(
        shape_type="pipe_flange", display_name="Pipe Flange",
        fields=fields, sections=sections,
        feature_tree_order=["flange_body", "hub_extrusion", "bore_cut", "bolt_holes", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# SHAFT
# ─────────────────────────────────────────────────────────────────────────────

def _make_shaft():
    fields = [
        FieldDef("length",         "Total Length",        "mm", "float", 1, 10000),
        FieldDef("diameter",       "Main Diameter",       "mm", "float", 1, 2000),
        FieldDef("step_diameter",  "Step Diameter",       "mm", "float", 0, 2000,
                 "Diameter of reduced section; 0 = no step"),
        FieldDef("step_position",  "Step Position",       "mm", "float", 0, 10000,
                 "Axial position where step begins"),
        FieldDef("step2_diameter", "2nd Step Diameter",   "mm", "float", 0, 2000),
        FieldDef("step2_position", "2nd Step Position",   "mm", "float", 0, 10000),
        FieldDef("keyway_width",   "Keyway Width",        "mm", "float", 0, 100),
        FieldDef("keyway_depth",   "Keyway Depth",        "mm", "float", 0, 50),
        FieldDef("chamfer_size",   "Chamfer Size",        "mm", "float", 0, 20),
        FieldDef("material",       "Material",            "",   "string"),
    ]
    sections = [
        SectionDef("Main Body",  ["length", "diameter"]),
        SectionDef("Steps",      ["step_diameter", "step_position", "step2_diameter", "step2_position"]),
        SectionDef("Keyway",     ["keyway_width", "keyway_depth"]),
        SectionDef("Finishes",   ["chamfer_size"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"length": 200.0, "diameter": 30.0, "step_diameter": 22.0, "step_position": 80.0,
           "step2_diameter": 0.0, "step2_position": 0.0,
           "keyway_width": 8.0, "keyway_depth": 4.0, "chamfer_size": 1.5, "material": "1045 steel"}
    prompt = """
You are analysing a shaft or axle drawing.
Extract: total length, main diameter, stepped section diameters and their axial positions,
keyway width and depth, chamfer sizes, material.
"""
    def _build(p):
        from app.services.shape_builders import build_shaft_occ
        return build_shaft_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_shaft
        return build_shaft(p)

    return ShapeDefinition(
        shape_type="shaft", display_name="Shaft / Axle",
        fields=fields, sections=sections,
        feature_tree_order=["main_body", "step_section", "step2_section", "keyway", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# BUSHING
# ─────────────────────────────────────────────────────────────────────────────

def _make_bushing():
    fields = [
        FieldDef("outer_diameter",  "Outer Diameter",  "mm", "float", 1, 2000),
        FieldDef("inner_diameter",  "Inner Diameter",  "mm", "float", 1, 1990),
        FieldDef("length",          "Length",          "mm", "float", 1, 2000),
        FieldDef("flange_diameter", "Flange Diameter", "mm", "float", 0, 2000,
                 "0 = no flange"),
        FieldDef("flange_thickness","Flange Thickness","mm", "float", 0, 200),
        FieldDef("chamfer_size",    "Chamfer Size",    "mm", "float", 0, 20),
        FieldDef("material",        "Material",        "",   "string"),
    ]
    sections = [
        SectionDef("Body",    ["outer_diameter", "inner_diameter", "length"]),
        SectionDef("Flange",  ["flange_diameter", "flange_thickness"]),
        SectionDef("Finishes",["chamfer_size"]),
        SectionDef("Material",["material"]),
    ]
    ref = {"outer_diameter": 40.0, "inner_diameter": 25.0, "length": 30.0,
           "flange_diameter": 0.0, "flange_thickness": 0.0,
           "chamfer_size": 1.0, "material": "bronze"}
    prompt = """
You are analysing a bushing or bearing sleeve.
Extract: outer diameter, inner bore diameter, length,
flange outer diameter and thickness (if flanged bushing), chamfer size, material.
"""
    def _build(p):
        from app.services.shape_builders import build_bushing_occ
        return build_bushing_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_bushing
        return build_bushing(p)

    return ShapeDefinition(
        shape_type="bushing", display_name="Bushing / Sleeve",
        fields=fields, sections=sections,
        feature_tree_order=["bushing_body", "bore_cut", "flange", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# BRACKET
# ─────────────────────────────────────────────────────────────────────────────

def _make_bracket():
    fields = [
        FieldDef("base_length",     "Base Length",     "mm", "float", 1, 5000),
        FieldDef("base_width",      "Base Width",      "mm", "float", 1, 5000),
        FieldDef("base_thickness",  "Base Thickness",  "mm", "float", 1, 500),
        FieldDef("rib_height",      "Rib Height",      "mm", "float", 0, 5000),
        FieldDef("rib_thickness",   "Rib Thickness",   "mm", "float", 0, 500),
        FieldDef("hole_count",      "Hole Count",      "",   "int",   0, 32),
        FieldDef("hole_diameter",   "Hole Diameter",   "mm", "float", 0, 200),
        FieldDef("hole_circle_radius","Hole Circle R", "mm", "float", 0, 2000),
        FieldDef("fillet_radius",   "Fillet Radius",   "mm", "float", 0, 50),
        FieldDef("material",        "Material",        "",   "string"),
    ]
    sections = [
        SectionDef("Base",       ["base_length", "base_width", "base_thickness"]),
        SectionDef("Rib",        ["rib_height", "rib_thickness"]),
        SectionDef("Bolt Holes", ["hole_count", "hole_diameter", "hole_circle_radius"]),
        SectionDef("Finishes",   ["fillet_radius"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"base_length": 100.0, "base_width": 60.0, "base_thickness": 8.0,
           "rib_height": 60.0, "rib_thickness": 8.0,
           "hole_count": 4, "hole_diameter": 10.0, "hole_circle_radius": 25.0,
           "fillet_radius": 3.0, "material": "mild steel"}
    prompt = """
You are analysing a structural bracket or mounting bracket.
Extract: base plate length, width, thickness; rib/web height and thickness;
mounting hole count, hole diameter, hole circle radius; fillet radius; material.
"""
    def _build(p):
        from app.services.shape_builders import build_bracket_occ
        return build_bracket_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_bracket
        return build_bracket(p)

    return ShapeDefinition(
        shape_type="bracket", display_name="Bracket",
        fields=fields, sections=sections,
        feature_tree_order=["base_plate", "rib", "bolt_holes", "fillets"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GEAR
# ─────────────────────────────────────────────────────────────────────────────

def _make_gear():
    fields = [
        FieldDef("pitch_diameter",  "Pitch Diameter",  "mm", "float", 1, 2000),
        FieldDef("face_width",      "Face Width",      "mm", "float", 1, 1000),
        FieldDef("bore_diameter",   "Bore Diameter",   "mm", "float", 1, 1990),
        FieldDef("tooth_count",     "Tooth Count",     "",   "int",   4, 500),
        FieldDef("module",          "Module",          "mm", "float", 0.1, 50,
                 "Gear module = pitch diameter / tooth count"),
        FieldDef("keyway_width",    "Keyway Width",    "mm", "float", 0, 100),
        FieldDef("keyway_depth",    "Keyway Depth",    "mm", "float", 0, 50),
        FieldDef("pressure_angle",  "Pressure Angle",  "°",  "float", 14.5, 25),
        FieldDef("material",        "Material",        "",   "string"),
    ]
    sections = [
        SectionDef("Gear",    ["pitch_diameter", "face_width", "tooth_count", "module", "pressure_angle"]),
        SectionDef("Bore",    ["bore_diameter"]),
        SectionDef("Keyway",  ["keyway_width", "keyway_depth"]),
        SectionDef("Material",["material"]),
    ]
    ref = {"pitch_diameter": 80.0, "face_width": 20.0, "bore_diameter": 20.0,
           "tooth_count": 20, "module": 4.0, "keyway_width": 6.0, "keyway_depth": 3.0,
           "pressure_angle": 20.0, "material": "20CrMnTi"}
    prompt = """
You are analysing a spur gear or helical gear drawing.
Extract: pitch circle diameter, face width, bore diameter, number of teeth,
module (m = pitch diameter / tooth count), keyway width and depth,
pressure angle (typically 20°), material.
"""
    def _build(p):
        from app.services.shape_builders import build_gear_occ
        return build_gear_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_gear
        return build_gear(p)

    return ShapeDefinition(
        shape_type="gear", display_name="Gear",
        fields=fields, sections=sections,
        feature_tree_order=["gear_disc", "tooth_gaps", "bore_cut", "keyway"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ELBOW FITTING
# ─────────────────────────────────────────────────────────────────────────────

def _make_elbow():
    fields = [
        FieldDef("outer_diameter",   "Pipe OD",            "mm", "float", 1, 2000),
        FieldDef("bore_diameter",    "Bore / ID",          "mm", "float", 1, 1990),
        FieldDef("arm_length",       "Arm Length",         "mm", "float", 1, 5000),
        FieldDef("elbow_angle_degrees","Elbow Angle",      "°",  "float", 15, 180),
        FieldDef("flange_diameter",  "Flange OD",          "mm", "float", 0, 2000),
        FieldDef("flange_thickness", "Flange Thickness",   "mm", "float", 0, 500),
        FieldDef("bolt_hole_count",  "Bolt Hole Count",    "",   "int",   0, 32),
        FieldDef("bolt_hole_diameter","Bolt Hole Ø",       "mm", "float", 0, 100),
        FieldDef("material",         "Material",           "",   "string"),
    ]
    sections = [
        SectionDef("Pipe",    ["outer_diameter", "bore_diameter", "arm_length", "elbow_angle_degrees"]),
        SectionDef("Flange",  ["flange_diameter", "flange_thickness", "bolt_hole_count", "bolt_hole_diameter"]),
        SectionDef("Material",["material"]),
    ]
    ref = {"outer_diameter": 60.0, "bore_diameter": 40.0, "arm_length": 80.0,
           "elbow_angle_degrees": 90.0, "flange_diameter": 96.0, "flange_thickness": 12.0,
           "bolt_hole_count": 4, "bolt_hole_diameter": 10.0, "material": "ductile iron"}
    prompt = """
You are analysing a pipe elbow fitting (90°, 45°, or other angle).
Extract: pipe outer diameter, bore/inner diameter, arm length,
elbow angle in degrees, flange outer diameter, flange thickness,
bolt hole count, bolt hole diameter, material.
"""
    def _build(p):
        from app.services.shape_builders import build_elbow_occ
        return build_elbow_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_elbow
        return build_elbow(p)

    return ShapeDefinition(
        shape_type="elbow_fitting", display_name="Elbow Fitting",
        fields=fields, sections=sections,
        feature_tree_order=["arm1", "arm2", "flanges", "bore_cut"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# T-FITTING
# ─────────────────────────────────────────────────────────────────────────────

def _make_t_fitting():
    fields = [
        FieldDef("outer_diameter",     "Main Pipe OD",        "mm", "float", 1, 2000),
        FieldDef("bore_diameter",      "Main Bore / ID",      "mm", "float", 1, 1990),
        FieldDef("arm_length",         "Arm Length",          "mm", "float", 1, 5000),
        FieldDef("branch_diameter",    "Branch OD",           "mm", "float", 1, 2000),
        FieldDef("branch_bore_diameter","Branch Bore / ID",   "mm", "float", 1, 1990),
        FieldDef("flange_diameter",    "Flange OD",           "mm", "float", 0, 2000),
        FieldDef("flange_thickness",   "Flange Thickness",    "mm", "float", 0, 500),
        FieldDef("bolt_hole_count",    "Bolt Hole Count",     "",   "int",   0, 32),
        FieldDef("bolt_hole_diameter", "Bolt Hole Ø",         "mm", "float", 0, 100),
        FieldDef("material",           "Material",            "",   "string"),
    ]
    sections = [
        SectionDef("Main Run",  ["outer_diameter", "bore_diameter", "arm_length"]),
        SectionDef("Branch",    ["branch_diameter", "branch_bore_diameter"]),
        SectionDef("Flanges",   ["flange_diameter", "flange_thickness", "bolt_hole_count", "bolt_hole_diameter"]),
        SectionDef("Material",  ["material"]),
    ]
    ref = {"outer_diameter": 60.0, "bore_diameter": 40.0, "arm_length": 80.0,
           "branch_diameter": 60.0, "branch_bore_diameter": 40.0,
           "flange_diameter": 96.0, "flange_thickness": 12.0,
           "bolt_hole_count": 4, "bolt_hole_diameter": 10.0, "material": "ductile iron"}
    prompt = """
You are analysing a T-junction or tee pipe fitting.
Extract: main pipe outer diameter, main bore/ID, arm length,
branch pipe outer diameter and bore, flange outer diameter, flange thickness,
bolt hole count, bolt hole diameter, material.
"""
    def _build(p):
        from app.services.shape_builders import build_t_fitting_occ
        return build_t_fitting_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_t_fitting
        return build_t_fitting(p)

    return ShapeDefinition(
        shape_type="t_fitting", display_name="T-Fitting",
        fields=fields, sections=sections,
        feature_tree_order=["main_run", "branch", "flanges", "bore_cut"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# HOUSING
# ─────────────────────────────────────────────────────────────────────────────

def _make_housing():
    fields = [
        FieldDef("length",             "Length",           "mm", "float", 1, 5000),
        FieldDef("width",              "Width",            "mm", "float", 1, 5000),
        FieldDef("height",             "Height",           "mm", "float", 1, 5000),
        FieldDef("wall_thickness",     "Wall Thickness",   "mm", "float", 1, 500),
        FieldDef("bore_diameter",      "Bore Diameter",    "mm", "float", 0, 4990),
        FieldDef("bolt_hole_count",    "Bolt Hole Count",  "",   "int",   0, 32),
        FieldDef("bolt_hole_diameter", "Bolt Hole Ø",      "mm", "float", 0, 100),
        FieldDef("bolt_circle_diameter","Bolt Circle Ø",   "mm", "float", 0, 4990),
        FieldDef("split_height",       "Split Line Height","mm", "float", 0, 5000,
                 "Height of split line for two-piece housings; 0 = no split"),
        FieldDef("material",           "Material",         "",   "string"),
    ]
    sections = [
        SectionDef("Body",       ["length", "width", "height", "wall_thickness"]),
        SectionDef("Bore",       ["bore_diameter"]),
        SectionDef("Bolt Pattern",["bolt_hole_count", "bolt_hole_diameter", "bolt_circle_diameter"]),
        SectionDef("Advanced",   ["split_height"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"length": 150.0, "width": 100.0, "height": 80.0, "wall_thickness": 8.0,
           "bore_diameter": 50.0, "bolt_hole_count": 4, "bolt_hole_diameter": 10.0,
           "bolt_circle_diameter": 80.0, "split_height": 0.0, "material": "grey iron"}
    prompt = """
You are analysing a gearbox housing, bearing housing, or enclosure.
Extract: outer length, width, height, wall thickness, bore/shaft hole diameter,
bolt hole count, bolt hole diameter, bolt circle diameter,
split line height (for two-piece housings), material.
"""
    def _build(p):
        from app.services.shape_builders import build_housing_occ
        return build_housing_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_housing
        return build_housing(p)

    return ShapeDefinition(
        shape_type="housing", display_name="Housing / Enclosure",
        fields=fields, sections=sections,
        feature_tree_order=["housing_body", "bore_cut", "cavity", "bolt_holes", "fillets"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM (catch-all)
# ─────────────────────────────────────────────────────────────────────────────

def _make_custom():
    fields = [
        FieldDef("length",          "Length / Overall X",  "mm", "float", 0, 10000),
        FieldDef("width",           "Width / Overall Y",   "mm", "float", 0, 10000),
        FieldDef("height",          "Height / Overall Z",  "mm", "float", 0, 10000),
        FieldDef("outer_diameter",  "Outer Diameter",      "mm", "float", 0, 10000),
        FieldDef("bore_diameter",   "Bore / Inner Diameter","mm","float", 0, 10000),
        FieldDef("wall_thickness",  "Wall Thickness",      "mm", "float", 0, 5000),
        FieldDef("fillet_radius",   "Fillet Radius",       "mm", "float", 0, 500),
        FieldDef("material",        "Material",            "",   "string"),
    ]
    sections = [
        SectionDef("Dimensions", ["length", "width", "height", "outer_diameter", "bore_diameter"]),
        SectionDef("Features",   ["wall_thickness", "fillet_radius"]),
        SectionDef("Material",   ["material"]),
    ]
    ref = {"length": 100.0, "width": 60.0, "height": 40.0,
           "outer_diameter": 0.0, "bore_diameter": 0.0,
           "wall_thickness": 0.0, "fillet_radius": 0.0, "material": "unknown"}
    prompt = """
You are analysing an engineering component that does not clearly fit standard categories.
Extract whatever dimensional information you can: overall length, width, height,
any diameters, bore sizes, wall thickness, fillet radii, material.
"""
    def _build(p):
        from app.services.shape_builders import build_custom_occ
        return build_custom_occ(p)

    def _fallback(p):
        from app.services.generic_fallback import build_custom
        return build_custom(p)

    return ShapeDefinition(
        shape_type="custom", display_name="Custom Shape",
        fields=fields, sections=sections,
        feature_tree_order=["body", "bore_cut", "fillets", "chamfers"],
        build_fn=_build, validate_fn=_generic_validate, fallback_build_fn=_fallback,
        gemini_prompt_detail=prompt, reference_values=ref,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────────────────────

def register_all(registry) -> None:
    for factory in [
        _make_box, _make_plate, _make_pipe_flange, _make_shaft,
        _make_bushing, _make_bracket, _make_gear,
        _make_elbow, _make_t_fitting, _make_housing, _make_custom,
    ]:
        registry.register(factory())
