"""Audit optional paired tile tables without promoting attention to response scores."""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import math
from pathlib import Path

from .schema import ContractError

PREDICTIONS_FILE = "predictions/tile_predictions.csv"
FEATURES_FILE = "predictions/tile_features.csv"
PREDICTION_FIELDS = ["Patient_id", "slide_id", "tile_x", "tile_y", "tile_prob"]
FEATURE_PREFIX = ["Patient_id", "tile_id", "tile_x", "tile_y", "attention"]


def _text(value: str, path: str, limit: int = 256) -> str:
    if (not isinstance(value, str) or not value or value != value.strip() or len(value) > limit
            or any(ord(character) < 32 for character in value)):
        raise ContractError(f"{path} must be a bounded nonempty identifier without surrounding whitespace or control characters")
    return value


def _number(value: str, path: str, *, unit_interval: bool = False, coordinate: bool = False) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        raise ContractError(f"{path} must be numeric and finite") from None
    if not number.is_finite() or not math.isfinite(float(number)):
        raise ContractError(f"{path} must be finite")
    if unit_interval and not 0 <= number <= 1:
        raise ContractError(f"{path} must be in [0, 1]")
    if coordinate and number < 0:
        raise ContractError(f"{path} must be a nonnegative coordinate")
    return number


def _csv(content: bytes, name: str) -> tuple[list[str], list[dict]]:
    try:
        reader = csv.reader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True)
        header = next(reader, [])
        if not header or len(header) != len(set(header)):
            raise ContractError(f"{name} must have nonempty, unique CSV headers")
        for field in header:
            _text(field, f"{name} header")
        rows = []
        for line, row in enumerate(reader, 2):
            if not row:
                continue
            if len(row) != len(header):
                raise ContractError(f"{name} row {line} has the wrong number of columns")
            rows.append(dict(zip(header, row)))
    except (UnicodeError, csv.Error):
        raise ContractError(f"{name} must be well-formed UTF-8 CSV") from None
    if not rows:
        raise ContractError(f"{name} must contain at least one tile row")
    return header, rows


