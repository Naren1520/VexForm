import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(tags=["extract"])

ACCEPTED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


@router.post("/extract")
async def extract_parameters(blueprint: UploadFile = File(...)):
    if blueprint.content_type not in ACCEPTED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail={"error": f"Unsupported media type '{blueprint.content_type}'. Accepted: JPEG, PNG, PDF"},
        )

    image_bytes = await blueprint.read()

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail={"error": "File exceeds the 20 MB size limit."})

    t0 = time.perf_counter()
    from app.services.gemini_client import extract_params
    params_dict, source = await extract_params(image_bytes, blueprint.content_type)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return JSONResponse(content={"params": params_dict, "source": source, "elapsed_ms": round(elapsed_ms, 2)})
