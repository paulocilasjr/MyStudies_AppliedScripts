"""Structured patient reports: grounded facts plus screened model prose for the hackathon research demo."""
from __future__ import annotations

import json
import re
import threading
from typing import Callable

from .backends import PROMPT_VERSION, TransformersBackend, VLLMBackend, build_messages
from .nim import NIMBackend
from .prompts import PROMPT_SHA256, REPLY_FIELDS
from .report import fallback_sections, hypothesis, plain_name, render_report
from .schema import MODALITIES, ContractError, PatientPrediction

# Each engine name is also the narrative_source of its accepted generations.
GENERATIVE_BACKENDS = {"vllm": VLLMBackend, "transformers": TransformersBackend, "nim": NIMBackend}


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


_MODALITY = {"clinical": "clinical", "spatial mif": "mif", "mif": "mif", "tissue": "mif", "fused": "fused", "combined": "fused"}
# "clinical features", "tissue resection" and similar phrases name evidence, not a model's score.
_NOT_MODALITY = (r"(?!\s+(?:features?|attributions?|variables?|measurements?|data|context|review|information|notes?"
                 r"|literature|findings?|contrasts?|factors?|history|resection|covariates?|sampling))")
_SIDE_CLAIM = (r"\b(?:favou?r\w*|support\w*|point\w*(?:\s+to(?:wards?)?)?|lean\w*(?:\s+towards?)?"
               r"|push\w*(?:\s+\S+){0,4}?\s+towards?|towards?)\s+(?:the\s+|a\s+)?(?P<side>non-?respon\w*|respon\w*)")
_CLAUSE = re.compile(r"[,:]|\b(?:while|whereas|but|although|though|however|yet)\b")
_SENTENCE = re.compile(r"[.;!?]\s")
_MARKERS = re.compile(r"\b(?:anti-)?(?:cd\d{1,3}[a-z]?|pd-?l?1|ctla-?4|lag-?3|sox10|m1[a-d])\+?", re.I)
_FORBIDDEN = [r"\b(recommend\w*|prescrib\w*|dos(?:e|es|ing|age)|administer\w*|mg)\b",
              r"\b(start|stop|switch|continue|initiate|discontinue|escalate|select|choose|offer)\b.{0,50}"
              r"\b(therapy|treatment|drug|pembrolizumab|ipilimumab|nivolumab|immunotherapy)\b",
              r"\b(should|must)\b.{0,40}\b(receive|be treated|be given|start|stop)\b",
              r"\bwill\s+(?:not\s+)?(?:respond|benefit|survive|progress|relapse)\b",
              r"\b(guarantee\w*|cure[sd]?|curative|definitive\w*|definitely|certainly|proves?|proven|causal|causes?)\b",
              r"\b(outperform\w*|superior)\b", r"\b(trial matching|eligible for|eligibility|enrol\w*)\b"]


def _side(word: str) -> int:
    return 0 if word.startswith("non") else 1


