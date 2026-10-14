"""Check skill loading, the structured report contract, and reviewable raw generations."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from icb_copilot.backends import build_messages
from icb_copilot.copilot import Copilot, report_contradictions, screen_report, summarize_evidence
from icb_copilot.experiment import run_experiment
from icb_copilot.io import load_jsonl
from icb_copilot.prompts import FIELD_INPUTS, FIELD_PROMPTS, PROMPT_SHA256, PROMPT_VERSION, REPLY_FIELDS, WORKED_EXAMPLES
from icb_copilot.report import SOURCES, describe_comparison, hypothesis, literature, model_payload
from icb_copilot.schema import PatientPrediction

from helpers import generator, part_of, prediction

ROOT = Path(__file__).resolve().parents[1]
# Actual local Nemotron reply for the synthetic P12 case with prompt 2.0.
P12_REPLY = {
    "prediction_summary": "The models disagree: the clinical score sits moderately below its responder threshold while the spatial mIF "
                          "score sits moderately above it, and the fused score sits just above, so there is no strong hypothesis and "
                          "the tendency is toward responder. The scores are uncalibrated, so neither side is an exact chance of responding.",
    "clinical_interpretation": "LDH level pushes the clinical score toward non-responder. In the literature, elevated lactate dehydrogenase "
                               "is an established adverse prognostic factor in metastatic melanoma, which tempers the responder reading.",
    "conclusion": "There is no strong hypothesis because the clinical evidence favours non-responder while the tissue evidence favours "
                  "responder; the tendency is toward responder, following the fused score. Review the discordant evidence before "
                  "relying on either side. Cautions: the scores are uncalibrated, the response endpoint is not specified, both models "
                  "come from small cohorts, and the fused score only recombines the other two.",
}


def case(scores, threshold=0.5, clinical=(), mif=()):
    """Canonical synthetic case with optional (name, SHAP) clinical and (name, contrast) mIF features."""
    features = {}
    if clinical:
        features["clinical"] = [{"feature": name, "value": 1, "unit": "", "direction": "source-coded value",
                                 "attribution": None if att is None else {"method": "SHAP", "value": att, "scale": "responder_probability"}}
                                for name, att in clinical]
    if mif:
        features["mif"] = [{"feature": name, "value": 1.0, "unit": "", "attribution": None,
                            "direction": f"high-minus-low attention feature contrast={c:+g}; not responder attribution"}
                           for name, c in mif]
    patient = PatientPrediction.from_dict({"patient_id": "X", "top_features": features, "predictions": {
        m: {"probability": v, "decision_threshold": threshold} for m, v in scores.items()}}).to_dict()
    return patient, summarize_evidence(patient)[0]


class PromptTests(unittest.TestCase):
    def test_runtime_includes_packaged_skill_and_worked_examples(self):
        patient = PatientPrediction.from_dict(prediction()).to_dict()
        for field in REPLY_FIELDS:
            with self.subTest(field=field):
                messages = build_messages(patient, comparison=summarize_evidence(patient)[0], field=field)
                self.assertEqual(messages[0]["content"], FIELD_PROMPTS[field])
                self.assertIn("Project:", messages[0]["content"])
                for example in WORKED_EXAMPLES:
                    self.assertIn(json.dumps(example["output"][field], ensure_ascii=True), messages[0]["content"])
                for other in set(REPLY_FIELDS) - {field}:
                    self.assertNotIn("Task: " + other, messages[0]["content"])
        self.assertEqual(len(PROMPT_SHA256), 64)
        self.assertTrue(PROMPT_VERSION.startswith("icb-interpretation-2."))

    def test_worked_examples_match_their_source_evidence_and_pass_screen(self):
        for example in WORKED_EXAMPLES:
            with self.subTest(example=example["input"]["hypothesis"]):
                evidence = copy.deepcopy(example["source_evidence"])
                patient = PatientPrediction.from_dict({"patient_id": "EXAMPLE", **evidence}).to_dict()
                comparison, _ = summarize_evidence(patient)
                payload = model_payload(patient, comparison)
                self.assertEqual(example["input"], {key: payload[key] for key in example["input"]})
                self.assertEqual(set(example["output"]), set(REPLY_FIELDS))
                replies = {field: json.dumps({"text": example["output"][field]}) for field in REPLY_FIELDS}
                sections, issues = screen_report(replies, patient=patient, comparison=comparison)
                self.assertEqual(sections, example["output"])
                self.assertEqual(issues, [])

    def test_part_prompts_stay_short_for_the_small_model(self):
        # Long prompts measurably degraded Nemotron-Mini's replies; each part's prompt stays near a
        # thousand tokens (about four and a half to six thousand characters).
        for field, prompt in FIELD_PROMPTS.items():
            with self.subTest(field=field):
                self.assertLess(len(prompt), 7000)
                self.assertNotIn("source_evidence", prompt)

    def test_hypothesis_is_computed_from_threshold_sides(self):
        expectations = [({"clinical": 0.85, "mif": 0.79, "fused": 0.95}, "consistent", 1, 1),
                        ({"clinical": 0.12, "mif": 0.18, "fused": 0.03}, "consistent", 0, 0),
                        ({"clinical": 0.58, "mif": 0.90, "fused": 0.92}, "uneven", 1, 1),
                        ({"clinical": 0.11, "mif": 0.80, "fused": 0.34}, "conflicting", None, 0),
                        ({"clinical": 0.49, "mif": 0.53, "fused": 0.51}, "conflicting", None, 1),
                        ({"clinical": 0.66}, "single-modality", 1, 1)]
        for scores, kind, side, tendency in expectations:
            with self.subTest(scores=scores):
                result = hypothesis(case(scores)[1])
                self.assertEqual((result["kind"], result["side"], result["tendency"]), (kind, side, tendency))
                self.assertNotRegex(result["statement"], r"\d")
        undetermined = hypothesis(case({"clinical": 0.4, "mif": 0.6, "fused": 0.5}, threshold=None)[1])
        self.assertEqual((undetermined["kind"], undetermined["side"]), ("undetermined", None))

    def test_situation_restates_comparison_with_margins_in_plain_words(self):
        patient, comparison = case({"clinical": 0.11, "mif": 0.80, "fused": 0.34})
        self.assertEqual(describe_comparison(patient["predictions"], comparison),
                         "models disagree on opposite sides of the threshold; clinical well below threshold; "
                         "spatial mIF well above threshold; fused moderately below threshold; fused joins clinical")
        patient, comparison = case({"clinical": 0.66})
        self.assertEqual(describe_comparison(patient["predictions"], comparison),
                         "spatial mIF and fused missing; clinical moderately above threshold")

    def test_prompt_carries_plain_evidence_and_curated_literature(self):
        patient, comparison = case({"clinical": 0.11, "mif": 0.80, "fused": 0.34},
                                   clinical=[("Prior targeted therapy", -0.43), ("LDH level", None)],
                                   mif=[("T cell → iNOS+ tumor proximity", 7.2), ("Unlisted marker", 0.0)])
        payload = model_payload(patient, comparison)
        clinical_part = json.loads(build_messages(patient, comparison=comparison, field="clinical_interpretation")[-1]["content"].split("\n", 1)[1])
        self.assertEqual(clinical_part, {"clinical_evidence": payload["clinical_evidence"]})
        self.assertEqual(payload["clinical_evidence"][0], {"feature": "Prior targeted therapy", "value": "coded one",
                                                           "pushes_toward": "non-responder",
                                                           "literature": literature("Prior targeted therapy", "clinical")["gist"]})
        self.assertEqual(payload["clinical_evidence"][1]["direction"], "none supplied")
        self.assertNotIn("pushes_toward", payload["clinical_evidence"][1])
        garbled = generator(clinical_interpretation="LDH level pushes the clinical score toward not supplied; the literature notes an adverse factor.")
        result = Copilot(backend="vllm", generator=garbled).interpret(prediction())
        self.assertIn("garbled_feature_direction", result["quality"]["issues"])
        self.assertEqual(payload["immune_evidence"][0], {"feature": "T cell to iNOS+ tumor proximity", "focus": "higher",
                                                         "literature": "mixed, leaning responder in the foundation cohort"})
        self.assertEqual(payload["immune_evidence"][1]["literature"], "no curated note")
        self.assertNotRegex(payload["situation"] + payload["hypothesis"], r"\d")
        self.assertNotIn("comparison", payload)

    def test_literature_entries_cite_known_sources(self):
        names = ["Prior targeted therapy", "Lung metastases", "Metastatic stage", "Gender (male)", "Tissue resection",
                 "LDH level", "Prior ipilimumab"]
        self.assertTrue(all(literature(name, "clinical") for name in names))
        tissue = ["T cell → B/T cell co-localization", "T cell → iNOS+ tumor proximity", "Cytotoxic T cell → PDL1+ proximity",
                  "B/T cell → CD8+ T cell co-localization", "nNOS+/SOX10+ tumor subpopulation", "CD3+CD8+iNOS+ proportion",
                  "CD3+CD8+PDL1+ proportion", "Biopsy site: visceral", "CD3+ CD8+ Ripley's L (20um)", "PDL1+ proportion"]
        entries = {name: literature(name, "mif") for name in tissue}
        self.assertTrue(all(entries.values()))
        self.assertIn("CD8+ iNOS+", entries["CD3+CD8+iNOS+ proportion"]["note"])
        self.assertIn("CD3+CD20+", entries["B/T cell → CD8+ T cell co-localization"]["note"])
        self.assertIn("nNOS", entries["nNOS+/SOX10+ tumor subpopulation"]["note"])
        for entry in list(entries.values()) + [literature(name, "clinical") for name in names]:
            self.assertTrue(set(entry["sources"]) <= set(SOURCES))

    def test_replies_contradicting_the_report_facts_are_rejected(self):
        # Real local Nemotron statements that the earlier screen accepted or that a later prompt produced.
        concordant_no = case({"clinical": 0.07, "mif": 0.09, "fused": 0.01}, clinical=[("Prior targeted therapy", -0.4)])
        discordant = case({"clinical": 0.96, "mif": 0.14, "fused": 0.81}, clinical=[("Prior targeted therapy", -0.2)])
        unthresholded = case({"clinical": 0.49, "mif": 0.53, "fused": 0.51}, threshold=None, clinical=[("Metastatic stage", None)])
        unsigned = case({"clinical": 0.85, "mif": 0.79, "fused": 0.82}, clinical=[("LDH level", None), ("Prior ipilimumab", None)])
        wrong = [(concordant_no, {"prediction_summary": "The clinical score sits well below its responder threshold, so responder is the strongest hypothesis."}),
                 (discordant, {"conclusion": "Responder is the strongest hypothesis, leaning on the clinical model. Non-responder is the strongest hypothesis, leaning on the spatial mIF model."}),
                 (discordant, {"prediction_summary": "The clinical score sits above its responder threshold and the spatial mIF score sits above it."}),
                 (discordant, {"clinical_interpretation": "Prior targeted therapy pushes the clinical score toward responder."}),
                 (discordant, {"prediction_summary": "The models agree on the responder side."}),
                 (unthresholded, {"conclusion": "The tendency is toward non-responder, following the clinical evidence."}),
                 (unsigned, {"clinical_interpretation": "LDH level and Prior ipilimumab both push the clinical score toward responder."}),
                 (unsigned, {"prediction_summary": "The spatial mIF score is missing, so only clinical evidence remains."}),
                 (discordant, {"clinical_interpretation": "No signed attribution was supplied, so Prior targeted therapy cannot be assigned a direction."})]
        for (patient, comparison), sections in wrong:
            with self.subTest(sections=sections):
                full = {"prediction_summary": "x", "clinical_interpretation": "x", "conclusion": "x", **sections}
                self.assertEqual(report_contradictions(full, patient, comparison), ["contradicts_supplied_comparison"])
        right = [(concordant_no, {"prediction_summary": "Non-responder is the strongest hypothesis because every score sits below its responder threshold.",
                                  "clinical_interpretation": "Prior targeted therapy pushes the clinical score toward non-responder."}),
                 (discordant, {"prediction_summary": "The models disagree: the clinical score sits well above its responder threshold while the spatial mIF score sits below it, and the fused score joins the clinical side, so there is no strong hypothesis and the tendency is toward responder.",
                               "conclusion": "There is no strong hypothesis because the clinical evidence favours responder while the tissue evidence favours non-responder."}),
                 (unthresholded, {"conclusion": "No strong hypothesis can be drawn because no responder thresholds were supplied."}),
                 (unsigned, {"clinical_interpretation": "No signed attribution was supplied, so LDH level cannot be assigned a direction."})]
        for (patient, comparison), sections in right:
            with self.subTest(sections=sections):
                full = {"prediction_summary": "x", "clinical_interpretation": "x", "conclusion": "x", **sections}
                self.assertEqual(report_contradictions(full, patient, comparison), [])

    def test_current_patient_context_is_separate_and_labels_do_not_leak(self):
        patients = load_jsonl(ROOT / "examples/prompt_quality_cases.jsonl")
        seen = []

        def recording(conversations):
            seen.extend(conversations)
            return generator()(conversations)

        Copilot(backend="vllm", generator=recording).interpret_many(patients)
        self.assertEqual(len(seen), len(REPLY_FIELDS) * len(patients))
        for index, conversation in enumerate(seen):
            data = patients[index // len(REPLY_FIELDS)].to_dict()
            field = part_of(conversation)
            self.assertEqual(field, REPLY_FIELDS[index % len(REPLY_FIELDS)])
            payload = json.loads(conversation[-1]["content"].split("\n", 1)[1])
            full = model_payload(data, summarize_evidence(data)[0])
            self.assertEqual(payload, {key: full[key] for key in FIELD_INPUTS[field]})
            for leaked in ("patient_id", "ground_truth", "evaluation_partition", "clinical_context"):
                self.assertNotIn(leaked, payload)
            self.assertNotIn("<assistant>", conversation[-1]["content"])

    def test_irrelevant_generic_reply_falls_back_for_disagreement(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[1]
        result = Copilot(backend="vllm", generator=generator(**WORKED_EXAMPLES[0]["output"])).interpret(patient)
        self.assertEqual(result["narrative_source"], "fallback")
        self.assertIn("missing_disagreement_context", result["quality"]["issues"])
        self.assertEqual(result["predictions"], patient.to_dict()["predictions"])

    def test_generic_reply_falls_back_when_modalities_are_missing(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[2]
        result = Copilot(backend="vllm", generator=generator(**WORKED_EXAMPLES[0]["output"])).interpret(patient)
        self.assertIn("missing_modality_context", result["quality"]["issues"])

    def test_matched_reply_is_retained_with_prompt_provenance(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[1]
        result = Copilot(backend="vllm", generator=generator(**P12_REPLY)).interpret(patient)
        self.assertEqual(result["narrative_source"], "vllm", result["quality"])
        self.assertEqual(result["provenance"]["prompt_version"], PROMPT_VERSION)
        self.assertEqual(result["provenance"]["prompt_sha256"], PROMPT_SHA256)
        self.assertEqual(result["predictions"], patient.to_dict()["predictions"])
        for text in P12_REPLY.values():
            self.assertIn(text, result["narrative"])

    def test_patient_template_and_quality_cases_are_valid_synthetic_inputs(self):
        template = PatientPrediction.from_dict(json.loads((ROOT / "examples/patient_template.json").read_text()))
        self.assertEqual(template.data["evaluation_partition"], "synthetic")
        cases = load_jsonl(ROOT / "examples/prompt_quality_cases.jsonl")
        self.assertEqual(len(cases), 6)
        self.assertTrue(all(case.data["evaluation_partition"] == "synthetic" and case.data["ground_truth"] is None for case in cases))
        no_threshold = next(p for p in cases if p.patient_id == "P_NO_THRESHOLD")
        self.assertTrue(all(value is None for value in summarize_evidence(no_threshold.to_dict())[0]["predicted_classes"].values()))

    def test_raw_rejected_text_is_saved_separately_from_display_narrative(self):
        bad = "The treatment guarantees cure at ninety-nine percent."
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            manifest = run_experiment(ROOT / "examples/mock_predictions.jsonl", output,
                                      Copilot(backend="vllm", generator=generator(conclusion=bad)))
            reviews = [json.loads(line) for line in (output / "generation_review.jsonl").read_text().splitlines()]
            results = [json.loads(line) for line in (output / "narratives.jsonl").read_text().splitlines()]
            self.assertIn("generation_review.jsonl", manifest["artifacts"])
            self.assertEqual([row["patient_id"] for row in reviews], [row["patient_id"] for row in results])
            for review, result in zip(reviews, results):
                self.assertEqual(json.loads(json.loads(review["raw_generation"])["conclusion"])["text"], bad)
                self.assertEqual(review["screen_status"], "fallback")
                self.assertTrue(review["screen_issues"])
                self.assertNotIn("guarantees cure", result["narrative"])


if __name__ == "__main__":
    unittest.main()
