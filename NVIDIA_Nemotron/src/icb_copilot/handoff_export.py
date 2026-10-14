"""Publish the five-patient demonstration without modifying its source packet."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile

from .handoff import canonical_jsonl_bytes, read_handoff
from .results import read_run
from .schema import ContractError
from .ui_export import export_ui_bundle


def _json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def export_handoff_bundle(handoff_dir: str | Path, run_dir: str | Path, output_dir: str | Path) -> dict:
    """Combine verified narratives with original synthetic labels and figures.

    Invalid clinical SHAP explanations remain visible as explicitly flagged
    source assets for testing. They are never repaired or relabeled by this
    exporter. Model inputs omit those inconsistent signed contributions.
    """
    source = Path(handoff_dir).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("handoff UI output must be absent or empty; use a new directory")
    packet = read_handoff(source)
    canonical_bytes = canonical_jsonl_bytes(packet["patients"])
    manifest, _, _, _, _ = read_run(Path(run_dir).expanduser().resolve())
    if manifest["input_sha256"] != hashlib.sha256(canonical_bytes).hexdigest():
        raise ContractError("run input does not match this handoff packet; generate from prepare-handoff patients.jsonl first")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".handoff-export-", dir=output.parent) as temporary:
        staging = Path(temporary)
        canonical = staging / "patients.jsonl"
        canonical.write_bytes(canonical_bytes)
        canonical.chmod(0o600)
        bundle = staging / "bundle"
        summary = export_ui_bundle(run_dir, bundle, canonical_input=canonical, include_synthetic_labels=True)
        _json(bundle / "patient_feature_analysis.json", packet["original_analysis"])
        _json(bundle / "feature_importances.json", packet["global_importance"])
        assets = packet["assets"]
        seen = set()
        for asset in assets:
            relative = asset["relative_path"]
            path = PurePosixPath(relative)
            if (path.is_absolute() or ".." in path.parts or "\\" in relative or not path.parts
                    or path.parts[0] != "figures" or path.suffix not in {".png", ".pdf"} or relative in seen):
                raise ContractError("invalid or duplicate handoff figure path")
            seen.add(relative)
            original = source / relative
            if original.is_symlink() or not original.resolve().is_relative_to(source):
                raise ContractError("handoff figure must stay inside the source packet without a symlink")
            contents = original.read_bytes()
            if len(contents) != asset["size_bytes"] or hashlib.sha256(contents).hexdigest() != asset["sha256"]:
                raise ContractError("handoff figure changed during export; retry from an unchanged packet")
            destination = bundle / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contents)
        _json(bundle / "patient_assets.json", {"schema_version": "1.0", "synthetic": True, "assets": assets})
        _json(bundle / "handoff_manifest.json", packet["report"])
        source_data = []
        for entry in packet.get("tile_files", []):
            relative = entry["relative_path"]
            if relative not in {"predictions/tile_predictions.csv", "predictions/tile_features.csv"}:
                raise ContractError("unsupported handoff tile source path")
            original = source / relative
            if original.is_symlink() or not original.resolve().is_relative_to(source):
                raise ContractError("tile source must remain inside the handoff packet")
            contents = original.read_bytes()
            if len(contents) != entry["size_bytes"] or hashlib.sha256(contents).hexdigest() != entry["sha256"]:
                raise ContractError("tile source changed during export; retry with an unchanged packet")
            destination = bundle / "source_data" / Path(relative).name
            destination.parent.mkdir(exist_ok=True)
            destination.write_bytes(contents)
            source_data.append({**entry, "exported_path": destination.relative_to(bundle).as_posix()})
        if source_data:
            _json(bundle / "source_data" / "manifest.json", {
                "schema_version": "1.0", "files": source_data, "tile_audit": packet["report"]["tile_audit"],
                "usage": "Source inspection only. These files are not admitted as tile response probabilities."})
        texts = json.loads((bundle / "narratives.json").read_text(encoding="utf-8"))
        for patient_id, text in texts.items():
            warnings = packet["report"]["patients"][patient_id]["warnings"][:]
            warnings.extend(warning for asset in assets if asset["patient_id"] == patient_id
                            for warning in asset.get("warnings", []))
            warnings = list(dict.fromkeys(warnings))
            if warnings:
                text += "\n\nSupplied figure/evidence checks:\n" + "\n".join("- " + warning for warning in warnings)
            texts[patient_id] = text
        _json(bundle / "narratives.json", texts)
        summary.update({"bundle_kind": "synthetic_paulo_handoff", "handoff_input_sha256": packet["input_sha256"],
                        "figure_count": len(assets), "patient_assets": "patient_assets.json",
                        "handoff_manifest": "handoff_manifest.json", "shap_policy": "original plots preserved with audit notes; structured SHAP admitted only when output and rounded additivity checks pass",
                        "placeholder_narratives_used": False, "source_data": source_data,
                        "tile_response_probabilities_exported": False})
        summary["warnings"].extend([
            "Observed labels are synthetic scenario labels, not clinical outcomes or held-out evaluation data.",
            "The supplied clinical SHAP figures are retained for display testing; consult patient-specific mismatch notes.",
            "mIF attention contrast describes high- versus low-attention tiles and is not a signed response attribution.",
            "Any supplied tile tables are retained under source_data/ for inspection, not exposed to a tile response-probability heatmap.",
            "Patient figure display requires the local companion demo or an extension to the upstream Streamlit viewer."])
        _json(bundle / "ui_export_manifest.json", summary)
        for path in bundle.rglob("*"):
            path.chmod(0o700 if path.is_dir() else 0o600)
        if output.exists():
            output.rmdir()
        os.rename(bundle, output)
    return summary
