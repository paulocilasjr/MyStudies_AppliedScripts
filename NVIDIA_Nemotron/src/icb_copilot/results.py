"""Shared validation of completed copilot run snapshots; no model is executed."""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import re

from .copilot import _strict_json, summarize_evidence, score_sentence, REVIEW_SENTENCE
from .schema import ContractError, PatientPrediction

EVIDENCE_FIELDS = ("schema_version", "patient_id", "predictions", "top_features", "clinical_context", "response_definition")
RESULT_FIELDS = set(EVIDENCE_FIELDS) | {"narrative", "narrative_source", "review_required", "limitations", "comparison", "quality", "provenance"}
RUN_ARTIFACTS = ("narratives.jsonl", "narratives.csv", "report.md", "manifest.json", "metrics.json")
SOURCE_QUALITY = {"mock": "mock", "vllm": "passed", "fallback": "fallback"}


def _text(value, name, *, limit=20_000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ContractError(f"{name} must be nonempty text within its size limit")
    return value


def _strings(value, name, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ContractError(f"{name} must be a {'nonempty ' if nonempty else ''}list of text")
    for item in value:
        _text(item, name)
    return value


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise ContractError(f"{name} must be a finite number") from None
    if not math.isfinite(number):
        raise ContractError(f"{name} must be a finite number")
    return number


def _validate_result(value, backend, gap_threshold):
    if not isinstance(value, dict) or set(value) != RESULT_FIELDS:
        raise ContractError("each result must have the implemented schema 1.0 result fields")
    evidence = {key: value[key] for key in EVIDENCE_FIELDS}
    patient = PatientPrediction.from_dict(evidence).to_dict()
    if any(patient[key] != evidence[key] for key in EVIDENCE_FIELDS):
        raise ContractError("result evidence must already be normalized canonical data")
    if value["review_required"] is not True:
        raise ContractError("result review_required must be true")
    _text(value["narrative"], "result narrative")
    prefix, suffix = score_sentence(patient) + " ", " " + REVIEW_SENTENCE
    if not value["narrative"].startswith(prefix) or not value["narrative"].endswith(suffix):
        raise ContractError("result narrative factual prefix or review sentence conflicts with canonical evidence")
    _strings(value["limitations"], "result limitations", nonempty=True)
    source = value["narrative_source"]
    if not isinstance(source, str) or source not in SOURCE_QUALITY:
        raise ContractError("result narrative_source must be mock, vllm, or fallback")
    if (backend == "mock") != (source == "mock"):
        raise ContractError("result narrative source conflicts with the run backend")
    quality = value["quality"]
    if not isinstance(quality, dict) or set(quality) != {"status", "issues", "screen"}:
        raise ContractError("result quality must contain status, issues, and screen")
    if quality["status"] != SOURCE_QUALITY[source]:
        raise ContractError("result quality status conflicts with narrative_source")
    issues = _strings(quality["issues"], "result quality issues")
    _text(quality["screen"], "result quality screen")
    if bool(issues) != (source == "fallback"):
        raise ContractError("screen issues must be present for fallback and absent for passed/mock results")
    provenance = value["provenance"]
    if not isinstance(provenance, dict) or provenance.get("backend") != backend:
        raise ContractError("result provenance must identify the run backend")
    _text(provenance.get("prompt_version"), "result prompt_version")
    comparison = value["comparison"]
    expected, _ = summarize_evidence(patient, disagreement_threshold=gap_threshold)
    if not isinstance(comparison, dict) or set(comparison) != set(expected):
        raise ContractError("result comparison has an invalid structure")
    for flag in ("score_disagreement", "threshold_disagreement"):
        if type(comparison[flag]) is not bool or comparison[flag] != expected[flag]:
            raise ContractError(f"result {flag} conflicts with supplied scores and thresholds")
    if comparison["missing_modalities"] != expected["missing_modalities"]:
        raise ContractError("result missing_modalities conflicts with supplied predictions")
    classes = comparison["predicted_classes"]
    if not isinstance(classes, dict) or set(classes) != set(expected["predicted_classes"]):
        raise ContractError("result predicted_classes has an invalid structure")
    for modality, expected_class in expected["predicted_classes"].items():
        actual = classes[modality]
        if actual is not None and (type(actual) is not int or actual not in (0, 1)):
            raise ContractError("result predicted_classes must contain integer classes or null")
        if actual != expected_class:
            raise ContractError("result predicted_classes conflicts with supplied thresholds")
    for field in ("clinical_mif_gap", "disagreement_threshold"):
        actual, reference = comparison[field], expected[field]
        if reference is None:
            if actual is not None:
                raise ContractError(f"result {field} conflicts with supplied predictions")
        elif not math.isclose(_finite(actual, field), reference, rel_tol=0, abs_tol=1e-12):
            raise ContractError(f"result {field} conflicts with supplied predictions")
    return patient


def read_run(run):
    """Read one completed local run and validate critical result invariants.

    Return manifest, manifest bytes, result bytes, results, and canonical evidence.
    These checks validate structural consistency, not clinical correctness.
    """
    run = Path(run).expanduser().resolve()
    missing = [name for name in RUN_ARTIFACTS if not (run / name).is_file()]
    if missing:
        raise ContractError("completed run is missing artifacts: " + ", ".join(missing))
    manifest_bytes = (run / "manifest.json").read_bytes()
    result_bytes = (run / "narratives.jsonl").read_bytes()
    manifest = _strict_json(manifest_bytes.decode("utf-8-sig"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0" or manifest.get("review_required") is not True:
        raise ContractError("run manifest must identify schema 1.0 and require review")
    fingerprint = manifest.get("input_sha256")
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ContractError("run manifest requires a valid input_sha256")
    backend_info = manifest.get("backend")
    if not isinstance(backend_info, dict) or not isinstance(backend_info.get("backend"), str) or backend_info["backend"] not in {"mock", "vllm"}:
        raise ContractError("run manifest backend must be mock or vllm")
    gap_threshold = _finite(manifest.get("disagreement_threshold"), "run disagreement_threshold")
    if not 0 < gap_threshold <= 1:
        raise ContractError("run disagreement_threshold must be in (0, 1]")
    results, evidence, seen = [], {}, set()
    for number, line in enumerate(result_bytes.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            if len(line) > 2_000_000:
                raise ContractError("result exceeds maximum size")
            result = _strict_json(line)
            patient = _validate_result(result, backend_info["backend"], gap_threshold)
            patient_id = patient["patient_id"]
            if patient_id in seen:
                raise ContractError("duplicate result patient ID")
            seen.add(patient_id)
            results.append(result)
            evidence[patient_id] = patient
        except (ValueError, TypeError) as error:
            raise ContractError(f"result line {number}: {error}") from None
    if not results or type(manifest.get("patient_count")) is not int or manifest["patient_count"] != len(results):
        raise ContractError("run patient_count does not match nonempty result records")
    for key, field in (("source_counts", "narrative_source"), ("quality_counts", None)):
        supplied = manifest.get(key)
        expected = dict(Counter(row[field] if field else row["quality"]["status"] for row in results))
        if not isinstance(supplied, dict) or any(type(count) is not int or count <= 0 for count in supplied.values()) or supplied != expected:
            raise ContractError(f"run {key} does not match results")
    if manifest.get("response_definitions") != sorted({row["response_definition"] for row in evidence.values()}):
        raise ContractError("run response_definitions does not match results")
    return manifest, manifest_bytes, result_bytes, results, evidence
