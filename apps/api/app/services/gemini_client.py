import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

REFERENCE_KEYS = (
    "overall_height", "outer_body_diameter", "main_bore_upper_diameter",
    "main_bore_lower_inner_diameter", "main_bore_lower_outer_step_diameter",
    "side_port_bore_diameter", "top_flange_outer_diameter", "top_flange_bolt_hole_diameter",
    "top_flange_bolt_hole_depth", "top_flange_bolt_hole_count", "top_flange_counterbore_diameter",
    "top_flange_counterbore_depth", "bottom_flange_outer_diameter", "bottom_flange_bolt_circle_diameter",
    "bottom_flange_outer_flange_diameter", "bottom_flange_bolt_hole_diameter", "bottom_flange_bolt_hole_count",
    "bottom_flange_counterbore_diameter", "bottom_flange_counterbore_depth", "side_port_flange_outer_diameter",
    "side_port_bolt_hole_diameter", "side_port_bolt_hole_spacing", "side_port_angle_degrees",
    "side_port_offset_from_top", "unspecified_fillet_radius", "internal_step_chamfer",
    "other_chamfer", "material",
)

_EXTRACTION_PROMPT = """You are a precise mechanical engineering CAD parameter extractor.

Analyse the provided engineering blueprint image for a Lower Valve Body
(Injector Assembly, Globe Valve type, material HT150).

Extract the following dimensional parameters and return ONLY a valid JSON object
with exactly these keys. If a value is not legible or not shown in the drawing,
set it to null. Do NOT add any explanation or text outside the JSON.

Keys to extract:
- overall_height (total height of valve body in mm)
- outer_body_diameter (outer diameter of main cylindrical body in mm)
- main_bore_upper_diameter (upper bore diameter in mm, shown as Ø28 in section A-A)
- main_bore_lower_inner_diameter (lower bore inner diameter in mm, shown as Ø26)
- main_bore_lower_outer_step_diameter (lower bore outer step diameter in mm)
- side_port_bore_diameter (side port bore diameter in mm, shown as Ø20 HB)
- top_flange_outer_diameter (top flange outer diameter in mm)
- top_flange_bolt_hole_diameter (top flange bolt hole diameter in mm)
- top_flange_bolt_hole_depth (top flange bolt hole depth in mm)
- top_flange_bolt_hole_count (number of top flange bolt holes, integer)
- top_flange_counterbore_diameter (top flange counterbore diameter in mm)
- top_flange_counterbore_depth (top flange counterbore depth in mm)
- bottom_flange_outer_diameter (bottom flange outer diameter at body level in mm)
- bottom_flange_bolt_circle_diameter (bottom flange bolt circle diameter in mm)
- bottom_flange_outer_flange_diameter (bottom flange overall outer diameter in mm)
- bottom_flange_bolt_hole_diameter (bottom flange bolt hole diameter in mm)
- bottom_flange_bolt_hole_count (number of bottom flange bolt holes, integer)
- bottom_flange_counterbore_diameter (bottom flange counterbore diameter in mm)
- bottom_flange_counterbore_depth (bottom flange counterbore depth in mm)
- side_port_flange_outer_diameter (side port flange outer diameter in mm)
- side_port_bolt_hole_diameter (side port bolt hole diameter in mm)
- side_port_bolt_hole_spacing (side port bolt hole centre-to-centre spacing in mm)
- side_port_angle_degrees (side port angle from main axis in degrees, e.g. 135)
- side_port_offset_from_top (side port boss offset from top of body in mm)
- unspecified_fillet_radius (default fillet radius in mm, shown as R1 in notes)
- internal_step_chamfer (internal step chamfer in mm, e.g. 1.5 for C1.5)
- other_chamfer (other chamfer size in mm, e.g. 1.0 for C1)
- material (material specification string, e.g. "HT150")

Return JSON only, nothing else."""


def _normalise_response(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in REFERENCE_KEYS:
        val = raw.get(key)
        if val is None:
            result[key] = None
        elif key in ("top_flange_bolt_hole_count", "bottom_flange_bolt_hole_count"):
            try:
                result[key] = int(float(str(val)))
            except (ValueError, TypeError):
                result[key] = None
        elif key == "material":
            result[key] = str(val) if val is not None else None
        else:
            try:
                result[key] = float(str(val))
            except (ValueError, TypeError):
                result[key] = None
    return result


async def extract_params(image_bytes: bytes, mime_type: str) -> tuple[dict[str, Any], str]:
    from app.reference.lower_valve_body import LOWER_VALVE_BODY_REFERENCE
    fallback = _normalise_response(LOWER_VALVE_BODY_REFERENCE.model_dump())

    try:
        from app.config import settings
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        image_part = {"mime_type": mime_type, "data": image_bytes}

        async def _call() -> dict:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, lambda: model.generate_content([_EXTRACTION_PROMPT, image_part])
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)

        raw = await asyncio.wait_for(_call(), timeout=30.0)
        logger.info("Gemini extraction successful")
        return _normalise_response(raw), "gemini"

    except asyncio.TimeoutError:
        logger.error("Gemini API timed out; using fallback")
    except json.JSONDecodeError as exc:
        logger.error(f"Gemini response not valid JSON: {exc}; using fallback")
    except Exception as exc:
        logger.error(f"Gemini extraction failed: {exc}; using fallback")

    return fallback, "fallback"
