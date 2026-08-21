"""Generic Gemini client — identifies shape type from blueprint, then extracts its parameters."""
import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Phase 1: shape identification prompt ─────────────────────────────────────

_IDENTIFY_PROMPT = """\
You are a mechanical engineering blueprint analyser.

Look at the engineering drawing and identify the SINGLE best matching shape type.
Return ONLY a JSON object with exactly one key "shape_type". Choose from:

- "lower_valve_body"  — Globe valve body with top/bottom flanges and a side port boss
- "pipe_flange"       — Circular flange plate with bolt hole pattern, no elongated body
- "shaft"             — Cylindrical shaft / axle, possibly with steps, keyways, chamfers
- "bracket"           — Structural bracket or mounting plate with a vertical rib/web
- "gear"              — Spur, helical, or bevel gear with tooth profile
- "bushing"           — Short hollow cylinder / bearing sleeve
- "elbow_fitting"     — Pipe elbow (90°, 45° etc.) with flanged or plain ends
- "t_fitting"         — T-junction pipe fitting with three ports
- "housing"           — Gearbox / bearing housing — box-like enclosure with bore hole
- "box"               — Simple rectangular block or hollow box (no circular features)
- "plate"             — Flat plate with holes and/or cutouts, thickness << length/width
- "custom"            — Does not clearly match any category above

Return JSON only, e.g.: {"shape_type": "shaft"}
"""

# ── Phase 2: parameter extraction prompts per shape type ─────────────────────

_EXTRACTION_PROMPTS: dict[str, str] = {}

_EXTRACTION_BASE = """\
You are a precise mechanical engineering CAD parameter extractor.

Analyse the provided engineering blueprint image.
Extract ONLY the parameters listed below and return a valid JSON object with exactly those keys.
If a value is not legible or not shown, set it to null.
Do NOT add any explanation or text outside the JSON.

{shape_detail}

Keys to extract:
{keys_list}

Return JSON only, nothing else.\
"""


def _build_extraction_prompt(shape_detail: str, fields: list) -> str:
    keys = "\n".join(
        f"- {f['key']} ({f['label']}{', ' + f['unit'] if f['unit'] else ''})"
        for f in fields
    )
    return _EXTRACTION_BASE.format(shape_detail=shape_detail, keys_list=keys)


# ── Generic extraction ─────────────────────────────────────────────────────────

def _normalise_response(raw: dict[str, Any], fields: list) -> dict[str, Any]:
    """Cast extracted values to correct Python types based on field definitions."""
    result: dict[str, Any] = {}
    int_keys = {f["key"] for f in fields if f["field_type"] == "int"}
    str_keys = {f["key"] for f in fields if f["field_type"] == "string"}

    for f in fields:
        key = f["key"]
        val = raw.get(key)
        if val is None:
            result[key] = None
        elif key in str_keys:
            result[key] = str(val)
        elif key in int_keys:
            try:
                result[key] = int(float(str(val)))
            except (ValueError, TypeError):
                result[key] = None
        else:
            try:
                result[key] = float(str(val))
            except (ValueError, TypeError):
                result[key] = None
    return result


async def _call_gemini(model, prompt: str, image_part: dict, timeout: float = 30.0) -> dict:
    async def _invoke():
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: model.generate_content([prompt, image_part])
        )
        text = response.text.strip()
        # Strip markdown code fences
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    return await asyncio.wait_for(_invoke(), timeout=timeout)


async def identify_shape(image_bytes: bytes, mime_type: str) -> str:
    """Use Gemini to identify the shape type from a blueprint image.

    Returns shape_type string (falls back to 'lower_valve_body' on failure).
    """
    try:
        from app.config import settings
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        image_part = {"mime_type": mime_type, "data": image_bytes}
        raw = await _call_gemini(model, _IDENTIFY_PROMPT, image_part, timeout=20.0)
        shape_type = raw.get("shape_type", "lower_valve_body")
        logger.info(f"Gemini identified shape type: {shape_type}")
        return shape_type
    except Exception as exc:
        logger.warning(f"Shape identification failed: {exc}; defaulting to lower_valve_body")
        return "lower_valve_body"


async def extract_params(
    image_bytes: bytes,
    mime_type: str,
    shape_type: str | None = None,
) -> tuple[dict[str, Any], str, str]:
    """Extract parameters from a blueprint image.

    If shape_type is None, auto-identifies it first.
    Returns (params_dict, source, shape_type).
    source is 'gemini' or 'fallback'.
    """
    from app.shapes.registry import get_registry

    registry = get_registry()

    # Step 1: identify shape if not given
    if shape_type is None:
        shape_type = await identify_shape(image_bytes, mime_type)

    # Step 2: resolve shape definition
    defn = registry.get(shape_type)
    if defn is None:
        # Unknown shape — fall back to lower_valve_body
        logger.warning(f"Unknown shape_type '{shape_type}', falling back to lower_valve_body")
        shape_type = "lower_valve_body"
        defn = registry.get(shape_type)

    fields = registry.schema_for(shape_type)["fields"]
    reference = defn.reference_values

    # Build fallback from reference values
    fallback_params = _normalise_response(reference, fields)

    # Step 3: extract params via Gemini
    try:
        from app.config import settings
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        image_part = {"mime_type": mime_type, "data": image_bytes}

        prompt = _build_extraction_prompt(defn.gemini_prompt_detail, fields)
        raw = await _call_gemini(model, prompt, image_part, timeout=30.0)
        logger.info(f"Gemini extraction successful for shape: {shape_type}")
        return _normalise_response(raw, fields), "gemini", shape_type

    except asyncio.TimeoutError:
        logger.error("Gemini API timed out; using fallback")
    except json.JSONDecodeError as exc:
        logger.error(f"Gemini response not valid JSON: {exc}; using fallback")
    except Exception as exc:
        logger.error(f"Gemini extraction failed: {exc}; using fallback")

    return fallback_params, "fallback", shape_type
