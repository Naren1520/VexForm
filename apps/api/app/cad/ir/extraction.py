"""Strict envelope for blueprint interpretation responses."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from app.cad.ir.models import CADModel


class BlueprintMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")
    filename: str | None = None
    mime_type: str | None = None
    units: str = "mm"


class Uncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    message: str
    feature_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class CADIRExtractionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    blueprint: BlueprintMetadata
    cad_ir: CADModel
    uncertainties: list[Uncertainty] = Field(default_factory=list)
    validation_hints: list[str] = Field(default_factory=list)
    source: str = "gemini"
    elapsed_ms: float = 0.0

    @property
    def overall_confidence(self) -> float:
        return self.cad_ir.overall_confidence
