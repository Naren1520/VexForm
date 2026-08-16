import time
import asyncio
import concurrent.futures
from fastapi import APIRouter, HTTPException, Request

from app.models.params import LowerValveBodyParams
from app.models.generate_response import GenerateResponse, FeatureNode
from app.models.mesh_payload import MeshPayload, BoundingBox
from app.services.validator import validate_constraints

router = APIRouter(tags=["generate"])

_session_store: dict[str, dict] = {}
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def _build_sync(params_dict: dict) -> tuple[dict, list[dict]]:
    try:
        from app.models.params import LowerValveBodyParams as P
        from app.services.geometry_engine import build_lower_valve_body
        from app.services.mesh_serialiser import serialise_mesh

        p = P(**params_dict)
        shape, tree = build_lower_valve_body(p)
        return serialise_mesh(shape), tree
    except ImportError:
        from app.services.fallback_mesh import build_fallback_lower_valve_body
        return build_fallback_lower_valve_body(params_dict)


@router.post("/generate", response_model=GenerateResponse)
async def generate_model(request: Request, params: LowerValveBodyParams):
    validation = validate_constraints(params)
    if validation.has_errors:
        raise HTTPException(status_code=422, detail={"errors": [e.model_dump() for e in validation.errors]})

    t0 = time.perf_counter()
    loop = asyncio.get_running_loop()

    try:
        mesh_data, tree_dicts = await asyncio.wait_for(
            loop.run_in_executor(_executor, _build_sync, params.model_dump()),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=500, detail={"error": "Geometry generation timed out (>120s)"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": f"Geometry generation failed: {exc}"})

    elapsed_ms = (time.perf_counter() - t0) * 1000

    session_token = request.headers.get("X-Session-Token", "default")
    _session_store[session_token] = params.model_dump()

    bb = mesh_data.get("bounding_box", {"min": [0, 0, 0], "max": [0, 0, 0]})
    mesh = MeshPayload(
        vertices=mesh_data["vertices"],
        indices=mesh_data["indices"],
        normals=mesh_data["normals"],
        bounding_box=BoundingBox(min=bb.get("min", [0, 0, 0]), max=bb.get("max", [0, 0, 0])),
    )

    feature_tree = [FeatureNode(id=n["id"], label=n["label"], status=n["status"]) for n in tree_dicts]

    return GenerateResponse(mesh=mesh, feature_tree=feature_tree, elapsed_ms=elapsed_ms)


def get_session_params(session_token: str) -> dict | None:
    return _session_store.get(session_token)
