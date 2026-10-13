"""Local-only ingestion and patient-key joins for the upstream model teams."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .copilot import _strict_json
from .schema import MODALITIES, ContractError, PatientPrediction


def parse_jsonl(content: str) -> list[PatientPrediction]:
    patients = []
    seen = set()
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        try:
            if len(line) > 2_000_000:
                raise ContractError("record exceeds maximum size")
            patient = PatientPrediction.from_dict(_strict_json(line))
            if patient.patient_id in seen:
                raise ContractError("duplicate patient ID")
            seen.add(patient.patient_id)
            patients.append(patient)
        except (ValueError, TypeError) as exc:
            raise ContractError(f"input line {line_number}: {exc}") from None
    if not patients:
        raise ContractError("input contains no patient records")
    return patients


def load_jsonl(path: str | Path) -> list[PatientPrediction]:
    return parse_jsonl(Path(path).read_text(encoding="utf-8-sig"))


def write_jsonl(path: str | Path, records) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            value = record.to_dict() if isinstance(record, PatientPrediction) else record
            handle.write(json.dumps(value, ensure_ascii=True, allow_nan=False) + "\n")


def assemble_predictions(*, clinical_csv=None, mif_csv=None, fused_csv=None, context_jsonl=None) -> list[PatientPrediction]:
    """Join by canonical patient_id, preserving the union, never by row order.

    A slide-to-patient mapping and slide aggregation must be applied upstream.
    This adapter intentionally refuses to guess how multiple slides are combined.
    """
    rows = {}
    for modality, source in zip(MODALITIES, (clinical_csv, mif_csv, fused_csv)):
        if source is None:
            continue
        seen = set()
        with Path(source).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            allowed = {"patient_id", "probability", "model_id", "calibration", "decision_threshold"}
            if len(set(headers)) != len(headers) or not {"patient_id", "probability"} <= set(headers) or set(headers) - allowed:
                raise ContractError(f"{modality} CSV requires unique patient_id,probability headers and only documented optional columns")
            for line_number, row in enumerate(reader, 2):
                try:
                    if None in row or any(value is None for value in row.values()):
                        raise ContractError("CSV row has an incorrect number of columns")
                    patient_id = row["patient_id"].strip()
                    if patient_id in seen:
                        raise ContractError("duplicate patient ID")
                    seen.add(patient_id)
                    probability = float(row["probability"])
                    threshold = row.get("decision_threshold", "").strip()
                    prediction = {"probability": probability, "model_id": row.get("model_id", "").strip() or "unspecified",
                                  "calibration": row.get("calibration", "").strip() or "unknown",
                                  "decision_threshold": float(threshold) if threshold else None}
                    PatientPrediction.from_dict({"patient_id": patient_id, "predictions": {modality: prediction}})
                    rows.setdefault(patient_id, {"patient_id": patient_id, "predictions": {}})["predictions"][modality] = prediction
                except (ValueError, TypeError) as exc:
                    raise ContractError(f"{modality} CSV line {line_number}: {exc}") from None
    if not rows:
        raise ContractError("at least one nonempty prediction CSV is required")
    if context_jsonl is not None:
        seen = set()
        with Path(context_jsonl).open(encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    obj = _strict_json(line)
                    if not isinstance(obj, dict) or "patient_id" not in obj:
                        raise ContractError("context record requires patient_id")
                    if set(obj) - {"patient_id", "schema_version", "top_features", "clinical_context", "response_definition", "ground_truth", "evaluation_partition"}:
                        raise ContractError("context has unsupported fields; predictions must come from the modality CSVs")
                    patient_id = obj["patient_id"]
                    if not isinstance(patient_id, str) or patient_id != patient_id.strip():
                        raise ContractError("context patient_id must be a canonical string without surrounding whitespace")
                    if patient_id in seen:
                        raise ContractError("duplicate context patient ID")
                    if patient_id not in rows:
                        raise ContractError("context patient ID has no matching prediction")
                    seen.add(patient_id)
                    rows[patient_id].update(obj)
                    PatientPrediction.from_dict(rows[patient_id])
                except (ValueError, TypeError) as exc:
                    raise ContractError(f"context line {line_number}: {exc}") from None
    return [PatientPrediction.from_dict(row) for row in rows.values()]
