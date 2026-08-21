import json
from pathlib import Path

import pytest

from app.cad.executor import execute_cad_ir_shape
from app.cad.ir import validate_cad_ir
from app.services.extraction_provider import MockGeminiProvider
from app.cad import shape_metrics


@pytest.mark.asyncio
async def test_five_local_blueprints_mock_to_occ_pipeline():
    root = Path(__file__).parent / "blueprints"
    provider = MockGeminiProvider(root)
    for fixture in ("bracket", "flange", "shaft", "housing", "pulley"):
        model = await provider.extract((root / fixture / "drawing.svg").read_bytes(), "image/svg+xml", fixture)
        assert not validate_cad_ir(model)
        shape, tree = execute_cad_ir_shape(model)
        metrics = shape_metrics(shape)
        assert shape.ShapeType() == 2
        assert metrics["solid_count"] == 1
        expected = json.loads((root / fixture / "expected_cad_ir.json").read_text())
        assert {feature["type"] for feature in expected["features"]} == {feature.type for feature in model.features}
        assert tree