def read_tile_tables(root: Path, predictions: dict, sources: list, read_source) -> dict:
    """Return JSON-safe audit data and metadata for unchanged raw-file copies.

    Rows pair by patient and exact numeric coordinates, independent of row
    order. The features table has no slide_id, so overlapping coordinates on
    multiple slides cannot be joined unambiguously and are rejected. Known
    patients without tiles remain explicit in the audit rather than fabricated.
    """
    relative_paths = [PREDICTIONS_FILE, FEATURES_FILE]
    present = [(root / relative).exists() or (root / relative).is_symlink() for relative in relative_paths]
    if not any(present):
        return {"report": {"present": False, "status": "absent", "warnings": [
            "Optional tile tables were not supplied; no tile response probabilities or attention maps are inferred."]},
            "raw_files": []}
    if not all(present):
        raise ContractError("optional tile_predictions.csv and tile_features.csv must both be present or both absent")
    contents = {relative: read_source(root, relative, sources) for relative in relative_paths}
    raw_files = [{"relative_path": relative, "sha256": hashlib.sha256(contents[relative]).hexdigest(),
                  "size_bytes": len(contents[relative])} for relative in relative_paths]
    prediction_header, prediction_rows = _csv(contents[PREDICTIONS_FILE], PREDICTIONS_FILE)
    feature_header, feature_rows = _csv(contents[FEATURES_FILE], FEATURES_FILE)
    if prediction_header != PREDICTION_FIELDS:
        raise ContractError("tile_predictions.csv header must be exactly " + ",".join(PREDICTION_FIELDS))
    if feature_header[:len(FEATURE_PREFIX)] != FEATURE_PREFIX or len(feature_header) != len(FEATURE_PREFIX) + 10:
        raise ContractError("tile_features.csv requires Patient_id,tile_id,tile_x,tile_y,attention followed by exactly 10 feature columns")
    feature_columns = feature_header[len(FEATURE_PREFIX):]

    prediction_tiles, feature_tiles, seen_tile_ids = {}, {}, set()
    for name, rows, target in ((PREDICTIONS_FILE, prediction_rows, prediction_tiles),
                               (FEATURES_FILE, feature_rows, feature_tiles)):
        for line, row in enumerate(rows, 2):
            path = f"{name} row {line}"
            patient_id = _text(row["Patient_id"], path + " Patient_id", 100)
            if patient_id not in predictions:
                raise ContractError(f"{path} has an unknown Patient_id: {patient_id}")
            x = _number(row["tile_x"], path + " tile_x", coordinate=True)
            y = _number(row["tile_y"], path + " tile_y", coordinate=True)
            key = (patient_id, x, y)
            if key in target:
                raise ContractError(f"{path} has duplicate or ambiguous patient/tile coordinates")
            if name == PREDICTIONS_FILE:
                slide = _text(row["slide_id"], path + " slide_id")
                target[key] = {"slide_id": slide, "tile_prob": _number(row["tile_prob"], path + " tile_prob", unit_interval=True)}
            else:
                tile_id = _text(row["tile_id"], path + " tile_id")
                if tile_id in seen_tile_ids:
                    raise ContractError(f"{path} has a duplicate tile_id: {tile_id}")
                seen_tile_ids.add(tile_id)
                for column in feature_columns:
                    _number(row[column], path + " " + column)
                target[key] = {"attention": _number(row["attention"], path + " attention", unit_interval=True)}
    if prediction_tiles.keys() != feature_tiles.keys():
        raise ContractError("tile tables must contain the same patient/coordinate rows; no row-position join or tile imputation is performed")

    patients = {}
    for patient_id in predictions:
        keys = [key for key in prediction_tiles if key[0] == patient_id]
        equal = sum(prediction_tiles[key]["tile_prob"] == feature_tiles[key]["attention"] for key in keys)
        patients[patient_id] = {
            "row_count": len(keys), "prediction_rows": len(keys), "feature_rows": len(keys),
            "slide_ids": sorted({prediction_tiles[key]["slide_id"] for key in keys}),
            "attention_sum": math.fsum(float(feature_tiles[key]["attention"]) for key in keys),
            "tile_prob_sum": math.fsum(float(prediction_tiles[key]["tile_prob"]) for key in keys),
            "identical_value_count": equal,
            "all_tile_prob_equals_attention": bool(keys) and equal == len(keys),
        }
    identical = sum(patient["identical_value_count"] for patient in patients.values())
    all_identical = identical == len(prediction_tiles)
    missing = [patient_id for patient_id, patient in patients.items() if not patient["row_count"]]
    warnings = [
        "The legacy tile_prob column is not certified as a tile-level response probability; raw tile tables are retained as source data only.",
        "Attention and its per-patient sums are descriptive audits; values are not normalized, repaired, or used as response-class attributions.",
        "Paired rows are matched by patient and coordinates; tile_features.csv has no slide_id, so ambiguous overlapping slide coordinates are rejected.",
    ]
    if all_identical:
        warnings.append("Every supplied tile_prob is numerically identical to paired attention. Treat these supplied values as attention weights, not tile response probabilities.")
    else:
        warnings.append("Some supplied tile_prob values differ from paired attention. Their prediction semantics are unknown and require producer confirmation; inequality does not establish response probabilities.")
    if missing:
        warnings.append("No tile rows were supplied for these known patients: " + ", ".join(missing) + ".")
    report = {"present": True, "status": "audited", "prediction_rows": len(prediction_rows),
              "feature_rows": len(feature_rows), "paired_rows": len(prediction_tiles),
              "feature_columns": feature_columns, "feature_count": len(feature_columns),
              "identical_value_count": identical, "all_tile_prob_equals_attention": all_identical,
              "tile_prob_semantics": "attention_weight" if all_identical else "unknown",
              "response_probabilities_verified": False, "missing_patient_ids": missing,
              "patients": patients, "warnings": warnings}
    return {"report": report, "raw_files": raw_files}
