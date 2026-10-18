"""Acceptance checks for completed runs; never load a model or infer new scores."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .copilot import summarize_evidence
from .io import parse_jsonl
from .results import read_run
from .prompts import REPLY_FIELDS


def verify_run(input_path: str | Path, output_dir: str | Path, *,
               require_vllm: bool = False, require_synthetic: bool = False,
               expected_model_id: str | None = None, expected_model_revision: str | None = None,
               require_backend: str | None = None) -> dict:
    """Write verification.json and return a pass/fail report.

    Real-model acceptance is deliberately strict: every narrative must pass the
    screen. Rejected prose still leaves the experiment artifacts for diagnosis.
    Recorded execution metadata is evidence from this program, not attestation
    against deliberately edited artifacts or proof of clinical correctness.
    """
    if require_vllm:
        if require_backend not in (None, "vllm"):
            raise ValueError("require_vllm conflicts with the requested backend")
        require_backend = "vllm"
    if require_backend not in (None, "vllm", "transformers", "nim"):
        raise ValueError("required backend must be vllm, transformers, or nim")
    output = Path(output_dir).expanduser().resolve()
    if not output.is_dir():
        raise ValueError("completed run directory does not exist")
    checks = {}
    report = {"schema_version": "1.0", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "ok": False, "require_vllm": require_backend == "vllm", "require_backend": require_backend,
              "require_synthetic": require_synthetic,
              "expected_model_id": expected_model_id, "expected_model_revision": expected_model_revision,
              "checks": checks, "errors": [],
              "scope": "Interface and generation acceptance only; clinical correctness and predictive performance are not verified."}
    try:
        snapshot = Path(input_path).expanduser().read_bytes()
        patients = [p.to_dict() for p in parse_jsonl(snapshot.decode("utf-8-sig"))]
        manifest, _, _, results, _ = read_run(output)
        checks["completed_run_contract_valid"] = True
        checks["input_hash_matches"] = manifest.get("input_sha256") == hashlib.sha256(snapshot).hexdigest()
        checks["patient_count_matches"] = len(results) == len(patients) == manifest.get("patient_count")
        checks["patient_ids_and_order_match"] = [r.get("patient_id") for r in results] == [p["patient_id"] for p in patients]
        checks["schema_versions_match"] = manifest.get("schema_version") == "1.0" and all(r.get("schema_version") == "1.0" for r in results)
        evidence_keys = ("predictions", "top_features", "clinical_context", "response_definition")
        checks["supplied_evidence_preserved"] = len(results) == len(patients) and all(
            all(r.get(key) == p[key] for key in evidence_keys) for r, p in zip(results, patients))
        gap = manifest.get("disagreement_threshold")
        if isinstance(gap, bool) or not isinstance(gap, (int, float)) or not 0 < gap <= 1:
            raise ValueError("manifest disagreement threshold is invalid")
        checks["comparison_matches_evidence"] = len(results) == len(patients) and all(
            r.get("comparison") == summarize_evidence(p, disagreement_threshold=gap)[0]
            for r, p in zip(results, patients))
        checks["review_and_limitations_present"] = manifest.get("review_required") is True and all(
            r.get("review_required") is True and isinstance(r.get("limitations"), list) and r["limitations"]
            and all(isinstance(s, str) and s.strip() for s in r["limitations"]) for r in results)
        checks["narratives_present"] = bool(results) and all(isinstance(r.get("narrative"), str) and r["narrative"].strip() for r in results)
        quality_status = {"mock": "mock", "vllm": "passed", "transformers": "passed", "nim": "passed", "fallback": "fallback"}
        checks["source_quality_consistent"] = all(
            r.get("narrative_source") in quality_status and isinstance(r.get("quality"), dict)
            and r["quality"].get("status") == quality_status[r["narrative_source"]]
            and isinstance(r["quality"].get("issues"), list)
            and (r["narrative_source"] == "fallback" or not r["quality"]["issues"])
            for r in results)
        counts = dict(Counter(r.get("narrative_source") for r in results))
        checks["source_counts_match"] = counts == manifest.get("source_counts")
        checks["quality_counts_match"] = dict(Counter(r.get("quality", {}).get("status") for r in results)) == manifest.get("quality_counts")
        report["patient_count"] = len(results)
        report["source_counts"] = counts
        if expected_model_id is not None or expected_model_revision is not None:
            model = manifest["backend"].get("model", {})
            checks["expected_model_matches"] = isinstance(model, dict) and (
                expected_model_id is None or model.get("model_id") == expected_model_id) and (
                expected_model_revision is None or model.get("revision") == expected_model_revision)
        if require_synthetic:
            checks["inputs_declared_synthetic"] = all(p["evaluation_partition"] == "synthetic" for p in patients)
        if require_backend:
            backend = manifest.get("backend", {})
            execution = backend.get("execution", {})
            calls, records = execution.get("generation_calls"), execution.get("generated_records")
            recorded = (
                backend.get("backend") == require_backend and "generator" not in backend
                and type(calls) is int and calls > 0
                and type(records) is int and records >= len(patients))
            if require_backend == "nim":
                requests, successes = execution.get("remote_requests"), execution.get("remote_successes")
                checks["remote_nim_executed"] = (
                    recorded and records >= len(patients) * len(REPLY_FIELDS)
                    and type(successes) is int and successes >= records
                    and type(requests) is int and requests >= successes)
            else:
                checks[f"local_{require_backend}_executed"] = recorded and execution.get("model_loaded") is True
            checks["all_generated_narratives_accepted"] = counts == {require_backend: len(patients)}
            checks[f"result_backend_is_{require_backend}"] = all(
                isinstance(r.get("provenance"), dict) and r["provenance"].get("backend") == require_backend
                and "generator" not in r["provenance"] for r in results)
        report["errors"] = [name for name, passed in checks.items() if not passed]
        report["ok"] = bool(checks) and not report["errors"]
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        report["errors"].append(f"invalid_run_artifact: {exc}")
    # Atomic replacement allows rerunning verification without a partial report.
    with tempfile.NamedTemporaryFile(mode="w", dir=output, prefix=".verification-", encoding="utf-8", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(report, handle, ensure_ascii=True, allow_nan=False, indent=2)
            handle.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, output / "verification.json")
    finally:
        temporary.unlink(missing_ok=True)
    return report
