"""Transparent confidence scoring for blueprint interpretations."""
from __future__ import annotations
from app.cad.ir.models import CADModel


def calculate_confidence(model: CADModel, validation_errors: list[str] | None = None, occ_success: bool | None = None) -> float:
    feature_scores = [feature.confidence for feature in model.features]
    dimension_scores = [dimension.confidence for dimension in model.dimensions]
    evidence_scores = feature_scores + dimension_scores
    score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else model.overall_confidence
    if validation_errors:
        score -= min(0.35, 0.08 * len(validation_errors))
    if occ_success is True:
        score += 0.05
    elif occ_success is False:
        score -= 0.2
    return round(max(0.0, min(1.0, score)), 3)


def confidence_breakdown(model: CADModel, validation_errors: list[str] | None = None) -> dict:
    return {
        "blueprint": model.blueprint_confidence,
        "features": round(sum(f.confidence for f in model.features) / len(model.features), 3) if model.features else 0.0,
        "dimensions": round(sum(d.confidence for d in model.dimensions) / len(model.dimensions), 3) if model.dimensions else 0.0,
        "validation_penalty": round(min(0.35, 0.08 * len(validation_errors or [])), 3),
        "overall": calculate_confidence(model, validation_errors),
    }
