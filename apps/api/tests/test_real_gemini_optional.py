import os
from pathlib import Path

import pytest

from app.cad.ir import validate_cad_ir
from app.services.extraction_provider import RealGeminiProvider


@pytest.mark.asyncio
async def test_real_gemini_blueprint_is_opt_in():
    if os.getenv("RUN_GEMINI_TESTS") != "1":
        pytest.skip("set RUN_GEMINI_TESTS=1 to run the live Gemini integration")
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is required for the live Gemini integration")
    drawing = Path(__file__).parent / "blueprints" / "bracket" / "drawing.svg"
    model = await RealGeminiProvider().extract(drawing.read_bytes(), "image/svg+xml")
    assert model.features
    assert not validate_cad_ir(model)
