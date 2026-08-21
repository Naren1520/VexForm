import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter(tags=["extract"])
logger = logging.getLogger(__name__)

ACCEPTED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


@router.get("/shapes")
async def list_shapes():
    """Return all registered shape types and their display names."""
    from app.shapes.registry import get_registry
    registry = get_registry()
    shapes = registry.list_display_names()
    shapes["programmatic"] = "Any Blueprint (AI Program)"
    return JSONResponse(content={"shapes": shapes})


@router.get("/shapes/{shape_type}/schema")
async def get_shape_schema(shape_type: str):
    """Return the full parameter schema for a specific shape type."""
    from app.shapes.registry import get_registry
    registry = get_registry()
    schema = registry.schema_for(shape_type)
    if schema is None:
        raise HTTPException(status_code=404, detail={"error": f"Unknown shape type: {shape_type}"})
    return JSONResponse(content=schema)


@router.post("/extract")
async def extract_parameters(
    blueprint: UploadFile = File(...),
    shape_type: str = Query(
        default=None,
        description="Compatibility parameter. All blueprint extraction uses the generic CAD-IR pipeline."
    ),
):
    """Extract parameters from a blueprint image.

    Returns shape_type, params, schema, source, elapsed_ms.

    Every blueprint uses the generic CAD-IR interpretation path. The legacy
    shape-specific parameter extraction path is retained only for compatibility
    with callers that do not use blueprint extraction.
    """
    if blueprint.content_type not in ACCEPTED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail={"error": f"Unsupported media type '{blueprint.content_type}'. Accepted: JPEG, PNG, PDF"},
        )

    image_bytes = await blueprint.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail={"error": "File exceeds 20 MB."})

    t0 = time.perf_counter()

    # Generic CAD-IR is now the only blueprint extraction path.
    from app.services.blueprint_to_program import blueprint_to_program, build_schema_from_params

    program_data, source = await blueprint_to_program(image_bytes, blueprint.content_type)
    schema = build_schema_from_params(
        program_data.get("params", {}),
        program_data.get("part_name", "Part")
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return JSONResponse(content={
        "shape_type": "programmatic",
        "params": program_data.get("params", {}),
        "schema": schema,
        "construction_program": program_data.get("construction_program", []),
        "cad_ir": program_data.get("cad_ir"),
        "part_name": program_data.get("part_name", "Part"),
        "material": program_data.get("material", ""),
        "overall_dimensions": program_data.get("overall_dimensions", {}),
        "source": source,
        "review_state": "NEEDS_REVIEW" if source == "fallback" else "EXTRACTED",
        "elapsed_ms": round(elapsed_ms, 2),
    })
