"""Grounded facts plus screened narrative text for the hackathon research demo."""
from __future__ import annotations

import json
import re
import threading
from typing import Callable

from .backends import PROMPT_VERSION, VLLMBackend, build_messages
from .schema import MODALITIES, ContractError, PatientPrediction

DISPLAY = {"clinical": "clinical", "mif": "spatial mIF", "fused": "fused"}
REVIEW_SENTENCE = "Research output requires independent clinical review and does not establish treatment benefit."


def summarize_evidence(patient: dict, *, disagreement_threshold: float = 0.20) -> tuple[dict, list[str]]:
    predictions = patient["predictions"]
    missing = [m for m in MODALITIES if m not in predictions]
    single = [predictions[m]["probability"] for m in ("clinical", "mif") if m in predictions]
    gap = abs(single[0] - single[1]) if len(single) == 2 else None
    classes = {m: (int(p["probability"] >= p["decision_threshold"]) if p["decision_threshold"] is not None else None)
               for m, p in predictions.items()}
    defined = [classes[m] for m in ("clinical", "mif") if m in classes and classes[m] is not None]
    threshold_disagreement = len(defined) == 2 and defined[0] != defined[1]
    limitations = ["Research demonstration; predictions and narratives are not clinically validated."]
    if missing:
        limitations.append("Missing predictions: " + ", ".join(missing) + "; unavailable modalities are not inferred.")
    if any(p["calibration"] != "calibrated" for p in predictions.values()):
        limitations.append("Calibration is unknown or absent for one or more models; scores are not established individual outcome probabilities.")
    if any(p["decision_threshold"] is None for p in predictions.values()):
        limitations.append("One or more decision thresholds were not supplied; no responder classification is assigned for those models.")
    if patient["response_definition"].lower() in {"not specified", "unspecified", "unknown"}:
        limitations.append("The ICB response endpoint and assessment time were not specified.")
    if gap is not None and gap >= disagreement_threshold - 1e-12:
        limitations.append("Clinical and mIF scores differ materially; review discordant evidence and model uncertainty.")
    if threshold_disagreement:
        limitations.append("Clinical and mIF classifications disagree at their supplied thresholds.")
    if not any(f.get("attribution") for features in patient["top_features"].values() for f in features):
        limitations.append("Signed feature attributions were not supplied; measurement directions do not establish model effects.")
    limitations.append("A fused score alone cannot demonstrate better performance; compare paired held-out predictions using the same patients and endpoint.")
    return {"missing_modalities": missing, "clinical_mif_gap": gap,
            "disagreement_threshold": disagreement_threshold,
            "score_disagreement": gap is not None and gap >= disagreement_threshold - 1e-12,
            "threshold_disagreement": threshold_disagreement, "predicted_classes": classes}, limitations


def score_sentence(patient: dict) -> str:
    scores = ", ".join(f"{DISPLAY[m]} {patient['predictions'][m]['probability']:.3f}"
                       for m in MODALITIES if m in patient["predictions"])
    evidence = []
    for modality in MODALITIES:
        # Keep the narrative concise; the complete feature list remains in the
        # structured result for the patient selector and audit.
        for feature in patient["top_features"].get(modality, [])[:2]:
            value = json.dumps(feature["value"], ensure_ascii=False) if not isinstance(feature["value"], str) else feature["value"]
            value = value[:64] + ("…" if len(value) > 64 else "")
            unit = " " + feature["unit"] if feature["unit"] else ""
            detail = f"{DISPLAY[modality]} {feature['feature']}={value}{unit} (measurement: {feature['direction']})"
            if feature["attribution"]:
                attribution = feature["attribution"]
                detail += f" [supplied {attribution['method']} attribution {attribution['value']:+.3g} {attribution['scale']}]"
            evidence.append(detail)
    suffix = "; supplied features include " + "; ".join(evidence) if evidence else ""
    return f"Supplied ICB responder model scores are {scores}{suffix}."


