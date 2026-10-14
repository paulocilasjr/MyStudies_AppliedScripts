"""Read a prepared synthetic handoff bundle; the viewer never loads a language model.

Run from the repository root:
streamlit run demo/handoff_app.py -- --bundle-dir results/handoff/ui [--api-url http://127.0.0.1:8000]

With --api-url, the displayed patient's supplied evidence (never its label) can be
sent to the loopback copilot API (`nemotron_copilot serve`) for live regeneration.
The stdlib loader is deliberately importable without Streamlit or GPU packages.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import time
import urllib.error
import urllib.parse
import urllib.request

MODALITIES = ("clinical", "mif", "fused")
LABELS = {"clinical": "Clinical", "mif": "Spatial mIF", "fused": "Fused"}
MAX_ASSET_BYTES = 64 * 1024 * 1024
SOURCE_QUALITY = {"mock": "mock", "vllm": "passed", "transformers": "passed", "fallback": "fallback"}
SOURCE_TEXT = {"mock": "Mock — no language model executed",
               "fallback": "Deterministic fallback — generated text failed screening",
               "vllm": "vLLM generated text — heuristic screen passed",
               "transformers": "Local Nemotron generated text (Hugging Face Transformers) — heuristic screen passed"}
LIVE_FIELDS = ("schema_version", "patient_id", "predictions", "top_features", "clinical_context", "response_definition")


def _json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key in {path.name}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON number")))


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("patient IDs must be nonempty simple identifiers without paths")
    return value


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("scores and explanation outputs must be finite numbers")
    return float(value)


def _probability(value):
    number = _number(value)
    if not 0 <= number <= 1:
        raise ValueError("scores must be between zero and one")
    return number


def _strings(values, name):
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError(f"{name} must be a list of strings")
    return values


def local_asset(root: Path, entry: dict) -> Path:
    """Reject absolute paths, traversal, symlink escapes, and altered assets."""
    relative = entry.get("relative_path")
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("asset path must be a relative POSIX path")
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(part in {".", ".."} for part in relative.split("/")):
        raise ValueError("asset path must stay inside the bundle")
    if path.parts[0] != "figures" or path.suffix != "." + entry.get("format", ""):
        raise ValueError("asset extension and figures directory must match its declared format")
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError("asset must be an existing file inside the bundle")
    size = entry.get("size_bytes")
    digest = entry.get("sha256")
    if type(size) is not int or not 0 < size <= MAX_ASSET_BYTES or result.stat().st_size != size:
        raise ValueError("asset size does not match its manifest")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("asset requires a SHA256 digest")
    if hashlib.sha256(result.read_bytes()).hexdigest() != digest:
        raise ValueError("asset SHA256 does not match its manifest")
    return result


def load_bundle(directory: str | Path) -> dict:
    """Read a synthetic complete-score bundle and check cross-file identity."""
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("bundle directory does not exist; prepare and export the handoff first")
    handoff = _json(root / "handoff_manifest.json")
    assets = _json(root / "patient_assets.json")
    export = _json(root / "ui_export_manifest.json")
    if not isinstance(handoff, dict) or handoff.get("synthetic") is not True:
        raise ValueError("this companion accepts explicitly synthetic handoff bundles only")
    if not isinstance(assets, dict) or assets.get("synthetic") is not True or assets.get("schema_version") != "1.0":
        raise ValueError("invalid synthetic patient asset manifest")
    if not isinstance(export, dict) or export.get("display_threshold") != 0.5:
        raise ValueError("the viewer requires an explicitly declared display threshold of 0.5")
    if export.get("synthetic_labels") is not True or export.get("bundle_kind") != "synthetic_paulo_handoff":
        raise ValueError("this companion requires the dedicated synthetic Paulo handoff export")
    patients = {}
    with (root / "patient_predictions.csv").open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"Patient_id", "prob_mif", "prob_clinical", "prob_fused", "actual_response"}
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or not required <= set(reader.fieldnames):
            raise ValueError("prediction CSV has missing or duplicate required columns")
        for row in reader:
            pid = _id(row["Patient_id"])
            if pid in patients:
                raise ValueError("duplicate patient ID in predictions")
            label = row["actual_response"]
            if label not in {"", "0", "1"}:
                raise ValueError("synthetic response label must be 0, 1, or blank")
            try:
                scores = {m: _probability(float(row["prob_" + m])) for m in MODALITIES}
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid supplied score for {pid}: {exc}") from exc
            patients[pid] = {"patient_id": pid, "scores": scores, "actual_response": int(label) if label else None}
    if not patients:
        raise ValueError("bundle contains no patients")
    included = export.get("included_patient_ids")
    if (not isinstance(included, list) or any(not isinstance(pid, str) for pid in included)
            or len(set(included)) != len(included) or set(included) != set(patients)
            or type(handoff.get("patient_count")) is not int or handoff["patient_count"] != len(patients)):
        raise ValueError("export and handoff manifest patient identities/counts must match the prediction CSV")
    narratives = _json(root / "narratives.json")
    analysis = _json(root / "patient_feature_analysis.json")
    if not isinstance(narratives, dict) or set(narratives) != set(patients) or any(not isinstance(v, str) or not v.strip() for v in narratives.values()):
        raise ValueError("narratives must contain nonempty text for exactly the supplied patient IDs")
    if not isinstance(analysis, dict) or set(analysis) != set(patients):
        raise ValueError("feature analysis must match the supplied patient IDs")
    results = {}
    for line in (root / "copilot_results.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        # Duplicate keys and nonfinite values are rejected by the same parser.
        result = json.loads(line, object_pairs_hook=_unique_pairs,
                            parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON number")))
        if not isinstance(result, dict):
            raise ValueError("copilot results must be JSON objects")
        pid = _id(result.get("patient_id"))
        if pid in results or pid not in patients:
            raise ValueError("duplicate or unknown patient in copilot results")
        source = result.get("narrative_source")
        quality = result.get("quality")
        if source not in SOURCE_QUALITY or not isinstance(quality, dict):
            raise ValueError("copilot source and quality are required")
        expected = SOURCE_QUALITY[source]
        if quality.get("status") != expected or result.get("review_required") is not True:
            raise ValueError("copilot source/quality/review metadata disagree")
        _strings(quality.get("issues"), "quality issues")
        _strings(result.get("limitations"), "limitations")
        if not isinstance(result.get("provenance"), dict):
            raise ValueError("copilot provenance is required")
        if not isinstance(result.get("narrative"), str) or not result["narrative"].strip() or result["narrative"] not in narratives[pid]:
            raise ValueError("display narrative must preserve its patient's structured copilot narrative")
        for m in MODALITIES:
            predictions = result.get("predictions")
            if not isinstance(predictions, dict) or not isinstance(predictions.get(m), dict):
                raise ValueError("all three structured copilot predictions are required")
            prediction = predictions[m]
            score = _probability(prediction.get("probability"))
            if prediction.get("decision_threshold") != 0.5 or not math.isclose(score, patients[pid]["scores"][m], rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"CSV and copilot score/threshold disagree for {pid}/{m}")
        results[pid] = result
    if set(results) != set(patients):
        raise ValueError("copilot results must match all supplied patient IDs")
    report = handoff.get("report", handoff)
    reports = report.get("patients", {}) if isinstance(report, dict) else {}
    if not isinstance(reports, dict):
        raise ValueError("invalid per-patient handoff report")
    entries = assets.get("assets")
    if not isinstance(entries, list):
        raise ValueError("patient assets must be a list")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid patient asset entry")
        pid = _id(entry.get("patient_id"))
        key = (pid, entry.get("kind"), entry.get("format"))
        if pid not in patients or key[1] not in {"clinical_shap", "mif_contrast"} or key[2] not in {"png", "pdf"} or key in seen:
            raise ValueError("duplicate or unsupported patient asset")
        seen.add(key)
        _strings(entry.get("warnings", []), "asset warnings")
        entry = {**entry, "path": local_asset(root, entry)}
        patients[pid].setdefault("assets", {})[(key[1], key[2])] = entry
    for pid, patient in patients.items():
        if any((kind, "png") not in patient.get("assets", {}) for kind in ("clinical_shap", "mif_contrast")):
            raise ValueError(f"both supplied PNG plots are required for {pid}")
        detail = analysis[pid]
        if not isinstance(detail, dict) or not isinstance(detail.get("clinical"), dict):
            raise ValueError("clinical feature analysis is required")
        patient_report = reports.get(pid, {})
        if not isinstance(patient_report, dict):
            raise ValueError("invalid patient handoff report")
        warnings = _strings(patient_report.get("warnings", []), "patient warnings")[:]
        figure = patient_report.get("clinical_figure", {})
        if not isinstance(figure, dict):
            raise ValueError("invalid clinical figure audit")
        figure_mismatch = figure.get("mismatch_detected")
        if figure_mismatch is not None and type(figure_mismatch) is not bool:
            raise ValueError("clinical figure mismatch must be boolean or null")
        if figure.get("png_sha256") is not None and figure["png_sha256"] != patient["assets"][("clinical_shap", "png")]["sha256"]:
            raise ValueError("clinical figure audit does not match the displayed PNG")
        clinical_output = _number(detail["clinical"].get("output_value"))
        if not math.isclose(clinical_output, patient["scores"]["clinical"], rel_tol=0, abs_tol=1e-9):
            warnings.insert(0, f"Clinical explanation output {clinical_output:g} differs from the supplied clinical score {patient['scores']['clinical']:g}. The original SHAP plot is retained for testing; it cannot be treated as an explanation of that score.")
        producer_mif = detail.get("prob_mif_real")
        if producer_mif is not None:
            producer_mif = _probability(producer_mif)
        mif_score = {"csv_probability": patient["scores"]["mif"], "prob_mif_real": producer_mif,
                     "matches_csv": (None if producer_mif is None else math.isclose(producer_mif, patient["scores"]["mif"], rel_tol=0, abs_tol=1e-9))}
        patient.update(narrative=narratives[pid], result=results[pid], analysis=detail,
                       warnings=list(dict.fromkeys(warnings)), audit=patient_report,
                       clinical_plot_mismatch=figure_mismatch, mif_score=mif_score)
    return {"root": root, "patients": patients, "handoff_manifest": handoff, "ui_export_manifest": export}


def _unique_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key in copilot results")
        result[key] = value
    return result


def outcome_label(score: float, actual: int | None) -> str:
    if actual is None:
        return "Synthetic response label unknown"
    predicted = int(score >= 0.5)
    if predicted == actual:
        return "True positive" if actual else "True negative"
    return "False positive" if predicted else "False negative"


def white_image(path: Path):
    """Composite a display copy; keep original transparent plot bytes intact."""
    from PIL import Image
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        white = Image.new("RGBA", rgba.size, "white")
        white.alpha_composite(rgba)
        return white.convert("RGB")


def loopback_api(url: str) -> str:
    """Accept only a plain http://127.0.0.1:PORT (or localhost) copilot API base URL."""
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.username
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("--api-url must be a loopback copilot API such as http://127.0.0.1:8000")
    return f"http://{parsed.hostname}:{parsed.port or 80}"


