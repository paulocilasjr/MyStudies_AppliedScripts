"""Local file adapter for the audited melanoma-demo-ui; never runs a model.

The viewer requires complete three-score rows and imposes a 0.5 display
threshold. Export fails rather than silently changing an upstream threshold.
Only an explicitly supplied, fingerprint-matching canonical input can provide
labels; otherwise the viewer's actual_response column remains blank.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .io import parse_jsonl
from .results import EVIDENCE_FIELDS, read_run
from .schema import ContractError, MODALITIES

UI_REPOSITORY = "https://github.com/qchiujunhao/melanoma-demo-ui"
UI_COMMIT = "59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f"


def _ui_text(result):
    source = result["narrative_source"]
    source_label = {"mock": "mock (no language model executed)",
                    "nim": "nim (NVIDIA-hosted NIM; remote inference)",
                    "transformers": "transformers (local Nemotron via Hugging Face Transformers)"}.get(source, source)
    if result["provenance"].get("generator") == "injected":
        source_label += " (injected test generator)"
    scores = ", ".join(f"{m}={result['predictions'][m]['probability']!r}" for m in MODALITIES)
    calibration = ", ".join(f"{m}={result['predictions'][m]['calibration']}" for m in MODALITIES)
    lines = ["RESEARCH OUTPUT — independent human review required.",
             f"Narrative source: {source_label}; quality: {result['quality']['status']}.",
             "Producer-declared calibration: " + calibration + ".",
             "Full-precision supplied scores: " + scores + ".",
             "Viewer display threshold 0.5 matches the supplied thresholds for all three models.",
             "", result["narrative"], "", "Limitations:", *["- " + text for text in result["limitations"]]]
    if result["provenance"].get("backend") == "nim":
        model = result["provenance"].get("model", {})
        if model.get("model_id"):
            lines.insert(2, f"NIM model: {model['model_id']}; revision: {model.get('revision', 'not recorded')}.")
    if result["quality"]["issues"]:
        lines.extend(["", "Screen issues: " + ", ".join(result["quality"]["issues"])])
    return "\n".join(lines)


def export_ui_bundle(run_dir: str | Path, output_dir: str | Path, *, canonical_input: str | Path | None = None,
                     include_synthetic_labels: bool = False) -> dict:
    """Export a complete-score subset for the audited file-only Streamlit UI.

    Critical record/provenance consistency is checked, not medical truth or a
    standalone universal result schema. Optional labels require the exact input
    snapshot used by the run, declared held-out status, and one endpoint/partition.
    """
    run = Path(run_dir).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("UI output directory must be absent or empty; use a new bundle directory")
    manifest, manifest_bytes, result_bytes, results, evidence = read_run(run)
    canonical = {}
    if canonical_input is not None:
        raw = Path(canonical_input).expanduser().read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest["input_sha256"]:
            raise ContractError("canonical input does not match the run input_sha256; labels were not exported")
        canonical = {p.patient_id: p.to_dict() for p in parse_jsonl(raw.decode("utf-8-sig"))}
        if set(canonical) != set(evidence) or any(
            any(canonical[pid][field] != evidence[pid][field] for field in EVIDENCE_FIELDS) for pid in evidence
        ):
            raise ContractError("canonical input evidence does not match run results")
    if include_synthetic_labels and (not canonical or any(row["evaluation_partition"] != "synthetic" for row in canonical.values())):
        raise ContractError("synthetic label export requires matching canonical input with every patient declared synthetic")
    included, excluded = [], []
    for result in results:
        missing = [m for m in MODALITIES if m not in result["predictions"]]
        if missing:
            excluded.append({"patient_id": result["patient_id"], "reason": "UI requires all three scores", "missing_modalities": missing})
            continue
        incompatible = [m for m in MODALITIES if result["predictions"][m]["decision_threshold"] != 0.5]
        if incompatible:
            raise ContractError(f"patient {result['patient_id']}: UI imposes threshold 0.5 but supplied thresholds are missing/different for {', '.join(incompatible)}; update the UI or use genuinely matching upstream thresholds")
        included.append(result)
    if not included:
        raise ContractError("no patients have all three scores required by the current UI")
    labels, withheld, groups = {}, [], set()
    for result in included:
        pid = result["patient_id"]
        row = canonical.get(pid)
        if row is None:
            reason = "canonical input not supplied; label unavailable in interpretation result"
        elif row["ground_truth"] is None:
            reason = "ground truth unknown"
        elif include_synthetic_labels:
            labels[pid] = row["ground_truth"]
            groups.add(("synthetic", row["response_definition"]))
            continue
        elif row["evaluation_partition"] not in {"test", "out_of_fold"}:
            reason = "not declared test or out_of_fold"
        elif row["response_definition"].lower() in {"not specified", "unspecified", "unknown"}:
            reason = "response endpoint unspecified"
        else:
            labels[pid] = row["ground_truth"]
            groups.add((row["evaluation_partition"], row["response_definition"]))
            continue
        withheld.append({"patient_id": pid, "reason": reason})
    if len(groups) > 1:
        raise ContractError("UI pools labeled patients; export requires one declared evaluation partition and response endpoint")
    summary = {"schema_version": "1.0", "ui_repository": UI_REPOSITORY, "ui_commit": UI_COMMIT,
               "exported_at_utc": datetime.now(timezone.utc).isoformat(), "source_run_dir": str(run),
               "source_input_sha256": manifest["input_sha256"],
               "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
               "source_results_sha256": hashlib.sha256(result_bytes).hexdigest(),
               "patient_count": len(included), "included_patient_ids": [r["patient_id"] for r in included],
               "excluded_patients": excluded, "actual_response_count": len(labels), "withheld_labels": withheld,
               "label_policy": ("synthetic demonstration labels only; never clinical evaluation" if include_synthetic_labels else
                                "matching canonical input; declared test/out_of_fold and specified endpoint; otherwise blank"),
               "synthetic_labels": include_synthetic_labels,
               "evaluation_group": list(next(iter(groups))) if groups else None, "display_threshold": 0.5,
               "source_counts": dict(Counter(r["narrative_source"] for r in included)), "review_required": True,
               "warnings": ["The current UI displays only the complete three-score subset; exclusions are explicit and scores are never imputed.",
                            "Calibration and held-out/endpoint metadata are producer declarations, not independently validated here.",
                            "The UI labels scores P(response) and uses a fixed display threshold; it does not read the structured copilot metadata.",
                            "Global feature importance and tile predictions are not generated from patient-level features or scores.",
                            "Mock/fallback/injected source and review limitations remain in displayed text; the UI's generic Nemotron caption does not verify inference."]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ui-export-", dir=output.parent) as temporary:
        staging = Path(temporary)
        with (staging / "patient_predictions.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Patient_id", "prob_mif", "prob_clinical", "prob_fused", "actual_response"])
            writer.writeheader()
            for result in included:
                writer.writerow({"Patient_id": result["patient_id"],
                                 **{"prob_" + m: result["predictions"][m]["probability"] for m in MODALITIES},
                                 "actual_response": labels.get(result["patient_id"], "")})
        banner = "SYNTHETIC DEMONSTRATION: patient inputs and response labels are simulated; supplied scores do not measure clinical performance.\n\n" if include_synthetic_labels else ""
        (staging / "narratives.json").write_text(json.dumps({r["patient_id"]: banner + _ui_text(r) for r in included}, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")
        (staging / "copilot_results.jsonl").write_bytes(result_bytes)
        (staging / "copilot_manifest.json").write_bytes(manifest_bytes)
        (staging / "ui_export_manifest.json").write_text(json.dumps(summary, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")
        for path in staging.iterdir():
            path.chmod(0o600)
        if output.exists():
            output.rmdir()
        os.rename(staging, output)
        output.chmod(0o700)
    return summary
