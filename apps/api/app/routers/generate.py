import logging
import sys
import time
import asyncio
import concurrent.futures
from fastapi import APIRouter, HTTPException, Request

from app.models.params import LowerValveBodyParams
from app.models.generate_response import GenerateResponse, FeatureNode
from app.models.mesh_payload import MeshPayload, BoundingBox
from app.services.validator import validate_constraints

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

_session_store: dict[str, dict] = {}


def _run_occ_pipeline(params_dict: dict) -> tuple[dict, list[dict]]:
    """Run full OCC Boolean pipeline. Raises on any failure — no fallback."""
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from app.models.params import LowerValveBodyParams as P
    from app.services.geometry_engine import build_lower_valve_body
    from app.services.mesh_serialiser import serialise_mesh

    logger.info(f"OCC pipeline starting in thread, python={sys.executable}")
    p = P(**params_dict)
    shape, tree = build_lower_valve_body(p)
    logger.info(f"OCC pipeline done. Success ops: {sum(1 for n in tree if n['status']=='success')}/{len(tree)}")
    return serialise_mesh(shape), tree


def _build_sync(params_dict: dict) -> tuple[dict, list[dict]]:
    try:
        return _run_occ_pipeline(params_dict)
    except ImportError as exc:
        logger.warning(f"OCC not available: {exc}. Using fallback mesh.")
        from app.services.fallback_mesh import build_fallback_lower_valve_body
        return build_fallback_lower_valve_body(params_dict)
    except Exception as exc:
        logger.error(f"OCC pipeline failed ({type(exc).__name__}): {exc}", exc_info=True)
        raise


@router.get("/debug/occ")
async def debug_occ():
    occ_ok = False
    occ_error = None
    try:
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        cyl = BRepPrimAPI_MakeCylinder(10.0, 20.0)
        occ_ok = cyl.IsDone()
    except Exception as exc:
        occ_error = str(exc)

    def thread_test():
        try:
            from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
            cyl = BRepPrimAPI_MakeCylinder(10.0, 20.0)
            return cyl.IsDone(), None
        except Exception as exc:
            return False, str(exc)

    with concurrent.futures.ThreadPoolExecutor() as ex:
        loop = asyncio.get_running_loop()
        thread_ok, thread_error = await loop.run_in_executor(ex, thread_test)

    return {
        "main_thread_occ": occ_ok,
        "main_thread_error": occ_error,
        "worker_thread_occ": thread_ok,
        "worker_thread_error": thread_error,
        "python": sys.executable,
    }


@router.get("/debug/occ-full")
async def debug_occ_full():
    """Run a minimal Boolean cut test to confirm OCC works end-to-end."""
    def _test():
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
        outer = BRepPrimAPI_MakeCylinder(18.0, 118.0).Shape()
        bore = BRepPrimAPI_MakeCylinder(14.0, 120.0).Shape()
        cut = BRepAlgoAPI_Cut(outer, bore)
        return {"done": cut.IsDone(), "null": cut.Shape().IsNull()}

    with concurrent.futures.ThreadPoolExecutor() as ex:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(ex, _test)
    return result


@router.post("/generate", response_model=GenerateResponse)
async def generate_model(request: Request, params: LowerValveBodyParams):
    validation = validate_constraints(params)
    if validation.has_errors:
        raise HTTPException(status_code=422, detail={"errors": [e.model_dump() for e in validation.errors]})

    t0 = time.perf_counter()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    try:
        loop = asyncio.get_running_loop()
        mesh_data, tree_dicts = await asyncio.wait_for(
            loop.run_in_executor(executor, _build_sync, params.model_dump()),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=500, detail={"error": "Geometry generation timed out (>120s)"})
    except Exception as exc:
        logger.error(f"Generate failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": f"Geometry generation failed: {exc}"})
    finally:
        executor.shutdown(wait=False)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"Generate done in {elapsed_ms:.0f}ms")

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


