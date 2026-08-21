"""Measured offline benchmark helpers for blueprint-to-CAD-IR fixtures."""
from __future__ import annotations
import time
from app.cad.executor import execute_cad_ir_shape
from app.cad.ir import validate_cad_ir
from app.cad import shape_metrics
from app.services.confidence import calculate_confidence


def benchmark_model(model, fixture_name: str) -> dict:
    started = time.perf_counter()
    validation_errors = validate_cad_ir(model)
    if validation_errors:
        return {"fixture": fixture_name, "validation": "FAIL", "errors": validation_errors, "elapsed_ms": (time.perf_counter() - started) * 1000}
    shape, tree = execute_cad_ir_shape(model)
    return {
        "fixture": fixture_name,
        "validation": "PASS",
        "occ": "PASS",
        "feature_count": len(model.features),
        "successful_features": sum(item["status"] == "success" for item in tree),
        "confidence": calculate_confidence(model, validation_errors, True),
        "metrics": shape_metrics(shape),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }
