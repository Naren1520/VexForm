"""Blueprint → CAD-IR interpretation pipeline.

Gemini reads the blueprint image and outputs a JSON construction program.
The program is a list of OCC operations (cylinder, box, fuse, cut, etc.)
that the program_executor runs to build the 3D model.

This is the "no hardcoding" path — Gemini figures out the topology.
"""
from __future__ import annotations
import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── The core prompt ────────────────────────────────────────────────────────────

_PROGRAM_PROMPT = """\
You are an expert mechanical CAD engineer and programmer.
You will analyse an engineering blueprint image and produce strict JSON CAD-IR.
CAD-IR is a feature graph, not Python code. Never return executable code.

INSTRUCTIONS:
1. Study the blueprint carefully — look at all views (front, side, top, section views, isometric).
2. Identify every geometric feature: main body, flanges, bores, holes, bosses, slots, ribs, etc.
3. Read all dimension annotations (diameters, lengths, heights, angles, hole counts).
4. Output a JSON object with exactly these keys:
   - "part_name": string, the name of the part
   - "material": string, the material (e.g. "SS316", "grey iron", "aluminum 6061")
   - "overall_dimensions": {"length": X, "width": Y, "height": Z}  (bounding box in mm)
    - "cad_ir": {"version":"1.0", "units":"mm", "views":[], "features":[...], "blueprint_confidence":0.0, "overall_confidence":0.0}
   - "params": flat key-value dict of all extracted dimensions (for the parameter panel)

CAD-IR FEATURE TYPES:
Use sketch entities (line, polyline, circle, arc, ellipse), then features such as
sketch, extrude, revolve, sweep, loft, hole, cut, union, fillet, chamfer, shell,
rib, draft, pattern, mirror, and transform. Every feature has an id, type,
parameters, optional confidence, and depends_on feature IDs. Return structured JSON only.
Include every drawing view once in cad_ir.views and relate views to the same feature IDs;
front, top, side, section, detail, and isometric views describe one component, not separate parts.
For every uncertain dimension or feature, preserve null/unknown values with confidence 0.0
and a reason. Never invent a dimension that is not visible or inferable from the views.

LEGACY OPERATION BRIDGE:
For primitive-compatible features, a derived construction_program may also be included
for older clients. It is never executable code and must not contain Python.

Available operations:
  {"op":"cylinder",     "r":RADIUS, "h":HEIGHT, "x":0,"y":0,"z":0,
   "dx_dir":0,"dy_dir":0,"dz_dir":1, "label":"..."}
  — Creates a cylinder at position (x,y,z) pointing in direction (dx,dy,dz).
  — First solid in the program OR fused onto existing solid.

  {"op":"box",          "sx":W,"sy":D,"sz":H, "x":CX,"y":CY,"z":Z_BOTTOM,
   "centered":true, "label":"..."}
  — Creates an axis-aligned box. If centered=true, x/y are the center; z is the bottom.

  {"op":"sphere",       "r":RADIUS, "x":CX,"y":CY,"z":CZ, "label":"..."}

  {"op":"cone",         "r1":R_BOTTOM,"r2":R_TOP,"h":HEIGHT,
   "x":0,"y":0,"z":0, "label":"..."}

  {"op":"add_cylinder", "r":R,"h":H, "x":X,"y":Y,"z":Z_BOTTOM, "label":"..."}
  — Fuse a cylinder onto the existing solid.

  {"op":"add_box",      "sx":W,"sy":D,"sz":H, "x":CX,"y":CY,"z":Z_BOTTOM,
   "centered":true, "label":"..."}
  — Fuse a box onto the existing solid.

  {"op":"cut_cylinder", "r":R,"h":H, "x":X,"y":Y,"z":Z_BOTTOM, "label":"..."}
  — Cut a cylindrical hole from the existing solid.

  {"op":"cut_box",      "sx":W,"sy":D,"sz":H, "x":CX,"y":CY,"z":Z_BOTTOM,
   "centered":true, "label":"..."}
  — Cut a rectangular slot/pocket from the existing solid.

  {"op":"cut_sphere",   "r":R, "x":CX,"y":CY,"z":CZ, "label":"..."}
  — Cut a spherical cavity.

  {"op":"bolt_circle",  "r_hole":R,"count":N,"r_circle":PCD_RADIUS,
   "z":Z_START,"depth":DEPTH, "label":"..."}
  — Cut N equally-spaced bolt holes on a circle of radius r_circle.

  {"op":"rectangular_hole_pattern", "r_hole":R,"cols":C,"rows":R_COUNT,
   "col_spacing":CS,"row_spacing":RS, "z":Z,"depth":D, "label":"..."}
  — Grid pattern of holes.

  {"op":"fillet",  "radius":R, "max_edges":20, "label":"Fillets"}
  {"op":"chamfer", "size":S,   "max_edges":12, "label":"Chamfers"}

COORDINATE SYSTEM:
- Origin (0,0,0) is the bottom-center of the main body.
- Z axis points UP.
- All dimensions in MILLIMETRES.
- For horizontal features (side ports, lateral bores): use dx_dir/dy_dir/dz_dir to set direction.

RULES:
- Always start with the largest/main body as the first step (cylinder or box).
- Build additively first (fuse all bosses/flanges), THEN cut (bores, holes, slots).
- Model bodies, flanges, bosses, and side branches as additive cylinder/box features when their dimensions and placement are given. Their depends_on may point to the existing solid so they fuse onto it.
- Use extrude only when depends_on points to a separate sketch or profile face/wire. Never use an existing solid body as an extrude profile.
- For side or inclined branches, include radius/diameter, length/height, position, and direction [dx,dy,dz] so the branch is oriented from the drawing rather than defaulting to vertical.
- For bolt-hole patterns, include count, hole diameter/radius, pitch-circle radius or row/column spacing, and depth.
- If a dimension is not shown in the drawing, make a reasonable engineering estimate.
- Never leave a feature out because a dimension is missing — estimate it.
- For a flanged part: main body first, then flanges (add_cylinder), then bore (cut_cylinder),
  then bolt holes (bolt_circle).
- For a rectangular part: box first, then subtract features.

EXAMPLE — Simple flanged bushing:
{
  "part_name": "Flanged Bushing",
  "material": "Bronze",
  "overall_dimensions": {"length": 80, "width": 80, "height": 50},
  "construction_program": [
    {"op":"cylinder",     "r":35, "h":38, "label":"Main body"},
    {"op":"add_cylinder", "r":55, "h":12, "z":38, "label":"Flange"},
    {"op":"cut_cylinder", "r":20, "h":52, "z":-1, "label":"Bore"},
    {"op":"bolt_circle",  "r_hole":7, "count":6, "r_circle":44, "z":38, "depth":13,
     "label":"Flange bolt holes"},
    {"op":"chamfer", "size":1.5, "label":"Chamfers"}
  ],
  "params": {
    "outer_diameter": 70, "bore_diameter": 40, "length": 38,
    "flange_diameter": 110, "flange_thickness": 12,
    "bolt_hole_count": 6, "bolt_hole_diameter": 14,
    "bolt_circle_diameter": 88, "material": "Bronze"
  }
}

Now analyse the provided blueprint and output the CAD-IR JSON for the actual part shown.
Return ONLY valid JSON. No explanation text outside the JSON object.
"""

