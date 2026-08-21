import pytest

from app.cad.executor import execute_cad_ir_shape
from app.cad.ir import CADFeature, CADModel
from app.services.mesh_serialiser import serialise_mesh_to_obj

pytest.importorskip("OCC")


def test_step_stl_obj_exports_are_non_empty(tmp_path):
    model = CADModel(features=[CADFeature(id="base", type="box", parameters={"sx": 10, "sy": 20, "sz": 30})])
    shape, _ = execute_cad_ir_shape(model)

    from OCC.Core.IFSelect import IFSelect_RetDone
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCC.Core.StlAPI import StlAPI_Writer

    step_path = tmp_path / "fixture.step"
    step_writer = STEPControl_Writer()
    step_writer.Transfer(shape, STEPControl_AsIs)
    assert step_writer.Write(str(step_path)) == IFSelect_RetDone
    assert step_path.stat().st_size > 0

    stl_path = tmp_path / "fixture.stl"
    BRepMesh_IncrementalMesh(shape, 0.1, False, 0.5, True).Perform()
    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(False)
    stl_writer.Write(shape, str(stl_path))
    assert stl_path.stat().st_size > 0

    obj = serialise_mesh_to_obj(shape, object_name="fixture")
    assert obj.startswith("# VexForm")
    assert "v " in obj and "f " in obj