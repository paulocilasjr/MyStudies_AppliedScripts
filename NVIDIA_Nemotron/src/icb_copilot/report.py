"""Structured patient report: deterministic facts, curated literature, and screened model prose.

The application renders every number, feature list and literature note. The language
model writes only the three prose fields in REPLY_FIELDS; a rejected reply is replaced
by deterministic fallback prose built from the same facts.
"""
from __future__ import annotations

from importlib.resources import files
import json
import math
import re

from .schema import MODALITIES

REVIEW_SENTENCE = "Research output requires independent clinical review and does not establish treatment benefit."
RULE = "------------------------"
SCORE_LABELS = {"clinical": "Clinical model score", "mif": "Spatial mIF model score", "fused": "Fused model prediction score"}
DISPLAY = {"clinical": "clinical", "mif": "spatial mIF", "fused": "fused"}
SIDE = {1: "responder", 0: "non-responder"}
SECTION_HEADERS = ("1) Model evaluation predictions:", "2) Clinical evaluation:", "3) Immune evaluation:", "4) Conclusions:")
CAUTIONS = ("the scores are uncalibrated, the response endpoint is not specified, both models come from small cohorts, "
            "and the fused score only recombines the other two")
CLINICAL_FEATURES_FOR_MODEL = 3
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")

_KNOWLEDGE = json.loads(files("icb_copilot").joinpath("skills/icb-interpretation/references/feature-literature.json")
                        .read_text(encoding="utf-8"))
SOURCES = _KNOWLEDGE["sources"]
_ENTRIES = [{**entry, "pattern": re.compile(entry["match"], re.I)} for entry in _KNOWLEDGE["features"]]


def literature(feature: str, modality: str) -> dict | None:
    """Return the first curated literature entry matching a supplied feature name."""
    return next((e for e in _ENTRIES if e["modality"] == modality and e["pattern"].search(feature)), None)


def plain_name(feature: str) -> str:
    """Feature name as written for the model; JSON escaping would turn arrows into digits."""
    return feature.replace("→", "to")


def _number(value) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "not supplied" if value is None else str(value)
    return str(int(value)) if float(value).is_integer() else f"{value:.4g}"


def _with_unit(feature: dict) -> str:
    return _number(feature["value"]) + (" " + feature["unit"] if feature["unit"] else "")


def _value_words(value) -> str:
    """Integer codes in words; the model must not copy digits."""
    if isinstance(value, (int, float)) and not isinstance(value, bool) and float(value).is_integer() and 0 <= value <= 10:
        return f"coded {NUMBER_WORDS[int(value)]}"
    return "see report"


def margin(probability: float, threshold: float | None) -> str:
    if threshold is None:
        return "no threshold"
    distance = probability - threshold
    size = "just" if abs(distance) < 0.1 else "moderately" if abs(distance) < 0.3 else "well"
    return f"{size} {'above' if distance >= 0 else 'below'} threshold"


def describe_comparison(predictions: dict, comparison: dict) -> str:
    """Render the application's comparison flags in plain words for the prompt.

    A small model restates words more reliably than it decodes class flags; the
    wording avoids digits, which the screen rejects in generated prose.
    """
    classes = comparison["predicted_classes"]
    parts = []
    if comparison["threshold_disagreement"] and not comparison["score_disagreement"]:
        parts.append("models disagree in a near-threshold split although the scores are close")
    elif comparison["threshold_disagreement"]:
        parts.append("models disagree on opposite sides of the threshold")
    elif comparison["score_disagreement"]:
        parts.append("models disagree because their scores differ materially on the same side")
    elif "clinical" in classes and "mif" in classes:
        parts.append("models agree")
    if comparison["missing_modalities"]:
        parts.append(" and ".join(DISPLAY[m] for m in comparison["missing_modalities"]) + " missing")
    if classes and all(side is None for side in classes.values()):
        parts.append("no thresholds supplied, so no side is assigned")
    else:
        parts.extend(f"{DISPLAY[m]} {margin(predictions[m]['probability'], predictions[m]['decision_threshold'])}"
                     for m in classes)
        clinical, mif, fused = (classes.get(m) for m in ("clinical", "mif", "fused"))
        if None not in (clinical, mif, fused) and "fused" in classes:
            parts.append("fused on the same side as both" if clinical == mif else
                         "fused joins " + DISPLAY["clinical" if fused == clinical else "mif"])
    return "; ".join(parts)