def _call_api(url: str, payload=None, *, timeout: float):
    body = None if payload is None else json.dumps(payload, ensure_ascii=True, allow_nan=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="GET" if body is None else "POST",
                                     headers={} if body is None else {"Content-Type": "application/json"})
    # Never route loopback traffic through a system or environment proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def api_health(api_url: str) -> dict:
    return _call_api(api_url + "/health", timeout=3)


def live_interpret(api_url: str, result: dict) -> dict:
    """Regenerate from exactly the displayed patient's supplied evidence; labels are not sent."""
    return _call_api(api_url + "/v1/interpret", {key: result[key] for key in LIVE_FIELDS}, timeout=900)


def live_panel(st, api_url: str, pid: str, result: dict) -> None:
    st.subheader("Live local Nemotron")
    try:
        health = api_health(api_url)
    except (OSError, ValueError) as exc:
        st.error(f"The local copilot API at {api_url} is not reachable ({type(exc).__name__}). Start it with run_local_mvp.sh.")
        return
    st.caption(f"Connected to {api_url} · backend {health.get('backend')} · model loaded: {health.get('model_loaded')}. "
               "Only this patient's supplied evidence is sent; the synthetic label is not.")
    if st.button("Generate this patient's narrative live", key=f"live-{pid}"):
        with st.spinner("Nemotron is generating on this computer…"):
            started = time.monotonic()
            try:
                live = live_interpret(api_url, result)
            except urllib.error.HTTPError as exc:
                st.error(f"Local API returned HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:500]}")
            except (OSError, ValueError) as exc:
                st.error(f"Live generation failed ({type(exc).__name__}).")
            else:
                st.session_state.setdefault("live_results", {})[pid] = {"result": live, "seconds": time.monotonic() - started}
    entry = st.session_state.get("live_results", {}).get(pid)
    if entry:
        live = entry["result"]
        source = live.get("narrative_source")
        quality = live.get("quality", {})
        st.text(f"Source: {SOURCE_TEXT.get(source, source)} · {entry['seconds']:.1f}s")
        if quality.get("issues"):
            st.warning("Screen issues: " + ", ".join(quality["issues"]))
        st.text(live.get("narrative", ""))
        st.caption("Scores, feature lists, literature notes and the review notice are printed by the application; the prose after each "
                   "dashed line and the conclusions are model-generated. "
                   + ("This live output is identical to the exported batch narrative." if live.get("narrative") == result["narrative"]
                      else "This live output differs from the exported batch narrative, which is unchanged."))


