import math
import pytest

from app.cad.executor import execute_cad_ir_shape
from app.cad.ir import CADFeature, CADModel
from .cad_fixtures import (
    extruded_rectangle_model, generic_mechanical_models, lofted_component_model,
    revolved_shaft_model, swept_pipe_model, valve_generic_cad_ir_model,
)

pytest.importorskip("OCC")


def _assert_valid_solid(model):
    shape, tree = execute_cad_ir_shape(model)
    assert shape.ShapeType() == 2
    assert tree
    return shape


def test_sketch_extrude_revolve_sweep_loft_real_occ():
    for model in (extruded_rectangle_model(), revolved_shaft_model(), swept_pipe_model(), lofted_component_model()):
        _assert_valid_solid(model)


def test_topology_referenced_finishing_features_real_occ():
    base = {"sx": 40, "sy": 30, "sz": 20}
    for feature_type, parameters in (
        ("fillet", {"radius": 1, "edges": [{"feature_id": "base", "topology": "edge", "reference": "edge:base:curve:01"}]}),
        ("chamfer", {"size": 1, "edges": [{"feature_id": "base", "topology": "edge", "reference": "edge:base:curve:01"}]}),
        ("shell", {"thickness": 2, "removed_faces": [{"feature_id": "base", "topology": "face", "reference": "top"}]}),
        ("draft", {"angle": 3, "direction": [0, 0, 1], "faces": [{"feature_id": "base", "topology": "face", "reference": "side_01"}]}),
    ):
        model = CADModel(features=[
            CADFeature(id="base", type="box", parameters=base),
            CADFeature(id="finish", type=feature_type, depends_on=["base"], parameters=parameters),
        ])
        _assert_valid_solid(model)


def test_five_generic_mechanical_models_real_occ():
    for model in generic_mechanical_models():
        _assert_valid_solid(model)


def test_generic_valve_fixture_and_lineage_real_occ():
    shape, tree = execute_cad_ir_shape(valve_generic_cad_ir_model())
    assert shape.ShapeType() == 2
    assert len(tree) == 4
    assert tree[-1]["topology"]["lineage"]["derived_from"] == ["bottom_flange"]


def test_modification_rebuilds_real_occ_model():
    from app.cad.services import apply_modification
    model = extruded_rectangle_model()
    updated = apply_modification(model, {
        "operation": "update", "target_feature": "base",
        "parameter": "distance", "value": 60,
    })
    assert execute_cad_ir_shape(updated)[0].ShapeType() == 2
