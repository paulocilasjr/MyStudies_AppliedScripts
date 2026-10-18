"""Import the explicitly synthetic Paulo handoff without repairing its evidence.

Scores and original assets are preserved. Structured clinical SHAP is admitted
only after declared output/additivity checks, with an explicit provenance caveat.
mIF attention contrasts remain descriptive measurements. No model is loaded here.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import tempfile

from .copilot import _strict_json
from .handoff_tiles import read_tile_tables
from .schema import ContractError, MODALITIES, PatientPrediction

CSV_FIELDS = ["Patient_id", "prob_mif", "prob_clinical", "prob_fused", "actual_response"]
MAX_FILE_BYTES = 32 * 1024 * 1024
DEMO_THRESHOLD = 0.5
FOUR_DECIMAL_ROUNDING = 0.00005

# These observations apply only to the exact manually inspected source PNGs.
# They are not an OCR validator and must disappear if a figure is replaced.
KNOWN_PNG_AUDIT = {
    # Handoff v3: partial visible-label observations, October 14, 2026.
    "64c48eaeccae9753e46dca2c3dfc79fb5e97d55e8bd2eecfbb172f1668ac2f2e": {
        "output_value": 0.97, "base_value": 0.50,
        "feature_values": {"has_lung_mets": 1, "gender_male": 0, "met_stage": 1, "had_targeted_therapy": 0, "tissue_resection": 1},
        "shap_values": {"has_lung_mets": 0.21, "gender_male": 0.09}},
    "7a63756e9394544c1b6b6229b5b86d27ce6c2646c2273d530f06910d9c866173": {
        "output_value": 0.07, "base_value": 0.50,
        "feature_values": {"met_stage": 3, "tissue_resection": 0},
        "shap_values": {"had_targeted_therapy": -0.25}},
    "e60e4b678aedb2058779a8c9b272857f6c35e9be5dd31a9ad3bcf8eab08bb674": {
        "output_value": 0.11, "base_value": 0.50,
        "feature_values": {"gender_male": 0, "met_stage": 3},
        "shap_values": {"had_targeted_therapy": -0.43, "gender_male": 0.12}},
    "41a710e8e48ace646829a3dbee21f3f4dcf4dc0a76dd33f219e9b9fc04f7f885": {
        "output_value": 0.96, "base_value": 0.50,
        "feature_values": {"has_lung_mets": 1, "met_stage": 2, "tissue_resection": 1, "had_targeted_therapy": 0, "gender_male": 1},
        "shap_values": {"has_lung_mets": 0.20, "met_stage": 0.17}},
    "358b513fab4b1aa2859212274f4fcbc123a6e0f3d74ee60e51fd1397f2670c0e": {
        "output_value": 0.58, "base_value": 0.50,
        "feature_values": {"gender_male": 0, "has_lung_mets": 0, "had_targeted_therapy": 0, "tissue_resection": 1, "met_stage": 3},
        "shap_values": {"gender_male": 0.17, "has_lung_mets": -0.15, "had_targeted_therapy": 0.12, "tissue_resection": -0.06}},
    "13b38cf9f45cd66c2844889c394b646f595ca68f2f7d3091824361b6783bd2c2": {
        "output_value": 0.91, "base_value": 0.50,
        "feature_values": {"has_lung_mets": 1, "had_targeted_therapy": 0, "gender_male": 0, "tissue_resection": 1, "met_stage": 2},
        "shap_values": {"has_lung_mets": 0.18, "had_targeted_therapy": 0.11, "gender_male": 0.09}},
    "de1a6156c8d4ec5ebce69c8fd21ba5a1d06ebcb0d1d033d3ce77d81fc130fa66": {
        "output_value": 0.07, "base_value": 0.50,
        "feature_values": {"had_targeted_therapy": 1, "met_stage": 3, "gender_male": 1, "has_lung_mets": 0, "tissue_resection": 0},
        "shap_values": {"had_targeted_therapy": -0.23, "met_stage": -0.08}},
    "1e752b6595b4e85a08d6d48e955ee2baaf7930cc465b04579c51add77a241012": {
        "output_value": 0.39, "base_value": 0.50,
        "feature_values": {"gender_male": 1, "had_targeted_therapy": 0, "met_stage": 3, "has_lung_mets": 0, "tissue_resection": 0},
        "shap_values": {"gender_male": -0.12, "had_targeted_therapy": 0.08, "met_stage": -0.07}},
    "ce44874fcce6a3b884eca72c5f7239308513b79636b77993797f4b8a8990511e": {
        "output_value": 0.96, "base_value": 0.50,
        "feature_values": {"has_lung_mets": 1, "met_stage": 2, "tissue_resection": 1, "had_targeted_therapy": 0, "gender_male": 1},
        "shap_values": {"has_lung_mets": 0.21, "met_stage": 0.16}},
    "9c87930914b9633108bdd574d78995dfbef2dc8c6e3b5f59b6778e24d02c878f": {
        "output_value": 0.56, "base_value": 0.50,
        "feature_values": {"gender_male": 0, "has_lung_mets": 0, "had_targeted_therapy": 0, "tissue_resection": 1, "met_stage": 3},
        "shap_values": {"gender_male": 0.15, "has_lung_mets": -0.13, "had_targeted_therapy": 0.10, "tissue_resection": -0.05}},
}


def _clinical_figure_audit(digest: str, clinical: dict, csv_probability: float) -> dict:
    """Compare partial manual PNG observations with the current source values."""
    observed = KNOWN_PNG_AUDIT.get(digest)
    result = {"manual_png_audit": observed is not None, "png_sha256": digest,
              "display_rounding_tolerance": 0.005, "mismatch_detected": None,
              "observed": observed, "mismatches": []}
    if observed is None:
        return result
    mismatches = result["mismatches"]
    for description, expected in (("clinical JSON output", clinical["output_value"]), ("CSV clinical score", csv_probability)):
        if abs(observed["output_value"] - expected) > 0.005 + 1e-12:
            mismatches.append(f"displayed output {observed['output_value']:g} differs from {description} {expected:g}")
    if abs(observed["base_value"] - clinical["base_value"]) > 0.005 + 1e-12:
        mismatches.append(f"displayed base {observed['base_value']:g} differs from JSON base {clinical['base_value']:g}")
    features = {feature["raw_feature"]: feature for feature in clinical["features"]}
    for raw, value in observed["feature_values"].items():
        if raw not in features or features[raw]["value"] != value:
            expected = features[raw]["value"] if raw in features else "not supplied"
            mismatches.append(f"displayed {raw}={value:g} differs from current JSON value {expected}")
    for raw, value in observed["shap_values"].items():
        if raw not in features or abs(features[raw]["shap"] - value) > 0.005 + 1e-12:
            expected = features[raw]["shap"] if raw in features else "not supplied"
            mismatches.append(f"displayed {raw} SHAP {value:g} differs from current JSON SHAP {expected}")
    result["mismatch_detected"] = bool(mismatches)
    return result


def _product_score(mif: float, clinical: float):
    numerator = mif * clinical
    denominator = numerator + (1 - mif) * (1 - clinical)
    return numerator / denominator if denominator else None


def _fusion_audit(mif: float, clinical: float, fused: float) -> dict:
    recomputed = _product_score(mif, clinical)
    exact = recomputed is not None and math.isclose(round(recomputed, 4), fused, rel_tol=0, abs_tol=1e-9)
    lower = _product_score(max(0, mif - FOUR_DECIMAL_ROUNDING), max(0, clinical - FOUR_DECIMAL_ROUNDING))
    upper = _product_score(min(1, mif + FOUR_DECIMAL_ROUNDING), min(1, clinical + FOUR_DECIMAL_ROUNDING))
    supplied_interval = [max(0, fused - FOUR_DECIMAL_ROUNDING), min(1, fused + FOUR_DECIMAL_ROUNDING)]
    compatible = lower is not None and upper is not None and max(lower, supplied_interval[0]) <= min(upper, supplied_interval[1]) + 1e-12
    return {"supplied_probability": fused, "recomputed_probability": recomputed,
            "rounded_4dp_matches": exact, "rounding_compatible": compatible,
            "rounding_half_unit": FOUR_DECIMAL_ROUNDING,
            "recomputed_interval": [lower, upper], "supplied_rounding_interval": supplied_interval,
            "supplied_score_preserved": True}


def canonical_jsonl_bytes(patients: list[dict]) -> bytes:
    """Deterministic normalized bytes used both by preparation and export checks."""
    normalized = [PatientPrediction.from_dict(patient).to_dict() for patient in patients]
    ids = [patient["patient_id"] for patient in normalized]
    if not normalized or len(ids) != len(set(ids)):
        raise ContractError("handoff patients must be nonempty with unique patient IDs")
    return "".join(json.dumps(patient, ensure_ascii=True, allow_nan=False) + "\n" for patient in normalized).encode("utf-8")


def _object(value, path: str, fields: set[str]):
    if not isinstance(value, dict) or set(value) != fields:
        raise ContractError(f"{path} must be an object with exactly: {', '.join(sorted(fields))}")
    return value


def _text(value, path: str, limit: int = 160):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > limit:
        raise ContractError(f"{path} must be a nonempty bounded string without surrounding whitespace")
    if any(ord(character) < 32 for character in value):
        raise ContractError(f"{path} contains control characters")
    return value


def _number(value, path: str, *, probability: bool = False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{path} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ContractError(f"{path} must be a finite number") from None
    if not math.isfinite(result) or (probability and not 0 <= result <= 1):
        raise ContractError(f"{path} must be {'in [0, 1]' if probability else 'finite'}")
    return result


def _finite_tree(value, path: str):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        _number(value, path)
    elif isinstance(value, dict):
        for key, child in value.items():
            _finite_tree(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _finite_tree(child, f"{path}[{index}]")


def _read_source(root: Path, relative: str, sources: list[dict]) -> bytes:
    candidate = root / relative
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ContractError(f"handoff source must not contain symlinks: {relative}")
    if not candidate.resolve().is_relative_to(root) or not candidate.is_file():
        raise ContractError(f"handoff source file missing or outside source directory: {relative}")
    if candidate.stat().st_size > MAX_FILE_BYTES:
        raise ContractError(f"handoff source file exceeds {MAX_FILE_BYTES} bytes: {relative}")
    content = candidate.read_bytes()
    if len(content) > MAX_FILE_BYTES:
        raise ContractError(f"handoff source file exceeds its size limit: {relative}")
    sources.append({"relative_path": relative, "sha256": hashlib.sha256(content).hexdigest(), "size_bytes": len(content)})
    return content


def _read_json(root: Path, relative: str, sources: list[dict]):
    try:
        value = _strict_json(_read_source(root, relative, sources).decode("utf-8-sig"))
    except (UnicodeError, ValueError) as error:
        raise ContractError(f"invalid handoff JSON {relative}: {error}") from None
    _finite_tree(value, relative)
    return value


def _features(values, path: str, effect: str):
    if not isinstance(values, list) or not 1 <= len(values) <= 10:
        raise ContractError(f"{path} must contain 1 to 10 features")
    names, raw_names = set(), set()
    for index, feature in enumerate(values):
        key = f"{path}[{index}]"
        _object(feature, key, {"feature", "raw_feature", "value", effect})
        name = _text(feature["feature"], key + ".feature")
        raw = _text(feature["raw_feature"], key + ".raw_feature", 256)
        if name in names or raw in raw_names:
            raise ContractError(f"{path} has duplicate feature names or raw feature identifiers")
        names.add(name)
        raw_names.add(raw)
        _number(feature["value"], key + ".value")
        _number(feature[effect], key + "." + effect)
    return values


def read_handoff(source_dir: str | Path) -> dict:
    """Read and audit a synthetic packet; never alter its scores or source assets.

    Structural errors fail closed. Numerically finite but inconsistent SHAP or
    fusion declarations are retained in a report with warnings, not repaired.
    The fixed 0.5 threshold is an unvalidated synthetic-demo display choice.
    """
    supplied_root = Path(source_dir).expanduser().absolute()
    if supplied_root.is_symlink() or not supplied_root.is_dir():
        raise ContractError("handoff source must be an existing directory, not a symlink")
    root = supplied_root.resolve()
    sources = []
    try:
        handoff_text = _read_source(root, "HANDOFF_PAULO.md", sources).decode("utf-8-sig")
    except UnicodeError:
        raise ContractError("HANDOFF_PAULO.md must be UTF-8 text") from None
    if "synthetic patient data only" not in handoff_text.lower():
        raise ContractError("handoff must explicitly declare synthetic patient data only; this adapter is for the synthetic demo packet")
    score_provenance = ("producer_reported_trained_models_on_synthetic_inputs" if "real trained models" in handoff_text.lower()
                        else "producer_declared_synthetic_demonstration_outputs")
    try:
        csv_text = _read_source(root, "predictions/patient_predictions.csv", sources).decode("utf-8-sig")
    except UnicodeError:
        raise ContractError("handoff prediction CSV must be UTF-8") from None
    reader = csv.DictReader(io.StringIO(csv_text, newline=""))
    if reader.fieldnames != CSV_FIELDS:
        raise ContractError("handoff CSV header must be exactly " + ",".join(CSV_FIELDS))
    predictions = {}
    for line, row in enumerate(reader, 2):
        if None in row or any(value is None for value in row.values()):
            raise ContractError(f"handoff CSV row {line} has the wrong number of fields")
        pid = _text(row["Patient_id"], f"CSV row {line} Patient_id", 100)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", pid) or pid in predictions:
            raise ContractError(f"handoff CSV has an invalid or duplicate Patient_id: {pid}")
        scores = {}
        for modality in MODALITIES:
            try:
                value = float(row["prob_" + modality])
            except ValueError:
                raise ContractError(f"patient {pid} prob_{modality} must be numeric") from None
            scores[modality] = _number(value, f"patient {pid} prob_{modality}", probability=True)
        if row["actual_response"] not in {"0", "1"}:
            raise ContractError(f"patient {pid} actual_response must be integer 0 or 1")
        predictions[pid] = {"scores": scores, "label": int(row["actual_response"])}
    if not 1 <= len(predictions) <= 128:
        raise ContractError("handoff must contain between 1 and 128 synthetic patients")
    analysis = _read_json(root, "predictions/patient_feature_analysis.json", sources)
    narratives = _read_json(root, "predictions/narratives.json", sources)
    importance = _read_json(root, "predictions/feature_importances.json", sources)
    for name, records in (("patient_feature_analysis", analysis), ("narratives", narratives)):
        if not isinstance(records, dict) or set(records) != set(predictions):
            raise ContractError(f"{name} patient IDs must exactly match the prediction CSV")
    for pid, narrative in narratives.items():
        _text(narrative, f"source placeholder narrative {pid}", 4000)
    _object(importance, "feature_importances", {"clinical", "mif"})
    for modality, values in importance.items():
        if not isinstance(values, list) or not 1 <= len(values) <= 1000:
            raise ContractError(f"feature_importances.{modality} must be a nonempty bounded list")
        names = set()
        for index, item in enumerate(values):
            path = f"feature_importances.{modality}[{index}]"
            _object(item, path, {"feature", "importance"})
            name = _text(item["feature"], path + ".feature", 256)
            if name in names:
                raise ContractError(f"feature_importances.{modality} contains duplicate feature names")
            names.add(name)
            _number(item["importance"], path + ".importance")

    patients, audits, assets = [], {}, []
    expected_assets = set()
    for pid, supplied in predictions.items():
        item = analysis[pid]
        if not isinstance(item, dict) or not {"clinical", "mif"} <= set(item) or set(item) - {"clinical", "mif", "prob_mif_real"}:
            raise ContractError(f"analysis.{pid} requires clinical and mif, with only optional prob_mif_real")
        alternate_mif = None
        alternate_matches = None
        if "prob_mif_real" in item:
            alternate_mif = _number(item["prob_mif_real"], f"analysis.{pid}.prob_mif_real", probability=True)
            alternate_matches = math.isclose(alternate_mif, supplied["scores"]["mif"], rel_tol=0, abs_tol=1e-9)
        clinical = _object(item["clinical"], f"analysis.{pid}.clinical", {"base_value", "output_value", "features"})
        base = _number(clinical["base_value"], f"analysis.{pid}.clinical.base_value", probability=True)
        shap_output = _number(clinical["output_value"], f"analysis.{pid}.clinical.output_value", probability=True)
        clinical_features = _features(clinical["features"], f"analysis.{pid}.clinical.features", "shap")
        mif_features = _features(item["mif"], f"analysis.{pid}.mif", "contrast")
        try:
            shap_sum = math.fsum(feature["shap"] for feature in clinical_features)
        except OverflowError:
            raise ContractError(f"analysis.{pid}.clinical SHAP sum must be finite") from None
        reconstruction = _number(base + shap_sum, f"analysis.{pid}.clinical.reconstructed_output")
        clinical_score = supplied["scores"]["clinical"]
        additivity_tolerance = (len(clinical_features) + 2) * FOUR_DECIMAL_ROUNDING
        exact_additive = math.isclose(reconstruction, shap_output, rel_tol=0, abs_tol=1e-9)
        additive = math.isclose(reconstruction, shap_output, rel_tol=0, abs_tol=additivity_tolerance + 1e-12)
        matches = math.isclose(shap_output, clinical_score, rel_tol=0, abs_tol=1e-9)
        import_shap = additive and matches
        warnings = []
        if not additive:
            warnings.append(f"Clinical SHAP base plus contributions reconstructs {reconstruction!r}, not declared SHAP output {shap_output!r}, outside the explicit four-decimal rounding tolerance {additivity_tolerance:g}.")
        if not matches:
            warnings.append(f"Clinical SHAP output {shap_output!r} does not match supplied clinical score {clinical_score!r}; it is not an explanation of that prediction.")
        if import_shap:
            warnings.append("Clinical signed SHAP is admitted from source-declared responder-probability contributions because its output matches the CSV and additivity is compatible with four-decimal rounding. This checks numerical consistency, not independent model provenance, causal effects or clinical validity.")
        else:
            warnings.append("Clinical signed SHAP is retained only in original source data; canonical responder attributions are omitted because output/additivity checks failed.")
        warnings.append("mIF attention contrast is a high-minus-low-attention feature difference, not a responder attribution or tile response probability.")
        if alternate_matches is False:
            warnings.append(f"Source prob_mif_real {alternate_mif!r} differs from CSV mIF score {supplied['scores']['mif']!r}; CSV remains authoritative and linkage of mIF explanations to that displayed score is unresolved.")
        mif, clin = supplied["scores"]["mif"], clinical_score
        fusion = _fusion_audit(mif, clin, supplied["scores"]["fused"])
        if not fusion["rounding_compatible"]:
            warnings.append("Supplied fused score is outside the product-formula interval allowing four-decimal rounding of both inputs and output; original supplied score is preserved.")
        elif not fusion["rounded_4dp_matches"]:
            warnings.append("Supplied fused score differs from exact recomputation using rounded CSV inputs but is compatible with four-decimal input/output rounding; original supplied score is preserved.")
        audits[pid] = {
            "warnings": warnings,
            "clinical_shap": {"csv_probability": clinical_score, "base_value": base, "output_value": shap_output,
                              "shap_sum": shap_sum, "reconstructed_output": reconstruction,
                              "additivity_matches": additive, "exact_additivity_matches": exact_additive,
                              "additivity_tolerance": additivity_tolerance, "rounding_half_unit": FOUR_DECIMAL_ROUNDING,
                              "output_matches_prediction": matches,
                              "output_delta": shap_output - clinical_score, "attributions_imported": import_shap,
                              "attribution_scale": "responder_probability", "provenance_independently_validated": False},
            "mif_score": {"csv_probability": mif, "prob_mif_real": alternate_mif,
                          "matches_csv": alternate_matches, "explanation_linkage_resolved": False},
            "fusion": fusion,
        }
        for kind, directory, filename in (("clinical_shap", "clinical_shap", "shap_waterfall"),
                                           ("mif_contrast", "mif_features", "mif_contrast")):
            for extension in ("png", "pdf"):
                relative = f"figures/{directory}/{filename}_{pid}.{extension}"
                expected_assets.add(relative)
                content = _read_source(root, relative, sources)
                signature = b"\x89PNG\r\n\x1a\n" if extension == "png" else b"%PDF-"
                if not content.startswith(signature):
                    raise ContractError(f"handoff asset does not have its declared {extension.upper()} signature: {relative}")
                fingerprint = sources[-1]
                asset_warnings = ["Original source figure retained for testing; image contents are not automatically validated."]
                if kind == "clinical_shap":
                    if not matches or not additive:
                        asset_warnings.append("The associated clinical JSON is inconsistent with its supplied prediction; this figure must not be treated as a validated explanation of that score.")
                    if extension == "png":
                        figure_audit = _clinical_figure_audit(fingerprint["sha256"], clinical, clinical_score)
                        audits[pid]["clinical_figure"] = figure_audit
                        if figure_audit["mismatch_detected"]:
                            note = "Manual audit of this original PNG: " + "; ".join(figure_audit["mismatches"]) + ". The original plot is retained for testing and does not represent the current structured explanation."
                            asset_warnings.append(note)
                            warnings.append(note)
                    elif audits[pid]["clinical_figure"]["mismatch_detected"]:
                        asset_warnings.append("The associated PNG has manually observed discrepancies against current source data; this PDF is retained for testing and was not individually visually verified.")
                else:
                    asset_warnings.append("Attention contrasts are feature measurements, not responder attributions or tile response probabilities.")
                    if alternate_matches is False:
                        asset_warnings.append("The source alternate mIF model score differs from the authoritative CSV score; linkage of this figure to the displayed prediction is unresolved.")
                assets.append({"patient_id": pid, "kind": kind, "format": extension, **fingerprint,
                               "warnings": asset_warnings})
        canonical = {
            "schema_version": "1.0", "patient_id": pid,
            "predictions": {modality: {"probability": supplied["scores"][modality],
                                        "model_id": "paulo-handoff-synthetic-" + modality,
                                        "calibration": "unknown", "decision_threshold": DEMO_THRESHOLD}
                            for modality in MODALITIES},
            "top_features": {
                "clinical": [{"feature": f["feature"], "value": f["value"], "unit": "",
                              "direction": "source-coded value; coding not independently validated",
                              "attribution": {"method": "SHAP", "value": f["shap"], "scale": "responder_probability"} if import_shap else None}
                             for f in clinical_features],
                "mif": [{"feature": f["feature"], "value": f["value"], "unit": "",
                         "direction": f"high-minus-low attention feature contrast={f['contrast']:+g}; not responder attribution",
                         "attribution": None} for f in mif_features],
            },
            "clinical_context": "Synthetic inputs and scenario labels. "
                                + ("The producer reports trained-model outputs on these synthetic inputs; local model execution is not independently verified. " if score_provenance == "producer_reported_trained_models_on_synthetic_inputs" else "Outputs are producer-declared synthetic demonstration data. ")
                                + ("Clinical SHAP is source-declared on the responder-probability scale and passes output/additivity checks with explicit rounding tolerance; this does not establish causal or clinical validity. " if import_shap else "Clinical signed SHAP is excluded because output/additivity checks failed. ")
                                + "Clinical feature values retain source coding. mIF values are descriptive attention-weighted tile feature means and contrasts, not responder attributions; their linkage to the CSV mIF score is unresolved. Original plots may be stale and are audited separately. Threshold 0.5 is an unvalidated demo choice. Endpoint and clinical coding dictionary remain unverified.",
            "response_definition": "Not specified", "ground_truth": supplied["label"], "evaluation_partition": "synthetic",
        }
        patients.append(PatientPrediction.from_dict(canonical).to_dict())
    figures_dir = root / "figures"
    actual_assets = {path.relative_to(root).as_posix() for path in figures_dir.rglob("*") if path.is_file() or path.is_symlink()}
    if actual_assets != expected_assets:
        raise ContractError("handoff figure inventory contains unexpected paths or does not match patient IDs")
    tile_tables = read_tile_tables(root, predictions, sources, _read_source)
    report = {
        "schema_version": "1.0", "synthetic": True, "patient_count": len(patients),
        "decision_threshold": DEMO_THRESHOLD, "response_definition": "Not specified",
        "score_provenance": score_provenance,
        "clinical_shap_mismatch_count": sum(not row["clinical_shap"]["output_matches_prediction"] for row in audits.values()),
        "clinical_shap_imported_count": sum(row["clinical_shap"]["attributions_imported"] for row in audits.values()),
        "clinical_plot_mismatch_count": sum(row["clinical_figure"]["mismatch_detected"] is True for row in audits.values()),
        "mif_score_mismatch_count": sum(row["mif_score"]["matches_csv"] is False for row in audits.values()),
        "tile_audit": tile_tables["report"],
        "warnings": [
            "Synthetic status is a source declaration; this importer does not establish de-identification or permission for other data.",
            "Threshold 0.5 is a synthetic-demo display choice, not an estimated or clinically validated cutoff.",
            "Original scores are preserved; no fusion is inferred and no inconsistent SHAP value is repaired.",
            "The source fusion product formula is audited numerically only; independence, priors and calibration assumptions are not verified.",
            "Structured clinical SHAP is admitted only if its output matches the CSV and reconstruction is compatible with four-decimal rounding (half a unit per base, contribution and output). Its responder-probability scale and model provenance remain producer declarations, not independent validation.",
            "mIF attention contrasts are descriptive feature differences, not response-class attributions.",
            "Original figures are retained for testing with visible warnings. Image contents are not automatically validated; known manual observations are keyed to exact PNG hashes. PDFs were not individually visually audited.",
            "Source placeholder narratives and aggregate real-cohort performance claims are excluded from canonical inputs and prompts.",
            "Synthetic labels are retained as ground_truth with evaluation_partition=synthetic; the copilot withholds labels from language-model prompts and excludes synthetic rows from clinical performance evaluation.",
            "Source global importance is preserved separately, not relabeled as patient-specific explanation. Optional tile files are audited separately; an attention weight must never be relabeled as a response probability.",
        ],
        "patients": audits,
    }
    content = canonical_jsonl_bytes(patients)
    return {"source_dir": str(root), "patients": patients, "report": report, "original_analysis": analysis,
            "global_importance": importance, "assets": assets, "source_files": sources, "tile_files": tile_tables["raw_files"],
            "input_sha256": hashlib.sha256(content).hexdigest()}


def prepare_handoff(source_dir: str | Path, output_dir: str | Path) -> dict:
    """Publish canonical input and audit sidecars into a new private directory."""
    output = Path(output_dir).expanduser().absolute()
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError("handoff output directory must be absent or empty and not a symlink")
    dataset = read_handoff(source_dir)
    if output.resolve().is_relative_to(Path(dataset["source_dir"])):
        raise ValueError("handoff output directory must be outside the original source packet")
    canonical = canonical_jsonl_bytes(dataset["patients"])
    assets = {"schema_version": "1.0", "synthetic": True, "assets": dataset["assets"]}
    asset_bytes = (json.dumps(assets, ensure_ascii=True, allow_nan=False, indent=2) + "\n").encode("utf-8")
    manifest = {"schema_version": "1.0", "synthetic": True, "source_directory": dataset["source_dir"],
                "input_sha256": dataset["input_sha256"], "patient_count": len(dataset["patients"]),
                "report": dataset["report"], "source_files": dataset["source_files"],
                "artifact_hashes": {"patients.jsonl": hashlib.sha256(canonical).hexdigest(),
                                    "patient_assets.json": hashlib.sha256(asset_bytes).hexdigest()}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".handoff-prepare-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / "patients.jsonl").write_bytes(canonical)
        (staging / "patient_assets.json").write_bytes(asset_bytes)
        (staging / "handoff_manifest.json").write_text(json.dumps(manifest, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")
        for path in staging.iterdir():
            path.chmod(0o600)
        if output.exists():
            output.rmdir()
        os.rename(staging, output)
        output.chmod(0o700)
    return manifest
