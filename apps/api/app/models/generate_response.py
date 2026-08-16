"""Pydantic model for the geometry generation response."""
from typing import Optional, Literal
from pydantic import BaseModel
from app.models.mesh_payload import MeshPayload


class FeatureNode(BaseModel):
    id: str
    label: str
    status: Literal["success", "failed", "pending"]
    geometry_ref: Optional[str] = None


class GenerateResponse(BaseModel):
    mesh: MeshPayload
    feature_tree: list[FeatureNode]
    elapsed_ms: float