def report_contradictions(sections: dict, patient: dict, comparison: dict) -> list[str]:
    """Reject generated prose that contradicts the scores, attributions or hypothesis the application computed.

    Small models restate example templates with the wrong sides; these clause-level
    heuristics catch such statements. Passing them does not prove the text correct.
    """
    classes = comparison["predicted_classes"]
    hyp = hypothesis(comparison)
    # Clinical feature names map to their attribution sign; None means no direction was supplied.
    signs = {}
    for feature in patient["top_features"].get("clinical", []):
        attribution = feature["attribution"]
        sign = int(attribution["value"] > 0) if attribution and attribution["value"] != 0 else None
        for alias in {feature["feature"], plain_name(feature["feature"]), re.sub(r"\s*\(.*?\)", "", feature["feature"])}:
            signs[alias.lower().strip()] = sign
    features = "|".join(re.escape(alias) for alias in sorted(signs, key=len, reverse=True))
    claim = re.compile((rf"(?P<feature>{features})|" if features else "")
                       + r"\bjoins? the (?P<joined>clinical|spatial mif|mif|tissue) side\b|(?P<both>\bsame side as both\b)"
                       + rf"|\b(?P<modality>clinical|spatial mif|mif|tissue|fused|combined)\b{_NOT_MODALITY}"
                       + r"|\b(?P<threshold>above|below)\b|" + _SIDE_CLAIM)
    text = " ".join(sections.values()).lower()
    wrong = False
    if comparison["threshold_disagreement"]:
        wrong = bool(re.search(r"\b(?:models|scores|modalities|they)\s+(?:\w+\s+)?(?<!not )agree\b|\bin agreement\b", text))
    elif not comparison["score_disagreement"]:
        wrong = bool(re.search(r"(?<!not )(?<!no )\b(?:disagree\w*|discordan\w*|conflict\w*)", text))
    for sentence in _SENTENCE.split(text):
        for clause in _CLAUSE.split(sentence):
            if re.search(r"\b(?:missing|unavailable|absent|never supplied|not supplied)\b", clause):
                wrong = wrong or any(_MODALITY[name] in classes for name in re.findall(r"\b(?:spatial mif|mif|fused)\b", clause))
            if re.search(r"\bhypothes[ie]s\b", clause) and not re.search(r"\bno (?:strong|clear|firm)\b|\bnot (?:a )?(?:strong|clear)\b", clause):
                claimed = {_side(word) for word in re.findall(r"\b(non-?responders?|responders?)\b(?!\s+thresholds?)", clause)}
                if hyp["side"] is not None:
                    wrong = wrong or bool(claimed - {hyp["side"]})
                elif claimed:
                    tentative = re.search(r"\b(weak|tentative|leaning|tendency)\b", clause)
                    wrong = wrong or not tentative or claimed != {hyp["tendency"]}
            if re.search(r"\b(?:tendency|tends?)\b", clause) and not claim.search(re.sub(_SIDE_CLAIM, "", clause)):
                claimed = {_side(word) for word in re.findall(r"\b(non-?respon\w*|respon\w*)\b(?!\s+thresholds?)", clause)}
                wrong = wrong or bool(claimed and claimed != {hyp["tendency"]})
            # A feature with a signed attribution must not be described as having no direction.
            if re.search(r"\b(?:cannot be assigned|no signed attribution|not supplied|no direction|without a direction)\b", clause):
                named = [match["feature"] for match in claim.finditer(clause) if match.groupdict().get("feature")]
                wrong = wrong or any(signs[name] is not None for name in named)
            pending_features, pending_modalities = [], []
            for match in claim.finditer(clause):
                if match.groupdict().get("feature"):
                    pending_features.append(signs[match["feature"]])
                    continue
                if match["modality"]:
                    pending_modalities.append(_MODALITY[match["modality"]])
                    continue
                if match["joined"]:
                    checks = [("fused", classes.get(_MODALITY[match["joined"]]))]
                elif match["both"]:
                    checks = [("fused", classes.get("clinical")), ("fused", classes.get("mif"))]
                elif match["threshold"]:
                    checks = [(m, int(match["threshold"] == "above")) for m in pending_modalities]
                elif pending_features:
                    wrong = wrong or any(sign != _side(match["side"]) for sign in pending_features)
                    checks = []
                else:
                    checks = [(m, _side(match["side"])) for m in pending_modalities]
                wrong = wrong or any(classes.get(m) is None or classes[m] != side for m, side in checks)
                pending_features, pending_modalities = [], []
    return ["contradicts_supplied_comparison"] if wrong else []


def screen_report(replies: dict, *, patient: dict, comparison: dict) -> tuple[dict | None, list[str]]:
    """Heuristic screen of the generated report parts, one raw `{"text": ...}` reply per part.

    Passing does not imply clinical correctness.
    """
    if not isinstance(replies, dict) or set(replies) != set(REPLY_FIELDS):
        return None, ["invalid_generation_schema"]
    sections = {}
    for field in REPLY_FIELDS:
        raw = replies[field]
        if not isinstance(raw, str) or len(raw) > 3000:
            return None, ["invalid_generation_size"]
        try:
            obj = _strict_json(raw)
        except (ValueError, TypeError):
            return None, ["invalid_generation_json"]
        if not isinstance(obj, dict) or set(obj) != {"text"} or not isinstance(obj["text"], str):
            return None, ["invalid_generation_schema"]
        sections[field] = " ".join(obj["text"].split())
    issues = []
    if not all(30 <= len(text) <= 900 for text in sections.values()):
        issues.append("invalid_section_length")
    text = " ".join(sections.values())
    # Numbers come only from the application; supplied feature and marker names may contain digits.
    scrubbed = text
    for feature in (f for features in patient["top_features"].values() for f in features):
        for name in (feature["feature"], plain_name(feature["feature"])):
            scrubbed = re.sub(re.escape(name), " ", scrubbed, flags=re.I)
    scrubbed = _MARKERS.sub(" ", scrubbed)
    if re.search(r"\d|%", scrubbed):
        issues.append("generated_numeric_claim")
    if re.search(r"<|>|```|https?://|www\.|\[|\]|\b(system|assistant|ignore previous|ignore instructions)\b", text, re.I):
        issues.append("generated_instruction_or_markup")
    if any(re.search(pattern, scrubbed, re.I | re.S) for pattern in _FORBIDDEN):
        issues.append("unsupported_clinical_or_performance_claim")
    framing = sections["prediction_summary"] + " " + sections["conclusion"]
    if comparison["score_disagreement"] or comparison["threshold_disagreement"]:
        mentions = re.search(r"\b(disagree\w*|discordan\w*|conflict\w*|differ\w*|split|uneven)\b", framing, re.I)
        denies = re.search(r"\b(?:do not|does not|no|without(?: a)?(?: flagged)?)\s+(?:disagree\w*|discordance|conflict\w*)\b", framing, re.I)
        if not mentions or denies:
            issues.append("missing_disagreement_context")
    if comparison["missing_modalities"] and not re.search(r"\b(missing|unavailable|absent|not available)\b", text, re.I):
        issues.append("missing_modality_context")
    if re.search(r"\btowards? (?:not supplied|none supplied|no direction|cannot)\b", text, re.I):
        issues.append("garbled_feature_direction")
    issues.extend(report_contradictions(sections, patient, comparison))
    return (None, issues) if issues else (sections, [])


