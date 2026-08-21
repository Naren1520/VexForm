"""Small filesystem-backed model/revision store behind a replaceable interface."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any


class ModelStore:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or Path(__file__).parents[2] / ".vexform_models")
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, model_id: str) -> Path:
        return self.root / f"{model_id}.json"

    def create(self, cad_ir: dict[str, Any], blueprint: dict[str, Any] | None = None) -> dict[str, Any]:
        model_id = f"model_{uuid.uuid4().hex[:12]}"
        record = {
            "id": model_id, "created_at": time.time(), "blueprint": blueprint or {},
            "revisions": [{"revision": 1, "created_at": time.time(), "cad_ir": cad_ir, "reason": "initial extraction"}],
            "current_revision": 1, "generation_status": "EXTRACTED", "validation": {}, "metrics": {}, "exports": {},
        }
        self.save(record)
        return record

    def get(self, model_id: str) -> dict[str, Any] | None:
        path = self._path(model_id)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def save(self, record: dict[str, Any]) -> None:
        self._path(record["id"]).write_text(json.dumps(record, indent=2), encoding="utf-8")

    def add_revision(self, model_id: str, cad_ir: dict[str, Any], reason: str) -> dict[str, Any]:
        record = self.get(model_id)
        if record is None:
            raise KeyError(model_id)
        revision = len(record["revisions"]) + 1
        record["revisions"].append({"revision": revision, "created_at": time.time(), "cad_ir": cad_ir, "reason": reason})
        record["current_revision"] = revision
        record["generation_status"] = "EXTRACTED"
        self.save(record)
        return record

    def restore(self, model_id: str, revision: int) -> dict[str, Any]:
        record = self.get(model_id)
        if record is None:
            raise KeyError(model_id)
        source = next((item for item in record["revisions"] if item["revision"] == revision), None)
        if source is None:
            raise KeyError(f"revision {revision}")
        return self.add_revision(model_id, source["cad_ir"], f"restore revision {revision}")
