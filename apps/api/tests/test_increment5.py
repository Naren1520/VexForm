import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.cad.ir import CADFeature, CADModel, semantic_issues, review_state
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