def hypothesis(comparison: dict) -> dict:
    """Strongest hypothesis implied by the supplied threshold sides; the model explains it, never chooses it."""
    classes = comparison["predicted_classes"]
    known = {m: side for m, side in classes.items() if side is not None}
    unavailable = ([f"{DISPLAY[m]} missing" for m in comparison["missing_modalities"]]
                   + [f"{DISPLAY[m]} without a threshold" for m, side in classes.items() if side is None])
    if not known:
        return {"side": None, "tendency": None, "kind": "undetermined",
                "statement": "no strong hypothesis: no responder thresholds were supplied, so no score is assigned a side"}
    singles = {m: known[m] for m in ("clinical", "mif") if m in known}
    fused = known.get("fused")
    if len(set(singles.values())) > 1 or (fused is not None and singles and fused not in singles.values()):
        favours = " and ".join(f"the {DISPLAY[m]} model favours {SIDE[side]}" for m, side in singles.items())
        lean = f"; the fused score leans {SIDE[fused]}" if fused is not None else ""
        return {"side": None, "tendency": fused, "kind": "conflicting", "statement": f"no strong hypothesis: {favours}{lean}"}
    side = next(iter(known.values()))
    if len(singles) < 2:
        source = " and ".join(DISPLAY[m] for m in known)
        return {"side": side, "tendency": side, "kind": "single-modality",
                "statement": f"weak hypothesis: {SIDE[side]}, from the {source} score only; " + ", ".join(unavailable)}
    uneven = comparison["score_disagreement"]
    statement = f"strongest hypothesis: {SIDE[side]}, with every model on the {SIDE[side]} side"
    if uneven:
        statement += ", although the clinical and spatial mIF scores differ materially, so support is uneven"
    return {"side": side, "tendency": side, "kind": "uneven" if uneven else "consistent", "statement": statement}


def clinical_groups(features: list[dict]) -> tuple[list, list, list]:
    """Split clinical features by the sign of their supplied attribution, strongest first."""
    toward = {1: [], 0: []}
    unsigned = []
    for feature in features:
        attribution = feature["attribution"]
        if attribution and attribution["value"] != 0:
            toward[1 if attribution["value"] > 0 else 0].append(feature)
        else:
            unsigned.append(feature)
    strength = lambda f: -abs(f["attribution"]["value"])
    return sorted(toward[1], key=strength), sorted(toward[0], key=strength), unsigned


def contrast(feature: dict) -> float | None:
    """Attention contrast recorded by the handoff importer in the direction text, if any."""
    match = re.search(r"contrast=([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)", feature["direction"], re.I)
    return float(match.group(1)) if match and math.isfinite(float(match.group(1))) else None


def model_focus(feature: dict) -> str:
    value = contrast(feature)
    if value is None:
        return f"supplied direction: {feature['direction']}"
    if value == 0:
        return "no difference between the tiles the mIF model weighted most and least"
    return f"{'higher' if value > 0 else 'lower'} in the tiles the mIF model weighted most"


