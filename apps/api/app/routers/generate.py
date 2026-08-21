import logging
import sys
import time
import asyncio
import concurrent.futures
import math
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.models.generate_response import GenerateResponse, FeatureNode
from app.models.mesh_payload import MeshPayload, BoundingBox

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

_session_store: dict[str, dict] = {}


def _sanitize_params(raw: dict, defn) -> dict:
    """Coerce raw params to the correct Python types using the shape's field definitions.

    This ensures string-encoded numbers from the frontend (e.g. "118.0") are
    converted to float/int, and None values are replaced with reference fallbacks.
    """
    from app.shapes.registry import get_registry
    schema = get_registry().schema_for(defn.shape_type)
    if schema is None:
        return raw

    result = {}
    for field in schema["fields"]:
        key = field["key"]
        val = raw.get(key)
        ref = defn.reference_values.get(key)

        if field["field_type"] == "string":
            result[key] = str(val) if val is not None else (str(ref) if ref is not None else "")
        elif field["field_type"] == "int":
            try:
                n = int(float(str(val))) if val is not None else None
                result[key] = n if n is not None else int(ref) if ref is not None else 1
            except (ValueError, TypeError):
                result[key] = int(ref) if ref is not None else 1
        else:  # float
            try:
                import math as _math
                n = float(str(val)) if val is not None else None
                if n is None or not _math.isfinite(n):
                    n = float(ref) if ref is not None else 0.0
                result[key] = n
            except (ValueError, TypeError):
                result[key] = float(ref) if ref is not None else 0.0

    return result


class GenerateRequest(BaseModel):
    """Generic generate request — accepts any shape type."""
    shape_type: str
    params: dict[str, Any]
    cad_ir: dict[str, Any] | None = None

    model_config = {"extra": "ignore"}


class ValidateRequest(BaseModel):
    cad_ir: dict[str, Any]


class ModifyRequest(BaseModel):
    cad_ir: dict[str, Any] | None = None
    modification: dict[str, Any]


def _build_sync(shape_type: str, params_dict: dict) -> tuple[dict, list[dict]]:
    """Dispatch build to the correct shape builder via registry.
    
    For shape_type='programmatic', expects params_dict to contain
    a 'construction_program' key with the list of OCC operations.
    """
    # ── Programmatic path: execute AI-generated construction program ───────────
    if shape_type in {"programmatic", "cad_ir"}:
        if shape_type == "cad_ir" or params_dict.get("cad_ir"):
            from app.cad.ir import CADModel
            from app.cad.executor import execute_cad_ir
            return execute_cad_ir(CADModel.model_validate(params_dict["cad_ir"]))
        program = params_dict.get("construction_program")
        if not program or not isinstance(program, list) or len(program) == 0:
            raise ValueError("Programmatic build requires 'construction_program' in params")
        try:
            from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder  # probe OCC
            from app.services.program_executor import execute_program_to_mesh
            logger.info(f"Executing programmatic construction: {len(program)} steps")
            return execute_program_to_mesh(program)
        except ImportError as exc:
            logger.warning(f"OCC not available: {exc}. Using programmatic fallback.")
            from app.services.program_executor_fallback import execute_program_fallback
            return execute_program_fallback(program)

    # ── Registry path: named shape type ───────────────────────────────────────
    from app.shapes.registry import get_registry
    registry = get_registry()
    defn = registry.get(shape_type)
    if defn is None:
        raise ValueError(f"Unknown shape type: {shape_type}")

    try:
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder  # noqa: F401 — probe OCC
        logger.info(f"OCC pipeline starting for shape={shape_type}, python={sys.executable}")
        mesh_data, tree = defn.build_fn(params_dict)
        logger.info(f"OCC pipeline done. Success ops: {sum(1 for n in tree if n['status']=='success')}/{len(tree)}")
        return mesh_data, tree
    except ImportError as exc:
        logger.warning(f"OCC not available: {exc}. Using fallback mesh.")
        return defn.fallback_build_fn(params_dict)
    except Exception as exc:
        logger.error(f"Shape build failed ({type(exc).__name__}): {exc}", exc_info=True)
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
async def generate_model(request: Request, body: GenerateRequest):
    """Generate a 3D model for any registered shape type, or a programmatic build."""
    from app.shapes.registry import get_registry

    # For programmatic builds, skip registry lookup and validation
    if body.shape_type not in {"programmatic", "cad_ir"}:
        registry = get_registry()
        defn = registry.get(body.shape_type)
        if defn is None:
            raise HTTPException(
                status_code=400,
                detail={"error": f"Unknown shape type '{body.shape_type}'. Available: {registry.list_types()}"},
            )
        params = _sanitize_params(body.params, defn)
        logger.debug(f"Sanitized params for {body.shape_type}: {params}")
        try:
            validation = defn.validate_fn(params)
            if validation.has_errors:
                logger.warning(f"Validation errors for {body.shape_type}: {[e.model_dump() for e in validation.errors]}")
                raise HTTPException(
                    status_code=422,
                    detail={"errors": [e.model_dump() for e in validation.errors]},
                )
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning(f"Validator raised exception (non-fatal, proceeding): {exc}")
    else:
        # Programmatic — params pass through as-is (contain construction_program)
        params = dict(body.params)
        if body.cad_ir is not None:
            params["cad_ir"] = body.cad_ir
        elif params.get("construction_program") and not params.get("cad_ir"):
            from app.services.blueprint_to_program import program_to_cad_ir
            params["cad_ir"] = program_to_cad_ir(params["construction_program"])

    t0 = time.perf_counter()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    try:
        loop = asyncio.get_running_loop()
        mesh_data, tree_dicts = await asyncio.wait_for(
            loop.run_in_executor(executor, _build_sync, body.shape_type, params),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=500, detail={"error": "Geometry generation timed out (>120s)"})
    except Exception as exc:
        from app.cad.errors import CADExecutionError
        if isinstance(exc, CADExecutionError):
            raise HTTPException(status_code=422, detail={"error": exc.as_dict()})
        logger.error(f"Generate failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": f"Geometry generation failed: {exc}"})
    finally:
        executor.shutdown(wait=False)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"Generate done in {elapsed_ms:.0f}ms")

    session_token = request.headers.get("X-Session-Token", "default")
    _session_store[session_token] = {"shape_type": body.shape_type, "params": params,
                                     "cad_ir": params.get("cad_ir")}

    bb = mesh_data.get("bounding_box", {"min": [0, 0, 0], "max": [0, 0, 0]})
    mesh = MeshPayload(
        vertices=mesh_data["vertices"],
        indices=mesh_data["indices"],
        normals=mesh_data["normals"],
        bounding_box=BoundingBox(min=bb.get("min", [0, 0, 0]), max=bb.get("max", [0, 0, 0])),
    )

    feature_tree = [FeatureNode(
        id=n["id"], label=n["label"], status=n["status"],
        confidence=n.get("confidence"), output_type=n.get("output_type"), topology=n.get("topology"),
        evidence=n.get("evidence"),
    ) for n in tree_dicts]
    return GenerateResponse(mesh=mesh, feature_tree=feature_tree, elapsed_ms=elapsed_ms)


