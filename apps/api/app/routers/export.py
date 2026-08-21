import tempfile
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

router = APIRouter(prefix="/export", tags=["export"])


def _get_shape_for_export(session_token: str):
    """Rebuild the OCC shape for the last generated model in this session."""
    from app.routers.generate import get_session_store
    from app.shapes.registry import get_registry

    session = get_session_store(session_token)
    if session is None:
        return None, None, None

    shape_type = session.get("shape_type", "programmatic")
    params_dict = session.get("params", {})

    registry = get_registry()
    defn = registry.get(shape_type)
    if defn is None:
        return None, None, shape_type

    try:
        # Rebuild OCC shape (build_fn returns mesh_data + tree; we need the raw shape)
        # For shapes that have an OCC-backed builder we go through the geometry engine directly.
        # The build_fn is designed for mesh output, so we use a shape-aware rebuild path.
        shape = _rebuild_occ_shape(shape_type, params_dict)
        return shape, params_dict, shape_type
    except ImportError:
        return None, params_dict, shape_type
    except Exception as exc:
        raise RuntimeError(f"Export rebuild failed: {exc}") from exc


def _rebuild_occ_shape(shape_type: str, params_dict: dict):
    """Rebuild the raw OCC TopoDS_Shape for export without mesh serialisation."""
    if shape_type in {"programmatic", "cad_ir"} and params_dict.get("cad_ir"):
        from app.cad.ir import CADModel
        from app.cad.executor import execute_cad_ir_shape
        return execute_cad_ir_shape(CADModel.model_validate(params_dict["cad_ir"]))[0]
    if shape_type == "lower_valve_body":
        from app.models.params import LowerValveBodyParams
        from app.services.geometry_engine import build_lower_valve_body
        p = LowerValveBodyParams(**params_dict)
        shape, _ = build_lower_valve_body(p)
        return shape
    raise NotImplementedError(f"OCC export requires CAD-IR for shape type: {shape_type}")


def _filename(shape_type: str, ext: str) -> str:
    return f"{shape_type}.{ext}"


@router.get("/step")
async def export_step(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict, shape_type = _get_shape_for_export(session_token)
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STEP failed: {exc}"})

    if params_dict is None:
        raise HTTPException(404, detail={"error": "No model generated yet. Call /generate first."})
    if shape is None:
        raise HTTPException(503, detail={"error": "STEP export requires OpenCascade. Install: conda install -c conda-forge pythonocc-core=7.9.0"})

    try:
        from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
        from OCC.Core.IFSelect import IFSelect_RetDone

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp_path = tmp.name

        writer = STEPControl_Writer()
        writer.Transfer(shape, STEPControl_AsIs)
        if writer.Write(tmp_path) != IFSelect_RetDone:
            raise RuntimeError("STEPControl_Writer failed")

        with open(tmp_path, "rb") as f:
            content = f.read()
        os.unlink(tmp_path)

        fname = _filename(shape_type, "step")
        return Response(content=content, media_type="application/step",
                        headers={"Content-Disposition": f'attachment; filename="{fname}"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STEP failed: {exc}"})


@router.get("/stl")
async def export_stl(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict, shape_type = _get_shape_for_export(session_token)
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STL failed: {exc}"})

    if params_dict is None:
        raise HTTPException(404, detail={"error": "No model generated yet. Call /generate first."})
    if shape is None:
        raise HTTPException(503, detail={"error": "STL export requires OpenCascade."})

    try:
        from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
        from OCC.Core.StlAPI import StlAPI_Writer

        BRepMesh_IncrementalMesh(shape, 0.1, False, 0.5, True).Perform()

        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name

        writer = StlAPI_Writer()
        writer.SetASCIIMode(False)
        writer.Write(shape, tmp_path)

        with open(tmp_path, "rb") as f:
            content = f.read()
        os.unlink(tmp_path)

        fname = _filename(shape_type, "stl")
        return Response(content=content, media_type="model/stl",
                        headers={"Content-Disposition": f'attachment; filename="{fname}"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STL failed: {exc}"})


@router.get("/obj")
async def export_obj(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict, shape_type = _get_shape_for_export(session_token)
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export OBJ failed: {exc}"})

    if params_dict is None:
        raise HTTPException(404, detail={"error": "No model generated yet. Call /generate first."})
    if shape is None:
        raise HTTPException(503, detail={"error": "OBJ export requires OpenCascade."})

    try:
        from app.services.mesh_serialiser import serialise_mesh_to_obj
        # Use a display-friendly name for the OBJ header
        obj_name = shape_type.replace("_", " ").title().replace(" ", "")
        obj_content = serialise_mesh_to_obj(shape, object_name=obj_name)
        fname = _filename(shape_type, "obj")
        return Response(content=obj_content.encode("utf-8"), media_type="text/plain",
                        headers={"Content-Disposition": f'attachment; filename="{fname}"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export OBJ failed: {exc}"})