# ── Fallback program generator (when Gemini is unavailable) ───────────────────

def _fallback_program(part_name: str = "Unknown Part") -> dict:
    """Generic cylinder as absolute last resort."""
    return {
        "part_name": part_name,
        "material": "unknown",
        "overall_dimensions": {"length": 100, "width": 100, "height": 80},
        "construction_program": [
            {"op": "cylinder", "r": 50, "h": 80, "label": "Main body"},
        ],
        "cad_ir": {
            "version": "1.0",
            "units": "mm",
            "features": [{"id": "main_body", "type": "cylinder", "parameters": {"r": 50, "h": 80}, "confidence": 0.2}],
        },
        "params": {"outer_diameter": 100, "height": 80, "material": "unknown"},
    }


# ── Main entry point ───────────────────────────────────────────────────────────

async def blueprint_to_program(
    image_bytes: bytes,
    mime_type: str,
) -> tuple[dict, str]:
    """Send blueprint image to Gemini and get back a construction program.

    Returns (program_dict, source) where source is 'gemini' or 'fallback'.
    program_dict has keys: part_name, material, overall_dimensions,
                           construction_program, params
    """
    try:
        from app.config import settings
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Starting CAD-IR extraction with Gemini model: {settings.gemini_model}")
        image_part = {"mime_type": mime_type, "data": image_bytes}

        async def _call():
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    [_PROGRAM_PROMPT, image_part],
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 8192,
                        "response_mime_type": "application/json",
                    },
                )
            )
            text = response.text.strip()

            # Strip markdown fences
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                # Keep malformed model output visible; do not repair or execute it.
                tail = text[max(0, exc.pos - 120):exc.pos + 120].replace("\n", " ")
                raise ValueError(f"Gemini returned malformed JSON near: {tail}") from exc

        # Multi-view engineering drawings can require more than one minute.
        program = await asyncio.wait_for(_call(), timeout=180.0)

        if "cad_ir" in program:
            from app.cad.ir import CADModel
            from app.cad.executor.occ_executor import _operation_for
            cad_ir = CADModel.model_validate(program["cad_ir"])
            program["cad_ir"] = cad_ir.model_dump(mode="json")
            try:
                program["construction_program"] = [_operation_for(feature) for feature in cad_ir.features]
            except ValueError:
                program.pop("construction_program", None)
        if "cad_ir" not in program:
            raise ValueError("Gemini response missing 'cad_ir'")

        logger.info(
            f"Gemini generated CAD-IR: {len(cad_ir.features)} features "
            f"using {settings.gemini_model} for '{program.get('part_name', 'unknown')}'"
        )
        return program, "gemini"

    except asyncio.TimeoutError:
        logger.error("Gemini blueprint_to_program timed out")
    except ValueError as exc:
        logger.error(f"Gemini CAD-IR response rejected: {exc}")
    except Exception as exc:
        logger.error(f"blueprint_to_program failed: {exc}")

    return _fallback_program(), "fallback"