@router.post("/validate")
async def validate_model(body: ValidateRequest):
    from app.cad.ir import CADModel, validate_cad_ir, review_state, semantic_issues
    model = CADModel.model_validate(body.cad_ir)
    structural_errors = validate_cad_ir(model)
    issues = semantic_issues(model)
    return {"valid": not structural_errors and not any(issue.severity == "error" for issue in issues),
            "errors": structural_errors, "issues": [issue.model_dump() for issue in issues],
            "review_state": review_state(model, issues)}


@router.post("/modify")
async def modify_model(request: Request, body: ModifyRequest):
    from app.cad.ir import CADModel, CADModification
    from app.cad.services import apply_modification

    session_token = request.headers.get("X-Session-Token", "default")
    source = body.cad_ir
    if source is None:
        session = _session_store.get(session_token)
        source = session.get("cad_ir") if session else None
    if source is None:
        raise HTTPException(status_code=404, detail={"error": "No CAD-IR model found"})
    try:
        updated = apply_modification(CADModel.model_validate(source), CADModification.model_validate(body.modification))
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc)})

    params = {"cad_ir": updated.model_dump(mode="json")}
    mesh_data, tree_dicts = await asyncio.get_running_loop().run_in_executor(
        None, _build_sync, "cad_ir", params
    )
    _session_store[session_token] = {"shape_type": "cad_ir", "params": params, "cad_ir": params["cad_ir"]}
    bb = mesh_data.get("bounding_box", {"min": [0, 0, 0], "max": [0, 0, 0]})
    return {"cad_ir": params["cad_ir"], "mesh": {**mesh_data, "bounding_box": bb},
            "feature_tree": tree_dicts}


@router.get("/model/{model_id}")
async def get_model(model_id: str):
    session = _session_store.get(model_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "Model not found"})
    return {"model_id": model_id, "shape_type": session.get("shape_type"),
            "cad_ir": session.get("cad_ir")}


@router.get("/model/{model_id}/features")
async def get_model_features(model_id: str):
    session = _session_store.get(model_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "Model not found"})
    cad_ir = session.get("cad_ir") or {}
    return {"model_id": model_id, "features": cad_ir.get("features", [])}


@router.get("/model/{model_id}/mesh")
async def get_model_mesh(model_id: str):
    session = _session_store.get(model_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "Model not found"})
    mesh_data, tree = await asyncio.get_running_loop().run_in_executor(
        None, _build_sync, session["shape_type"], session["params"]
    )
    return {"model_id": model_id, "mesh": mesh_data, "feature_tree": tree}


def get_session_store(session_token: str) -> dict | None:
    """Return stored {shape_type, params} for a session."""
    return _session_store.get(session_token)


# Backwards compat alias used by export.py
def get_session_params(session_token: str) -> dict | None:
    entry = _session_store.get(session_token)
    if entry is None:
        return None
    return entry.get("params")
