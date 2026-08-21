"""Pydantic contract between engineering interpretation and CAD execution."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CoordinateSystem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0)
    y_axis: tuple[float, float, float] = (0.0, 1.0, 0.0)
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0)


class Dimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: float | None
    unit: str = "mm"
    tolerance: float | None = Field(default=None, ge=0)
    confidence: float = Field(default=1.0, ge=0, le=1)
    source: str | None = None
    reason: str | None = None

    @field_validator("value")
    @classmethod
    def finite_value(cls, value: float) -> float:
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("dimension value must be finite")
        return value


class GeometryEntity(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    type: Literal["line", "arc", "circle", "ellipse", "spline", "point"]
    parameters: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0, le=1)


class Sketch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    plane: str = "XY"
    entities: list[GeometryEntity] = Field(default_factory=list)
    closed: bool | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)


class DrawingView(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    view_type: Literal["front", "top", "side", "section", "detail", "isometric", "unknown"]
    features: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0, le=1)


class CADFeature(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0, le=1)
    label: str | None = None
    output_type: Literal["wire", "face", "solid", "compound", "surface"] | None = None
    enabled: bool = True
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class CADModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    units: str = "mm"
    coordinate_system: CoordinateSystem = Field(default_factory=CoordinateSystem)
    views: list[DrawingView] = Field(default_factory=list)
    sketches: list[Sketch] = Field(default_factory=list)
    features: list[CADFeature] = Field(default_factory=list)
    dimensions: list[Dimension] = Field(default_factory=list)
    constraints: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    blueprint_confidence: float = Field(default=1.0, ge=0, le=1)
    overall_confidence: float = Field(default=1.0, ge=0, le=1)


class CADModification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["update", "add", "remove"]
    target_feature: str | None = None
    parameter: str | None = None
    value: Any = None
    feature: CADFeature | None = None

    @field_validator("target_feature")
    @classmethod
    def target_required_for_update_remove(cls, value: str | None, info):
        operation = info.data.get("operation")
        if operation in {"update", "remove"} and not value:
            raise ValueError(f"target_feature is required for {operation}")
        return value
