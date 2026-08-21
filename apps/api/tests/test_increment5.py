import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.cad.ir import CADFeature, CADModel, semantic_issues, review_state, validate_cad_ir
from app.cad.ir.models import DrawingView
from app.cad.ir.extraction import CADIRExtractionResponse
from app.services.confidence import calculate_confidence
from app.services.extraction_provider import MockGeminiProvider
from app.services.model_store import ModelStore


@pytest.mark.asyncio
async def test_mock_provider_reads_local_blueprint_fixture():
    provider = MockGeminiProvider(Path(__file__).parent / "blueprints")
    model = await provider.extract(b"fixture", "image/svg+xml", "bracket")
    assert {feature.type for feature in model.features} == {"box"}
    assert len(model.views) == 2


def test_strict_extraction_envelope_rejects_unknown_top_level_fields():
    payload = {"blueprint": {"units": "mm"}, "cad_ir": {"features": []}, "unexpected": True}
    with pytest.raises(ValidationError):
        CADIRExtractionResponse.model_validate(payload)


def test_semantic_conflict_and_review_state_are_structured():
    model = CADModel(blueprint_confidence=0.9, overall_confidence=0.9, features=[
        CADFeature(id="boss", type="cylinder", parameters={"r": 10, "h": 20}),
        CADFeature(id="hole", type="hole", depends_on=["boss"], parameters={"diameter": 25, "parent_diameter": 20}, confidence=0.4),
    ])
    issues = semantic_issues(model)
    assert issues[0].code == "GEOMETRIC_CONSTRAINT_CONFLICT"
    assert review_state(model, issues) == "NEEDS_REVIEW"
    assert calculate_confidence(model, [issue.message for issue in issues]) < 0.9


def test_extrusion_dimension_aliases_are_accepted():
    for key in ("distance", "depth", "height", "length", "thickness", "extrusion_distance", "extrusion_length", "stem_length", "port_length"):
        model = CADModel(features=[CADFeature(id="extrude", type="extrude", parameters={key: 40})])
        assert not any("extrusion" in error for error in validate_cad_ir(model))
    model = CADModel(features=[CADFeature(id="extrude", type="extrude", parameters={"dimensions": {"port_length": 40}})])
    assert not any("extrusion" in error for error in validate_cad_ir(model))


def test_gemini_dependency_aliases_are_normalized():
    feature = CADFeature.model_validate({
        "id": "f1_main_stem", "type": "extrusion",
        "dependencies": ["profile_01"],
        "profile_reference": "profile_01",
        "parameters": {"length_mm": 25},
    })
    assert feature.type == "extrude"
    assert feature.depends_on == ["profile_01"]
    assert feature.parameters["profile_id"] == "profile_01"


def test_explicit_profile_dimensions_can_represent_first_extrusion():
    feature = CADFeature.model_validate({
        "id": "f1", "type": "extrude",
        "parameters": {"diameter": 36, "length": 118},
    })
    assert feature.depends_on == []
    model = CADModel(features=[CADFeature(id="extrude", type="extrude", parameters={"dimensions": [{"name": "length_mm", "value": 40}]} )])
    assert not any("extrusion" in error for error in validate_cad_ir(model))


def test_disabled_feature_is_preserved_in_ir():
    model = CADModel(features=[CADFeature(id="optional", type="fillet", enabled=False)])
    assert model.features[0].enabled is False


def test_model_store_revisions_and_restore(tmp_path):
    store = ModelStore(tmp_path)
    original = {"version": "1.0", "units": "mm", "features": []}
    record = store.create(original, {"filename": "drawing.svg"})
    updated = {**original, "metadata": {"edited": True}}
    store.add_revision(record["id"], updated, "user edit")
    restored = store.restore(record["id"], 1)
    loaded = store.get(record["id"])
    assert restored["current_revision"] == 3
    assert loaded["revisions"][-1]["cad_ir"] == original


def test_fixture_metadata_is_semantic_not_byte_comparison():
    root = Path(__file__).parent / "blueprints"
    for fixture in ("bracket", "flange", "shaft", "housing", "pulley", "valve"):
        metadata = json.loads((root / fixture / "metadata.json").read_text())
        assert metadata["name"] == fixture
        assert (root / fixture / "drawing.svg").exists()
        assert (root / fixture / "expected_cad_ir.json").exists()


def test_gemini_view_type_aliases_are_normalized():
    assert DrawingView.model_validate({"id": "view_front_section", "type": "section_a_a"}).view_type == "section"
    assert DrawingView.model_validate({"id": "view_iso", "type": "3D Render"}).view_type == "isometric"
    assert DrawingView.model_validate({"view_id": "view_top", "view_type": "top"}).id == "view_top"
    assert DrawingView.model_validate("SECTION A-A").view_type == "section"
    assert DrawingView.model_validate({"type": "top", "label": "Top View"}).id == "top_view"