def fallback_interpretation(patient: dict, comparison: dict) -> str:
    if comparison["score_disagreement"] or comparison["threshold_disagreement"]:
        first = "Clinical and spatial mIF predictions are discordant and warrant review of the supplied evidence."
    elif all(m in patient["predictions"] for m in ("clinical", "mif")):
        first = "Clinical and spatial mIF predictions provide complementary tabular and tissue evidence for review."
    else:
        first = "Only the supplied modality predictions can be interpreted; missing evidence limits multimodal comparison."
    return first + " Feature measurements and model attributions should be reviewed separately; neither establishes a causal treatment effect."


def _strict_json(text: str) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON number")))


def screen_narrative(raw: str) -> tuple[str | None, list[str]]:
    """Heuristic screen only: passing does not imply clinical correctness."""
    issues = []
    if not isinstance(raw, str) or len(raw) > 5000:
        return None, ["invalid_generation_size"]
    try:
        obj = _strict_json(raw)
    except (ValueError, TypeError):
        return None, ["invalid_generation_json"]
    if not isinstance(obj, dict) or set(obj) != {"interpretation"} or not isinstance(obj["interpretation"], str):
        return None, ["invalid_generation_schema"]
    text = obj["interpretation"].strip()
    if not 40 <= len(text) <= 1200:
        issues.append("invalid_narrative_length")
    if re.search(r"\d|%", text):
        issues.append("generated_numeric_claim")
    if re.search(r"<|>|```|https?://|www\.|\[|\]|\b(system|assistant|ignore previous|ignore instructions)\b", text, re.I):
        issues.append("generated_instruction_or_markup")
    # Conservative lexical screen; negated language can also fall back safely.
    forbidden = [r"\b(recommend\w*|prescrib\w*|dose\w*|dosage|mg|administer\w*)\b",
                 r"\b(start|stop|switch|continue|initiate|discontinue|select|choose)\b.{0,50}\b(therapy|treatment|drug|pembrolizumab|ipilimumab|nivolumab)\b",
                 r"\b(should|must|will)\b.{0,50}\b(respond|receive|benefit|survive|remission)\b",
                 r"\b(guarantee\w*|cure\w*|definit\w*|diagnos\w*|prognosis|outperform\w*|superior|proves?|causes?|causal)\b",
                 r"\b(improv\w*|increas\w*|decreas\w*)\b.{0,40}\b(accuracy|survival|outcomes?|response|benefit)\b",
                 r"\b(trial matching|eligible for|clinical trial|likely responder|non-responder|nonresponder)\b"]
    if any(re.search(pattern, text, re.I | re.S) for pattern in forbidden):
        issues.append("unsupported_clinical_or_performance_claim")
    if re.search(r"\b(high|low|elevated)\b.{0,60}\b(driv\w*|favors?|predict\w*|suggest\w*|indicat\w*)\b", text, re.I):
        issues.append("measurement_direction_used_as_effect")
    if re.search(r"\b(patient|tumou?r)\b.{0,30}\b(has|have|is|shows|demonstrates|exhibits|suffers)\b|"
                 r"\b(metastatic|mutation\w*|resistance|sensitivity|prognostic|immune infiltration)\b", text, re.I):
        issues.append("generated_patient_or_biological_claim")
    return (None, issues) if issues else (text, [])


