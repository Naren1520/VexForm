"""CAD-IR updates used by natural-language modification endpoints."""
from __future__ import annotations
from copy import deepcopy
from app.cad.ir.models import CADModel, CADModification
from app.cad.ir.validation import validate_cad_ir


def apply_modification(model: CADModel, modification: CADModification | dict) -> CADModel:
    if isinstance(modification, dict):
        modification = CADModification.model_validate(modification)
    data = model.model_dump(mode="python")
    features = data["features"]
    by_id = {feature["id"]: feature for feature in features}

    if modification.operation == "update":
        feature = by_id.get(modification.target_feature or "")
        if feature is None:
            raise ValueError(f"unknown target feature '{modification.target_feature}'")
        if not modification.parameter:
            raise ValueError("parameter is required for update")
        feature["parameters"][modification.parameter] = modification.value
    elif modification.operation == "remove":
        target = modification.target_feature or ""
        if any(target in feature.get("depends_on", []) for feature in features):
            raise ValueError(f"cannot remove '{target}'; another feature depends on it")
        data["features"] = [feature for feature in features if feature["id"] != target]
    else:
        if modification.feature is None:
            raise ValueError("feature is required for add")
        if modification.feature.id in by_id:
            raise ValueError(f"feature ID already exists: '{modification.feature.id}'")
        data["features"].append(modification.feature.model_dump(mode="python"))

    updated = CADModel.model_validate(deepcopy(data))
    errors = validate_cad_ir(updated)
    if errors:
        raise ValueError("Invalid modified CAD-IR: " + "; ".join(errors))
    return updated
