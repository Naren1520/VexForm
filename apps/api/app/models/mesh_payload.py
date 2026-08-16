"""Pydantic model for the serialised mesh payload."""
from pydantic import BaseModel


class BoundingBox(BaseModel):
    min: list[float]
    max: list[float]


class MeshPayload(BaseModel):
    vertices: list[float]
    indices: list[int]
    normals: list[float]
    bounding_box: BoundingBox