def program_to_cad_ir(program: list[dict], part_name: str = "Part") -> dict:
    """Convert a compatibility operation list into a validated CAD-IR document."""
    from app.cad.ir import CADModel
    from app.cad.ir.models import CADFeature

    features = []
    previous_id = None
    for index, operation in enumerate(program):
        values = dict(operation)
        op = values.pop("op", "")
        feature = CADFeature(
            id=f"feature_{index:03d}",
            type=op,
            parameters=values,
            depends_on=[previous_id] if previous_id else [],
            label=values.get("label") or op,
        )
        features.append(feature)
        previous_id = feature.id
    return CADModel(features=features, metadata={"part_name": part_name}).model_dump(mode="json")


def build_schema_from_params(params: dict, part_name: str) -> dict:
    """Convert flat params dict into a ShapeSchema-compatible object for the frontend."""
    fields = []
    sections_main = []
    sections_other = []

    for key, val in params.items():
        if key == "material":
            fields.append({
                "key": key, "label": key.replace("_", " ").title(),
                "unit": "", "field_type": "string",
                "min_val": None, "max_val": None, "description": "",
            })
            sections_other.append(key)
        elif isinstance(val, int):
            fields.append({
                "key": key, "label": key.replace("_", " ").title(),
                "unit": "" if "count" in key or "angle" not in key else "°",
                "field_type": "int",
                "min_val": 0, "max_val": None, "description": "",
            })
            sections_main.append(key)
        else:
            unit = "°" if "angle" in key or "degrees" in key else "mm"
            fields.append({
                "key": key, "label": key.replace("_", " ").title(),
                "unit": unit, "field_type": "float",
                "min_val": 0, "max_val": None, "description": "",
            })
            sections_main.append(key)

    # Build two sections: Dimensions + Material
    sections = []
    dim_keys = [k for k in sections_main if k not in sections_other]
    if dim_keys:
        sections.append({"label": "Dimensions", "keys": dim_keys})
    if sections_other:
        sections.append({"label": "Material", "keys": sections_other})

    return {
        "shape_type": "programmatic",
        "display_name": part_name,
        "fields": fields,
        "sections": sections,
        "feature_tree_order": [],
        "reference_values": {k: v for k, v in params.items()},
    }