def model_payload(patient: dict, comparison: dict) -> dict:
    """The current case as the model reads it: plain words, curated notes, and no digits to copy."""
    clinical = []
    # The strongest signed features only; the report itself lists every supplied feature.
    ranked = sorted(patient["top_features"].get("clinical", []),
                    key=lambda f: -abs(f["attribution"]["value"]) if f["attribution"] else 0)
    for feature in ranked[:CLINICAL_FEATURES_FOR_MODEL]:
        entry = literature(feature["feature"], "clinical")
        attribution = feature["attribution"]
        item = {"feature": plain_name(feature["feature"]), "value": _value_words(feature["value"])}
        # Unsigned features get a different key, so the model does not fill "pushes toward" with it.
        if attribution and attribution["value"] != 0:
            item["pushes_toward"] = SIDE[1 if attribution["value"] > 0 else 0]
        else:
            item["direction"] = "none supplied"
        item["literature"] = entry["gist"] if entry else "no curated note"
        clinical.append(item)
    immune = []
    for feature in patient["top_features"].get("mif", []):
        entry = literature(feature["feature"], "mif")
        value = contrast(feature)
        focus = (feature["direction"] if value is None else "no difference" if value == 0
                 else "higher" if value > 0 else "lower")
        immune.append({"feature": plain_name(feature["feature"]), "focus": focus,
                       "literature": entry["direction"] if entry else "no curated note"})
    return {"situation": describe_comparison(patient["predictions"], comparison),
            "hypothesis": hypothesis(comparison)["statement"],
            "clinical_evidence": clinical or "none supplied", "immune_evidence": immune or "none supplied",
            "clinical_context": patient["clinical_context"], "response_definition": patient["response_definition"]}


def fallback_sections(patient: dict, comparison: dict) -> dict:
    """Deterministic prose for the mock backend and for screened-out generations."""
    hyp = hypothesis(comparison)
    classes = comparison["predicted_classes"]
    if hyp["kind"] == "undetermined":
        summary = "No responder thresholds were supplied, so the scores are not assigned to responder or non-responder."
        conclusion = "No strong hypothesis can be drawn because no thresholds were supplied."
    elif hyp["kind"] == "conflicting":
        sides = " while ".join(f"the {DISPLAY[m]} score favours {SIDE[classes[m]]}"
                               for m in ("clinical", "mif") if classes.get(m) is not None)
        lean = f", and the fused score leans {SIDE[hyp['tendency']]}" if hyp["tendency"] is not None else ""
        summary = f"The models disagree: {sides}{lean}, so there is no strong hypothesis."
        conclusion = ("No strong hypothesis can be drawn because the models disagree"
                      + (f"; the fused score leans {SIDE[hyp['tendency']]}, but it only recombines the two inputs"
                         if hyp["tendency"] is not None else "")
                      + ". Review the discordant clinical and tissue evidence before relying on either side.")
    elif hyp["kind"] == "single-modality":
        summary = (f"Only part of the evidence is available and it favours {SIDE[hyp['side']]}, a single-model hypothesis; "
                   + ", ".join(f"the {DISPLAY[m]} score is missing" for m in comparison["missing_modalities"]) + ".")
        conclusion = f"{SIDE[hyp['side']].capitalize()} is only a weak hypothesis because missing evidence was not inferred."
    else:
        summary = f"Every available model sits on the {SIDE[hyp['side']]} side of its threshold, so {SIDE[hyp['side']]} is the strongest hypothesis from these scores."
        if hyp["kind"] == "uneven":
            summary += " The clinical and spatial mIF scores differ materially, so the support is uneven."
        conclusion = f"{SIDE[hyp['side']].capitalize()} is the strongest hypothesis from the supplied scores."
    summary += " The scores are uncalibrated, so they favour a side rather than give an exact chance of response."
    toward_responder, toward_non, unsigned = clinical_groups(patient["top_features"].get("clinical", []))
    if toward_responder or toward_non:
        parts = [f"{_join([f['feature'] for f in group])} {'push' if len(group) > 1 else 'pushes'} the clinical score toward {SIDE[side]}"
                 for group, side in ((toward_responder, 1), (toward_non, 0)) if group]
        clinical = "; ".join(parts) + ". Signed attributions describe the model, not causes; the literature notes give published context."
    elif unsigned:
        clinical = "No signed clinical attributions were supplied, so the clinical features cannot be assigned a direction."
    else:
        clinical = "No clinical feature evidence was supplied."
    if comparison["missing_modalities"]:
        conclusion += " Missing modalities were not inferred."
    conclusion += f" Cautions: {CAUTIONS}."
    return {"prediction_summary": summary, "clinical_interpretation": clinical, "conclusion": conclusion}


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _sources(keys) -> str:
    return "; ".join(SOURCES[key]["short"] for key in dict.fromkeys(keys))