class Copilot:
    """Reuse one instance per process. Mock is explicit; vLLM never silently becomes mock.

    generator, when provided, receives a list of chat conversations and returns
    a corresponding list of JSON strings. It is intended for offline tests.
    """
    def __init__(self, backend: str = "vllm", model_path: str | None = None, *,
                 generator: Callable | None = None, disagreement_threshold: float = 0.20, **settings):
        if backend not in {"mock", "vllm"}:
            raise ValueError("backend must be mock or vllm")
        if not 0 < disagreement_threshold <= 1:
            raise ValueError("disagreement_threshold must be in (0, 1]")
        if backend == "mock" and (generator is not None or settings):
            raise ValueError("mock backend does not accept a generator or GPU settings")
        self.backend = backend
        self.disagreement_threshold = disagreement_threshold
        self._generator = generator
        self._engine = None
        if backend == "vllm" and generator is None:
            if model_path is None:
                raise ValueError("vllm requires model_path for a local prepared snapshot")
            self._engine = VLLMBackend(model_path, **settings)
        self._lock = threading.Lock()

    @property
    def metadata(self) -> dict:
        if self._engine:
            return self._engine.metadata
        return {"backend": self.backend, "generator": "injected" if self._generator else "deterministic_mock"}

    def interpret(self, patient: PatientPrediction | dict) -> dict:
        return self.interpret_many([patient])[0]

    def interpret_many(self, patients: list[PatientPrediction | dict]) -> list[dict]:
        # Revalidate even dataclass inputs, which could have been manually constructed.
        normalized = [PatientPrediction.from_dict(p.to_dict() if isinstance(p, PatientPrediction) else p).to_dict()
                      for p in patients]
        if len({p["patient_id"] for p in normalized}) != len(normalized):
            raise ContractError("batch contains duplicate patient IDs")
        if not normalized:
            return []
        raw = []
        if self.backend == "vllm":
            with self._lock:
                generate = self._generator or self._engine.generate
                raw = generate([build_messages(p) for p in normalized])
            if not isinstance(raw, list) or len(raw) != len(normalized):
                raise RuntimeError("backend output count does not match input count")
        results = []
        for i, patient in enumerate(normalized):
            comparison, limitations = summarize_evidence(patient, disagreement_threshold=self.disagreement_threshold)
            if self.backend == "mock":
                interpretation, issues, source, status = fallback_interpretation(patient, comparison), [], "mock", "mock"
                limitations.insert(0, "Synthetic narrative from the mock backend; no language model was executed.")
            else:
                interpretation, issues = screen_narrative(raw[i])
                source, status = "vllm", "passed"
                if interpretation is None:
                    interpretation = fallback_interpretation(patient, comparison)
                    source, status = "fallback", "fallback"
                    limitations.insert(0, "Generated text failed the automated screen; a deterministic evidence summary is shown.")
            results.append({
                "schema_version": "1.0", "patient_id": patient["patient_id"],
                "predictions": patient["predictions"], "top_features": patient["top_features"],
                "clinical_context": patient["clinical_context"],
                "response_definition": patient["response_definition"],
                "narrative": score_sentence(patient) + " " + interpretation + " " + REVIEW_SENTENCE,
                "narrative_source": source, "review_required": True, "limitations": limitations,
                "comparison": comparison,
                "quality": {"status": status, "issues": issues, "screen": "heuristic; human review required"},
                "provenance": {"prompt_version": PROMPT_VERSION, **self.metadata},
            })
        return results


def generate_clinical_narrative(patient_id: str, prob_mif: float | None, prob_clinical: float | None,
                                prob_fused: float | None, top_features_mif: list[dict],
                                top_features_clinical: list[dict], clinical_context: str, *,
                                copilot: Copilot, response_definition: str = "Not specified") -> str:
    """Compatibility function for the originally proposed team integration.

    Inject a reusable Copilot to make backend and local model selection explicit.
    Pass None for an unavailable modality; never substitute a zero score.
    """
    probabilities = {"mif": prob_mif, "clinical": prob_clinical, "fused": prob_fused}
    features = {m: f for m, f in (("mif", top_features_mif), ("clinical", top_features_clinical)) if f}
    return copilot.interpret({"patient_id": patient_id,
        "predictions": {m: {"probability": p} for m, p in probabilities.items() if p is not None},
        "top_features": features, "clinical_context": clinical_context,
        "response_definition": response_definition})["narrative"]