class Copilot:
    """Reuse one instance per process. Mock is explicit; a model backend never silently becomes mock.

    generator, when provided, receives a list of chat conversations and returns
    a corresponding list of JSON strings. It is intended for offline tests.
    """
    def __init__(self, backend: str = "vllm", model_path: str | None = None, *,
                 generator: Callable | None = None, disagreement_threshold: float = 0.20, **settings):
        if backend != "mock" and backend not in GENERATIVE_BACKENDS:
            raise ValueError("backend must be mock, vllm, transformers, or nim")
        if not 0 < disagreement_threshold <= 1:
            raise ValueError("disagreement_threshold must be in (0, 1]")
        if backend == "mock" and (generator is not None or settings):
            raise ValueError("mock backend does not accept a generator or GPU settings")
        self.backend = backend
        self.disagreement_threshold = disagreement_threshold
        self._generator = generator
        self._engine = None
        if backend in GENERATIVE_BACKENDS and generator is None:
            if backend == "nim":
                if model_path is not None:
                    raise ValueError("nim uses a hosted model_id, not a local model_path")
                self._engine = NIMBackend(**settings)
            elif model_path is None:
                raise ValueError(f"{backend} requires model_path for a local prepared snapshot")
            else:
                self._engine = GENERATIVE_BACKENDS[backend](model_path, **settings)
        self._lock = threading.Lock()

    @property
    def metadata(self) -> dict:
        if self._engine:
            return self._engine.metadata
        return {"backend": self.backend, "generator": "injected" if self._generator else "deterministic_mock"}

    def interpret(self, patient: PatientPrediction | dict) -> dict:
        return self.interpret_many([patient])[0]

    def interpret_many(self, patients: list[PatientPrediction | dict], *, generation_review: list | None = None) -> list[dict]:
        # Revalidate even dataclass inputs, which could have been manually constructed.
        normalized = [PatientPrediction.from_dict(p.to_dict() if isinstance(p, PatientPrediction) else p).to_dict()
                      for p in patients]
        if len({p["patient_id"] for p in normalized}) != len(normalized):
            raise ContractError("batch contains duplicate patient IDs")
        if not normalized:
            return []
        summaries = [summarize_evidence(p, disagreement_threshold=self.disagreement_threshold) for p in normalized]
        raw = []
        if self.backend != "mock":
            # One short conversation per report part keeps the small model's prompts focused.
            conversations = [build_messages(p, comparison=s[0], field=field)
                             for p, s in zip(normalized, summaries) for field in REPLY_FIELDS]
            with self._lock:
                generate = self._generator or self._engine.generate
                replies = generate(conversations)
            if not isinstance(replies, list) or len(replies) != len(conversations):
                raise RuntimeError("backend output count does not match input count")
            parts = len(REPLY_FIELDS)
            raw = [dict(zip(REPLY_FIELDS, replies[i * parts:(i + 1) * parts])) for i in range(len(normalized))]
        results = []
        for i, patient in enumerate(normalized):
            comparison, limitations = summaries[i]
            if self.backend == "mock":
                sections, issues, source, status = fallback_sections(patient, comparison), [], "mock", "mock"
                limitations.insert(0, "Synthetic narrative from the mock backend; no language model was executed.")
            else:
                sections, issues = screen_report(raw[i], patient=patient, comparison=comparison)
                source, status = self.backend, "passed"
                if sections is None:
                    sections = fallback_sections(patient, comparison)
                    source, status = "fallback", "fallback"
                    limitations.insert(0, "Generated text failed the automated screen; deterministic report text is shown.")
            if generation_review is not None:
                generation_review.append({"patient_id": patient["patient_id"],
                    "raw_generation": json.dumps(raw[i], ensure_ascii=True) if self.backend != "mock" else None,
                    "narrative_source": source, "screen_status": status, "screen_issues": issues,
                    "prompt_version": PROMPT_VERSION, "prompt_sha256": PROMPT_SHA256})
            results.append({
                "schema_version": "1.0", "patient_id": patient["patient_id"],
                "predictions": patient["predictions"], "top_features": patient["top_features"],
                "clinical_context": patient["clinical_context"],
                "response_definition": patient["response_definition"],
                "narrative": render_report(patient, comparison, sections),
                "narrative_source": source, "review_required": True, "limitations": limitations,
                "comparison": comparison,
                "quality": {"status": status, "issues": issues, "screen": "heuristic; human review required"},
                "provenance": {"prompt_version": PROMPT_VERSION, "prompt_sha256": PROMPT_SHA256, **self.metadata},
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
