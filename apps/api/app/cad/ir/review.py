"""Human-review and semantic validation results for CAD-IR."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from app.cad.ir.models import CADModel


class ValidationIssue(BaseModel):
    severity: Literal["warning", "error"]
    code: str
    message: str
    features: list[str] = Field(default_factory=list)
    suggestion: str | None = None


def semantic_issues(model: CADModel) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    features = {feature.id: feature for feature in model.features}
    for feature in model.features:
        if not feature.enabled:
            continue
        p = feature.parameters
        if feature.type in {"hole", "cut_cylinder"} and "diameter" in p:
            parent = next((features[item] for item in feature.depends_on if item in features), None)
            parent_diameter = p.get("parent_diameter") or (parent.parameters.get("diameter") if parent else None)
            if parent_diameter is not None and float(p["diameter"]) >= float(parent_diameter):
                issues.append(ValidationIssue(severity="error", code="GEOMETRIC_CONSTRAINT_CONFLICT", message="Hole diameter exceeds its parent diameter.", features=[feature.id, parent.id] if parent else [feature.id]))
        if feature.type == "pattern":
            count = p.get("count", 1)
            if float(count) < 1 or int(float(count)) != float(count):
                issues.append(ValidationIssue(severity="error", code="INVALID_PATTERN", message="Pattern count must be a positive integer.", features=[feature.id]))
    return issues


def review_state(model: CADModel, issues: list[ValidationIssue] | None = None, threshold: float = 0.7) -> str:
    issues = issues or semantic_issues(model)
    if any(issue.severity == "error" for issue in issues):
        return "NEEDS_REVIEW"
    return "NEEDS_REVIEW" if model.overall_confidence < threshold else "VALIDATED"
