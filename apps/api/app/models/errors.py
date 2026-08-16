"""Pydantic models for API error responses."""
from typing import Union, Literal
from pydantic import BaseModel


class ValidationError(BaseModel):
    constraint: str
    parameter: Union[str, list[str]]
    submitted_value: Union[float, list[float], str, None] = None
    expected_bound: str


class ValidationErrorResponse(BaseModel):
    errors: list[ValidationError]


class ExportErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    opencascade_version: str