def report_prefix(patient: dict) -> str:
    """The deterministic opening, up to the first generated text; validated in every completed run."""
    lines = [f"Patient {patient['patient_id']} report:", "", SECTION_HEADERS[0]]
    for modality in MODALITIES:
        prediction = patient["predictions"].get(modality)
        lines.append(f"{SCORE_LABELS[modality]} = " + (f"{prediction['probability']:.4f}" if prediction
                                                       else "not available (missing; not inferred)"))
    return "\n".join(lines) + "\n" + RULE + " "


def render_report(patient: dict, comparison: dict, sections: dict) -> str:
    lines = [report_prefix(patient) + sections["prediction_summary"], "", SECTION_HEADERS[1]]
    clinical_features = patient["top_features"].get("clinical", [])
    toward_responder, toward_non, unsigned = clinical_groups(clinical_features)
    listed = lambda group: "; ".join(f"{f['feature']} = {_with_unit(f)} ({f['attribution']['method']} {f['attribution']['value']:+.3g})"
                                     for f in group) or "none supplied"
    lines.append(f"Clinical features towards responder = {listed(toward_responder)}")
    lines.append(f"Clinical features towards non-responder = {listed(toward_non)}")
    if unsigned:
        lines.append("Clinical features without a signed attribution = "
                     + "; ".join(f"{f['feature']} = {_with_unit(f)} ({f['direction']})" for f in unsigned))
    lines.append(f"{RULE} {sections['clinical_interpretation']}")
    noted = [(f, entry) for f in clinical_features if (entry := literature(f["feature"], "clinical"))]
    if noted:
        lines.append("Literature notes:")
        lines.extend(f"{f['feature']}: {entry['note']} ({_sources(entry['sources'])})" for f, entry in noted)
    lines += ["", SECTION_HEADERS[2]]
    immune = patient["top_features"].get("mif", [])
    if not immune:
        lines.append("No spatial mIF features were supplied; tissue evidence is not inferred.")
    first_use = {}
    for feature in immune:
        entry = literature(feature["feature"], "mif")
        value = contrast(feature)
        detail = f"value {_with_unit(feature)}; {model_focus(feature)}"
        if value:
            detail += f", contrast {value:+.4g}"
        if feature["attribution"]:
            detail += f"; {feature['attribution']['method']} {feature['attribution']['value']:+.3g} {feature['attribution']['scale']}"
        if entry is None:
            note = "No curated literature note; read as model evidence only."
        elif entry["match"] in first_use:
            note = f"Same literature as {first_use[entry['match']]}. Classification: {entry['direction']}."
        else:
            first_use[entry["match"]] = feature["feature"]
            note = f"{entry['note']} Classification: {entry['direction']}. ({_sources(entry['sources'])})"
        lines.append(f"{feature['feature']} ({detail}): {note}")
    if immune:
        lines.append("Attention contrasts show where the mIF model focused; they are not signed effects on the score.")
    lines += ["", SECTION_HEADERS[3], sections["conclusion"], "", REVIEW_SENTENCE]
    return "\n".join(lines)


def validate_report(narrative: str, patient: dict) -> bool:
    """Check the deterministic frame of a stored report against its canonical evidence."""
    return (narrative.startswith(report_prefix(patient)) and narrative.endswith("\n\n" + REVIEW_SENTENCE)
            and all(header in narrative for header in SECTION_HEADERS))
