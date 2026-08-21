"""Pydantic contract between engineering interpretation and CAD execution."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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

    @model_validator(mode="before")
    @classmethod
    def normalize_view_type(cls, value: Any) -> Any:
        if isinstance(value, str):
            label = value.strip()
            raw_type = label.lower()
            if "section" in raw_type:
                view_type = "section"
            elif "iso" in raw_type or "3d" in raw_type:
                view_type = "isometric"
            elif "top" in raw_type or "bottom" in raw_type:
                view_type = "top"
            elif "front" in raw_type:
                view_type = "front"
            elif "side" in raw_type or raw_type.startswith("view_c"):
                view_type = "side"
            elif "detail" in raw_type:
                view_type = "detail"
            else:
                view_type = "unknown"
            return {"id": raw_type.replace(" ", "_"), "view_type": view_type}
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if "id" not in data and "view_id" in data:
            data["id"] = data["view_id"]
        if "id" not in data:
            label = str(data.get("label") or data.get("type") or "view").strip()
            data["id"] = label.lower().replace(" ", "_").replace("/", "_")
        if "view_type" not in data and "type" in data:
            data["view_type"] = data["type"]
        raw_type = str(data.get("view_type", "unknown")).lower()
        if raw_type not in {"front", "top", "side", "section", "detail", "isometric", "unknown"}:
            if "section" in raw_type or raw_type.startswith("view_a"):
                raw_type = "section"
            elif "iso" in raw_type or "3d" in raw_type:
                raw_type = "isometric"
            elif "top" in raw_type or "bottom" in raw_type:
                raw_type = "top"
            elif "front" in raw_type:
                raw_type = "front"
            elif "side" in raw_type or raw_type.startswith("view_c"):
                raw_type = "side"
            elif "detail" in raw_type:
                raw_type = "detail"
            else:
                raw_type = "unknown"
        data["view_type"] = raw_type
        return data


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

    @model_validator(mode="before")
    @classmethod
    def normalize_feature_contract(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if "depends_on" not in data:
            for key in ("dependencies", "dependency_ids", "inputs"):
                if key in data:
                    dependencies = data[key]
                    data["depends_on"] = dependencies if isinstance(dependencies, list) else [dependencies]
                    break
        parameters = dict(data.get("parameters") or {})
        for key in ("profile_reference", "profile_feature", "profile_sketch", "sketch_id"):
            if key in data and "profile_id" not in parameters:
                parameters["profile_id"] = data[key]
        for key in ("path_reference", "path_feature", "path_sketch", "path_id"):
            if key in data and "path_id" not in parameters:
                parameters["path_id"] = data[key]
        data["parameters"] = parameters
        feature_type = str(data.get("type", "")).lower().strip()
        if feature_type == "extrusion":
            data["type"] = "extrude"
        return data


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