def main(argv=None):
    import streamlit as st

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", required=True, help="exported synthetic handoff UI directory")
    parser.add_argument("--api-url", help="optional loopback copilot API for live regeneration")
    args = parser.parse_args(argv)
    api_url = loopback_api(args.api_url) if args.api_url else None
    st.set_page_config(page_title="Synthetic ICB handoff", layout="wide")
    st.title("ICB response · synthetic patient handoff")
    st.warning("Inputs and response labels are simulated. The producer reports scores computed by trained models; that execution has not been independently reproduced here. These cases do not measure clinical performance.")
    try:
        bundle = load_bundle(args.bundle_dir)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        st.error("The handoff bundle could not be loaded safely.")
        st.text(str(exc))
        st.stop()
    ids = sorted(bundle["patients"])
    pid = st.selectbox("Synthetic patient", ids, key="handoff_patient")
    patient = bundle["patients"][pid]
    result = patient["result"]
    st.subheader(f"Patient {pid}")
    for column, modality in zip(st.columns(3), MODALITIES):
        with column:
            st.metric(LABELS[modality] + " supplied score", f"{patient['scores'][modality]:.4f}")
            st.caption("Display class: " + ("responder" if patient["scores"][modality] >= 0.5 else "non-responder"))
    st.caption("Positive class = ICB responder. Display threshold = 0.5 for testing; calibration is unknown and the response endpoint remains unspecified.")
    label = patient["actual_response"]
    st.text("Synthetic response label: " + ("unknown" if label is None else f"{label} ({'responder' if label else 'non-responder'})"))
    outcome = outcome_label(patient["scores"]["fused"], label)
    if outcome in {"False positive", "False negative"}:
        st.warning("Fused display outcome: " + outcome.lower() + " against the supplied synthetic label.")
    else:
        st.info("Fused display outcome: " + outcome.lower() + " against the supplied synthetic label.")
    mismatch = next((warning for warning in patient["warnings"]
                     if "differs from the supplied clinical score" in warning), None)
    clinical_figure_problem = patient["clinical_plot_mismatch"] is True
    if clinical_figure_problem:
        st.warning("Clinical figure warning: the original SHAP plot contains discrepancies against the current source data. Scores use the supplied CSV; details remain in the audit notes.")
    elif mismatch:
        st.warning(mismatch)
    clinical, mif = st.columns(2)
    for column, kind, title in ((clinical, "clinical_shap", "Original clinical SHAP plot"),
                                (mif, "mif_contrast", "Original mIF attention-contrast plot")):
        with column:
            st.subheader(title)
            entry = patient["assets"][(kind, "png")]
            if kind == "mif_contrast" and patient["mif_score"]["matches_csv"] is False:
                mif_score = patient["mif_score"]
                st.warning(f"mIF score mismatch: CSV {mif_score['csv_probability']:g}; producer field prob_mif_real {mif_score['prob_mif_real']:g}. Display and narrative use the CSV score; explanation linkage is unresolved.")
            st.image(white_image(entry["path"]), width="stretch")
            st.caption("Supplied synthetic image; original bytes preserved.")
            if kind == "clinical_shap" and (mismatch or clinical_figure_problem):
                st.caption("Unverified figure: differences from current evidence are recorded in the audit notes below.")
            if kind == "mif_contrast":
                st.caption("Attention contrast describes feature differences between higher- and lower-attention tiles. It is not a signed response attribution or a tile response probability.")
            pdf = patient["assets"].get((kind, "pdf"))
            if pdf:
                st.download_button("Download supplied PDF", pdf["path"].read_bytes(),
                                   file_name=pdf["path"].name, mime="application/pdf", key=f"{pid}-{kind}-pdf")
    with st.expander("Patient and figure audit notes"):
        notes = list(patient["warnings"])
        for entry in patient["assets"].values():
            notes.extend(entry.get("warnings", []))
        st.text("\n\n".join(dict.fromkeys(notes)))
    st.subheader("Copilot report")
    source = result["narrative_source"]
    source_text = SOURCE_TEXT[source]
    if result["provenance"].get("generator") == "injected":
        source_text += " (injected test generator)"
    st.text("Source: " + source_text)
    st.text("Quality: " + result["quality"]["status"] + " · independent human review required")
    if result["quality"]["issues"]:
        st.warning("Screen issues: " + ", ".join(result["quality"]["issues"]))
    if "[Placeholder" in patient["narrative"]:
        st.warning("This narrative is a source placeholder, not generated interpretive output.")
    st.text(result["narrative"])
    if api_url:
        live_panel(st, api_url, pid, result)
    with st.expander("Full exported report and disclosures"):
        st.text(patient["narrative"])
    with st.expander("Source features, warnings and provenance"):
        st.caption("Original feature analysis is retained for inspection, including declared output mismatches. No values or figures are repaired by this viewer.")
        st.json({"patient_id": pid, "original_analysis": patient["analysis"], "provenance": result["provenance"],
                 "quality": result["quality"], "limitations": result["limitations"], "review_required": result["review_required"],
                 "handoff_audit": patient["audit"]})
    with st.expander("Local bundle"):
        st.caption(f"{len(ids)} synthetic patients · file viewer only; inference runs separately.")
        st.text(str(bundle["root"]))


if __name__ == "__main__":
    main()
