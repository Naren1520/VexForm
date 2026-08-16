"""GET /health — service health check."""
from fastapi import APIRouter
from app.models.errors import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service status and OpenCascade version."""
    try:
        import importlib.metadata
        occ_version = importlib.metadata.version("pythonocc-core")
    except Exception:
        occ_version = "unknown"

    return HealthResponse(status="ok", opencascade_version=occ_version)
