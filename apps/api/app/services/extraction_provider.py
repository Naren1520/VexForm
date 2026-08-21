"""Structured blueprint interpretation providers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.cad.ir import CADModel


class GeminiProvider(Protocol):
    async def extract(self, image_bytes: bytes, mime_type: str, fixture_name: str | None = None) -> CADModel:
        ...


class MockGeminiProvider:
    """Offline deterministic provider used by tests and local development."""

    def __init__(self, fixtures_root: str | Path | None = None):
        self.fixtures_root = Path(fixtures_root or Path(__file__).parents[2] / "tests" / "blueprints")

    async def extract(self, image_bytes: bytes, mime_type: str, fixture_name: str | None = None) -> CADModel:
        if not fixture_name:
            raise ValueError("fixture_name is required for MockGeminiProvider")
        path = self.fixtures_root / fixture_name / "expected_cad_ir.json"
        if not path.exists():
            raise ValueError(f"blueprint fixture not found: {fixture_name}")
        return CADModel.model_validate(json.loads(path.read_text(encoding="utf-8")))


class RealGeminiProvider:
    """Gemini Vision adapter. The response is always parsed into CADModel."""

    async def extract(self, image_bytes: bytes, mime_type: str, fixture_name: str | None = None) -> CADModel:
        from app.services.blueprint_to_program import blueprint_to_program
        payload, source = await blueprint_to_program(image_bytes, mime_type)
        if source != "gemini" or not payload.get("cad_ir"):
            raise ValueError("Gemini did not return CAD-IR")
        return CADModel.model_validate(payload["cad_ir"])


async def extract_with_provider(provider: GeminiProvider, image_bytes: bytes, mime_type: str, fixture_name: str | None = None) -> CADModel:
    """Shared provider entry point used by offline and live integrations."""
    return await provider.extract(image_bytes, mime_type, fixture_name)
