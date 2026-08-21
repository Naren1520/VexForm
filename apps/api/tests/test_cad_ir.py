from app.cad.executor import topological_features
from app.cad.ir import CADFeature, CADModel, validate_cad_ir
from app.cad.services import apply_modification
from .cad_fixtures import (
    complex_prismatic_model,
    extruded_rectangle_model,
    lofted_component_model,
    revolved_shaft_model,
    swept_pipe_model,
)


def test_feature_graph_is_topologically_ordered():
    model = CADModel(features=[
        CADFeature(id="hole", type="hole", depends_on=["base"], parameters={"r": 2, "h": 10}),
        CADFeature(id="base", type="box", parameters={"sx": 20, "sy": 20, "sz": 10}),
    ])
    assert [feature.id for feature in topological_features(model)] == ["base", "hole"]


def test_dependency_validation_rejects_cycles_and_unknown_features():
    model = CADModel(features=[
        CADFeature(id="a", type="box", depends_on=["b"]),
        CADFeature(id="b", type="future_feature", depends_on=["a"]),
    ])
    errors = validate_cad_ir(model)
    assert any("unsupported feature" in error for error in errors)
    assert any("circular dependency" in error for error in errors)


def test_modification_updates_feature_without_code_execution():
    model = CADModel(features=[
        CADFeature(id="base", type="cylinder", parameters={"r": 20, "h": 40}),
        CADFeature(id="hole", type="hole", depends_on=["base"], parameters={"r": 5, "h": 40}),
    ])
    modified = apply_modification(model, {
        "operation": "update",
        "target_feature": "hole",
        "parameter": "r",
        "value": 12.5,
    })
    assert modified.features[1].parameters["r"] == 12.5


def test_closed_sketch_and_extrusion_graph_is_valid():
    model = extruded_rectangle_model()
    assert validate_cad_ir(model) == []
    assert [feature.id for feature in topological_features(model)] == ["sketch_01", "base"]


def test_open_closed_profile_is_rejected():
    model = extruded_rectangle_model()
    model.sketches[0].entities[-1].parameters["end"] = [1, 1]
    assert any("endpoints are not connected" in error for error in validate_cad_ir(model))


def test_complex_fixture_has_dependency_chain():
    model = complex_prismatic_model()
    assert validate_cad_ir(model) == []
    assert [feature.id for feature in topological_features(model)] == ["base", "hole", "fillet", "chamfer"]


def test_revolve_sweep_and_loft_fixtures_are_valid_graphs():
    for model in (revolved_shaft_model(), swept_pipe_model(), lofted_component_model()):
        assert validate_cad_ir(model) == []
        assert topological_features(model)
