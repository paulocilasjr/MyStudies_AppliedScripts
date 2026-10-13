"""Versioned input contract. Probability always refers to the responder class."""
from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass
from typing import Any

MODALITIES = ("clinical", "mif", "fused")
SCHEMA_VERSION = "1.0"
PARTITIONS = {"unspecified", "train", "validation", "test", "out_of_fold", "synthetic"}


class ContractError(ValueError):
    """Input does not satisfy the shared prediction contract."""


def _object(value: Any, path: str, allowed: set[str]) -> dict:
    if not isinstance(value, dict):
        raise ContractError(f"{path} must be an object")
    if not all(isinstance(k, str) for k in value):
        raise ContractError(f"{path} field names must be strings")
    if set(value) - allowed:
        raise ContractError(f"{path} has unsupported fields: {', '.join(sorted(set(value) - allowed))}")
    return value


def _text(value: Any, path: str, limit: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ContractError(f"{path} must be a {'possibly empty ' if empty else 'nonempty '}string")
    if len(value) > limit or any(ord(c) < 32 and c not in '\n\t\r' for c in value):
        raise ContractError(f"{path} exceeds its size limit or contains control characters")
    return value.strip()


def _number(value: Any, path: str, *, probability: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{path} must be a finite number")
    try:
        result = float(value)
    except (ValueError, OverflowError):
        raise ContractError(f"{path} must be a finite number") from None
    if not math.isfinite(result) or (probability and not 0 <= result <= 1):
        raise ContractError(f"{path} must be {'in [0, 1]' if probability else 'finite'}")
    return result


def _feature(value: Any, path: str) -> dict:
    item = _object(value, path, {"feature", "value", "unit", "direction", "attribution"})
    name = _text(item.get("feature"), f"{path}.feature", 160)
    measurement = item.get("value")
    if isinstance(measurement, (int, float)) and not isinstance(measurement, bool):
        measurement = _number(measurement, f"{path}.value")
    elif isinstance(measurement, str):
        measurement = _text(measurement, f"{path}.value", 256, empty=True)
    elif measurement is not None and not isinstance(measurement, bool):
        raise ContractError(f"{path}.value must be a number, string, boolean, or null")
    attribution = item.get("attribution")
    if attribution is not None:
        att = _object(attribution, f"{path}.attribution", {"method", "value", "scale"})
        attribution = {
            "method": _text(att.get("method"), f"{path}.attribution.method", 80),
            "value": _number(att.get("value"), f"{path}.attribution.value"),
            "scale": _text(att.get("scale"), f"{path}.attribution.scale", 80),
        }
    return {
        "feature": name, "value": measurement,
        "unit": _text(item.get("unit", ""), f"{path}.unit", 80, empty=True),
        "direction": _text(item.get("direction", "not supplied"), f"{path}.direction", 160),
        "attribution": attribution,
    }


@dataclass(frozen=True)
class PatientPrediction:
    """Validated canonical input; use from_dict rather than direct construction."""
    data: dict

    @classmethod
    def from_dict(cls, value: Any) -> "PatientPrediction":
        obj = _object(value, "patient", {"schema_version", "patient_id", "predictions", "top_features",
                                           "clinical_context", "response_definition", "ground_truth", "evaluation_partition"})
        if obj.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ContractError("schema_version must be 1.0")
        patient_id = _text(obj.get("patient_id"), "patient_id", 100)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", patient_id):
            raise ContractError("patient_id must be a pseudonymous identifier using letters, numbers, _.:-")
        supplied = _object(obj.get("predictions"), "predictions", set(MODALITIES))
        if not supplied:
            raise ContractError("at least one prediction is required")
        predictions = {}
        for modality in MODALITIES:
            if modality not in supplied:
                continue
            pred = _object(supplied[modality], f"predictions.{modality}",
                           {"probability", "model_id", "calibration", "decision_threshold"})
            calibration = pred.get("calibration", "unknown")
            if not isinstance(calibration, str) or calibration not in {"unknown", "uncalibrated", "calibrated"}:
                raise ContractError(f"predictions.{modality}.calibration must be unknown, uncalibrated, or calibrated")
            threshold = pred.get("decision_threshold")
            predictions[modality] = {
                "probability": _number(pred.get("probability"), f"predictions.{modality}.probability", probability=True),
                "model_id": _text(pred.get("model_id", "unspecified"), f"predictions.{modality}.model_id", 160),
                "calibration": calibration,
                "decision_threshold": None if threshold is None else _number(threshold, f"predictions.{modality}.decision_threshold", probability=True),
            }
        features = _object(obj.get("top_features", {}), "top_features", set(MODALITIES))
        top_features = {}
        for modality, values in features.items():
            if modality not in predictions:
                raise ContractError(f"top_features.{modality} requires a {modality} prediction")
            if not isinstance(values, list) or len(values) > 10:
                raise ContractError(f"top_features.{modality} must be a list of at most 10 features")
            top_features[modality] = [_feature(v, f"top_features.{modality}[{i}]") for i, v in enumerate(values)]
            if len({f['feature'] for f in top_features[modality]}) != len(values):
                raise ContractError(f"top_features.{modality} contains duplicate feature names")
        label = obj.get("ground_truth")
        if label is not None and (type(label) is not int or label not in (0, 1)):
            raise ContractError("ground_truth must be integer 0 (non-responder), 1 (responder), or null")
        partition = obj.get("evaluation_partition", "unspecified")
        if not isinstance(partition, str) or partition not in PARTITIONS:
            raise ContractError("evaluation_partition is not supported")
        return cls({
            "schema_version": SCHEMA_VERSION, "patient_id": patient_id, "predictions": predictions,
            "top_features": top_features,
            "clinical_context": _text(obj.get("clinical_context", ""), "clinical_context", 2000, empty=True),
            "response_definition": _text(obj.get("response_definition", "Not specified"), "response_definition", 500),
            "ground_truth": label, "evaluation_partition": partition,
        })

    @property
    def patient_id(self) -> str:
        return self.data["patient_id"]

    def to_dict(self) -> dict:
        return copy.deepcopy(self.data)
