import tempfile
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

router = APIRouter(prefix="/export", tags=["export"])


def _get_shape_or_mesh(session_token: str):
    from app.routers.generate import get_session_params
    from app.models.params import LowerValveBodyParams

    params_dict = get_session_params(session_token)
    if params_dict is None:
        return None, None

    try:
        from app.services.geometry_engine import build_lower_valve_body
        shape, _ = build_lower_valve_body(LowerValveBodyParams(**params_dict))
        return shape, params_dict
    except ImportError:
        return None, params_dict


@router.get("/step")
async def export_step(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict = _get_shape_or_mesh(session_token)
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

        return Response(content=content, media_type="application/step",
                        headers={"Content-Disposition": 'attachment; filename="lower_valve_body.step"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STEP failed: {exc}"})


@router.get("/stl")
async def export_stl(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict = _get_shape_or_mesh(session_token)
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

        return Response(content=content, media_type="model/stl",
                        headers={"Content-Disposition": 'attachment; filename="lower_valve_body.stl"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export STL failed: {exc}"})


@router.get("/obj")
async def export_obj(request: Request):
    session_token = request.headers.get("X-Session-Token", "default")
    try:
        shape, params_dict = _get_shape_or_mesh(session_token)
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export OBJ failed: {exc}"})

    if params_dict is None:
        raise HTTPException(404, detail={"error": "No model generated yet. Call /generate first."})
    if shape is None:
        raise HTTPException(503, detail={"error": "OBJ export requires OpenCascade."})

    try:
        from app.services.mesh_serialiser import serialise_mesh_to_obj
        obj_content = serialise_mesh_to_obj(shape)
        return Response(content=obj_content.encode("utf-8"), media_type="text/plain",
                        headers={"Content-Disposition": 'attachment; filename="lower_valve_body.obj"'})
    except Exception as exc:
        raise HTTPException(500, detail={"error": f"Export OBJ failed: {exc}"})
