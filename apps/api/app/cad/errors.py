"""Structured failures raised by deterministic CAD execution."""
from __future__ import annotations


class CADExecutionError(RuntimeError):
    def __init__(self, feature_id: str, code: str, message: str):
        self.feature_id = feature_id
        self.code = code
        self.message = message
        super().__init__(f"{feature_id} [{code}]: {message}")

    def as_dict(self) -> dict[str, str]:
        return {"feature_id": self.feature_id, "code": self.code, "message": self.message}
